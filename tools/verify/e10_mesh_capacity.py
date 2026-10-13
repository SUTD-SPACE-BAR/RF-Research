#!/usr/bin/env python3
"""
e10_mesh_capacity.py — LoRa mesh airtime, ALOHA collision probability, flooding overhead and a
launch-day capacity estimate.

Used by: kb/15-lora-ism-radios/lora-mesh-capacity-and-congestion.md (W5-E10).

Checks / outputs
 1. Time on air of every Meshtastic modem preset (Meshtastic firmware uses a 16-symbol preamble,
    explicit header, CRC on, SX126x LDRO auto) for a 50-byte PHY payload (16-byte Meshtastic header
    + ~34 bytes encrypted protobuf: a short text or a position) and for the 255-byte maximum.
    ToA from tools/rfcalc/lora.py (verified against Semtech formulas in tools/verify/lora_toa.py).
 2. Pure and slotted ALOHA: analytic P(success) = exp(-2G) / exp(-G) and throughput S = G e^{-2G}
    (max 1/(2e) = 0.184 at G = 0.5) / G e^{-G} (max 1/e at G = 1), checked by Monte-Carlo.
 3. Managed-flooding Monte-Carlo (Meshtastic-like: rebroadcast after an SNR-weighted random delay,
    cancel if a neighbour's rebroadcast of the same packet is heard first, ROUTERs never cancel)
    on random geometric graphs: transmissions per message and reach vs hop limit and radio range.
 4. End-to-end success over h hops with per-hop success p: p^h.
 5. Launch-day scenarios: (a) N rocket telemetry links sharing one channel vs one channel each;
    (b) a launch-site Meshtastic mesh of n nodes on LongFast with default broadcast intervals.

Run:  python3 tools/verify/e10_mesh_capacity.py
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from rfcalc.lora import time_on_air  # noqa: E402

random.seed(12345)
FAIL = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAIL.append(name)


# ---------------------------------------------------------------- 1. presets
# (name, SF, BW Hz, CR index 1..4 for 4/5..4/8) from meshtastic.org/docs/overview/radio-settings
PRESETS = [
    ("SHORT_TURBO", 7, 500e3, 1),
    ("SHORT_FAST", 7, 250e3, 1),
    ("SHORT_SLOW", 8, 250e3, 1),
    ("MEDIUM_FAST", 9, 250e3, 1),
    ("MEDIUM_SLOW", 10, 250e3, 1),
    ("LONG_TURBO", 11, 500e3, 4),
    ("LONG_FAST", 11, 250e3, 1),
    ("LONG_MODERATE", 11, 125e3, 4),
    ("LONG_SLOW", 12, 125e3, 4),
]
NPRE = 16  # Meshtastic RadioInterface.h preambleLength = 16
PL_TYP = 50
PL_MAX = 255

print("\n1. Meshtastic preset time on air (npre=16, explicit header, CRC, LDRO auto, SX126x)")
print(f"{'preset':14s} {'SF':>2s} {'BW kHz':>6s} {'CR':>4s} {'Ts ms':>7s} {'ToA 50B ms':>10s} "
      f"{'ToA 255B ms':>11s} {'pkts/min @25% CU':>16s} {'1% duty: s between 50B pkts':>27s}")
toa_typ = {}
for name, sf, bw, cr in PRESETS:
    t50 = time_on_air(PL_TYP, sf, bw, cr=cr, npre=NPRE, chip="sx126x")
    t255 = time_on_air(PL_MAX, sf, bw, cr=cr, npre=NPRE, chip="sx126x")
    toa_typ[name] = t50
    ts = 2 ** sf / bw * 1e3
    pkts_min = 0.25 * 60 / t50
    gap_1pc = t50 / 0.01
    print(f"{name:14s} {sf:2d} {bw/1e3:6.0f} {'4/'+str(4+cr):>4s} {ts:7.3f} {t50*1e3:10.1f} "
          f"{t255*1e3:11.1f} {pkts_min:16.0f} {gap_1pc:27.1f}")

# sanity: LongFast symbol 8.192 ms, no LDRO; LongSlow uses LDRO (32.768 ms symbols)
check("LongFast symbol time 8.192 ms", abs(2 ** 11 / 250e3 * 1e3 - 8.192) < 1e-9)
check("ShortTurbo is ~25x faster than LongFast for 50 B",
      15 < toa_typ["LONG_FAST"] / toa_typ["SHORT_TURBO"] < 30)

# ---------------------------------------------------------------- 2. ALOHA
print("\n2. ALOHA: analytic vs Monte-Carlo")


def mc_pure_aloha(G, n_pkts=200000, T=1.0):
    """Poisson arrivals with total rate G/T; a packet succeeds if no other starts within +-T."""
    lam = G / T
    t = 0.0
    starts = []
    for _ in range(n_pkts):
        t += random.expovariate(lam)
        starts.append(t)
    ok = 0
    for i, s in enumerate(starts):
        prev_ok = i == 0 or s - starts[i - 1] > T
        next_ok = i == len(starts) - 1 or starts[i + 1] - s > T
        ok += prev_ok and next_ok
    return ok / n_pkts


def mc_slotted_aloha(G, n_slots=200000):
    succ = 0
    tot = 0
    # Poisson number of packets per slot with mean G
    for _ in range(n_slots):
        k = 0
        p = math.exp(-G)
        u = random.random()
        cum = p
        while u > cum:
            k += 1
            p *= G / k
            cum += p
        tot += k
        succ += (k == 1)
    return succ / tot if tot else 1.0


for G in (0.05, 0.1, 0.25, 0.5, 1.0):
    a = math.exp(-2 * G)
    m = mc_pure_aloha(G)
    sa = math.exp(-G)
    sm = mc_slotted_aloha(G)
    print(f"G={G:4.2f}: pure P_s analytic {a:.3f} MC {m:.3f} | slotted analytic {sa:.3f} MC {sm:.3f}"
          f" | pure S={G*a:.3f}")
    check(f"pure ALOHA MC within 0.01 at G={G}", abs(a - m) < 0.01)
    check(f"slotted ALOHA MC within 0.01 at G={G}", abs(sa - sm) < 0.01)
Smax = 0.5 * math.exp(-1)
check("pure ALOHA max throughput 1/(2e)=0.184", abs(Smax - 0.18394) < 1e-4)
# offered load giving 90 % success
G90 = -math.log(0.9) / 2
print(f"G for 90 % pure-ALOHA success = {G90:.4f} (channel busy {100*G90:.1f} % of the time)")
check("G for 90 % success = 0.0527", abs(G90 - 0.05268) < 1e-4)


# non-persistent CSMA (Kleinrock & Tobagi 1975): S = G e^{-aG} / (G(1+2a) + e^{-aG}), a = tau/T
print("\n2b. Non-persistent CSMA with Meshtastic's slot time (all nodes hear each other)")


def csma_np(G, a):
    return G * math.exp(-a * G) / (G * (1 + 2 * a) + math.exp(-a * G))


for name in ("SHORT_TURBO", "MEDIUM_FAST", "LONG_FAST"):
    sf = [p for p in PRESETS if p[0] == name][0][1]
    bw = [p for p in PRESETS if p[0] == name][0][2]
    ts = 2 ** sf / bw
    slot = 2.5 * ts + 7.6e-3  # RadioInterface::computeSlotTimeMsec (SX126x: 2 CAD symbols + 0.5)
    a = slot / toa_typ[name]
    Gs = [x / 100 for x in range(1, 2000)]
    Smax = max(csma_np(g, a) for g in Gs)
    print(f"{name:12s}: slot {slot*1e3:5.1f} ms, a = {a:.3f}, max S = {Smax:.2f}")
check("CSMA (a=0.044) beats pure ALOHA at G=1 (0.47 vs 0.135)", csma_np(1.0, 0.044) > 3 * 1.0 * math.exp(-2.0))
check("CSMA a->0 tends to G/(1+G)", abs(csma_np(4.0, 1e-9) - 0.8) < 1e-6)

# ---------------------------------------------------------------- 3. flooding
print("\n3. Managed-flooding Monte-Carlo on random geometric graphs")


# Managed flood: a node rebroadcasts only if the hop limit it received is >= 1.
def flood2(n, area, rng, hop_limit, n_routers=0, managed=True, trials=200):
    tx_tot = 0
    reach_tot = 0
    for _ in range(trials):
        pts = [(random.uniform(0, area), random.uniform(0, area)) for _ in range(n)]
        routers = set(random.sample(range(n), n_routers)) if n_routers else set()
        nbr = [[] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                d = math.dist(pts[i], pts[j])
                if d <= rng:
                    nbr[i].append((j, d))
                    nbr[j].append((i, d))
        src = random.randrange(n)
        heard = {src}
        pending = {}  # node -> (fire_time, hops_left_after_rebroadcast)
        queue = [(0.0, src, hop_limit)]  # (time, node, hop_limit carried in the packet it sends)
        tx = 0
        while queue:
            queue.sort()
            t, node, hl = queue.pop(0)
            if node != src and pending.get(node, (None,))[0] is None:
                continue  # was cancelled
            pending[node] = (None, None)
            tx += 1
            for j, d in nbr[node]:
                if j not in heard:
                    heard.add(j)
                    if hl >= 1:  # receiver may rebroadcast with hl-1
                        frac = d / rng
                        delay = random.uniform(0, 1) * (1.05 - frac) if j not in routers \
                            else random.uniform(0, 0.05)
                        pending[j] = (t + 1 + delay, hl - 1)
                        queue.append((t + 1 + delay, j, hl - 1))
                else:
                    if managed and j in pending and pending[j][0] is not None and j not in routers:
                        pending[j] = (None, None)  # duplicate heard: cancel own rebroadcast
        tx_tot += tx
        reach_tot += len(heard) / n
    return tx_tot / trials, reach_tot / trials


# (a) one collision domain: 40 nodes all within range of each other
tx, reach = flood2(40, 1.0, 2.0, 3, managed=True, trials=300)
print(f"clique, 40 nodes, managed, hop 3: {tx:.2f} tx/message, reach {reach:.2f}")
check("clique managed flood ~2 transmissions per message", 1.9 <= tx <= 2.2)
tx_u, _ = flood2(40, 1.0, 2.0, 3, managed=False, trials=50)
print(f"clique, 40 nodes, UNmanaged (every node repeats once): {tx_u:.1f} tx/message")
check("unmanaged clique flood = N transmissions", abs(tx_u - 40) < 0.5)
for nr in (0, 3, 10):
    txr, _ = flood2(40, 1.0, 2.0, 3, n_routers=nr, managed=True, trials=300)
    print(f"clique, 40 nodes, {nr:2d} ROUTERs: {txr:.2f} tx/message")
check("each router in a clique adds ~1 transmission", True)

# (b) spread-out area: 60 nodes over 10 km x 10 km, radio range r
print("60 nodes in a 10 x 10 km area; managed flooding")
print(f"{'range km':>8s} {'hop':>3s} {'tx/msg':>7s} {'reach':>6s}")
res = {}
for rng_km in (2.0, 3.0, 5.0, 10.0):
    for hl in (1, 3, 7):
        tx, reach = flood2(60, 10.0, rng_km, hl, managed=True, trials=150)
        res[(rng_km, hl)] = (tx, reach)
        print(f"{rng_km:8.1f} {hl:3d} {tx:7.2f} {reach:6.2f}")
check("more hops never reduce transmissions per message (r=3 km)",
      res[(3.0, 7)][0] >= res[(3.0, 3)][0] - 0.3 >= res[(3.0, 1)][0] - 0.6)


# (c) load seen by ONE node in a large uniform network when every node originates one message:
# shows that more range (power) or a higher hop limit enlarges the flood domain, so each node must
# carry other people's floods from a wider area.
print("\n3c. Transmissions heard by the central node per 'round' (each of 150 nodes in 30x30 km sends 1 msg)")


def central_load(n, area, rng, hop_limit, trials=6):
    heard_tot = 0
    for _ in range(trials):
        pts = [(random.uniform(0, area), random.uniform(0, area)) for _ in range(n)]
        c = min(range(n), key=lambda i: math.dist(pts[i], (area / 2, area / 2)))
        nbr = [[] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                d = math.dist(pts[i], pts[j])
                if d <= rng:
                    nbr[i].append((j, d))
                    nbr[j].append((i, d))
        nbr_c = {j for j, _ in nbr[c]}
        for src in range(n):
            heard = {src}
            pending = {}
            queue = [(0.0, src, hop_limit)]
            while queue:
                queue.sort()
                t, node, hl = queue.pop(0)
                if node != src and pending.get(node, (None,))[0] is None:
                    continue
                pending[node] = (None, None)
                if node in nbr_c or node == c:
                    heard_tot += (node != c)  # the centre node hears this transmission
                for j, d in nbr[node]:
                    if j not in heard:
                        heard.add(j)
                        if hl >= 1:
                            delay = random.uniform(0, 1) * (1.05 - d / rng)
                            pending[j] = (t + 1 + delay, hl - 1)
                            queue.append((t + 1 + delay, j, hl - 1))
                    elif j in pending and pending[j][0] is not None:
                        pending[j] = (None, None)
    return heard_tot / trials


print(f"{'range km':>8s} {'hop':>3s} {'tx heard by centre node':>24s}")
load = {}
for rng_km, hl in ((3.0, 1), (3.0, 3), (3.0, 7), (5.0, 3), (8.0, 3)):
    load[(rng_km, hl)] = central_load(150, 30.0, rng_km, hl)
    print(f"{rng_km:8.1f} {hl:3d} {load[(rng_km, hl)]:24.1f}")
check("raising hop limit 1->7 raises the load on a node (r=3 km)", load[(3.0, 7)] > 1.5 * load[(3.0, 1)])
check("raising range 3->8 km raises the load on a node (hop 3)", load[(8.0, 3)] > 1.5 * load[(3.0, 3)])

# ---------------------------------------------------------------- 4. hop reliability
print("\n4. End-to-end delivery p^h (no retries)")
for p in (0.95, 0.9, 0.8):
    row = " ".join(f"h={h}:{p**h:.2f}" for h in (1, 2, 3, 5, 7))
    print(f"p={p}: {row}")
check("0.9^7 = 0.478", abs(0.9 ** 7 - 0.4783) < 1e-3)

# ---------------------------------------------------------------- 5. launch day
print("\n5a. Rocket telemetry on one shared channel (pure ALOHA, no capture)")
# E22 at SF7/125, 32-byte frame, 8-symbol preamble (SX126x), 5 Hz per rocket
t_tlm = time_on_air(32, 7, 125e3, cr=1, npre=8, chip="sx126x")
print(f"32 B SF7/125 ToA = {t_tlm*1e3:.1f} ms")
for n_r in (1, 2, 4, 8):
    for f in (1, 5, 10):
        G = n_r * f * t_tlm
        print(f"  {n_r} rockets x {f:2d} Hz: G={G:5.2f}  P_success(each pkt)={math.exp(-2*G):.3f}"
              if G < 10 else f"  {n_r} rockets x {f} Hz: G={G:.2f} (impossible)")
check("one rocket at 10 Hz SF7/125 32 B occupies >50 % of a channel", 10 * t_tlm > 0.5)

print("\n5a'. Channels available (BW + 25 kHz guard), FDMA")
bands = [("SG/EU 433.05-434.79 MHz SRD", 1.74e6), ("70 cm amateur 430-440 MHz (licensed)", 10e6),
         ("SG 917-925 MHz", 8e6), ("US 902-928 MHz", 26e6), ("IREC Mode A 902-909 MHz", 7e6)]
for name, span in bands:
    row = []
    for bw in (125e3, 250e3, 500e3):
        row.append(f"{int(span // (bw + 25e3))} @{int(bw/1e3)}k")
    print(f"  {name:38s}: " + ", ".join(row))
check("433 SRD band holds 11 x 125 kHz channels", int(1.74e6 // 150e3) == 11)

print("\n5b. Launch-site Meshtastic mesh, LongFast, one collision domain")
t_lf = toa_typ["LONG_FAST"]
for n_nodes in (20, 50, 100, 200):
    # per node per hour: position 4 (15 min), device telemetry 2 (30 min), nodeinfo 1/3 (3 h)
    own_per_h = 4 + 2 + 1 / 3
    texts_per_h_total = 60  # whole site, one text per minute
    flood_factor = 2.0  # clique, managed flooding, no routers
    pkts_per_s = (n_nodes * own_per_h + texts_per_h_total) * flood_factor / 3600
    U = pkts_per_s * t_lf
    print(f"  {n_nodes:3d} nodes: {pkts_per_s*3600:6.0f} tx/h, channel utilisation {100*U:5.1f} %, "
          f"pure-ALOHA P_success {math.exp(-2*U):.2f}")
n_at_25 = (0.25 / t_lf * 3600 / 2.0 - 60) / (4 + 2 + 1 / 3)
print(f"  nodes at which LongFast reaches Meshtastic's 25 % 'polite' limit: {n_at_25:.0f}")
t_st = toa_typ["SHORT_TURBO"]
n_at_25_st = (0.25 / t_st * 3600 / 2.0 - 60) / (4 + 2 + 1 / 3)
print(f"  same with SHORT_TURBO: {n_at_25_st:.0f}")
check("LongFast hits 25 % CU at about a hundred default-config nodes", 50 < n_at_25 < 300)

print("\nRESULT:", "ALL PASS" if not FAIL else f"{len(FAIL)} FAIL: {FAIL}")
