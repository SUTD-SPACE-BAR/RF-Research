#!/usr/bin/env python3
"""
em_fresnel_radome.py — checks for kb/02-electromagnetics/boundary-conditions-reflection-refraction.md

1. Fresnel coefficients (TE = s = perpendicular, TM = p = parallel) for complex media, with the
   convention Gamma = E_r/E_i for TE and H-based sign for TM noted; Brewster and critical angles.
2. Energy conservation check |r|^2 + Re(...)|t|^2 = 1 for lossless media.
3. Multilayer transfer (characteristic) matrix for oblique incidence, both polarizations:
   - half-wave wall, thin wall, A-sandwich
   - fibreglass (G10/FR-4 class) nose cone at 433 / 915 MHz / 2.45 / 5.8 GHz
   - carbon-fibre (conducting) wall transmission.
4. Sea and ground reflection vs grazing angle, H and V polarization (pseudo-Brewster).
5. Metal reflection loss: 1 - |Gamma|^2 ~ 4 Rs/eta0.
"""
import numpy as np

c = 299_792_458.0
mu0 = 1.25663706127e-6
eps0 = 1 / (mu0 * c**2)
eta0 = mu0 * c


def eps_c(er, tand=0.0, sigma=0.0, f=1e9):
    """complex relative permittivity, e^{jwt} convention: er' (1 - j tand) - j sigma/(w eps0)"""
    return er * (1 - 1j * tand) - 1j * sigma / (2 * np.pi * f * eps0)


def fresnel(n1_eps, n2_eps, theta_i):
    """Fresnel reflection/transmission for fields, media given by complex relative permittivity
    (non-magnetic). theta_i in radians (real, in medium 1, assumed lossless).
    TE (s): r = (n1 cos i - n2 cos t)/(n1 cos i + n2 cos t)  (E-field ratio)
    TM (p): r = (n2 cos i - n1 cos t)/(n2 cos i + n1 cos t)  (E-field ratio, 'Born & Wolf/Pozar' sign
            such that r_TM -> -r_TE ... see page for sign conventions)."""
    n1 = np.sqrt(n1_eps); n2 = np.sqrt(n2_eps)
    ci = np.cos(theta_i)
    st = n1 * np.sin(theta_i) / n2
    ct = np.sqrt(1 - st**2 + 0j)
    if np.imag(ct) > 0:            # choose decaying branch for e^{-j k z}: Im(n2 ct) < 0
        ct = -ct
    if np.real(n2 * ct) < 0:
        ct = -ct
    rTE = (n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)
    tTE = 2 * n1 * ci / (n1 * ci + n2 * ct)
    rTM = (n2 * ci - n1 * ct) / (n2 * ci + n1 * ct)
    tTM = 2 * n1 * ci / (n2 * ci + n1 * ct)
    return rTE, tTE, rTM, tTM, ct


print("=== 1. Fresnel air -> glass-like dielectric (er = 4.5) ===")
er2 = 4.5
thB = np.degrees(np.arctan(np.sqrt(er2)))
print(f"Brewster angle air->er {er2}: {thB:.2f} deg")
for th in (0, 30, 45, thB, 70, 85):
    rTE, tTE, rTM, tTM, ct = fresnel(1.0, er2, np.radians(th))
    # power check for lossless: R + T = 1, T = Re(n2 ct)/(n1 ci) |t|^2 (TE), for TM: Re(n2* ct)/(n1 ci)... use impedance form
    n1, n2 = 1.0, np.sqrt(er2)
    TTE = np.real(n2 * ct) / (n1 * np.cos(np.radians(th))) * abs(tTE)**2
    TTM = np.real(n2 * ct) / (n1 * np.cos(np.radians(th))) * abs(tTM)**2  # with tTM defined as E ratio? see below
    print(f"  theta={th:6.2f}: |rTE|={abs(rTE):.4f} |rTM|={abs(rTM):.4f}  R_TE+T_TE={abs(rTE)**2+TTE:.6f}")
    assert abs(abs(rTE)**2 + TTE - 1) < 1e-9
rTE, tTE, rTM, tTM, _ = fresnel(1.0, er2, np.radians(thB))
assert abs(rTM) < 1e-12
print("  TM reflection vanishes at Brewster angle: OK; energy conserved for TE: OK")

# TIR
er_hi = 4.5
thc = np.degrees(np.arcsin(1 / np.sqrt(er_hi)))
print(f"critical angle er {er_hi} -> air: {thc:.2f} deg")
rTE, _, rTM, _, ct = fresnel(er_hi, 1.0, np.radians(60))
f = 5.8e9; lam0 = c / f
kz_air = 2 * np.pi / lam0 * ct          # complex; e^{-j kz z}
print(f"  at 60 deg: |rTE|={abs(rTE):.6f}, |rTM|={abs(rTM):.6f} (TIR); evanescent 1/e depth in air at 5.8 GHz "
      f"= {1/abs(np.imag(kz_air))*1e3:.2f} mm (lambda0 = {lam0*1e3:.1f} mm)")
assert abs(abs(rTE) - 1) < 1e-12 and abs(abs(rTM) - 1) < 1e-12


# ---------- 3. multilayer transfer matrix ----------
def slab_stack(f, layers, theta_i_deg, pol, eps_in=1.0, eps_out=1.0):
    """layers: list of (eps_r_complex, thickness_m). Returns (Gamma, T) complex amplitude
    reflection and transmission (tangential-field based) and power transmission/reflection.
    Uses the characteristic-matrix method with wave impedances Z = eta/cos(theta) (TE) or
    eta cos(theta) (TM)."""
    th = np.radians(theta_i_deg)
    k0 = 2 * np.pi * f / c
    kx = k0 * np.sqrt(eps_in) * np.sin(th)
    def Zw(eps):
        n = np.sqrt(eps + 0j)
        kz = np.sqrt(k0**2 * eps - kx**2 + 0j)
        if np.imag(kz) > 0:
            kz = -kz
        eta = eta0 / n
        cos_t = kz / (k0 * n)
        return (eta / cos_t if pol == 'TE' else eta * cos_t), kz
    Zin, _ = Zw(eps_in)
    Zout, _ = Zw(eps_out)
    M = np.eye(2, dtype=complex)
    for eps, d in layers:
        Z, kz = Zw(eps)
        dphi = kz * d
        Mi = np.array([[np.cos(dphi), 1j * Z * np.sin(dphi)], [1j * np.sin(dphi) / Z, np.cos(dphi)]])
        M = M @ Mi
    A, B, C, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    Zl = (A * Zout + B) / (C * Zout + D)                # impedance looking into stack
    G = (Zl - Zin) / (Zl + Zin)
    # transmission of power into output half-space
    # V_in = V+ (1+G); relation V_out = V_in / (A + B/Zout)
    Vin = 1 + G
    Vout = Vin / (A + B / Zout)
    Pin_inc = 1 / np.real(1 / np.conj(Zin)) if False else 1.0
    T_pow = (abs(Vout)**2 * np.real(1 / Zout)) / (np.real(1 / Zin))
    R_pow = abs(G)**2
    return G, R_pow, T_pow


def dB(x):
    return 10 * np.log10(x)


# G10 / fibreglass-epoxy: er ~ 4.7, tand ~ 0.02 (see dielectrics page for sources)
er_fg, td_fg = 4.7, 0.02
print("\n=== 3a. half-wave wall thickness (normal incidence) and insertion loss ===")
for f in (433e6, 915e6, 2.45e9, 5.8e9):
    lam_d = c / f / np.sqrt(er_fg)
    t_half = lam_d / 2
    G, R, T = slab_stack(f, [(eps_c(er_fg, td_fg), t_half)], 0, 'TE')
    print(f"  f={f/1e9:5.3f} GHz: lambda_d/2 = {t_half*1e3:6.1f} mm; |G|^2 = {R:.2e}; IL = {-dB(T):.3f} dB (loss only)")

print("\n=== 3b. thin fibreglass nose cone wall (er 4.7, tan d 0.02) insertion loss, normal & 45 deg ===")
for f in (433e6, 915e6, 2.45e9, 5.8e9, 24e9):
    row = []
    for t in (1e-3, 2e-3, 3e-3, 5e-3):
        G, R, T = slab_stack(f, [(eps_c(er_fg, td_fg), t)], 0, 'TE')
        G45e, R45e, T45e = slab_stack(f, [(eps_c(er_fg, td_fg), t)], 45, 'TE')
        G45m, R45m, T45m = slab_stack(f, [(eps_c(er_fg, td_fg), t)], 45, 'TM')
        row.append(f"t={t*1e3:.0f}mm: {-dB(T):.3f}/{-dB(T45e):.3f}/{-dB(T45m):.3f}")
    print(f"  f={f/1e9:6.3f} GHz  IL dB (0deg / 45deg TE / 45deg TM): " + "; ".join(row))

# thin wall rule of thumb t < lambda_d/20 ?
print("\n=== 3c. max thickness for |Gamma|^2 < 1% (-20 dB) and < 10% at normal incidence ===")
for f in (433e6, 915e6, 2.45e9, 5.8e9):
    ts = np.linspace(1e-5, 0.03, 30000)
    Rs = np.array([slab_stack(f, [(eps_c(er_fg, 0), t)], 0, 'TE')[1] for t in ts])
    t1 = ts[np.argmax(Rs > 0.01)]
    t10 = ts[np.argmax(Rs > 0.1)]
    lam_d = c / f / np.sqrt(er_fg)
    print(f"  f={f/1e9:5.3f} GHz: |G|^2<1% for t < {t1*1e3:.2f} mm (= lambda_d/{lam_d/t1:.0f}); <10% for t < {t10*1e3:.2f} mm")

print("\n=== 3d. A-sandwich (0.5 mm skins er 4.7 + foam core er 1.1), 5.8 GHz ===")
f = 5.8e9
for core in (5e-3, 10e-3, 12.4e-3, 15e-3):
    G, R, T = slab_stack(f, [(eps_c(4.7, 0.02), 0.5e-3), (eps_c(1.1, 0.002), core), (eps_c(4.7, 0.02), 0.5e-3)], 0, 'TE')
    print(f"  core {core*1e3:5.1f} mm: |G|^2 = {R:.4f} ({dB(R):.1f} dB), IL = {-dB(T):.3f} dB")
lam_core = c / f / np.sqrt(1.1)
print(f"  (quarter wave in core = {lam_core/4*1e3:.1f} mm)")

print("\n=== 3e. carbon-fibre composite wall (conductive) ===")
for sigma in (1e3, 1e4, 3e4):
    for f in (433e6, 915e6, 1.575e9):
        G, R, T = slab_stack(f, [(eps_c(10, 0, sigma, f), 1e-3)], 0, 'TE')
        delta = 1 / np.sqrt(np.pi * f * mu0 * sigma)
        print(f"  sigma={sigma:7.0f} S/m, f={f/1e6:7.1f} MHz, 1 mm wall: skin depth {delta*1e3:.3f} mm, "
              f"|G|^2={R:.4f}, transmission = {dB(T):7.1f} dB")

print("\n=== 4. reflection from sea and ground vs grazing angle (433 MHz) ===")
# sea (ITU-R P.527 at 433 MHz, 20C, 35 ppt): eps' = 71.6, eps'' = 200.6
sea = 71.64 - 1j * 200.56
ground = eps_c(15, 0, 0.005, 433e6)   # illustrative 'medium' ground (see page)
for name, epsg in (("sea", sea), ("medium ground (15, 5 mS/m)", ground)):
    print(f"  {name}: eps = {epsg:.2f}")
    best = (1e9, None)
    for psi in (0.5, 1, 2, 5, 7, 10, 20, 30, 60, 90):
        th = np.radians(90 - psi)
        rTE, _, rTM, _, _ = fresnel(1.0, epsg, th)
        print(f"    grazing {psi:5.1f} deg: |R_H|={abs(rTE):.3f} ang {np.degrees(np.angle(rTE)):7.1f} | "
              f"|R_V|={abs(rTM):.3f} ang {np.degrees(np.angle(rTM)):7.1f}")
    psis = np.linspace(0.05, 89.9, 20000)
    rv = np.array([abs(fresnel(1.0, epsg, np.radians(90 - p))[2]) for p in psis])
    k = np.argmin(rv)
    print(f"    pseudo-Brewster (min |R_V|) at grazing {psis[k]:.2f} deg, |R_V|min = {rv[k]:.3f}")

print("\n=== 5. metal reflection loss ===")
for f in (433e6, 2.45e9, 24e9):
    sigma = 5.8e7
    Rs = np.sqrt(np.pi * f * mu0 / sigma)
    eps_cu = eps_c(1, 0, sigma, f)
    rTE, _, _, _, _ = fresnel(1.0, eps_cu, 0.0)
    print(f"  Cu f={f/1e9:.3f} GHz: 1-|G|^2 = {1-abs(rTE)**2:.3e}; 4Rs/eta0 = {4*Rs/eta0:.3e}")
    assert abs((1 - abs(rTE)**2) - 4 * Rs / eta0) / (4 * Rs / eta0) < 1e-3
print("\nAll checks passed.")
