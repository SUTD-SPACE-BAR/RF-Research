# 19-regulations-safety — Radio regulations, licensing, certification and RF safety

Scope: what the team may legally transmit, where, at what power and under which licence —
Singapore first (Telecommunications Act, Exemption Notification, IMDA TS SRD, amateur, experimental,
temporary and localised-station routes, equipment registration), then the places the team launches
(USA/IREC at Spaceport America, EU/Portugal/EuRoC, Australia); how certification (FCC, CE/RED, IMDA)
relates to operating rules; human RF exposure limits and safe distances; and lab safety for RF work,
including RF-induced ignition of igniters (HERO). Engineering numbers for LoRa timing and band plans are
in [15-lora-ism-radios](../15-lora-ism-radios/ism-band-plans-duty-cycle.md); this domain owns the legal
interpretation.

> **Everything here is informational, not legal advice.** Each page carries a "last verified" date
> (2026-09-27); rules and competition band plans change — re-read the cited clause before relying on it.

Reader context: Space Bar flies an EBYTE **E22-400T33D** (433 MHz, 2 W) on the primary flight computer
and an **E220-900T30D** (900 MHz band, 1 W) on the secondary; RTK corrections have used a separate
ground-to-rocket LoRa bridge.

## The priority answer (Singapore)
At rated power **neither module is licence-exempt in Singapore**: the exemption stops at **10 mW e.r.p.**
at 433.05–434.79 MHz, **100 mW e.r.p. with ≤ 1 % duty** for LoRa end devices at 917–925 MHz, and
**500 mW e.r.p.** at 866–869 MHz (no duty stated; band under refarm review). The E220 can be made exempt
at 866–869 MHz (≤ 24–27 dBm with a dipole) or 917–925 MHz (21 dBm lowest step + ≥ 1 dB pad, 1 %); the E22-400T33D cannot
(lowest step 24 dBm is 13.5 dB over). Full power needs an **amateur licence** (430–440 MHz, ≤ 10 W ERP,
IMDA's prior written consent, no encryption, callsign), a **Temporary Use of Radio Frequency Permit**
(≤ 90 days), an **Experimental Station Licence** (institution, ≥ 1 year) or a **Localised
Radio-communication Station Licence**. Details and clauses: [singapore-imda-rules](singapore-imda-rules.md).

## Reading order (beginner → advanced)
1. [spectrum-allocation-ism-bands](spectrum-allocation-ism-bands.md) — ITU regions, ISM vs SRD, primary/secondary, radar and protected bands.
2. [singapore-imda-rules](singapore-imda-rules.md) — the law, TS SRD tables, our two radios, licence routes, compliance checklist.
3. [amateur-radio-licensing](amateur-radio-licensing.md) — Singapore amateur licence and FCC Part 97 for rocket telemetry.
4. [international-rules-for-competitions](international-rules-for-competitions.md) — IREC/Spaceport America, EuRoC/EU, Australia.
5. [certification-fcc-ce-imda](certification-fcc-ce-imda.md) — FCC ID/modular approval, CE/RED, IMDA registration, antennas, pre-compliance.
6. [rf-exposure-safety](rf-exposure-safety.md) — ICNIRP 2020, FCC MPE, SAR, safe distances.
7. [lab-safety-esd-high-power](lab-safety-esd-high-power.md) — ESD, no-load TX, receiver overload, batteries, e-match RF hazards.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [spectrum-allocation-ism-bands](spectrum-allocation-ism-bands.md) | RR 5.138/5.150 ISM (433 ISM is Region 1 only; 902–928 Region 2 only), 5.276 Singapore 430–440 fixed/mobile primary, SRD summary by country, radar bands, RR 5.340 passive and GNSS bands | intro | high |
| [singapore-imda-rules](singapore-imda-rules.md) | Telecom Act ss53–56, 85; Exemption Notification Sch. 1; TS SRD Iss. 1 Rev 3 (Sep 2023) Table 1/1-a/2; e.r.p. vs e.i.r.p.; priority-question resolution with margins; amateur/temporary/experimental/localised licences with fees; registration (EQR); checklist | mixed | high |
| [amateur-radio-licensing](amateur-radio-licensing.md) | SG Rg 5 regs 37–44 + Handbook 5th ed. (RAE, classes, 70 cm 10 W ERP, no encryption, callsign, logbook, emission-class question); FCC Part 97 (telemetry, automatic control, ID, SS 10 W, 100 kHz data BW, NM 50 W, no 33 cm at Spaceport America, space station > 50 km, reciprocity) | mixed | high |
| [international-rules-for-competitions](international-rules-for-competitions.md) | IREC DTEG 2026 V1.1 + SBP Rev D (33 cm Modes A/B/C, 70 cm SRAD ≤ 200 mW/125 kHz), Part 15 (15.231/15.247/15.249), SBP-vs-97.303(n)(2) conflict; EU 2025/105 SRD table; EuRoC 2026 SRD/CR radio requirements; ACMA LIPD 2025; travel notes | mixed | high |
| [certification-fcc-ce-imda](certification-fcc-ce-imda.md) | 15.23 home-built, 15.203/15.204 antennas, 15.212 modular approval, 2.1043 permissive changes, RED Arts 3/10/17 and Annex I exclusions, IMDA ESER/GER, pre-compliance tests | intermediate | medium |
| [rf-exposure-safety](rf-exposure-safety.md) | **RF is non-ionising** (photon energy 1.8 µeV at 433 MHz vs ≈ 12.4 eV ionisation boundary; heating as the mechanism), ICNIRP 2020 Tables 2/5/6, FCC 1.1310 Table 1 and 1.1307 exemption, OET-65 model, near-field validity, safe distances for our radios (2 W + 12 dBi Yagi: 1.0 m / 1.6 m) | mixed | high |
| [lab-safety-esd-high-power](lab-safety-esd-high-power.md) | HBM classes, LNA ESD/overload example, no-load TX, RF burns, MIL-STD-464C 16.5 dB EID margin, IME SLP-20 distances, e-match pickup bound (reproduces SLP-20), avionics-bay RF test, lithium batteries | mixed | medium |
| [regulatory-faq-misc](regulatory-faq-misc.md) | NextNav 902–928 MHz (NOI FCC 25-20; status 2026-10-12; channel arithmetic), Baofeng/DA 18-980 and SG walkie-talkies, hobby radar (§15.245/15.249 EIRP, Part 97 pulse bands), jammers, GNSS simulators, home FM/TV, 1 W mesh nodes, open §15.247 question for 250 kHz LoRa, CE self-declaration, per-radio licence table | intro | medium |

Verification scripts: `tools/verify/reg_erp_compliance.py` (e.r.p./EIRP margins vs SG/EU/AU/US limits,
field-strength → EIRP, PSD caps, duty intervals), `tools/verify/reg_rf_exposure.py` (ICNIRP/FCC limits and
safe distances), `tools/verify/reg_hero_distance.py` (igniter RF pickup bound vs IME SLP-20).

## Domain FAQ (top questions → page#section)
- Is my 2 W 433 MHz LoRa module legal in Singapore? → [singapore-imda-rules#resolution-of-the-priority-question](singapore-imda-rules.md)
- Which channel/power makes the E220-900T30D licence-exempt in Singapore? → [singapore-imda-rules#resolution-of-the-priority-question](singapore-imda-rules.md)
- How do I get a Singapore ham licence and what does it allow on 70 cm? → [amateur-radio-licensing#singapore-amateur-licence-in-detail](amateur-radio-licensing.md)
- Can IMDA give us a temporary permit for a test campaign? → [singapore-imda-rules#licence-and-permit-routes](singapore-imda-rules.md)
- What can a Singapore team fly at the Spaceport America Cup? → [international-rules-for-competitions#usa--spaceport-america-cup--irec-2026](international-rules-for-competitions.md)
- Is a fixed-channel 915 MHz LoRa link legal in the US at 1 W? → [international-rules-for-competitions#tldr](international-rules-for-competitions.md)
- What are the EU 868 MHz and 433 MHz limits for EuRoC? → [international-rules-for-competitions#eu--portugal--euroc](international-rules-for-competitions.md)
- Does antenna gain count? → [singapore-imda-rules#the-math](singapore-imda-rules.md), [certification-fcc-ce-imda#level-2](certification-fcc-ce-imda.md)
- Is encryption allowed on amateur telemetry? → [amateur-radio-licensing#tldr](amateur-radio-licensing.md)
- How far should people stay from a 2 W transmitter on a Yagi? → [rf-exposure-safety#worked-examples](rf-exposure-safety.md)
- Is RF radiation ionising like X-rays? Can LoRa, Wi-Fi or 5G damage DNA? → [rf-exposure-safety#rf-is-non-ionising--photon-energy-vs-the-ionisation-threshold](rf-exposure-safety.md#rf-is-non-ionising--photon-energy-vs-the-ionisation-threshold); beginner version: [00/rf-concepts-for-beginners §10](../00-math-foundations/rf-concepts-for-beginners.md#10-why-rf-is-non-ionising)
- Can our telemetry radio fire the e-matches? → [lab-safety-esd-high-power#worked-examples](lab-safety-esd-high-power.md)
- Is 433 MHz an ISM band? → [spectrum-allocation-ism-bands#tldr](spectrum-allocation-ism-bands.md)
- Why are exposure limits strictest at 30–300 MHz, and am I exempt on HF? → [rf-exposure-safety § rule details](rf-exposure-safety.md#rule-details--body-resonance-several-transmitters-who-is-responsible-hf-exemptions)
- How far up must the FCC radiated scan go for my board? → [certification-fcc-ce-imda § lab day](certification-fcc-ce-imda.md#radio-test-modes-and-the-lab-day)

## Key references (→ [_sources.md](_sources.md))
Singapore Telecommunications Act 1999 and subsidiary legislation (SSO); IMDA TS SRD Iss. 1 Rev 3 (Sep 2023);
IMDA Amateur Radio Handbook 5th ed. (Nov 2025); IMDA IRIS licence pages; IMDA GUIDE EQR Rev 13 (Mar 2026);
47 CFR Parts 1, 2, 15, 18, 97 (eCFR); ESRA IREC DTEG 2026 V1.1 and Student Band Plan Rev D; EU
Decision 2006/771/EC as amended by (EU) 2025/105; Directive 2014/53/EU; EuRoC 2026 SRD/CR; ACMA LIPD
Class Licence 2025; ICNIRP 2020; FCC OET-65; MIL-STD-464C; IME SLP-20; Tschurlovits (IAEA-CN-67/153, 1997) on ionising-radiation definitions.

## Known gaps
- IMDA written positions needed: LoRa class at 917–925 MHz (30b vs 30c); rocket telemetry as "tracking, tracing and data acquisition" at 866–869 MHz; LoRa (data/chirp) emission on 70 cm under an amateur licence; 866–869 MHz refarm timetable.
- "Technical Trial (with use of Frequency)" licence conditions (page did not render).
- Whether EBYTE E22/E220 SMA modules hold FCC grants; FCC position on LoRa as SS vs data under Part 97.
- Portugal/ANACOM amateur route for Singapore licensees; national 915–921 MHz status in Portugal.
- Australian amateur class licence and visiting-operator rules; LIPD definition of "digital modulation".
- Other Asian launch venues not covered; ERC Rec 70-03 itself not read (CEPT server unreachable — EU Decision used).
- E-match no-fire ratings for the team's igniters; MIL-HDBK-240A procedures not read directly.
