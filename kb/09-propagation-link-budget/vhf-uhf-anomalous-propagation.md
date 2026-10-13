---
title: VHF/UHF anomalous propagation — tropospheric ducting, super-refraction, sporadic-E, meteor scatter, aurora, TEP, aircraft scatter and EME
domain: 09-propagation-link-budget
slug: vhf-uhf-anomalous-propagation
tags: [anomalous-propagation, refractivity, M-units, ducting, evaporation-duct, super-refraction, temperature-inversion, sporadic-E, ITU-R-P.534, meteor-scatter, MSK144, auroral-propagation, transequatorial-propagation, TEP, aTEP, eTEP, aircraft-scatter, EME, moonbounce, libration-fading, LoRa-interference, 433-MHz, 915-MHz]
prerequisites: [fresnel-zones-los-radio-horizon.md, ionospheric-hf-propagation.md, friis-free-space-path-loss.md]
related: [solar-activity-and-space-weather.md, hf-propagation-modes-and-prediction.md, diffraction-knife-edge.md, empirical-path-loss-models.md, link-budget-methodology.md, ../11-radar/radar-range-equation.md, ../15-lora-ism-radios/lora-sensitivity-and-link-budget.md, ../15-lora-ism-radios/lorawan-vs-raw-lora.md, ../15-lora-ism-radios/ground-station-design.md, ../08-antennas/antenna-polarization-and-circular-polarization.md]
level: mixed
confidence: high
last_updated: 2026-10-03
---

# VHF/UHF anomalous propagation — tropospheric ducting, super-refraction, sporadic-E, meteor scatter, aurora, TEP, aircraft scatter and EME

## Questions this page answers
- Why is the VHF/UHF radio horizon about 15 % farther than the visual horizon?
- What is tropospheric ducting? What causes it (temperature inversions, evaporation over water), and how far can it carry signals?
- Where does the "−157 N/km" ducting threshold come from, and what are M-units?
- Which frequencies can a given duct trap? Can a duct carry my 433/915 MHz LoRa signal hundreds of km or bring in interference?
- What is sporadic-E? When does it happen (season, time of day), and how high in frequency does it work?
- How does meteor-scatter communication work, and why is 6 m the best band for it?
- What causes auroral propagation, why does it sound raspy, and why is CW best?
- What is transequatorial propagation (TEP), when does it occur, and how far does it reach? Is Singapore a good place for it?
- What is aircraft scatter, and what limits its range?
- How much path loss does an EME (moon-bounce) path have, and what are libration fading and the perigee advantage?
- Why do VHF/UHF weak-signal operators use horizontal polarisation?
- My Meshtastic node "heard" a station 400 km away. Is that ducting or the internet?

## TL;DR
- **Refraction normally extends the VHF/UHF horizon.** Air's radio refractivity $N = (n-1)\times10^6$ (≈ 315 at mid-latitudes; ≈ 400 in humid Singapore air) falls by ≈ 40 N/km with height. That bends rays down with an effective Earth radius $k a$, $k$ = 4/3, so the radio horizon is $\sqrt{4/3}$ = **1.15× (≈ 15 %)** the geometric one ([Fresnel/horizon](fresnel-zones-los-radio-horizon.md)).
- **Ducting:** when $dN/dh \le -157$ N/km over a layer, the ray curvature equals or exceeds the Earth's curvature (derived below: $-10^6/a$). Waves are then trapped in a "waveguide" and travel hundreds of km with little more than free-space loss. In **modified refractivity** $M = N + 157h$ (h in km), a duct is wherever $dM/dh < 0$. Causes:
  - temperature inversions (warm dry air over cool moist air);
  - nocturnal radiation;
  - subsidence;
  - **evaporation over warm sea**, which gives a near-permanent 10–20 m "evaporation duct".
  
  Typical ducting ranges are **≈ 160–500 km (100–300 mi)**, sometimes > 1000 km over sea.
- **A duct only traps wavelengths shorter than ≈ 2.5 d √(ΔM × 10⁻⁶)** (d = duct thickness, ΔM = M-deficit; derived below). A 15 m evaporation duct traps **≥ 2 GHz** only. A 100 m inversion duct traps **≥ 270 MHz**, so 433 and 915 MHz LoRa *can* be ducted by elevated or surface-based inversion layers, not by the sea-surface evaporation duct (`tools/verify/prop2_vhf_anomalous.py` §3).
- **Sporadic-E (Es):** thin, dense patches of E-layer ionisation (90–120 km) with foEs of 5–25+ MHz. One hop reaches up to ≈ 2300 km, with a MUF up to ≈ 5.4 × foEs: 6 m and 10 m often, 2 m occasionally (needs foEs ≳ 26 MHz). At mid-latitudes it peaks **around the solstices, especially in summer**, **in daytime (≈ 08–23 LT)**. The P.1239 maps put Tokyo's June noon upper-decile foEs at 12.8 MHz vs 5.7 MHz in January. Over Singapore a weak, year-round equatorial Es (median ≈ 5 MHz at noon) is the norm.
- **Meteor scatter:** meteors ablating in the **E region** leave linear ionised trails at 80–120 km that reflect VHF for 0.01–1 s. Range ≤ ≈ 2250 km. Lower VHF lasts longer and is stronger: trail duration ∝ λ², underdense power ∝ λ³. **28–148 MHz is the useful range, and 6 m the best band**; MSK144 handles the short bursts. Major showers include the Perseids (Aug) and Geminids (Dec).
- **Aurora:** during severe geomagnetic storms, field-aligned E-region irregularities in the auroral oval scatter VHF. Signals are Doppler-spread by hundreds of Hz, giving a **raspy, hissy** tone; **CW** is best. It does not occur at Singapore's latitude.
- **TEP:** VHF links of **≈ 3000–8000 km across the geomagnetic equator** between stations roughly symmetric about the dip equator. Afternoon TEP runs 15–19 LT up to ~60 MHz. Evening TEP runs **20–23 LT** up to 144 (rarely 432) MHz, with deep flutter, so CW only. It is most common near the equinoxes and at solar maximum. Classic pairs are Japan/Okinawa–northern Australia: Okinawa–Darwin is 4313 km with dip latitudes +21.7°/−22.5°. Singapore (dip latitude −6.5°) sits too close to the dip equator to be a classic TEP endpoint.
- **EME:** the two-way isotropic loss is $\eta r^2\lambda^2/(64\pi^2 d^4)$ (Moon radius $r$, reflectivity η = 0.065). That is **252.1 dB at 144 MHz, 261.6 dB at 432 MHz and 271.2 dB at 1296 MHz** (script = ARRL table to 0.1 dB). Perigee gives ≈ 2.3 dB less loss than apogee. The echo delay is ≈ 2.5 s. Libration fading is fluttery and irregular. Two stations can work each other at almost any separation (≈ 12 000 mi) while both see the Moon.

## Intuition (no math)
The lower atmosphere is a lens. Its refractive index depends mostly on pressure (which falls steadily with height) and water vapour (which can change abruptly). Normally the index decreases smoothly upward, so radio rays bend gently downward and see a horizon a little farther away than your eye does. Light's refractive index barely depends on water vapour, while radio's does strongly.

If a layer forms where the index drops *very* fast with height, rays bend as much as or more than the Earth curves. Examples are warm, dry air sitting on top of cool, moist air (an **inversion**), or the sticky-humid layer just above a warm sea. The rays then hug the surface or skip along inside the layer like light in an optical fibre: a **duct**. A duct guides only waves small enough to "fit". Thin sea-surface ducts guide microwaves; thick inversions can also guide UHF. Inside a duct, signals stay strong far beyond the horizon. This brings in distant TV, distant repeaters, and distant LoRa nodes that should be impossible to hear, and it can make a normally good link fade when the duct bends energy away.

Above 60 km, at VHF the ionosphere is mostly transparent, but there are bright mirrors that come and go:
- **Sporadic-E clouds**, mostly in summer daytime at mid-latitudes;
- **Meteor trails**, lasting a fraction of a second each;
- **Aurora**, when a big geomagnetic storm pushes the auroral oval toward the equator;
- **The equatorial F-region** in the afternoon and evening, giving TEP.

Each has its own season, hour and sound. Finally, you can use the **Moon** as a passive reflector. It is a poor mirror (6.5 % reflectivity) 384 000 km away, so it costs ≈ 250–290 dB, but big antennas and digital modes overcome that.

## The math

### Level 1 — formulas and symbols
- **Refractivity** (ITU-R P.453-14 eq. 7): $N = \dfrac{77.6}{T}\left(P + 4810\dfrac{e}{T}\right)$. Here $T$ is in K, $P$ is total pressure in hPa and $e$ is water-vapour pressure in hPa (from relative humidity and saturation pressure, P.453 eqs 8–9). Script §1: 15 °C dry air, N = 273; 15 °C at 60 % RH, N = 319; Singapore afternoon (30 °C, 80 %, 1009 hPa), **N = 396**, of which the wet term is ≈ 138.
- **k-factor**: $k = 1/(1 + a\,dn/dh)$, with $a$ = 6371 km and $dn/dh = 10^{-6}\,dN/dh$. −40 N/km gives k = 1.34; 0 gives 1; −100 gives 2.76; **−157 gives k → ∞**.
- **Modified refractivity** $M = N + 157\,h_\text{km}$ (P.453 eq. 17). There is a trapping layer where $dM/dh < 0$. The duct **strength** ΔM is the M-deficit (M-units) and the **thickness** is d (m).
- **Maximum trapped wavelength** (surface duct): $\lambda_\text{max} \approx 2.5\,d\sqrt{\Delta M\times10^{-6}}$.
- **Es one-hop MUF** = foEs sec $i$. The maximum obliquity at 110 km is sec $i$ = 5.45 at 0° take-off (2351 km). P.534 field strength: $E = E_0 + P + G_t - L_t - \Gamma$ with $E_0 = 104.8 - 20\log l$ dB(µV/m) for 1 kW and $l$ (km) the slant path. The attenuation is $\Gamma_\text{1 hop} = \dfrac{40}{1 + d/130 + (d/250)^2} + 0.2\left(\dfrac{d}{2600}\right)^2\left(\dfrac{f}{f_oEs}\right)^2 + e^{(d-1660)/280}$ dB.
- **Meteor (underdense) echo**: amplitude $\propto e^{-t/\tau}$ with $\tau = \lambda^2\sec^2\phi/(16\pi^2D)$. Here $D$ ≈ 1–10 m²/s is the ambipolar diffusion coefficient at 85–100 km and φ is the forward-scatter half-angle ($\phi$ = 0 for backscatter).
- **Aircraft (bistatic) scatter**: $P_r = P_tG_tG_r\lambda^2\sigma_b/((4\pi)^3R_1^2R_2^2)$ ([radar equation](../11-radar/radar-range-equation.md)). The maximum path is the sum of both stations' radio horizons to the aircraft altitude.
- **EME**: $P_r/P_t = G_tG_r\,\eta r^2\lambda^2/(64\pi^2d^4)$, with $r$ = 1.738 × 10⁶ m, $d$ = 3.844 × 10⁸ m (mean) and η = 0.065 [6].

### Level 2 — derivations
**The −157 N/km ducting threshold.** For a nearly horizontal ray in a spherically stratified medium, Snell's law $n r\cos\theta$ = const gives a ray curvature (relative to a straight line) of $1/\rho = -(1/n)(dn/dh)\cos\theta \approx -dn/dh$. The ray stays at constant height above the Earth when its curvature equals the Earth's, $1/a$, so $-dn/dh = 1/a$. In N-units, $dN/dh = -10^6/a = -10^6/6371$ km = **−157.0 N/km** (script §2). With gradients more negative than this the ray curves *more* than the Earth and returns to the surface: trapping. Mapping to a flat Earth, $n \to n + h/a$, gives the modified index $m = n + h/a$. Hence $M = N + 10^6h/a = N + 157h_\text{km}$, and the trapping condition becomes simply $dM/dh < 0$. Gradients between −40 and −157 N/km are **super-refraction**: extended horizons but no trapping. Positive gradients are **sub-refraction**: shortened horizons and "fading by Earth bulge".

**Which wavelengths a duct can trap.** In a surface duct with a linear M profile, a ray at elevation θ turns back at the height where $\theta^2 = 2\,(dm/dz)\,z_t$. The vertical wavenumber is $k_z = k\sqrt{\theta^2 - 2g'z}$, with $g' = \Delta M\cdot10^{-6}/d$. The lowest trapped mode must satisfy the transverse-resonance (WKB) condition, with phase π at the ground reflection and π/2 at the caustic:
$$2\int_0^{z_t}k_z\,dz = \frac{2}{3}\frac{k\theta^3}{g'} = \frac{3\pi}{2}.$$
For the mode to fit inside the duct we need $z_t \le d$, i.e. $\theta^2 \le 2g'd$. Eliminating θ gives
$$\lambda_\text{max} = \frac{16\sqrt2}{9}\,d\sqrt{\Delta M\times10^{-6}} = 2.51\,d\sqrt{\Delta M\times10^{-6}},$$
matching the classic coefficient ≈ 2.5 (script §3). Consequences:
- An evaporation duct (d = 10–25 m, ΔM = 10–25) has $f_\text{min}$ ≈ 3.8–0.95 GHz. It guides 2.4/5.8/10 GHz over water but **not 433/915 MHz** (a strong 25 m duct only just reaches 954 MHz).
- A 100 m surface-based inversion with ΔM = 20 has $f_\text{min}$ = 267 MHz, so it traps 433 and 915 MHz.
- 200–300 m elevated/subsidence ducts trap down to ~60–110 MHz (VHF FM and TV DX).

Antennas must also be *inside* the duct (or within a few duct thicknesses) to couple strongly.

**Ducted path loss.** Inside a duct the energy spreads in azimuth but not in height, so beyond a few duct-heights the loss grows ≈ 10 log d (cylindrical) instead of 20 log d. Modelling 915 MHz as free space to 50 km, then cylindrical, plus 10 dB of coupling and leakage loss, a 400 km ducted path costs ≈ 145 dB. A 1 W-class LoRa node at SF12 (22 dBm, 3 dBi antennas, −137 dBm sensitivity) then still has **≈ +20 dB margin** (script §4). Without the duct, the smooth-Earth diffraction loss at 400 km would add well over 100 dB. Hence real, if rare, multi-hundred-km UHF receptions in coastal climates.

**Meteor-trail echo duration and the best band.** A thin ("underdense") trail of line density $q < 10^{14}$ e/m scatters coherently while its radius $r_0$ is small compared with λ. Ambipolar diffusion broadens it as $r^2 = r_0^2 + 4Dt$, and the coherent amplitude falls as $\exp(-16\pi^2Dt/\lambda^2)$ for backscatter [7]. Forward scatter between two stations lengthens the effective wavelength by $\sec\phi$. With D = 2 m²/s and φ = 70° (a long path) the echo amplitude time constants are (script §6):

| 28 MHz | 50 MHz | 144 MHz | 222 MHz | 432 MHz |
|---|---|---|---|---|
| 3.1 s | 0.97 s | 0.12 s | 0.05 s | 0.013 s |

Duration scales as λ², so 6 m bursts last **8.3× longer** than 2 m bursts. The underdense reflected power also scales ≈ λ³, so 6 m is 14 dB stronger. Below ≈ 28 MHz, normal ionospheric modes and higher sky noise compete, and the trails are larger than needed. Hence 6 m is the meteor band, 2 m is workable with digital modes (MSK144, 15 s periods) and 70 cm is rare. "Overdense" trails ($q > 10^{14}$ e/m) behave like metallic cylinders and can last seconds even at 2 m. The geometric range limit, set by both stations seeing a 100 km trail at 0° elevation, is $2\sqrt{2a h}$ = **2258 km**.

**EME path loss.** The Moon is a radar target with cross-section $\sigma = \eta\pi r^2$ = 6.2 × 10¹¹ m². The radar equation with isotropic antennas, $P_r/P_t = \lambda^2\sigma/((4\pi)^3d^4)$, reduces to $\eta r^2\lambda^2/(64\pi^2d^4)$. The script reproduces the ARRL Handbook table to ≤ 0.1 dB from 50 MHz to 10 GHz (242.9 → 289.2 dB). The $d^4$ law makes perigee (356 500 km) 40 log(406 700/356 500) = **2.29 dB** better than apogee. The echo delay $2d/c$ is 2.4–2.7 s. The Moon's apparent rocking (libration) plus a rough surface gives Rayleigh-like **libration fading**: coherence times of seconds at 144 MHz and tenths of a second at 1296 MHz [6]. Doppler from the Earth's rotation reaches ≈ ±440 Hz at 144 MHz. Faraday rotation through the ionosphere twice (several turns at 144 MHz) can produce apparent one-way propagation for fixed linear polarisation.

### Level 3 — the ionospheric VHF modes in more detail
**Sporadic-E.**
- *Mechanism.* At mid-latitudes, wind shear in the lower thermosphere compresses long-lived metallic ions (Fe⁺, Mg⁺ of meteoric origin) into thin layers ~1–2 km thick at 95–120 km. foEs can exceed 20 MHz. At the magnetic equator a different, weaker "q-type" Es (equatorial electrojet irregularities) occurs almost daily. At high latitudes Es is tied to particle precipitation.
- *Statistics (ITU-R P.534-6).*
  - Mid-latitude occurrence peaks in **summer daytime** (P.534 gives summer 08–23 h curves as the most intense); a secondary winter maximum around the December solstice is often seen in the Northern Hemisphere.
  - The probability of exceeding a frequency follows the empirical Phillips rule, log p = a + b f.
  - Low-latitude statistics (|dip| < 20°) use separate curves.
- *Map values.* The P.1239 foEs maps (in the ITU data files; `prop2_ccir.py`) give, at R12 = 78:
  - Tokyo: noon median/upper-decile foEs 6.7/12.8 MHz in June vs 4.4/5.7 MHz in January.
  - Singapore: 5.1–5.4/6.9–8.0 MHz in every month, falling to 1.8–2.8/3.9–5.5 MHz at 20 LT (script §5).
- *What works.* Single-hop Es MUF ≈ foEs × 5.45 at the longest range: a Tokyo June upper decile gives ≈ 70 MHz (6 m open), whereas 2 m needs foEs ≥ 26 MHz. P.534 field strengths are high: ≈ 38 dB(µV/m) at 1500 km for 1 kW EIRP with f/foEs = 5 (Γ ≈ 3 dB). That is why Es is a major *interference* source for low-VHF broadcasting. Double-hop Es (2600–4000 km) has Γ(2 hop)(d) = 2.6 Γ(1 hop)(d/2).
- *Exam note.* The pool states Es is most likely "around the solstices, especially the summer solstice" and "between sunrise and sunset", consistent with these statistics.

**Auroral propagation.**
- *Mechanism.* Severe geomagnetic storms (high Kp; [space weather](solar-activity-and-space-weather.md)) expand the auroral oval equatorward. Precipitating particles create field-aligned E-region irregularities driven by the auroral electrojet.
- *What operators do.* Stations point their antennas roughly toward the magnetic pole, at the auroral curtain, and work each other via backscatter over ≈ 200–2000 km.
- *Why it sounds raspy and why CW.* The irregularities move at hundreds of m/s, which spreads the Doppler to ~0.1–1 kHz at 144 MHz. Voice becomes a rough hiss ("raspy"); CW, with its narrow, keyed carrier, survives best.
- *Bands.* 6 m and 2 m are common; 70 cm occurs in strong events. It requires geomagnetic latitudes ≳ 50–55°; Singapore (geomagnetic latitude −7.8°) never sees it.

**Transequatorial propagation (TEP)** [8]:
- **Afternoon TEP (aTEP), ≈ 15–19 LT.**
  - Mechanism: the signal reflects from one equatorial-anomaly crest to the other without touching the ground (a chordal "FF" mode with grazing incidence). It passes the D layer only twice.
  - Frequencies: MUF up to ~60 MHz, 15–25 MHz above the 2F MUF.
  - Signals: strong and fairly clean.
  - Paths: 5000–6500 km.
- **Evening TEP (eTEP), ≈ 20–23 LT.**
  - Mechanism: guiding by field-aligned plasma bubbles (equatorial spread-F).
  - Frequencies: 144 MHz, rarely 432 MHz.
  - Signals: deep rapid fading and Doppler spread up to ~2 kHz, so CW only.
  - Paths: 3000–8000 km.
- **Conditions for both.**
  - Stations roughly **symmetric about the dip equator**, typically at or beyond the anomaly crests (±15–25° dip latitude).
  - Paths within ~15° of geomagnetic north–south.
  - Equinoxes.
  - High solar activity.
- **Geometry check (IGRF dip latitudes at 300 km; script §9).**
  - Okinawa (+21.7°)–Darwin (−22.5°): 4313 km. This is the classic Japan–Australia TEP.
  - Tokyo (+30.8°)–Townsville (−29.7°): 6155 km.
  - Singapore (−6.5°) lies *between* the dip equator (≈ 6.7° N at 104° E) and the southern crest. It is not a classic TEP endpoint, but it sits under the bubble-generating zone. That makes it ideal for observing evening spread-F, scintillation and equatorial scatter.
- **Exam note.** The pool's numbers ("2000–3000 miles" separation, "≈ 5000 miles" maximum) understate the measured 3000–8000 km range a little. The physics and timing ("afternoon or early evening") agree.

**Aircraft scatter.** An airliner at 11 km is within the radio horizon of stations up to $2 \times 4.12\sqrt{11\,000}$ ≈ **864 km** apart (script §7). The bistatic return with σ ≈ 100 m², 100 W and 14 dBi antennas at both ends is ≈ −148 dBm at 300 + 300 km. That is weak but decodable with narrowband digital modes. Forward-scatter cross-sections near the baseline can be 10–30 dB larger. The Doppler shift sweeps by up to ~240 Hz at 144 MHz as the aircraft crosses.

## Design equations & rules of thumb

| Quantity | Formula / value | Notes |
|---|---|---|
| Radio vs geometric horizon | ×√(4/3) = 1.15 | standard atmosphere, −40 N/km |
| Ducting threshold | dN/dh ≤ −157 N/km ⇔ dM/dh < 0 | M = N + 157 h(km) |
| Super-refraction | −157 < dN/dh < −40 N/km | extended horizon, no trapping |
| Trapped wavelength | λ_max ≈ 2.5 d √(ΔM·10⁻⁶) | 15 m evaporation duct → ≥ 2 GHz |
| Typical duct reach | 160–500 km (100–300 mi), > 1000 km over sea | inversions, subsidence, monsoon/sea breeze |
| Ducted loss | ≈ FSPL(d₀) + 10 log(d/d₀) + coupling | cylindrical spreading |
| Es MUF (one hop) | foEs × ≤ 5.45 | 6 m when foEs ≥ 9.2 MHz; 2 m when ≥ 26 MHz |
| Es range | ≤ 2350 km (one hop), 4000 km (two hops) | summer solstice, daytime |
| Meteor range | ≤ 2250 km | 6 m best; τ ∝ λ² |
| Aircraft-scatter range | ≤ 2 × 4.12√h | 864 km at 11 km altitude |
| EME loss | 252.1 / 261.6 / 271.2 dB at 144 / 432 / 1296 MHz | perigee −1.1 dB, apogee +1.1 dB |
| TEP | 3000–8000 km, 15–23 LT, equinox, solar max | symmetric about the dip equator |

## Worked examples
**1 — "My 915 MHz Meshtastic node heard a station 400 km away this morning."**
- *Check the internet first.* MQTT/internet bridging makes far-away nodes appear in your list without any RF path. Look at the hop count and the "via MQTT" flag ([LoRaWAN vs raw LoRa](../15-lora-ism-radios/lorawan-vs-raw-lora.md)).
- *If it was RF:* 400 km is far beyond the 2 × ~10 km radio horizon of two low antennas. Diffraction loss would add > 100 dB, so only a duct explains it.
- *Which duct?* A sea-surface evaporation duct cannot trap 915 MHz unless it is unusually strong (≥ 25 m). A morning **surface-based inversion** or marine layer ~100 m thick with ΔM ≈ 20 traps everything above ≈ 270 MHz.
- *Does the budget close?* With cylindrical spreading, the ducted loss is ≈ 145 dB, and a +22 dBm SF12 node keeps ≈ 20 dB margin (script §4).
- *Consequence.* The same duct can make your 915 MHz ground station hear unwanted transmitters (interference, raised noise floor) or push your own transmissions into someone else's band plan region.

**2 — Would a duct affect the rocket downlink?** Rarely, and mostly near the ground. The rocket at kilometres altitude is above surface ducts, and steep rays (elevation > a few degrees) are not trapped by gradients of −157 N/km (trapping needs θ ≲ √(2ΔM·10⁻⁶) ≈ 0.4°). Effects appear in the final descent and the landed phase. There, an inversion can either extend range (good for recovery) or produce deep slow fades on an otherwise clear LOS path. Budget the fade margin as in [link margin](link-margin-availability.md) rather than relying on ducts.

**3 — Planning a 6 m sporadic-E contact from Tokyo in June.** Upper-decile noon foEs is 12.8 MHz (P.1239 map). The one-hop Es MUF at 2000 km is ≈ 12.8 × 5.3 ≈ 68 MHz, so 50 MHz is open on ≈ 10 % of days around noon. At 1500 km with foEs 10 MHz, f/foEs = 5 gives Γ = 3 dB and E ≈ 38 dB(µV/m) per kW EIRP (P.534). For 100 W into a 10 dBi Yagi (1 kW EIRP), that is a very strong signal.

**4 — Meteor scatter on 2 m vs 6 m.** With D = 2 m²/s on a 1500 km path (φ ≈ 70°), a typical underdense ping lasts ≈ 0.12 s at 144 MHz and ≈ 1 s at 50 MHz, and is ≈ 14 dB stronger on 6 m. MSK144 sends a 72 ms frame repeatedly, so even 2 m pings decode. During the Geminids (peak ~13–14 Dec) the ping rate rises several-fold.

**5 — EME link budget at 144 MHz.**
- *Stations:* each has 4 × 14 dBi Yagis (≈ 20 dBi array) and 500 W (57 dBm).
- *Received power:* 57 + 20 + 20 − 252.1 = **−155.1 dBm** at mean distance; perigee adds +1.1 dB.
- *Noise:* the system noise temperature is ~200 K (sky ~180 K away from the galactic plane, plus receiver). The noise in 2500 Hz is −174 + 10 log(200/290) + 34 = −141.6 dBm.
- *SNR:* ≈ **−13.5 dB in 2.5 kHz**. That is fine for JT65/Q65 (thresholds −25 to −28 dB) and marginal for CW by ear (≈ 0 dB in ~50 Hz ⇒ −17 dB in 2.5 kHz).
- *Echo:* the delay is 2.56 s, and own-echo Doppler at moonrise reaches ≈ +440 Hz.

**6 — Can a Singapore station work TEP into Australia?** Not by the classic geometry. Singapore (−6.5°) and Darwin (−22.5°) are on the same side of the dip equator. The symmetric partner for Darwin is around Okinawa or Taiwan (+20°), and for Singapore (−6.5°) around +6.5°, a short ~1500 km path that needs no TEP. Singapore stations do see evening **equatorial spread-F scatter** and strong scintillation of VHF/UHF satellite signals, the same plasma-bubble physics that drives eTEP.

## Practical notes
- **Ducting forecasts:** tropospheric ducting maps (e.g. the Hepburn tropo index), radiosonde soundings (Singapore Changi launches twice daily) and ITU-R P.453 statistics give the climatology. P.453 maps the percentage of time that $dN/dh \le -100$ N/km in the lowest 100 m. This is highest over warm seas, e.g. the Persian Gulf, Red Sea and Bay of Bengal in season; SE Asia is moderate. Inversions are common:
  - in the early morning, after clear nights;
  - in sea-breeze and monsoon transition periods;
  - under stationary high pressure.
- **Interference management at 433/915 MHz:**
  - Ducting can raise the noise floor with distant transmitters, so log RSSI of empty channels over days.
  - Use listen-before-talk / CAD in LoRa.
  - Pick channels with the least ducted interference ([ground station design](../15-lora-ism-radios/ground-station-design.md)).
- **Polarisation conventions:**
  - VHF/UHF weak-signal operators (SSB/CW, Es, meteor, tropo) use **horizontal polarisation**. Partly this is convention: the cross-polar loss between H and V is 20 dB or more on LOS paths ([polarisation](polarization-mismatch-loss.md)). Horizontal Yagis are also easy to stack and rotate, and man-made noise is predominantly vertically polarised.
  - FM, repeater and mobile work uses vertical polarisation.
  - EME at ≥ 1296 MHz and satellites use circular polarisation (Faraday rotation and the moon's sense reversal).
- **Operating modes:** WSJT-X modes are designed for these channels:
  - MSK144 for meteor scatter;
  - FT8/FT4 for Es and tropo;
  - Q65 and JT65 for EME;
  - FST4/WSPR for weak beacons.
  
  CW remains best for aurora and eTEP.
- **Range-test sanity:** before claiming an RF "record", check:
  - time of day and weather (inversions);
  - whether the path is over water;
  - Es season (summer daytime);
  - meteor-shower dates;
  - MQTT bridging.

## Common mistakes & misconceptions
- **"Ducting happens only over the sea."** Evaporation ducts are over water, but inversions over land (nocturnal cooling, subsidence) duct VHF/UHF too. Conversely, the sea's evaporation duct traps only microwaves.
- **"A duct makes any frequency travel far."** Only wavelengths below ≈ 2.5 d √(ΔM·10⁻⁶) are trapped, and only when the antennas are in or near the duct.
- **"Sporadic-E is an F-layer effect."** It is thin E-region ionisation at 95–120 km, so the hop range is ≤ ≈ 2300 km, much shorter than F2's 4000 km.
- **"Meteor scatter works better at higher VHF because there is less noise."** Trail echoes are much shorter (∝ λ²) and weaker (∝ λ³) at higher frequencies: 6 m is the sweet spot.
- **"Aurora sounds raspy because of weak signals."** It is Doppler spreading by moving irregularities; even strong auroral signals sound rough.
- **"TEP works between any two stations either side of the equator."** It needs near-symmetry about the *dip* equator, a roughly N–S path, afternoon or evening local time, the equinox season and high solar activity.
- **"EME loss is ~250 dB, so it needs megawatts."** With 20 dBi arrays at both ends and digital modes, a few hundred watts suffice at 144 MHz. The large free-space loss is offset by gain² and by narrow bandwidths.
- **"The radio horizon equals the visual horizon."** It is ≈ 15 % farther (k = 4/3), and it varies with weather: k ≈ 1 to ∞ in ducts.

## How to simulate / verify
- `tools/verify/prop2_vhf_anomalous.py` (ALL PASS; output `prop2_vhf_anomalous_output.txt`) covers:
  - P.453 refractivity and k-factors;
  - the −157 N/km derivation;
  - λ_max via the WKB phase integral (coefficient 2.514);
  - trapped-frequency tables;
  - the ducted LoRa margin;
  - Es geometry, the P.534 Γ and field strength, and P.1239 foEs map values for Singapore and Tokyo (via `prop2_ccir.py`);
  - meteor decay times, the λ³ ratio and the range limit;
  - aircraft-scatter horizon, bistatic budget and Doppler;
  - EME loss vs the ARRL table (≤ 0.1 dB), perigee/apogee, delay and Doppler;
  - TEP endpoint dip latitudes from IGRF-14.
- For site-specific duct analysis use a parabolic-equation propagation model (e.g. open-source PE codes or AREPS-like tools) with radiosonde M-profiles.
- For a trans-horizon *interference* climatology use ITU-R P.452 (ducting/layer reflection mechanisms).
- [Empirical path-loss models](empirical-path-loss-models.md) lists P.452/P.1812 scopes.

## Open questions / gaps
- No Singapore-specific duct-occurrence statistics: the P.453 digital duct maps are in the >137 MB supplement, which was not downloaded.
- The D values (1–10 m²/s) for meteor-trail diffusion and the λ³ underdense power law come from standard meteor-physics knowledge with one peer-reviewed confirmation of the decay law [7]. They were not re-derived from first principles.
- P.534 eq. (5) (path length) is ambiguous in the extracted layout. The script uses the geometric two-leg length; the difference from the alternative reading is < 1 dB in E₀.
- Auroral Doppler spread and range figures are typical values from operating literature, not from a primary measurement paper.

## Sources
1. ITU-R Recommendation P.453-14 (08/2019), *The radio refractive index: its formula and refractivity data* — eqs 1–10 (N), exponential profile N0 = 315, h0 = 7.35 km, gradient statistics, M = N + 157h (eq. 17), duct types and parameters. https://www.itu.int/rec/R-REC-P.453/en (standard)
2. ITU-R Recommendation P.534-6 (09/2021), *Method for calculating sporadic-E field strength* — eqs 1–5, Phillips rule, seasonal/diurnal statistics, low-latitude curves. https://www.itu.int/rec/R-REC-P.534/en (standard)
3. ITU-R Recommendation P.1239-4 (08/2023) and the ITU-R SG3 P.533 data files (foEs median/decile maps). https://github.com/ITU-R-Study-Group-3/ITU-R-HF (standard / reference data)
4. M. P. M. Hall, *Effects of the Troposphere on Radio Communication*, Peter Peregrinus 1979, and M. P. M. Hall, L. W. Barclay, M. T. Hewitt (eds.), *Propagation of Radiowaves*, IEE 1996 — refractivity, ducts, trapping. (textbooks) *cited from standard knowledge, not re-read*
5. J. D. Turton, D. A. Bennetts, S. F. G. Farmer, "An introduction to radio ducting," *Meteorological Magazine* 117, 245–254 (1988) — λ_max ≈ 2.5 d √(ΔM·10⁻⁶) form (re-derived here). (peer-reviewed) *cited from standard knowledge; coefficient independently derived*
6. J. Taylor (K1JT), "EME (Earth–Moon–Earth) communication," *ARRL Handbook* 2010, ch. 30 §30.9 — path-loss formula and table (η = 0.065), ±1.1 dB distance variation, echo delay, libration fading, Doppler, Faraday rotation. https://wsjt.sourceforge.io/Hbk_2010_Ch30_EME.pdf (handbook chapter)
7. Underdense meteor echo decay $A(t) = A_0\exp(-16\pi^2D_at/\lambda^2)$ — "Improved method of estimating temperatures at meteor peak heights," *Atmos. Meas. Tech.* 14, 4157 (2021). https://amt.copernicus.org/articles/14/4157/2021/ (peer-reviewed); D. W. R. McKinley, *Meteor Science and Engineering*, McGraw-Hill 1961 (textbook, *standard knowledge*).
8. Australian Bureau of Meteorology Space Weather Services, *Transequatorial Radio Propagation* — aTEP/eTEP characteristics, timing, frequencies, path lengths and diagnostics; and R. W. Heron, L. F. McNamara (Heron & McNamara 1979, *Radio Science*), "Transequatorial VHF propagation through equatorial plasma bubbles". https://www.sws.bom.gov.au/Educational/5/2/3 (government educational note; peer-reviewed paper cited via it)
9. ITU-R Recommendation P.452 (current) — interference prediction including ducting and layer reflection. https://www.itu.int/rec/R-REC-P.452/en (standard — scope only)
10. WSJT-X User Guide (K1JT et al.) — MSK144, FT8, Q65/JT65 modes and thresholds. https://wsjt.sourceforge.io/ (software documentation)
11. ARRL, *The ARRL Handbook* / *ARRL Antenna Book*, VHF/UHF propagation chapters — Es, aurora, meteor scatter and tropo operating practice. (handbook) *cited from standard knowledge*
12. `tools/verify/prop2_vhf_anomalous.py`, `tools/verify/prop2_ccir.py`, `tools/verify/prop2_igrf.py` (this KB).
