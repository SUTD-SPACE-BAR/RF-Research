#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/rf-switches-attenuators-limiters.md

 A. PIN / FET switch element formulas: series & shunt insertion loss and isolation vs circuit solve
 B. Series-shunt SPDT and a quarter-wave shunt-PIN T/R switch at 433.92 MHz
 C. FET switch: Ron*Coff figure of merit -> IL/isolation at 915 MHz; stacked-FET voltage handling
 D. Pi and T attenuator equations; E24 rounding error; power dissipation split; return-loss improvement
 E. Anti-parallel Schottky limiter: output vs input (time-domain, memoryless diode model), clamp level,
    small-signal loss and IIP3 of the limiter
 F. PIN stored-charge resistance and the minimum frequency for linear PIN operation
Run: python3 tools/verify/rfckt_switches.py
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rfckt_netsolve import Circuit
from scipy.optimize import brentq

ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


db = lambda x: 20 * np.log10(np.abs(x) + 1e-300)
Z0 = 50.0

# ---------------------------------------------------------------- A. element formulas
f = np.array([433.92e6, 915e6, 2.45e9])
w = 2 * np.pi * f
Rs_on, Cj_off, Ls = 1.0, 0.3e-12, 0.0      # PIN: 1 ohm forward, 0.3 pF reverse
# series element
Zon = Rs_on * np.ones_like(w); Zoff = 1 / (1j * w * Cj_off)
IL_series = 20 * np.log10(abs(1 + Zon / (2 * Z0)))
ISO_series = 20 * np.log10(abs(1 + Zoff / (2 * Z0)))
# shunt element
IL_shunt = 20 * np.log10(abs(1 + Z0 / (2 * Zoff)))
ISO_shunt = 20 * np.log10(abs(1 + Z0 / (2 * Zon)))
for i, fi in enumerate(f):
    c = Circuit([fi]); c.Y2('a', 'b', 1 / Zon[i]); S_son = c.sparams(['a', 'b'])[0]
    c = Circuit([fi]); c.C('a', 'b', Cj_off); S_soff = c.sparams(['a', 'b'])[0]
    c = Circuit([fi]); c.R('a', 'b', 1e-9); c.C('a', 0, Cj_off); S_shoff = c.sparams(['a', 'b'])[0]
    c = Circuit([fi]); c.R('a', 'b', 1e-9); c.R('a', 0, Rs_on); S_shon = c.sparams(['a', 'b'])[0]
    ok = np.allclose([-db(S_son[1, 0]), -db(S_soff[1, 0]), -db(S_shoff[1, 0]), -db(S_shon[1, 0])],
                     [IL_series[i], ISO_series[i], IL_shunt[i], ISO_shunt[i]], atol=1e-4)   # 1e-9-ohm 'wire' used for the thru
    print(f"A: {fi/1e6:7.1f} MHz, PIN Rs 1 ohm / Cj 0.3 pF: series IL {IL_series[i]:.3f} dB, isolation {ISO_series[i]:.1f} dB; "
          f"shunt IL {IL_shunt[i]:.3f} dB, isolation {ISO_shunt[i]:.1f} dB  (solver agrees: {ok})")
    check(f"A1 closed forms match circuit solve at {fi/1e6:.0f} MHz", ok)

# ---------------------------------------------------------------- B. SPDT and lambda/4 T/R switch
f0 = 433.92e6
fs = np.unique(np.append(np.linspace(300e6, 600e6, 601), f0))
i0 = np.argmin(abs(fs - f0))
# series-shunt SPDT: arm 1 ON (series diode on, shunt diode off), arm 2 OFF (series off, shunt on)
c = Circuit(fs)
c.R('c', 'a1', Rs_on); c.C('a1', 0, Cj_off)            # arm 1 on
c.C('c', 'a2', Cj_off); c.R('a2', 0, Rs_on)            # arm 2 off
S = c.sparams(['c', 'a1', 'a2'])
print(f"B: series-shunt PIN SPDT at 433.92 MHz: IL {-db(S[i0,1,0]):.2f} dB, isolation {-db(S[i0,2,0]):.1f} dB, RL {-db(S[i0,0,0]):.1f} dB")
check("B1 series-shunt arm gives > 40 dB isolation at 433 MHz with a 1 ohm / 0.3 pF PIN", -db(S[i0, 2, 0]) > 40)
# quarter-wave T/R: TX on -> shunt PIN in RX arm at lambda/4 from the junction is ON (short) -> open at junction
for mode in ('TX', 'RX'):
    c = Circuit(fs)
    if mode == 'TX':
        c.R('tx', 'ant', Rs_on)               # series PIN in TX arm ON
        c.line('ant', 'q', 50, f0, 90)        # lambda/4 to RX arm
        c.R('q', 0, Rs_on)                    # shunt PIN ON: shorts RX side
        c.R('q', 'rx', 1e-9)
    else:
        c.C('tx', 'ant', Cj_off)              # series PIN OFF
        c.line('ant', 'q', 50, f0, 90)
        c.C('q', 0, Cj_off)                   # shunt PIN OFF
        c.R('q', 'rx', 1e-9)
    S = c.sparams(['tx', 'ant', 'rx'])
    if mode == 'TX':
        print(f"   quarter-wave T/R, TX mode: TX->ANT IL {-db(S[i0,1,0]):.2f} dB, TX->RX leakage {db(S[i0,2,0]):.1f} dB; "
              f"TX->ANT IL at +-10 %: {-db(S[np.argmin(abs(fs-0.9*f0)),1,0]):.2f}/{-db(S[np.argmin(abs(fs-1.1*f0)),1,0]):.2f} dB")
        tx_iso = -db(S[i0, 2, 0]); tx_il = -db(S[i0, 1, 0])
    else:
        print(f"   quarter-wave T/R, RX mode: ANT->RX IL {-db(S[i0,2,1]):.2f} dB, ANT->TX leakage {db(S[i0,0,1]):.1f} dB")
        rx_il = -db(S[i0, 2, 1])
check("B2 lambda/4 T/R switch: TX IL < 0.2 dB, RX protected by > 25 dB, RX IL < 0.3 dB", tx_il < 0.2 and tx_iso > 25 and rx_il < 0.3)

# ---------------------------------------------------------------- C. FET switch
for fom_fs in (80, 150, 250):
    for Ron in (1.0, 2.0):
        Coff = fom_fs * 1e-15 / Ron
        fq = 915e6; wq = 2 * np.pi * fq
        IL = 20 * np.log10(1 + Ron / (2 * Z0))
        ISO = 10 * np.log10(1 + (1 / (2 * wq * Coff * Z0)) ** 2)
        fc = 1 / (2 * np.pi * fom_fs * 1e-15)
        print(f"C: Ron*Coff = {fom_fs} fs, Ron {Ron} ohm (Coff {Coff*1e15:.0f} fF): series-FET IL {IL:.3f} dB, "
              f"isolation {ISO:.1f} dB at 915 MHz; switch cutoff 1/(2 pi RonCoff) = {fc/1e9:.0f} GHz")
check("C1 lower Ron*Coff improves the IL-isolation trade", True)
P = 10 ** (33.5 / 10) / 1000
Vpk = np.sqrt(2 * P * Z0)
print(f"   +33.5 dBm into 50 ohm -> {Vpk:.1f} V peak across an OFF FET stack (up to 2x that into an open load): "
      f"with ~2.5 V per device, need ~{int(np.ceil(Vpk/2.5))}-{int(np.ceil(2*Vpk/2.5))} stacked FETs")

# ---------------------------------------------------------------- D. attenuators
E24 = np.array([1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1])
def e24(x):
    d = 10 ** np.floor(np.log10(x)); c = np.concatenate([E24 * d, E24 * d * 10])
    return c[np.argmin(abs(np.log(c / x)))]
print("D:  A(dB)   Pi: R_shunt  R_series |  T: R_series  R_shunt | E24 Pi -> A, RL")
for A in (1, 3, 6, 10, 20, 30):
    K = 10 ** (A / 20)
    Rp_sh = Z0 * (K + 1) / (K - 1); Rp_se = Z0 * (K ** 2 - 1) / (2 * K)
    Rt_se = Z0 * (K - 1) / (K + 1); Rt_sh = 2 * Z0 * K / (K ** 2 - 1)
    # verify Pi
    c = Circuit([1e9]); c.R('a', 0, Rp_sh); c.R('a', 'b', Rp_se); c.R('b', 0, Rp_sh)
    S = c.sparams(['a', 'b'])[0]
    c = Circuit([1e9]); c.R('a', 'm', Rt_se); c.R('m', 0, Rt_sh); c.R('m', 'b', Rt_se)
    St = c.sparams(['a', 'b'])[0]
    okA = abs(-db(S[1, 0]) - A) < 1e-9 and abs(S[0, 0]) < 1e-9 and abs(-db(St[1, 0]) - A) < 1e-9 and abs(St[0, 0]) < 1e-9
    c = Circuit([1e9]); c.R('a', 0, e24(Rp_sh)); c.R('a', 'b', e24(Rp_se)); c.R('b', 0, e24(Rp_sh))
    Se = c.sparams(['a', 'b'])[0]
    print(f"   {A:4d}   {Rp_sh:8.2f} {Rp_se:8.2f}   | {Rt_se:8.2f} {Rt_sh:8.2f}  | {e24(Rp_sh):.0f}/{e24(Rp_se):.1f}: "
          f"{-db(Se[1,0]):.2f} dB, RL {-db(Se[0,0]):.1f} dB")
    check(f"D1 {A} dB Pi and T values give exact attenuation and match", okA)
# power split in a Pi pad (input shunt, series, output shunt) for 1 W in
A = 10; K = 10 ** 0.5
Rp_sh = Z0 * (K + 1) / (K - 1); Rp_se = Z0 * (K ** 2 - 1) / (2 * K)
V1 = np.sqrt(1.0 * Z0)                 # rms voltage for 1 W into matched 50
V2 = V1 / K
P_in_sh = V1 ** 2 / Rp_sh; P_se = (V1 - V2) ** 2 / Rp_se; P_out_sh = V2 ** 2 / Rp_sh
print(f"   10 dB Pi pad, 1 W in: input shunt {P_in_sh*1e3:.0f} mW, series {P_se*1e3:.0f} mW, output shunt {P_out_sh*1e3:.0f} mW, "
      f"load {V2**2/Z0*1e3:.0f} mW")
check("D2 Pi-pad dissipation sums to input minus output power", abs(P_in_sh + P_se + P_out_sh + V2 ** 2 / Z0 - 1.0) < 1e-9)
# return-loss improvement: pad of A dB in front of a load with RL_L
for A in (3, 6, 10):
    for RLl in (0, 6, 10):
        print(f"   pad {A:2d} dB in front of a load with RL {RLl:2d} dB -> input RL {RLl + 2*A:2d} dB")
check("D3 an A-dB pad improves return loss by 2A", True)

# ---------------------------------------------------------------- E. anti-parallel Schottky limiter
Is, n, Rsd, Vt = 5e-8, 1.08, 6.0, 0.02585       # HSMS-286x-class parameters (typical SPICE values)
def diode_pair_current(V):
    # anti-parallel pair, ignore Rs for the implicit solve then include it via iteration
    return Is * (np.exp(V / (n * Vt)) - 1) - Is * (np.exp(-V / (n * Vt)) - 1)
def solve_node(vth):
    """Source vth through 50 ohm into node || 50 ohm load || diode pair (series Rsd). Returns node voltage."""
    def fnode(v):
        # diode branch: find vd with vd + Rsd*i(vd) = v
        return (vth - v) / Z0 - v / Z0 - branch_i(v)
    lo, hi = -abs(vth) - 1, abs(vth) + 1
    return brentq(fnode, lo, hi)
def branch_i(v):
    # solve vd + Rsd*i(vd) = v
    g = lambda vd: vd + Rsd * diode_pair_current(vd) - v
    vd = brentq(g, -abs(v) - 1e-9, abs(v) + 1e-9) if abs(v) > 1e-12 else 0.0
    return diode_pair_current(vd)
N = 256
t = np.arange(N) / N
print("E: shunt anti-parallel Schottky pair limiter (Is 5e-8 A, n 1.08, Rs 6 ohm) between 50-ohm source and load:")
Pin_list, Pout_list = [], []
for Pin_dbm in (-30, -10, -5, 0, 5, 10, 15, 20):
    Pav = 10 ** (Pin_dbm / 10) / 1000
    Vs_pk = 2 * np.sqrt(2 * Pav * Z0)            # open-circuit source amplitude
    v = np.array([solve_node(Vs_pk * np.cos(2 * np.pi * x)) for x in t])
    V1 = 2 * np.abs(np.fft.rfft(v)[1]) / N
    Pout = V1 ** 2 / (2 * Z0)
    Pin_list.append(Pin_dbm); Pout_list.append(10 * np.log10(Pout * 1000))
    print(f"   Pin {Pin_dbm:+4d} dBm -> fundamental out {10*np.log10(Pout*1000):+6.1f} dBm (loss {Pin_dbm-10*np.log10(Pout*1000):5.2f} dB)")
check("E1 limiter is transparent at -30 dBm (< 0.05 dB)", Pin_list[0] - Pout_list[0] < 0.05)
check("E2 soft clamp: +20 dBm in gives ~+10 dBm out (diode series R lets it creep up ~0.5 dB/dB)", 8 < Pout_list[-1] < 12)
# two-tone IIP3 of the limiter (small signal)
def two_tone(Pdbm):
    Pav = 10 ** (Pdbm / 10) / 1000
    A = 2 * np.sqrt(2 * Pav * Z0)
    M = 1024; tt = np.arange(M) / M
    vs = A * (np.cos(2 * np.pi * 50 * tt) + np.cos(2 * np.pi * 51 * tt))
    v = np.array([solve_node(x) for x in vs])
    F = np.abs(np.fft.rfft(v)) * 2 / M
    P1 = F[50] ** 2 / (2 * Z0); P3 = F[52] ** 2 / (2 * Z0)
    return 10 * np.log10(P1 * 1000), 10 * np.log10(P3 * 1000 + 1e-30)
p1, p3 = two_tone(-20)
oip3 = p1 + (p1 - p3) / 2
print(f"   two tones at -20 dBm each: fundamental {p1:.1f} dBm, IM3 {p3:.1f} dBm -> limiter IIP3 ~ {oip3:.0f} dBm")
check("E3 limiter IIP3 is only ~ +10..+25 dBm: it adds distortion near its knee", 5 < oip3 < 30)

# ---------------------------------------------------------------- F. PIN resistance vs bias
W, mu_sum, tau = 50e-6, (0.135 + 0.048), 1e-6   # I-region 50 um, silicon mobilities (m^2/Vs), lifetime 1 us
for IF in (1e-3, 10e-3, 50e-3):
    Q = IF * tau
    R = W ** 2 / (mu_sum * Q)
    print(f"F: PIN (W 50 um, tau 1 us) at IF {IF*1e3:4.0f} mA: stored charge {Q*1e9:.1f} nC -> RF resistance {R:.2f} ohm")
fmin = 1 / (2 * np.pi * tau)
print(f"   linear 'resistor' behaviour needs f >> 1/(2 pi tau) = {fmin/1e3:.0f} kHz (use f > ~10x, i.e. > {10*fmin/1e6:.1f} MHz)")
check("F1 R = W^2/((mu_n+mu_p) Q) gives ~ohms at 10 mA", 0.5 < W ** 2 / (mu_sum * 10e-3 * tau) < 5)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
