#!/usr/bin/env python3
"""
proj_gnss_frontend.py -- design calculations for kb/20-projects-recipes/gnss-front-end-design.md

GNSS front end on a rocket that also carries a 2 W 433 MHz (EBYTE E22-400T33D) and a 0.25-1 W 868/905 MHz
(E220-900T30D) LoRa transmitter. Receivers: u-blox ZED-F9P (L1/L2, needs an active antenna) and MAX-M10S
(L1, internal LNA+SAW, accepts passive antennas).

 1. Antenna-to-antenna coupling vs separation on the airframe (Friis with explicit gain assumptions; a
    near-field caveat below ~lambda/2pi).
 2. Out-of-band blocking budget: MAX-M10S immunity (u-blox figures via kb/21) and an external active-antenna
    LNA (BGA524N6 IP1dB -16 dBm) -> required isolation, with and without a front SAW.
 3. Transmitter wideband noise in L1: desense of the GNSS system temperature vs PA far-out noise floor,
    coupling and the TX-side harmonic/low-pass filter's rejection at 1575 MHz.
 4. In-band harmonic jamming of L2 (E22 CH 0-6) and Galileo E6 (CH 10-22): J/S and effective C/N0
    (Kaplan-Hegarty form 1/CN0_eff = 1/CN0 + (J/S)/(Q Rc), as in tools/verify/gnss_self_interference.py).
 5. ZED-F9P active-antenna gain window (17-50 dB) for cable choices; MAX-M10S gain for LNA-bypass mode.
Run: python3 tools/verify/proj_gnss_frontend.py
"""
import math

import numpy as np

C0 = 299_792_458.0
K_B = 1.380649e-23


def fspl(f, d):
    return 20 * math.log10(4 * math.pi * d * f / C0)


def cn0_eff(cn0_db, js_db, q=1.0, rc=1.023e6):
    """Kaplan-Hegarty effective C/N0 with an interferer of power ratio J/S (spectral factor Q)."""
    cn0 = 10 ** (cn0_db / 10)
    js = 10 ** (js_db / 10)
    return 10 * math.log10(1 / (1 / cn0 + js / (q * rc)))


def main():
    print("=" * 92)
    print("1) Antenna-to-antenna coupling (free-space Friis; G_tx = LoRa antenna gain toward the GNSS antenna,")
    print("   G_rx = GNSS antenna out-of-band gain; both are assumptions until measured)")
    cases = [(433.125e6, "433", 2.15, -10.0), (868.125e6, "868", 2.15, -6.0), (905e6, "905", 2.15, -6.0)]
    for f, lab, gt, gr in cases:
        lam = C0 / f
        row = []
        for d in (0.2, 0.3, 0.5, 1.0, 1.5):
            c = -fspl(f, d) + gt + gr
            row.append(f"{d:.1f} m {c:6.1f} dB")
        print(f"   {lab} MHz (lambda/2pi = {lam/2/math.pi*100:.0f} cm; G_tx {gt} dBi, G_rx {gr} dBi): " + ", ".join(row))
    print("   axial dipole and GNSS patch on the same axis (nose cone + aft bay) see each other near the dipole's"
          " axial null -> extra 10-20 dB isolation (pattern), but coax/airframe currents can undo it: MEASURE (S21)")

    print("\n2) Out-of-band blocking budget")
    tx = [("E22 433 MHz 33 dBm", 33.0, -15.0, 433.125e6), ("E220 868 MHz 24 dBm (SG)", 24.0, -17.0, 868.125e6),
          ("E220 905 MHz 30 dBm (IREC)", 30.0, -17.0, 905e6)]
    # MAX-M10S immunity figures (u-blox, via kb/21): -15 dBm @400-500 MHz, -17 dBm @915 MHz; use -17 for 868 too
    for name, p, imm, f in tx:
        need_m10 = p - imm
        need_bga = p - (-16.0 - 10.0)        # keep >= 10 dB below BGA524N6 IP1dB (-16 dBm)
        need_abs = p - 0.0                   # BGA524N6 abs max 0 dBm
        print(f"   {name:28s}: MAX-M10S RF_IN needs >= {need_m10:4.0f} dB isolation (immunity {imm} dBm); "
              f"active-antenna BGA524N6 needs >= {need_bga:4.0f} dB (no compression) / {need_abs:4.0f} dB (survival)")
    print("   isolation available = coupling (20-40 dB) + GNSS antenna OOB rejection (included in coupling above)"
          " + front SAW (~35 dB listing) -> SAW-first closes every case with >= 20 dB coupling")

    print("\n3) Transmitter wideband noise at 1575 MHz (desense of T_sys)")
    tsys = 150.0     # sky-pointing antenna + LNA (K)
    n_sys = 10 * math.log10(K_B * tsys / 1e-3)
    print(f"   GNSS T_sys {tsys:.0f} K -> noise density {n_sys:.1f} dBm/Hz at the antenna terminals")
    for p, lab in ((33.0, "E22 33 dBm"), (30.0, "E220 30 dBm")):
        for floor in (-130.0, -140.0, -150.0):
            for lpf in (0.0, 40.0, 60.0):
                for coup in (25.0, 40.0):
                    ntx = p + floor - lpf - coup      # dBm/Hz at the GNSS antenna terminals
                    t_int = 10 ** (ntx / 10) * 1e-3 / K_B
                    des = 10 * math.log10((tsys + t_int) / tsys)
                    if lpf in (0.0, 60.0) and coup == 25.0 or (lpf == 40.0 and coup == 40.0):
                        print(f"   {lab}, PA floor {floor:.0f} dBc/Hz at 1575 MHz, TX LPF {lpf:2.0f} dB, coupling {coup:.0f} dB: "
                              f"{ntx:7.1f} dBm/Hz -> C/N0 loss {des:5.1f} dB")
    # requirement: desense <= 1 dB -> interferer density <= n_sys - 5.9 dB
    req = n_sys - 5.87
    for p in (33.0, 30.0):
        for coup in (25.0, 40.0):
            print(f"   for <= 1 dB desense at {p:.0f} dBm and {coup:.0f} dB coupling: (PA floor - LPF) <= "
                  f"{req - p + coup:.1f} dBc/Hz")

    print("\n4) In-band 3rd-harmonic jamming (E22 CH 0-6 -> L2, CH 10-22 -> E6)")
    s = -130.0          # nominal received L2/E6 signal power (dBm), ~ -128.5 L1 C/A min; L2C min -160 dBW = -130 dBm
    for harm_dbm in (-30.0, -50.0, -70.0, -90.0):
        for coup in (25.0, 40.0):
            j = harm_dbm - coup
            js = j - s
            cn = cn0_eff(45.0, js, q=1.0, rc=1.023e6)
            print(f"   3f at the LoRa antenna {harm_dbm:5.0f} dBm (legal limit -30), coupling {coup:.0f} dB: J {j:6.1f} dBm, "
                  f"J/S {js:5.1f} dB -> L2C C/N0 45 -> {cn:5.1f} dB-Hz (CW, Q=1)")
    print("   tracking threshold ~28 dB-Hz: at 25 dB coupling the 3f must stay <= ~-75 dBm (>= 108 dBc below 33 dBm),")
    print("   i.e. 45 dB better than the -30 dBm legal limit -> CH 0-6 are unusable with a ZED-F9P on board; choose CH >= 23")

    print("\n5) Gain windows")
    for cab, loss in (("0.15 m 1.13 mm U.FL", 0.4), ("0.5 m RG-316", 1.2), ("1 m RG-174", 1.1), ("2 m RG-174", 2.2)):
        for g_ant in (17.0, 28.0, 36.0):
            tot = g_ant - loss
            ok = 17 <= tot <= 50
            print(f"   ZED-F9P: active antenna {g_ant:.0f} dB, cable {cab} ({loss} dB): total {tot:5.1f} dB "
                  f"{'in' if ok else 'OUT of'} the 17-50 dB window")
    print("   MAX-M10S with an active antenna: u-blox advises LNA bypass/low-gain mode with >= 10-15 dB external gain")


if __name__ == "__main__":
    main()
