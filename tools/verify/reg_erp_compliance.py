#!/usr/bin/env python3
"""
reg_erp_compliance.py — radiated-power compliance checker for the Space Bar LoRa radios.

Used by: kb/19-regulations-safety/singapore-imda-rules.md (worked examples, compliance table)
         kb/19-regulations-safety/amateur-radio-licensing.md (10 W ERP ground-station check)
         kb/19-regulations-safety/international-rules-for-competitions.md (FCC/ETSI/ACMA checks)

What it does
  * Converts conducted power + cable loss + antenna gain into e.i.r.p. and e.r.p.
      EIRP[dBm] = P_cond[dBm] - L_cable[dB] + G[dBi]
      ERP[dBm]  = EIRP[dBm] - 2.15            (half-wave dipole = 2.15 dBi; IMDA TS SRD §3)
  * Compares every (module power step x antenna) combination with the limits transcribed in
    LIMITS below (each with its clause and source), prints the margin and the attenuation or
    power step needed to comply.
  * Computes the minimum packet interval for a duty-cycle limit (T_min = ToA / duty).

The LIMITS table is data transcribed from primary sources (see the KB pages for citations):
  SG  IMDA TS SRD Issue 1 Rev 3 (Sep 2023) Table 1 + Telecommunications (Exemption from
      sections 53, 54(1)(b) and 55) Notification, First Schedule item 13 (as at 2026-09-27)
  SG  IMDA Amateur Radio Handbook 5th ed. (21 Nov 2025) Appendix 1 (430-440 MHz: 10 W ERP)
  US  47 CFR 15.247(b)(2),(b)(4) (902-928 MHz FHSS >= 50 ch: 1 W conducted, 6 dBi rule)
      47 CFR 97.313 (amateur: 1.5 kW PEP max; "minimum power necessary")
  EU  ERC Rec 70-03 Annex 1 / EC Decision (EU) 2017/1483 (433.05-434.79 MHz 10 mW e.r.p.;
      869.40-869.65 MHz 500 mW e.r.p.)
  AU  Radiocommunications (Low Interference Potential Devices) Class Licence 2025 (commenced
      1 Oct 2025), Sch. 1 Part 1 Table 1 item 19 (433.05-434.79 MHz, any transmitter, 25 mW EIRP)
      and Part 8 Table 8 item 6 (915-928 MHz digital modulation, 1 W EIRP, cl. 43: peak PSD
      <= 25 mW per 3 kHz); item 1 FHSS 915-928 MHz 1 W EIRP with >= 20 hopping frequencies
Numbers not verified on the page itself are flagged there, not here.

Run:  python3 tools/verify/reg_erp_compliance.py
"""
import math

DIPOLE_DBI = 2.15


def field_to_eirp_w(e_v_per_m, d_m=3.0):
    """Free-space far-field conversion used by FCC Part 15: E = sqrt(30 * EIRP) / d  ->  EIRP = (E d)^2 / 30."""
    return (e_v_per_m * d_m) ** 2 / 30.0


def fcc_15_231_limit_uv(f_mhz, para="e"):
    """47 CFR 15.231 fundamental field-strength limit at 3 m (uV/m), linear interpolation 260-470 MHz."""
    lo, hi = (1500.0, 5000.0) if para == "e" else (3750.0, 12500.0)
    if 260 <= f_mhz <= 470:
        return lo + (f_mhz - 260) / (470 - 260) * (hi - lo)
    raise ValueError("only 260-470 MHz implemented")


def dbm_to_mw(dbm):
    return 10 ** (dbm / 10.0)


def mw_to_dbm(mw):
    return 10 * math.log10(mw)


def eirp_dbm(p_cond_dbm, cable_db, g_dbi):
    return p_cond_dbm - cable_db + g_dbi


def erp_dbm(p_cond_dbm, cable_db, g_dbi):
    return eirp_dbm(p_cond_dbm, cable_db, g_dbi) - DIPOLE_DBI


# (name, lo_MHz, hi_MHz, limit_mW, quantity, duty, clause)
# quantity: "erp" | "eirp" | "cond" (conducted, with antenna-gain rule handled separately)
LIMITS = [
    ("SG TS SRD 26a non-specific SRD", 433.05, 434.79, 10, "erp", 0.10,
     "IMDA TS SRD Table 1 sub-band 26a; Exemption Notif. Sch.1 item 13"),
    ("SG TS SRD 26b non-specific SRD", 433.05, 434.79, 1, "erp", 1.00,
     "IMDA TS SRD Table 1 sub-band 26b"),
    ("SG TS SRD 29 tracking/data acq. incl. LPWAN", 866.0, 869.0, 500, "erp", 1.00,
     "IMDA TS SRD Table 1 sub-band 29 (no duty stated; refarm review fn)"),
    ("SG TS SRD 30b non-LPWAN end device", 917.0, 925.0, 500, "erp", 1.00,
     "IMDA TS SRD Table 1 sub-band 30b (+ mitigation per ECC Rep 181)"),
    ("SG TS SRD 30c LPWAN end device (LoRa)", 917.0, 925.0, 100, "erp", 0.01,
     "IMDA TS SRD Table 1 sub-band 30c (+ mitigation)"),
    ("SG TS SRD 30d non-specific SRD", 917.0, 925.0, 100, "erp", 1.00,
     "IMDA TS SRD Table 1 sub-band 30d (+ mitigation)"),
    ("SG amateur 70 cm (Restricted/General)", 430.0, 440.0, 10000, "erp", 1.00,
     "IMDA Amateur Radio Handbook 5th ed. App. 1 (prior written consent, fn 5)"),
    ("EU 433 non-specific SRD", 433.05, 434.79, 10, "erp", 0.10,
     "ERC Rec 70-03 Annex 1 / EU 2017/1483"),
    ("EU 869.4-869.65 non-specific SRD", 869.40, 869.65, 500, "erp", 0.10,
     "ERC Rec 70-03 Annex 1 / EU 2017/1483"),
    ("AU LIPD 433 any transmitter", 433.05, 434.79, 25, "eirp", 1.00,
     "LIPD Class Licence 2025 Sch.1 Table 1 item 19"),
    ("AU LIPD 915-928 digital modulation", 915.0, 928.0, 1000, "eirp", 1.00,
     "LIPD Class Licence 2025 Sch.1 Table 8 item 6 + cl.43"),
]

# Module power steps from the EBYTE manuals (kb/15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)
MODULES = {
    "E22-400T33D": {"steps_dbm": [33, 30, 27, 24], "f_MHz": 433.125},
    "E220-900T30D": {"steps_dbm": [30, 27, 24, 21], "f_MHz": 920.125},
}

ANTENNAS = {
    "rocket dipole (2.15 dBi)": 2.15,
    "rocket monopole on small airframe (0 dBi, assumed)": 0.0,
    "ground 5 dBi collinear": 5.0,
    "ground 12 dBi Yagi": 12.0,
}


def check(p_dbm, cable_db, g_dbi, limit):
    name, lo, hi, lim_mw, qty, duty, clause = limit
    if qty == "erp":
        val = erp_dbm(p_dbm, cable_db, g_dbi)
    elif qty == "eirp":
        val = eirp_dbm(p_dbm, cable_db, g_dbi)
    else:
        val = p_dbm - cable_db
    lim_dbm = mw_to_dbm(lim_mw)
    return val, lim_dbm, lim_dbm - val


def duty_interval(toa_s, duty):
    """Minimum average packet period [s] for back-to-back packets under a duty limit."""
    return toa_s / duty


def self_test():
    # 2.15 dBi dipole: conducted power equals e.r.p.
    assert abs(erp_dbm(10.0, 0.0, 2.15) - 10.0) < 1e-12
    # 10 mW e.r.p. = 12.15 dBm e.i.r.p.
    assert abs(eirp_dbm(10.0, 0.0, 2.15) - 12.15) < 1e-12
    assert abs(dbm_to_mw(33) - 1995.26) < 0.01
    # 2 W into a 12 dBi Yagi (9.85 dBd) -> 19.3 W e.r.p. (> 10 W amateur limit)
    erp_w = dbm_to_mw(erp_dbm(33, 0, 12)) / 1000
    assert abs(erp_w - 19.3) < 0.1, erp_w
    # 1 % duty, 71.9 ms packet -> 7.19 s interval
    assert abs(duty_interval(0.0719, 0.01) - 7.19) < 1e-9
    # 15.249: 50 mV/m at 3 m -> 0.75 mW EIRP (-1.25 dBm)
    assert abs(field_to_eirp_w(0.050) * 1e3 - 0.75) < 1e-9
    # 15.231(e) at 433.92 MHz: 1500 + (173.92/210)*3500 = 4398.7 uV/m
    assert abs(fcc_15_231_limit_uv(433.92) - 4398.67) < 0.05
    print("self-test OK")


def main():
    self_test()
    cable = 0.5
    for mod, spec in MODULES.items():
        f = spec["f_MHz"]
        print(f"\n=== {mod} at {f} MHz, cable loss {cable} dB ===")
        lims = [l for l in LIMITS if l[1] <= f <= l[2]]
        # also show the band the module could be retuned into
        if mod == "E220-900T30D":
            lims = [l for l in LIMITS if l[1] >= 860 and l[2] <= 930]
        if mod == "E22-400T33D":
            lims = [l for l in LIMITS if 430 <= l[1] <= 435]
        for ant, g in ANTENNAS.items():
            print(f"  antenna: {ant}")
            for p in spec["steps_dbm"]:
                row = []
                for l in lims:
                    val, lim, margin = check(p, cable, g, l)
                    ok = "OK " if margin >= 0 else "OVER"
                    row.append(f"{l[0][:26]:26s} {ok} {margin:+6.1f} dB")
                erp = erp_dbm(p, cable, g)
                print(f"    {p:2d} dBm cond -> ERP {erp:5.1f} dBm ({dbm_to_mw(erp):7.1f} mW)")
                for r in row:
                    print("        " + r)

    print("\n=== Power needed at the module to hit a limit exactly (0.5 dB cable) ===")
    for lim_name, lim_mw, g in [("SG 433 SRD 10 mW e.r.p., dipole", 10, 2.15),
                                ("SG 917-925 LPWAN 100 mW e.r.p., dipole", 100, 2.15),
                                ("SG 866-869 500 mW e.r.p., dipole", 500, 2.15),
                                ("SG amateur 10 W ERP, 12 dBi Yagi", 10000, 12.0),
                                ("SG amateur 10 W ERP, dipole", 10000, 2.15)]:
        p_needed = mw_to_dbm(lim_mw) + DIPOLE_DBI - g + cable
        print(f"  {lim_name:42s}: P_cond <= {p_needed:5.1f} dBm ({dbm_to_mw(p_needed):8.1f} mW)")

    print("\n=== US Part 15 field-strength limits expressed as EIRP (free space, 3 m) ===")
    for label, e in [("15.249 902-928 MHz, 50 mV/m", 0.050),
                     ("15.231(b) 433.92 MHz average", fcc_15_231_limit_uv(433.92, "b") * 1e-6),
                     ("15.231(e) 433.92 MHz (data allowed, <=1 s TX, >=10 s off)", fcc_15_231_limit_uv(433.92, "e") * 1e-6)]:
        w = field_to_eirp_w(e)
        print(f"  {label:58s}: {e*1e6:8.0f} uV/m -> EIRP {mw_to_dbm(w*1e3):6.1f} dBm ({w*1e6:8.1f} uW)")
    # AU LIPD 2025 clause 43: peak PSD <= 25 mW / 3 kHz for digital modulation 915-928 MHz
    for bw in (125e3, 250e3, 500e3):
        p_max = 25.0 * bw / 3e3  # mW, flat-spectrum approximation
        print(f"  AU LIPD cl.43 PSD cap for flat {bw/1e3:.0f} kHz signal: {min(p_max,1000):.0f} mW EIRP"
              f" (PSD-limited {p_max:.0f} mW vs 1 W item cap)")

    print("\n=== Duty-cycle packet intervals (32-byte frames, ToA from lora_toa.py) ===")
    for label, toa in [("SF7/125 32 B", 0.0719), ("SF7/500 32 B", 0.0180),
                       ("SF9/125 32 B", 0.2468), ("SF12/125 32 B", 1.810)]:
        print(f"  {label:14s}: 10 % -> {duty_interval(toa, 0.10):7.2f} s,"
              f" 1 % -> {duty_interval(toa, 0.01):7.2f} s")


if __name__ == "__main__":
    main()
