#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/pa-control-protection-and-sequencing.md  (W5-E7)

 A. ALC loop on a compressing PA (Rapp model): loop gain falls with compression; time constant vs
    operating point; integrator wind-up when the set point exceeds Psat, and an anti-wind-up clamp
 B. TX power ramping (key clicks): spectrum of a keyed carrier with rectangular vs raised-cosine
    ramps of 10/40/200/800 us (SX126x RampTime options), power at 25/100/250 kHz offsets
 C. VSWR measurement with finite coupler directivity: reading bounds; foldback law
 D. Mismatch stress on a class-B current-source PA: dissipation and attempted voltage swing vs VSWR and phase
 E. T/R sequencing timeline check (relay operate/bounce, PIN switch, PA bias, RF ramp)
 F. Class D: ngspice transient of voltage-mode (VMCD) and current-mode (CMCD) class D at 7 MHz:
    P = 2 V^2/(pi^2 R) and eta = R/(R+Ron) (VMCD), C_oss loss C V^2 f; CMCD P = pi^2 V^2/(2R),
    eta = 1/(1 + pi^2 Ron/(2R)), zero-voltage switching with C_oss absorbed in the tank
 G. Thermal: one-pole junction model under LoRa duty cycle; peak vs average junction temperature
Run: python3 tools/verify/rf2_pa_control.py   (runtime ~20 s; needs ngspice)
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rf2_common import check, finish, ngspice

print("=== A. ALC on a compressing PA")
Psat_dBm = 33.0         # 2 W
Gss = 30.0              # small-signal gain dB
p_rapp = 2.0


def pa_out_dBm(pin_dBm):
    # Rapp AM/AM in power terms: Pout = G Pin / (1 + (G Pin / Psat)^p)^(1/p)
    G = 10 ** (Gss / 10); Pin = 1e-3 * 10 ** (pin_dBm / 10); Ps = 1e-3 * 10 ** (Psat_dBm / 10)
    Po = G * Pin / (1 + (G * Pin / Ps) ** p_rapp) ** (1 / p_rapp)
    return 10 * np.log10(Po / 1e-3)


def slope(pin):
    return (pa_out_dBm(pin + 0.01) - pa_out_dBm(pin - 0.01)) / 0.02


# drive VGA dB-linear: Pin = Pdrv0 + Kv*Vc ; detector Kd V/dB; integrator KI
Kv, Kd, KI = 20.0, 0.025, 2000.0
for target in (20.0, 30.0, 32.0):
    # find operating drive
    from scipy.optimize import brentq
    pin_op = brentq(lambda p: pa_out_dBm(p) - target, -40, 20)
    s = slope(pin_op)
    tau = 1 / (Kv * Kd * KI * s)
    print(f"  target {target:.0f} dBm: PA input {pin_op:5.1f} dBm, dPout/dPin = {s:.3f} dB/dB -> ALC tau = {tau*1e3:.2f} ms")
    if target == 20.0:
        tau_lin = tau
    if target == 32.0:
        tau_comp = tau
check("ALC slows as the PA compresses (1 dB below Psat: >2.5x slower than in the linear region)", tau_comp / tau_lin > 2.5)
# time-domain: wind-up when target > Psat, then target lowered
dt = 1e-6
def first_within(x, tgt, tol, dt):
    idx = np.where(np.abs(x - tgt) < tol)[0]
    return idx[0] * dt if len(idx) else np.inf


for clamp in (False, True):
    Vc = 0.0; n = int(0.25 / dt); out = np.empty(n); k2 = int(0.10 / dt)
    for k in range(n):
        tgt = 35.0 if k < k2 else 30.0               # 35 dBm is unreachable (Psat 33 dBm)
        pin = -30 + Kv * Vc
        out[k] = pa_out_dBm(pin)
        Vc += -KI * Kd * (out[k] - tgt) * dt
        Vc = min(Vc, 3.0)                            # op-amp rail: drive up to +30 dBm (VGA end stop)
        if clamp:
            Vc = min(Vc, (8.0 + 30) / Kv)            # anti-wind-up clamp at +8 dBm PA input (~2 dB compression)
        if k == k2 - 1:
            drive_wound = -30 + Kv * Vc
    settle = first_within(out[k2:], 30.0, 0.5, dt)
    print(f"  wind-up test ({'with' if clamp else 'no'} clamp): drive wound up to {drive_wound:.1f} dBm during 100 ms at an "
          f"unreachable 35 dBm set point; after it drops to 30 dBm, settles to 0.5 dB in {settle*1e3:.2f} ms")
    if clamp:
        t_clamp = settle
    else:
        t_noclamp = settle
check("anti-wind-up clamp: recovery > 2.5x faster and overdrive capped (no 22 dB overdrive into saturation)", t_noclamp > 2.5 * t_clamp)

print("\n=== B. TX ramp shaping and spectral splatter")
fs = 20e6
Tb = 4e-3                               # 4 ms burst
t = np.arange(int(12e-3 * fs)) / fs


def envelope(tr, shape):
    e = np.zeros_like(t)
    t0, t1 = 4e-3, 4e-3 + Tb
    on = (t >= t0) & (t <= t1)
    e[on] = 1.0
    if tr > 0:
        r1 = (t >= t0) & (t < t0 + tr); r2 = (t > t1 - tr) & (t <= t1)
        x1 = (t[r1] - t0) / tr; x2 = (t1 - t[r2]) / tr
        if shape == "rc":
            e[r1] = 0.5 - 0.5 * np.cos(np.pi * x1); e[r2] = 0.5 - 0.5 * np.cos(np.pi * x2)
        else:
            e[r1] = x1; e[r2] = x2
    return e


def offset_power(e, foffs, rbw=10e3):
    E = np.fft.fft(e) / len(e)
    f = np.fft.fftfreq(len(e), 1 / fs)
    P = np.abs(E) ** 2
    Ptot = P.sum()
    return [10 * np.log10(P[(np.abs(f - fo) < rbw / 2)].sum() / Ptot) for fo in foffs]


offs = [25e3, 100e3, 250e3]
res = {}
for label, tr, sh in [("rectangular", 0, "rc"), ("10 us linear", 10e-6, "lin"), ("10 us raised-cos", 10e-6, "rc"),
                      ("40 us raised-cos", 40e-6, "rc"), ("200 us raised-cos", 200e-6, "rc"),
                      ("800 us raised-cos", 800e-6, "rc")]:
    pw = offset_power(envelope(tr, sh), offs)
    res[label] = pw
    print(f"  {label:18s}: power in 10 kHz at +25/+100/+250 kHz = " + " / ".join(f"{p:6.1f}" for p in pw) + " dBc")
check("200 us raised-cosine ramp lowers the 100 kHz key-click level by > 30 dB vs rectangular",
      res["rectangular"][1] - res["200 us raised-cos"][1] > 30)
check("raised-cosine beats linear ramp of the same length at 250 kHz", res["10 us raised-cos"][2] < res["10 us linear"][2])

print("\n=== C. VSWR reading with finite coupler directivity")
for D in (15, 20, 30):
    eps = 10 ** (-D / 20)
    for G in (0.1, 0.333, 0.5, 1.0):
        lo, hi = max(G - eps, 0), G + eps
        vs = lambda g: (1 + g) / (1 - g) if g < 1 else np.inf
        print(f"  D={D} dB, true |G|={G:.3f} (VSWR {vs(G):5.2f}): reads |G| {lo:.3f}..{hi:.3f}"
              f" (VSWR {vs(lo):.2f}..{vs(min(hi,0.9999)):.2f})")
    if D == 20:
        eps20 = eps
check("20 dB directivity: true 3:1 (|G|=0.5) reads between 2.33:1 and 4:1",
      abs((1 + 0.5 - eps20) / (1 - 0.5 + eps20) - 2.333) < 0.01 and abs((1 + 0.5 + eps20) / (1 - 0.5 - eps20) - 4.0) < 0.01)
# foldback law: forward power limited so that reflected power <= Pr_max
Pset, Prmax = 2.0, 0.5
for G in (0.2, 0.5, 0.7, 1.0):
    Pf = min(Pset, Prmax / G ** 2)
    print(f"  foldback (2 W set, 0.5 W reflected limit): |G|={G:.1f} -> forward {Pf:.2f} W, reflected {Pf*G**2:.2f} W")
check("foldback: open circuit -> 0.5 W forward", abs(min(Pset, Prmax / 1.0) - 0.5) < 1e-12)

print("\n=== D. mismatch stress on a class-B current-source PA")
Vdd, Vk = 7.5, 0.5
Vm = Vdd - Vk
P0 = 2.0
Ropt = Vm ** 2 / (2 * P0)
I1 = Vm / Ropt                               # fundamental current amplitude at full drive
Ip = 2 * I1                                  # class-B half-sine peak
Pdc_full = Vdd * Ip / np.pi
print(f"  load line Ropt = {Ropt:.2f} ohm, P = {P0} W, Pdc = {Pdc_full:.2f} W, eta = {P0/Pdc_full*100:.1f} %, Pdiss = {Pdc_full-P0:.2f} W")
worst = {}
for S in (1.5, 2, 3, 10, 1e6):
    Gm = (S - 1) / (S + 1)
    ph = np.linspace(0, 2 * np.pi, 721)
    Gam = Gm * np.exp(1j * ph)
    Z = Ropt * (1 + Gam) / (1 - Gam)
    # fixed drive: current source I1 unless voltage would exceed Vm (then voltage-limited, current falls)
    I = np.minimum(I1, Vm / np.abs(Z))
    Pout = 0.5 * I ** 2 * Z.real
    Pdc = Vdd * (2 * I) / np.pi
    Pdiss = Pdc - Pout
    swing_attempt = I1 * np.abs(Z) / Vm           # what the drive would force without clipping
    worst[S] = (Pdiss.max(), Pout.min(), swing_attempt.max())
    print(f"  VSWR {S if S<1e5 else np.inf:>5}: worst Pdiss {Pdiss.max():.2f} W ({Pdiss.max()/(Pdc_full-P0):.1f}x matched), "
          f"min Pout {Pout.min():.2f} W, attempted swing up to {swing_attempt.max():.1f}x Vm")
check("short/open (VSWR inf): dissipation rises to ~Pdc (all DC power -> heat)", abs(worst[1e6][0] - Pdc_full) / Pdc_full < 0.01)
check("VSWR 3:1 raises worst-case dissipation by > 2x vs matched", worst[3][0] > 2 * (Pdc_full - P0))

print("\n=== E. T/R sequencing timeline")
steps = [("PTT asserted (MCU)", 0.0), ("LNA bias off / RX path to bypass", 0.1e-3),
         ("T/R relay coil energised", 0.2e-3), ("relay contacts closed (operate 8 ms max)", 0.2e-3 + 8e-3),
         ("contact bounce over (3 ms)", 0.2e-3 + 11e-3), ("PA bias (gate) enabled", 0.2e-3 + 12e-3),
         ("RF ramp starts (SX126x RampTime 200 us)", 0.2e-3 + 13e-3), ("RF at full power", 0.2e-3 + 13.2e-3)]
for name, tt in steps:
    print(f"  t = {tt*1e3:6.2f} ms : {name}")
rf_start = steps[6][1]; relay_done = steps[4][1]
check("RF starts only after relay settling (no hot switching) with >= 1 ms margin", rf_start - relay_done >= 1e-3)
# reverse order on release: RF ramp down -> PA bias off -> relay -> LNA on
print("  release: RF ramp-down (0.2 ms) -> PA bias off -> relay de-energise (release 5 ms max + bounce) -> LNA on")

print("\n=== F. class D (ngspice transient)")
f0 = 7.0e6; T0 = 1 / f0; Vdd = 12.0; R = 10.0; Ron = 0.2; QL = 5.0
L0 = QL * R / (2 * np.pi * f0); C0 = 1 / ((2 * np.pi * f0) ** 2 * L0)
ncyc = 60
tstep = T0 / 400
sw_model = f".model SWM SW(RON={Ron} ROFF=1e7 VT=0.5 VH=0.01)\n"
drv = (f"VG1 g1 0 PULSE(0 1 0 1p 1p {T0/2-2e-12} {T0})\n"
       f"VG2 g2 0 PULSE(1 0 0 1p 1p {T0/2-2e-12} {T0})\n")


def avg_last(t, x, ncycles=20):
    m = t >= t[-1] - ncycles * T0
    return np.trapezoid(x[m], t[m]) / (t[m][-1] - t[m][0])


def vmcd(Coss):
    net = (f"VDD vdd 0 DC {Vdd}\n{drv}"
           f"S1 vdd sw g1 0 SWM\nS2 sw 0 g2 0 SWM\n"
           + (f"CSW sw 0 {Coss}\n" if Coss > 0 else "")
           + f"L0 sw a {L0}\nC0 a b {C0}\nRL b 0 {R}\n" + sw_model)
    t, (vb, isup) = ngspice(net, f".tran {tstep} {ncyc*T0} 0 {tstep}", ["v(b)", "i(VDD)"])
    Pload = avg_last(t, vb ** 2 / R)
    Psup = avg_last(t, -Vdd * isup)
    return Pload, Psup


Pl, Ps = vmcd(0.0)
P_th = 2 * Vdd ** 2 / (np.pi ** 2 * (R + Ron) ** 2) * R
eta_th = R / (R + Ron)
print(f"  VMCD ideal-C: Pload {Pl:.3f} W (theory {P_th:.3f}), eta {Pl/Ps*100:.2f} % (theory {eta_th*100:.2f} %)")
check("VMCD power and efficiency match 2V^2/(pi^2 R) and R/(R+Ron) within 2 %", abs(Pl / P_th - 1) < 0.02 and abs(Pl / Ps - eta_th) < 0.02)
Coss = 200e-12
Pl2, Ps2 = vmcd(Coss)
loss_th = Coss * Vdd ** 2 * f0
print(f"  VMCD with 200 pF switch-node C: extra loss {(Ps2-Pl2)-(Ps-Pl):.3f} W (theory C V^2 f = {loss_th:.3f} W), eta {Pl2/Ps2*100:.1f} %")
check("hard-switched C_oss loss = C V^2 f within 10 %", abs(((Ps2 - Pl2) - (Ps - Pl)) / loss_th - 1) < 0.10)


def cmcd(Ccoss_total, QLc=10.0):
    Rd = 20.0                                  # differential load
    Lt = Rd / (QLc * 2 * np.pi * f0)
    Ct = 1 / ((2 * np.pi * f0) ** 2 * Lt) - Ccoss_total / 2   # Coss of each switch appears in series across tank
    net = (f"VDD vdd 0 DC {Vdd}\n{drv}"
           f"LCH1 vdd d1 20u\nLCH2 vdd d2 20u\n"
           f"S1 d1 0 g1 0 SWM\nS2 d2 0 g2 0 SWM\n"
           + (f"CS1 d1 0 {Ccoss_total}\nCS2 d2 0 {Ccoss_total}\n" if Ccoss_total > 0 else "")
           + f"LT d1 d2 {Lt}\nCT d1 d2 {Ct}\nRD d1 d2 {Rd}\n" + sw_model)
    t, (v1, v2, isup) = ngspice(net, f".tran {tstep} {400*T0} 0 {tstep}", ["v(d1)", "v(d2)", "i(VDD)"])
    vd = v1 - v2
    Pload = avg_last(t, vd ** 2 / Rd)
    Psup = avg_last(t, -Vdd * isup)
    vpk = np.max(np.abs(vd[t > t[-1] - 20 * T0]))
    # drain voltage at switch turn-on instants (ZVS check)
    m = t > t[-1] - 20 * T0
    ton = np.arange(np.ceil(t[m][0] / T0), np.floor(t[-1] / T0)) * T0
    v_on = np.interp(ton, t, v1)
    return Pload, Psup, vpk, np.max(np.abs(v_on)), Rd


Pl3, Ps3, vpk3, von3, Rd = cmcd(0.0)
P3_th = np.pi ** 2 * Vdd ** 2 / (2 * Rd)
eta3_th = 1 / (1 + np.pi ** 2 * Ron / (2 * Rd))
print(f"  CMCD: Pload {Pl3:.2f} W (ideal pi^2 V^2/(2R) = {P3_th:.2f}), eta {Pl3/Ps3*100:.2f} % (theory {eta3_th*100:.2f} %),"
      f" differential peak {vpk3:.1f} V (pi*Vdd = {np.pi*Vdd:.1f}), drain voltage at turn-on {von3:.2f} V")
print(f"  CMCD with Ron: P = (pi^2 V^2/2R) * eta^2 = {P3_th*eta3_th**2:.2f} W")
check("CMCD power = pi^2 V^2/(2R) * eta^2 within 2 % and efficiency within 0.5 point of 1/(1+pi^2 Ron/2R)",
      abs(Pl3 / (P3_th * eta3_th ** 2) - 1) < 0.02 and abs(Pl3 / Ps3 - eta3_th) < 0.005)
Pl4, Ps4, vpk4, von4, _ = cmcd(200e-12)
print(f"  CMCD with 200 pF per switch absorbed into the tank: eta {Pl4/Ps4*100:.2f} %, drain voltage at turn-on {von4:.2f} V (ZVS)")
check("CMCD absorbs C_oss: efficiency drop < 1 point (vs VMCD's C V^2 f loss)", (Pl3 / Ps3 - Pl4 / Ps4) < 0.01)
# UHF scaling of the VMCD C_oss loss
for f, C in ((433e6, 20e-12), (915e6, 5e-12)):
    print(f"  VMCD at {f/1e6:.0f} MHz, 7.5 V, C_oss {C*1e12:.0f} pF: C V^2 f = {C*7.5**2*f:.2f} W lost per switch node")

print("\n=== G. thermal: duty-cycled LoRa transmitter")
Pd, th_ja, tau_th = 3.0, 25.0, 5.0         # W dissipated while transmitting, C/W, thermal time constant s
Ta = 40.0
for t_on, period in ((1.5, 15.0), (1.5, 3.0), (0.06, 1.0)):
    dtt = 1e-3; n = int(20 * period / dtt); Tj = Ta; Tmax = Ta; Tavg = []
    for k in range(n):
        on = (k * dtt) % period < t_on
        Tj += ((Ta + (Pd * th_ja if on else 0) - Tj) / tau_th) * dtt
        if k * dtt > 15 * period:
            Tmax = max(Tmax, Tj); Tavg.append(Tj)
    Tav = Ta + Pd * th_ja * t_on / period
    print(f"  on {t_on} s every {period} s (duty {t_on/period*100:.0f} %): steady-state peak Tj {Tmax:.1f} C,"
          f" duty-average estimate {Tav:.1f} C, continuous {Ta+Pd*th_ja:.0f} C")
    if period == 3.0:
        peak_mid, av_mid = Tmax, Tav
check("with t_on comparable to tau_th, peak Tj exceeds the duty-average estimate by > 5 C", peak_mid - av_mid > 5)

finish()
