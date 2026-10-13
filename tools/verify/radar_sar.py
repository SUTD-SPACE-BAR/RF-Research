#!/usr/bin/env python3
"""Verification for kb/11-radar/sar-and-imaging.md

Run:  python3 tools/verify/radar_sar.py      (~20 s)

Checks:
  1. Rail SAR (wide-beam, "spotlight-like" full-aperture) at 10 GHz, B = 1.5 GHz, aperture L = 1.5 m,
     positions every lambda/4: time-domain backprojection of point targets; measured -3 dB widths
     vs range 0.886 c/(2B) and cross-range 0.886 lambda R/(2L).
  2. Along-track undersampling: spacing lambda (4x too coarse) creates grating-lobe ghosts at
     cross-range offset ~ lambda R/(2 du); spacing lambda/4 keeps ghosts below -25 dB.
  3. Stripmap with a real antenna of length D = 0.1 m (two-way pattern weighting): cross-range
     resolution ~ D/2 independent of range (targets at 5 m and 10 m).
  4. ISAR cross-range resolution lambda/(2 dtheta) and DIY SAR parameter examples (printed).
"""
import numpy as np

c = 299_792_458.0
ok_all = True


def check(name, got, want, tol, rel=False):
    global ok_all
    err = abs(got - want) / (abs(want) if rel else 1.0)
    ok = err <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.6g}, expected {want:.6g} (tol {tol}{' rel' if rel else ''})")
    return ok


def simulate(fc, B, Nf, u, targets, D=None):
    """Stepped-frequency / dechirped-FMCW equivalent data: s[u_i, f_k] = sum a w(theta) exp(-j 4 pi f R / c).
    Radar moves along x (positions u), targets at (x, y) with y = broadside range."""
    fk = fc - B / 2 + B * np.arange(Nf) / Nf
    s = np.zeros((len(u), Nf), complex)
    lam = c / fc
    for (xt, yt, a) in targets:
        R = np.sqrt((xt - u) ** 2 + yt ** 2)
        w = np.ones_like(u)
        if D is not None:
            sin_th = (xt - u) / R
            w = np.sinc(D * sin_th / lam) ** 2      # two-way (amplitude) pattern of a uniform aperture D
        s += (a * w)[:, None] * np.exp(-4j * np.pi * fk[None, :] * R[:, None] / c)
    return s, fk


def backproject(s, fk, u, xg, yg, osf=16):
    """Range-compress (IFFT over frequency), then for each position interpolate the range profile at
    every pixel's range and apply the carrier phase correction."""
    Nf = len(fk)
    B = fk[-1] - fk[0] + (fk[1] - fk[0])
    nfft = Nf * osf
    prof = np.fft.ifft(s, nfft, axis=1)                   # range profiles
    dr = c / (2 * B) / osf * 1.0                          # range per bin (oversampled)
    rbins = np.arange(nfft) * c / (2 * B * osf / (Nf / Nf)) / Nf * Nf / nfft * osf
    rbins = np.arange(nfft) * (c / (2 * (fk[1] - fk[0]))) / nfft
    X, Y = np.meshgrid(xg, yg)
    img = np.zeros_like(X, complex)
    f0 = fk[0]
    for i, ui in enumerate(u):
        R = np.sqrt((X - ui) ** 2 + Y ** 2)
        # interpolate complex profile at R (linear, on oversampled grid)
        idx = R / rbins[1]
        i0 = np.floor(idx).astype(int)
        fr = idx - i0
        i0 = np.clip(i0, 0, nfft - 2)
        v = prof[i, i0] * (1 - fr) + prof[i, i0 + 1] * fr
        img += v * np.exp(4j * np.pi * f0 * R / c)
    return img


def width_3db(profile, axis_vals):
    a = np.abs(profile) / np.abs(profile).max()
    k = np.argmax(a)
    thr = 10 ** (-3 / 20)
    i = k
    while i > 0 and a[i] > thr:
        i -= 1
    j = k
    while j < len(a) - 1 and a[j] > thr:
        j += 1
    li = axis_vals[i] + (thr - a[i]) / (a[i + 1] - a[i]) * (axis_vals[i + 1] - axis_vals[i])
    lj = axis_vals[j - 1] + (a[j - 1] - thr) / (a[j - 1] - a[j]) * (axis_vals[j] - axis_vals[j - 1])
    return lj - li


print("=" * 78)
print("1. Rail SAR, backprojection, resolution")
fc, B, Nf = 10e9, 1.5e9, 128
lam = c / fc
L = 1.5
du = lam / 4
u = np.arange(-L / 2, L / 2, du)
targets = [(0.0, 5.0, 1.0), (0.4, 5.6, 0.8), (-0.5, 4.5, 0.6)]
s, fk = simulate(fc, B, Nf, u, targets)
# fine grid around target 0 for resolution
xg = np.linspace(-0.3, 0.3, 601)
yg = np.linspace(4.7, 5.3, 601)
img = backproject(s, fk, u, xg, yg)
iy, ix = np.unravel_index(np.argmax(np.abs(img)), img.shape)
w_cr = width_3db(img[iy, :], xg)
w_r = width_3db(img[:, ix], yg)
R0 = 5.0
th_cr = 0.886 * lam * R0 / (2 * L)
th_r = 0.886 * c / (2 * B)
print(f"    target at (0, 5 m): peak at ({xg[ix]:.3f}, {yg[iy]:.3f}); -3 dB cross-range {w_cr*100:.2f} cm (theory 0.886 lambda R/2L = {th_cr*100:.2f}), "
      f"range {w_r*100:.2f} cm (theory 0.886 c/2B = {th_r*100:.2f})")
check("cross-range resolution ~ 0.886 lambda R/(2L)", w_cr, th_cr, 0.1, rel=True)
check("range resolution ~ 0.886 c/(2B)", w_r, th_r, 0.1, rel=True)
check("target position focused correctly (cm)", np.hypot(xg[ix], yg[iy] - 5.0) * 100, 0.0, 1.0)

print("=" * 78)
print("2. Along-track sampling and grating-lobe ghosts (searched on the arc of constant slant range)")
Rarc = 5.0
ang = np.radians(np.linspace(-60, 60, 2401))
for du2, lab in ((lam / 4, "lambda/4"), (lam, "lambda")):
    u2 = np.arange(-L / 2, L / 2, du2)
    s2, fk2 = simulate(fc, B, Nf, u2, [(0.0, Rarc, 1.0)])
    # evaluate the image at points on the arc R = 5 m
    vals = []
    for a in ang:
        vals.append(backproject(s2, fk2, u2, np.array([Rarc * np.sin(a)]), np.array([Rarc * np.cos(a)]))[0, 0])
    im2 = np.abs(np.array(vals))
    im2 /= im2.max()
    far = np.abs(np.degrees(ang)) > 5
    ghost = 20 * np.log10(im2[far].max())
    agh = np.degrees(ang[far][np.argmax(im2[far])])
    pred = np.degrees(np.arcsin(min(1.0, lam / (2 * du2))))
    print(f"    spacing {lab:8s} ({du2*1000:.1f} mm): strongest off-target response {ghost:.1f} dB at {agh:+.1f} deg "
          f"(grating: sin(theta) = lambda/(2 du) -> {pred:.1f} deg)")
    if lab == "lambda":
        # wideband (15 % fractional BW) smears the grating angle (it depends on lambda), so the ghost peak is ~-16 dB, not 0 dB
        check("undersampled aperture produces a clear ghost (> -20 dB)", float(ghost > -20), 1.0, 0)
        check("ghost at sin(theta) = lambda/(2 du) (deg)", abs(agh), pred, 1.5)
    else:
        check("lambda/4 sampling: no ghost above -25 dB", float(ghost < -25), 1.0, 0)

print("=" * 78)
print("3. Stripmap: cross-range resolution D/2, independent of range")
D = 0.10
res = {}
for R0 in (5.0, 10.0):
    Lsa = lam * R0 / D
    u3 = np.arange(-1.5 * Lsa, 1.5 * Lsa, D / 4)
    s3, fk3 = simulate(fc, B, 256, u3, [(0.0, R0, 1.0)], D=D)   # 256 steps -> 12.8 m unambiguous range
    xg3 = np.linspace(-0.25, 0.25, 501)
    im3 = backproject(s3, fk3, u3, xg3, np.array([R0]))[0]
    res[R0] = width_3db(im3, xg3)
    print(f"    R = {R0} m: synthetic aperture lambda R/D = {Lsa:.2f} m; -3 dB cross-range = {res[R0]*100:.2f} cm (D/2 = {D/2*100:.1f} cm)")
# Two-way amplitude weighting sinc^2(D sin(theta)/lambda) -> PSF = FT = triangle with zeros at +-D/2:
# "D/2" is the null-to-peak (Rayleigh) resolution; the -3 dB full width of a triangle is 2*(1-1/sqrt2)*D/2 = 0.293 D
check("stripmap -3 dB width ~ 0.29-0.36 D (triangle PSF; D/2 is null-to-peak)", res[5.0] / D, 0.33, 0.05)
check("stripmap resolution independent of range (10 m vs 5 m within 10%)", res[10.0] / res[5.0], 1.0, 0.1)

print("=" * 78)
print("4. ISAR and DIY examples")
for f, dth_deg in ((77e9, 3.0), (10e9, 5.0), (2.4e9, 20.0)):
    lam_ = c / f
    print(f"    ISAR {f/1e9:.1f} GHz, rotation {dth_deg} deg: cross-range res lambda/(2 dtheta) = {lam_/(2*np.radians(dth_deg))*100:.1f} cm")
check("ISAR 77 GHz 3 deg", c / 77e9 / (2 * np.radians(3.0)) * 100, 3.72, 0.02)
# coffee-can rail SAR: 2.4 GHz, ~93 MHz sweep, rail 2 m, target 20 m
lam24 = c / 2.44e9
print(f"    coffee-can rail SAR (2.44 GHz, ~90 MHz, 2 m rail, 20 m): range res {c/(2*90e6):.2f} m, cross-range lambda R/2L = {lam24*20/4:.2f} m,"
      f" spacing <= lambda/4 = {lam24/4*100:.1f} cm")
print(f"    drone SAR (6 GHz, D ~ 5 cm patch): stripmap res D/2 = 2.5 cm cross-range; 1 GHz sweep -> {c/2e9*100:.0f} cm range")

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
