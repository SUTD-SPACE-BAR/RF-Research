# 09-propagation-link-budget — Propagation and link budgets

How radio waves get from a transmitter to a receiver and how to predict whether a link closes: the Friis equation and free-space loss (and why "high frequencies attenuate more" is a myth); the line-by-line link budget with G/T and C/N0 forms, worked for the team's 433 MHz 2 W (E22-400T33D) and 915 MHz 1 W (E220-900T30D) rocket downlinks; Fresnel zones, earth curvature and the radio horizon (when a descending rocket drops out of view); two-ray ground reflection, plane-earth loss, lobing and the landed-rocket problem; empirical and ITU-R/NTIA models (Hata, Egli, P.528 air-to-ground, P.1546, P.1812, ITM); multipath fading, delay spread and Doppler — including the Doppler *rate* limit of LoRa during boost; gases, rain, fog, vegetation and buildings; the ionosphere (HF, Faraday rotation, scintillation, GNSS delay); solar activity and space weather; HF modes and prediction (MUF/LUF, NVIS, grey line, P.533/VOACAP); VHF/UHF anomalous propagation (ducting, sporadic-E, meteor, aurora, TEP, EME); ground wave at LF/MF; knife-edge and multiple-edge diffraction; fade margin and availability; and polarisation mismatch with rocket attitude. Antenna design lives in [08-antennas](../08-antennas/_index.md), receiver noise in [07-noise-linearity](../07-noise-linearity/_index.md), LoRa PHY details in [15-lora-ism-radios](../15-lora-ism-radios/_index.md). Every numeric claim is reproduced by a script in `tools/verify/prop_*.py` or `tools/verify/prop2_*.py`.

## Reading order (beginner → advanced)
1. [Friis equation and free-space path loss](friis-free-space-path-loss.md) — aperture derivation, FSPL constants and table, EIRP/ERP, field strength, the frequency myth.
2. [Link budget methodology](link-budget-methodology.md) — template, G/T–C/N0 form, 433/915 MHz rocket downlinks at 30 km, impairment allocation, plume, landed case.
3. [Fresnel zones, LOS and radio horizon](fresnel-zones-los-radio-horizon.md) — Fresnel radius, 60 % rule, k = 4/3, horizon, descent LOS/Fresnel loss altitudes.
4. [Two-ray ground reflection](two-ray-ground-reflection.md) — plane-earth law, breakpoint, Brewster, minimum effective height, GS lobing, landed rocket H vs V.
5. [Polarisation mismatch loss](polarization-mismatch-loss.md) — PLF, AR formula, rocket attitude (ψ) geometry, roll, CP vs linear ground antennas.
6. [Multipath fading and Doppler](multipath-fading-doppler.md) — Rayleigh/Rician, delay spread, coherence, rocket Doppler and the LoRa drift limit, diversity.
7. [Link margin and availability](link-margin-availability.md) — margin vs outage, Suzuki composite, RSS vs linear, bursty losses, per-flight-phase budgets.
8. [Diffraction and knife-edge](diffraction-knife-edge.md) — J(v), P.526 approximation, Deygout/Epstein–Peterson/Bullington, landed rocket behind a ridge.
9. [Empirical path-loss models](empirical-path-loss-models.md) — log-distance, Hata, COST-231, Egli, P.528/P.1546/P.1812/P.1411/P.452, ITM; model choice.
10. [Atmospheric, rain, fog, vegetation, building loss](atmospheric-rain-attenuation.md) — P.676 line-by-line, P.838, P.840, P.833, P.2109.
11. [Ionosphere and HF propagation](ionospheric-hf-propagation.md) — plasma frequency, MUF, NVIS, Faraday, scintillation, GNSS iono delay.
12. [Solar activity and space weather](solar-activity-and-space-weather.md) — sunspot cycle (SC25 peak 160.9 in Oct 2024), F10.7, K/A/Kp, flares and SIDs (HAF), CMEs and Bz, NOAA R/S/G scales, PCA, equatorial anomaly and Singapore GNSS scintillation.
13. [HF propagation modes and prediction](hf-propagation-modes-and-prediction.md) — MUF/LUF/FOT, critical angle, hop limits, skip, chordal hop, grey line, long path, NVIS, o/x waves, scatter, P.1239/P.533 prediction (validated vs ITURHFProp), Singapore → Perth/Sydney, WSPR/RBN/PSKReporter.
14. [VHF/UHF anomalous propagation](vhf-uhf-anomalous-propagation.md) — refractivity and M-units, −157 N/km ducting, trapped wavelength, ducted LoRa, sporadic-E (P.534), meteor scatter, aurora, TEP, aircraft scatter, EME.
15. [Ground wave and LF/MF propagation](ground-wave-and-lf-mf-propagation.md) — Sommerfeld–Norton surface wave, numerical distance, P.368/LFMF (re-implemented), conductivity, vertical polarisation, MF day/night, Millington, LF/VLF.
16. [Satellite links, Doppler and tracking](satellite-links-doppler-tracking.md) — LEO/MEO/GEO geometry, slant range, Singapore pass simulation, Doppler and Doppler rate (v⊥²/R), transponder Doppler, G/T, 437 MHz CubeSat / TinyGS LoRa / Meteor-M 137.9 MHz budgets, Gpredict + hamlib, keyhole, QO-100 from Singapore.

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [friis-free-space-path-loss](friis-free-space-path-loss.md) | Friis 1946, $A_e = G\lambda^2/4\pi$ from thermodynamics, FSPL dB constants and table 433 MHz–77 GHz, frequency-myth numbers, flux density/field strength, far-field condition, balloon-record sanity check | mixed | high |
| [link-budget-methodology](link-budget-methodology.md) | template, noise reference, G/T and C/N0, 433 MHz (−75.8 dBm, +52 dB) and 915 MHz (−83.0 dBm, +45 dB) at 30 km, range vs SF table, impairment allocation incl. plume, landed rocket | mixed | high |
| [fresnel-zones-los-radio-horizon](fresnel-zones-los-radio-horizon.md) | Fresnel radius (exact vs paraxial vs ITU), 60 % rule from J(v), k-factor from dN/dh, horizon 4.12√h, ground-clearance heights, rocket-descent LOS/Fresnel altitudes, elevation angles | mixed | high |
| [two-ray-ground-reflection](two-ray-ground-reflection.md) | two-ray with Fresnel coefficients, $d_c = 4h_1h_2/\lambda$, 40 dB/dec, Brewster angles, min effective height (V 44 cm / H 3 cm at 433 MHz), lobing nulls/depth/rate, CP reflection, roughness, landed and pad cases | mixed | high |
| [empirical-path-loss-models](empirical-path-loss-models.md) | model-selection table, log-distance + σ, Hata/COST-231/Egli formulas with validity, ITU-R/NTIA methods and scopes, secondary-source contradictions, 2 m-node misuse of Hata | mixed | medium |
| [multipath-fading-doppler](multipath-fading-doppler.md) | Rayleigh/Rician outage, delay spread/Bc, Clarke/LCR/AFD, Tc, rocket Doppler 1.5 kHz @433 (Mach 3), Doppler-rate vs Freq_drift_max table, K for air-to-ground, diversity | mixed | high |
| [atmospheric-rain-attenuation](atmospheric-rain-attenuation.md) | P.676-11 line-by-line gases, P.838-3 rain, P.840 fog, P.833/Weissberger foliage, P.2109 building entry, 77 GHz radar in tropical rain | mixed | high |
| [ionospheric-hf-propagation](ionospheric-hf-propagation.md) | plasma dispersion, secant law, MUF/skip/NVIS, curved-earth hop geometry, Faraday (P.531), scintillation, GNSS 40.3 TEC/f², iono-free combination; rocket below ionosphere | mixed | medium |
| [diffraction-knife-edge](diffraction-knife-edge.md) | Fresnel–Kirchhoff derivation, exact J(v) vs P.526 approx (≤ 0.12 dB), asymptote, rounded obstacle, Deygout/E–P/Bullington comparison, landed rocket behind ridges | mixed | high |
| [link-margin-availability](link-margin-availability.md) | lognormal/Rayleigh/Rician/Suzuki margins (median-referenced), mean-vs-median trap, RSS vs linear, Gilbert–Elliott repetition, flight-phase reliability | intermediate | high |
| [polarization-mismatch-loss](polarization-mismatch-loss.md) | PLF, Poincaré-sphere derivation of the AR formula, finite-AR tables, rocket attitude (ψ) cases, roll modulation, depolarisation, polarisation diversity | mixed | high |
| [solar-activity-and-space-weather](solar-activity-and-space-weather.md) | SILSO/SWPC cycle data to Sep 2026, F10.7–SSN relation, flare classes and D-RAP HAF, absorption theory, K→a_k→A, CME timing, PCA, NOAA scales, P.1239 foE, IGRF dip of Singapore (−12.7°), equatorial-anomaly GNSS effects with NTU scintillation statistics | mixed | high |
| [hf-propagation-modes-and-prediction](hf-propagation-modes-and-prediction.md) | MUF/LUF/FOT, critical angle, E/F2 hop limits, skip, NVIS, grey line, long path, chordal hop, o/x, scatter, P.533 absorption and link budget, own P.1239/P.533 implementation validated vs ITURHFProp, Singapore→Perth hourly MUF table, prediction and reporting tools | mixed | high |
| [vhf-uhf-anomalous-propagation](vhf-uhf-anomalous-propagation.md) | P.453 refractivity, −157 N/km and M-units derivation, λ_max = 2.5 d √ΔM (WKB derivation), ducted 915 MHz LoRa budget, Es (P.534 + foEs maps), meteor decay ∝ λ², aurora, TEP geometry (IGRF), aircraft scatter, EME loss table | mixed | high |
| [ground-wave-and-lf-mf-propagation](ground-wave-and-lf-mf-propagation.md) | Sommerfeld–Norton numerical distance and attenuation, P.368-10/LFMF re-implementation (5/5 reference cases), field-strength tables 0.2–30 MHz, V vs H, coverage ranges, Millington mixed path, MF day/night, VLF waveguide | mixed | high |
| [satellite-links-doppler-tracking](satellite-links-doppler-tracking.md) | orbit classes, slant range/footprint, two-body + J2 pass simulation from Singapore, Doppler ±10.3 kHz @437 MHz and 151 Hz/s at zenith, keyhole 156°/s, inverting-transponder Doppler, G/T and C/N0 budgets (437 MHz 9k6, LoRa SF7–12 incl. per-packet drift, Meteor-M LRPT vs P.372 man-made noise), Gpredict/hamlib/rigctld/rotctld, GEO elevation | mixed | medium |

## Domain FAQ (top questions → page#section)
- *How far will my 433 MHz 2 W LoRa reach from a rocket?* → [link budget § Example A](link-budget-methodology.md#example-a--433-mhz-e22-400t33d-downlink-30-km-slant-range-crossed-yagi-ground-station)
- *Is 433 or 915 MHz better for range?* → [Friis § Worked example 2](friis-free-space-path-loss.md#worked-examples)
- *Do higher frequencies attenuate more in free space?* → [Friis § Common mistakes](friis-free-space-path-loss.md#common-mistakes--misconceptions)
- *When will my descending rocket drop below the horizon?* → [Fresnel § Worked example 2](fresnel-zones-los-radio-horizon.md#worked-examples)
- *Why can't I hear the rocket after it lands?* → [two-ray § Worked example 1](two-ray-ground-reflection.md#worked-examples) and [link budget § Example E](link-budget-methodology.md#example-e--landed-rocket-the-case-that-actually-limits-recovery)
- *Why does the signal fade every few seconds during ascent?* → [two-ray § Level 3 lobing](two-ray-ground-reflection.md#level-3--minimum-effective-height-lobing-roughness-curvature)
- *Can LoRa handle the Doppler of a Mach 3 rocket?* → [multipath § Level 2](multipath-fading-doppler.md#level-2--derivations)
- *Which SF should I use during boost?* → [multipath § Worked example 2](multipath-fading-doppler.md#worked-examples)
- *Linear or circular ground antenna?* → [polarisation § Worked example 1](polarization-mismatch-loss.md#worked-examples)
- *Where should the ground station be relative to the pad?* → [polarisation § Worked example 3](polarization-mismatch-loss.md#worked-examples)
- *How much fade margin do I need?* → [margin § TL;DR](link-margin-availability.md#tldr)
- *Does rain affect my LoRa link?* → [atmospheric § TL;DR](atmospheric-rain-attenuation.md#tldr)
- *How much do trees/buildings cost?* → [atmospheric § Worked examples 4–5](atmospheric-rain-attenuation.md#worked-examples)
- *Which propagation model should I use?* → [empirical § TL;DR](empirical-path-loss-models.md#tldr)
- *Does the rocket plume block the signal?* → [link budget § Level 3](link-budget-methodology.md#level-3--what-the-nominal-budget-leaves-out)
- *How big is the GNSS ionospheric error?* → [ionosphere § Level 3](ionospheric-hf-propagation.md#level-3--layers-variability-and-the-effects-that-matter-to-marcus)
- *What do the K-index, A-index and solar flux mean? Where is Solar Cycle 25 now?* → [space weather § TL;DR](solar-activity-and-space-weather.md#tldr)
- *Why does GNSS degrade after sunset near the equinoxes in Singapore?* → [space weather § Level 3](solar-activity-and-space-weather.md#level-3--storms-polar-caps-and-the-equatorial-ionosphere)
- *Which HF band reaches Australia from Singapore, and when?* → [HF modes § Worked example 1](hf-propagation-modes-and-prediction.md#worked-examples)
- *What are MUF, LUF, FOT, skip zone, grey line, long path and NVIS?* → [HF modes § TL;DR](hf-propagation-modes-and-prediction.md#tldr)
- *My LoRa node heard a station 400 km away — ducting?* → [anomalous § Worked example 1](vhf-uhf-anomalous-propagation.md#worked-examples)
- *How does meteor scatter, sporadic-E, TEP or EME work?* → [anomalous § Level 2–3](vhf-uhf-anomalous-propagation.md#level-2--derivations)
- *Why does ground-wave range fall with frequency, and why vertical polarisation?* → [ground wave § Level 2](ground-wave-and-lf-mf-propagation.md#level-2--where-it-comes-from-and-what-it-means)

- *How much Doppler does a CubeSat have, and can LoRa decode it?* → [satellite links § Worked examples](satellite-links-doppler-tracking.md#worked-examples)
- *Why does my 137 MHz weather-satellite reception not improve with an LNA?* → [satellite links § Example 4](satellite-links-doppler-tracking.md#worked-examples)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Rappaport *Wireless Communications*; Goldsmith *Wireless Communications*; Parsons *The Mobile Radio Propagation Channel*; Saunders & Aragón-Zavala *Antennas and Propagation for Wireless Communication Systems*; Seybold *Introduction to RF Propagation*; Balanis *Antenna Theory*; Friis 1946; Bullington 1947/1957; Deygout 1966; Hata 1980; ITU-R P.368, P.372, P.453, P.525, P.526, P.527, P.528, P.531, P.533, P.534, P.676, P.833, P.838, P.840, P.1239, P.1546, P.1812, P.2109; NTIA ITM and LFMF; ITURHFProp; NOAA SWPC; SILSO; Davies *Ionospheric Radio*; McNamara *Radio Amateur's Guide to the Ionosphere*.

## Known gaps
- No site-specific (DEM-based) ITM/P.1812/P.528 predictions for actual launch/landing sites; NTIA libraries not yet wrapped in `tools/`.
- Plume attenuation for student-scale motors at 433/915 MHz is unquantified (large-launcher data only).
- Installed rocket-antenna patterns (co/cross-pol) unknown — the sin²ψ dipole model is an idealisation (domain 08).
- LoRa PER vs Doppler-rate has not been measured; the SX126x drift limit is the only criterion.
- EBYTE air-rate → SF/BW mapping unknown (sensitivity −128 dBm at 2.4 kb/s is a physics estimate).
- Scintillation statistics for Singapore now quoted from NTU measurements (2012–2014, near SC24 max); a TEC climatology and P.453 duct-occurrence maps for Singapore are still not extracted.
- P.533 detailed mirror height (eqs 14–16) and full absorption/noise (ATnoon, φn, p, P.372 atmospheric noise maps) are not implemented, so there is no own LUF/reliability calculation. Use ITURHFProp or VOACAP.
- P.368 very-dry-ground and ice constants are unconfirmed; no Singapore ground-conductivity values from P.832.
