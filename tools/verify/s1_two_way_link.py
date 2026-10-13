#!/usr/bin/env python3
"""
s1_two_way_link.py — two-direction (uplink vs downlink) LoRa budget between the rocket and the ground
station, the near-receiver overload distances, and LoRaWAN TXPower index -> conducted dBm.

Used by: kb/15-lora-ism-radios/ground-station-design.md, section
"Link asymmetry and receiver overload near the pad".

Assumptions are listed in ASSUME and printed. Sensitivity S = -174 + NF + 10 log10(BW) + SNR_req
(canonical form, kT0 = -173.98 dBm/Hz). LoRa SNR_req: SF7 -7.5 ... SF12 -20 dB (2.5 dB/SF).
Run: python3 tools/verify/s1_two_way_link.py
"""
import math

C = 299_792_458.0
F = 434.125e6                      # E22 CH 24
ASSUME = {
    "rocket antenna gain (dBi, broadside dipole)": 2.15,
    "rocket feeder loss (dB)": 0.5,
    "GS Yagi gain (dBi)": 12.0,
    "GS feeder loss (dB)": 1.0,
    "GS T/R relay loss in TX (dB)": 0.3,
    "GS system NF with masthead LNA (dB)": 1.8,      # ground-station-design.md cascade
    "rocket receiver NF (dB) (E22 module, estimate)": 6.0,
    "rocket local noise rise (dB) (own electronics, estimate)": 3.0,
    "slant range (km)": 30.0,
    "fade/polarisation margin (dB)": 13.0,
}
checks = []


def check(name, ok):
    checks.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")


def fspl(d_m, f=F):
    return 20 * math.log10(4 * math.pi * d_m * f / C)


def sens(sf, bw=125e3, nf=6.0):
    return -173.98 + nf + 10 * math.log10(bw) + (-7.5 - 2.5 * (sf - 7))


print("=== Assumptions ===")
for k, v in ASSUME.items():
    print(f"  {k}: {v}")

A = ASSUME
d = A["slant range (km)"] * 1e3
L = fspl(d)
print(f"\n  FSPL at {d/1e3:.0f} km, {F/1e6:.3f} MHz = {L:.1f} dB")


def budget(case, p_rocket, p_gs):
    """p_rocket / p_gs: conducted dBm at the module ports."""
    eirp_dn = p_rocket - A["rocket feeder loss (dB)"] + A["rocket antenna gain (dBi, broadside dipole)"]
    eirp_up = p_gs - A["GS T/R relay loss in TX (dB)"] - A["GS feeder loss (dB)"] + A["GS Yagi gain (dBi)"]
    pr_gs = eirp_dn - L + A["GS Yagi gain (dBi)"]                          # LNA at the antenna
    pr_rk = eirp_up - L + A["rocket antenna gain (dBi, broadside dipole)"] - A["rocket feeder loss (dB)"]
    nf_rk = A["rocket receiver NF (dB) (E22 module, estimate)"] + A["rocket local noise rise (dB) (own electronics, estimate)"]
    print(f"\n=== {case} ===")
    print(f"  downlink EIRP {eirp_dn:.1f} dBm (e.r.p. {eirp_dn-2.15:.1f}); uplink EIRP {eirp_up:.1f} dBm (e.r.p. {eirp_up-2.15:.1f})")
    print("   SF   downlink: Pr  sens   margin |  uplink: Pr  sens   margin | asymmetry")
    out = {}
    for sf in [7, 9, 12]:
        s_gs = sens(sf, nf=A["GS system NF with masthead LNA (dB)"])
        s_rk = sens(sf, nf=nf_rk)
        m_dn = pr_gs - s_gs - A["fade/polarisation margin (dB)"]
        m_up = pr_rk - s_rk - A["fade/polarisation margin (dB)"]
        out[sf] = (m_dn, m_up)
        print(f"   {sf:2d}  {pr_gs:7.1f} {s_gs:7.1f} {m_dn:+7.1f}  | {pr_rk:7.1f} {s_rk:7.1f} {m_up:+7.1f}  | {m_dn-m_up:+.1f} dB")
    return out, eirp_dn, eirp_up


# 1. licensed: same module both ends at 33 dBm would put 33-1.3+12 = 43.7 dBm EIRP (≈ 14 W ERP) on the GS
o1, edn, eup = budget("Licensed, E22 33 dBm on the rocket; GS E22 stepped down to 30 dBm (amateur ≤ 10 W ERP)", 33, 30)
check("GS uplink at 30 dBm stays under 10 W ERP (40 dBm)", eup - 2.15 <= 40.0)
check("33 dBm into the GS Yagi would exceed 10 W ERP", 33 - 1.3 + 12 - 2.15 > 40.0)
# 2. licence-exempt: both ends at 10 mW e.r.p. -> equal EIRP, GS must pad its TX by its antenna gain
p_rk = 10 + 2.15 + A["rocket feeder loss (dB)"] - A["rocket antenna gain (dBi, broadside dipole)"]
p_gs = 10 + 2.15 + A["GS T/R relay loss in TX (dB)"] + A["GS feeder loss (dB)"] - A["GS Yagi gain (dBi)"]
print(f"\n  licence-exempt conducted settings: rocket {p_rk:.2f} dBm, GS {p_gs:.2f} dBm (needs a pad: lowest E22 step is 24 dBm)")
o2, edn2, eup2 = budget("Licence-exempt, both ends 10 mW e.r.p. (433.05–434.79 MHz)", p_rk, p_gs)
asym = o2[9][0] - o2[9][1]
expect = (A["GS Yagi gain (dBi)"] - A["rocket antenna gain (dBi, broadside dipole)"] + A["rocket feeder loss (dB)"]) + \
         (A["rocket receiver NF (dB) (E22 module, estimate)"] + A["rocket local noise rise (dB) (own electronics, estimate)"]
          - A["GS system NF with masthead LNA (dB)"])
print(f"  equal-EIRP asymmetry = (G_GS − G_rocket + L_rocket) + (NF_rocket,eff − NF_GS) = {expect:.1f} dB (budget: {asym:.1f} dB)")
check("equal-EIRP asymmetry equals receive-gain + NF difference", abs(asym - expect) < 0.05)

# 3. 'louder node fixes the mesh': raise one node by 10 dB
print("\n=== A louder node fixes only its own transmit direction ===")
base_dn, base_up = o2[9]
print(f"  SF9 licence-exempt: downlink {base_dn:+.1f} dB, uplink {base_up:+.1f} dB → bidirectional (ACK) margin = min = {min(base_dn, base_up):+.1f} dB")
print(f"  rocket +10 dB TX: downlink {base_dn+10:+.1f}, uplink {base_up:+.1f} → min {min(base_dn+10, base_up):+.1f} dB (unchanged)")
check("raising one end's TX does not raise the bidirectional margin when the other direction is weaker",
      min(base_dn + 10, base_up) == min(base_dn, base_up) or base_up < base_dn)

# 4. near-receiver overload
print("\n=== Near-receiver overload: distance at which the receive input reaches a threshold ===")
thresholds = {
    "SX126x IIP3 −5 dBm − 9.6 dB ≈ P1dB (rule of thumb, estimate)": -14.6,
    "EBYTE 'blocking/damage' rating +10 dBm": 10.0,
    "SX126x absolute-max RF input +10 dBm": 10.0,
    "pHEMT masthead LNA CW limit +17 dBm (PSA4-5043+)": 17.0,
    "module with ~15 dB internal LNA: chip P1dB referred to the SMA (estimate)": -14.6 - 15,
}
for txname, eirp in [("2 W rocket, 34.65 dBm EIRP", 33 - 0.5 + 2.15), ("10 mW e.r.p., 12.15 dBm EIRP", 12.15)]:
    print(f"  {txname}, received on a 12 dBi Yagi (free space; at < 2D²/λ these are rough):")
    for nm, th in thresholds.items():
        # Pr = EIRP + G - FSPL(d) = th  ->  d
        Lneed = eirp + 12 - th
        dm = 10 ** (Lneed / 20) * C / (4 * math.pi * F)
        print(f"     {nm:72s}: inside {dm:8.1f} m")
pr1 = 33 - 0.5 + 2.15 + 12 - fspl(1.0)
print(f"  check: 2 W at 1 m into the 12 dBi Yagi → {pr1:.1f} dBm (ground-station page TL;DR says +17 dBm with a 10 dBi Yagi)")
p17 = 33 + 10 - fspl(1.0)
print(f"  same convention as that page (33 dBm EIRP, 10 dBi Yagi, 1 m): {p17:.1f} dBm")
check("ground-station page +17 dBm at 1 m reproduced (33 dBm EIRP, 10 dBi)", abs(p17 - 17.0) < 1.0)

# 5. LoRaWAN TXPower index
print("\n=== LoRaWAN TXPower index → conducted power (RP002-1.0.3) ===")
print("  AS923 / EU868: EIRP = MaxEIRP − 2·n (n = 0…7), default MaxEIRP 16 dBm; US915: conducted = 30 − 2·n dBm (n = 0…14)")
print("   n   AS923 EIRP   conducted with 2.15 dBi   with 0 dBi + 1 dB cable   SG 917–925 LPWAN limit 22.15 dBm EIRP")
for n in range(8):
    eirp = 16 - 2 * n
    print(f"   {n}   {eirp:5.0f} dBm      {eirp-2.15:6.2f} dBm              {eirp+1:6.2f} dBm               "
          f"{'OK' if eirp <= 22.15 else 'over'}")
check("AS923 TXPower 0 (16 dBm EIRP) is under the SG 100 mW e.r.p. limit", 16 <= 22.15)
print("  Max EIRP can be raised by the network (TxParamSetupReq); to use the SG 100 mW e.r.p. the device would need "
      "MaxEIRP 22 dBm and ≤ 1 % duty.")

print(f"\nSummary: {sum(checks)} of {len(checks)} checks pass")
