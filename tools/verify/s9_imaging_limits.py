#!/usr/bin/env python3
"""W5-S9 checks for kb/11-radar/sar-and-imaging.md section
"Real-beam imaging limits: DBS, RF cameras, mechanical scanning and aperture outlines".

Run:  python3 tools/verify/s9_imaging_limits.py   (~3 s)

1. Doppler beam sharpening: delta_theta = lambda/(2 v T sin(theta)), sharpening ratio, unfocused limit sqrt(lambda R/2).
2. "RF camera": angular resolution lambda/D, resolvable beams per axis ~ 2D/lambda, cross-range at R.
3. Mechanically scanned radar: hits per beamwidth n = theta_B * PRF / (6 * rpm), revisit time.
4. Aperture outline on a lambda/2 grid (32 x 32 bounding square): square vs octagon vs circle,
   uniform and tapered: element count, directivity pi*(sum w)^2/sum w^2, peak sidelobe (principal and
   diagonal planes) from a 2-D FFT array factor.
"""
import numpy as np

c = 299_792_458.0
ok_all = True
db = lambda x: 10 * np.log10(x)


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.5g}, expected {want:.5g} (tol {tol})")


print("=" * 78)
print("1. Doppler beam sharpening (DBS)")
cases = (("X-band aircraft, 100 m/s, T 50 ms, 45 deg, beam 3 deg, R 10 km", 0.03, 100, 0.05, 45, 3.0, 10e3),
         ("77 GHz car, 20 m/s, T 20 ms, 60 deg, beam 20 deg, R 30 m", c / 77e9, 20, 0.02, 60, 20.0, 30.0),
         ("24 GHz drone, 10 m/s, T 0.1 s, 90 deg, beam 30 deg, R 50 m", c / 24.125e9, 10, 0.1, 90, 30.0, 50.0))
for lab, lam, v, T, th, beam, R in cases:
    dth = lam / (2 * v * T * np.sin(np.radians(th)))
    ratio = np.radians(beam) / dth
    unf = np.sqrt(lam * R / 2)
    print(f"    {lab}: d_theta = {np.degrees(dth):.3f} deg, sharpening x{ratio:.1f}, cross-range {R*dth:.2f} m "
          f"(real beam {R*np.radians(beam):.1f} m; unfocused limit sqrt(lambda R/2) = {unf:.2f} m)")
dth = 0.03 / (2 * 100 * 0.05 * np.sin(np.radians(45)))
check("DBS X-band d_theta (deg)", np.degrees(dth), 0.243, 0.001)
check("DBS X-band sharpening ratio", np.radians(3) / dth, 12.3, 0.1)
for th in (90, 30, 10, 5):
    print(f"    squint {th:2d} deg from the velocity vector: resolution degrades x{1/np.sin(np.radians(th)):.1f} vs broadside (blind ahead)")

print("=" * 78)
print("2. RF camera: diffraction limit")
for lab, f, D, R in (("77 GHz, 10 cm aperture, 10 m", 77e9, 0.10, 10.0),
                     ("77 GHz, TI EVM 12 virtual ch. (~6 lambda ~ 2.3 cm), 10 m", 77e9, 6 * c / 77e9, 10.0),
                     ("60 GHz BGT60 3 RX (~lambda), 2 m", 60.5e9, c / 60.5e9, 2.0),
                     ("2.4 GHz Wi-Fi, 30 cm, 5 m", 2.44e9, 0.30, 5.0),
                     ("10 GHz, 1 m, 1 km", 10e9, 1.0, 1000.0)):
    lam = c / f
    th = lam / D
    beams = 2 * D / lam
    print(f"    {lab:56s}: lambda/D = {np.degrees(th):6.2f} deg, ~{beams:5.1f} beams per axis over +/-90 deg, cross-range at R {R*th:6.2f} m")
check("77 GHz 10 cm at 10 m (m)", 10 * (c / 77e9) / 0.10, 0.389, 0.001)
lam = c / 77e9
print(f"    to match a 1 mrad camera pixel at 77 GHz needs D = lambda/1e-3 = {lam/1e-3:.1f} m")
check("aperture for 1 mrad at 77 GHz (m)", lam / 1e-3, 3.89, 0.01)

print("=" * 78)
print("3. Mechanically scanned radar: hits per beamwidth and revisit")
for lab, thB, prf, rpm in (("small marine X-band", 1.9, 1000, 24), ("marine X-band 4 ft open array", 1.2, 1000, 24),
                           ("airport surveillance", 1.4, 1000, 15)):
    n = thB * prf / (6 * rpm)
    print(f"    {lab:30s}: beam {thB} deg, PRF {prf} Hz, {rpm} rpm -> n = {n:5.1f} hits, time on target {thB/(6*rpm)*1e3:5.1f} ms, revisit {60/rpm:.1f} s")
check("hits per scan 1.2 deg, 1 kHz, 24 rpm", 1.2 * 1000 / (6 * 24), 8.33, 0.01)

print("=" * 78)
print("4. Aperture outline: square vs octagon vs circle (32 x 32 bounding box, lambda/2 grid)")
M = 32
x = (np.arange(M) - (M - 1) / 2)
X, Y = np.meshgrid(x, x)
r = np.hypot(X, Y) / (M / 2)
masks = {
    "square": np.ones_like(X, dtype=bool),
    "octagon": (np.abs(X) + np.abs(Y)) <= (M / 2) * np.sqrt(2),   # regular octagon, all 8 edges at apothem M/2
    "circle": r <= 1.0,
}


def taper(rr, ped=0.2):
    return ped + (1 - ped) * np.clip(1 - rr**2, 0, None) ** 1.0   # parabolic-on-pedestal (radial)


def analyse(w):
    Ntot = int(np.count_nonzero(w))
    D = db(np.pi * w.sum() ** 2 / (w**2).sum())
    P = 512
    F = np.abs(np.fft.fftshift(np.fft.fft2(w, (P, P)))) ** 2
    F /= F.max()
    Fd = 10 * np.log10(F + 1e-30)
    cidx = P // 2
    prin = Fd[cidx, :]
    diag = np.array([Fd[cidx + k, cidx + k] for k in range(-P // 2, P // 2)])

    def psl(cut):
        loc = (cut[1:-1] > cut[:-2]) & (cut[1:-1] > cut[2:])
        pk = np.sort(cut[1:-1][loc])[::-1]
        return pk[1] if len(pk) > 1 else -99

    return Ntot, D, psl(prin), psl(diag)


res = {}
for name, m in masks.items():
    for tname, w in (("uniform", m.astype(float)), ("tapered", m * taper(r))):
        Ntot, D, sp, sd = analyse(w)
        res[(name, tname)] = (Ntot, D, sp, sd)
        print(f"    {name:8s} {tname:8s}: {Ntot:5d} elements, directivity {D:5.2f} dBi, peak sidelobe principal {sp:6.1f} dB, diagonal {sd:6.1f} dB")
Nsq, Dsq, _, _ = res[("square", "tapered")]
Nci, Dci, _, _ = res[("circle", "tapered")]
Noc, Doc, _, _ = res[("octagon", "tapered")]
print(f"    tapered: circle uses {100*(1-Nci/Nsq):.1f} % fewer elements than the square for {Dsq-Dci:.2f} dB less directivity; octagon {100*(1-Noc/Nsq):.1f} % fewer for {Dsq-Doc:.2f} dB")
check("square uniform principal sidelobe (dB)", res[("square", "uniform")][2], -13.3, 0.3)
check("circle uniform sidelobe (dB)", res[("circle", "uniform")][2], -17.6, 0.6)
check("square uniform directivity = pi*N (dBi)", res[("square", "uniform")][1], db(np.pi * 1024), 1e-6)

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
