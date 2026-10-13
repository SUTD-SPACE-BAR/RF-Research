#!/usr/bin/env python3
"""
Verification for kb/03-transmission-lines-matching/broadband-matching-bode-fano.md

Checks:
  1. Fano's integral is a fixed budget: for a parallel RC load with R = R0 and NO matching network,
     int_0^inf ln(1/|Gamma|) dw = pi/(RC) exactly (Gamma has no RHP zeros).
  2. For lossless ladder matching networks (random and optimised), the integral never exceeds pi/(RC).
  3. Optimised N-element lossless ladders approach the Bode-Fano rectangular bound
     Gamma_min = exp(-pi / (dw R C)) as N grows.
  4. Series-RLC (resonant, antenna-like) load: bound  B * ln(1/Gm) <= pi / Q  (fractional B);
     compare single-tuned VSWR bandwidth (Yaghjian-Best (s-1)/(Q sqrt(s))) with the Bode-Fano limit.
  5. Chu limit Q for small antennas at 433 / 915 MHz and implied best-case bandwidths.

Run: python3 tools/verify/tline_bode_fano.py
"""
import warnings
import numpy as np
from scipy.integrate import quad

warnings.filterwarnings("ignore")
from scipy.optimize import minimize

ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


R0 = 50.0
R = 50.0
C = 5e-12
RC = R * C
bound = np.pi / RC


# ---------------------------------------------------------------- helpers
def zload(w):
    return R / (1 + 1j * w * R * C)


def ladder_zin(w, elems):
    """elems: list of ('s',L) series inductor / ('p',Cp) shunt capacitor / ('sc',C) series C / ('pl',L) shunt L,
    applied from the LOAD outward toward the source."""
    Z = zload(w)
    for kind, v in elems:
        if kind == "s":
            Z = Z + 1j * w * v
        elif kind == "p":
            Z = 1 / (1 / Z + 1j * w * v)
        elif kind == "sc":
            Z = Z + 1 / (1j * w * v)
        elif kind == "pl":
            Z = 1 / (1 / Z + 1 / (1j * w * v))
    return Z


def fano_integral(elems, wmax_factor=2000):
    f = lambda w: np.log(1 / abs((ladder_zin(w, elems) - R0) / (ladder_zin(w, elems) + R0)))
    w_c = 1 / RC
    # integrate on a log grid, piecewise, to catch narrow features
    edges = np.concatenate([[0], w_c * np.logspace(-3, np.log10(wmax_factor), 60)])
    tot = 0.0
    for a, b in zip(edges[:-1], edges[1:]):
        tot += quad(f, a, b, limit=400)[0]
    # analytic tail: for large w, |Gamma| -> 1 - 2/(w R C)*(...)~; ln(1/|G|) ~ 2 R0/(w^2 R^2 C^2 R) ... tiny
    return tot


# ---------------------------------------------------------------- 1. bare load
I0 = fano_integral([])
check("bare parallel-RC load: integral = pi/RC (equality, no RHP zeros)", abs(I0 - bound) / bound < 2e-3,
      f"(integral {I0:.4e}, pi/RC {bound:.4e})")

# ---------------------------------------------------------------- 2. random lossless ladders never beat it
rng = np.random.default_rng(3)
worst = 0
for _ in range(15):
    n = rng.integers(1, 4)
    elems = []
    for k in range(n):
        elems.append(("s", 10 ** rng.uniform(-9.5, -7.5)))
        elems.append(("p", 10 ** rng.uniform(-12.5, -10.5)))
    Ii = fano_integral(elems)
    worst = max(worst, Ii / bound)
check("15 random lossless LC ladders: integral <= pi/RC", worst <= 1 + 3e-3, f"(max ratio {worst:.4f})")

# ---------------------------------------------------------------- 3. optimised ladders vs rectangular bound
# Use a higher-Q load so the bound bites: 50 ohm || C with Q = w0 R C = 5 at 915 MHz, 20 % band.
f0 = 915e6
w0 = 2 * np.pi * f0
Qload = 5.0
C = Qload / (w0 * R)
RC = R * C
bound = np.pi / RC
fbw = 0.20
Gm_bf = np.exp(-np.pi / (w0 * fbw * RC))
print(f"      load: 50 ohm || {C*1e12:.2f} pF (Q = {Qload} at 915 MHz); band 20 %;"
      f" Bode-Fano rectangular bound |Gamma| >= {Gm_bf:.4f} (RL <= {-20*np.log10(Gm_bf):.2f} dB)")


# band edges placed geometrically about f0 (bandpass mapping), 20 % fractional bandwidth
w1 = w0 * (np.sqrt(1 + fbw**2 / 4) - fbw / 2)
w2 = w1 + fbw * w0
wb = np.linspace(w1, w2, 121)
Gm_bf = np.exp(-np.pi / ((w2 - w1) * RC))
Lres = 1 / (w0**2 * C)          # shunt L resonating the load C
nominal = {"pl": Lres, "p": C, "s": R0 / w0, "sc": 1 / (w0 * R0)}
topologies = {                  # bandpass ladders from the load outward, counted in resonators
    1: ["pl"],
    2: ["pl", "s", "sc"],
    3: ["pl", "s", "sc", "pl", "p"],
    4: ["pl", "s", "sc", "pl", "p", "s", "sc"],
}


def gam_band(x, kinds):
    """x = log(element/nominal) ..., log(t): ideal transformer ratio t on the source side (ref. R0*t)."""
    vals = np.exp(x[:-1]) * np.array([nominal[k] for k in kinds])
    t = np.exp(x[-1])
    Z = ladder_zin(wb, list(zip(kinds, vals)))
    return np.abs((Z - R0 * t) / (Z + R0 * t)), vals


results = {}
rng2 = np.random.default_rng(0)
for N, kinds in topologies.items():
    best, bestx = 1.0, None
    for trial in range(60):
        x0 = np.concatenate([rng2.uniform(-2.5, 2.5, len(kinds)), [rng2.uniform(-1.5, 1.5)]])
        g0, _ = gam_band(x0, kinds)
        if not np.all(np.isfinite(g0)):
            continue
        z0 = np.concatenate([x0, [g0.max()]])
        cons = {"type": "ineq", "fun": lambda z, k=kinds: z[-1] - gam_band(z[:-1], k)[0]}
        r = minimize(lambda z: z[-1], z0, constraints=[cons], method="SLSQP",
                     options=dict(maxiter=500, ftol=1e-12))
        g, _ = gam_band(r.x[:-1], kinds)
        if np.all(np.isfinite(g)) and g.max() < best:
            best, bestx = g.max(), r.x[:-1]
    results[N] = best
    _, vals = gam_band(bestx, kinds)
    Ii = fano_integral(list(zip(kinds, vals)))
    print(f"      {N} resonator(s): best worst-case in-band |Gamma| = {best:.4f} (RL {-20*np.log10(best):.2f} dB); "
          f"Fano integral / (pi/RC) = {Ii/bound:.3f}")
print(f"      Bode-Fano (infinitely many elements): {Gm_bf:.4f} (RL {-20*np.log10(Gm_bf):.2f} dB)")
check("optimised ladders never beat the Bode-Fano bound", all(v >= Gm_bf * 0.999 for v in results.values()))
check("adding resonators approaches the bound (monotone improvement)",
      results[1] > results[2] > results[3] > results[4] > Gm_bf)
check("single resonator + ideal transformer: |Gamma| = sqrt(2)-1 = 0.4142 for decrement 1 (Q*FBW = 1)",
      abs(results[1] - (np.sqrt(2) - 1)) < 2e-3)

# ---------------------------------------------------------------- 4. series RLC (antenna-like) load
Qa = 12.9
for s in [1.5, 2.0, 3.0]:
    Gm = (s - 1) / (s + 1)
    fbw_single = (s - 1) / (Qa * np.sqrt(s))          # Yaghjian-Best, single tuned, matched at centre
    fbw_bf = np.pi / (Qa * np.log(1 / Gm))            # Bode-Fano upper limit (infinite-order network)
    print(f"      Q = {Qa}: VSWR {s}: single-tuned BW = {fbw_single*100:.2f} %, Bode-Fano max = {fbw_bf*100:.2f} %"
          f"  (ratio {fbw_bf/fbw_single:.2f})")
# numerically confirm the single-tuned formula for s = 2 on a series RLC with Q = 12.9
wr = 1.0
Ra, La = 50.0, Qa * 50.0 / wr
Ca = 1 / (wr**2 * La)
ww = np.linspace(0.8, 1.2, 400001)
Za = Ra + 1j * ww * La + 1 / (1j * ww * Ca)
G = np.abs((Za - 50) / (Za + 50))
s_ = (1 + G) / (1 - G)
band = ww[s_ <= 2.0]
fbw_num = (band.max() - band.min()) / wr
check("single-tuned series RLC: VSWR-2 bandwidth = (s-1)/(Q sqrt s)", abs(fbw_num - 1 / (Qa * np.sqrt(2))) < 2e-4,
      f"({fbw_num*100:.3f} % vs {100/(Qa*np.sqrt(2)):.3f} %)")

# ---------------------------------------------------------------- 5. Chu limit examples
c0 = 299_792_458.0
for f, a_cm in [(433e6, 5.6), (433e6, 5.0), (433e6, 2.0), (915e6, 3.0), (915e6, 2.0), (915e6, 1.0), (1575.42e6, 2.0), (2450e6, 1.0)]:
    k = 2 * np.pi * f / c0
    ka = k * a_cm / 100
    Qchu = 1 / ka**3 + 1 / ka
    bw1 = 1 / (Qchu * np.sqrt(2))
    bwbf = np.pi / (Qchu * np.log(3))
    print(f"      f = {f/1e6:.0f} MHz, radius a = {a_cm} cm: ka = {ka:.3f}, Q_Chu = {Qchu:.1f}, "
          f"VSWR<2 BW: single-tuned <= {bw1*100:.2f} % ({bw1*f/1e6:.1f} MHz), Bode-Fano <= {bwbf*100:.2f} % ({bwbf*f/1e6:.1f} MHz)")
k = 2 * np.pi * 433e6 / c0
ka = k * 0.05
check("Chu Q for 433 MHz, a = 5 cm is ~12.9", abs((1 / ka**3 + 1 / ka) - 12.9) < 0.2)

# ---------------------------------------------------------------- 6. Q from a measured impedance sweep (Q_Z)
# Yaghjian & Best (2005): Q_Z(w0) ~ (w0 / (2 R(w0))) |Z'(w0)| at a frequency where the antenna is tuned
# (X = 0, or after adding the series reactance that tunes it).  Check on a series RLC and on a
# parallel-RLC-plus-series-L "antenna" model.
wr = 2 * np.pi * 433e6
Rr, Lr = 30.0, 30.0 * 40 / wr
Cr = 1 / (wr**2 * Lr)
dw = wr * 1e-6
Zf = lambda w: Rr + 1j * w * Lr + 1 / (1j * w * Cr)
dZ = (Zf(wr + dw) - Zf(wr - dw)) / (2 * dw)
QZ = wr / (2 * Rr) * abs(dZ)
check("Q_Z = (w0/2R)|dZ/dw| recovers Q = 40 of a series RLC", abs(QZ - 40) < 1e-4, f"({QZ:.3f})")

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
