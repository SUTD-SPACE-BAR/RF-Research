"""W5-S18 (G-05-08): numbers for the analog-IC building-block section of 05/fets-mosfet-jfet-gaas-gan.
Pelgrom mismatch (with a Monte-Carlo check of 1/sqrt(area) averaging), common-centroid gradient
cancellation, PTAT/bandgap arithmetic, gain boosting, CMOS swing vs R_opt. Run: python3 tools/verify/s18_analog_blocks.py"""
import numpy as np
ok = True
def chk(n, v, ref, tol):
    global ok
    g = abs(v - ref) <= tol; ok &= g
    print(f"{'PASS' if g else 'FAIL'}  {n}: {v:.6g} (page {ref})")

# Pelgrom: sigma(dVT) = A_VT/sqrt(WL)
A = 5.0  # mV um
chk("sigma dVT 10x1 um (mV)", A / np.sqrt(10 * 1), 1.58, 0.01)
chk("3 sigma (mV)", 3 * A / np.sqrt(10), 4.74, 0.01)
chk("area for 1 mV (um^2)", (A / 1.0) ** 2, 25, 0)
# MC: a device of area WL made of n unit cells each with independent VT error sigma_u -> 1/sqrt(n)
rng = np.random.default_rng(0)
su = 5.0  # mV for a 1 um^2 cell -> pair difference sigma = sqrt(2)*su/sqrt(n) ... define A_VT for the pair difference
n = 10
d = rng.normal(0, su / np.sqrt(2), (200000, n)).mean(1) - rng.normal(0, su / np.sqrt(2), (200000, n)).mean(1)
chk("MC pair sigma for 10 unit cells (mV)", d.std(), 1.58, 0.02)
# bipolar: A_VBE 0.35 mV um (Pelgrom IEDM 98) -> same 10 um^2 emitter pair
chk("bipolar 10 um^2 sigma (mV)", 0.35 / np.sqrt(10), 0.11, 0.005)

# common centroid: linear gradient g (mV per 100 um), unit cells 20 um pitch
g = 0.5 / 100  # mV/um (illustrative)
x = np.array([0, 20, 40, 60])  # um
AB = {"AABB": (x[[0, 1]], x[[2, 3]]), "ABBA": (x[[0, 3]], x[[1, 2]])}
side = g * (x[[0, 1]].mean() - x[[2, 3]].mean())
chk("side-by-side offset (mV)", abs(side), 0.20, 0.001)
cc = g * (x[[0, 3]].mean() - x[[1, 2]].mean())
chk("ABBA offset (mV)", abs(cc), 0.0, 1e-12)

# PTAT / bandgap
k, q = 1.380649e-23, 1.602176634e-19
VT = k * 300 / q
chk("VT(300K) mV", VT * 1e3, 25.85, 0.01)
dvbe = VT * np.log(8)
chk("dVBE n=8 (mV)", dvbe * 1e3, 53.8, 0.05)
chk("dVBE tempco (mV/K)", k / q * np.log(8) * 1e3, 0.179, 0.001)
K = 2.0 / (k / q * np.log(8) * 1e3)
chk("gain K for -2 mV/K VBE", K, 11.2, 0.05)
chk("Vref (V)", 0.65 + K * dvbe, 1.25, 0.005)

# gain boosting
gmro = 20
chk("single dB", 20 * np.log10(gmro), 26.0, 0.05)
chk("cascode dB", 20 * np.log10(gmro ** 2), 52.0, 0.05)
chk("boosted (Ab=20) dB", 20 * np.log10(gmro ** 2 * 20), 78.1, 0.05)

# CMOS swing vs R_opt for +22 dBm
P = 10 ** (22 / 10) * 1e-3
chk("P W", P, 0.158, 0.001)
chk("V peak into 50 ohm", np.sqrt(2 * P * 50), 3.98, 0.01)
chk("R_opt for 2 V peak", 2.0 ** 2 / (2 * P), 12.6, 0.05)
chk("transformation ratio", 50 / (2.0 ** 2 / (2 * P)), 3.96, 0.02)
chk("PVT combinations", 5 * 3 * 3, 45, 0)
print("ALL PASS" if ok else "SOME FAILED")
