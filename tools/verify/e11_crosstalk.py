#!/usr/bin/env python3
"""e11_crosstalk.py — checks for kb/13-pcb-rf-layout-emc/digital-termination-and-crosstalk.md (W5-E11).

1. Reflections and termination (method of characteristics / Bergeron, lossless line):
   CMOS driver (step, rise time tr, output resistance Rs) -> 50-ohm line (delay TD) -> 5 pF receiver.
   Overshoot vs TD/tr unterminated; series, parallel, Thevenin and AC (RC) terminations: overshoot,
   settling and DC power.
2. NEXT/FEXT from mutual L and C: 2-D field solver (tline_fd2d.coupled_params) -> even/odd Z and eeff ->
   L, C matrices -> Kb = (Lm/L + Cm/C)/4, kf = (Cm/C - Lm/L)/2; checked against an exact even/odd-mode
   frequency-domain simulation of the matched coupled pair driven by a ramp (inverse FFT).
3. The 3W rule evaluated numerically on JLC04161H-7628 and on a 2-layer 1.5 mm board.
4. A clock trace beside an RF trace: coupling at 920 MHz vs spacing over a 10 mm run.

Run: python3 tools/verify/e11_crosstalk.py      (~1-2 min; the field solves dominate)
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tline_fd2d as fd                    # noqa: E402
from tline_microstrip import ms_hj          # noqa: E402

C0 = 299792458.0
RES = []


def check(name, ok, detail=""):
    RES.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


# ------------------------------------------------------------------ 1. Bergeron line simulation
def ramp(t, tr, V=3.3):
    return V * np.clip(t / tr, 0, 1)


def simulate(TD, tr, Rs=25.0, Z0=50.0, CL=5e-12, term="none", Rt=50.0, Ct=None, R1=100.0, R2=100.0,
             Vcc=3.3, n_per_td=200, t_end_td=40):
    """Lossless line, delay TD. Near end: ramp source through Rs (+ series Rt if term == 'series').
    Far end: CL plus optional termination. Returns t, v_near, v_far, DC far-end termination power."""
    dt = TD / n_per_td
    nsteps = int(t_end_td * n_per_td)
    a = np.zeros(nsteps + n_per_td + 1)       # forward wave launched at near end (delayed n_per_td)
    b = np.zeros(nsteps + n_per_td + 1)       # backward wave launched at far end
    Rsrc = Rs + (Rt if term == "series" else 0.0)
    vf_prev, vc_prev = 0.0, 0.0
    t = np.arange(nsteps) * dt
    vn, vf = np.zeros(nsteps), np.zeros(nsteps)
    for k in range(nsteps):
        b_arr = b[k - n_per_td] if k >= n_per_td else 0.0
        vs = ramp(t[k], tr)
        # near end: (vs - v)/Rsrc = (v - 2 b_arr)/Z0 ... line seen as Thevenin 2 b_arr behind Z0
        v = (vs / Rsrc + 2 * b_arr / Z0) / (1 / Rsrc + 1 / Z0)
        a[k] = v - b_arr
        vn[k] = v
        a_arr = a[k - n_per_td] if k >= n_per_td else 0.0
        # far end node: (2 a_arr - v)/Z0 = CL dv/dt + i_term(v)   (backward Euler companion models)
        G = 1 / Z0 + CL / dt
        I = 2 * a_arr / Z0 + CL / dt * vf_prev
        if term == "parallel":
            G += 1 / Rt
        elif term == "thevenin":
            G += 1 / R1 + 1 / R2; I += Vcc / R1
        elif term == "ac":
            # series Rt + Ct: companion of the capacitor in series with Rt
            gc = 1 / (Rt + dt / Ct)
            G += gc; I += gc * vc_prev
        v = I / G
        if term == "ac":
            ic = (v - vc_prev) / (Rt + dt / Ct)
            vc_prev = vc_prev + ic * dt / Ct
        vf_prev = v
        b[k] = v - a_arr
        vf[k] = v
    if term == "parallel":
        p = Vcc ** 2 / Rt
    elif term == "thevenin":
        p = Vcc ** 2 / (R1 + R2)
    else:
        p = 0.0
    return t, vn, vf, p


def part1():
    print("1. Reflections and termination (Rs 25 ohm, Z0 50 ohm, 5 pF receiver, tr = 1 ns, 3.3 V)")
    tr = 1e-9
    rows = []
    for ratio in (0.05, 0.1, 0.17, 0.25, 0.5, 1.0, 2.0):
        TD = ratio * tr
        t, vn, vf, _ = simulate(TD, tr)
        os_ = (vf.max() - 3.3) / 3.3 * 100
        us = (3.3 - vf[t > 2 * tr + 4 * TD].min()) / 3.3 * 100 if np.any(t > 2 * tr + 4 * TD) else 0
        rows.append((ratio, os_, us))
        L_mm = TD * C0 / np.sqrt(3.3) * 1e3
        print(f"   TD/tr = {ratio:4.2f} (≈ {L_mm:5.1f} mm on FR-4 microstrip): far-end overshoot {os_:5.1f} %, "
              f"later undershoot {us:5.1f} %")
    # find the TD/tr where overshoot crosses 10 %
    r = np.array([x[0] for x in rows]); o = np.array([x[1] for x in rows])
    crit = np.interp(10.0, o, r) if o.max() > 10 else np.nan
    print(f"   overshoot reaches 10 % at TD/tr ≈ {crit:.2f}")
    check("unterminated overshoot is small (< 5 %) for TD < tr/10", rows[1][1] < 5, f"{rows[1][1]:.1f} %")
    check("unterminated overshoot exceeds 15 % once TD > tr/2", rows[4][1] > 15, f"{rows[4][1]:.1f} %")
    print("   terminations at TD = tr (≈ 165 mm), 3.3 V:")
    TD = tr
    res = {}
    for name, kw in (("none", {}), ("series (Rs+Rt = Z0)", dict(term="series", Rt=25.0)),
                     ("parallel 50 ohm to GND", dict(term="parallel", Rt=50.0)),
                     ("Thevenin 100/100 to 3.3 V", dict(term="thevenin", R1=100.0, R2=100.0)),
                     ("AC 50 ohm + 100 pF", dict(term="ac", Rt=50.0, Ct=100e-12)),
                     ("AC 50 ohm + 22 pF (too small)", dict(term="ac", Rt=50.0, Ct=22e-12))):
        t, vn, vf, p = simulate(TD, tr, **kw)
        final = vf[-1]
        os_ = (vf.max() - final) / max(final, 1e-9) * 100
        # time to settle within 5 % of final
        bad = np.where(np.abs(vf - final) > 0.05 * max(final, 1e-9))[0]
        ts = t[bad[-1]] * 1e9 if len(bad) else 0.0
        res[name] = (os_, final, ts, p)
        print(f"     {name:30s}: final {final:4.2f} V, overshoot {os_:5.1f} %, settle(5 %) {ts:5.2f} ns, "
              f"DC power {p*1e3:6.1f} mW (high state)")
    check("series termination removes far-end overshoot (< 3 %)", res["series (Rs+Rt = Z0)"][0] < 3)
    check("parallel 50 ohm at 3.3 V costs > 200 mW in the high state and cuts the swing to 2/3 (Rs 25 ohm)",
          res["parallel 50 ohm to GND"][3] > 0.2 and res["parallel 50 ohm to GND"][1] < 2.3,
          f"{res['parallel 50 ohm to GND'][1]:.2f} V")
    check("AC termination with RC >> 2TD settles faster than unterminated",
          res["AC 50 ohm + 100 pF"][2] < res["none"][2])
    # series-terminated near-end half-step plateau
    t, vn, vf, _ = simulate(TD, tr, term="series", Rt=25.0)
    mid = vn[(t > 1.2 * tr) & (t < 1.8 * tr)].mean()
    check("series termination: near-end plateau at V/2 for 2TD (do not load mid-line)", abs(mid - 1.65) < 0.05,
          f"{mid:.2f} V")


# ------------------------------------------------------------------ 2. coupled lines
def lc_matrices(W, s, h, t, er):
    geo = fd.coupled_microstrip_geo(W, s, h, t, er)
    hmin, hmax = min(W, s, h) / 12, h / 3
    Ze, Zo, ee, eo = fd.coupled_params(geo, hmin=hmin, hmax=hmax)
    ve, vo = C0 / np.sqrt(ee), C0 / np.sqrt(eo)
    Le, Lo = Ze / ve, Zo / vo
    Ce, Co = 1 / (Ze * ve), 1 / (Zo * vo)
    L11, Lm = (Le + Lo) / 2, (Le - Lo) / 2
    C11, Cm = (Ce + Co) / 2, (Co - Ce) / 2
    return dict(Ze=Ze, Zo=Zo, ee=ee, eo=eo, L=L11, Lm=Lm, C=C11, Cm=Cm,
                Kb=0.25 * (Lm / L11 + Cm / C11), kf=0.5 * (Cm / C11 - Lm / L11))


def modal_sim(p, length, tr, R, N=2 ** 14, tmax=None):
    """Matched coupled pair: aggressor driven by a 1 V ramp through R; all four ends R. Even/odd superposition.
    Returns t, near-end victim, far-end victim (V) and aggressor far end."""
    tmax = tmax or 40 * length * np.sqrt(max(p["ee"], p["eo"])) / C0 + 10 * tr
    dt = tmax / N
    f = np.fft.rfftfreq(N, dt)
    w = 2 * np.pi * f
    # spectrum of a ramp-step (rise tr): derivative is a rectangular pulse of height 1/tr
    with np.errstate(divide="ignore", invalid="ignore"):
        Sd = np.where(f > 0, np.sinc(f * tr) * np.exp(-1j * w * tr / 2), 1.0)   # spectrum of d/dt(step)
    out = {}
    for mode, Z, e in (("e", p["Ze"], p["ee"]), ("o", p["Zo"], p["eo"])):
        b = w * np.sqrt(e) / C0
        Gs = (R - Z) / (R + Z)
        GL = Gs
        P = np.exp(-1j * b * length)
        # source Vs/2 per mode through R into line Z, load R: voltage at x=0 and x=l
        Vplus = 0.5 * Z / (Z + R) / (1 - Gs * GL * P ** 2)
        out[mode + "0"] = Vplus * (1 + GL * P ** 2)
        out[mode + "l"] = Vplus * P * (1 + GL)
    def td(H):
        # response to step = integral of response to d/dt(step)
        x = np.fft.irfft(H * Sd, N) / dt * dt
        return np.cumsum(x)
    t = np.arange(N) * dt
    near_v = td(out["e0"] - out["o0"])
    far_v = td(out["el"] - out["ol"])
    far_a = td(out["el"] + out["ol"])
    return t, near_v, far_v, far_a


def part2():
    print("2. NEXT / FEXT from mutual L and C (JLC04161H-7628, h 0.2104 mm, er 4.4, 35 um Cu)")
    h, er, tcu = 0.2104e-3, 4.4, 35e-6
    W = 0.20e-3
    p = lc_matrices(W, 0.20e-3, h, tcu, er)
    print(f"   W = 0.20 mm, gap 0.20 mm: Ze {p['Ze']:.1f}, Zo {p['Zo']:.1f} ohm, eeff e/o {p['ee']:.3f}/{p['eo']:.3f}; "
          f"Lm/L = {p['Lm']/p['L']:.4f}, Cm/C = {p['Cm']/p['C']:.4f}; Kb = {p['Kb']:.4f} ({20*np.log10(p['Kb']):.1f} dB), "
          f"kf = {p['kf']:.4f}")
    R = np.sqrt(p["Ze"] * p["Zo"])
    for length, tr in ((0.10, 0.5e-9), (0.10, 2e-9), (0.02, 1e-9)):
        t, nv, fv, fa = modal_sim(p, length, tr, R)
        v = C0 / np.sqrt(0.5 * (p["ee"] + p["eo"]))
        TD = length / v
        # incident signal on the aggressor = 0.5 V (1 V source into matched R)
        next_pk = np.max(np.abs(nv)) / 0.5
        fext_pk = np.max(np.abs(fv)) / 0.5
        next_pred = p["Kb"] * min(1.0, 2 * TD / tr)
        fext_pred = abs(p["kf"]) * TD / tr
        print(f"   length {length*1e3:4.0f} mm, tr {tr*1e9:.1f} ns (2TD/tr = {2*TD/tr:4.2f}): NEXT sim {next_pk:.4f} vs "
              f"formula {next_pred:.4f}; FEXT sim {fext_pk:.4f} vs formula {fext_pred:.4f} (sign {np.sign(fv[np.argmax(np.abs(fv))]):+.0f})")
        if length == 0.10 and tr == 0.5e-9:
            check("saturated NEXT = Kb within 10 % (10 cm, 0.5 ns)", abs(next_pk / next_pred - 1) < 0.10)
            check("FEXT = kf * TD/tr within 15 % (10 cm, 0.5 ns)", abs(fext_pk / fext_pred - 1) < 0.15)
            check("microstrip FEXT is negative (inductive coupling dominates)", np.sign(fv[np.argmax(np.abs(fv))]) < 0)
        if length == 0.02:
            check("short coupled length (2TD < tr): NEXT scales as Kb * 2TD/tr within 15 %", abs(next_pk / next_pred - 1) < 0.15)
    # stripline-like homogeneous medium: FEXT vanishes
    print("   (homogeneous dielectric -> Lm/L = Cm/C -> kf = 0; checked with a fully embedded pair)")
    g = fd.Geometry(-5e-3, 5e-3, 0.42e-3)
    g.add_dielectric(-5e-3, 5e-3, 0, 0.42e-3, 4.4)
    g.add_conductor(-0.1e-3 - 0.2e-3, -0.1e-3, 0.2e-3, 0.22e-3, "s1")
    g.add_conductor(0.1e-3, 0.3e-3, 0.2e-3, 0.22e-3, "s2")
    Ze, Zo, ee, eo = fd.coupled_params(g, hmin=0.01e-3, hmax=0.1e-3)
    check("stripline (homogeneous): eeff_even = eeff_odd (FEXT ~ 0)", abs(ee - eo) < 0.01 * ee, f"{ee:.3f} vs {eo:.3f}")


def part3():
    print("3. The 3W rule, evaluated")
    cases = (("JLC04161H-7628, W 0.20 mm", 0.20e-3, 0.2104e-3, 4.4), ("2-layer h 1.51 mm, W 0.30 mm", 0.30e-3, 1.51e-3, 4.5))
    table = {}
    for name, W, h, er in cases:
        for cc in (2, 3, 5, 10):          # centre-to-centre spacing in W
            s = (cc - 1) * W
            p = lc_matrices(W, s, h, 35e-6, er)
            D = cc * W
            jg = 1 / (1 + (D / h) ** 2)
            table[(name, cc)] = p["Kb"]
            print(f"   {name}: centre spacing {cc}W = {D*1e3:.2f} mm (D/h {D/h:4.2f}): Kb = {p['Kb']:.4f} "
                  f"({20*np.log10(p['Kb']):6.1f} dB), |kf| = {abs(p['kf']):.4f}; J&G 1/(1+(D/h)^2) = {jg:.3f}")
    k3_thin = table[("JLC04161H-7628, W 0.20 mm", 3)]
    k3_thick = table[("2-layer h 1.51 mm, W 0.30 mm", 3)]
    check("3W on thin prepreg gives NEXT below -25 dB (Kb < 0.056)", k3_thin < 0.056, f"{20*np.log10(k3_thin):.1f} dB")
    check("3W on a 1.5 mm 2-layer board is far worse (> 10 dB more NEXT than on 7628)",
          20 * np.log10(k3_thick / k3_thin) > 10, f"{20*np.log10(k3_thick):.1f} dB")


def part4():
    print("4. Clock trace beside a 50-ohm RF trace, 10 mm parallel run, 920 MHz (JLC-7628)")
    h, er = 0.2104e-3, 4.4
    W = 0.36e-3
    for gap in (0.2e-3, 0.5e-3, 1.0e-3, 2.0e-3):
        p = lc_matrices(W, gap, h, 35e-6, er)
        f = 920e6
        L = 0.010
        b = 2 * np.pi * f * np.sqrt(0.5 * (p["ee"] + p["eo"])) / C0
        # weak-coupling backward coupling of a matched pair: |S31| = Kb |1 - exp(-2j beta l)| = 2 Kb |sin beta l|
        s31 = 2 * p["Kb"] * abs(np.sin(b * L))
        print(f"   gap {gap*1e3:.1f} mm (centre {(gap+W)*1e3:.2f} mm): Kb {20*np.log10(p['Kb']):6.1f} dB; "
              f"backward coupling at 920 MHz over 10 mm = {20*np.log10(s31):6.1f} dB")
        if gap == 2.0e-3:
            check("2 mm gap, 10 mm run at 920 MHz couples below -50 dB", 20 * np.log10(s31) < -50, f"{20*np.log10(s31):.1f} dB")


if __name__ == "__main__":
    part1(); part2(); part3(); part4()
    print(f"\nSummary: {sum(RES)}/{len(RES)} checks passed")
