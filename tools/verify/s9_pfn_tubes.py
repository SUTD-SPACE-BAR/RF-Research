#!/usr/bin/env python3
"""W5-S9 checks for kb/11-radar/diy-radar-hardware.md section "Microwave tubes and pulse modulators".

Run:  python3 tools/verify/s9_pfn_tubes.py   (<1 s)

1. Line-type modulator: pulse-forming network (PFN) Z0 = sqrt(L/C), pulse width tau = 2 sqrt(L_tot C_tot);
   matched load gets V0/2; energy per pulse 0.5 C_tot V0^2 = V_load I_load tau; pulse-transformer ratio.
   Lumped 5-section Guillemin-free (equal LC ladder) simulation of the output pulse into a matched load.
2. Average power and duty of pulsed magnetron radars (marine X-band examples).
3. Electron beam velocity vs beam voltage (relativistic) -> slow-wave phase velocity for a TWT / klystron drift.
4. Microwave-oven parts hazard numbers: HV capacitor energy; power density of an unshielded 800 W magnetron
   vs ICNIRP 2020 general-public reference level (10 W/m^2) and the oven leakage limit (50 W/m^2 at 5 cm).
"""
import numpy as np
from scipy.integrate import solve_ivp

c = 299_792_458.0
e = 1.602176634e-19
me = 9.1093837015e-31
ok_all = True


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.5g}, expected {want:.5g} (tol {tol})")


print("=" * 78)
print("1. PFN sizing: 1 us pulse, 50 ohm line, magnetron 12 kV / 10 A")
tau, Z0 = 1e-6, 50.0
Ct = tau / (2 * Z0); Lt = Z0 * tau / 2
print(f"    C_tot = tau/(2 Z0) = {Ct*1e9:.1f} nF, L_tot = Z0 tau/2 = {Lt*1e6:.1f} uH")
check("C_tot (nF)", Ct * 1e9, 10.0, 1e-9)
check("L_tot (uH)", Lt * 1e6, 25.0, 1e-9)
Vk, Ik = 12e3, 10.0
Rk = Vk / Ik
n = np.sqrt(Rk / Z0)
V0 = 2 * Vk / n
E = 0.5 * Ct * V0**2
print(f"    magnetron as a load: {Rk:.0f} ohm -> transformer 1:{n:.2f}; PFN charged to V0 = 2 Vk/n = {V0/1e3:.2f} kV")
print(f"    energy per pulse 0.5 C V0^2 = {E:.3f} J = Vk Ik tau = {Vk*Ik*tau:.3f} J; resonant charging needs a {V0/2/1e3:.2f} kV supply")
check("energy balance (J)", E, Vk * Ik * tau, 1e-6)
# 5-section LC ladder discharging into a matched resistor
Ns = 5
L = Lt / Ns; C = Ct / Ns


def rhs(t, y):
    v = y[:Ns]; i = y[Ns:]
    dv = np.zeros(Ns); di = np.zeros(Ns)
    # node k capacitor, inductor k from node k to node k+1 (last inductor to the load resistor)
    for k in range(Ns):
        iin = i[k - 1] if k > 0 else 0.0
        dv[k] = (iin - i[k]) / C
    for k in range(Ns):
        vnext = v[k + 1] if k < Ns - 1 else i[k] * Z0
        di[k] = (v[k] - vnext) / L
    return np.concatenate([dv, di])


y0 = np.concatenate([np.full(Ns, V0), np.zeros(Ns)])
t = np.linspace(0, 3e-6, 3001)
sol = solve_ivp(rhs, (0, 3e-6), y0, t_eval=t, max_step=2e-9, rtol=1e-8, atol=1e-6)
vout = sol.y[-1] * Z0
flat = vout[(t > 0.4e-6) & (t < 0.8e-6)]
above = t[vout > 0.5 * V0 / 2]
width = above[-1] - above[0]
print(f"    5-section ladder into {Z0:.0f} ohm: mean flat-top {flat.mean()/1e3:.2f} kV (V0/2 = {V0/2e3:.2f} kV), ripple +/-{(flat.max()-flat.min())/2/flat.mean()*100:.0f} %, 50 % width {width*1e6:.2f} us")
check("flat-top = V0/2 (rel)", flat.mean() / (V0 / 2), 1.0, 0.05)
check("pulse width at 50 % (us)", width * 1e6, 1.0, 0.1)

print("=" * 78)
print("2. Pulsed magnetron radar duty and average power")
for P, tw, prf in ((4e3, 0.08e-6, 3000), (4e3, 1.0e-6, 750), (25e3, 1.2e-6, 750)):
    print(f"    peak {P/1e3:4.0f} kW, {tw*1e6:4.2f} us, PRF {prf:4d} Hz: duty {tw*prf*100:.3f} %, average {P*tw*prf:5.2f} W, range resolution {c*tw/2:5.0f} m, blind range {c*tw/2:5.0f} m")
check("4 kW 0.08 us 3 kHz average (W)", 4e3 * 0.08e-6 * 3000, 0.96, 1e-9)

print("=" * 78)
print("3. Beam velocity vs voltage (relativistic)")
for V in (1e3, 3e3, 10e3, 30e3, 100e3):
    g = 1 + e * V / (me * c**2)
    beta = np.sqrt(1 - 1 / g**2)
    print(f"    {V/1e3:5.0f} kV: v = {beta:.3f} c -> a TWT slow-wave circuit must slow the RF to ~{beta:.3f} c (helix pitch angle ~ {np.degrees(np.arcsin(beta)):.1f} deg)")
g = 1 + e * 3e3 / (me * c**2)
check("3 kV beam velocity (v/c)", np.sqrt(1 - 1 / g**2), 0.108, 0.001)

print("=" * 78)
print("4. Microwave-oven parts: hazard numbers")
for Cap, Vrms in ((0.9e-6, 2000), (1.0e-6, 2100)):
    Vp = Vrms * np.sqrt(2)
    print(f"    HV cap {Cap*1e6:.1f} uF charged to {Vp/1e3:.2f} kV: stored {0.5*Cap*Vp**2:.1f} J (half-wave doubler cathode up to ~{2*Vp/1e3:.1f} kV unloaded)")
check("1 uF at 2.83 kV (J)", 0.5 * 1e-6 * (2000 * np.sqrt(2)) ** 2, 4.0, 0.01)
P, G = 800.0, 1.64
for R in (0.3, 1.0, 3.0, 10.0):
    S = P * G / (4 * np.pi * R**2)
    print(f"    unshielded 800 W magnetron (stub ~2.15 dBi) at {R:4.1f} m: {S:8.1f} W/m^2 = {S/10:7.2f} x ICNIRP general-public 10 W/m^2")
Rsafe = np.sqrt(P * G / (4 * np.pi * 10))
print(f"    distance to fall to 10 W/m^2 (far-field estimate): {Rsafe:.2f} m; oven door leakage limit is 50 W/m^2 (5 mW/cm^2) at 5 cm in service")
check("distance to 10 W/m^2 (m)", Rsafe, 3.23, 0.02)

print("=" * 78)
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
