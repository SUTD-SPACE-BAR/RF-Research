#!/usr/bin/env python3
"""
proj_preflight_rf.py -- automated pre-flight RF checks for kb/20-projects-recipes/design-review-checklists.md

Give it the flight radio configuration (edit CONFIG below or pass a JSON file); it checks, with PASS/FAIL and
the evidence printed (team tenet: tools gate their own output and fail on absent evidence):
  R1 frequency inside the venue band (Singapore SRD bands, amateur 70 cm, IREC SRAD ranges)
  R2 e.r.p./e.i.r.p. vs the venue limit (antenna peak gain and cable loss included)
  R3 channel occupancy of the frame schedule vs 70 % cap and the venue duty limit
  R4 Doppler-rate tolerance of the SF/BW at the vehicle's max radial acceleration (Semtech per-packet rule)
  R5 harmonics (2f..5f) of every onboard transmitter vs GNSS bands tracked by the onboard receiver,
     and the 2nd harmonic of the primary vs the secondary link's channel
  R6 measured evidence present (conducted power, harmonics, installed S11, range test) -- FAIL if missing
Usage: python3 tools/verify/proj_preflight_rf.py [config.json]
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from rfcalc.lora import time_on_air  # noqa: E402

C0 = 299_792_458.0
G0 = 9.80665

VENUES = {
    # name: list of (f_lo, f_hi, limit_dBm, kind 'erp'|'eirp'|'cond', duty, note)
    "SG-exempt": [(433.05e6, 434.79e6, 10.0, "erp", 0.10, "TS SRD 26a"),
                  (866.0e6, 869.0e6, 27.0, "erp", 1.0, "TS SRD 29"),
                  (917.0e6, 925.0e6, 20.0, "erp", 0.01, "TS SRD 30c (LoRa end device)")],
    "SG-amateur": [(430.0e6, 440.0e6, 40.0, "erp", 1.0, "Amateur licence, IMDA consent per frequency")],
    "IREC": [(902.0e6, 909.0e6, 30.0, "cond", 1.0, "SBP Mode A: BW >= 500 kHz, antenna <= 6 dBi"),
             (420.6e6, 438.0e6, 23.0, "cond", 1.0, "70 cm SRAD: <= 200 mW, ham licence, <= 125 kHz")],
}
GNSS = {"GPS L1/E1/B1C": (1563.144, 1587.696), "BeiDou B1I": (1559.052, 1563.144), "GLONASS G1": (1597.551, 1605.886),
        "GPS L2": (1215.0, 1240.0), "GLONASS G2": (1242.4, 1249.1), "E5b/B2I": (1196.91, 1217.37),
        "L5/E5a/B2a": (1166.22, 1186.68), "Galileo E6": (1258.29, 1299.21)}

CONFIG = {
    "venue": "SG-exempt",
    "gnss_tracked": ["GPS L1/E1/B1C", "GLONASS G1", "GPS L2", "GLONASS G2", "Galileo E6"],
    "max_radial_accel_g": 14.0,
    "radios": [
        # Singapore licence-exempt test plan: CH24 434.125 MHz (433.125 MHz +-125 kHz would start at 433.000 MHz,
        # below the 433.05 MHz band edge); 9.5 dBm conducted for 0.5 dB e.r.p. margin; one 48-B frame at 2 Hz (<= 10 % duty)
        {"name": "primary E22", "f_hz": 434.125e6, "p_cond_dbm": 9.5, "cable_db": 0.5, "ant_peak_dbi": 2.15,
         "sf": 7, "bw_hz": 250e3, "schedule": [[48, 2.0]],
         "evidence": {"conducted_power": None, "harmonics": None, "installed_s11": None, "range_test": None}},
        # E220 on CH17 867.125 MHz: 2f of 434.125 MHz is 868.25 MHz, so CH18 (868.125) would collide
        {"name": "secondary E220", "f_hz": 867.125e6, "p_cond_dbm": 24.0, "cable_db": 0.5, "ant_peak_dbi": 2.15,
         "sf": 7, "bw_hz": 250e3, "schedule": [[40, 10.0], [32, 2.0], [16, 1.0]],
         "evidence": {"conducted_power": None, "harmonics": None, "installed_s11": None, "range_test": None}},
    ],
}


def check(ok, tag, msg):
    print(f"   [{'PASS' if ok else 'FAIL'}] {tag}: {msg}")
    return ok


def main():
    cfg = CONFIG
    if len(sys.argv) > 1:
        cfg = json.load(open(sys.argv[1]))
    allok = True
    venue = VENUES[cfg["venue"]]
    print(f"Venue {cfg['venue']}; onboard GNSS bands tracked: {', '.join(cfg['gnss_tracked'])}")
    for r in cfg["radios"]:
        print(f"\n== {r['name']}: {r['f_hz']/1e6:.3f} MHz, {r['p_cond_dbm']} dBm conducted, SF{r['sf']}/{r['bw_hz']/1e3:.0f} kHz")
        band = [b for b in venue if b[0] + r["bw_hz"] / 2 <= r["f_hz"] <= b[1] - r["bw_hz"] / 2]
        allok &= check(bool(band), "R1 band", f"channel edges {(r['f_hz']-r['bw_hz']/2)/1e6:.4f}-{(r['f_hz']+r['bw_hz']/2)/1e6:.4f} MHz "
                       + (f"inside {band[0][0]/1e6:.2f}-{band[0][1]/1e6:.2f} MHz ({band[0][5]})" if band else "NOT inside any venue band"))
        if not band:
            continue
        lo, hi, lim, kind, duty_lim, note = band[0]
        eirp = r["p_cond_dbm"] - r["cable_db"] + r["ant_peak_dbi"]
        val = {"erp": eirp - 2.15, "eirp": eirp, "cond": r["p_cond_dbm"]}[kind]
        allok &= check(val <= lim, "R2 power", f"{kind} {val:.2f} dBm vs limit {lim:.2f} dBm (margin {lim-val:+.2f} dB)")
        occ = sum(rate * time_on_air(pl, r["sf"], r["bw_hz"], cr=1, npre=8, crc=True, explicit=True, chip="sx126x")
                  for pl, rate in r["schedule"])
        allok &= check(occ <= min(0.7, duty_lim), "R3 occupancy", f"{100*occ:.1f} % vs cap {100*min(0.7, duty_lim):.1f} % "
                       f"(70 % practical, venue duty {100*duty_lim:.0f} %)")
        # Doppler-rate (Semtech rule, longest frame in the schedule)
        pl_max = max(pl for pl, _ in r["schedule"])
        t = time_on_air(pl_max, r["sf"], r["bw_hz"], cr=1, npre=8, crc=True, explicit=True, chip="sx126x")
        ldro = (2 ** r["sf"] / r["bw_hz"]) >= 16.38e-3
        lim_hz = r["bw_hz"] / (3 * 2 ** r["sf"]) * (16 if ldro else 1)
        drift = cfg["max_radial_accel_g"] * G0 * r["f_hz"] / C0 * t
        allok &= check(drift <= 0.5 * lim_hz, "R4 Doppler rate", f"drift {drift:.1f} Hz per {pl_max}-B packet at "
                       f"{cfg['max_radial_accel_g']} g vs limit {lim_hz:.1f} Hz (pass needs <= 50 % of limit)")
        hits = []
        for n in (2, 3, 4, 5):
            fh = n * r["f_hz"] / 1e6
            for gname in cfg["gnss_tracked"]:
                glo, ghi = GNSS[gname]
                if glo <= fh <= ghi:
                    hits.append(f"{n}f={fh:.3f} MHz in {gname}")
        allok &= check(not hits, "R5 GNSS harmonics", "; ".join(hits) if hits else "no 2f-5f harmonic in a tracked GNSS band")
        for other in cfg["radios"]:
            if other is r:
                continue
            off = abs(2 * r["f_hz"] - other["f_hz"])
            allok &= check(off > 1.5 * other["bw_hz"], "R5 2f vs other link",
                           f"2f = {2*r['f_hz']/1e6:.3f} MHz is {off/1e6:.3f} MHz from {other['name']} ({other['f_hz']/1e6:.3f} MHz)")
        for k, v in r["evidence"].items():
            allok &= check(v is not None, f"R6 evidence:{k}", v if v is not None else "MISSING - attach the measurement file/plot")
    print(f"\nOVERALL: {'PASS' if allok else 'FAIL (do not fly until every FAIL is closed or waived in writing)'}")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
