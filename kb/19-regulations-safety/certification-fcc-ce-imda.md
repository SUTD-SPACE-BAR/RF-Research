---
title: Radio equipment certification — FCC ID and modular approval, CE/RED, IMDA registration, antennas, pre-compliance
domain: 19-regulations-safety
slug: certification-fcc-ce-imda
tags: [certification, fcc-id, part-15, modular-approval, 15.212, 15.203, 15.204, permissive-change, 2.1043, sdoc, home-built, 15.23, ce-marking, red-2014-53-eu, notified-body, imda-registration, eser, ger, pre-compliance, ansi-c63.10, etsi-en-300-220, test-mode, continuous-wave, duty-cycle-correction, lab-day, failed-test, pre-scan]
prerequisites:
  - singapore-imda-rules.md
  - international-rules-for-competitions.md
related:
  - rf-exposure-safety.md
  - amateur-radio-licensing.md
  - ../13-pcb-rf-layout-emc/emc-emi-fundamentals.md
  - ../17-test-measurement/spectrum-analyzers.md
  - ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md
  - ../15-lora-ism-radios/semtech-chip-family.md
  - ../17-test-measurement/interference-hunting-and-rf-immunity.md
level: intermediate
confidence: medium
last_updated: 2026-10-13
---

# Radio equipment certification — FCC, CE/RED, IMDA

> **Not legal advice; last verified 2026-09-27.** Certification law is about *placing products on the
> market*; operating a one-off device is governed mainly by the spectrum-use rules (Part 15/97,
> EU SRD decision, IMDA exemption). This page separates the two and flags where they overlap.

## Questions this page answers
- If I buy a "FCC/CE certified" LoRa module, is my flight computer certified?
- What does an FCC modular approval cover, and what breaks it?
- Can I change the antenna on a certified module?
- Do I need to certify a radio I built myself for our team?
- What is the EU Radio Equipment Directive (RED) and does it apply to amateur or student-built radios?
- Does IMDA require our flight computer to be registered?
- What pre-compliance tests should we do before a competition?
- Why does a module with an SMA connector usually not have a US modular grant?
- What "test mode" firmware does a test lab need from us, and how do I put an SX1262 into continuous-wave transmission?
- What should we bring to a test-lab day, and what do we do if the product fails?

## TL;DR
- **USA.** Operating an intentional radiator not in accordance with Part 15 requires a licence; marketing uncertified Part 15 devices is prohibited (§15.1(b),(c)) [1]. **Home-built exemption (§15.23)**: no equipment authorisation needed for devices *not marketed, not built from a kit, ≤ 5 units, personal use* — they must still meet the technical limits "to the greatest extent practicable" [1]. Amateur-band equipment needs no equipment authorisation at all (Part 97 has none).
- **Modular approval (§15.212)**: a module grant requires its own shielding, buffered data inputs, own supply regulation, an antenna that is **permanently attached or uses a unique coupler** (§15.203/§15.204), stand-alone testing, and a label; hosts then show "Contains FCC ID: …" [1]. **A module sold with a standard SMA connector cannot meet the unique-coupler requirement** for a full modular grant — treat vendor "FCC certified" claims on SMA "D" modules as unverified until you find the grant on the FCC database.
- **Antennas (§15.204(c))**: an authorised radiator may be used only with antennas of the authorised type; **same type and equal-or-lower gain is allowed without retest**; a different type or higher gain requires a permissive change (§2.1043) by the grantee [1][2]. Adding an external PA to a Part 15 radio is prohibited except as an authorised system (§15.204(a),(b)).
- **Permissive changes (§2.1043)**: Class I (no degradation, no filing), Class II (degradation within limits, grantee files test data), Class III (SDR software changes to frequency/modulation/power); changes to frequency-determining circuitry, modulator or maximum power need a new grant [2]. Software changes that don't affect emissions need no filing.
- **EU (RED 2014/53/EU)** [3]: essential requirements Art. 3(1)(a) safety/health, 3(1)(b) EMC, **3(2) efficient spectrum use**; conformity by Annex II (internal production control, if harmonised standards such as EN 300 220-2 are fully applied), else Annex III/IV (notified body); CE marking and EU declaration of conformity; documentation kept 10 years (Art. 10). **Annex I excludes equipment used by radio amateurs unless made available on the market**, including kits assembled by amateurs, equipment modified by amateurs, and equipment built by individual amateurs for experimental purposes; and custom-built evaluation kits for professionals at R&D facilities.
- **Singapore**: registration is a **supplier obligation before sale/hire** (IMDA Guide EQR: ESER self-declaration for TS SRD Table 1 devices, GER for Table 2; **standalone modules sold separately need registration**); own-use imports must comply with the TS before use; individual approval of personal imports was discontinued [4][5]. Amateur equipment must be approved by IMDA as part of the licence [6].
- **Test modes decide how smooth the lab day is**: the lab needs firmware that holds a fixed channel (low, mid and high), each power step, a CW carrier, continuous modulated TX at ≥ 98 % duty (or a stated duty for a 10 log(1/D) correction) and continuous RX. SX126x has `SetTxContinuousWave` and `SetTxInfinitePreamble` commands [8]; EBYTE UART modules document no CW mode (unverified), so plan around back-to-back packets. The pre-scan and failed-test workflow is in [EMC pre-compliance](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md#conducted-and-radiated-pre-compliance) ([§ radio test modes](#radio-test-modes-and-the-lab-day)).
- **Integrating a certified module does not certify the product** for unintentional emissions (the host's digital circuits) or for antenna/power changes — and certification never overrides the operating rules (a certified 1 W 915 MHz module still breaks Singapore's 100 mW LPWAN limit).

## Intuition (no math)
Two different questions are always being asked: **"May this product be sold here?"** (certification, type approval, registration, CE) and **"May this transmission be made here?"** (spectrum rules, licences). A module certificate answers the first question only for that module, only with its tested antennas and power settings, and only in the jurisdiction that issued it. Our flight computers are not sold, so the second question dominates — but certification concepts still matter because (a) competitions and customs sometimes ask, (b) exemption rules often assume certified equipment (IMDA's SRD regime is enforced through registration against TS SRD), and (c) the test methods behind certification are exactly the pre-compliance tests we should run.

## The math
### Level 1 — what a test lab measures (and what we can pre-measure)
| Parameter | Typical method | Relevant limit |
|---|---|---|
| Conducted output power | power meter / spectrum analyser channel power via attenuator | FCC §15.247(b); IMDA/EU via e.r.p. |
| Radiated power (e.r.p./EIRP) | substitution method on a range; or conducted + antenna gain | IMDA TS SRD Table 1; EU SRD decision |
| Occupied bandwidth (6 dB, 20 dB, 99 %) | spectrum analyser, RBW ≈ 1–5 % of BW | §15.247(a) (DTS 6 dB ≥ 500 kHz; FHSS 20 dB); IMDA 30a 400 kHz |
| Peak PSD | analyser PSD in 3 kHz | §15.247(e) 8 dBm/3 kHz; AU 25 mW/3 kHz |
| Spurious / harmonics | analyser, preselector/notch at fundamental | IMDA Table 1-a (−36/−54/−30 dBm); §15.209; RED via EN 300 220 |
| Frequency error/drift | counter or analyser, over temperature | EN 300 220; amateur band edges |
| Duty cycle / dwell | time-domain capture | EU/IMDA duty; FCC dwell 0.4 s |
| Receiver blocking (EU) | EN 300 220-1 receiver categories | RED 3(2) |

### Level 2 — the antenna-gain arithmetic behind §15.204(c)(4)
If a module was tested with a 2 dBi dipole at 30 dBm conducted, the tested EIRP was 32 dBm. A 5 dBi collinear of the same type would raise EIRP to 35 dBm: not allowed without a permissive change, even though §15.247 itself would allow up to 36 dBm EIRP — because the *grant* only covers what was tested.

### Level 3 — why modules with SMA connectors are awkward
§15.212(a)(1)(iv) makes the §15.203 antenna rule apply to modules with no "professional installation" escape (that escape exists only for limited modular approvals) [1]. A standard SMA lets any user attach any antenna, so full modular approval is unavailable; vendors of SMA-equipped modules may hold test reports or limited approvals. Always search the FCC Equipment Authorization database for the claimed FCC ID and read the grant conditions (antenna list, power, "for OEM integration only", limited-modular notes).

## Design equations & rules of thumb
| Situation | Rule |
|---|---|
| Same antenna type, ≤ gain | OK under the grant (§15.204(c)(4)) |
| Higher gain or different type | grantee Class II permissive change or new grant (§15.204(c)(4), §2.1043) |
| External PA on Part 15 radio | prohibited unless authorised as a system (§15.204(a),(b)) |
| Host with certified module | host label "Contains FCC ID"; host still needs Part 15B unintentional-emission compliance |
| ≤ 5 home-built, not a kit, not sold | no FCC authorisation; must meet limits (§15.23) |
| Amateur transmitter | no FCC equipment authorisation; SG: IMDA approval via licence |
| Sale in EU | RED conformity + CE + DoC; amateur-built and R&D evaluation kits excluded (Annex I) |
| Sale in Singapore | dealer's licence + registration (ESER for TS SRD Table 1) |

## Worked examples
**1. Our E22-400T33D flight radio, Singapore.** Not sold → no registration duty. But operating it needs a licence (it cannot meet TS SRD limits at any of its power steps) — certification status is irrelevant ([Singapore page](singapore-imda-rules.md)).

**2. The E220-900T30D at IREC (USA), Mode A.** Not marketed, one or two units, built into our own flight computer → §15.23 home-built status is arguable (the radio is a purchased module, not a kit, integrated by us). It must still meet §15.247 DTS limits: 6 dB BW ≥ 500 kHz, ≤ 1 W, ≤ 8 dBm/3 kHz, ≤ 6 dBi antenna, harmonics per §15.209/§15.247(d). Bring measurement plots.

**3. A vendor's "FCC" E22-900T30D on an SMA.** Even if a grant exists, a fixed-channel 125 kHz LoRa configuration at 1 W is not a §15.247 mode (needs hopping or ≥ 500 kHz); the grant would only cover the modes tested. Configuration, not the sticker, decides compliance.

**4. Selling five spare flight computers to another team.** Now it is marketing: US — needs authorisation (§15.23 no longer applies); SG — dealer's licence and registration; EU — RED conformity and CE. Don't.

## Practical notes — pre-compliance on a student budget
- **Conducted tests first**: module → 30–40 dB attenuator → spectrum analyser (or SDR with a calibrated attenuator chain for relative measurements). Measure power, 6/20 dB bandwidth, PSD, harmonics to 5–10× the carrier (a 433 MHz 2nd harmonic at 866 MHz lands in someone else's SRD band).
- **Radiated sanity check**: known-gain reference antenna at a fixed distance outdoors; compare with conducted + antenna gain.
- **Temperature**: repeat frequency-error measurement cold/hot (LoRa crystal drift, see [impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md)).
- **Standards used by labs**: ANSI C63.10 (US unlicensed test methods, referenced by IMDA TS SRD), ETSI EN 300 220-1/-2 (25–1000 MHz SRD), EN 300 328 (2.4 GHz), EN 301 489-1/-3 (EMC) [4].
- **Keep a compliance file** per radio: configuration, firmware hash, measurement plots, antenna datasheets — the same file answers competition RF officers, customs and IMDA queries.

## Radio test modes and the lab day
*Added 2026-10-13 (W5-S16, G-13-03).*

**Why test modes exist.** Every certification measurement assumes the transmitter is in a defined, repeatable state. Normal LoRa telemetry gives a short burst every few seconds, on whatever channel the firmware chose, at a power the link needs. That state cannot be measured repeatably. The lab therefore asks the manufacturer, here the team, for a way to command these states:

| State | Used for | How on Space Bar hardware |
|---|---|---|
| Fixed channel: lowest, middle, highest in the band | all TX tests are repeated at band edges | firmware command / serial menu; the E22/E220 channel register |
| Each power step | max-power tests plus the lowest step | 33/30/27/24 dBm (E22), 30/27/24/21 dBm (E220) |
| CW carrier (unmodulated) | frequency error and drift, harmonics, spurious emissions | SX126x `SetTxContinuousWave` [8]; a bare SX1262 board if the module hides it |
| Continuous modulated TX, duty ≥ 98 % | occupied bandwidth, PSD, average power | SX126x `SetTxInfinitePreamble` gives a continuous chirp signal; otherwise back-to-back maximum-length packets with the duty measured and reported, so the lab can apply $10\log(1/D)$ to average readings (from knowledge — confirm with the lab) |
| Each modulation setting (SF, BW, CR, data rate) | worst case per test | a table of all configurations the product can use |
| Continuous RX | receiver spurious emissions; EU receiver blocking (EN 300 220-1 categories) | radio held in RX on a fixed channel |
| "Normal operation" with all digital subsystems active | unintentional (Part 15B / CISPR 32) emissions from the host | flight firmware with SD logging, sensors and USB as in use |

All of these modes radiate. **Use them conducted** (into pads and a dummy load), in a shielded room, or within the band limits in force ([Singapore rules](singapore-imda-rules.md)). A CW test mode at 33 dBm on an antenna is not a legal Singapore SRD emission.

**The lab also needs the highest internal frequency.** It sets how far up the radiated scan goes. The FCC rule (47 CFR §15.33 [9], checked 2026-10-13) works like this. For an **intentional radiator below 10 GHz**, the scan goes to the **10th harmonic** of the highest fundamental or 40 GHz, whichever is lower; at 10–30 GHz to the 5th harmonic or 100 GHz. For the **unintentional (digital) part**, the limit follows the highest frequency generated or used: below 1.705 MHz → 30 MHz; 1.705–108 MHz → 1 GHz; 108–500 MHz → 2 GHz; 500–1000 MHz → 5 GHz; above 1 GHz → 5th harmonic or 40 GHz. A 433 MHz LoRa board is therefore scanned to ≈ 4.3 GHz for the transmitter. Its 240 MHz ESP32 clock alone would need a scan to 2 GHz. So list every crystal, PLL and clock: ESP32 40 MHz/240 MHz, SD, USB, the switcher, and the radio TCXO and LO.

**Bring to the lab:**
- Two units. One should be a *conducted sample* with an SMA or U.FL test port in place of the antenna, plus the cable.
- The real antennas, with their data sheets (gain, type).
- The test-mode command sheet, a laptop with the serial tool, and spare batteries or a bench supply with the flight harness.
- A block diagram, the frequency list above, and the configuration list.
- Your own pre-scan plots, with cable-layout photos.
- Ferrites, copper tape, spare capacitors and resistors for on-site debugging.

**If it fails:** get the failing frequency, detector, polarisation and antenna height. Divide the frequency by your clock list. Then follow the [failed-test workflow](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md#from-a-failed-test-to-a-fix--workflow) (board or cable → localise → cheapest fix first → retest relative to the same baseline).

## Common mistakes & misconceptions
- **"We'll just transmit normal telemetry at the lab."** Without fixed-channel, CW and continuous modes the lab cannot measure repeatably, and duty-cycle-averaged readings will be challenged. Write the test-mode firmware first.
- **"The module is certified, so my board is certified."** Only if you meet every grant condition (antenna, power, label, host emissions).
- **"CE on the module means legal in Singapore."** CE is EU market access; Singapore uses TS SRD and IMDA registration.
- **"Certification makes any configuration legal."** Operating rules still apply (power, band, duty, hopping).
- **"Swapping to a bigger antenna is fine because the transmitter power is unchanged."** EIRP rises; the grant and the spectrum rules both care.
- **"RED doesn't apply because it's a prototype."** RED obligations attach to placing on the market *and* putting into service; a team-built one-off operated at EuRoC is arguably put into service in the EU. The clear exclusions are equipment built/modified by radio amateurs for amateur use and custom-built R&D evaluation kits for professionals (Annex I). Either way the EU spectrum conditions apply to its operation, and giving units to others is placing on the market.

## How to simulate / verify
- `python3 tools/verify/reg_erp_compliance.py` — e.r.p./EIRP vs limits for each power step and antenna.
- FCC Equipment Authorization Search (FCC ID lookup) to check module grants; IMDA IRIS Equipment Search for Singapore registrations [4].

## Open questions / gaps
- Whether EBYTE's E22/E220 "D" (SMA) modules hold FCC grants, and on what conditions — not verified.
- FCC KDB 996369 (modular integration guidance) and KDB on home-built/modular devices — not read.
- RED Article 3(3)(d)(e)(f) cybersecurity delegated act and its applicability to LoRa modules — not read here.
- ACMA supplier obligations (RCM, Radiocommunications Equipment (General) Rules) — not researched.
- The duty-cycle correction practice (FCC KDB 558074) is stated from knowledge (a search on 2026-10-13 did not reach the KDB text); the §15.33 upper-frequency rule was checked against the CFR text on 2026-10-13 and corrected (the old wording said "5th harmonic" for intentional radiators; below 10 GHz it is the 10th); EBYTE's lack of a CW test mode is unverified (manual not searched for undocumented commands).

## Sources
1. 47 CFR Part 15, eCFR current (read 2026-09-27): §§15.1, 15.19, 15.21, 15.23, 15.203, 15.204, 15.212, 15.247. https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15 (regulation)
2. 47 CFR §2.1043 Changes in certificated equipment, eCFR current (amendments 90 FR 38070 and 91 FR 57801 pending at time of reading). https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-2 (regulation)
3. Directive 2014/53/EU (Radio Equipment Directive), Arts. 3, 10, 17; Annex I (equipment not covered), Annex II (Module A). https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32014L0053 (EU law)
4. IMDA, *Guide for Registration of Telecommunication Equipment*, IMDA GUIDE EQR Issue 1 Rev 13 (Mar 2026), §2.2, §3.2, Annex B; IMDA TS SRD Issue 1 Rev 3 (Sep 2023) §2 references. (regulator guide/standard) — see [Singapore page](singapore-imda-rules.md) sources 3, 9.
5. IMDA, "Requirement for Import of Telecommunication Equipment" (23 May 2024). (regulator web)
6. IMDA, *Amateur Radio Handbook*, 5th ed. (21 Nov 2025) §3.4.1(d). (regulator handbook)
7. EBYTE product pages claiming "CE, FCC, RoHS" for E22-900T30D/E220-900T30D (vendor claim, unverified). https://ebyteiot.com/products/e220-900t30d-ebyte-llcc68-10km-long-distance-wireless-transmitter-module-915mhz-lora-rf-module (vendor — unverified)
8. Semtech, *SX1261/2 Data Sheet* rev 2.x, §13 command list — `SetTxContinuousWave` (opcode 0xD1, continuous unmodulated carrier) and `SetTxInfinitePreamble` (0xD2, continuous preamble), intended for test. (data sheet; from knowledge — see [Semtech chip family](../15-lora-ism-radios/semtech-chip-family.md))
9. US Code of Federal Regulations, 47 CFR §15.33 "Frequency range of radiated measurements", (a)(1)–(a)(4) intentional radiators and (b)(1) table for unintentional radiators, as published by the Cornell LII (law.cornell.edu/cfr/text/47/15.33), read 2026-10-13. (regulation)
