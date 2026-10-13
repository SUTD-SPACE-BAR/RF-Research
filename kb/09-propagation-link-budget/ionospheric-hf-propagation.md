---
title: The ionosphere — HF skywave, MUF, NVIS, Faraday rotation, scintillation and GNSS delay
domain: 09-propagation-link-budget
slug: ionospheric-hf-propagation
tags: [ionosphere, plasma-frequency, critical-frequency, foF2, MUF, secant-law, skip-distance, NVIS, D-layer-absorption, sporadic-E, faraday-rotation, scintillation, S4, TEC, GNSS-ionospheric-delay, ionosphere-free-combination]
prerequisites: [fresnel-zones-los-radio-horizon.md, ../02-electromagnetics/wave-equation-plane-waves-polarization.md]
related: [hf-propagation-modes-and-prediction.md, solar-activity-and-space-weather.md, vhf-uhf-anomalous-propagation.md, ground-wave-and-lf-mf-propagation.md, polarization-mismatch-loss.md, atmospheric-rain-attenuation.md, ../07-noise-linearity/thermal-noise-and-noise-temperature.md, ../08-antennas/gnss-antennas.md, ../19-regulations-safety/amateur-radio-licensing.md]
level: mixed
confidence: medium
last_updated: 2026-10-03
---

# The ionosphere — HF skywave, MUF, NVIS, Faraday rotation, scintillation and GNSS delay

## Questions this page answers
- Does the ionosphere affect my rocket's 433/915 MHz telemetry?
- Why does HF (3–30 MHz) travel thousands of km while UHF does not?
- What are the critical frequency, the MUF and the skip zone?
- What is NVIS and when is it used?
- What is Faraday rotation, and why do satellite links at VHF/UHF use circular polarisation?
- What is ionospheric scintillation, and is Singapore affected?
- How much ionospheric error does GNSS see, and how do dual-frequency receivers remove it?
- What are the ordinary and extraordinary waves, and why does a vertical or a horizontal antenna both work for HF skywave?
- What is the "critical angle"?

## TL;DR
- The ionosphere is a plasma (60–1000 km). A wave of frequency $f$ is reflected at vertical incidence where the **plasma frequency** $f_p = 8.98\sqrt{N_e}$ Hz reaches $f$ ($N_e$ in electrons/m³). The F2 peak ($N_e \sim 10^{11}$–$3\times10^{12}$ m⁻³) gives a **critical frequency foF2 ≈ 3–15 MHz** (`tools/verify/prop_ionosphere.py`).
- **Secant law:** at oblique incidence (angle $i$ from vertical at the layer) the layer reflects up to $f = foF2\cdot\sec i$: the **MUF** of a path. For a 3000 km hop via a 300 km layer, $\sec i$ ≈ 3.3 (standard factor M(3000)F2 ≈ 3). Single-hop F2 range ≤ ~3800 km.
- Above the MUF the wave goes through → **skip zone** (e.g. 14 MHz with foF2 = 8 MHz: ~860 km flat-earth skip). **NVIS**: $f$ < foF2 (typ. 2–10 MHz) radiated near vertically covers 0–~400 km with no skip zone — used for regional HF comms in rough terrain.
- **Your rocket telemetry is not affected:** rockets below ~60 km and their ground stations are *below* the ionosphere (D region starts ~60 km), and 433/915 MHz is far above foF2. The ionosphere matters for **GNSS** (and would matter for any satellite link or for HF).
- **GNSS delay:** $\Delta\rho = 40.3\,\text{TEC}/f^2$ m (TEC in el/m²): **0.162 m per TECU at L1**, 0.267 m at L2, 0.291 m at L5 (1 TECU = 10¹⁶ el/m²); daytime TEC 10–100+ TECU ⇒ 1.6–16 m at L1. Dual-frequency iono-free combination $P_{IF} = 2.546P_1 - 1.546P_2$ removes the first-order term (noise ×2.98).
- **Faraday rotation** $\Omega = 2.36\times10^{4}B_LN_T/f^2$ rad (ITU-R P.531): at 433 MHz with 10¹⁸ el/m² and $B_L$ = 3×10⁻⁵ T, 216° — linear-polarised Earth–space links fade unpredictably; hence CP for satellites below ~3 GHz.
- **Scintillation** (S4 ∝ $f^{-1.5}$ in weak/moderate regimes) is strongest near the geomagnetic equator after sunset; Singapore lies in the equatorial belt — expect occasional L1 tracking degradation, not a telemetry issue.

## Intuition (no math)
Sunlight (UV and X-rays) strips electrons from upper-atmosphere atoms, creating layers of free electrons. A radio wave passing through makes these electrons oscillate; below a certain frequency (the **plasma frequency**) the electrons can follow the field fast enough to cancel it, and the wave is reflected. Above it, the electrons cannot keep up and the wave passes through, slightly slowed and bent.

HF waves (3–30 MHz) are near the plasma frequencies of the F layer, so they are bent back to Earth and can hop around the planet. The steeper the angle at which a wave hits the layer, the easier it passes through — so a given layer can reflect higher frequencies at grazing angles (long paths) than straight up. The highest frequency that still comes back on a given path is the **MUF**. Choose a frequency below the MUF; too far below and the D layer (low, collisional, daytime) absorbs it.

VHF/UHF (≥ 100 MHz) go straight through the ionosphere with only small effects: a slight delay (which GNSS must correct), a rotation of the polarisation plane (Faraday), and in some regions rapid twinkling (scintillation) caused by turbulent electron-density bubbles.

A rocket that flies to tens of kilometres never reaches the ionosphere, so its link to the ground is pure troposphere. Only its GNSS receiver, listening to satellites 20 000 km up, looks through the ionosphere.

## The math

### Level 1 — core relations
- Plasma frequency: $f_p = \dfrac{1}{2\pi}\sqrt{\dfrac{N_ee^2}{\varepsilon_0m_e}} = 8.98\sqrt{N_e}$ Hz. Refractive index (collisionless, no magnetic field): $n^2 = 1 - (f_p/f)^2$.
- Vertical-incidence reflection when $f \le f_p$ somewhere; **critical frequency** foF2 = $f_p$ at the F2 peak: 5 MHz ↔ 3.1×10¹¹ m⁻³; 8 MHz ↔ 7.9×10¹¹; 12 MHz ↔ 1.8×10¹² (script §1).
- **Secant law (flat mirror):** $\text{MUF} = f_c\sec i$, with $i$ the incidence angle from vertical at the layer. For ground range $D$ and virtual height $h'$: $\tan i = (D/2)/h'$.
- **Skip distance** (flat): $D_\text{skip} = 2h'\sqrt{(f/f_c)^2 - 1}$.
- **Group delay / range error** (P.531 eq. 4): $\Delta t = 1.345\times10^{-7}N_T/f^2$ s ⇒ $\Delta\rho = c\,\Delta t = 40.3\,N_T/f^2$ m ($N_T$ = TEC along the path, el/m²; $f$ Hz). The phase is advanced by the same amount (phase–group divergence).
- **Faraday rotation** (P.531 eq. 2): $\Omega = 2.36\times10^{-14}B_{av}N_T/f_\text{GHz}^2$ rad ⇔ $2.36\times10^{4}B_{av}N_T/f_\text{Hz}^2$; XPD for aligned linear antennas $= -20\log_{10}|\tan\Omega|$ dB.
- **Scintillation index** $S_4 = \sqrt{(\langle I^2\rangle - \langle I\rangle^2)/\langle I\rangle^2}$; weak: S4 < 0.3, moderate 0.3–0.6, strong > 0.6; weak–moderate frequency scaling $S_4 \propto f^{-1.5}$ (P.531 [1]).

### Level 2 — derivations
**Plasma dispersion.** An electron in field $E_0e^{j\omega t}$ obeys $m\ddot x = -eE$ (collisionless), so $x = eE/(m\omega^2)$ and the polarisation $P = -N_eex = -N_ee^2E/(m\omega^2)$. Then $\varepsilon_r = 1 + P/(\varepsilon_0E) = 1 - \omega_p^2/\omega^2$ with $\omega_p^2 = N_ee^2/(\varepsilon_0m)$. For $\omega < \omega_p$, $n$ is imaginary (evanescent) — total reflection. Phase velocity $c/n > c$, group velocity $cn < c$, and $v_pv_g = c^2$: the group is delayed and the phase advanced by the same amount, $\approx \frac{1}{2}(f_p/f)^2$ per unit length for $f \gg f_p$. Integrating $\frac{1}{2}\cdot\frac{e^2N_e}{4\pi^2\varepsilon_0m f^2}$ along the path gives $\Delta\rho = \frac{e^2}{8\pi^2\varepsilon_0m}\frac{\text{TEC}}{f^2} = 40.3\,\text{TEC}/f^2$ m — the constant 40.3 m³/s² follows from fundamental constants (script cross-checks it against the P.531 1.345×10⁻⁷ form: 0.162 m/TECU at L1 both ways).

**Secant law.** In a horizontally stratified layer (Snell's law with $n$ varying with height), a ray entering at angle $i$ from vertical turns back where $n = \sin i$, i.e. $1 - f_p^2/f^2 = \sin^2i$ ⇒ $f = f_p/\cos i$. The maximum usable frequency for the path is therefore foF2 · sec $i$. With a curved Earth, the incidence angle at a 300 km mirror for ground ranges 1000/2000/3000 km is sec $i$ = 1.86/2.82/3.28, with take-off elevations 28°, 12° and 4° (script §3); zero-elevation take-off limits one F2 hop to ~3840 km (2350 km via the E layer at 110 km).

**Ionosphere-free combination.** With pseudoranges $P_k = \rho + 40.3\,\text{TEC}/f_k^2 + \dots$, the combination $P_{IF} = \frac{f_1^2P_1 - f_2^2P_2}{f_1^2 - f_2^2}$ cancels the $1/f^2$ term exactly (script: residual 3.6×10⁻¹⁵ m for 50 TECU). For L1/L2 the coefficients are 2.5457 and −1.5457, amplifying uncorrelated noise by $\sqrt{2.546^2 + 1.546^2}$ = 2.98.

### Level 3 — layers, variability and the effects that matter to Marcus
**Layers (typical daytime mid-latitude values; textbook ranges [3][4]).** D: 60–90 km, $N_e$ ~10⁸–10¹⁰ m⁻³, disappears at night; collisions make it absorbing (absorption ∝ $1/(f \pm f_L)^2$ in theory and in ITU-R P.533; operational models such as NOAA D-RAP fit $f^{-1.5}$ — see [space weather Level 2](solar-activity-and-space-weather.md#level-2--derivations)), limiting daytime use of low HF. E: ~90–130 km, foE ~2–4 MHz by day. F1: 150–220 km (day only). F2: 250–450 km, foF2 3–15 MHz, varying strongly with local time, season, the 11-year solar cycle (Solar Cycle 25 peaked at a smoothed sunspot number of 160.9 in October 2024 — [space weather](solar-activity-and-space-weather.md)), latitude and geomagnetic storms. ITU-R P.1239 (reference ionospheric characteristics) and P.533 (HF circuit prediction) give global models; programs like VOACAP implement them.

**Sporadic E (Es).** Thin, dense E-layer patches, mostly in summer at mid-latitudes, can reflect up to ~50–150 MHz over 1000–2000 km — the one way VHF can "skip". Not relevant at 433 MHz. Seasons, times, ITU-R P.534 field strengths and the other VHF modes (meteor scatter, aurora, TEP, EME) are in [VHF/UHF anomalous propagation](vhf-uhf-anomalous-propagation.md).

**Magneto-ionic splitting and the polarisation of skywave.** Because of the Earth's magnetic field, the ionosphere is birefringent. Appleton–Hartree theory gives two characteristic waves, the **ordinary (o)** and **extraordinary (x)** waves. They are independently propagating and elliptically polarised, with different refractive indices, reflection heights and absorption. The x-wave reflects where $f_p^2 = f(f - f_H)$, so its critical frequency exceeds foF2 by about $f_H/2$: ≈ 0.5 MHz over Singapore, where $f_H$ ≈ 1.0 MHz. It is also absorbed more, because its loss scales with $(f - f_L)^{-2}$. Faraday rotation is the slowly varying phase difference between the two modes. Consequence: a returning HF skywave has a random, time-varying elliptical polarisation, so **either a vertically or a horizontally polarised antenna can be used** for skywave transmission and reception. Choose on pattern (take-off angle) and noise, not polarisation match. The o/x interference also contributes to irregular fading. Details: [HF modes and prediction, Level 2](hf-propagation-modes-and-prediction.md#level-2--derivations-and-what-they-imply).

**Critical angle.** For a frequency $f$ above foF2, rays steeper than $\cos i_c = f_oF2/f$ at the layer penetrate. The corresponding highest take-off angle that still returns to Earth is the **critical angle**: about 31° for 14 MHz with foF2 = 8 MHz. Below it the wave returns, beyond the skip zone. Hop ranges, LUF/FOT, grey line, long path, chordal hop and real path predictions (Singapore → Perth/Sydney) are in [HF propagation modes and prediction](hf-propagation-modes-and-prediction.md).

**Faraday rotation (P.531 [1]).** For Earth–space paths, the plane of a linearly polarised wave rotates by $\Omega \propto B_LN_T/f^2$: at 433 MHz, 22° for 10¹⁷ el/m² and 216° for 10¹⁸ el/m² ($B_L$ = 3×10⁻⁵ T); at 915 MHz 5–49°; at L1 1.6–16° (script §5). P.531 Table 3 quotes 108° at 1 GHz for 10¹⁸ el/m² vertical TEC at 30° elevation — consistent with the formula for a slant factor of 1.75 and $B_L$ ≈ 4.6×10⁻⁵ T. Because $\Omega$ varies with time, linear-polarised satellite links at VHF/UHF fade unpredictably; circular polarisation is immune (a rotation of CP is only a phase shift). **Not applicable to the rocket-to-ground path** (below the ionosphere).

**Scintillation.** Small-scale irregularities (equatorial plasma bubbles after sunset near equinoxes; auroral/polar irregularities) diffract the wave, producing rapid amplitude and phase fluctuations. Strong equatorial scintillation affects L-band (GNSS, 1.2–1.6 GHz) and even C-band; S4 ∝ $f^{-1.5}$ in the weak regime saturates near 1 in the strong regime (Rayleigh-like intensity). Singapore lies within about 10° of the geomagnetic dip equator, in the equatorial scintillation region; post-sunset L1 tracking losses and degraded RTK are documented phenomena in the region (qualitative here — see Open questions).

**GNSS error magnitudes.** Vertical TEC ranges roughly 10¹⁶–10¹⁸ el/m² (1–100 TECU) (P.531 §3.1); near the equatorial anomaly crests daytime values toward the upper end are common. Slant paths multiply by the obliquity factor (≈ 1.75 at 30° elevation, ~3 near the horizon). Single-frequency receivers apply a broadcast model (Klobuchar for GPS, NeQuick-G for Galileo) that removes roughly half the delay; dual-frequency receivers (ZED-F9P: L1/L2) remove the first-order term almost entirely; RTK removes the common part between base and rover (short baselines). For a rocket GNSS (MAX-M10S L1-only; ZED-F9P L1/L2 but flown with an L1-only antenna per the avionics notes) the ionospheric error during flight is the single-frequency residual (metres) — negligible for recovery, relevant for precise trajectory reconstruction.

**Effect on 433/915 MHz satellite reception (if ever used):** group delay 2.15 m/TECU at 433 MHz (21–215 m for 10–100 TECU), strong Faraday rotation, scintillation stronger than at L-band by $(1575/433)^{1.5}$ = 6.9× in S4 (saturating).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $f_p = 8.98\sqrt{N_e}$ | cold plasma | $N_e$ = 10¹² → 9.0 MHz |
| MUF = foF2 · sec $i$ | oblique incidence | 3000 km hop: ≈ 3 × foF2 |
| $D_\text{skip} = 2h'\sqrt{(f/f_c)^2-1}$ | flat approx. | 14 MHz, foF2 8: ~860 km |
| FOT ≈ 0.85 MUF | operating practice | |
| $\Delta\rho = 40.3\,\text{TEC}/f^2$ | $f \gg f_p$ | L1: 0.162 m/TECU |
| $P_{IF} = 2.546P_1 - 1.546P_2$ | L1/L2 | noise × 2.98 |
| $\Omega = 2.36\times10^4B_LN_T/f^2$ rad | Earth–space | 433 MHz, 10¹⁸, 3e-5 T: 216° |
| $S_4 \propto f^{-1.5}$ | weak/moderate scintillation | |
| D-layer absorption ∝ $1/(f+f_L)^2$ (theory/P.533); $f^{-1.5}$ (D-RAP fit) | daytime HF | worst at 2–5 MHz |

## Worked examples
**1 — Is there any ionospheric effect on the 433 MHz downlink?** No: the rocket (≤ tens of km) and the ground station are both below the D region; 433 MHz ≫ foF2 anyway. Tropospheric refraction (k = 4/3) is the only "atmospheric bending" to include ([fresnel-zones-los-radio-horizon](fresnel-zones-los-radio-horizon.md)).

**2 — Picking an HF frequency for a 1000 km path.** foF2 = 8 MHz, $h'$ = 300 km: flat-earth sec $i$ gives MUF 15.5 MHz, FOT ≈ 13 MHz (script §2); curved-earth sec $i$ = 1.86 gives 14.9 MHz. The 20 m amateur band (14 MHz) would work; 21 MHz would skip.

**3 — NVIS for field comms at a remote launch site.** Target 0–300 km with no skip zone: choose $f$ ≈ 0.85·foF2 (e.g. 5–7 MHz by day, 3–4 MHz at night), horizontal dipole about 0.1–0.25 λ above ground to radiate upward. (Requires the appropriate licence — [19-regulations-safety/amateur-radio-licensing](../19-regulations-safety/amateur-radio-licensing.md).)

**4 — GNSS ionospheric error on the rocket.** Midday TEC 50 TECU, satellite at 30° elevation (obliquity 1.75): slant 87.5 TECU → 14.2 m at L1. A broadcast Klobuchar correction removing ~50 % leaves ~7 m (varies between satellites, mostly common-mode for position → a few metres of position error, mostly vertical). Dual-frequency L1/L2 removes it at the cost of ×3 code noise.

## Practical notes
- **HF propagation is a forecast problem:** use VOACAP/ITU-R P.533-based predictions and real-time ionosonde data (foF2 maps) rather than fixed rules.
- **For satellites (e.g. amateur LEO at 145/435 MHz)** use CP antennas because of Faraday rotation; expect Doppler (±10 kHz at 435 MHz from LEO) — see [multipath-fading-doppler](multipath-fading-doppler.md).
- **GNSS in Singapore after sunset near equinox:** expect occasional cycle slips/RTK float solutions from scintillation; schedule precision tests accordingly (qualitative guidance).

## Common mistakes & misconceptions
- **"The ionosphere bends my UHF rocket signal."** It does not reach the ionosphere; UHF passes straight through anyway.
- **Thinking higher power beats the MUF.** Above the MUF the wave does not come back regardless of power.
- **Using foF2 as the usable frequency for long paths** — the MUF is foF2 × sec i, several times higher.
- **Forgetting that group delay and phase advance have opposite signs** (code–carrier divergence in GNSS).
- **Assuming dual-frequency removes all ionospheric error** — higher-order terms (∝ 1/f³) and scintillation remain, and the combination amplifies noise.

## How to simulate / verify
- `tools/verify/prop_ionosphere.py` — plasma frequency, $n^2$, secant-law MUF, skip, curved-earth hop geometry, GNSS delay per TECU (two forms), iono-free combination check, Faraday rotation and XPD, P.531 Table 3 consistency, S4 scaling.
- VOACAP / ITU-R P.533 software for HF circuit predictions; IRI (International Reference Ionosphere) or NeQuick for TEC; RTKLIB to analyse GNSS iono residuals from logged raw data (u-blox RXM-RAWX).

## Open questions / gaps
- No quantitative scintillation or TEC climatology for Singapore was extracted (ITU-R P.531 figures, regional literature); statements are qualitative.
- Layer height/density ranges are textbook generalities (Davies; Saunders) rather than extracted from P.1239.
- HF antenna/NVIS practice belongs to domain 08; licensing to 19.

## Sources
1. ITU-R Recommendation P.531-13 (09/2016), *Ionospheric propagation data and prediction methods required for the design of satellite services and systems*: §3.1 TEC (10¹⁶–10¹⁸ el/m²), §3.2 Faraday rotation eq. (2) and XPD eq. (3), §3.3 group delay eq. (4), §4 scintillation (S4, f^−1.5), Table 3 (maximum effects at 1 GHz). https://www.itu.int/rec/R-REC-P.531/en (standard)
2. IS-GPS-200 (GPS interface specification): L1/L2/L5 frequencies; single-frequency (Klobuchar) ionospheric model. https://www.gps.gov/technical/icwg/ (standard)
3. K. Davies, *Ionospheric Radio*, IEE Electromagnetic Waves Series 31, Peter Peregrinus 1990 — layers, critical frequencies, secant law, MUF, absorption. (textbook) *cited from standard knowledge*
4. S. R. Saunders, A. Aragón-Zavala, *Antennas and Propagation for Wireless Communication Systems*, 2nd ed., Wiley 2007, ch. 7 (ionospheric propagation) — and J. S. Seybold, *Introduction to RF Propagation*, Wiley 2005, ch. 9. (textbooks)
5. P. Misra, P. Enge, *Global Positioning System: Signals, Measurements, and Performance*, 2nd ed., Ganga-Jamuna 2006, ch. 5 (ionospheric delay 40.3 TEC/f², iono-free combination). (textbook)
6. ITU-R P.1239 (reference ionospheric characteristics) and P.533 (HF propagation prediction). https://www.itu.int/rec/R-REC-P.533 (standards — cited for scope)
7. `tools/verify/prop_ionosphere.py` (this KB).
