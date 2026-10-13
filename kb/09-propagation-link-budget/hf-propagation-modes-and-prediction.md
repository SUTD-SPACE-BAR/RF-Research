---
title: HF propagation modes and prediction — MUF/LUF/FOT, skip, multihop, grey line, long path, NVIS, scatter and how to predict a path (VOACAP, ITU-R P.533, WSPR/RBN/PSKReporter)
domain: 09-propagation-link-budget
slug: hf-propagation-modes-and-prediction
tags: [HF, skywave, MUF, LUF, FOT, critical-frequency, critical-angle, secant-law, skip-zone, multihop, chordal-hop, grey-line, long-path, NVIS, ordinary-wave, extraordinary-wave, HF-scatter, backscatter, atmospheric-noise, ITU-R-P.533, ITU-R-P.1239, ITU-R-P.372, VOACAP, ITURHFProp, WSPR, reverse-beacon-network, PSKReporter, Singapore-Australia]
prerequisites: [ionospheric-hf-propagation.md, solar-activity-and-space-weather.md, friis-free-space-path-loss.md]
related: [link-budget-methodology.md, ground-wave-and-lf-mf-propagation.md, vhf-uhf-anomalous-propagation.md, multipath-fading-doppler.md, ../07-noise-linearity/thermal-noise-and-noise-temperature.md, ../08-antennas/wire-antennas-hf-random-wire-fan-dipole.md, ../08-antennas/dipoles-and-monopoles.md, ../19-regulations-safety/amateur-radio-licensing.md]
level: mixed
confidence: high
last_updated: 2026-10-03
---

# HF propagation modes and prediction — MUF/LUF/FOT, skip, multihop, grey line, long path, NVIS, scatter and how to predict a path

## Questions this page answers
- What are the MUF, the LUF and the FOT, and why should I operate just below the MUF?
- What happens to a signal above the MUF, between the LUF and MUF, and below the LUF? What if the LUF is above the MUF?
- What is the critical angle, and why does a lower take-off angle give a longer hop?
- How far does one hop reach via the E layer and via the F2 layer?
- What is the skip zone, and how can I hear stations inside it (scatter)?
- What are chordal hop, grey-line, long-path and NVIS propagation?
- What are the ordinary and extraordinary waves, and why can either a horizontal or a vertical antenna receive skywave?
- Why is 160 m DX only possible when the whole path is dark, and why is low HF so noisy in summer?
- How do VOACAP and ITU-R P.533 predict a path? What do WSPR, the Reverse Beacon Network and PSKReporter tell me?
- Which HF frequencies would link Singapore to Perth or Sydney in October 2026, at noon and at night?
- How do I do an HF link budget (field strength, absorption, noise, SNR)?

## TL;DR
- **MUF** (maximum usable frequency) is the highest frequency the ionosphere returns over a *given path*: MUF ≈ foF2 × (an obliquity factor of 3–4 for 3000–4000 km hops). **LUF** (lowest usable frequency) is the lowest frequency that still gives the required SNR. D-layer absorption (∝ 1/(f + f_L)²) and noise set it. **FOT** (optimum working, or "frequency of optimum traffic") ≈ 0.85 × MUF: it has the least absorption while staying below the day-to-day MUF spread.
- **Above the MUF** the wave escapes to space; **between LUF and MUF** it is refracted back; **below the LUF** it is absorbed. **LUF > MUF ⇒ no skywave on that path at that hour.**
- **One hop:** E layer (≈ 110 km) ≤ **≈ 2350 km** at 0° take-off (≈ 1800 km at 3°; the exam figure is "1200 mi"). F2 (≈ 300–350 km) ≤ **≈ 3800–4100 km** ("2500 mi"). The F2 hop is longest because the layer is highest. **Lower take-off angles give longer hops.** The **critical angle** is the highest take-off angle that still returns for a given frequency and foF2.
- **Prediction = monthly-median ionosphere maps + ray geometry + absorption + noise.** ITU-R **P.533** (reference program ITURHFProp), VOACAP (IONCAP family) and others use the **P.1239 (CCIR 1966) foF2/M(3000)F2 maps**. This KB re-implements those maps and the P.533 basic-MUF equations (`tools/verify/prop2_ccir.py`). It reproduces the ITU program's control-point foF2 to ≤ 0.07 MHz, and its Kranji (Singapore) → Beijing basic MUF to 0.8 %.
- **Singapore → Perth (3914 km, 2F), October, R12 ≈ 80:**
  - Path MUF: **≈ 27 MHz at noon SGT, ≈ 30 MHz at 16 SGT, ≈ 13 MHz at 04 SGT**.
  - Noon absorption: 63 dB at 7 MHz, 16 dB at 14 MHz, 7 dB at 21 MHz.
  - Daytime choice: 18–24 MHz, with 14 MHz in the evening and 10–7 MHz before dawn.
  - At solar minimum (R12 = 10) the noon MUF is still ≈ 22 MHz, because the equatorial anomaly is a strong ionosphere (`prop2_hf_paths.py`).
- **Real-time truth beats prediction:** WSPR (decodes to −28 dB SNR in 2.5 kHz), the Reverse Beacon Network (CW/RTTY/FT8 skimmers) and PSKReporter (digital-mode reports). All three report **who heard your digital or CW signal, where, and at what SNR**.
- **For Marcus:** HF is not the rocket-telemetry band. It is the band for range-to-base comms over hundreds to thousands of km without infrastructure, by NVIS or skywave, and it needs an amateur licence ([licensing](../19-regulations-safety/amateur-radio-licensing.md)).

## Intuition (no math)
The ionosphere acts like a curved, leaky mirror whose "reflectivity" depends on frequency and angle. A wave arriving steeply needs a dense layer to turn it round. A wave arriving at a glancing angle needs much less, so the same layer reflects far higher frequencies on long, low-angle paths than straight up. For any path there is therefore a top frequency (MUF) above which the mirror is transparent.

On the way up and down, the wave crosses the D layer. Low frequencies make the electrons there oscillate with large excursions, and collisions turn that energy into heat. The lower the frequency, the more it is absorbed, and only by day (the D layer vanishes at night). The usable window is therefore squeezed from below by absorption (LUF) and from above by penetration (MUF). Pick the highest frequency comfortably below the MUF: that is the FOT.

The window moves with the Sun:
- **Daytime:** a dense F2 gives a high MUF, and a strong D layer gives a high LUF, so high bands (14–28 MHz) work.
- **Night:** the F2 layer decays, so the MUF falls, and the D layer vanishes, so the LUF falls too. Low bands (1.8–7 MHz) work, and the high bands close.
- **Dawn and dusk (grey line):** the D layer is weak or absent while the F2 layer is still dense, so low bands reach far along the terminator.

Paths can be one hop or several. A hop that skips over the ground without reflecting off it (**chordal hop**) avoids ground-reflection and D-layer losses and arrives stronger. A wave may also go the "wrong way round" the Earth (**long path**). If both paths are open, you hear an echo about 0.1 s later.

## The math

### Level 1 — definitions and formulas with units
- **Critical frequency** foF2 (MHz) is the highest frequency reflected at vertical incidence: $f_oF2 = 8.98\times10^{-6}\sqrt{N_mF2}$ MHz for $N_m$ in m⁻³ ([ionosphere](ionospheric-hf-propagation.md)).
- **Secant law** (flat layer): a wave incident at angle $i$ from vertical is returned if $f \le f_c\sec i$. The **MUF** of a hop is $f_c\sec i$ at the incidence angle that hop geometry forces.
- **Curved-Earth hop geometry** (spherical mirror at height $h$, Earth radius $R_0$ = 6371 km, take-off elevation $\Delta$, hop length $d$; P.533 eq. 13):
$$\Delta = \arctan\!\left(\cot\frac{d}{2R_0} - \frac{R_0}{R_0+h}\csc\frac{d}{2R_0}\right),\qquad \sin i = \frac{R_0\cos\Delta}{R_0+h}.$$
- **ITU practical MUF** for an F2 hop of length $d$ (P.533-14 eq. 3–6, the form used by all ITU-family programs):
$$\text{MUF}(d) = \Big[1 + \frac{C_d}{C_{3000}}(B-1)\Big]f_oF2 + \frac{f_H}{2}\Big(1-\frac{d}{d_\text{max}}\Big)$$
  - $B$ is a function of the propagation factor **M(3000)F2** (= MUF(3000 km)/foF2, typically 2.5–3.5) and of $x$ = foF2/foE.
  - $C_d$ is a 6th-order polynomial in $Z = 1 - 2d/d_\text{max}$; $C_d(d_\text{max}) = 1$.
  - $d_\text{max}$ (≤ 4000 km) is the maximum hop length.
  - $f_H$ is the electron gyrofrequency at 300 km (≈ 1.0 MHz over Singapore).
  - The mirror height is $h_r = 1490/\text{M(3000)F2} - 176$ km (≤ 500 km).
- **E-layer MUF:** $\text{MUF}_E = f_oE\sec i_{110}$, mirror at 110 km. Usable up to 4000 km (two E hops).
- **FOT** ≈ 0.85 MUF. The operational MUF exceeded on 90 % of days is the P.533 "optimum working frequency".
- **Absorption** per n-hop F2 mode (P.533 eq. 20 as coded in the ITU reference program) [1][13]:
$$L_i = \frac{n\,(1 + 0.0067R_{12})\,A_{T,\text{noon}}\,\phi_n\,F(\chi)/F(\chi_\text{noon})}{(f + f_L)^2\cos i_{110}}\ \text{dB}.$$
  - $A_{T,\text{noon}}$ is 120–375 (Fig. 1 of P.533); ≈ 300 near the equator in October.
  - $\phi_n$ ≈ 1–1.6 is the penetration factor, a function of $f\cos i_{110}/f_oE$.
  - $F(\chi) = \max(\cos^p 0.881\chi, 0.02)$ gives the diurnal variation.
  - $f_L = |f_H\sin I|$ at 100 km (0.25 MHz at Singapore, where the dip $I$ is small).
- **Field strength** (P.533 eqs 17–18): $E_w = 136.6 + P_t + G_t + 20\log f - L_b$ dB(µV/m), with $P_t$ in dB(1 kW) and $L_b = 32.45 + 20\log f + 20\log p' + L_i + L_m + L_g + L_h + L_z$.
  - $p'$ = virtual slant range (km).
  - $L_m$ = above-MUF loss.
  - $L_g = 2(n-1)$ dB = ground-reflection loss.
  - $L_h$ = auroral loss (0 below 42.5° geomagnetic latitude).
  - $L_z$ = 8.72 dB, an empirical excess.
- **Received power** from an isotropic antenna: $P_r = E + G_r - 20\log f - 107.2$ dBW.
- **Noise:** external noise factor $F_a$ dB above $kT_0b$. Man-made noise is $F_{am} = c - d\log_{10}f_\text{MHz}$, with (c, d) = city (76.8, 27.7), residential (72.5, 27.7), rural (67.2, 27.7), quiet rural (53.6, 28.6); galactic (52.0, 23.0). These are P.372, checked against ITURHFProp outputs to 0.01 dB [3][13]. Atmospheric (lightning) noise comes from P.372 maps; it is highest in the tropics, in summer, and at night on low HF.

### Level 2 — derivations and what they imply
**Why the MUF is several times foF2.** Snell's law in a horizontally stratified plasma, $n(h)\sin i(h) = \sin i_0$, turns the ray where $n = \sin i_0$. With $n^2 = 1 - f_p^2/f^2$ this gives $f = f_p/\cos i_0$, the secant law. On a curved Earth, even a ray launched horizontally meets a 300 km layer at $\sin i = R_0/(R_0+300)$, i.e. $i$ = 72.8° and sec $i$ = 3.37. This is the largest obliquity a single F2 hop can have, and it is why MUF(3000) ≈ 3 foF2. The ITU's M(3000)F2 parameter is exactly this ratio, measured from ionograms rather than computed from a mirror.

**Critical angle.** For a given $f$ > foF2, the steepest ray that still returns has $\cos i_c = f_oF2/f$. Translated to the ground through the hop geometry, that is the critical (maximum) take-off angle. Example: 14 MHz with foF2 = 8 MHz gives $i_c$ = 55.2° and a maximum take-off of ≈ 31° (script §1). Steeper rays penetrate, and the ground between the transmitter and the first returning ray is the **skip zone**. **Lower take-off angles mean longer hops.** The maximum one-hop range follows from $\Delta$ = 0: 2351 km via E (110 km) and 3836 km via F2 at 300 km (4130 km at 350 km). With the 3° minimum elevation that P.533 assumes, these become 1776 km and 3225 km (script §1).

**Skip distance.** Invert MUF($d$) = $f$. Over Singapore at noon in October 2026 (foF2 10.6 MHz, M(3000)F2 2.33, foE 3.8 MHz): 10 MHz has no skip zone, 14 MHz skips ≈ 735 km, 21 MHz ≈ 1950 km, and 28 MHz is above even the 4000 km MUF, so it skips everything (script §4). A station 300 km away on 21 MHz is in the silent zone. It is beyond the few tens of km that HF ground wave covers ([ground wave](ground-wave-and-lf-mf-propagation.md)) and inside the skip zone.

**Why absorption makes the LUF and why it is diurnal.** The D-region term scales as $N\nu/(\omega+\omega_L)^2$ ([space weather Level 2](solar-activity-and-space-weather.md#level-2--derivations)), and $N_D$ follows $\cos^p\chi$ of the solar zenith angle. Noon absorption therefore peaks, and absorption collapses within an hour or two of local sunset. For the 2-hop Singapore–Perth path at noon (sec $i_{110}$ = 3.6, R12 = 78) the P.533 form gives **63 dB at 7 MHz, 31 dB at 10 MHz, 16 dB at 14 MHz, 7 dB at 21 MHz** (script §3, $\phi_n$ = 1). That is why 40 m is dead for daytime DX in the tropics and comes alive after dark. **LUF > MUF** happens on long daytime paths at solar minimum and during absorption events: the absorption floor rises above the falling MUF, and no ordinary skywave survives.

**Magneto-ionic (o and x) waves.** In the Earth's field, the Appleton–Hartree refractive index splits into two characteristic waves, ordinary (o) and extraordinary (x). They are **independently propagating, elliptically polarised** waves with different reflection heights, absorption and group delay. The x-wave reflects where $f_p^2 = f(f - f_H)$, so for $f_oF2 \gg f_H$ its critical frequency is higher by about $f_H/2$: **fxF2 − foF2 = 0.52 MHz** over Singapore for foF2 = 10 MHz (exact quadratic, script §6). The x-wave suffers more absorption, since its denominator is $(f - f_L)^2$. Because each mode is elliptically polarised, and the mix and Faraday rotation vary with path and time, a skywave arrives with a random, slowly changing polarisation. **Either a vertical or a horizontal antenna works for HF skywave reception**, and the choice is made on pattern and noise, not polarisation match. The o/x interference is also one source of irregular fading, alongside multipath (T3A08).

### Level 3 — the modes that the simple picture misses
- **Multihop vs chordal hop.** A normal 2F path reflects off the ground once, losing ≈ 2 dB per ground reflection ($L_g$) plus two more D-layer crossings. In **chordal hop** the wave is refracted by the ionosphere twice in succession without touching the ground. This happens where the layer tilts, e.g. near the terminator or across the equatorial anomaly ("FF" mode). The result is **less loss than ground-reflected multihop**, and paths at frequencies above the 2F MUF. Afternoon transequatorial propagation is a chordal mode ([anomalous propagation](vhf-uhf-anomalous-propagation.md)).
- **Grey line.** Along the day/night terminator the D layer has decayed (dusk) or not yet formed (dawn), while the F2 layer is still well ionised. Stations both near their terminators can work long paths on 160–40 m with little absorption, and 160 m DX needs essentially **an all-dark path** because its absorption is so high (f + f_L ≈ 3 MHz). Mid-October terminators (script §5): Singapore sunset ≈ 11:04 UT and sunrise ≈ 23:05 UT; Perth sunset ≈ 10:38 UT and sunrise ≈ 21:55 UT. London sunrise ≈ 06:43 UT and New York sunset ≈ 22:27 UT. The grey-line window for Singapore–Europe on 40/80 m is therefore around Singapore sunset (≈ 11 UT, European afternoon). For Singapore–eastern North America it is around Singapore sunrise (≈ 23 UT, US evening).
- **Long path.** The signal can take the long great-circle arc (40 030 − D km). The long path is best when it lies largely in darkness (low absorption) or along the grey line. It is most often observed on **20 m and 40 m**: 20 m because daylit long paths need a high MUF but low absorption, 40 m because it works on darkened long paths. When both paths are open the long-path signal arrives later, by (36 116 − 3 914) km / c = **107 ms** for Singapore–Perth, heard as a slight echo.
- **NVIS (near-vertical-incidence skywave).** Radiate upward (horizontal dipole 0.1–0.25 λ high) at a frequency **below foF2**, so even vertical rays return. This gives 0–400 km coverage with no skip zone, useful in hilly terrain or across a launch range. Over Singapore in October 2026, foF2 runs from 4.9 MHz (06 SGT) to 12.4 MHz (17 SGT) (script §4). The NVIS window is ≈ 5–10 MHz by day (absorption sets the floor) and ≈ 3–4 MHz pre-dawn.
- **HF scatter.** Inhomogeneities scatter energy in all directions:
  - **Ground backscatter:** the ground far away scatters back toward the transmitter.
  - **Ionospheric sidescatter.**
  - **Equatorial spread-F scatter** after sunset.

  Scatter puts weak energy into the skip zone. The energy arrives via many paths with different delays and Doppler shifts, so signals sound **fluttery and distorted** and are **weak**, because only a small fraction of the power is scattered toward the listener. P.533 models equatorial scatter occurrence (1 for |dip| ≤ 15° at 20–03 LT; [space weather](solar-activity-and-space-weather.md#level-3--storms-polar-caps-and-the-equatorial-ionosphere)). It also models its time spread (σ = 1 ms) and frequency spread (σ = 3 Hz), which matter for digital-mode reliability.
- **Day-to-day variability.** The monthly-median MUF is exceeded on only 50 % of days. P.1239 decile factors give MUF(10 %) ≈ 1.2–1.3 × median and MUF(90 %) ≈ 0.8 × median. The Kranji–Beijing reference case: 36.4/27.8/21.8 MHz [13]. That spread is why the FOT sits ≈ 15 % below the median MUF.
- **What the prediction programs share.**
  - VOACAP (the Voice of America's version of IONCAP), ITURHFProp (P.533), REC533 and many web/phone apps all start from **monthly median** maps of foF2 and M(3000)F2 (P.1239, CCIR 1966). They are driven by a smoothed sunspot number or flux.
  - They differ in mode and loss models (absorption, above-MUF loss, long-path empirical method beyond 7000–9000 km) and in noise maps.
  - None predicts a specific day; use real-time ionosondes (e.g. Australian SWS) and reception networks for that.
  - **Sunspot-number convention matters:** P.1239 coefficients assume the version-1 sunspot scale. SILSO version-2 numbers since 2015 are ≈ 1.4–1.7× larger. Here the R12 choice (53 "V1-like", 78 from F10.7 via the P.1239 relation, 88 V2) changed the peak Singapore–Perth MUF by only ≤ 2 MHz. That is small compared with the day-to-day spread, but it matters near band edges.

## Design equations & rules of thumb

| Rule | Value | Notes |
|---|---|---|
| MUF(3000) / foF2 = M(3000)F2 | 2.5–3.5 | low near the dip equator by day (high hmF2) |
| Max one-hop range E / F2 | 2350 / 3840–4130 km (0°) | 1780 / 3230–3520 km at 3° take-off |
| FOT | ≈ 0.85 × median MUF | MUF(90 %) ≈ 0.8 × median |
| Skip distance | invert MUF(d) = f | 14 MHz ≈ 700 km, 21 MHz ≈ 2000 km (Singapore, noon, 2026) |
| o/x split | fx − fo ≈ fH/2 | 0.5 MHz at Singapore |
| D absorption | ∝ (1 + 0.0067R12)/(f + fL)² × sec i110 | 7 MHz: tens of dB per daytime hop in the tropics |
| Ground-reflection loss | 2 dB per intermediate reflection | chordal hop avoids it |
| Man-made noise | Fam = c − 27.7 log f | residential: 49 dB at 7 MHz, 41 dB at 14 MHz |
| Noise floor | −174 + 10 log B + Fa dBm | Fa 45 dB, 3 kHz → −94 dBm |
| Long-path echo | ΔD/c | 107 ms for a 3900 km path |
| WSPR / FT8 thresholds | −28 / −20 dB SNR in 2.5 kHz | reception reports with SNR |

## Worked examples
**1 — Singapore → Perth, mid-October 2026 (prediction with the P.1239/P.533 machinery; `prop2_hf_paths.py` §2–3).**
- *Geometry.* Singapore (1.35° N, 103.82° E) to Perth (31.95° S, 115.86° E): 3914 km great circle, initial bearing 162°. That exceeds the P.533 3°-elevation one-hop limit, so the lowest-order mode is **2F**: two 1957 km hops, take-off ≈ 13–16°. The midpoint (15.4° S, 109.3° E) lies under the southern equatorial-anomaly crest.
- *Ionosphere.* R12 = 78, the "effective" SSN from the predicted F10.7 ≈ 126 sfu. At 04 UT (12 SGT) the midpoint has foF2 = 11.5 MHz, M(3000)F2 = 2.72, foE = 3.8 MHz and $h_r$ = 372 km.
- *Hourly path MUF* (UT / SGT):

| UT | SGT | F2 basic MUF (MHz) | E MUF | FOT ≈ 0.85 MUF |
|---|---|---|---|---|
| 00 | 08 | 23.7 | 12.0 | 20.2 |
| 04 | 12 | 26.8 | 17.3 | 22.8 |
| 08 | 16 | 29.8 | 15.2 | 25.3 |
| 12 | 20 | 25.1 | 2.5 | 21.3 |
| 16 | 00 | 19.0 | 2.2 | 16.1 |
| 20 | 04 | 12.6 | 2.2 | 10.7 |

- *Absorption at noon (2 hops):* 63 dB at 7 MHz, 31 dB at 10 MHz, 16 dB at 14 MHz, 7.3 dB at 21 MHz.
- *Link budget* (P.533 eqs 17–19; 100 W, residential noise at the receiver, 3 kHz):

| Frequency | SNR, isotropic antennas | SNR, 8 dBi Yagis at both ends |
|---|---|---|
| 14 MHz | −7 dB | +9 dB |
| 21 MHz | +3 dB | +19 dB |
| 24.9 MHz | +6 dB | +22 dB |
| 28 MHz | above the 26.8 MHz MUF: 7.6 dB above-MUF loss | — |

- *Plan:*
  - **18–24 MHz from ~09 to 19 SGT.**
  - **14 MHz in the evening** (20–24 SGT: MUF 25 → 19 MHz).
  - **10 MHz around 02–06 SGT**, when the MUF bottoms at ≈ 12.6 MHz and absorption has vanished.
  - 7 MHz works only at night, and only if the MUF stays above it.
- *Sensitivity:* R12 = 53 or 88 moves the 16-SGT peak to 28.3 or 30.3 MHz. At solar minimum (R12 = 10) the noon MUF is still 21.8 MHz but the pre-dawn MUF falls to 8.2 MHz.

**2 — Singapore → Sydney (6306 km, longer than $d_\text{max}$).** P.533 uses the two control points 1576 km from each end. The basic MUF (2F) is 28.3 MHz at 12 SGT and 19.9 MHz at 20 SGT (R12 = 78), with a minimum of 14.4 MHz at 02 SGT. Daytime choice: 21–24 MHz. The long path (33 724 km) is not useful.

**3 — Why does my 21 MHz contact 300 km away fail at noon?** The skip distance on 21 MHz is ≈ 1950 km at noon (example above), and HF ground wave over land dies within ≈ 30–50 km. The station is in the skip zone. Drop to 7–10 MHz for NVIS (below foF2 ≈ 10.6 MHz; 10 MHz has no skip at noon), or rely on scatter (weak and fluttery).

**4 — Reading a WSPR map.** You run a 1 W WSPR beacon on 14.0956 MHz from Singapore with a dipole. Overnight, spots appear from Western Australia at −15 dB and Japan at −22 dB. Europe appears near Singapore sunset. WSPR decodes to −28 dB in 2.5 kHz, so a −15 dB spot means an SSB signal (needing ≈ +10 dB) would require ≈ +25 dB more: 300× the power, or better antennas. CW or FT8 would already work. Compare the spot times with the predicted MUF table: if 14 MHz spots to Perth vanish after 04 SGT, the MUF (12.6 MHz) has dropped below 14 MHz, as predicted.

**5 — HF link from a remote launch site.** Range 150 km, daytime: NVIS on 5–7 MHz with a low horizontal dipole (MUF for 150 km ≈ 1.05 × foF2 ≈ 11 MHz). At night use 3.5–4.5 MHz. Check absorption: at noon a near-vertical 7 MHz NVIS hop crosses the D layer twice at sec $i_{110}$ ≈ 1.05, so absorption is ≈ 2.1 × 300 × 1.5/(7.25²) ≈ 18 dB (rough). It is workable with SSB at 100 W, but marginal at 5 W.

## Practical notes
- **Prediction tools:**
  - **VOACAP**: Voice of America Coverage Analysis Program, a refined IONCAP. Online point-to-point and area maps exist (e.g. voacap.com); inputs are month, SSN, power, antennas, minimum take-off angle and required SNR. Outputs are MUF, REL (circuit reliability) and SDBW (signal level).
  - **ITURHFProp**: the ITU-R SG3 reference implementation of P.533 and P.372, open source on GitHub. Its example outputs validate `prop2_ccir.py`.
  - **Proppy** and similar web front-ends wrap ITURHFProp.
  - All of these give **monthly medians**. Treat REL < 50 % as "might work on some days".
- **Real-time sources:**
  - **WSPR** (wsprnet.org): 110.6-s, 6 Hz-wide 4-FSK beacons. They report callsign, locator, power and the receiver's measured SNR to a database, so you can map who heard you.
  - **Reverse Beacon Network** (reversebeacon.net): automated SDR "skimmers" that decode CW, RTTY and FT8 and post spots with SNR and speed.
  - **PSKReporter** (pskreporter.info): aggregates reception reports automatically uploaded by digital-mode software (FT8/FT4, JS8, PSK…).
  - All three answer "where is my signal being received right now?" (an exam item). Their data are digital-mode and CW spots, not voice.
  - **Ionosondes:** real-time foF2/MUF(3000) from Australian SWS (Darwin, Learmonth, Cocos, Townsville…) or the GIRO network.
- **Antenna implications:**
  - Long single hops need low take-off angles (3–15°): verticals with radials, or high horizontal antennas.
  - A horizontal dipole at height $h$ has its first lobe at $\sin\Delta = \lambda/4h$. At 14 MHz a 10 m-high dipole peaks near 32°, which is better for NVIS and medium range than for 4000 km DX.
  - NVIS wants the opposite: a low dipole (0.1–0.25 λ).
  - See [HF wire antennas](../08-antennas/wire-antennas-hf-random-wire-fan-dipole.md).
- **Noise decides the LUF in practice.** Singapore's frequent tropical thunderstorms give high atmospheric noise on 1.8–7 MHz, especially in the evening. Atmospheric noise is generally highest in summer at low HF, which is why summer low bands are noisy. Urban man-made noise (residential: 49 dB above $kT_0b$ at 7 MHz) often dominates in a city. A quiet rural receiving site gains up to ~20 dB of SNR on low HF.
- **Exam-style quick answers** (paraphrased; the reasons follow from the sections above):
  - Lower frequency when the MUF falls at night.
  - Least attenuation just below the MUF.
  - Below the LUF, signals are absorbed; LUF > MUF means no skywave.
  - Critical angle = the highest take-off angle that returns.
  - D is the lowest and most absorbing region below 10 MHz by day.
  - The F2 skip is longest because F2 is the highest layer.
  - Scatter is weak and fluttery and fills the skip zone.
  - The long-path echo is "slightly delayed".
  - 10 m F-region DX runs from dawn to shortly after sunset at high sunspot numbers; 6 m and 10 m open at the cycle peak.
  - 160 m needs an all-dark path.
  - Long path is most frequent on 40 m and 20 m.
  - Lower take-off angle means longer hops.
  - Chordal hop is successive ionospheric refractions without a ground reflection, with less loss.
  - VOACAP models HF propagation.
  - Reporting networks report digital-mode and CW reception.

## Common mistakes & misconceptions
- **"The MUF is a property of the ionosphere."** foF2 is; the MUF belongs to a *path* (distance and geometry). The same ionosphere gives MUF ≈ foF2 for NVIS and ≈ 3–3.5 × foF2 for a 3000–4000 km hop.
- **"More power beats the MUF."** Above the MUF the wave escapes to space regardless of power. Power only helps against the LUF (absorption and noise).
- **"Operate right at the MUF for the strongest signal."** The median MUF is exceeded on only half the days, so use the FOT (≈ 0.85 MUF). The best signal is usually just below the MUF.
- **"HF is always a long-distance band."** Within the skip zone, beyond ground-wave range, nothing is heard except weak scatter. Short ranges need NVIS frequencies below foF2.
- **"Low bands are better at night because of less noise."** Atmospheric noise is usually *higher* at night. The bands improve because D-layer absorption disappears.
- **"Polarisation matters for HF skywave."** The returning wave is elliptical and time-varying (o/x modes, Faraday rotation), so either polarisation works. Choose antennas for pattern and noise.
- **"Prediction programs forecast tomorrow."** They give monthly medians. Use WSPR, RBN, PSKReporter and ionosondes for today, and space-weather alerts for disturbances.
- **Plugging a V2 sunspot number into a V1-calibrated model without thinking.** Usually a small effect (≤ 2 MHz on the peak MUF here), but it biases band-edge decisions.

## How to simulate / verify
- `tools/verify/prop2_ccir.py` (ALL PASS; output `prop2_ccir_output.txt`) implements the P.1239 foF2, M(3000)F2 and foEs maps from the official ITU coefficient files. The data live in `tools/verify/data/p1239_maps.npz`, and the modified dip uses a 1960 IGRF field. It also implements P.1239 foE and P.533-14 basic MUF (eqs 2–6, the control-point rules, mode elevation). It is validated against ITURHFProp outputs:
  - 9 control-point foF2 values within 0.07 MHz;
  - M(3000)F2 within 0.004;
  - foE exact;
  - Kranji→Beijing MUF 27.98 vs 27.77 MHz;
  - the mode elevations.
- `tools/verify/prop2_hf_paths.py` (ALL PASS; output `prop2_hf_paths_output.txt`) covers:
  - hop limits and critical angle;
  - Singapore→Perth/Darwin/Sydney hourly MUF for four R12 values;
  - noon absorption and a rough P.533 SNR budget;
  - skip distance and the NVIS window;
  - grey-line times;
  - o/x splitting;
  - P.372 man-made noise constants.
- For full predictions, run ITURHFProp (github.com/ITU-R-Study-Group-3/ITU-R-HF) or VOACAP. Compare with WSPR/PSKReporter spots logged over a month.

## Open questions / gaps
- **Elevation/mirror height:** my transcription of P.533 eqs 14–16 gives ≈ 185 km for the Kranji–Beijing case, whereas ITURHFProp's printed elevations imply 306 km for every mode. The detailed $h_r$ is not implemented; take-off angles use a fixed 300 km mirror.
- The ATnoon (Fig. 1), $\phi_n$ (Fig. 2) and $p$ (Fig. 3) absorption inputs are approximated (ATnoon = 300, $\phi_n$ = 1, noon). There is no LUF/REL calculation with full P.372 atmospheric-noise maps: use ITURHFProp or VOACAP for that.
- No comparison with Singapore-region ionosonde medians: the GIRO DIDBase API was unavailable (HTTP 404) on 2026-10-02.

## Sources
1. ITU-R Recommendation P.533-14 (08/2019), *Method for the prediction of the performance of HF circuits* — control points (Table 1), eqs 1–13 (MUF, screening, elevation), 17–28 (field strength), LUF definition (§9), equatorial scattering (Att. 1). https://www.itu.int/rec/R-REC-P.533/en (standard)
2. ITU-R Recommendation P.1239-4 (08/2023), *ITU-R reference ionospheric characteristics* — numerical maps of foF2 and M(3000)F2 (eqs 1–4, Table 1), foE (eqs 12–18), decile factors. https://www.itu.int/rec/R-REC-P.1239/en (standard)
3. ITU-R Recommendation P.372 (radio noise) — man-made noise lines Fam = c − d log f, galactic noise, atmospheric noise maps; constants confirmed via the ITURHFProp outputs [13]. https://www.itu.int/rec/R-REC-P.372/en (standard)
4. K. Davies, *Ionospheric Radio*, IEE/Peter Peregrinus 1990 — secant law, magneto-ionic theory (o/x), absorption, chordal and scatter modes. (textbook) *cited from standard knowledge*
5. L. F. McNamara, *Radio Amateur's Guide to the Ionosphere*, Krieger 1994 — MUF/LUF/FOT practice, grey line, long path, NVIS. (textbook) *cited from standard knowledge, not re-read*
6. ARRL, *The ARRL Antenna Book* and *ARRL Handbook*, propagation chapters (current eds.) — take-off angles vs antenna height, HF band behaviour over the cycle. (handbook) *cited from standard knowledge*
7. S. R. Saunders, A. Aragón-Zavala, *Antennas and Propagation for Wireless Communication Systems*, 2nd ed., Wiley 2007, ch. 7. (textbook)
8. VOACAP — Voice of America Coverage Analysis Program (IONCAP derivative), online service and documentation, https://www.voacap.com/ (software documentation)
9. J. Taylor (K1JT) et al., *WSJT-X User Guide* — WSPR: 110.6 s, ≈ 6 Hz, 4-FSK at 1.4648 Hz spacing, decodes to −28 dB SNR in 2500 Hz; FT8. https://wsjt.sourceforge.io/ (software documentation)
10. Reverse Beacon Network, https://www.reversebeacon.net/ ; PSKReporter (P. Gladstone), https://pskreporter.info/ (service documentation)
11. Australian Bureau of Meteorology Space Weather Services — ionosonde data and HF prediction products for the Australian/SE-Asian region. https://www.sws.bom.gov.au/ (government service)
12. CCIR Report 340 / "Oslo 1966" foF2 and M(3000)F2 coefficients as distributed with IRI (ccirNN.asc) — identical to the ITU COEFF files to 1.5e-4. (data)
13. ITU-R Study Group 3, *ITURHFProp* (P.533 v14.2, P.372 v14.3) and its example outputs (Kranji–Beijing `itu_old.out`, Sydney–Birmingham, noise test 164-1-78) and P.533 C source (`MUFBasic.c`, `MedianSkywaveFieldStrengthShort.c`). https://github.com/ITU-R-Study-Group-3/ITU-R-HF (reference software)
14. `tools/verify/prop2_ccir.py`, `tools/verify/prop2_hf_paths.py`, `tools/verify/prop2_igrf.py` (this KB).
