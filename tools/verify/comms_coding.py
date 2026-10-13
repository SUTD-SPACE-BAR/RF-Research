#!/usr/bin/env python3
"""Verification for kb/10-comms-modulation/channel-coding-fec.md

Run:  python3 tools/verify/comms_coding.py      (about 1-2 min; Viterbi Monte-Carlo dominates)

Checks:
  1. K=7, r=1/2 convolutional code (171,133 octal; CCSDS/NASA/Voyager "standard" code):
     free distance 10 and information-weight spectrum B_d (36, 211, 1404, 11633 for d = 10..16)
     computed by dynamic programming over the state diagram.
  2. Union bounds for soft- and hard-decision Viterbi decoding -> Eb/N0 at BER 1e-5.
  3. Monte-Carlo Viterbi decoder (soft, unquantised, and hard decision) vs the bounds.
  4. Hamming (7,4) and extended (8,4) codes: d_min, single-error correction; LoRa CR 4/5..4/8
     minimum distances; (6,4) cannot exceed d_min = 2.
  5. Reed-Solomon (255,223) t=16 bounded-distance decoding with hard-decision BPSK:
     required Eb/N0 for decoded BER 1e-5; and RS(255,223) concatenated with the K=7 code
     (ideal interleaving, independent symbol errors) -> compare with CCSDS 130.1-G-3 (~5.5 dB
     gain for conv alone, ~2 dB more with RS).
  6. Block interleaver: a burst of length <= depth hits each codeword at most once.
"""
import itertools
import numpy as np
from scipy import special, optimize, stats

rng = np.random.default_rng(7)
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.5g}, expected {want:.5g} (tol {tol}{' rel' if rel else ''})")


def Q(x):
    return 0.5 * special.erfc(np.asarray(x) / np.sqrt(2))


def db2lin(x):
    return 10 ** (np.asarray(x) / 10)

# ------------------------------------------------------------------------------------------
# 1. Convolutional code K=7 (171,133)
# ------------------------------------------------------------------------------------------
K = 7
G = (0o171, 0o133)
NS = 1 << (K - 1)                      # 64 states; state = last 6 input bits, newest in MSB


def parity(x):
    return bin(x).count("1") & 1


# register = (input << 6) | state ; generator taps apply to the 7-bit register with the
# newest bit as MSB (octal 171 = 1111001: taps on newest and ... oldest)
out_bits = np.zeros((NS, 2, 2), dtype=int)   # [state, input] -> (c1, c2)
next_state = np.zeros((NS, 2), dtype=int)
for s in range(NS):
    for u in (0, 1):
        reg = (u << (K - 1)) | s
        out_bits[s, u] = [parity(reg & G[0]), parity(reg & G[1])]
        next_state[s, u] = reg >> 1


def encode(bits):
    s = 0
    out = np.empty(2 * len(bits), dtype=int)
    for i, u in enumerate(bits):
        out[2 * i:2 * i + 2] = out_bits[s, u]
        s = next_state[s, u]
    return out


# Distance spectrum by DP over paths that leave state 0 and first return to it.
DMAX = 18
# spec[d] = sum over error events of weight d of their information weight
spec = np.zeros(DMAX + 1)
nev = np.zeros(DMAX + 1)
# frontier: dict (state) -> array over output weight of [count, info weight sum]
s1 = next_state[0, 1]
w1 = out_bits[0, 1].sum()
front = {s1: {w1: (1, 1)}}
for step in range(200):
    new = {}
    for s, dd in front.items():
        for u in (0, 1):
            ns = next_state[s, u]
            w = out_bits[s, u].sum()
            for d, (cnt, iw) in dd.items():
                nd = d + w
                if nd > DMAX:
                    continue
                if ns == 0:
                    nev[nd] += cnt
                    spec[nd] += iw + cnt * u
                else:
                    cur = new.setdefault(ns, {}).get(nd, (0, 0))
                    new[ns][nd] = (cur[0] + cnt, cur[1] + iw + cnt * u)
    front = new
    if not front:
        break
dfree = int(np.nonzero(nev)[0][0])
check("K=7 (171,133) free distance", dfree, 10, 0)
for d, want in ((10, 36), (12, 211), (14, 1404), (16, 11633)):
    check(f"information weight B_{d}", spec[d], want, 0)
print("  (A_d number of error events:", {d: int(nev[d]) for d in range(10, 19) if nev[d]}, ")")

R = 0.5


def pb_soft_bound(g):
    return sum(spec[d] * Q(np.sqrt(2 * d * R * g)) for d in range(dfree, DMAX + 1) if spec[d])


def pd_hard(d, p):
    # probability that d-weight path beats the correct one with BSC crossover p
    if d % 2:
        return sum(special.comb(d, e) * p ** e * (1 - p) ** (d - e) for e in range((d + 1) // 2, d + 1))
    return 0.5 * special.comb(d, d // 2) * p ** (d // 2) * (1 - p) ** (d // 2) + \
        sum(special.comb(d, e) * p ** e * (1 - p) ** (d - e) for e in range(d // 2 + 1, d + 1))


def pb_hard_bound(g):
    p = Q(np.sqrt(2 * R * g))
    return sum(spec[d] * pd_hard(d, p) for d in range(dfree, DMAX + 1) if spec[d])


def req(f, t=1e-5, lo=0.5, hi=12):
    return optimize.brentq(lambda x: np.log(f(db2lin(x))) - np.log(t), lo, hi)


soft_1e5 = req(pb_soft_bound)
hard_1e5 = req(pb_hard_bound)
print(f"  union bound, soft decision: Eb/N0 @1e-5 = {soft_1e5:.2f} dB; @1e-6 = {req(pb_soft_bound, 1e-6):.2f} dB")
print(f"  union bound, hard decision: Eb/N0 @1e-5 = {hard_1e5:.2f} dB")
print(f"  soft-vs-hard advantage at 1e-5: {hard_1e5 - soft_1e5:.2f} dB (CCSDS 130.1-G-3: hard loses > 2 dB)")
check("soft union bound Eb/N0 @1e-5 ~ 4.2 dB", soft_1e5, 4.2, 0.25)
check("hard-vs-soft penalty ~ 2 dB", hard_1e5 - soft_1e5, 2.0, 0.5)
check("coding gain vs uncoded BPSK (9.59 dB) ~ CCSDS 5.5 dB", 9.59 - soft_1e5, 5.5, 0.35)

# ------------------------------------------------------------------------------------------
# 3. Monte-Carlo Viterbi
# ------------------------------------------------------------------------------------------
# precompute branch outputs as +-1 for metric: bit 0 -> +1, bit 1 -> -1
prev_state = np.zeros((NS, 2), dtype=int)   # for each next state, the two predecessor states
prev_input = np.zeros((NS, 2), dtype=int)
cnt = np.zeros(NS, dtype=int)
for s in range(NS):
    for u in (0, 1):
        ns = next_state[s, u]
        prev_state[ns, cnt[ns]] = s
        prev_input[ns, cnt[ns]] = u
        cnt[ns] += 1
assert (cnt == 2).all()
bo = 1 - 2 * out_bits                      # (NS, 2 inputs, 2 bits) in +-1
brc1 = bo[prev_state, prev_input, 0]         # (NS, 2)
brc2 = bo[prev_state, prev_input, 1]


def viterbi(y):
    """y: received soft values (length 2N), larger positive = bit 0. Max correlation metric."""
    N = len(y) // 2
    y1 = y[0::2]
    y2 = y[1::2]
    metric = np.full(NS, -1e18)
    metric[0] = 0.0
    dec = np.empty((N, NS), dtype=np.uint8)
    for i in range(N):
        cand = metric[prev_state] + brc1 * y1[i] + brc2 * y2[i]     # (NS, 2)
        ch = np.argmax(cand, axis=1)
        dec[i] = ch
        metric = cand[np.arange(NS), ch]
    # traceback from best state (terminated code -> state 0)
    s = 0
    bits = np.empty(N, dtype=int)
    for i in range(N - 1, -1, -1):
        c = dec[i, s]
        bits[i] = prev_input[s, c]
        s = prev_state[s, c]
    return bits


def sim_conv(ebn0_db, nbits, hard=False):
    g = db2lin(ebn0_db)
    u = rng.integers(0, 2, nbits)
    u[-(K - 1):] = 0                                   # tail bits to terminate
    c = encode(u)
    x = 1 - 2.0 * c
    es_n0 = R * g
    y = x + rng.standard_normal(len(x)) / np.sqrt(2 * es_n0)
    if hard:
        y = np.sign(y)
    d = viterbi(y)
    return np.mean(d[:-(K - 1)] != u[:-(K - 1)])


mc_soft = {}
for eb, hard, nb in ((3.0, False, 600_000), (4.0, False, 3_000_000), (5.0, True, 600_000)):
    p = sim_conv(eb, nb, hard)
    if not hard:
        mc_soft[eb] = p
    bound = pb_hard_bound(db2lin(eb)) if hard else pb_soft_bound(db2lin(eb))
    print(f"  MC Viterbi {'hard' if hard else 'soft'} @ {eb} dB: BER = {p:.2e}  (union bound {bound:.2e}, {nb:.0e} bits)")
    # union bound is an upper bound; at these BERs the true BER is within a factor ~1-5 below it
    ok = (p <= bound * 1.3) and (p >= bound / 8)
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] MC within [bound/8, 1.3*bound]")

# ------------------------------------------------------------------------------------------
# 4. Hamming codes and LoRa coding rates
# ------------------------------------------------------------------------------------------
Gh = np.array([[1, 0, 0, 0, 1, 1, 0],
               [0, 1, 0, 0, 1, 0, 1],
               [0, 0, 1, 0, 0, 1, 1],
               [0, 0, 0, 1, 1, 1, 1]])


def dmin(Gm):
    k = Gm.shape[0]
    return min(int((np.array(m) @ Gm % 2).sum()) for m in itertools.product((0, 1), repeat=k) if any(m))


check("Hamming(7,4) d_min", dmin(Gh), 3, 0)
Ge = np.hstack([Gh, (Gh.sum(1) % 2)[:, None]])
check("extended Hamming(8,4) d_min", dmin(Ge), 4, 0)
# LoRa CR 4/5: single parity bit
G5 = np.hstack([np.eye(4, dtype=int), np.ones((4, 1), dtype=int)])
check("CR4/5 (parity) d_min", dmin(G5), 2, 0)
# best possible (6,4) binary linear code: exhaustive search over 2 parity columns
best = max(dmin(np.hstack([np.eye(4, dtype=int), np.array(P).reshape(4, 2)]))
           for P in itertools.product((0, 1), repeat=8))
check("best (6,4) binary code d_min (so CR4/6 can only detect)", best, 2, 0)
# syndrome decoding corrects every single error of Hamming(7,4)
H = np.hstack([Gh[:, 4:].T, np.eye(3, dtype=int)])
synd = {tuple(H[:, i]): i for i in range(7)}
good = True
for m in itertools.product((0, 1), repeat=4):
    c = np.array(m) @ Gh % 2
    for e in range(7):
        r = c.copy()
        r[e] ^= 1
        s = tuple(H @ r % 2)
        r[synd[s]] ^= 1
        good &= (r == c).all()
check("Hamming(7,4) corrects all 7x16 single errors", float(good), 1.0, 0)

# ------------------------------------------------------------------------------------------
# 5. Reed-Solomon (255,223), t = 16, 8-bit symbols, hard-decision BPSK
# ------------------------------------------------------------------------------------------
n, k_rs, t = 255, 223, 16


def rs_ber_from_symbol_error(ps):
    i = np.arange(t + 1, n + 1)
    # standard approximation: decoded symbol error ~ sum i/n C(n,i) ps^i (1-ps)^(n-i)
    logc = special.gammaln(n + 1) - special.gammaln(i + 1) - special.gammaln(n - i + 1)
    pse = np.sum(i / n * np.exp(logc + i * np.log(ps) + (n - i) * np.log1p(-ps)))
    return pse * (2 ** 7) / (2 ** 8 - 1)          # symbol->bit conversion for random symbol errors


def rs_alone(g):
    rate = k_rs / n
    pb_ch = Q(np.sqrt(2 * rate * g))
    ps = 1 - (1 - pb_ch) ** 8
    return rs_ber_from_symbol_error(ps)


rs_1e5 = optimize.brentq(lambda x: np.log(rs_alone(db2lin(x))) - np.log(1e-5), 3, 12)
print(f"  RS(255,223) alone, hard BPSK: Eb/N0 @1e-5 = {rs_1e5:.2f} dB (gain {9.59 - rs_1e5:.2f} dB)")

# Concatenated RS(255,223) outer + K=7 soft Viterbi inner, ideal interleaving.
# Measure the Viterbi output *byte* error rate by simulation (captures burst clustering inside a
# byte), then treat byte errors as independent across RS symbols (ideal interleaving).
inner_db = np.array([1.2, 1.5, 1.8, 2.1])
byte_err = []
for eb in inner_db:
    g = db2lin(eb)
    nbits = 1_600_000
    u = rng.integers(0, 2, nbits)
    u[-(K - 1):] = 0
    x = 1 - 2.0 * encode(u)
    y = x + rng.standard_normal(len(x)) / np.sqrt(2 * R * g)
    d = viterbi(y)
    e = (d[:nbits - 8] != u[:nbits - 8]).reshape(-1, 8).any(axis=1)
    byte_err.append(e.mean())
byte_err = np.array(byte_err)
post = np.array([rs_ber_from_symbol_error(ps) for ps in byte_err])
for eb, ps, pb in zip(inner_db, byte_err, post):
    print(f"  inner Eb/N0 {eb:.1f} dB (overall {eb + 10*np.log10(n/k_rs):.2f} dB): Viterbi byte err {ps:.2e} -> RS decoded BER {pb:.1e}")
f_interp = np.interp(np.log(1e-5), np.log(post[::-1]), inner_db[::-1])
cc_1e5 = f_interp + 10 * np.log10(n / k_rs)
print(f"  concatenated: Eb/N0 @1e-5 = {cc_1e5:.2f} dB -> extra gain over conv alone (bound {soft_1e5:.2f} dB) = {soft_1e5 - cc_1e5:.2f} dB (CCSDS ~2.0 dB)")
check("concatenated extra gain ~2 dB (CCSDS 130.1-G-3)", soft_1e5 - cc_1e5, 2.0, 0.5)

# ------------------------------------------------------------------------------------------
# 6. Block interleaver
# ------------------------------------------------------------------------------------------
depth, ncw, cwlen = 8, 8, 32         # 8 codewords of 32 symbols written as rows, read by columns
idx = np.arange(ncw * cwlen).reshape(ncw, cwlen)   # row r = codeword r
tx_order = idx.T.flatten()                          # read column-wise
worst = 0
for start in range(len(tx_order) - depth + 1):
    hit = tx_order[start:start + depth] // cwlen
    worst = max(worst, np.bincount(hit, minlength=ncw).max())
check("burst of length = depth hits each codeword at most once", worst, 1, 0)

# ------------------------------------------------------------------------------------------
# 7. Small block codes with hard decisions: Hamming(7,4) and Golay(23,12) coding gain at 1e-5
# ------------------------------------------------------------------------------------------
def post_ber_block(n, k, t, g):
    p = Q(np.sqrt(2 * k / n * g))
    return sum((i + (t if i < n else 0)) / n * special.comb(n, i) * p ** i * (1 - p) ** (n - i)
               for i in range(t + 1, n + 1))


for nm, n_, k_, t_, want in (("Hamming(7,4)", 7, 4, 1, 0.4), ("Golay(23,12)", 23, 12, 3, 2.3)):
    x = optimize.brentq(lambda x: np.log(post_ber_block(n_, k_, t_, db2lin(x))) - np.log(1e-5), 3, 15)
    print(f"  {nm} hard decision: Eb/N0 @1e-5 = {x:.2f} dB, gain {9.59 - x:.2f} dB")
    check(f"{nm} hard-decision coding gain @1e-5 [dB]", 9.59 - x, want, 0.2)
check("K=7 r=1/2 asymptotic soft coding gain 10log(R dfree) [dB]", 10 * np.log10(R * dfree), 6.99, 0.01)
check("RS(255,223) guaranteed burst correction [bits] = 8(t-1)+1", 8 * (t - 1) + 1, 121, 0)

print("\nOVERALL:", "PASS" if ok_all else "FAIL")
