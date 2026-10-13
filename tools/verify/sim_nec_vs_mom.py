#!/usr/bin/env python3
"""sim_nec_vs_mom.py — cross-check of NEC-2 (PyNEC / NEC2++) against this repository's own Galerkin
thin-wire MoM (tools/verify/ant_mom_wire.py, ant_yagi.py by W1-A6), for
kb/16-simulation-tools/nec-antenna-modelling.md (and the open gap in kb/08-antennas/antenna-simulation-nec-openems.md).

The two codes discretise the same integral equation differently (NEC-2: point matching, three-term
sinusoidal basis, delta-gap "applied field" source; ours: Galerkin, triangle basis, mixed potential,
node delta-gap), so agreement is a meaningful independent check.

Pre-registered expectation (before the first run):
  1. 433 MHz dipole, 2 mm wire: resonant length within 1 mm (0.3 %) between codes; R at resonance within 1 ohm;
     peak gain 2.1-2.2 dBi; NEC average-gain test 1.00 +- 0.01.
  2. Thin dipole a = 1e-4 lambda: resonance 0.483-0.485 lambda, R ~ 72 ohm in both.
  3. DL6WU 433 MHz Yagi (6 mm elements, ~2.3 lambda boom): directivity within 0.2 dB, F/B within 2 dB,
     feed impedance within a few ohm, once NEC's segment rules are respected (extended kernel for dA < 8).
  4. Monopole lambda/4 over perfect ground (NEC GN 1) = half the dipole impedance, gain +3 dB.

Run: python3 tools/verify/sim_nec_vs_mom.py      (needs `pip install PyNEC`; ~1-2 min)
"""
import os
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import PyNEC                                                   # noqa: E402

from ant_mom_wire import C0, Wire, directivity, far_field_U, solve   # noqa: E402
from ant_yagi import dl6wu_design, evaluate_yagi                  # noqa: E402

ok_all = True
misses = []


def check(name, cond, detail=""):
    """Pre-registered expectations are reported, not tuned: a miss prints [MISS] and is summarised at the end
    (engineering-ethos rule: faithful reporting). A MISS is a finding about the models, not a script error."""
    global ok_all
    ok_all &= bool(cond)
    if not cond:
        misses.append(name)
    print(f"[{'PASS' if cond else 'MISS'}] {name} {detail}")


# ------------------------------------------------------------------ NEC helpers
def nec_run(wires, f, feed, ek=False, ground=None, nth=91, nph=180, pattern=True):
    """wires: list of (x, y, z0, z1, radius, nseg) z-directed; feed = (wire_index, segment 1-based).
    ground None = free space, 'pec' = perfect ground (GN 1). Returns dict(Z, Gmax_dBi, avg_gain, fwd, back)."""
    c = PyNEC.nec_context()
    g = c.get_geometry()
    for i, (x, y, z0, z1, a, ns) in enumerate(wires):
        g.wire(i + 1, ns, x, y, z0, x, y, z1, a, 1.0, 1.0)
    c.geometry_complete(1 if ground == "pec" else 0)
    if ek:
        # NB: like the EK card (which must follow GE), PyNEC's flag only takes effect AFTER geometry_complete();
        # set before it, it is silently ignored (found while writing this script).
        c.set_extended_thin_wire_kernel(True)
    if ground == "pec":
        c.gn_card(1, 0, 0, 0, 0, 0, 0, 0)
    else:
        c.gn_card(-1, 0, 0, 0, 0, 0, 0, 0)
    c.ex_card(0, feed[0] + 1, feed[1], 0, 1.0, 0, 0, 0, 0, 0)
    c.fr_card(0, 1, f / 1e6, 0)
    out = {}
    if pattern:
        th_n = nth if ground != "pec" else (nth + 1) // 2
        dth = 180.0 / (nth - 1)
        dph = 360.0 / nph
        # RP 0: normal mode, theta 0..180 (0..90 over ground), full phi circle, power gain, average gain on (A=1).
        # The phi grid starts at 90 deg so that the main beam (phi = 0) is NOT on the first phi column:
        # NEC2++'s average-gain sum under-weights the first column (DL6WU Yagi: AGT 0.958 with phi0 = 0,
        # 1.004 with phi0 = 90, own periodic integration 0.999 either way -- found while writing this script).
        c.rp_card(0, th_n, nph, 0, 0, 0, 1, 0.0, 90.0, dth, dph, 0.0, 0.0)
        # RP 1: forward and back gain in the theta = 90 plane (phi = 0 and 180)
        c.rp_card(0, 1, 2, 0, 0, 0, 0, 90.0, 0.0, 0.0, 180.0, 0.0, 0.0)
        rp = c.get_radiation_pattern(0)
        gdb = np.array(rp.get_gain())
        th = np.radians(np.array(rp.get_theta_angles()))
        out["Gmax_dBi"] = float(gdb.max())
        out["avg_gain"] = float(rp.get_average_power_gain())
        G = 10 ** (gdb / 10)
        own = np.trapezoid(G.sum(axis=1) * np.radians(dph) * np.sin(th), th) / (4 * np.pi)
        out["avg_gain_own"] = float(own if ground != "pec" else 2 * own)
        g1 = np.array(c.get_radiation_pattern(1).get_gain()).ravel()
        out["fwd"], out["back"] = float(g1[0]), float(g1[1])
    else:
        c.xq_card(0)
    out["Z"] = complex(c.get_input_parameters(0).get_impedance()[0])
    return out


def nec_dipole(f, L, a, ns, ek=False, pattern=True):
    return nec_run([(0, 0, -L / 2, L / 2, a, ns)], f, (0, ns // 2 + 1), ek=ek, pattern=pattern)


def mom_dipole(f, L, a, nseg=40):
    sol = solve([Wire(0, 0, -L / 2, L / 2, a, nseg)], [(0, nseg // 2, 1.0)], f)
    D, Prad = directivity(sol, np.pi / 2, 0.0, nth=91, nph=36)
    return sol["Zin"][0], 10 * np.log10(D), Prad / sol["Pin"]


def main():
    f = 433e6
    lam = C0 / f
    print("=== 1. 433 MHz dipole, 2 mm wire (a = 1 mm) ===")
    a = 1e-3
    Lres_nec = brentq(lambda L: nec_dipole(f, L, a, 41, pattern=False)["Z"].imag, 0.30, 0.34, xtol=1e-5)
    Lres_nec_ek = brentq(lambda L: nec_dipole(f, L, a, 81, ek=True, pattern=False)["Z"].imag, 0.30, 0.34, xtol=1e-5)
    Lres_mom = brentq(lambda L: mom_dipole(f, L, a)[0].imag, 0.30, 0.34, xtol=1e-5)
    r_nec = nec_dipole(f, Lres_nec, a, 41)
    r_nec_ek = nec_dipole(f, Lres_nec_ek, a, 81, ek=True)
    z_mom, d_mom, e_mom = mom_dipole(f, Lres_mom, a)
    print(f"  NEC-2 41 seg (dA = {Lres_nec/41/a:.1f}): L_res = {Lres_nec*1e3:.2f} mm, R = {r_nec['Z'].real:.2f} ohm, "
          f"Gmax = {r_nec['Gmax_dBi']:.3f} dBi, average gain = {r_nec['avg_gain']:.4f}")
    print(f"  NEC-2 81 seg + EK (dA = {Lres_nec_ek/81/a:.1f}): L_res = {Lres_nec_ek*1e3:.2f} mm, "
          f"R = {r_nec_ek['Z'].real:.2f} ohm, Gmax = {r_nec_ek['Gmax_dBi']:.3f} dBi, avg = {r_nec_ek['avg_gain']:.4f}")
    print(f"  own MoM 40 seg:                L_res = {Lres_mom*1e3:.2f} mm, R = {z_mom.real:.2f} ohm, "
          f"D = {d_mom:.3f} dBi, Prad/Pin = {e_mom:.4f}")
    check("resonant length NEC vs MoM within 1 mm", abs(Lres_nec - Lres_mom) < 1e-3,
          f"({(Lres_nec-Lres_mom)*1e3:+.2f} mm)")
    check("resonant R NEC vs MoM within 1 ohm", abs(r_nec["Z"].real - z_mom.real) < 1.0,
          f"({r_nec['Z'].real - z_mom.real:+.2f} ohm)")
    check("NEC average gain test 1.00 +- 0.01", abs(r_nec["avg_gain"] - 1) < 0.01, f"({r_nec['avg_gain']:.4f})")

    print("  NEC segmentation study at L = 328 mm (thin kernel vs extended kernel):")
    for ns, ek in ((11, False), (21, False), (41, False), (81, False), (81, True), (161, True)):
        z = nec_dipole(f, 0.328, a, ns, ek=ek, pattern=False)["Z"]
        print(f"     {ns:4d} seg {'EK' if ek else '  '} (dA = {0.328/ns/a:5.2f}, dl = lambda/{lam/(0.328/ns):5.0f}): "
              f"Z = {z.real:6.2f}{z.imag:+6.2f}j ohm")

    print("\n=== 2. thin dipole a = 1e-4 lambda ===")
    a2 = 1e-4 * lam
    Ln = brentq(lambda L: nec_dipole(f, L * lam, a2, 51, pattern=False)["Z"].imag, 0.46, 0.5, xtol=1e-6)
    Lm = brentq(lambda L: mom_dipole(f, L * lam, a2)[0].imag, 0.46, 0.5, xtol=1e-6)
    zn = nec_dipole(f, Ln * lam, a2, 51, pattern=False)["Z"]
    zm = mom_dipole(f, Lm * lam, a2)[0]
    print(f"  NEC: {Ln:.4f} lambda, R = {zn.real:.2f} ohm;  MoM: {Lm:.4f} lambda, R = {zm.real:.2f} ohm")
    check("thin-dipole resonance agrees within 0.2 %", abs(Ln - Lm) / Lm < 2e-3)
    check("thin-dipole R agrees within 1 ohm", abs(zn.real - zm.real) < 1.0)

    print("\n=== 3. DL6WU 433 MHz Yagi, 6 mm elements, ~2.3 lambda boom ===")
    dia = 6e-3
    des = dl6wu_design(2.3, dia / lam, dia / lam)
    lengths_m = [L * lam for L in [des["refl"], 0.47] + list(des["dirs"])]
    pos_m = des["pos"] * lam
    res = evaluate_yagi(lengths_m, pos_m, dia / 2, f)         # MoM, driven element re-resonated
    lengths_m[1] = res["Lde"]
    print(f"  {len(lengths_m)} elements, boom {pos_m[-1]*1e3:.0f} mm, DE (resonated in MoM) {res['Lde']*1e3:.1f} mm")
    print(f"  own MoM: D = {10*np.log10(res['D']):.2f} dBi, F/B = {res['FB']:.1f} dB, "
          f"Zin = {res['Zin'].real:.1f}{res['Zin'].imag:+.1f}j ohm, Prad/Pin = {res['PradPin']:.4f}")
    rows = []
    for nseg, ek in ((21, False), (21, True), (41, True), (61, True)):
        wires = [(x, 0.0, -L / 2, L / 2, dia / 2, nseg) for L, x in zip(lengths_m, pos_m)]
        r = nec_run(wires, f, (1, nseg // 2 + 1), ek=ek)
        rows.append((nseg, ek, r))
        print(f"  NEC-2 {nseg} seg/element {'EK' if ek else 'thin'} (dA = {lengths_m[1]/nseg/(dia/2):.1f}): "
              f"G = {r['fwd']:.2f} dBi, F/B = {r['fwd']-r['back']:.1f} dB, Zin = {r['Z'].real:.1f}{r['Z'].imag:+.1f}j ohm, "
              f"avg gain NEC = {r['avg_gain']:.4f} / own integration = {r['avg_gain_own']:.4f}")
    best = rows[-1][2]
    check("Yagi forward gain NEC(61 seg, EK) vs MoM within 0.2 dB",
          abs(best["fwd"] - 10 * np.log10(res["D"])) < 0.2, f"({best['fwd'] - 10*np.log10(res['D']):+.2f} dB)")
    check("Yagi feed resistance within 3 ohm", abs(best["Z"].real - res["Zin"].real) < 3.0,
          f"({best['Z'].real - res['Zin'].real:+.1f} ohm)")

    print("\n=== 4. lambda/4 monopole over perfect ground (NEC GN 1) vs half of a dipole ===")
    a4 = 1e-3 * lam
    zd = nec_dipole(f, 0.5 * lam, a4, 42, ek=True, pattern=False)["Z"]
    rm = nec_run([(0, 0, 0.0, 0.25 * lam, a4, 21)], f, (0, 1), ek=True, ground="pec")
    print(f"  dipole 0.5 lambda: {zd.real:.2f}{zd.imag:+.2f}j; monopole 0.25 lambda on PEC: "
          f"{rm['Z'].real:.2f}{rm['Z'].imag:+.2f}j ohm (page MoM: 42.8+j22.8), Gmax {rm['Gmax_dBi']:.2f} dBi "
          f"(page 5.19), average gain (upper hemisphere) = {rm['avg_gain']:.3f}")
    check("monopole R within 1.5 ohm of half the dipole", abs(rm["Z"].real - zd.real / 2) < 1.5)
    check("monopole on PEC gain 5.0-5.3 dBi", 5.0 < rm["Gmax_dBi"] < 5.3)
    print("\nALL PRE-REGISTERED EXPECTATIONS MET" if ok_all else
          f"\n{len(misses)} pre-registered expectation(s) missed (see page for discussion): " + "; ".join(misses))


if __name__ == "__main__":
    main()
