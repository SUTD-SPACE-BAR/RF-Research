#!/usr/bin/env python3
"""
prop_link_budget.py — link-budget engine + the worked examples of
kb/09-propagation-link-budget/link-budget-methodology.md

Library use:
    from prop_link_budget import Link
    L = Link(f_hz=433.125e6, d_m=30e3)
    L.add('Tx power', +33); L.add('Tx feeder', -0.5); ... ; L.report(sens_dbm=-128)

Every line item is in dB (gains +, losses -). The receiver side is described either by a
sensitivity (dBm) or by (NF, Ta, B, SNRmin). Both are printed so they can be cross-checked.

Worked examples (numbers quoted on the page):
  A. 433 MHz, EBYTE E22-400T33D (33 dBm) rocket downlink to a ground Yagi at 30 km slant range
  B. 915 MHz, EBYTE E220-900T30D (30 dBm) secondary link, same geometry
  C. Maximum free-space range vs LoRa setting and required margin
  D. G/T and C/N0 form of the same budget (k = -228.6 dBW/K/Hz) — must agree with A
  E. The landed-rocket case (ground-level, plane-earth) — pointer to prop_two_ray.py
"""
import numpy as np
c = 299792458.0
k_dBW = 10*np.log10(1.380649e-23)   # -228.6 dBW/K/Hz

def fspl_db(f_hz, d_m):
    return 20*np.log10(4*np.pi*d_m*f_hz/c)

class Link:
    def __init__(self, f_hz, d_m, title=""):
        self.f = f_hz; self.d = d_m; self.items = []; self.title = title
    def add(self, name, db, note=""):
        self.items.append((name, float(db), note)); return self
    def pr_dbm(self):
        return sum(v for _, v, _ in self.items) - fspl_db(self.f, self.d)
    def report(self, sens_dbm=None, NF=None, Ta=290.0, B=None, snr_min=None, show=True):
        L = fspl_db(self.f, self.d)
        pr = self.pr_dbm()
        if show:
            print(f"\n--- {self.title} ---  f = {self.f/1e6:.3f} MHz, d = {self.d/1e3:.1f} km")
            for n, v, note in self.items:
                print(f"  {n:38s} {v:+8.2f} dB   {note}")
            print(f"  {'Free-space path loss':38s} {-L:+8.2f} dB")
            print(f"  {'=> Received power':38s} {pr:8.2f} dBm")
        out = dict(pr=pr, fspl=L)
        if NF is not None and B is not None:
            Te = 290.0*(10**(NF/10) - 1)
            N = 10*np.log10(1.380649e-23*(Ta+Te)*B/1e-3)
            out['N'] = N; out['snr'] = pr - N
            if show:
                print(f"  Noise: Ta={Ta:.0f} K, NF={NF} dB (Te={Te:.0f} K), B={B/1e3:.1f} kHz -> N = {N:.1f} dBm; SNR = {pr-N:.1f} dB")
            if snr_min is not None:
                s = N + snr_min
                out['sens_calc'] = s; out['margin_calc'] = pr - s
                if show:
                    print(f"  Sensitivity from noise model (SNRmin {snr_min:+.1f} dB) = {s:.1f} dBm -> margin {pr-s:+.1f} dB")
        if sens_dbm is not None:
            out['margin'] = pr - sens_dbm
            if show:
                print(f"  Against stated sensitivity {sens_dbm:.1f} dBm -> link margin {pr-sens_dbm:+.1f} dB")
        return out
    def max_range(self, sens_dbm, margin_db):
        """Free-space distance at which margin equals margin_db."""
        excess = self.pr_dbm() - sens_dbm - margin_db
        return self.d*10**(excess/20)

if __name__ == "__main__":
    # ------------------------------------------------------------------------------------------
    # A. 433 MHz primary downlink
    A = Link(433.125e6, 30e3, "A: 433 MHz E22-400T33D downlink, 30 km slant, ground crossed-Yagi (RHCP)")
    A.add('Tx power (E22-400T33D)', 33.0, 'datasheet 33 +/- 0.5 dBm')
    A.add('Tx feeder + connectors (rocket)', -0.5, '~30 cm RG-316 + 2 SMA')
    A.add('Rocket antenna gain toward GS', 0.0, 'dipole-like; 2.15 dBi peak, 0 dBi used, nulls handled in margin')
    A.add('Polarisation: linear -> circular', -3.0, 'fixed 3 dB for any linear orientation')
    A.add('Ground antenna gain (crossed Yagi)', 11.0, 'assumed 2x7-element, ~11 dBic')
    A.add('Pointing loss', -1.0, 'tracking within ~1/3 beamwidth')
    A.add('Rx feeder (5 m LMR-400)', -0.45, '~9 dB/100 m at 433 MHz')
    A.add('Atmospheric gases', -0.1, 'P.676-11: 0.0025 dB/km at sea level x 30 km (less aloft)')
    Ta_rx = 150.0/10**(0.045) + 290*(1 - 10**(-0.045))   # sky-ish Yagi 150 K seen through the 0.45 dB feeder
    rA = A.report(sens_dbm=-128.0, NF=6.0, Ta=Ta_rx, B=125e3, snr_min=-7.5-2.5)  # 2.4 kb/s ~ SF8 BW125 SNR -10
    print("  NOTE: -128 dBm = physics-based sensitivity at ~2.4 kb/s (see noise_sensitivity.py), NOT the -147 dBm "
          "EBYTE figure.")
    for sens, lab in ((-147.0, "EBYTE datasheet claim"), (-137.0, "SF12/BW125 (SX126x DS)"),
                      (-128.0, "~2.4 kb/s physics"), (-124.0, "SF7/BW125")):
        for m in (10.0, 20.0, 30.0):
            print(f"  max free-space range, sensitivity {sens:6.1f} dBm ({lab:22s}), margin {m:4.0f} dB: "
                  f"{A.max_range(sens, m)/1e3:8.0f} km")
    # fade/impairment allocation
    print("  Impairment allocation example (not in the budget above):")
    for n, v in (("rocket antenna null / body shadowing", 15.0), ("ground-reflection lobing at GS", 6.0),
                 ("plume / flame attenuation (aft view, solid motor; uncertain)", 10.0), ("detuning, temperature, ageing", 2.0)):
        print(f"    {n:60s} {v:5.1f} dB")
    print(f"    remaining margin after 33 dB of impairments at 30 km (2.4 kb/s): {rA['margin'] - 33:+.1f} dB")

    # ------------------------------------------------------------------------------------------
    # B. 915 MHz secondary link
    Bl = Link(915e6, 30e3, "B: 915 MHz E220-900T30D secondary downlink, 30 km slant, ground Yagi (linear)")
    Bl.add('Tx power (E220-900T30D)', 30.0, 'datasheet 29.5-30 dBm')
    Bl.add('Tx feeder + connectors', -0.7)
    Bl.add('Rocket antenna gain toward GS', 0.0)
    Bl.add('Polarisation mismatch (linear-linear, 30 deg)', 20*np.log10(np.cos(np.radians(30))), 'cos^2(30 deg); can be >>20 dB near 90 deg')
    Bl.add('Ground antenna gain (Yagi)', 12.0, 'assumed ~10 elements, 12 dBi')
    Bl.add('Pointing loss', -1.0)
    Bl.add('Rx feeder (5 m LMR-400)', -0.7, '~14 dB/100 m at 915 MHz')
    Bl.add('Atmospheric gases', -0.15, 'P.676-11: 0.005 dB/km x 30 km')
    rB = Bl.report(sens_dbm=-128.0, NF=6.0, Ta=100.0, B=125e3, snr_min=-10.0)
    for sens in (-128.0, -137.0):
        print(f"  max free-space range at 20 dB margin, sensitivity {sens} dBm: {Bl.max_range(sens, 20)/1e3:.0f} km")
    print(f"  433 vs 915 at equal antenna GAINS: FSPL difference = {fspl_db(915e6,30e3)-fspl_db(433.125e6,30e3):.2f} dB, "
          f"Tx power difference = 3 dB")

    # ------------------------------------------------------------------------------------------
    # C. Range vs LoRa setting
    print("\n--- C: free-space range (km) for link A, 20 dB margin, vs LoRa setting (NF 6 dB, SX126x SNR table) ---")
    snr = {7: -7.5, 8: -10, 9: -12.5, 10: -15, 11: -17.5, 12: -20}
    for Bw in (500e3, 250e3, 125e3, 62.5e3):
        row = []
        for SF in range(7, 13):
            s = -173.975 + 10*np.log10(Bw) + 6.0 + snr[SF]
            row.append(A.max_range(s, 20.0)/1e3)
        print(f"  BW {Bw/1e3:6.1f} kHz: " + "  ".join(f"SF{sf}:{r:6.0f}" for sf, r in zip(range(7, 13), row)))

    # ------------------------------------------------------------------------------------------
    # D. G/T - C/N0 form
    print("\n--- D: same link A in G/T - C/N0 form ---")
    eirp_dbW = 33.0 - 0.5 + 0.0 - 30.0
    G_r = 11.0 - 0.45    # gain referred to the LNA/receiver input (after feeder)
    # system temperature referred to the same point: antenna through feeder + receiver Te
    Lf = 10**(0.45/10); Ta = 150.0
    Tin = Ta/Lf + 290*(1-1/Lf)
    Te = 290*(10**0.6 - 1)
    Tsys = Tin + Te
    GT = G_r - 10*np.log10(Tsys)
    C_N0 = eirp_dbW - fspl_db(433.125e6, 30e3) - 3.0 - 1.0 - 0.1 + GT - k_dBW
    print(f"  EIRP = {eirp_dbW:.1f} dBW, G/T = {G_r:.2f} dBi - 10log({Tsys:.0f} K) = {GT:.2f} dB/K")
    print(f"  C/N0 = EIRP - FSPL - losses + G/T - k = {C_N0:.1f} dB-Hz")
    print(f"  From budget A: Pr - N0 = {rA['pr']:.1f} - (10log(k Tsys)+30) = "
          f"{rA['pr'] - (10*np.log10(1.380649e-23*Tsys)+30):.1f} dB-Hz  (must agree)")
    Rb = 2400.0
    print(f"  Eb/N0 at 2.4 kb/s = C/N0 - 10log(Rb) = {C_N0 - 10*np.log10(Rb):.1f} dB (LoRa needs ~6 dB)")

    # ------------------------------------------------------------------------------------------
    print("\n--- E: landed rocket (antenna ~0.1 m above ground) — free space is the WRONG model ---")
    print("  See prop_two_ray.py: at 5 km, 433 MHz, h_rocket 0.1 m (horizontal pol), h_GS 5 m, plane-earth loss")
    hr, hg, d = 0.1, 5.0, 5e3
    Lpe = 40*np.log10(d) - 20*np.log10(hr*hg)
    print(f"  plane-earth L = 40log d - 20log(h1 h2) = {Lpe:.1f} dB vs FSPL {fspl_db(433.125e6, d):.1f} dB "
          f"(extra {Lpe - fspl_db(433.125e6, d):.1f} dB)")
