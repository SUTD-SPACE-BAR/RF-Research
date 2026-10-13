---
title: Solar activity and space weather — sunspot cycle, solar flux, K/A indices, flares, storms and what they do to HF, VHF and GNSS
domain: 09-propagation-link-budget
slug: solar-activity-and-space-weather
tags: [space-weather, sunspot-cycle, solar-cycle-25, solar-flux-index, F10.7, K-index, A-index, Kp, Bz, solar-flare, X-ray-class, sudden-ionospheric-disturbance, D-layer-absorption, radio-blackout, CME, coronal-hole, geomagnetic-storm, polar-cap-absorption, NOAA-scales, SWPC, equatorial-anomaly, plasma-bubbles, scintillation, GNSS-Singapore]
prerequisites: [ionospheric-hf-propagation.md, ../02-electromagnetics/wave-equation-plane-waves-polarization.md]
related: [hf-propagation-modes-and-prediction.md, ionospheric-hf-propagation.md, vhf-uhf-anomalous-propagation.md, ground-wave-and-lf-mf-propagation.md, ../21-gnss/gnss-receiver-architecture-acquisition-tracking.md, ../21-gnss/gnss-signals-and-codes.md, ../21-gnss/gnss-error-sources-dop.md, ../21-gnss/rtk-ppp-and-corrections.md, ../08-antennas/gnss-antennas.md, ../07-noise-linearity/thermal-noise-and-noise-temperature.md, ../19-regulations-safety/amateur-radio-licensing.md]
level: mixed
confidence: high
last_updated: 2026-10-03
---

# Solar activity and space weather — sunspot cycle, solar flux, K/A indices, flares, storms and what they do to HF, VHF and GNSS

## Questions this page answers
- What is the sunspot cycle, and where is Solar Cycle 25 in 2026?
- What is the solar flux index (SFI, F10.7), and how does it relate to the sunspot number and to usable HF frequencies?
- What do the K-index, A-index, Kp and Ap measure, and how do I read them?
- What is a solar flare, what do the A/B/C/M/X classes mean, and why does a flare black out HF for an hour?
- Why does a sudden ionospheric disturbance hurt 80 m more than 15 m?
- What is a coronal mass ejection (CME), how long does it take to reach Earth, and what is Bz?
- What do the NOAA R, S and G scales (e.g. "G5", "R3") mean?
- What is polar cap absorption, and why do auroral paths fade when the K-index is high?
- Why does HF noise suddenly rise across the whole band?
- Does space weather affect my 433/915 MHz rocket telemetry or my GNSS receiver in Singapore?
- What are the equatorial anomaly and plasma bubbles, and why does GNSS degrade after sunset near the equinoxes in Singapore?
- Where do I get live space-weather data (NOAA SWPC), and what should I check before a launch or an HF contact?

## TL;DR
- **The Sun drives the ionosphere.** Its extreme-ultraviolet (EUV) and X-ray output sets the electron density, and so the critical frequencies and the MUF ([ionosphere](ionospheric-hf-propagation.md)). The output follows the **≈11-year sunspot cycle**. Solar flares (photons, minutes to hours) and coronal mass ejections and coronal-hole streams (particles and magnetic field, hours to days) disturb it.
- **Solar Cycle 25 peaked at a 13-month smoothed sunspot number (SSN) of 160.9 in October 2024**. That is 1.38 × Cycle 24's 116.4 (SILSO V2.0). Smoothed F10.7 peaked at 194.5 sfu. By late 2026 the cycle is declining: monthly SSN was 60 in Sep 2026, daily F10.7 ≈ 92 sfu on 1 Oct 2026, and NOAA predicts F10.7 ≈ 126 → 70 sfu between late 2026 and 2030 (`tools/verify/prop2_space_weather.py` §1). **10/12/15 m (21–30 MHz) DX fades through 2027–2030. 20 m works by day at any point in the cycle.**
- **F10.7 (the "solar flux index", SFI)** is the Sun's 10.7 cm (2800 MHz) radio flux in solar flux units (1 sfu = 10⁻²² W m⁻² Hz⁻¹). It ranges from ≈ 65–70 sfu at solar minimum to ≈ 200–250 sfu near maximum. It tracks EUV, so higher SFI gives higher foF2 and MUF. The classic relation is Φ ≈ 63.7 + 0.728 R + 0.00089 R²; it matches the 2019–2026 data to ±15 sfu.
- **Flares → sudden ionospheric disturbance (SID, short-wave fade):** soft X-rays (0.1–0.8 nm) arrive **8.3 min** after the flare and ionise the D layer on the **sunlit side only**. Absorption grows roughly as 1/f^1.5–1/f², so **low HF is lost first**. NOAA's D-RAP rule gives the highest frequency with 1 dB vertical absorption as HAF = 10 log₁₀(flux) + 65 MHz: 15 MHz for M1 and 25 MHz for X1, falling as (cos χ)^0.75 to zero at the terminator. Classes: A, B, C, M, X = ≥10⁻⁸, 10⁻⁷, 10⁻⁶, 10⁻⁵, 10⁻⁴ W/m². **R1–R5 = M1, M5, X1, X10, X20.**
- **Geomagnetic indices:** **K** (0–9, quasi-logarithmic) measures the largest 3-hour disturbance of the horizontal field at one observatory: *short-term* activity. **A** (0–400) is the daily mean of the 8 three-hourly equivalent amplitudes: the *day's* activity. **Kp/Ap** are planetary versions. **K ≥ 5 is a storm. G1–G5 = Kp 5, 6, 7, 8, 9.** Rising K or A means a disturbed field. HF then degrades at high latitudes and through the auroral oval, and aurora can reflect VHF.
- **CMEs travel at < 250 to ~3000 km/s**, reaching Earth in **≈ 14 h (fastest) to several days**. A **southward IMF Bz** (north–south component of the interplanetary field, negative = south) couples the solar wind into the magnetosphere and drives storms. **Coronal holes** emit 500–800 km/s streams that recur every **~27 days** (synodic solar rotation 27.3 d).
- **Space weather does not touch a 433/915 MHz rocket-to-ground link.** The link is line-of-sight below the ionosphere and far above any absorbing frequency. It **does** affect **GNSS**: storms bring TEC gradients, ionospheric errors of tens of metres, RTK failures and scintillation. **Singapore** (dip −12.7°, dip latitude −6.4°; the dip equator is at 6.7° N at 104° E) sits between the dip equator and the southern **equatorial-anomaly crest**. Its **post-sunset equinox scintillation** is the dominant local effect. In April 2013 more than two GPS satellites had S4 > 0.2 for **15.7 % of 20–02 LT**, against < 0.1 % in June–July [11].

## Intuition (no math)
Think of the ionosphere as a mirror made by sunlight. The more UV the Sun emits, the denser and higher-reaching the mirror, and the higher the frequencies it can return to Earth. Sunspots mark magnetically active regions. These also brighten the corona in EUV and in the 10.7 cm radio band. That is why the sunspot number and the "solar flux" both predict how high on the HF spectrum the bands stay open. Over ~11 years the Sun swings between quiet (few spots, low MUF, 10 m dead) and active (many spots, 10 m and even 6 m open worldwide).

Two kinds of storm then break the mirror in different ways:
- **Light-speed storms (flares).** A flare is a flash of X-rays. It reaches Earth in 8 minutes and over-ionises the lowest, collision-heavy D layer on the day side. That layer does not reflect HF; it soaks it up. A wave spends more time in each electron collision the lower its frequency, so 160–40 m disappear first and 10 m last. The effect fades as the flare decays, typically in tens of minutes to an hour. Night-side paths are untouched.
- **Particle storms (CMEs, coronal-hole streams, solar protons).** Clouds of plasma and magnetic field arrive hours to days later. When their field points **south**, opposite to Earth's field at the dayside magnetopause, the two reconnect and energy floods into the magnetosphere. The result is a **geomagnetic storm**: the field at the ground wobbles (high K and A), aurora expands toward the equator, and the high-latitude ionosphere becomes absorbing and turbulent. After a day or so the F2 layer is often depleted world-wide (a "negative storm"), so MUFs fall. Very energetic solar protons, on the other hand, rain into the polar caps and black out polar HF for days (**polar cap absorption**).

Near the magnetic equator the Earth's field is horizontal, and this gives the tropics their own weather. During the day an eastward electric field lifts plasma upward. It then slides down the field lines and piles up in two **crests about 15° north and south of the magnetic equator** (the equatorial ionisation anomaly, EIA). After sunset the bottom of the F layer becomes unstable. **Bubbles** of depleted plasma rise through it like oil through water, and these break up GNSS signals (scintillation) from about 20:00 to 02:00 local time. The effect is worst near the equinoxes and in high-SSN years. Singapore sits between the magnetic equator and the southern crest, so this is its normal pattern.

## The math

### Level 1 — the indices and what each symbol means
- **Sunspot number** $R$ (dimensionless; SILSO version 2 scale). The smoothed value $R_{12}$ (13-month running mean) is used by ITU-R prediction methods (P.371, P.1239, P.533).
- **Solar radio flux** $\Phi$ (F10.7) in sfu (10⁻²² W m⁻² Hz⁻¹), measured daily at 2800 MHz (Penticton, Canada). Empirically $\Phi_{12} \approx 63.7 + 0.728R_{12} + 0.00089R_{12}^2$. Script check: 65 vs 69 sfu observed at the 2019 minimum, 204 vs 195 sfu at the 2024 maximum.
- **Flare class** from the peak GOES 0.1–0.8 nm flux $F$ (W/m²): A ≥ 10⁻⁸, B ≥ 10⁻⁷, C ≥ 10⁻⁶, M ≥ 10⁻⁵, X ≥ 10⁻⁴; the number multiplies (M5.2 = 5.2 × 10⁻⁵ W/m²). X is open-ended (X10 = 10⁻³) [2][3].
- **Highest affected frequency** (D-RAP; 1 dB absorption on a vertical up-and-down path at the sub-solar point) [3]:
$$\text{HAF}_\text{MHz} = 10\log_{10}F + 65,\qquad \text{HAF}(\chi) = \text{HAF}(0)\,(\cos\chi)^{0.75}$$
($\chi$ = solar zenith angle). Absorption at any other frequency: $A(f) = A(f_0)(f_0/f)^{1.5}$ dB.
- **K-index** (0–9) is a station-specific quasi-log code of the range of the horizontal field in a 3-hour UT block. Scales differ by observatory so each sees the same K statistics; at Boulder K = 9 means ≥ 500 nT. **Equivalent amplitude** $a_k$: K = 0…9 → 0, 3, 7, 15, 27, 48, 80, 140, 240, 400. **A-index** = mean of the day's eight $a_k$. **Kp** = standardised mean K of 13 observatories at 44–60° geomagnetic latitude; **Ap** = daily mean of the eight $a_{Kp}$ [4].
- **NOAA scales** [2]: G1–G5 for Kp = 5, 6, 7, 8 (incl. 9−) and 9. S1–S5 for ≥10 MeV proton flux of 10, 10², 10³, 10⁴ and 10⁵ pfu. R1–R5 for flares of M1, M5, X1, X10 and X20.
- **Bz**: the north–south component of the interplanetary magnetic field (nT, GSM frame). Bz < 0 (southward) is geo-effective.

### Level 2 — derivations

**Why absorption hits low frequencies (D layer).** An electron driven by $E_0e^{j\omega t}$ in a gas with collision frequency $\nu$ obeys $m\ddot x + m\nu\dot x = -eE$. The plasma permittivity becomes $\varepsilon_r = 1 - \omega_p^2/(\omega(\omega - j\nu))$. For $\omega \gg \omega_p$ the imaginary part gives an amplitude attenuation constant
$$\kappa = \frac{e^2}{2\varepsilon_0 m c}\,\frac{N\nu}{\omega^2 + \nu^2}\ \ \text{Np/m},\qquad \frac{e^2}{2\varepsilon_0mc} = 5.31\times10^{-6}\ \text{m}^2/\text{s}.$$
In the D region (60–90 km) $\nu \sim 10^6$ s⁻¹ is far below $\omega$ at HF, so $\kappa \propto N\nu/f^2$. Example (script §3): $N$ = 10⁹ m⁻³ over a 20 km slab gives 0.93 dB per vertical pass at 5 MHz, 0.23 dB at 10 MHz and 0.06 dB at 20 MHz. The absorption is **linear in $N$**: an X-class flare that multiplies D-region density tenfold turns 0.9 dB into ~9 dB per pass, and an oblique path crosses the layer twice per hop at sec $i$ ≈ 2–4. With the Earth's field the denominator becomes $(\omega \pm \omega_L)^2$ (o and x waves; $f_L = |f_H\sin I|$ ≈ 0.25–1.4 MHz), which is why ITU-R P.533 writes the absorption as ∝ $(1+0.0067R_{12})\sec i/(f+f_L)^2$ [7]. Operational models fit $f^{-1.5}$ instead (D-RAP, after Davies and Stonehocker). The two laws differ by $(f_2/f_1)^{0.5}$, a factor 1.4 per octave. That gap is real, not a typo: theory gives the $f^{-2}$ asymptote, and measured flare absorption falls off more slowly because the electron density and collision frequency vary through the D region. **Consequence:** an SID wipes out 3.5–7 MHz while 21–28 MHz may barely notice (X1, vertical: 19 dB at 3.5 MHz, 6.7 dB at 7 MHz, 0.8 dB at 28 MHz by the D-RAP law).

**HAF line.** The SWPC forecasters' table (M1 → 15, M5 → 20, X1 → 25, X5 → 30 MHz) is fitted by $10\log_{10}F + 65$. The fit reproduces M1 and X1 exactly but gives 22 and 32 MHz for M5 and X5, a 2 MHz residual (script §2). Use the formula as a ±2 MHz guide.

**From flux to foF2 and MUF.** Photo-ionisation production is $\propto$ EUV flux $\times \cos\chi$, so $N_mF2$ and $f_oF2 \propto \sqrt{N_m}$ grow with activity. ITU-R P.1239 models monthly median foF2 as **linear in $R_{12}$** between $R_{12}$ = 0 and 100, saturating above 160 [8]. In practice foF2 roughly doubles from solar minimum to a strong maximum at a given place and hour. With MUF ≈ 3 foF2 for a 3000 km hop, a daytime mid-latitude MUF of ~15–20 MHz at minimum becomes ~30–40 MHz at maximum. This is the physics behind the exam's "20 m at any point of the cycle" and "15/12/10 m least reliable at solar minimum". The E layer depends weakly on activity: P.1239 gives $(f_oE)^4 \propto 1 + 0.0094(\Phi - 66)$, so Singapore's noon foE moves only from 3.45 MHz (Φ = 70) to 4.17 MHz (Φ = 195) (script §7).

**Timing.** Photons cover 1 AU in $1.496\times10^{11}/c$ = 499 s = **8.3 min**. A CME at constant speed $v$ takes $t = 1\,\text{AU}/v$: 13.9 h at 3000 km/s, 41.6 h at 1000 km/s, 4.3 d at 400 km/s (script §5). The "15 hours to several days" rule follows directly; real CMEs decelerate or accelerate toward the ambient wind speed. The Sun's sidereal rotation is ≈ 25.4 d near the equator. Seen from the orbiting Earth it is $1/(1/25.38 - 1/365.26)$ = **27.3 d**, the period on which coronal-hole streams and long-lived active regions recur. That is the "26–28-day cycle" in HF conditions.

**K → A.** The A-index averages *amplitudes*, not K codes. A day of K = 2, 3, 3, 5, 6, 5, 4, 3 has $a_k$ = 7, 15, 15, 48, 80, 48, 27, 15, so A = 31.9 (script §4). One storm block dominates the day: A is a daily ("long-term") measure and K a 3-hour ("short-term") one.

### Level 3 — storms, polar caps and the equatorial ionosphere

**Solar-wind coupling.** The magnetosphere responds mainly to the dawn–dusk electric field $E_y = -v_xB_z$ of the solar wind ($v$ ~ 400–800 km/s; a southward Bz of −10 to −50 nT in a CME's magnetic cloud). This is why forecasters watch DSCOVR at L1, which gives 15–60 minutes' warning of arrival [5]. A storm has an initial phase (sudden commencement as the shock compresses the field), a main phase (ring-current build-up; Dst falls by 100 to 400+ nT) and recovery. In the **May 2024 "Gannon" storm**, the first G5 since 2003, Dst reached −412 nT. Ionospheric gradients produced GNSS errors of up to 60 m, and US farmers using RTK auto-steer lost an estimated US$0.5 billion [12].

**Geomagnetic coordinates matter more than geographic ones.**
- **Auroral and polar effects** organise by geomagnetic (dipole) latitude. The IGRF-14 dipole pole is at 80.9° N in 2026. Singapore's dipole latitude is −7.8°: aurora never reaches it.
- **Equatorial effects** organise by **dip latitude** $\mu$ ($\tan\mu = \tan I/2$, with $I$ the dip angle). At Asian longitudes the dip equator lies 6–7° north of the geographic equator. Singapore at 1.35° N is therefore magnetically in the southern hemisphere, with dip latitude −6.4°.
- **ITU-R HF methods** use the **modified dip** $X = \arctan(I/\sqrt{\cos\lambda})$, evaluated with a 1960 field model at 300 km (P.1239). For Singapore it is −17.2° (script).

**Ionospheric storm effects on HF.** In the auroral oval, particle precipitation creates **auroral absorption** (E/D-region ionisation). Paths through the oval fade when K is high, and the oval expands equatorward with Kp: aurora to ~55° geomagnetic latitude at G2, ~40° at G5 [2]. In the F region, storm-time heating changes the neutral composition (lower O/N₂), which depletes foF2 for a day or more (negative storm). Sometimes there is an early **positive storm** at low and mid latitudes. The usual operational result is MUFs 20–30 % below normal and noisy, fluttery high-latitude paths. Aurora itself is a VHF reflector, with characteristic Doppler-spread "raspy" signals best copied on CW ([anomalous propagation](vhf-uhf-anomalous-propagation.md)).

**Polar cap absorption (PCA).** Solar energetic protons (1–200 MeV) reach the atmosphere only where field lines open to space, poleward of ~60° geomagnetic latitude. There they ionise the D region down to ~50 km for days. D-RAP uses the Sauer & Wilkinson relations at 30 MHz for vertical paths: $A_\text{day} = 0.115\sqrt{J(>5.2\,\text{MeV})}$ dB and $A_\text{night} = 0.020\sqrt{J(>2.2\,\text{MeV})}$ dB [3]. At 10⁴ pfu, polar daytime HF below ~33 MHz suffers more than 10 dB (script §6). Trans-polar HF routes (e.g. Asia–North America flights) shift to satellite links; Singapore is unaffected.

**HF noise bursts.** Flares and CME-driven shocks emit **solar radio bursts** (types II, III, IV) whose broadband noise covers HF–VHF. A sudden rise in background noise across a large part of HF is therefore a flare or CME signature. This is the opposite of an SID: during an SID the band goes *quiet* because absorption removes both signals and distant atmospheric noise.

**304 Å.** The He II 30.4 nm EUV line is a major ionising wavelength for the F region and is monitored by spacecraft (e.g. SOHO, SDO). It correlates with F10.7, which is a ground-measurable proxy for the same chromospheric/coronal emission (stated from standard heliophysics; not re-derived here).

**The equatorial ionosphere and GNSS.** At the dip equator the daytime eastward electric field and the horizontal **B** give an upward $\mathbf E\times\mathbf B$ drift. This **fountain effect** builds EIA crests at ~±15° dip latitude with TEC up to ~100–200 TECU in high-SSN years (P.531 bounds vertical TEC at 10¹⁶–10¹⁸ el/m², i.e. 1–100 TECU, typically; SWPC quotes "a few to several hundred TECU") [6]. At L1, 1 TECU = 0.162 m, so a 30°-elevation path through a 150 TECU crest delays 43 m (script §8). Single-frequency broadcast models (Klobuchar) leave metres of residual there. After sunset the pre-reversal enhancement lifts the F layer, and a Rayleigh–Taylor instability grows. Field-aligned **plasma bubbles** (depletions) rise through the layer and break into irregularities of tens of metres to km. These scatter L-band (amplitude S4 and phase σφ scintillation), causing cycle slips, loss of lock and RTK float or no-fix periods. The occurrence peaks at the **equinoxes**, at **20–02 LT** and at **high SSN**, the same physics that makes [equatorial evening scatter and eTEP](vhf-uhf-anomalous-propagation.md). ITU-R P.533 models HF equatorial-scatter occurrence as 1 for |dip| ≤ 15° at 20–03 LT, tapering to 0 at 25°, scaled by $\min(0.1 + 0.008R_{12}, 1)$ and a season factor. For Singapore (|dip| = 12.7°) the model gives probability ≈ 0.8 × season in late-evening hours at $R_{12}$ = 90 [7]. In weak scattering S4 scales as $f^{-1.5}$: L5 and L2 scintillate ×1.5 more than L1, and a 433 MHz satellite downlink ×7.

**Singapore numbers.** IGRF-14 (own synthesis, validated against published magnetic coordinates of Kototabang, Chumphon, Trivandrum and Jicamarca; `prop2_igrf.py`) puts Singapore at **dip −12.7°, dip latitude −6.4°** in 2026. The dip equator crosses 104° E at **6.7° N** (southern Thailand/Gulf of Thailand). The southern EIA crest (~−15° dip latitude) therefore lies near 8–10° S, over Java, south of Singapore. NTU measurements in 2013, near the Cycle 24 maximum, found more than two GPS satellites with S4 > 0.2 for 7.9 % of the night (18–06 LT) in April and 15.7 % of 20–02 LT, against 0.01–0.07 % in June–July [11]. Cycle 25 is stronger, so 2024–2026 equinoxes were at least as active.

## Design equations & rules of thumb

| Quantity / rule | Formula or value | Notes |
|---|---|---|
| Solar flux ↔ sunspot number | $\Phi \approx 63.7 + 0.728R + 0.00089R^2$ sfu | ±15 sfu vs 2019–2026 smoothed data |
| Flare class | A/B/C/M/X = 10⁻⁸ … 10⁻⁴ W/m² (0.1–0.8 nm) | X10 = 10⁻³; R1/R2/R3/R4/R5 = M1/M5/X1/X10/X20 |
| Highest affected frequency | $10\log_{10}F + 65$ MHz × $(\cos\chi)^{0.75}$ | 1 dB vertical; ±2 MHz fit residual |
| Absorption vs frequency | $A \propto f^{-1.5}$ (empirical) … $(f+f_L)^{-2}$ (theory, P.533) | low HF lost first |
| D-layer absorption constant | $\kappa = 5.31\times10^{-6}N\nu/(\omega^2+\nu^2)$ Np/m | linear in $N$ |
| Flare photons | 8.3 min | sunlit hemisphere only |
| CME transit | 1 AU/$v$: 14 h (3000 km/s) … 4 d (400 km/s) | DSCOVR gives 15–60 min warning |
| Recurrence | 27.3 d synodic rotation | coronal-hole storms repeat |
| K → $a_k$ | 0,3,7,15,27,48,80,140,240,400 | A = mean of 8 $a_k$ |
| Storm thresholds | K ≥ 5; G1..G5 = Kp 5..9 | G5 ≈ 4 per cycle |
| PCA (30 MHz, vertical) | day 0.115√J, night 0.020√J dB | polar caps only |
| GNSS L1 delay | 0.162 m/TECU (vertical) × obliquity | EIA crest 100–200 TECU at solar max |
| Scintillation season (Singapore) | equinox, 20–02 LT, high SSN | S4 ∝ f^−1.5 (weak) |

**What each phenomenon does, and to what** (a summary of [2][3][5] and the physics above; "—" means no practical effect)

| Phenomenon | Arrives after | Lasts | Low HF (2–10 MHz) | High HF (14–30 MHz) | VHF (50–150 MHz) | GNSS (L-band) | 433/915 MHz ground link |
|---|---|---|---|---|---|---|---|
| Solar flare / SID | 8.3 min | minutes–2 h | blackout on day side | weaker, shorter fade | — | small TEC jump; R4–R5: errors on day side | — |
| Solar radio burst | 8.3 min | minutes | noise rise | noise rise | noise rise (can hit GNSS/radar receivers) | possible C/N0 loss if the Sun is in view, rare | — |
| CME-driven storm (G1–G5) | 14 h–4 d | 1–3 d | high-latitude absorption; MUF falls | MUF falls 20–30 %; polar paths fade | aurora reflection at high latitude | TEC gradients, errors to tens of m, scintillation, RTK failures | — |
| Coronal-hole stream | 2–4 d after the hole crosses the central meridian | days; recurs every 27 d | mild storm effects | mild MUF depression | occasional aurora | mild | — |
| Solar proton event (S1–S5) / PCA | 15 min–hours | 1–5 d | polar-cap blackout | polar-cap blackout | — | polar SBAS/position errors | — |
| Equatorial plasma bubbles | post-sunset (20–02 LT) | hours | spread-F, flutter, equatorial scatter | flutter, eTEP at VHF | eTEP, scintillation | **scintillation, cycle slips (Singapore)** | — |

## Worked examples
**1 — An X1.5 flare at 03:00 UTC (11:00 SGT).** The sub-solar point is near Singapore (October, declination −8°), so $\chi \approx 10°$. HAF = 10 log(1.5 × 10⁻⁴) + 65 = 26.8 MHz, × cos^0.75 10° = 26.5 MHz. A 7 MHz path from Singapore to Perth has two D-layer crossings at sec $i$ ≈ 2.5 each. It sees about 2.5 × (26.5/7)^1.5 ≈ 18 dB extra loss at the Singapore end alone, so the path is gone for tens of minutes. A 21 MHz path loses ≈ 2.5 × (26.5/21)^1.5 ≈ 3.5 dB and survives. Night-side paths (e.g. Europe–Americas at 03 UTC) are unaffected. A 433 MHz rocket downlink is unaffected: line-of-sight, below the D layer, and ≫ HAF. GNSS sees a small, fast TEC increase on the day side, but the effect on positioning is minor (R3 navigation impact: "low-frequency navigation degraded for about an hour" [2]).

**2 — A halo CME launched toward Earth at 1500 km/s at 12:00 UTC on launch day − 2.** Constant-speed transit is 1 AU/1500 km/s = 27.7 h, so arrival is around 16:00 UTC on day − 1. A fast CME usually decelerates, so expect 1–2 days. If the magnetic cloud carries Bz ≈ −20 nT for several hours, a G3–G4 storm (Kp 7–8) is plausible. For a launch at 09:00 SGT on day 0 the storm's main phase may coincide. **Consequences:** the 433/915 MHz telemetry is unaffected. GNSS: the rocket's L1-only MAX-M10S may show extra metres of error and slower fixes. The ground ZED-F9P RTK base–rover over a few km keeps most of the common-mode error out, but storm-time gradients can still force float solutions. Plan a pre-launch fix check, and log raw data (RXM-RAWX) for post-processing. HF backup links to the range will be degraded, worst at night.

**3 — Reading a solar-cycle forecast for an HF field station.** NOAA's September 2026 prediction gives F10.7 ≈ 126 sfu for Oct 2026, ≈ 104 by Oct 2027, ≈ 85 by Oct 2028 and ≈ 71 by Oct 2030 [1]. Converting with the P.1239 relation gives effective R12 = 78, 52, 28 and 10. The ITU-R P.1239 maps with the P.533 MUF method (`prop2_ccir.py`) give, for Singapore → Perth (October):

| Year | Noon SGT path MUF | 16 SGT path MUF | 04 SGT path MUF | Singapore noon foF2 |
|---|---|---|---|---|
| 2026 | 26.8 MHz | 29.8 | 12.6 | 10.6 |
| 2027 | 25.0 | 28.2 | 10.9 | 9.8 |
| 2028 | 23.3 | 26.7 | 9.4 | 9.1 |
| 2030 | 21.8 | 25.3 | 8.2 | 8.6 |

The decline is gentle on this low-latitude path, where the equatorial anomaly keeps daytime MUFs above 20 MHz even at solar minimum. The night-time MUF, however, falls below 10 MHz, which closes 30 m to Perth before dawn. On mid- and high-latitude paths the solar-cycle swing is much larger. Check any specific path with VOACAP or ITURHFProp ([HF modes and prediction](hf-propagation-modes-and-prediction.md)).

**4 — K-index and A-index from a daily report.** Boulder reports K = 2, 3, 3, 5, 6, 5, 4, 3. A = (7 + 15 + 15 + 48 + 80 + 48 + 27 + 15)/8 = 31.9 (the units are 2 nT at Boulder). The day contained a G2 interval (K = 6). Expect high-latitude HF degradation, aurora visible at ~55° geomagnetic latitude, and an elevated chance of post-sunset scintillation near the equator if the storm timing favours it.

**5 — Equinox GNSS testing in Singapore.** You plan RTK accuracy tests of the ground station in late March 2026 (smoothed SSN ≈ 95). Schedule them before 19:00 SGT. From the 2013 statistics at a similar activity level, up to ~16 % of 20–02 LT has several satellites in scintillation. If evening data are unavoidable, log S4/C/N0 per satellite and allow time for re-convergence after cycle slips.

## Practical notes
- **Where to look (NOAA SWPC, swpc.noaa.gov):**
  - The **Space Weather Scales** banner gives the current R, S and G levels.
  - The **3-Day Forecast** and **Forecast Discussion** give flare probabilities and Kp predictions.
  - **27-Day Outlook** covers F10.7 and Ap.
  - **GOES X-ray flux** shows flares in real time.
  - **D-RAP** maps where HF is absorbed right now.
  - **Planetary K-index** is updated every 3 h.
  - **Solar wind** (DSCOVR/ACE) shows speed, density and Bz.
  - **Aurora 30-min forecast**.
  - **GloTEC / US-TEC** shows TEC maps.
  - Machine-readable JSON lives under `services.swpc.noaa.gov`: e.g. `/json/f107_cm_flux.json`, `/products/noaa-planetary-k-index.json`, `/json/solar-cycle/observed-solar-cycle-indices.json` and `/json/solar-cycle/predicted-solar-cycle.json`, used by `prop2_space_weather.py`.
**SWPC products and what to use them for**

| Product | Shows | Use it to |
|---|---|---|
| NOAA Scales banner (R/S/G now and 24-h max) | current severity | one-glance "is anything happening" |
| GOES X-ray flux (1-min) | 0.1–0.8 nm flux, flare class | explain a sudden daytime HF fade; estimate HAF |
| D-RAP map | where HF has more than 1 dB absorption, and the recovery clock | decide which paths are dead and for how long |
| Planetary K-index (3-h) | Kp history and estimates | storm level; high-latitude HF quality |
| Solar wind (DSCOVR/ACE) | speed, density, Bt, **Bz** | 15–60 min warning of CME arrival; Bz south means storm likely |
| 3-day forecast / discussion | flare probabilities, Kp forecast | launch-day GNSS risk; HF scheduling |
| 27-day outlook | F10.7 and Ap by day | plan around recurrent coronal-hole storms |
| Solar cycle progression | SSN and F10.7 observed vs predicted | multi-year HF band planning |
| GloTEC / US-TEC | TEC maps | GNSS error context (global vs regional) |

- **Regional sources:** Australia's Bureau of Meteorology Space Weather Services (sws.bom.gov.au) runs ionosondes in the Australian–SE Asian sector (e.g. Darwin, Learmonth, Cocos Island). Its HF prediction products and TEP notes are directly relevant to Singapore.
- **Sunspot numbers:** SILSO (Royal Observatory of Belgium) is the reference, and its version 2 scale is ~1.4–1.7× the old version 1. ITU-R P.1239 coefficients assume the version-1 convention (observatory factor 0.6). Check which convention a prediction program expects before typing in $R_{12}$, because the factor changes MUFs.
- **Rocket operations checklist:**
  1. Note the G level and 3-day Kp forecast.
  2. Note whether launch is at dusk or after near an equinox.
  3. Keep GNSS logging raw.
  4. Keep the LoRa link budget unchanged: space weather adds no loss at 433/915 MHz for a sub-ionospheric path.
- **HF operators:**
  - Low bands die during a daytime SID, so move up in frequency or wait 30–60 min.
  - During a geomagnetic storm, move *down* in frequency because foF2 is depressed, and avoid polar and auroral paths.
  - Expect conditions to recur ~27 days later when a coronal hole caused the storm.

### Quick answers to common exam-style questions
The questions are paraphrased from the ham-radio question pools. Each answer comes with the reason behind it.
- *Higher sunspot number?* Usually better propagation at higher HF frequencies, because more EUV raises foF2 and the MUF.
- *Sudden ionospheric disturbance?* It disrupts daytime lower-frequency signals more than higher ones (absorption ∝ $f^{-1.5}$…$f^{-2}$).
- *How long until a flare's UV/X-rays affect propagation?* About 8 minutes (light travel time, 8.3 min).
- *Least reliable long-distance bands at solar minimum?* 15, 12 and 10 m: the MUF rarely reaches 21–30 MHz.
- *What is the solar flux index?* The 10.7 cm (2800 MHz) solar radio flux.
- *Geomagnetic storm?* A temporary disturbance of the Earth's magnetic field. It degrades high-latitude HF and can create aurora that reflects VHF.
- *20 m daytime worldwide?* Yes, at any point in the cycle: even at solar minimum the daytime MUF over 3000-km hops exceeds 14 MHz.
- *26–28-day variation?* Solar rotation as seen from Earth (27.3 d).
- *CME arrival?* From about 15 hours to several days.
- *K-index vs A-index?* K is short-term (3-hour) stability of the geomagnetic field; A is the daily (longer-term) stability. Rising K or A means increasing disturbance.
- *Coronal holes?* Their high-speed solar-wind particles disturb HF communication.
- *Short-term radio blackout cause?* A solar flare.
- *Path most absorbed when K or A is elevated?* One through the auroral oval.
- *Bz?* The north–south component of the interplanetary magnetic field. Southward Bz increases the chance of disturbed conditions.
- *Strongest flare class?* X.
- *Extreme geomagnetic storm?* G5.
- *The 304 Å parameter?* UV (EUV) emission at 30.4 nm, correlated with the solar flux index.
- *Sudden rise in HF background noise over a wide band?* A flare or CME impact (solar radio burst).
- *Most likely cause of auroral propagation?* Severe geomagnetic storms.

## Common mistakes & misconceptions
- **"A solar flare and a geomagnetic storm are the same event."** A flare is a light-speed photon event that affects the sunlit D layer for minutes to hours. A storm comes from particles and fields 1–4 days later, affecting the whole magnetosphere and ionosphere for days. A big flare often, but not always, comes with a CME.
- **"High SFI is always good."** High SFI raises foF2 and the MUF, but active Suns also flare (SIDs) and launch CMEs (storms). Good HF needs high SFI with low K/A.
- **"A low K-index means bad conditions."** Low K means a quiet, stable field, which is good for HF, especially at high latitude. Rising K or A means increasing disturbance.
- **"An SID affects all bands equally."** Absorption scales as ~$f^{-1.5}$ to $f^{-2}$, so lower frequencies suffer most. Night-side paths are not affected at all.
- **"Space weather will knock out my LoRa telemetry."** Not for a rocket-to-ground or ground-to-ground UHF link. Only Earth–space links (satellites, GNSS) cross the ionosphere, and PCA or flare absorption is negligible above ~50 MHz.
- **"Dual-frequency GNSS is immune to storms."** It removes the first-order delay, but not scintillation, loss of lock or the steep gradients that break RTK and SBAS assumptions ([ionosphere](ionospheric-hf-propagation.md)).
- **Mixing sunspot-number versions.** SILSO V2 (since 2015) is ~1.4–1.7× larger than V1. ITU-R maps use V1-era coefficients, so confusing the two biases MUF predictions.
- **"Bz positive is the dangerous direction."** It is **southward** (negative) Bz that reconnects with Earth's field and drives storms.

## How to simulate / verify
- `tools/verify/prop2_space_weather.py` (output in `prop2_space_weather_output.txt`; ALL PASS) covers:
  - embedded SILSO/SWPC cycle data and the Φ–R relation;
  - flare classes and the HAF formula, with its residual vs the SWPC table;
  - non-deviative absorption from first principles;
  - K → $a_k$ → A;
  - photon, CME and rotation timing;
  - PCA;
  - P.1239 foE at Singapore;
  - GNSS TEC delays;
  - P.533 equatorial-scatter factors;
  - S4 scaling.
- `tools/verify/prop2_igrf.py` implements IGRF-14 spherical-harmonic synthesis from the official coefficients (`tools/verify/data/igrf14coeffs.txt`). It computes dip, dip latitude, modified dip, gyrofrequency and the dip-equator location, and is validated against Boulder and four equatorial stations.
- Live checks: compare D-RAP maps with HF beacon/WSPR reception during a flare ([HF modes and prediction](hf-propagation-modes-and-prediction.md)). Log GNSS C/N0 and S4 proxies (u-blox `NAV-SAT` C/N0, `RXM-RAWX`) and correlate them with Kp and local time.

## Open questions / gaps
- No Singapore TEC climatology (monthly median vertical TEC by hour) was extracted. The EIA TEC numbers here are generic low-latitude ranges.
- The f^-1.5 (empirical) vs f^-2 (theory/P.533) absorption laws are both used operationally. No first-hand measurement reconciles them for the Singapore region.
- The 304 Å statement relies on standard heliophysics knowledge, without a primary instrument paper re-read.
- Cycle 25 sunspot values after March 2026 are provisional (SILSO smoothing lags by 6 months).

## Sources
1. SILSO, Royal Observatory of Belgium, *Sunspot Number version 2.0* — monthly mean and 13-month smoothed total sunspot number files (SN_m_tot_V2.0, SN_ms_tot_V2.0), fetched 2026-10-02; and NOAA SWPC JSON products `observed-solar-cycle-indices`, `predicted-solar-cycle`, `f107_cm_flux` (fetched 2026-10-02). https://www.sidc.be/SILSO/ ; https://services.swpc.noaa.gov/ (data) — cycle extrema, 2026 status, F10.7.
2. NOAA SWPC, *NOAA Space Weather Scales* (R, S, G definitions, thresholds, effects, frequency per cycle). https://www.swpc.noaa.gov/noaa-scales-explanation (official documentation)
3. NOAA SWPC, *Global D-Region Absorption Prediction documentation* — flare classes, HAF = 10 log F + 65 MHz, (cos χ)^0.75, A ∝ f^-1.5 (citing Davies 1990; Stonehocker 1970; Sauer & Wilkinson 2008), PCA formulas. https://www.swpc.noaa.gov/content/global-d-region-absorption-prediction-documentation (official documentation)
4. NOAA SWPC, *Planetary K-index* and *Station K and A Indices* pages — K, a_k table, A, Kp (13 observatories, 44–60°), Ap; Bartels 1938. https://www.swpc.noaa.gov/products/planetary-k-index (official documentation)
5. NOAA SWPC phenomena pages: *Coronal Mass Ejections* (250–3000 km/s, fastest 15–18 h, DSCOVR 15–60 min warning), *Coronal Holes* (high-speed streams, CIR, 27-day recurrence, G1–G2), *Solar Wind* (400 vs 500–800 km/s), *Solar Flares (Radio Blackouts)*, *Ionospheric Scintillation*, *Total Electron Content*. https://www.swpc.noaa.gov/phenomena (official documentation)
6. ITU-R Recommendation P.531-13 (09/2016), ionospheric effects on Earth–space paths (TEC range, scintillation S4 ∝ f^-1.5). https://www.itu.int/rec/R-REC-P.531/en (standard)
7. ITU-R Recommendation P.533-14 (08/2019), *Method for the prediction of the performance of HF circuits* — absorption eq. (20) ∝ (1 + 0.0067 R12) sec i/(f + fL)², Attachment 1 equatorial-scatter model. https://www.itu.int/rec/R-REC-P.533/en (standard)
8. ITU-R Recommendation P.1239-4 (08/2023), *ITU-R reference ionospheric characteristics* — foE formula (eqs 12–18), foF2/M(3000)F2 linear in R12 to 160, modified dip. https://www.itu.int/rec/R-REC-P.1239/en (standard)
9. K. Davies, *Ionospheric Radio*, IEE Electromagnetic Waves Series 31, Peter Peregrinus 1990 — absorption theory, SID, PCA, storms. (textbook) *cited via [3] and standard knowledge*
10. L. F. McNamara, *Radio Amateur's Guide to the Ionosphere*, Krieger 1994 — SID, storms, K/A practice for operators. (textbook) *cited from standard knowledge, not re-read*
11. D. S. Murti, *GNSS ionospheric scintillation studies in Singapore*, M.Eng. thesis, Nanyang Technological University, 2015 — PolaRxS measurements at NTU, 2012–2014: equinox maxima, 20–02 LT, occurrence statistics. https://dr.ntu.edu.sg/handle/10356/65415 (thesis)
12. "The May 2024 geomagnetic storm: UK experience and perspective," *Royal Society Open Science* 13(4), 251943 (2026), doi:10.1098/rsos.251943 — Dst −412 nT, GNSS errors to 60 m; and Wikipedia *May 2024 solar storms* for the precision-agriculture loss estimate. (peer-reviewed; encyclopedia — secondary, *via search summary*)
13. Australian Bureau of Meteorology Space Weather Services, *Transequatorial Radio Propagation* (educational note) — EIA crests at 10–20° magnetic latitude; dip equator north of the geographic equator at Asian longitudes. https://www.sws.bom.gov.au/Educational/5/2/3 (government educational note)
14. IAGA, *International Geomagnetic Reference Field, 14th generation* coefficients (igrf14coeffs.txt), NOAA NGDC. https://www.ngdc.noaa.gov/IAGA/vmod/coeffs/ (data/standard model) — Singapore dip and dip equator via `tools/verify/prop2_igrf.py`.
15. `tools/verify/prop2_space_weather.py`, `tools/verify/prop2_igrf.py` (this KB).
