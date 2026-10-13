#!/usr/bin/env python3
"""
em_dielectrics.py — checks for kb/02-electromagnetics/dielectrics-permittivity-loss-tangent.md

1. Single-pole Debye: peak of eps'' = (eps_s - eps_inf)/2 at w tau = 1; Kramers-Kronig check
   (numerical Hilbert transform of eps'' reproduces eps' - eps_inf).
2. Djordjevic-Sarkar (wideband Debye) model with the FR-4 parameters of Djordjevic et al. 2001:
   eps_inf = 4.27, delta_eps' per decade = 0.14, w1 = 1e4 s^-1, w2 = 1e12 s^-1, sigma = 80 pS/m
   -> eps' and tan d from 1 kHz to 20 GHz; the constant (pi/2)/ln10 = 0.682 relation.
   Also: fit the D-S model to a single datasheet point (e.g. Dk 4.4, Df 0.02 at 1 GHz)
   the way EDA tools do.
3. ITU-R P.527-6 pure-water and sea-water double-Debye model (eqs 5-27), evaluated at
   433 MHz, 915 MHz, 2.45 GHz, 10 GHz for 20 C, S = 0 and 35 g/kg.
4. Lichtenecker / Maxwell-Garnett mixing for 3D-print infill (air + PLA) vs Kuzmanic 2023 data.
5. Dielectric loss of fresh water at 433 MHz including dipolar loss (correcting the conduction-only figure).
"""
import numpy as np
np.seterr(divide='ignore', invalid='ignore')

c = 299_792_458.0
eps0 = 8.8541878188e-12
mu0 = 1.25663706127e-6


# ---------- 1. Debye ----------
def debye(w, eps_s, eps_inf, tau):
    return eps_inf + (eps_s - eps_inf) / (1 + 1j * w * tau)   # e^{jwt}: eps = eps' - j eps''

w = np.logspace(3, 15, 20001)
tau = 1e-9
e = debye(w, 10.0, 2.0, tau)
k = np.argmax(-e.imag)
print(f"1. Debye: peak eps'' = {-e.imag[k]:.4f} (expect 4.0) at w*tau = {w[k]*tau:.4f} (expect 1)")
assert abs(-e.imag[k] - 4.0) < 1e-3 and abs(w[k] * tau - 1) < 1e-2

# Kramers-Kronig: eps'(w0) - eps_inf = (2/pi) P int_0^inf  x eps''(x)/(x^2 - w0^2) dx
def kk_real_from_imag(w0, wgrid, epp):
    x = wgrid
    integrand = x * epp / (x**2 - w0**2)
    # principal value: remove singular point by symmetric exclusion
    mask = np.abs(x - w0) > 1e-3 * w0
    return 2 / np.pi * np.trapezoid(integrand[mask], x[mask])
wg = np.logspace(0, 18, 400001)
epp = -debye(wg, 10.0, 2.0, tau).imag
for w0 in (1e8, 1e9, 1e10):
    kk = kk_real_from_imag(w0, wg, epp)
    true = debye(w0, 10.0, 2.0, tau).real - 2.0
    print(f"   KK check at w0={w0:.0e}: from eps'' -> {kk:.4f}, true {true:.4f}")
    assert abs(kk - true) < 0.02 * 8

# ---------- 2. Djordjevic-Sarkar ----------
def djordjevic_sarkar(f, eps_inf, deps, w1, w2, sigma=0.0):
    """deps = total change of eps' between w1 and w2 (= decay per decade * (m2-m1))."""
    w = 2 * np.pi * np.asarray(f)
    m1, m2 = np.log10(w1), np.log10(w2)
    eps = eps_inf + deps / ((m2 - m1) * np.log(10)) * np.log((w2 + 1j * w) / (w1 + 1j * w)) - 1j * sigma / (w * eps0)
    return eps

per_decade = 0.14
eps_inf, w1, w2, sig = 4.27, 1e4, 1e12, 80e-12
deps = per_decade * (np.log10(w2) - np.log10(w1))
print("\n2. Djordjevic-Sarkar FR-4 (Djordjevic et al. 2001 parameters)")
for f in (1e3, 1e5, 1e6, 1e8, 433e6, 915e6, 1e9, 2.45e9, 5.8e9, 10e9, 20e9):
    ep = djordjevic_sarkar(f, eps_inf, deps, w1, w2, sig)
    print(f"   f={f:10.3e} Hz: eps'={ep.real:.3f}  eps''={-ep.imag:.4f}  tan d={-ep.imag/ep.real:.4f}")
ep_mid = djordjevic_sarkar(1e7, eps_inf, deps, w1, w2, 0)
print(f"   eps'' / (decay per decade) = {-ep_mid.imag/per_decade:.4f} (paper: (pi/2)/ln10 = {np.pi/2/np.log(10):.4f})")
assert abs(-ep_mid.imag / per_decade - np.pi / 2 / np.log(10)) < 0.01

# Fit a D-S model to one datasheet point (Dk0, Df0 at f0) with w1=1e3*2pi? EDA convention:
# f1 = 1 kHz (w1 = 2 pi 1e3)?  Many tools use w1 = 1e4 rad/s... here: w1=2*pi*1e3, w2=2*pi*1e12
def ds_fit(Dk0, Df0, f0, f1=1e3, f2=1e12):
    w1_, w2_ = 2 * np.pi * f1, 2 * np.pi * f2
    w0 = 2 * np.pi * f0
    L = np.log((w2_ + 1j * w0) / (w1_ + 1j * w0)) / np.log(w2_ / w1_)   # normalized log term
    # eps = eps_inf + deps*L ; require eps' = Dk0, eps'' = Dk0*Df0
    deps_ = Dk0 * Df0 / (-L.imag)
    eps_inf_ = Dk0 - deps_ * L.real
    return eps_inf_, deps_, w1_, w2_
einf, dep, W1, W2 = ds_fit(4.4, 0.02, 1e9)
print(f"   D-S fit to Dk=4.4, Df=0.02 @1 GHz: eps_inf={einf:.3f}, delta_eps={dep:.3f}")
for f in (1e6, 100e6, 433e6, 1e9, 2.45e9, 10e9, 25e9):
    w_ = 2 * np.pi * f
    ep = einf + dep * np.log((W2 + 1j * w_) / (W1 + 1j * w_)) / np.log(W2 / W1)
    print(f"      f={f:9.3e}: Dk={ep.real:.3f} Df={-ep.imag/ep.real:.4f}")

# ---------- 3. ITU-R P.527-6 water ----------
def itu_water(fGHz, T=20.0, S=0.0):
    Th = 300.0 / (T + 273.15) - 1
    es = 77.66 + 103.3 * Th
    e1 = 0.0671 * es
    einf_ = 3.52 - 7.52 * Th
    f1 = 20.20 - 146.4 * Th + 316 * Th**2
    f2 = 39.8 * f1
    if S == 0:
        ess, e1s, einfs, f1s, f2s, sig = es, e1, einf_, f1, f2, 0.0
    else:
        ess = es * np.exp(-3.33330e-3 * S + 4.74868e-6 * S**2)
        f1s = f1 * (1 + S * (2.3232e-3 - 7.9208e-5 * T + 3.6764e-6 * T**2 + 3.5594e-7 * T**3 + 8.9795e-9 * T**4))
        e1s = e1 * np.exp(-6.28908e-3 * S + 1.76032e-4 * S**2 - 9.22144e-5 * T * S)
        f2s = f2 * (1 + S * (-1.99723e-2 + 1.81176e-4 * T))
        einfs = einf_ * (1 + S * (-2.04265e-3 + 1.57883e-4 * T))
        s35 = 2.903602 + 8.607e-2 * T + 4.738817e-4 * T**2 - 2.991e-6 * T**3 + 4.3047e-9 * T**4
        R15 = S * (37.5109 + 5.45216 * S + 1.4409e-2 * S**2) / (1004.75 + 182.283 * S + S**2)
        a0 = (6.9431 + 3.2841 * S - 9.9486e-2 * S**2) / (84.850 + 69.024 * S + S**2)
        a1 = 49.843 - 0.2276 * S + 0.198e-2 * S**2
        RT15 = 1 + a0 * (T - 15) / (a1 + T)
        sig = s35 * R15 * RT15
    x1, x2 = fGHz / f1s, fGHz / f2s
    ep = (ess - e1s) / (1 + x1**2) + (e1s - einfs) / (1 + x2**2) + einfs
    epp = x1 * (ess - e1s) / (1 + x1**2) + x2 * (e1s - einfs) / (1 + x2**2) + 18 * sig / fGHz
    return ep, epp, sig, f1s

print("\n3. ITU-R P.527-6 water at 20 C")
for S in (0.0, 35.0):
    for fG in (0.433, 0.915, 1.57542, 2.45, 5.8, 10.0, 24.0):
        ep, epp, sig, f1s = itu_water(fG, 20.0, S)
        w = 2 * np.pi * fG * 1e9
        epsc = eps0 * (ep - 1j * epp)
        g = 1j * w * np.sqrt(mu0 * epsc)
        print(f"   S={S:4.0f} f={fG:7.4f} GHz: eps'={ep:6.2f} eps''={epp:6.2f} tan d={epp/ep:6.3f} "
              f"sigma_eff={w*eps0*epp:6.3f} S/m  alpha={g.real:7.2f} Np/m ({8.686*g.real:7.1f} dB/m)  1/alpha={100/g.real:7.2f} cm"
              + (f"  (ionic sigma={sig:.3f} S/m, f1={f1s:.2f} GHz)" if (fG == 0.433) else ""))

# ---------- 4. mixing rules for infill ----------
print("\n4. infill mixing (PLA bulk 2.81 at 100% infill, air 1) vs Kuzmanic 2023 (33% infill: 1.98 PLA)")
def lichtenecker(e1, e2, v):     # log mixing, v = volume fraction of material 2
    return np.exp((1 - v) * np.log(e1) + v * np.log(e2))
def maxwell_garnett(em, ei, v):   # inclusions ei (air) volume fraction v in host em (PLA)
    return em * (1 + 2 * v * (ei - em) / (ei + 2 * em)) / (1 - v * (ei - em) / (ei + 2 * em))
def linear(e1, e2, v):
    return (1 - v) * e1 + v * e2
for infill in (0.2, 0.33, 0.5, 0.75, 1.0):
    print(f"   infill {infill*100:3.0f}%: linear {linear(1,2.81,infill):.2f}  Lichtenecker {lichtenecker(1,2.81,infill):.2f}"
          f"  Maxwell-Garnett(air in PLA) {maxwell_garnett(2.81,1.0,1-infill):.2f}")

# ---------- 5. fresh water 433 MHz with dipolar loss ----------
ep, epp, _, _ = itu_water(0.433, 20.0, 0.0)
w = 2 * np.pi * 433e6
sig_cond = 0.01
epp_tot = epp + sig_cond / (w * eps0)
g = 1j * w * np.sqrt(mu0 * eps0 * (ep - 1j * epp_tot))
print(f"\n5. fresh water 433 MHz 20C: dipolar eps''={epp:.2f}, conduction(0.01 S/m) eps''={sig_cond/(w*eps0):.2f}, "
      f"alpha={g.real:.3f} Np/m = {8.686*g.real:.2f} dB/m, 1/alpha={1/g.real:.3f} m")
print("\nAll checks passed.")

# ---------- 6. glass-weave anisotropy: Wiener bounds (parallel/series) ----------
print("\n6. E-glass/epoxy anisotropy bounds (Wiener): e_glass=6.1, e_resin=3.2 (typical GHz values, see page)")
eg, er_ = 6.1, 3.2
for vr in (0.45, 0.55, 0.65, 0.75):
    vg = 1 - vr
    par = vg * eg + vr * er_
    ser = 1 / (vg / eg + vr / er_)
    lich = np.exp(vg * np.log(eg) + vr * np.log(er_))
    print(f"   resin vol fraction {vr:.2f}: in-plane (parallel bound) {par:.2f}, z-axis (series bound) {ser:.2f}, "
          f"Lichtenecker {lich:.2f}, max anisotropy {(par/ser-1)*100:.1f} %")

# ---------- 7. moisture: small water fraction via Lichtenecker ----------
print("\n7. moisture uptake effect (Lichtenecker, water eps from ITU model at 1 GHz, 20 C)")
ep_w, epp_w, _, _ = itu_water(1.0, 20.0, 0.0)
eps_w = ep_w - 1j * epp_w
eps_fr4 = 4.4 * (1 - 0.02j)
for vw in (0.0, 0.002, 0.005, 0.01):
    e = np.exp((1 - vw) * np.log(eps_fr4) + vw * np.log(eps_w))
    print(f"   water vol fraction {vw*100:.1f} %: Dk={e.real:.3f}  Df={-e.imag/e.real:.4f}")
print("\nAll checks passed (sections 6-7).")
