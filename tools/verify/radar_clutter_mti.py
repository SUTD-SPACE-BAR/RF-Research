#!/usr/bin/env python3
"""Verification for kb/11-radar/clutter-and-mti.md

Run:  python3 tools/verify/radar_clutter_mti.py     (~30 s)

Checks:
  1. MTI cancellers: |H1| = 2|sin(pi f T)|, |H2| = 4 sin^2(pi f T); blind speeds v_n = n lambda PRF/2.
  2. Improvement factor for Gaussian clutter spectrum (std sigma_f):
       single canceller I1 = f_r^2/(2 pi^2 sigma_f^2), double I2 = f_r^4/(8 pi^4 sigma_f^4)  vs Monte-Carlo.
  3. Staggered PRF (2 PRIs in ratio 4:5) moves the first blind speed out to ~4-5x the unstaggered one
     (response averaged over the stagger).
  4. Rain: Marshall-Palmer DSD N(D) = 8000 exp(-Lambda D) m^-3 mm^-1, Lambda = 4.1 R^-0.21:
       Z from the DSD vs the Z = 200 R^1.6 relation (known mismatch); volume reflectivity
       eta = pi^5 |K|^2 Z / lambda^4 (Rayleigh) vs Mie-integrated backscatter at 3/10/24/77 GHz.
  5. Clutter-cell size: surface (pulse/range-limited) A = R theta_az dR sec(psi) and volume
     V = pi R^2 theta phi dR / (8 ln 2) (Gaussian beam, Probert-Jones); worked signal-to-clutter examples.
  6. STAP / SMI: Reed-Mallett-Brennan average SNR loss (K+2-N)/(K+1) vs Monte-Carlo (N=8, K=16 -> ~-3 dB).
  7. FMCW static-clutter removal (mean over chirps) = zero-Doppler notch: suppression of a static
     reflector vs pass of a mover.
"""
import numpy as np
from scipy import integrate, special

c = 299_792_458.0
ok_all = True
rng = np.random.default_rng(9)


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol}{' rel' if rel else ''})")
    return ok


db = lambda x: 10 * np.log10(x)

print("=" * 78)
print("1. MTI canceller responses and blind speeds")
T = 1e-3
f = np.linspace(0, 2000, 2001)
H1 = np.abs(1 - np.exp(-2j * np.pi * f * T))
H2 = np.abs((1 - np.exp(-2j * np.pi * f * T)) ** 2)
check("single canceller |H| = 2|sin(pi f T)|", np.max(np.abs(H1 - 2 * np.abs(np.sin(np.pi * f * T)))), 0, 1e-12)
check("double canceller |H| = 4 sin^2(pi f T)", np.max(np.abs(H2 - 4 * np.sin(np.pi * f * T) ** 2)), 0, 1e-12)
lam = c / 3e9
prf = 1e3
vb = lam * prf / 2
print(f"    S-band 3 GHz, PRF 1 kHz: first blind speed lambda PRF/2 = {vb:.2f} m/s (then {2*vb:.1f}, {3*vb:.1f} ...)")
check("blind speed S-band 1 kHz", vb, 49.97, 0.05)

print("=" * 78)
print("2. MTI improvement factor, Gaussian clutter spectrum")
fr = 1e3
sig_v = 0.3                     # m/s (e.g. wind-blown vegetation, order of magnitude)
sig_f = 2 * sig_v / lam
I1_th = fr ** 2 / (2 * np.pi ** 2 * sig_f ** 2)
I2_th = fr ** 4 / (8 * np.pi ** 4 * sig_f ** 4)
# MC: generate correlated clutter with Gaussian PSD (std sig_f), unit power
Npulse = 1 << 16
freqs = np.fft.fftfreq(Npulse, 1 / fr)
psd = np.exp(-freqs ** 2 / (2 * sig_f ** 2))
clut = np.fft.ifft(np.sqrt(psd) * (rng.standard_normal(Npulse) + 1j * rng.standard_normal(Npulse)))
clut /= np.sqrt(np.mean(np.abs(clut) ** 2))
o1 = clut[1:] - clut[:-1]
o2 = clut[2:] - 2 * clut[1:-1] + clut[:-2]
CA1 = 1 / np.mean(np.abs(o1) ** 2)
CA2 = 1 / np.mean(np.abs(o2) ** 2)
# improvement factor = CA x average target gain (2 for single, 6 for double over uniform Doppler)
I1_mc = CA1 * 2
I2_mc = CA2 * 6
print(f"    sigma_v {sig_v} m/s -> sigma_f {sig_f:.2f} Hz at 3 GHz, PRF {fr:.0f} Hz")
print(f"    I1: theory {db(I1_th):.2f} dB, MC {db(I1_mc):.2f} dB;  I2: theory {db(I2_th):.2f} dB, MC {db(I2_mc):.2f} dB")
check("single-canceller improvement factor (dB)", db(I1_mc), db(I1_th), 0.5)
# the double-canceller small-sigma formula uses rho expansion to 2nd order; allow 1 dB
check("double-canceller improvement factor (dB)", db(I2_mc), db(I2_th), 1.0)

print("=" * 78)
print("3. Staggered PRF (PRIs 4:5)")
T1, T2 = 4 / 4.5e3, 5 / 4.5e3            # mean PRI 1/0.9 ms... ratio 4:5
Tm = (T1 + T2) / 2
v = np.linspace(0.5, 400, 8000)
fd = 2 * v / lam
resp_unstag = np.abs(1 - np.exp(-2j * np.pi * fd * Tm)) ** 2 / 2       # normalised avg gain 1
resp_stag = (np.abs(1 - np.exp(-2j * np.pi * fd * T1)) ** 2 + np.abs(1 - np.exp(-2j * np.pi * fd * T2)) ** 2) / 4
vb_m = lam / (2 * Tm)
# first velocity where response < -20 dB (blind)
sel = v > 5.0                                   # skip the clutter notch around zero Doppler
first_blind_unstag = v[sel][np.argmax(resp_unstag[sel] < 0.01)]
first_blind_stag = v[sel][np.argmax(resp_stag[sel] < 0.01)]
print(f'    staggered response at the unstaggered blind speed {vb_m:.1f} m/s: {10*np.log10(np.interp(vb_m, v, resp_stag)):.1f} dB (not blind)')
print(f"    unstaggered (mean PRI {Tm*1e3:.3f} ms): first blind ~{first_blind_unstag:.1f} m/s (lambda/(2 Tm) = {vb_m:.1f});"
      f" staggered 4:5: first deep null ~{first_blind_stag:.1f} m/s (theory: lambda/(2 (T2-T1)) = {lam/(2*(T2-T1)):.1f})")
check("stagger pushes first blind speed to lambda/(2|T2-T1|)", first_blind_stag, lam / (2 * (T2 - T1)), 3.0)
check("stagger ratio ~ (n1+n2)/2 = 4.5 x the mean-PRI blind speed", first_blind_stag / vb_m, 4.5, 0.1)

print("=" * 78)
print("4. Rain volume reflectivity")


def mie_backscatter_eff(x, m):
    nmax = int(x + 4 * x ** (1 / 3) + 10)
    n = np.arange(1, nmax + 1)
    def ric(z):
        jn = special.spherical_jn(n, z)
        jnp = special.spherical_jn(n, z, derivative=True)
        return z * jn, jn + z * jnp
    psi_x, dpsi_x = ric(x)
    yn = special.spherical_yn(n, x)
    ynp = special.spherical_yn(n, x, derivative=True)
    jn = special.spherical_jn(n, x)
    jnp = special.spherical_jn(n, x, derivative=True)
    xi = x * (jn + 1j * yn)
    dxi = (jn + 1j * yn) + x * (jnp + 1j * ynp)
    psi_mx, dpsi_mx = ric(m * x)
    a = (m * psi_mx * dpsi_x - psi_x * dpsi_mx) / (m * psi_mx * dxi - xi * dpsi_mx)
    b = (psi_mx * dpsi_x - m * psi_x * dpsi_mx) / (psi_mx * dxi - m * xi * dpsi_mx)
    return np.abs(np.sum((2 * n + 1) * (-1.0) ** n * (a - b))) ** 2 / x ** 2


def water_eps(f_ghz, T_c=20.0):
    th = 300.0 / (T_c + 273.15)
    e0 = 77.66 + 103.3 * (th - 1)
    e1 = 0.0671 * e0
    e2 = 3.52
    fp = 20.20 - 146.0 * (th - 1) + 316.0 * (th - 1) ** 2
    fs = 39.8 * fp
    epp = f_ghz * (e0 - e1) / (fp * (1 + (f_ghz / fp) ** 2)) + f_ghz * (e1 - e2) / (fs * (1 + (f_ghz / fs) ** 2))
    ep = (e0 - e1) / (1 + (f_ghz / fp) ** 2) + (e1 - e2) / (1 + (f_ghz / fs) ** 2) + e2
    return ep - 1j * epp


for Rr in (10.0, 50.0):
    Lam = 4.1 * Rr ** -0.21             # mm^-1
    N0 = 8000.0                          # m^-3 mm^-1
    Z_dsd = N0 * special.gamma(7) / Lam ** 7          # mm^6 m^-3
    Z_mp = 200 * Rr ** 1.6
    print(f"    R = {Rr} mm/h: Z(MP DSD) = {Z_dsd:.0f} mm^6/m^3 ({10*np.log10(Z_dsd):.1f} dBZ), Z = 200R^1.6 -> {Z_mp:.0f} ({10*np.log10(Z_mp):.1f} dBZ), "
          f"296 R^1.47 -> {296*Rr**1.47:.0f}")
    check(f"MP DSD integrates to ~296 R^1.47 (R={Rr})", Z_dsd, 296 * Rr ** 1.47, 0.05, rel=True)
    for fg in (3.0, 10.0, 24.125, 77.0):
        lamr = c / (fg * 1e9)
        eps = water_eps(fg)
        m = np.sqrt(eps)
        K2 = abs((eps - 1) / (eps + 2)) ** 2
        eta_ray = np.pi ** 5 * K2 * Z_dsd * 1e-18 / lamr ** 4          # m^2/m^3
        # Mie integral over drop diameters (mm): sigma_b(D) N(D) dD
        m_bh = np.conj(m)
        Dg = np.linspace(0.05, 7.0, 400)
        sb = np.array([mie_backscatter_eff(np.pi * D * 1e-3 / lamr, m_bh) * np.pi * (D * 1e-3 / 2) ** 2 for D in Dg])
        eta_mie = np.trapezoid(sb * N0 * np.exp(-Lam * Dg), Dg)
        print(f"      {fg:6.2f} GHz: |K|^2 {K2:.3f}; eta Rayleigh {db(eta_ray):7.1f} dB(m^-1), Mie {db(eta_mie):7.1f} dB(m^-1)  (diff {db(eta_mie/eta_ray):+.1f} dB)")
        if fg == 3.0:
            check(f"Rayleigh valid at 3 GHz (R={Rr}): Mie/Rayleigh within 0.6 dB", db(eta_mie / eta_ray), 0.0, 0.6)

print("=" * 78)
print("5. Clutter-cell sizes and signal-to-clutter examples")
# (a) 24 GHz FMCW (IPM-165-like beam 80 x 35 deg), 250 MHz sweep (0.6 m), rain 10 mm/h, drone -15 dBsm at 50 m
lam24 = c / 24.125e9
th, ph = np.radians(80), np.radians(35)
dR = c / (2 * 250e6)
R = 50.0
V = np.pi * R ** 2 * th * ph * dR / (8 * np.log(2))
Rr = 10.0
Lam = 4.1 * Rr ** -0.21
Dg = np.linspace(0.05, 7.0, 400)
m_bh = np.conj(np.sqrt(water_eps(24.125)))
sb = np.array([mie_backscatter_eff(np.pi * D * 1e-3 / lam24, m_bh) * np.pi * (D * 1e-3 / 2) ** 2 for D in Dg])
eta24 = np.trapezoid(sb * 8000 * np.exp(-Lam * Dg), Dg)
sig_rain = eta24 * V
print(f"    24 GHz, 80x35 deg beam, dR {dR:.2f} m, R {R} m: cell volume {V:.0f} m^3; rain 10 mm/h eta {db(eta24):.1f} dB(m^-1) -> sigma_rain {db(sig_rain):.1f} dBsm vs drone -15 dBsm: S/C {-15-db(sig_rain):.1f} dB")
# (b) S-band tracker, 5.8 deg beam, dR 15 m, low grazing 1 deg, grass sigma0 via constant gamma
lam3 = c / 3e9
thaz = np.radians(5.8)
dR3 = 15.0
psi = np.radians(1.0)
for gamma_db, lab in ((-15, "farmland/grass (gamma -15 dB)"), (-10, "wooded/suburban (gamma -10 dB)")):
    for Rg in (1000.0, 3000.0):
        A = Rg * thaz * dR3 / np.cos(psi)
        sig0 = 10 ** (gamma_db / 10) * np.sin(psi)
        sc = sig0 * A
        print(f"    S-band, {lab}, R {Rg/1e3:.0f} km, psi 1 deg: A = {A:.0f} m^2, sigma0 = {db(sig0):.1f} dB, sigma_clutter = {db(sc):.1f} dBsm")
check("surface cell area formula sanity (1 km, 5.8 deg, 15 m)", 1000 * np.radians(5.8) * 15 / np.cos(np.radians(1)), 1518.5, 1.0)

print("=" * 78)
print("6. STAP/SMI sample support: Reed-Mallett-Brennan")
N = 8
s = np.exp(1j * np.pi * 0.3 * np.arange(N)) / np.sqrt(N)
# covariance with strong interference
a_int = np.exp(1j * np.pi * -0.5 * np.arange(N)) / np.sqrt(N)
Rtrue = np.eye(N) + 1e3 * np.outer(a_int, a_int.conj())
Ri = np.linalg.inv(Rtrue)
sinr_opt = np.real(s.conj() @ Ri @ s)
Lc = np.linalg.cholesky(Rtrue)
for K in (8, 16, 32, 64):
    losses = []
    for _ in range(3000):
        X = Lc @ (rng.standard_normal((N, K)) + 1j * rng.standard_normal((N, K))) / np.sqrt(2)
        Rh = X @ X.conj().T / K
        w = np.linalg.solve(Rh, s)
        sinr = np.abs(w.conj() @ s) ** 2 / np.real(w.conj() @ Rtrue @ w)
        losses.append(sinr / sinr_opt)
    rmb = (K + 2 - N) / (K + 1)
    print(f"    N={N}, K={K:3d}: MC mean SINR loss {db(np.mean(losses)):6.2f} dB, RMB {db(rmb):6.2f} dB")
    if K == 16:
        check("RMB: K = 2N -> ~-3 dB", db(np.mean(losses)), db(rmb), 0.3)

print("=" * 78)
print("7. FMCW static-clutter removal (zero-Doppler notch)")
Nc = 128
Tc = 50e-6
lam77 = c / 77e9
n = np.arange(Nc)
static = 10.0 * np.exp(1j * 0.7) * np.ones(Nc)
mover = 0.1 * np.exp(1j * 4 * np.pi * 1.0 * n * Tc / lam77)
x = static + mover
y = x - x.mean()
supp_static = db(np.mean(np.abs((static - static.mean())) ** 2) + 1e-30) - db(np.mean(np.abs(static) ** 2))
Y = np.abs(np.fft.fft(y * np.hanning(Nc)))
X0 = np.abs(np.fft.fft(mover * np.hanning(Nc)))
check("mean-subtraction removes a static reflector completely", float(supp_static < -200), 1.0, 0)
check("mover at 1 m/s passes (peak within 0.1 dB)", 20 * np.log10(Y.max() / X0.max()), 0.0, 0.1)
print(f"    (vibrating or slowly swaying clutter leaks: notch width is ~1 Doppler bin = {lam77/(2*Nc*Tc)*100:.1f} cm/s)")

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
