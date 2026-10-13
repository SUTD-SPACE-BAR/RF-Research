---
title: Satellite links — orbits, pass geometry, Doppler and Doppler rate, G/T, link budgets and tracking (Gpredict/hamlib)
domain: 09-propagation-link-budget
slug: satellite-links-doppler-tracking
tags: [satellite, leo, meo, geo, orbit, pass-geometry, slant-range, footprint, doppler, doppler-rate, tle, sgp4, j2, sun-synchronous, cubesat, amateur-satellite, tinygs, lora, meteor-m, lrpt, 137-mhz, 437-mhz, g-over-t, c-n0, linear-transponder, gpredict, hamlib, rigctld, rotctld, keyhole, singapore, qo-100]
prerequisites:
  - friis-free-space-path-loss.md
  - link-budget-methodology.md
  - multipath-fading-doppler.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
related:
  - ionospheric-hf-propagation.md
  - polarization-mismatch-loss.md
  - atmospheric-rain-attenuation.md
  - ../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../08-antennas/antenna-polarization-and-circular-polarization.md
  - ../08-antennas/antenna-measurement.md
  - ../08-antennas/helical-antennas.md
  - ../14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md
  - ../20-projects-recipes/beginner-project-ladder.md
  - ../21-gnss/gnss-signals-and-codes.md
  - ../19-regulations-safety/singapore-imda-rules.md
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Satellite links — orbits, pass geometry, Doppler, G/T, link budgets and tracking

## Questions this page answers
- How high are LEO, MEO and GEO satellites, how fast do they move, and how long is a pass?
- How far away is a satellite at 10° elevation, and how much path loss is that at 137 MHz or 437 MHz?
- Why does the Doppler shift sweep from + to − during a pass, and where is it changing fastest?
- Can a LoRa receiver decode a CubeSat without Doppler correction? Which spreading factors fail near zenith?
- What is G/T, and why does my 137 MHz weather-satellite antenna not improve with a better LNA in town?
- How do I do a link budget for a 437 MHz CubeSat or a Meteor-M weather satellite?
- What is a TLE, what does SGP4 do, and how does Gpredict steer a radio and a rotator through hamlib?
- Why can't my az/el rotator follow an overhead pass (the "keyhole")?
- Why do linear transponders invert the passband?
- Can I see QO-100 (the amateur geostationary transponder) from Singapore?

## TL;DR
- **Orbits** (`tools/verify/s17_satellite_pass.py` §1): LEO 400–850 km (period 93–101 min, 7.4–7.7 km/s), MEO GPS 20 180 km (11 h 58 min, 3.87 km/s), GEO 35 786 km (one sidereal day). Slant range at **10° elevation**: 1493 km (420 km orbit), **1756 km (525 km)**, 2408 km (820 km), 24 700 km (GPS), 40 590 km (GEO).
- **Free-space loss** at 437 MHz from a 525 km orbit: **139.7 dB overhead → 150.1 dB at 10° → 153.7 dB at the horizon**. At 137.9 MHz from 820 km: 133.5 → 142.9 → 145.7 dB. Most of the 10 dB swing comes from range. The satellite antenna pattern and the ground antenna's elevation gain decide how much of it you see.
- **Doppler** $f_D = -\dot R f/c$ is an S-curve: largest at AOS/LOS, zero at closest approach. The bound is $f\,vR_E/(c(R_E+h))$, plus Earth rotation. **±10.3 kHz at 437 MHz** (525 km), **±3.07 kHz at 137.9 MHz** (820 km), ±4.9 kHz for GPS L1.
- **Doppler rate** $\dot f_D = -\ddot R f/c$, with $\ddot R = \mathbf a_{rel}\cdot\hat{\mathbf r} + v_\perp^2/R$ (the same formula as for a rocket, [15 impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)). It peaks at closest approach: **≈ 150 Hz/s at 437 MHz on a near-overhead 525 km pass** ($\ddot R$ = 104 m/s² ≈ 10.6 g), and 28 Hz/s at 137.9 MHz.
- **LoRa from LEO:** the ±10 kHz shift sits inside the ±31 kHz (±25 % of 125 kHz) window. The *rate* breaks **SF10/125 and SF12/125 near zenith** (per-packet drift 67 Hz vs a 41 Hz limit, and 269 Hz vs 163 Hz), while SF7–9, SF11/125 + LDRO and SF12/250 pass. This matches the Norby flight result.
- **Link budgets** (§5): a 1 W, 0 dBi, 437 MHz CubeSat at 9600 bit/s closes by **+10.5 dB at 10°** into a 12 dBic crossed Yagi with a masthead LNA (G/T ≈ −10 dB/K). An omni (G/T −24 dB/K) only closes above ≈ 19°. A 22 dBm LoRa CubeSat at SF10/125 reaches a 2 dBi ground plane with +2.4 dB at 10° and +12.9 dB overhead, which is why TinyGS works with simple stations.
- **137 MHz is noise-limited by the environment.** P.372's man-made noise (valid below 250 MHz) is **1800 K rural, 6100 K residential, 16 400 K city**, on top of a 400–4000 K galactic sky. A QFH's G/T is −33 to −41 dB/K, and an LNA buys only **0.5 dB** in a residential site.
- **Tracking:** Gpredict propagates TLEs with SGP4/SDP4. Through **hamlib** it tunes the radio via `rigctld` (default TCP port 4532) and turns the rotator via `rotctld` (4533), applying Doppler to RX and TX separately. On a near-overhead pass the azimuth rate reaches **≈ 156°/s** at closest approach, so an az/el rotator (a few °/s) loses the satellite. Use flip mode, an X–Y mount, or an omni antenna for high passes.
- **From Singapore** an 820 km sun-synchronous satellite gives ≈ 4.5 passes/day (≈ 3 above 10°). **QO-100 (25.9° E) is only 3.4° above the horizon**, so it is marginal behind any obstruction. A geostationary satellite at 103.8° E would be at 88°.

## Intuition (no math)
A low satellite is a fast, nearby transmitter that rises, crosses the sky in about 10 minutes, and sets. At rise and set it is far away (2000–3000 km) and moving almost straight towards or away from you, so the signal is weak and strongly Doppler-shifted. Near the top of the pass it is close (500–800 km) and moving across your line of sight. The signal is strongest there, and the Doppler passes through zero, but it changes fastest because the line of sight swings round quickly. Everything that is hard about satellite links follows from that picture. You need gain at low elevations, where the range is long. You need frequency tracking for the shift, and fast frequency tracking near the top for the rate. You need a pointing system that can swing fast, or an antenna that does not need pointing. A geostationary satellite is the opposite case: it is very far (36 000–41 000 km), so the path loss is huge, but it hangs still. Then the hard parts are gain and its elevation from your latitude and longitude.

## The math

### Level 1 — orbit, range, Doppler
- Circular orbit radius $a = R_E + h$ ($R_E$ = 6378.137 km). Speed $v = \sqrt{\mu/a}$ and period $T = 2\pi\sqrt{a^3/\mu}$, with $\mu = 3.986\,004\,418\times10^{14}$ m³/s². 525 km gives 7.60 km/s and 95.1 min (15.1 rev/day).
- Slant range at elevation $\varepsilon$: $\rho(\varepsilon) = \sqrt{a^2 - R_E^2\cos^2\varepsilon} - R_E\sin\varepsilon$. Overhead $\rho = h$; at 0°, $\rho = \sqrt{a^2 - R_E^2}$.
- Earth-central angle from the station to the sub-satellite point: $\lambda = \arccos(R_E\cos\varepsilon/a) - \varepsilon$. This is the footprint radius at elevation $\varepsilon$ (22.5° at 0° and 14.5° at 10° for 525 km).
- Doppler: $f_D = -\dot R\,f/c$, where $\dot R$ is the range rate (positive when receding). Doppler rate: $\dot f_D = -\ddot R\,f/c$.
- Link: $C/N_0 = \mathrm{EIRP} - L_{path} - L_{other} + G/T + 228.6$ dB-Hz, with $G/T = G - 10\log_{10}T_{sys}$ in dB/K. The link closes if $C/N_0 \ge (E_b/N_0)_{req} + 10\log_{10}R_b$ + implementation loss ([link budget methodology](link-budget-methodology.md)).

### Level 2 — derivations
**Slant range.** In the triangle formed by the Earth centre, the station and the satellite, the angle at the station is $90° + \varepsilon$. The law of cosines, $a^2 = R_E^2 + \rho^2 + 2R_E\rho\sin\varepsilon$, solved for $\rho$ gives the formula above. The script checks it against the law-of-cosines form using $\lambda$ (1756 km at 10° for 525 km).

**Maximum range rate.** For a pass whose orbit plane contains the observer (and ignoring Earth rotation), the satellite velocity is perpendicular to its radius vector. The component along the line of sight is largest at the horizon, where $\dot R_{max} = v\,R_E/a$. That is 7.02 km/s for 525 km, giving 10.23 kHz at 437 MHz. Earth rotation adds or subtracts up to $\omega_E R_E\cos\phi\cdot(\ldots)$ ≈ 0.46 km/s at the equator. A retrograde sun-synchronous orbit seen from Singapore picks up part of it, giving the simulated 7.09 km/s and **10.34 kHz**. For GPS the bound is $3.87\times6378/26558$ = 0.93 km/s, or **4.89 kHz** at L1. GNSS receivers therefore search ±5 kHz ([21 receiver](../21-gnss/gnss-receiver-architecture-acquisition-tracking.md)).

**Doppler rate.** Differentiate $R^2 = \mathbf r\cdot\mathbf r$ twice, where $\mathbf r$ is satellite minus station:
$$\ddot R = (\mathbf a_{sat} - \mathbf a_{stn})\cdot\hat{\mathbf r} + \frac{|\mathbf v_{rel}|^2 - \dot R^2}{R}.$$
At closest approach $\dot R = 0$, so the second term is $v_{rel}^2/R_{min}$, the line of sight sweeping round. The first term is the satellite's gravitational acceleration projected on the line of sight. Overhead, that is −8.4 m/s², because it points away from the station. On the near-overhead 525 km pass, $v_{rel}$ = 7.68 km/s: the satellite is retrograde (i = 97.5°) while the station moves east at 0.46 km/s. So $\ddot R = 7680^2/525\,000 - 8.4 = 104$ m/s², and $\dot f_D = 104 \times 437\times10^6/c$ = **151 Hz/s**. The script's analytic $\ddot R$ agrees with a finite-difference second derivative of the range to < 0.02 m/s². This is the same physics as a ground station near a rocket pad (13.7 g vs 11.1 g, [15 impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)).

**Doppler through a linear transponder.** The satellite receives $f_u(1-\beta)$, with $\beta = \dot R/c$. A non-inverting transponder retransmits $f_u(1-\beta) + \Delta$; an inverting one retransmits $C - f_u(1-\beta)$ with $C = f_u + f_d$. The ground then hears the retransmitted frequency × $(1-\beta)$. To first order the net shift is $-\beta(f_d + f_u)$ for a non-inverting transponder and $-\beta(f_d - f_u)$ for an inverting one. For V/U (145.9 up, 435.9 down) at 7.09 km/s that is **13.8 kHz vs 6.9 kHz** (§4; the exact second-order value agrees to 0.1 %). Inversion halves the Doppler your own signal sees in the passband. That is why most amateur linear transponders invert, and why "full Doppler" operation means correcting the uplink so the satellite hears a fixed frequency, then correcting the downlink separately.

**G/T and the system temperature.** $T_{sys} = T_A + (L-1)T_0 + L\,T_{rx}$ at the antenna terminal, for a feed loss $L$ before a receiver of noise temperature $T_{rx}$. $T_A$ is the pattern-weighted brightness of sky, ground and man-made noise ([07 thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md), [08 antenna measurement](../08-antennas/antenna-measurement.md#antenna-temperature-and-gt-vs-elevation-over-ground)). Galactic brightness scales as $f^{-2.75}$: the 408 MHz values of 20/60/200 K become **395/1185/3950 K at 137.9 MHz**. P.372 man-made noise $F_{am} = c - d\log f$ is *inside* its 0.3–250 MHz validity range at 137.9 MHz. It gives 50 K quiet rural, 1800 K rural, 6100 K residential and 16 400 K city. At 437 MHz both are much smaller, and for a Yagi pointed up the receiver dominates.

### Level 3 — real orbits, tracking models, limits
- **TLEs and SGP4.** NORAD two-line element sets carry the epoch, inclination, RAAN, eccentricity, argument of perigee, mean anomaly, mean motion (rev/day), its derivatives and a drag term B*. They are *mean* elements fitted for the **SGP4** model, near-Earth, period < 225 min. **SDP4** adds deep-space lunar–solar terms for longer periods. Propagating a TLE with a different model (e.g. pure Kepler) gives errors that grow quickly. The standard implementation is Vallado et al. 2006 [3]. Gpredict uses SGP4/SDP4 [4]. TLE accuracy degrades by roughly km per day from epoch, more for low, high-drag CubeSats (order of magnitude; see Open questions). Refresh TLEs before each session, and after a launch use the operator's or the deployment's published elements.
- **This page's script is not SGP4.** It uses a circular orbit with the J2 secular drift of the node, $\dot\Omega = -\tfrac32 nJ_2(R_E/a)^2\cos i$. The sun-synchronous condition $\dot\Omega$ = 360°/year gives **i = 97.50° at 525 km and 98.69° at 820 km**. That is enough for geometry, Doppler and rates, but not for predicting real pass times.
- **Pass statistics from Singapore** (1.35° N). A sun-synchronous orbit's ground tracks are spaced ≈ 24–25° of longitude at the equator, so an equatorial station sees fewer passes than a high-latitude one. In 96 h the 525 km orbit gave 15 passes above 0° (8 with a maximum above 10°). The 820 km orbit gave 18 (12 above 10°, 5 above 30°).
- **Ionosphere.** Faraday rotation is large at VHF and UHF (216° at 433 MHz for 10¹⁸ el/m², [ionosphere](ionospheric-hf-propagation.md)). A linear satellite antenna into a linear ground antenna therefore fades unpredictably; use circular polarisation on the ground and accept a fixed 3 dB loss against a linear satellite antenna. Singapore sits under the equatorial anomaly: post-sunset scintillation near the equinoxes affects VHF/UHF satellite links as well as GNSS ([space weather](solar-activity-and-space-weather.md)).
- **Atmosphere and rain** are negligible below 3 GHz (gases ≲ 0.2 dB even at 10° elevation). They matter at 10 GHz and up ([atmospheric](atmospheric-rain-attenuation.md)).
- **Satellite antennas.** CubeSat monopoles and dipoles have nulls and tumble, so a fixed "0 dBi" is an average with ± several dB of spin fading. Some weather satellites use shaped "isoflux" patterns that put more gain towards the horizon to offset the range.

## Design equations & rules of thumb
| Quantity | Equation | Values (script) |
|---|---|---|
| Period, speed | $T = 2\pi\sqrt{a^3/\mu}$, $v = \sqrt{\mu/a}$ | 525 km: 95.1 min, 7.60 km/s; GPS 717.9 min; GEO 1436.1 min |
| Slant range | $\sqrt{a^2 - R_E^2\cos^2\varepsilon} - R_E\sin\varepsilon$ | 525 km: 525/951/1756/2641 km at 90/30/10/0° |
| Footprint half-angle | $\arccos(R_E\cos\varepsilon/a) - \varepsilon$ | 525 km: 22.5° (0°), 14.5° (10°) |
| Max range rate | $\le vR_E/a$ (+ Earth rotation ≤ 0.46 km/s) | 7.02 km/s (525 km); 0.93 km/s GPS |
| Doppler | $-\dot R f/c$ | ±10.3 kHz @437 MHz; ±3.07 kHz @137.9 MHz; ±4.9 kHz GPS L1 |
| Doppler rate | $-f\ddot R/c$, $\ddot R = \mathbf a_{rel}\cdot\hat r + v_\perp^2/R$; peak ≈ $f(v_{rel}^2/R_{min} - g_h)/c$ | 151 Hz/s @437 MHz overhead 525 km; 28 Hz/s @137.9 MHz |
| Transponder Doppler | inverting $\beta(f_d - f_u)$; non-inverting $\beta(f_d + f_u)$ | V/U: 6.9 vs 13.8 kHz |
| SSO inclination | $\cos i = -\dot\Omega_{SSO}/(\tfrac32 nJ_2(R_E/a)^2)$ | 97.50° (525 km), 98.69° (820 km) |
| C/N0 | EIRP − L + G/T + 228.6 | see worked examples |
| GEO elevation | $\tan\varepsilon = (\cos\gamma - R_E/a)/\sin\gamma$, $\cos\gamma = \cos\phi\cos\Delta\lambda$ | QO-100 from Singapore 3.4°; Himawari (140.7° E) 47.2° |

## Worked examples

**1. A 525 km sun-synchronous CubeSat pass over Singapore** (§2, illustrative elements: i = 97.50°, RAAN₀ = 100°, GMST = 0 at t = 0).
- *Highest pass in 96 h*: maximum elevation 79.4° at azimuth 257°. It is above 0° for 11.8 min and above 10° for 7.5 min. It rises at az 171° (south) and sets at az 347° (north-north-west), so it is a northbound (ascending) pass. The range runs 2641 km → 533 km → 2641 km. The Doppler at 437 MHz goes from **+10.34 kHz to −10.33 kHz**, crossing zero at closest approach. The peak rate is **149 Hz/s**, at maximum elevation. The rotator needs at most 4.5°/s in azimuth and 0.65°/s in elevation.
- *Pass nearest 30°* (max 26.6°): 11.1 min above 0°, 6.4 min above 10°. Doppler ±9.7 kHz (the low-elevation ends dominate). Peak rate 76 Hz/s, half that of the high pass, because $R_{min}$ is 1032 km. Azimuth rate 0.48°/s.
- *Keyhole*: nudge RAAN₀ to 100.84° and the same pass goes through 89.9° elevation. The azimuth then has to swing 180° in about a second: **156°/s at closest approach**. No hobby az/el rotator follows that. Options: pre-rotate and accept a dropout of a few seconds, use flip mode (elevation over 90° with the azimuth turned 180°, if your rotator and controller support it), use an X–Y mount, or use an omni antenna for passes above ≈ 75°.

**2. 437 MHz CubeSat at 9600 bit/s, 1 W into 0 dBi** (§5a). EIRP 0 dBW. A linear satellite antenna into a CP ground antenna costs 3 dB; add 0.5 dB of other losses. Required C/N0 = 12 dB ($E_b/N_0$ for non-coherent GMSK/FSK at about 10⁻⁵, an assumed figure) + 39.8 + 2 (implementation) = **53.8 dB-Hz**.

| Ground station | T_sys | G/T | Margin at 90° / 30° / 10° |
|---|---|---|---|
| 12 dBic crossed Yagi, masthead LNA NF 0.8 dB, 0.3 dB feed; $T_A$ 49/60/101 K ([08]; the 30° value is interpolated) | 133–185 K | −9.2 … −10.7 dB/K | **+22.4 / +16.9 / +10.5 dB** |
| 0 dBic omni (turnstile/eggbeater), LNA NF 0.8 dB, $T_A$ ≈ 150 K | 234 K | −23.7 dB/K | +7.9 / +2.8 / **−2.6 dB** |
| RTL-SDR (NF 6 dB) on the Yagi after 5 m of RG-58 (1.5 dB) | ≈ 1400 K | −19.5 dB/K | +12.2 / +7.0 / +1.5 dB |

A masthead LNA is worth ≈ 9–10 dB here: at 437 MHz the receiver, not the sky, sets $T_{sys}$, which agrees with [08](../08-antennas/antenna-measurement.md#antenna-temperature-and-gt-vs-elevation-over-ground). An omni closes only above ≈ 19° (−1.0 dB at 15°, +0.4 dB at 20°), so it loses the first and last few minutes of each pass. For an omni-CP antenna that serves overhead passes well, see [08 polarisation § omni-CP](../08-antennas/antenna-polarization-and-circular-polarization.md#omni-cp-antennas-for-overhead-passes-turnstile-eggbeater-lindenblad).

**3. TinyGS-style LoRa from 525 km** (§5b): 22 dBm (SX1268 maximum) into 0 dBi, a 2 dBi ground plane, a 6 dB-NF module, 3 dB polarisation and 0.5 dB other losses.

| SF/125 kHz | sensitivity | margin 90° | 30° | 10° |
|---|---|---|---|---|
| SF7 | −124.5 dBm | +5.4 dB | +0.2 | −5.1 |
| SF10 | −132.0 dBm | +12.9 dB | +7.7 | +2.4 |
| SF12 | −137.0 dBm | +17.9 dB | +12.7 | +7.4 |

*Doppler.* The static offset (≤ 10.3 kHz) is inside the ±31.25 kHz window, so no correction is needed to acquire. The **drift during a 32-byte packet** on the near-overhead pass, against Semtech's $BW/(3\cdot2^{SF})$ (×16 with LDRO): SF7 10.7/326 Hz, SF9 36.7/81 Hz, **SF10 67/41 Hz (fails near closest approach, for 13 % of packet start times)**, SF11/125 + LDRO 147/326 Hz, **SF12/125 + LDRO 269/163 Hz (fails)**, SF12/250 + LDRO 135/326 Hz. High-SF links fail near zenith and survive at low elevation. That is the pattern reported from the Norby CubeSat (436.7 MHz, 560 km) [5]. It is also why LoRa satellites often use SF ≤ 9, 250 kHz, or LDRO, or pre-correct the carrier from the TLE.

**4. Meteor-M LRPT at 137.9 MHz into a QFH** (§5c). LRPT is QPSK at 72 kBd, ≈ 120–150 kHz wide, RHCP [6][7]; the EIRP is **not published** in the sources read. Assume $E_b/N_0$ ≈ 2.5 dB at 10⁻⁵ for the K = 7, r = ½ Viterbi + Reed–Solomon chain plus 2 dB of implementation loss. The required C/N0 is then ≈ **53 dB-Hz**. The QFH is 2 dBic, sees 70 % sky (typical 1185 K) and 30 % ground, and has a 0.5 dB feed.

| Site (P.372 man-made added to $T_A$) | T_sys, RTL-SDR NF 6 dB | G/T | EIRP needed at 90° / 30° / 10° |
|---|---|---|---|
| Rural | 3720 K | −33.7 dB/K | −7.8 / −3.0 / +1.6 dBW |
| Residential | 8030 K | −37.0 dB/K | −4.5 / +0.3 / +4.9 dBW |
| City | 18 360 K | −40.6 dB/K | −0.9 / +3.9 / +8.5 dBW |

An LNA (NF 1 dB) gains only **0.5 dB** in the residential case, because the antenna is already 7000 K. Spend effort on location, a filter against 138–175 MHz pagers ([14 recipe](../14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md#recipe--meteor-m-lrpt-weather-images-noaa-apt-is-gone)) and elevation, not on noise figure. The common advice to use passes above ≈ 25–30° in a town is consistent with an EIRP of a few dBW. That is an inference, not a published value.

**5. Linear transponder (V/U, inverting)** (§4). At 7.09 km/s your own uplink shifts 3.45 kHz at 145.9 MHz and the downlink 10.31 kHz. Heard back through an inverting transponder, your signal moves by only 6.86 kHz across the pass; through a non-inverting one it would move by 13.76 kHz. Gpredict's radio controller handles both: it keeps the uplink on a fixed satellite-receive frequency and corrects the downlink.

**6. Geostationary from Singapore** (§5d). From $\cos\gamma = \cos\phi\cos\Delta\lambda$, QO-100 (Es'hail-2, 25.9° E, 77.9° west of Singapore) is at **3.4° elevation**, 41 300 km away; the 10.489 GHz downlink FSPL is 205.2 dB. It is usable only with a clear western horizon. A satellite at Singapore's own longitude would be at 88.4° (35 788 km), and Himawari at 140.7° E at 47.2°.

## Practical notes
- **Tracking stack.** Gpredict (TLE download from CelesTrak/AMSAT, SGP4/SDP4) → **hamlib** daemons. `rigctld` controls the radio over TCP (default port 4532) and `rotctld` the rotator (default 4533; hamlib suggests even ports for rigs and odd ports for rotators) [4][8]. In Gpredict's radio controller set the downlink and uplink, choose the transponder, and "Engage". It writes Doppler-corrected frequencies to the receive and transmit VFOs separately; `rigctld -x` selects which VFO is the uplink so Gpredict does not read the other one back [8]. SDR software (SDR++, GQRX) can act as a rigctld-compatible radio. For Meteor-M, SatDump does its own scheduling and Doppler.
- **Rotators**: an az/el rotator with ±180–450° azimuth needs a cable-wrap plan and a strategy for the keyhole (Example 1). Gpredict's rotator controller has a tolerance setting so it does not chatter; set it well below half the antenna beamwidth (a 12 dBic Yagi is ≈ 50° wide by $\sqrt{41\,253/G}$, so ±5–10° is fine).
- **Antennas**: crossed Yagis (switchable RHCP/LHCP) for 437 MHz; QFH or V-dipole for 137 MHz ([helical/QFH](../08-antennas/helical-antennas.md)); turnstile or eggbeater omni-CP for TinyGS-type stations. Put the LNA at the antenna; the masthead LNA matters at UHF but much less at 137 MHz in town (Examples 2 and 4).
- **Frequency accuracy**: an RTL-SDR with a ±1 ppm TCXO is ±437 Hz at 437 MHz, small compared with the Doppler but enough to bias a narrow FSK demodulator. Calibrate against a known carrier before a pass.
- **Licensing**: receiving satellites needs no licence. Transmitting to an amateur satellite needs an amateur licence. A CubeSat's own frequencies are IARU-coordinated and ITU-notified ([19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md)).
- **Weather satellites today**: NOAA-15/18/19 APT ended in 2025. Meteor-M N2-3 and N2-4 on 137.9 MHz (137.1 MHz backup) are the 137 MHz targets [6][7] (status changes; see the [beginner project ladder](../20-projects-recipes/beginner-project-ladder.md)).

## Common mistakes & misconceptions
- **"The Doppler is worst when the satellite is overhead."** The *shift* is zero there; the *rate* is at its maximum. The shift is largest near the horizon.
- **"Use the satellite's orbital speed for the Doppler."** Only the line-of-sight component counts, and it is at most $vR_E/a$ (≈ 92 % of v for LEO, 24 % for GPS), plus Earth rotation.
- **Doppler rate from the satellite's acceleration alone.** The satellite's acceleration is only 8–9 m/s² (gravity), but $\ddot R$ reaches ≈ 100 m/s² because of the $v_\perp^2/R$ term. The same mistake understates rocket budgets ([15](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)).
- **"A better LNA will fix my 137 MHz reception."** In a town, man-made noise sets $T_{sys}$ at thousands of kelvin (Example 4). Move the antenna, filter, and wait for higher passes.
- **Propagating TLEs with a Kepler model, or using old TLEs.** TLEs are SGP4 mean elements. Use SGP4 (Gpredict, SatDump, `sgp4` in Python) and fresh elements, especially just after a launch.
- **Linear antenna on the ground for a VHF/UHF satellite.** Faraday rotation and spacecraft tumble turn a fixed polarisation loss into deep random fades. A CP ground antenna costs a constant 3 dB against a linear spacecraft antenna instead.
- **Forgetting the keyhole.** A high pass on an az/el rotator drops out for the most important (strongest) minute.

## How to simulate / verify
- `python3 tools/verify/s17_satellite_pass.py` — orbit table, slant range and footprint, a 96 h pass list from Singapore (two-body + J2), Doppler and Doppler-rate curves with the analytic $\ddot R$ checked against finite differences, the keyhole demonstration, transponder Doppler, the 437 MHz / LoRa / LRPT budgets with G/T, the per-packet LoRa drift check and GEO elevations. Ends ALL PASS (output in `s17_satellite_pass_output.txt`).
- `python3 tools/verify/s17_doppler_rate_los.py` — symbolic proof of $\ddot R = \mathbf a\cdot\hat r + v_\perp^2/R$.
- For real passes: Gpredict (or `sgp4` + a current TLE) for times and azimuths. Record the Doppler curve with an SDR; the zero-crossing time gives closest approach, and the slope there gives $v_{rel}^2/R_{min}$, a self-check of the TLE.
- Bench: replay a recorded LoRa packet from an SDR with a programmed frequency ramp of 150 Hz/s to reproduce the zenith condition ([15 impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#how-to-simulate--verify)).

## Open questions / gaps
- Meteor-M LRPT EIRP and antenna pattern are not in any source read (WMO OSCAR, sigidwiki and SatNOGS list frequency, bandwidth, polarisation and rate only). Example 4 therefore gives the EIRP *needed*.
- The LRPT symbol rate is given as 72 kBd (sigidwiki, SatNOGS) and 80 kbit/s (WMO OSCAR, SatNOGS). This may be a symbol-rate vs data-rate labelling difference, and it is unresolved.
- The TLE/SGP4 accuracy figure ("≈ km/day") is an order of magnitude from general literature, not a measured value for CubeSats in 500 km orbits.
- No measured Space Bar satellite reception yet. A Singapore Meteor-M or TinyGS log (SNR vs elevation) would calibrate Examples 2–4.
- The $E_b/N_0$ requirements in Examples 2 and 4 are assumed demodulator figures.

## Sources
1. D. A. Vallado, *Fundamentals of Astrodynamics and Applications*, 4th ed., Microcosm, 2013, chs. 2–4 and 9 (two-body motion, J2 secular rates, sun-synchronous condition, look angles). (textbook; standard relations re-derived in the script)
2. W. J. Larson, J. R. Wertz (eds.), *Space Mission Analysis and Design*, 3rd ed., 1999, ch. 5 (space mission geometry) and ch. 13 (communications architecture) (Earth-geometry slant range and footprint, satellite link budget with G/T and C/N0). (textbook)
3. D. A. Vallado, P. Crawford, R. Hujsak, T. S. Kelso, "Revisiting Spacetrack Report #3," AIAA 2006-6753 — the reference SGP4/SDP4 implementation and the TLE mean-element convention. (peer-reviewed conference paper)
4. Gpredict package description (Debian/Ubuntu AppStream metadata): real-time tracking with SGP4/SDP4 and NORAD TLEs, Doppler tuning via hamlib rigctld, rotator control via rotctld. https://appstream.debian.org/trixie/main/metainfo/gpredict.html (software documentation; via search summary)
5. "Doppler estimation and compensation in LoRa direct-to-satellite," arXiv:2506.20858 (2025), summarising Doroshkin et al. 2019 and the Norby CubeSat flight (SX1278, 436.703 MHz, 560 km: Doppler-shift failures at low elevation, Doppler-rate failures at zenith). (preprint; same source as [15 impairments] [5])
6. WMO OSCAR/Space, "Meteor-M N2-3" — SSO 820 km, 15:00 ascending node; LRPT 137.1/137.9/137.9125 MHz, 150 kHz, RHCP, 80 kbit/s; operational with limitations (page updated 2025-06-09). https://space.oscar.wmo.int/satellites/view/meteor_m_n2_3 (agency database)
7. sigidwiki, "Low Rate Picture Transmission (LRPT)" — QPSK 72 kBd, ≈ 120 kHz, 144 kbit/s raw, RS + convolutional coding. https://sigidwiki.com/wiki/Low_Rate_Picture_Transmission_(LRPT) (community wiki)
8. hamlib `rigctld(1)` and `rotctld(1)` manual pages (openSUSE Leap 15.6) — default ports 4532/4533, even/odd port advice, `-x` uplink VFO option for Gpredict. https://manpages.opensuse.org/Leap-15.6/hamlib/rigctld.1.en.html (software manual; via search summary)
9. ITU-R P.372-13 (2016), §5 and Table 1 — man-made noise $F_{am} = c - d\log f$, valid 0.3–250 MHz; galactic noise. Read from the ITU PDF 2026-10-13 (see `tools/verify/s17_p372_city.py`). (standard)
10. NOAA POES decommissioning (NOAA-18 June 2025; NOAA-19 13 Aug 2025; NOAA-15 19 Aug 2025), as recorded in [14 _sources](../14-sdr-dsp/_sources.md) and the RTL-SDR.com / ARNewsline reports. (operator notices via news; secondary)
