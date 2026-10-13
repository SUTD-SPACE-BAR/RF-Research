#!/usr/bin/env python3
"""W5-S3 verification for kb/05-analog-electronics/diodes-schottky-pin-varactor.md, section
"Rectennas — far-field RF energy harvesting" (G-09-02).

 1. ngspice, 915 MHz: RF-to-DC efficiency vs available power of a single series-diode rectenna (HSMS-2850
    datasheet SPICE model incl. Cj 0.18 pF, RS 25 ohm, BV 3.8 V). The antenna + matching network is modelled as a
    Norton source with resistance Rg and a parallel tank (Q 10) that resonates the diode capacitance and shorts the
    harmonics — an ideal step-up match; Rg and RL optimised at every power. Repeated with a matching inductor of
    unloaded Q 50 (realistic loss), and with an HSMS-282x-class diode (BV 15 V) at high power.
 2. Resistive source with no harmonic termination (quasi-static exact solution, memoryless diode): the ~40 %
    (4/pi^2) ceiling of a half-wave rectifier; ngspice spot check.
 3. Friis budgets for dedicated and ambient sources, and the exposure cap  P_max = S_lim * A_e  (ICNIRP 2020
    general-public reference level f/200 W/m^2 for 400-2000 MHz, 2 W/m^2 below 400 MHz — 19/rf-exposure-safety).
Run: python3 tools/verify/s3_rectenna.py   (about 30 s)
"""
import numpy as np
from scipy.optimize import brentq
from s3_spice import run

k, q = 1.380649e-23, 1.602176634e-19
T = 298.15
VT = k * T / q

def diode_i(v, IS, N, BV=3.8, IBV=3e-4):
    i = IS * (np.exp(np.clip(v / (N * VT), -50, 60)) - 1)
    # reverse breakdown (SPICE-like exponential knee)
    i = i - IBV * np.exp(np.clip((-BV - v) / (N * VT), -60, 60))
    return i

def solve_i(vs_inst, Rtot, Vo, IS, N):
    """Solve vs - i*Rtot - Vo = vd(i) for i (Rtot = Rg + RS)."""
    f = lambda i: vs_inst - i * Rtot - Vo - vd_of_i(i, IS, N)
    return f

def vd_of_i(i, IS, N, BV=3.8, IBV=3e-4):
    # invert the forward law; for reverse currents beyond -IS use the breakdown branch
    if i > -IS * 0.999999:
        return N * VT * np.log1p(i / IS)
    # breakdown: i = -IS - IBV*exp((-BV-v)/NVT)  ->  v = -BV - NVT*ln((-i-IS)/IBV)
    return -BV - N * VT * np.log(max((-i - IS * 0.999999) / IBV, 1e-300))

def vd_vec(i, IS, N, BV=3.8, IBV=3e-4):
    fwd = i > -IS * 0.999999
    v = np.empty_like(i)
    v[fwd] = N * VT * np.log1p(i[fwd] / IS)
    r = ~fwd
    v[r] = -BV - N * VT * np.log(np.maximum((-i[r] - IS * 0.999999) / IBV, 1e-300))
    return v

def avg_current(Vp, Rg, RS, Vo, IS, N, n=512):
    """Average diode current over one cycle; per-sample implicit equation solved by vectorised bisection."""
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    Rt = Rg + RS
    vsi = Vp * np.cos(th)
    lo = np.full(n, -1.0); hi = (np.abs(vsi) + 5) / Rt + 1e-9
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        g = vsi - mid * Rt - Vo - vd_vec(mid, IS, N)
        pos = g > 0          # g decreasing in i: root is above mid
        lo = np.where(pos, mid, lo); hi = np.where(pos, hi, mid)
    return float(np.mean(0.5 * (lo + hi)))

def efficiency(Pav, Rg, RL, IS=3e-6, N=1.06, RS=25.0):
    Vp = np.sqrt(8 * Rg * Pav)   # open-circuit source amplitude for available power Pav
    h = lambda Vo: avg_current(Vp, Rg, RS, Vo, IS, N) - Vo / RL
    Vo = brentq(h, 0.0, Vp + 1e-9, xtol=1e-9)
    return Vo ** 2 / RL / Pav, Vo

HS2850 = "IS=3e-6 N=1.06 RS=25 CJO=0.18p VJ=0.35 M=0.5 EG=0.69 XTI=2 BV=3.8 IBV=3e-4"
HS2820 = "IS=2.2e-8 N=1.08 RS=6 CJO=0.7p VJ=0.65 M=0.5 EG=0.69 XTI=2 BV=15 IBV=1e-4"

def tank(PdBm, Rg, RL, model, cj, f=915e6, Q=10, QL=None):
    Pav = 1e-3 * 10 ** (PdBm / 10); Ip = np.sqrt(8 * Pav / Rg)
    w = 2 * np.pi * f; Cn = Q / (w * Rg); Ct = max(Cn - cj, 0.0); L = 1 / (w * w * (Ct + cj))
    loss = f"RLq a 0 {QL*w*L:g}\n" if QL else ""
    net = f"""Is 0 a SIN(0 {Ip:.6g} {f:g})
Rg a 0 {Rg:g}
Lt a 0 {L:g}
Ct a 0 {max(Ct, 1e-18):g}
{loss}D1 a out HS
Co out 0 10p
RL out 0 {RL:g}
.model HS D({model})
.options temp=25
"""
    T = 1 / f
    x, d = run(net, f"tran {T/50:g} {1500*T:g} {1200*T:g} {T/50:g}", ["v(out)"])
    v = d["v(out)"].mean()
    return v * v / RL / Pav, v

def best(PdBm, model, cj, Rgs, RLs, QL=None):
    return max(tank(PdBm, Rg, RL, model, cj, QL=QL) + (Rg, RL) for Rg in Rgs for RL in RLs)

print("=== 1. ngspice 915 MHz rectenna efficiency vs available power (single series diode, tank match Q 10) ===")
res = {}
for PdBm in (-40, -30, -20, -10, 0, 10):
    e1 = best(PdBm, HS2850, 0.18e-12, (300, 1e3, 3e3, 1e4), (1e3, 3e3, 1e4, 3e4))
    e2 = best(PdBm, HS2850, 0.18e-12, (300, 1e3, 3e3, 1e4), (1e3, 3e3, 1e4, 3e4), QL=50)
    res[PdBm] = e2[0]
    print(f"  {PdBm:+4d} dBm  HSMS-2850 ideal match: {e1[0]*100:5.1f} % (Vdc {e1[1]*1e3:7.1f} mV, Rg {e1[2]:g}, RL {e1[3]:g});"
          f"  with Q_L = 50 inductor: {e2[0]*100:5.1f} %")
for PdBm in (0, 10, 20):
    e3 = best(PdBm, HS2820, 0.7e-12, (30, 100, 300, 1e3), (300, 1e3, 3e3, 1e4), QL=50)
    print(f"  {PdBm:+4d} dBm  HSMS-282x class (BV 15 V), Q_L = 50: {e3[0]*100:5.1f} % (Vdc {e3[1]:.2f} V, Rg {e3[2]:g}, RL {e3[3]:g})")
    res[("2820", PdBm)] = e3[0]
assert res[-40] < 0.05 and res[-30] < 0.2 and res[0] > 0.5 and res[10] < res[0]
assert res[("2820", 20)] > 0.6

print("\n=== 2. Resistive source, no harmonic termination (quasi-static), HSMS-2850 without Cj ===")
for PdBm in (-10, 0):
    Pav = 1e-3 * 10 ** (PdBm / 10)
    bb = max(efficiency(Pav, Rg, RL) + (Rg, RL) for Rg in (300, 1e3, 3e3, 1e4) for RL in (1e3, 3e3, 1e4, 3e4))
    print(f"  {PdBm:+d} dBm: best {bb[0]*100:.1f} % (Rg {bb[2]:g}, RL {bb[3]:g}) — half-wave ceiling 4/pi^2 = {400/np.pi**2:.1f} %")
    assert bb[0] < 4 / np.pi ** 2
    if PdBm == 0:
        e, Vo, Rg, RL = bb
        Vp = np.sqrt(8 * Rg * Pav)
        net = f"""Vs s 0 SIN(0 {Vp:.6g} 1MEG)
Rg s a {Rg:g}
D1 a out HS
Co out 0 1u IC={Vo:.6g}
RL out 0 {RL:g}
.model HS D(IS=3e-6 N=1.06 RS=25 CJO=0 TT=0 BV=3.8 IBV=3e-4)
.options temp=25
"""
        x, d = run(net, "tran 2n 400u 300u 2n uic", ["v(out)"])
        vdc = d["v(out)"].mean(); es = vdc ** 2 / RL / Pav
        print(f"  ngspice spot check at 0 dBm: eta {es*100:.2f} % vs quasi-static {e*100:.2f} %")
        assert abs(es / e - 1) < 0.05

print("\n=== 3. Power budgets (Friis, 2 dBi harvesting antenna) and the exposure cap ===")
c = 299792458.0
def friis(eirp_W, f, d, Gr_dBi=2.0):
    lam = c / f
    return eirp_W * 10 ** (Gr_dBi / 10) * (lam / (4 * np.pi * d)) ** 2
def eta_at(PdBm):
    ps = sorted(p for p in res if not isinstance(p, tuple))
    return np.interp(PdBm, ps, [res[p] for p in ps])
cases = [("SG 920-925 MHz LPWAN, 100 mW e.r.p. (164 mW EIRP), 3 m", 0.1 * 10 ** 0.215, 922e6, 3),
         ("SG 920-925 MHz LPWAN, 100 mW e.r.p., 10 m", 0.1 * 10 ** 0.215, 922e6, 10),
         ("FCC 15.247 915 MHz, 4 W EIRP, 3 m", 4.0, 915e6, 3),
         ("E22 33 dBm into a 2.15 dBi dipole (3.3 W EIRP) at 433 MHz, 10 m", 2.0 * 10 ** 0.215, 433e6, 10),
         ("same, 100 m", 2.0 * 10 ** 0.215, 433e6, 100)]
for lab, eirp, f, d in cases:
    p = friis(eirp, f, d); pd = 10 * np.log10(p / 1e-3)
    print(f"  {lab:62s}: Pr = {pd:6.1f} dBm = {p*1e6:9.2f} uW -> DC ~ {p*eta_at(pd)*1e6:8.3f} uW (eta {eta_at(pd)*100:.0f} %, upper bound)")
for pd in (-40, -50, -60):
    print(f"  ambient {pd} dBm: {10**(pd/10)*1e-3*1e9:7.2f} nW in, DC <= {10**(pd/10)*1e-3*eta_at(max(pd,-40))*1e9:.3f} nW (eta at -40 dBm used as an optimistic cap)")
for f in (433e6, 915e6, 2.45e9):
    fM = f / 1e6
    S = 2.0 if fM < 400 else (fM / 200 if fM <= 2000 else 10.0)
    lam = c / f
    Ae = 10 ** 0.2 * lam ** 2 / (4 * np.pi)
    print(f"  {fM:6.0f} MHz: ICNIRP public S = {S:5.2f} W/m^2, A_e(2 dBi) = {Ae*1e4:6.1f} cm^2 -> P_max = {S*Ae*1e3:6.1f} mW "
          f"where a person may stand; 5 W phone charge needs S = {5/Ae:7.0f} W/m^2 = {5/Ae/S:5.0f} x the limit "
          f"(EIRP {5/Ae*4*np.pi*5**2/1e3:6.0f} kW at 5 m)")
print("\nALL S3 RECTENNA CHECKS PASS")
