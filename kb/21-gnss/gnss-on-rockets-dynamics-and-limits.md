---
title: GNSS on rockets — export/COCOM limits and how u-blox implements them, dynamic models, tracking loss under boost (acceleration, jerk, oscillator g-sensitivity), antennas, roll and re-acquisition
domain: 21-gnss
slug: gnss-on-rockets-dynamics-and-limits
tags: [gnss, rocket, cocom, export-control, ear-7a105, mtcr, itar, 500-m-s, 600-m-s, 18-km, 50-km, 80-km, u-blox, dynamic-model, airborne-4g, jerk, doppler-rate, pll, fll, cycle-slip, g-sensitivity, tcxo, vibration, phase-wind-up, roll, nose-cone, tip-antenna, blade-antenna, reacquisition, sounding-rocket, dlr, zed-f9p, max-m10s]
prerequisites: [gnss-receiver-architecture-acquisition-tracking.md, gnss-signals-and-codes.md, ../08-antennas/gnss-antennas.md]
related: [gnss-receiver-integration-u-blox.md, gnss-interference-jamming-spoofing.md, rtk-ppp-and-corrections.md, ttff-agps-almanac-ephemeris.md, gnss-timing-1pps.md, gnss-error-sources-dop.md, ../18-components-parts/rf-modules.md, ../08-antennas/antennas-on-rockets.md, ../15-lora-ism-radios/rocket-telemetry-radio-design.md, ../10-comms-modulation/synchronization-carrier-timing.md]
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# GNSS on rockets — dynamics, export limits and practical limits

## Questions this page answers
- Will my u-blox GNSS stop working above 500 m/s, 18 km, 50 km or 80 km? Is it "speed AND altitude" or "speed OR altitude"?
- What do the export rules (COCOM, EAR 7A105, MTCR, ITAR) actually say today?
- Which u-blox dynamic platform model should a rocket use, and what does "Airborne <4g" really limit?
- Why do GNSS receivers lose lock during motor boost and regain it after burnout?
- How much acceleration and jerk can a tracking loop take? Is it the acceleration or the jerk that kills it?
- Does the receiver's crystal oscillator care about 15 g?
- Where should the GNSS antenna go on a rocket, and what happens when the rocket rolls or hangs under a parachute?
- How quickly does the receiver re-acquire after losing lock, and how do I make that faster?
- What have amateur and professional rocket flights actually observed?

## TL;DR
- **Three independent limits** stop GNSS on a rocket: (1) **firmware operational limits** — u-blox: velocity 500 m/s, altitude 80 km (50 km on older firmware), "dynamics ≤ 4 g", all "assuming Airborne 4 g platform" [1–5]; (2) the **navigation-filter dynamic model** (sanity checks: Portable invalidates fixes above 12 km altitude and 310/50 m/s horizontal/vertical speed; Airborne models check altitude only) [3][4]; (3) **tracking-loop physics** — jerk at ignition/burnout, oscillator g-sensitivity, vibration, roll and antenna pattern.
- **AND vs OR**: no primary u-blox document states the logic; datasheets list the limits separately. The only u-blox staff statement found (u-blox 7, 2016) says the module will not output data above 500 m/s regardless of altitude [7]; a vendor blog claims AND (1000 kn above 18 km) [8]. **Design for a speed-only 500 m/s cut-off at any altitude**, plus 80 km (F9P HPG ≥ 1.13, M10) or 50 km (F9P HPG 1.00–1.12, M8, u-blox 7) [1][2][5][9].
- **The law today** (US): EAR ECCN **7A105.b.1** controls GNSS receivers "designed or modified for airborne applications" capable of navigation information above **600 m/s** (MTCR item 11.A.3); military receivers are USML XII(d) [6]. The famous "1000 knots / 60 000 ft" CoCom figures are historical; manufacturers keep a margin (u-blox 500 m/s). Buying and flying a COTS receiver is fine; modifying firmware to remove limits creates a controlled item — don't.
- **Tracking physics** (3rd-order PLL, `tools/verify/gnss_tracking_loops.py`): constant acceleration costs nothing in steady state; **jerk** costs $\theta_e = 360 J/(\lambda\omega_0^3)$ — 26.5° per 10 g/s at B_n = 15 Hz. A typical motor ignition (0 → 10–15 g in 0.05–0.2 s, i.e. 50–300 g/s) makes a 10–15 Hz PLL slip cycles; a 25 Hz PLL survives 15 g in 0.2 s; an **FLL-assisted** loop keeps frequency lock in every simulated case, with a few half-cycle slips. So expect **carrier-phase/RTK loss and possibly short fix gaps at ignition and burnout, recovery within seconds**.
- **Oscillator**: a TCXO's acceleration sensitivity (≈ 0.5–2 ppb/g, assumed typical) shifts L1 by 12–47 Hz at 15 g — a common-mode frequency step that looks like dynamics; DLR measured ≈ 100 Hz of L1 offset during an 18 g boost and blamed the reference oscillator for 90 m RMS position errors during thrust [10].
- **Professional evidence**: DLR's sounding-rocket receivers track through 18 g boosts and 4 Hz spin with aiding [10]; on MAPHEUS-15 (2024, apogee 309 km) commercial Septentrio receivers lost almost all signals leaving the launch tower but had a solution again within 4.5 s, while an L1-only NovAtel never reacquired [11].
- **Amateur reports (anecdotal)**: GPS commonly loses lock during boost and regains it within a couple of seconds of burnout; one tracker vendor reports ≈ 90 % lock retention below 10 g and ≈ 90 % loss above 20 g; u-blox modules shut off above 50 km and resumed below it on a 61 km flight [8][12].
- **Antenna placement dominates in practice**: nose-tip helix (best during ascent), never behind carbon fibre, side-mounted patches/blades combined for roll; under the chute the antenna may point sideways — DOP roughly doubles with a 90° tilt (`gnss_dop_errors.py`).

## Intuition (no math)
A GNSS receiver keeps a "mental model" of every satellite signal and nudges it a thousand times a second. Steady motion — even very fast motion — is easy: the model simply includes the speed. Steady acceleration is also fine for a third-order loop: it learns the acceleration. What hurts is a *change* of acceleration (jerk) faster than the loop can learn, like the motor lighting (0 to 15 g in a tenth of a second) or burning out. During that instant the loop's model is wrong by more than a quarter of a wavelength (5 cm at L1), the phase lock slips, and the receiver falls back to coarser frequency tracking or loses the satellite and searches again.

Separately, the receiver's navigation software has rules about what is believable for the platform you told it about ("Portable", "Automotive", "Airborne <4g"), and the firmware has built-in export-control limits. Those rules don't care about signal quality: exceed 500 m/s and a u-blox stops giving you fixes even with perfect signals.

Finally the rocket itself fights the antenna: carbon fibre is opaque, the nose cone detunes a patch, the vehicle rolls (changing the pattern and the phase of circularly polarized signals), and after apogee the antenna may point at the ground.

## The math

### Level 1 — the numbers a rocket produces
L1 wavelength λ = c/1575.42 MHz = 0.1903 m. For a line-of-sight (LOS) component $v_{LOS} = v\sin E$ (vertical flight, satellite at elevation $E$):

| Quantity | Formula | 10k-ft class (≈ 300 m/s, 10 g) | 30k-ft class (≈ 600 m/s, 12–15 g) |
|---|---|---|---|
| Doppler | $v_{LOS}/\lambda$ | 1.6 kHz | 3.2 kHz |
| Doppler rate | $a_{LOS}/\lambda$ | 515 Hz/s | 620–770 Hz/s |
| Jerk at ignition | $\Delta a/t_{rise}$ | 10 g / 0.1 s = 100 g/s | 15 g / 0.1 s = 150 g/s |
| u-blox 500 m/s limit | — | inside | exceeded for several seconds |
| u-blox "≤ 4 g" spec | — | exceeded during boost | exceeded |

(Doppler numbers are for a zenith satellite; profiles are illustrative, not a Space Bar trajectory.) The receiver's static search window (±5 kHz satellite Doppler) covers the rocket's Doppler — the problem is the *rates*.

### Level 1½ — hertz per m/s and degrees per g, algebra only
- **Doppler per unit speed.** At L1, λ = 0.1903 m. Each 1 m/s of line-of-sight speed is 5.26 Hz of Doppler, and each 1 g of line-of-sight acceleration is 51.5 Hz/s of Doppler rate.
- **A loop lags behind acceleration.** A 2nd-order PLL follows a steady acceleration a with a constant phase lag $\theta = 360\,a/(\lambda\omega_0^2)$ degrees, where $\omega_0 = B_n/0.53$. The lag grows in proportion to a and falls with the square of the loop bandwidth.
- **The lock budget.** Kaplan's rule allows 45° for the 3σ noise jitter plus this lag together ([receiver page](gnss-receiver-architecture-acquisition-tracking.md#level-2--acquisition-statistics-loop-noise-the-navigation-equations)).

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`).* 500 m/s along the line of sight is **2.63 kHz**, well inside the ±5 kHz search. With B_n = 15 Hz (ω₀ = 28.3 rad/s), a steady 10 g gives a lag of **232°**, so the loop loses lock. Even with no noise at all, the 45° budget allows only **≈ 1.9 g**. That is why rockets need 3rd-order or FLL-assisted loops (Level 2).

### Level 2 — tracking-loop stress, oscillators, vibration, roll
**Loop stress** ([derivation on the receiver page](gnss-receiver-architecture-acquisition-tracking.md#level-2--acquisition-statistics-loop-noise-the-navigation-equations)): a 2nd-order PLL's steady error to acceleration is $\theta = \frac{360}{\lambda}\frac{a}{\omega_0^2}$, $\omega_0 = B_n/0.53$ → 93° at 4 g and 347° at 15 g for B_n = 15 Hz — hopeless. A 3rd-order PLL ($\omega_0 = B_n/0.7845$) has zero steady error to constant acceleration and
$$\theta_{e}[\deg] = \frac{360\,J}{\lambda\,\omega_0^3}$$
to a constant jerk $J$ (m/s³): 89.6°, 26.5°, 5.7° per 10 g/s at B_n = 10, 15, 25 Hz. Keeping $\theta_e$ ≤ 15° (a third of the 45° Costas budget) allows only **5.7 g/s at 15 Hz and 26 g/s at 25 Hz** (script). Motor ignition is 10–30× worse, but lasts only $t_{rise}$ — so the outcome depends on the loop's transient response, which the script simulates:

| Net accel. | Rise time | B_n = 10 Hz | 15 Hz | 25 Hz | FLL(10 Hz)-assisted, 15 Hz PLL |
|---|---|---|---|---|---|
| 5 g | 0.5 s | slips | slips at burnout | **holds** | holds frequency, ≤ 1 half-cycle slip |
| 10 g | 0.2 s | slips | slips | **holds** | holds, ≤ 1 slip |
| 15 g | 0.2 s | slips | slips | **holds** (peak 64°) | holds |
| 15 g | 0.05 s | slips | slips | slips | holds |
| 20 g | 0.2 s | slips | slips | slips | holds, ≤ 2 slips |

(3rd-order Costas PLL, T = 1 ms, C/N₀ = 40 dB-Hz, satellite at 60° elevation, burnout ramp to −1.3 g in 0.2 s; "slips" = pure PLL lost lock and did not recover without help.) Interpretation: **a well-designed receiver keeps frequency lock (Doppler, code, position) through boost but its carrier phase slips** — fatal for RTK/carrier-phase, tolerable for a standard fix. The FLL, with 1/(4T) = 250 Hz of pull-in range, tolerates ≈ 580 g/s of jerk at B_n = 10 Hz (script). Real receivers' loop parameters are proprietary; DLR's Septentrio settings for MAPHEUS-15 were PLL ≈ 15–17 Hz with 1–2 ms coherent integration and DLL 0.1–0.25 Hz (my reading of their Table 1) [11].

**Oscillator acceleration sensitivity.** A quartz resonator's frequency shifts by $\Delta f/f = \boldsymbol\Gamma\cdot\mathbf a$ ($\Gamma$ in parts per g, direction-dependent). At L1: $\Delta f = \Gamma\, a\, f_{L1}$ = 23.6 Hz for 1 ppb/g at 15 g (0.5–2 ppb/g → 12–47 Hz). Because every channel sees it, it is a *common-mode* frequency step at ignition — an extra "jerk" the loops must absorb even for satellites at the horizon. The DLR Orion receiver on Test Maxus-4 (18 g boost) showed large frequency spikes at ignition and a ≈ 100 Hz L1 offset during thrust, and position differences vs a reference receiver of 90 m RMS in the boost phase (1.5 m in free flight), attributed to the oscillator [10]. Mitigations: low-g-sensitivity TCXO/OCXO (SC-cut), orientation of the crystal's least-sensitive axis along thrust, mechanical isolation, and IMU-aided tracking.

*IMU-aided (tightly/deeply coupled) GNSS/INS architectures are outlined on the [Kalman filtering page](../00-math-foundations/kalman-filter-and-state-estimation.md).*

**Vibration.** Random vibration of PSD $P(f_m)$ (g²/Hz) modulates the oscillator, giving phase jitter $\sigma_v = \frac{360 f_L}{2\pi}\sqrt{\int \Gamma^2 P(f_m)/f_m^2\,df_m}$ deg [13]. With a NASA-GEVS-like 14.1 g_rms qualification profile and Γ = 1 ppb/g: **≈ 6.4° rms** — a noticeable bite out of the 15° (1σ) PLL budget (script). Motor-induced vibration of solid motors is of this order or larger.

**Roll and phase wind-up.** For circular polarization, rotating the antenna about its boresight by ψ rotates the carrier phase by ψ: a roll rate $\Omega$ (rev/s) adds an apparent frequency offset of ≈ Ω Hz (exactly for a satellite on boresight; geometry-dependent otherwise), common to all satellites. MAPHEUS-15 rolled at up to 2000°/s = 5.6 rev/s → ≈ 5.6 Hz [11] — small compared with Doppler, but it corrupts carrier-phase velocity and RTK unless modelled. More damaging is **pattern modulation**: side-mounted antennas sweep their pattern past each satellite once per revolution, producing C/N₀ fades at the roll frequency; two antennas combined around the airframe create interference lobes (DLR: lobes 30–60° apart for elements ≈ 2λ apart) [10].

### Level 3 — export controls and how u-blox implements limits
**Regulation (US, which drives global COTS behaviour)** [6]:
- **EAR ECCN 7A105**: receiving equipment for navigation satellite systems (a) designed or modified for use in missiles, or (b) designed or modified for airborne applications and (b.1) capable of providing navigation information at speeds > **600 m/s**, (b.2) employing military decryption, or (b.3) specially designed anti-jam features. This implements **MTCR Annex item 11.A.3**.
- **USML Category XII(d)(2)**: military GNSS receivers (MT-controlled if airborne and > 600 m/s); (iv) receivers specially designed for rockets/missiles/UAVs capable of ≥ 500 kg to ≥ 300 km.
- **ECCN 7A994**: typical commercial GPS (no decryption, no adaptive antenna). Spaceborne receivers: 9A515.x.
- The **"1000 knots and/or 60 000 ft (18 km)"** CoCom wording is the historical origin of manufacturer limits (1000 kn = 514 m/s). The current controls are speed-based (600 m/s) without an altitude criterion.

**u-blox implementation — what the primary documents say** (per firmware):

| Product / firmware | Velocity | Altitude | Dynamics | Source |
|---|---|---|---|---|
| u-blox 7 | 500 m/s | 50 000 m | ≤ 4 g | [7] (staff answer quoting datasheet) |
| u-blox M8 (protocol 15–23) | 500 m/s (datasheets) | 50 000 m; Airborne models: 50 000 m, horiz. 100/250/500 m/s, **vertical 100 m/s**, altitude-only sanity check | ≤ 4 g | [9] |
| ZED-F9P-00B (HPG 1.00), -01B (HPG 1.12) | 500 m/s | **50 000 m** | ≤ 4 g | [5] |
| ZED-F9P-02B (HPG 1.13), -04B (HPG 1.32) | 500 m/s | **80 000 m** | ≤ 4 g | [1][5] |
| MAX-M10S (SPG 5.10) | 500 m/s | **80 000 m** ("maximum altitude limit increased to 80 000 m" vs M8) | ≤ 4 g | [2][4] |
| F9/M10 Airborne <1g / <2g / <4g model tables | horiz. 100 / 250 / 500 m/s, vert. 6400 / 10 000 / 20 000 m/s | 80 000 m | — | [3][4] |

All datasheet limits carry the footnote "Assuming Airborne 4 g platform" [1][2][5]. The dynamic-model tables state that if a sanity check fails "the position solution becomes invalid", and that Airborne models apply an **altitude** sanity check only [3][4]. **No u-blox document states whether the velocity and altitude limits combine with AND or OR.** The one u-blox staff answer found (2016, u-blox 7): the module will not output data above 500 m/s regardless of altitude [7]. Contradicting it, BigRedBee writes that u-blox "MAX" modules implement CoCom correctly as an AND (1000 knots above 18 km), shutting down abruptly when both are exceeded and resuming below [8] — anecdotal vendor experience, and not consistent with "500 m/s at any altitude". Community users report that outputs stop above 500 m/s on the M10S [12]. **Engineering conclusion:** assume no valid fix whenever |v| > 500 m/s at any altitude, and above 80 km (50 km on older firmware); verify on your firmware with a cabled GNSS simulator before relying on anything else. (Also cross-referenced in [RF modules](../18-components-parts/rf-modules.md).)

Separately, "≤ 4 g" is an operational specification, not a documented hard cut-off; flights show tracking through higher accelerations with gaps ([amateur and professional reports](#practical-notes)). A forum answer attributes a "~4 g implicit limit" to correlator dwell time — unverified [12].

Note also that DLR could not publish raw MAPHEUS-15 GNSS data because of "legal restrictions imposed by the use of GNSS on sounding rockets flying faster than 600 m/s" [11] — the controls bite researchers, not just manufacturers.

## Design equations & rules of thumb

| Item | Value / rule | Source |
|---|---|---|
| u-blox fix cut-off | > 500 m/s (assume any altitude); > 80 km (F9P HPG ≥ 1.13, M10) / 50 km (older) | [1–5][7] |
| Dynamic model for flight | **Airborne <4g** (CFG-NAVSPG-DYNMODEL = 8) | [3][4] |
| Portable model limits | 12 km, 310 m/s horiz., 50 m/s vert. (fix invalidated) | [3][4] |
| 2nd-order PLL accel. error | 93° at 4 g (B_n 15 Hz) → avoid | script |
| 3rd-order PLL jerk error | 26.5°/(10 g/s) at 15 Hz; 5.7°/(10 g/s) at 25 Hz | script |
| Oscillator g-shift at L1 | Γ·a·1575 MHz ≈ 24 Hz at 15 g for 1 ppb/g | derivation |
| Vibration jitter | ≈ 6° rms for 14 g_rms, 1 ppb/g | script |
| Phase wind-up | ≈ roll rate (rev/s) in Hz | derivation |
| Expect | PLL slips at ignition/burnout; FLL holds; fix gaps ~0–5 s; RTK → float | sim + [10][11] |

## Worked examples
**1 — A 10 000 ft (3 km) competition rocket, MAX-M10S secondary FC.** Assume net 10 g for 2.5 s (rise 0.1 s) → ≈ 245 m/s at burnout, apogee ≈ 3 km. Velocity and altitude are inside the u-blox envelope. Ignition jerk 100 g/s × sin 60° ≈ 87 g/s LOS → a 15 Hz PLL slips; the receiver will likely keep frequency lock or briefly lose some satellites. Plan: Airborne <4g model, all three default constellations at the default rate (3 Hz with B1I — or GPS+GAL at 10 Hz if rate matters more), hot start on the pad (keep powered), fuse IMU + baro for boost, treat GNSS as a coast/descent sensor.

**2 — A 30 000 ft (9 km) rocket reaching 600 m/s.** With burnout at 600 m/s and ≈ 2 g of combined drag and gravity deceleration after burnout, the vehicle stays above 500 m/s for roughly (600 − 500)/(2 × 9.81) ≈ 5 s after burnout plus the end of the burn. Expect **no valid u-blox fix for ≈ 5–8 s**, independent of signal quality, then normal fixes resume (if the antenna still sees the sky). Plan your state estimator and telemetry for a GNSS gap; log `UBX-NAV-PVT` flags (`gnssFixOK`, `fixType`) and `RXM-RAWX` to document what your firmware actually does — and report it (faithful reporting).

**3 — RTK on the ZED-F9P during boost.** A carrier-phase slip on most satellites at ignition forces the RTK engine to float; with good signals and corrections the F9P datasheet quotes RTK convergence < 10 s (multi-GNSS) [1], but at 300–600 m/s with an L1-only antenna and a few slips per satellite, cm-level fixes during the powered phase are unrealistic. Use RTK for pad survey, coast-to-apogee (if the antenna is good) and landing position — [RTK page](rtk-ppp-and-corrections.md).

**4 — How big is the oscillator term for the Avionics-B ZED-F9P?** Its TCXO g-sensitivity isn't published. Assuming 1 ppb/g along the thrust axis and 12 g boost: 18.9 Hz at L1 appearing over the 0.1 s rise → 189 Hz/s, i.e. as large as a 3.7 g line-of-sight acceleration for every satellite, including those at the horizon. That is a good reason to mount the GNSS module where vibration is lowest and to log its frequency estimate (clock drift in `UBX-NAV-CLOCK`) through boost.

**5 — Under the main parachute.** If the antenna boresight tilts 90° from zenith, the receiver sees ≈ 12 satellites instead of ≈ 29 (GPS+GAL+BDS, Singapore, synthetic constellation) and median HDOP rises from 0.50 to 2.0 (`gnss_dop_errors.py`). Swinging adds C/N₀ fades. Recovery fixes remain usable (tens of metres); design the recovery telemetry to repeat the last good fix.

## Practical notes
- **Antenna location**: best is a nose-tip helix or patch facing forward (DLR uses a helical tip antenna for ascent and switches to body-mounted blades after nose-cone separation [10][11]); keep it out of carbon fibre (≈ 50–160 dB for a 1 mm wall at L1, σ 10³–3×10⁴ S/m — [02 reflection](../02-electromagnetics/boundary-conditions-reflection-refraction.md)) and away from the 433/900 MHz telemetry antenna ([antennas on rockets](../08-antennas/antennas-on-rockets.md), [GNSS antennas](../08-antennas/gnss-antennas.md)). Linear blade antennas cost 3 dB and add pattern lobes [10].
- **On the pad**: power the receiver for ≥ 15 min with a sky view (or an RF-transparent pad cover) so it has ephemeris for all satellites; keep V_BCKP alive; DLR even feeds the rocket through a GNSS re-radiation kit inside its launch tower and still loses all signals briefly while passing the tower tube [11] — never radiate GNSS signals yourself without authorization ([interference page](gnss-interference-jamming-spoofing.md)).
- **Configure**: `CFG-NAVSPG-DYNMODEL = AIR4`; choose constellations vs rate deliberately; output `NAV-PVT` (and `NAV-SAT`, `RXM-RAWX` for analysis); use the timepulse to timestamp ([integration](gnss-receiver-integration-u-blox.md), [timing](gnss-timing-1pps.md)).
- **Flight software**: never block on GNSS; accept fix gaps; gate GNSS updates in the EKF on `gnssFixOK`, `numSV`, `pDOP` and the reported accuracies; expect lag in the receiver's own filter at high vertical speed (a u-blox 7 user saw output lag above 100 m/s vertical with the Airborne model [7] — M8's Airborne model assumes ≤ 100 m/s vertical [9]).
- **Re-acquisition**: with valid ephemeris and a running clock, re-acquisition is local ("reacquisition sensitivity" −160 dBm [1][2]) and takes ~1 s; after a long outage under high dynamics, a receiver's predicted Doppler may be off — DLR solved this with trajectory aiding [10]; COTS u-blox has no external Doppler aiding input for this purpose.
- **Amateur observations (anecdotal)**: "loses lock in boost, back within a couple of seconds after burnout" is the common report; BigRedBee's u-blox-based tracker went above 61 km, stopped above 50 km and resumed below [8]; a tracker vendor reports ≈ 90 % lock retention at ≤ 10 g and ≈ 90 % loss at ≥ 20 g (via search summary of a rocketry-forum thread; not read in full) [12].
- **Jamming at altitude**: the radio horizon grows with altitude, so a rocket "sees" distant ground jammers; sounding rockets from northern Scandinavia have experienced L1 jamming above ≈ 25 km since 2022, with C/N₀ drops of 5–10 dB [11]. Multi-frequency, multi-constellation receivers kept navigating.

## Common mistakes & misconceptions
- **"The COCOM limit is 1000 knots AND 18 km, so my 600 m/s rocket is fine below 18 km."** Don't rely on it: u-blox's documented limit is 500 m/s and its only staff statement says speed alone suffices [7].
- **"Airborne <4g means the receiver loses lock above 4 g."** The model is a navigation-filter setting; tracking survives more than 4 g of *steady* acceleration — it's jerk and oscillator effects at transitions that break lock.
- **"Leaving the default Portable model is harmless."** Portable invalidates fixes above 12 km or 50 m/s vertical [3][4]; it's the classic high-altitude-balloon failure too.
- **"GNSS position during boost is as good as on the ground."** Even when tracking, boost-phase errors can be tens of metres (DLR: 90 m RMS from oscillator effects [10]); weight GNSS low during boost in your EKF.
- **"Removing the limits is just a firmware setting."** It's not offered on COTS modules and would turn the receiver into an export-controlled item.

## How to simulate / verify
- `python3 tools/verify/gnss_tracking_loops.py` — dynamic stress formulas, oscillator g-sensitivity and vibration jitter, 3rd-order PLL ± FLL assist simulated through ignition/boost/burnout profiles. ALL PASS.
- `python3 tools/verify/gnss_dop_errors.py` — sky-mask/tilt effect on DOP. ALL PASS.
- Hardware-in-the-loop: a cabled (conducted, shielded) GNSS simulator with a rocket trajectory is the only legal way to test limits on the ground — see the user's HIL methods notes (`~/.claude/knowledge/space-bar-avionics/hil-bench-testing-methods.md`) and the [SDR page](sdr-gnss-and-diy-receivers.md) on gps-sdr-sim (cabled only).
- Flight: log `NAV-PVT`, `NAV-SAT`, `NAV-CLOCK`, `RXM-RAWX` at the highest sustainable rate and compare with IMU-integrated trajectory.

## Open questions / gaps
- AND/OR logic and exact behaviour at 500 m/s for current u-blox firmware (HPG 1.32, SPG 5.10) are undocumented; needs a simulator test.
- u-blox loop bandwidths/orders and TCXO g-sensitivity are unpublished; the simulation uses generic values.
- The DLR flight-performance paper comparing three receivers (Bull et al., NTRS 20020060112) could not be downloaded (403); not read.
- Amateur flight statistics are anecdotal; no systematic dataset of u-blox behaviour on high-power rockets was found.

## Sources
1. u-blox, *ZED-F9P-04B Data sheet*, UBX-21044850 R05 (HPG 1.32), 2024 — operational limits ≤4 g / 80 000 m / 500 m/s "assuming Airborne 4 g platform"; RTK convergence; sensitivity. https://content.u-blox.com/sites/default/files/ZED-F9P-04B_DataSheet_UBX-21044850.pdf (manufacturer)
2. u-blox, *MAX-M10S Data sheet*, UBX-20035208 R08 (SPG 5.10) — same operational limits; reacquisition sensitivity. https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf (manufacturer)
3. u-blox, *ZED-F9P Integration manual*, UBX-18010802 R16 — dynamic platform model tables and sanity-check rule. https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf (manufacturer)
4. u-blox, *MAX-M10S Integration manual*, UBX-20053088 R05 — §2.2.1 dynamic models (Tables 9–10); migration table "maximum altitude limit increased to 80 000 m". https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf (manufacturer)
5. u-blox, *ZED-F9P Data sheets* UBX-17051259 R02 (2018, ZED-F9P-00B, HPG 1.00; SparkFun mirror https://cdn.sparkfun.com/assets/8/3/2/b/8/ZED-F9P_Data_Sheet.pdf) and R09 (2023, -01B, HPG 1.12, https://content.u-blox.com/sites/default/files/documents/ZED-F9P-01B_DataSheet_UBX-17051259.pdf): 50 000 m; UBX-21023276 R04 (2024, -02B, HPG 1.13, https://content.u-blox.com/sites/default/files/documents/ZED-F9P-02B_DataSheet_UBX-21023276.pdf): 80 000 m. (manufacturer)
6. J. Y. Kim, U.S. Office of Space Commerce, "U.S. Export Controls on GPS/GNSS Equipment," National Space-Based PNT Advisory Board, 18 Mar 2022 — USML XII(d), ECCN 7A105 (600 m/s, MTCR 11.A.3), 7A005, 7A994, 9A515.x. https://www.space.commerce.gov/wp-content/uploads/2022-03-US-export-controls-GPS-GNSS-equipment.pdf (government summary)
7. u-blox Support Community, "Clarifying the velocity limit of 500 m/sec" (2016), answer by u-blox staff; user report of lag above 100 m/s vertical. https://portal.u-blox.com/s/question/0D52p00008HKChmCAH/clarifying-the-velocity-limit-of-500-msec (vendor forum)
8. BigRedBee, "High Altitude GPS operation" (2018, 2023 update) — CoCom AND claim, PHX4 > 200 000 ft flight, 50 km cut-off, newer 80 km. https://shop.bigredbee.com/blogs/news/high-altitude-gps-operation (vendor blog — anecdotal)
9. u-blox, *u-blox 8 / u-blox M8 Receiver Description incl. Protocol Specification*, UBX-13003221 R28 — dynamic platform model details (Airborne: 50 000 m, vertical 100 m/s). https://content.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_UBX-13003221.pdf (manufacturer)
10. M. Markgraf, O. Montenbruck, F. Hassenpflug, P. Turner, B. Bull, "A Low Cost GPS System for Real-Time Tracking of Sounding Rockets," 15th ESA Symposium on European Rocket and Balloon Programmes, Biarritz, 2001 (NTRS 20010069267) — 15 g unmodified tracking, reacquisition problem, trajectory aiding, limits removal, Test Maxus-4 (18 g, 3.8 Hz spin), oscillator offset ≈ 100 Hz, 90 m RMS boost error, tip helix and blade antennas. https://archive.org/details/nasa_techdoc_20010069267 (conference paper)
11. B. Braun, M. Markgraf, L. Rheinwald, S. Weiß, M. Hörschgen-Eggers, "First Test of a Multi-Constellation, Multi-Frequency GNSS Receiver on Board a Sounding Rocket," *Eng. Proc.* 126:39, 2026 (ENC 2025) — MAPHEUS-15, launch-tower loss/4.5 s recovery, 2000°/s roll, loop settings, jamming above 25 km, 600 m/s data restriction. https://elib.dlr.de/214653/1/engproc-126-00039.pdf (conference paper, open access)
12. u-blox Support Community, "U-blox M10S velocity and altitude operational limits" (2023, customer answers); Rocketry Forum threads "USC and GPS", "GPS g limits?", "Highest Altitude GPS?" (search-result summaries only; site blocked automated reading). https://portal.u-blox.com/s/question/0D52p0000DRuM7ICQV/ublox-m10s-velocity-and-altitude-operational-limits ; https://www.rocketryforum.com/threads/usc-and-gps.152925/ (forum — anecdotal)
13. E. D. Kaplan, C. J. Hegarty (eds.), *Understanding GPS/GNSS*, 3rd ed., Artech House, 2017 — ch. 8: dynamic stress, Allan-deviation and vibration-induced oscillator phase jitter, FLL-assisted PLL. (textbook)
14. Space Bar avionics knowledge base (user's notes) — Avionics B (ZED-F9P, L1-only antenna, RTK via LoRa bridge), Avionics C (MAX-M10S), GPS recovery-ladder lesson. (internal)
