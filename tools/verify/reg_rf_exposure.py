#!/usr/bin/env python3
"""
reg_rf_exposure.py — RF exposure (MPE / reference level) safe-distance calculator.

Used by: kb/19-regulations-safety/rf-exposure-safety.md (worked examples, tables)
         kb/19-regulations-safety/lab-safety-esd-high-power.md (bench distances)

Limits transcribed from primary sources (see the KB page for citations):
  ICNIRP (2020) Health Phys 118(5):483-524
      Table 5 (whole body, 30-min average, incident power density S_inc):
          general public: 30-400 MHz 2 W/m^2;  400-2000 MHz f_MHz/200;  2-300 GHz 10 W/m^2
          occupational : 30-400 MHz 10 W/m^2; 400-2000 MHz f_MHz/40;   2-300 GHz 50 W/m^2
      Table 6 (local, 6-min average):
          general public: 30-400 MHz 10 W/m^2; 400-2000 MHz 0.058 f^0.86; 2-6 GHz 40 W/m^2
          occupational : 30-400 MHz 50 W/m^2; 400-2000 MHz 0.29 f^0.86;  2-6 GHz 200 W/m^2
  FCC 47 CFR 1.1310(e)(1) Table 1 (MPE, power density; 1 mW/cm^2 = 10 W/m^2):
          general population (30-min avg): 30-300 MHz 0.2; 300-1500 MHz f/1500; 1.5-100 GHz 1.0 mW/cm^2
          occupational      (6-min avg):  30-300 MHz 1.0; 300-1500 MHz f/300;  1.5-100 GHz 5 mW/cm^2
  FCC 47 CFR 1.1307(b)(3)(i)(C) Table 1 exemption threshold ERP (W), R in m, f in MHz:
          30-300 MHz 3.83 R^2; 300-1500 MHz 0.0128 R^2 f; 1500-100000 MHz 19.2 R^2  (R >= lambda/2pi)

Model (FCC OET Bulletin 65, Ed. 97-01, eqs. 3-4):
    S = k * EIRP * D / (4 pi R^2)
    k = 1 (free space) or 2.56 (worst-case in-phase ground reflection, (1.6)^2),
    D = time-averaging duty factor (fraction of the averaging time the transmitter is on).
    OET 65 notes the far-field equation over-predicts power density in the near field, so using it
    close to a high-gain antenna is conservative.
    Safe distance: R = sqrt(k * EIRP * D / (4 pi S_limit)).

Run:  python3 tools/verify/reg_rf_exposure.py
"""
import math

C0 = 299_792_458.0


def s_limit_icnirp(f_mhz, who="public", kind="wholebody"):
    """ICNIRP 2020 incident power density reference level [W/m^2] (30 MHz - 6 GHz here)."""
    if kind == "wholebody":
        if 30 < f_mhz <= 400:
            return 2.0 if who == "public" else 10.0
        if 400 < f_mhz <= 2000:
            return f_mhz / 200.0 if who == "public" else f_mhz / 40.0
        if 2000 < f_mhz <= 300_000:
            return 10.0 if who == "public" else 50.0
    else:  # local, 6-min
        if 30 < f_mhz <= 400:
            return 10.0 if who == "public" else 50.0
        if 400 < f_mhz <= 2000:
            return (0.058 if who == "public" else 0.29) * f_mhz ** 0.86
        if 2000 < f_mhz <= 6000:
            return 40.0 if who == "public" else 200.0
    raise ValueError("frequency outside implemented range")


def s_limit_fcc(f_mhz, who="public"):
    """FCC 1.1310 Table 1 MPE power density [W/m^2]."""
    if 30 <= f_mhz < 300:
        mw_cm2 = 0.2 if who == "public" else 1.0
    elif 300 <= f_mhz < 1500:
        mw_cm2 = f_mhz / 1500.0 if who == "public" else f_mhz / 300.0
    elif 1500 <= f_mhz <= 100_000:
        mw_cm2 = 1.0 if who == "public" else 5.0
    else:
        raise ValueError("frequency outside implemented range")
    return mw_cm2 * 10.0


def fcc_exempt_erp_w(f_mhz, r_m):
    """FCC 1.1307(b)(3)(i)(C) threshold ERP [W] at separation r_m (valid for r >= lambda/2pi)."""
    if 30 <= f_mhz < 300:
        return 3.83 * r_m ** 2
    if 300 <= f_mhz < 1500:
        return 0.0128 * r_m ** 2 * f_mhz
    if 1500 <= f_mhz <= 100_000:
        return 19.2 * r_m ** 2
    raise ValueError


def power_density(eirp_w, r_m, duty=1.0, k=1.0):
    return k * eirp_w * duty / (4 * math.pi * r_m ** 2)


def safe_distance(eirp_w, s_lim, duty=1.0, k=1.0):
    return math.sqrt(k * eirp_w * duty / (4 * math.pi * s_lim))


def dbm_to_w(dbm):
    return 10 ** ((dbm - 30) / 10)


def self_test():
    # ICNIRP 2020 general public at 433 MHz: 2.165 W/m^2; FCC general population: 433/1500 mW/cm^2 = 2.887 W/m^2
    assert abs(s_limit_icnirp(433) - 2.165) < 1e-9
    assert abs(s_limit_fcc(433) - 2.8867) < 1e-3
    # OET-65 style check: 100 W EIRP at 10 m free space -> 0.0796 W/m^2
    assert abs(power_density(100, 10) - 0.0796) < 1e-4
    # safe distance inverse check
    r = safe_distance(31.6, 2.165)
    assert abs(power_density(31.6, r) - 2.165) < 1e-9
    # FCC exemption at 433 MHz, R = 1 m: 0.0128*433 = 5.54 W ERP
    assert abs(fcc_exempt_erp_w(433, 1.0) - 5.5424) < 1e-4
    print("self-test OK")


def case(label, f_mhz, p_dbm, g_dbi, cable_db=0.5, duties=(1.0, 0.5, 0.2)):
    eirp = dbm_to_w(p_dbm - cable_db + g_dbi)
    erp = eirp / 1.64
    lam = C0 / (f_mhz * 1e6)
    print(f"\n--- {label}: {f_mhz} MHz, {p_dbm} dBm, {g_dbi} dBi, cable {cable_db} dB"
          f" -> EIRP {eirp:.2f} W, ERP {erp:.2f} W, lambda/2pi = {lam/2/math.pi:.3f} m")
    print("   duty | ICNIRP pub WB | ICNIRP occ WB | FCC gen pop | FCC occ   (safe distance, m;"
          " k=1 free space / k=2.56 ground reflection)")
    for d in duties:
        row = []
        for s in (s_limit_icnirp(f_mhz, "public"), s_limit_icnirp(f_mhz, "occ"),
                  s_limit_fcc(f_mhz, "public"), s_limit_fcc(f_mhz, "occ")):
            r1 = safe_distance(eirp, s, d, 1.0)
            r2 = safe_distance(eirp, s, d, 2.56)
            row.append(f"{r1:5.2f}/{r2:5.2f}")
        print(f"   {d:4.0%} | " + " | ".join(row))
    # FCC exemption distance: smallest R with ERP <= threshold
    r_ex = math.sqrt(erp / (0.0128 * f_mhz)) if 300 <= f_mhz < 1500 else float("nan")
    print(f"   FCC 1.1307(b)(3)(i)(C) routine-evaluation exemption needs R >= {max(r_ex, lam/2/math.pi):.2f} m")


def main():
    self_test()
    print("Limits used (W/m^2):")
    for f in (433.0, 868.0, 915.0, 2440.0):
        print(f"  {f:7.1f} MHz: ICNIRP WB public {s_limit_icnirp(f):6.2f}, occ {s_limit_icnirp(f,'occ'):6.2f};"
              f" ICNIRP local 6-min public {s_limit_icnirp(f,'public','local'):6.2f};"
              f" FCC gen {s_limit_fcc(f):6.2f}, occ {s_limit_fcc(f,'occ'):6.2f}")
    case("E22-400T33D + 12 dBi ground Yagi", 433.0, 33, 12.0)
    case("E22-400T33D + rocket dipole", 433.0, 33, 2.15)
    case("E220-900T30D + dipole", 915.0, 30, 2.15)
    case("E220-900T30D + 12 dBi Yagi (uplink)", 915.0, 30, 12.0)
    case("SG-legal 433 MHz SRD (10 mW e.r.p.)", 433.0, 10.5, 2.15)
    # time-averaging example: LoRa telemetry at 1 packet/s with 0.25 s ToA => duty 25 %
    print("\nDuty examples: 32-byte SF7/125 at 1 Hz -> D = 0.072; SF9/125 at 1 Hz -> D = 0.25;"
          " continuous RTK uplink -> D ~ 1")


if __name__ == "__main__":
    main()
