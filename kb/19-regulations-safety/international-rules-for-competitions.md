---
title: Radio rules at launches abroad — USA (FCC Part 15/97, IREC/Spaceport America Cup), EU/Portugal (EuRoC), Australia (ACMA LIPD)
domain: 19-regulations-safety
slug: international-rules-for-competitions
tags: [fcc-part-15, 15.247, 15.249, 15.231, part-97, irec, spaceport-america-cup, student-band-plan, euroc, portugal, anacom, etsi-en-300-220, eu-2006-771, erc-70-03, acma, lipd-class-licence, travel, lora, e22-400t33d, e220-900t30d]
prerequisites:
  - singapore-imda-rules.md
  - amateur-radio-licensing.md
  - spectrum-allocation-ism-bands.md
related:
  - certification-fcc-ce-imda.md
  - rf-exposure-safety.md
  - ../15-lora-ism-radios/ism-band-plans-duty-cycle.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../08-antennas/antennas-on-rockets.md
level: mixed
confidence: high
last_updated: 2026-10-02
---

# Radio rules at launches abroad — USA, EU/Portugal, Australia

> **Not legal advice; last verified 2026-09-27.** Competition rulebooks change every year and are
> revised during the season (the IREC band plan reached Rev D in April 2026). Always use the
> current edition and the host country's primary regulation; a competition's band plan is **not**
> a licence.

## Questions this page answers
- Which radios can a Singapore team legally fly at the Spaceport America Cup (IREC)?
- What does the IREC 2026 Student Band Plan require for 433 MHz and 915 MHz telemetry?
- Is a fixed-channel LoRa link legal under FCC Part 15 at 915 MHz?
- Can we use our 2 W 433 MHz module in the USA without a ham licence?
- What are the EU 433 and 868 MHz limits that apply at EuRoC in Portugal?
- What radio does EuRoC require on board?
- What are Australia's LIPD class-licence limits at 433 and 915–928 MHz?
- How do we pack, declare and configure radios when travelling to a launch?
- Why can't we use amateur 33 cm (902–928 MHz) at Spaceport America?

## TL;DR
- **USA / IREC (Spaceport America, New Mexico).** Competition rules: IREC 2026 DTEG V1.1 §4 [1] and **Student Band Plan (SBP) Rev D, 14 Apr 2026** [2]. SRAD telemetry goes in **33 cm SRAD range 902.0–909.0 MHz** (Mode A wideband Part 15: 500 kHz ≤ BW ≤ 1 MHz, no hopping, ≤ 1 W, no licence; Mode B FHSS per §15.247; Mode C narrowband = ham licence) or **70 cm SRAD range 420.6–438.0 MHz** (≤ 125 kHz, **≤ 200 mW** unless ESRA approves more, **ham licence + callsign** in each packet or every 10 min). Everything must be listed in Progress Report 3; 33 cm frequencies are assigned at the Final Flight Readiness Review and surrendered after Post Flight.
- **Singapore team at IREC**: no US–Singapore reciprocal amateur arrangement is listed [3], and IREC steers such teams to 900 MHz (DTEG 4.3.2.1, 4.5.5) [1]. So: **E220-900T30D in Mode A (LoRa BW 500 kHz, ≤ 1 W conducted, ≤ 6 dBi) at 902.5–908.5 MHz** is the no-licence option; **E22-400T33D on 70 cm needs a US-licensed control operator (Technician or above) and ESRA approval above 200 mW**.
- **Contradiction to know about**: SBP Mode C (ham narrowband at 33 cm) conflicts with **47 CFR 97.303(n)(2)**, which bars all amateur transmissions from the White Sands box (31°41′–34°30′ N, 104°11′–107°30′ W) that contains Spaceport America [4]. The SBP itself says it is not an authorising document. **Use Mode A or B, never Mode C, at Spaceport America.**
- **FCC Part 15 at 902–928 MHz** [5]: §15.247 FHSS (< 250 kHz BW: ≥ 50 channels, ≤ 0.4 s per 20 s, ≤ 1 W; 25–49 channels ≤ 0.25 W) or DTS (6 dB BW ≥ 500 kHz, ≤ 1 W, ≤ 8 dBm/3 kHz); > 6 dBi antennas reduce power dB-for-dB; §15.249 otherwise only 50 mV/m at 3 m ≈ **0.75 mW EIRP**. A **fixed-channel 125 kHz LoRa link is not a §15.247 device** and at 1 W is illegal under Part 15.
- **433 MHz in the USA without a licence** is effectively unusable for telemetry: §15.231(e) permits data only at ~4.4 mV/m at 3 m ≈ **5.8 µW EIRP**, ≤ 1 s per transmission and ≥ 10 s silence [5][`reg_erp_compliance.py`].
- **EU / Portugal (EuRoC)**: harmonised SRD conditions in Decision 2006/771/EC as last amended by **(EU) 2025/105** [6]: 433.05–434.79 MHz **10 mW e.r.p., ≤ 10 % duty** (or 1 mW; 434.04–434.79 MHz 10 mW at ≤ 25 kHz BW, 100 %); 868.0–868.6 MHz 25 mW, ≤ 1 %; **869.40–869.65 MHz 500 mW e.r.p., ≤ 10 %** (250 kHz wide — 125 kHz LoRa fits, 500 kHz does not). EuRoC 2026 mandates a **CATS Vega** tracker on 2.4 GHz ≤ 100 mW, internal antennas behind non-carbon **RF windows**, and a declared telemetry system [7].
- **Australia (ACMA LIPD Class Licence 2025, from 1 Oct 2025)** [8]: 433.05–434.79 MHz **25 mW EIRP** (any transmitter); 915–928 MHz **1 W EIRP** for frequency-hopping (≥ 20 hop frequencies) or **digital modulation** transmitters (peak PSD ≤ 25 mW per 3 kHz); otherwise 3 mW EIRP. A 1 W LoRa 125 kHz signal sits just at the PSD cap (flat-spectrum estimate 1.04 W), so ≤ 27–28 dBm EIRP is the sensible setting; whether LoRa counts as "digital modulation" under the instrument's definitions was not verified.

## Intuition (no math)
Every country has its own version of Singapore's two-tier system — a licence-exempt short-range tier with tight power/duty limits, and licensed tiers (amateur, experimental, event permits). Competitions add a **third layer**: a frequency plan that divides the legal spectrum among ~150 teams so trackers don't collide. The competition plan can be *stricter* than the law (IREC caps 70 cm SRAD at 200 mW although Part 97 allows far more) but can never make an illegal transmission legal. Design the radio so it can be **re-tuned and re-powered in minutes** — every competition assigns frequencies late.

## The math
### Level 1 — FCC field-strength limits as EIRP
FCC Part 15 often states limits as field strength $E$ at distance $d$ (3 m). In the far field of an isotropic-equivalent source, $E = \sqrt{30\,\mathrm{EIRP}}/d$, so
$$\mathrm{EIRP} = \frac{(E\,d)^2}{30}\ \mathrm{W}.$$
50 mV/m at 3 m → $(0.05\times3)^2/30 = 0.75$ mW (−1.2 dBm). §15.231(e) at 433.92 MHz: $E = 1500 + \tfrac{433.92-260}{470-260}(5000-1500) = 4399$ µV/m → 5.8 µW (−22.4 dBm) (`tools/verify/reg_erp_compliance.py`).

### Level 2 — §15.247 antenna-gain rule
Conducted limit $P_{max}$ = 30 dBm for $G \le 6$ dBi; for $G > 6$ dBi, $P_{max} = 30 - (G - 6)$ dBm, i.e. **EIRP is capped at 36 dBm (4 W)** for non-point-to-point systems [5 §15.247(b)(4)]. A 1 W transmitter into a 12 dBi Yagi must drop to 24 dBm.

### Level 3 — PSD-type limits and LoRa
A PSD limit $S$ (power per reference bandwidth $B_{ref}$) caps total power at $P = S\,B/B_{ref}$ for a flat spectrum of width $B$. LoRa's spectrum is close to flat across $BW$ (the chirp sweeps it uniformly), so for Australia's 25 mW/3 kHz: 125 kHz → 1.04 W, 500 kHz → 4.2 W (then the 1 W item cap binds). FCC DTS (8 dBm/3 kHz) with a 500 kHz LoRa signal allows 8 + 10 log(500/3) = 30.2 dBm — again the 1 W cap binds. Real spectra have edges and ripple; measure the peak PSD with the analyser's PSD/channel-power function before relying on this.

## USA — Spaceport America Cup / IREC 2026
### Competition rules (DTEG 2026 V1.1 §4 [1], SBP Rev D [2])
| Item | Rule |
|---|---|
| Authority | SBP incorporated by reference; **not an authorising document** — teams responsible for FCC compliance (DTEG 4.1.2.3) |
| Registration | all 33 cm and 70 cm transmitters listed in Progress Report 3 with bandwidth, power, mode; unlisted radios may not operate (SBP) |
| Count | ≤ 2 transmitters per band per rocket section plus the Primary COTS GPS tracker, more only with ESRA approval (SBP) |
| COTS GPS tracker | mandatory per independently recovered body, independently switched/powered (DTEG 4.2) |
| Pit area | no transmissions unless authorised; 33 cm only 909–910 MHz Mode A in pits; 70 cm allowed on assigned frequency (DTEG 4.3.5; SBP) |
| Re-tuning | teams must be able to change frequencies quickly (DTEG 4.3.6); penalties for unassigned frequencies (4.3.7) |
| Ham | control operator Technician+; control operator's callsign used by the transmitter and registered with ESRA; non-US teams need US operating authority or use 900 MHz; bring English documentation (DTEG 4.5) |
| APRS | 1200 baud AFSK APRS recommended for SRAD GPS on 2 m/70 cm/33 cm (4.4.2) |

**SBP Rev D frequency plan [2]:**

| Band | Range (MHz) | User | BW | Power | Hopping | Ham |
|---|---|---|---|---|---|---|
| 33 cm | 902.0–909.0 | SRAD (any) | Mode A/B/C | ≤ 1 W (A, B) | B only, within range | C only |
| 33 cm | 909.0–910.0 | Pit radio check | Mode A | | no | no |
| 33 cm | 910.0–925.0 | COTS GPS (Featherweight, AIM Xtra, Fluctus) | Mode A | | no (Swift exception) | no |
| 33 cm | 925.0–928.0 | FW-NET (Featherweight functions) | | | | |
| 70 cm | 420.0–420.6 | Voice | ≤ 25 kHz | ≤ 1 W | no | yes |
| 70 cm | **420.6–438.0** | **SRAD (GPS, telemetry, video)** | **≤ 125 kHz** | **≤ 200 mW** (more with ESRA approval) | no | yes |
| 70 cm | 438.0–450.0 | COTS GPS (Altus Metrum, BigRedBee) | ≤ 100 kHz | ≤ 200 mW | no | yes |

33 cm modes: **A** — BW 500 kHz–1 MHz, no hopping, ≤ 1 W, no licence (Part 15 DTS); **B** — FHSS ≥ 50 channels ≤ 1 W or 25–49 channels ≤ 0.25 W, per §15.247; **C** — narrowband < 500 kHz, ham licence, callsign each packet or every 10 min, no encryption. Centre frequencies must sit at least half the bandwidth plus a guard band inside each range.

### Federal rules that sit underneath
- **Part 15 (no licence)** [5]: §15.5(b) no harmful interference, accept interference; §15.203 antenna must be permanently attached or use a unique connector (a standard SMA is not allowed on a certified product); §15.23 **home-built devices** need no equipment authorisation if not marketed, not built from a kit and ≤ 5 units for personal use — but must still meet the technical limits using good engineering practice; §15.247/§15.249/§15.231 as in the TL;DR.
- **Part 97 (ham)** [4]: see [amateur page](amateur-radio-licensing.md). New Mexico 70 cm ≤ 50 W PEP (97.313(f)); SS ≤ 10 W PEP (97.313(j)); **no amateur 33 cm in the WSMR box** (97.303(n)(2)).
- **Importing radios** (47 CFR 2.1204(a)) [9]: devices needing no FCC authorisation that comply with the rules (e.g. amateur transmitters) may be imported; up to 4 000 units for "testing and evaluation … product development" not offered for sale; the personal-use allowance (≤ 3 devices) covers Part 15 intentional radiators only in client mode. An amendment (91 FR 57801, 11 Sep 2026) was pending when read — recheck.

### What a Singapore team should fly at IREC (recommendation)
| Radio | Configuration | Rule basis | Paperwork |
|---|---|---|---|
| E220-900T30D (LLCC68) | LoRa **BW 500 kHz** (EBYTE 62.5k air rate = SF5/BW500 per [module page](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md); verify 6 dB BW ≥ 500 kHz on an analyser), CH 53–58 (903.125–908.125 MHz), ≤ 30 dBm conducted with ≤ 6 dBi antenna | SBP Mode A; §15.247(a)(2),(b)(3) DTS | list in PR3; retune at FFRR |
| E22-400T33D (SX1268) | 420.6–438.0 MHz assigned frequency, ≤ 125 kHz, **≤ 200 mW (23 dBm)** unless ESRA approves more — the module's lowest step is 24 dBm (251 mW), so either ask ESRA for approval in PR3 or add a ≥ 2 dB pad; callsign in each packet | SBP 70 cm SRAD; Part 97 with US control operator | US Technician licensee on team (or reciprocal authority); register callsign with ESRA |
| Primary COTS GPS tracker | Featherweight/AIM/Fluctus in 910–925 MHz (no licence) | SBP COTS range | assigned token at FFRR |

If no US licensee is available, fly only the 900 MHz Mode A link plus the COTS tracker.

## EU / Portugal — EuRoC
### Harmonised SRD conditions (Decision 2006/771/EC as amended by (EU) 2025/105) [6]
| Entry | Band (MHz) | Power | Conditions |
|---|---|---|---|
| 44a | 433.05–434.79 | 1 mW e.r.p. | — |
| 44b | 433.05–434.79 | 10 mW e.r.p. | duty ≤ 10 % |
| 45c | 434.04–434.79 | 10 mW e.r.p. | duty ≤ 100 %, bandwidth ≤ 25 kHz |
| 87 | 862–863 | 25 mW e.r.p. | duty ≤ 0.1 %, BW ≤ 350 kHz |
| 46a | 863–865 | 25 mW e.r.p. | mitigation techniques, or duty ≤ 0.1 % |
| 47 | 865–868 | 25 mW e.r.p. | mitigation, or duty ≤ 1 % |
| 47b | 865.6–865.8, 866.2–866.4, 866.8–867.0, 867.4–867.6 | 500 mW e.r.p. | data networks only; APC; BW ≤ 200 kHz; duty ≤ 10 % access points, ≤ 2.5 % otherwise |
| 48 | 868.0–868.6 | 25 mW e.r.p. | mitigation, or duty ≤ 1 % |
| 50 | 868.7–869.2 | 25 mW e.r.p. | mitigation, or duty ≤ 0.1 % |
| **54** | **869.40–869.65** | **500 mW e.r.p.** | **mitigation, or duty ≤ 10 %** |
| 56a / 56b | 869.7–870.0 | 5 mW / 25 mW e.r.p. | — / mitigation or duty ≤ 1 % |
| 57a | 2400–2483.5 | 10 mW e.i.r.p. | — |

"Mitigation techniques" (footnote [7]) means spectrum-access techniques at least as good as those in the harmonised standard (ETSI EN 300 220-2 for 25–1000 MHz: polite access/LBT + adaptive frequency agility) [6]. The same bands are the basis of IMDA's references to ERC Rec 70-03 [see Singapore page]. Networked-SRD bands 874–876 and 915–921 MHz are harmonised separately (Decision (EU) 2018/1538, amended by (EU) 2025/650) with national variations — **not verified for Portugal**; check ANACOM's national frequency plan before using 915–921 MHz there.

**Consequences for our radios in Portugal:** E22-400T33D → 10 mW e.r.p., 10 % (the 2 W module is again ~22 dB over); E220-900T30D → **869.525 MHz, ≤ 27 dBm e.r.p., 125 kHz LoRa, ≤ 10 % duty** (a 32-byte SF7/125 frame at most every 0.72 s). EBYTE CH arithmetic: 850.125 + 19 = 869.125 MHz is the nearest integer channel and is **outside** 869.40–869.65 MHz — the E220's 1 MHz channel grid cannot hit this sub-band; a bare LLCC68/SX126x with arbitrary frequency setting can.

**Amateur in Portugal:** ANACOM recognises CEPT licences; holders from non-CEPT countries need a reciprocity arrangement or a temporary authorisation — Singapore's status was not verified (ANACOM "Procedures for the amateur service" [10]).

### EuRoC 2026 radio-related requirements [7]
- Mandatory **CATS Vega** flight computer/tracker with EuRoC firmware, **2400–2483.5 MHz, ≤ 100 mW**, with a prescribed call-sign string (team number _ stage/payload number) (SRD App. D; RQT-0440/0450/0460).
- **RF windows**: internally mounted transmitters without external antennas need a 360° RF window ≥ 2 calibres long, **not carbon fibre**; antennas at the window mid-point and away from wiring/metal (RQT-0780–0820). Transmitters may not be mounted externally.
- Telemetry details (frequencies, RF power, range, antennas, data rate) must be declared in the Technical Report (Competition Rules App. A7).
- No SRAD frequency plan is published in these documents — national (EU/ANACOM) rules apply to SRAD radios.

## Australia — ACMA LIPD Class Licence 2025 [8]
| Item | Band | Max EIRP | Conditions |
|---|---|---|---|
| Sch.1 Table 1 item 19 | 433.05–434.79 MHz | 25 mW | any transmitter |
| Table 1 item 20 | 915–928 MHz | 3 mW | any transmitter |
| Table 1 item 21 | 2400–2483.5 MHz | 10 mW | any transmitter |
| Table 8 item 1 | 915–928 MHz | 1 W | frequency hopping, ≥ 20 hopping frequencies (cl. 39) |
| Table 8 item 6 | 915–928 MHz | 1 W | digital modulation, peak PSD ≤ 25 mW/3 kHz (cl. 43) |
| RFID items | 918–926 MHz 1 W; 920–926 MHz 4 W | | RFID only |

Notes: LIPD devices get no protection from ISM equipment in 918–926 MHz; the 2025 instrument replaced the 2015 one on 1 October 2025. Australian amateur rules and reciprocity for Singapore licensees were **not researched** here (gap).

## Worked examples
(Arithmetic only, using the rules tabulated above; `tools/verify/reg_erp_compliance.py` reproduces the margins.)

**1. IREC Mode A with the E220-900T30D.** LoRa BW 500 kHz on CH 53 (903.125 MHz), 30 dBm conducted, 0.5 dB cable, 3 dBi rocket antenna: conducted power at the antenna 29.5 dBm ≤ 30 dBm and $G$ ≤ 6 dBi, so §15.247(b)(3)/(4) is met (EIRP 32.5 dBm, below the 36 dBm ceiling). With an 8 dBi ground-station-style antenna the conducted limit becomes 30 − (8 − 6) = 28 dBm. The DTS condition still has to be *measured*: 6 dB bandwidth ≥ 500 kHz on a spectrum analyser (LoRa's 500 kHz chirp is marginal) — keep the plot for the RF officer.

**2. E22-400T33D on the IREC 70 cm SRAD range.** Cap 200 mW = 23.0 dBm unless ESRA approves more. The module's lowest step is 24 dBm (251 mW): add a 2 dB pad → 22 dBm (158 mW, −1 dB margin to the cap) or request approval in Progress Report 3; a US-licensed control operator's callsign goes in every packet.

**3. EuRoC at 869.525 MHz with a bare SX1262 (the E220 cannot tune there).** +22 dBm, 0.5 dB cable, dipole: e.r.p. = 22 − 0.5 + 2.15 − 2.15 = 21.5 dBm = 141 mW ≤ 500 mW (entry 54). Duty ≤ 10 %: a 32-byte SF7/125 frame (71.9 ms) at most every 0.72 s, i.e. ≈ 1.4 Hz; 125 kHz LoRa fits the 250 kHz sub-band, 500 kHz does not.

**4. Australia, 915–928 MHz LoRa under the digital-modulation item.** Peak PSD ≤ 25 mW per 3 kHz; for a flat 125 kHz LoRa spectrum the PSD cap alone would allow 25 × 125/3 = 1.04 W (30.2 dBm), so the 1 W EIRP item cap binds: with a 2.15 dBi dipole and no cable loss, conducted ≤ 27.85 dBm → set 27 dBm. If LoRa were *not* accepted as "digital modulation" (unverified), only 3 mW EIRP would apply — check with ACMA before relying on 1 W.

## Practical notes for travelling teams
- **Make power and frequency software-configurable**, with a config file per venue (SG / IREC-33cm / IREC-70cm / EU / AU) and print the active profile at boot into the log.
- **Measure before you travel**: conducted power, occupied bandwidth (6 dB and 20 dB), peak PSD, harmonics; keep the plots — competition RF officers and customs sometimes ask.
- **Antennas**: the power limits above are conducted (US §15.247, with a 6 dBi rule) or radiated (EU/SG e.r.p., AU EIRP) — recompute for the actual antenna at each venue.
- **Customs**: carry datasheets and a one-page description of each transmitter (frequency, power, purpose); lithium batteries follow airline rules ([lab safety](lab-safety-esd-high-power.md)).
- **Receivers** (SDRs, ground stations) are not licensed anywhere discussed here; transmit-capable SDRs (HackRF, PlutoSDR) are transmitters when they transmit.
- **Ground uplinks count**: RTK-correction or command uplinks must obey the same rules as the downlink.

## Common mistakes & misconceptions
- **"915 MHz ISM is licence-free at 1 W in the US."** Only for FHSS or ≥ 500 kHz digital modulation under §15.247; a fixed-channel 125 kHz LoRa link at 1 W is not compliant.
- **"The competition assigned us a frequency, so we're licensed."** IREC's SBP explicitly is not an authorising document.
- **"Mode C in the SBP means ham 33 cm is OK at Spaceport America."** 97.303(n)(2) prohibits it there.
- **"EU 868 MHz allows 500 mW."** Only in 869.40–869.65 MHz (and 47b's four 200 kHz data-network slots at 2.5 % duty); elsewhere 25 mW.
- **"500 kHz LoRa fits the 869.5 MHz sub-band."** The sub-band is 250 kHz wide.
- **"Australia's 433 MHz limit is like Singapore's."** It is 25 mW EIRP (≈ 15.2 mW e.r.p.), slightly higher, with no duty cycle in the class licence.
- **Leaving the default channel/power from the last venue** — the most common real violation.

## How to simulate / verify
- `python3 tools/verify/reg_erp_compliance.py` — e.r.p./EIRP margins vs SG/EU/AU limits; FCC field-strength → EIRP; AU PSD cap for LoRa bandwidths; duty-cycle intervals.
- `python3 tools/verify/lora_toa.py` — time-on-air for dwell-time and duty-cycle planning (400 ms FCC FHSS dwell).
- Spectrum analyser checks: 6 dB BW (DTS ≥ 500 kHz), 20 dB BW (FHSS channel, §15.231 0.25 %), peak PSD per 3 kHz.

## Open questions / gaps
- Whether LoRa BW 500 kHz from an LLCC68 reliably meets the §15.247(a)(2) 6 dB bandwidth ≥ 500 kHz (needs measurement).
- Legal status in the US of operating a non-certified Part 15 module-based flight radio built by a team (§15.23 "home-built … not from a kit" vs modules; FCC KDB guidance not read).
- Portugal: national implementation of 915–921 MHz; ANACOM route for Singapore amateurs.
- Australia: amateur class licence and visiting-operator rules; the LIPD definition of "digital modulation transmitter".
- Other Asian venues (e.g. Japan, Taiwan, India) not covered.

## Sources
1. ESRA, *International Rocket Engineering Competition — Design, Test & Evaluation Guide*, Revision 2026 V1.1 (23 Feb 2026), §4.0–4.6. https://www.esrarocket.org/s/2026-IREC-DTEG-V11.pdf (competition rules)
2. ESRA, *IREC 2026 Frequency Student Band Plan*, Revision D (14 Apr 2026). https://www.esrarocket.org/s/IREC-2026-Frequency-Student-Band-Plan-Rev-D-041426.pdf (competition rules)
3. ARRL, *Information for US Amateurs Traveling Abroad* (May 2023) — US bilateral reciprocal list (Singapore not listed). https://www.arrl.org/files/file/VEs/International%20Operating%20May%202023.pdf (society guide)
4. 47 CFR Part 97, eCFR current (through 91 FR 1431, 14 Jan 2026): §§97.303(n), 97.313(f),(g),(j). https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-97 (regulation)
5. 47 CFR Part 15, eCFR current (read 2026-09-27): §§15.5, 15.23, 15.203, 15.231, 15.247, 15.249. https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15 (regulation)
6. Commission Implementing Decision (EU) 2025/105 of 22 January 2025 amending Decision 2006/771/EC (annex entries 44a–57a; footnote [7]); also (EU) 2022/180. https://eur-lex.europa.eu/eli/dec_impl/2025/105/oj/eng (EU law)
7. Portuguese Space Agency, *EuRoC System Requirements Document* PTS_EDU_EuRoC_ST_001928 Issue 1.1 (30 Apr 2026) and *EuRoC Competition Rules* PTS_EDU_EuRoC_ST_001905 Issue 1.1 (30 Apr 2026). https://euroc.pt/system-requirements-document/ ; https://euroc.pt/competition-rules/ (competition rules)
8. *Radiocommunications (Low Interference Potential Devices) Class Licence 2025* (F2025L01047), commenced 1 Oct 2025, Schedule 1 Part 1 Table 1 items 19–21, Part 8 Table 8 items 1 and 6, clauses 39 and 43. https://www.legislation.gov.au/F2025L01047/latest/text (legislation)
9. 47 CFR §2.1204 Import conditions (eCFR, read 2026-09-27; amendment 91 FR 57801 pending). https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-2/subpart-K/section-2.1204 (regulation)
10. ANACOM, "Procedures for the amateur service" (search summary only — not read in full). https://www.anacom.pt/render.jsp?contentId=956629 (regulator web — unverified)
