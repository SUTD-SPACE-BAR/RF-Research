#!/usr/bin/env python3
"""
Verification for kb/04-real-components-hf/inductors-at-rf.md

  1. Nagaoka coefficient kL of a current-sheet solenoid, computed three independent ways:
       (a) Lorenz/Nagaoka closed form with complete elliptic integrals,
       (b) direct numerical double integration of Maxwell's coaxial-loop mutual inductance,
       (c) Lundin's 1985 handbook formula (claimed < 3 ppm);
     and the error of Wheeler's long-coil formula kW = 1/(1 + 0.45 D/l).
  2. Rosa round-wire corrections (ks, km) -> practical air-coil inductance; worked 433/915 MHz coils.
  3. Coilcraft 0402HP datasheet: single-pole L(f) model with datasheet SRF vs published L at 900 MHz/1.7 GHz;
     parallel capacitance implied by SRF.
  4. Skin depth in copper and a crude AC-resistance/Q estimate.
Run: python3 tools/verify/components_inductors.py
"""
import numpy as np
from scipy.special import ellipk, ellipe, ellipkm1
from scipy import integrate

MU0 = 4e-7 * np.pi

def kL_elliptic(D_over_l):
    """Nagaoka coefficient via Lorenz's formula; modulus k^2 = D^2/(D^2+l^2)."""
    x = D_over_l
    k2 = x**2 / (1 + x**2)
    k = np.sqrt(k2)
    kp2 = 1 - k2
    K = ellipk(k2); E = ellipe(k2)   # scipy uses parameter m = k^2
    # Nagaoka: kL = 4/(3 pi) * (1/k') * [ (k'^2/k^2)(K - E) + E - k ]
    kp = np.sqrt(kp2)
    return 4 / (3 * np.pi) * (1 / kp) * ((kp2 / k2) * (K - E) + E - k)

def M_loops(a, d):
    """Maxwell: mutual inductance of two coaxial circles radius a, axial separation d."""
    p = d**2 / (4 * a**2 + d**2)          # complementary parameter 1 - k^2 (avoids K(1) overflow)
    k2 = 1 - p
    k = np.sqrt(k2)
    return MU0 * a * ((2 / k - k) * ellipkm1(p) - 2 / k * ellipe(k2))

def kL_numeric(D_over_l, a=1.0):
    D = 2 * a; l = D / D_over_l
    # current sheet with n = N/l turns per metre: L = n^2 * int_{-l}^{l} (l - |d|) M(d) dd ; singular at d=0 (log), integrable
    f = lambda d: (l - d) * M_loops(a, d)
    val, err = integrate.quad(f, 0, l, limit=500, epsabs=0, epsrel=1e-11)
    Lsheet_per_n2 = 2 * val
    Llong_per_n2 = MU0 * np.pi * a**2 * l      # mu0 pi a^2 N^2 / l with N = n l
    return Lsheet_per_n2 / Llong_per_n2

def kL_lundin(D_over_l):
    x = D_over_l; xx = x * x
    if x < 1:
        return (1 + 0.383901 * xx + 0.017108 * xx**2) / (1 + 0.258952 * xx) - 4 * x / (3 * np.pi)
    num = (np.log(4 * x) - 0.5) * (1 + 0.383901 / xx + 0.017108 / xx**2)
    den = 1 + 0.258952 / xx
    kk = 0.093842 / xx + 0.002029 / xx**2 - 0.000801 / xx**3
    return 2 * (num / den + kk) / (np.pi * x)

def kL_wheeler(D_over_l):
    return 1 / (1 + 0.45 * D_over_l)

print("=== 1. Nagaoka coefficient ===")
print(" l/D    elliptic     numeric      Lundin      Wheeler(err %)")
for l_over_D in [0.1, 0.2, 0.4, 0.5, 0.8, 1.0, 2.0, 5.0, 10.0]:
    x = 1 / l_over_D
    ke = kL_elliptic(x); kn = kL_numeric(x); kl = kL_lundin(x); kw = kL_wheeler(x)
    print(f"{l_over_D:5.2f}  {ke:.7f}  {kn:.7f}  {kl:.7f}  {kw:.5f} ({(kw/ke-1)*100:+.2f} %)")
    assert abs(ke - kn) < 2e-6 and abs(ke - kl) / ke < 5e-6
print(f"check: kL(l/D=1) = {kL_elliptic(1.0):.6f} (Knight/Lundin: 0.688423)")
assert abs(kL_elliptic(1.0) - 0.688423) < 2e-6
# Wheeler's stated accuracy: +-1% for b > 0.8a (l > 0.4 D)
xs = 1 / np.linspace(0.4, 50, 2000)
errs = np.array([kL_wheeler(x) / kL_elliptic(x) - 1 for x in xs])
print(f"Wheeler max |error| for l >= 0.4 D: {np.max(np.abs(errs))*100:.3f} %")

print("\n=== 2. Practical air coils (Rosa corrections, HF limit) ===")
def gamma_m(m):
    return (m**2 + 1) * np.log(m) + 1.5 - (m + 1)**2 / 2 * np.log(m + 1) - ((m - 1)**2 / 2 * np.log(m - 1) if m > 1 else 0)
def km_rosa(N):
    return 2 / N * sum((N - m) * gamma_m(m) for m in range(1, N))
print("  Rosa km(N): " + ", ".join(f"N={N}: {km_rosa(N):.4f}" for N in [2, 3, 5, 10, 100, 2000]))
def air_coil(N, D_mean, pitch, d_wire, hf=True):
    l = N * pitch
    r = D_mean / 2
    Ls = MU0 * np.pi * r**2 * N**2 / l * kL_elliptic(D_mean / l)
    ks = (1.5 if hf else 1.25) - np.log(2 * pitch / d_wire)
    L = Ls - MU0 * r * N * (ks + km_rosa(N))
    return Ls, L, ks
for (N, Dm, p, dw, tag) in [(5, 3.5e-3, 1.0e-3, 0.5e-3, "5 t, 3 mm ID, 0.5 mm wire, 1 mm pitch"),
                            (3, 3.5e-3, 1.0e-3, 0.5e-3, "3 t, same"),
                            (8, 2.5e-3, 0.6e-3, 0.4e-3, "8 t, 2.1 mm ID, 0.4 mm wire, 0.6 mm pitch")]:
    Ls, L, ks = air_coil(N, Dm, p, dw)
    kw = kL_wheeler(Dm / (N * p))
    Lw = MU0 * np.pi * (Dm / 2)**2 * N**2 / (N * p) * kw
    print(f"  {tag}: current-sheet {Ls*1e9:.2f} nH (Wheeler {Lw*1e9:.2f}), Rosa-corrected {L*1e9:.2f} nH (ks={ks:.3f}, km={km_rosa(N):.3f})")
    for f in [433.92e6, 915e6]:
        print(f"      X at {f/1e6:.0f} MHz = {2*np.pi*f*L:.1f} ohm")

a3 = air_coil(3, 3.5e-3, 1.0e-3, 0.5e-3)[1]; b3 = air_coil(3, 3.5e-3, 1.3e-3, 0.5e-3)[1]
print(f"  tuning: 3-turn coil pitch 1.0 -> 1.3 mm: {a3*1e9:.2f} -> {b3*1e9:.2f} nH ({(b3/a3-1)*100:+.1f} %)")

print("\n=== 3. Coilcraft 0402HP: one-pole L(f) model vs datasheet ===")
rows = [  # (name, L_nom nH at 250 MHz, L@900, L@1.7G, SRF GHz)
    ("2N2", 2.2, 2.17, 2.17, 15.1), ("6N8", 6.8, 6.78, 6.97, 5.80), ("10N", 10.0, 9.98, 10.4, 4.70),
    ("22N", 22.0, 22.3, 24.4, 3.30), ("47N", 47.0, 49.0, 58.9, 2.40), ("68N (HPH)", 68.0, 72.2, 91.4, 1.84)]
print(" part   L900 meas/model   L1700 meas/model   C_par from SRF   SRF implied by L(1.7G)")
for name, L0, L9, L17, srf in rows:
    m9 = L0 / (1 - (0.9 / srf)**2); m17 = L0 / (1 - (1.7 / srf)**2)
    Cp = 1 / ((2 * np.pi * srf * 1e9)**2 * L0 * 1e-9)
    ratio = L0 / L17
    srf_imp = 1.7 / np.sqrt(1 - ratio) if ratio < 1 else np.inf
    print(f" {name:9s} {L9:6.2f}/{m9:6.2f}     {L17:6.2f}/{m17:6.2f}       {Cp*1e15:6.1f} fF        {srf_imp:6.2f} GHz (datasheet {srf})")

print("\n=== 4. Skin depth and AC resistance ===")
rho = 1.68e-8
for f in [433.92e6, 915e6, 2450e6]:
    delta = np.sqrt(rho / (np.pi * f * MU0))
    print(f"  Cu skin depth at {f/1e6:.0f} MHz = {delta*1e6:.2f} um")
# crude Q estimate for the 5-turn air coil at 433.92 MHz: wire length, R = rho*len/(pi d delta) (x proximity factor ~2)
N, Dm, dw = 5, 3.5e-3, 0.5e-3
length = N * np.pi * Dm
f = 433.92e6
delta = np.sqrt(rho / (np.pi * f * MU0))
Rac = rho * length / (np.pi * dw * delta)
Ls, L, _ = air_coil(5, 3.5e-3, 1e-3, 0.5e-3)
X = 2 * np.pi * f * L
print(f"  5-turn coil: wire length {length*1e3:.1f} mm, isolated-wire R_ac = {Rac*1e3:.1f} mohm, X = {X:.1f} ohm ->"
      f" Q(no proximity) = {X/Rac:.0f}; with proximity factor 2-3: Q ~ {X/(3*Rac):.0f}-{X/(2*Rac):.0f}")
print("OK")
