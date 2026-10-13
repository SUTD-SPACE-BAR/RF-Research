#!/usr/bin/env python3
"""sim_ngspice_examples.py — runs the example netlists printed on kb/16-simulation-tools/spice-circuit-simulation.md
with ngspice and checks them against closed-form results (tools/rfcalc).

Two routes to ngspice on macOS are exercised:
  * the ngspice CLI from Homebrew (`brew install ngspice`, ngspice-47), batch mode `ngspice -b file.cir`;
  * the ngspice shared library bundled inside KiCad (ngspice-44.2 in KiCad 10), driven through ctypes by
    tools/verify/analog_ngspice.py (W2-B1) — no separate install needed.

Examples (pre-registered expectations in brackets):
  A. 433 MHz L-match 12.5 -> 50 ohm, two-port .sp analysis        [|S11| < 0.01 at 433 MHz; RL >= 10 dB span
                                                                   ~ 1/Q_n of f0; finite-Q loss ~ 0.21 dB]
  B. 5th-order Butterworth low-pass, 600 MHz, 50 ohm (.sp)        [-3.01 dB at fc; 16.05 dB at 2 x 433 MHz;
                                                                   33.6 dB at 3 x 433 MHz; exact to < 0.05 dB]
  C. Colpitts oscillator (transient + FFT)                        [f within 5 % of 1/(2 pi sqrt(L C1C2/(C1+C2)))]
  D. 6 dB pi attenuator noise analysis (.noise)                   [NF = 6.02 dB at 290 K; 6.13 dB at SPICE's
                                                                   default 27 C]
  E. S-parameter network -> scikit-rf vector fit -> SPICE subcircuit -> ngspice   [< 0.01 dB from the original]
Addendum (after first run, 2026-09-27 — the bracketed expectations above are left as written):
  B: the "16.05 dB" hand estimate was a slip; 10log10(1+(867.84/600)^10) = 16.14 dB, which SPICE matches.
  A: the 0.21 dB figure assumed capacitor Q = 300; with an ideal capacitor SPICE gives 0.186 dB vs 0.184 dB estimate.
  D: 27 C gives 6.149 dB if the source resistor is also at 27 C (L T/T0) and 6.112 dB if only the pad is warm;
     "6.13" was a rough guess. A noisy load adds 3 dB (9.01 dB) - hence `noisy=0`.
Run: python3 tools/verify/sim_ngspice_examples.py
"""
import math
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from rfcalc import matching, noise as rnoise   # noqa: E402

NGSPICE = shutil.which("ngspice") or "/opt/homebrew/bin/ngspice"
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def run_cli(netlist, datafile="out.dat"):
    """Run a netlist with the ngspice CLI in a temp dir; the netlist's .control block must `wrdata out.dat ...`.
    Returns the numeric columns of out.dat and the stdout text."""
    d = tempfile.mkdtemp(prefix="rfkb_spice_")
    p = os.path.join(d, "c.cir")
    with open(p, "w") as fh:
        fh.write(netlist)
    r = subprocess.run([NGSPICE, "-b", p], cwd=d, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"ngspice exit {r.returncode}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    data = np.loadtxt(os.path.join(d, datafile), ndmin=2) if datafile else None
    return data, r.stdout


# ------------------------------------------------------------------ A. L-match
LMATCH = """* A: 433 MHz L-match, 12.5 ohm load (port 2) to 50 ohm (port 1): shunt C at the 50 ohm side, series L
* values from rfcalc: python -m rfcalc lmatch 12.5 --f 433M  -> 7.96 nH, 12.73 pF
V1 in 0 dc 0 ac 1 portnum 1 z0 50
C1 in 0 {c1}
L1 in mid {l1}
RLS mid out {rl_esr}
V2 out 0 dc 0 ac 1 portnum 2 z0 12.5
.control
sp lin 2601 250meg 616meg
let s11m = mag(s_1_1)
let s21m = mag(s_2_1)
wrdata out.dat s11m s21m
quit
.endc
.end
"""


def example_a():
    print("=== A. L-match 12.5 -> 50 ohm at 433 MHz (.sp two-port analysis) ===")
    q, xs, xp = matching.l_match_real(50.0, 12.5)
    L = xs / (2 * math.pi * 433e6)
    C = -1 / (2 * math.pi * 433e6 * xp)
    data, _ = run_cli(LMATCH.format(c1=f"{C:.6e}", l1=f"{L:.6e}", rl_esr="1e-6"))
    f, s11 = data[:, 0], data[:, 1]
    i0 = np.argmin(abs(f - 433e6))
    band = f[s11 <= 10 ** (-10 / 20)]
    print(f"   L = {L*1e9:.3f} nH, C = {C*1e12:.3f} pF, Q_n = {q:.3f}; |S11(433 MHz)| = {s11[i0]:.2e}; "
          f"RL >= 10 dB from {band.min()/1e6:.0f} to {band.max()/1e6:.0f} MHz ({(band.max()-band.min())/433e6*100:.0f} %)")
    check("A: ideal L-match |S11| < 0.01 at 433 MHz", s11[i0] < 0.01)
    # finite Q: inductor Q 40 (ESR = X/Q in series); the capacitor ideal here
    esr = xs / 40
    data, _ = run_cli(LMATCH.format(c1=f"{C:.6e}", l1=f"{L:.6e}", rl_esr=f"{esr:.6e}"))
    s21 = data[np.argmin(abs(data[:, 0] - 433e6)), 3]
    il = -20 * math.log10(s21)
    est = matching.l_match_loss_db(q, 40)
    print(f"   inductor Q = 40 (ESR {esr:.3f} ohm): |S21| loss = {il:.3f} dB; estimate 10log(1+Qn/QL) = {est:.3f} dB")
    check("A: finite-Q loss within 15 % of the 10log(1+Qn/QL) estimate", abs(il - est) / est < 0.15)
    return f, s11


# ------------------------------------------------------------------ B. Butterworth LPF
LPF = """* B: 5th-order Butterworth low-pass (C-L-C-L-C), fc = 600 MHz, 50 ohm (g = 0.618 1.618 2 1.618 0.618)
V1 in 0 dc 0 ac 1 portnum 1 z0 50
C1 in 0 {c1}
L2 in n2 {l2}
C3 n2 0 {c3}
L4 n2 out {l4}
C5 out 0 {c5}
V2 out 0 dc 0 ac 1 portnum 2 z0 50
.control
sp lin 1001 1meg 1500meg
let s21db = db(s_2_1)
let s11db = db(s_1_1)
wrdata out.dat s21db s11db
quit
.endc
.end
"""


def example_b():
    print("=== B. 5th-order Butterworth LPF, fc = 600 MHz (.sp) ===")
    fc, R = 600e6, 50.0
    w = 2 * math.pi * fc
    g = [2 * math.sin((2 * k - 1) * math.pi / 10) for k in range(1, 6)]
    vals = dict(c1=g[0] / (w * R), l2=g[1] * R / w, c3=g[2] / (w * R), l4=g[3] * R / w, c5=g[4] / (w * R))
    print("   " + ", ".join(f"{k.upper()} = {v*1e12:.3f} pF" if k.startswith("c") else f"{k.upper()} = {v*1e9:.3f} nH"
                            for k, v in vals.items()))
    data, _ = run_cli(LPF.format(**{k: f"{v:.6e}" for k, v in vals.items()}))
    f, s21 = data[:, 0], data[:, 1]
    worst = 0.0
    for ft in (600e6, 2 * 433.92e6, 3 * 433.92e6):
        sim = -np.interp(ft, f, s21)
        exact = 10 * math.log10(1 + (ft / fc) ** 10)
        worst = max(worst, abs(sim - exact))
        print(f"   {ft/1e6:7.2f} MHz: SPICE {sim:6.2f} dB, Butterworth formula {exact:6.2f} dB")
    check("B: SPICE matches the Butterworth response within 0.05 dB", worst < 0.05, f"(worst {worst:.3f} dB)")


# ------------------------------------------------------------------ C. Colpitts
COLPITTS = """* C: common-collector Colpitts oscillator (generic NPN, own model parameters - not a vendor model)
VCC vcc 0 PULSE(0 5 0 20n 20n 1 2)
R1 vcc b 10k
R2 b 0 10k
Q1 vcc b e QGEN
RE e 0 1k
C1 b e 100p
C2 e 0 330p
L1 b t 1u
CB t 0 1n
.model QGEN NPN (IS=1e-16 BF=100 VAF=50 CJE=1p CJC=0.5p TF=20p RB=10 RE=0.5 RC=2)
.options reltol=1e-4
.control
tran 1n 30u 0 1n
linearize v(e)
wrdata out.dat v(e)
quit
.endc
.end
"""


def example_c():
    print("=== C. Colpitts oscillator (transient) ===")
    data, _ = run_cli(COLPITTS)
    t, v = data[:, 0], data[:, 1]
    sel = t > 20e-6                      # bias settles through (R1||R2) CB = 5 us; analyse the last 10 us
    tt = t[sel]
    vv = v[sel] - np.polyval(np.polyfit(tt, v[sel], 1), tt)
    n = len(vv) * 8
    spec = np.abs(np.fft.rfft(vv * np.hanning(len(vv)), n))
    fr = np.fft.rfftfreq(n, tt[1] - tt[0])
    fosc = fr[np.argmax(spec)]
    L, C1, C2 = 1e-6, 100e-12, 330e-12
    f_lc = 1 / (2 * math.pi * math.sqrt(L * C1 * C2 / (C1 + C2)))
    h2 = spec[np.argmin(abs(fr - 2 * fosc))] / spec.max()
    print(f"   oscillation {fosc/1e6:.3f} MHz vs LC formula {f_lc/1e6:.3f} MHz ({100*(fosc-f_lc)/f_lc:+.2f} %); "
          f"amplitude {vv.max()-vv.min():.2f} Vpp at the emitter; 2nd harmonic {20*math.log10(h2):.1f} dBc")
    check("C: oscillates, and within 5 % of the tank formula", vv.max() - vv.min() > 0.1 and abs(fosc - f_lc) / f_lc < 0.05)


# ------------------------------------------------------------------ D. noise of a pad
PAD = """* D: 6.02 dB (voltage ratio 2) 50-ohm pi attenuator, noise analysis; source 50 ohm, load 50 ohm
.options temp={temp}
VS src 0 dc 0 ac 1
RS src in 50 {rs_temp}
RP1 in 0 150.476
RSER in out 37.35
RP2 out 0 150.476
RL out 0 50 {noisy}
.control
noise v(out) VS lin 3 100meg 300meg
setplot noise1
wrdata out.dat inoise_spectrum
quit
.endc
.end
"""


def example_d():
    print("=== D. noise analysis of a 6 dB pi pad ===")
    # exact 6.0206 dB pi pad (K = 2): Rshunt = 50 (K+1)/(K-1) = 150, Rseries = 50 (K^2-1)/(2K) = 37.5
    # (values above are E96-ish; recompute the exact loss for the comparison)
    rp, rs = 150.476, 37.35
    zin = lambda zl: 1 / (1 / rp + 1 / (rs + 1 / (1 / rp + 1 / zl)))
    # available-power loss for a 50 ohm source and 50 ohm load (transducer gain)
    vin = zin(50.0) / (50 + zin(50.0))
    vout = vin * (1 / (1 / rp + 1 / 50.0)) / (rs + 1 / (1 / rp + 1 / 50.0))
    loss_db = -10 * math.log10(4 * abs(vout) ** 2)
    # NF = inoise^2 / (4 k T0 Rs). The load resistor must be made noiseless (ngspice `noisy=0`), otherwise its
    # noise is counted as part of the DUT: F = F_pad + (F_load - 1)/G = 4 + 1/0.25 = 8 (9.03 dB).
    # Case list: (circuit temp C, label, load noise flag, source-resistor instance temperature)
    #  * SPICE's default temperature is 27 C (300.15 K), not T0 = 290 K; the source resistor is then ALSO at
    #    300.15 K, so inoise^2/(4 k T0 Rs) = L T/T0 (6.149 dB), not the IEEE NF 1 + (L-1)T/T0 (6.112 dB).
    #    Fix: give the source resistor its own temperature (ngspice instance parameter temp=16.85).
    cases = ((16.85, "290 K", "noisy=0", ""),
             (27.0, "27 C default, source also at 27 C", "noisy=0", ""),
             (27.0, "27 C, source resistor at 290 K", "noisy=0", "temp=16.85"),
             (16.85, "290 K, NOISY load", "", ""))
    for temp_c, label, noisy, rs_temp in cases:
        data, _ = run_cli(PAD.format(temp=temp_c, noisy=noisy, rs_temp=rs_temp))
        inoise = data[:, 1]            # V/sqrt(Hz), input-referred (at the source)
        tk = temp_c + 273.15
        t_src = 290.0 if (rs_temp or abs(temp_c - 16.85) < 1e-9) else tk
        L = 10 ** (loss_db / 10)
        nf = 10 * math.log10(inoise[0] ** 2 / (4 * 1.380649e-23 * 290.0 * 50.0))
        # expected inoise^2/(4 k T0 Rs) = [T_src + (L - 1) T_pad + (load noise referred to input)] / T0
        load = (tk * L) if not noisy else 0.0
        expect = 10 * math.log10((t_src + (L - 1) * tk + load) / 290.0)
        print(f"   {label}: SPICE 'NF' = {nf:.3f} dB (pad loss {loss_db:.3f} dB; expected {expect:.3f} dB)")
        check(f"D: NF at {label} matches theory within 0.02 dB", abs(nf - expect) < 0.02)


# ------------------------------------------------------------------ E. Touchstone -> SPICE via vector fitting
def example_e():
    """Vector-fit an S-parameter network (here the ideal Butterworth LPF of example B, as scikit-rf would load
    it from a .s2p file), export it as a SPICE subcircuit with scikit-rf, and run that in ngspice."""
    print("=== E. S-parameters -> SPICE subcircuit (scikit-rf VectorFitting) -> ngspice ===")
    import warnings
    warnings.filterwarnings("ignore")
    import skrf as rf
    from skrf.vectorFitting import VectorFitting
    fc = 600e6
    w = 2 * math.pi * fc
    g = [2 * math.sin((2 * k - 1) * math.pi / 10) for k in range(1, 6)]
    fr = rf.Frequency(1, 2000, 400, unit="MHz")
    m = rf.media.DefinedGammaZ0(frequency=fr, z0_port=50)
    lp = (m.shunt_capacitor(g[0] / (w * 50)) ** m.inductor(g[1] * 50 / w) ** m.shunt_capacitor(g[2] / (w * 50))
          ** m.inductor(g[3] * 50 / w) ** m.shunt_capacitor(g[4] / (w * 50)))
    vf = VectorFitting(lp)
    vf.auto_fit()
    d = tempfile.mkdtemp(prefix="rfkb_vf_")
    sub = os.path.join(d, "lpf_vf.sp")
    vf.write_spice_subcircuit_s(sub)
    net = f"""* E: vector-fitted LPF as a subcircuit
.include {sub}
V1 a 0 dc 0 ac 1 portnum 1 z0 50
V2 b 0 dc 0 ac 1 portnum 2 z0 50
X1 a b s_equivalent
.control
sp lin 5 433.92meg 1301.76meg
let s21db = db(s_2_1)
wrdata out.dat s21db
quit
.endc
.end
"""
    data, _ = run_cli(net)
    worst = 0.0
    for fq, sim in zip(data[:, 0], data[:, 1]):
        exact = -10 * math.log10(1 + (fq / fc) ** 10)
        worst = max(worst, abs(sim - exact))
    print(f"   {len(vf.poles)} poles, fit rms error {vf.get_rms_error():.1e}; ngspice S21 at 433.92/867.84/1301.76 MHz = "
          f"{data[0,1]:.3f}/{data[2,1]:.3f}/{data[4,1]:.3f} dB; worst deviation from Butterworth {worst:.4f} dB "
          f"(passivity check: {vf.is_passive()})")
    check("E: vector-fitted subcircuit reproduces the network in ngspice within 0.01 dB", worst < 0.01)


def kicad_route():
    print("=== KiCad-bundled libngspice route (tools/verify/analog_ngspice.py) ===")
    try:
        import analog_ngspice as an
    except Exception as e:                   # pragma: no cover
        print(f"   skipped: {e}")
        return
    q, xs, xp = matching.l_match_real(50.0, 12.5)
    L = xs / (2 * math.pi * 433e6)
    C = -1 / (2 * math.pi * 433e6 * xp)
    net = LMATCH.format(c1=f"{C:.6e}", l1=f"{L:.6e}", rl_esr="1e-6").split(".control")[0] + \
        ".sp lin 3 400meg 466meg\n.end\n"
    try:
        v = an.run_netlist(net, ["frequency", "S_1_1"])
    except Exception as e:
        print(f"   .sp via KiCad libngspice failed: {e}")
        return
    s = np.abs(v["S_1_1"])
    print(f"   KiCad ngspice-44.2: |S11| at 400/433/466 MHz = {s[0]:.4f} / {s[1]:.2e} / {s[2]:.4f}")
    check("KiCad libngspice gives the same L-match result", s[1] < 0.01)


if __name__ == "__main__":
    print(f"ngspice CLI: {NGSPICE}")
    example_a()
    example_b()
    example_c()
    example_d()
    example_e()
    kicad_route()
    print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
