#!/usr/bin/env python3
"""Verification for kb/10-comms-modulation/ber-ebn0-and-shannon.md (and digital-modulation page).

Run:  python3 tools/verify/comms_ber_awgn.py      (about 20-40 s)

What it checks (prints PASS/FAIL for each):
  1. Closed-form AWGN BER formulas vs Monte-Carlo simulation (complex baseband, noise N0/2 per
     real dimension) for BPSK, QPSK (Gray), 8-PSK (Gray), 16-QAM and 64-QAM (Gray), coherent
     orthogonal BFSK, non-coherent BFSK, DBPSK (differentially coherent), non-coherent 8-FSK,
     and coherent OOK.
  2. Required Eb/N0 for BER = 1e-3, 1e-5, 1e-6 (table printed; spot values asserted).
  3. Shannon limits: Eb/N0_min(eta) = (2^eta - 1)/eta, the -1.59 dB ultimate limit,
     and binary-input AWGN (BI-AWGN) capacity limits for code rates 1/2, 1/3, 1/4, 1/6
     (compared with CCSDS 130.1-G-3: 0.2, -0.5, -0.8, -1.1 dB).
  4. Unit conversions Eb/N0 <-> Es/N0 <-> SNR <-> C/N0 for a worked example.
All formulas are derived in the KB page; nothing is copied from a table.
"""
import numpy as np
from scipy import special, optimize, integrate

rng = np.random.default_rng(12345)
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


def lin2db(x):
    return 10 * np.log10(x)

# ---------------------------------------------------------------------------------------------
# Closed-form bit error probabilities (g = Eb/N0 linear)
# ---------------------------------------------------------------------------------------------

def pb_bpsk(g):
    return Q(np.sqrt(2 * g))


def pb_qpsk(g):  # Gray-coded QPSK = two independent BPSK rails
    return Q(np.sqrt(2 * g))


def ps_mpsk_exact(M, es):
    """Exact symbol error probability of M-PSK (Craig's form)."""
    def f(e):
        return integrate.quad(lambda th: np.exp(-e * np.sin(np.pi / M) ** 2 / np.sin(th) ** 2),
                              0, (M - 1) * np.pi / M)[0] / np.pi
    return np.vectorize(f)(es)


def pb_mpsk_gray_approx(M, g):
    k = np.log2(M)
    return 2 / k * Q(np.sqrt(2 * k * g) * np.sin(np.pi / M))


def pb_mqam_gray_approx(M, g):
    """Square M-QAM, Gray, nearest-neighbour approximation (tight at BER < 1e-2)."""
    k = np.log2(M)
    return 4 / k * (1 - 1 / np.sqrt(M)) * Q(np.sqrt(3 * k * g / (M - 1)))


def pb_bfsk_coherent(g):
    return Q(np.sqrt(g))


def pb_bfsk_noncoherent(g):
    return 0.5 * np.exp(-g / 2)


def pb_dbpsk(g):
    return 0.5 * np.exp(-g)


def ps_mfsk_noncoherent(M, es):
    """Symbol error prob. of non-coherent orthogonal M-FSK, by numerical integration.

    Normalise N0 = 1 (complex noise variance 1 per correlator). Signal-branch envelope r is
    Rician: p(r) = 2 r exp(-(r^2 + Es)) I0(2 r sqrt(Es)); each of the M-1 noise branches is
    Rayleigh with CDF 1 - exp(-r^2). Pc = int p(r) (1 - exp(-r^2))^(M-1) dr.
    (The textbook alternating binomial sum is equivalent but cancels catastrophically for M > ~30.)
    """
    es = np.atleast_1d(es).astype(float)
    out = []
    for e in es:
        a = np.sqrt(e)
        f = lambda r: 2 * r * np.exp(-(r - a) ** 2) * special.i0e(2 * r * a) * \
            np.exp((M - 1) * np.log1p(-np.exp(-r * r) + 1e-300))
        pc = integrate.quad(f, 0, a + 12, limit=400, points=[a])[0]
        out.append(max(1 - pc, 1e-300))
    return np.array(out)


def pb_mfsk_noncoherent(M, g):
    k = np.log2(M)
    return M / 2 / (M - 1) * ps_mfsk_noncoherent(M, k * g)


def pb_ook_coherent(g):  # g = average Eb/N0 (on-symbol energy 2Eb, off 0)
    return Q(np.sqrt(g))

# ---------------------------------------------------------------------------------------------
# Monte-Carlo simulators (complex baseband, one sample per symbol after an ideal matched filter)
# ---------------------------------------------------------------------------------------------

def awgn(n, n0):
    return np.sqrt(n0 / 2) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))


def gray(n):
    return n ^ (n >> 1)


def sim_psk(M, ebn0_db, nsym):
    k = int(np.log2(M))
    g = db2lin(ebn0_db)
    es = 1.0
    n0 = es / (k * g)
    idx = rng.integers(0, M, nsym)                      # symbol index = Gray code of phase index
    phase_idx = np.empty(M, int)
    phase_idx[gray(np.arange(M))] = np.arange(M)        # label -> phase position
    s = np.exp(2j * np.pi * phase_idx[idx] / M)
    r = s + awgn(nsym, n0)
    ph = np.round(np.angle(r) / (2 * np.pi / M)).astype(int) % M
    lab = gray(ph)
    diff = lab ^ idx
    bit_err = sum(((diff >> b) & 1).sum() for b in range(k))
    return bit_err / (nsym * k)


def pam_gray_levels(L):
    # positions 0..L-1 -> amplitudes; labels Gray
    return 2 * np.arange(L) - (L - 1)


def sim_qam(M, ebn0_db, nsym):
    L = int(np.sqrt(M))
    kh = int(np.log2(L))
    k = 2 * kh
    g = db2lin(ebn0_db)
    lev = pam_gray_levels(L).astype(float)
    es = 2 * np.mean(lev ** 2)
    n0 = es / (k * g)
    pi_ = rng.integers(0, L, nsym)
    pq = rng.integers(0, L, nsym)
    r = lev[pi_] + 1j * lev[pq] + awgn(nsym, n0)
    di = np.clip(np.round((r.real + (L - 1)) / 2), 0, L - 1).astype(int)
    dq = np.clip(np.round((r.imag + (L - 1)) / 2), 0, L - 1).astype(int)
    e = 0
    for a, b in ((pi_, di), (pq, dq)):
        diff = gray(a) ^ gray(b)
        e += sum(((diff >> j) & 1).sum() for j in range(kh))
    return e / (nsym * k)


def sim_fsk_coherent(ebn0_db, nbits):
    g = db2lin(ebn0_db)
    n0 = 1.0 / g                                        # Eb = 1
    b = rng.integers(0, 2, nbits)
    # orthogonal basis: correlator outputs (real) for tone 0 and tone 1
    z0 = (b == 0) * 1.0 + np.sqrt(n0 / 2) * rng.standard_normal(nbits)
    z1 = (b == 1) * 1.0 + np.sqrt(n0 / 2) * rng.standard_normal(nbits)
    return np.mean((z1 > z0).astype(int) != b)


def sim_mfsk_noncoherent(M, ebn0_db, nsym):
    k = int(np.log2(M))
    g = db2lin(ebn0_db)
    es = 1.0
    n0 = es / (k * g)
    idx = rng.integers(0, M, nsym)
    z = awgn(nsym * M, n0).reshape(nsym, M)
    z[np.arange(nsym), idx] += np.sqrt(es) * np.exp(2j * np.pi * rng.random(nsym))  # unknown phase
    dec = np.argmax(np.abs(z), axis=1)
    diff = idx ^ dec
    return sum(((diff >> j) & 1).sum() for j in range(k)) / (nsym * k)


def sim_dbpsk(ebn0_db, nbits):
    g = db2lin(ebn0_db)
    n0 = 1.0 / g
    b = rng.integers(0, 2, nbits)
    d = np.cumsum(b) % 2                                  # differential encoding
    s = np.concatenate(([1.0], 1 - 2.0 * d)) * np.exp(1j * rng.random() * 2 * np.pi)  # unknown fixed phase
    r = s + awgn(nbits + 1, n0)
    dec = (np.real(r[1:] * np.conj(r[:-1])) < 0).astype(int)
    return np.mean(dec != b)


def sim_ook_coherent(ebn0_db, nbits):
    g = db2lin(ebn0_db)
    A = np.sqrt(2.0)                                     # on-energy 2, off 0 -> average Eb = 1
    n0 = 1.0 / g
    b = rng.integers(0, 2, nbits)
    r = A * b + np.sqrt(n0 / 2) * rng.standard_normal(nbits)
    return np.mean((r > A / 2).astype(int) != b)


def mc_compare(name, sim, theory, ebn0_db, n, tol_rel=0.12):
    p_sim = sim(ebn0_db, n)
    p_th = theory(db2lin(ebn0_db))
    check(f"{name} @ Eb/N0={ebn0_db} dB  (MC {n:.0e})", p_sim, float(np.squeeze(p_th)), tol_rel, rel=True)


print("=== 1. Monte-Carlo vs theory ===")
mc_compare("BPSK", lambda e, n: sim_psk(2, e, n), pb_bpsk, 6.0, 2_000_000)
mc_compare("QPSK Gray", lambda e, n: sim_psk(4, e, n), pb_qpsk, 6.0, 1_000_000)
mc_compare("8-PSK Gray (approx)", lambda e, n: sim_psk(8, e, n), lambda g: pb_mpsk_gray_approx(8, g), 10.0, 1_000_000)
mc_compare("16-QAM Gray (approx)", lambda e, n: sim_qam(16, e, n), lambda g: pb_mqam_gray_approx(16, g), 10.0, 1_000_000)
mc_compare("64-QAM Gray (approx)", lambda e, n: sim_qam(64, e, n), lambda g: pb_mqam_gray_approx(64, g), 14.0, 1_000_000)
mc_compare("coherent BFSK", sim_fsk_coherent, pb_bfsk_coherent, 9.0, 2_000_000)
mc_compare("non-coherent BFSK", lambda e, n: sim_mfsk_noncoherent(2, e, n), pb_bfsk_noncoherent, 10.0, 2_000_000)
mc_compare("DBPSK", sim_dbpsk, pb_dbpsk, 7.0, 2_000_000)
mc_compare("non-coherent 8-FSK", lambda e, n: sim_mfsk_noncoherent(8, e, n), lambda g: pb_mfsk_noncoherent(8, g), 7.0, 600_000)
mc_compare("coherent OOK (avg Eb)", sim_ook_coherent, pb_ook_coherent, 9.0, 2_000_000)
# exact M-PSK symbol error vs MC symbol error for 8PSK
es_db = 14.0
p_ex = float(ps_mpsk_exact(8, db2lin(es_db)))
M = 8
nsym = 1_000_000
s = np.exp(2j * np.pi * rng.integers(0, M, nsym) / M)
r = s + awgn(nsym, 1 / db2lin(es_db))
ser = np.mean(np.round(np.angle(r / s) / (2 * np.pi / M)) != 0)
check("8-PSK exact SER (Craig) vs MC @ Es/N0=14 dB", ser, p_ex, 0.1, rel=True)

print("\n=== 2. Required Eb/N0 (dB) for target BER ===")
schemes = {
    "BPSK / QPSK (coherent, Gray)": pb_bpsk,
    "DBPSK (differential detection)": pb_dbpsk,
    "coherent BFSK (orthogonal)": pb_bfsk_coherent,
    "non-coherent BFSK": pb_bfsk_noncoherent,
    "coherent OOK (average Eb)": pb_ook_coherent,
    "8-PSK Gray": lambda g: pb_mpsk_gray_approx(8, g),
    "16-QAM Gray": lambda g: pb_mqam_gray_approx(16, g),
    "64-QAM Gray": lambda g: pb_mqam_gray_approx(64, g),
    "non-coherent 4-FSK": lambda g: pb_mfsk_noncoherent(4, g),
    "non-coherent 16-FSK": lambda g: pb_mfsk_noncoherent(16, g),
    "non-coherent 128-FSK": lambda g: pb_mfsk_noncoherent(128, g),
}


def req_ebn0(f, target):
    return optimize.brentq(lambda x: np.log(float(np.squeeze(f(db2lin(x))))) - np.log(target), -5, 40)


req = {}
print(f"{'scheme':34s} {'1e-3':>7s} {'1e-5':>7s} {'1e-6':>7s}")
for nm, f in schemes.items():
    vals = [req_ebn0(f, t) for t in (1e-3, 1e-5, 1e-6)]
    req[nm] = vals
    print(f"{nm:34s} {vals[0]:7.2f} {vals[1]:7.2f} {vals[2]:7.2f}")
check("BPSK Eb/N0 @1e-5 [dB]", req["BPSK / QPSK (coherent, Gray)"][1], 9.59, 0.02)
check("BPSK Eb/N0 @1e-6 [dB]", req["BPSK / QPSK (coherent, Gray)"][2], 10.53, 0.02)
check("DBPSK Eb/N0 @1e-5 [dB]", req["DBPSK (differential detection)"][1], 10.34, 0.02)
check("NC-BFSK Eb/N0 @1e-5 [dB]", req["non-coherent BFSK"][1], 13.35, 0.02)
check("coh BFSK Eb/N0 @1e-5 [dB]", req["coherent BFSK (orthogonal)"][1], 12.60, 0.02)

print("\n=== 3. Shannon limits ===")
for eta in (0.01, 0.5, 1, 2, 4, 6, 8):
    print(f"  eta = {eta:5.2f} b/s/Hz -> Eb/N0_min = {lin2db((2 ** eta - 1) / eta):6.2f} dB")
check("ultimate Shannon limit ln2 [dB]", lin2db(np.log(2)), -1.592, 0.001)
check("Eb/N0_min at eta=1 [dB]", lin2db(1.0), 0.0, 1e-9)
check("Eb/N0_min at eta=2 [dB]", lin2db(1.5), 1.761, 0.001)

# Binary-input AWGN capacity (bits per channel use) via Gauss-Hermite quadrature
gh_x, gh_w = np.polynomial.hermite.hermgauss(200)


def c_biawgn(es_n0):
    # x=+1 sent, y = 1 + n, n ~ N(0, s2) with s2 = N0/(2Es); LLR = 2y/s2
    s2 = 1 / (2 * es_n0)
    y = 1 + np.sqrt(2 * s2) * gh_x
    return 1 - np.sum(gh_w * np.logaddexp(0, -2 * y / s2)) / np.sqrt(np.pi) / np.log(2)


def ebn0_limit_biawgn(r):
    return optimize.brentq(lambda x: c_biawgn(r * db2lin(x)) - r, -1.59, 10)


for r, ccsds in ((1 / 2, 0.2), (1 / 3, -0.5), (1 / 4, -0.8), (1 / 6, -1.1)):
    lim = ebn0_limit_biawgn(r)
    check(f"BI-AWGN capacity limit rate {r:.3f} [dB] vs CCSDS 130.1-G-3", lim, ccsds, 0.06)
# Unconstrained (Gaussian-input) limit for rate r BPSK-like signalling: eta = 2r (real dim: C=0.5log2(1+2rEb/N0))
for r in (1 / 2, 1 / 3):
    lim = lin2db((2 ** (2 * r) - 1) / (2 * r))
    print(f"  Gaussian-input limit, rate {r:.3f} on one real dimension: {lim:.2f} dB")

print("\n=== 4. Conversion worked example (10 kbps link) ===")
Rb = 10e3
ebn0 = 9.59
cn0 = ebn0 + lin2db(Rb)
check("C/N0 for BPSK 1e-5 at 10 kbps [dB-Hz]", cn0, 49.59, 0.01)
nf = 6.0
sens = -173.98 + nf + cn0
check("sensitivity (NF 6 dB) [dBm]", sens, -118.39, 0.02)
# SNR in a noise bandwidth equal to 1.35 x symbol rate (RRC beta=0.35), BPSK
snr = ebn0 + lin2db(Rb / (1.35 * Rb))
check("SNR in B=1.35 Rs for BPSK [dB]", snr, 9.59 - 1.303, 0.01)
# QPSK: Es = 2Eb, Rs = Rb/2
check("QPSK Es/N0 = Eb/N0 + 3.01 dB", ebn0 + lin2db(2), 12.60, 0.01)

print("\n=== 5. Finite-blocklength penalty (Polyanskiy-Poor-Verdu normal approximation) ===")
# Real AWGN channel, Gaussian-like input: C = 0.5 log2(1+P), V = P(P+2)/(2(P+1)^2) (log2 e)^2
# log2 M* ~= n C - sqrt(n V) Qinv(eps) + 0.5 log2 n.  Rate 1/2: n = 2k.  Eb/N0 = P n / (2k).
from scipy.stats import norm


def ebn0_normal_approx(k, rate, eps):
    n = k / rate

    def f(P):
        C = 0.5 * np.log2(1 + P)
        V = P * (P + 2) / (2 * (P + 1) ** 2) * np.log2(np.e) ** 2
        return n * C - np.sqrt(n * V) * norm.isf(eps) + 0.5 * np.log2(n) - k
    P = optimize.brentq(f, 1e-4, 1e3)
    return lin2db(P * n / (2 * k))


vals = {}
for k in (64, 100, 256, 1000, 10000, 100000):
    vals[k] = ebn0_normal_approx(k, 0.5, 1e-4)
    print(f"  k = {k:6d} info bits, rate 1/2, WER 1e-4: Eb/N0 >= ~{vals[k]:.2f} dB (asymptote 0.00 dB)")
print(f"  penalty 100 -> 1000 bits: {vals[100]-vals[1000]:.2f} dB (CCSDS 130.1-G-3 quotes ~1.3 dB from sphere-packing bound)")
check("normal-approx gap 100 vs 1000 bits ~ CCSDS 1.3 dB", vals[100] - vals[1000], 1.3, 0.35)

print("\n=== 6. Flat Rayleigh fading (average Eb/N0), coherent BPSK and non-coherent BFSK ===")
def pb_bpsk_rayleigh(gb):
    return 0.5 * (1 - np.sqrt(gb / (1 + gb)))


def pb_ncfsk_rayleigh(gb):
    return 1 / (2 + gb)


nb = 2_000_000
gb_db = 20.0
gb = db2lin(gb_db)
h = (rng.standard_normal(nb) + 1j * rng.standard_normal(nb)) / np.sqrt(2)   # E|h|^2 = 1
b = rng.integers(0, 2, nb)
r = h * (1 - 2 * b) + awgn(nb, 1 / gb)
dec = (np.real(r * np.conj(h)) < 0).astype(int)                           # perfect CSI
check("Rayleigh BPSK MC vs 0.5(1-sqrt(g/(1+g))) @20 dB", np.mean(dec != b), pb_bpsk_rayleigh(gb), 0.1, rel=True)
z0 = h * (b == 0) + awgn(nb, 1 / gb)
z1 = h * (b == 1) + awgn(nb, 1 / gb)
dec = (np.abs(z1) > np.abs(z0)).astype(int)
check("Rayleigh NC-BFSK MC vs 1/(2+g) @20 dB", np.mean(dec != b), pb_ncfsk_rayleigh(gb), 0.1, rel=True)
for nm, f in (("BPSK", pb_bpsk_rayleigh), ("NC-BFSK", pb_ncfsk_rayleigh)):
    x = optimize.brentq(lambda x: np.log(f(db2lin(x))) - np.log(1e-5), 0, 80)
    print(f"  Rayleigh {nm}: average Eb/N0 for 1e-5 = {x:.1f} dB")

print("\nOVERALL:", "PASS" if ok_all else "FAIL")
