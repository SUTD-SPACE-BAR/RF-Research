#!/usr/bin/env python3
"""
array_taper.py — verification for kb/12-phased-arrays/tapering-sidelobe-control.md

  1. Dolph–Chebyshev: own implementation from the Chebyshev-polynomial derivation (sample T_{N-1}(x0 cos(psi/2))
     on N points and invert the DFT) vs scipy.signal.windows.chebwin; check Balanis/Nikolova N=10, 26 dB
     example (x0 = 1.08515, weights 1 : 1.357 : 1.974 : 2.496 : 2.789) and the 00-math page 8-el 30 dB weights.
     Equal-sidelobe check, HPBW vs uniform, directivity (exact formula) vs Dolph's approximation
     D = 2R^2 / (1 + (R^2-1) f lambda/(L+d)), broadening factor f; maximum spacing d/lambda < 1 - acos(1/x0)/pi.
  2. Binomial: weights, no sidelobes at d = lambda/2, HPBW ~ 1.06/sqrt(N-1), D ~ 1.77 sqrt(N).
  3. Taylor n-bar: own implementation from Taylor's line-source formulas (zeros, sigma, F(m)) sampled at element
     positions vs scipy.signal.windows.taylor; achieved SLL for small N; HPBW, taper efficiency.
  4. Other tapers: Hamming, Hann, Blackman, cosine- and cosine^2-on-pedestal, Gaussian: SLL, HPBW broadening,
     taper efficiency, edge taper.
  5. Random errors: Monte Carlo of amplitude/phase errors -> average sidelobe (error) floor vs
     sigma^2/(N eta) and gain loss vs exp(-sigma_phi^2); element failures.
     Probability that the peak sidelobe exceeds the design SLL.
  6. Monopulse sum/difference (split-aperture) for a tracking array: difference null depth, slope (error
     sensitivity) and difference-pattern sidelobes for uniform vs Taylor halves.
  7. 8-element 5.8 GHz worked example: taper choices, with ADAR1000-like 0.5 dB gain steps and 2.8° phase steps.
Convention: d = lambda/2 unless stated; theta from broadside.
"""
import numpy as np
from math import factorial
from scipy.signal.windows import chebwin, taylor, hamming, hann, blackman, gaussian
from scipy.optimize import brentq

rng = np.random.default_rng(11)


def pattern(a, d=0.5, n=40001, u0=0.0, umax=1.0):
    N = len(a)
    x = (np.arange(N) - (N - 1) / 2) * d
    u = np.linspace(-umax, umax, n)
    AF = np.exp(1j * 2 * np.pi * np.outer(u, x)) @ (a * np.exp(-1j * 2 * np.pi * x * u0))
    P = np.abs(AF) ** 2
    return u, P / P.max()


def sll_hpbw(a, d=0.5):
    u, P = pattern(a, d)
    ip = np.argmax(P)
    # main lobe edges: first local minima either side
    r = ip
    while r < len(P) - 1 and P[r + 1] < P[r]:
        r += 1
    l = ip
    while l > 0 and P[l - 1] < P[l]:
        l -= 1
    mask = np.ones_like(P, bool); mask[l:r + 1] = False
    sll = 10 * np.log10(P[mask].max()) if mask.any() else -np.inf
    # HPBW in degrees (broadside, u = sin theta)
    f = P - 0.5
    rr = ip
    while f[rr] > 0:
        rr += 1
    ll = ip
    while f[ll] > 0:
        ll -= 1
    hp = np.degrees(np.arcsin(u[rr]) - np.arcsin(u[ll]))
    return sll, hp


def taper_eff(a):
    a = np.asarray(a, float)
    return np.sum(a) ** 2 / (len(a) * np.sum(a ** 2))


def directivity_iso(a, d=0.5):
    N = len(a)
    x = np.arange(N) * d
    dx = x[:, None] - x[None, :]
    S = np.sinc(2 * dx)  # sinc(k dx) with k = 2 pi, numpy sinc = sin(pi t)/(pi t)
    return np.sum(a) ** 2 / (a @ S @ a)


def dolph_own(N, sll_db):
    """Dolph–Chebyshev weights by sampling the Chebyshev polynomial pattern and inverse DFT.
    AF(psi) = T_{N-1}(x0 cos(psi/2)), psi = kd(u-u0); AF is (up to phase) a trig polynomial of degree N-1 in psi/2,
    so N samples at psi_m = 2 pi m / N determine the weights."""
    R = 10 ** (sll_db / 20)
    M = N - 1
    x0 = np.cosh(np.arccosh(R) / M)
    m = np.arange(N)
    psi = 2 * np.pi * m / N
    xx = x0 * np.cos(psi / 2)
    T = np.where(np.abs(xx) <= 1, np.cos(M * np.arccos(np.clip(xx, -1, 1))),
                 np.sign(xx) ** M * np.cosh(M * np.arccosh(np.maximum(np.abs(xx), 1))))
    # AF(psi_m) = sum_n w_n e^{j (n-(N-1)/2) psi_m}; remove the half-integer phase for even N
    Ahat = T * np.exp(1j * (N - 1) / 2 * psi)  # = sum_n w_n e^{j n psi_m}
    w = np.real(np.fft.fft(Ahat)) / N  # e^{-j} convention: w_n = (1/N) sum_m Ahat_m e^{-j n psi_m}
    w = np.abs(w)
    return w / w.max(), x0


print("=" * 78)
print("1. Dolph–Chebyshev")
for N, s in ((8, 30), (10, 26), (8, 20), (8, 25), (16, 30), (16, 40), (32, 35)):
    w, x0 = dolph_own(N, s)
    ws = chebwin(N, s)
    ws = ws / ws.max()
    sll, hp = sll_hpbw(w)
    sllu, hpu = sll_hpbw(np.ones(N))
    D = directivity_iso(w)
    R = 10 ** (s / 20)
    f = 1 + 0.636 * (2 / R * np.cosh(np.sqrt(np.arccosh(R) ** 2 - np.pi ** 2))) ** 2
    L = (N - 1) * 0.5
    Dapprox = 2 * R ** 2 / (1 + (R ** 2 - 1) * f / (L + 0.5))
    dmax = 1 - np.arccos(1 / x0) / np.pi
    # large-N ("ideal", continuous) Chebyshev/Taylor beamwidth: HPBW_u = (2/(pi N d)) sqrt(acosh(R)^2 - acosh(R/sqrt2)^2)
    hp_ideal = np.degrees(2 / (np.pi * N * 0.5) * np.sqrt(np.arccosh(R) ** 2 - np.arccosh(R / np.sqrt(2)) ** 2))
    print(f"     large-N ideal HPBW {hp_ideal:5.2f}° (ratio to uniform-ideal {hp_ideal/np.degrees(0.8859/(N*0.5)):.3f})")
    print(f"  N={N:2d} SLL={s} dB: x0={x0:.5f}; max|own-scipy|={np.max(np.abs(w-ws)):.1e}; achieved SLL {sll:6.2f} dB; "
          f"HPBW {hp:5.2f}° (uniform {hpu:5.2f}°, x{hp/hpu:.3f}; Dolph f={f:.3f}); η_t={taper_eff(w):.3f}; "
          f"D={10*np.log10(D):5.2f} dB (Dolph approx {10*np.log10(Dapprox):5.2f}, uniform {10*np.log10(N):5.2f}); d_max={dmax:.3f}λ")
    if (N, s) == (10, 26):
        half = w[N // 2:]  # centre to edge
        print(f"     N=10/26 dB weights edge→centre normalised to edge: {np.round((half/half[-1])[::-1],3)}")
    if (N, s) == (8, 30):
        print(f"     N=8/30 dB weights: {np.round(w,3)}")
# equal-ripple check
w, x0 = dolph_own(16, 30)
u, P = pattern(w)
pk = [10 * np.log10(P[i]) for i in range(1, len(P) - 1) if P[i] > P[i - 1] and P[i] > P[i + 1] and P[i] < 0.9]
print(f"  N=16 30 dB: all sidelobe peaks (dB): {np.round(sorted(pk)[-6:],2)} ... min {min(pk):.2f}")

print("=" * 78)
print("2. Binomial (d = λ/2)")
from scipy.special import comb
for N in (3, 5, 8, 10, 16):
    w = np.array([comb(N - 1, k) for k in range(N)], float)
    w /= w.max()
    sll, hp = sll_hpbw(w)
    D = directivity_iso(w)
    print(f"  N={N:2d}: weights edge ratio 1:{w.max()/w.min():.0f}; SLL {sll:7.1f} dB; HPBW {hp:6.2f}° vs 1.06/sqrt(N-1) rad = {np.degrees(1.06/np.sqrt(N-1)):6.2f}°; "
          f"D={D:6.3f} vs 1.77√N={1.77*np.sqrt(N):6.3f}; η_t={taper_eff(w):.3f}")

print("=" * 78)
print("3. Taylor n-bar (own from Taylor 1955 formulas vs scipy)")


def taylor_own(N, nbar, sll_db):
    R = 10 ** (sll_db / 20)
    A = np.arccosh(R) / np.pi
    sig2 = nbar ** 2 / (A ** 2 + (nbar - 0.5) ** 2)
    ma = np.arange(1, nbar)

    def Fm(m):
        num = np.prod([1 - m ** 2 / (sig2 * (A ** 2 + (n - 0.5) ** 2)) for n in ma])
        den = np.prod([1 - m ** 2 / j ** 2 for j in ma if j != m])
        return ((-1) ** (m + 1)) * num / (2 * den)

    F = np.array([Fm(m) for m in ma])
    xi = (np.arange(N) - (N - 1) / 2) / N  # element position / aperture length (aperture = N d)
    w = 1 + 2 * np.cos(2 * np.pi * np.outer(xi, ma)) @ F
    return w / w.max(), np.sqrt(sig2)


for N, nbar, s in ((8, 3, 25), (8, 4, 30), (16, 4, 30), (16, 5, 35), (32, 5, 30), (32, 6, 40), (64, 5, 30), (64, 8, 40)):
    w, sig = taylor_own(N, nbar, s)
    ws = taylor(N, nbar=nbar, sll=s, norm=True)
    ws = ws / ws.max()
    sll, hp = sll_hpbw(w)
    _, hpu = sll_hpbw(np.ones(N))
    edge_db = 20 * np.log10(w[0] / w.max())
    print(f"  N={N:2d} n̄={nbar} {s} dB: max|own-scipy|={np.max(np.abs(w-ws)):.1e}; achieved SLL {sll:6.2f} dB; σ={sig:.4f}; "
          f"HPBW {hp:5.2f}° (x{hp/hpu:.3f} uniform); η_t={taper_eff(w):.3f} ({10*np.log10(taper_eff(w)):.2f} dB); edge {edge_db:.1f} dB")
# n-bar too large -> non-monotonic; compare largest monotonic n-bar with Hansen-type rule 2A^2 + 1/2
for sdb in (20, 25, 30, 35, 40):
    A = np.arccosh(10 ** (sdb / 20)) / np.pi
    best = 0
    for nb in range(2, 25):
        w, _ = taylor_own(200, nb, sdb)
        if np.all(np.diff(w[:100]) >= -1e-12):
            best = nb
    print(f"    SLL {sdb} dB: largest n̄ with monotonic taper (N=200) = {best}; 2A²+1/2 = {2*A*A+0.5:.2f}")
# n-bar too large -> non-monotonic
for nbar in (3, 5, 8, 12, 20):
    w, _ = taylor_own(32, nbar, 30)
    mono = np.all(np.diff(w[: 16]) >= -1e-9)
    print(f"    N=32 30 dB n̄={nbar:2d}: η_t={taper_eff(w):.4f}, monotonic to edge: {mono}, edge {20*np.log10(w[0]):.1f} dB")

print("=" * 78)
print("4. Other tapers (N = 32)")
N = 32
xi = (np.arange(N) - (N - 1) / 2) / (N / 2)  # -1..1 roughly
tapers = {
    "uniform": np.ones(N),
    "Hamming": hamming(N), "Hann (no zero ends)": hann(N + 2)[1:-1], "Blackman (no zero ends)": blackman(N + 2)[1:-1],
    "cos on 0 dB ped (cos)": np.cos(np.pi * xi / 2 * (N - 1) / N * 1.0),
}
for ped_db in (-10, -20):
    p = 10 ** (ped_db / 20)
    tapers[f"cos on {ped_db} dB ped"] = p + (1 - p) * np.cos(np.pi * xi / 2)
    tapers[f"cos² on {ped_db} dB ped"] = p + (1 - p) * np.cos(np.pi * xi / 2) ** 2
tapers["Gaussian σ=N/5"] = gaussian(N, N / 5)
_, hpu = sll_hpbw(np.ones(N))
for k, w in tapers.items():
    w = np.asarray(w, float)
    sll, hp = sll_hpbw(w)
    print(f"  {k:22s}: SLL {sll:7.2f} dB  HPBW x{hp/hpu:.3f}  η_t {taper_eff(w):.3f} ({10*np.log10(taper_eff(w)):6.2f} dB)  edge {20*np.log10(w[0]/w.max()):6.1f} dB")

print("=" * 78)
print("5. Random errors (Monte Carlo)")
for N, name, a in ((64, "Taylor 30 dB n̄=5", taylor(64, 5, 30)), (16, "Taylor 25 dB n̄=4", taylor(16, 4, 25)), (8, "uniform", np.ones(8))):
    a = a / a.max()
    eta = taper_eff(a)
    for sa_db, sp_deg in ((0.5, 3), (1.0, 5), (1.0, 10), (0.25, 2)):
        sa = sa_db * np.log(10) / 20  # fractional amplitude sigma
        sp = np.radians(sp_deg)
        trials = 1500
        x = (np.arange(N) - (N - 1) / 2) * 0.5
        u = np.linspace(-1, 1, 4001)
        E = np.exp(1j * 2 * np.pi * np.outer(u, x))
        far = np.abs(u) > min(0.8, 4 / (N * 0.5))  # well away from the main beam
        floor = []
        gain = []
        pk_sll = []
        P0 = np.abs(E @ a) ** 2
        for _ in range(trials):
            ae = a * (1 + sa * rng.standard_normal(N)) * np.exp(1j * sp * rng.standard_normal(N))
            P = np.abs(E @ ae) ** 2
            err = np.abs(E @ (ae - a)) ** 2
            floor.append(np.mean(err[far]) / P0.max())
            gain.append(P.max() / P0.max())
            pk_sll.append(10 * np.log10(P[far].max() / P.max()))
        pred = (sa ** 2 + sp ** 2) / (N * eta)
        print(f"  N={N:2d} {name:18s} σa={sa_db} dB σφ={sp_deg:2d}°: error floor MC {10*np.log10(np.mean(floor)):6.2f} dB vs (σa²+σφ²)/(Nη) {10*np.log10(pred):6.2f} dB; "
              f"gain loss MC {10*np.log10(np.mean(gain)):6.3f} dB vs exp(-σφ²) {10*np.log10(np.exp(-sp**2)):6.3f}; far-out peak SLL median {np.median(pk_sll):6.1f} dB, 90th pct {np.percentile(pk_sll,90):6.1f} dB")
# element failures
N = 64
a = taylor(64, 5, 30); a /= a.max()
for pf in (0.02, 0.05, 0.1):
    fl = []; gl = []
    x = (np.arange(N) - (N - 1) / 2) * 0.5
    u = np.linspace(-1, 1, 4001)
    E = np.exp(1j * 2 * np.pi * np.outer(u, x))
    far = np.abs(u) > min(0.8, 4 / (N * 0.5))
    P0 = np.abs(E @ a) ** 2
    for _ in range(1500):
        alive = rng.random(N) > pf
        ae = a * alive
        err = np.abs(E @ (ae - a * (1 - pf))) ** 2
        P = np.abs(E @ ae) ** 2
        fl.append(np.mean(err[far]) / P0.max())
        gl.append(P.max() / P0.max())
    pred = pf / ((1 - pf) * N * taper_eff(a)) * (1 - pf) ** 2 / (1 - pf) ** 2
    print(f"  N=64 Taylor30: failures {100*pf:4.1f}%: gain loss MC {10*np.log10(np.mean(gl)):6.2f} dB vs 20log(1-p) {20*np.log10(1-pf):6.2f}; "
          f"floor MC {10*np.log10(np.mean(fl)):6.2f} dB vs p(1-p)/(Nη) {10*np.log10(pf*(1-pf)/(N*taper_eff(a))):6.2f} dB")

print("=" * 78)
print("6. Monopulse (split aperture), N = 16, d = λ/2")
N = 16
x = (np.arange(N) - (N - 1) / 2) * 0.5
u = np.linspace(-0.3, 0.3, 60001)
E = np.exp(1j * 2 * np.pi * np.outer(u, x))
for name, a in (("uniform", np.ones(N)), ("Taylor 30 dB n̄=4", taylor(N, 4, 30))):
    a = a / a.max()
    sgn = np.where(x < 0, -1, 1)
    S = E @ a
    D = E @ (a * sgn)
    ratio = np.imag(D / S)  # for symmetric real a: D/S is purely imaginary near boresight
    i0 = np.argmin(np.abs(u))
    slope = (ratio[i0 + 10] - ratio[i0 - 10]) / (u[i0 + 10] - u[i0 - 10])
    # difference pattern peak and its sidelobes over full visible space
    uf, Pd = pattern(a * sgn)
    ip = np.argmax(Pd)
    pd_db = 10 * np.log10(Pd)
    peaks = [pd_db[i] for i in range(1, len(Pd) - 1) if Pd[i] > Pd[i - 1] and Pd[i] > Pd[i + 1]]
    peaks = sorted(peaks)
    diff_sll = peaks[-3] if len(peaks) >= 3 else np.nan
    _, Ps = pattern(a)
    print(f"  {name:18s}: Δ/Σ slope at boresight = {slope:.2f} per unit u ({slope*np.pi/180:.4f} per degree); "
          f"Δ peak at u=±{abs(uf[ip]):.4f} ({np.degrees(np.arcsin(abs(uf[ip]))):.2f}°); Δ-pattern highest sidelobe {diff_sll:.1f} dB rel Δ peak")
print("  (Bayliss taper is the Δ-pattern analogue of Taylor; the split-Taylor Δ has high sidelobes)")

print("=" * 78)
print("7. 8-element worked example with ADAR1000-like quantisation (0.5 dB gain steps, 2.8125° phase steps)")
N = 8
for name, a in (("uniform", np.ones(N)), ("Dolph 25 dB", chebwin(N, 25)), ("Taylor 25 dB n̄=3", taylor(N, 3, 25)),
                ("Dolph 30 dB", chebwin(N, 30)), ("Hamming", hamming(N))):
    a = a / a.max()
    sll, hp = sll_hpbw(a)
    # quantise amplitude to 0.5 dB steps (attenuation from max)
    att = np.round(-20 * np.log10(a) / 0.5) * 0.5
    aq = 10 ** (-att / 20)
    sllq, hpq = sll_hpbw(aq)
    # plus phase quantisation at 30° steer, 2.8125° steps, plus random residuals 0.3 dB / 3°
    worst = []
    for _ in range(400):
        ph = -np.pi * np.arange(N) * np.sin(np.radians(30))
        phq = np.round(ph / np.radians(2.8125)) * np.radians(2.8125)
        ae = aq * 10 ** (0.3 * rng.standard_normal(N) / 20) * np.exp(1j * (phq + np.radians(3) * rng.standard_normal(N)))
        xx = np.arange(N) * 0.5
        uu = np.linspace(-1, 1, 8001)
        P = np.abs(np.exp(1j * 2 * np.pi * np.outer(uu, xx)) @ ae) ** 2
        P /= P.max()
        ip = np.argmax(P)
        r = ip
        while r < len(P) - 1 and P[r + 1] < P[r]:
            r += 1
        l = ip
        while l > 0 and P[l - 1] < P[l]:
            l -= 1
        m = np.ones_like(P, bool); m[l:r + 1] = False
        worst.append(10 * np.log10(P[m].max()))
    print(f"  {name:18s}: ideal SLL {sll:6.2f} dB, HPBW {hp:5.2f}°, η_t {taper_eff(a):.3f} ({10*np.log10(taper_eff(a)):5.2f} dB); "
          f"0.5 dB-quantised SLL {sllq:6.2f}; with 7-bit phase @30° + 0.3 dB/3° residuals: median SLL {np.median(worst):6.2f}, 90th pct {np.percentile(worst,90):6.2f} dB")
print("done")
