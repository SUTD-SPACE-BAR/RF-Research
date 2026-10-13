---
title: Recipe — Tracking ground station for rocket telemetry (433 / 868–915 MHz DL6WU crossed Yagis, masthead LNA + SAW, tracking, diversity, SDR recording)
domain: 20-projects-recipes
slug: ground-station-tracking-yagi
tags: [recipe, ground-station, yagi, dl6wu, crossed-yagi, circular-polarization, phasing-harness, lna, saw-filter, bias-tee, limiter, coax, tracking, rotator, gnss-pointing, diversity, sdr-recording, gr-lora-sdr, pre-registration]
prerequisites:
  - ../15-lora-ism-radios/ground-station-design.md
  - ../08-antennas/yagi-uda-and-log-periodic.md
  - ../07-noise-linearity/noise-figure-and-friis.md
  - lora-rocket-telemetry-link.md
related:
  - ../08-antennas/antenna-polarization-and-circular-polarization.md
  - ../08-antennas/helical-antennas.md
  - ../08-antennas/antenna-matching-and-baluns.md
  - ../03-transmission-lines-matching/coax-and-cables.md
  - ../06-rf-circuits/rf-switches-attenuators-limiters.md
  - ../18-components-parts/lna-pa-gain-block-mmics.md
  - ../14-sdr-dsp/sdr-hardware-survey.md
  - ../17-test-measurement/antenna-range-ota-testing.md
  - lna-design-walkthrough.md
  - sdr-receiver-build.md
  - phased-array-starter-build.md
level: intermediate
confidence: medium
last_updated: 2026-10-14
---

# Recipe — Tracking ground station for rocket telemetry (433 / 868–915 MHz)

The receiving end of [the telemetry link recipe](lora-rocket-telemetry-link.md). Numbers come from
`python3 tools/verify/proj_ground_station.py` (DL6WU designs evaluated by the KB's own thin-wire MoM in
`tools/verify/ant_yagi.py`, CP harness ABCD analysis, cascades, blocking levels, tracking simulation on
the modelled 10 km flight, diversity, recording rates). `FAST=1` skips the 2-minute MoM.

## Questions this page answers
- What Yagi should I build for a 433 MHz and a 868/915 MHz rocket ground station, and with what dimensions?
- How big a beam can I still point by hand, and do I need a rotator?
- How do I make a crossed Yagi circularly polarised, and why can the phasing harness look perfectly matched while the CP is bad?
- Where do the LNA, SAW filter and limiter go, and how much gain is too much?
- Which coax, and how much does 15 or 30 m of it cost me at 433 vs 905 MHz?
- Will my own rocket on the pad, another team's radio or a phone next to me overload the receiver?
- Can a Yaesu-class rotator keep up with a rocket?
- Is a second station worth it, and where should it go?
- How do I record the raw signal with an SDR, and how much disk do I need?

## TL;DR
- **Antennas (MoM-checked DL6WU designs):** 433 MHz **6 elements on a 637 mm boom: 11.2 dBi, F/B 13 dB, beam 50° × 61°, Z ≈ 73 Ω**; 433 MHz 11 el on 1.72 m: 14.2 dBi, 36° × 40°, Z ≈ 52 Ω; 868/905 MHz 6 el on ≈ 0.31 m: 11.2 dBi, 49° × 60°, Z ≈ 81–83 Ω; 868/905 MHz 11 el on ≈ 0.84 m: 14.3 dBi, 36° × 39°, Z ≈ 50 Ω.
- **Pick the 6-element pair for a hand-steered or fixed station.** On the modelled 10 km flight from a station 5 km cross-range, a *fixed* 6-el pointed at az 172°/el 31° loses at most 4.9 dB (median 3.6 dB) over the whole ascent — affordable given the 30–50 dB margins of the link recipe. An 11-el fixed loses up to 9.1 dB; tablet-steered with 1 s latency and 5° rms hand error it loses ≤ 1.2 dB (p95).
- **Rotators are too slow in elevation for the boost**: a Yaesu G-5500-class (6.2°/s az, 2.7°/s el, manufacturer rotation times) lags by up to 18° at t ≈ 11 s (loss 1.6 dB with a 6-el, 2.9 dB with an 11-el); peak demand is 6.3°/s elevation. Pre-point, then let it catch up — or hand-steer.
- **Crossed Yagi CP**: two λ/4 75 Ω transformers (114 mm of VF-0.66 coax at 433.5 MHz, 57 mm at 868 MHz) in parallel, one branch delayed by λ/4 of 50 Ω, gives **56 Ω (S11 −24.6 dB) and AR ≤ 0.3 dB over 425–442 MHz** — *if each Yagi is 50 Ω*. With the 6-el's native 73–81 Ω the harness input still looks excellent (S11 −33 to −48 dB) but the split becomes **3.3–4.1 dB unequal → AR 3.3–4.1 dB**. Match each Yagi first, or use the λ/4 boom-offset method with identical feeds.
- **Handedness does not matter** for a linear rocket antenna (either CP sense receives it at −3 dB); an AR of 3 dB leaves a 3 dB roll ripple (−1.8 to −4.8 dB).
- **Feeder**: 15 m of LMR-240 costs 2.6 dB at 433 MHz and 3.7 dB at 905 MHz; RG-58 4.3 / 6.7 dB. Module at the end of 15 m RG-58: NF 10.3 dB (433) / 12.7 dB (905). **Masthead LNA → SAW → 15 m LMR-240 → 4-way splitter → module: NF 2.8 / 3.3 dB**; with a second gain stage 0.9 dB — but then pad-side signals exceed the module's 10 dBm damage rating.
- **Blockers**: own rocket on the pad at 30 m in the main lobe puts −9.6 dBm into the LNA; another team's 2 W 20 m away −6 dBm; a phone's 900 MHz uplink 2 m away −5 dBm (GSM peak) / −15 dBm (LTE). Keep the rocket-side receivers ≥ 100 m or insert 20–30 dB during pad checks; keep phones away from the 868/905 chain.
- **Diversity**: two stations at 10 % loss each give 1 % if independent, 3.7 % at correlation 0.3, 7.3 % at 0.7 — put them on different azimuths (tail null), polarisations or bands.
- **Recording**: RTL-SDR at 1.024 MS/s × 8-bit = 2 MB/s = 3.7 GB per 30 min per band.

## Intuition (no math)
A ground station is a funnel (the antenna), an ear (the LNA), ear-plugs for loud neighbours (filter, limiter), a hose to the tent (coax — every dB lost *before* the ear is lost for good) and several listeners (module, SDR, SX126x board) sharing the same sound. The rocket moves fast only in elevation and only in the first ~15 s; after that it is a slowly moving dot, then a dot drifting down under a parachute. A moderately wide beam that one person can wave in roughly the right direction captures almost all of the available signal; a long, narrow Yagi gains 3 dB on paper and loses more than that whenever it is mis-pointed. Circular polarisation on the ground trades a steady 3 dB for immunity to the rocket's roll.

## Requirements
| ID | Requirement | Value |
|---|---|---|
| G1 | Bands | 433.05–434.79 MHz (primary), 866–869 MHz (SG) and 902–928 MHz (IREC) (secondary) |
| G2 | Antenna | CP (or dual-linear), ≥ 10 dBic per band, beam ≥ 45° for hand/fixed pointing |
| G3 | System NF | ≤ 3 dB at the receiver inputs with 15 m feeder and a 4-way split |
| G4 | Survivability | no damage with the flight transmitter on the pad at ≥ 30 m; no compression from a 2 W transmitter at 20 m |
| G5 | Tracking | pointing loss ≤ 1.5 dB (p95) during ascent from a 3–5 km offset station |
| G6 | Receivers | flight-identical module + SX126x receiver (SNR, FEI) + SDR IQ recorder, per band; GNSS-PPS timestamps |
| G7 | Landed phase | mast ≥ 6 m available; handheld 3-el Yagi for walking in |
| G8 | Field | 2 people, ≤ 30 min set-up, ≥ 4 h on battery |

## Architecture options and trade study
| Option | Gain / beam | Polarisation | Tracking | + | − |
|---|---|---|---|---|---|
| Vertical collinear / ground plane omni | 2–6 dBi, omni | linear | none | trivial | roll nulls, overhead null exactly where the rocket goes, no rejection of ground interference |
| **6-el crossed Yagi (per band)** | 11.2 dBic, 50° × 61° | CP | fixed or by hand | tolerant of pointing; short booms (0.64 m / 0.31 m) share one mast | 3 dB less than 11-el |
| 11-el crossed Yagi | 14.2–14.3 dBic, 36° × 40° | CP | tablet/rotator | +3 dB, better F/B (16 dB) | 9 dB worst loss if fixed; 1.7 m boom at 433 MHz |
| Axial-mode helix (10 turns) | ≈ 13 dBic realistic ([helical antennas](../08-antennas/helical-antennas.md)) | CP by construction | tablet/rotator | no harness | 1.7 m long, 0.22 m diameter at 433 MHz; heavy |
| GNSS-driven az/el rotator (G-5500-class) | any | any | automatic | hands-free | slow in elevation (2.7°/s), ≈ US$700+, mains/12 V power |
| Phased array | electronic steering | any | automatic | no moving parts | cost/complexity — see [phased-array starter](phased-array-starter-build.md) for the honest comparison |

**Decision:** station 1 (primary, 5 km cross-range): dual-band 6-el crossed Yagis on one non-metallic boom support, hand-steered from a tablet showing az/el computed from the downlinked GNSS; station 2 (3–5 km on another azimuth, or down-range): same antennas **fixed-pointed** at the predicted mid-ascent direction, unattended. Optional upgrade: 11-el on a fast DIY rotator (≥ 20°/s).

## The math — design calculations

### Level 1 — the Yagis
DL6WU spacing table, director curve fit and reflector formula as implemented in `tools/verify/ant_yagi.py` ([Yagi page](../08-antennas/yagi-uda-and-log-periodic.md)); element diameters 6 mm (433 MHz) and 4 mm (868/905 MHz); elements insulated from (or clear of) the boom; plain-dipole driven element re-resonated in the MoM.

| Design | Boom | Directivity (MoM) | DL6WU estimate | F/B | $Z_{in}$ | HPBW (element plane × other) |
|---|---|---|---|---|---|---|
| 433 MHz 6 el | 637 mm | **11.19 dBi** | 11.07 dBi | 13.3 dB | 73.4 Ω | 49.6° × 60.8° |
| 433 MHz 11 el | 1724 mm | **14.20 dBi** | 14.44 dBi | 16.3 dB | 52.2 Ω | 36.4° × 39.8° |
| 868 MHz 6 el | 318 mm | 11.21 dBi | 11.07 dBi | 13.1 dB | 80.5 Ω | 49.2° × 60.4° |
| 868 MHz 11 el | 860 mm | 14.25 dBi | 14.44 dBi | 16.6 dB | 50.4 Ω | 36.2° × 39.6° |
| 905 MHz 6 el | 305 mm | 11.21 dBi | 11.07 dBi | 13.0 dB | 82.7 Ω | 49.2° × 60.2° |
| 905 MHz 11 el | 825 mm | 14.26 dBi | 14.44 dBi | 16.6 dB | 50.2 Ω | 36.2° × 39.4° |

(The DL6WU gain formula is only claimed for 2.2–39λ booms; for the 0.9λ designs the MoM agrees with it to 0.1 dB anyway. MoM directivity = gain for lossless aluminium elements.)

Element tables (mm; positions from the reflector; DE = plain dipole, resonated):

| Element | 433 MHz 6 el: position / length | 433 MHz 11 el | 868 MHz 6 el | 905 MHz 6 el | 905 MHz 11 el |
|---|---|---|---|---|---|
| Reflector | 0 / 336.2 | 0 / 336.2 | 0 / 167.3 | 0 / 160.4 | 0 / 160.4 |
| DE | 138 / 327.5 | 138 / 335.1 | 69 / 165.0 | 66 / 159.0 | 66 / 159.8 |
| D1 | 190 / 297.1 | 190 / 297.1 | 95 / 146.2 | 91 / 140.0 | 91 / 140.0 |
| D2 | 315 / 293.0 | 315 / 293.0 | 157 / 144.2 | 151 / 138.0 | 151 / 138.0 |
| D3 | 464 / 288.9 | 464 / 288.9 | 231 / 142.0 | 222 / 136.0 | 222 / 136.0 |
| D4 | 637 / 285.2 | 637 / 285.2 | 318 / 140.0 | 305 / 134.0 | 305 / 134.0 |
| D5–D9 | — | 831/281.9, 1039/279.1, 1257/276.7, 1485/274.5, 1724/272.6 | — | — | 398/132.4, 497/130.9, 601/129.7, 711/128.6, 825/127.7 |

Tolerance: DL6WU's ±0.003λ → ±2 mm at 433 MHz, ±1 mm at 905 MHz. A metal boom with elements bonded through it needs DL6WU's boom correction (≈ 11 mm per element for a 20 mm boom at 433 MHz, [Yagi page](../08-antennas/yagi-uda-and-log-periodic.md)).

### Level 2 — circular polarisation from two Yagis
Two identical Yagis at 90° on one boom, fed 90° apart, radiate CP on boresight. The harness modelled (ABCD in the script): each Yagi through a λ/4 of 75 Ω to a common junction, branch B additionally through a λ/4 of 50 Ω at the Yagi end (the 90° delay).

| Band | 75 Ω λ/4 (VF 0.66) | 50 Ω delay λ/4 (VF 0.66) | $Z_{in}$ at centre | S11 | AR over band |
|---|---|---|---|---|---|
| 433.5 MHz | 114.1 mm | 114.1 mm | 56.2 Ω | −24.6 dB | ≤ 0.27 dB (425–442 MHz) |
| 868.125 MHz | 57.0 mm | 57.0 mm | 56.2 Ω | −24.6 dB | ≤ 0.13 dB (860–876 MHz) |
| 905 MHz | 54.7 mm | 54.7 mm | 56.2 Ω | −24.6 dB | ≤ 0.23 dB (890–920 MHz) |

**The trap:** with the 6-el Yagis' native impedance the same harness gives

| Yagi $Z$ | Harness S11 | Branch amplitude ratio | AR |
|---|---|---|---|
| 73.4 Ω (433 MHz 6 el) | **−32.8 dB** | −3.33 dB | **3.3 dB** |
| 80.5 Ω (868 MHz 6 el) | **−47.5 dB** | −4.14 dB | **4.1 dB** |

The λ/4 50 Ω delay line transforms a non-50 Ω load (80.5 → 31 Ω), so the two branches present different impedances at the junction and take unequal power; the input match *improves* by coincidence while the polarisation degrades. A NanoVNA on the harness input cannot see this. Cures: (1) match each Yagi to 50 Ω first (trim/hairpin/gamma; check each alone for RL ≥ 20 dB), or (2) **offset one Yagi's elements λ/4 along the boom** and feed both through identical lines, so any common impedance error stays balanced.

AR sensitivity (script): 5° phase error → 0.76 dB; 10° → 1.5 dB; 20° → 3.1 dB; 1 dB amplitude imbalance alone → 1.0 dB. Receiving a rotating linear rocket antenna with a CP antenna of axial ratio AR gives a roll ripple equal to AR: 1 dB → −2.5…−3.5 dB; 3 dB → −1.8…−4.8 dB; 6 dB → −1.0…−7.0 dB ([polarisation](../08-antennas/antenna-polarization-and-circular-polarization.md), [PLF](../09-propagation-link-budget/polarization-mismatch-loss.md)).

### Level 2 — feeder and noise cascade
Coax loss from the fits in [coax & cables](../03-transmission-lines-matching/coax-and-cables.md) ($A = k_1\sqrt f + k_2 f$):

| Cable | 433 MHz, 15 m / 30 m | 868 MHz, 15 / 30 m | 905 MHz, 15 / 30 m |
|---|---|---|---|
| LMR-400 | 1.3 / 2.6 dB | 1.9 / 3.8 dB | 1.9 / 3.9 dB |
| LMR-240 | 2.6 / 5.1 dB | 3.7 / 7.3 dB | 3.7 / 7.5 dB |
| RG-58 | 4.3 / 8.6 dB | 6.6 / 13.1 dB | 6.7 / 13.5 dB |

Cascades (LNA = TQP3M9036-class, NF 0.45 dB, 19.8 dB; SAW 2.5 dB; module NF 6 dB; `rfcalc.noise.cascade`):

| Chain | NF 433 MHz | NF 905 MHz | Gain 433 / 905 |
|---|---|---|---|
| module at the end of 15 m RG-58 | 10.3 dB | 12.7 dB | −4.3 / −6.7 dB |
| module at the end of 15 m LMR-240 | 8.6 dB | 9.7 dB | −2.6 / −3.7 dB |
| LNA at the receiver end (after 15 m LMR-240) | 3.3 dB | 4.4 dB | 14.7 / 13.6 dB |
| **masthead: 0.3 dB jumper → LNA → SAW → 15 m LMR-240 → 4-way split (7 dB) → module** | **2.8 dB** | **3.3 dB** | 7.4 / 6.3 dB |
| masthead: limiter 0.3 dB → SAW → LNA → … (filter first) | 4.5 dB | 4.8 dB | 7.4 / 6.3 dB |
| masthead: limiter → LNA → SAW → 2nd LNA (1 dB, 18 dB) → 30 m LMR-240 → split → module | 0.9 dB | 0.9 dB | 22.9 / 20.5 dB |

The one-stage masthead chain meets G3. The two-stage chain is the lowest-noise option, but see the blocking table: 23 dB of net gain puts a pad-side −10 dBm signal at +13 dBm into the module.

### Level 2 — blocking and survival
Received power into the LNA input (free space; rocket/other transmitter antenna 2.15 dBi):

| Source | LNA input | Module input (one-stage chain) |
|---|---|---|
| own rocket on the pad, 33 dBm, 100 m, main lobe (10 dBi) | −20.0 dBm | −12.3 dBm |
| same at 30 m, main lobe | **−9.6 dBm** | −1.9 dBm |
| same at 30 m, side/back lobe (−5 dBi) | −24.6 dBm | −16.9 dBm |
| another team's 2 W at 433.9 MHz, 20 m, main lobe (in-band: the SAW does not help) | **−6.1 dBm** | +1.6 dBm |
| phone GSM-900 uplink 33 dBm peak, 2 m, 0 dBi (868/905 chain) | −4.6 dBm | +3.1 dBm |
| phone LTE-900 uplink 23 dBm, 2 m | −14.6 dBm | −6.9 dBm |
| own secondary (E220 30 dBm) on the pad, 30 m, main lobe (12 dBi) | −17.0 dBm | −9.3 dBm |

TQP3M9036: OIP3 +36 dBm → IIP3 ≈ +16 dBm; LCSC lists +20 dBm output P1dB → input P1dB ≈ 0 to +1 dBm. So nothing above compresses the one-stage chain, and nothing exceeds EBYTE's +10 dBm module rating — **but** a second gain stage or a closer pad distance does. Rules: pad checks with the Yagi pointed away or a 20–30 dB pad in line; a shunt Schottky limiter at the LNA input as a last resort (soft clamp: 0 dBm → −0.5 dBm, +20 dBm → +10 dBm; [switches & limiters](../06-rf-circuits/rf-switches-attenuators-limiters.md)); phones off/away from the 868/905 mast. In Singapore the 917–925 MHz band abuts 925–960 MHz cellular downlink and 880–915 MHz LTE uplink ([ground station design](../15-lora-ism-radios/ground-station-design.md)); a 902–928 MHz SAW passes part of that uplink.

### Level 2 — tracking the flight
Station C (5 km cross-range) and the 10 km trajectory of the link recipe:

| Phase | Azimuth span | Elevation span | Max az rate | Max el rate |
|---|---|---|---|---|
| Ascent (0.5 s … apogee) | 163–180° (17°) | 0–62° | 0.85 °/s | **6.3 °/s** (around burnout) |
| Descent | 137–163° | 62° → 0° | 0.08 °/s | 0.27 °/s |

Pointing loss model: elliptical Gaussian beam, $L = 12[(\Delta az\cos el/\theta_{az})^2 + (\Delta el/\theta_{el})^2]$ dB ([ground station design](../15-lora-ism-radios/ground-station-design.md)).

| Strategy | 3-el (59° × 84°) | 6-el (50° × 61°) | 11-el (36° × 40°) |
|---|---|---|---|
| (a) fixed at the optimum (az ≈ 172°, el 31°): worst / median | 3.4 / 2.5 dB | **4.9 / 3.6 dB** | 9.1 / 6.7 dB |
| (b) tablet pointing, 1 s latency, 5° rms hand error: p95 / max | 0.4 / 2.0 dB | **0.6 / 2.8 dB** | 1.2 / 5.2 dB |
| (b) 2 s latency, 10° rms: p95 / max | 1.7 / 7.5 dB | 2.5 / 10.7 dB | 4.9 / 20.1 dB |
| (c) G-5500-class rotator (2.7°/s el), 0.5 s latency: max error / loss | 17.9° / 1.1 dB | 17.9° / 1.6 dB | 17.9° / 2.9 dB |
| (c) fast DIY rotator (20°/s): max error / loss | 3.1° / 0.0 dB | 3.1° / 0.0 dB | 3.1° / 0.1 dB |

(Latency here is only the *pointing* delay: GNSS fix age + telemetry + display + human. The rotator rates are Yaesu's published rotation times for the G-5500DC — 58 s per 360° azimuth, 67 s per 180° elevation [3] — not measured.)

**GNSS-driven pointing.** Convert the rocket's downlinked latitude/longitude/height and the station's own fix to local east–north–up: $E \approx R_N\cos\phi_0\,\Delta\lambda$, $N \approx R_M\,\Delta\phi$, $U = \Delta h$ (flat-earth is adequate: the Earth's curvature over 15 km drops the target by $d^2/2R$ = 18 m, 0.07°). Then $az = \mathrm{atan2}(E, N)$, $el = \mathrm{atan2}(U, \sqrt{E^2+N^2})$. Between fixes, extrapolate with the downlinked velocity. Before GNSS lock (or if the GNSS frame is lost), fall back to the pre-computed nominal trajectory.

*Latency-compensated pointing (velocity extrapolation vs a constant-acceleration Kalman predictor, simulated) and RSSI step-track accuracy: [radar tracking § RF-telemetry ground-station tracking](../11-radar/radar-tracking-monopulse-and-trackers.md).*

### Level 3 — where the models break
- Low-elevation lobing: during the first seconds and after landing the ground reflection under a 2–3 m mast adds ±6 dB lobes in elevation ([two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md)); the Gaussian beam model ignores it.
- The MoM model is of isolated Yagis; the second Yagi of a crossed pair, the mast, the harness coax and the operator's body all perturb pattern and impedance. Measure.
- Blocking levels assume free space and main-lobe coupling; near-field coupling at < 10 m can be larger or smaller.
- Diversity gains assume the stated correlation; losses caused at the rocket (tail null, plume, a brown-out) are fully correlated across stations.

## Design equations & rules of thumb
| Rule | Value |
|---|---|
| DL6WU gain | $G \approx 9.2 + 3.39\ln(B/\lambda)$ dBd; 6 el ≈ 11.2 dBi, 11 el ≈ 14.2 dBi |
| Element tolerance | ±0.003λ (±2 mm at 433 MHz, ±1 mm at 905 MHz) |
| λ/4 in VF-0.66 coax | 114 mm at 433.5 MHz, 57 mm at 868 MHz, 55 mm at 905 MHz |
| CP harness | 2 × λ/4 75 Ω in parallel + λ/4 50 Ω delay on one branch → ≈ 56 Ω; **Yagis must be 50 Ω** |
| AR vs phase error | ≈ 0.15 dB per degree near 90° |
| Pointing loss | $12(\theta_e/\theta_{3dB})^2$ dB; ≤ 1 dB needs $\theta_e \le 0.29\,\theta_{3dB}$ |
| Peak elevation rate | $\approx v/D$ early, here 6.3 °/s at 5 km |
| Coax before the LNA | adds dB-for-dB to NF |
| Net gain before the module | ≤ (module damage level − worst pad-side signal) — ≈ 10–20 dB |
| Diversity | $P_{both} = p_1p_2 + \rho\sqrt{p_1(1-p_1)p_2(1-p_2)}$ |
| IQ storage | $f_s \times 2 \times$ bits/8 bytes/s: 2 MB/s at 1.024 MS/s 8-bit |

## Worked examples

### 1. The chosen station, end to end (433 MHz branch; 868/905 MHz identical in structure)
1. 6-el DL6WU Yagi ×2, crossed ("X" orientation, ±45° to the vertical mast so neither element set is parallel to the mast), elements 6 mm aluminium, 20 × 20 mm fibreglass/wood boom, DE split at the centre in a small ABS box.
2. Each DE matched to 50 Ω (trim DE + hairpin, or gamma), with a ferrite-sleeve choke balun on the feed ([baluns](../08-antennas/antenna-matching-and-baluns.md)); each Yagi checked alone: RL ≥ 20 dB at 433.125 MHz.
3. Harness: two 114 mm RG-316/RG-59-class 75 Ω λ/4 sections to a tee (junction), plus a 114 mm 50 Ω delay section at one Yagi (measure VF of *your* cable with the NanoVNA first; VF 0.66 is nominal).
4. Masthead box (die-cast): SMA in → (optional limiter) → TQP3M9036 LNA → B39431B3710 SAW (433.00–434.71 MHz, ≤ 2.7 dB, 50 Ω) → SMA out; DC via bias-tee from the coax; DC-blocking capacitor at the LNA input (a hairpin/folded DE is a DC short).
5. 15 m LMR-240 to the tent; bias-tee injects 5 V; 4-way splitter → E22 module, SX1268 dev board, RTL-SDR, spare/tinySA.
6. NF 2.8 dB (433 MHz); with 11.2 dBic CP and a linear rocket antenna the effective gain is 8.2 dB. Relative to the link recipe's assumption (2.0 dB NF with a 2-way split, 10 dBic CP), this station is 0.8 dB noisier and 1.2 dB higher gain — net +0.4 dB; margins there stand.

### 2. Fixed backup station
Same antenna, fixed at az/el of the mid-ascent direction from *its* site (compute with the script's section 5 for its coordinates). Worst ascent loss 4.9 dB, median 3.6 dB for the 6-el. Its value is diversity (a different look angle at the tail null), not gain.

### 3. Recovery
After landing, raise the mast to 6 m (landed range 7.5 → 13 km for the 433 MHz 33 dBm link with this masthead-LNA station in the link recipe's flat-earth model, 2.1 → 3.6 km at 10 mW e.r.p.; the KB's other landed-range assumption sets are compared in [09 Example E](../09-propagation-link-budget/link-budget-methodology.md#example-e--landed-rocket-the-case-that-actually-limits-recovery); a bare module on a 2 m tripod gets only 5.6 km / 1.7 km — [LoRa sensitivity](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md); +6 dB per doubling of height) and switch the ground receiver to the landed mode. Then walk in with a handheld 3-el Yagi (59° × 84°, 242 mm boom, [Yagi page example 3](../08-antennas/yagi-uda-and-log-periodic.md)) using peak-and-null direction finding. Budget **≈ 8.5 dBi** for it: the 9.2 dBi MoM figure (quoted here before 2026-10-14) needs a separate match for its ≈ 11 Ω feed, while a directly 50 Ω-fed, band-constrained 3-element design reaches 8.55 dBi in NEC ([NEC modelling Example 4](../16-simulation-tools/nec-antenna-modelling.md); a simulation result, to be measured with the gain-comparison method of [antenna measurement](../08-antennas/antenna-measurement.md)).

## Part selection
Prices: LCSC qty 1–9, JLCPCB parts DB snapshot 2026-07-08 (USD); "est." = estimate.

| Function | Part | Key specs | Price | Notes |
|---|---|---|---|---|
| LNA 433/868/905 | Qorvo **TQP3M9036** (C920261) | 50 MHz–2 GHz, NF 0.45 dB, 19.8 dB, OIP3 +36 dBm, 3.3–5.25 V | $2.84 | [LNA/PA MMICs](../18-components-parts/lna-pa-gain-block-mmics.md); stable-by-layout, follow the EVB |
| 2nd stage (optional) | Mini-Circuits **PGA-103+** (C3008207) | 50 MHz–4 GHz, ≈ 18 dB, very linear | $2.41 | only with a switchable pad for pad operations |
| SAW 433 MHz | TDK/RF360 **B39431B3710U410** (C2649317) | passband 433.00–434.71 MHz, IL ≤ 2.7 dB, 50 Ω, 3 × 3 mm | $0.98 | covers the whole SRD band |
| Filter 868 MHz | Murata **LFD21868MMF1D386** (C910735, LTCC) or TDK B39871B3744H110 (SAW 868.3 MHz, 600 kHz BW, 290 Ω // 1.3 pF — needs matching; 868.125 MHz sits on its lower edge) | 3.3 dB / 3.7 dB | $0.37 / $1.29 | LTCC is wide (little rejection of 880–915 MHz); the narrow SAW needs an L-C match |
| SAW 902–928 MHz | **B39921B3728U410** (C2650953, 3 × 3 mm, 26 MHz BW, 2.2 dB) or TA0281A (C596627) | 50 Ω | $1.92 / $0.93 | IREC band |
| Limiter | anti-parallel Schottky pair (e.g. HSMS-286x/SMS7630-class) | soft clamp | < $0.5 | adds ≈ 0.3 dB before the LNA |
| Bias-tee | DIY (≥ 1 µH choke with SRF above band + 100 pF blocks) or commercial | 5 V, ≤ 100 mA | est. $10 | DC drop on 15 m LMR-240 ≈ 30 mV at 60 mA (estimated loop resistance) |
| Coax | LMR-240 15 m with N or SMA | 17.0 dB/100 m at 433 MHz | est. $35 | LMR-400 for 30 m runs |
| Splitter | 4-way Wilkinson, 400–1000 MHz | 6.5–7 dB | est. $20 | or two 2-way |
| Receivers | flight-identical EBYTE module; SX1268/SX1262 dev board (RadioLib); RTL-SDR Blog V3/V4L | — | est. $10 / $20 / $40 | V4 is end of line ([SDR survey](../14-sdr-dsp/sdr-hardware-survey.md)) |
| Mast/tripod | 6 m telescopic fibreglass (non-metallic top section) | — | est. $60–120 | guy lines |
| Rotator (optional) | Yaesu G-5500DC class or DIY stepper az/el (≥ 20°/s) | — | ≈ $700+ / est. $150 | see tracking table |

## Block diagram
```
  [433 crossed 6-el Yagi X-mount]            [868/905 crossed 6-el Yagi X-mount]
     |  Yagi A      Yagi B                       (same structure)
     |  75R L/4     75R L/4 + 50R L/4 delay
     +----tee (56 ohm)----+
            |
   masthead box: [limiter]-[DC blk]-[TQP3M9036]-[SAW B3710]---+  (5 V from bias-tee)
            |                                                  |
        15 m LMR-240 ------------------------------------------+
            |
   tent: bias-tee (5 V in) -> 4-way splitter -> E22 UART rx  -> logger (raw bytes + RSSI + GNSS time)
                                             -> SX1268 board -> logger (SNR, FEI, RSSI)
                                             -> RTL-SDR       -> IQ file 1.024 MS/s (+ start time from PPS)
                                             -> tinySA / spare
   GNSS receiver (PPS, position) -> laptop clock; tablet app: az/el from downlinked GNSS + station fix
```

## Layout notes (masthead LNA board)
- 2-layer or 4-layer JLC board, 50 Ω CPWG in/out, solid ground under the RF path, stitching vias every ≤ λ/20 of the highest frequency the LNA has gain at (the TQP3M9036 has gain to ≈ 2 GHz: ≤ 7 mm) ([stackups](../13-pcb-rf-layout-emc/stackups-and-materials.md), [grounding](../13-pcb-rf-layout-emc/grounding-and-return-paths.md)).
- Follow the vendor EVB exactly for the bias choke, decoupling and any stability resistor; broadband LNAs with 20 dB at 100 MHz oscillate on sloppy layouts ([amplifier stability](../06-rf-circuits/amplifier-stability-and-biasing.md), [LNA recipe](lna-design-walkthrough.md)).
- Bias-tee choke SRF above the band (check with the NanoVNA, [inductors at RF](../04-real-components-hf/inductors-at-rf.md)); a 100 nF + 100 pF decoupling pair at the LNA supply; TVS on the DC line.
- Die-cast box, SMA bulkheads, drain hole at the bottom, self-amalgamating tape on outdoor connectors.

## Simulation plan
| What | Tool | Pass |
|---|---|---|
| Single Yagi gain/pattern/Z | `tools/verify/ant_yagi.py` MoM (done above) and independent NEC-2 (4nec2 or PyNEC) ([NEC modelling](../16-simulation-tools/nec-antenna-modelling.md)) | NEC and MoM agree within 0.3 dB and 5 Ω |
| Crossed pair on the boom, with mast | NEC-2 wire model incl. the second Yagi and a mast stub | boresight AR ≤ 1.5 dB, gain within 0.5 dB of the single Yagi |
| Harness | `proj_ground_station.py` §2 (ABCD); cross-check with scikit-rf network cascade ([Python RF toolkit](../16-simulation-tools/python-rf-toolkit.md)) | S11 ≤ −15 dB and AR ≤ 1 dB with the *measured* Yagi impedances |
| LNA board | vendor S2P in scikit-rf/Qucs-S + K-factor ([stability](../06-rf-circuits/amplifier-stability-and-biasing.md)) | K > 1 from 10 MHz to 6 GHz with the real bias network |
| Tracking | `proj_ground_station.py` §5 with the team's 6-DOF trajectory and site coordinates | p95 pointing loss ≤ 1.5 dB (G5) |

## Build, bring-up and test plan (pass/fail fixed in advance)
| # | Test | Method | Pass |
|---|---|---|---|
| S1 | Coax VF and loss | NanoVNA: open-ended stub resonance → VF; S21 of the 15 m run ([NanoVNA](../17-test-measurement/nanovna-librevna-practical.md)) | loss within ±0.5 dB of the table |
| S2 | Each Yagi alone | NanoVNA S11 at the feed through the choke, antenna 2 m above ground pointing up | RL ≥ 20 dB at the channel after matching; record the trim |
| S3 | Harness + pair | S11 at the harness input | ≤ −15 dB over the channel |
| S4 | Axial ratio | rotate a linear source (dipole on a low-power 10 mW beacon, or a signal generator) at 30–100 m ([OTA testing](../17-test-measurement/antenna-range-ota-testing.md)); record received power vs source angle. **In Singapore the beacon must be in a legal band**: 433.05–434.79 MHz at ≤ 10 mW e.r.p.; test the 900 MHz Yagis at 866–869 MHz (≤ 500 mW e.r.p.) or 917–925 MHz (≤ 100 mW e.r.p., ≤ 1 % duty) — **905 MHz (IREC, US 902–928 MHz) is not a Singapore band**; a Yagi pattern measured at 917–925 MHz is within the 890–920 MHz match of the 905 MHz design, otherwise use the 868 MHz Yagi | max/min ≤ 1.5 dB (prediction 0.3–1 dB with 50 Ω-matched Yagis) |
| S5 | Gain | gain transfer against a reference dipole at 30–100 m, ground-reflection range geometry ([antenna measurement](../08-antennas/antenna-measurement.md)); same band rule as S4 (no radiated test at 905 MHz in Singapore) | 11.2 ± 1 dBi per Yagi (linear), ≈ 8 dB CP-vs-linear-dipole |
| S6 | LNA board | S21, S11, NF (Y-factor with a noise source, [NF measurement](../17-test-measurement/noise-figure-measurement.md)), P1dB with a signal generator + attenuator | gain 17–20 dB, NF ≤ 1 dB at 433/905 MHz, no oscillation 10 MHz–3 GHz on the tinySA with input open and shorted |
| S7 | Whole chain | radiated sensitivity test of the link recipe (T8) | P2/P3 of the link recipe |
| S8 | Tracking rehearsal | a 10 mW beacon on a drone at 100–300 m altitude or a car on a road; tablet app pointing | operators keep p95 loss ≤ 1.5 dB (RSSI vs beacon's GNSS) |
| S9 | Field endurance | full station on battery 4 h, logging | no dropouts; log files grow; clock drift < 1 ms vs PPS |

## Regulatory check
- Receive-only equipment needs no transmit licence in Singapore ([IMDA](../19-regulations-safety/singapore-imda-rules.md)); the SDR, modules and LNA are receivers.
- **Test beacons are transmitters**: at 433 MHz ≤ 10 mW e.r.p. (antenna gain counts — a beacon into one of these Yagis at 10 dBm would be 9 dB over), ≤ 10 % duty; at 866–869 MHz ≤ 500 mW e.r.p.; at 917–925 MHz ≤ 100 mW e.r.p. and ≤ 1 % duty. **902–928 MHz (the 905 MHz IREC branch) is a US band only**: radiate it only at IREC or into a dummy load/shielded box in Singapore
- Any ground uplink (e.g. an RTK-corrections bridge) needs its own legal basis; a Yagi multiplies its e.r.p.
- At IREC, pit-area and range transmission rules apply to any beacon ([competitions](../19-regulations-safety/international-rules-for-competitions.md)).

## Pre-registered predictions
| ID | Prediction | Tolerance | Interpretation if outside |
|---|---|---|---|
| Q1 | 433 MHz 6-el Yagi, plain-dipole DE as built to the table: resonant $Z$ ≈ 73 Ω (RL ≈ 14 dB) before matching | ±15 Ω | element diameter/boom coupling differs from the model |
| Q2 | Gain 11.2 dBi (each Yagi, linear) by gain transfer | ±1 dB | construction/ground-reflection range error |
| Q3 | F/B 13 dB (6 el), 16 dB (11 el) | ±3 dB | mast/feed-line pattern distortion |
| Q4 | CP axial ratio on boresight: ≤ 1 dB with 50 Ω-matched Yagis; ≈ 3–4 dB if the 6-el is connected unmatched to the harness | ±1 dB | harness VF error, element misalignment |
| Q5 | Chain NF 2.8 dB (433) / 3.3 dB (905) with 4-way split | ±0.7 dB | LNA NF at 433 MHz differs from the 0.45 dB datasheet figure |
| Q6 | Tablet-steered 6-el during the flight: p95 pointing loss ≤ 0.6 dB, max ≤ 3 dB | ×2 | operator latency larger than 1 s |
| Q7 | Fixed backup station 6-el: ascent RSSI at most 5 dB below the tracked station after correcting for range and look angle | ±3 dB | pointing solution or trajectory differs from the model |

## Risks and common failure modes
| Failure | Symptom | Prevention |
|---|---|---|
| LNA oscillation | noise floor jumps, spurs, RSSI high with no signal | EVB layout, K-factor check, S6 open/short test |
| Bias-tee DC into a receiver without DC block | receiver input destroyed | DC-block at every receiver input; check with a multimeter before connecting |
| DC short through a folded/hairpin DE shorting the bias supply | LNA dead, bias-tee hot | DC-blocking cap at the LNA input |
| Harness VF wrong (different coax than assumed) | AR high, roll ripple | measure VF (S1) |
| Crossed Yagi mounted "+" on a metal mast | pattern/impedance of the vertical set distorted | "X" mount, non-metallic top section |
| Water in connectors | slow loss increase, intermittent | tape, drip loops, drain holes |
| Pad overload | module resets, LNA damage | 100 m rule, pad-check attenuator, limiter |
| Operator points at the wrong sky | long dropouts | tablet az/el from GNSS; rehearse (S8) |
| SDR records nothing | empty file after the flight | check file growth every minute; second recorder |

## Cost estimate (per station, both bands)
| Item | Cost (USD, est.) |
|---|---|
| Aluminium rod, booms, hardware, harness coax for 2 crossed 6-el Yagis | 40–70 |
| 2 masthead LNA/SAW boards (JLC-assembled, 5 pcs) + boxes + connectors | 60–100 |
| 2 × 15 m LMR-240 with connectors, 2 bias-tees, 2 splitters | 110–150 |
| Receivers: 2 modules, 2 SX126x boards, 2 RTL-SDRs | 140 |
| Fibreglass mast + tripod + guys | 60–120 |
| GNSS PPS receiver, 12 V battery, cables | 60 |
| **Station total** | **≈ 470–640** (rotator option + 150 DIY / 700 commercial) |

## Practical notes
- Label every coax with its measured loss and VF; the budget depends on it.
- Put a small "sniffer" (the tinySA on the spare splitter port) on screen during pad operations: you see the rocket's carrier, any interferer and receiver saturation at once ([spectrum analyzers](../17-test-measurement/spectrum-analyzers.md)).
- The tablet app should show az/el *and* the time since the last GNSS frame; stale data is worse than none.
- Log antenna pointing (if a rotator/IMU on the boom) with the packets — it lets you separate pointing loss from link loss post-flight.
- Survey the site noise floor for an hour with the SDR (ambient-RSSI command on the EBYTE module too) before choosing channels.

## Common mistakes & misconceptions
- **"More elements are always better."** The 11-el gives 3 dB on boresight and loses 9 dB if you cannot point it; the 6-el is the better field antenna for this flight.
- **"The harness S11 is −40 dB, so the CP is perfect."** A mismatched Yagi behind a λ/4 delay line produces an unequal split with an excellent input match (AR 4 dB at S11 −47 dB in the example).
- **"RHCP vs LHCP matters for my rocket."** Not for a linear rocket antenna — both senses receive it at −3 dB; it matters for GNSS/satellites.
- **"A rotator will track the boost."** A G-5500-class elevation drive (2.7°/s) lags the 6.3°/s boost demand by up to 18°.
- **"Put the SAW first to protect the LNA."** That adds its loss to the NF (2.8 → 4.5 dB here); do it only for real out-of-band blockers — in-band 433 MHz transmitters pass the SAW anyway.
- **"More LNA gain fixes the splitter loss."** It does, and it also pushes pad-side signals past the module's damage rating.
- **Mounting the Yagi elements horizontal** when the rocket antenna is vertical on the pad: −20 dB or worse.

## How to simulate / verify
- `python3 tools/verify/proj_ground_station.py` (≈ 2 min; `FAST=1` for cached MoM results) — every number above.
- `python3 tools/verify/ant_yagi.py` — the DL6WU algorithm and MoM; `lora_ground_station.py` — generic cascades, Fresnel radii, pointing loss.
- `python3 tools/verify/proj_lora_link.py` — the trajectory and link budgets this station is designed for.

## Open questions / gaps
- NF of the TQP3M9036 at 433 MHz (datasheet NF curve not read here; 0.45 dB is the headline figure).
- Measured AR of a real crossed 6-el Yagi (Q4) and mast interaction — no data yet.
- The rotator slew figures are manufacturer rotation times, unverified; affordable fast az/el rotators were not surveyed.
- Singapore cellular deployment near candidate test sites (blocking of the 868/905 chain) not surveyed.

## Sources
1. This KB, [Yagi-Uda and log-periodic](../08-antennas/yagi-uda-and-log-periodic.md) and `tools/verify/ant_yagi.py` (W1-A6) — DL6WU algorithm (G. Hoch, *VHF Communications* 3/1982, via DL6WU.BAS by KY4Z/W6NBI/G3SEK), MoM, tolerances, boom correction, 3-el design. (internal; design data)
2. This KB, [LoRa ground-station design](../15-lora-ism-radios/ground-station-design.md) — cascade logic, pointing-loss approximation, diversity, recording, Singapore cellular adjacency. (internal)
3. Yaesu, G-5500DC product page / instruction manual — rotation times 58 s (360° az) and 67 s (180° el), 1° backlash. https://yaesu.com/product-detail.aspx?Model=G-5500DC&CatName=Rotators (manufacturer — via search summary)
4. This KB, [Coax and cables](../03-transmission-lines-matching/coax-and-cables.md) — attenuation fits for LMR-400/240/195, RG-58, RG-174. (internal; manufacturer data)
5. This KB, [Antenna polarization & CP](../08-antennas/antenna-polarization-and-circular-polarization.md), [polarisation mismatch](../09-propagation-link-budget/polarization-mismatch-loss.md) — crossed-Yagi CP, AR, PLF. (internal)
6. This KB, [LNAs, PAs, gain blocks](../18-components-parts/lna-pa-gain-block-mmics.md) — TQP3M9036, PGA-103+ specs and LCSC numbers. (internal; datasheets)
7. This KB, [RF switches, attenuators & limiters](../06-rf-circuits/rf-switches-attenuators-limiters.md) — Schottky limiter behaviour. (internal)
8. TDK/EPCOS B39431B3710U410 (B3710) SAW filter — passband 433.00–434.71 MHz, IL ≤ 2.7 dB, 50 Ω, DCC6C 3 × 3 mm (distributor listings of the datasheet: Newark/Farnell). (datasheet — via search summary)
9. TDK/EPCOS B39871B3744H110 (B3744) — 868.3 MHz, 600 kHz 3 dB BW, 290 Ω // 1.3 pF, IL 3.7 dB (distributor summary). (datasheet — via search summary)
10. JLCPCB/LCSC parts database snapshot 2026-07-08 — prices/stock for TQP3M9036, PGA-103+, B3710, B3728, TA0281A, LFD21868MMF1D386. (distributor data)
11. This KB, [SDR hardware survey](../14-sdr-dsp/sdr-hardware-survey.md) — RTL-SDR V3/V4L status, NF, sample rates. (internal)
12. J. Tapparel et al., gr-lora_sdr (SPAWC 2020) — offline LoRa decoding, via [software demodulation](../14-sdr-dsp/software-demodulation.md). (peer-reviewed + code)
