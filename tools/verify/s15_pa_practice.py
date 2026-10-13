#!/usr/bin/env python3
"""W5-S15 / G-06-07 — PA practice checks for kb/06-rf-circuits/power-amplifiers.md ("Level 3 — PA practice").

 A. Doherty: peaking-branch offset line. Off-state peaking reflection Γ_off rotated to an open; efficiency at
    6 dB back-off vs offset-line error and off-state |Γ| (leakage loads the combining node).
 B. Class J: v = Vdc(1-cos θ)(1-α sin θ) with a class-B half-sine current -> Z1 = Ropt(1+jα), Z2 = -j(3π/8)α Ropt
    (sign as found by FFT), efficiency π/4 and power constant for |α| ≤ 1, v ≥ 0, peak voltage vs α.
 C. DIY load-pull: device-plane |Γ| reach through a lossy tuner/cable, pre-match, cable-length phase rotation
    (and the 2f0 impedance rotating twice as fast).
 D. AM/AM + AM/PM -> EVM (16-QAM); IM3 asymmetry needs memory AND a phase difference between the static and
    the memory coefficients: |a3 + bH|^2 - |a3 + bH*|^2 = -4 Im(H) Im(a3* b).
 E. Thermal runaway and emitter ballasting: loop gain θ V φ/(R_E + V_T/I) < 1; per-finger ballast; LDMOS
    zero-temperature-coefficient bias point (illustrative square-law model).
 F. Neutralisation: cancelling C_gd makes y12 = 0 (K -> ∞) without changing Mason's U.
Run: python3 tools/verify/s15_pa_practice.py   (a few seconds)
"""
import sys
import numpy as np
from scipy import signal

ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


# ================================================================ A. Doherty offset line
print("A: Doherty, normalised (Vdd = 1, Ropt = 1, inverter Z_T = 1, common load R_L = 1/2); peaking device = current source")
print("   I_p = -j 2(x-1/2) for x > 1/2 with its off-state admittance Y_off in parallel at the node; main class B, voltage-limited")
from scipy.optimize import brentq


def doherty_curve(Yoff=0.0, n=400):
    xs = np.linspace(0.01, 1.0, n); P = np.zeros(n); E = np.zeros(n)
    for k, x in enumerate(xs):
        Ip = -1j * 2 * (x - 0.5) if x > 0.5 else 0.0
        V1 = lambda Im: 1j * ((-1j * Im) * (2.0 + Yoff) - Ip)      # V2 = -j Z_T I_m ; I2 = V2 (G_L + Y_off) - I_p ; V1 = j Z_T I2
        Im = x
        if abs(V1(Im)) > 1.0:                                      # main saturates: reduce its current until |V1| = 1
            Im = brentq(lambda s: abs(V1(s)) - 1.0, 1e-9, x) if abs(V1(1e-9)) < 1.0 else 0.0
        V2 = -1j * Im
        P[k] = 0.5 * abs(V2) ** 2 * 2.0
        E[k] = P[k] / ((2 / np.pi) * (abs(Im) + abs(Ip)))
    return xs, P, E


xs, P, E = doherty_curve()
i5 = np.argmin(abs(xs - 0.5)); i23 = np.argmin(abs(xs - 2 / 3))
print(f"   ideal: eta {100*E[i5]:.1f} % at x = 0.5 (P {P[i5]:.3f} = -6 dB), {100*E[i23]:.1f} % at x = 2/3, {100*E[-1]:.1f} % at full power {P[-1]:.3f}")
check("A0 normalised Doherty model reproduces 78.5 / 69.8 / 78.5 %", abs(E[i5] - np.pi / 4) < 0.01 and abs(E[i23] - 0.698) < 0.01 and abs(E[-1] - np.pi / 4) < 0.01)


def eta_at_backoff(Yoff, bo_db=6.0):
    xs, P, E = doherty_curve(Yoff)
    Pt = P[-1] * 10 ** (-bo_db / 10)
    k = np.argmin(abs(P - 0.25))                                    # -6 dB below the IDEAL full power (1.0)
    return E[k], 10 * np.log10(P[-1] / 1.0), P[k]


res = {}
for gmag in (0.98, 0.9, 0.8):
    row = []
    for err in (0, 30, 60, 90, 180):
        G = gmag * np.exp(1j * np.radians(err))                    # residual angle from an open after the offset line
        Yoff = (1 - G) / (1 + G)                                    # admittance normalised to the 1-ohm (Ropt) line
        e6, pmax, _ = eta_at_backoff(Yoff)
        res[(gmag, err)] = (e6, pmax)
        row.append(f"{err:3d}°: {100*e6:4.1f} % / {pmax:+.1f} dB")
    print(f"   |Γ_off| {gmag}: eta at P = -6 dB / change of full power -> " + ", ".join(row))
check("A1 the offset line matters: 90-180° residual error costs > 10 points at -6 dB; |Γ_off| 0.8 costs > 3 points even when aligned",
      E[i5] - res[(0.98, 90)][0] > 0.10 and E[i5] - res[(0.98, 180)][0] > 0.10 and E[i5] - res[(0.8, 0)][0] > 0.03
      and E[i5] - res[(0.98, 0)][0] < 0.02)
# offset length for a given off-state phase at 433.92 MHz in 50-ohm coax (vf 0.66) and FR-4 microstrip (eps_eff 3.3)
phi0 = 140.0                                 # example off-state reflection phase (deg) at the peaking output plane
theta = (0 - phi0) / -2 % 180                # need Γ e^{-j2θ} = |Γ|∠0  ->  θ = phi0/2 (mod 180)
lam_coax = 299792458 / 433.92e6 * 0.66; lam_ms = 299792458 / 433.92e6 / np.sqrt(3.3)
print(f"   example: Γ_off ∠{phi0:.0f}° -> offset line θ = {theta:.0f}° = {theta/360*lam_coax*1e3:.0f} mm of vf-0.66 coax "
      f"or {theta/360*lam_ms*1e3:.0f} mm of FR-4 microstrip at 433.92 MHz")

# ================================================================ B. class J
print("B: class J continuum, half-sine (class B) current, v = Vdc(1-cos θ)(1+α sin θ), e^{jωt}, Z_n = -V_n/I_n")
th = np.linspace(0, 2 * np.pi, 8192, endpoint=False)
Vdc, Imax = 1.0, 1.0
i_d = Imax * np.maximum(np.cos(th), 0)
Ropt = 2 * Vdc / Imax
okJ = True
for a in (-1.0, -0.5, 0.0, 0.5, 1.0):
    v = Vdc * (1 - np.cos(th)) * (1 + a * np.sin(th))
    V = np.fft.rfft(v) / len(th) * 2; I = np.fft.rfft(i_d) / len(th) * 2
    Z1 = -V[1] / I[1]; Z2 = -V[2] / I[2]; Z3 = -V[3] / I[3] if abs(I[3]) > 1e-12 else 0
    P = 0.5 * np.real(-V[1] * np.conj(I[1])); Pdc = Vdc * np.mean(i_d)
    eta = P / Pdc
    okJ &= abs(Z1 - Ropt * (1 + 1j * a)) < 1e-6 and abs(Z2 - (-1j * 3 * np.pi / 8 * a * Ropt)) < 1e-6 and abs(eta - np.pi / 4) < 1e-6 \
        and v.min() > -1e-9
    print(f"   α {a:+.1f}: Z1/Ropt = {Z1.real/Ropt:.3f}{Z1.imag/Ropt:+.3f}j, Z2/Ropt = {Z2.real:+.3f}{Z2.imag:+.3f}j, "
          f"eta {100*eta:.2f} %, P {P:.4f}, v_min {v.min():+.3f}, v_peak {v.max()/Vdc:.2f} Vdc")
a = 1.2
v = Vdc * (1 - np.cos(th)) * (1 + a * np.sin(th))
print(f"   α 1.2: v_min {v.min():+.3f} Vdc < 0 -> the device would be driven into the knee (continuum ends at |α| = 1)")
check("B1 class J: Z1 = Ropt(1+jα), Z2 = -j(3π/8)α Ropt, eta = π/4 and P constant for |α| ≤ 1, v ≥ 0", okJ and v.min() < 0)
# fundamental power factor: a broadband match only needs to stay on the Z1/Z2 locus
alphas = np.linspace(-1, 1, 201)
pk = [np.max((1 - np.cos(th)) * (1 + aa * np.sin(th))) for aa in alphas]
print(f"   peak drain voltage rises from 2.00 Vdc (α = 0, class B) to {max(pk):.2f} Vdc at |α| = 1 — breakdown margin needed")

# ================================================================ C. DIY load-pull
print("C: DIY load-pull reach and cable rotation")
for tuner_gmax, loss_db in ((0.95, 0.2), (0.9, 0.5), (0.9, 1.0)):
    gdev = tuner_gmax * 10 ** (-2 * loss_db / 20)
    vswr = (1 + gdev) / (1 - gdev)
    print(f"   tuner |Γ|max {tuner_gmax}, line/tuner loss {loss_db} dB one way: device-plane |Γ| ≤ {gdev:.3f} "
          f"(VSWR {vswr:.1f}) -> lowest reachable R = {50/vswr:.1f} ohm")
# pre-match: lambda/4 of sqrt(50*12.5) = 25 ohm takes the tuner's 50-ohm centre to 12.5 ohm; reach scales by 4
gdev = 0.9 * 10 ** (-2 * 0.5 / 20); vswr = (1 + gdev) / (1 - gdev)
Rmin_pm = 12.5 / vswr
print(f"   with a 4:1 pre-match (λ/4 of 25 ohm), the same tuner reaches R down to {Rmin_pm:.2f} ohm — covers the AFT05MS003N's 5.9 + j6 ohm")
# lossy tuner: power at the device = power at the meter + loss, and the loss grows with |Γ| (standing wave in the lossy section)
a_loss = 10 ** (-0.5 / 20)
for g in (0.0, 0.5, 0.8):
    # power delivered into the line at the device end vs power reaching the load: P_load/P_in = a^2(1-|ΓL|^2)/(1-|a^2 ΓL|^2)
    GL = g / a_loss ** 2
    if GL >= 1:
        continue
    eff = a_loss ** 2 * (1 - GL ** 2) / (1 - (a_loss ** 2 * GL) ** 2)
    print(f"   device-plane |Γ| {g}: fraction of device power reaching a matched meter behind 0.5 dB of loss = "
          f"{10*np.log10(eff):.2f} dB (matched-line value -0.50 dB)")
f0 = 433.92e6; vf = 0.70
lam = 299792458 / f0 * vf
step = lam / 2 / 12
print(f"   cable rotation at 433.92 MHz (vf 0.70): full 360° of Γ per {lam/2*100:.1f} cm; 30° steps = {step*100:.2f} cm; "
      f"the 2f0 impedance rotates 60° per step (harmonic terminations change too)")
check("C1 a 1 dB-per-way tuner cannot reach below ~8 ohm; a 4:1 pre-match brings ~1.4 ohm in reach; λ/2 = 24 cm at 434 MHz",
      50 * (1 - 0.9 * 10 ** (-0.1)) / (1 + 0.9 * 10 ** (-0.1)) > 8 and Rmin_pm < 3 and abs(lam / 2 - 0.242) < 0.01)

# ================================================================ D. AM/AM, AM/PM -> EVM; IM3 asymmetry
print("D1: 16-QAM (RRC 0.25) through Rapp (p = 2) AM/AM and Saleh-type AM/PM; EVM vs output back-off")
rng = np.random.default_rng(3)
nsym, sps = 4000, 8
const = np.array([a + 1j * b for a in (-3, -1, 1, 3) for b in (-3, -1, 1, 3)]) / np.sqrt(10)
syms = const[rng.integers(0, 16, nsym)]
x = np.zeros(nsym * sps, complex); x[::sps] = syms
tt = np.arange(-8 * sps, 8 * sps + 1) / sps; beta = 0.25
h = np.sinc(tt) * np.cos(np.pi * beta * tt) / (1 - (2 * beta * tt) ** 2 + 1e-12)
x = np.convolve(x, h, mode='same')
x /= np.sqrt(np.mean(abs(x) ** 2))


def pa(x, drive, p=2.0, ampm_deg=15.0, use_am=True, use_pm=True):
    u = drive * x; r = abs(u)
    g = r / (1 + r ** (2 * p)) ** (1 / (2 * p)) if use_am else r
    phi = np.radians(ampm_deg) * r ** 2 / (1 + r ** 2) if use_pm else 0
    return g * np.exp(1j * (np.angle(u) + phi))


def evm(y, drive):
    ys = y[::sps] / drive
    c = np.vdot(syms, ys) / np.vdot(syms, syms)               # best complex gain (as a receiver equaliser would)
    return 100 * np.sqrt(np.mean(abs(ys / c - syms) ** 2) / np.mean(abs(syms) ** 2))


for ibo in (12, 8, 6, 4):
    drive = 10 ** (-ibo / 20) * 1.0 / np.sqrt(np.mean(abs(x) ** 2)) * 1.0
    e_all = evm(pa(x, drive), drive); e_am = evm(pa(x, drive, use_pm=False), drive); e_pm = evm(pa(x, drive, use_am=False), drive)
    print(f"   input back-off {ibo:2d} dB (rms re saturation): EVM {e_all:5.2f} % (AM/AM only {e_am:5.2f} %, AM/PM only {e_pm:5.2f} %)")
d6 = 10 ** (-6 / 20)
check("D1 AM/AM and AM/PM both add EVM; EVM rises steeply as back-off shrinks",
      evm(pa(x, 10 ** (-4 / 20)), 10 ** (-4 / 20)) > 2 * evm(pa(x, 10 ** (-12 / 20)), 10 ** (-12 / 20))
      and evm(pa(x, d6, use_pm=False), d6) > 0.5 and evm(pa(x, d6, use_am=False), d6) > 0.5)

print("D2: two-tone IM3 asymmetry: y = a1 x + a3 x|x|^2 + b x (h * |x|^2), h = 1st-order 'bias network' at the envelope")
fs = 1.0; n = 1 << 16; k1, kd = 1000, 64          # tones at bins k1 and k1 + kd (spacing kd)
tn = np.arange(n)
xt = 0.1 * (np.exp(2j * np.pi * k1 * tn / n) + np.exp(2j * np.pi * (k1 + kd) * tn / n))


def two_tone(a3, b, fc_env):
    env = abs(xt) ** 2
    if b != 0:
        # first-order low-pass at fc_env (in bins): exact periodic filtering in the frequency domain
        E = np.fft.fft(env); kk = np.fft.fftfreq(n) * n
        Hk = 1 / (1 + 1j * kk / fc_env)
        envf = np.fft.ifft(E * Hk)
    else:
        envf = 0
    y = xt + a3 * xt * env + b * xt * envf
    Y = np.fft.fft(y) / n
    lo, hi = abs(Y[k1 - kd]), abs(Y[k1 + 2 * kd])
    return 20 * np.log10(hi / lo), Hk[kd] if b != 0 else 0


cases = [("memoryless, complex a3 (AM/PM)", -0.2 * np.exp(1j * 0.5), 0, 1.0),
         ("memory, a3 and b in phase", -0.2, -0.1, kd),
         ("memory, a3 and b 90° apart", -0.2, -0.1j, kd),
         ("memory far below the envelope (fc = 100 x spacing)", -0.2, -0.1j, 100 * kd)]
asy = {}
for lab, a3, b, fce in cases:
    d, Hd = two_tone(a3, b, fce)
    pred = 0.0
    if b != 0:
        A = a3; B = b * Hd; Bc = b * np.conj(Hd)
        pred = 20 * np.log10(abs(A + B) / abs(A + Bc))
    asy[lab] = d
    print(f"   {lab:52s}: upper - lower IM3 = {d:+6.2f} dB (closed form {pred:+6.2f} dB)")
check("D2 IM3 asymmetry needs memory (complex H at the spacing) AND Im(a3* b) != 0",
      abs(asy[cases[0][0]]) < 0.01 and abs(asy[cases[1][0]]) < 0.01 and abs(asy[cases[2][0]]) > 1.0 and abs(asy[cases[3][0]]) < 0.3)

# ================================================================ E. thermal runaway / ballasting
print("E: BJT electro-thermal loop, φ = |dV_BE/dT| = 2 mV/K at fixed I_C, V_T = 25.9 mV")
VT, phi = 0.0259, 2e-3


def loop_gain(theta, V, I, RE):
    return theta * V * phi / (RE + VT / I)


def settle(theta, V, I0, RE, Ta=25.0, n=4000):
    # bias: fixed base voltage chosen so that I = I0 at T = Ta; iterate T -> I (solve emitter loop) -> P -> T
    VB = VT * np.log(I0 / 1e-14) + I0 * RE
    T = Ta
    for _ in range(n):
        f = lambda I: VB - VT * np.log(I / 1e-14) - I * RE + phi * (T - Ta)
        lo, hi = 1e-9, 1e3
        for _ in range(200):
            mid = np.sqrt(lo * hi)
            if f(mid) > 0:
                lo = mid
            else:
                hi = mid
        I = lo
        Tn = Ta + theta * V * I
        if Tn > 400:
            return I, Tn, False
        if abs(Tn - T) < 1e-9:
            return I, Tn, True
        T = Tn
    return I, T, True


print("   (bias: fixed base voltage set for I0 when cold — worst case; T rise amplified by 1/(1-L), and L grows as I rises)")
runs = {}
for theta, V, I0, RE, lab in ((30, 7.5, 0.3, 0.0, "2 W stage, no ballast"), (30, 7.5, 0.3, 0.5, "same, R_E 0.5 ohm (cold L 0.77)"),
                              (30, 7.5, 0.3, 1.5, "same, R_E 1.5 ohm"),
                              (300, 7.5, 0.03, 0.0, "one of 10 fingers, no ballast"), (300, 7.5, 0.03, 4.0, "one finger, R_E 4 ohm (cold L 0.93)"),
                              (300, 7.5, 0.03, 10.0, "one finger, R_E 10 ohm")):
    L = loop_gain(theta, V, I0, RE)
    I, T, okk = settle(theta, V, I0, RE)
    runs[(theta, RE)] = (okk, I, T, L)
    need = theta * V * phi - VT / I0
    hot = f"I {I*1e3:.0f} mA, T {T:.0f} °C, hot L {loop_gain(theta, V, I, RE):.2f}" if okk else "T > 400 °C"
    print(f"   {lab:38s}: θ {theta} K/W, cold loop gain {L:.2f} -> {'settles' if okk else 'RUNAWAY'} ({hot}); "
          f"R_E > θVφ − V_T/I = {max(need,0):.2f} ohm is only the marginal value")
check("E1 runaway without ballast; cold L close to 1 still runs away; L ≈ 0.3-0.4 settles",
      not runs[(30, 0.0)][0] and not runs[(30, 0.5)][0] and runs[(30, 1.5)][0] and not runs[(300, 0.0)][0]
      and not runs[(300, 4.0)][0] and runs[(300, 10.0)][0])
# LDMOS: I_D = K0 (T/T0)^-m (V_GS - V_th(T))^2, V_th falls by s per K -> zero-TC overdrive V_ov = 2 s T/m
for s_, m_ in ((2.5e-3, 1.5), (3e-3, 2.0)):
    vz = 2 * s_ * 300 / m_
    print(f"   LDMOS square-law illustration (dV_th/dT = -{s_*1e3:.1f} mV/K, mobility ∝ T^-{m_}): zero-TC overdrive "
          f"≈ {vz:.2f} V; class-AB quiescent bias sits below it -> I_DQ rises with temperature (needs a tracking gate bias)")

# ================================================================ F. neutralisation
print("F: neutralisation of C_gd (FET: gm 0.5 S, Cgs 20 pF, Cgd 1 pF, Rds 200 ohm, input loss G_in 2 mS), 433.92 MHz")
w = 2 * np.pi * 433.92e6
gm, Cgs, Cgd, Rds, Gin = 0.5, 20e-12, 1e-12, 200.0, 2e-3


def ymat(Cn):
    # intrinsic y with Cgd; neutralising capacitor Cn from the gate to an INVERTED drain (ideal 1:-1 transformer):
    # a lossless reciprocal embedding y_n = jω Cn [[1, 1], [1, 1]]
    Yi = np.array([[Gin + 1j * w * (Cgs + Cgd), -1j * w * Cgd], [gm - 1j * w * Cgd, 1 / Rds + 1j * w * Cgd]])
    Yn = 1j * w * Cn * np.array([[1, 1], [1, 1]])
    return Yi + Yn


def mason_U(Y):
    y11, y12, y21, y22 = Y[0, 0], Y[0, 1], Y[1, 0], Y[1, 1]
    return abs(y21 - y12) ** 2 / (4 * (y11.real * y22.real - y12.real * y21.real))


def rollett_K(Y):
    y11, y12, y21, y22 = Y[0, 0], Y[0, 1], Y[1, 0], Y[1, 1]
    return (2 * y11.real * y22.real - (y12 * y21).real) / abs(y12 * y21)


for Cn in (0.0, 0.5e-12, 1.0e-12):
    Y = ymat(Cn)
    K = rollett_K(Y) if abs(Y[0, 1]) > 1e-15 else np.inf
    print(f"   C_n {Cn*1e12:.1f} pF: |y12| {abs(Y[0,1])*1e3:.3f} mS, K {K:8.2f}, U {10*np.log10(mason_U(Y)):.2f} dB")
U0 = mason_U(ymat(0)); U1 = mason_U(ymat(1e-12))
check("F1 full neutralisation zeroes y12 (unconditionally stable) and leaves Mason's U unchanged",
      abs(ymat(1e-12)[0, 1]) < 1e-9 and abs(10 * np.log10(U1 / U0)) < 1e-6 and rollett_K(ymat(0)) < 1)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
