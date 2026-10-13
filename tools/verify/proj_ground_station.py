#!/usr/bin/env python3
"""
proj_ground_station.py -- design calculations for kb/20-projects-recipes/ground-station-tracking-yagi.md

 1. DL6WU Yagis (433 MHz 6-el and 11-el, 868/905 MHz 11-el) generated with the DL6WU algorithm in
    tools/verify/ant_yagi.py and evaluated with its thin-wire MoM (gain, F/B, beamwidths, Zin).
    (~1-2 min; set FAST=1 in the environment to use cached values printed by a previous run.)
 2. Crossed-Yagi CP harness: two 50-ohm Yagis combined through lambda/4 75-ohm transformers, one
    branch delayed by a lambda/4 50-ohm line. ABCD analysis over the band: input match, phase and
    amplitude balance, axial ratio. Axial-ratio sensitivity to phase/amplitude error.
 3. Feeder: coax loss fits (kb/03) at 433/868/905 MHz for several cables/lengths; cascade NF with
    LNA at the mast vs at the receiver; bias-tee DC drop.
 4. Blocking: LNA and module input levels from the rocket on the pad, a handset nearby, a 2 W
    transmitter of another team; LNA P1dB/IIP3 check.
 5. Tracking: az/el of the modelled 10 km flight (proj_lora_link trajectory) from a 5 km cross-range
    station; pointing loss for (a) fixed pointing, (b) GNSS-driven hand/tablet pointing with latency
    and human error, (c) Yaesu-G-5500-class rotator slew limits.
 6. Diversity: packet-loss combination with correlated losses.
 7. SDR recording data rates and storage.

Run: python3 tools/verify/proj_ground_station.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
from rfcalc.noise import Stage, cascade  # noqa: E402

C0 = 299_792_458.0

COAX = {"LMR-400": (0.403, 0.00082), "LMR-240": (0.796, 0.00109), "LMR-195": (1.169, 0.00157),
        "RG-58": (1.123, 0.0123), "RG-174": (2.63, 0.0220)}   # dB/100 m, f in MHz (kb/03 coax page)


def coax_db(kind, f_mhz, length_m):
    k1, k2 = COAX[kind]
    return (k1 * math.sqrt(f_mhz) + k2 * f_mhz) * length_m / 100.0


# ----------------------------------------------------------------------------- 1. Yagis
CACHED = {  # from a full run (MoM), used when FAST=1
    (433e6, 0.9): dict(n=6, boom=0.637, D=11.19, est=11.07, FB=13.3, Z=73.4, bwe=49.6, bwh=60.8),
    (433e6, 2.3): dict(n=11, boom=1.724, D=14.20, est=14.44, FB=16.3, Z=52.2, bwe=36.4, bwh=39.8),
    (868e6, 2.3): dict(n=11, boom=0.860, D=14.25, est=14.44, FB=16.6, Z=50.4, bwe=36.2, bwh=39.6),
    (905e6, 2.3): dict(n=11, boom=0.825, D=14.26, est=14.44, FB=16.6, Z=50.2, bwe=36.2, bwh=39.4),
    (868.125e6, 0.9): dict(n=6, boom=0.318, D=11.21, est=11.07, FB=13.1, Z=80.5, bwe=49.2, bwh=60.4),
    (905e6, 0.9): dict(n=6, boom=0.305, D=11.21, est=11.07, FB=13.0, Z=82.7, bwe=49.2, bwh=60.2),
}


def yagis(fast=False):
    out = {}
    designs = [(433e6, 6e-3, 0.9), (433e6, 6e-3, 2.3), (868e6, 4e-3, 2.3), (905e6, 4e-3, 2.3),
               (868.125e6, 4e-3, 0.9), (905e6, 4e-3, 0.9)]
    if not fast:
        import ant_yagi as y
    for f, dia, BL in designs:
        lam = C0 / f
        if fast:
            out[(f, BL)] = CACHED[(f, BL)]
            continue
        des = y.dl6wu_design(BL, dia / lam, dia / lam)
        L = [des["refl"], 0.47] + list(des["dirs"])
        Lm = [l * lam for l in L]
        pm = des["pos"] * lam
        r = y.evaluate_yagi(Lm, pm, dia / 2, f)
        out[(f, BL)] = dict(n=2 + des["ndir"], boom=des["boom"] * lam, D=10 * np.log10(r["D"]),
                            est=des["G_dBd"] + 2.15, FB=r["FB"], Z=r["Zin"].real, bwe=r["bw_plane_elem"],
                            bwh=r["bw_plane_perp"], lengths_mm=[x * 1e3 for x in Lm[:1]] + [r["Lde"] * 1e3] +
                            [x * 1e3 for x in Lm[2:]], pos_mm=list(pm * 1e3), dia=dia)
    return out


# ----------------------------------------------------------------------------- 2. CP harness
def abcd_line(z0, beta_l):
    c, s = np.cos(beta_l), np.sin(beta_l)
    return np.array([[c, 1j * z0 * s], [1j * s / z0, c]])


def branch_voltage_and_zin(chain, zl):
    """chain: list of (z0, beta_l) from junction to load. Returns Zin at the junction and V_load/V_in."""
    M = np.eye(2, dtype=complex)
    for z0, bl in chain:
        M = M @ abcd_line(z0, bl)
    A, B, Cc, D = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    zin = (A * zl + B) / (Cc * zl + D)
    vin = 1.0
    iin = vin / zin
    # solve load voltage: [vin; iin] = M [vl; il], il = vl/zl
    vl = vin / (A + B / zl)
    return zin, vl


def axial_ratio_db(rho, phi_deg):
    """AR [dB] of E = x + rho*exp(j phi) y."""
    phi = np.radians(phi_deg)
    a = 1 + rho ** 2
    b = np.sqrt(1 + rho ** 4 + 2 * rho ** 2 * np.cos(2 * phi))
    return 10 * np.log10((a + b) / np.maximum(a - b, 1e-15))


def harness(f0, vf75=0.66, vf50=0.66, zyagi=50.0, freqs=None):
    lam0 = C0 / f0
    L75 = vf75 * lam0 / 4
    L50 = vf50 * lam0 / 4
    rows = []
    for f in freqs:
        k = 2 * np.pi * f / C0
        bl75 = k * L75 / vf75
        bl50 = k * L50 / vf50
        zA, vA = branch_voltage_and_zin([(75.0, bl75)], zyagi)
        zB, vB = branch_voltage_and_zin([(75.0, bl75), (50.0, bl50)], zyagi)   # junction->75 xfmr->50 delay->load
        zin = 1 / (1 / zA + 1 / zB)
        g = (zin - 50) / (zin + 50)
        rho = abs(vB) / abs(vA)
        dphi = np.degrees(np.angle(vB / vA))
        rows.append((f, zin, 20 * np.log10(abs(g)), rho, dphi, axial_ratio_db(rho, dphi)))
    return L75, L50, rows


def main():
    fast = os.environ.get("FAST", "0") == "1"
    print("=" * 96)
    print("1) DL6WU Yagis evaluated with the thin-wire MoM of tools/verify/ant_yagi.py" + (" [cached]" if fast else ""))
    Y = yagis(fast)
    for (f, BL), r in Y.items():
        print(f"   {f/1e6:6.1f} MHz, {r['n']:2d} el, boom {r['boom']*1e3:5.0f} mm ({BL} lambda design): "
              f"D = {r['D']:.2f} dBi (DL6WU est {r['est']:.2f}), F/B {r['FB']:.1f} dB, Zin {r['Z']:.1f} ohm, "
              f"HPBW {r['bwe']:.1f} x {r['bwh']:.1f} deg")
        if "lengths_mm" in r:
            print("      lengths (mm): " + ", ".join(f"{x:.1f}" for x in r["lengths_mm"]))
            print("      positions from reflector (mm): " + ", ".join(f"{x:.0f}" for x in r["pos_mm"]))

    print("\n2) Crossed-Yagi CP harness: 2 x lambda/4 75-ohm transformers, branch B + lambda/4 50-ohm delay")
    for f0, band in ((433.5e6, (425e6, 442e6)), (868.125e6, (860e6, 876e6)), (905e6, (890e6, 920e6))):
        fr = np.linspace(band[0], band[1], 9)
        L75, L50, rows = harness(f0, freqs=fr)
        print(f"   f0 = {f0/1e6:.3f} MHz: 75-ohm lambda/4 (VF 0.66) = {L75*1e3:.1f} mm; 50-ohm delay lambda/4 (VF 0.66) = {L50*1e3:.1f} mm")
        for f, zin, rl, rho, dphi, ar in rows:
            print(f"      {f/1e6:7.2f} MHz: Zin {zin.real:6.1f}{zin.imag:+6.1f}j  S11 {rl:6.1f} dB  |VB/VA| {rho:5.3f}  "
                  f"phase {dphi:7.1f} deg  AR {ar:5.2f} dB")
    for zy in (73.4, 80.5):
        L75, L50, rows = harness(433.5e6 if zy < 75 else 868.125e6, zyagi=zy,
                                 freqs=[433.5e6 if zy < 75 else 868.125e6])
        f, zin, rl, rho, dphi, ar = rows[0]
        mm = abs((zy - 50) / (zy + 50))
        print(f"   harness with {zy} ohm Yagis (6-el, plain dipole DE): Zin {zin.real:.1f}{zin.imag:+.1f}j, S11 {rl:.1f} dB "
              f"(single Yagi on 50 ohm: RL {-20*np.log10(mm):.1f} dB, mismatch loss {-10*np.log10(1-mm**2):.2f} dB); "
              f"|VB/VA| {rho:.3f} ({20*np.log10(rho):+.2f} dB), phase {dphi:.1f} deg -> AR {ar:.2f} dB")
    print("   AR sensitivity (dB): amplitude imbalance x phase error")
    for amp_db in (0.0, 0.5, 1.0, 2.0):
        rho = 10 ** (amp_db / 20)
        print("      " + f"{amp_db:3.1f} dB: " + "  ".join(f"{e:2d} deg -> {axial_ratio_db(rho, 90 + e):5.2f}" for e in (0, 5, 10, 20, 30)))
    # loss vs a linear rocket antenna: CP receiver with AR r receiving linear: between -3 dB +/- ripple
    for ar in (1.0, 3.0, 6.0):
        r = 10 ** (ar / 20)
        # polarisation ellipse of receiver with axial ratio r; linear incident at angle psi: PLF = (r^2 cos^2 psi + sin^2 psi)/(1+r^2)
        psi = np.linspace(0, np.pi, 181)
        plf = (r ** 2 * np.cos(psi) ** 2 + np.sin(psi) ** 2) / (1 + r ** 2)
        print(f"   CP receiver AR {ar:.0f} dB vs rotating linear TX: PLF {10*np.log10(plf.max()):5.2f} .. "
              f"{10*np.log10(plf.min()):5.2f} dB (roll ripple {10*np.log10(plf.max()/plf.min()):4.1f} dB)")

    print("\n3) Feeder loss (dB) and cascade NF")
    for f in (433.125, 868.125, 905.0):
        print(f"   {f:7.3f} MHz: " + "  ".join(f"{k} 15 m {coax_db(k, f, 15):4.1f}/30 m {coax_db(k, f, 30):4.1f}"
                                            for k in ("LMR-400", "LMR-240", "RG-58")))
    for f in (433.125, 905.0):
        l240 = coax_db("LMR-240", f, 15)
        l58 = coax_db("RG-58", f, 15)
        cases = {
            "module at the end of 15 m RG-58": [Stage("RG58", -l58), Stage("module", 0, nf=6.0)],
            "module at the end of 15 m LMR-240": [Stage("LMR240", -l240), Stage("module", 0, nf=6.0)],
            "LNA at the receiver end (after 15 m LMR-240)": [Stage("LMR240", -l240), Stage("LNA", 19.8, nf=0.45),
                                                             Stage("SAW", -2.5), Stage("module", 0, nf=6.0)],
            "mast: 0.3 dB jumper, LNA, SAW, 15 m LMR-240, 4-way split 7 dB, module": [
                Stage("jumper", -0.3), Stage("LNA", 19.8, nf=0.45), Stage("SAW", -2.5), Stage("LMR240", -l240),
                Stage("split4", -7.0), Stage("module", 0, nf=6.0)],
            "mast: limiter 0.3 dB, SAW, LNA, 15 m LMR-240, split 7 dB, module": [
                Stage("limiter", -0.3), Stage("SAW", -2.5), Stage("LNA", 19.8, nf=0.45), Stage("LMR240", -l240),
                Stage("split4", -7.0), Stage("module", 0, nf=6.0)],
            "mast: limiter, LNA, SAW, LNA2 (PGA-103+ 1.0 dB/18 dB), 30 m LMR-240, split 7, module": [
                Stage("limiter", -0.3), Stage("LNA", 19.8, nf=0.45), Stage("SAW", -2.5), Stage("LNA2", 18, nf=1.0),
                Stage("LMR240", -coax_db("LMR-240", f, 30)), Stage("split4", -7.0), Stage("module", 0, nf=6.0)],
        }
        print(f"   {f} MHz cascades:")
        for k, st in cases.items():
            c = cascade(st)[-1]
            print(f"      {k:78s} NF {c['NF_cum_dB']:5.2f} dB, gain {c['G_cum_dB']:5.1f} dB")
    # bias tee DC drop: LMR-240 centre 1.42 mm Cu-clad Al? use loop resistance per 100 m (assumed)
    for kind, r100 in (("LMR-240 (loop ~ 3.6 ohm/100 m, est.)", 3.6), ("RG-58 (loop ~ 4.5 ohm/100 m, est.)", 4.5)):
        r = r100 * 0.15
        print(f"   bias-tee drop {kind}: 15 m at 60 mA -> {r*0.06*1e3:.0f} mV")

    print("\n4) Blocking / survival at the LNA input (antenna gain toward the source in brackets)")
    def rx(p_dbm, g_tx, g_rx, f, d):
        return p_dbm + g_tx + g_rx - 20 * math.log10(4 * math.pi * d * f / C0)
    cases = [("own rocket on pad, 33 dBm, Yagi main lobe (10 dBi), 100 m", 33, 2.15, 10, 433e6, 100),
             ("own rocket on pad, 33 dBm, Yagi main lobe, 30 m", 33, 2.15, 10, 433e6, 30),
             ("own rocket on pad, 33 dBm, Yagi side/back lobe (-5 dBi), 30 m", 33, 2.15, -5, 433e6, 30),
             ("other team 2 W at 433.9 MHz, 20 m, main lobe", 33, 2.15, 10, 433.9e6, 20),
             ("handset GSM-900 uplink 33 dBm peak, 2 m, sidelobe 0 dBi (868/905 chain)", 33, 0, 0, 900e6, 2),
             ("handset LTE-900 uplink 23 dBm, 2 m, sidelobe 0 dBi", 23, 0, 0, 900e6, 2),
             ("E220 own secondary on pad 30 dBm, 30 m, main lobe 12 dBi", 30, 2.15, 12, 905e6, 30)]
    for name, p, gt, gr, f, d in cases:
        pin = rx(p, gt, gr, f, d)
        print(f"   {name:72s}: {pin:6.1f} dBm at LNA input; at module after 19.8 dB LNA: {pin+19.8-2.5-2.6-7:6.1f} dBm")
    print("   TQP3M9036 (datasheet via kb/18): OIP3 +36 dBm -> IIP3 ~ +16 dBm; LCSC lists +20 dBm (P1dB out) -> input P1dB ~ +1 dBm")

    print("\n5) Tracking the modelled 10 km flight from station C (5 km cross-range)")
    import proj_lora_link as pl
    tr = pl.tune_apogee(10000.0)
    st = np.array([0.0, 5000.0, 2.0])
    t = tr["t"]
    p = np.stack([tr["x"], np.zeros_like(tr["x"]), tr["z"]], axis=1)
    d = p - st
    east, north, up = d[:, 0], d[:, 1], d[:, 2]
    az = np.degrees(np.arctan2(east, north)) % 360
    el = np.degrees(np.arctan2(up, np.hypot(east, north)))
    asc = (t > 0.5) & (t < tr["t_apo"] - 1.0)
    desc = t > tr["t_apo"] + 1
    daz = np.gradient(np.unwrap(np.radians(az)), t)
    delv = np.gradient(np.radians(el), t)
    print(f"   ascent: az {az[asc].min():.1f}..{az[asc].max():.1f} deg, el {el[asc].min():.1f}..{el[asc].max():.1f} deg; "
          f"max az rate {np.degrees(np.abs(daz[asc])).max():.2f} deg/s, max el rate {np.degrees(np.abs(delv[asc])).max():.2f} deg/s")
    print(f"   descent: az {az[desc].min():.1f}..{az[desc].max():.1f} deg, el {el[desc].min():.1f}..{el[desc].max():.1f} deg; "
          f"max rates az {np.degrees(np.abs(daz[desc])).max():.3f}, el {np.degrees(np.abs(delv[desc])).max():.3f} deg/s")

    def point_loss(daz_deg, del_deg, el_deg, bw_az, bw_el):
        # elliptical Gaussian beam: L = 12[(daz cos el / bw_az)^2 + (del / bw_el)^2] dB
        return 12 * ((daz_deg * np.cos(np.radians(el_deg)) / bw_az) ** 2 + (del_deg / bw_el) ** 2)

    beams = {"3-el (59 x 84 deg)": (84.0, 59.0), "6-el (61 x 50 deg)": (60.8, 49.6), "11-el (40 x 36 deg)": (39.8, 36.4)}
    # (a) fixed pointing optimised for the ascent (minimise the worst loss)
    phase = asc
    for name, (bwa, bwe) in beams.items():
        best = None
        for az0 in np.arange(170, 200.1, 1.0):
            for el0 in np.arange(0, 70.1, 1.0):
                daz_ = ((az[phase] - az0 + 180) % 360) - 180
                L = point_loss(daz_, el[phase] - el0, el[phase], bwa, bwe)
                m = L.max()
                if best is None or m < best[0]:
                    best = (m, az0, el0, np.median(L))
        print(f"   (a) fixed pointing, {name:20s}: best az {best[1]:.0f}, el {best[2]:.0f} deg -> worst ascent loss "
              f"{best[0]:5.1f} dB (median {best[3]:4.1f} dB)")
    # (b) GNSS-driven pointing with latency tau and human error sigma
    rng = np.random.default_rng(1)
    for tau in (1.0, 2.0):
        for sig in (0.0, 5.0, 10.0):
            tt = t[asc]
            az_cmd = np.interp(tt - tau, t, np.unwrap(np.radians(az)))
            el_cmd = np.interp(tt - tau, t, el)
            e_az = np.degrees(np.unwrap(np.radians(az))[asc] - az_cmd) + rng.normal(0, sig, tt.size)
            e_el = el[asc] - el_cmd + rng.normal(0, sig, tt.size)
            row = []
            for name, (bwa, bwe) in beams.items():
                L = point_loss(e_az, e_el, el[asc], bwa, bwe)
                row.append(f"{name.split()[0]}: p50 {np.percentile(L,50):4.1f} p95 {np.percentile(L,95):5.1f} max {L.max():5.1f}")
            print(f"   (b) latency {tau:.0f} s, human error {sig:4.1f} deg rms: " + " | ".join(row))
    # (c) rotator: slew-limited follower of the true direction delayed by 0.5 s
    for name_r, raz, rel in (("Yaesu G-5500-class (6.2 az / 2.7 el deg/s)", 6.2, 2.7), ("fast DIY (20/20 deg/s)", 20.0, 20.0)):
        dt = t[1] - t[0]
        a_ptr, e_ptr = az[0], el[0]   # pre-pointed at the pad
        errs = []
        tgt_az = np.degrees(np.unwrap(np.radians(az)))
        for i in np.where(asc)[0][::20]:
            late = t[i] > 1.0
            j = max(0, i - int(0.5 / dt))
            ga, ge = tgt_az[j], el[j]
            step = 20 * dt
            a_ptr += np.clip(ga - a_ptr, -raz * step, raz * step)
            e_ptr += np.clip(ge - e_ptr, -rel * step, rel * step)
            errs.append((tgt_az[i] - a_ptr, el[i] - e_ptr, el[i], t[i]))
        errs = np.array(errs)
        for bn, (bwa, bwe) in beams.items():
            L = point_loss(errs[:, 0], errs[:, 1], errs[:, 2], bwa, bwe)
            k = np.argmax(np.abs(errs[:, 1]))
            print(f"   (c) {name_r:42s} {bn:20s}: max el error {np.abs(errs[:,1]).max():5.1f} deg at t={errs[k,3]:.1f} s, max loss {L.max():5.1f} dB")

    print("\n6) Diversity (packet level)")
    for p1, p2, rho in ((0.1, 0.1, 0.0), (0.1, 0.1, 0.3), (0.1, 0.1, 0.7), (0.05, 0.2, 0.0), (0.02, 0.02, 0.0)):
        both = p1 * p2 + rho * math.sqrt(p1 * (1 - p1) * p2 * (1 - p2))
        print(f"   p1 {p1:.2f}, p2 {p2:.2f}, correlation {rho:.1f}: combined loss {100*both:5.2f} %")

    print("\n7) SDR recording")
    for fs, bits, lab in ((1.024e6, 8, "RTL-SDR 1.024 MS/s 8-bit"), (2.4e6, 8, "RTL-SDR 2.4 MS/s"),
                          (2.0e6, 16, "Airspy/Pluto 2 MS/s 16-bit"), (10e6, 16, "Pluto 10 MS/s 16-bit")):
        rate = fs * 2 * bits / 8
        print(f"   {lab:28s}: {rate/1e6:5.1f} MB/s -> {rate*1800/1e9:6.1f} GB per 30 min")


if __name__ == "__main__":
    main()
