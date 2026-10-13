#!/usr/bin/env python3
"""
s16_snubber_transients.py — transient-suppression numbers for kb/13-pcb-rf-layout-emc/emc-emi-fundamentals.md
("EMC standards and transients for avionics").

  1. RC snubber from the ring-halving method: measured ring f0, added C halves it -> C_par, L_par, R = sqrt(L/C),
     C_s = 3-4 C_par, dissipation C_s V^2 f_sw.  ODE check of the turn-off ring with and without the snubber.
  2. Pyro-channel turn-off: firing current through battery-side and lead-side wiring inductance; unclamped spike
     I*sqrt(L/Coss), avalanche energy, freewheel diode across the output + local bulk capacitor.
  3. Inductive load (solenoid/relay/brushed motor) decay: diode only vs diode + Zener / TVS clamp; times and switch stress.
  4. Hot-plugging a 2S/3S LiPo through an arming switch into ceramic input capacitors: undamped overshoot ~2x,
     damping with a bulk electrolytic/polymer (R_d ~ sqrt(L/C)); ODE check.
  5. Surge (IEC 61000-4-5 1.2/50-8/20, 2 ohm) and EFT (IEC 61000-4-4 5/50 ns, 50 ohm) energy delivered to a clamp.

Run: python3 tools/verify/s16_snubber_transients.py     (a few seconds)
"""
import numpy as np
from scipy.integrate import solve_ivp

ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


print("=" * 96)
print("1. RC snubber by ring halving (FET switching an inductive harness load, Vdd 8.4 V, 2 A, 20 kHz PWM)")
print("=" * 96)
f0, Cadd = 80e6, 470e-12
f1 = 40e6
Cpar = Cadd / ((f0 / f1) ** 2 - 1)
Lpar = 1 / ((2 * np.pi * f0) ** 2 * Cpar)
Rs = np.sqrt(Lpar / Cpar)
Cs = 4 * Cpar
Vdd, I0, fsw = 8.4, 2.0, 20e3
Psn = Cs * Vdd**2 * fsw
print(f"  ring {f0/1e6:.0f} MHz; +{Cadd*1e12:.0f} pF -> {f1/1e6:.0f} MHz  =>  C_par = {Cpar*1e12:.0f} pF, L_par = {Lpar*1e9:.1f} nH,"
      f" Z = sqrt(L/C) = {Rs:.1f} ohm")
print(f"  snubber: R = {Rs:.1f} ohm (use 12 ohm), C_s = 4 C_par = {Cs*1e12:.0f} pF (use 680 pF); "
      f"loss C V^2 f = {Psn*1e3:.2f} mW at {fsw/1e3:.0f} kHz")


def turnoff(L, Cp, I0, V, R=None, C=None, tmax=200e-9):
    # state: iL, vD (drain), vCs (snubber cap). FET off at t=0; iL flows into Cp and snubber.
    def f(t, y):
        iL, vD, vC = y
        isn = 0.0 if R is None else (vD - vC) / R
        return [(V - vD) / L, (iL - isn) / Cp, 0.0 if R is None else isn / C]
    sol = solve_ivp(f, (0, tmax), [I0, 0.0, 0.0], max_step=tmax / 4000, rtol=1e-8)
    return sol.t, sol.y[1]


t, vd0 = turnoff(Lpar, Cpar, I0, Vdd)
t2, vd1 = turnoff(Lpar, Cpar, I0, Vdd, R=12.0, C=680e-12)
pk0, pk1 = vd0.max(), vd1.max()
pk_formula = Vdd + np.hypot(Vdd, I0 * np.sqrt(Lpar / Cpar))
# ringing amplitude remaining after 100 ns
late0 = np.ptp(vd0[t > 100e-9]); late1 = np.ptp(vd1[t2 > 100e-9])
print(f"  turn-off peak without snubber {pk0:.1f} V (formula Vdd + sqrt(Vdd^2 + (I sqrt(L/C))^2) = {pk_formula:.1f} V), "
      f"with snubber {pk1:.1f} V")
print(f"  ringing p-p after 100 ns: {late0:.1f} V without, {late1:.3f} V with")
check("snubber cuts the peak", pk1 < 0.8 * pk0)
check("snubber kills the ring", late1 < 0.05 * late0)
check("undamped peak matches the energy formula", abs(pk0 - pk_formula) / pk_formula < 0.02)

print()
print("=" * 96)
print("2. Pyro channel: 2S LiPo 8.4 V, low-side FET, igniter 1.0 ohm, total loop R 1.4 ohm (6 A)")
print("=" * 96)
Vb, Rtot = 8.4, 1.4
Ifire = Vb / Rtot
Lb, Ll = 0.3e-6, 0.5e-6      # battery leads + switch (30 cm pair), igniter leads in the av-bay (0.5 m pair)
Coss, Vbr = 300e-12, 35.0    # small 30 V logic-level FET
E_tot = 0.5 * (Lb + Ll) * Ifire**2
Vspike = Ifire * np.sqrt((Lb + Ll) / Coss)
E_av = E_tot * Vbr / (Vbr - Vb)
t_av = (Lb + Ll) * Ifire / (Vbr - Vb)
print(f"  firing current {Ifire:.1f} A; stored in wiring 1/2 L I^2 = {E_tot*1e6:.1f} uJ")
print(f"  FET turned off while current still flows (end of a timed pulse into a shorted/intact bridge):")
print(f"    unclamped LC spike would be I*sqrt(L/Coss) = {Vspike:.0f} V -> the FET avalanches at ~{Vbr:.0f} V;")
print(f"    avalanche energy {E_av*1e6:.1f} uJ over {t_av*1e9:.0f} ns (di/dt {(Vbr-Vb)/(Lb+Ll)/1e6:.0f} A/us) — survivable"
      f" for a small FET (EAS tens of mJ) but a 27 V, 30 MA/s ground-bounce event on the board")
# freewheel diode across the output: lead current circulates through diode+bridge; battery side absorbed by bulk cap
tau_l = Ll / 1.0
Cbulk = 10e-6
dV = Ifire * np.sqrt(Lb / Cbulk)
print(f"  with a freewheel (Schottky) diode across the output terminals: lead current decays in the diode loop,"
      f" tau = L_lead/R_bridge = {tau_l*1e6:.2f} us;")
print(f"    with {Cbulk*1e6:.0f} uF of bulk at the pyro supply node the battery-side inductance only lifts it by"
      f" I sqrt(Lb/C) = {dV:.2f} V; FET sees ~Vb + Vf")
check("unclamped spike exceeds a 30 V FET rating", Vspike > 30)
check("bulk-cap rise small", dV < 1.5)

print()
print("=" * 96)
print("3. Inductive load decay: solenoid/relay L 10 mH, R 12 ohm, 8.4 V (0.70 A)")
print("=" * 96)
L, R = 10e-3, 12.0
I0 = Vb / R
tau = L / R
for name, Vc, Vdev in (("Schottky diode only (0.4 V)", 0.4, 0.4), ("diode + 24 V Zener", 24.7, 24.7),
                       ("TVS across FET, 33 V clamp", 33 - Vb, 33.0)):
    t0 = tau * np.log(1 + I0 * R / Vc)
    t10 = tau * np.log((I0 + Vc / R) / (0.1 * I0 + Vc / R))
    vds = Vb + Vc
    q = (I0 + Vc / R) * tau * (1 - np.exp(-t0 / tau)) - (Vc / R) * t0     # exact integral of i(t) to zero
    print(f"  {name:28s}: current to 10 % in {t10*1e3:.3f} ms, to zero {t0*1e3:.3f} ms; switch sees {vds:.1f} V;"
          f" energy into clamp V_clamp*int(i dt) = {Vdev*q*1e3:.2f} mJ (1/2 L I^2 = {0.5*L*I0**2*1e3:.2f} mJ)")
t_d = tau * np.log(1 + I0 * R / 0.4)
t_z = tau * np.log(1 + I0 * R / 24.7)
check("Zener clamp releases >5x faster than a bare diode", t_d / t_z > 5)

print()
print("=" * 96)
print("4. Hot-plug of a LiPo through an arming switch into ceramic input capacitance")
print("=" * 96)


def hotplug(V, L, R, C, Rd=None, Cd=None, tmax=40e-6):
    def f(t, y):
        i, vc, vd = y
        idamp = 0.0 if Rd is None else (vc - vd) / Rd
        return [(V - vc - R * i) / L, (i - idamp) / C, 0.0 if Rd is None else idamp / Cd]
    s = solve_ivp(f, (0, tmax), [0, 0, 0], max_step=tmax / 8000, rtol=1e-8)
    return s.t, s.y[1]


Lw, Rw = 0.5e-6, 0.03                  # 50 cm loop, pack + switch + wire resistance
Ceff = 5e-6                            # 10 uF 0805 X7R at 8 V DC bias ~ 5 uF
zeta = Rw / 2 * np.sqrt(Ceff / Lw)
for V in (8.4, 12.6):
    t, vc = hotplug(V, Lw, Rw, Ceff)
    pk_f = V * (1 + np.exp(-np.pi * zeta / np.sqrt(1 - zeta**2)))
    Rd = np.sqrt(Lw / Ceff)
    t2, vc2 = hotplug(V, Lw, Rw, Ceff, Rd=Rd, Cd=4 * Ceff)
    print(f"  {V:.1f} V pack: zeta {zeta:.3f}; peak {vc.max():.1f} V (formula {pk_f:.1f} V); "
          f"with damping R_d = sqrt(L/C) = {Rd:.2f} ohm + C_d = 4C = {4*Ceff*1e6:.0f} uF: peak {vc2.max():.1f} V")
    check(f"undamped overshoot ~2x ({V} V)", vc.max() > 1.7 * V)
    check(f"damped overshoot < 1.3x ({V} V)", vc2.max() < 1.3 * V)

print()
print("=" * 96)
print("5. Surge and EFT energy into a clamp (idealised generators)")
print("=" * 96)
# 8/20 us short-circuit current, shape i ~ t^3 exp(-t/tau), tau = 3.911 us (the analytic form given in IEC 61000-4-5 Annex)
tt = np.linspace(0, 200e-6, 400001)
w = tt**3 * np.exp(-tt / 3.911e-6); w /= w.max()
ip = np.argmax(w)
front = 1.25 * (tt[np.argmax(w > 0.9)] - tt[np.argmax(w > 0.1)])
t50 = tt[ip + np.argmax(w[ip:] < 0.5)]
t50a = tt[np.argmax(w > 0.5)]
print(f"  8/20 shape check: front time 1.25*(t90-t10) = {front*1e6:.2f} us, 50 % width Tw = {(t50-t50a)*1e6:.1f} us -> duration 1.18 Tw = {1.18*(t50-t50a)*1e6:.1f} us (Ed. 3 definition)")
charge_per_A = np.trapezoid(w, tt)
for Vs in (500, 1000, 2000):
    Vcl = 20.0
    Ip = (Vs - Vcl) / 2.0
    E = Vcl * Ip * charge_per_A
    print(f"  surge {Vs:4d} V into a 20 V clamp via 2 ohm: Ipk {Ip:.0f} A, energy in clamp {E*1e3:.0f} mJ "
          f"(charge {Ip*charge_per_A*1e3:.1f} mC)")
for Vs in (500, 1000, 2000):
    Ip = (Vs - 20) / 50
    E = 20 * Ip * 50e-9 * 0.75
    print(f"  EFT {Vs:4d} V, 50 ohm, 5/50 ns: Ipk {Ip:.0f} A, energy per pulse {E*1e6:.1f} uJ; 75 pulses/burst at 5 kHz:"
          f" {75*E*1e3:.2f} mJ per burst")
check("8/20 shape: front 8 us +/-20 %, duration 20 us +/-20 %", abs(front - 8e-6) < 1.6e-6 and abs(1.18 * (t50 - t50a) - 20e-6) < 4e-6)

print()
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
