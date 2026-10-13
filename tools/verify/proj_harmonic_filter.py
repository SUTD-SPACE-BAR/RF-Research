#!/usr/bin/env python3
"""
proj_harmonic_filter.py -- design calculations for kb/20-projects-recipes/bandpass-filter-design-walkthrough.md

433.125 MHz harmonic low-pass after a 2 W LoRa PA (EBYTE E22-400T33D / SX1268 + PA), and a 905/920 MHz
version for the E220-900T30D, taken from ideal prototype -> standard values -> real parts (finite Q,
self-resonance, ESL, pad/via parasitics) -> Monte-Carlo tolerances -> power handling.

 1. Requirement: harmonic suppression needed for Singapore TS SRD spurious limits (-36 dBm < 1 GHz,
    -30 dBm >= 1 GHz) at 33/24/10 dBm, for assumed intrinsic module harmonics.
 2. Designs: Chebyshev 0.1 dB N=5 and N=7 (fc 520 MHz, as kb/01), and a 5th-order elliptic ladder whose
    two transmission zeros are placed ON 2f0 and 3f0 (866.25 / 1299.375 MHz), optimised for return loss.
 3. Snap to standard values (Coilcraft 0603CS inductors, C0G capacitors in 0.1 pF / E24 steps).
 4. Real parts: inductor Q(f) and parallel capacitance (SRF), capacitor ESL/ESR, shunt-via inductance
    for a JLC 4-layer (L2 ground 0.21 mm) vs 2-layer (1.5 mm) board; stop-band re-entry up to 6 GHz.
 5. Monte-Carlo: L +/-2 %, C +/-0.1 pF (<10 pF) or +/-2 % -> distributions of IL, RL, rejection at 2f..5f.
 6. Power: branch currents/voltages and per-element dissipation at 33 dBm.
 7. 905 MHz (IREC) / 920 MHz variant, and the RX-side SAW comparison.
Run: python3 tools/verify/proj_harmonic_filter.py
"""
import numpy as np
from scipy import optimize

TP = 2 * np.pi
Z0 = 50.0
F0 = 433.125e6
RNG = np.random.default_rng(7)


# ----------------------------------------------------------------------------- network helpers
def ser(Z):
    Z = np.asarray(Z, complex)
    o, zz = np.ones_like(Z), np.zeros_like(Z)
    return np.moveaxis(np.array([[o, Z], [zz, o]]), -1, 0)


def shu(Y):
    Y = np.asarray(Y, complex)
    o, zz = np.ones_like(Y), np.zeros_like(Y)
    return np.moveaxis(np.array([[o, zz], [Y, o]]), -1, 0)


def chain(mats):
    M = mats[0]
    for m in mats[1:]:
        M = M @ m
    return M


def s_params(M):
    A, B, C, D = M[:, 0, 0], M[:, 0, 1], M[:, 1, 0], M[:, 1, 1]
    den = A + B / Z0 + C * Z0 + D
    s21 = 2 / den
    s11 = (A + B / Z0 - C * Z0 - D) / den
    return s11, s21


def g_cheby(N, rip):
    beta = np.log(1 / np.tanh(rip / 17.37))
    gam = np.sinh(beta / (2 * N))
    a = [np.sin((2 * k - 1) * np.pi / (2 * N)) for k in range(1, N + 1)]
    b = [gam ** 2 + np.sin(k * np.pi / N) ** 2 for k in range(1, N + 1)]
    g = [1.0, 2 * a[0] / gam]
    for k in range(2, N + 1):
        g.append(4 * a[k - 2] * a[k - 1] / (b[k - 2] * g[-1]))
    g.append(1.0 if N % 2 else 1 / np.tanh(beta / 4) ** 2)
    return g


# ----------------------------------------------------------------------------- part models
def q_inductor(f, q433=40.0, fq=433e6):
    """Wire-wound chip inductor Q: rises ~sqrt(f) below the SRF region (empirical shape)."""
    return q433 * np.sqrt(np.asarray(f) / fq)


def z_inductor(f, L, real=True, cp=0.11e-12, q433=40.0):
    w = TP * f
    if not real:
        return 1j * w * L
    R = w * L / q_inductor(f, q433)
    Zs = R + 1j * w * L
    return 1 / (1 / Zs + 1j * w * cp)


def z_capacitor(f, C, real=True, esl=0.45e-9, esr=0.15, via=0.0):
    w = TP * f
    if not real:
        return 1 / (1j * w * C)
    return esr + 1j * w * (esl + via) + 1 / (1j * w * C)


def ladder(f, parts, real=True, via=0.1e-9, q433=40.0, cp=0.11e-12, esl=0.45e-9, pad_c=0.05e-12):
    """parts: list of ('C', C) shunt, ('L', L) series, ('LC', L, C) series L||C.
    Shunt capacitors get an extra series via/ground inductance `via`; each node gets pad capacitance."""
    mats = []
    for p in parts:
        if p[0] == "C":
            Z = z_capacitor(f, p[1], real, esl=esl, via=via)
            mats.append(shu(1 / Z + (1j * TP * f * pad_c if real else 0)))
        elif p[0] == "L":
            mats.append(ser(z_inductor(f, p[1], real, cp=cp, q433=q433)))
        elif p[0] == "LC":
            ZL = z_inductor(f, p[1], real, cp=cp, q433=q433)
            ZC = z_capacitor(f, p[2], real, esl=(0.3e-9 if real else 0))
            mats.append(ser(1 / (1 / ZL + 1 / ZC)))
    return chain(mats)


def lpf_cheby(N, rip, fc):
    g = g_cheby(N, rip)
    wc = TP * fc
    parts = []
    for k in range(1, N + 1):
        parts.append(("C", g[k] / (Z0 * wc)) if k % 2 else ("L", g[k] * Z0 / wc))
    return parts


def elliptic_zeros(fz1, fz2, fband=(425e6, 442e6), fixed=None):
    """5th-order ladder: C1 | (L2||C2) | C3 | (L4||C4) | C5, zeros at fz1, fz2; maximise pass-band RL."""
    fb = np.linspace(*fband, 41)
    fs = np.array([fz1 * 0.97, fz1, fz1 * 1.03, fz2, 1.8e9, 2.2e9])

    def build(p):
        C1, L2, C3, L4, C5 = np.exp(p)
        C2 = 1 / ((TP * fz1) ** 2 * L2)
        C4 = 1 / ((TP * fz2) ** 2 * L4)
        return [("C", C1), ("LC", L2, C2), ("C", C3), ("LC", L4, C4), ("C", C5)]

    def cost(p):
        s11, s21 = s_params(ladder(fb, build(p), real=False))
        rl = -20 * np.log10(np.abs(s11) + 1e-12)
        return np.concatenate([np.maximum(0, 26 - rl) , [0.0]])
    scale = 866.25e6 / fz1
    p0 = np.log(np.array([5.8e-12, 16.7e-9, 11e-12, 20e-9, 6.8e-12]) * scale)
    best = None
    for trial in range(12):
        start = p0 + (RNG.normal(0, 0.15, 5) if trial else 0)
        r = optimize.least_squares(cost, start)
        if best is None or r.cost < best.cost:
            best = r
    return build(best.x)


E24 = np.array([1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6,
                6.2, 6.8, 7.5, 8.2, 9.1])
L_0603CS = np.array([1.8, 2.2, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 8.7, 9.1, 9.5, 10, 11, 12,
                     15, 16, 18, 20, 22, 24, 27, 30, 33, 36, 39, 43, 47, 51, 56, 62, 68, 72, 82, 91, 100]) * 1e-9


def snap_C(C):
    if C < 10e-12:
        return round(C * 1e12 * 10) / 10 * 1e-12    # 0.1 pF steps
    dec = 10 ** np.floor(np.log10(C))
    return E24[np.argmin(np.abs(E24 * dec - C))] * dec


def snap_L(L):
    return L_0603CS[np.argmin(np.abs(L_0603CS - L))]


def snap(parts):
    out = []
    for p in parts:
        if p[0] == "C":
            out.append(("C", snap_C(p[1])))
        elif p[0] == "L":
            out.append(("L", snap_L(p[1])))
        else:
            out.append(("LC", snap_L(p[1]), snap_C(p[2])))
    return out


def snap_zero_targeted(parts, fz, cp=0.11e-12, pad=0.05e-12, fband=(425e6, 442e6)):
    """Real-part workflow: for each trap pick the standard L (within +/-20 %) whose required C, after
    subtracting the inductor self-capacitance cp and pad capacitance, lands closest to a 0.1 pF step;
    then re-optimise and snap the shunt capacitors for pass-band return loss with the real models."""
    traps = []
    for p, f in zip([q for q in parts if q[0] == "LC"], fz):
        best = None
        for L in L_0603CS[(L_0603CS > 0.8 * p[1]) & (L_0603CS < 1.2 * p[1])]:
            c_need = 1 / ((TP * f) ** 2 * L) - cp - pad
            c_sn = snap_C(c_need)
            fz_real = 1 / (TP * np.sqrt(L * (c_sn + cp + pad)))
            # weigh zero accuracy and closeness to the prototype L (the pass band depends on L)
            err = abs(fz_real - f) / f + 0.25 * abs(L - p[1]) / p[1]
            if best is None or err < best[0]:
                best = (err, L, c_sn, fz_real)
        traps.append(best)
    fb = np.linspace(*fband, 41)

    def build(pc):
        C1, C3, C5 = np.exp(pc)
        return [("C", C1), ("LC", traps[0][1], traps[0][2]), ("C", C3), ("LC", traps[1][1], traps[1][2]), ("C", C5)]

    def cost(pc):
        s11, _ = s_params(ladder(fb, build(pc), real=True, via=0.1e-9, cp=cp))
        rl = -20 * np.log10(np.abs(s11) + 1e-12)
        return np.maximum(0, 30 - rl)
    shunts = np.array([q[1] for q in parts if q[0] == "C"])
    # bound each shunt capacitor to 0.6-1.6x its ideal-prototype value (unbounded runs drifted to 0.2 pF)
    lo, hi = np.log(0.6 * shunts), np.log(1.6 * shunts)
    r = optimize.least_squares(cost, np.log(shunts), bounds=(lo, hi))
    out = build(r.x)
    out = [("C", snap_C(q[1])) if q[0] == "C" else q for q in out]
    return out, traps


def fmt(parts, cpar=0.0):
    """cpar: extra capacitance across each trap in the real build (inductor self-C + pads), so the printed
    zero is the one the hardware will have; 0 for ideal prototypes."""
    s = []
    for p in parts:
        if p[0] == "C":
            s.append(f"C {p[1]*1e12:.2f} pF")
        elif p[0] == "L":
            s.append(f"L {p[1]*1e9:.2f} nH")
        else:
            fz = 1 / (TP * np.sqrt(p[1] * (p[2] + cpar)))
            s.append(f"L {p[1]*1e9:.2f} nH || C {p[2]*1e12:.2f} pF (zero {fz/1e6:.1f} MHz"
                     + (f" incl. {cpar*1e12:.2f} pF parasitic)" if cpar else ")"))
    return " | ".join(s)


def report(label, parts, freqs, real=True, **kw):
    s11, s21 = s_params(ladder(freqs, parts, real=real, **kw))
    il = -20 * np.log10(np.abs(s21))
    rl = -20 * np.log10(np.abs(s11))
    return il, rl


def perturb(parts, tolL=0.02, tolC_abs=0.1e-12, tolC_rel=0.02):
    out = []
    def pc(C):
        return C + RNG.uniform(-1, 1) * (tolC_abs if C < 10e-12 else tolC_rel * C)
    for p in parts:
        if p[0] == "C":
            out.append(("C", pc(p[1])))
        elif p[0] == "L":
            out.append(("L", p[1] * (1 + RNG.uniform(-tolL, tolL))))
        else:
            out.append(("LC", p[1] * (1 + RNG.uniform(-tolL, tolL)), pc(p[2])))
    return out


def power_flow(f, parts, p_avail_dbm=33.0, **kw):
    """Branch currents/voltages and dissipation per element for a matched source of available power."""
    # compute input impedance from the load side, then march forward with actual V, I
    zl = Z0
    mats = []
    for p in parts:
        mats.append(ladder(np.array([f]), [p], **kw)[0])
    Mtot = chain([m[None] for m in mats])[0]
    A, B, C, D = Mtot.ravel()
    zin = (A * zl + B) / (C * zl + D)
    Pav = 10 ** (p_avail_dbm / 10) / 1e3
    Vs = np.sqrt(8 * Z0 * Pav)          # source EMF for available power Pav
    Iin = Vs / (Z0 + zin)
    V, I = Iin * zin, Iin
    rows = []
    for p, m in zip(parts, mats):
        a, b, c, d = m.ravel()
        # [V1; I1] = M [V2; I2] -> [V2; I2] = M^-1 [V1; I1]
        Minv = np.linalg.inv(m)
        V2, I2 = Minv @ np.array([V, I])
        if p[0] == "C":
            Ish = I - I2
            pd = np.real(V * np.conj(Ish)) / 2
            rows.append((p, abs(V) / np.sqrt(2), abs(Ish) / np.sqrt(2), pd))
        else:
            pd = np.real((V - V2) * np.conj(I)) / 2
            rows.append((p, abs(V - V2) / np.sqrt(2), abs(I) / np.sqrt(2), pd))
        V, I = V2, I2
    pout = abs(V) ** 2 / (2 * Z0)
    return rows, pout, Pav


def main():
    print("=" * 96)
    print("1) Requirement (Singapore TS SRD Table 1-a spurious: -36 dBm < 1 GHz, -30 dBm >= 1 GHz)")
    for p in (33.0, 24.0, 10.0):
        for n, fh in ((2, 866.25e6), (3, 1299.375e6), (4, 1732.5e6), (5, 2165.6e6)):
            lim = -36.0 if fh < 1e9 else -30.0
            print(f"   P {p:4.0f} dBm, {n}f0 = {fh/1e6:7.1f} MHz: need >= {p - lim:5.1f} dBc total", end="")
            print("" if n < 5 else "\n", end="\n" if n < 5 else "")
    print("   If the module already gives X dBc, the external filter needs (total - X) + margin; X is unknown for the E22")

    fbands = np.array([F0, 866.25e6, 1299.375e6, 1732.5e6, 2165.6e6, 3000e6, 4000e6, 5000e6, 6000e6])
    names = ["f0", "2f", "3f", "4f", "5f", "3G", "4G", "5G", "6G"]
    print("\n2) Designs (ideal, then snapped to standard values, then real parts on a JLC 4-layer board)")
    designs = {
        "Cheb N=5 0.1 dB fc 520": lpf_cheby(5, 0.1, 520e6),
        "Cheb N=7 0.1 dB fc 520": lpf_cheby(7, 0.1, 520e6),
        "Elliptic N=5 zeros on 2f,3f": elliptic_zeros(866.25e6, 1299.375e6),
    }
    snapped = {}
    for k, parts in designs.items():
        if k.startswith("Elliptic"):
            sp, traps = snap_zero_targeted(parts, (866.25e6, 1299.375e6))
            print("   zero-targeted trap choice (incl. 0.11 pF inductor self-C + 0.05 pF pads): "
                  + "; ".join(f"L {t[1]*1e9:.0f} nH + C {t[2]*1e12:.1f} pF -> zero {t[3]/1e6:.1f} MHz" for t in traps))
        else:
            sp = snap(parts)
        snapped[k] = sp
        print(f"   {k}:\n      ideal : {fmt(parts)}\n      snapped: {fmt(sp, cpar=0.16e-12)}")
        for lab, pp, real, via in (("ideal", parts, False, 0.0), ("snapped ideal", sp, False, 0.0),
                                   ("snapped real, 4-layer via 0.1 nH", sp, True, 0.1e-9),
                                   ("snapped real, 2-layer via 0.8 nH", sp, True, 0.8e-9)):
            il, rl = report(lab, pp, fbands, real=real, via=via)
            fb = np.linspace(425e6, 442e6, 35)
            _, rlb = report(lab, pp, fb, real=real, via=via)
            print(f"      {lab:34s}: IL(f0) {il[0]:5.2f} dB, RL(425-442) >= {rlb.min():5.1f} dB; rejection "
                  + ", ".join(f"{n} {min(v, 150.0):5.1f}" for n, v in zip(names[1:], np.nan_to_num(il[1:], nan=999.0))))

    print("\n3) Stop-band vs frequency for the snapped elliptic on 4-layer (via 0.1 nH) and 2-layer (0.8 nH)")
    fsw = np.array([0.6, 0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0]) * 1e9
    for via in (0.1e-9, 0.8e-9):
        il, _ = report("", snapped["Elliptic N=5 zeros on 2f,3f"], fsw, real=True, via=via)
        print(f"   via {via*1e9:.1f} nH: " + ", ".join(f"{f/1e9:.1f}G {v:5.1f}" for f, v in zip(fsw, il)))

    print("\n4) Monte-Carlo (2000 trials): L +/-2 %, C +/-0.1 pF (<10 pF) / +/-2 %, real parts, 4-layer")
    for k in ("Cheb N=7 0.1 dB fc 520", "Elliptic N=5 zeros on 2f,3f"):
        res = []
        for _ in range(2000):
            pp = perturb(snapped[k])
            il, _ = report("", pp, fbands[:5], real=True, via=0.1e-9)
            fb = np.linspace(425e6, 442e6, 12)
            _, rlb = report("", pp, fb, real=True, via=0.1e-9)
            res.append(np.concatenate([il, [rlb.min()]]))
        res = np.array(res)
        print(f"   {k}: IL(f0) median {np.median(res[:,0]):.2f} dB (p95 {np.percentile(res[:,0],95):.2f}); "
              f"RL p5 {np.percentile(res[:,5],5):.1f} dB; rejection median/p5: "
              + ", ".join(f"{n} {np.median(res[:,i]):.1f}/{np.percentile(res[:,i],5):.1f}" for i, n in
                          zip(range(1, 5), names[1:5])))

    print("\n5) Power handling at 33 dBm available (snapped elliptic, real parts)")
    rows, pout, pav = power_flow(F0, snapped["Elliptic N=5 zeros on 2f,3f"], 33.0, real=True, via=0.1e-9)
    for p, vr, ir, pd in rows:
        tag = fmt([p], cpar=0.16e-12)
        print(f"   {tag:52s}: V {vr:5.2f} V rms, I {ir*1e3:6.1f} mA rms, dissipation {pd*1e3:6.1f} mW")
    print(f"   delivered {pout:.3f} W of {pav:.3f} W available -> loss {10*np.log10(pav/pout):.2f} dB")

    print("\n6) Q sensitivity: IL(f0) of the snapped elliptic vs inductor Q at 433 MHz")
    for q in (20, 30, 40, 60, 80):
        il, _ = report("", snapped["Elliptic N=5 zeros on 2f,3f"], np.array([F0]), real=True, via=0.1e-9, q433=q)
        print(f"   Q_L = {q:3d}: IL {il[0]:.2f} dB")

    print("\n7) 905 MHz (IREC) and 920 MHz variants: elliptic zeros on 2f/3f")
    for f1 in (905e6, 920.125e6):
        parts = elliptic_zeros(2 * f1, 3 * f1, fband=(f1 * 0.985, f1 * 1.015))
        print(f"   f0 {f1/1e6:.3f} MHz ideal:   {fmt(parts)}")
        sp, traps = snap_zero_targeted(parts, (2 * f1, 3 * f1), cp=0.15e-12, fband=(f1 * 0.985, f1 * 1.015))
        fb = np.array([f1, 2 * f1, 3 * f1, 4 * f1, 5e9, 6e9])
        print(f"   f0 {f1/1e6:.3f} MHz snapped: {fmt(sp, cpar=0.20e-12)}")
        for via in (0.1e-9, 0.8e-9):
            il, rl = report("", sp, fb, real=True, via=via, cp=0.15e-12, esl=0.35e-9, q433=30.0)
            fbb = np.linspace(f1 * 0.985, f1 * 1.015, 21)
            _, rlb = report("", sp, fbb, real=True, via=via, cp=0.15e-12, esl=0.35e-9, q433=30.0)
            print(f"      real (0402 parts, via {via*1e9:.1f} nH): IL {il[0]:.2f} dB, RL >= {rlb.min():.1f} dB, 2f {il[1]:.1f}, 3f {il[2]:.1f}, "
                  f"4f {il[3]:.1f}, 5G {il[4]:.1f}, 6G {il[5]:.1f} dB")
    print("   RX-side: SAW 902-928 MHz (B39921B3728U410, 2.2 dB, 3x3 mm) vs LC 3-pole coupled-resonator (kb/01: ~9 dB at 26 MHz BW)")


if __name__ == "__main__":
    main()
