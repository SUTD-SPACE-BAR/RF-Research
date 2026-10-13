#!/usr/bin/env python3
"""Verification for kb/10-comms-modulation/multiple-access-and-duplexing.md

 1. Pure ALOHA S = G e^{-2G} and slotted ALOHA S = G e^{-G}: event simulation vs formula,
    maxima 1/(2e) at G = 0.5 and 1/e at G = 1.
 2. Finite-population packet success probability for N independent periodic-ish (Poisson) senders.
 3. Capture effect (LoRa same-SF, >= 6 dB) with random received powers raises ALOHA throughput.
 4. Non-persistent CSMA (Kleinrock-Tobagi): S = G e^{-aG} / (G(1+2a) + e^{-aG}) vs simulation.
 5. LoRa time on air (Semtech formula) -- matches the KB value (32 B, SF7/125 kHz -> 71.9 ms).
 6. Launch-day numbers: shared-channel collision probability for several rockets; TDMA slot plan
    with guard times from clock drift; FDMA channel counts on the EBYTE 1 MHz grid.
 7. Duplexing: FDD duplexer isolation needed (TX noise desense and TX blocking); TDD T/R-switch
    leakage into an LNA; desensitisation formula.
 8. Near-far: path-loss disparity between a pad transmitter and a rocket at range vs LoRa
    co-SF capture (6 dB) and inter-SF (~ -16 dB) thresholds.
Run: python3 tools/verify/est_multiple_access.py   (about 20 s)
"""
import numpy as np

ok_all = True
rng = np.random.default_rng(2026)


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel and want != 0 else 1.0)
    ok = err <= tol
    ok_all &= bool(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol}{' rel' if rel else ''})")


def check_true(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


print("== 1. ALOHA throughput ==")


def sim_pure(G, n_pk=200000):
    t = np.cumsum(rng.exponential(1 / G, n_pk))     # packet length 1, offered load G per packet time
    gap_prev = np.diff(t, prepend=-np.inf)
    gap_next = np.diff(t, append=np.inf)
    ok = (gap_prev > 1) & (gap_next > 1)
    return ok.sum() / t[-1]


def sim_slotted(G, n_slots=400000):
    k = rng.poisson(G, n_slots)
    return np.mean(k == 1)


for G in (0.25, 0.5, 1.0, 2.0):
    check(f"pure ALOHA S at G = {G}", sim_pure(G), G * np.exp(-2 * G), 0.03, rel=True)
    check(f"slotted ALOHA S at G = {G}", sim_slotted(G), G * np.exp(-G), 0.02, rel=True)
check("pure ALOHA max = 1/(2e)", 0.5 * np.exp(-1), 1 / (2 * np.e), 1e-15)
check("slotted ALOHA max = 1/e", 1 * np.exp(-1), 1 / np.e, 1e-15)
Gs = np.linspace(0.01, 3, 3000)
check("argmax of G e^{-2G} = 0.5", Gs[np.argmax(Gs * np.exp(-2 * Gs))], 0.5, 1e-3)
check("argmax of G e^{-G} = 1", Gs[np.argmax(Gs * np.exp(-Gs))], 1.0, 1e-3)

print("\n== 2. success probability of one sender among N (pure ALOHA, Poisson others) ==")
# each other sender: rate r packets/s, airtime Ta -> vulnerable window 2 Ta
for N, r, Ta in ((6, 2.0, 0.0719), (10, 1.0, 0.0719), (3, 10.0, 0.0154)):
    G_other = (N - 1) * r * Ta
    p = np.exp(-2 * G_other)
    # Monte-Carlo: random independent Poisson senders over 2000 s
    T = 2000.0
    times = [np.sort(rng.uniform(0, T, rng.poisson(r * T))) for _ in range(N)]
    mine = times[0]; others = np.sort(np.concatenate(times[1:]))
    idx = np.searchsorted(others, mine)
    prev = np.where(idx > 0, others[np.maximum(idx - 1, 0)], -np.inf)
    nxt = np.where(idx < len(others), others[np.minimum(idx, len(others) - 1)], np.inf)
    succ = np.mean((mine - prev > Ta) & (nxt - mine > Ta))
    check(f"N={N}, {r} pkt/s, Ta={Ta*1e3:.1f} ms: P(success) = e^(-2(N-1) r Ta)", succ, p, 0.03, rel=True)
    print(f"      offered load of the others G = {G_other:.3f}; P(success) = {p:.3f}")

print("\n== 3. capture effect (same-SF LoRa, >= 6 dB) ==")


def sim_slotted_capture(G, thr_db=6.0, sigma_db=8.0, n_slots=200000):
    succ = 0
    k = rng.poisson(G, n_slots)
    for kk in k[k >= 1]:
        if kk == 1:
            succ += 1
        else:
            p = rng.normal(0, sigma_db, kk)       # log-normal received powers (dB)
            ps = np.sort(p)
            # strongest must exceed the sum of all others by thr
            others = 10 * np.log10(np.sum(10 ** (ps[:-1] / 10)))
            if ps[-1] - others >= thr_db:
                succ += 1
    return succ / n_slots


S_cap = sim_slotted_capture(1.0)
print(f"    slotted ALOHA at G = 1 with capture (8 dB spread, 6 dB threshold): S = {S_cap:.3f} vs {np.exp(-1):.3f} without")
check_true("capture raises throughput above 1/e at G = 1", S_cap > np.exp(-1) * 1.05)

print("\n== 4. non-persistent CSMA ==")


def csma_np_formula(G, a):
    return G * np.exp(-a * G) / (G * (1 + 2 * a) + np.exp(-a * G))


def sim_csma_np(G, a, n_arr=300000):
    """Non-persistent CSMA, packet length 1, propagation delay a; arrivals (incl. reschedules) Poisson G.
    A channel 'busy period' starts with a transmission; any arrival within a of it also transmits
    (collision); arrivals that sense busy back off (are lost to the Poisson stream, which is the
    standard infinite-population assumption)."""
    t = np.cumsum(rng.exponential(1 / G, n_arr))
    i, succ_time = 0, 0.0
    end_busy = -1.0
    while i < len(t):
        if t[i] < end_busy:                      # sensed busy -> defer (dropped from stream)
            i += 1
            continue
        start = t[i]
        j = i + 1
        last = start
        while j < len(t) and t[j] < start + a:   # vulnerable window: others don't yet sense it
            last = t[j]; j += 1
        if j == i + 1:
            succ_time += 1.0
            end_busy = start + 1 + a
        else:
            end_busy = last + 1 + a
        i = j
    return succ_time / t[-1]


for a in (0.01, 0.1):
    for G in (0.5, 2.0, 10.0):
        check(f"np-CSMA a={a}, G={G}", sim_csma_np(G, a), csma_np_formula(G, a), 0.05, rel=True)
Gg = np.logspace(-2, 3, 20000)
for a in (0.01, 0.1):
    print(f"    np-CSMA a = {a}: max S = {np.max(csma_np_formula(Gg, a)):.3f} at G = {Gg[np.argmax(csma_np_formula(Gg, a))]:.1f}")

print("\n== 5. LoRa time on air ==")


def lora_toa(pl, sf, bw, cr=1, preamble=8, crc=1, ih=0, de=None):
    if de is None:
        de = 1 if (2 ** sf / bw) > 16e-3 else 0
    ts = 2 ** sf / bw
    n_pay = 8 + max(int(np.ceil((8 * pl - 4 * sf + 28 + 16 * crc - 20 * ih) / (4 * (sf - 2 * de)))) * (cr + 4), 0)
    return (preamble + 4.25) * ts + n_pay * ts


check("ToA 32 B SF7/125 kHz CR4/5 [ms] (KB: 0.72 s per frame at 10 %)", lora_toa(32, 7, 125e3) * 1e3, 71.936, 1e-3)
check("ToA 32 B SF7/500 kHz [ms]", lora_toa(32, 7, 500e3) * 1e3, 17.984, 1e-3)
check("ToA 32 B SF9/125 kHz [ms] (60.25 symbols x 4.096 ms)", lora_toa(32, 9, 125e3) * 1e3, 246.784, 1e-3)
# cross-check against the KB calculator tools/rfcalc/lora.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from rfcalc.lora import time_on_air as _toa
for args in ((32, 7, 125e3), (32, 7, 500e3), (32, 9, 125e3), (60, 10, 250e3)):
    check(f"ToA {args} equals rfcalc.lora.time_on_air", lora_toa(*args), _toa(*args), 1e-12)

print("\n== 6. launch-day planning numbers ==")
# (a) shared channel: 6 rockets at 2 Hz, 32 B SF7/125 (71.9 ms)
Ta = lora_toa(32, 7, 125e3)
for nr in (2, 4, 6):
    p = np.exp(-2 * (nr - 1) * 2.0 * Ta)
    print(f"    {nr} rockets sharing one channel, 2 Hz each, Ta {Ta*1e3:.1f} ms: P(packet survives) = {p:.3f}")
check("6 rockets, 2 Hz, 71.9 ms, one channel: P(success)", np.exp(-2 * 5 * 2.0 * Ta), 0.2371, 1e-3)
# (b) TDMA on GNSS time: frame 0.5 s (2 Hz), slot = Ta + guard
drift_ppm, resync = 0.0, 1.0                     # GNSS PPS disciplined: timing error ~ 1 us + MCU latency
mcu_jitter = 2e-3                                # scheduling jitter of a UART module (assumed 2 ms)
guard = 2 * mcu_jitter + 30e3 / 3e8              # +- jitter both ends + 30 km propagation
slot = Ta + guard
n_slots = int(0.5 // slot)
check("TDMA: slots per 0.5 s frame with 71.9 ms packets and ~4.1 ms guard", n_slots, 6, 0)
check("TDMA efficiency Ta/slot", Ta / slot, 0.9461, 1e-3)
# free-running crystal TDMA: 20 ppm, resync every 10 s -> drift 0.2 ms per side
check("free-running 20 ppm over 10 s: slot drift [ms]", 20e-6 * 10 * 1e3, 0.2, 1e-12)
# (c) FDMA on the EBYTE 1 MHz grid
ch_ham = [410.125 + c for c in range(84) if 430.0 <= 410.125 + c - 0.0625 and 410.125 + c + 0.0625 <= 440.0]
ch_srd = [410.125 + c for c in range(84) if 433.05 <= 410.125 + c - 0.0625 and 410.125 + c + 0.0625 <= 434.79]
check("E22 channels fully inside 430-440 MHz (125 kHz BW)", len(ch_ham), 10, 0)
check("E22 channels inside 433.05-434.79 MHz SRD band", len(ch_srd), 2, 0)
ch_9 = [850.125 + c for c in range(81) if 917.0 <= 850.125 + c - 0.0625 and 850.125 + c + 0.0625 <= 925.0]
check("E220 channels inside 917-925 MHz", len(ch_9), 8, 0)

print("\n== 7. duplexing ==")
def desense_db(n_int_dbm_hz, nf_db):
    n_rx = -174 + nf_db
    return 10 * np.log10(1 + 10 ** ((n_int_dbm_hz - n_rx) / 10))
# FDD: TX 30 dBm with noise floor -135 dBc/Hz at the RX offset; RX NF 6 dB
ptx, tx_noise_dbc = 30.0, -135.0
need_iso_noise = (ptx + tx_noise_dbc) - (-174 + 6) + 10      # TX noise 10 dB below RX floor
check("FDD duplexer isolation for TX noise 10 dB under RX floor [dB]", need_iso_noise, 73.0, 1e-9)
check("desense when interferer is 10 dB under the noise floor [dB]", desense_db(-178, 6), 0.4139, 1e-3)
check("desense when interferer equals the noise floor [dB]", desense_db(-168, 6), 3.0103, 1e-3)
# TX carrier blocking: keep TX at RX input below -40 dBm (assumed blocker tolerance)
need_iso_block = ptx - (-40.0)
check("FDD isolation for TX carrier < -40 dBm at RX [dB]", need_iso_block, 70.0, 1e-9)
# TDD: T/R switch isolation 25 dB at 33 dBm -> leakage into LNA
check("TDD: 33 dBm through 25 dB T/R isolation at LNA input [dBm]", 33 - 25, 8.0, 0)
check_true("  exceeds EBYTE's 10 dBm damage/blocking rating margin? (8 dBm < 10 dBm, only 2 dB margin)", 33 - 25 < 10)

print("\n== 8. near-far at the pad ==")
f = 433e6
fspl = lambda d: 20 * np.log10(4 * np.pi * d * f / 3e8)
disp = fspl(30e3) - fspl(1e3)
check("path-loss disparity: rocket at 30 km vs pad TX at 1 km [dB]", disp, 29.54, 0.01)
disp2 = fspl(10e3) - fspl(50.0)
check("rocket at 10 km vs neighbouring pad TX 50 m away [dB]", disp2, 46.02, 0.01)
check_true("  disparity >> 6 dB co-SF capture: same channel + same SF is unusable near the pad", disp > 6)
check_true("  disparity > 16 dB inter-SF tolerance: different SF alone does not protect", disp > 16)

print("\n== 9. worked-example extras ==")
check("SF7/500 slots per 0.5 s frame (18.0 ms + 4.1 ms guard)", int(0.5 // (lora_toa(32, 7, 500e3) + guard)), 22, 0)
# bare-chip grid in 433.05-434.79 MHz: 125 kHz channels with +-10 kHz drift margin
for sp, want in ((0.25, 7), (0.2, 8)):
    usable = 1.74 - 0.125 - 0.02
    check(f"SRD band channels on a {sp*1e3:.0f} kHz grid (125 kHz + drift)", int(usable // sp) + 1, want, 0)
# neighbour TX phase noise: 30 dBm, -130 dBc/Hz at 1 MHz, 50 m and 500 m at 433 MHz, RX NF 6 dB
for dist, want in ((50.0, 9.38), (500.0, 0.32)):
    n_i = 30 - 130 - fspl(dist)
    check(f"desense from neighbour TX noise at {dist:.0f} m [dB]", desense_db(n_i, 6), want, 0.02)
check("Doppler at Mach 3 (1029 m/s), 433 MHz [Hz]", 433e6 * 1029 / 299792458, 1486.2, 0.5)
check("20 ppm at 433 MHz [kHz]", 20e-6 * 433e3, 8.66, 1e-9)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
