#!/usr/bin/env python3
# Runtime (W6-F5, 2026-10-14): ~153 s (2.5 min) measured on a 10-core Apple-silicon Mac, run 3 at a time
# under load average 7-70 from other jobs; expect less on an idle machine. It exceeds the 120 s per-script budget
# used by the D7 verify sweep, so give it a >= 15 min timeout and run it with `python3 -u` to see progress.
# Measured run: exit 0, no FAIL lines. Comment only; no code or results changed.
"""
Microstrip / stripline / edge-coupled microstrip calculators + verification for
kb/03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md

Calculators (importable):
  ms_simple(W, h, er)                      Hammerstad (1975) simple closed forms (as in Pozar sec. 3.8)
  ms_hj(W, h, er, t=0)                     Hammerstad & Jensen (1980), incl. strip-thickness correction
  ms_wheeler77(W, h, er, t=0)              Wheeler (1977) Z0 formula (with its thickness correction)
  ms_kj(W, h, er, f, t=0)                  Kirschning & Jansen (1982) eps_eff(f) + Jansen & Kirschning (1983) Z0(f)
  ms_loss(W, h, er, tand, f, t, sigma, rough) conductor (Hammerstad current-distribution + roughness) and dielectric loss
  sl_cohn(W, b, er)                        exact zero-thickness centred stripline (Cohn 1954)
  sl_wheeler78(W, b, t, er)                finite-thickness centred stripline (Wheeler 1978)
  width_for(z_target, fun, ...)            synthesis by root finding
Checks:
  1. H-J vs own FD field solver (tools/verify/tline_fd2d.py) over W/h = 0.1..10, er = 2.2 / 4.4 / 10.
  2. H-J == scikit-rf MLine quasi-static (implementation cross-check); Wheeler-77 and simple formulas vs H-J.
  3. Thickness correction vs FD (t = 35 um on a 0.21 mm prepreg).
  4. K-J dispersion: own implementation == skrf 'kirschningjansen'; compare Kobayashi/Yamashita; size of dispersion
     at 0.433 / 2.45 / 5.8 / 24 GHz.
  5. Stripline: Cohn exact & Wheeler-78 vs FD.
  6. Edge-coupled microstrip (differential): FD even/odd modes vs the IPC-2141 approximation and vs a published
     JLCPCB-stackup design (JITX DRS_100: 0.1722 mm / 0.15 mm on JLC04161H-7628).
  7. JLCPCB 50-ohm widths (2-layer 1.6 mm, JLC04161H-7628/3313/1080/2116), with/without soldermask (FD).
  8. Loss per cm at 433 / 915 / 2450 / 5800 MHz on FR-4.
  9. Higher-order mode / surface-wave limits.

Run: python3 tools/verify/tline_microstrip.py        (about 1-2 minutes)
"""
import os
import sys
import warnings
import numpy as np
from scipy.optimize import brentq
from scipy.special import ellipk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tline_fd2d as fd  # noqa: E402

warnings.filterwarnings("ignore")
ETA0 = 376.730313668
C0 = 299_792_458.0
MU0 = 4e-7 * np.pi
ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


# ============================================================ calculators
def ms_simple(W, h, er):
    u = W / h
    ee = (er + 1) / 2 + (er - 1) / 2 / np.sqrt(1 + 12 / u)
    if u <= 1:
        z = 60 / np.sqrt(ee) * np.log(8 / u + u / 4)
    else:
        z = 120 * np.pi / (np.sqrt(ee) * (u + 1.393 + 0.667 * np.log(u + 1.444)))
    return z, ee


def _hj_z01(u):
    fu = 6 + (2 * np.pi - 6) * np.exp(-(30.666 / u) ** 0.7528)
    return ETA0 / (2 * np.pi) * np.log(fu / u + np.sqrt(1 + (2 / u) ** 2))


def _hj_ee(u, er):
    a = 1 + np.log((u**4 + (u / 52) ** 2) / (u**4 + 0.432)) / 49 + np.log(1 + (u / 18.1) ** 3) / 18.7
    b = 0.564 * ((er - 0.9) / (er + 3)) ** 0.053
    return (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / u) ** (-a * b)


def ms_hj(W, h, er, t=0.0):
    """Hammerstad & Jensen 1980. Returns (Z0, eps_eff) quasi-static."""
    u = W / h
    if t <= 0:
        ee = _hj_ee(u, er)
        return _hj_z01(u) / np.sqrt(ee), ee
    tn = t / h
    du1 = tn / np.pi * np.log(1 + 4 * np.e / (tn / np.tanh(np.sqrt(6.517 * u)) ** 2))
    dur = 0.5 * (1 + 1 / np.cosh(np.sqrt(er - 1))) * du1
    u1, ur = u + du1, u + dur
    ee_r = _hj_ee(ur, er)
    z = _hj_z01(ur) / np.sqrt(ee_r)
    ee = ee_r * (_hj_z01(u1) / _hj_z01(ur)) ** 2
    return z, ee


def ms_wheeler77(W, h, er, t=0.0):
    """Wheeler 1977 synthesis-quality analysis formula (Z0 only; accuracy ~1 %)."""
    if t > 0:
        dW = t / np.pi * np.log(4 * np.e / np.sqrt((t / h) ** 2 + (1 / np.pi / (W / t + 1.1)) ** 2)) * (1 + 1 / er) / 2
        Wp = W + dW
    else:
        Wp = W
    k = (14 + 8 / er) / 11 * 4 * h / Wp
    return ETA0 / (2 * np.pi * np.sqrt(2 * (1 + er))) * np.log(
        1 + 4 * h / Wp * (k + np.sqrt(k**2 + np.pi**2 * (1 + 1 / er) / 2)))


def ms_kj(W, h, er, f, t=0.0):
    """Kirschning-Jansen 1982 eps_eff(f) and Jansen-Kirschning 1983 Z0(f), applied to the H-J quasi-static values."""
    z0s, ee0 = ms_hj(W, h, er, t)
    u = W / h
    fn = f / 1e9 * h * 1e3     # GHz * mm
    P1 = 0.27488 + (0.6315 + 0.525 / (1 + 0.0157 * fn) ** 20) * u - 0.065683 * np.exp(-8.7513 * u)
    P2 = 0.33622 * (1 - np.exp(-0.03442 * er))
    P3 = 0.0363 * np.exp(-4.6 * u) * (1 - np.exp(-(fn / 38.7) ** 4.97))
    P4 = 1 + 2.751 * (1 - np.exp(-(er / 15.916) ** 8))
    P = P1 * P2 * ((0.1844 + P3 * P4) * fn) ** 1.5763
    eef = er - (er - ee0) / (1 + P)
    R1 = 0.03891 * er**1.4
    R2 = 0.267 * u**7.0
    R3 = 4.766 * np.exp(-3.228 * u**0.641)
    R4 = 0.016 + (0.0514 * er) ** 4.524
    R5 = (fn / 28.843) ** 12
    R6 = 22.2 * u**1.92
    R7 = 1.206 - 0.3144 * np.exp(-R1) * (1 - np.exp(-R2))
    R8 = 1 + 1.275 * (1 - np.exp(-0.004625 * R3 * er**1.674 * (fn / 18.365) ** 2.745))
    R9 = 5.086 * R4 * R5 / (0.3838 + 0.386 * R4) * np.exp(-R6) / (1 + 1.2992 * R5) * (er - 1) ** 6 / (1 + 10 * (er - 1) ** 6)
    R10 = 0.00044 * er**2.136 + 0.0184
    R11 = (fn / 19.47) ** 6 / (1 + 0.0962 * (fn / 19.47) ** 6)
    R12 = 1 / (1 + 0.00245 * u**2)
    R13 = 0.9408 * eef**R8 - 0.9603
    R14 = (0.9408 - R9) * ee0**R8 - 0.9603
    R15 = 0.707 * R10 * (fn / 12.3) ** 1.097
    R16 = 1 + 0.0503 * er**2 * R11 * (1 - np.exp(-(u / 15) ** 6))
    R17 = R7 * (1 - 1.1241 * R12 / R16 * np.exp(-0.026 * fn**1.15656 - R15))
    zf = z0s * (R13 / R14) ** R17
    return zf, eef


def ms_loss(W, h, er, tand, f, t=35e-6, sigma=5.8e7, rough=0.0):
    """Returns (alpha_c, alpha_d) in dB/m (Hammerstad-style; as in Qucs / skrf)."""
    z, ee = ms_hj(W, h, er, t)
    Rs = np.sqrt(np.pi * f * MU0 / sigma)
    ds = 1 / np.sqrt(np.pi * f * MU0 * sigma)
    Ki = np.exp(-1.2 * (z / ETA0) ** 0.7)
    Kr = 1 + 2 / np.pi * np.arctan(1.4 * (rough / ds) ** 2)
    ac = Rs / (z * W) * Ki * Kr
    ad = np.pi * er / (er - 1) * (ee - 1) / np.sqrt(ee) * tand * f / C0
    k = 20 / np.log(10)
    return ac * k, ad * k


def sl_cohn(W, b, er):
    k = 1 / np.cosh(np.pi * W / (2 * b))
    kp = np.sqrt(1 - k * k)
    return 30 * np.pi / np.sqrt(er) * ellipk(k * k) / ellipk(kp * kp)


def sl_wheeler78(W, b, t, er):
    x = t / b
    m = 2 / (1 + 2 / 3 * x / (1 - x))
    dW = x / np.pi * (1 - 0.5 * np.log((x / (2 - x)) ** 2 + (0.0796 * x / (W / b + 1.1 * x)) ** m)) * (b - t)
    Wp = W + dW
    q = 4 / np.pi * (b - t) / Wp
    return 30 / np.sqrt(er) * np.log(1 + q * (2 * q + np.sqrt((2 * q) ** 2 + 6.27)))


def ms_synth_pozar(Z0, h, er):
    """Closed-form width synthesis (Pozar eq. 3.197, from Wheeler/Hammerstad), t = 0."""
    A = Z0 / 60 * np.sqrt((er + 1) / 2) + (er - 1) / (er + 1) * (0.23 + 0.11 / er)
    B = 377 * np.pi / (2 * Z0 * np.sqrt(er))
    u1 = 8 * np.exp(A) / (np.exp(2 * A) - 2)
    if u1 < 2:
        return u1 * h
    u2 = 2 / np.pi * (B - 1 - np.log(2 * B - 1) + (er - 1) / (2 * er) * (np.log(B - 1) + 0.39 - 0.61 / er))
    return u2 * h


def width_for(z_target, fun, lo=1e-5, hi=20e-3):
    return brentq(lambda w: fun(w) - z_target, lo, hi, xtol=1e-9)


def fd_ms(W, h, t, er, mask_t=0.0, mask_er=3.8, levels=(1.0, 0.5, 0.25), mask_fill=False):
    """FD field-solver Z0 and eps_eff (Richardson-extrapolated over three meshes)."""
    geo = fd.microstrip_geo(W, h, t, er, mask_t=mask_t, mask_er=mask_er, mask_fill=mask_fill)
    hmin = min(W, h, max(t, 1e-9) * 4 if t > 0 else h) / 40
    hmax = h / 3
    _, ext, _ = fd.refine_study(lambda s: fd.line_params(geo, hmin=hmin * s, hmax=hmax * s)[:2], levels)
    return ext[0], ext[1]


if __name__ == "__main__":
    import skrf as rf

    # ------------------------------------------------ 1. H-J vs FD
    print("1. Hammerstad-Jensen (t = 0) vs own FD solver (Richardson-extrapolated)")
    h = 1.0e-3
    worst_z, worst_e = 0, 0
    for er in [2.2, 4.4, 10.0]:
        for u in [0.1, 0.3, 1.0, 2.0, 5.0, 10.0]:
            zhj, ehj = ms_hj(u * h, h, er)
            zfd, efd = fd_ms(u * h, h, 0.0, er)
            dz, de = (zhj - zfd) / zfd, (ehj - efd) / efd
            worst_z, worst_e = max(worst_z, abs(dz)), max(worst_e, abs(de))
            print(f"   er {er:4.1f} W/h {u:5.1f}: H-J {zhj:7.2f} ohm eeff {ehj:.3f} | FD {zfd:7.2f} ohm eeff {efd:.3f}"
                  f" | dZ {dz*100:+.2f} %  deeff {de*100:+.2f} %")
    check("H-J agrees with independent FD field solution (|dZ| < 1 %, |deeff| < 1 %)", worst_z < 0.01 and worst_e < 0.01,
          f"(worst {worst_z*100:.2f} % / {worst_e*100:.2f} %)")

    # ------------------------------------------------ 2. vs skrf and other formulas
    fq = rf.Frequency(1, 1, 1, unit="MHz")
    dev_skrf, dev_w, dev_s = 0, 0, 0
    for er in [2.2, 4.4, 10.0]:
        for u in [0.1, 0.3, 1.0, 2.0, 5.0, 10.0]:
            m = rf.media.MLine(frequency=fq, w=u * 1e-3, h=1e-3, t=None, ep_r=er, disp="none", diel="frequencyinvariant",
                               rough=0, z0_port=50)
            zhj, ehj = ms_hj(u * 1e-3, 1e-3, er)
            dev_skrf = max(dev_skrf, abs(m.z0[0].real - zhj) / zhj, abs(m.ep_reff_f[0].real - ehj) / ehj)
            dev_w = max(dev_w, abs(ms_wheeler77(u * 1e-3, 1e-3, er) - zhj) / zhj)
            dev_s = max(dev_s, abs(ms_simple(u * 1e-3, 1e-3, er)[0] - zhj) / zhj)
    check("own H-J == scikit-rf MLine (quasi-static, t = 0)", dev_skrf < 1e-6, f"(max rel dev {dev_skrf:.1e})")
    check("Wheeler-77 Z0 within 1.5 % of H-J over W/h 0.1-10, er 2.2-10", dev_w < 0.015, f"(max {dev_w*100:.2f} %)")
    check("simple Hammerstad-75 (Pozar) Z0 within 1.5 % of H-J", dev_s < 0.015, f"(max {dev_s*100:.2f} %)")

    worst_syn = 0
    for er in [2.2, 4.4, 10.0]:
        for z in [25, 50, 75, 100]:
            w = ms_synth_pozar(z, 1e-3, er)
            worst_syn = max(worst_syn, abs(ms_hj(w, 1e-3, er)[0] - z) / z)
    check("Pozar closed-form synthesis gives Z0 within 1.5 % of target (checked with H-J)", worst_syn < 0.015,
          f"(worst {worst_syn*100:.2f} %)")

    # ------------------------------------------------ 3. thickness
    print("3. Strip thickness (JLC04161H-7628: h = 0.2104 mm, er 4.4)")
    hh, err = 0.2104e-3, 4.4
    for W, t in [(0.35e-3, 35e-6), (0.35e-3, 17.5e-6), (0.2e-3, 35e-6)]:
        zt, et = ms_hj(W, hh, err, t)
        z0_, e0_ = ms_hj(W, hh, err, 0)
        zfd, efd = fd_ms(W, hh, t, err)
        print(f"   W {W*1e3:.3f} mm t {t*1e6:.1f} um: H-J(t=0) {z0_:.2f}, H-J(t) {zt:.2f} ohm (eeff {et:.3f}); FD {zfd:.2f} ohm (eeff {efd:.3f})")
        check(f"   H-J thickness correction within 1.5 % of FD (W {W*1e3:.2f} mm, t {t*1e6:.1f} um)", abs(zt - zfd) / zfd < 0.015)

    # ------------------------------------------------ 4. dispersion
    print("4. Dispersion (Kirschning-Jansen) — own vs skrf; vs Kobayashi / Yamashita")
    fr = rf.Frequency(0.1, 40, 400, unit="GHz")
    cases = [(3.0e-3, 1.6e-3, 4.5, "1.6 mm FR-4, W 3.0 mm"), (0.36e-3, 0.2104e-3, 4.4, "JLC7628 0.21 mm, W 0.36 mm, t=0")]
    for W, hh, er, name in cases:
        mk = rf.media.MLine(frequency=fr, w=W, h=hh, t=None, ep_r=er, disp="kirschningjansen", diel="frequencyinvariant",
                            rough=0, z0_port=50)
        zo, eo = ms_kj(W, hh, er, fr.f)
        d1 = np.max(np.abs(mk.ep_reff_f.real - eo) / eo)
        d2 = np.max(np.abs(mk.z0.real - zo) / zo)
        check(f"   own K-J == skrf ({name}) eeff and Z0", d1 < 1e-6 and d2 < 1e-6, f"(dev {d1:.1e}, {d2:.1e})")
        others = {}
        for dm in ["kobayashi", "yamashita"]:
            try:
                mo = rf.media.MLine(frequency=fr, w=W, h=hh, t=None, ep_r=er, disp=dm, diel="frequencyinvariant", rough=0, z0_port=50)
                others[dm] = mo.ep_reff_f.real
            except Exception:
                pass
        for fx in [0.433e9, 2.45e9, 5.8e9, 24e9]:
            i = np.argmin(abs(fr.f - fx))
            e_static = ms_hj(W, hh, er)[1]
            txt = ", ".join(f"{k} {v[i]:.3f}" for k, v in others.items())
            print(f"   {name} @ {fx/1e9:5.2f} GHz: eeff static {e_static:.3f}, K-J {eo[i]:.3f} (+{(eo[i]/e_static-1)*100:.2f} %), "
                  f"Z0 {zo[i]:.2f} ohm; {txt}")
    e1 = ms_kj(3.0e-3, 1.6e-3, 4.5, 2.45e9)[1] / ms_hj(3.0e-3, 1.6e-3, 4.5)[1] - 1
    check("dispersion below 2 % at 2.45 GHz even on 1.6 mm FR-4 (eeff rise)", e1 < 0.02, f"({e1*100:.2f} %)")

    # ------------------------------------------------ 5. stripline
    print("5. Stripline (centred)")
    for W, b, t, er in [(0.3e-3, 0.6e-3, 0.0, 4.4), (0.2e-3, 0.5e-3, 17.5e-6, 4.4), (0.15e-3, 0.4e-3, 35e-6, 4.2)]:
        zc = sl_cohn(W, b, er)
        zw = sl_wheeler78(W, b, t, er) if t > 0 else sl_wheeler78(W, b, 1e-9, er)
        geo = fd.stripline_geo(W, b, t, er)
        _, zfd, _ = fd.refine_study(lambda s: fd.line_params(geo, hmin=min(W, b, 4 * t if t > 0 else b) / 40 * s, hmax=b / 6 * s)[0])
        print(f"   W {W*1e3:.2f} b {b*1e3:.2f} t {t*1e6:.1f} um er {er}: Cohn(t=0) {zc:.2f}, Wheeler-78 {zw:.2f}, FD {zfd:.2f} ohm")
        check(f"   Wheeler-78 within 1.5 % of FD (t = {t*1e6:.1f} um; Wheeler quotes ~1 % accuracy)", abs(zw - zfd) / zfd < 0.015)

    # ------------------------------------------------ 6. edge-coupled microstrip (differential)
    print("6. Edge-coupled microstrip, JLC04161H-7628 (h 0.2104 mm, er 4.4, t 35 um)")
    hh, er, t = 0.2104e-3, 4.4, 35e-6

    def fd_pair(W, s, mask_t=0.0):
        geo = fd.coupled_microstrip_geo(W, s, hh, t, er, mask_t=mask_t)
        hmin = min(W, s) / 30
        res = np.array([fd.coupled_params(geo, hmin=hmin * sc, hmax=hh / 3 * sc) for sc in (1.0, 0.5, 0.25)])
        return [fd._richardson(*res[:, k])[0] for k in range(4)]

    jitx = {}
    for W, s, target in [(0.1722e-3, 0.15e-3, 100), (0.2332e-3, 0.15e-3, 90), (0.2e-3, 0.2e-3, None)]:
        Ze, Zo, ee_e, ee_o = fd_pair(W, s)
        Zem, Zom, _, _ = fd_pair(W, s, mask_t=10e-6)
        z0s = ms_hj(W, hh, er, t)[0]
        ipc = 2 * z0s * (1 - 0.48 * np.exp(-0.96 * s / hh))
        print(f"   W {W*1e3:.4f} s {s*1e3:.3f} mm: FD Zodd {Zo:.2f} Zeven {Ze:.2f} -> Zdiff {2*Zo:.2f} ohm, Zcomm {Ze/2:.2f} ohm;"
              f" eeff odd/even {ee_o:.3f}/{ee_e:.3f}; IPC-2141 approx {ipc:.2f} ohm;"
              f" with gap-filling mask (+10 um, er 3.8): Zdiff {2*Zom:.2f}, Zcomm {Zem/2:.2f} ohm")
        if target:
            jitx[target] = (2 * Zo, 2 * Zom, ipc)
    check("IPC-2141 edge-coupled approximation within 3 % of FD (bare, these geometries)",
          all(abs(v[2] - v[0]) / v[0] < 0.03 for v in jitx.values()))
    check("JITX/JLC DRS_100 and DRS_90 are reproduced (within 3 %) only when soldermask is included",
          abs(jitx[100][1] - 100) < 3 and abs(jitx[90][1] - 90) < 2.7 and jitx[100][0] > 105 and jitx[90][0] > 95,
          f"(bare {jitx[100][0]:.1f}/{jitx[90][0]:.1f}, masked {jitx[100][1]:.1f}/{jitx[90][1]:.1f} ohm)")

    # ------------------------------------------------ 7. JLCPCB 50-ohm widths
    print("7. 50-ohm microstrip widths on JLCPCB stackups (H-J with t; FD with and without soldermask)")
    stacks = [("2-layer 1.6 mm FR-4 (er 4.5)", 1.51e-3, 4.5, 35e-6),     # 1.6 mm board: core ~1.51 mm between 35 um coppers
              ("JLC04161H-7628 (0.2104 mm, er 4.4)", 0.2104e-3, 4.4, 35e-6),
              ("JLC04161H-2116 (0.1164 mm, er 4.16)", 0.1164e-3, 4.16, 35e-6),
              ("JLC04161H-3313 (0.0994 mm, er 4.1)", 0.0994e-3, 4.1, 35e-6),
              ("JLC04161H-1080 (0.0764 mm, er 3.91)", 0.0764e-3, 3.91, 35e-6)]
    jlc_w = {}
    for name, hh, er, t in stacks:
        w_hj = width_for(50, lambda w: ms_hj(w, hh, er, t)[0])
        z_fd, e_fd = fd_ms(w_hj, hh, t, er)
        z_fdm, e_fdm = fd_ms(w_hj, hh, t, er, mask_t=15e-6, mask_er=3.8)
        jlc_w[name] = w_hj
        print(f"   {name}: W(50 ohm, H-J) = {w_hj*1e3:.3f} mm (eeff {ms_hj(w_hj, hh, er, t)[1]:.3f}); FD at that W: {z_fd:.2f} ohm;"
              f" with 15 um soldermask (er 3.8): {z_fdm:.2f} ohm (eeff {e_fdm:.3f})")
    # sensitivity on 2-layer
    for er in [4.3, 4.5, 4.7]:
        print(f"      2-layer 1.51 mm core, er {er}: W50 = {width_for(50, lambda w: ms_hj(w, 1.51e-3, er, 35e-6)[0])*1e3:.3f} mm")
    w7628 = jlc_w["JLC04161H-7628 (0.2104 mm, er 4.4)"]
    zjitx = ms_hj(0.3244e-3, 0.2104e-3, 4.4, 35e-6)[0]
    zjitx_m = fd_ms(0.3244e-3, 0.2104e-3, 35e-6, 4.4, mask_t=15e-6)[0]
    zjitx_f = fd_ms(0.3244e-3, 0.2104e-3, 35e-6, 4.4, mask_t=10e-6, mask_fill=True)[0]
    print(f"      JITX RS_50 width 0.3244 mm on JLC7628: H-J {zjitx:.2f} ohm, FD + 15 um conformal mask {zjitx_m:.2f} ohm,"
          f" FD + gap-filling mask {zjitx_f:.2f} ohm")
    w_fill = None
    zA = fd_ms(0.35e-3, 0.2104e-3, 35e-6, 4.4, mask_t=10e-6, mask_fill=True)[0]
    zB = fd_ms(0.33e-3, 0.2104e-3, 35e-6, 4.4, mask_t=10e-6, mask_fill=True)[0]
    w_fill = 0.35e-3 + (50 - zA) * (0.33e-3 - 0.35e-3) / (zB - zA)
    print(f"      JLC7628 50-ohm width with gap-filling mask model: {w_fill*1e3:.3f} mm")
    check("JLC7628 50-ohm width 0.33-0.40 mm (H-J/FD) — consistent with JITX 0.3244 mm within ~15 %",
          0.33e-3 < w7628 < 0.40e-3 and abs(w7628 - 0.3244e-3) / 0.3244e-3 < 0.2)

    # ------------------------------------------------ 8. loss
    print("8. Loss of 50-ohm microstrip (dB/cm): conductor (smooth / 1 um rms roughness) + dielectric (tand 0.02)")
    for name, hh, er, t in stacks[:2]:
        W = jlc_w[name]
        for f in [433e6, 915e6, 2.45e9, 5.8e9]:
            acs, ad = ms_loss(W, hh, er, 0.02, f, t, rough=0)
            acr, _ = ms_loss(W, hh, er, 0.02, f, t, rough=1.0e-6)
            print(f"   {name:36s} {f/1e9:5.3f} GHz: ac {acs/100:.4f} (rough {acr/100:.4f}) + ad {ad/100:.4f} = {(acr+ad)/100:.4f} dB/cm")
    m = rf.media.MLine(frequency=rf.Frequency(2.45, 2.45, 1, unit="GHz"), w=jlc_w[stacks[0][0]], h=1.51e-3, t=35e-6,
                       ep_r=4.5, tand=0.02, rho=1 / 5.8e7, rough=0, disp="none", diel="frequencyinvariant", z0_port=50)
    a_skrf = m.alpha[0] * 20 / np.log(10)
    acs, ad = ms_loss(jlc_w[stacks[0][0]], 1.51e-3, 4.5, 0.02, 2.45e9, 35e-6, rough=0)
    check("own loss formulas == skrf MLine alpha (2.45 GHz, 1.6 mm FR-4)", abs(a_skrf - (acs + ad)) / (acs + ad) < 0.02,
          f"(skrf {a_skrf/100:.4f} dB/cm vs own {(acs+ad)/100:.4f} dB/cm)")

    # ------------------------------------------------ 9. higher-order modes
    print("9. Higher-order mode / surface-wave onset estimates")
    for name, hh, er, t in stacks[:2]:
        W = jlc_w[name]
        f_te1 = C0 / (4 * hh * np.sqrt(er - 1))
        f_tr = C0 / (np.sqrt(er) * (2 * W + 0.8 * hh))
        print(f"   {name}: TE1 surface-wave cutoff {f_te1/1e9:.1f} GHz; transverse resonance ~{f_tr/1e9:.1f} GHz")

    print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
