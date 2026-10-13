#!/usr/bin/env python3
# Runtime (W6-F5, 2026-10-14): ~186 s (3.1 min) measured on a 10-core Apple-silicon Mac, run 3 at a time
# under load average 7-70 from other jobs; expect less on an idle machine. It exceeds the 120 s per-script budget
# used by the D7 verify sweep, so give it a >= 15 min timeout and run it with `python3 -u` to see progress. (The docstring's ~40 s is the unloaded figure.)
# Measured run: exit 0, no FAIL lines. Comment only; no code or results changed.
"""Verification for kb/11-radar/detection-theory-cfar.md (also used by radar-range-equation.md)

Run:  python3 tools/verify/radar_detection_cfar.py        (~40 s)

Model: complex baseband samples x_n = s_n + w_n, noise w_n ~ CN(0,1) (unit power per complex
sample), per-pulse SNR chi = E|s_n|^2.  Square-law detector z = sum_{n=1}^{N} |x_n|^2.

Checks:
  1. Single-pulse known-noise detection: Pfa = exp(-T); Pd (Swerling 0) = Marcum Q1(sqrt(2chi),
     sqrt(2T)) == ncx2 formulation; vs Monte-Carlo.  Swerling 1, N=1 closed form Pd = Pfa^(1/(1+chi)).
  2. Exact required SNR for Swerling 0..4 with N-pulse non-coherent integration
     (SW0: noncentral chi-square; SW2: Gamma; SW1/SW3: numerical average of SW0 over the
     scan-to-scan fluctuation pdf; SW4: numerical average over per-pulse chi^2-4 fluctuation via
     a Monte-Carlo with common random numbers) -- cross-checked against direct Monte-Carlo.
  3. Albersheim's equation (linear detector, SW0) vs exact square-law SW0 and vs Monte-Carlo
     linear-detector: error <= ~0.2-0.3 dB inside its validity range.
  4. Shnidman's equation vs exact for SW0..SW4 over a grid (Pd .5/.9/.99, Pfa 1e-4/1e-6/1e-8,
     N 1/10/30): max |error| < 1 dB, typical < 0.5 dB (Shnidman's claim).
  5. Non-coherent integration gain exponent alpha (Gnc = N^alpha) -- Richards' example
     (Pfa 1e-8, Pd 0.8, N=10: ~14 dB -> ~5.7 dB, alpha ~0.83) and that alpha is >0.5.
  6. Coherent integration: SNR gain exactly N (MC).
  7. CFAR: CA-CFAR Pfa = (1 + a/N)^-N (threshold a x mean of N cells), OS-CFAR Pfa =
     prod_{i=0}^{k-1} (N-i)/(N-i+a), GO/SO-CFAR closed forms (Hansen & Sawyers) -- all vs MC.
     CFAR loss for Swerling-1 single pulse: exact CA-CFAR Pd = (1 + a/(N(1+chi)))^-N.
  8. OS-CFAR robustness demo: interfering target in the reference window (masking) CA vs OS.
"""
import numpy as np
from scipy import special, stats, optimize, integrate

rng = np.random.default_rng(11)
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.5g}, expected {want:.5g} (tol {tol}{' rel' if rel else ''})")
    return ok


def db(x):
    return 10 * np.log10(x)


def undb(x):
    return 10 ** (x / 10)


# ----------------------------------------------------------------------------- exact models
def threshold_sqlaw(pfa, N):
    """Threshold T on z = sum |x|^2 (noise CN(0,1)): z ~ Gamma(N,1)."""
    return special.gammainccinv(N, pfa)


def pd_sw0(chi, T, N):
    # 2z ~ noncentral chi2 with 2N dof, noncentrality 2 N chi
    return stats.ncx2.sf(2 * T, 2 * N, 2 * N * chi)


def pd_sw2(chi, T, N):
    # each pulse signal is CN(0,chi) independent -> |x|^2 ~ Exp(1+chi), sum ~ Gamma(N, 1+chi)
    return special.gammaincc(N, T / (1 + chi))


def pd_scan(chi, T, N, shape):
    """Scan-to-scan fluctuation (SW1 shape=1, SW3 shape=2): power factor s ~ Gamma(shape, 1/shape)."""
    f = lambda s: pd_sw0(chi * s, T, N) * stats.gamma.pdf(s, shape, scale=1 / shape)
    val, _ = integrate.quad(f, 0, np.inf, limit=200)
    return val


# SW4: per-pulse chi-square 4-dof power fluctuation. Use MC with fixed random numbers so that
# Pd(chi) is smooth & monotone in chi and can be root-found.
_SW4_TRIALS = 400000


def pd_sw4_mc(chi, T, N, seed=5):
    r = np.random.default_rng(seed)
    total = 0.0
    # generate in chunks
    ntr = _SW4_TRIALS
    chunk = 100000
    cnt = 0
    for i in range(ntr // chunk):
        s = r.gamma(2.0, 0.5, size=(chunk, N))              # mean-1 power, chi2 4 dof
        ph = r.uniform(0, 2 * np.pi, size=(chunk, N))
        w = (r.standard_normal((chunk, N)) + 1j * r.standard_normal((chunk, N))) / np.sqrt(2)
        x = np.sqrt(chi * s) * np.exp(1j * ph) + w
        z = np.sum(np.abs(x) ** 2, axis=1)
        cnt += np.count_nonzero(z > T)
    return cnt / ntr


def pd_model(model, chi, T, N):
    if model == 0:
        return pd_sw0(chi, T, N)
    if model == 1:
        return pd_scan(chi, T, N, 1)
    if model == 2:
        return pd_sw2(chi, T, N)
    if model == 3:
        return pd_scan(chi, T, N, 2)
    if model == 4:
        return pd_sw4_mc(chi, T, N)


def req_snr_exact(model, pd, pfa, N):
    T = threshold_sqlaw(pfa, N)
    f = lambda sdb: pd_model(model, undb(sdb), T, N) - pd
    return optimize.brentq(f, -25, 60, xtol=1e-3)


# ----------------------------------------------------------------------------- approximations
def albersheim(pd, pfa, N=1):
    A = np.log(0.62 / pfa)
    B = np.log(pd / (1 - pd))
    return -5 * np.log10(N) + (6.2 + 4.54 / np.sqrt(N + 0.44)) * np.log10(A + 0.12 * A * B + 1.7 * B)


def shnidman(pd, pfa, N=1, model=0):
    K = {0: np.inf, 1: 1.0, 2: float(N), 3: 2.0, 4: 2.0 * N}[model]
    alpha = 0.0 if N < 40 else 0.25
    eta = np.sqrt(-0.8 * np.log(4 * pfa * (1 - pfa))) + np.sign(pd - 0.5) * np.sqrt(-0.8 * np.log(4 * pd * (1 - pd)))
    Xinf = eta * (eta + 2 * np.sqrt(N / 2 + (alpha - 0.25)))
    if np.isinf(K):
        CdB = 0.0
    else:
        C1 = (((17.7006 * pd - 18.4496) * pd + 14.5339) * pd - 3.525) / K
        C2 = (1 / K) * (np.exp(27.31 * pd - 25.14) + (pd - 0.8) * (0.7 * np.log(1e-5 / pfa) + (2 * N - 20) / 80))
        CdB = C1 if pd <= 0.872 else C1 + C2
    C = 10 ** (CdB / 10)
    X1 = C * Xinf / N
    return db(X1)


print("=" * 78)
print("1. Single-pulse detection (known noise power)")
T1 = -np.log(1e-6)
check("threshold T for Pfa=1e-6 (single pulse, exp)", threshold_sqlaw(1e-6, 1), T1, 1e-9)
chi = undb(13.0)
# Marcum Q1 via ncx2 identity equals Rice integration
pd_ncx = pd_sw0(chi, T1, 1)
# direct integration of Rice pdf of amplitude r (noise per real dim 1/2)
A = np.sqrt(chi)
rice = lambda r: 2 * r * np.exp(-(r - A) ** 2) * special.i0e(2 * A * r)   # = 2r e^{-(r^2+A^2)} I0(2Ar), overflow-safe
pd_rice, _ = integrate.quad(rice, np.sqrt(T1), np.inf)
check("SW0 N=1 Pd (ncx2) == Rice-pdf integral (chi=13 dB, Pfa 1e-6)", pd_ncx, pd_rice, 1e-6)
M = 2_000_000
w = (rng.standard_normal(M) + 1j * rng.standard_normal(M)) / np.sqrt(2)
pd_mc = np.mean(np.abs(np.sqrt(chi) + w) ** 2 > T1)
check("SW0 N=1 Pd vs Monte-Carlo", pd_mc, pd_ncx, 0.002)
pfa_mc = np.mean(np.abs(w) ** 2 > -np.log(1e-3))
check("Pfa=1e-3 threshold vs Monte-Carlo", pfa_mc, 1e-3, 1e-4)
check("SW1 N=1 closed form Pd = Pfa^(1/(1+chi))", pd_scan(chi, T1, 1, 1), 1e-6 ** (1 / (1 + chi)), 1e-6)
for pd_t in (0.5, 0.9, 0.99):
    print(f"    required single-pulse SNR (Pfa=1e-6): Pd={pd_t}: SW0 {req_snr_exact(0, pd_t, 1e-6, 1):.2f} dB, "
          f"SW1 {req_snr_exact(1, pd_t, 1e-6, 1):.2f} dB")

print("=" * 78)
print("2. Exact models vs direct Monte-Carlo (N=10, Pfa=1e-4, SNR/pulse = 3 dB)")
N = 10
T = threshold_sqlaw(1e-4, N)
chi = undb(3.0)
Mmc = 400000


def mc_pd(model, chi, T, N, trials=Mmc):
    r = np.random.default_rng(99)
    if model == 0:
        s = np.ones((trials, N))
    elif model == 1:
        s = np.repeat(r.exponential(1.0, (trials, 1)), N, axis=1)
    elif model == 2:
        s = r.exponential(1.0, (trials, N))
    elif model == 3:
        s = np.repeat(r.gamma(2.0, 0.5, (trials, 1)), N, axis=1)
    else:
        s = r.gamma(2.0, 0.5, (trials, N))
    ph = r.uniform(0, 2 * np.pi, (trials, N))
    w = (r.standard_normal((trials, N)) + 1j * r.standard_normal((trials, N))) / np.sqrt(2)
    z = np.sum(np.abs(np.sqrt(chi * s) * np.exp(1j * ph) + w) ** 2, axis=1)
    return np.mean(z > T)


for m in range(5):
    if m == 4:
        # the SW4 "exact" is itself MC with a different seed; compare the two
        check(f"SW{m} Pd model vs independent MC", pd_model(m, chi, T, N), mc_pd(m, chi, T, N), 0.004)
    else:
        check(f"SW{m} Pd exact vs MC", pd_model(m, chi, T, N), mc_pd(m, chi, T, N), 0.003)

print("=" * 78)
print("3. Albersheim (linear detector, SW0) vs exact square-law and MC linear detector")
worst = 0
for pd_t in (0.5, 0.9):
    for pfa in (1e-4, 1e-6):
        for Nn in (1, 10):
            ex = req_snr_exact(0, pd_t, pfa, Nn)
            al = albersheim(pd_t, pfa, Nn)
            worst = max(worst, abs(al - ex))
            print(f"    Pd={pd_t} Pfa={pfa:g} N={Nn:2d}: Albersheim {al:6.2f} dB, exact square-law {ex:6.2f} dB, diff {al-ex:+.2f}")
check("max |Albersheim - exact square-law| (dB)", worst, 0.0, 0.35)

# linear-detector MC for one case to show linear vs square law ~0.1-0.2 dB
Nn, pfa, pd_t = 10, 1e-4, 0.9
r = np.random.default_rng(7)
trials = 1_000_000
wn = (r.standard_normal((trials, Nn)) + 1j * r.standard_normal((trials, Nn))) / np.sqrt(2)
zlin0 = np.sum(np.abs(wn), axis=1)
Tlin = np.quantile(zlin0, 1 - pfa)
ph = r.uniform(0, 2 * np.pi, (trials // 4, Nn))
wn2 = (r.standard_normal((trials // 4, Nn)) + 1j * r.standard_normal((trials // 4, Nn))) / np.sqrt(2)


def pd_lin(sdb):
    return np.mean(np.sum(np.abs(np.sqrt(undb(sdb)) * np.exp(1j * ph) + wn2), axis=1) > Tlin) - pd_t


slin = optimize.brentq(pd_lin, -10, 20, xtol=0.01)
print(f"    MC linear detector N=10 Pfa=1e-4 Pd=0.9: {slin:.2f} dB; square-law exact {req_snr_exact(0, pd_t, pfa, Nn):.2f} dB; Albersheim {albersheim(pd_t, pfa, Nn):.2f} dB")
check("Albersheim vs MC linear detector (N=10)", albersheim(pd_t, pfa, Nn), slin, 0.3)

print("=" * 78)
print("4. Shnidman vs exact, Swerling 0-4")
errs = []
rows = []
for m in range(5):
    for pd_t in (0.5, 0.9, 0.99):
        for pfa in (1e-4, 1e-6, 1e-8):
            for Nn in (1, 10, 30):
                if m == 4 and pd_t == 0.99 and pfa == 1e-8 and Nn == 30:
                    pass
                ex = req_snr_exact(m, pd_t, pfa, Nn)
                sh = shnidman(pd_t, pfa, Nn, m)
                errs.append(sh - ex)
                rows.append((m, pd_t, pfa, Nn, ex, sh))
errs = np.array(errs)
for (m, pd_t, pfa, Nn, ex, sh) in rows:
    if pfa == 1e-6:
        print(f"    SW{m} Pd={pd_t:<4} Pfa=1e-6 N={Nn:2d}: exact {ex:6.2f} dB  Shnidman {sh:6.2f} dB  err {sh-ex:+.2f}")
print(f"    max |err| = {np.max(np.abs(errs)):.2f} dB, mean |err| = {np.mean(np.abs(errs)):.2f} dB, "
      f"fraction <0.5 dB = {np.mean(np.abs(errs) < 0.5):.2f}")
check("Shnidman max |error| over grid (dB)", np.max(np.abs(errs)), 0.0, 1.0)
check("Shnidman fraction of grid with |err|<0.5 dB", np.mean(np.abs(errs) < 0.5), 1.0, 0.25)

print("=" * 78)
print("5. Non-coherent integration gain exponent")
s1 = req_snr_exact(0, 0.8, 1e-8, 1)
s10 = req_snr_exact(0, 0.8, 1e-8, 10)
alpha = (s1 - s10) / 10
print(f"    SW0 Pfa=1e-8 Pd=0.8: N=1 {s1:.2f} dB, N=10 {s10:.2f} dB, Gnc {s1-s10:.2f} dB, alpha {alpha:.3f}")
check("Richards example Gnc (N=10, dB) ~8.3", s1 - s10, 8.3, 0.4)
for Nn in (2, 5, 10, 30, 100):
    a = (req_snr_exact(0, 0.9, 1e-6, 1) - req_snr_exact(0, 0.9, 1e-6, Nn)) / (10 * np.log10(Nn))
    print(f"    Pd=0.9 Pfa=1e-6 N={Nn:3d}: alpha = {a:.3f}  (sqrt law would be 0.5)")
a100 = (req_snr_exact(0, 0.9, 1e-6, 1) - req_snr_exact(0, 0.9, 1e-6, 100)) / 20
check("alpha at N=100 in 0.65-0.8 (Richards: 'a little more than 0.7')", a100, 0.72, 0.07)
# fluctuating targets: gain can exceed N (SW1 vs SW2 diversity)
g_sw2 = req_snr_exact(2, 0.9, 1e-6, 1) - req_snr_exact(2, 0.9, 1e-6, 10)
print(f"    SW2 (pulse-to-pulse) Pd 0.9 Pfa 1e-6: Gnc(N=10) = {g_sw2:.2f} dB (> 10 dB: diversity gain)")
check("SW2 Gnc(N=10) exceeds coherent 10 dB (fluctuation diversity)", float(g_sw2 > 10), 1.0, 0)

print("=" * 78)
print("6. Coherent integration gain = N")
for Nn in (8, 64):
    r = np.random.default_rng(1)
    trials = 20000
    A = 0.3
    x = A * np.exp(1j * 0.7) + (r.standard_normal((trials, Nn)) + 1j * r.standard_normal((trials, Nn))) / np.sqrt(2)
    y = x.sum(axis=1)
    snr_out = (Nn * A) ** 2 / np.var(y - Nn * A * np.exp(1j * 0.7))
    check(f"coherent gain N={Nn} (dB)", db(snr_out / A ** 2), db(Nn), 0.1)

print("=" * 78)
print("7. CFAR false-alarm formulas vs Monte-Carlo (exponential/square-law noise)")
Ncfar = 16
pfa_des = 1e-3
a_ca = Ncfar * (pfa_des ** (-1 / Ncfar) - 1)           # multiplier on the MEAN of N cells
trials = 3_000_000
r = np.random.default_rng(2024)
ref = r.exponential(1.0, (trials, Ncfar))
cut = r.exponential(1.0, trials)
pfa_ca = np.mean(cut > a_ca * ref.mean(axis=1))
check("CA-CFAR Pfa (N=16, design 1e-3)", pfa_ca, pfa_des, 0.08, rel=True)
print(f"    CA-CFAR multiplier on mean alpha = {a_ca:.3f} ({db(a_ca):.2f} dB) vs known-noise T = {-np.log(pfa_des):.3f} ({db(-np.log(pfa_des)):.2f} dB)")

# OS-CFAR
k = int(0.75 * Ncfar)   # Rohling: k ~ 3N/4
def pfa_os(a, N, k):
    i = np.arange(k)
    return np.prod((N - i) / (N - i + a))
a_os = optimize.brentq(lambda a: pfa_os(a, Ncfar, k) - pfa_des, 0.1, 1000)
srt = np.sort(ref, axis=1)
pfa_os_mc = np.mean(cut > a_os * srt[:, k - 1])
check(f"OS-CFAR Pfa (N=16, k={k})", pfa_os_mc, pfa_des, 0.08, rel=True)
print(f"    OS-CFAR multiplier on k-th sample = {a_os:.3f}")

# GO / SO (Hansen & Sawyers 1980), n = N/2 per side, threshold a * max/min(sum_lead, sum_lag)
n = Ncfar // 2
def pfa_so(a, n):
    i = np.arange(n)
    return 2 * np.sum(special.comb(n + i - 1, i) * (2 + a) ** (-(n + i)))
def pfa_go(a, n):
    return 2 * (1 + a) ** (-n) - pfa_so(a, n)
a_go = optimize.brentq(lambda a: pfa_go(a, n) - pfa_des, 1e-3, 100)
a_so = optimize.brentq(lambda a: pfa_so(a, n) - pfa_des, 1e-3, 100)
Sx = ref[:, :n].sum(axis=1)
Sy = ref[:, n:].sum(axis=1)
check("GO-CFAR Pfa (Hansen-Sawyers formula)", np.mean(cut > a_go * np.maximum(Sx, Sy)), pfa_des, 0.08, rel=True)
check("SO-CFAR Pfa (Hansen-Sawyers formula)", np.mean(cut > a_so * np.minimum(Sx, Sy)), pfa_des, 0.08, rel=True)

# CFAR loss, Swerling 1 single pulse: Pd = (1 + a/(N(1+chi)))^-N with a on the mean
def req_snr_ca_sw1(pd, pfa, N):
    a = N * (pfa ** (-1 / N) - 1)
    f = lambda sdb: (1 + a / (N * (1 + undb(sdb)))) ** (-N) - pd
    return optimize.brentq(f, -10, 80)
def req_snr_known_sw1(pd, pfa):
    return db(np.log(pfa) / np.log(pd) - 1)
print("    CFAR loss (Swerling 1, single pulse, Pfa=1e-6, Pd=0.9):")
for Nn in (8, 16, 32, 64, 128):
    L = req_snr_ca_sw1(0.9, 1e-6, Nn) - req_snr_known_sw1(0.9, 1e-6)
    print(f"      N_ref = {Nn:3d}: CA-CFAR loss = {L:.2f} dB")
L16 = req_snr_ca_sw1(0.9, 1e-6, 16) - req_snr_known_sw1(0.9, 1e-6)
# MC check of CA-CFAR Pd formula at that SNR
chi16 = undb(req_snr_ca_sw1(0.9, 1e-6, 16))
tr = 400000
r = np.random.default_rng(5)
refm = r.exponential(1.0, (tr, 16)).mean(axis=1)
cut_s = r.exponential(1 + chi16, tr)
a16 = 16 * (1e-6 ** (-1 / 16) - 1)
check("CA-CFAR SW1 Pd formula vs MC at design SNR", np.mean(cut_s > a16 * refm), 0.9, 0.003)
# Rule of thumb in literature: CFAR loss ~ a few dB for N=16 at Pfa 1e-6 -- print only
print(f"    -> N=16 CFAR loss {L16:.2f} dB")

print("=" * 78)
print("8. Masking by an interfering target in the reference window (N=16, Pfa 1e-3)")
chi_t = undb(15)
tr = 300000
r = np.random.default_rng(8)
ref = r.exponential(1.0, (tr, Ncfar))
ref[:, 3] = r.exponential(1 + chi_t, tr)            # interferer of same strength in one ref cell
cut_s = r.exponential(1 + chi_t, tr)                 # SW1 target in CUT
pd_ca = np.mean(cut_s > a_ca * ref.mean(axis=1))
pd_os = np.mean(cut_s > a_os * np.sort(ref, axis=1)[:, k - 1])
refc = r.exponential(1.0, (tr, Ncfar))
pd_ca0 = np.mean(cut_s > a_ca * refc.mean(axis=1))
print(f"    15 dB SW1 target, clean window: CA Pd={pd_ca0:.3f}; with equal interferer: CA Pd={pd_ca:.3f}, OS Pd={pd_os:.3f}")
check("OS-CFAR more robust than CA with one interferer", float(pd_os > pd_ca + 0.05), 1.0, 0)

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
