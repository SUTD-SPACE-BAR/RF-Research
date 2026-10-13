#!/usr/bin/env python3
"""
e3_bench.py -- numerical checks for kb/17-test-measurement/bench-measurement-recipes.md

1.  Output (source) resistance by the two-load method; error propagation vs load choice (Monte Carlo).
2.  Complex source impedance by the four-load linear method (one reactive load removes the X sign
    ambiguity); Monte Carlo with 0.05 dB power errors.
3.  "Load-pull-lite": |Gamma_s| of a transmitter from the power ripple into a rotated known mismatch;
    cable lengths needed to rotate the phase at 433/915 MHz.
4.  SWR meter / coupler directivity: reading bounds, calibration with known loads, extracting
    directivity from a rotated mismatch, forward-power error.
5.  Shield boxes: isolation needed for conducted tests, slot leakage 20log(lambda/2L) - 20log n,
    waveguide-below-cutoff (32.0 dB per diameter, 27.3 dB per width), box/cap cavity resonances,
    TEM-cell field E = sqrt(P Z0)/h.
6.  EBYTE E22-400T33D (2 W, 433 MHz) power + harmonics: pad dissipation, analyser levels, harmonic
    limits (IMDA Table 1-a), analyser-generated harmonics with and without a high-pass filter,
    uncertainty budget (RSS).
7.  Wheeler cap: efficiency uncertainty from resistance errors; cap size and its cavity resonance
    (cube: f_res/f = pi/sqrt(2); sphere: 2.744).
8.  Range test with attenuators: equivalent distance, attenuator-accuracy -> range error, leakage rule.
9.  Pulsed signals on a spectrum analyser: Gaussian RBW impulse bandwidth K = sqrt(pi/(2 ln 2)) = 1.505;
    pulse desensitisation 20log(K tau B) vs numerical filter response; line-spectrum factor 20log(tau PRF).
10. Ferrite core permeability from a winding measurement (mu', mu'' from Z = R + jX); A_L of a toroid.
11. "Is it transmitting?" field strength and SDR level at a distance.

Run: python3 tools/verify/e3_bench.py   (PASS/FAIL per check, < 5 s)
"""
import numpy as np

rng = np.random.default_rng(7)
C = 299_792_458.0
MU0 = 4e-7 * np.pi
Z0 = 50.0
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


def db10(x):
    return 10 * np.log10(x)


# ---------------------------------------------------------------- 1. two-load method
print("=== 1. Two-load output resistance ===")


def rs_two_load(p1, r1, p2, r2):
    v1, v2 = np.sqrt(p1 * r1), np.sqrt(p2 * r2)
    return (v2 - v1) / (v1 / r1 - v2 / r2)


def p_into(r, voc, rs):
    return (voc * r / (rs + r)) ** 2 / r


voc = 1.0
for rs_true in [50.0, 10.0, 150.0]:
    est = rs_two_load(p_into(50, voc, rs_true), 50, p_into(100, voc, rs_true), 100)
    check(f"exact recovery R_s = {rs_true:.0f} ohm (50/100 ohm loads)", abs(est - rs_true) < 1e-9, f"{est:.3f}")
# Monte Carlo: 0.1 dB (1 sigma) independent power errors, different second loads
rs_true = 50.0
for r2 in [25.0, 75.0, 100.0, 200.0, 1000.0]:
    est = []
    for _ in range(20000):
        e1, e2 = 10 ** (rng.normal(0, 0.1, 2) / 10)
        est.append(rs_two_load(p_into(50, voc, rs_true) * e1, 50, p_into(r2, voc, rs_true) * e2, r2))
    est = np.array(est)
    print(f"  loads 50 & {r2:6.0f} ohm, 0.1 dB power error: R_s = {np.median(est):6.1f} ohm, "
          f"spread (16-84 %) {np.percentile(est,16):6.1f} .. {np.percentile(est,84):6.1f}")
    if r2 == 100.0:
        spread100 = np.percentile(est, 84) - np.percentile(est, 16)
    if r2 == 1000.0:
        spread1000 = np.percentile(est, 84) - np.percentile(est, 16)
check("widely spaced loads (50 & 1000) beat close ones (50 & 100)", spread1000 < spread100,
      f"spread {spread1000:.1f} vs {spread100:.1f} ohm")
# open-circuit (high-Z probe) variant
vl = voc * 50 / (rs_true + 50)
check("loaded-vs-open voltage: R_s = R_L (V_oc/V_L - 1)", abs(50 * (voc / vl - 1) - rs_true) < 1e-9)

# ---------------------------------------------------------------- 2. four-load complex method
print("\n=== 2. Complex source impedance from four loads (linear least squares) ===")


def solve_zs(loads, pw):
    # |Zs + Zk|^2 = c |Zk|^2 / |Vk|^2 with |Vk|^2 = Pk |Zk|^2 / Rk  ->  q_k = Rk / Pk
    A, b = [], []
    for zk, pk in zip(loads, pw):
        qk = zk.real / pk
        A.append([1.0, 2 * zk.real, 2 * zk.imag, -qk])
        b.append(-abs(zk) ** 2)
    sol, *_ = np.linalg.lstsq(np.array(A), np.array(b), rcond=None)
    return sol[1] + 1j * sol[2]


def p_complex(zk, zs, voc=1.0):
    i = voc / (zs + zk)
    return abs(i) ** 2 * zk.real


zs_true = 30 + 20j
loads = [50 + 0j, 100 + 0j, 25 + 0j, 50 + 50j]
pw = [p_complex(z, zs_true) for z in loads]
zs_est = solve_zs(loads, pw)
check("four-load solve recovers 30 + j20 ohm exactly", abs(zs_est - zs_true) < 1e-9, f"{zs_est:.4f}")
# all-real loads cannot tell the sign of X
pw_neg = [p_complex(z, 30 - 20j) for z in loads[:3]]
pw_pos = [p_complex(z, 30 + 20j) for z in loads[:3]]
check("with only resistive loads, +jX and -jX give identical powers", np.allclose(pw_neg, pw_pos))
est = []
for _ in range(5000):
    pe = [p * 10 ** (rng.normal(0, 0.05) / 10) for p in pw]
    est.append(solve_zs(loads, pe))
est = np.array(est)
print(f"  0.05 dB power errors: R_s = {np.median(est.real):.1f} (+/-{np.std(est.real):.1f}), "
      f"X_s = {np.median(est.imag):.1f} (+/-{np.std(est.imag):.1f}) ohm")
check("0.05 dB errors give a few-ohm uncertainty", np.std(est.real) < 8 and np.std(est.imag) < 8)

# ---------------------------------------------------------------- 3. load-pull-lite |Gamma_s|
print("\n=== 3. Source match from power ripple into a rotated mismatch ===")
gl = 1 / 3          # VSWR 2 load
for gs in [0.1, 0.3, 0.5, 0.7]:
    ph = np.linspace(0, 2 * np.pi, 721)
    p = (1 - gl ** 2) / np.abs(1 - gs * gl * np.exp(1j * ph)) ** 2
    ripple = db10(p.max() / p.min())
    r = p.max() / p.min()
    gs_est = (np.sqrt(r) - 1) / ((np.sqrt(r) + 1) * gl)
    print(f"  |Gs| = {gs:.1f}: P_max/P_min = {ripple:5.2f} dB -> recovered |Gs| = {gs_est:.3f}")
    check(f"  inversion |Gs| = {gs}", abs(gs_est - gs) < 1e-3)
for f, vf in [(433e6, 0.695), (915e6, 0.695)]:
    lg = vf * C / f
    print(f"  {f/1e6:.0f} MHz, PTFE coax vf {vf}: lambda_g/2 = {lg/2*100:.1f} cm rotates Gamma_L by 360 deg; "
          f"8 phases -> steps of {lg/16*100:.1f} cm")

# ---------------------------------------------------------------- 4. directivity
print("\n=== 4. SWR meter / coupler directivity ===")


def swr(g):
    return (1 + g) / (1 - g)


for swr_true in [1.2, 1.5, 2.0]:
    g = (swr_true - 1) / (swr_true + 1)
    row = []
    for dd in [20, 25, 30, 35]:
        d = 10 ** (-dd / 20)
        lo, hi = max(g - d, 0), g + d
        row.append(f"D {dd} dB: {swr(lo):.2f}-{swr(hi):.2f}")
    print(f"  true SWR {swr_true}: " + "; ".join(row))
d = 10 ** (-20 / 20)
g = (1.22 - 1) / 2.22
check("20 dB directivity, SWR 1.22 reads 1.00-1.50 (matches rf-power-measurement Ex. 4)",
      abs(swr(max(g - d, 0)) - 1.00) < 0.01 and abs(swr(g + d) - 1.50) < 0.02)
# extract directivity by rotating a VSWR-2 load with cable lengths
d_true, g_load = 10 ** (-23 / 20), 1 / 3
ph = np.linspace(0, 2 * np.pi, 361)
read = np.abs(g_load * np.exp(1j * ph) + d_true)
d_est = (read.max() - read.min()) / 2
g_est = (read.max() + read.min()) / 2
check("rotated-mismatch method recovers directivity and |Gamma|",
      abs(-20 * np.log10(d_est) - 23) < 0.05 and abs(g_est - g_load) < 1e-3,
      f"D = {-20*np.log10(d_est):.2f} dB, |G| = {g_est:.4f}")
for dd, gg in [(25, 0.333), (25, 0.1), (35, 0.333)]:
    dlin = 10 ** (-dd / 20)
    print(f"  forward-power error, D {dd} dB, |Gamma_L| {gg}: {20*np.log10(1-dlin*gg):+.3f} / {20*np.log10(1+dlin*gg):+.3f} dB")

# ---------------------------------------------------------------- 5. shield boxes
print("\n=== 5. Shield boxes, apertures, waveguide-below-cutoff, cavity resonances, TEM cell ===")
p_tx, p_test = -10.0, -130.0
atten = p_tx - p_test
print(f"  conducted test {p_tx} dBm -> {p_test} dBm: path attenuation {atten:.0f} dB, leakage paths >= {atten+20:.0f} dB")
check("isolation rule = attenuation + 20 dB", atten + 20 == 140)
for f in [433e6, 915e6, 2.45e9]:
    lam = C / f
    row = [f"L {L*1e3:4.0f} mm: {20*np.log10(lam/(2*L)):5.1f} dB" for L in (0.001, 0.005, 0.01, 0.03, 0.1)]
    print(f"  slot SE at {f/1e6:6.0f} MHz: " + ", ".join(row))
check("10 mm slot at 915 MHz ~ 24 dB", abs(20 * np.log10(C / 915e6 / 0.02) - 24.3) < 0.2)
print(f"  10 closely spaced holes: -{20*np.log10(10):.0f} dB vs one hole (rule of thumb, holes within ~lambda/2)")
# waveguide below cutoff
for kind, lam_c_factor, dbper in [("circular TE11", 1.706, 32.0), ("rectangular TE10", 2.0, 27.3)]:
    alpha = 2 * np.pi / lam_c_factor * 20 / np.log(10)      # dB per unit diameter/width (f << fc)
    print(f"  {kind}: {alpha:.2f} dB per diameter/width of length (f << fc)")
    check(f"  {kind} attenuation rule {dbper}", abs(alpha - dbper) < 0.1)
d = 0.010
print(f"  10 mm hole: cutoff {C/(1.706*d)/1e9:.1f} GHz; a 20 mm long tube gives {2*32.0:.0f} dB at 915 MHz "
      f"(exact {2*2*np.pi/1.706*np.sqrt(1-(915e6*1.706*d/C)**2)*20/np.log(10):.1f} dB)")


def rect_modes(a, b, d, nmax=3):
    fs = []
    for m in range(0, nmax):
        for n in range(0, nmax):
            for p in range(0, nmax):
                if sum(x > 0 for x in (m, n, p)) >= 2:
                    fs.append(C / 2 * np.sqrt((m / a) ** 2 + (n / b) ** 2 + (p / d) ** 2))
    return sorted(fs)


for dims in [(0.30, 0.20, 0.10), (0.25, 0.18, 0.08), (0.40, 0.30, 0.20)]:
    print(f"  box {dims[0]*1e3:.0f}x{dims[1]*1e3:.0f}x{dims[2]*1e3:.0f} mm: lowest resonances "
          + ", ".join(f"{f/1e6:.0f}" for f in rect_modes(*dims)[:4]) + " MHz")
check("300x200x100 mm box lowest mode ~901 MHz", abs(rect_modes(0.3, 0.2, 0.1)[0] - 901e6) < 2e6)
R = 0.10
print(f"  cylindrical tin, radius 100 mm: TM010 {2.405*C/(2*np.pi*R)/1e6:.0f} MHz")
for p_w, h in [(1.0, 0.1), (0.01, 0.05)]:
    print(f"  TEM cell, P = {p_w} W, septum spacing h = {h*100:.0f} cm: E = sqrt(P Z0)/h = {np.sqrt(p_w*Z0)/h:.1f} V/m")
check("TEM cell 1 W, h 10 cm -> 70.7 V/m", abs(np.sqrt(1 * Z0) / 0.1 - 70.71) < 0.01)

# ---------------------------------------------------------------- 6. EBYTE power & harmonics
print("\n=== 6. E22-400T33D (33 dBm, 433.125 MHz): pads, harmonics, uncertainty ===")
p0 = 33.0
chain = [(20, "20 dB, rated 10 W"), (20, "20 dB, rated 2 W")]
p = p0
for a, name in chain:
    pin_w = 10 ** (p / 10) / 1e3
    pout = p - a
    diss = pin_w - 10 ** (pout / 10) / 1e3
    print(f"  {name}: in {p:5.1f} dBm ({pin_w:.3f} W) -> dissipates {diss:.3f} W, out {pout:5.1f} dBm")
    p = pout
check("first pad dissipates ~1.98 W continuous", abs((10 ** 3.3 / 1e3) * (1 - 0.01) - 1.976) < 0.01)
f0 = 433.125e6
lim = {2: -36.0, 3: -30.0}   # 866 MHz (<1 GHz, outside 470-862) and 1299 MHz (>1 GHz) - IMDA Table 1-a
for n in (2, 3):
    print(f"  harmonic {n}: {n*f0/1e6:.2f} MHz, limit {lim[n]} dBm -> required {p0-lim[n]:.0f} dBc")
check("2nd harmonic must be <= -69 dBc", p0 - lim[2] == 69)
# analyser-generated 2nd harmonic: H2 = 2 P_mixer - IP2 (assumed IP2 = +35 dBm, illustrative)
ip2 = 35.0
pin_sa = p0 - 40
h2_sa = 2 * pin_sa - ip2
print(f"  without filter: fundamental at analyser {pin_sa:.0f} dBm -> analyser H2 {h2_sa:.0f} dBm "
      f"= {h2_sa-pin_sa:.0f} dBc (cannot verify -69 dBc)")
hpf_rej, hpf_il = 40.0, 1.0
pin_f = pin_sa - hpf_rej
h2_f = 2 * pin_f - ip2
dut_h2_at_sa = lim[2] - 40 - hpf_il
print(f"  with HPF (40 dB at f0, 1 dB at 2f0): fundamental {pin_f:.0f} dBm -> analyser H2 {h2_f:.0f} dBm; "
      f"a DUT harmonic at the limit arrives at {dut_h2_at_sa:.0f} dBm")
check("HPF puts analyser H2 > 30 dB below a limit-level DUT harmonic", dut_h2_at_sa - h2_f > 30)
# uncertainty budget (dB, treated as uniform/normal limits -> RSS of standard uncertainties)
gs, gpad = 0.3, (1.1 - 1) / (1.1 + 1)
mm = 20 * np.log10(1 + gs * gpad)
terms = {"pad calibration (VNA, 2 pads)": 0.10, "mismatch module-pad (|Gs| 0.3 assumed, pad VSWR 1.1)": mm,
         "power sensor (thermal, calibrated)": 0.20, "temperature drift of pads under 2 W": 0.10}
rss = np.sqrt(sum(v ** 2 for v in terms.values()))
for k, v in terms.items():
    print(f"  +/-{v:.3f} dB  {k}")
print(f"  RSS (k=1 style combination of limits): +/-{rss:.2f} dB; with a tinySA (+/-1.5 dB assumed) instead of a sensor: "
      f"+/-{np.sqrt(rss**2 - 0.2**2 + 1.5**2):.2f} dB")
check("power-meter route ~ +/-0.3 dB", 0.2 < rss < 0.4)
# GUM-style: rectangular limits / sqrt(3), U-shaped mismatch / sqrt(2), then expanded k = 2
u = np.sqrt((0.10 / np.sqrt(3)) ** 2 + (mm / np.sqrt(2)) ** 2 + (0.20 / np.sqrt(3)) ** 2 + (0.10 / np.sqrt(3)) ** 2)
print(f"  GUM combination: standard uncertainty {u:.3f} dB, expanded (k = 2) +/-{2*u:.2f} dB")
check("GUM expanded uncertainty ~ +/-0.33 dB", abs(2 * u - 0.33) < 0.02)

# ---------------------------------------------------------------- 7. Wheeler cap
print("\n=== 7. Wheeler cap: uncertainty and cap resonance ===")
for rf_, rc_ in [(12.0, 1.5), (2.0, 0.6), (0.9, 0.5)]:
    eta = 1 - rc_ / rf_
    e = []
    for _ in range(20000):
        a = rf_ + rng.normal(0, 0.1 + 0.01 * rf_)
        b = rc_ + rng.normal(0, 0.1 + 0.01 * rc_)
        e.append(1 - b / a)
    e = np.array(e)
    print(f"  R_free {rf_:5.1f}, R_cap {rc_:4.1f} ohm: eta {eta*100:5.1f} % "
          f"(1-sigma {np.std(e)*100:4.1f} % for 0.1 ohm + 1 % resistance errors)")
    if rf_ < 1:
        sd_small = np.std(e)
    if rf_ > 10:
        sd_large = np.std(e)
check("small antennas (R_free < 1 ohm) give >10 % efficiency uncertainty; R_free 12 ohm < 2 %",
      sd_small > 0.10 and sd_large < 0.02)
for f in [433e6, 868e6, 915e6, 2.45e9]:
    r = C / f / (2 * np.pi)
    a = 2 * r
    f_cube = C / (a * np.sqrt(2))
    print(f"  {f/1e6:6.0f} MHz: radiansphere r = {r*1e3:5.1f} mm; cube of side {a*1e3:5.0f} mm resonates at "
          f"{f_cube/1e6:6.0f} MHz ({f_cube/f:.2f} x f)")
check("cube cap with half-side lambda/2pi resonates at pi/sqrt(2) = 2.22 f", abs(np.pi / np.sqrt(2) - 2.221) < 1e-3)
print("  sphere of radius lambda/2pi: lowest TM mode at ka = 2.744 -> 2.74 x f")

# ---------------------------------------------------------------- 8. attenuator range test
print("\n=== 8. Range testing with attenuators ===")
d0, A = 200.0, 43.5
deq = d0 * 10 ** (A / 20)
print(f"  {A} dB extra at {d0:.0f} m -> free-space equivalent {deq/1e3:.1f} km; 2-ray (d^-4) regime: {d0*10**(A/40)/1e3:.2f} km")
check("43.5 dB at 200 m = 29.9 km (matches antenna-range-ota-testing Ex. 3)", abs(deq - 29.9e3) < 100)
for err in [0.5, 1.0, 2.0]:
    print(f"  attenuator error {err} dB -> range error {100*(10**(err/20)-1):.1f} %")
print(f"  leakage around a 100 dB attenuator must be >= 120 dB (else the test overstates margin)")

# ---------------------------------------------------------------- 9. pulsed signals on an SA
print("\n=== 9. Pulse desensitisation (Gaussian RBW) ===")
K = np.sqrt(np.pi / (2 * np.log(2)))
check("Gaussian impulse bandwidth factor K = 1.505 (AN 150-2 quotes ~1.5)", abs(K - 1.505) < 1e-3, f"K = {K:.4f}")
B = 1.0
a = 2 * np.log(2) / B ** 2         # H(f) = exp(-a f^2), voltage 3 dB at f = B/2
hfun = lambda tt: np.sqrt(np.pi / a) * np.exp(-(np.pi ** 2) * tt ** 2 / a)   # inverse FT of exp(-a f^2)
tt = np.linspace(-20, 20, 400001)
_trap = getattr(np, "trapezoid", None) or np.trapz
check("impulse response integrates to H(0) = 1 (CW gain)", abs(_trap(hfun(tt), tt) - 1) < 1e-6)
for tb in [0.02, 0.05, 0.1, 0.2, 0.5, 1.0]:
    tau = tb / B
    # symmetric pulse -> output envelope peaks at t = 0: integral of h over the pulse
    tw = np.linspace(-tau / 2, tau / 2, 20001)
    peak = _trap(hfun(tw), tw)
    approx = K * tau * B
    print(f"  tau*B = {tb:4.2f}: peak/CW = {20*np.log10(peak):6.2f} dB, 20log(K tau B) = {20*np.log10(approx):6.2f} dB")
    if tb == 0.2:
        err02 = 20 * np.log10(approx) - 20 * np.log10(peak)
check("approximation within 0.3 dB for tau*B <= 0.2", abs(err02) < 0.3, f"error {err02:.2f} dB at 0.2")
for name, tau, rbw in [("0.5 us pulses (ADS-B-like), RBW 300 kHz", 0.5e-6, 300e3),
                       ("1 us radar pulse, RBW 100 kHz", 1e-6, 100e3)]:
    print(f"  {name}: desensitisation {20*np.log10(K*tau*rbw):.1f} dB")
prf, tau = 1e3, 1e-4
print(f"  line spectrum (RBW < 0.3 PRF): central line = 20log(tau PRF) = {20*np.log10(tau*prf):.0f} dB below the pulse peak")

# ---------------------------------------------------------------- 10. ferrite permeability
print("\n=== 10. Ferrite core permeability ===")
OD, ID, Ht = 9.5e-3, 4.75e-3, 3.18e-3            # FT37-size toroid
Lair_per_n2 = MU0 * Ht * np.log(OD / ID) / (2 * np.pi)
for mu in [800, 125]:
    print(f"  FT37-size, mu_i {mu}: A_L = {mu*Lair_per_n2*1e9:.0f} nH/turn^2")
check("FT37-size with mu 800 -> ~353 nH/turn^2", abs(800 * Lair_per_n2 * 1e9 - 353) < 3)
N, f = 5, 10e6
L0 = Lair_per_n2 * N ** 2
Z = 30 + 140j   # synthetic measurement
mu_p, mu_pp = Z.imag / (2 * np.pi * f * L0), Z.real / (2 * np.pi * f * L0)
print(f"  N = {N}, f = 10 MHz, Z = {Z} ohm -> L0 = {L0*1e9:.2f} nH, mu' = {mu_p:.0f}, mu'' = {mu_pp:.0f} "
      f"(wire and fixture parasitics must be de-embedded)")

# ---------------------------------------------------------------- 11. is it transmitting?
print("\n=== 11. Quick 'is it transmitting' levels ===")
for eirp_dbm, d, f in [(20, 1, 433e6), (20, 10, 433e6), (33, 10, 433e6), (14, 3, 915e6)]:
    e = np.sqrt(30 * 10 ** (eirp_dbm / 10) / 1e3) / d
    pr = eirp_dbm - 20 * np.log10(4 * np.pi * d * f / C)
    print(f"  {eirp_dbm} dBm EIRP at {d:2d} m, {f/1e6:.0f} MHz: E = {e:.3f} V/m, 0 dBi SDR antenna gets {pr:6.1f} dBm")
check("100 mW EIRP at 1 m = 1.73 V/m", abs(np.sqrt(30 * 0.1) - 1.732) < 1e-3)

print(f"\n{sum(results)}/{len(results)} checks passed")
print("ALL PASS" if all(results) else "SOME FAILED")
