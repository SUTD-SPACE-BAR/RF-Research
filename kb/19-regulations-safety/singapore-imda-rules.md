---
title: Singapore radio rules (IMDA) — short-range devices, licences, equipment registration, and whether our LoRa radios are legal
domain: 19-regulations-safety
slug: singapore-imda-rules
tags: [imda, singapore, ts-srd, short-range-devices, exemption-notification, telecommunications-act, erp, eirp, duty-cycle, lpwan, lora, e22-400t33d, e220-900t30d, amateur-licence, experimental-station-licence, temporary-frequency-permit, localised-station-licence, equipment-registration, compliance-checklist]
prerequisites:
  - spectrum-allocation-ism-bands.md
  - ../00-math-foundations/decibels-and-log-units.md
  - ../08-antennas/antenna-fundamentals.md
related:
  - amateur-radio-licensing.md
  - international-rules-for-competitions.md
  - certification-fcc-ce-imda.md
  - rf-exposure-safety.md
  - ../15-lora-ism-radios/ism-band-plans-duty-cycle.md
  - ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../15-lora-ism-radios/ground-station-design.md
level: mixed
confidence: high
last_updated: 2026-10-03
---

# Singapore radio rules (IMDA) — SRDs, licences, registration, and our LoRa radios

> **Not legal advice.** This page summarises Singapore primary law and IMDA documents as read on
> **2026-09-27** (last verified date). Regulations change; before relying on any statement, re-read
> the cited clause and, for anything non-obvious, ask IMDA (Spectrum Management / Licensing) in
> writing and keep the reply. Where the sources are ambiguous this page says so.

## Questions this page answers
- Is my 2 W EBYTE E22-400T33D (433 MHz) legal to use in Singapore?
- Is my 1 W EBYTE E220-900T30D (900 MHz band) legal in Singapore, and on which channel?
- What power and duty cycle does IMDA allow for LoRa at 433 MHz, 866–869 MHz and 917–925 MHz?
- What law actually makes low-power radios licence-free in Singapore?
- Is it illegal just to *own* a 2 W radio module in Singapore?
- Does antenna gain count towards the IMDA power limit?
- What is the difference between e.r.p. and e.i.r.p. in IMDA documents?
- What licences can a student rocketry team get to transmit at higher power (amateur, experimental, temporary permit)?
- How much does an IMDA temporary frequency permit cost and how long does it take?
- Do I need to register equipment with IMDA if I build my own radio?
- What should our rocket and ground station comply with before we switch them on in Singapore?
- Can I use a 24 GHz, 60 GHz or 77–81 GHz radar module in Singapore?

## TL;DR
- **Legal architecture.** The Telecommunications Act 1999 makes it an offence to *possess* (s54(1)(b)) or *operate* (s55(1)) radio-communication equipment without a licence; possession is presumed to be operation until proved otherwise (s55(2)) [1]. The **Telecommunications (Exemption from sections 53, 54(1)(b) and 55) Notification**, First Schedule, lists the equipment that is licence-exempt [2]. **IMDA TS SRD** (Issue 1 Rev 3, Sep 2023 — the latest issue found) sets the technical conditions that exempt short-range devices must meet [3].
- **433.05–434.79 MHz: 10 mW e.r.p. maximum** (TS SRD 26a, with "duty cycle ≤ 10 %"; or 1 mW e.r.p. under 26b with no access condition) [2][3]. There is **no licence-exempt route above 10 mW at 433 MHz**.
- **917–925 MHz:** the Notification allows 500 mW e.r.p. [2], but the TS SRD splits the band: **LoRa-type "LPWAN end devices" ≤ 100 mW e.r.p. and ≤ 1 % duty (30c)**; non-specific SRD ≤ 100 mW (30d); non-LPWAN end devices and LPWAN access points ≤ 500 mW (30b; access points ≤ 10 % duty); all with "suitable mitigation techniques" (ECC Report 181) [3]. Footnote 5 names LoRa as an LPWAN example.
- **866–869 MHz: ≤ 500 mW e.r.p. for "tracking, tracing and data acquisition including LPWAN, RFID", no duty cycle stated (TS SRD 29)** — but IMDA flags the band as "under review with the intent to refarm" [3]. This is the most permissive licence-exempt home for the E220-900T30D.
- **Priority answer.** At full power **neither module is licence-exempt anywhere in Singapore**: the E22-400T33D (33 dBm ≈ 1.8 W e.r.p. with a dipole) is **~22.5 dB over** the 433 MHz limit and even its lowest step (24 dBm) is 13.5 dB over; the E220-900T30D at 30 dBm is 9.5 dB over the 917–925 MHz LPWAN limit and 2.5 dB over the 500 mW classes. The E220 **can** be made exempt by retuning to 866–869 MHz at ≤ 27 dBm (dipole, ≥ 0.5 dB cable) or to 917–925 MHz at 21 dBm (its lowest step) plus a ≥ 1 dB pad or a ≤ 1.15 dBi antenna, with ≤ 1 % duty (`tools/verify/reg_erp_compliance.py`; the module has no 20 dBm setting).
- **Licensed routes** that can cover 1–2 W: (1) **Amateur Station Licence** — 430–440 MHz at ≤ **10 W ERP**, secondary basis, **prior written consent of IMDA** for the frequency, plain language, no encryption, callsign at start and end of each transmission, personal licence, IMDA-approved equipment [4][5]; (2) **Temporary Use of Radio Frequency Permit** — ≤ 90 days, any entity, unlisted frequencies "case-by-case", ~S$150–275 for a 25–500 kHz signal, 14 working days [6]; (3) **Experimental Station Licence** — for an educational institution/qualified person doing ≥ 1-year R&D, S$50/station/yr (+ S$300/frequency and a frequency fee outdoors) [7]; (4) **Localised Radio-communication Station Licence** — for telemetry equipment that does not meet the TS SRD, S$50/yr + S$300 + frequency fee, equipment must be registered or approved [8].
- **Antenna gain counts.** Limits below 1 GHz are e.r.p. (relative to a half-wave dipole); above 1 GHz e.i.r.p.; e.i.r.p. = e.r.p. + 2.15 dB (TS SRD §3) [3]. A 12 dBi Yagi turns 10 mW conducted into ~96 mW e.r.p.
- **What to do now:** stop radiating the 2 W / 1 W modules at full power in Singapore; for bench work transmit into a dummy load or attenuators; move the E220 to 866–869 MHz at ≤ 24–27 dBm (or 917–925 MHz at 21 dBm, the lowest step, plus a ≥ 1 dB pad or a ≤ 1.15 dBi antenna, ≤ 1 % duty); get team members amateur licences (the RAE is run by SARTS) and ask IMDA in writing for consent to use LoRa telemetry on 70 cm; for campaigns at higher power apply for a temporary permit, or have SUTD hold an Experimental Station Licence.

## Intuition (no math)
Singapore regulates radio in three layers. The **Act** says: nobody may own or use a transmitter unless licensed. The **Exemption Notification** then carves out a list of everyday low-power gear (Wi-Fi, walkie-talkies, remote controls, LoRa-class devices) that anyone may use, each with a maximum power in a specific band. The **IMDA technical specification (TS SRD)** is the rulebook those exempt devices must satisfy — it adds duty cycles, bandwidth caps and "politeness" requirements, and it is what equipment suppliers test against when they register a product. Anything outside that box needs an individual licence or permit, which IMDA grants for specific frequencies, powers and places.

Two consequences matter for rocketry. First, the limits are on **radiated** power (e.r.p.), so a bigger antenna uses up the allowance. Second, the licence-exempt bands are **unprotected and shared**: you must not cause interference and must accept any you receive (TS SRD §4.1(a)) — acceptable for a hobby link, uncomfortable for flight-critical telemetry, which is one reason to pursue a licensed or permitted assignment.

## The math
### Level 1 — the quantities in the limits
- Conducted power $P$ (dBm) at the module's antenna port; cable/connector loss $L$ (dB); antenna gain $G$ (dBi).
- $\mathrm{EIRP} = P - L + G$ (dBm); $\mathrm{ERP} = \mathrm{EIRP} - 2.15$ dB, because the reference half-wave dipole has 2.15 dBi gain. IMDA uses e.r.p. below 1 GHz and e.i.r.p. above 1 GHz and states the 2.15 dB constant explicitly (TS SRD §3) [3].
- Reference points: 1 mW = 0 dBm; 10 mW = 10 dBm; 100 mW = 20 dBm; 500 mW = 27 dBm; 1 W = 30 dBm; 2 W = 33 dBm; 10 W = 40 dBm.
- The amateur handbook defines ERP the same way: transmitter PEP multiplied by the antenna gain relative to a half-wave dipole (0 dBd) [5 §4.5.3]. For a constant-envelope LoRa/FSK signal the PEP equals the average power.

### Level 2 — duty cycle
A duty-cycle limit $d$ constrains the fraction of time transmitting, $\sum T_{on} \le d\,T_{obs}$. TS SRD does not define the observation window; ETSI EN 300 220 uses one hour (see [ISM band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md)). For back-to-back packets of time-on-air $T_p$ the minimum mean period is $T_{min} = T_p/d$: a 32-byte SF7/125 kHz LoRa frame (71.9 ms) may repeat every 0.72 s at 10 % and every 7.2 s at 1 % [`tools/verify/reg_erp_compliance.py`, ToA from `tools/verify/lora_toa.py`].

### Level 3 — what "e.r.p." hides
e.r.p. is defined in the direction of maximum radiation. A rocket-body antenna with a distorted pattern may have a peak gain above 2.15 dBi in some direction even if its average gain is lower, and the limit applies to the peak. For compliance, use the **maximum** gain from a pattern measurement or simulation ([antenna measurement](../08-antennas/antenna-measurement.md)), not the average. Mismatch loss reduces radiated power but is not a compliance tool — the PA may still deliver full power into a better-matched antenna later.

## Legal architecture and clauses (primary sources)

| Instrument | Clause | What it says (paraphrased) |
|---|---|---|
| Telecommunications Act 1999 (2020 Rev Ed) [1] | s54(1)(b) | No one may **possess** radio-communication equipment except in accordance with a licence or regulations. |
| | s55(1) | Offence to establish, install, maintain, provide or **operate** radio-communication equipment anywhere in Singapore (including in a vehicle, vessel or aircraft) without a licence. |
| | s55(2) | A person in possession of radio-communication equipment is **presumed to have operated it** until the contrary is proved. |
| | s85 | General penalty where none is specified: fine up to S$10,000 or imprisonment up to 3 years or both, plus forfeiture of seized articles; daily fine for continuing offences. |
| | s57 | Police/authorised IMDA officers may enter, inspect and seize radio equipment. |
| | s56 | Sections 53–55 do not apply to holders of foreign licences recognised under a treaty/arrangement (reciprocity), subject to IMDA conditions. |
| Telecommunications (Exemption from sections 53, 54(1)(b) and 55) Notification (N 1), current as at 2026-09-27 [2] | para 2(a) | Exempts stations permitted by IMDA to use a band under **reg 75** (temporary assignment) of the Radio-communication Regulations. |
| | para 2(b), First Schedule | Exempts installation/operation of the listed equipment, e.g. item 13 "Wireless LAN, RFID or Low Power Devices": **433.05–434.79 MHz 10 mW ERP; 866–869 MHz 500 mW ERP; 917–925 MHz 500 mW ERP**; 2400–2483.5 MHz 200 mW EIRP; 24.00–24.25 GHz 100 mW EIRP; 57–66 GHz 10 W EIRP. |
| | First Schedule footnote | Other low-power equipment in unlisted bands is exempt only if IMDA has approved both the band and the power. |
| Telecommunications (Radio-communication) Regulations (Rg 5) [4] | regs 25, 37–58, 75 | Station licence types (Amateur, Experimental, Localised Radio-communication, Special Purpose, etc.); amateur conditions (regs 37–44); experimental licences (regs 45–46); all station equipment must be approved before use (reg 58(2)); ad hoc temporary frequency assignment ≤ 90 days at a time (reg 75). |
| IMDA TS SRD Issue 1 Rev 3 (Sep 2023) [3] | §1.4, §4.1, §5, Table 1, Table 2 | Technical requirements; Table 1 = normal SRD provisions; Table 2 = higher-power provisions granted only "on an exception basis" with approval. |

**Two layers disagree at 917–925 MHz.** The Notification gives one number (500 mW ERP) for all "low power devices"; the TS SRD restricts LoRa-type end devices to 100 mW and 1 %. The TS SRD is what equipment conformity and registration are assessed against (TS SRD §5; IMDA Guide EQR Table B.1 lists SRDs against "Table 1 of IMDA TS SRD" [9]), and IMDA's import page says imported equipment for own use must comply with the relevant technical specification before use [10]. **Treat the TS SRD limit (100 mW, 1 %) as binding for LoRa at 917–925 MHz**; do not rely on the Notification's higher figure without IMDA's written agreement.

## Singapore SRD bands relevant to our work (TS SRD Iss. 1 Rev 3 Table 1 [3], cross-checked with the Notification [2])

| Sub-band | Band | Max power | Access conditions | Application type |
|---|---|---|---|---|
| 8b | 13.553–13.567 MHz | 10 mW e.r.p. | — | non-specific SRD |
| 9b | 26.96–27.28 MHz | 100 mW e.r.p. | duty ≤ 0.1 % | non-specific SRD (Notification item 10 also lists "Radio Telemetry Equipment" 26.96–27.28 MHz at 500 mW ERP) |
| 11 | 34.995–35.225 MHz | 100 mW e.r.p. | 10 kHz BW | control of flying models |
| 13a | 40.66–40.70 MHz | 10 mW e.r.p. | — | non-specific SRD |
| 25d | 444.40–444.80 MHz | (100 mW ERP per Notification item 7) | — | intermittent/periodic control signals, radio detection |
| **26a** | **433.05–434.79 MHz** | **10 mW e.r.p.** | "Duty cycle ≤ 10 % for bandwidth over entire band" | non-specific SRD |
| 26b | 433.05–434.79 MHz | 1 mW e.r.p. | — | non-specific SRD |
| 26c | 433.05–434.79 MHz | 10 mW e.r.p. | — | intermittent/periodic control signals |
| 26d | 433.05–434.79 MHz | 10 mW e.r.p. | — | container RFID at ports, rail terminals, warehouses |
| **29** | **866–869 MHz** | **500 mW e.r.p.** | none stated; band "under review with the intent to refarm" | tracking, tracing and data acquisition incl. LPWAN, RFID |
| 30a | 917–925 MHz | 500 mW e.r.p. | BW ≤ 400 kHz; transmit no longer than needed | RFID |
| 30b | 917–925 MHz | 500 mW e.r.p. | duty ≤ 10 % for network access points; mitigation (ECC Rep. 181) | non-LPWAN end devices, LPWAN access points |
| **30c** | **917–925 MHz** | **100 mW e.r.p.** | **duty ≤ 1 %**; mitigation | **LPWAN end devices** (LoRa, Sigfox named) |
| 30d | 917–925 MHz | 100 mW e.r.p. | mitigation | non-specific SRD |
| 32a–e | 2.400–2.4835 GHz | 10 / 25 / 100 / 100 / 200 mW e.i.r.p. | 32d: sharing mechanism (LBT/DAA); 32e: PSD ≤ 10 mW/MHz for non-FHSS wideband | non-specific / radio-determination / RFID-model-video / wideband data (BT, Zigbee) / RLAN |
| 35, 36a | 5.725–5.850 / 5.725–5.875 GHz | 1 W / 100 mW e.i.r.p. | 35: TPC + DFS | RLAN & fixed broadband / non-specific SRD |
| 37 | 10.50–10.55 GHz | 117 dBµV/m at 10 m | — | radio-determination |
| 38a–c | 24.00–24.25 GHz | 100 mW e.i.r.p. | 38c: radar guns not allowed | automotive radar / tank-level radar / non-specific SRD |
| 39b | 57–64 GHz | 100 mW e.i.r.p. | — | non-specific SRD |
| 40 | 57–66 GHz | 10 W e.i.r.p. | LBT, ≤ 13 dBm/MHz mean EIRP density | RLAN |
| 41 | 76–77 GHz | 55 dBm peak; 23.5 dBm average (pulse) / 50 dBm average (other) e.i.r.p. | — | fixed-infrastructure TTT and ground vehicle radar (also Notification item 15 "Short Range Radar System") |
| (not in TS SRD) | **77–81 GHz** | **mean e.i.r.p. density ≤ −3 dBm/MHz; peak ≤ 55 dBm/50 MHz** | must be UWB (10 dB BW ≥ 500 MHz or fractional > 0.2); not a fixed outdoor installation / externally mounted antenna | "Ultra-Wideband Devices" — Notification item 17 + **IMDA TS UWB** Table 1 (generic UWB and automotive SRR columns) [2][12] |
| 42 / 43 | 122–123 / 244–246 GHz | 100 mW e.i.r.p. | — | non-specific SRD |

Other points from TS SRD:
- **Spurious emissions** (Table 1-a, ITU-R SM.329 Category B): −36 dBm below 1 GHz, −54 dBm in 47–74, 87.5–118, 174–230 and 470–862 MHz, −30 dBm from 1 GHz up [3]. A 433 MHz transmitter's 2nd harmonic (866 MHz) and 3rd (1299 MHz) must meet −36/−30 dBm; at 10 dBm output that is ≥ 46 dBc and 40 dBc suppression.
- **§4.1(b):** an SRD must not have an external or readily accessible control that lets the user adjust it into non-compliance [3]. A module whose power can be set to 2 W by a UART command is, in my reading, not a compliant SRD *product* even if you configure it to 10 mW — another reason the E22-400T33D belongs under a licence rather than the exemption (interpretation; not stated by IMDA for this module).
- **Table 2 (approval, exceptional basis only):** 920–925 MHz **RFID only** > 500 mW to 2 W e.r.p.; 5.725–5.850 GHz WLAN to 4 W e.i.r.p.; 57.1–62.9 GHz fixed links to 55 dBm e.i.r.p. [3]. **There is no Table 2 provision for 433 MHz or for LoRa telemetry** — the "2 W at 920 MHz" figure seen online is RFID-only.
- **Radar bands (checked 2026-09-29, W5-E1).** TS SRD Table 1 lists radar-type use at 10.50–10.55 GHz (37), 24.00–24.25 GHz (38a automotive, 38b tank-level, 38c non-specific — "radar gun devices are not allowed"), 57–64 GHz (39a tank-level, 39b non-specific, 100 mW e.i.r.p.) and 76–77 GHz (41); Table 2 has no radar rows. **77–81 GHz is absent from TS SRD** (FCC Part 95 M 76–81 GHz is cited only as a measurement reference), **but it is licence-exempt as an Ultra-Wideband device**: Notification First Schedule item 17 lists 77.00–81.00 GHz at −3 dBm/MHz [2], and IMDA TS UWB Issue 1 (Oct 2016) Table 1 sets mean e.i.r.p. density −3 dBm/MHz and peak 55 dBm/50 MHz, with §1.2 (UWB = ≥ 500 MHz or > 20 % fractional 10 dB bandwidth) and §4.1 (not for outdoor fixed installations or externally mounted antennas) [12]. A 77–81 GHz FMCW board sweeping ≥ 500 MHz therefore fits the exemption if its mean density is under −3 dBm/MHz (a TI board with a 4 GHz sweep is ≈ −14 dBm/MHz — [DIY radar Example 4](../11-radar/diy-radar-hardware.md#worked-examples)); a narrower sweep above 77 GHz has no exemption. TS UWB also allows 21.65–26.65 GHz automotive SRR at −41.3 dBm/MHz mean.
- **Airborne use:** neither TS SRD nor the Notification mentions airborne restrictions. (In practice no launches occur from Singapore; the question arises for balloons and drones — check CAAS rules separately.)

## Resolution of the priority question

**Short answer.** At their rated power the **E22-400T33D (2 W, 433 MHz) and the E220-900T30D (1 W, 900 MHz band) are not covered by any Singapore licence exemption**. Operating — and arguably merely possessing — them without an IMDA licence or permit is an offence under the Telecommunications Act (s54(1)(b), s55) [1]. The 433 MHz exemption stops at 10 mW e.r.p.; the 917–925 MHz exemption stops at 100 mW e.r.p. and 1 % duty for LoRa end devices; 866–869 MHz allows 500 mW e.r.p. [2][3].

Margins from `tools/verify/reg_erp_compliance.py` (0.5 dB cable, rocket dipole 2.15 dBi):

| Configuration | e.r.p. | Limit | Margin |
|---|---|---|---|
| E22-400T33D, 33 dBm, 433.125 MHz | 32.5 dBm (1.78 W) | 26a 10 mW | **−22.5 dB** |
| E22-400T33D, 24 dBm (lowest step) | 23.5 dBm (224 mW) | 26a 10 mW | **−13.5 dB** |
| E22-400T33D, 33 dBm, 433.125 MHz (amateur) | 1.78 W | 10 W ERP | +7.5 dB (licence + IMDA consent needed) |
| E22-400T33D, 33 dBm into 12 dBi ground Yagi (amateur) | 42.4 dBm (17.2 W) | 10 W ERP | **−2.4 dB** — step down to 30 dBm |
| E220-900T30D, 30 dBm at 920.125 MHz | 29.5 dBm (891 mW) | 30c 100 mW | **−9.5 dB** |
| E220-900T30D, 21 dBm (lowest) at 920.125 MHz | 20.5 dBm (112 mW) | 30c 100 mW | −0.5 dB (needs ≥ 1 dB more loss or a lower-gain antenna, plus 1 % duty) |
| E220-900T30D, 27 dBm at 867.125 MHz | 26.5 dBm (447 mW) | 29 500 mW | +0.5 dB (too thin — use 24 dBm: +3.5 dB) |

**Channel arithmetic for the E220** ($f = 850.125 + \mathrm{CH}$ MHz, from the EBYTE manual via [module page](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)): CH 16/17/18 = 866.125/867.125/868.125 MHz lie in 866–869 MHz with room for a 125 kHz (and, at 867.125 and 868.125 MHz, a 500 kHz) signal; CH 67–74 = 917.125–924.125 MHz lie in 917–925 MHz. The default CH 23 = 873.125 MHz is **outside both bands**. The same edge rule (the whole channel $f_c \pm BW/2$ inside the band) applies to the E22 ($f = 410.125 + \mathrm{CH}$ MHz) in 433.05–434.79 MHz: CH 24 = 434.125 MHz holds 125/250/500 kHz, while the default CH 23 = 433.125 MHz is legal only at BW ≤ 125 kHz (433.0625 MHz lower edge; at 250 kHz it starts at 433.000 MHz).

**Honest ambiguities.**
1. *Which 917–925 MHz class is a raw point-to-point LoRa telemetry link?* IMDA footnote 5 names LoRa as an LPWAN; the conservative reading is 30c (100 mW, 1 %). A 500 mW reading (30b, "non-LPWAN end device") would require arguing the link is not LPWAN despite using LoRa — ask IMDA before relying on it.
2. *Is rocket telemetry "tracking, tracing and data acquisition" (sub-band 29)?* TS SRD says unclear terms follow ERC Rec 70-03 (Table 1 footnote 3), whose "tracking, tracing and data acquisition" category covers telemetry-type data collection; the fit looks good but is an interpretation. The band may be refarmed.
3. *"Duty cycle ≤ 10 % for bandwidth over entire band" (26a)* is not explained in TS SRD. Read it as a flat 10 % limit for any signal in 433.05–434.79 MHz under 26a; under 26b (1 mW) there is no duty limit.
4. *Possession.* The exemption covers equipment "specified in the First Schedule". Whether a 2 W-capable module configured to 10 mW counts is not addressed; s55(2)'s presumption makes owning 2 W modules without any licence risky. Holding an amateur licence (with the equipment declared) or an experimental licence resolves this.
5. *Notification (500 mW) vs TS SRD (100 mW) at 917–925 MHz* — see above; treat the lower number as binding.

## Licence and permit routes

| Route | Legal basis | Who | Bands/power | Cost & time | Fits |
|---|---|---|---|---|---|
| Licence-exempt SRD | Notification Sch. 1 item 13 + TS SRD Table 1 [2][3] | anyone | 433: 10 mW e.r.p.; 866–869: 500 mW; 917–925: 100 mW (LoRa, 1 %) | free | low-power bench/field tests, E220 at 866–869 MHz |
| **Amateur Station Licence** (Restricted or General class) | Rg 5 regs 37–44 [4]; Amateur Radio Handbook 5th ed. [5] | natural person ≥ 16 (16–21 supervised); pass RAE (Section I for Restricted, I + II for General) | 430–440 MHz ≤ 10 W ERP (secondary, shared, prior written consent per frequency); 2 m 144–146 MHz 25 W PEP; portable/mobile ≤ 10 W ERP | exam S$20 (students)/S$40; licence S$50 (Restricted) or S$100 (General) for 5 years | 433 MHz telemetry experiments by licensed members; see [amateur page](amateur-radio-licensing.md) |
| **Temporary Use of Radio Frequency Permit** | Rg 5 reg 75; Notification para 2(a) [4][2]; IRIS page [6] | any entity, incl. unregistered and foreign | listed frequencies incl. 433.79–434.79 MHz (10 mW), 866–869, 923–925 MHz (500 mW); **unlisted frequencies case-by-case** | 25–500 kHz BW: S$150 (1–10 days) / S$275 (11–90 days) + GST; 14 working days | a test campaign or demonstration at higher power on an IMDA-assigned frequency |
| **Experimental Station Licence** | Rg 5 regs 45–46 [4]; IRIS page [7] | educational institute, training establishment, qualified person, dealer | as assigned; IMDA may cap power (reg 46) | S$50/station/yr (shielded/confined); outdoors + S$300/frequency + annual frequency fee; 10 working days; activity must span ≥ 1 year | SUTD-held licence covering the team's radio R&D |
| **Localised Radio-communication Station Licence** | Rg 5 reg 47(e) telemetry [4]; IRIS page [8] | approved applicants | as assigned | S$50/yr (telemetry) + S$300 application + frequency fee; 10 working days | an ongoing telemetry system that does not meet TS SRD; equipment must be registered/approved |
| TS SRD Table 2 approval | TS SRD §1.4, §5.3 [3] | exceptional basis | 920–925 MHz >500 mW–2 W **RFID only** | — | not applicable to LoRa telemetry |

A "Technical Trial (with use of Frequency)" licence is also listed on GoBusiness for short-term trials (< 1 year); its page did not render when checked, so its conditions are **not verified** here — ask IMDA or use the IRIS e-Advisor.

## Equipment registration and dealing
- **Registration is a supplier obligation before sale or hire**, not a user obligation: SRDs meeting TS SRD Table 1 are registered under the self-declared ESER scheme (no fee); Table 2 high-power SRDs need GER [9 §2.2, Table B.1]. **Standalone radio modules sold separately are subject to registration** [9 Table B.1 note 3].
- **Import for own use:** no dealer's licence is needed, but the importer must ensure the equipment complies with the relevant IMDA technical specification **before use**; individual approval of personally imported items was discontinued and the individual carries the responsibility [9][10]. So importing E22-400T33D modules from China is not itself illegal, but using them outside a licence or the SRD limits is.
- **Selling or giving away** radios (e.g. kits to other teams) requires a dealer's licence and registered equipment [10].
- A home-built radio you do not sell needs no registration, but it must still meet the TS SRD to be exempt, or be covered by a licence (for amateurs, the equipment must be approved by IMDA per the handbook [5 §3.4.1(d)]).

## Worked examples
**1. E22-400T33D to 10 mW e.r.p. at 433 MHz.** Required conducted power with a dipole and 0.5 dB cable: $P \le 10 + 2.15 - 2.15 + 0.5 = 10.5$ dBm. The module's lowest step is 24 dBm → a **≥ 14 dB (use 15–16 dB) attenuator** between module and antenna. That wastes 97 % of the PA power, heats the attenuator by ~0.24 W and still leaves the §4.1(b) problem (the module can be commanded back to 2 W). Better: a 22 dBm-class module or bare SX1268 set to ≤ 10 dBm.

**2. Is 10 mW at 433 MHz enough for flight?** From the [link budget page](../09-propagation-link-budget/link-budget-methodology.md): with a 10 dBi ground Yagi, SF9/125 and 30 km LOS, free-space loss ≈ 115 dB; received ≈ 12.15 − 115 + 10 = −93 dBm vs ≈ −129 dBm sensitivity → ~36 dB margin before pattern nulls and polarisation loss. Enough in flight; tight for a landed rocket behind terrain.

**3. E220-900T30D at 867.125 MHz.** Set CH = 17 (`C0 05 01 11` in configuration mode — register 05H; value 0x11 = 17) and power 24 dBm (REG1 bits 1–0 = the 24 dBm code for the T30 table). e.r.p. = 24 − 0.5 + 2.15 − 2.15 = 23.5 dBm = 224 mW ≤ 500 mW: compliant with sub-band 29, no duty limit stated. Check the 2nd harmonic at 1734 MHz is ≤ −30 dBm (≥ 54 dBc below 24 dBm) with a spectrum analyser before claiming compliance.

**4. Temporary permit cost for a 3-day test at 2 W, 433.5 MHz, 125 kHz LoRa.** 125 kHz falls in "25 kHz < x < 500 kHz" → S$150 + GST for 1–10 days [6]; lead time 14 working days; the frequency is not on the listed menu at that power, so it is "case-by-case" and may be refused or moved.

**5. Amateur ground uplink with a Yagi.** 33 dBm into a 12 dBi Yagi = 42.4 dBm e.r.p. = 17 W > 10 W ERP. Step the module to 30 dBm (8.6 W ERP, +0.6 dB margin) or 27 dBm (4.3 W, +3.6 dB).

## Practical notes — compliance checklist for Space Bar in Singapore
Rocket (flight computers):
- [ ] E22-400T33D: do **not** radiate at any power under the SRD exemption; use only under an amateur licence with IMDA consent (430–440 MHz), a temporary permit or an experimental licence. Otherwise bench-test **conducted** into a 50 Ω dummy load / ≥ 40 dB attenuator chain.
- [ ] E220-900T30D: change CH from the default 23 (873.125 MHz) to 16–18 (866–869 MHz) at ≤ 24 dBm, or to 67–74 (917–925 MHz) at ≤ 21 dBm with a ≤ 0 dBi-equivalent path and ≤ 1 % duty.
- [ ] Record the configured power, channel and air rate in the flight log header (proves compliance later).
- [ ] Verify the 2nd/3rd harmonic and spurious levels against TS SRD Table 1-a on a spectrum analyser.
- [ ] Disable the EBYTE "CRYPT" scrambler if operating under an amateur licence (no encryption, reg 41 [4]).
- [ ] If amateur: callsign in every packet (satisfies "beginning and end of each transmission"), transmissions < 10 min uninterrupted [5 §4.7.1], logbook kept.

Ground station:
- [ ] Receive-only equipment needs no transmit licence (GNSS receivers are listed as exempt [2 item 14]); SDRs used as receivers are fine.
- [ ] **Any ground transmitter counts** — including the RTK-correction LoRa bridge flown on Avionics B (it transmits continuously, so a 1 % or 10 % duty class is unsuitable; it needs 866–869 MHz at ≤ 500 mW e.r.p. or a licence).
- [ ] Compute e.r.p. with the real antenna gain; a Yagi multiplies it.
- [ ] Keep a copy of the licence/permit and the IMDA consent letter at the station.

Organisation:
- [ ] Team members sit the RAE (SARTS-run) → Restricted class is enough for 70 cm.
- [ ] Ask SUTD whether it will hold an Experimental Station Licence for the lab; its outdoor frequencies can then be assigned per project.
- [ ] Write to IMDA describing the telemetry (frequency, bandwidth, emission, power, antenna gain, location, dates) before a campaign; keep the reply.

## Common mistakes & misconceptions
- **"433 MHz is licence-free, so any power is fine."** In Singapore the exemption is 10 mW e.r.p. [2][3]; the 2 W module is ~180× too strong.
- **"The module's rated power is the legal power."** Modules are sold worldwide; the legal limit is the local regulator's, measured as radiated power.
- **"ISM means anything goes."** ISM designation (ITU RR 5.138/5.150) concerns industrial heating equipment; SRD permission is a separate national instrument with strict limits ([spectrum allocation](spectrum-allocation-ism-bands.md)).
- **"IMDA allows 2 W at 920 MHz."** Only for RFID, only on an exception basis with approval (TS SRD Table 2) [3].
- **"The Notification says 500 mW at 917–925 MHz, so LoRa can use 500 mW."** The TS SRD caps LoRa end devices at 100 mW and 1 % [3].
- **Using AS923 or Meshtastic "SG_923" defaults as proof of legality.** Network/app defaults are not law; Meshtastic's SG region does not enforce 1 % duty.
- **Forgetting antenna gain** — e.r.p. includes it; an attenuator after a high-gain antenna is not how it works.
- **Assuming receive-only testing needs no care** — true for licensing, but a receiver near a 2 W transmitter can be damaged ([lab safety](lab-safety-esd-high-power.md)).
- **Thinking an amateur licence makes any use legal.** It covers personal, non-commercial, plain-language experiments with IMDA-approved equipment at approved locations; no encryption, no third-party traffic [4][5].

## How to simulate / verify
- `python3 tools/verify/reg_erp_compliance.py` — e.r.p./e.i.r.p. margins for every EBYTE power step × antenna × limit, required conducted power, duty-cycle packet intervals; self-tests the 2.15 dB and 19.3 W Yagi cases.
- Measure conducted power with a power meter through a known attenuator; measure harmonics with a spectrum analyser (RBW 100 kHz below 1 GHz, 1 MHz above, per SM.329); get antenna peak gain from a pattern measurement.
- Before any campaign, re-read the current Exemption Notification First Schedule on Singapore Statutes Online (SSO — use a browser; automated fetches are refused) and the latest TS SRD on imda.gov.sg.

## Open questions / gaps
- IMDA's written position on (a) which 917–925 MHz class applies to point-to-point LoRa telemetry, (b) whether rocket telemetry qualifies as "tracking, tracing and data acquisition" at 866–869 MHz, (c) whether LoRa (an F1D-type data emission) is acceptable on 70 cm under an amateur licence, whose Appendix 1 lists AM/FM/PM telegraphy and telephony emission classes but no data classes. **Ask IMDA.**
- Timing and outcome of the 866–869 MHz refarm review (none found as of 2026-09-27).
- The "Technical Trial (with use of Frequency)" licence conditions (page did not render).
- The IMDA Spectrum Allocation Chart (Jan 2026, v1.3) is graphical; the primary allocation of 430–440 MHz in Singapore was not transcribed (the handbook confirms amateur use is secondary and shared).
- Exact current fee tables in Annex 1 of the Experimental and Localised licence guidelines (not read).

## Sources
1. *Telecommunications Act 1999* (2020 Revised Edition), ss 53, 54, 55, 56, 57, 85 — Singapore Statutes Online, current version as at 2026-09-27. https://sso.agc.gov.sg/Act/TA1999 (legislation)
2. *Telecommunications (Exemption from sections 53, 54(1)(b) and 55) Notification* (N 1, G.N. No. S 115/2001, Rev. Ed. 2002, as amended incl. S 588/2023 wef 1 Sep 2023), para 2 and First Schedule items 2, 7, 10, 13, 14, 15 (Short Range Radar System 76–77 GHz), 17 (Ultra-Wideband Devices, incl. 77.00–81.00 GHz −3 dBm/MHz) — SSO, current version as at 2026-09-27; items 13/15/17 re-read 2026-09-29. https://sso.agc.gov.sg/SL/TA1999-N1 (legislation). Historic item 13 wording: S 179/2011 (IMDA PDF). (legislation)
3. IMDA, *Technical Specification — Short Range Devices*, IMDA TS SRD Issue 1 Revision 3, **September 2023** (also the April 2023 printing; the Sep 2023 issue adds the 5.945–6.425 GHz rows; 433/866/917 MHz rows identical) — §1.4, §3 (e.r.p./e.i.r.p.), §4.1, §5, Table 1 sub-bands 8b–43, Table 1-a, Table 2, Annex B. https://www.imda.gov.sg/-/media/imda/files/regulation-licensing-and-consultations/ict-standards/telecommunication-standards/radio-comms/imdatssrd.pdf (regulator standard)
4. *Telecommunications (Radio-communication) Regulations* (Rg 5), regs 2, 25, 37–48, 55–58, 75 — SSO, current as at 2026-09-27. https://sso.agc.gov.sg/SL/323-RG5 (legislation)
5. IMDA, *Amateur Radio Handbook*, Fifth Edition (21 November 2025) — Parts B–D, Appendix 1. https://www.imda.gov.sg/-/media/imda/files/regulations-and-licensing/licensing/telecommunication/amateur-station/amateur-handbook.pdf (regulator handbook)
6. IMDA IRIS, "Temporary Use of Radio Frequency Permit" (page last updated 24 Sep 2026) — scope, frequency list, fees, processing time. https://iris.imda.gov.sg/application/temporary-use-of-radio-frequency-permit (regulator procedure)
7. IMDA IRIS, "Experimental Station Licence" (24 Sep 2026). https://iris.imda.gov.sg/application/experimental-station-licence (regulator procedure)
8. IMDA IRIS, "Localised Radio-communication Station Licence" (24 Sep 2026). https://iris.imda.gov.sg/application/localised-radio-communication-station-licence (regulator procedure)
9. IMDA, *Guide for Registration of Telecommunication Equipment*, IMDA GUIDE EQR Issue 1 Rev 13 (Mar 2026) — §2.2 (ESER/SER/GER), §3.2.2, Annex B Table B.1 and notes (standalone modules), revision history (personal imports). https://www.imda.gov.sg/-/media/imda/files/regulations-and-licensing/regulations/frameworks-and-policies/dealer-and-equipment-registration/equipment-registration-framework/eqrguide.pdf (regulator guide)
10. IMDA, "Requirement for Import of Telecommunication Equipment" (last updated 23 May 2024). https://www.imda.gov.sg/regulations-and-licensing-listing/dealer-and-equipment-registration-framework/requirement-for-import-of-telecommunication-equipment (regulator web)
11. EBYTE E22-400TXXX datasheet and E220-900T30D manual, via [lora-modules-ebyte-rfm-heltec](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md) — power steps and channel formula. (module datasheets)
12. IMDA, *Technical Specification — Ultra-Wideband (UWB) Devices*, IMDA TS UWB Issue 1 (1 October 2016) — §1.2 (UWB definition), §4.1 (no fixed outdoor installations/externally mounted antennas), Table 1 (77–81 GHz mean e.i.r.p. density −3 dBm/MHz, peak 55 dBm/50 MHz; 21.65–26.65 GHz SRR −41.3 dBm/MHz). https://www.imda.gov.sg/-/media/imda/files/regulation-licensing-and-consultations/ict-standards/telecommunication-standards/radio-comms/imda-ts-uwb.pdf (regulator standard)
