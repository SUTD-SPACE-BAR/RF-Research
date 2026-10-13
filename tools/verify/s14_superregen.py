#!/usr/bin/env python3
"""W5-S14 checks for 06/receiver-architectures#first-radio receivers (superregeneration,
crystal sets, cheap OOK modules, the one-transistor FM "bug").

Superregenerative oscillator (SRO) model: a parallel resonator whose net damping is swept
through zero by the quench. Complex-envelope equation (slowly varying, input near f0):
    da/dt = -alpha(t) a + b exp(j Dw t),   alpha(t) = zeta(t) w0
with a linear quench ramp alpha(t) = k (t0 - t)  (k = d(zeta)/dt * w0, units 1/s^2).
Linear-mode solution: a(te) = K * integral b exp(j Dw tau) s(tau) d tau with a Gaussian
sensitivity curve s(tau) = exp(-k (tau - t0)^2 / 2), sigma_t = 1/sqrt(k).

A. ODE vs closed form: RF -3 dB bandwidth  B = sqrt(ln2 * k) / pi.
B. Design law: with regenerative gain K = exp(k Tg^2 / 2) reached after a growth time Tg,
   B = sqrt(2 ln2 lnK) / (pi Tg) — bandwidth set by the quench rate, not by the tank Q.
C. Noise bandwidth of the Gaussian window and the thermal floor (sensitivity estimate).
D. Logarithmic (saturated) mode: detected output vs input level is compressed (quasi-log).
E. Re-radiation estimate vs FCC 15.109/15.111 and ETSI receiver limits (order of magnitude).
F. OOK range: superregen vs superhet (CC1101) — two-ray 40 log d regime and free space.
G. The FM bug: hand-capacitance pulling, and the 15.239 limit as EIRP.
H. Crystal set: diode detector output at strong vs weak fields (square-law collapse).
Ends with ALL PASS.
"""
import numpy as np
from scipy.integrate import solve_ivp

ok_all = True
def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name)

kT0 = -173.98
f0 = 433.92e6
w0 = 2 * np.pi * f0
c = 299792458.0

def envelope_out(k, Tg, dw, b=1.0, sat=None):
    """integrate da/dt = -k (t0 - t) a + b e^{j dw t} from t=0 (a=0) to te = 2 t0 (t0 = Tg)."""
    t0 = Tg
    def f(t, y):
        a = y[0] + 1j * y[1]
        alpha = k * (t0 - t)
        if sat is not None:                      # soft limiter for the saturated mode
            alpha = alpha + max(0.0, -alpha) * (abs(a) / sat) ** 2
        da = -alpha * a + b * np.exp(1j * dw * t)
        return [da.real, da.imag]
    sol = solve_ivp(f, [0, 2 * t0], [0.0, 0.0], rtol=1e-9, atol=1e-30, max_step=t0 / 400,
                    dense_output=sat is not None)
    return sol

# ---------------------------------------------------------------- A
print("A: linear-mode selectivity, ODE vs Gaussian closed form")
Tg = 1.0e-6                       # growth time = half of a 500 kHz quench period
lnK = 15.0
k = 2 * lnK / Tg ** 2
B_cf = np.sqrt(np.log(2) * k) / np.pi
ref = abs(complex(*envelope_out(k, Tg, 0.0).y[:, -1]))
dws = 2 * np.pi * np.linspace(0, 3e6, 61)
resp = np.array([abs(complex(*envelope_out(k, Tg, d).y[:, -1])) for d in dws]) / ref
f3 = np.interp(-3.0103, 20 * np.log10(resp[::-1]), dws[::-1] / (2 * np.pi))
print(f"  k = {k:.3e} 1/s^2, sigma_t = {1/np.sqrt(k)*1e9:.1f} ns; ODE -3 dB at +/-{f3/1e6:.3f} MHz -> B = {2*f3/1e6:.3f} MHz; "
      f"closed form {B_cf/1e6:.3f} MHz")
check("A1 ODE bandwidth matches sqrt(ln2 k)/pi within 2 %", abs(2 * f3 / B_cf - 1) < 0.02)
gain = ref / (1.0 * np.sqrt(2 * np.pi / k))            # |a| relative to b*integral of a flat window
print(f"  regenerative gain at te relative to the window integral: ln = {np.log(ref/np.sqrt(2*np.pi/k)):.2f} (expect lnK = {lnK})")
check("A2 regenerative gain = exp(k Tg^2/2)", abs(np.log(ref / np.sqrt(2 * np.pi / k)) - lnK) < 0.05)
for off in [1e6, 2e6, 5e6]:
    rej = -20 * np.log10(np.exp(-(2 * np.pi * off) ** 2 / (2 * k)))
    print(f"  rejection {off/1e6:.0f} MHz off: {rej:.1f} dB (Gaussian)")
rej1 = (2 * np.pi * 1e6) ** 2 / (2 * k) * 20 / np.log(10)
check("A3 a signal 1 MHz off-tune is rejected by only ~6 dB at 500 kHz quench", 4 < rej1 < 8)

# ---------------------------------------------------------------- B
print("\nB: bandwidth vs quench frequency (lnK = 15, Tg = half the quench period)")
for fq in [50e3, 100e3, 250e3, 500e3, 1e6]:
    Tg_ = 1 / (2 * fq)
    B = np.sqrt(2 * np.log(2) * lnK) / (np.pi * Tg_)
    print(f"  quench {fq/1e3:6.0f} kHz: B = {B/1e3:7.0f} kHz, effective Q at 433.92 MHz = {f0/B:6.0f}")
B500 = np.sqrt(2 * np.log(2) * lnK) / (np.pi * 1e-6)
check("B1 design law equals closed form at 500 kHz", abs(B500 / B_cf - 1) < 1e-9)
# tank Q needed for the same selectivity in a plain tuned circuit
print(f"  a passive tank with that bandwidth would need Q = {f0/B500:.0f}; a 433 MHz SAW is ~1.6 MHz wide")

# ---------------------------------------------------------------- C
print("\nC: noise bandwidth and thermal floor")
ENBW = np.sqrt(k) / (2 * np.sqrt(np.pi))
for NF in [6, 10]:
    print(f"  ENBW = {ENBW/1e6:.2f} MHz; floor with NF {NF} dB: {kT0 + 10*np.log10(ENBW) + NF:.1f} dBm")
check("C1 ENBW / B3dB = sqrt(pi/(4 ln2)) = 1.064", abs(ENBW / B_cf - np.sqrt(np.pi / (4 * np.log(2)))) < 1e-9)
floor = kT0 + 10 * np.log10(ENBW) + 8
print(f"  NF 8 dB: {floor:.1f} dBm in the RF window -> a -105 dBm seller claim needs detection at {(-105)-floor:.1f} dB "
      f"pre-detection SNR, i.e. heavy post-detection averaging over many quench cycles per bit")
check("C2 floor ~ -104 dBm at 500 kHz quench, NF 8 dB", -106 < floor < -102)

# ---------------------------------------------------------------- D
print("\nD: saturated (logarithmic) mode — detected output = mean envelope over the cycle")
Asat = 1.0
lnKD = 30.0                                    # growth large enough to reach saturation
kD = 2 * lnKD / Tg ** 2
u1 = np.sqrt(2 * np.pi / kD) * np.exp(lnKD)    # unsaturated |a(te)| per unit b
outs = []
levels = np.arange(0, 101, 10)                 # dB above the input that just reaches A_sat at te
for L in levels:
    b = 10 ** (L / 20) * Asat / u1
    sol = envelope_out(kD, Tg, 0.0, b=b, sat=Asat)
    tt = np.linspace(0, 2 * Tg, 4001)
    a = sol.sol(tt)
    outs.append(np.mean(np.hypot(a[0], a[1])))
outs = np.array(outs)
for L, o in zip(levels, outs):
    print(f"  input +{L:3d} dB -> mean envelope {o:.4f} x A_sat")
slope = np.diff(outs)
print(f"  output step per 10 dB of input: {slope.min():.4f} ... {slope.max():.4f} x A_sat (roughly constant = logarithmic law); "
      f"100 dB of input -> output ratio {outs[-1]/outs[0]:.2f}")
check("D1 equal output steps per 10 dB (within 1.6:1) over 100 dB: logarithmic law", np.all(slope > 0) and slope.max() / slope.min() < 1.6)

# ---------------------------------------------------------------- E
print("\nE: re-radiation (order of magnitude, assumed tank values)")
L_t, QL, Vpk, frac, duty = 20e-9, 30, 1.0, 0.5, 0.3
Rp = QL * w0 * L_t
P_osc = Vpk ** 2 / (2 * Rp)
P_rad = P_osc * frac * duty
Prad_dBm = 10 * np.log10(P_rad / 1e-3)
E_lim = 200e-6                             # FCC 15.109 Class B 216-960 MHz at 3 m
EIRP_lim = 10 * np.log10((E_lim * 3) ** 2 / 30 / 1e-3)
print(f"  R_p = {Rp:.0f} ohm, oscillation {10*np.log10(P_osc/1e-3):.1f} dBm peak, radiated average ~{Prad_dBm:.1f} dBm")
print(f"  FCC 15.109 200 uV/m @3 m = {EIRP_lim:.1f} dBm EIRP; 15.111 2 nW = {10*np.log10(2e-9/1e-3):.1f} dBm conducted; "
      f"excess ~{Prad_dBm - EIRP_lim:.0f} dB without an isolating RF stage")
check("E1 200 uV/m at 3 m = -49.2 dBm EIRP; 2 nW = -57.0 dBm", abs(EIRP_lim + 49.2) < 0.1 and abs(10*np.log10(2e-6) + 57.0) < 0.05)
check("E2 bare SRO on an antenna is tens of dB over receiver limits", Prad_dBm - EIRP_lim > 30)

# ---------------------------------------------------------------- F
print("\nF: OOK range, FS1000A-class 10 dBm, -5 dBi wire antennas both ends, 10 dB margin")
lam = c / f0
def range_two_ray(Lmax, h1=1.5, h2=1.5):
    return 10 ** ((Lmax + 20 * np.log10(h1 * h2)) / 40)
def range_fs(Lmax):
    return 10 ** ((Lmax - 20 * np.log10(4 * np.pi / lam)) / 20)
dc = 4 * np.pi * 1.5 * 1.5 / lam
print(f"  two-ray 40 log d regime beyond d_c = 4 pi h1 h2/lambda = {dc:.0f} m (h = 1.5 m)")
rows = {}
for name, S in [("superregen (realistic)", -100), ("superregen (seller claim)", -105),
                ("CC1101 1.2 kBaud", -112), ("CC1101 0.6 kBaud", -116)]:
    Lmax = 10 - 5 - 5 - S - 10
    rows[name] = (range_two_ray(Lmax), range_fs(Lmax))
    print(f"  {name:26s} S = {S} dBm: allowed path loss {Lmax} dB -> two-ray {rows[name][0]:5.0f} m, free space {rows[name][1]/1e3:5.1f} km")
r_ratio = rows["CC1101 1.2 kBaud"][0] / rows["superregen (realistic)"][0]
print(f"  12 dB better sensitivity: x{r_ratio:.2f} range near the ground (40 log d) vs x{10**(12/20):.2f} in free space")
check("F1 12 dB -> 2.0x range two-ray, 4.0x free space", abs(r_ratio - 10 ** (12 / 40)) < 1e-6)
check("F2 superregen ground range of order 100-300 m", 100 < rows["superregen (realistic)"][0] < 300)

# ---------------------------------------------------------------- G
print("\nG: one-transistor FM bug")
f_bug, Ct = 100e6, 20e-12
for dC in [0.1e-12, 0.5e-12]:
    df = f_bug * dC / (2 * Ct)
    print(f"  tank C {Ct*1e12:.0f} pF + {dC*1e12:.1f} pF (hand/antenna) -> shift {df/1e3:.0f} kHz (FM channel spacing 200 kHz)")
check("G1 0.1 pF on 20 pF pulls 250 kHz at 100 MHz", abs(f_bug * 0.1e-12 / (2 * Ct) - 250e3) < 1)
E239 = 250e-6
EIRP239 = 10 * np.log10((E239 * 3) ** 2 / 30 / 1e-3)
print(f"  FCC 15.239: 250 uV/m @3 m = {EIRP239:.1f} dBm EIRP; a 10 mW bug on a whip (~0 dBi) is {10 - EIRP239:.0f} dB over")
check("G2 15.239 limit = -47.3 dBm EIRP", abs(EIRP239 + 47.3) < 0.05)

# ---------------------------------------------------------------- H
print("\nH: crystal set detector (germanium/Schottky diode, n = 1.05, unbiased, very high-Z load)")
from scipy.special import i0e
VT = 0.025852 * 1.05
def vdc(V):                                   # exact for an ideal diode into an open-circuit RC load
    x = V / VT
    return VT * (np.log(i0e(x)) + x)          # n VT ln I0(V/nVT)
for E, heff in [(10e-3, 20), (0.5e-3, 10)]:
    V = E * heff
    print(f"  field {E*1e3:.1f} mV/m x h_eff {heff} m = {V*1e3:.0f} mV peak -> DC {vdc(V)*1e3:.2f} mV "
          f"({100*vdc(V)/V:.0f} % of peak; square-law approx {V**2/(4*VT)*1e3:.2f} mV)")
check("H1 strong field: >= 70 % of peak (envelope detection)", vdc(0.2) / 0.2 > 0.7)
check("H2 weak field 5 mV: 0.23 mV, square law (~5 % of peak)", abs(vdc(5e-3) - (5e-3)**2/(4*VT)) < 0.01e-3 and vdc(5e-3) < 0.3e-3)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
