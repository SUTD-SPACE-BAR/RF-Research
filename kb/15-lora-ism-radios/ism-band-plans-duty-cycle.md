---
title: ISM/SRD band plans, power limits, duty cycle and dwell time for LoRa (433, 868, 915, 923 MHz)
domain: 15-lora-ism-radios
slug: ism-band-plans-duty-cycle
tags: [ism, srd, band-plan, duty-cycle, dwell-time, erp, eirp, imda, singapore, etsi-en-300-220, fcc-15-247, as923, eu868, us915, in865, lorawan-regional-parameters]
prerequisites:
  - lora-phy-css-math.md
  - ../00-math-foundations/decibels-and-log-units.md
related:
  - ../19-regulations-safety/spectrum-allocation-ism-bands.md
  - ../19-regulations-safety/singapore-imda-rules.md
  - ../19-regulations-safety/amateur-radio-licensing.md
  - ../19-regulations-safety/certification-fcc-ce-imda.md
  - lorawan-vs-raw-lora.md
  - lora-sensitivity-and-link-budget.md
  - rocket-telemetry-radio-design.md
level: intro
confidence: medium
last_updated: 2026-10-14
---

# ISM/SRD band plans, power limits, duty cycle and dwell time for LoRa

> **Scope note.** This page gives the engineering numbers (bands, power, duty cycle, dwell) and their timing consequences for LoRa. The **legal interpretation** — which class your device falls into, licences, approvals, penalties — belongs to domain 19 ([Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md), [spectrum allocation](../19-regulations-safety/spectrum-allocation-ism-bands.md)). Nothing here is legal advice.

## Questions this page answers
- Which frequencies and power levels may a LoRa radio use in Singapore?
- Is my 2 W E22-400T33D at 433 MHz or 1 W E220-900T30D at 900 MHz legal in Singapore?
- What are the EU 868 MHz sub-bands and duty-cycle limits (ETSI EN 300 220)?
- What do the US FCC §15.247 rules (hopping, 400 ms dwell, 1 W, 6 dBi) mean for LoRa?
- What is AS923 and why does Singapore use it?
- What is the difference between e.r.p., e.i.r.p. and conducted power?
- How often may I transmit a telemetry packet under a 1 % or 10 % duty cycle?
- Why can't SF11/SF12 at 125 kHz be used in 400 ms-dwell regions?
- Can we use amateur 33 cm (902–928 MHz) LoRa at Spaceport America?
- What are Australia's LIPD limits for LoRa at 433 and 915–928 MHz?
- Which licence lets us run 1–2 W LoRa telemetry in Singapore?

## TL;DR
- **Singapore (IMDA TS SRD Issue 1 Rev 3, Sep 2023 — the latest issue; the 433/866/917 MHz rows are unchanged from the Apr 2023 printing)** [1]:
  - **433.05–434.79 MHz**: ≤ **10 mW e.r.p.** (sub-band 26a, non-specific SRD; "duty cycle ≤ 10 % for bandwidth over entire band" — read by [domain 19](../19-regulations-safety/singapore-imda-rules.md) as a flat 10 %) or ≤ 1 mW e.r.p. (26b, no extra condition). This is the **only** licence-exempt 433 MHz route in Singapore. (433.05–434.79 MHz is an ITU *ISM* band only in Region 1 and the RR 5.280 countries; Singapore is Region 3 and permits it nationally as an SRD band [7][11].)
  - **866–869 MHz**: ≤ **500 mW e.r.p.** for tracking, tracing and data acquisition incl. LPWAN and RFID (29), no duty cycle stated — *under review for re-farming*.
  - **917–925 MHz** (amended from 920–925): RFID ≤ 500 mW e.r.p.; non-LPWAN end devices & LPWAN access points ≤ 500 mW e.r.p. (access points ≤ 10 % duty); **LPWAN end devices (LoRa named as an example) ≤ 100 mW e.r.p., ≤ 1 % duty (30c)**; non-specific SRD ≤ 100 mW e.r.p.; mitigation techniques (ECC Report 181) required.
  - **Two instruments disagree at 917–925 MHz**: the legal exemption itself (Telecommunications (Exemption from ss 53, 54(1)(b) and 55) Notification, First Schedule item 13) lists 917–925 MHz at **500 mW ERP** for all low-power devices [7], while TS SRD 30c caps LoRa-type end devices at **100 mW e.r.p. and 1 %** [1]. Conformity and equipment registration are assessed against TS SRD, so **treat 100 mW / 1 % as binding** unless IMDA agrees otherwise in writing ([19 Singapore page](../19-regulations-safety/singapore-imda-rules.md)).
- **Consequence**: the **E22-400T33D (33 dBm, 0.5 dB cable, dipole → 32.5 dBm ≈ 1.8 W e.r.p.) is ≈ 22.5 dB above the 433 MHz SRD limit** (its lowest step, 24 dBm, is still 13.5 dB over), and the **E220-900T30D (1 W)** exceeds the 917–925 MHz LPWAN-end-device limit by ≈ 9.5 dB (and the 500 mW class by ≈ 2.5 dB). **Resolved by domain 19:** full power is legal only under (1) an **amateur station licence** (430–440 MHz ≤ 10 W ERP, secondary, prior written IMDA consent per frequency, no encryption, callsign), (2) a **Temporary Use of Radio Frequency Permit** (≤ 90 days, case-by-case), (3) an **Experimental Station Licence** (institution, ≥ 1-year R&D) or (4) a **Localised Radio-communication Station Licence** (telemetry not meeting TS SRD). TS SRD Table 2 (approval route) is RFID-only at 920–925 MHz — there is **no Table 2 route for LoRa**. The E220 *can* be exempt at **866–869 MHz (CH 16–18) at ≤ 24–27 dBm** (CH 16 only if the E22 is not on CH 23; normally CH 17 with E22 CH 24, CH 18 with CH 23) — the best licence-exempt home — or at 917–925 MHz at 21 dBm (lowest step) plus a ≥ 1 dB pad or a ≤ 1.15 dBi antenna, with 1 % duty [19 Singapore page] (Example 2).
- **LoRaWAN plan for Singapore**: AS923-1 (default channels 923.2/923.4 MHz, 400 ms dwell, default max EIRP 16 dBm) per LoRa Alliance RP002 [4]; RP002 still lists 920–925 MHz — IMDA's 917–925 MHz supersedes it.
- **EU (legal source: Commission Implementing Decision (EU) 2025/105 of 22 Jan 2025 amending Decision 2006/771/EC; the ETSI EN 300 220-2 Table B.1 figures are the same)** [2]: 433.05–434.79 MHz 1 mW e.r.p. (44a) or 10 mW e.r.p. ≤ 10 % duty (44b), and 434.04–434.79 MHz 10 mW at ≤ 100 % duty if BW ≤ 25 kHz (45c); 863–865 25 mW 0.1 %; 865–868 25 mW 1 % (plus four 200 kHz data-network slots at 500 mW, ≤ 2.5 % for end devices, entry 47b); 868.0–868.6 25 mW 1 %; 868.7–869.2 25 mW 0.1 %; **869.40–869.65 MHz 500 mW 10 % (entry 54)**; 869.7–870 5 mW (no limit) / 25 mW 1 %; "mitigation techniques" (polite access, LBT+AFA) may replace duty cycle. **The EBYTE E220's 1 MHz channel grid (850.125 + CH MHz) cannot reach 869.40–869.65 MHz** (nearest channel 869.125 MHz is outside) — use a bare SX126x/LLCC68 or a module with fine frequency setting.
- **US (47 CFR §15.247)** [3]: 902–928 MHz; FHSS with 20 dB BW < 250 kHz needs ≥ 50 channels, ≤ 0.4 s dwell per 20 s, ≤ 1 W; digital modulation (6 dB BW ≥ 500 kHz) ≤ 1 W and ≤ 8 dBm/3 kHz PSD; antenna gain above 6 dBi reduces allowed power dB-for-dB; hybrid systems allowed. **Amateur 33 cm is prohibited at Spaceport America**: 47 CFR 97.303(n)(2) bars all amateur 902–928 MHz transmissions in the White Sands box (31°41′–34°30′ N, 104°11′–107°30′ W) [8], so IREC Student Band Plan Rev D "Mode C" (ham narrowband at 33 cm) conflicts with federal law — use **Mode A** (902.0–909.0 MHz SRAD range, 500 kHz ≤ BW ≤ 1 MHz, no hopping, ≤ 1 W, Part 15 DTS) or **Mode B** (§15.247 FHSS). IREC's 70 cm SRAD range is 420.6–438.0 MHz, ≤ 125 kHz, **≤ 200 mW** unless ESRA approves more, and needs a US amateur control operator [9].
- **Australia (Radiocommunications (LIPD) Class Licence 2025, in force 1 Oct 2025)** [10]: 433.05–434.79 MHz **25 mW EIRP** (any transmitter); 915–928 MHz **1 W EIRP** for frequency-hopping (≥ 20 hop frequencies) or digital-modulation transmitters (peak PSD ≤ 25 mW per 3 kHz), otherwise **3 mW EIRP**. A flat 125 kHz LoRa spectrum reaches the PSD cap at ≈ 1.04 W, so ≤ 27–28 dBm EIRP is the sensible setting; whether LoRa is "digital modulation" under the instrument was not verified.
- **Timing consequences** (`tools/verify/lora_toa.py`): a 32-byte SF7/125 packet (71.9 ms) may repeat only every **7.2 s at 1 %** or 0.72 s at 10 %; at SF12/125 (1.81 s) every 181 s at 1 %. Under a 400 ms dwell, SF11–12 at 125 kHz cannot send any packet; SF10/125 is limited to 24 bytes.

## Intuition (no math)
Licence-free bands are shared rooms. Regulators keep them usable by limiting how loud you may talk (power, usually measured as radiated power relative to a dipole, e.r.p., or to an isotropic antenna, e.i.r.p.), how much of the time you may talk (duty cycle), how long you may sit on one frequency (dwell time), or requiring you to listen first (LBT). LoRa makes packets long, so these limits bite hard on update rate: a device that must stay silent 99 % of the time cannot send 10 telemetry frames per second no matter how clever the radio is. Rocketry telemetry wants exactly that high rate, which is why many teams end up in amateur bands or seek special permission — a legal question, not an engineering one.

## The math
### Level 1 — power units
- Conducted power $P$ (dBm) at the antenna connector; antenna gain $G$ (dBi); cable loss $L$.
- $\text{EIRP} = P - L + G_{dBi}$; $\text{ERP} = \text{EIRP} - 2.15$ dB (half-wave dipole = 2.15 dBi) [1].
- 10 mW e.r.p. = 10 dBm e.r.p. = 12.15 dBm EIRP. 100 mW e.r.p. = 22.15 dBm EIRP. 500 mW e.r.p. = 29.15 dBm EIRP.
- Example: E22-400T33D, 33 dBm, 0.5 dB cable, 2.15 dBi dipole → EIRP 34.65 dBm, ERP 32.5 dBm ≈ 1.8 W e.r.p. vs 10 mW allowed: **22.5 dB over**.

### Level 2 — duty cycle and dwell
Duty cycle $d$ over an observation window (ETSI: typically one hour; Meshtastic implements a rolling hour [6]) means $\sum T_{on} \le d\cdot T_{window}$. For back-to-back periodic packets of air time $T_p$, the minimum period is $T_{min} = T_p/d$ and the maximum rate $f_{max} = d/T_p$.

| 32-byte packet | ToA | 1 % | 10 % | 0.1 % |
|---|---|---|---|---|
| SF7/125 | 71.9 ms | 7.19 s | 0.72 s | 71.9 s |
| SF9/125 | 246.8 ms | 24.7 s | 2.47 s | 247 s |
| SF12/125 | 1810 ms | 181 s | 18.1 s | 1810 s |
| SF7/250 | 36.0 ms | 3.60 s | 0.36 s | 36 s |
| SF7/500 | 18.0 ms | 1.80 s | 0.18 s | 18 s |

**Dwell time** (FCC FHSS channels, AS923 with UplinkDwellTime = 1) limits a *single* transmission to 400 ms [3][4]. Maximum PHY payload in 400 ms (preamble 8, explicit header, CRC, CR4/5):

| BW | SF7 | SF8 | SF9 | SF10 | SF11 | SF12 |
|---|---|---|---|---|---|---|
| 125 kHz | 255 B | 138 B | 66 B | 24 B | none | none |
| 500 kHz | 255 B | 255 B | 255 B | 174 B | 82 B | 30 B |

This is why AS923 joins use DR2–DR5 (SF10–SF7 at 125 kHz) until the network signals the dwell setting, and why DR0/DR1 are unusable with dwell on [4].

### Level 3 — FCC §15.247 in LoRa terms
- A LoRa 125 kHz signal has a 20 dB bandwidth < 250 kHz ⇒ as an FHSS device it needs ≥ 50 hopping channels, ≤ 0.4 s per channel in any 20 s, ≤ 1 W conducted [3]. LoRaWAN US915 uses 64 × 125 kHz uplink channels (902.3 + 0.2n MHz) plus 8 × 500 kHz channels [4].
- A LoRa 500 kHz signal can qualify as a **digital modulation** system if its 6 dB bandwidth ≥ 500 kHz — marginal, must be measured — then no hopping is required but PSD ≤ 8 dBm in any 3 kHz: for a flat 500 kHz spectrum the total may be 8 + 10 log(500/3) = 30.2 dBm, so the 1 W limit is the binding one [3].
- **Hybrid** (§15.247(f)): hopping with dwell ≤ 0.4 s in (N × 0.4 s) *and* the digital PSD limit [3].
- Directional antennas > 6 dBi: reduce conducted power by the excess (a 12 dBi Yagi on a 1 W transmitter → 24 dBm) [3]. (Point-to-point exceptions exist; see domain 19.)
- 433 MHz in the US is **not** an ISM data band; §15.231/§15.240 cover periodic control signals and container RFID only (and IMDA borrows these as measurement references [1]); 70 cm amateur allocations cover it in many countries — licence rules apply.

## Design equations & rules of thumb
| Region / band | Power | Access rule | Source |
|---|---|---|---|
| SG 433.05–434.79 MHz | 10 mW e.r.p. (or 1 mW) | ≤ 10 % "for bandwidth over entire band" | [1] |
| SG 866–869 MHz | 500 mW e.r.p. | tracking/data acquisition, LPWAN, RFID; refarm review | [1] |
| SG 917–925 MHz LPWAN end device | 100 mW e.r.p. | ≤ 1 % duty + mitigation | [1] |
| SG 917–925 MHz non-LPWAN end device / AP | 500 mW e.r.p. | AP ≤ 10 %; mitigation (Notification item 13 says 500 mW for all LPDs — TS SRD 30c's 100 mW/1 % treated as binding for LoRa) | [1][7] |
| SG amateur 430–440 MHz (licensed) | 10 W ERP | secondary; prior written IMDA consent; callsign; no encryption | 19 amateur page |
| EU 869.4–869.65 MHz | 500 mW e.r.p. | ≤ 10 % or polite access | [2] |
| EU 868.0–868.6 MHz | 25 mW e.r.p. | ≤ 1 % | [2] |
| EU 433.05–434.79 MHz | 10 mW e.r.p. | ≤ 10 % (or 1 mW, no limit) | [2] |
| EU 434.04–434.79 MHz | 10 mW e.r.p. | ≤ 100 %, BW ≤ 25 kHz (LoRa 125 kHz does not qualify) | [2] |
| US 902–928 MHz | 1 W conducted (+6 dBi) | FHSS ≥ 50 ch, 0.4 s/20 s; or DTS ≥ 500 kHz, 8 dBm/3 kHz; **no amateur 33 cm in the WSMR box (97.303(n)(2))** | [3][8] |
| US IREC 70 cm SRAD 420.6–438.0 MHz (licensed) | ≤ 200 mW (more with ESRA approval) | ≤ 125 kHz; US amateur control operator + callsign | [9] |
| AU 433.05–434.79 MHz | 25 mW EIRP | any transmitter | [10] |
| AU 915–928 MHz | 1 W EIRP (else 3 mW) | FHSS ≥ 20 hops, or digital modulation ≤ 25 mW/3 kHz | [10] |
| IN865 (865–867 MHz) | 30 dBm EIRP default (LoRaWAN plan) | no duty in RP002 table | [4] |
| AS923 (LoRaWAN) | 16 dBm EIRP default | < 1 %, 400 ms dwell | [4] |
| EU433 (LoRaWAN) | 12 dBm EIRP default | < 10 % | [4] |

## Worked examples
**1. Is a Singapore-legal 433 MHz rocket downlink useful?** 10 mW e.r.p. (12.15 dBm EIRP). With a 10 dBi tracking Yagi and SF9/125, the [link budget](lora-sensitivity-and-link-budget.md) leaves ~150 dB MAPL: ≫ the 115 dB free-space loss at 30 km. Yes — for in-flight LOS; not for a landed rocket kilometres away. Duty: at 10 %, a 32-byte SF7/125 frame every 0.72 s (1.4 Hz); SF7/500 every 0.18 s (5.6 Hz). Domain 19 reads "≤ 10 % for bandwidth over entire band" as a flat 10 % limit for any 26a signal ([19 Singapore page](../19-regulations-safety/singapore-imda-rules.md), ambiguity 3). **Licensed comparison:** the same link at the E22's full 33 dBm under an amateur licence (≤ 10 W ERP, IMDA consent) has 22.5 dB more EIRP and no SRD duty limit — the extra margin matters for the landed-rocket case, not for LOS flight.

**2. E220-900T30D in Singapore.** Set a channel in 917–925 MHz (e.g. CH 70 = 920.125 MHz) and reduce the power: 21 dBm is the E220's lowest step [see modules]; 21 dBm − 0.5 dB cable + 2.15 dBi = 22.65 dBm EIRP = 20.5 dBm e.r.p. ≈ 112 mW — still slightly above 100 mW e.r.p.; use a lower-gain antenna or add an attenuator, or use a bare-chip design with fine power control. At 1 % duty, one 32-byte SF7/500 packet per 1.8 s. **Better licence-exempt alternative:** CH 16–18 (866.125–868.125 MHz, TS SRD 29) at ≤ 24–27 dBm conducted — up to 500 mW e.r.p. with **no duty cycle stated** (e.g. 24 dBm → 224 mW e.r.p., +3.5 dB margin), so 10 Hz telemetry is allowed; the catch is IMDA's refarm review of the band ([modules page](lora-modules-ebyte-rfm-heltec.md), [19](../19-regulations-safety/singapore-imda-rules.md)).

**3. US launch (e.g. Spaceport America Cup) with a 900 MHz LoRa link.** A fixed-channel 125 kHz LoRa link at 1 W is *not* §15.247-compliant (needs ≥ 50-channel hopping with 0.4 s dwell); a 500 kHz LoRa link might qualify as DTS if its measured 6 dB bandwidth is ≥ 500 kHz. FCC-certified FHSS modems (e.g. RFD900x, [other radios](other-ism-radios-fsk-2g4.md)) avoid the question. IREC SBP Rev D Mode A puts SRAD 33 cm links in 902.0–909.0 MHz with 500 kHz ≤ BW ≤ 1 MHz (an E220 at LoRa BW 500 kHz, CH 53–58) [9]; a ham licence does **not** help at 33 cm there, because 97.303(n)(2) forbids amateur 902–928 MHz transmissions in the White Sands box that contains Spaceport America [8] ([19 international page](../19-regulations-safety/international-rules-for-competitions.md)).

**4. EU test campaign at 869.5 MHz.** 500 mW e.r.p., 10 %: SF7/125 32-byte frames at most every 0.72 s — marginal for boost-phase telemetry; SF7/500 at 5.6 Hz may exceed the sub-band's 250 kHz width (869.4–869.65 MHz) — **500 kHz LoRa does not fit this sub-band**; 125 kHz does. **Hardware catch:** the E220-900T30D tunes only to 850.125 + CH MHz; CH 19 = 869.125 MHz is outside 869.40–869.65 MHz and CH 20 = 870.125 MHz is outside the SRD band altogether, so the E220 cannot use entry 54 — only 25 mW sub-bands (e.g. CH 18 = 868.125 MHz lies in 868.0–868.6 MHz: 25 mW e.r.p., 1 %). Use a bare SX126x/LLCC68 (frequency set in ~1 Hz steps) for 869.525 MHz [2].

## Practical notes
- Check both the **frequency** *and* the **occupied bandwidth** fit the sub-band (a 500 kHz signal centred at 869.525 MHz spills outside 869.4–869.65).
- Modules default to channels that may be illegal locally (E220 default 873.125 MHz; E22 default 433.125 MHz is inside 433.05–434.79 but the power is not, and at BW 250/500 kHz its lower channel edge, 433.000/432.875 MHz, falls below 433.05 MHz: use CH 24 = 434.125 MHz, or CH 23 only at BW ≤ 125 kHz).
- **Duty cycle is per device over time**, so a ground station that never transmits (downlink-only architecture, as Space Bar flew) keeps the rocket's duty as the only budget.
- Meshtastic's SG_923 region uses 917–925 MHz at 20 dBm and does *not* enforce a duty cycle [6] — convenient but not evidence of legality for LPWAN end devices under IMDA's 1 % rule. Also, 20 dBm **conducted** into any antenna with more than 2.15 dBi gain (minus cable loss) already exceeds 100 mW **e.r.p.** — e.g. a 5 dBi whip gives ≈ 193 mW e.r.p.
- LoRaWAN regional plans (RP002) are *network* conventions layered on local law; raw LoRa is bound by local law only ([LoRaWAN vs raw LoRa](lorawan-vs-raw-lora.md)).

## Common mistakes & misconceptions
- **"ISM means anything goes."** SRD bands have strict power/duty limits; 433 MHz in Singapore is 10 mW e.r.p.
- **"433 MHz is an ISM band, so it is licence-free in Singapore."** 433.05–434.79 MHz is ISM only in ITU Region 1 and the RR 5.280 countries (RR 5.138); Singapore (Region 3) allows it purely as a national SRD band at 10 mW e.r.p. [1][11]. ISM status never authorised a transmitter anyway.
- **"The Notification says 500 mW at 917–925 MHz, so LoRa may use 500 mW."** TS SRD 30c caps LPWAN end devices (LoRa named) at 100 mW e.r.p. and 1 % [1][7].
- **"A ham licence makes 33 cm LoRa legal at Spaceport America."** 97.303(n)(2) forbids amateur 902–928 MHz transmissions there; use Part 15 (IREC Mode A/B) [8][9].
- **Confusing conducted power with e.r.p./e.i.r.p.** A 2.15 dBi dipole makes 100 mW conducted = 100 mW e.r.p.; a 5 dBi collinear makes it ~190 mW e.r.p.
- **"915 MHz is legal everywhere."** Singapore: 917–925 (and 866–869); EU: 863–870; US: 902–928; India: 865–867.
- **Assuming LoRaWAN duty limits apply to raw LoRa** (or vice-versa) — local regulation governs; LoRaWAN plans add their own defaults.
- **Using SF12/125 in a dwell-limited plan** — impossible (> 400 ms for any payload).
- **Ignoring harmonics**: legal fundamental power is useless if the 2nd harmonic of a 433 MHz PA lands in 866 MHz above spurious limits.

## How to simulate / verify
- `python3 tools/verify/lora_toa.py` — prints the dwell-limited maximum payloads and duty-cycle packet intervals used above (function `regulatory_timing`).
- Measure the occupied bandwidth (20 dB and 6 dB) and PSD of your transmitter with a spectrum analyser before claiming a regulatory class.
- ERP check: measured conducted power (power meter/attenuator) + antenna gain (from simulation or range measurement) − 2.15 dB.

## Open questions / gaps
- **Interpretation for rocket telemetry in Singapore** — partly resolved by domain 19 (2026-09-29): 30c (100 mW, 1 %) is the conservative class for LoRa at 917–925 MHz; 1–2 W needs an amateur licence, temporary permit, experimental or localised station licence (no TS SRD Table 2 route). Still open: IMDA's written view on 30b vs 30c for point-to-point LoRa, and whether rocket telemetry is "tracking, tracing and data acquisition" (29) — ask IMDA.
- The exact meaning of "duty cycle ≤ 10 % for bandwidth over entire band" in IMDA 26a (domain 19 reads it as a flat 10 %; not confirmed by IMDA).
- Singapore amateur 70 cm: resolved in [19 amateur page](../19-regulations-safety/amateur-radio-licensing.md) (430–440 MHz, ≤ 10 W ERP, secondary, prior written consent).
- ETSI EN 300 220-2 V3.3.1 (2025) supersedes V3.2.1; the EU legal numbers were re-checked against Decision (EU) 2025/105 (unchanged for 433/868 MHz). RP002-1.0.4/1.0.5 exist; 1.0.3 used here.
- Corrections applied 2026-09-29 by W5-E1 from W3-C5 cross-domain notes X1–X6, X9, X10, X13 (TS SRD date, Notification-vs-TS conflict, licence routes, EU 2025/105, E220 grid, US 97.303(n)(2)/IREC, Australia LIPD 2025, Region-1 ISM).
- CN470-510 and KR920 details not transcribed.

## Sources
1. IMDA, *Technical Specification — Short Range Devices*, IMDA TS SRD Issue 1 Rev 3, **September 2023** (latest; the 433/866/917 MHz rows are identical to the April 2023 printing; current URL https://www.imda.gov.sg/-/media/imda/files/regulation-licensing-and-consultations/ict-standards/telecommunication-standards/radio-comms/imdatssrd.pdf) — Table 1 sub-bands 26a–d (433.05–434.79 MHz), 29 (866–869 MHz), 30a–d (917–925 MHz, amended from 920–925), 32a–e (2.4 GHz), e.i.r.p. = e.r.p. + 2.15 dB; Table 2 approval-only 920–925 MHz RFID ≤ 2 W. https://www.imda.gov.sg/-/media/Imda/Files/Regulation-Licensing-and-Consultations/ICT-Standards/Telecommunication-Standards/IMDA-Technical/IMDA-TS-SRD.pdf (regulator standard)
2. Commission Implementing Decision (EU) 2025/105 of 22 January 2025 amending Decision 2006/771/EC — annex entries 44a, 44b, 45c, 46a, 47, 47b, 48, 50, 54, 56a/b and footnote on mitigation techniques (primary legal source; via [19 international page](../19-regulations-safety/international-rules-for-competitions.md) source 6). https://eur-lex.europa.eu/eli/dec_impl/2025/105/oj/eng (EU law). Also ETSI EN 300 220-2 V3.2.1 (2018-06), Annex B Table B.1 and FHSS duty-cycle clause (harmonised standard; same numbers). https://www.etsi.org/deliver/etsi_en/300200_300299/30022002/03.02.01_60/en_30022002v030201p.pdf (standard)
3. 47 CFR §15.247 (via Cornell LII) — 902–928 MHz FHSS channel/dwell/power rules, digital modulation 6 dB BW and PSD, antenna-gain rule, hybrid systems. https://www.law.cornell.edu/cfr/text/47/15.247 (regulation)
4. LoRa Alliance, *RP002-1.0.3 LoRaWAN Regional Parameters* (2021) — country table (Singapore: AS923-1 920–925, EU433, 866–869), dynamic/fixed plan summaries (duty, dwell, default EIRP), AS923 default channels and DR table, US915 channel plan. https://lora-alliance.org/wp-content/uploads/2021/05/RP002-1.0.3-FINAL-1.pdf (standard)
5. EBYTE E22-400TXXX datasheet / E220-900T30D manual — default channels and power steps. (module datasheets)
6. Meshtastic docs, LoRa configuration (region SG_923 917–925 MHz 20 dBm; EU duty handling). https://meshtastic.org/docs/configuration/radio/lora/ (project docs)
7. *Telecommunications (Exemption from sections 53, 54(1)(b) and 55) Notification* (Singapore, N 1), First Schedule item 13 (433.05–434.79 MHz 10 mW ERP; 866–869 MHz 500 mW ERP; 917–925 MHz 500 mW ERP) — SSO current version, via [19 Singapore page](../19-regulations-safety/singapore-imda-rules.md) source 2. https://sso.agc.gov.sg/SL/TA1999-N1 (legislation)
8. 47 CFR Part 97, §97.303(n)(2) (no amateur 33 cm transmissions in the 31°41′–34°30′ N, 104°11′–107°30′ W box), eCFR current. https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-97 (regulation)
9. ESRA, *IREC 2026 Frequency Student Band Plan*, Revision D (14 Apr 2026) — 33 cm Modes A/B/C, 70 cm SRAD 420.6–438.0 MHz ≤ 125 kHz ≤ 200 mW. https://www.esrarocket.org/s/IREC-2026-Frequency-Student-Band-Plan-Rev-D-041426.pdf (competition rules; not an authorising document)
10. *Radiocommunications (Low Interference Potential Devices) Class Licence 2025* (F2025L01047), Sch. 1 Table 1 items 19–20, Table 8 items 1 and 6. https://www.legislation.gov.au/F2025L01047/latest/text (legislation)
11. ITU Radio Regulations footnotes 5.138 and 5.280 (433.05–434.79 MHz ISM in Region 1 and listed countries), as reproduced in 47 CFR §2.106 — via [19 spectrum allocation](../19-regulations-safety/spectrum-allocation-ism-bands.md). (treaty text via regulation)
