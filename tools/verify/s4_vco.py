#!/usr/bin/env python3
# Runtime (W6-F5, 2026-10-14): ~198 s (3.3 min) measured on a 10-core Apple-silicon Mac, run 3 at a time
# under load average 7-70 from other jobs; expect less on an idle machine. It exceeds the 120 s per-script budget
# used by the D7 verify sweep, so give it a >= 15 min timeout and run it with `python3 -u` to see progress. Needs ngspice on PATH (sections 2-3 are skipped without it).
# Measured run: exit 0, no FAIL lines. Comment only; no code or results changed.
"""
W5-S4 verification for kb/05-analog-electronics/oscillators.md (#level-3--cross-coupled-lc-vcos-...):
  1. Cross-coupled pair: differential negative resistance -2/gm; start-up gm*Rp > 1 (Rp = per-side tank).
  2. ngspice (batch CLI) NMOS cross-coupled LC oscillator at ~433 MHz: start-up threshold vs tail current,
     current-limited amplitude vs (4/pi) I_T Rp, frequency vs hand formula.
  3. ngspice varactor tuning (junction-diode varactors) vs the analytic C(V) prediction.
  4. Switched-capacitor bank arithmetic: bands, overlap, K_VCO reduction, switch Q and Ron*Coff trade.
  5. Quadrature VCO (two coupled tanks, van der Pol devices, ODE): frequency shift = m*w0/(2Q),
     90 deg phase, phase error vs tank mismatch, and the phase-slope (effective-Q) penalty.
Run: python3 tools/verify/s4_vco.py      (needs ngspice on PATH for sections 2-3; skipped otherwise)
"""
import os
import shutil
import subprocess
import tempfile
import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import hilbert

TP = 2 * np.pi

# ---------------------------------------------------------------- 1
print("=== 1. Cross-coupled pair negative resistance ===")
# Each device: drain current gm*v_gs. With gate1 = drain2 and gate2 = drain1, a differential test voltage
# v_d = v1 - v2 makes i1 - i2 = gm*(v2 - v1) = -gm*v_d; the differential current is i_d = (i1 - i2)/2
# into the port (current in at node 1, out at node 2) -> Z_d = v_d/i_d = -2/gm.
gm = 5e-3
print(f"gm = {gm*1e3} mS -> R_diff = -2/gm = {-2/gm:.0f} ohm; per-side tank Rp: differential tank = 2Rp;"
      f" start-up 2/gm < 2Rp  <=>  gm*Rp > 1")
L, C, Q = 10e-9, 13.5e-12, 15.0
f0 = 1 / (TP * np.sqrt(L * C))
Rp = Q * TP * f0 * L
print(f"tank L {L*1e9:.0f} nH, C {C*1e12:.1f} pF, Q {Q}: f0 = {f0/1e6:.1f} MHz, Rp = {Rp:.0f} ohm, gm_crit = {1/Rp*1e3:.2f} mS")
KP, WL, VT = 200e-6, 200.0, 0.5
beta = KP * WL
ID_crit = (1 / Rp) ** 2 / (2 * beta)
print(f"NMOS level 1, KP {KP*1e6:.0f} uA/V^2, W/L {WL:.0f}: gm = sqrt(2*beta*ID) -> I_T,crit = 2*ID = {2*ID_crit*1e6:.0f} uA")

# ---------------------------------------------------------------- 2, 3
NG = shutil.which("ngspice")

def run_osc(IT, vtune=None, tstop=400e-9, cvar=None):
    tank_c = "" if vtune is not None else f"C1 d1 0 {C}\nC2 d2 0 {C}\n"
    var = ""
    if vtune is not None:
        var = (f"Cf1 d1 0 {cvar['Cfix']}\nCf2 d2 0 {cvar['Cfix']}\n"
               f"Vt vt 0 DC {vtune}\nDv1 vt d1 dvar\nDv2 vt d2 dvar\n"
               f".model dvar D(IS=1e-16 CJO={cvar['CJO']} VJ={cvar['VJ']} M={cvar['M']} RS=0.5)\n")
    net = f"""* cross-coupled NMOS LC oscillator
VDD vdd 0 DC 1.8
L1 vdd d1 {L}
L2 vdd d2 {L}
R1 vdd d1 {Rp}
R2 vdd d2 {Rp}
{tank_c}{var}M1 d1 d2 s 0 nm W=200u L=1u
M2 d2 d1 s 0 nm W=200u L=1u
IT s 0 DC {IT}
.model nm NMOS(LEVEL=1 VTO={VT} KP={KP} LAMBDA=0)
.ic v(d1)=1.81 v(d2)=1.79
.tran 20p {tstop} 0 20p uic
.control
run
wrdata OUTFILE v(d1) v(d2)
quit
.endc
.end
"""
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "o.txt")
        cir = os.path.join(td, "o.cir")
        open(cir, "w").write(net.replace("OUTFILE", out))
        subprocess.run([NG, "-b", cir], capture_output=True, text=True, timeout=600)
        d = np.loadtxt(out)
    t, v1, v2 = d[:, 0], d[:, 1], d[:, 3]
    return t, v1 - v2

def analyse(t, vd):
    n = len(t)
    a0 = np.max(np.abs(vd[n // 10: n // 5]))
    a1 = np.max(np.abs(vd[-n // 5:]))
    seg = t > t[-1] * 0.7
    tt, vv = t[seg], vd[seg]
    zc = tt[1:][(vv[:-1] < 0) & (vv[1:] >= 0)]
    f = (len(zc) - 1) / (zc[-1] - zc[0]) if len(zc) > 2 else float("nan")
    return a0, a1, f

if NG:
    print("\n=== 2. ngspice start-up and amplitude (differential peak) ===")
    print("(initial kick 0.02 V differential)")
    print(" I_T (uA)  early pk (V)  late pk (V)  grows?   f (MHz)   (4/pi) I_T Rp (V)")
    for IT in (100e-6, 160e-6, 300e-6, 1e-3, 2e-3):
        t, vd = run_osc(IT, tstop=1500e-9 if IT < 400e-6 else 400e-9)
        a0, a1, f = analyse(t, vd)
        print(f"{IT*1e6:8.0f}  {a0:12.4f}  {a1:11.4f}  {'yes' if a1 > 0.025 else 'no ':5s}  {f/1e6:8.1f}   {4/np.pi*IT*Rp:8.3f}")
    print("\n=== 3. ngspice varactor tuning vs analytic ===")
    cv = dict(Cfix=8e-12, CJO=10e-12, VJ=0.7, M=0.5)
    print(" Vtune  Vr(DC)  C_var analytic (pF)  f analytic (MHz)  f ngspice (MHz)")
    for vt in (0.0, 0.6, 1.2, 1.6):
        vr = 1.8 - vt
        cvv = cv["CJO"] / (1 + vr / cv["VJ"]) ** cv["M"]
        fa = 1 / (TP * np.sqrt(L * (cv["Cfix"] + cvv)))
        t, vd = run_osc(1e-3, vtune=vt, tstop=300e-9, cvar=cv)
        _, _, fs = analyse(t, vd)
        print(f"{vt:5.1f}  {vr:6.1f}  {cvv*1e12:18.2f}  {fa/1e6:16.1f}  {fs/1e6:15.1f}")
    cmin = cv["CJO"] / (1 + 1.8 / cv["VJ"]) ** 0.5
    cmax = cv["CJO"] / (1 + 0.2 / cv["VJ"]) ** 0.5
    print(f"tuning ratio sqrt((Cfix+Cmax)/(Cfix+Cmin)) = {np.sqrt((cv['Cfix']+cmax)/(cv['Cfix']+cmin)):.3f}"
          f" (varactor alone {np.sqrt(cmax/cmin):.3f}) -> fixed C dilutes range")
else:
    print("\n(ngspice not found: sections 2-3 skipped)")

# ---------------------------------------------------------------- 4
print("\n=== 4. Switched-capacitor bank ===")
fmin, fmax = 3.4e9, 4.0e9
ratio = (fmax / fmin) ** 2
print(f"cover {fmin/1e9}-{fmax/1e9} GHz (/4 -> 850-1000 MHz, /8 -> 425-500 MHz): C_max/C_min = {ratio:.3f}")
Ltank = 1.0e-9
Cmin = 1 / ((TP * fmax) ** 2 * Ltank)
Cmax = 1 / ((TP * fmin) ** 2 * Ltank)
for nbits in (0, 3, 4, 5):
    nb = 2 ** nbits
    dC = (Cmax - Cmin)
    var_needed = dC / nb * 1.3  # 30 % overlap between adjacent bands
    kv = (fmax - fmin) / nb * 1.3 / 1.0  # Hz per volt for a 1 V usable tuning range
    print(f"{nbits} bits: {nb:3d} bands, varactor swing {var_needed*1e15:7.1f} fF, K_VCO ~ {kv/1e6:6.1f} MHz/V (1 V range)")
print(f"(C_min {Cmin*1e12:.2f} pF, C_max {Cmax*1e12:.2f} pF for L = 1 nH)")
w = TP * 3.7e9
for Ron, Cu in ((20.0, 100e-15), (10.0, 100e-15), (5.0, 200e-15)):
    print(f"unit {Cu*1e15:.0f} fF, switch Ron {Ron} ohm: Q_on = 1/(w Ron C) = {1/(w*Ron*Cu):6.0f}")
RonCoff = 20.0 * 25e-15  # technology figure of merit Ron*Coff (illustrative 0.5 ps)
for Ron in (40.0, 20.0, 10.0):
    Coff = RonCoff / Ron
    Coff_series = 100e-15 * Coff / (100e-15 + Coff)
    print(f"Ron {Ron:4.0f} ohm -> Coff {Coff*1e15:5.1f} fF -> unit 100 fF 'off' = {Coff_series*1e15:5.1f} fF "
          f"(on/off ratio {100/(Coff_series*1e15):4.1f}), Q_on {1/(w*Ron*100e-15):5.0f}")

# ---------------------------------------------------------------- 5
print("\n=== 5. Quadrature VCO: two van der Pol tanks, cross-coupled with + and - signs (ODE) ===")
def qvco(m, delta, Qt=10.0, margin=2.0, ncyc=3000):
    # normalised: w0 = 1, C = 1, L = 1/w^2, G = 1/Q; device i = -g1 v + g3 v^3 with g1 = margin*G.
    # tank 1 is driven by +Gc*v2, tank 2 by -Gc*v1 (the QVCO's in-phase / anti-phase coupling).
    G = 1 / Qt
    g1, g3 = margin * G, margin * G / 3
    w2 = 1 + delta
    Gc = m * G
    def rhs(t, y):
        v1, i1, v2, i2 = y
        return [-(G * v1 + i1 - g1 * v1 + g3 * v1**3 - Gc * v2), v1,
                -(G * v2 + i2 - g1 * v2 + g3 * v2**3 + Gc * v1), w2**2 * v2]
    T = ncyc * TP
    sol = solve_ivp(rhs, (0, T), [0.01, 0, 0, 0], max_step=0.05, rtol=1e-8, atol=1e-10, dense_output=True)
    tu = np.linspace(0.8 * T, T, 300000)
    y = sol.sol(tu)
    a, b = y[0], y[2]
    ha, hb = hilbert(a), hilbert(b)
    mid = slice(30000, -30000)
    ph = np.unwrap(np.angle(hb / ha))[mid]
    drift = np.degrees(ph[-1] - ph[0])
    mean = (np.degrees(np.mean(ph)) + 180) % 360 - 180
    zc = tu[1:][(a[:-1] < 0) & (a[1:] >= 0)]
    wosc = TP * (len(zc) - 1) / (zc[-1] - zc[0])
    return wosc, mean, drift, np.median(np.abs(hb[mid])) / np.median(np.abs(ha[mid]))
Qt = 10.0
print(f"Q = {Qt}. Locked if the phase drift over the window is ~0; the mode is +90 or -90 deg.")
print(" margin  m     delta    w_osc/w0-1  m/(2Q)   phase deg  error deg  Q*delta/m (deg)  amp ratio  locked")
for margin in (2.0, 3.0):
    for m, dl in ((0.2, 0.0), (0.4, 0.0), (0.4, 0.0005), (0.4, 0.001), (0.4, 0.002), (0.2, 0.0005), (0.2, 0.002), (0.2, 0.005)):
        wo, ph, dr, ar = qvco(m, dl, Qt, margin)
        locked = abs(dr) < 30
        err = ph - 90 if ph > 0 else ph + 90
        print(f"{margin:5.1f}  {m:4.1f}  {dl:7.4f}   {wo-1:+.5f}   {m/(2*Qt):.4f}   {ph:8.2f}  {err:8.2f}"
              f"   {np.degrees(Qt*dl/m):8.2f}        {ar:6.3f}    {'yes' if locked else 'NO'}")
for m in (0.2, 0.4):
    pen = 20 * np.log10(1 + m**2)
    print(f"m {m}: tank runs at tan(phi) = m off resonance -> phase slope x cos^2(phi) = 1/(1+m^2): "
          f"Leeson penalty ~ {pen:.2f} dB (tank only; coupling devices add noise)")
