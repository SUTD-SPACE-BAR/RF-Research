#!/usr/bin/env python3
"""Side-by-side LoRa link budgets: Singapore licence-exempt limits vs licensed / full-module power.

Written by W5-E1 (2026-09-29) so that every rocket link budget in the KB can quote both cases.
Regulatory limits (see kb/19-regulations-safety/singapore-imda-rules.md):
  433.05-434.79 MHz  10 mW e.r.p., duty <= 10 %           (IMDA TS SRD 26a)
  866-869 MHz        500 mW e.r.p., no duty stated          (TS SRD 29; band under refarm review)
  917-925 MHz        100 mW e.r.p., duty <= 1 % (LoRa)      (TS SRD 30c)
  430-440 MHz amateur licence: <= 10 W ERP (Rg 5 / Amateur Handbook App. 1), IMDA consent needed
  E220 30 dBm at 917-925 MHz: no exemption -> temporary permit / experimental / localised licence
e.r.p. = e.i.r.p. - 2.15 dB.

Assumptions (same as tools/verify/lora_link_budget.py): rocket antenna 0 dBi, rocket cable 0.5 dB,
ground Yagi 10 dBi (433) / 12 dBi (868/923), ground cable 1 dB, NF 6 dB, Semtech SNR table,
margins: polarisation 3 dB + fade 10 dB + pattern null 10 dB. 32-byte packet ToA from lora_toa.py
(SF7/125: 71.9 ms, SF7/500: 18.0 ms, SF9/125: 246.8 ms).
Run: python3 tools/verify/fix_legal_vs_licensed_link_budgets.py   (self-checks at the end)
"""
import math

C = 299_792_458.0
SNR_REQ = {5: -2.5, 6: -5.0, 7: -7.5, 8: -10.0, 9: -12.5, 10: -15.0, 11: -17.5, 12: -20.0}
TOA_32B = {("SF7", 125): 0.0719, ("SF7", 500): 0.0180, ("SF9", 125): 0.2468}
ROCKET_ANT, ROCKET_CABLE, GS_CABLE, NF = 0.0, 0.5, 1.0, 6.0
MARGIN = 3.0 + 10.0 + 10.0


def sens(sf, bw_hz, nf=NF):
    return -174.0 + 10 * math.log10(bw_hz) + nf + SNR_REQ[sf]


def fspl(d_m, f_hz):
    return 20 * math.log10(4 * math.pi * d_m * f_hz / C)


def range_km(loss_db, f_hz):
    return 10 ** (loss_db / 20) * C / (4 * math.pi * f_hz) / 1e3


# name, f (Hz), EIRP (dBm), ground Yagi gain (dBi), duty limit, legal status
CASES = [
    ("SG exempt 433 MHz: 10 mW e.r.p.", 433.125e6, 10.0 + 2.15, 10.0, 0.10, "licence-exempt (26a)"),
    ("SG amateur 433 MHz: E22-400T33D 33 dBm", 433.125e6, 33.0 - ROCKET_CABLE + ROCKET_ANT, 10.0, 1.0,
     "amateur licence + IMDA consent (<=10 W ERP)"),
    ("SG exempt 868 MHz: 500 mW e.r.p. limit", 868.125e6, 27.0 + 2.15, 12.0, 1.0, "licence-exempt (29)"),
    ("SG exempt 868 MHz: E220 CH18 at 24 dBm", 868.125e6, 24.0 - ROCKET_CABLE + ROCKET_ANT, 12.0, 1.0,
     "licence-exempt (29), +3.5 dB margin with a dipole"),
    ("SG exempt 923 MHz: 100 mW e.r.p., 1 %", 923.125e6, 20.0 + 2.15, 12.0, 0.01, "licence-exempt (30c)"),
    ("E220-900T30D 30 dBm at 923 MHz", 923.125e6, 30.0 - ROCKET_CABLE + ROCKET_ANT, 12.0, 1.0,
     "NOT exempt in SG: temporary permit / experimental licence"),
]


def main():
    print(f"{'case':42s} {'EIRP':>6s} {'MAPL9':>6s} {'mgn30km':>8s} {'R_null':>7s} {'32B SF7/125 rate':>17s}  status")
    rows = {}
    for name, f, eirp, gyagi, duty, status in CASES:
        mapl9 = eirp + gyagi - GS_CABLE - sens(9, 125e3)
        mapl7w = eirp + gyagi - GS_CABLE - sens(7, 500e3)
        m30 = mapl9 - fspl(30e3, f) - MARGIN
        rn = range_km(mapl9 - MARGIN, f)
        rate = min(duty / TOA_32B[("SF7", 125)], 1 / TOA_32B[("SF7", 125)])
        rows[name] = (eirp, mapl9, m30, rn, rate, mapl7w)
        print(f"{name:42s} {eirp:6.2f} {mapl9:6.1f} {m30:8.1f} {rn:7.0f} {rate:14.2f} Hz  {status}")
    print("\nMAPL9 = max allowable path loss at SF9/125 (dB); mgn30km = SF9/125 margin at 30 km LOS after"
          " 23 dB of pol+fade+null;\nR_null = free-space range after those margins (km); rate = duty-limited"
          " max rate for back-to-back 32-byte SF7/125 frames.")

    # self-checks against numbers quoted in the KB
    assert abs(rows["SG exempt 433 MHz: 10 mW e.r.p."][1] - 150.65) < 0.1          # 15/link-budget Ex. 3
    assert abs(rows["SG amateur 433 MHz: E22-400T33D 33 dBm"][1] - 171.0) < 0.1     # 15/link-budget Ex. 1
    assert abs(rows["SG exempt 923 MHz: 100 mW e.r.p., 1 %"][1] - 162.65) < 0.1    # 15/link-budget Ex. 3
    assert abs(rows["SG exempt 923 MHz: 100 mW e.r.p., 1 %"][4] - 0.139) < 0.005   # 1 % -> one frame / 7.2 s
    assert abs(rows["SG exempt 433 MHz: 10 mW e.r.p."][4] - 1.39) < 0.01           # 10 % -> one frame / 0.72 s
    # licensed vs exempt difference at 433 MHz is 20.35 dB of EIRP
    d = rows["SG amateur 433 MHz: E22-400T33D 33 dBm"][0] - rows["SG exempt 433 MHz: 10 mW e.r.p."][0]
    assert abs(d - 20.35) < 0.01
    # the 868 MHz exempt case beats the 923 MHz exempt case by 7 dB EIRP and has no duty limit
    assert rows["SG exempt 868 MHz: 500 mW e.r.p. limit"][0] - rows["SG exempt 923 MHz: 100 mW e.r.p., 1 %"][0] > 6.9
    print("\nALL PASS")


if __name__ == "__main__":
    main()
