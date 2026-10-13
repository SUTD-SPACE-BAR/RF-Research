#!/usr/bin/env python3
"""
lora_link_budget.py — LoRa sensitivity model and rocket-telemetry link budgets.

Used by: kb/15-lora-ism-radios/lora-sensitivity-and-link-budget.md,
         kb/15-lora-ism-radios/rocket-telemetry-radio-design.md,
         kb/15-lora-ism-radios/ground-station-design.md

1. Sensitivity model  S = −174 + 10 log10(BW) + NF + SNR_req   [dBm]
   and the noise figure implied by each datasheet sensitivity entry
   (SX1276 Rev 7 HF/LF tables, SX1261/2 Rev 1.2 table) using Semtech's SNR table.
2. EBYTE claims (−147 dBm "at 2.4 kbps") checked against Eb/N0 physics and Shannon.
3. Link budgets for Marcus's modules:
     E22-400T33D (SX1268 + PA/LNA, 33 dBm) at 433.125 MHz
     E220-900T30D (LLCC68 + PA/LNA, 30 dBm) at 923 MHz
   with free-space path loss, antenna gains, cable, polarisation and fade margins, giving
   the maximum line-of-sight range per SF/BW.  Also the Singapore SRD-legal cases
   (10 mW e.r.p. @433; 100 mW e.r.p. @917–925 LPWAN end device) and the near-pad
   received-power (saturation) check.
Assumptions are explicit in the ASSUMPTIONS dict — change them to match your hardware.

Run:  python3 tools/verify/lora_link_budget.py
"""
import math

C = 299_792_458.0
KT0_DBM_HZ = -174.0  # 10log10(k·290 K·1 Hz / 1 mW) = −173.98

SNR_REQ = {5: -2.5, 6: -5.0, 7: -7.5, 8: -10.0, 9: -12.5, 10: -15.0, 11: -17.5, 12: -20.0}
BW = {7.8: 7812.5, 10.4: 10416.7, 15.6: 15625, 20.8: 20833.3, 31.25: 31250, 41.7: 41666.7,
      62.5: 62500, 125: 125000, 250: 250000, 500: 500000}

# Datasheet sensitivity tables [dBm]  (BW_kHz, SF) -> value
SX1276_HF = {(10.4, 6): -131, (10.4, 7): -134, (10.4, 8): -138, (10.4, 11): -146,
             (62.5, 6): -121, (62.5, 7): -126, (62.5, 8): -129, (62.5, 9): -132, (62.5, 10): -135,
             (62.5, 11): -137, (62.5, 12): -139,
             (125, 6): -118, (125, 7): -123, (125, 8): -126, (125, 9): -129, (125, 10): -132,
             (125, 11): -133, (125, 12): -136,
             (250, 6): -115, (250, 7): -120, (250, 8): -123, (250, 9): -125, (250, 10): -128,
             (250, 11): -130, (250, 12): -133,
             (500, 6): -111, (500, 7): -116, (500, 8): -119, (500, 9): -122, (500, 10): -125,
             (500, 11): -128, (500, 12): -130}
SX1276_LF = {(7.8, 12): -148, (7.8, 11): -145, (10.4, 6): -132, (10.4, 7): -136, (10.4, 8): -138,
             (62.5, 6): -123, (62.5, 7): -128, (62.5, 8): -131, (62.5, 9): -134, (62.5, 10): -135,
             (62.5, 11): -137, (62.5, 12): -140,
             (125, 6): -121, (125, 7): -125, (125, 8): -128, (125, 9): -131, (125, 10): -134,
             (125, 11): -136, (125, 12): -137,
             (250, 6): -118, (250, 7): -122, (250, 8): -125, (250, 9): -128, (250, 10): -131,
             (250, 11): -133, (250, 12): -134,
             (500, 6): -112, (500, 7): -118, (500, 8): -121, (500, 9): -124, (500, 10): -127,
             (500, 11): -129, (500, 12): -130}
SX1262 = {(10.4, 7): -134, (10.4, 12): -148, (125, 7): -124, (125, 12): -137,
          (250, 7): -121, (250, 12): -134, (500, 7): -117, (500, 12): -129}

ASSUMPTIONS = dict(
    nf_db=6.0,            # chip-level NF implied by Semtech tables (see section 1)
    impl_margin_db=0.0,   # extra implementation loss on top of Semtech SNR table
    rocket_ant_dbi=0.0,   # dipole/monopole on airframe, typical broadside minus body effects
    rocket_null_db=10.0,  # extra loss if ground station sits in a pattern null (nose-on/tail-on)
    rocket_cable_db=0.5,  # U.FL pigtail + SMA
    gs_ant_dbi_433=10.0,  # ~5-6 element 70 cm Yagi (see 08-antennas/yagi-uda-and-log-periodic)
    gs_ant_dbi_923=12.0,  # ~9-10 element 33 cm Yagi
    gs_cable_db=1.0,      # mast-head LNA assumed; otherwise use coax loss here
    pol_loss_db=3.0,      # linear rocket vs circular ground (or random roll with linear-linear)
    fade_margin_db=10.0,  # multipath/ground-reflection/plume/body-shadowing reserve
)


def sensitivity(sf, bw_hz, nf_db=6.0, impl_db=0.0):
    return KT0_DBM_HZ + 10 * math.log10(bw_hz) + nf_db + SNR_REQ[sf] + impl_db


def fspl_db(d_m, f_hz):
    return 20 * math.log10(4 * math.pi * d_m * f_hz / C)


def range_for_loss(loss_db, f_hz):
    return 10 ** (loss_db / 20) * C / (4 * math.pi * f_hz)


def implied_nf(table):
    out = {}
    for (bwk, sf), s in table.items():
        out[(bwk, sf)] = s - (KT0_DBM_HZ + 10 * math.log10(BW[bwk]) + SNR_REQ[sf])
    return out


def bitrate(sf, bw_hz, cr=1, de=False):
    return (sf - 2 * int(de)) * bw_hz / 2 ** sf * 4 / (4 + cr)


def main():
    a = ASSUMPTIONS
    print("1) Noise figure implied by datasheet sensitivities (S − (−174 + 10logBW + SNR_req)):")
    for name, tab in (("SX1276 HF (868/915, band 1)", SX1276_HF), ("SX1276 LF (433, band 3)", SX1276_LF),
                      ("SX1261/2 boosted", SX1262)):
        nfs = implied_nf(tab)
        vals = list(nfs.values())
        print(f"   {name:30s}: NF mean {sum(vals)/len(vals):5.2f} dB, range {min(vals):5.2f}…{max(vals):5.2f} dB")
        worst = sorted(nfs.items(), key=lambda kv: kv[1])
        print(f"      lowest {worst[0][0]} {worst[0][1]:.1f} dB, highest {worst[-1][0]} {worst[-1][1]:.1f} dB")

    print("\n2) Model sensitivity (NF 6 dB) vs SX1262 datasheet:")
    for (bwk, sf), s in SX1262.items():
        m = sensitivity(sf, BW[bwk], a["nf_db"])
        print(f"   BW{bwk:>5} SF{sf:2d}: model {m:7.1f} dBm, datasheet {s} dBm, diff {m - s:+.1f} dB")

    print("\n3) EBYTE '−147 dBm at 2.4 kbps' check:")
    for rb in (2400, 1758, 2148):
        # best case LoRa Eb/N0 ≈ 5.7 dB (ideal, lora_css_sim.py) → S = −174 + NF + 10log(Rb) + Eb/N0
        s = KT0_DBM_HZ + a["nf_db"] + 10 * math.log10(rb) + 5.7
        ebn0_needed = -147 - (KT0_DBM_HZ + a["nf_db"] + 10 * math.log10(rb))
        print(f"   Rb {rb:5d} b/s: physics-limited S ≈ {s:6.1f} dBm; −147 dBm would need Eb/N0 = "
              f"{ebn0_needed:6.1f} dB (Shannon limit −1.59 dB)")
    print("   E22 (SX1268) best chip setting SF12/BW7.8: "
          f"{sensitivity(12, BW[7.8], a['nf_db']):.1f} dBm at {bitrate(12, BW[7.8], de=True):.0f} b/s")
    print("   E220 (LLCC68) best allowed setting SF9/BW125: "
          f"{sensitivity(9, BW[125], a['nf_db']):.1f} dBm at {bitrate(9, BW[125]):.0f} b/s "
          "(LLCC68 has no SF10-12 at 125 kHz)")

    print("\n4) Rocket link budgets (line of sight, free space) — assumptions:", a)
    cases = [("E22-400T33D @433.125 MHz", 33.0, 433.125e6, a["gs_ant_dbi_433"]),
             ("E220-900T30D @923 MHz", 30.0, 923e6, a["gs_ant_dbi_923"]),
             ("SG-legal 10 mW e.r.p. @433 (12.15 dBm EIRP)", 12.15 - a["rocket_ant_dbi"] + a["rocket_cable_db"],
              433.125e6, a["gs_ant_dbi_433"]),
             ("SG-legal 100 mW e.r.p. @923 (22.15 dBm EIRP)", 22.15 - a["rocket_ant_dbi"] + a["rocket_cable_db"],
              923e6, a["gs_ant_dbi_923"])]
    for name, ptx, f, g_gs in cases:
        eirp = ptx - a["rocket_cable_db"] + a["rocket_ant_dbi"]
        print(f"\n   {name}: EIRP {eirp:.1f} dBm, ground antenna {g_gs} dBi")
        print("     BW   SF  Rb[b/s]  Sens[dBm]  MAPL[dB]  range@0 margin  range with pol+fade  +null")
        for bwk in (125, 250, 500):
            for sf in (7, 8, 9, 10, 11, 12):
                if "E220" in name and ((bwk == 125 and sf > 9) or (bwk == 250 and sf > 10) or (bwk == 500 and sf > 11)):
                    continue
                bw = BW[bwk]
                s = sensitivity(sf, bw, a["nf_db"], a["impl_margin_db"])
                mapl = eirp + g_gs - a["gs_cable_db"] - s
                r0 = range_for_loss(mapl, f)
                r1 = range_for_loss(mapl - a["pol_loss_db"] - a["fade_margin_db"], f)
                r2 = range_for_loss(mapl - a["pol_loss_db"] - a["fade_margin_db"] - a["rocket_null_db"], f)
                de = (2 ** sf / bw) >= 16.38e-3
                print(f"    {bwk:4} {sf:3d} {bitrate(sf, bw, de=de):8.0f}  {s:8.1f}  {mapl:8.1f}  "
                      f"{r0/1e3:8.0f} km   {r1/1e3:8.1f} km          {r2/1e3:6.1f} km")

    print("\n5) Near-pad received power (EIRP 33 dBm @433 MHz, 10 dBi Yagi):")
    for d in (1, 3, 10, 30, 100, 300, 1000):
        prx = 33 - a["rocket_cable_db"] + a["rocket_ant_dbi"] + a["gs_ant_dbi_433"] - fspl_db(d, 433.125e6)
        note = "  <-- above EBYTE 10 dBm 'blocking/damage' rating" if prx > 10 else ""
        note = note or ("  <-- strong: expect RX compression/AGC limits" if prx > -20 else "")
        print(f"   d = {d:5d} m: FSPL {fspl_db(d, 433.125e6):5.1f} dB, Prx ≈ {prx:6.1f} dBm{note}")
    print("   (far-field formula is optimistic below ~λ = 0.7 m; still indicates the risk)")

    print("\n6) Landed rocket (antenna near ground): plane-earth (two-ray) loss vs free space")
    print("   PL_2ray ≈ 40 log10 d − 20 log10(h_t h_r)  valid beyond d_c = 4 h_t h_r / λ")
    for f, name in ((433.125e6, "433"), (923e6, "923")):
        lam = C / f
        for ht, hr in ((0.2, 2.0), (0.2, 6.0), (1.0, 6.0)):
            dc = 4 * ht * hr / lam
            row = []
            for d in (1000, 3000, 5000, 10000):
                pl2 = 40 * math.log10(d) - 20 * math.log10(ht * hr)
                pl = max(pl2, fspl_db(d, f))
                row.append(f"{d/1e3:4.0f} km: {pl:5.1f} dB (FS {fspl_db(d, f):5.1f})")
            print(f"   {name} MHz h_t={ht} m h_r={hr} m (d_c={dc:5.1f} m): " + "; ".join(row))
    # max range for landed rocket with E22 SF9/BW125 after pol+fade margins
    for ht, hr in ((0.2, 2.0), (0.2, 6.0)):
        mapl = 32.5 + a["gs_ant_dbi_433"] - a["gs_cable_db"] - sensitivity(9, BW[125]) - a["pol_loss_db"] - a["fade_margin_db"]
        d = 10 ** ((mapl + 20 * math.log10(ht * hr)) / 40)
        print(f"   E22 SF9/BW125, margins applied (MAPL {mapl:.1f} dB): landed range ≈ {d/1e3:.1f} km "
              f"for h_t={ht} m, h_r={hr} m  (two-ray, flat ground, no obstacles)")
    print("   Radio horizon (4/3 earth): d ≈ 4.12(√h_t + √h_r) km, h in m")
    for ht in (100, 1000, 3000, 10000, 30000):
        print(f"     rocket at {ht:6d} m, station mast 2 m: {4.12*(math.sqrt(ht)+math.sqrt(2)):6.0f} km")

    print("\n7) What SF buys you: +2.5 dB per SF step (Semtech) = ×1.33 range in free space;")
    for step in (2.5, 5, 7.5, 10, 12.5):
        print(f"   +{step:4.1f} dB -> range ×{10**(step/20):.2f}")


if __name__ == "__main__":
    main()
