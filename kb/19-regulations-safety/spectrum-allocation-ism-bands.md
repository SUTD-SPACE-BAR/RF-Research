---
title: Spectrum allocation, ITU regions, ISM vs SRD bands, radar and protected bands, band names, emission designators and unwanted-emission domains
domain: 19-regulations-safety
slug: spectrum-allocation-ism-bands
tags: [itu-radio-regulations, itu-regions, frequency-allocation, primary-secondary, ism, 5.138, 5.150, srd, licence-exempt, radar-bands, 24-ghz, 60-ghz, 77-ghz, gnss, rnss, passive-bands, 5.340, 70cm, 5.276, band-names, vhf-uhf-shf, ieee-521, letter-bands, emission-designator, necessary-bandwidth, sm-1138, appendix-1, f1d, j3e, f3e, out-of-band-domain, spurious-domain, sm-329, sm-1539]
prerequisites:
  - ../00-math-foundations/decibels-and-log-units.md
related:
  - singapore-imda-rules.md
  - international-rules-for-competitions.md
  - amateur-radio-licensing.md
  - ../15-lora-ism-radios/ism-band-plans-duty-cycle.md
  - ../11-radar/fmcw-radar.md
  - ../08-antennas/gnss-antennas.md
level: intro
confidence: high
last_updated: 2026-10-13
---

# Spectrum allocation, ITU regions, ISM vs SRD, radar and protected bands

> **Informational, not legal advice; last verified 2026-09-27.** The ITU Radio Regulations (RR)
> footnotes below are quoted from their reproduction in 47 CFR 2.106 (current eCFR); the national
> rules that actually govern your transmitter are on the [Singapore](singapore-imda-rules.md) and
> [international](international-rules-for-competitions.md) pages.

## Questions this page answers
- What is the difference between an ISM band and a licence-free (SRD) band?
- Is 433 MHz an ISM band in Singapore?
- Why is 915 MHz used in the USA but 868 MHz in Europe and 920 MHz in Singapore?
- What do "primary" and "secondary" allocation mean for a hobby transmitter?
- Which bands can I use for a hobby radar (24, 60, 77 GHz)?
- Which bands must I never transmit in (GNSS, radio astronomy, passive sensing)?
- Why does IMDA need to consent to each amateur frequency at 430–440 MHz?
- What are HF, VHF, UHF and SHF exactly, and what frequencies are the L, S, C, X, Ku, K and Ka bands?
- What does an emission designator such as 16K0F3E, 2K70J3E or 125KF1D mean?
- What emission designator should I put on a licence or permit application for LoRa?
- What is "necessary bandwidth", and how is it calculated for CW, AM, SSB, FM and FSK?
- Where does "out-of-band" end and "spurious" begin, and which limit applies to my LoRa signal's skirts and harmonics?

## TL;DR
- **Three ITU Regions** (RR Article 5): Region 1 Europe/Africa/Middle East/Russia; Region 2 the Americas; **Region 3 Asia-Pacific incl. Singapore and Australia**. Allocations differ by region and by country footnote.
- **ISM ≠ licence-free.** ISM applications (RR 1.15; FCC Part 18 definition: equipment that generates and uses RF *locally*, excluding telecommunication) are industrial heaters, microwave ovens, diathermy, etc. [1][2]. RR **5.150** designates 13.56, 27.12, 40.68 MHz, **902–928 MHz (Region 2 only)**, 2.45 GHz, 5.8 GHz and 24.125 GHz for ISM, and radio services there **must accept harmful interference from ISM** [1]. RR **5.138** designates 6.78 MHz, **433.05–434.79 MHz (Region 1 only, plus the 5.280 countries)**, 61.25, 122.5 and 245 GHz — subject to special authorisation [1].
- **Therefore 433.92 MHz is not an ITU ISM band in Singapore (Region 3)**; Singapore permits 433.05–434.79 MHz *SRDs* at 10 mW e.r.p. by national decision ([Singapore page](singapore-imda-rules.md)). Likewise 902–928 MHz ISM exists only in Region 2 — Singapore's 917–925 MHz SRD band is national.
- **SRD / licence-exempt use** is a national regime (IMDA TS SRD, EU Decision 2006/771/EC, FCC Part 15, ACMA LIPD) that permits low-power devices, often inside ISM bands (because those bands are "polluted" anyway), always with power/duty limits and no protection.
- **Primary vs secondary**: a secondary service must not cause harmful interference to, and cannot claim protection from, primary services. Amateur 70 cm is secondary in most of the world; RR **5.276** additionally allocates **430–440 MHz to FIXED (primary) and 430–435/438–440 MHz to MOBILE (primary) in Singapore** [1] — which is why IMDA assigns amateur 70 cm frequencies individually.
- **Radar**: 24.00–24.25 GHz (SRD 100 mW e.i.r.p. in SG; radar guns excluded), 57–64 GHz, **76–77 GHz** (SG vehicle/infrastructure radar), 77.5–78 GHz short-range radar per RR 5.559B [1][3]; in Singapore **77–81 GHz** is exempt only as a UWB device (mean ≤ −3 dBm/MHz) [5][6].
- **Never transmit in**: GNSS bands (RNSS 1164–1300 MHz, 1559–1610 MHz; RR 5.328B), and the passive bands where **RR 5.340 prohibits all emissions** (e.g. 1400–1427 MHz, 23.6–24 GHz, 50.2–50.4 GHz, 86–92 GHz) [1]. Note 23.6–24.0 GHz sits just below the 24 GHz radar band — harmonics and wide FMCW sweeps must stay out.
- Miscellaneous regulatory questions (NextNav 902–928 MHz status, Baofeng handhelds, hobby radar, jammers, GNSS simulators): [regulatory FAQ](regulatory-faq-misc.md).
- **Band names** (ITU-R V.431 / RR No. 2.1): band *N* runs from 0.3 × 10ᴺ to 3 × 10ᴺ Hz — HF 3–30 MHz, **VHF 30–300 MHz, UHF 300–3000 MHz** (433, 868, 915 MHz, GNSS L1 and 2.45 GHz are all UHF), SHF 3–30 GHz, EHF 30–300 GHz [8]. Radar letter bands (IEEE Std 521) are a different scheme: L 1–2, S 2–4, C 4–8, X 8–12, Ku 12–18, K 18–27, Ka 27–40, V 40–75, W 75–110 GHz [8][9].
- **Emission designator** = necessary bandwidth (3 digits + H/K/M/G as the decimal point) + 3 class symbols (modulation, signal nature, information) [10]. 16K0F3E = 16 kHz FM telephony; 2K70J3E = 2.7 kHz SSB-SC voice; 100HA1A = Morse at 25 WPM. LoRa is usually written **125KF1D** (frequency-modulated chirp, one digital channel, data); strictly the 99 % occupied bandwidth is ≈ 1.05 × BW at SF7, so 131KF1D is the more defensible figure for a filing [11] (`tools/verify/s2_necessary_bandwidth.py`).
- **Unwanted emissions** split into the **out-of-band domain** (from the edge of the necessary bandwidth out to ±250 % of it from the centre) and the **spurious domain** beyond [12]. For E22 CH 24 at 125 kHz the spurious domain starts 312.5 kHz from the carrier (below 433.8125 / above 434.4375 MHz); harmonics are always spurious and meet the TS SRD −36/−30 dBm limits ([Singapore page](singapore-imda-rules.md)).

## Intuition (no math)
The ITU divides the spectrum into **allocations** to *services* (fixed, mobile, broadcasting, radiolocation, amateur, radionavigation-satellite…), region by region, with footnotes for individual countries. National regulators then **assign** frequencies to licensees within those allocations, and additionally carve out **licence-exempt** niches for low-power devices. "ISM" is a third, older idea: frequencies where machines that just *heat* things with RF are allowed to be noisy, so radio services there must tolerate them. Because nobody can be protected there anyway, regulators like to put licence-free devices (Wi-Fi at 2.4 GHz, many SRDs) into ISM bands — but the permission for those devices comes from the SRD rules, with their own strict limits, not from the ISM designation.

## The math
### Level 1 — frequency ↔ wavelength and band names
$\lambda = c/f$: 433 MHz → 0.692 m (the "70 cm" amateur band 420/430–440/450 MHz); 915 MHz → 0.328 m ("33 cm"); 2.45 GHz → 12.2 cm; 24.125 GHz → 12.4 mm; 77 GHz → 3.9 mm.
The ITU band number is $N = \lceil \log_{10}(f/3\ \mathrm{Hz}) \rceil$, so that $0.3\times10^N < f \le 3\times10^N$ Hz: 433.92 MHz → $\log_{10}(1.45\times10^8) = 8.16$ → **band 9 (UHF)**; exactly 300 MHz is still band 8 (VHF) because the upper limit is inclusive [8]. The band names and the "metric" names (band 8 = metric waves, band 9 = decimetric waves) are tabulated in [§ Band names](#band-names-itu-numbers-and-radar-letter-bands).

### Level 2 — why a harmonic can land in a protected band
A transmitter at $f_0$ produces harmonics at $n f_0$. 433.92 MHz × 2 = 867.8 MHz (inside the 866–869 MHz SRD band); × 3 = 1301.8 MHz (just above the 1164–1300 MHz RNSS allocation). A 12.0 GHz oscillator doubled for a 24 GHz radar leaks at 12 GHz; a 24.125 GHz FMCW radar sweeping 250 MHz stays inside 24.00–24.25 GHz only if its sweep and drift are controlled — 23.6–24.0 GHz is a no-emission passive band [1]. Filters and spurious limits (IMDA TS SRD Table 1-a) exist for exactly this reason.

### Level 3 — the legal hierarchy
ITU RR (treaty) → national table of allocations (Singapore Spectrum Allocation Chart, US 47 CFR 2.106) → national licensing/exemption instruments (Singapore Telecommunications Act + Exemption Notification + TS SRD; US Parts 15/97; EU SRD Decision + RED) → competition band plans (which can only restrict further). A device is legal only if it fits every layer.

## ISM designations (RR 5.138 and 5.150, via 47 CFR 2.106 [1])
| Band | Centre | RR footnote | Region | Status |
|---|---|---|---|---|
| 6765–6795 kHz | 6.78 MHz | 5.138 | all | special authorisation |
| 13.553–13.567 MHz | 13.56 MHz | 5.150 | all | services accept ISM interference |
| 26.957–27.283 MHz | 27.12 MHz | 5.150 | all | " |
| 40.66–40.70 MHz | 40.68 MHz | 5.150 | all | " |
| **433.05–434.79 MHz** | 433.92 MHz | 5.138 (+5.280 countries incl. Portugal, Germany, Switzerland) | **Region 1 only** | special authorisation |
| **902–928 MHz** | 915 MHz | 5.150 | **Region 2 only** | services accept ISM interference |
| 2400–2500 MHz | 2.45 GHz | 5.150 | all | " |
| 5725–5875 MHz | 5.8 GHz | 5.150 | all | " |
| 24.00–24.25 GHz | 24.125 GHz | 5.150 | all | " |
| 61.0–61.5 GHz | 61.25 GHz | 5.138 | all | special authorisation |
| 122–123 GHz | 122.5 GHz | 5.138 | all | special authorisation |
| 244–246 GHz | 245 GHz | 5.138 | all | special authorisation |

## SRD bands commonly used for telemetry, by jurisdiction
| Jurisdiction | Sub-GHz SRD for LoRa-type telemetry | Source page |
|---|---|---|
| Singapore | 433.05–434.79 MHz 10 mW e.r.p.; 866–869 MHz 500 mW e.r.p.; 917–925 MHz 100 mW e.r.p. (LPWAN end device, 1 %) | [Singapore](singapore-imda-rules.md) |
| EU | 433.05–434.79 MHz 10 mW e.r.p. (10 %); 863–870 MHz sub-bands 5–500 mW e.r.p. | [international](international-rules-for-competitions.md) |
| USA | 902–928 MHz Part 15 (FHSS/DTS 1 W; otherwise ~0.75 mW EIRP); 433 MHz only §15.231 (µW) | [international](international-rules-for-competitions.md) |
| Australia | 433.05–434.79 MHz 25 mW EIRP; 915–928 MHz 1 W EIRP (FHSS/digital modulation) | [international](international-rules-for-competitions.md) |

## Radar-relevant bands
| Band | Singapore (TS SRD) | International note |
|---|---|---|
| 10.50–10.55 GHz | 117 dBµV/m at 10 m, radio-determination (sub-band 37) | classic Doppler "Gunnplexer" band |
| 24.00–24.25 GHz | 100 mW e.i.r.p.; automotive, tank-level, non-specific SRD — **radar guns not allowed** (38a–c) | ISM (5.150); amateur 24.00–24.25 GHz; 23.6–24.0 GHz passive (5.340) |
| 57–64 GHz | 100 mW e.i.r.p. (39a/b); 57–66 GHz RLAN 10 W (40) | oxygen absorption ~60 GHz |
| 76–77 GHz | 55 dBm peak; 23.5 dBm average (pulse) / 50 dBm average (other) e.i.r.p. (41) | 76–81 GHz radiolocation; 77.5–78 GHz short-range radar (5.559B) |
| 77–81 GHz | **not in TS SRD**; licence-exempt only as an *Ultra-Wideband device*: mean e.i.r.p. density ≤ −3 dBm/MHz, peak ≤ 55 dBm/50 MHz, ≥ 500 MHz bandwidth, not a fixed outdoor installation (Exemption Notification item 17; IMDA TS UWB 2016 Table 1) [5][6] | EU 79 GHz automotive SRR regime (ECC/DEC/(04)03) is the model |
| 122–123 GHz | 100 mW e.i.r.p. (42) | ISM (5.138) |

(Singapore values from IMDA TS SRD Iss. 1 Rev 3 [3], except 77–81 GHz [5][6] — see [Singapore page § radar bands](singapore-imda-rules.md); FMCW design in [radar](../11-radar/fmcw-radar.md).)

## Protected bands — do not transmit
| Band | Why | Reference |
|---|---|---|
| 1164–1300 MHz, 1559–1610 MHz | GNSS (RNSS) — L5/E5, L2/E6, L1/E1/B1 | RR 5.328B [1]; Singapore lists GNSS receivers as exempt equipment only |
| 1400–1427 MHz | radio astronomy / passive sensing (hydrogen line) — all emissions prohibited | RR 5.340 [1] |
| 23.6–24.0 GHz | passive (water vapour) — all emissions prohibited | RR 5.340 [1] |
| 50.2–50.4, 52.6–54.25 GHz | passive (oxygen) | RR 5.340 [1] |
| 86–92 GHz | passive | RR 5.340 [1] |
| 406–406.1 MHz, 121.5 MHz | distress beacons (COSPAS-SARSAT) | general knowledge — not re-verified here |

GNSS **jammers or re-radiators** are not permitted as SRDs anywhere reviewed (none of the SRD tables includes RNSS bands). Testing GNSS receivers with a simulator must be done conducted or in a shielded enclosure.

## Band names: ITU numbers and radar letter bands
**ITU nomenclature** (Rec. ITU-R V.431-8 Table 1, which follows RR No. 2.1) [8]. Lower limit exclusive, upper limit inclusive; band *N* spans $0.3\times10^N$ to $3\times10^N$ Hz.

| Band no. | Symbol | Range | Metric name | Examples relevant here |
|---|---|---|---|---|
| 3 | ULF | 300–3000 Hz | hectokilometric | speech audio band |
| 4 | VLF | 3–30 kHz | myriametric | submarine comms, lightning sferics |
| 5 | LF | 30–300 kHz | kilometric | 40/60/77.5 kHz time signals |
| 6 | MF | 300–3000 kHz | hectometric | AM broadcast |
| 7 | HF | 3–30 MHz | decametric | shortwave, 6.78/13.56/27.12 MHz ISM, 20 m amateur |
| 8 | VHF | 30–300 MHz | metric | FM broadcast, 2 m amateur, APRS 144.39/144.80 MHz, air band |
| 9 | UHF | 300–3000 MHz | decimetric | **433/868/915/923 MHz LoRa, GNSS L1/L2/L5, 2.45 GHz** |
| 10 | SHF | 3–30 GHz | centimetric | 5.8 GHz, 10 GHz Doppler, 24 GHz radar |
| 11 | EHF | 30–300 GHz | millimetric | 60 GHz, 77–81 GHz radar, 122 GHz |
| 12 | — | 300–3000 GHz | decimillimetric | (no ITU symbol; "THF" is informal) |

V.431 also lists the broadcast bands I–V (Region 3: I 47–68, II 87–108, III 174–230, IV 470–582, V 582–960 MHz) [8]. "Shortwave", "microwave" (roughly 1–300 GHz in common use) and "millimetre-wave" are informal terms with no fixed edges.

**Radar / satellite letter bands.** These are *not* ITU nomenclature. V.431 says they have no standard correspondence and advises against them in ITU texts, but it lists them for information [8]. The usual reference is IEEE Std 521-2019 [9]:

| Letter | Range (GHz) | Typical use near the reader |
|---|---|---|
| (HF / VHF / UHF in IEEE 521) | 0.003–0.03 / 0.03–0.3 / 0.3–1 | note: IEEE "UHF" stops at **1 GHz**, ITU UHF at 3 GHz |
| L | 1–2 | GNSS (1164–1610 MHz), "L-band" SDR work |
| S | 2–4 | 2.45 GHz ISM, weather/ATC radar |
| C | 4–8 | 5.8 GHz, satellite TV (C-band) |
| X | 8–12 | 10.5 GHz Doppler modules, marine radar |
| Ku | 12–18 | satellite TV/LNB (10.7–12.75 GHz straddles X/Ku) |
| K | 18–27 | 24.0–24.25 GHz radar |
| Ka | 27–40 | satellite broadband |
| V | 40–75 | 57–64 GHz radar/RLAN |
| W | 75–110 | 76–81 GHz automotive radar |
| mm | 110–300 | 122 GHz SRD (IEEE 521 calls 110–300 GHz the millimetre-wave band) |
| THz | 300–1000 | added in the 2019 revision |

Other letter schemes exist. The NATO/EU ECM bands A–M and the old WW2 "P band" (≈ 230–1000 MHz) reuse the same letters for different ranges, so always give the frequency the first time you use a letter.

## Emission designators and necessary bandwidth
**Necessary bandwidth** (RR No. 1.152) is the width of the band that is "just sufficient" for the information rate and quality required [12]. It is a calculated quantity for a class of emission, not the measured width. The **occupied bandwidth** (99 % power) is measured, and for digital emissions administrations generally use the theoretical 99 % OBW as the necessary bandwidth [13].

**The designator** (RR Appendix 1, Rev. WRC-12) [10]:
1. **Bandwidth, 4 characters.** Three significant figures, with the unit letter in place of the decimal point: H (0.001–999 Hz), K (1.00–999 kHz), M (1.00–999 MHz), G (1.00–999 GHz). The first character is never 0, K, M or G. Examples: 400 Hz = 400H, 2.4 kHz = 2K40, 12.5 kHz = 12K5, 180.5 kHz = 181K, 5.65 GHz = 5G65.
2. **First symbol, modulation of the main carrier:** N unmodulated; A DSB AM; H SSB full carrier; R SSB reduced carrier; J SSB suppressed carrier; B independent sidebands; C vestigial sideband; **F frequency modulation; G phase modulation**; D amplitude and angle together or in sequence (e.g. QAM is often written D); P/K/L/M/Q/V pulse types; W combinations; X other.
3. **Second symbol, nature of the modulating signal:** 0 none; **1 one digital channel without a modulating sub-carrier**; 2 one digital channel with a sub-carrier (e.g. AFSK tones into an FM radio); 3 one analogue channel; 7 two or more digital channels; 8 two or more analogue channels; 9 mixed digital and analogue; X other.
4. **Third symbol, information:** N none; A aural telegraphy; B automatic telegraphy; C facsimile; **D data, telemetry, telecommand**; E telephony (incl. sound broadcasting); F television; W combination; X other.
5. **Optional 4th and 5th symbols** (detail of signal; multiplexing). For example the 4th symbol E means a multi-condition code, J commercial-quality sound; the 5th symbol C means code-division, which RR Appendix 1 says "includes bandwidth expansion techniques", N none, T time-division. A dash stands for an unused position.

**Necessary-bandwidth formulas** (Rec. ITU-R SM.1138-3 Annex 1 [11]; NTIA Annex J [13]). B = modulation rate in baud, M = highest modulating frequency, D = peak deviation, K = a numerical factor. Every row is recomputed by `tools/verify/s2_necessary_bandwidth.py`.

| Emission | Formula | SM.1138 / NTIA sample | Designator |
|---|---|---|---|
| Morse, on–off carrier | $B_n = BK$, K = 5 (fading) or 3; B ≈ 0.8 × WPM | 25 WPM: B = 20 Bd → 100 Hz | **100HA1A** |
| Morse, keyed tone on AM | $B_n = BK + 2M$ | B = 20, M = 1 kHz → 2.1 kHz | 2K10A2A |
| AM telephony (DSB) | $B_n = 2M$ | M = 3 kHz → 6 kHz | **6K00A3E** |
| SSB, full carrier | $B_n = M$ | 3 kHz | 3K00H3E |
| SSB, suppressed carrier | $B_n = M - M_{low}$ | 3000 − 300 Hz → 2.7 kHz | **2K70J3E** |
| FM telephony (Carson) | $B_n = 2M + 2DK$, K = 1 | D 5 kHz, M 3 kHz → 16 kHz; D 2.5 kHz → 11 kHz | **16K0F3E**, 11K0F3E |
| FM broadcast | $B_n = 2M + 2DK$ | D 75 kHz, M 15 kHz → 180 kHz | 180KF3E |
| FSK telegraphy/data | $B_n = 2M + 2DK$ with M = B/2, i.e. $B + 2DK$, K ≈ 1.2 | 100 Bd, 170 Hz shift → 304 Hz | 304HF1B |
| PSK/QAM (filtered) | $B_n = 2KR/\log_2 S$ (K from the filter roll-off, ≈ 0.6–1) | — | e.g. G1D, D7W |
| OFDM | $B_n = N_s K$ (sub-carrier spacing × active sub-carriers) | 53 × 312.5 kHz → 16.6 MHz | 16M6W7D |
| Unmodulated radar pulse | $B_n = 2K/t$, K ≈ 1.5 | t = 1 µs → 3 MHz | 3M00P0N |

**LoRa and the team's radios.** There is no SM.1138 formula for chirp spread spectrum, so RR Appendix 1 §2.3 points to measurement (or the theoretical 99 % OBW). A simulated ideal LoRa signal has a 99 % OBW of **1.047 × BW at SF7** (131 kHz at 125 kHz, 262 kHz at 250 kHz, 524 kHz at 500 kHz) and ≈ 1.00 × BW at SF ≥ 9, because the frequency jumps at symbol boundaries matter less when symbols are long (script §3). The [canonical page](../00-math-foundations/canonical-values-and-conventions.md) uses 133 kHz as a conservative edge figure for the band-edge check. The class is **F1D**: the carrier is angle-modulated (a frequency chirp), there is one digital channel with no sub-carrier, and the information is data. The amateur LoRa-APRS community writes 125KF1D and a recent IARU Region 1 MeshCore frequency-coordination proposal writes 62K5F1D [14]. These designators use the nominal BW, which is common practice but slightly narrower than the 99 % OBW. A five-symbol form such as 131KF1DEC (multi-condition code; "bandwidth expansion") is this page's reading of Appendix 1, not an IMDA-stated designator. APRS over an FM radio is **F2D** (an AFSK sub-carrier on FM), e.g. 16K0F2D. GFSK telemetry from an SX126x in FSK mode is F1D with $B_n = B + 2DK$.

Put the designator, the centre frequency, the e.r.p. and the antenna on any IMDA permit or licence request ([Singapore page § licence routes](singapore-imda-rules.md#licence-and-permit-routes)). IMDA's amateur handbook lists telephony/telegraphy classes but no data classes, which is why the Singapore page lists "is F1D acceptable on 70 cm?" as a question to ask IMDA.

## Out-of-band vs spurious domains (ITU-R SM.329, SM.1539)
Definitions (RR Article 1, as given in SM.329-13 §1) [12]:
- **Out-of-band emission** (No. 1.144): emission just outside the necessary bandwidth that results from the modulation process (spectral skirts, splatter, key clicks), excluding spurious emissions.
- **Spurious emission** (No. 1.145): emission outside the necessary bandwidth whose level can be reduced without affecting the information. This includes harmonics, parasitic oscillations, intermodulation and frequency-conversion products (LO leakage, mixer images).
- **Unwanted emissions** (No. 1.146) = out-of-band + spurious.
- **Domains** (Nos. 1.146A/B): the *out-of-band domain* is the range just outside the necessary bandwidth where OoB emissions usually dominate. The *spurious domain* lies beyond it. Domains are frequency ranges and emissions are mechanisms: a harmonic that falls in the OoB domain is still a spurious emission, but the OoB-domain limit applies there.

**Boundary.** The spurious domain generally starts at **±250 % of the necessary bandwidth from the centre frequency** (SM.329 §2.3) [12]. SM.1539-2 replaces 2.5 $B_n$ with a fixed $2.5 B_L$ for very narrow emissions and with $B_U + 1.5 B_n$ for very wide ones [15]:

| Centre frequency | Narrow-band threshold $B_L$ (boundary 2.5 $B_L$) | Wideband threshold $B_U$ (boundary $B_U$ + 1.5 $B_n$) |
|---|---|---|
| 150 kHz–30 MHz | 4 kHz (10 kHz) | 100 kHz |
| 30 MHz–1 GHz | 25 kHz (62.5 kHz) | 10 MHz |
| 1–3 GHz | 100 kHz (250 kHz) | 50 MHz |
| 15–26 GHz | 500 kHz (1.25 MHz) | 500 MHz |

**Spurious-domain limits.** These are given in a **reference bandwidth**: 1 kHz (9–150 kHz), 10 kHz (150 kHz–30 MHz), **100 kHz (30 MHz–1 GHz), 1 MHz (above 1 GHz)**. Category A (the RR Appendix 3 worldwide minimum) requires attenuation of $43 + 10\log_{10}P$ (P in W) or 70 dBc, whichever is less stringent. That works out to −13 dBm absolute below the 70 dBc cap. Category B (European; also used by IMDA TS SRD Table 1-a) sets SRDs at **−36 dBm below 1 GHz, −54 dBm in the broadcast bands, −30 dBm above 1 GHz** [12]. Measure from 30 MHz up to 3 GHz for a 300–600 MHz transmitter and up to the 5th harmonic for 600 MHz–5.2 GHz (SM.329 Table 1). The OoB domain is governed by spectrum masks or adjacent-channel limits in the equipment standard (ETSI EN 300 220 for SRDs), not by SM.329.

## Worked examples
**1. "433 MHz is ISM, so I can use it in Singapore."** Singapore is Region 3; RR 5.138's 433.05–434.79 MHz ISM designation applies in Region 1 (and 5.280 countries) only. Singapore's permission is TS SRD sub-band 26a: 10 mW e.r.p., 10 % duty.

**2. Choosing a radar band for a student FMCW project in Singapore.** 24.00–24.25 GHz at ≤ 100 mW e.i.r.p. (non-specific SRD, 38c) — but not as a speed gun. 250 MHz of sweep gives ΔR = c/2B = 0.6 m range resolution; keep the sweep inside the band edges with margin for temperature drift, and filter any 12 GHz sub-harmonic.

**3. A 433.92 MHz transmitter's 3rd harmonic.** 1301.76 MHz lies 1.8 MHz above the 1300 MHz RNSS upper edge; with a 125 kHz signal and ±20 ppm drift the harmonic stays outside, but a 433.35 MHz carrier's 3rd harmonic (1300.05 MHz) would touch the edge — and 5th harmonics at 2.17 GHz fall in cellular bands. Filter.

**4. Decode and build designators.** *16K0F3E*: 16.0 kHz, F (frequency modulation), 3 (one analogue channel), E (telephony), i.e. 25 kHz-channel NBFM voice. *2K70J3E*: 2.7 kHz SSB suppressed-carrier voice. *304HF1B*: 304 Hz FSK, automatic telegraphy (RTTY). For the team's E22 at SF7/250 kHz: 99 % OBW ≈ 1.047 × 250 = 262 kHz → **262KF1D** (or 250KF1D on the nominal-bandwidth convention). For the E220 in GFSK at 2.4 kb/s with ±5 kHz deviation, $B_n = B + 2DK = 2.4 + 2·5·1.2 = 14.4$ kHz → 14K4F1D.

**5. Where does the E22's spurious domain start?** CH 24 (434.125 MHz), $B_n$ = 125 kHz is above $B_L$ = 25 kHz, so the boundary is 2.5 × 125 = 312.5 kHz from the centre. The OoB domain is 434.1875–434.4375 MHz above the carrier (and mirror-image below). Everything beyond, including the 868.25 MHz 2nd harmonic and the 1302.4 MHz 3rd, is the spurious domain. TS SRD Table 1-a then sets −36 dBm in 100 kHz below 1 GHz and −30 dBm in 1 MHz above. At 500 kHz BW the OoB domain extends to ±1.25 MHz, i.e. 432.875–435.375 MHz, past both band edges. That is one more reason to keep wide LoRa channels away from the 433.05/434.79 MHz edges.

## Practical notes
- Look up the **national** allocation chart (Singapore: IMDA Spectrum Allocation Chart, Jan 2026 v1.3 — graphical) before designing for a band.
- Design radios to be **frequency-agile** so one board can meet each region's plan.
- ISM bands are **noisy**: microwave ovens at 2.45 GHz, RFID readers at 866/920 MHz, industrial equipment — budget link margin accordingly.

## Common mistakes & misconceptions
- **"ISM means anything goes."** ISM designation protects nobody and authorises no transmitter; SRD rules do, with limits.
- **"433 MHz is licence-free everywhere at any power."** Only low-power SRD use, and only where the national rules say so (10 mW e.r.p. in SG/EU, 25 mW EIRP in AU, µW-level in the US).
- **"915 MHz is a worldwide ISM band."** Region 2 only.
- **"Secondary allocation means second priority but still protected."** Secondary users get no protection and must not interfere.
- **"UHF is 300 MHz to 1 GHz and 1–3 GHz is microwave."** That is the IEEE 521 radar usage. In ITU nomenclature UHF runs to 3 GHz, so GNSS L1 and 2.4 GHz Wi-Fi are UHF. State which scheme you mean.
- **"X band is 8–12 GHz everywhere."** Letter bands have several incompatible schemes (IEEE 521, NATO/ECM, satellite usage); V.431 advises against them without frequencies.
- **"The designator's bandwidth is my channel spacing or my filter setting."** It is the *necessary* bandwidth for the emission class, computed by SM.1138 (or the theoretical 99 % OBW for digital signals). An NBFM radio on a 12.5 kHz channel is 11K0F3E, and a LoRa signal at BW 125 kHz occupies ≈ 131 kHz at SF7.
- **"F1D means FSK."** F is any frequency modulation of the main carrier, which includes LoRa chirps, GFSK and FSK. An AFSK tone into an FM radio is F2D (digital *with* a sub-carrier), and phase-modulated data (BPSK/QPSK) is G1D.
- **"Spurious means anything outside my channel."** Skirts and splatter created by the modulation are *out-of-band* emissions. Spurious emissions (harmonics, parasitics, intermod, LO leakage) can be removed without touching the information. The two are limited by different rules and in different frequency domains.
- **"Receiving is regulated like transmitting."** Receive-only equipment is generally not licensed (though intercepting some communications may be restricted by other laws).
- **"2.4 GHz was chosen because it is water's resonant frequency."** Liquid water has no resonance there: its dielectric loss is a broad Debye relaxation peaking near 17 GHz at 20 °C (≈ 19 GHz at 25 °C) ([dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md), ITU-R P.527). 2450 MHz is an ISM frequency because the 1947 Atlantic City ITU conference designated it, following a US request for an existing diathermy/heating frequency [7]; ovens use it because loss there is high enough to heat yet low enough to penetrate (power penetration depth ≈ 1.6 cm vs ≈ 1 mm at 10 GHz), magnetrons were mature, and it was a legal band. Wi-Fi, Bluetooth and Zigbee followed later because the band was licence-exempt worldwide (RR 5.150) — and they inherit the microwave-oven interference. (Half-addressed myth from W4-D1, electronics.stackexchange.com/q/125692.)

## How to simulate / verify
- Harmonic placement: a few lines of Python ($n f_0$ vs protected-band list) — see `tools/verify/reg_erp_compliance.py` for the limit tables; add band edges as needed.
- Spectrum-analyser sweep to ≥ 5 f₀ before any transmission test.
- `python3 tools/verify/s2_necessary_bandwidth.py` checks five things: the RR Appendix 1 bandwidth formatter against all 15 Appendix 1 examples; the SM.1138/NTIA formulas against their 13 sample designators; LoRa 99 % OBW by simulation; OoB/spurious boundaries per SM.329/SM.1539; and ITU band numbers. ALL PASS.
- On the bench: use the analyser's occupied-bandwidth (99 %) function to measure the necessary bandwidth of your own emission, and compare it with the formula.

## Open questions / gaps
- Singapore's primary allocations in the IMDA Spectrum Allocation Chart (Jan 2026) were not transcribed (graphical PDF); RR 5.276 used instead for 430–440 MHz.
- ITU RR Article 5 region boundary text and RR 1.15 not read directly (FCC Part 18 definition used).
- Distress bands row not re-verified.
- IEEE Std 521-2019 was read via a reproduction of its chart (the standard is paywalled). W5-S18b rechecked on 2026-10-13. Both Bucknell charts (from the 2002 and 2019 editions) show only L to W, mm and THz. A publisher abstract of the 1984 revision says its HF and VHF definitions are identical to the ITU bands, which supports 3–30 and 30–300 MHz. The **UHF = 300–1000 MHz** row is still not confirmed from the standard text and remains single-sourced (memory plus the V.431 comparison).
- No IMDA-stated designator for LoRa telemetry was found. The F1D class and the 99 % OBW figure are this page's reading of RR Appendix 1 and SM.1138; ask IMDA in writing.
- RR Appendix 3 (the treaty spurious limits) was read only through SM.329 Category A, not directly.

## Sources
1. 47 CFR §2.106 Table of Frequency Allocations — international footnotes 5.138, 5.150, 5.276, 5.280, 5.282, 5.328B, 5.340, 5.559B (reproducing ITU RR footnotes), eCFR current text read 2026-09-27. https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-2/subpart-B/section-2.106 (regulation reproducing treaty text)
2. 47 CFR §18.107(c) definition of ISM equipment. https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-18/subpart-A/section-18.107 (regulation)
3. IMDA TS SRD Issue 1 Rev 3 (Sep 2023), Table 1 sub-bands 37–43. (regulator standard) — see [Singapore page](singapore-imda-rules.md) source 3.
4. ITU, *Radio Regulations* (2024 edition), Article 5 (regions, Table of Frequency Allocations) — primary source for the footnotes above (not read directly in this task). https://www.itu.int/pub/R-REG-RR (treaty)
5. *Telecommunications (Exemption from sections 53, 54(1)(b) and 55) Notification* (Singapore), First Schedule items 15 (Short Range Radar System, 76–77 GHz) and 17 (Ultra-Wideband Devices, 77.00–81.00 GHz −3 dBm/MHz), SSO current version read 2026-09-29. https://sso.agc.gov.sg/SL/TA1999-N1 (legislation)
6. IMDA TS UWB Issue 1 (1 Oct 2016), §1.2, §4.1, Table 1. https://www.imda.gov.sg/-/media/imda/files/regulation-licensing-and-consultations/ict-standards/telecommunication-standards/radio-comms/imda-ts-uwb.pdf (regulator standard)
7. "ISM radio band," Wikipedia (accessed 2026-10-02) — summary of the 1947 ITU Atlantic City conference records establishing the ISM bands and the US request for 2450 MHz (diathermy). https://en.wikipedia.org/wiki/ISM_radio_band (encyclopedia — secondary; ITU conference documents not read directly)
8. ITU-R, *Recommendation V.431-8 (08/2015): Nomenclature of the frequency and wavelength bands used in telecommunications* — Table 1 (band numbers 3–15, symbols, metric names; lower limit exclusive), Note 1, Table 3 (broadcast bands I–V), Note 5 and Table 4 (letter designations "not advisable"; L–Ka examples). https://www.itu.int/dms_pubrec/itu-r/rec/v/R-REC-V.431-8-201508-I!!PDF-E.pdf (standard)
9. IEEE, *Std 521-2019 Standard Letter Designations for Radar-Frequency Bands* (approved 7 Nov 2019) — L…W, mm (110–300 GHz) and THz (300–1000 GHz) bands, as reproduced in D. Kelley (Bucknell Univ.), "Radar band letter designations (from IEEE Standard 521-2019)". https://www.eg.bucknell.edu/~dkelley/eceg497/RadarBandLetterDesignations_IEEE521-2019.pdf (standard via lecture handout)
10. ITU, *Radio Regulations Appendix 1 (Rev. WRC-12): Classification of emissions and necessary bandwidths* — §2 (four-character bandwidth and its examples), §6 (first–third symbols), §7 (optional fourth and fifth symbols). https://www.itu.int/en/ITU-R/terrestrial/workshops/wrs12/Miscellaneous/Appendix1.pdf (treaty text)
11. ITU-R, *Recommendation SM.1138-3 (10/2019): Determination of necessary bandwidths including examples for their calculation and associated examples for the designation of emissions* — Annex 1 formulas and sample designators (100HA1AAN, 2K70J3EJN, 16K0F3EJN, 304HF1BBN, 180KF3EGN, 3M00P0NAN, 16M6W7D). https://www.itu.int/dms_pubrec/itu-r/rec/sm/R-REC-SM.1138-3-201910-I!!PDF-E.pdf (standard)
12. ITU-R, *Recommendation SM.329-13 (09/2024): Unwanted emissions in the spurious domain* — §1 (RR definitions 1.144–1.146B, 1.152), §2.3 (250 % boundary), §2.5 Table 1 (measurement ranges), §4.1 (reference bandwidths), Table 2 Category A, §4.3 Category B SRD limits, Annex 4 (43 + 10 log P examples). https://www.itu.int/dms_pubrec/itu-r/rec/sm/R-REC-SM.329-13-202409-I!!PDF-E.pdf (standard)
13. NTIA, *Manual of Regulations and Procedures for Federal Radio Frequency Management*, Annex J (Jan 2021 ed., rev. 1/2023) — method preference, 99 % OBW basis for digital emissions, B20dB for radars, FSK and Morse formulas, Table A examples. https://www.ntia.gov/sites/default/files/2023-11/j_2021_edition_rev_2023.pdf (regulator)
14. Guru-RF, "70 cm MeshCore standard frequency coordination proposal for IARU Region 1" (GitHub RFC, read 2026-10-03) — 62K5F1D, and LoRa-APRS's 125KF1D. https://github.com/Guru-RF/meshcore-rfc-iaru-r1 (community proposal — usage evidence only)
15. ITU-R, *Recommendation SM.1539-2 (09/2024): Variation of the boundary between the out-of-band and spurious domains* — Table of $B_L$/$B_U$ per frequency range and Example 1. https://www.itu.int/dms_pubrec/itu-r/rec/sm/R-REC-SM.1539-2-202409-I!!PDF-E.pdf (standard)
