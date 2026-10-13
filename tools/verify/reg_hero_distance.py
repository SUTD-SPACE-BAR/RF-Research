#!/usr/bin/env python3
"""
reg_hero_distance.py — worst-case RF pickup by igniter (e-match) leads and transmitter safe distances.

Used by: kb/19-regulations-safety/lab-safety-esd-high-power.md (HERO / e-match section)

Model (upper bound, far field):
  The igniter circuit is treated as a matched, resonant receiving antenna of gain G_lead
  (1.64 = half-wave dipole, the worst practical case for a lead pair that happens to resonate).
  Effective aperture A_e = G_lead * lambda^2 / (4 pi).  Power delivered to the bridgewire
  P_rx = S * A_e = EIRP * G_lead * lambda^2 / (4 pi R)^2  (Friis).
  Safe distance for a no-fire power P_nf with a margin M_dB (MIL-STD-464C 5.4: 16.5 dB of the
  maximum no-fire stimulus for safety; 6 dB for reliability):
      R = lambda/(4 pi) * sqrt(EIRP * G_lead / (P_nf / 10^(M_dB/10)))
Reference comparison: IME SLP-20 (Dec 2011) bases its tables on a 40 mW no-fire power for
commercial 1-ohm detonators; its UHF (450-470 MHz) column gives 8 ft at 1 W and 14 ft at 3 W
delivered to the antenna, and 11 ft for unknown-mode handheld transmitters <= 2 W.
Rocketry e-matches have different no-fire ratings: use the manufacturer's value.

Run:  python3 tools/verify/reg_hero_distance.py
"""
import math

C0 = 299_792_458.0
FT = 0.3048


def p_rx(eirp_w, f_hz, r_m, g_lead=1.64):
    lam = C0 / f_hz
    return eirp_w * g_lead * lam ** 2 / (4 * math.pi * r_m) ** 2


def safe_r(eirp_w, f_hz, p_nf_w, margin_db=16.5, g_lead=1.64):
    lam = C0 / f_hz
    p_allow = p_nf_w / 10 ** (margin_db / 10)
    return lam / (4 * math.pi) * math.sqrt(eirp_w * g_lead / p_allow)


def self_test():
    # inverse consistency
    r = safe_r(3.3, 433e6, 0.040, 0.0)
    assert abs(p_rx(3.3, 433e6, r) - 0.040) < 1e-12
    # 16.5 dB is the 15 % current ratio quoted in MIL-STD-464C: 20 log10(0.15) = -16.48 dB
    assert abs(20 * math.log10(0.15) + 16.48) < 0.01
    print("self-test OK")


def main():
    self_test()
    print("Worst-case (matched, resonant lead) safe distance, 40 mW no-fire (SLP-20 basis):")
    print(f"{'source':38s} {'EIRP W':>7s} {'0 dB':>8s} {'6 dB':>8s} {'16.5 dB':>9s}  (metres)")
    for label, eirp, f in [("E22-400T33D 2 W, dipole (433 MHz)", 3.3, 433e6),
                           ("E22-400T33D 2 W, 12 dBi Yagi", 31.6, 433e6),
                           ("E220-900T30D 1 W, dipole (915 MHz)", 1.64, 915e6),
                           ("1 W at 460 MHz, 0 dBd (SLP-20 case)", 1.64, 460e6),
                           ("3 W at 460 MHz, 0 dBd (SLP-20 case)", 4.92, 460e6),
                           ("SG SRD 10 mW e.r.p. (433 MHz)", 0.0164, 433e6),
                           ("CATS Vega 100 mW (2.44 GHz)", 0.1, 2.44e9)]:
        r0, r6, r16 = (safe_r(eirp, f, 0.040, m) for m in (0, 6, 16.5))
        print(f"{label:38s} {eirp:7.2f} {r0:8.2f} {r6:8.2f} {r16:9.2f}")
    print(f"\nSLP-20 UHF table for comparison: 1 W -> {8*FT:.2f} m, 3 W -> {14*FT:.2f} m;"
          f" handheld <= 2 W unknown mode -> {11*FT:.2f} m")
    print("Inside the rocket (R ~ 0.05-0.3 m) this far-field bound is not valid: the transmitter is in the"
          " reactive near field of the pyro wiring -> verify by test (continuous TX, monitor bridgewire current).")


if __name__ == "__main__":
    main()
