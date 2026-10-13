#!/usr/bin/env python3
"""
prop_two_ray.py — verification for kb/09-propagation-link-budget/two-ray-ground-reflection.md

Flat-earth two-ray model with exact (complex) Fresnel reflection coefficients for a lossy ground,
for horizontal (TE, E parallel to ground) and vertical (TM, E in the plane of incidence) polarisation.

  E/E0 = 1 + Gamma(psi) * (d_dir/d_ref) * exp(-j k (d_ref - d_dir))        (isotropic antennas)
  Pr   = Pt Gt Gr (lambda/(4 pi d_dir))^2 |E/E0|^2

Checks:
  1. Breakpoint distance d_c = 4 h1 h2/lambda (last maximum ~ 2 h1 h2... definitions) and the 1/d^4 regime:
     for d >> d_c and Gamma -> -1:  L = 40 log d - 20 log(h1 h2)  (d, h in m).
  2. Pseudo-Brewster angle for vertical polarisation.
  3. "Minimum effective antenna height" at grazing: h_eff = |h - j/(k z)|, with
     z = sqrt(eps_c - 1) (H-pol), z = sqrt(eps_c - 1)/eps_c (V-pol): h0 = lambda/(2 pi |z|).
     Compared with the exact two-ray result for a very low antenna.
  4. Ground-station elevation lobing: null elevations sin(theta_n) ~ n lambda/(2 h) for Gamma ~ -1.
  5. Landed rocket (antenna near the ground) at 433 / 915 MHz, H vs V polarisation, 1-20 km.
  6. Rocket on the pad (antenna 2-5 m) to a GS 1-5 km away.

Ground constants: ITU-R P.527 legacy categories (medium dry ground eps_r ~ 15, sigma ~ 1e-3 S/m;
wet ground 30, 1e-2; sea water 70, 5; very dry 3, 1e-4). Reliability: typical values only.
"""
import numpy as np
c = 299792458.0

GROUNDS = {'very dry': (3.0, 1e-4), 'medium dry': (15.0, 1e-3), 'wet ground': (30.0, 1e-2), 'sea water': (70.0, 5.0)}

def eps_c(f, er, sig):
    return er - 1j*sig/(2*np.pi*f*8.8541878128e-12)   # = er - j 60 sigma lambda

def gamma(psi, f, er, sig, pol):
    """Fresnel reflection coefficient vs grazing angle psi (rad)."""
    e = eps_c(f, er, sig)
    s, cs = np.sin(psi), np.cos(psi)
    root = np.sqrt(e - cs**2)
    if pol == 'H':
        return (s - root)/(s + root)
    return (e*s - root)/(e*s + root)

def two_ray_loss(d, h1, h2, f, er, sig, pol):
    """Basic transmission loss (dB) between isotropic antennas, flat earth."""
    lam = c/f; k = 2*np.pi/lam
    d = np.asarray(d, float)
    rd = np.sqrt(d**2 + (h1 - h2)**2)
    rr = np.sqrt(d**2 + (h1 + h2)**2)
    psi = np.arctan((h1 + h2)/d)
    G = gamma(psi, f, er, sig, pol)
    E = 1 + G*(rd/rr)*np.exp(-1j*k*(rr - rd))
    return 20*np.log10(4*np.pi*rd/lam) - 20*np.log10(np.abs(E))

def fspl(d, f):
    return 20*np.log10(4*np.pi*d*f/c)

if __name__ == "__main__":
    print("=== 1. Breakpoint and 1/d^4 regime ===")
    f = 433.125e6; lam = c/f
    h1, h2 = 2.0, 5.0
    dc = 4*h1*h2/lam
    print(f"  433 MHz, h1={h1} m, h2={h2} m: d_c = 4 h1 h2/lambda = {dc:.1f} m")
    for d in (20, 50, 100, dc/2, dc, 2*dc, 1e3, 5e3, 20e3):
        Lh = two_ray_loss(d, h1, h2, f, *GROUNDS['medium dry'], 'H')
        Lv = two_ray_loss(d, h1, h2, f, *GROUNDS['medium dry'], 'V')
        Lpe = 40*np.log10(d) - 20*np.log10(h1*h2)
        print(f"  d={d:8.0f} m: FSPL {fspl(d,f):6.1f}  two-ray H {Lh:6.1f}  V {Lv:6.1f}  plane-earth {Lpe:6.1f} dB")
    # slope check far beyond breakpoint
    d_a, d_b = 10e3, 100e3
    s = (two_ray_loss(d_b, h1, h2, f, *GROUNDS['medium dry'], 'H') - two_ray_loss(d_a, h1, h2, f, *GROUNDS['medium dry'], 'H'))
    print(f"  slope 10 -> 100 km (H pol): {s:.2f} dB/decade (expect 40)")

    print("\n=== 2. Pseudo-Brewster angle (V pol, |Gamma| minimum) ===")
    psi = np.radians(np.linspace(0.01, 90, 90000))
    for name, (er, sig) in GROUNDS.items():
        for ff in (433.125e6, 915e6):
            gv = np.abs(gamma(psi, ff, er, sig, 'V'))
            i = np.argmin(gv)
            print(f"  {name:10s} f={ff/1e6:6.1f} MHz: psi_B = {np.degrees(psi[i]):5.2f} deg, |Gamma_V|min = {gv[i]:.3f}; "
                  f"lossless arctan(1/sqrt(er)) = {np.degrees(np.arctan(1/np.sqrt(er))):5.2f} deg")

    print("\n=== 3. Minimum effective antenna height at grazing ===")
    for ff in (433.125e6, 915e6):
        lam = c/ff; k = 2*np.pi/lam
        for name in ('medium dry', 'wet ground', 'sea water'):
            e = eps_c(ff, *GROUNDS[name])
            zH = np.sqrt(e - 1); zV = np.sqrt(e - 1)/e
            print(f"  {ff/1e6:6.1f} MHz {name:10s}: h0(H) = {1/(k*abs(zH))*100:6.2f} cm, h0(V) = {1/(k*abs(zV))*100:6.1f} cm")
    # compare exact two-ray vs effective-height formula for a very low antenna
    ff = 433.125e6; lam = c/ff; k = 2*np.pi/lam
    er, sig = GROUNDS['medium dry']; e = eps_c(ff, er, sig)
    for pol in ('H', 'V'):
        z = np.sqrt(e - 1) if pol == 'H' else np.sqrt(e - 1)/e
        for h1 in (0.02, 0.1, 0.5, 1.0):
            h2, d = 5.0, 5e3
            Lx = two_ray_loss(d, h1, h2, ff, er, sig, pol)
            he1 = abs(h1 - 1j/(k*z)); he2 = abs(h2 - 1j/(k*z))
            Lapp = 40*np.log10(d) - 20*np.log10(he1*he2)
            print(f"  {pol}-pol h1={h1:4.2f} m h2=5 m d=5 km: exact two-ray {Lx:6.1f} dB; effective-height formula {Lapp:6.1f} dB; "
                  f"naive plane-earth {40*np.log10(d)-20*np.log10(h1*h2):6.1f} dB")

    print("\n=== 4. Ground-station elevation lobing (far-field, GS height h) ===")
    for ff in (433.125e6, 915e6):
        lam = c/ff
        for h in (2.0, 5.0, 10.0):
            nulls = [np.degrees(np.arcsin(n*lam/(2*h))) for n in range(0, 4) if n*lam/(2*h) < 1]
            peaks = [np.degrees(np.arcsin((n+0.5)*lam/(2*h))) for n in range(0, 3) if (n+0.5)*lam/(2*h) < 1]
            print(f"  {ff/1e6:6.1f} MHz, GS h={h:4.1f} m: nulls at elevation {np.round(nulls,2)} deg; first lobe peaks {np.round(peaks,2)} deg")
    # rate of lobing for an ascending rocket
    ff = 433.125e6; lam = c/ff; h = 3.0
    for (R, vz, el) in ((20e3, 300.0, 10.0), (10e3, 500.0, 20.0)):
        th = np.radians(el)
        thdot = vz*np.cos(th)/R
        ffade = 2*h*np.cos(th)*thdot/lam
        print(f"  rocket at {R/1e3:.0f} km, climbing {vz:.0f} m/s at {el:.0f} deg elevation, GS h=3 m: lobing rate {ffade:.3f} Hz "
              f"(one null every {1/ffade:.1f} s)")

    print("\n=== 5. Landed rocket (antenna h1 near ground) to GS h2 = 5 m ===")
    for ff in (433.125e6, 915e6):
        for pol, h1, lab in (('H', 0.1, 'rocket lying flat, dipole along body (H-pol)'),
                             ('V', 0.3, 'vertical whip 0.3 m up (V-pol)')):
            row = []
            for d in (1e3, 2e3, 5e3, 10e3, 20e3):
                row.append(two_ray_loss(d, h1, 5.0, ff, *GROUNDS['medium dry'], pol))
            print(f"  {ff/1e6:6.1f} MHz {lab:45s}: L(1,2,5,10,20 km) = " + " ".join(f"{x:6.1f}" for x in row) + " dB")
        print(f"  {ff/1e6:6.1f} MHz FSPL(1,2,5,10,20 km) = " + " ".join(f"{fspl(d, ff):6.1f}" for d in (1e3, 2e3, 5e3, 10e3, 20e3)))
    # budget: 33 dBm, 0 dBi rocket, 11 dBi GS, -3 dB pol (circular GS), 1 dB feeder
    for pol, h1 in (('H', 0.1), ('V', 0.3)):
        for d in (2e3, 5e3, 10e3, 20e3):
            Pr = 33 + 0 + 11 - 3 - 1 - two_ray_loss(d, h1, 5.0, 433.125e6, *GROUNDS['medium dry'], pol)
            print(f"  433 MHz landed ({pol}-pol, h1={h1} m), d={d/1e3:4.0f} km: Pr = {Pr:7.1f} dBm "
                  f"(margin vs -128 dBm: {Pr+128:+6.1f} dB; vs -137 dBm: {Pr+137:+6.1f} dB)")

    print("\n=== 6. Rocket on the pad (vertical antenna at 3 m) to GS h=5 m, 433 MHz, V-pol ===")
    for d in (500, 1e3, 2e3, 3e3, 5e3):
        L = two_ray_loss(d, 3.0, 5.0, 433.125e6, *GROUNDS['medium dry'], 'V')
        print(f"  d={d/1e3:4.1f} km: two-ray {L:6.1f} dB vs FSPL {fspl(d, 433.125e6):6.1f} dB")

    print("\n=== 7. Lobing depth vs elevation: |Gamma| for H and V over medium-dry ground, 433 MHz ===")
    for el in (1, 3, 5, 10, 14.5, 20, 30, 45, 60):
        psi = np.radians(el)
        gh = abs(gamma(psi, 433.125e6, *GROUNDS['medium dry'], 'H'))
        gv = abs(gamma(psi, 433.125e6, *GROUNDS['medium dry'], 'V'))
        dh = 20*np.log10((1+gh)/(1-gh)); dv = 20*np.log10((1+gv)/max(1-gv, 1e-9))
        print(f"  elevation {el:5.1f} deg: |Gamma_H| {gh:.3f} (peak-to-null {dh:5.1f} dB), |Gamma_V| {gv:.3f} (peak-to-null {dv:5.1f} dB)")

    print("\n=== 8. Rough-surface specular reduction (Ament): rho_s = exp(-8 (pi sigma_h sin(psi)/lambda)^2) ===")
    lam = c/433.125e6
    for sig_h in (0.1, 0.3, 1.0):
        for el in (2.0, 10.0, 30.0):
            rho = np.exp(-8*(np.pi*sig_h*np.sin(np.radians(el))/lam)**2)
            print(f"  433 MHz, sigma_h={sig_h} m, grazing {el:4.1f} deg: rho_s = {rho:.3f}")
