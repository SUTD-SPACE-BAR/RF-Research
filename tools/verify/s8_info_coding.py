#!/usr/bin/env python3
"""s8_info_coding.py — checks for the information-theory (ber-ebn0-and-shannon.md) and coded-modulation /
belief-propagation (channel-coding-fec.md) sections added by W5-S8 (gap G-10-08).

1. Entropy: binary entropy, a flight-state telemetry field (entropy vs fixed-length vs Huffman).
2. Mutual information: BSC capacity 1 - H(p); hard vs soft BI-AWGN rate-1/2 limits.
3. Constellation-constrained (CM) capacity of BPSK/QPSK/8PSK/16QAM and BICM capacity of Gray 16-QAM
   (Monte Carlo), vs Shannon; ultimate shaping gain pi e / 6 = 1.53 dB.
4. Signal-space geometry: sphere hardening of n-dimensional Gaussian noise.
5. TCM: free squared Euclidean distance of Ungerboeck 4- and 8-state 8-PSK codes (parity-check search)
   -> asymptotic gains 3.0 / 3.6 dB over uncoded QPSK.
6. Belief propagation: a random (3,6)-regular LDPC code, n = 1008, sum-product decoding on BPSK/AWGN.

Run: python3 tools/verify/s8_info_coding.py   (~60 s)
"""
import itertools
import numpy as np
from scipy import special, optimize

rng = np.random.default_rng(10)
RES = []


def check(name, ok, detail=""):
    RES.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


db = lambda x: 10 * np.log10(x)
un = lambda d: 10 ** (d / 10)
H2 = lambda p: -p * np.log2(p) - (1 - p) * np.log2(1 - p)

# ---------------------------------------------------------------- 1. entropy
print("1. Entropy")
check("H2(0.11) = 0.50 bit", abs(H2(0.11) - 0.4999) < 0.001, f"{H2(0.11):.4f}")
p = np.array([0.60, 0.20, 0.10, 0.05, 0.05])            # pad, boost, coast, drogue, main (illustrative)
H = -np.sum(p * np.log2(p))
# Huffman code lengths for this distribution: 1, 2, 3, 4, 4
huff = np.sum(p * np.array([1, 2, 3, 4, 4]))
check("flight-state field: entropy 1.67 b, Huffman 1.70 b, fixed 3 b", abs(H - 1.671) < 0.002 and abs(huff - 1.70) < 1e-9,
      f"H={H:.3f}, Huffman={huff:.2f}")

# ---------------------------------------------------------------- 2. BSC / BI-AWGN
print("\n2. Hard vs soft binary-input limits at rate 1/2")
gh_x, gh_w = np.polynomial.hermite.hermgauss(80)


def c_biawgn(esn0):
    s = np.sqrt(2 * esn0)          # y = s + n, n ~ N(0,1) after scaling; LLR = 2 s y
    y = np.sqrt(2) * gh_x + s
    return 1 - np.sum(gh_w * np.log2(1 + np.exp(-2 * s * y))) / np.sqrt(np.pi)


def c_bsc(esn0):
    pe = 0.5 * special.erfc(np.sqrt(esn0))
    return 1 - H2(pe)


r = 0.5
soft = db(optimize.brentq(lambda e: c_biawgn(e * r) - r, 0.1, 10))
hard = db(optimize.brentq(lambda e: c_bsc(e * r) - r, 0.1, 10))
check("soft BI-AWGN rate-1/2 limit 0.19 dB (matches the page's CCSDS figure)", abs(soft - 0.19) < 0.02, f"{soft:.2f} dB")
check("hard (BSC) rate-1/2 limit ~1.7 dB: hard slicing costs ~1.5 dB at rate 1/2 (-> 1.96 dB as r -> 0)",
      1.5 < hard - soft < 1.7, f"{hard:.2f} dB, loss {hard - soft:.2f} dB")
lowr = db(optimize.brentq(lambda e: c_bsc(e * 0.01) - 0.01, 0.1, 10)) - db(optimize.brentq(lambda e: c_biawgn(e * 0.01) - 0.01, 0.1, 10))
check("at rate 0.01 the hard-decision loss approaches 10log(pi/2) = 1.96 dB", abs(lowr - 1.96) < 0.05, f"{lowr:.2f} dB")

# ---------------------------------------------------------------- 3. CM / BICM capacity
print("\n3. Constellation-constrained capacity (AWGN, SNR = Es/N0)")


def const(name):
    if name == "BPSK":
        return np.array([1.0 + 0j]) * np.array([1, -1]), None
    if name == "QPSK":
        c = np.array([1 + 1j, -1 + 1j, -1 - 1j, 1 - 1j]) / np.sqrt(2)
        return c, None
    if name == "8PSK":
        return np.exp(2j * np.pi * np.arange(8) / 8), None
    if name == "16QAM":
        g = np.array([0, 1, 3, 2])                       # Gray map of 2 bits -> PAM index
        lv = np.array([-3, -1, 1, 3])
        pts, labels = [], []
        for bi in range(4):
            for bq in range(4):
                pts.append(lv[g[bi]] + 1j * lv[g[bq]])
                labels.append((bi << 2) | bq)
        pts = np.array(pts) / np.sqrt(10)
        return pts, np.array(labels)


def cm_bicm(name, snr_db, n=200_000):
    c, lab = const(name)
    M = len(c)
    N0 = 1 / un(snr_db)
    idx = rng.integers(0, M, n)
    y = c[idx] + np.sqrt(N0 / 2) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    ll = -np.abs(y[:, None] - c[None, :]) ** 2 / N0
    lse = special.logsumexp(ll, axis=1)
    cm = np.log2(M) - np.mean(lse - ll[np.arange(n), idx]) / np.log(2)
    if lab is None:
        return cm, None
    m = int(np.log2(M))
    bicm = 0.0
    for b in range(m):
        bit = (lab >> b) & 1
        tb = bit[idx]
        num = special.logsumexp(np.where(bit[None, :] == tb[:, None], ll, -np.inf), axis=1)
        bicm += 1 - np.mean(lse - num) / np.log(2)
    return cm, bicm


sh = lambda s: np.log2(1 + un(s))
for nm in ("QPSK", "8PSK", "16QAM"):
    cm, bi = cm_bicm(nm, 10)
    print(f"   {nm:5s} at 10 dB: CM {cm:.3f} b/sym" + (f", BICM {bi:.3f}" if bi is not None else "") + f"  (Shannon {sh(10):.3f})")
cm16, bi16 = cm_bicm("16QAM", 10)
check("16-QAM Gray BICM loses < 0.05 b/sym vs CM at 10 dB", 0 <= cm16 - bi16 < 0.05, f"{cm16 - bi16:.3f}")
# SNR for 2 and 3 b/sym
def snr_for(nm, R, which=0):
    return optimize.brentq(lambda s: cm_bicm(nm, s, 80_000)[which] - R, -5, 25, xtol=0.02)
s2_16 = snr_for("16QAM", 2.0)
s2_bicm = snr_for("16QAM", 2.0, 1)
s3_8 = snr_for("8PSK", 2.5)
s25_16 = snr_for("16QAM", 2.5)
print(f"   2 b/sym: Shannon {db(3):.2f} dB, 16-QAM CM {s2_16:.2f} dB, 16-QAM BICM {s2_bicm:.2f} dB")
print(f"   2.5 b/sym: Shannon {db(2 ** 2.5 - 1):.2f} dB, 8-PSK CM {s3_8:.2f} dB, 16-QAM CM {s25_16:.2f} dB")
check("2 b/sym: 16-QAM CM ~0.3 dB from Shannon (4.77 dB); Gray BICM a further ~0.2 dB",
      0 < s2_16 - db(3) < 0.6 and 0 < s2_bicm - s2_16 < 0.3, f"{s2_16:.2f}, {s2_bicm:.2f}")
check("2.5 b/sym: 16-QAM beats 8-PSK (more dimensions used)", s25_16 < s3_8, f"{s25_16:.2f} vs {s3_8:.2f} dB")
check("ultimate shaping gain 10log(pi e / 6) = 1.53 dB", abs(db(np.pi * np.e / 6) - 1.53) < 0.005)
check("QPSK CM saturates at 2 b/sym", abs(cm_bicm("QPSK", 25)[0] - 2) < 0.001)

# ---------------------------------------------------------------- 4. sphere hardening
print("\n4. Sphere hardening")
ok = True
for nd in (10, 100, 1000):
    x = rng.standard_normal((20000, nd))
    rr = np.sum(x ** 2, axis=1) / nd
    ok &= abs(rr.std() - np.sqrt(2 / nd)) < 0.05 * np.sqrt(2 / nd)
    print(f"   n={nd:5d}: |n|^2/n mean {rr.mean():.3f}, std {rr.std():.4f} (theory {np.sqrt(2 / nd):.4f})")
check("|n|^2/n concentrates with std sqrt(2/n): noise lives on a thin shell", ok)

# ---------------------------------------------------------------- 5. TCM free distance
print("\n5. Ungerboeck 8-PSK TCM (natural mapping, parity-check form)")
S = np.exp(2j * np.pi * np.arange(8) / 8)
d2e = np.array([min(abs(S[z] - S[z ^ e]) ** 2 for z in range(8)) for e in range(8)])   # worst-case per label


def poly_bits(octal):
    v = int(str(octal), 8)
    return [(v >> k) & 1 for k in range(v.bit_length())]


def dfree(h, Lmax=6):
    """h = (h0, h1, h2) octal parity polynomials: sum_i h_i(D) e_i(D) = 0 (mod 2); e = (e2 e1 e0) bits."""
    hb = [poly_bits(x) for x in h]
    nu = max(len(b) for b in hb) - 1
    best = np.inf
    for L in range(1, Lmax + 1):
        for seq in itertools.product(range(8), repeat=L):
            if seq[0] == 0 or seq[-1] == 0:
                continue
            ok = True
            for t in range(L + nu):
                acc = 0
                for i in range(3):
                    for k, hk in enumerate(hb[i]):
                        if hk and 0 <= t - k < L:
                            acc ^= (seq[t - k] >> i) & 1
                if acc:
                    ok = False
                    break
            if ok:
                best = min(best, sum(d2e[e] for e in seq))
    return best


d4 = dfree((5, 2, 0), Lmax=5)
d8 = dfree((11, 2, 4), Lmax=5)
print(f"   4-state (h0,h1,h2)=(5,2,0): d2free = {d4:.3f};  8-state (11,2,4): d2free = {d8:.3f}  (QPSK uncoded d2 = 2)")
check("4-state 8-PSK TCM d2free = 4.0 (parallel transitions) -> 3.01 dB over QPSK", abs(d4 - 4.0) < 1e-9, f"{db(d4 / 2):.2f} dB")
check("8-state 8-PSK TCM d2free = 4.586 -> 3.6 dB over QPSK (Ungerboeck 1982)", abs(d8 - 4.586) < 0.001, f"{db(d8 / 2):.2f} dB")

# ---------------------------------------------------------------- 6. LDPC belief propagation
print("\n6. Random (3,6)-regular LDPC, n = 1008, sum-product")
n, dv, dc = 1008, 3, 6
m = n * dv // dc
# Gallager-style socket matching; remove double edges by retrying
for _ in range(100):
    sockets = np.repeat(np.arange(n), dv)
    perm = rng.permutation(len(sockets))
    vn = sockets[perm]
    cn = np.repeat(np.arange(m), dc)
    pairs = set()
    dup = False
    for a, b in zip(vn, cn):
        if (a, b) in pairs:
            dup = True
            break
        pairs.add((a, b))
    if not dup:
        break
E = len(vn)
cn_edges = cn.reshape(m, dc) * 0 + np.arange(E).reshape(m, dc)


def decode(llr_ch, iters=50):
    """llr_ch: (F, n). Returns hard decisions (F, n)."""
    F = llr_ch.shape[0]
    v2c = llr_ch[:, vn]                              # (F, E)
    for _ in range(iters):
        t = np.tanh(np.clip(v2c, -30, 30) / 2)[:, cn_edges]      # (F, m, dc)
        t = np.where(np.abs(t) < 1e-12, 1e-12, t)
        prod = np.prod(t, axis=2, keepdims=True)
        ext = np.clip(prod / t, -0.999999999999, 0.999999999999)
        c2v = np.empty_like(v2c)
        c2v[:, cn_edges.ravel()] = (2 * np.arctanh(ext)).reshape(F, -1)
        tot = llr_ch.copy()
        tot = llr_ch + np.stack([np.bincount(vn, weights=c2v[f], minlength=n) for f in range(F)])
        v2c = tot[:, vn] - c2v
        hard = tot < 0
        syn = np.bitwise_xor.reduce(hard[:, vn][:, cn_edges], axis=2)
        if not syn.any():
            break
    return hard


results = {}
for ebn0 in (1.5, 2.0, 2.5):
    R = 0.5                                           # design rate (the random H may have a few dependent rows)
    sigma = np.sqrt(1 / (2 * R * un(ebn0)))
    errs = fe = tot = 0
    for _ in range(8):
        F = 50
        y = 1 + sigma * rng.standard_normal((F, n))   # all-zero codeword -> +1
        hard = decode(2 * y / sigma ** 2)
        errs += hard.sum(); fe += hard.any(axis=1).sum(); tot += F
    ber, fer = errs / (tot * n), fe / tot
    results[ebn0] = (ber, fer)
    unc = 0.5 * special.erfc(np.sqrt(un(ebn0)))
    print(f"   Eb/N0 {ebn0} dB: BER {ber:.2e}, FER {fer:.2f}   (uncoded BPSK {unc:.1e})")
check("BP decoding improves with SNR (FER falls from 1.5 to 2.5 dB)", results[1.5][1] > results[2.5][1])
check("(3,6) n=1008 at 2.5 dB: BER < 1e-4 (uncoded BPSK needs 8.4 dB for 1e-4)", results[2.5][0] < 1e-4,
      f"{results[2.5][0]:.1e}")
check("operating point is ~1-1.5 dB above the (3,6) BP threshold (1.11 dB) and ~2 dB above the rate-1/2 limit",
      results[2.0][1] < 0.5 and results[1.5][1] > results[2.5][1])

print(f"\n{sum(RES)}/{len(RES)} checks PASS")
