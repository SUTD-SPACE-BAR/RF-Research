#!/usr/bin/env python3
"""
pcb_thermal.py — verification script for kb/13-pcb-rf-layout-emc/thermal-management-rf.md

  1. PA dissipation from efficiency: P_diss = P_DC - P_out (+ P_in) for an E22-400T33D (5 V x 0.85-1.2 A, 2 W out),
     an E220-900T30D (5 V x 0.62 A, 1 W), an SX1262 at +22 dBm (3.3 V x 118 mA), a 1 W FEM (SKY66122: 5 V x 640 mA).
  2. Junction temperature T_j = T_a + P theta_JA, and the theta_JC + theta_board split; theta_JA for an exposed-pad
     QFN with/without thermal vias (series model: vias || + plane spreading + board-to-air).
  3. Spreading resistance in copper planes (thin disk source in an annulus): R = ln(r2/r1)/(2 pi k t), for 35 um and
     15 um planes; and board-to-air convection + radiation h ~ 5-10 + ~6 W/m^2K.
  4. Duty-cycled LoRa telemetry in a sealed av-bay: lumped RC model of a 26 g module (C ~ 21 J/K) coupled to bay air
     and airframe; time to reach a temperature limit; average vs peak; Singapore pad ambient.
  5. Short-time (single-packet) junction heating: 3-node RC ladder (die / package+pad / board), pulse response.
  6. Crystal drift link: temperature rise of an XO 5 mm vs 15 mm from the PA (spreading model) -> ppm (Semtech note).

Run: python3 tools/verify/pcb_thermal.py      (a few seconds)
"""
import numpy as np
from scipy.integrate import solve_ivp

ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


print("=" * 96)
print("1. PA / module dissipation")
print("=" * 96)
cases = [("EBYTE E22-400T33D, 5 V x 1.2 A, 33 dBm", 5.0 * 1.2, 2.0),
         ("EBYTE E22-400T33D, 5 V x 0.85 A, 33 dBm", 5.0 * 0.85, 2.0),
         ("EBYTE E220-900T30D, 5 V x 0.62 A, 30 dBm", 5.0 * 0.62, 1.0),
         ("SX1262 +22 dBm, 3.3 V x 118 mA", 3.3 * 0.118, 0.158),
         ("SKY66122 1 W FEM, 5 V x 0.64 A", 5.0 * 0.64, 1.0)]
for n, pdc, pout in cases:
    print(f"  {n:42s}: P_DC {pdc:5.2f} W, P_out {pout:5.3f} W, efficiency {pout/pdc*100:4.1f} %, heat {pdc-pout:5.2f} W")
check("a 2 W LoRa module dissipates ~2-4 W while transmitting", 2.0 < 5.0 * 0.85 - 2.0 and 5.0 * 1.2 - 2.0 <= 4.0 + 1e-9)

print("\n" + "=" * 96)
print("2-3. Thermal resistance chain for an exposed-pad QFN (4 x 4 mm) on a JLC 4-layer board")
print("=" * 96)
kcu = 385.0
A_wall = np.pi * (0.15e-3**2 - 0.13e-3**2)       # 0.3 mm drill, 20 um wall


def R_via(l, n):
    return l / (kcu * A_wall) / n


def R_spread(r1, r2, t):
    return np.log(r2 / r1) / (2 * np.pi * kcu * t)


for lab, r2 in [("board 30 mm radius", 30e-3), ("board 15 mm radius", 15e-3)]:
    r1 = 2.0e-3
    rs35 = R_spread(r1, r2, 35e-6)
    rs15 = R_spread(r1, r2, 15.2e-6)
    print(f"  {lab}: spreading from a 2 mm-radius pad: 35 um plane {rs35:5.1f} K/W, 15 um plane {rs15:5.1f} K/W")
Rs_top = R_spread(2e-3, 25e-3, 35e-6)
Rs_l2 = R_spread(2e-3, 25e-3, 15.2e-6)
Rs_l3 = Rs_l2
Rs_bot = Rs_top
Rpar_planes = 1 / (1 / Rs_top + 1 / Rs_l2 + 1 / Rs_l3 + 1 / Rs_bot)
h_conv, h_rad = 8.0, 6.0
A_board = 2 * 0.05 * 0.05
R_air = 1 / ((h_conv + h_rad) * A_board)
print(f"  4 planes in parallel (top 35, L2/L3 15.2, bottom 35 um) to 25 mm: {Rpar_planes:5.1f} K/W (if vias connect them all)")
print(f"  50 x 50 mm board to still air (h_conv {h_conv} + h_rad {h_rad} W/m2K, both sides): {R_air:5.1f} K/W")
def theta_ja(nv, Rjc=5.0, A_pad=16e-6):
    """Nodal model: pad(L1) -> {top spreading, prepreg+vias to L2}; L2 -> {spreading, vias through core to L3};
    L3 -> {spreading, prepreg+vias to L4}; L4 -> spreading; all spreading -> board node -> air."""
    kfr4 = 0.3
    def par(*r):
        return 1 / sum(1 / x for x in r if np.isfinite(x))
    seg_pp = 0.2104e-3 + 0.035e-3
    seg_core = 1.065e-3
    Rpp = 0.2104e-3 / (kfr4 * A_pad)
    Rcore = 1.065e-3 / (kfr4 * A_pad)
    Ra = par(R_via(seg_pp, nv), Rpp) if nv else Rpp
    Rb = par(R_via(seg_core, nv), Rcore) if nv else Rcore
    # nodes: 0 pad, 1 L2, 2 L3, 3 L4, 4 board ; conductance matrix
    G = np.zeros((5, 5))
    def link(i, j, R):
        g = 1 / R
        G[i, i] += g; G[j, j] += g; G[i, j] -= g; G[j, i] -= g
    link(0, 4, Rs_top); link(0, 1, Ra); link(1, 4, Rs_l2); link(1, 2, Rb); link(2, 4, Rs_l3)
    link(2, 3, Ra); link(3, 4, Rs_bot)
    # board node to ambient through R_air (ambient = reference, eliminated)
    G[4, 4] += 1 / R_air
    q = np.zeros(5); q[0] = 1.0
    T = np.linalg.solve(G, q)
    return Rjc + T[0], T[0] - T[4], T[4]


for nv in [0, 4, 9, 16]:
    tot, rspread, rair = theta_ja(nv)
    print(f"  {nv:2d} EPAD vias: theta_JC ~5 + pad-to-board spreading/vias {rspread:5.1f} + board-air {rair:5.1f} = theta_JA ~{tot:5.1f} K/W")
R9 = theta_ja(9)[0]
R0 = theta_ja(0)[0]
check("with 9 EPAD vias theta_JA lands in the 25-50 K/W range typical of 4x4 QFNs on 4-layer boards", 25 < R9 < 50,
      f"({R9:.1f} K/W)")
check("EPAD vias lower theta_JA vs no vias", R9 < R0, f"({R0:.1f} -> {R9:.1f} K/W)")
print(f"  SX1262 +22 dBm (0.23 W heat incl. PA): dT_j ~ {0.23*R9:.1f} K; a discrete 1 W FEM (2.2 W): {2.2*R9:.0f} K -> needs"
      f" a much larger copper area, more vias and a heat path to the structure")

print("\n" + "=" * 96)
print("4. 2 W module duty-cycled in a sealed av-bay (lumped model)")
print("=" * 96)
m_mod, c_mod = 0.0259, 800.0
C_mod = m_mod * c_mod
A_mod = 2 * 0.037 * 0.060
R_mod_air = 1 / ((5.0 + 6.0) * A_mod)       # weak natural convection in a closed bay + radiation
C_bay = 0.15 * 900.0                        # board(s), battery share, bulkheads ~150 g effective, c ~900
R_bay_out = 1 / (6.0 * np.pi * 0.098 * 0.25)    # 98 mm OD x 250 mm bay section, outside h ~6 W/m2K (still air on pad)
print(f"  module C {C_mod:.1f} J/K, module->bay R {R_mod_air:.1f} K/W (tau {C_mod*R_mod_air/60:.1f} min);"
      f" bay C {C_bay:.0f} J/K, bay->outside R {R_bay_out:.1f} K/W (tau {C_bay*R_bay_out/60:.0f} min)")
T_amb = 32.0
res = {}
for duty in [1.0, 0.5, 0.2, 0.05]:
    P = 4.0 * duty

    def rhs(t, T):
        Tm, Tb = T
        q1 = (Tm - Tb) / R_mod_air
        q2 = (Tb - T_amb) / R_bay_out
        return [(P - q1) / C_mod, (q1 - q2) / C_bay]

    sol = solve_ivp(rhs, [0, 3600 * 2], [T_amb, T_amb], max_step=10.0, dense_output=True)
    t60 = sol.sol(3600)[0]
    tss = T_amb + P * (R_mod_air + R_bay_out)
    hit85 = None
    for tt in np.arange(0, 7200, 10):
        if sol.sol(tt)[0] >= 85:
            hit85 = tt
            break
    res[duty] = (t60, tss)
    print(f"  TX duty {duty*100:5.1f} % (avg {P:.2f} W): module after 60 min {t60:6.1f} C, steady state {tss:6.1f} C;"
          f" reaches 85 C at {('%.0f min' % (hit85/60)) if hit85 else 'never (2 h)'}")
check("continuous 2 W TX in a sealed bay exceeds the 85 C module rating within an hour (lumped estimate)", res[1.0][0] > 85,
      f"({res[1.0][0]:.0f} C)")
check("20 % duty stays below 85 C after 60 min from a 32 C pad", res[0.2][0] < 85, f"({res[0.2][0]:.0f} C)")
print("  (solar heating of the airframe on the pad adds tens of degrees to T_amb; treat these as lower bounds)")

print("\n" + "=" * 96)
print("5. Single-packet junction heating (3-node ladder: die - package/pad - local board)")
print("=" * 96)
Cn = [0.002, 0.05, 2.0]          # J/K: die, package + pad copper, local board area
Rn = [5.0, 15.0, 25.0]           # K/W: die->pkg, pkg->board, board->ambient
P_pk = 0.25
for ton in [0.05, 0.3, 1.0, 3.0]:
    def rhs3(t, T):
        p = P_pk if t < ton else 0.0
        T1, T2, T3 = T
        q12 = (T1 - T2) / Rn[0]
        q23 = (T2 - T3) / Rn[1]
        q3a = T3 / Rn[2]
        return [(p - q12) / Cn[0], (q12 - q23) / Cn[1], (q23 - q3a) / Cn[2]]
    s = solve_ivp(rhs3, [0, ton], [0, 0, 0], max_step=ton / 200)
    print(f"  {P_pk} W for {ton:4.2f} s: die rise {s.y[0,-1]:5.2f} K, pad {s.y[1,-1]:5.2f} K, board {s.y[2,-1]:5.2f} K"
          f" (steady-state die rise would be {P_pk*sum(Rn):.1f} K)")
print("  -> per-packet die heating is small; what drifts a crystal is the slow board-temperature rise (seconds)")

print("\n" + "=" * 96)
print("6. Crystal / TCXO temperature rise vs distance from the PA (top-copper spreading model)")
print("=" * 96)
for d in [3e-3, 5e-3, 10e-3, 15e-3]:
    dT = 0.23 * np.log(25e-3 / d) / (2 * np.pi * kcu * 35e-6 * 4)       # 4 planes in parallel, crude
    print(f"  XO {d*1e3:4.0f} mm from an SX1262 dissipating 0.23 W: steady rise above board-edge temperature ~{dT:4.1f} K"
          f" -> a crystal near its 25 C turnover slope (~ -0.3 ppm/K assumed) drifts ~{0.3*dT:4.2f} ppm")
print("  Semtech measured drift beyond tolerance for +22 dBm packets > 0.4-0.5 s without insulation (AN1200.37);"
      " copper voids around the XO raise the local thermal resistance from the PA.")

print("\nALL CHECKS PASSED" if ok_all else "\nSOME CHECKS FAILED")
