---
title: RF exposure safety — ICNIRP 2020, FCC MPE, SAR, and safe distances for our 433/915 MHz transmitters
domain: 19-regulations-safety
slug: rf-exposure-safety
tags: [rf-exposure, icnirp-2020, fcc-1.1310, mpe, sar, power-density, near-field, oet-65, safe-distance, yagi, nea-singapore, time-averaging]
prerequisites:
  - ../02-electromagnetics/poynting-vector-power-flow.md
  - ../02-electromagnetics/near-field-far-field.md
  - ../08-antennas/antenna-fundamentals.md
related:
  - lab-safety-esd-high-power.md
  - singapore-imda-rules.md
  - amateur-radio-licensing.md
  - ../15-lora-ism-radios/ground-station-design.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# RF exposure safety — ICNIRP 2020, FCC MPE, SAR and safe distances

> **Not medical or legal advice; last verified 2026-09-27.** Limits below are transcribed from
> ICNIRP (2020) and 47 CFR 1.1310/1.1307. Singapore's NEA "takes guidance from" ICNIRP without
> naming an edition [4]; this page uses ICNIRP 2020 and notes where FCC differs.

## Questions this page answers
- How close can I stand to a 2 W 433 MHz transmitter feeding a 12 dBi Yagi?
- What are the ICNIRP 2020 and FCC exposure limits at 433, 868/915 MHz and 2.4 GHz?
- What is SAR and why do limits switch from SAR to power density?
- Does the duty cycle of my telemetry reduce the exposure?
- Is the far-field formula valid a metre from a Yagi?
- Is it safe to hold a rocket while its 2 W radio is transmitting?
- Does an amateur station need an RF exposure evaluation?
- Are the US and ICNIRP limits the same?
- Is RF "radiation" like X-rays? Can a LoRa radio, Wi-Fi or a 5G mast ionise atoms or damage DNA?
- Why is the eye the organ most often mentioned for microwave heating?
- Why are the exposure limits strictest between about 30 and 300 MHz?
- With two transmitters on one rocket or one mast, how do I add up the exposure, and who is responsible at a shared site?
- Is my HF station exempt from an RF-exposure evaluation?

## TL;DR
- **Basic restrictions (ICNIRP 2020 Table 2)** [1]: whole-body average SAR **0.4 W/kg occupational / 0.08 W/kg general public** (30-min average), local SAR (10 g) head/torso **10 / 2 W/kg**, limbs 20 / 4 W/kg (6-min). They come from 4 W/kg ↔ 1 °C core-temperature rise with reduction factors 10 (workers) and 50 (public).
- **Reference levels (ICNIRP 2020 Table 5, whole body, 30 min)**: general public **2 W/m² (30–400 MHz), f_MHz/200 W/m² (400–2000 MHz), 10 W/m² (2–300 GHz)**; occupational 10, f/40, 50 W/m². At 433 MHz: **2.17 W/m² public**, 10.8 W/m² occupational; 915 MHz: 4.58 / 22.9 W/m².
- **FCC MPE (47 CFR 1.1310 Table 1)** [2]: general population **f/1500 mW/cm²** (300–1500 MHz; 30-min average), occupational f/300 mW/cm² (6-min); 1 mW/cm² = 10 W/m². At 433 MHz: 2.89 W/m² public — ICNIRP 2020 is ~25 % stricter there.
- **Safe distance** $R = \sqrt{k\,\mathrm{EIRP}\,D/(4\pi S_{lim})}$ (OET 65 model; $k$ = 1 free space, 2.56 worst-case ground reflection; $D$ = duty factor) [3]. **2 W at 433 MHz into a 12 dBi Yagi (EIRP 28 W)**: continuous transmission → **1.0 m (free space) / 1.6 m (ground reflection)** for the public (ICNIRP); 0.5 / 0.7 m occupational. At 20 % duty: 0.46 / 0.73 m (`tools/verify/reg_rf_exposure.py`).
- **Rocket dipole at 2 W** (EIRP 2.9 W): 0.33 m (free space, continuous, public). Handling a transmitting rocket puts hands/torso **inside λ/2π ≈ 11 cm** of the antenna — reactive near field, where reference levels cannot demonstrate compliance and SAR applies. **Rule: radios off (or dummy-loaded) while people handle the airframe.**
- **FCC routine-evaluation exemption** (1.1307(b)(3)(i)(C)): at 300–1500 MHz, exempt if ERP ≤ 0.0128 R² f (W) → the 2 W + Yagi station (17 W ERP) needs R ≥ 1.8 m to be exempt; otherwise do an evaluation [2]. US amateur stations are covered by the same rules via 97.13(c) (cross-reference, not re-read here).
- Singapore-legal SRD power (10 mW e.r.p.) is an exposure non-issue (safe distance < 4 cm).
- **RF is non-ionising.** A photon's energy is $E = hf$: 1.8 µeV at 433 MHz, 10 µeV at 2.45 GHz, 0.32 meV at 77 GHz — 7 million to 39 000 times below the ≈ 12.4 eV (100 nm) boundary used for ionising radiation, and even below the 0.027 eV thermal energy of molecules at body temperature. Ionisation is a one-photon process, so more power does not change this; the established RF hazard is **heating**, which is what these limits control (section below; [beginner concepts](../00-math-foundations/rf-concepts-for-beginners.md)).

## Intuition (no math)
RF energy at these frequencies heats tissue; the established harms are thermal. The limits therefore cap the **rate of energy absorption** (SAR, watts per kilogram) averaged over minutes, with large safety factors below the level that raises core temperature by 1 °C. Because SAR is hard to measure, the guidelines also give **reference levels** — incident power density or field strength outside the body — that guarantee the SAR limit when met in the far field. Near an antenna, the field is not a plane wave, so the reference levels become approximations (and very close in, invalid). Exposure is **time-averaged**, so a transmitter that is on 20 % of the time delivers 20 % of the average dose.

## The math
### RF is non-ionising — photon energy vs the ionisation threshold
Electromagnetic energy is delivered in photons of energy $E = hf$ ($h = 6.626\times10^{-34}$ J·s;
1 eV = $1.602\times10^{-19}$ J). Ionising an atom or molecule — freeing an electron, the step that can break
DNA directly — needs one photon above a threshold of order 10 eV: valence-electron binding energies span
≈ 4–25 eV, water's first ionisation is ≈ 12.6 eV, and EU radiation-protection law drew the line at a
wavelength of 100 nm, i.e. 12.4 eV (3.0 × 10¹⁵ Hz, far ultraviolet) [5]. Radiation protection treats
anything below as **non-ionising**, governed by ICNIRP (this page) rather than ICRP.

| Source | f | Photon energy | 12.4 eV ÷ photon |
|---|---|---|---|
| LoRa 433.92 MHz | 4.34 × 10⁸ Hz | 1.79 × 10⁻⁶ eV | 6.9 × 10⁶ |
| LoRa 915 MHz | 9.15 × 10⁸ Hz | 3.78 × 10⁻⁶ eV | 3.3 × 10⁶ |
| Wi-Fi / microwave oven 2.45 GHz | 2.45 × 10⁹ Hz | 1.01 × 10⁻⁵ eV | 1.2 × 10⁶ |
| HB100 10.525 GHz | 1.05 × 10¹⁰ Hz | 4.35 × 10⁻⁵ eV | 2.9 × 10⁵ |
| Car radar 77 GHz | 7.7 × 10¹⁰ Hz | 3.18 × 10⁻⁴ eV | 3.9 × 10⁴ |
| Top of the ICNIRP range, 300 GHz | 3 × 10¹¹ Hz | 1.24 × 10⁻³ eV | 1.0 × 10⁴ |
| Thermal energy kT at 37 °C | — | 0.027 eV | (an RF photon at 433 MHz is ≈ 15 000× smaller) |
| Far UV, 100 nm | 3.0 × 10¹⁵ Hz | 12.4 eV | 1 |

Two consequences follow. (i) **Intensity cannot make RF ionising**: a 2 W 433 MHz transmitter emits
≈ 7 × 10²⁴ photons per second, but no single one can free an electron and their energies do not pool
into one bond. (ii) What RF *does* is drive charges and polar molecules collectively, and the absorbed
power appears as **heat** — the mechanism behind the SAR limits below (ICNIRP's basic restrictions start
from the ≈ 1 °C core-temperature rise at 4 W/kg [1]). Poorly perfused tissue, notably the lens of the eye
and the testes, is usually cited as the most sensitive to local heating (standard in exposure guidance;
not re-read in a primary source for this section), which is why "don't look into a high-power
waveguide or along a transmitting dish/Yagi boom" is standard practice. Contact with a transmitting
antenna causes RF burns ([lab safety](lab-safety-esd-high-power.md)). All numbers:
`tools/verify/e6_beginner_numbers.py` §1.

### Level 1 — power density and distance
Far-field power density from an antenna with EIRP (W) at distance $R$ (m):
$$S = \frac{\mathrm{EIRP}}{4\pi R^2}\quad[\mathrm{W/m^2}], \qquad E = \sqrt{\eta_0 S} \approx \sqrt{377\,S}\ \mathrm{V/m}.$$
Setting $S = S_{lim}$ gives the compliance distance. OET 65 recommends multiplying by $k = (1.6)^2 = 2.56$ for a worst-case in-phase ground reflection [3 eq. 4].

### Level 2 — time and spatial averaging, SAR
- Time average: $\bar S = S_{peak}\cdot D$, where $D$ is the fraction of the averaging window (30 min public, 6 min occupational for FCC; 30 min whole-body and 6 min local for ICNIRP) the transmitter is on. A LoRa frame of ToA $T_p$ sent every $T$ gives $D = T_p/T$ (e.g. 71.9 ms/1 s = 7.2 %).
- SAR: $\mathrm{SAR} = \sigma |E_{int}|^2/\rho = c\,\frac{dT}{dt}\big|_{t=0}$ (W/kg), where $\sigma$ is tissue conductivity (S/m), $E_{int}$ the internal rms field, $\rho$ density, $c$ specific heat. The second form is how SAR is measured calorimetrically (initial temperature slope).
- Why two regimes: below ~6 GHz energy penetrates centimetres (SAR is the right metric); above 6 GHz it is absorbed near the skin, so ICNIRP switches to absorbed power density $S_{ab}$ over 4 cm² [1 Table 2].

### Level 3 — near field and validity limits
- Reactive near field: $R \lesssim \lambda/2\pi$ (11 cm at 433 MHz, 5 cm at 915 MHz). ICNIRP 2020 Table 5 note 5(c): for 30 MHz–2 GHz in the reactive near field, **both** $E_{inc}$ and $H_{inc}$ must be below the reference levels — $S_{inc}$ alone cannot demonstrate compliance [1].
- Radiating near field (Fresnel), roughly $\lambda/2\pi < R < 2D^2/\lambda$ ($D$ = largest antenna dimension): a 1.5 m, 12 dBi 433 MHz Yagi has $2D^2/\lambda \approx 6.5$ m. The far-field formula **over-predicts** power density in the near field of such antennas, so it is conservative there [3 §2]. ICNIRP allows $S_{inc}$ (or both $E$ and $H$) in this zone [1].
- The FCC exemption formula requires $R \ge \lambda/2\pi$ [2].

### Rule details — body resonance, several transmitters, who is responsible, HF exemptions
**Why 30–300 MHz is the strictest band.** A human body absorbs most efficiently when it is roughly a resonant "antenna". For an ungrounded adult with the E-field along the body, the whole-body SAR peaks at about 65–70 MHz, where the height is ≈ 0.36–0.4 λ [6]. Standing on a conducting ground, the body acts like a λ/4 monopole and the resonance roughly halves [7]. Smaller bodies resonate higher. `s17_rf_exposure_rules.py` §1 gives, from $f \approx (0.36\text{–}0.4)\,c/L$: adult 1.75 m ≈ 62–69 MHz (grounded ≈ 31–34 MHz), child 1.2 m ≈ 90–100 MHz, infant 0.7 m ≈ 154–171 MHz. These are scaling estimates, not dosimetry. That is why both rule sets put their lowest flat power-density limit across this range: ICNIRP 2 W/m² public from 30 to 400 MHz, FCC 0.2 mW/cm² (2 W/m²) from 30 to 300 MHz. The FCC explicitly ties the 30–300 MHz minimum to efficient whole-body absorption (OET 65 [3]). Above a few hundred MHz the body is electrically large, so energy is absorbed nearer the surface and less of the incident power is taken up per kg. The limits therefore rise ∝ f and then flatten above 1.5–2 GHz. Below 30 MHz the body is electrically small and absorbs poorly, so the power-density limits rise again (∝ 1/f²).

**Several transmitters: the summation rule.** Exposure limits apply to the *total* field. For each source $i$ compute the fraction $S_i/S_{lim}(f_i)$ (for the reactive near field use $E^2$ and $H^2$ fractions). The site complies only if **$\sum_i S_i/S_{lim}(f_i) \le 1$**. This is the ICNIRP summation rule [1], and the FCC uses the same form for its multi-source exemption, "the sum of the fractional contributions" ≤ 1 (1.1307(b)(3)(ii)(B) [2]). *Example* (§3a): the E22 at 2 W (433 MHz) and the E220 at 1 W (868 MHz), both on dipoles and transmitting continuously. At 0.5 m the ICNIRP fractions are 0.43 + 0.11 = 0.54, which complies. At 0.3 m they are 1.19 + 0.30 = 1.49, over. The keep-out distance grows from 0.33 m for the E22 alone to **0.37 m** for both. The second radio adds little because the 868 MHz limit is twice as high.

**Who is responsible, and the 5 % rule.** In the US the licensee (or the applicant for equipment authorisation) carries the duty. Before an amateur station transmits from a place where people could be exposed above §1.1310, the licensee must evaluate it and keep people out of over-limit areas (47 CFR 97.13(c), read via LII). Household members who have been trained may be assessed against the occupational limits; everyone else is assessed against the general-population limits. At a **multi-transmitter site** where the limits are exceeded, compliance is the shared responsibility of every licensee whose source produces **more than 5 % of the applicable limit** (in power-density terms) in the over-limit area, and the licensees must share technical data (1.1307(b)(5)(i) [2]). *Example* (§3b): at one spot, an FM broadcaster contributes 93 %, a 2 m repeater 9 % and our 433 MHz uplink 3 %, for a total of 105 %. The broadcaster and the repeater are jointly responsible; we are not, because we are below 5 %. The 5 % rule is FCC-specific. Singapore has no published equivalent; NEA follows ICNIRP [4] and IMDA site rules apply. So treat summation as mandatory and responsibility as the operator's (see Open questions).

**Exemption thresholds, including HF** (1.1307(b)(3)(i) [2]). A transmitter needs no routine evaluation if any one of these holds: (A) its available time-averaged power is ≤ 1 mW at any distance; (B) for 0.3–6 GHz within 40 cm, a SAR-based power threshold is met; or (C) its ERP is at or below the Table 1 value for the separation $R$ (m) to the nearest person, with $R \ge \lambda/2\pi$:

| Frequency | Threshold ERP (W) | 100 W ERP exempt beyond |
|---|---|---|
| 0.3–1.34 MHz | 1920 R² | formula 0.23 m, but λ/2π ≥ 36 m (1.34 MHz) |
| 1.34–30 MHz | 3450 R²/f² | 7.1 MHz: 1.21 m (formula) → **6.72 m (λ/2π)**; 14.2 MHz: **3.36 m** (λ/2π); 28.5 MHz: **4.85 m** |
| 30–300 MHz | 3.83 R² | 5.11 m |
| 300–1500 MHz | 0.0128 R² f | 433 MHz: 4.25 m |
| 1.5–100 GHz | 19.2 R² | 2.28 m |

The trap is at HF. The formula alone exempts a 100 W ERP station on 40 m beyond 1.2 m, but the formula is valid only for $R \ge \lambda/2\pi$ (6.7 m at 7.1 MHz, 25 m at 1.9 MHz). Closer than that you are in the reactive near field and must evaluate, for example with an NEC near-field run or the OET 65 Supplement B tables. A 1 mW or less device is always exempt. That covers the Singapore 1 mW e.r.p. no-duty 433 MHz class [canonical](../00-math-foundations/canonical-values-and-conventions.md); the 10 mW class is exempt in practice at a few cm.

## Design equations & rules of thumb
| Quantity | Value | Source |
|---|---|---|
| ICNIRP 2020 whole-body S, public | 2 W/m² (30–400 MHz); f/200 (400–2000 MHz); 10 W/m² (2–300 GHz) | [1] Table 5 |
| ICNIRP 2020 whole-body S, occupational | 10; f/40; 50 W/m² | [1] Table 5 |
| ICNIRP 2020 local (6 min) S, public | 10 W/m² (30–400 MHz); 0.058 f^0.86 (400–2000 MHz); 40 W/m² (2–6 GHz) | [1] Table 6 |
| ICNIRP 2020 E-field, public, 30–400 MHz | 27.7 V/m; 400–2000 MHz 1.375 f^0.5 V/m | [1] Table 5 |
| FCC MPE, general population | 0.2 mW/cm² (30–300 MHz); f/1500 (300–1500 MHz); 1.0 mW/cm² (1.5–100 GHz); 30-min | [2] Table 1 |
| FCC MPE, occupational | 1.0; f/300; 5 mW/cm²; 6-min | [2] Table 1 |
| FCC SAR, public / occupational | 0.08 / 0.4 W/kg whole body; 1.6 W/kg (1 g) / 8 W/kg (1 g) peak; extremities 4 / 20 W/kg (10 g) | [2] 1.1310(b),(c) |
| FCC exemption threshold ERP | 3.83 R² (30–300 MHz); 0.0128 R² f (300–1500 MHz); 19.2 R² (1.5–100 GHz) W | [2] 1.1307(b)(3)(i)(C) |
| Ground reflection factor | 2.56 | [3] |

Numerical limits at our frequencies (from the script):

| f (MHz) | ICNIRP WB public | ICNIRP WB occ. | ICNIRP local public | FCC gen. pop. | FCC occ. |
|---|---|---|---|---|---|
| 433 | 2.17 W/m² | 10.8 | 10.7 | 2.89 | 14.4 |
| 868 | 4.34 | 21.7 | 19.5 | 5.79 | 28.9 |
| 915 | 4.58 | 22.9 | 20.4 | 6.10 | 30.5 |
| 2440 | 10.0 | 50.0 | 40.0 | 10.0 | 50.0 |

## Worked examples
**1. 2 W at 433 MHz with a 12 dBi Yagi (ground station uplink or an amateur beacon).** $P$ = 33 dBm, 0.5 dB cable → EIRP = 44.5 dBm = 28.2 W. ICNIRP public limit 2.165 W/m²:
$R = \sqrt{28.2/(4\pi\cdot 2.165)} = 1.02$ m (free space), ×1.6 = 1.63 m with ground reflection. At 20 % duty: 0.46 / 0.73 m. FCC general population (2.89 W/m²): 0.88 / 1.41 m. FCC exemption: ERP 17.2 W ≤ 0.0128·R²·433 → R ≥ 1.76 m. **Practical rule: keep people ≥ 2 m in front of the Yagi while it transmits, and never look along/lean over the boom while keyed.** Behind the antenna (front-to-back ratio ~15–20 dB) the distance shrinks ~6–10×.

**2. Rocket on the rail, E22-400T33D on a dipole, transmitting continuously.** EIRP 2.9 W. Public limit reached at 0.33 m (free space), 0.52 m (ground reflection). A team member arming the rocket with a hand 5 cm from the antenna is in the reactive near field; field estimates are invalid and local SAR could approach the limits for a 2 W source. Use a **radio-silent arming procedure** (see [lab safety](lab-safety-esd-high-power.md)) or transmit only after the pad is cleared.

**3. E220-900T30D, 1 W at 915 MHz, dipole.** EIRP 1.46 W; public limit 4.58 W/m² → 0.16 m (0.26 m with reflection). Low risk except when held.

**4. Singapore-exempt 433 MHz SRD, 10 mW e.r.p.** EIRP 16 mW → 2–4 cm. Negligible.

**5. Duty factor for telemetry.** SF9/125 kHz, 32-byte frame (247 ms) at 1 Hz → D = 0.25 → safe distance scales by √0.25 = 0.5. The E22 at 2 W on a Yagi then needs 0.5 m (free space, public).

## Practical notes
- **Ground stations:** mount transmit antennas above head height and away from where people stand; mark a keep-out zone in front of Yagis at ≥ 2 m for 2 W-class stations; interlock or clearly indicate "transmitting".
- **Receive-only antennas** (most of our ground stations — the telemetry link is downlink-only) create no exposure. The RTK-correction uplink does.
- **Bench work:** use a dummy load or attenuators; a 2 W PA into a bare SMA connector is an uncontrolled radiator at centimetre distances.
- **Measurement:** broadband isotropic field probes (E-field) or a calibrated antenna + spectrum analyser; average per the standard's window.
- **Multiple transmitters:** sum the fractions of each limit (both ICNIRP and FCC use a summation rule), e.g. the E22 + E220 rocket (keep-out 0.37 m continuous). At shared US sites the FCC 5 % rule decides who is jointly responsible ([rule details](#rule-details--body-resonance-several-transmitters-who-is-responsible-hf-exemptions)).
- **Singapore context:** NEA is the national radiation-protection authority and uses ICNIRP guidance [4]; IMDA/NEA state ambient levels are far below ICNIRP public limits.

## Common mistakes & misconceptions
- **"It's only 2 W, RF exposure doesn't matter."** Into a 12 dBi Yagi it is 28 W EIRP; the public limit is reached at ~1 m.
- **Using conducted power instead of EIRP** — antenna gain multiplies the power density on the main beam.
- **Using the far-field formula within λ/2π of an antenna** — not valid; SAR assessment is needed for body-worn/handheld conditions.
- **Ignoring time averaging** — it is allowed and significant for low-duty telemetry; conversely a stuck-on transmitter (firmware bug, continuous RTK) is D = 1.
- **"ICNIRP and FCC are the same."** They differ by ~25 % at 433 MHz and use different SAR averaging masses (FCC 1 g, ICNIRP 10 g).
- **"The exemption formula says 1.2 m, so my 40 m station is exempt at 2 m."** The Table 1 formula holds only for $R \ge \lambda/2\pi$ (6.7 m at 7 MHz). Closer than that, evaluate.
- **Checking each transmitter separately against its own limit.** Limits apply to the sum of the fractions. Two radios that are each at 60 % of their limit put the spot at 120 %.
- **Believing non-thermal claims** — ICNIRP 2020 found no substantiated adverse effects below the thresholds it uses; the limits already include factors 10–50.
- **"RF radiation is like X-rays, so any exposure risks DNA damage."** RF photons carry 10⁻⁶–10⁻³ eV, four to seven orders of magnitude below the ≈ 12 eV needed to ionise; more power means more heating, never ionisation (section above). The opposite error — **"non-ionising, so harmless at any power"** — is also wrong: high power density heats tissue (eyes first) and contact causes burns.

## How to simulate / verify
- `python3 tools/verify/reg_rf_exposure.py` — ICNIRP/FCC limits vs frequency, safe distances for our five configurations at 100/50/20 % duty, free space and ground reflection, FCC exemption distance; self-test checks the 433 MHz limits and the OET-65 formula.
- `python3 tools/verify/s17_rf_exposure_rules.py` — body-resonance scaling, FCC Table 1 exemption distances incl. HF and the λ/2π floor, ICNIRP/FCC sum of fractions for the two-radio rocket, 5 % rule example.
- For the near field of a Yagi, run an NEC-2 model and output near-field E/H on a grid ([antenna simulation](../08-antennas/antenna-simulation-nec-openems.md)); compare with the far-field estimate.
- SAR for a body next to a rocket antenna: openEMS/FDTD with a tissue phantom (advanced; usually unnecessary if the operating procedure keeps people away while transmitting).

## Open questions / gaps
- Which ICNIRP edition Singapore (NEA) applies for occupational settings; any Singapore workplace-safety requirement for RF.
- 47 CFR 97.13(c) read via the Cornell LII copy (2026-10-13, summary only). The SAR-based exemption (B) formula was not transcribed.
- No Singapore counterpart of the FCC 5 % shared-responsibility rule was found; whether IMDA/NEA assign responsibility at shared sites is unknown.
- The body-resonance numbers are scaling estimates. The grounded "half" factor rests on one peer-reviewed paper [7] read only as an abstract.
- Near-field measurements of our actual Yagi (none yet).

## Sources
1. ICNIRP, "Guidelines for limiting exposure to electromagnetic fields (100 kHz to 300 GHz)", *Health Physics* 118(5):483–524, 2020 — Tables 2, 5, 6; whole-body 4 W/kg rationale and reduction factors; near-/far-field compliance notes. https://www.icnirp.org/cms/upload/publications/ICNIRPrfgdl2020.pdf (peer-reviewed guideline)
2. 47 CFR §1.1310 (SAR limits; Table 1 MPE) and §1.1307(b)(3) (exemption thresholds; Table 1), eCFR current text read 2026-09-27. https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-1/subpart-I/section-1.1310 (regulation)
3. FCC OET, *Bulletin 65, Evaluating Compliance with FCC Guidelines for Human Exposure to Radiofrequency Electromagnetic Fields*, Edition 97-01 — far-field equations, 2.56 ground-reflection factor, near-field over-prediction. https://transition.fcc.gov/Bureaus/Engineering_Technology/Documents/bulletins/oet65/oet65.pdf (regulator bulletin)
4. NEA Singapore, "International Guidelines for RF Radiation" (last updated 19 Apr 2023). https://www.nea.gov.sg/our-services/radiation-safety/radiofrequency-radiation/international-guidelines-for-rf-radiation (regulator web)
5. M. Tschurlovits, "What is 'ionizing radiation'?", IAEA-CN-67/153 (IRPA/IAEA conference, 1997) — review of definitions: ICRU 33 (cut-off depends on circumstances), Attix (valence binding ≈ 4–25 eV), BEIR (≈ 34 eV per ion pair in tissue), EURATOM 1996 (wavelength ≤ 100 nm ⇔ 12.4 eV photons). https://www.osti.gov/etdeweb/servlets/purl/593131 (conference paper; read via pdftotext 2026-10-02). Photon energies computed with SI 2019 exact constants in `tools/verify/e6_beginner_numbers.py`.
6. DTIC report AD-A100029 (US Air Force dosimetry report; title not verified, the PDF was not retrievable and only a search excerpt was read): highest whole-body energy deposition for E ∥ body at 65–70 MHz for an adult, major length ≈ 0.36–0.4 λ. https://apps.dtic.mil/sti/tr/pdf/ADA100029.pdf. Consistent with the widely cited ≈ 70 MHz adult resonance of Durney et al., *Radiofrequency Radiation Dosimetry Handbook*, 4th ed., USAFSAM-TR-85-73 (1986), which was not re-read. (government report; medium)
7. A. Hirata et al., "Estimation of whole-body average SAR in human models due to plane-wave exposure at resonance frequency," 2012 (Nagoya Inst. Tech. repository) — the grounded standing posture is the worst case; a λ/4-monopole analogy for grounded humans. https://nitech.repo.nii.ac.jp/record/5747/files/HirataAkimasa_2012_A3.pdf (peer-reviewed; abstract-level)
