#!/usr/bin/env python3
"""
s16_crosstalk.py — termination and crosstalk budgets for flight-computer SPI / clock routing
(kb/13-pcb-rf-layout-emc/mixed-signal-layout.md, section "Termination and crosstalk budgets for SPI and clocks").

  A. Per-unit-length L and C matrices of two (and three, with a guard) 0.2 mm traces on L1 of JLC04161H-7628
     (h = 0.2104 mm, er 4.4, 35 um copper, no mask) from the independent 2-D FD field solver tools/verify/tline_fd2d.py.
     Coupling coefficients: k_C = Cm/C11, k_L = Lm/L11, saturated NEXT  kb = (k_C + k_L)/4,
     FEXT coefficient  kf = (k_C - k_L)/2 (FEXT/V = kf * TD/tr, TD = len/v).  tr everywhere = duration of a LINEAR 0-100 % ramp
     (= 1.25 x its 10-90 % time); FDTD in section C confirms the closed forms with this definition.
     Guard trace (0.2 mm) in the middle: floating (Kron-reduced C, L unchanged) or stitched to ground (held at 0 V).
  B. Saturation length L_sat = v*tr/2; NEXT vs coupled length; FEXT vs length.
  C. Independent check: 2-conductor FDTD (Paul's MTL method) of a matched coupled pair; NEXT and FEXT peaks
     compared with the closed forms for 30 mm and 150 mm coupled lengths.
  D. Single-line termination study (FDTD of one line with terminal ODEs): 100 mm SPI clock, driver R_out 30 ohm
     (assumed), tr 1 ns, receiver 5 pF: none / series / parallel / Thevenin / AC termination -> overshoot,
     undershoot, settling, and the mid-line half-step plateau of series termination (multi-drop SCK).
  E. Critical length l_crit = v*tr/6 for typical edges.

Run: python3 tools/verify/s16_crosstalk.py      (~1-2 min, the FD solves dominate)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tline_fd2d as fd  # noqa: E402

C0 = fd.C0
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


H, T, ER = 0.2104e-3, 35e-6, 4.4          # JLC04161H-7628 L1 over L2
W = 0.20e-3                                # typical digital trace width


def geo_traces(xs, names, box_w=12e-3, box_h=5e-3):
    g = fd.Geometry(-box_w / 2, box_w / 2, box_h)
    g.add_dielectric(-box_w / 2, box_w / 2, 0, H, ER)
    for x, n in zip(xs, names):
        g.add_conductor(x - W / 2, x + W / 2, H, H + T, n)
    return g


def cmatrix(g, names, diel, hmin=8e-6, hmax=0.25e-3):
    n = len(names)
    Wd = {}
    for i in range(n):
        Wd[(i,)] = fd.solve_energy(g, {names[i]: 1.0}, hmin, hmax, 1.25, diel)
    Cm = np.zeros((n, n))
    for i in range(n):
        Cm[i, i] = 2 * Wd[(i,)]
    for i in range(n):
        for j in range(i + 1, n):
            Wij = fd.solve_energy(g, {names[i]: 1.0, names[j]: 1.0}, hmin, hmax, 1.25, diel)
            Cm[i, j] = Cm[j, i] = Wij - Wd[(i,)] - Wd[(j,)]
    return Cm


def pair_params(gap, guard=None):
    """gap = edge-to-edge spacing between aggressor and victim. guard: None, 'float', 'gnd' (0.2 mm guard centred)."""
    pitch = gap + W
    xa, xv = -pitch / 2, pitch / 2
    if guard is None:
        g = geo_traces([xa, xv], ["a", "v"])
        C = cmatrix(g, ["a", "v"], True)
        Ca = cmatrix(g, ["a", "v"], False)
    elif guard == "gnd":
        g = geo_traces([xa, 0.0, xv], ["a", "gnd_guard", "v"])   # guard not listed -> held at 0 V
        C = cmatrix(g, ["a", "v"], True)
        Ca = cmatrix(g, ["a", "v"], False)
    else:  # floating guard: Kron-reduce the 3x3 C matrix (zero net charge on the guard); L from the no-guard case
        g = geo_traces([xa, 0.0, xv], ["a", "g", "v"])
        C3 = cmatrix(g, ["a", "g", "v"], True)
        s, k = [0, 2], [1]
        C = C3[np.ix_(s, s)] - C3[np.ix_(s, k)] @ np.linalg.inv(C3[np.ix_(k, k)]) @ C3[np.ix_(k, s)]
        g2 = geo_traces([xa, xv], ["a", "v"])
        Ca = cmatrix(g2, ["a", "v"], False)
    L = np.linalg.inv(Ca) / C0**2
    kC = -C[0, 1] / C[0, 0]
    kL = L[0, 1] / L[0, 0]
    Z0 = np.sqrt(L[0, 0] / C[0, 0])
    v = 1 / np.sqrt(L[0, 0] * C[0, 0])
    return dict(C=C, L=L, kC=kC, kL=kL, kb=(kC + kL) / 4, kf=(kC - kL) / 2, Z0=Z0, v=v)


print("=" * 100)
print("A. Coupled 0.2 mm traces on L1 of JLC04161H-7628 (h 0.2104 mm, er 4.4, no mask) — FD field solver")
print("=" * 100)
res = {}
for gap in (0.2e-3, 0.4e-3, 0.6e-3, 1.0e-3):
    r = pair_params(gap)
    res[gap] = r
    print(f"  gap {gap*1e3:.1f} mm (pitch {(gap+W)*1e3:.1f}): Z0 {r['Z0']:.1f} ohm, v {r['v']/C0:.3f} c, "
          f"kC {r['kC']*100:.2f} %, kL {r['kL']*100:.2f} %, NEXT_sat kb {r['kb']*100:.2f} % ({20*np.log10(r['kb']):.1f} dB), "
          f"kf {r['kf']*100:+.2f} %")
r06f = pair_params(0.6e-3, "float")
r06g = pair_params(0.6e-3, "gnd")
print(f"  gap 0.6 mm + floating 0.2 mm guard: kb {r06f['kb']*100:.2f} %, kf {r06f['kf']*100:+.2f} %")
print(f"  gap 0.6 mm + guard stitched to GND: kb {r06g['kb']*100:.2f} %, kf {r06g['kf']*100:+.2f} %")
check("NEXT falls with spacing", res[0.2e-3]['kb'] > res[0.4e-3]['kb'] > res[0.6e-3]['kb'] > res[1.0e-3]['kb'])
check("FEXT coefficient negative for microstrip (kL > kC)", all(res[g]['kf'] < 0 for g in res))
check("stitched guard beats floating guard", r06g['kb'] < r06f['kb'])
rel_ratio = res[0.2e-3]['kb'] / res[0.6e-3]['kb']
jg = (1 + ((0.6e-3 + W) / H) ** 2) / (1 + ((0.2e-3 + W) / H) ** 2)
print(f"  ratio kb(0.2 mm)/kb(0.6 mm) = {rel_ratio:.2f}; Johnson-Graham 1/(1+(D/h)^2) predicts {jg:.2f}")

print()
print("=" * 100)
print("B. Saturation length and NEXT/FEXT vs coupled length (gap 0.2 mm, 3.3 V edge)")
print("=" * 100)
r = res[0.2e-3]
for tr in (0.5e-9, 1e-9, 2e-9, 5e-9):
    Lsat = r['v'] * tr / 2
    print(f"  tr {tr*1e9:.1f} ns: L_sat = v*tr/2 = {Lsat*1e3:.0f} mm")
tr = 1e-9
Lsat = r['v'] * tr / 2
for Lc in (10e-3, 30e-3, 60e-3, 100e-3, 150e-3):
    next_v = 3.3 * r['kb'] * min(1.0, Lc / Lsat)
    fext_v = 3.3 * r['kf'] * (Lc / r['v']) / tr
    print(f"  coupled {Lc*1e3:5.0f} mm, tr 1 ns: NEXT {next_v*1e3:6.1f} mV, FEXT {fext_v*1e3:+7.1f} mV")

print()
print("=" * 100)
print("C. FDTD check of a matched coupled pair (Paul MTL FDTD), gap 0.2 mm, tr 1 ns, 1 V source (0.5 V on line)")
print("=" * 100)


def mtl_fdtd(L, C, length, tr, Rs, Rl, nz=300, tmax=None, vs=1.0):
    dz = length / nz
    v_max = 1 / np.sqrt(np.min(np.linalg.eigvals(L @ C).real))
    dt = 0.9 * dz / v_max
    td = length / v_max
    tmax = tmax or (3 * td + 4 * tr)
    nt = int(tmax / dt)
    n = L.shape[0]
    V = np.zeros((nz + 1, n))
    I = np.zeros((nz, n))
    Ci, Li = np.linalg.inv(C), np.linalg.inv(L)
    RS, RL = np.diag(Rs), np.diag(Rl)
    A1 = np.linalg.inv(dz / dt * RS @ C + np.eye(n))
    B1 = dz / dt * RS @ C - np.eye(n)
    A2 = np.linalg.inv(dz / dt * RL @ C + np.eye(n))
    B2 = dz / dt * RL @ C - np.eye(n)

    def src(t):
        return np.array([vs * np.clip(t / tr, 0, 1)] + [0.0] * (n - 1))   # linear 0-100 % ramp of duration tr
    near, far, ts = [], [], []
    for k in range(nt):
        t = k * dt
        Vs0, Vs1 = src(t), src(t + dt)
        Vn = V.copy()
        Vn[0] = A1 @ (B1 @ V[0] - 2 * RS @ I[0] + (Vs1 + Vs0))
        Vn[1:nz] = V[1:nz] - (dt / dz) * (I[1:] - I[:-1]) @ Ci.T
        Vn[nz] = A2 @ (B2 @ V[nz] + 2 * RL @ I[nz - 1])
        V = Vn
        I = I - (dt / dz) * (V[1:] - V[:-1]) @ Li.T
        near.append(V[0, 1]); far.append(V[nz, 1]); ts.append(t)
    return np.array(ts), np.array(near), np.array(far)


Z0 = r['Z0']
for Lc in (30e-3, 150e-3):
    t, vn, vf = mtl_fdtd(r['L'], r['C'], Lc, tr, [Z0, Z0], [Z0, Z0])
    next_pred = 0.5 * r['kb'] * min(1.0, Lc / Lsat)
    fext_pred = 0.5 * r['kf'] * (Lc / r['v']) / tr
    print(f"  {Lc*1e3:.0f} mm: NEXT peak FDTD {vn.max()*1e3:.2f} mV vs closed form {next_pred*1e3:.2f} mV; "
          f"FEXT peak FDTD {vf.min()*1e3:+.2f} mV vs {fext_pred*1e3:+.2f} mV")
    check(f"NEXT within 15 % ({Lc*1e3:.0f} mm)", abs(vn.max() - next_pred) / next_pred < 0.15)
    check(f"FEXT within 20 % ({Lc*1e3:.0f} mm)", abs(vf.min() - fext_pred) / abs(fext_pred) < 0.20)

print()
print("=" * 100)
print("D. Termination of a 100 mm SPI clock (single 0.2 mm line), R_out 30 ohm (assumed), tr 1 ns, 3.3 V, receiver 5 pF")
print("=" * 100)


def line_fdtd(Z0, v, length, tr, Rout, scheme, Rser=0.0, Cin=5e-12, nz=200, tmax=12e-9, vdd=3.3):
    Lp, Cp = Z0 / v, 1 / (Z0 * v)
    dz = length / nz
    dt = 0.5 * dz / v
    nt = int(tmax / dt)
    V = np.zeros(nz + 1); I = np.zeros(nz)
    Rs = Rout + Rser
    vc_ac = 0.0
    out_far, out_mid, ts = [], [], []
    for k in range(nt):
        t = k * dt
        vs0 = vdd * np.clip(t / tr, 0, 1); vs1 = vdd * np.clip((t + dt) / tr, 0, 1)
        Vn = V.copy()
        # source node: KCL, half-cell capacitance, trapezoidal source current
        cn = Cp * dz / 2
        # cn (V1-V0)/dt = ((vs1+vs0)/2 - (V1+V0)/2)/Rs - I[0]
        a = cn / dt + 0.5 / Rs
        Vn[0] = ((cn / dt - 0.5 / Rs) * V[0] + 0.5 * (vs1 + vs0) / Rs - I[0]) / a
        Vn[1:nz] = V[1:nz] - (dt / (Cp * dz)) * (I[1:] - I[:-1])
        # load node: cn+Cin, plus termination
        cl = cn + Cin
        if scheme in ("none", "series"):
            Vn[nz] = V[nz] + dt / cl * I[nz - 1]
        elif scheme == "parallel":       # R = Z0 to ground
            a = cl / dt + 0.5 / Z0
            Vn[nz] = ((cl / dt - 0.5 / Z0) * V[nz] + I[nz - 1]) / a
        elif scheme == "thevenin":       # 2 Z0 to VDD and 2 Z0 to GND (Thevenin Z0 at VDD/2)
            R = Z0
            a = cl / dt + 0.5 / R
            Vn[nz] = ((cl / dt - 0.5 / R) * V[nz] + I[nz - 1] + (vdd / 2) / R) / a
        elif scheme == "ac":             # R = Z0 in series with Cac to ground
            Rac, Cac = Z0, 100e-12
            # unknowns Vn, vc_new; i_ac = ((Vn+V)/2 - (vcn+vc)/2)/Rac ; Cac (vcn - vc)/dt = i_ac
            # cl (Vn - V)/dt = I - i_ac
            Mx = np.array([[cl / dt + 0.5 / Rac, -0.5 / Rac], [-0.5 / Rac, Cac / dt + 0.5 / Rac]])
            rhs = np.array([cl / dt * V[nz] + I[nz - 1] - (V[nz] - vc_ac) / (2 * Rac),
                            Cac / dt * vc_ac + (V[nz] - vc_ac) / (2 * Rac)])
            Vn[nz], vc_ac = np.linalg.solve(Mx, rhs)
        V = Vn
        I = I - (dt / (Lp * dz)) * (V[1:] - V[:-1])
        out_far.append(V[nz]); out_mid.append(V[nz // 2]); ts.append(t)
    return np.array(ts), np.array(out_far), np.array(out_mid)


r1 = pair_params(5e-3)          # isolated single trace (5 mm to neighbour)
Z0s, vs = r1['Z0'], r1['v']
length = 100e-3
TD = length / vs
print(f"  single 0.2 mm trace: Z0 {Z0s:.1f} ohm, v {vs/C0:.3f} c, TD(100 mm) {TD*1e9:.3f} ns")
cases = [("none", 0.0), ("series", max(Z0s - 30, 0)), ("parallel", 0.0), ("thevenin", 0.0), ("ac", 0.0)]
summ = {}
for name, rser in cases:
    t, vf, vm = line_fdtd(Z0s, vs, length, 1e-9, 30.0, name, Rser=rser)
    vfin = vf[-1]
    over = (vf.max() - vfin)
    under = vf[np.argmax(vf):].min() - vfin
    # settling to +/-5 % of 3.3 V
    band = 0.05 * 3.3
    idx = np.where(np.abs(vf - vfin) > band)[0]
    tset = t[idx[-1]] if len(idx) else 0.0
    t50 = t[np.argmax(vf > 1.65)]
    # mid-line plateau duration between 30 % and 70 % of final for series case
    plateau = np.sum((vm > 0.3 * vfin) & (vm < 0.7 * vfin)) * (t[1] - t[0])
    summ[name] = dict(over=over, under=under, vfin=vfin, tset=tset)
    print(f"  {name:9s} (Rser {rser:4.1f} ohm): final {vfin:.2f} V, overshoot {over:+.2f} V, ring-back {under:+.2f} V, "
          f"t50 {t50*1e9:.2f} ns, settles (±5 %) by {tset*1e9:.2f} ns, mid-line time in 30-70 % band {plateau*1e9:.2f} ns")
check("unterminated overshoot > 0.5 V", summ["none"]["over"] > 0.5)
check("series termination overshoot < 0.25 V", summ["series"]["over"] < 0.25)
check("parallel termination halves-ish DC level (R_out/(R_out+Z0) divider)", summ["parallel"]["vfin"] < 2.8)
print(f"  parallel termination DC load at 3.3 V: {3.3/(30+Z0s)*1e3:.0f} mA when high; Thevenin (2 x {2*Z0s:.0f} ohm): "
      f"{3.3/(4*Z0s)*1e3:.0f} mA standing either state; AC (R {Z0s:.0f} ohm + 100 pF): ~0 DC, "
      f"switching power C V^2 f = {100e-12*3.3**2*20e6*1e3:.0f} mW at 20 MHz")

print()
print("=" * 100)
print("E. Critical length l = v*tr/6 above which a trace needs to be treated (and usually terminated) as a line")
print("=" * 100)
for tr in (0.5e-9, 1e-9, 2e-9, 5e-9, 10e-9):
    print(f"  tr {tr*1e9:4.1f} ns: l_crit = {vs*tr/6*1e3:5.0f} mm")

print()
print("ALL PASS" if ok_all else "SOME CHECKS FAILED")
