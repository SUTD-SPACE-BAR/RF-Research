#!/usr/bin/env python3
"""
Verification for kb/04-real-components-hf/pcb-parasitics-traces-vias-pads.md

  1. Partial self-inductance of an isolated round wire and flat strip (Grover/Rosa/Ruehli forms).
  2. Microstrip per-unit-length L' and C' (quasi-static Pozar/Wheeler formulas, cross-checked with
     scikit-rf MLine Hammerstad-Jensen) for JLCPCB-like stackups; short high-Z line as a series inductor.
  3. Via inductance: Goldfarb-Pucel (via to ground plane) for 1.6 mm and 0.21 mm dielectric;
     H. Johnson's loop formula checked against his published numbers; parallel vias with mutual coupling.
  4. Pad capacitance (parallel plate + simple fringing estimate) for 0402 pads and an SMA edge-launch pad.
  5. Slot in the return plane crossed by a trace: shorted-slotline-stub estimate of the added inductance.
Run: python3 tools/verify/components_pcb_parasitics.py
"""
import numpy as np
MU0 = 4e-7 * np.pi; EPS0 = 8.854e-12; C0 = 299792458.0

def L_wire(l, r, hf=True):
    """partial self-inductance of straight round wire length l, radius r (Grover). hf: no internal L."""
    return MU0 * l / (2 * np.pi) * (np.log(2 * l / r) - (1.0 if hf else 0.75) + r / l)

def L_strip(l, w, t):
    """partial self-inductance of a flat rectangular conductor (Grover/Ruehli approximation)."""
    return MU0 * l / (2 * np.pi) * (np.log(2 * l / (w + t)) + 0.5 + 0.2235 * (w + t) / l)

print("=== 1. Isolated conductors ===")
for l_mm, d_um in [(1.0, 25), (1.0, 50), (2.0, 25), (10.0, 500)]:
    l = l_mm * 1e-3; r = d_um * 1e-6 / 2
    print(f"  round wire {l_mm} mm x {d_um} um dia: L(HF) = {L_wire(l,r)*1e9:.3f} nH, L(DC) = {L_wire(l,r,False)*1e9:.3f} nH "
          f"({L_wire(l,r)/l*1e6:.2f} nH/mm)")
for l_mm, w_mm in [(10, 0.3), (10, 1.0), (1, 0.3)]:
    print(f"  flat strip {l_mm} mm x {w_mm} mm x 35 um: L = {L_strip(l_mm*1e-3, w_mm*1e-3, 35e-6)*1e9:.2f} nH "
          f"(no nearby return plane)")

print("\n=== 2. Microstrip per-unit-length parameters ===")
def microstrip(W, d, er):
    eeff = (er + 1) / 2 + (er - 1) / 2 / np.sqrt(1 + 12 * d / W)
    u = W / d
    if u <= 1:
        Z = 60 / np.sqrt(eeff) * np.log(8 / u + u / 4)
    else:
        Z = 120 * np.pi / (np.sqrt(eeff) * (u + 1.393 + 0.667 * np.log(u + 1.444)))
    Lp = Z * np.sqrt(eeff) / C0; Cp = np.sqrt(eeff) / (C0 * Z)
    return Z, eeff, Lp, Cp
try:
    import skrf as rf
    from skrf.media import MLine
    freq = rf.Frequency(915, 915, 1, unit="MHz")
except Exception:
    MLine = None
cases = [("2-layer 1.6 mm FR-4 (er 4.5), W = 3.0 mm", 3.0e-3, 1.6e-3, 4.5),
         ("2-layer 1.6 mm, W = 0.25 mm (signal trace)", 0.25e-3, 1.6e-3, 4.5),
         ("4-layer, 0.2104 mm prepreg (er 4.4), W = 0.36 mm", 0.36e-3, 0.2104e-3, 4.4),
         ("4-layer, 0.2104 mm prepreg, W = 0.15 mm", 0.15e-3, 0.2104e-3, 4.4)]
for name, W, d, er in cases:
    Z, ee, Lp, Cp = microstrip(W, d, er)
    extra = ""
    if MLine is not None:
        m = MLine(frequency=freq, w=W, h=d, t=35e-6, ep_r=er, rough=0, tand=0, model="hammerstadjensen", disp="none")
        extra = f" | scikit-rf HJ (t=35um): Z0={m.z0_characteristic[0].real:.1f}, eeff={m.ep_reff_f[0].real:.2f}"
    print(f"  {name}: Z0={Z:6.1f} ohm, eeff={ee:.2f}, L'={Lp*1e6:.3f} nH/mm, C'={Cp*1e9:.4f} pF/mm{extra}")
# short high-impedance line as series inductor
Z, ee, Lp, Cp = microstrip(0.15e-3, 0.2104e-3, 4.4)
for l_mm in [2, 5]:
    l = l_mm * 1e-3
    beta_l = 2 * np.pi * 915e6 * np.sqrt(ee) / C0 * l
    Leq = Lp * l
    # exact: series reactance of a line section in pi-model: Z0 sin(beta l)
    print(f"  {l_mm} mm of W=0.15 mm ({Z:.0f} ohm) at 915 MHz: beta*l = {np.degrees(beta_l):.1f} deg, L'l = {Leq*1e9:.3f} nH, "
          f"X_series(exact pi-model) = {Z*np.sin(beta_l):.2f} ohm vs wL = {2*np.pi*915e6*Leq:.2f} ohm; shunt C'l/2 = {Cp*l/2*1e15:.0f} fF each end")

print("\n=== 3. Vias ===")
def L_via_GP(h, r):
    return MU0 / (2 * np.pi) * (h * np.log((h + np.sqrt(h**2 + r**2)) / r) + 1.5 * (r - np.sqrt(r**2 + h**2)))
for h_mm, drill_mm in [(1.6, 0.3), (1.6, 0.6), (1.6, 0.2), (0.2104, 0.3), (0.2104, 0.2), (1.2, 0.3)]:
    h = h_mm * 1e-3; r = drill_mm * 1e-3 / 2
    print(f"  Goldfarb-Pucel: h = {h_mm} mm, drill {drill_mm} mm: L = {L_via_GP(h,r)*1e9:.3f} nH ; "
          f"X @ 915 MHz = {2*np.pi*915e6*L_via_GP(h,r):.2f} ohm, @ 2.45 GHz = {2*np.pi*2.45e9*L_via_GP(h,r):.2f} ohm")
# Johnson loop check (inches)
inch = 25.4e-3
r = 0.005 * inch; h = 0.040 * inch
for s_in, pred_pub, meas in [(0.017, 0.49, 0.46), (0.12, 1.29, 1.41)]:
    s = s_in * inch
    Lloop = MU0 / np.pi * h * np.log(s / r)     # go + return via, each (mu/2pi) h ln(s/r)
    print(f"  Johnson loop (r=0.005\", h=0.040\", s={s_in}\"): (mu0/pi) h ln(s/r) = {Lloop*1e9:.3f} nH "
          f"(published prediction {pred_pub}, measured {meas} nH)")
    assert abs(Lloop * 1e9 - pred_pub) < 0.01
# parallel vias to ground with mutual coupling (filament approximation, each length h, spacing s)
def M_parallel(l, s):
    return MU0 * l / (2 * np.pi) * (np.log(l / s + np.sqrt(1 + (l / s)**2)) - np.sqrt(1 + (s / l)**2) + s / l)
h = 1.6e-3; r = 0.15e-3
Ls = L_via_GP(h, r)
for N, pitch in [(1, 0), (2, 1.0e-3), (4, 1.0e-3), (9, 1.0e-3), (9, 0.7e-3)]:
    if N == 1:
        print(f"  {N} via: {Ls*1e9:.3f} nH"); continue
    n = int(round(np.sqrt(N))) if N in (4, 9) else N
    pos = [(i * pitch, 0.0) for i in range(N)] if N == 2 else [(i * pitch, j * pitch) for i in range(n) for j in range(n)]
    Mmat = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i == j:
                Mmat[i, j] = Ls
            else:
                s = np.hypot(pos[i][0] - pos[j][0], pos[i][1] - pos[j][1])
                Mmat[i, j] = M_parallel(h, s)
    Leff = 1 / np.sum(np.linalg.inv(Mmat))
    print(f"  {N} vias at {pitch*1e3:.1f} mm pitch (h 1.6 mm, 0.3 mm drill): L_eff = {Leff*1e9:.3f} nH "
          f"(naive L/N = {Ls/N*1e9:.3f} nH)")

print("\n=== 4. Pad capacitance (pad treated as a short wide microstrip section; fringing included) ===")
def C_pad(Wp, Lp, d, er):
    _, _, _, Cp = microstrip(Wp, d, er)
    return Cp * Lp
for name, Wp, Lp, d, er, Wline in [("0402 pad 0.55 x 0.5 mm, 0.2104 mm prepreg", 0.55e-3, 0.5e-3, 0.2104e-3, 4.4, 0.36e-3),
                                   ("0402 pad on 1.6 mm FR-4", 0.55e-3, 0.5e-3, 1.6e-3, 4.5, 3.0e-3),
                                   ("0603 pad 0.95 x 0.9 mm, 0.2104 mm", 0.95e-3, 0.9e-3, 0.2104e-3, 4.4, 0.36e-3),
                                   ("SMA edge-launch pad 1.5 x 3 mm, 0.2104 mm", 1.5e-3, 3.0e-3, 0.2104e-3, 4.4, 0.36e-3),
                                   ("QFN exposed pad 3 x 3 mm, 0.2104 mm", 3e-3, 3e-3, 0.2104e-3, 4.4, None)]:
    Cpad = C_pad(Wp, Lp, d, er)
    excess = Cpad - (C_pad(Wline, Lp, d, er) if Wline else 0)
    tag = f"; excess vs a {Wline*1e3:.2f} mm 50-ohm-ish line of same length = {excess*1e12:+.3f} pF" if Wline else ""
    print(f"  {name}: C = {Cpad*1e12:.3f} pF (X @ 915 MHz = {1/(2*np.pi*915e6*Cpad):.0f} ohm){tag}")
print("  (parallel-plate only, 0402 on 0.2104 mm: %.3f pF)" % (EPS0 * 4.4 * 0.55e-3 * 0.5e-3 / 0.2104e-3 * 1e12))

print("\n=== 5. Slot in the return plane (shorted slotline stub estimate) ===")
Zslot = 100.0      # assumed slotline impedance for a ~0.5 mm slot in FR-4 (order of magnitude)
v = C0 / np.sqrt((4.4 + 1) / 2)
for ls_mm in [5, 10, 20, 40]:
    ls = ls_mm * 1e-3
    for f in [433.92e6, 915e6, 2.45e9]:
        bl = 2 * np.pi * f / v * ls / 2
        Zs = 1j * Zslot / 2 * np.tan(bl)       # two shorted stubs of length ls/2 in parallel, in series with the trace
        Leq = Zs.imag / (2 * np.pi * f)
        print(f"  slot {ls_mm:2d} mm, f={f/1e6:7.1f} MHz: series X = {Zs.imag:7.1f} ohm (L_eq = {Leq*1e9:5.2f} nH)")
print(f"  low-frequency limit L = Zslot*ls/(4 v) = {Zslot*10e-3/(4*v)*1e9:.2f} nH for 10 mm; half-wave slot resonance at 915 MHz when ls = {v/915e6/2*1e3:.0f} mm")
print("OK")
