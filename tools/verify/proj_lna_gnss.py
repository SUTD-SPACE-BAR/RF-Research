#!/usr/bin/env python3
"""
proj_lna_gnss.py -- design calculations for kb/20-projects-recipes/lna-design-walkthrough.md

GNSS L1 (1575.42 MHz) LNA for a rocket active-antenna board: Infineon BGA524N6 MMIC vs an Avago/Broadcom
ATF-54143 discrete pHEMT stage (the verified design of kb/06-rf-circuits/lna-design.md, example 3).

 1. Bare ATF-54143 (3 V / 60 mA datasheet S-parameters): K, mu, MAG/MSG vs frequency, Gamma_opt, NFmin;
    why the bare device is potentially unstable and what the realised design achieved.
 2. Cascades (Friis + input-referred IIP3/P1dB) for the candidate active-antenna chains:
    SAW->BGA524, BGA524->SAW->BGA524, ATF->SAW->BGA524, limiter variants, with cable to the receiver.
 3. Blockers from the rocket's own transmitters (E22 433 MHz 33 dBm, E220 868/905 MHz 30 dBm):
    LNA-input power vs antenna isolation, SAW rejection; compression and absolute-maximum checks.
 4. Datasheet linearity numbers disagree (BGA524N6 rev 3.0 table vs feature list vs AN420).
 5. Measurement planning: NanoVNA drive level, Y-factor with a 15 dB ENR source and an SDR as the
    second stage (second-stage correction), expected Y and its sensitivity.
 6. Bias/power: current and power per option; bias-tee drop.

Run: python3 tools/verify/proj_lna_gnss.py      (~1 s)
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
from rfckt_atf54143_data import interp_s, interp_noise  # noqa: E402
from rfcalc.noise import Stage, cascade  # noqa: E402

F_L1 = 1575.42e6


def k_mu(S):
    s11, s12, s21, s22 = S[0, 0], S[0, 1], S[1, 0], S[1, 1]
    d = s11 * s22 - s12 * s21
    K = (1 - abs(s11) ** 2 - abs(s22) ** 2 + abs(d) ** 2) / (2 * abs(s12 * s21))
    mu = (1 - abs(s11) ** 2) / (abs(s22 - d * np.conj(s11)) + abs(s12 * s21))
    return K, mu, abs(d)


def mag_db(S):
    K, mu, d = k_mu(S)
    s12, s21 = S[0, 1], S[1, 0]
    if K >= 1:
        return 10 * np.log10(abs(s21) / abs(s12) * (K - np.sqrt(K ** 2 - 1))), "MAG"
    return 10 * np.log10(abs(s21) / abs(s12)), "MSG"


def main():
    print("=" * 92)
    print("1) Bare ATF-54143, 3 V / 60 mA (datasheet S- and noise parameters, tools/verify/rfckt_atf54143_data.py)")
    for f in (0.1e9, 0.5e9, 1.0e9, 1.5e9, F_L1, 2.0e9, 4.0e9, 8.0e9):
        S = interp_s(np.array([f]))[0]
        K, mu, d = k_mu(S)
        g, kind = mag_db(S)
        print(f"   {f/1e9:6.3f} GHz: K {K:5.2f}, mu {mu:5.2f}, |Delta| {d:4.2f}, {kind} {g:5.1f} dB, |S21|^2 {20*np.log10(abs(S[1,0])):5.1f} dB")
    fmin, gopt, rn = interp_noise(np.array([F_L1]))
    print(f"   noise at L1 (interpolated): NFmin {10*np.log10(fmin[0]):.2f} dB, Gamma_opt {abs(gopt[0]):.2f} at "
          f"{np.degrees(np.angle(gopt[0])):.0f} deg, Rn {rn[0]:.1f} ohm; S11* = "
          f"{abs(interp_s(np.array([F_L1]))[0][0,0]):.2f} at {-np.degrees(np.angle(interp_s(np.array([F_L1]))[0][0,0])):.0f} deg "
          f"(noise match != conjugate match)")
    print("   realised design (kb/06 example 3, real 0603/0402 parts Q 40): NF 0.74 dB, G_T 19.2 dB, S11 -9.4 dB, "
          "S22 -15.2 dB, mu >= 1.05 over 0.1-10 GHz; Q 25 -> 0.83 dB, Q 80 -> 0.66 dB")

    print("\n2) Active-antenna cascades (to the receiver input; cable 1 m RG-174 at L1 ~ 1.1 dB, U.FL pigtail 0.3 dB)")
    # stage data: (name, gain, nf, iip3, ip1db)
    SAW = dict(g=-1.6, nf=None)                       # Murata SAFFB1G56KB0F0A listing IL 1.6 dB
    BGA = dict(g=19.6, nf=0.55, iip3=-9.0, ip1=-16.0)  # BGA524N6 rev 3.0 table (see section 4)
    ATF = dict(g=19.2, nf=0.74, iip3=36.0 - 19.2, ip1=20.0 - 19.2 + 1)   # OIP3 +36, P1dB(out) +20 (datasheet class)
    LIM = dict(g=-0.3, nf=None, iip3=27.0)              # anti-parallel Schottky limiter (kb/06 switches page)
    def st(name, d):
        return Stage(name, d["g"], nf=d.get("nf"), iip3=d.get("iip3"), ip1db=d.get("ip1"))
    chains = {
        "A  patch -> SAW -> BGA524 -> 1 m RG-174 -> rx": [st("SAW", SAW), st("BGA", BGA), Stage("RG174", -1.1)],
        "B  patch -> BGA524 -> SAW -> BGA524 -> cable": [st("BGA1", BGA), st("SAW", SAW), st("BGA2", BGA), Stage("RG174", -1.1)],
        "C  patch -> SAW -> BGA524 -> SAW -> BGA524 -> cable": [st("SAW1", SAW), st("BGA1", BGA), st("SAW2", SAW), st("BGA2", BGA), Stage("RG174", -1.1)],
        "D  patch -> ATF-54143 -> SAW -> BGA524 -> cable": [st("ATF", ATF), st("SAW", SAW), st("BGA", BGA), Stage("RG174", -1.1)],
        "E  patch -> limiter -> ATF-54143 -> SAW -> BGA524 -> cable": [st("LIM", LIM), st("ATF", ATF), st("SAW", SAW), st("BGA", BGA), Stage("RG174", -1.1)],
        "F  patch -> SAW -> ATF-54143 -> SAW -> BGA524 -> cable": [st("SAW1", SAW), st("ATF", ATF), st("SAW2", SAW), st("BGA", BGA), Stage("RG174", -1.1)],
    }
    res = {}
    for k, ch in chains.items():
        c = cascade(ch)[-1]
        res[k] = c
        print(f"   {k:58s}: NF {c['NF_cum_dB']:5.2f} dB, gain {c['G_cum_dB']:5.1f} dB, in-band IIP3 {c['IIP3_cum_dBm']:6.1f} dBm, "
              f"IP1dB {c['IP1dB_cum_dBm']:6.1f} dBm")
    print("   ZED-F9P active-antenna spec (via kb/08 gnss-antennas): total gain 17-50 dB (ideal 30-40), NF < 4 dB")
    # C/N0 at the minimum GPS L1 C/A level for a 0 dBic RHCP antenna (-128.5 dBm), antenna gain G, T_ant
    k = 1.380649e-23
    for g_ant, lab in ((-0.2, "FR-4 patch (-0.2 dBic, patch recipe)"), (3.0, "ceramic 25 mm (3 dBic)")):
        for t_ant in (100.0, 290.0):
            row = []
            for kk, c in res.items():
                tsys = t_ant + c["Te_cum_K"]
                cn0 = -128.5 + g_ant - 10 * np.log10(k * tsys / 1e-3)
                row.append(f"{kk.split()[0]} {cn0:4.1f}")
            print(f"   C/N0 [dB-Hz] {lab}, T_ant {t_ant:.0f} K: " + ", ".join(row))

    print("\n3) Own-transmitter blockers at the LNA input (rocket)")
    tx = [("E22 433.125 MHz", 33.0), ("E220 868.125 MHz (SG legal)", 24.0), ("E220 905 MHz (IREC)", 30.0)]
    # out-of-band rejection assumptions (dB): patch mismatch at the blocker freq, SAW rejection
    patch_rej = {"E22 433.125 MHz": 10.0, "E220 868.125 MHz (SG legal)": 6.0, "E220 905 MHz (IREC)": 6.0}
    saw_rej = 35.0                                   # SAFFB1G56 listing "35 dB" (frequency not stated -> assume)
    for iso in (20.0, 30.0, 40.0):
        print(f"   antenna-to-antenna coupling -{iso:.0f} dB:")
        for name, p in tx:
            at_ant = p - iso
            after_patch = at_ant - patch_rej[name]
            print(f"      {name:28s} at GNSS antenna port {at_ant:6.1f} dBm; after patch out-of-band mismatch "
                  f"{after_patch:6.1f} dBm -> LNA-first: {after_patch:6.1f} dBm (BGA abs max 0 dBm, IP1dB -16 dBm); "
                  f"SAW-first: {after_patch-saw_rej:6.1f} dBm")
    print("   rule used: keep a blocker >= 10 dB below the stage's input P1dB for < ~0.5 dB gain compression")
    print("   stage-by-stage for chain D (ATF first) at -30 dB coupling, E22: ATF input -7 dBm vs ATF input P1dB ~ +1.8 dBm "
          "(in-band figure; out-of-band gain of the L1-tuned stage is lower, so this is pessimistic) -> 8.8 dB headroom;"
          " after SAW (-35 dB) and ATF gain (assume +10 dB at 433 MHz) the BGA sees ~ -32 dBm (fine)")
    print("   BGA524N6 IIP3_oob (1712.7/1850 MHz tones): -5 dBm (table) / -4 dBm (feature list)")

    print("\n4) BGA524N6 linearity numbers by source (in-band IP1dB / IIP3 / out-of-band IIP3, dBm)")
    print("   data sheet rev 3.0 (2014) electrical table: -16 / -9 / -5   (2.8 V application, chapter 3)")
    print("   data sheet rev 3.0 feature list (p. 6):      -12 /  - / -4")
    print("   AN420 rev 1.0 (2015), 1.8 V, 0201 parts, input resistor: -12.3 / +3.5 (two -30 dBm tones) / -7.8")
    print("   -> design with the table values; verify IP1dB on the bench (it decides SAW-first vs LNA-first)")

    print("\n5) Measurement planning")
    # NanoVNA output ~ -10 dBm class (H4 below 300 MHz higher, harmonic mode above) -> pad to keep < IP1dB - 10
    for pad in (0, 10, 20, 30):
        pin = -10.0 - pad
        print(f"   NanoVNA drive ~-10 dBm with {pad:2d} dB pad -> {pin:5.1f} dBm at the LNA (BGA524 IP1dB -16): "
              f"{'OK' if pin <= -26 else 'too high'}")
    # Y-factor
    enr = 15.0
    t0 = 290.0
    th = t0 * (1 + 10 ** (enr / 10))
    for nf_dut, g_dut in ((0.55, 19.6), (0.74, 19.2), (0.97, 37.0)):
        te_dut = t0 * (10 ** (nf_dut / 10) - 1)
        for nf2 in (7.0, 25.0):
            te2 = t0 * (10 ** (nf2 / 10) - 1)
            te_tot = te_dut + te2 / 10 ** (g_dut / 10)
            y = (th + te_tot) / (t0 + te_tot)
            nf_meas_uncorr = 10 * math.log10(1 + te_tot / t0)
            # sensitivity: dNF/dY at this point
            y2 = y * 10 ** (0.1 / 10)
            te_y2 = (th - y2 * t0) / (y2 - 1)
            print(f"   DUT NF {nf_dut:.2f} dB G {g_dut:4.1f} dB, 2nd stage NF {nf2:4.1f} dB: Y = {10*math.log10(y):5.2f} dB, "
                  f"uncorrected NF {nf_meas_uncorr:5.2f} dB; a 0.1 dB error in Y -> {10*math.log10(1+te_tot/t0)-10*math.log10(1+te_y2/t0):+.2f} dB in NF")
    print("   ENR 15 dB source: T_hot = %.0f K" % th)

    print("\n6) Power")
    for name, v, i in (("BGA524N6", 2.8, 2.5e-3), ("ATF-54143 (3 V/60 mA via 5 V and Rd+R3)", 5.0, 60e-3),
                       ("ATF-54143 at 3.3 V supply, 3 V/20 mA (lower-current bias, S-params NOT in the table)", 3.3, 20e-3)):
        print(f"   {name:80s}: {v*i*1e3:6.1f} mW")
    # bias-tee drop on 1 m RG-174 (centre 7x0.16 mm Cu-clad steel ~ 0.3-0.4 ohm/m loop, est.)
    print("   bias via 1 m RG-174 (loop ~0.4 ohm, est.): 65 mA -> 26 mV drop (negligible)")


if __name__ == "__main__":
    main()
