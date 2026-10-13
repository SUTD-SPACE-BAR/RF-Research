"""W5-S18 (G-08-08): differential-cutoff waveguide polariser, cross-iris size, patch trimming.
Run: python3 tools/verify/s18_horn_polariser.py"""
import numpy as np
c = 299792458.0
ok = True
def chk(n, v, ref, tol):
    global ok
    g = abs(v - ref) <= tol; ok &= g
    print(f"{'PASS' if g else 'FAIL'}  {n}: {v:.6g} (page {ref})")
def beta(f, a):
    k = 2 * np.pi * f / c; fc = c / (2 * a)
    return k * np.sqrt(1 - (fc / f) ** 2)
def ar_db(dphi_deg):
    # equal-amplitude orthogonal components with phase difference dphi -> axial ratio
    e = np.array([1, np.exp(-1j * np.radians(dphi_deg))]) / np.sqrt(2)
    R = abs(e[0] + 1j * e[1]) / np.sqrt(2); L = abs(e[0] - 1j * e[1]) / np.sqrt(2)
    return 20 * np.log10((R + L) / abs(R - L))
f0 = 10.368e9
chk("TE10 cutoff 20 mm GHz", c / (2 * 0.020) / 1e9, 7.49, 0.01)
chk("TE01 cutoff 17 mm GHz", c / (2 * 0.017) / 1e9, 8.82, 0.01)
chk("TE11 cutoff 20x20 GHz", c / (2 * 0.020) * np.sqrt(2) / 1e9, 10.60, 0.01)
L = (np.pi / 2) / (beta(f0, 0.020) - beta(f0, 0.017))
chk("polariser length mm", L * 1e3, 43.8, 0.05)
for f, ref_phi, ref_ar in ((10.0e9, 100.2, 1.55), (10.7e9, 82.9, 1.08)):
    d = np.degrees((beta(f, 0.020) - beta(f, 0.017)) * L)
    chk(f"dphi at {f/1e9} GHz", d, ref_phi, 0.05)
    chk(f"AR at {f/1e9} GHz dB", ar_db(d), ref_ar, 0.01)
chk("AR closed form check: 20log tan(dphi/2), dphi=100", ar_db(100), 20*np.log10(np.tan(np.radians(50))), 1e-9)
chk("cross arm ~lambda/2 at 10.368 GHz mm", c / f0 / 2 * 1e3, 14.5, 0.05)
# patch trim: 2.45 GHz FR-4 patch, eps_eff 4.08 (patch page table)
Leff = c / (2 * 2.45e9 * np.sqrt(4.08))
chk("patch L_eff mm", Leff * 1e3, 30.3, 0.05)
chk("df for 0.3 mm trim MHz", 2.45e9 * 0.3e-3 / Leff / 1e6, 24.3, 0.1)
chk("fraction of 2.6% BW", (0.3e-3 / Leff) / 0.026, 0.38, 0.01)
print("ALL PASS" if ok else "SOME FAILED")
