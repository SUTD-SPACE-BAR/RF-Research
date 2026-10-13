---
title: Regulatory FAQ (miscellaneous) — the NextNav 902–928 MHz proposal (status 2026), Baofeng and uncertified handhelds (US and Singapore), radar licensing for hobbyists, jammers, home FM/TV transmitters, GNSS simulators, 1 W mesh nodes, Part 15 questions about LoRa, and why noisy products carry a CE mark
domain: 19-regulations-safety
slug: regulatory-faq-misc
tags: [regulation, fcc, imda, nextnav, 902-928, wt-25-110, m-lms, part-15, 15.247, 15.249, 15.245, 15.239, part-97, part-90, part-95, baofeng, uv-5r, da-18-980, pmr446, radar-licensing, field-disturbance-sensor, jammer, gnss-simulator, meshtastic, ce-marking, market-surveillance]
prerequisites:
  - spectrum-allocation-ism-bands.md
  - singapore-imda-rules.md
  - amateur-radio-licensing.md
related:
  - certification-fcc-ce-imda.md
  - international-rules-for-competitions.md
  - ../15-lora-ism-radios/ism-band-plans-duty-cycle.md
  - ../15-lora-ism-radios/lora-mesh-capacity-and-congestion.md
  - ../11-radar/diy-radar-hardware.md
  - ../11-radar/radar-applications-gpr-through-wall-sensing.md
  - ../21-gnss/gnss-interference-jamming-spoofing.md
level: intro
confidence: medium
last_updated: 2026-10-12
---

# Regulatory FAQ (miscellaneous)

> **Not legal advice; last verified 2026-10-12.** This page collects regulatory questions from the forum sweeps (D2/D3) that the other domain-19 pages do not answer directly. Rules change; the NextNav item in particular is a live proceeding. Re-read the cited rule or docket before relying on any answer. Statements that are interpretations are labelled as such.

## Questions this page answers
- What is the NextNav proposal for 902–928 MHz, why does it threaten LoRa, and where does it stand in 2026?
- Will proposed FCC changes to 902–928 MHz break LoRa meshes and US rocket telemetry?
- Are Baofeng UV-5R radios illegal? Can I use one in the US or in Singapore?
- Why can a ham handheld not be used on FRS/GMRS/PMR channels even though it can tune there?
- Can an amateur licence make a home-built radar legal? Is a 20 km hobby radar legal to operate?
- Can I build a 2.4 GHz radar from Wi-Fi parts, and is it legal?
- Are signal jammers legal for testing, or for finding who is jamming us?
- Can I run a small home FM or analog TV transmitter?
- Can I transmit a simulated GPS signal (gps-sdr-sim) to test our GNSS receiver?
- Is a 1 W LilyGO T-Beam (or a PA board) legal on a Meshtastic mesh?
- Under which US rule does non-hopping 250 kHz LoRa at 30 dBm operate?
- How did an obviously noisy product pass CE certification?
- Which licence does each of our team's radios need in Singapore and the USA?
- Is encryption allowed on our telemetry link?
- Where do I report interference, and what evidence should I collect first?

## TL;DR
- **NextNav (US 902–928 MHz)**:
  - NextNav petitioned the FCC in April 2024 (RM-11989, WT 24-240) to reconfigure the lower 900 MHz band for a terrestrial 5G positioning (PNT) network. It would hold 902–907 MHz uplink and 918–928 MHz downlink, leaving **907–918 MHz (11 of 26 MHz)** for everyone else, Part 15 included [1][2].
  - The FCC opened a **Notice of Inquiry** (FCC 25-20, WT 25-110, adopted 27 Mar 2025) [1].
  - A draft NPRM was reported to be at OMB review in March 2026 [2], but **as of 2026-10-12 we found no adopted NPRM and no rule change**. Over 2 000 comments have been filed, largely opposed [2].
  - Nothing changes for LoRa users unless a rule is adopted. If it were, 500 kHz hybrid/DTS LoRa could not keep 25 hopping channels in 11 MHz (only 22 fit), and high-power PNT transmitters would share the band.
- **Baofeng-class handhelds**:
  - **US**: a radio that can transmit outside the amateur bands must be FCC-certified for the service it is used in before it may be imported, advertised, sold *or used*. Only radios capable *only* of amateur frequencies are exempt (FCC Enforcement Advisory DA 18-980) [3]. A licensed ham may use an amateur-only radio on amateur bands. Nobody may use a UV-5R on FRS, GMRS, business (Part 90) or public-safety channels.
  - **Singapore**: licence-free walkie-talkies are low-power, type-approved 446 MHz devices [4]. A 4–8 W handheld exceeds that by roughly 9–12 dB and is legal only under an **amateur station licence** on amateur frequencies with IMDA's conditions ([amateur licensing](amateur-radio-licensing.md)), or under another licence.
- **Hobby radar**:
  - **US**: licence-exempt radar uses Part 15 field-disturbance-sensor rules. §15.245 allows 902–928, 2435–2465 and 5785–5815 MHz at 500 mV/m at 3 m (**18.8 dBm EIRP**), and 10.50–10.55 and 24.075–24.175 GHz at 2500 mV/m (**32.7 dBm EIRP**). §15.249 allows 24.0–24.25 GHz at 250 mV/m (12.7 dBm) [5].
  - Under Part 97, **pulse** emissions are authorised only on 33 cm, 13 cm, 5 cm, 1.2 cm and the mm bands, not on 70 cm, 23 cm or 3 cm [6]. Station identification rules apply. Whether continuous FMCW "radiolocation" is an amateur activity is an interpretation question; we found no FCC ruling.
  - **Singapore**: radar-type SRD bands at 10.50–10.55, 24.00–24.25 (no radar guns), 57–64 and 76–77 GHz ([Singapore rules](singapore-imda-rules.md)).
- **Jammers** are illegal to use (and in the US to market) for private persons in both the US and Singapore, testing and "finding the jammer" included [7][8]. Test receivers in a shielded box or by conducted injection instead ([GNSS interference](../21-gnss/gnss-interference-jamming-spoofing.md)).
- **GNSS simulators** (gps-sdr-sim on a HackRF): **never radiate**. Use a cable with ≥ 60–90 dB of attenuation, or a shielded enclosure. Transmitting in the RNSS bands is prohibited ([spectrum allocation](spectrum-allocation-ism-bands.md)).
- **1 W mesh nodes**:
  - Singapore 917–925 MHz LoRa end devices are limited to **100 mW e.r.p., ≤ 1 % duty** (TS SRD 30c, canonical), and Meshtastic's SG_923 preset (20 dBm, 100 %) does not enforce the duty cycle ([mesh page](../15-lora-ism-radios/lora-mesh-capacity-and-congestion.md)).
  - In the US, Meshtastic's region preset allows 30 dBm at 100 % duty [9]. The Part 15 basis of *non-hopping 250 kHz* LoRa at that power is an **open question** here (Level 2).
- **Home FM/TV transmitters**: US §15.239 allows only 250 µV/m at 3 m (≈ −47 dBm EIRP) in 88–108 MHz. Hobby kits at tens of mW are about 60 dB over. There is no licence-free home broadcast provision in Singapore.
- **Encryption** is banned on amateur bands in both countries, including EBYTE "key" scrambling.
- **CE marks on noisy products** are mostly *self-declared* (RED/EMC Module A internal production control). Enforcement is by market surveillance after the fact ([certification](certification-fcc-ce-imda.md)).

## Intuition (no math)
Spectrum rules answer two separate questions: **may this device be sold here** (equipment authorisation, certification, registration) and **may this person transmit this signal here** (licence or licence exemption). Most forum confusion comes from mixing them up:
- A ham licence lets *you* transmit on amateur bands with almost any equipment, but it does not make a radio legal to *sell*.
- A certified module is legal to sell, but that does not make *your* configuration (power, antenna, duty cycle) legal to operate.

The other recurring theme is **shared bands are not owned**. Licence-exempt users of 902–928 MHz (LoRa, RFID, meters) have never had protection from interference. The band's primary users are federal radiolocation, ISM equipment and licensed location services (M-LMS, where NextNav holds licences). That is why a petition to re-plan the band can threaten millions of unlicensed devices without taking away any "right" they legally held. It is also why the hobby and industry response is to comment in the docket, the only lever unlicensed users have.

## The math

### Level 1 — converting field-strength limits to EIRP
US Part 15 limits are often written as field strength $E$ (V/m) at a distance $r$ (usually 3 m). For an isotropic radiator, $S = \text{EIRP}/(4\pi r^2) = E^2/\eta_0$ with $\eta_0 \approx 120\pi$ Ω, so
$$\text{EIRP} = \frac{E^2 r^2}{30}\ \text{W}.$$

| Rule (3 m) | $E$ | EIRP |
|---|---|---|
| §15.209 general, above 960 MHz | 500 µV/m | −41.2 dBm |
| §15.239 FM band 88–108 MHz | 250 µV/m | −47.3 dBm |
| §15.249 902–928 / 2400–2483.5 / 5725–5875 MHz | 50 mV/m | −1.2 dBm |
| §15.249 24.0–24.25 GHz | 250 mV/m | 12.7 dBm |
| §15.245 field-disturbance sensors, 902–928 / 2435–2465 / 5785–5815 MHz | 500 mV/m | 18.8 dBm |
| §15.245 FDS, 10.50–10.55 / 24.075–24.175 GHz | 2500 mV/m | 32.7 dBm |

These are average limits. Part 15 allows peak emissions 20 dB above the average limit (§15.35). Harmonic limits are separate [5]. (`e10_regulatory.py` reproduces the column.)

### Level 2 — two US 900 MHz questions worked through

**(a) Hopping channels left if Part 15 were squeezed into 907–918 MHz.** §15.247 frequency-hopping systems in 902–928 MHz need at least 50 hopping channels if the 20 dB bandwidth is below 250 kHz, or at least 25 if it is 250 kHz or more, with channel separation at least the 20 dB bandwidth ([band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md)). Counting channels in 11 MHz:
- 125 kHz → 88 channels (needs 50): fits.
- 200 kHz → 55 (needs 50): fits.
- 250 kHz → 44 (needs 25): fits.
- 500 kHz → 22 (needs 25): **does not fit**.

Narrow LoRa hopping survives the arithmetic. Wide hybrid systems, and RAIN RFID's 500 kHz channels, do not, unless the rules change too [2]. Co-channel interference from high-power PNT transmitters is a separate question that arithmetic cannot settle.

**(b) The Part 15 basis of fixed-frequency 250 kHz LoRa at 30 dBm** (an *interpretation*, not settled here). §15.247 permits up to 1 W for:
- frequency-hopping systems;
- digital-modulation (DTS) systems with a 6 dB bandwidth of at least 500 kHz;
- hybrids of the two.

A LoRa signal's occupied bandwidth is about its configured BW. A **125 or 250 kHz** LoRa transmission on one fixed frequency is therefore neither hopping nor 500 kHz-wide DTS. If it fell back to §15.249, the limit would be 50 mV/m at 3 m (−1.2 dBm EIRP), and 30 dBm into a dipole would be about **33 dB** over (`e10_regulatory.py`). Meshtastic's US preset allows 30 dBm, 100 % duty, on 250 kHz LongFast [9]. Its docs page does not discuss §15.247 compliance, and we found no FCC statement either way. Certified LoRa modules are typically authorised as DTS (500 kHz modes) and/or FHSS. Using such a module in a non-hopping 125/250 kHz mode at full power is outside those grant modes. Treat this as **unresolved**. Check the module's grant (FCC ID search) for its authorised modes before relying on full power in the US.

### Level 3 — how proceedings work (for following NextNav)
- **Petition for rulemaking** (an RM number). The FCC may then issue a **Notice of Inquiry** (questions only, no proposal), then a **Notice of Proposed Rulemaking** (specific rules, comment rounds), then a **Report and Order** (adopted rules, effective after Federal Register publication), with petitions for reconsideration and court challenges possible.
- NextNav is at the NOI stage (FCC 25-20, comments closed May 2025) [1]. A draft NPRM going to OMB [2] is a step before a Commission vote on the NPRM, not a decision.
- A separate 2026 direct-to-device (D2D) rulemaking (docket 26-169) was reported in August 2026 to be considering, and possibly dropping, the 900 MHz unlicensed band [10] (trade press; not verified in the FCC record).
- Where to follow it: FCC ECFS, dockets **WT 25-110**, **WT 24-240** and **RM-11989**. Anyone can file comments.

**NextNav timeline (as found, 2026-10-12)**:

| Date | Event | Source |
|---|---|---|
| Apr 2024 | NextNav petition to reconfigure the lower 900 MHz band (RM-11989; WT 24-240) | [2] |
| 27–28 Mar 2025 | FCC adopts and releases the PNT Notice of Inquiry, FCC 25-20, WT 25-110 | [1] |
| 28 Apr / 13 May 2025 | NOI comment and reply deadlines | [1] |
| 2025 | NextNav filings (technical study, Part 15 coexistence supplement, Brattle report); strong opposition from utilities, public safety, RFID and unlicensed users | [2] (trade press) |
| Mar 2026 | Draft NPRM reported sent to OMB for interagency review | [2] |
| Jun 2026 | Analyst report: NPRM likely, "far from a done deal" | Comms Daily (snippet) |
| Aug 2026 | Separate D2D NPRM (docket 26-169) reported possibly dropping the 900 MHz band | [10] |
| 17 Sep 2026 | Opposition coalition (SpecTech Alliance) launched; > 2 000 comments on file | [2] |
| 2026-10-12 | No adopted NPRM or rule change found | this page |

**What would change for a rocket or mesh team if the plan were adopted as proposed** (speculative; depends on final rules):
- Telemetry and mesh channels would need to sit in 907–918 MHz, away from the 918–928 MHz high-power downlink, and receivers near PNT towers would face desense ([dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)).
- IREC Mode A (902.0–909.0 MHz) would overlap the proposed 902–907 MHz uplink, so the competition band plan would need revising ([launches abroad](international-rules-for-competitions.md)).
- Wide (500 kHz) hybrid LoRa modes could not meet 25 channels (Level 2a). Narrow hopping would survive.
- Singapore (917–925 MHz) and other countries are unaffected by an FCC rule. Equipment availability and LoRa Alliance US plans (US915) could still shift.

## Design equations & rules of thumb

| Question | Rule | Source |
|---|---|---|
| Field strength ↔ EIRP | $\text{EIRP} = E^2r^2/30$ | Level 1 |
| US radio capable of non-amateur TX | needs FCC certification before import, ad, sale or use; amateur-only radios exempt | DA 18-980 [3] |
| US narrowband land-mobile | 12.5 kHz maximum operational bandwidth (Part 90) | [3] fn. 2 |
| US amateur pulse emission | 33, 13, 5, 1.2 cm and mm bands only | 97.305(c) [6] |
| US hobby radar (licence-free) | §15.245 FDS: 18.8 / 32.7 dBm EIRP; §15.249 24 GHz 12.7 dBm | [5] |
| SG licence-free walkie-talkie | 446 MHz, low power, type-approved | [4] |
| SG LoRa end device 917–925 MHz | 100 mW e.r.p., ≤ 1 % duty | canonical / TS SRD 30c |
| Jammers | prohibited for private use (US and SG) | [7][8] |
| GNSS simulator | conducted only, never radiated | [spectrum](spectrum-allocation-ism-bands.md) |
| 902–928 MHz hopping in 11 MHz | 125–250 kHz OK; 500 kHz cannot reach 25 channels | Level 2 |

## Worked examples

**1. A team member brings a UV-5R to a US launch for recovery coordination.**
- On 2 m and 70 cm amateur frequencies, with a licensed operator, using a unit that is locked to amateur bands or is otherwise compliant: legal under Part 97.
- On FRS/GMRS (462/467 MHz) or a business channel: not legal, because the radio is not certified for those services and FRS needs FRS-certified radios. DA 18-980 also notes that many such radios transmit wideband (25 kHz) where 12.5 kHz is required [3].
- Use FRS radios for the unlicensed crew, or licensed GMRS radios.

**2. The same UV-5R in Singapore.** Licence-free walkie-talkies are low-power 446 MHz type-approved devices [4]; a UV-5R at 4–8 W on VHF/UHF is not one. Options:
- an amateur licence (430–440 MHz ≤ 10 W ERP with IMDA consent per frequency; 144–146 MHz at 25 W PEP per the KB's handbook table), see [amateur licensing](amateur-radio-licensing.md);
- licensed business radio;
- IMDA-approved licence-free sets.

Importing a handheld for own use places the compliance responsibility on the individual ([Singapore rules](singapore-imda-rules.md)).

**3. A 24 GHz FMCW radar for altitude tests in the US.**
- §15.249 (24.0–24.25 GHz, 12.7 dBm EIRP average) covers general devices.
- §15.245 (24.075–24.175 GHz, 32.7 dBm EIRP) covers field-disturbance sensors.
- A 250 MHz sweep fits §15.249's band, but only a 100 MHz sweep fits §15.245's, so range resolution is 0.6 m vs 1.5 m (c/2B).
- A TI/Infineon EVM is usually configured within these, but check the board's grant or the EVM's "not FCC approved, evaluation only" status. Evaluation kits are often exempt only for development use by professionals.
- Under Part 97, 24 GHz (1.2 cm) allows pulse emissions [6], but continuous FMCW as "radiolocation" is an interpretation question. Identify with your callsign if you rely on Part 97.

**4. "We'll find the jammer by building our own."** No. Use passive DF with a directional antenna or KrakenSDR, the body-fade and offset-attenuator techniques ([interference hunting](../17-test-measurement/interference-hunting-and-rf-immunity.md)), and report interference to the regulator (FCC Enforcement Bureau; IMDA).

**5. A 1 W node on a Singapore Meshtastic mesh.** 30 dBm into a 2 dBi antenna is about 29.85 dBm e.r.p., i.e. **≈ 0.97 W e.r.p.**, nearly 10 dB above the 100 mW e.r.p. limit for LPWAN end devices. Even at 20 dBm it must meet 1 % duty, which a ROUTER role usually breaks ([mesh capacity](../15-lora-ism-radios/lora-mesh-capacity-and-congestion.md) example 1). Legal options: ≤ 20 dBm, a role that does not relay, duty-cycle discipline, or an amateur licence on 430–440 MHz with no encryption.

**6. Testing the flight GNSS receiver with gps-sdr-sim.** Set the HackRF to its minimum TX gain, connect it to the receiver through ≥ 60 dB of fixed attenuation (more if the receiver's antenna port is unshielded), and run the setup inside a closed metal box. Never connect an antenna. Even milliwatts radiated in L1 can disrupt aviation and phone GNSS for hundreds of metres.

**7. Which authorisation does each common team radio need?** (A summary; the detailed rules are on the linked pages. *Interpretation*, not legal advice.)

| Radio | Singapore | USA |
|---|---|---|
| E22-400T33D, 433 MHz, up to 2 W | not licence-exempt (10 mW e.r.p. SRD limit); amateur licence on 430–440 MHz, Temporary/Experimental/Localised licence ([SG rules](singapore-imda-rules.md)) | Part 97 on 70 cm with a licensed control operator; IREC 70 cm SRAD ≤ 200 mW unless approved ([launches abroad](international-rules-for-competitions.md)) |
| E220-900T30D, 900 MHz, 1 W | exempt only at reduced power: 866–869 MHz ≤ 500 mW e.r.p., or 917–925 MHz ≤ 100 mW e.r.p. at ≤ 1 % duty | Part 15 §15.247 modes per the module grant; IREC Mode A/B |
| Meshtastic node (crew messaging) | SG_923 at ≤ 20 dBm and ≤ 1 % duty | US preset 30 dBm; Part 15 basis of 250 kHz non-hopping unresolved (Level 2) |
| Baofeng-class handheld | amateur licence on amateur frequencies only | Part 97, amateur frequencies only; never FRS/GMRS/Part 90 |
| FRS/PMR446-class walkie-talkies | IMDA-approved 446 MHz licence-free sets [4] | FRS radios (Part 95B) licence-free; GMRS needs a licence |
| 24 GHz radar module | 24.00–24.25 GHz ≤ 100 mW EIRP SRD (no radar guns) | §15.249 / §15.245 (Level 1 table) |
| HackRF / Pluto used as a transmitter | needs a licence for the band used (amateur, experimental); never GNSS bands | Part 97 within amateur privileges; Part 5 experimental licence otherwise; never GNSS |
| SDR receive-only | receivers exempt ([SG rules](singapore-imda-rules.md)) | no licence needed to receive |

**8. A US IREC team wants Meshtastic for the field crew plus 900 MHz telemetry.**
1. Put telemetry in its IREC-assigned Mode A/B allocation ([launches abroad](international-rules-for-competitions.md)).
2. Run Meshtastic on a frequency slot well away from the telemetry channel, at moderate power. Given the open §15.247 question, 20 dBm is a cautious choice.
3. Keep mesh nodes away from the telemetry ground station (desense: [mesh page](../15-lora-ism-radios/lora-mesh-capacity-and-congestion.md) example 8).
4. Remember the White Sands box prohibits amateur 33 cm, so Meshtastic cannot rely on Part 97 there ([amateur licensing](amateur-radio-licensing.md)).

## Practical notes
- **Check a module's FCC ID** (FCC Equipment Authorization search) for its authorised power, modes and antennas before a US competition ([certification](certification-fcc-ce-imda.md)). For IREC/Spaceport America band plans see [launches abroad](international-rules-for-competitions.md).
- **Keep a regulatory file per launch**: for each transmitter, record frequency, bandwidth, conducted power, antenna gain, e.r.p./e.i.r.p., duty cycle, and the rule or licence it operates under, with the licence or permit number. Range safety officers and IMDA/FCC inspectors ask exactly these questions.
- **Lead times**: Singapore Temporary Use permits and amateur frequency consents take weeks, and US licence exams need scheduling. Start a term before the launch ([Singapore rules](singapore-imda-rules.md), [amateur licensing](amateur-radio-licensing.md)).
- **Following NextNav**: ECFS dockets WT 25-110, WT 24-240 and RM-11989. LoRa Alliance, utilities, RFID (RAIN Alliance) and amateur organisations file there.
- **Home FM transmitters** in the US must meet §15.239: 250 µV/m at 3 m (about −47 dBm EIRP), 200 kHz bandwidth, 88–108 MHz. Typical "FM transmitter kits" at tens of mW are thousands of times over. Analog TV transmitters have no licence-free US rule (outside narrow exceptions). In Singapore, broadcast-band transmission needs a licence; the licence-exempt list in [Singapore rules](singapore-imda-rules.md) has no home broadcast provision.
- **Reporting interference.** In the US, the FCC Enforcement Bureau takes interference complaints, and the amateur community runs volunteer monitoring. In Singapore, report to IMDA through its spectrum-interference reporting channel. Record frequency, time pattern, bearings and spectrum screenshots first ([interference hunting](../17-test-measurement/interference-hunting-and-rf-immunity.md)).
- **Encryption** on amateur bands is prohibited in both countries (US 97.113(a)(4); SG regs 41–42). EBYTE modules' "key" scrambling counts, so disable it under an amateur licence ([amateur licensing](amateur-radio-licensing.md)).
- **CE "self-declaration"** means the manufacturer signs a Declaration of Conformity under RED/EMC rules (Module A). Market surveillance authorities test samples after products are on sale. A noisy product with a CE mark is a compliance failure to report, not proof that the limits allow that noise.

**Five questions before transmitting anything new**:
1. **Band**: is the whole occupied channel ($f_c \pm BW/2$) inside a band you may use (licence-exempt, amateur, or licensed)? ([canonical band-edge rule](../00-math-foundations/canonical-values-and-conventions.md))
2. **Power**: is the e.r.p./e.i.r.p., *including antenna gain*, within the limit in the reference the rule uses (e.r.p. below 1 GHz in Singapore; field strength at 3 m in US Part 15)?
3. **Time**: are the duty-cycle, dwell or hopping rules met, counting relays and retries?
4. **Equipment**: does the rule require certified or type-approved equipment (Part 15, FRS, PMR446), or does a licence cover home-built gear (amateur, experimental)?
5. **Content**: amateur rules on identification, no encryption and no third-party traffic; and never GNSS or jamming signals.

## Common mistakes & misconceptions
- **"NextNav already took 902–928 MHz."** As of 2026-10-12 the FCC has issued only an NOI. A draft NPRM was reported at OMB in March 2026 [2], with no adopted rules. Watch the docket instead of reacting to headlines (D3 #452/#455, D2 #230).
- **"Unlicensed users have rights in 902–928 MHz."** Part 15 devices have never had interference protection. That is why the proposal is a threat at all.
- **"Baofengs are illegal."** Owning one is not the issue. *Marketing* one that can transmit outside amateur bands without certification is, and *using* it off the amateur bands is (US) [3]. A licensed ham may use an amateur-only (or compliant) radio on amateur bands (D3 #627).
- **"My ham licence lets me use any radio on any frequency it tunes."** Only on amateur frequencies within your privileges.
- **"A ham licence makes my radar legal everywhere."** Only within Part 97: permitted bands and emissions, identification, no interference to primaries. 70 cm amateur use is secondary to US Government radiolocation (D3 #529, #462).
- **"Radar in the 2.4 GHz ISM band is fine because Wi-Fi is there."** ISM status protects ISM *equipment* from complaints; it does not license transmitters. In the US a 2.4 GHz radar needs §15.245 (2435–2465 MHz, 500 mV/m) or another Part 15 basis. In Singapore, 2.4 GHz radio-determination is ≤ 25 mW EIRP ([DIY radar](../11-radar/diy-radar-hardware.md)) (D3 #77).
- **"A jammer is fine for a quick test."** No exceptions for private persons [7][8].
- **"The region preset in my firmware makes it legal."** Firmware presets are not regulatory determinations: SG_923 at 100 % duty vs TS SRD 1 %, and the US 250 kHz non-hopping question above.
- **"It has a CE mark, so it can't be the RFI source."** CE is mostly self-declared (D2 #45).
- **"Receive-only SDRs need a licence."** Receivers are exempt in Singapore and need no licence in the US. What you do with received content can still be regulated, and that is outside this KB's scope.
- **"If the module is certified, any firmware setting is legal."** The grant covers specific modes, powers and antennas. Out-of-grant settings, such as non-hopping narrowband at full power or a high-gain antenna, are your responsibility ([certification](certification-fcc-ce-imda.md)).

## How to simulate / verify
- `python3 tools/verify/e10_regulatory.py` (output `tools/verify/e10_regulatory_output.txt`, all checks pass). It converts field-strength limits to EIRP, counts channels for the 907–918 MHz scenario, compares handheld powers with the 0.5 W and 10 W ERP references, and computes the §15.249 gap for 30 dBm LoRa.
- Primary sources to re-read before acting: eCFR 47 CFR Parts 2, 15, 90, 95 and 97; FCC ECFS dockets; IMDA TS SRD and the Exemption Notification (see [Singapore rules](singapore-imda-rules.md)).

## Open questions / gaps
- **NextNav status** comes from trade press [2][10] plus the FCC NOI [1]. We could not confirm from the FCC record whether a draft NPRM is circulating or scheduled. Re-check ECFS.
- **US Part 15 basis for non-hopping 125/250 kHz LoRa at up to 30 dBm** (Meshtastic US preset): unresolved. It needs either an FCC KDB statement or the module grants' authorised modes.
- **Singapore walkie-talkie rule**: IMDA material found is old (2005 allocation of 446.0–446.1 MHz [4]). Current power and frequency limits were not read from a current IMDA document. A separate IRIS licence covers 446.325–446.475 MHz at ≤ 1 W ERP.
- **US jammer law**: cited from the statute and FCC enforcement practice as commonly summarised; the FCC jammer page could not be retrieved (HTTP 403).
- **Amateur FMCW radar** (continuous "test" emissions vs radiolocation as a purpose): no FCC interpretation found.
- **Singapore radar under an amateur licence**: the IMDA handbook's emission-class list was not checked for pulse/FMCW radar. Ask IMDA in writing, as for LoRa ([amateur licensing](amateur-radio-licensing.md)).
- **FRS/GMRS details** (Part 95B/E power and antenna rules) were not re-read for this page; the FRS statements are limited to the certification requirement in DA 18-980 [3].
- **ACMA (Australia) and EU equivalents** of these FAQ items are not covered; see [launches abroad](international-rules-for-competitions.md).

## Sources
1. FCC, *Promoting the Development of Positioning, Navigation, and Timing Technologies and Solutions*, Notice of Inquiry, WT Docket No. 25-110, FCC 25-20, adopted 27 Mar 2025, released 28 Mar 2025 (comments 28 Apr, replies 13 May 2025). https://docs.fcc.gov/public/attachments/FCC-25-20A1.pdf (regulator)
2. RFID News, "The 900 MHz question: what NextNav's plan would mean for RAIN RFID worldwide," 27 Sep 2026 — dockets RM-11989, WT 24-240, WT 25-110; petition April 2024; draft NPRM to OMB March 2026; 902–907/918–928 MHz plan with 907–918 MHz shared; > 2 000 comments; SpecTech Alliance launched 17 Sep 2026; "nothing has been decided". https://www.rfidnews.co.uk/2026/09/27/the-900-mhz-question-what-nextnavs-plan-would-mean-for-rain-rfid-worldwide/ (trade press); Communications Daily, 23 Jun 2026 (New Street: NPRM likely, "far from a done deal") (trade press, snippet only).
3. FCC Enforcement Bureau, *Enforcement Advisory No. 2018-03: Two-way VHF/UHF radios may not be imported, advertised, or sold in the United States unless they comply with the Commission's rules*, DA 18-980, 24 Sep 2018 — certification before import/ad/sale/use; amateur-only exception; 12.5 kHz narrowband (47 CFR 90.209); Amcrest (Baofengradio.US) citation DA 18-801. https://docs.fcc.gov/public/attachments/DA-18-980A1.pdf (regulator)
4. IDA (now IMDA) press release, 12 Jul 2005 — allocation of 446.0–446.1 MHz for low-powered walkie-talkies, non-interference/non-protected basis, type approval for local sale; IMDA IRIS, "Localised Private Network (multi-channel radio communication) licence" — 446.325–446.475 MHz, ≤ 1 W ERP. https://www.imda.gov.sg/resources/press-releases-factsheets-and-speeches/archived/ida/press-releases/2004/20050712103130 ; https://iris.imda.gov.sg/application/localised-private-network-(multi-channel-radio-communication)-licence (regulator; dated)
5. 47 CFR §15.245 (field-disturbance sensors: bands and field strengths) and §15.249 (902–928, 2400–2483.5, 5725–5875 MHz, 24.0–24.25 GHz), eCFR current, read 2026-10-12; §15.209, §15.239, §15.35 as commonly cited. https://www.ecfr.gov/current/title-47/part-15 (regulation)
6. 47 CFR §97.305 *Authorized emission types*, eCFR current — pulse authorised on 33 cm, 13 cm, 5 cm, 1.2 cm and the mm bands; test emissions brief; no pulse where not authorised. https://www.ecfr.gov/current/title-47/part-97/section-97.305 (regulation)
7. 47 U.S.C. §302a(b) (marketing/use of non-compliant devices) and §333 (wilful interference), as applied in FCC jammer enforcement (from general knowledge; FCC page not retrievable). (statute)
8. WTO Import Licensing database, Singapore "Telecommunication equipment" entry — RF jammers are prohibited equipment, not allowed for use; dealers need IMDA approval for prohibited equipment. https://importlicensing.wto.org/content/telecommunication-equipment-5 (intergovernmental summary)
9. Meshtastic, "LoRa configuration" — region table: US 902.0–928.0 MHz, 100 % duty, 30 dBm; SG_923 917.0–925.0 MHz, 100 %, 20 dBm. https://meshtastic.org/docs/configuration/radio/lora/ (project docs)
10. Communications Daily, "FCC Could Remove 900 MHz Band From D2D NPRM," 3 Aug 2026 (docket 26-169) (trade press, snippet only).
11. This KB: [Singapore rules](singapore-imda-rules.md), [amateur licensing](amateur-radio-licensing.md), [certification](certification-fcc-ce-imda.md), [spectrum allocation](spectrum-allocation-ism-bands.md), [ISM band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md), canonical values (`kb/00-math-foundations/canonical-values-and-conventions.md`). (internal)
12. Forum demand: Meshtastic GitHub discussion #16 and Hackaday 2026-09-17 (NextNav); YouTube KB9VBR "Are Baofeng radios illegal?"; EEVblog (2.4 GHz radar legality); Hackaday 2026-03-12 (20 km open-source radar, licensing); r/meshtastic (FCC docket 25-110; 1 W T-Beam; PA boards); r/AskElectronics (CE on noisy products); r/rfelectronics (home TV transmitter; jammer finding); r/GNURadio (gps-sdr-sim) — `gaps/D3-forums-youtube.md` rows 77, 452, 455, 462, 529, 627; `gaps/D2-reddit.md` rows 45, 168, 228, 230, 240, 332, 481. (forum — anecdotal)
