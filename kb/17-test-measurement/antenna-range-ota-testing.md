---
title: Antenna ranges and over-the-air (OTA) testing — DIY far-field and ground-reflection ranges, reference antennas, SDR/turntable patterns, TRP/TIS, and field-testing a rocket telemetry link (drone/kite tests, range test by attenuation)
domain: 17-test-measurement
slug: antenna-range-ota-testing
tags: [antenna-range, far-field, ground-reflection-range, elevated-range, reference-antenna, gain-transfer, pattern, turntable, sdr, rssi, trp, tis, eirp, ota, range-test, drone, kite, attenuation, link-margin, two-ray, fresnel, rocket-telemetry]
prerequisites: [../08-antennas/antenna-measurement.md, ../09-propagation-link-budget/friis-free-space-path-loss.md, ../09-propagation-link-budget/two-ray-ground-reflection.md]
related: [sdr-as-test-equipment.md, nanovna-librevna-practical.md, noise-figure-measurement.md, rf-bring-up-debug-playbook.md, ../08-antennas/antennas-on-rockets.md, ../09-propagation-link-budget/link-budget-methodology.md, ../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md, ../09-propagation-link-budget/link-margin-availability.md, ../15-lora-ism-radios/rocket-telemetry-radio-design.md, ../15-lora-ism-radios/ground-station-design.md]
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# Antenna ranges and OTA testing

## Questions this page answers
- How do I set up a backyard/field antenna range at 433/915 MHz, and at what heights?
- What is a ground-reflection range, and why would I *want* the ground reflection?
- What reference antenna should I use for gain measurements?
- What do TRP and TIS mean, and can I estimate them without a chamber?
- My ground-level range test only reached 1.5 km — will the rocket link really work at 10 km?
- How does a "range test by attenuation" work, and how do I turn it into a link margin?
- How many packets/RSSI readings do I need for a meaningful field-test number?

## TL;DR
- Theory of antenna measurement (far-field distance 2D²/λ, gain transfer, three-antenna method, Wheeler cap, axial ratio, SDR pattern recipe) lives in [antenna measurement](../08-antennas/antenna-measurement.md). This page is the *range and field-test* layer.
- **Ground-reflection range** (IEEE Std 149 concept [1]): instead of fighting the ground bounce, place the AUT at the first interference maximum, h_r ≈ λR/(4h_t) (Γ ≈ −1 at grazing). 433 MHz, R = 30 m, h_t = 2 m → h_r = 2.6 m, with only −0.4 dB field taper over ±0.5 m; at 1575 MHz the lobe is so narrow (−6.9 dB at ±0.5 m) that an elevated/absorber range is better.
- **Ground-level link tests grossly underestimate flight range**: with both antennas at 1.5 m, two-ray loss at 433 MHz is 34 dB worse than free space at 2 km and 48 dB worse at 10 km (breakpoint 4h_th_r/λ = 13 m). A rocket or a 100 m drone is in near-free-space conditions (±6 dB lobing).
- **Range test by attenuation**: at a short, clear line-of-sight distance d₀, add calibrated attenuation until PER hits the limit (A_fail): free-space range ≈ d₀·10^{A_fail/20}; margin at distance d = A_fail − 20 log(d/d₀). Example: 43.5 dB at 200 m → 29.9 km limit, +9.5 dB margin at 10 km *before* allowances for antenna nulls, roll, plume and fading.
- **TRP** = spherical average of EIRP = P_accepted·η; **TIS** = harmonic spherical average of EIS = conducted sensitivity/η (script reproduces both exactly on a 15° grid). They combine antenna, matching and self-interference into one OTA number [2].
- **Statistics**: RSSI in the field scatters by 2–6 dB; for ±0.5 dB (95 %) on the mean you need N ≥ (1.96σ/0.5)² — 62 packets at σ = 2 dB, 554 at σ = 6 dB.

## Intuition (no math)
An antenna range is an attempt to create "free space" somewhere convenient: one antenna shines a clean, uniform wave on the other, and nothing else arrives. The ground is the big problem outdoors — it adds a second, reflected wave. You can either get so high and point so carefully that the reflection is weak (elevated range, absorbers), or you can accept it and put the antenna under test exactly where the direct and reflected waves add up smoothly (ground-reflection range). Both are standard.

For a rocket link, the field test that matters is not "how far can two people with handhelds get along a road" — near the ground the two waves nearly cancel and the signal falls 40 dB per decade instead of 20. The rocket is high up, in near-free-space conditions. The honest way to predict flight range from a ground test is to test at short range in clear line of sight with the *flight* hardware and antenna installation, then add calibrated attenuation to emulate distance.

## The math

### Level 1 — working formulas
- Free-space path loss: FSPL = 20 log₁₀(4πd/λ) dB ([Friis](../09-propagation-link-budget/friis-free-space-path-loss.md)).
- **Attenuation ↔ distance** (free space): an extra A dB is equivalent to multiplying d by 10^{A/20} (10 dB → 3.16×, 20 dB → 10×, 40 dB → 100×).
- **Two-ray breakpoint**: d_b = 4h_th_r/λ; beyond it the flat-earth loss → 40 log d − 20 log(h_th_r) ([two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md)).
- **First Fresnel zone radius** at mid-path: r₁ = √(λd/4); keep ≥ 0.6r₁ clear ([Fresnel zones](../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md)).
- **Ground-reflection range**: first field maximum at the AUT when the path difference 2h_th_r/R = λ/2 (with Γ = −1): h_r = λR/(4h_t) [1].
- **TRP** = (1/4π)∮ EIRP(θ, φ) dΩ; **TIS** = 4π / ∮ [1/EIS(θ, φ)] dΩ (CTIA definitions [2]).
- **Samples for a mean**: N = (1.96σ/Δ)² for ±Δ at 95 % confidence.

### Level 2 — derivations
**Ground-reflection range.** With transmitter height h_t, receiver height z and range R ≫ h, the direct and image paths differ by Δ ≈ 2h_tz/R. For grazing incidence over most ground (both polarisations) Γ ≈ −1, so the field ∝ |1 − e^{−jkΔ}| = 2|sin(πΔ/λ)| = 2|sin(2πh_tz/(λR))|. The first maximum is at 2πh_tz/(λR) = π/2 → z = λR/(4h_t). Its width sets the usable aperture: the script gives −0.41/−0.38 dB at ±0.5 m for 433 MHz (R = 30 m, h_t = 2 m, peak at 2.60 m), −1.9 dB at 915 MHz (peak 1.23 m) and −6.9 dB at 1575 MHz (peak 0.71 m). Hence ground-reflection ranges suit the lower UHF band and small AUTs; the vertical taper must be ≲ 0.25–0.5 dB over the AUT.

**Two-ray vs free space for field tests.** The exact two-ray field with Γ = −1, E ∝ |e^{−jkd₁}/d₁ − e^{−jkd₂}/d₂|, compared with free space (script §2):

| Geometry | 433 MHz: excess loss at 0.5 / 2 / 5 / 10 km | 915 MHz |
|---|---|---|
| Both at 1.5 m (hand-held) | +21.8 / +33.8 / +41.8 / +47.8 dB | +15.3 / +27.3 / +35.3 / +41.3 dB |
| GS mast 10 m, TX at 1.5 m | +5.4 / +17.3 / +25.3 / +31.3 dB | −0.7 / +10.9 / +18.8 / +24.8 dB |
| TX on 100 m drone, GS 10 m | −4.8 / −5.9 / −5.8 / −4.0 dB | +14.3 / +10.4 / −2.1 / −5.5 dB |
| Rocket at 3 km altitude, GS 10 m | −6.0 / +13.2 / +1.5 / −4.2 dB | −1.8 / −1.7 / −5.6 / −5.9 dB |

(Negative: the two rays add, up to +6 dB above free space. Γ = −1 over flat ground is a worst-case idealisation — real ground has |Γ| < 1 away from grazing and is rough — so the deep lobing nulls, e.g. 433 MHz at 2 km from a 3 km-high rocket, are shallower in practice; see domain 09.) The hand-held test at 2 km is ~34 dB pessimistic at 433 MHz: a link that "died at 1.5 km on the ground" can have tens of km in flight.

**Attenuation method.** Received power P_r = P_t + G_t + G_r − FSPL(d₀) − A. Setting A so that PER reaches the limit defines P_r = S (effective sensitivity including interference). At distance d without attenuation, P_r = P_t + G_t + G_r − FSPL(d₀) − 20 log(d/d₀), so the margin is M(d) = A_fail − 20 log(d/d₀), and d_max = d₀·10^{A_fail/20}. The test captures *everything* in the real hardware (antenna installation, cable, match, desense from the flight computer) — as long as the attenuator is in the *conducted* path (between radio and antenna) and nothing leaks around it, and the test geometry is genuinely free-space-like (drone/mast, first Fresnel zone clear: r₁ = √(λd/4) at 200 m is 5.9 m at 433 MHz).

**TRP/TIS.** EIRP(θ, φ) = P_acc·G(θ, φ) with G = ηD; since ∮D dΩ = 4π, TRP = P_acc·η. For reception, EIS(θ, φ) = S_cond/G(θ, φ) and ∮(1/EIS) dΩ = 4πη/S_cond, so TIS = S_cond/η. Script §4: η = 60 %, P_acc = 20 dBm → TRP 17.78 dBm; S_cond = −120 dBm → TIS −117.78 dBm (the harmonic average is dominated by the good directions). In practice TIS is *worse* than S_cond/η whenever the device's own electronics desense its receiver through the antenna — which is exactly why OTA tests exist [2].

### Level 3 — range design details and error sources
- **Far-field and taper criteria**: R ≥ 2D²/λ, R ≫ λ and R ≫ D; amplitude taper over the AUT ≤ 0.25 dB for precise gain, ≤ 1 dB for patterns ([antenna measurement](../08-antennas/antenna-measurement.md)).
- **Elevated range**: both antennas high on masts/buildings, source antenna directive enough that its pattern toward the specular point is ≥ 20–30 dB down; absorber or a fence to block the specular point; ripple from a reflection of relative level ρ: 20 log(1 ± ρ) (−20 dB → ±0.9 dB).
- **Compact ranges, near-field scanners, reverberation chambers** are the professional alternatives (a plane wave from a reflector; NF-to-FF transforms; statistical efficiency/TRP) — borrow university facilities for certification-grade numbers.
- **OTA metrics in regulations**: TRP/EIRP limits for ISM devices are defined as radiated power ([ISM band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md), [certification](../19-regulations-safety/certification-fcc-ce-imda.md)).

## Design equations & rules of thumb

| Item | Rule / value | Notes |
|---|---|---|
| Ground-reflection AUT height | h_r = λR/(4h_t) | 433 MHz, 30 m, 2 m → 2.6 m |
| Attenuation ↔ distance | ×10^{A/20} | 20 dB = 10× |
| Margin from attenuation test | M(d) = A_fail − 20 log(d/d₀) | free-space assumption |
| Breakpoint | 4h_th_r/λ | 1.5 m/1.5 m at 433 MHz → 13 m |
| Fresnel clearance | 0.6√(λd/4) | 2 km at 433 MHz → 11 m |
| TRP | P_acc·η | spherical EIRP average |
| TIS | S_cond/η (no self-desense) | harmonic average |
| RSSI samples | N = (1.96σ/Δ)² | σ 4 dB, ±1 dB → 62 |
| Reference dipole | 2.15 dBi (λ/2, choked) | gain transfer |

## Worked examples

**Example 1 — a backyard ground-reflection range at 433 MHz.** Source: a 3-element Yagi at h_t = 2 m; range R = 30 m (≫ 2D²/λ for a 0.35 m dipole-class AUT, and 43λ). AUT (the rocket's antenna section on a wooden turntable) at h_r = 0.692 × 30/(4 × 2) = 2.6 m. Field taper over ±0.5 m ≈ −0.4 dB (script). Check the geometry empirically: move a small probe dipole vertically ±0.5 m and confirm < 1 dB variation. Measure the pattern with an SDR (fixed gain) and log power vs angle; for gain, substitute a choked λ/2 dipole (2.15 dBi) at the same spot (gain transfer).

**Example 2 — why the ground test "failed" at 1.5 km.** Two E22-400T22S modules (22 dBm; the team's E22-400T33D has no 22 dBm step — at its 24 dBm step P_r is −60 dBm; 2.15 dBi whips), both hand-held at 1.5 m. Free-space budget at 1.5 km, 433 MHz: FSPL = 88.7 dB → P_r = 22 + 2.15 + 2.15 − 88.7 = −62 dBm (huge margin to the −137 dBm SF12 sensitivity). Two-ray at 1.5 m heights adds ≈ 32 dB, trees/bodies/fresnel blockage another 20–40 dB — the observed failure is terrain, not the radio. The flight geometry (rocket at altitude, ground-station Yagi on a mast) behaves like free space ± lobing.

**Example 3 — drone + attenuator test of the flight avionics bay (915 MHz).** Hang the *complete* avionics section (antenna installed, battery, flight computer running) 30 m under a drone at 100 m altitude, 200 m horizontal from the ground station (slant ≈ 224 m, clear LOS). Insert a calibrated step attenuator between the flight radio and its antenna (or between the ground-station antenna and receiver — the conducted path at either end; the latter is easier). Increase attenuation until PER reaches 10 %: suppose 43.5 dB at d₀ = 200 m (script §3) → d_max ≈ 29.9 km free space; margin at 10 km slant range +9.5 dB. Then subtract allowances: nose-on/tail-on pattern nulls (10–20 dB for a monopole along its axis; rotate the drone payload to measure them), roll-induced polarization loss (3–20 dB for linear-linear) and fading margin ([link margin](../09-propagation-link-budget/link-margin-availability.md), [antennas on rockets](../08-antennas/antennas-on-rockets.md)). If the result is negative, the attenuation test tells you by how much to improve before flight.

**Example 4 — TRP/TIS estimate without a chamber.** Measure the flight antenna's azimuth patterns at 3–5 elevation cuts on the range (relative), normalise with a gain-transfer point, integrate with sin θ weights → an approximate TRP; conducted TX power (power meter) × pattern-derived efficiency cross-checks it. For TIS, run the attenuation test in 8 orientations and harmonically average the 8 "equivalent sensitivities" — a crude TIS that includes desense from the flight computer (compare with the flight computer powered off: a difference > 2 dB means self-interference).

**Example 5 — how long to sit at each test point.** Field RSSI with σ ≈ 4 dB (people moving, multipath): ±1 dB on the mean at 95 % confidence needs ≥ 62 packets; ±0.5 dB needs 246 (script §5). At one packet per second, that is 1–4 minutes per point — plan the drone battery accordingly.

## Practical notes
- **Record everything**: GPS positions of both ends, heights, antenna orientations, attenuator settings (with calibration at the test frequency), radio settings (SF, BW, CR, power), packet counts, RSSI/SNR per packet, weather, and photos of cable routing.
- **Use the flight configuration**: airframe section, harness, battery, all electronics running (GNSS, flight computer, cameras) — self-generated noise is often the real limit.
- **Common-mode currents on the test cable** change the AUT pattern; choke cables and run them along the rotation axis ([baluns](../08-antennas/antenna-matching-and-baluns.md)).
- **Turntables**: wooden/plastic, metal ≥ λ/2 below the AUT; a stepper and an Arduino plus an SDR logging script make an automated pattern range ([SDR as test equipment](sdr-as-test-equipment.md)).
- **Kites and balloons** are alternatives to drones for long hovering at 100–300 m (check airspace rules; Singapore restricts drone and kite heights near airports — see [regulations](../19-regulations-safety/singapore-imda-rules.md)).
- **RSSI calibration**: LoRa chips' RSSI has an offset of several dB; calibrate against a known conducted level from the [conducted sensitivity setup](noise-figure-measurement.md) before trusting absolute numbers.
- **Attenuator placement**: put the step attenuator at the ground-station end so the flight hardware is untouched; account for its insertion loss at 0 dB setting.

## Common mistakes & misconceptions
- **"Our range test reached 1.5 km, so the rocket link is only good for 1.5 km."** Ground-level tests are 30–50 dB pessimistic (two-ray, blockage).
- **"Hanging the radio from a drone proves 20 km range."** Only if you also emulate the distance (attenuation) and the worst-case orientation.
- **Leaky attenuation tests**: the transmitter radiates around the step attenuator (bad cables, unshielded radio) and the test shows infinite margin.
- **Measuring patterns indoors at 433 MHz** — room reflections dominate.
- **Forgetting the source antenna's pattern toward the ground** — a whip source illuminates the specular point strongly.
- **Averaging RSSI in dB over deep fades** biases the mean low; report median and spread as well.

## How to simulate / verify
- `python3 tools/verify/meas_range.py` — (1) ground-reflection range heights and taper; (2) two-ray vs FSPL table for ground tests, drones and rockets, breakpoint and Fresnel radius; (3) attenuation-test range/margin arithmetic; (4) TRP/TIS integration on a 15° grid; (5) RSSI sample counts.
- `tools/verify/ant_measurement.py` (domain 08) for far-field and three-antenna checks; domain 09 scripts for two-ray and link budgets.

## Open questions / gaps
- Array testing (W2-B5 request): the embedded-element-pattern recipe (one port driven, all others matched-terminated, S-matrix logged for active reflection) is in [08 antenna measurement § E](../08-antennas/antenna-measurement.md#measurement-recipes) and power-meter-only REV calibration in [12 array calibration](../12-phased-arrays/array-calibration.md); no range-specific procedure (positioner indexing per element, switching matrix) is written yet.
- IEEE Std 149 was not read directly (cited via Balanis and domain 08); the ground-reflection-range formula is derived here from first principles.
- CTIA test-plan details (grid, weighting, NHPRP) cited via TI DN024 (domain 08), not read here.
- No measured team data yet for the attenuation-method margin; the 43.5 dB example is illustrative.

## Sources
1. IEEE Std 149-1979 (R2008), *IEEE Standard Test Procedures for Antennas* — elevated and ground-reflection ranges, gain-transfer and three-antenna methods. (standard; cited via Balanis ch. 17)
2. CTIA, *Test Plan for Wireless Device Over-the-Air Performance* — TRP, TIS, EIRP/EIS definitions; summarised in TI DN024 (SWRA227). (industry standard; cited via domain 08)
3. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Wiley, 2016, ch. 17 — ranges, far-field criteria, ground-reflection range geometry. (textbook; cited)
4. This KB: [antenna measurement](../08-antennas/antenna-measurement.md), [two-ray ground reflection](../09-propagation-link-budget/two-ray-ground-reflection.md), [link margin](../09-propagation-link-budget/link-margin-availability.md). (internal)
5. This repository: `tools/verify/meas_range.py`. (verification)
