---
title: Recipe — Phased-array starter build (KrakenSDR 5-element UCA for rocket-recovery direction finding at 433/868 MHz, ADI Phaser 8-element 10 GHz beamforming lab) and an honest array-vs-Yagi verdict
domain: 20-projects-recipes
slug: phased-array-starter-build
tags: [recipe, phased-array, krakensdr, uca, direction-finding, doa, music, bartlett, calibration, noise-source, multipath, triangulation, adi-phaser, cn0566, adar1000, ula, array-factor, taper, grating-lobes, ground-station, rocket-recovery, pre-registration]
prerequisites:
  - ../12-phased-arrays/array-factor-linear-arrays.md
  - ../12-phased-arrays/adaptive-beamforming-doa.md
  - ../12-phased-arrays/array-calibration.md
  - ../12-phased-arrays/diy-phased-array-projects.md
related:
  - ../12-phased-arrays/beam-steering-grating-lobes.md
  - ../12-phased-arrays/tapering-sidelobe-control.md
  - ../12-phased-arrays/beamforming-architectures.md
  - ../14-sdr-dsp/sdr-hardware-survey.md
  - ground-station-tracking-yagi.md
  - sdr-receiver-build.md
  - fmcw-radar-build.md
  - beginner-project-ladder.md
level: intermediate
confidence: medium
last_updated: 2026-10-02
---

# Recipe — Phased-array starter build and the array-vs-Yagi verdict

Two first arrays chosen for what Space Bar would actually use: (1) a **KrakenSDR 5-element circular array**
that finds the bearing of the landed rocket's LoRa beacon at 433 or 868 MHz from two or more points, and (2)
the **ADI Phaser** 8-element 10 GHz array as a bench lab for steering, tapering and grating lobes. It ends with
an honest comparison of an electronically steered ground station against the [tracked Yagi](ground-station-tracking-yagi.md).
Theory and broader options: [DIY phased-array projects](../12-phased-arrays/diy-phased-array-projects.md).
Numbers: `python3 tools/verify/proj_phased_array.py` (geometry, Monte-Carlo DOA with calibration error and
multipath, triangulation, snapshot budgets, Phaser array factor, array sizing).

## Questions this page answers
- What is the simplest coherent array I can build, and what does it teach?
- How big must a 5-element circular array be at 433 MHz and 868 MHz?
- How accurate are KrakenSDR bearings, and what limits them in the field — SNR, calibration or multipath?
- How precisely must the antenna cables match?
- How well can two direction-finding stations locate a landed rocket?
- Does a single LoRa packet give enough samples for DOA?
- What will I see when I steer and taper the ADI Phaser?
- Should my telemetry ground station be a phased array instead of a tracked Yagi?

## TL;DR
- **KrakenSDR UCA**: 5 elements at 0.4λ spacing → radius **23.6 cm (433 MHz) / 11.8 cm (868 MHz)**; Bartlett spectrum highest sidelobe −5.5 dB — **unambiguous over 360°** (a linear array cannot tell front from back).
- **Bearing accuracy** (Monte-Carlo, 1000 snapshots, true bearing 37°): noise-limited **0.12° rms at 10 dB SNR per element**, 0.41° at 0 dB — but **residual channel phase error dominates**: 2° rms → 0.65°, 5° → 1.4°, 10° → 2.9°. KrakenSDR's noise source calibrates only from its switch onward; **1 cm of cable-length mismatch = 7.9° at 433 MHz, 15.8° at 868 MHz** (VF 0.66) — cut the five cables to ≤ 2–3 mm or calibrate on a beacon at a known bearing.
- **Coherent multipath** (ground or building reflection, same waveform): −10 dB → 2.5° rms, −6 dB → 4.4°, −3 dB → 7.4° with 21 % outliers > 10° — MUSIC does not help with a single coherent reflection; site the array high and clear.
- **Triangulation**, stations 2 km apart, rocket 5 km away: 1° bearings → **220 m median** (90 % < 520 m); 2° → 460 m; 5° → 1.1 km. Good enough to start walking with the handheld Yagi.
- **Snapshots are free**: one 32-byte SF9/125 packet (247 ms) gives ≈ 62 000 complex samples at 2× BW; SF11 ≈ 250 000. DOA accuracy is set by SNR and calibration, not sample count; gate the processing on packet bursts.
- **ADI Phaser** (8 elements, 14 mm = 0.479λ at 10.25 GHz): no grating lobes for any scan; HPBW 13.3° broadside, 15.5° at 30°, 30.7° at 60°; uniform sidelobes −12.8 dB; a cos²-on-pedestal (0.3) taper → −25.1 dB with HPBW 16.5° — every textbook trade visible on the bench.
- **Array vs Yagi for telemetry**: 14 dBi at 433 MHz is ≈ 7 elements (6 dBi elements) on a 92 cm square plus 7 coherent channels and calibration — vs one 11-element Yagi (14.2 dBi, 1.72 m boom, one connector). The link has 30–50 dB of margin and the rocket moves ≤ 6.3°/s in elevation from 5 km. **Use the Yagi for telemetry; use the array for recovery DF.** Electronic steering earns its keep at 2.4/5.8 GHz (14 dBi in 16 / 7 cm squares) for high-rate links.

## Intuition (no math)
A plane wave arriving at several antennas reaches each at a slightly different time; with all receivers sharing one clock, those time differences become phase differences, and the pattern of phases across the array points back at the source. Direction finding is matching the measured phase pattern against the patterns you would get from every possible direction. Two things spoil the match: the receivers' own phase offsets (cables, filters, synthesisers — "calibration"), and echoes from the ground or buildings that add a second, coherent phase pattern. A circular array sees all around; a line array confuses a source in front with its mirror image behind. Beamforming is the same arithmetic run in reverse: choose weights so the array listens (or transmits) in one direction.

## Requirements
| ID | Requirement | Value |
|---|---|---|
| P1 | DF band | 433.05–434.79 MHz and 866–869 MHz (the rocket's two links) |
| P2 | Bearing accuracy | ≤ 2° rms in a clear site, 360° unambiguous |
| P3 | Localisation | ≤ 500 m (90 %) at 5 km with two stations |
| P4 | Signal | LoRa bursts (SF9–SF11 landed mode, ≥ every 5–10 s), SNR per element ≥ 0 dB |
| P5 | Portability | one person, battery, car roof or tripod |
| P6 | Lab array | visible steering/taper/grating-lobe behaviour with Python control |

## Architecture options and trade study
| Option | Coherent channels | Band | Cost (est.) | Calibration | Verdict |
|---|---|---|---|---|---|
| **KrakenSDR + 5 whips/dipoles (UCA)** | 5 (shared clock, internal noise source) | 24–1766 MHz | ≈ US$750 + antennas | automatic receiver cal; cables/antennas manual | **DF choice** |
| 2 × RTL-SDR on a shared clock + noise source | 2 | 24–1766 MHz | ≈ US$100 | DIY | interferometer lesson only ([DIY arrays](../12-phased-arrays/diy-phased-array-projects.md)) |
| Pluto Rev C/D (2 RX) | 2 | 325 MHz–3.8 GHz | ≈ US$250 | DIY | second channel not production-tested |
| USRP B210 | 2 | 70 MHz–6 GHz | ≈ US$2400 | DIY | lab-grade |
| **ADI Phaser (CN0566)** | 8 analog (2 × ADAR1000) → Pluto | 10.0–10.5 GHz | ≈ US$2875 | REV / on-off (analog) | **beamforming lab** |
| FR-4 2.4/5.8 GHz patch array + Butler matrix | 4 fixed beams | 2.4/5.8 GHz | ≈ US$50–150 | none (fixed) | high-rate link experiments |

## The math — design calculations

### Level 1 — geometry and steering vectors
UCA element positions $\mathbf p_n = r(\cos\phi_n, \sin\phi_n)$, $\phi_n = 2\pi n/N$; chord spacing $s = 2r\sin(\pi/N)$ → $r = s/(2\sin(\pi/N))$. Azimuth steering vector (elevation 0): $a_n(\theta) = e^{jk(x_n\cos\theta + y_n\sin\theta)}$. Bartlett $P(\theta)=\mathbf a^H\hat R\mathbf a$; MUSIC $P(\theta) = 1/\|\mathbf E_n^H\mathbf a\|^2$ ([adaptive beamforming & DOA](../12-phased-arrays/adaptive-beamforming-doa.md)).

| Band | λ | r (s = 0.4λ) | Diameter | Bartlett max sidelobe |
|---|---|---|---|---|
| 433.125 MHz | 69.2 cm | 23.6 cm | 47.1 cm | −5.5 dB |
| 868.125 MHz | 34.5 cm | 11.8 cm | 23.5 cm | −5.5 dB |

### Level 2 — what limits a field bearing
Monte-Carlo (`proj_phased_array.py` §2), 200 trials each, Bartlett and MUSIC (identical for one source, as theory predicts — [DOA](../12-phased-arrays/adaptive-beamforming-doa.md)):

| SNR/element | Residual phase error (rms) | Coherent multipath | Bearing error rms |
|---|---|---|---|
| 10 dB | 0° | none | 0.12° |
| 0 dB | 0° | none | 0.41° |
| 10 dB | 2° | none | 0.65° |
| 10 dB | 5° | none | 1.38° |
| 10 dB | 10° | none | 2.94° |
| 10 dB | 2° | −10 dB from 200° | 2.50° |
| 10 dB | 2° | −6 dB from 200° | 4.38° |
| 20 dB | 2° | −3 dB from 200° | 7.43° (21.5 % > 10°) |

Cable mismatch before the KrakenSDR's calibration switch (phase = 360° ΔL/(VF λ)): 0.5 cm → 3.9° (433 MHz) / 7.9° (868 MHz); 1 cm → 7.9° / 15.8°; 2 cm → 15.8° / 31.6° (VF 0.66). The KrakenSDR documentation's "cables equal to within 1 cm below ~900 MHz" therefore still leaves ≈ 8–16° — use 2–3 mm matching or a beacon calibration ([array calibration](../12-phased-arrays/array-calibration.md)).

### Level 2 — localisation
Two stations 2 km apart, target 5 km away near broadside (4000 trials): bearing σ 1° → median error 220 m (90th percentile 522 m); 2° → 459 m (1111 m); 5° → 1106 m (3462 m). Cross-range 1σ at 5 km per degree ≈ 87 m; the larger numbers come from the triangle's geometry (GDOP). A third station or a drive-by second fix shrinks it.

### Level 2 — the Phaser as a lab
d = 14 mm = 0.479λ at 10.25 GHz → grating-lobe-free to ±90° ([beam steering](../12-phased-arrays/beam-steering-grating-lobes.md)).

| Steer | Taper | HPBW | Highest sidelobe |
|---|---|---|---|
| 0° | uniform | 13.3° | −12.8 dB |
| 30° | uniform | 15.5° | −12.8 dB |
| 60° | uniform | 30.7° | −12.8 dB |
| 0° | cos² on 0.3 pedestal | 16.5° | −25.1 dB |
(Beam broadening ≈ 1/cos θ_s; taper trades 24 % beamwidth for 12 dB lower sidelobes — [tapering](../12-phased-arrays/tapering-sidelobe-control.md).)

### Level 3 — where this breaks
- Elevation: the steering model assumes the source in the array plane. A rocket hanging at 300 m altitude 2 km away is at 8.5° elevation — the azimuth error from ignoring it is small for a UCA ($\cos$ factor) but grows for nearby high targets.
- Polarisation: vertical monopoles/dipoles on the array vs a lying rocket's horizontal antenna → 10–20 dB of polarisation loss and more multipath sensitivity.
- Mutual coupling between elements 0.4λ apart distorts the steering vectors by a few degrees unless calibrated (self-calibration methods in [array calibration](../12-phased-arrays/array-calibration.md)).
- LoRa bursts: process only samples inside detected packets; between packets the covariance is noise and the "bearing" is random.

## Design equations & rules of thumb
| Rule | Value |
|---|---|
| UCA radius | $r = s/(2\sin(\pi/N))$: 5 el, 0.4λ → 0.34λ |
| Phase per cable length | 360° ΔL/(VF λ): 7.9°/cm at 433 MHz (VF 0.66) |
| Bearing error vs phase error | ≈ 0.3 × (rms phase error) for this 5-element UCA |
| Coherent multipath | reflection at −10 dB → ≈ 2.5° bias-like error |
| Cross-range per degree | ≈ 17.5 m per km |
| ULA grating-lobe-free | $d/\lambda \le 1/(1+|\sin\theta_{max}|)$ |
| Array gain sizing | $N \approx 10^{(G_{target}-G_{el})/10}$ |

## Worked examples

### 1. Recovery DF kit
1. KrakenSDR in a weatherproof box on a car-roof mount or 2 m tripod; five λ/4 ground-plane whips (433 MHz: ≈ 16–17 cm after trimming) on a 47 cm-diameter circle (0.4λ), or quarter-wave magmounts on a metal car roof.
2. Five *identical* cables cut and measured with the NanoVNA to equal electrical length (≤ 2–3 mm) ([NanoVNA cable recipe](../17-test-measurement/nanovna-librevna-practical.md)).
3. KrakenSDR DAQ/DSP software (auto noise-source calibration after each retune), centre 433.125 MHz, 2.4 MS/s; squelch/gate on LoRa bursts.
4. On site: place a 10 mW beacon (legal SRD) ≥ 100 m away at a surveyed bearing; record the offset; repeat from a second bearing to check.
5. After landing: take bearings from two points ≥ 1–2 km apart (or one station + a drive), plot on a map with the last downlinked GNSS fix; walk in with the 3-element Yagi.

### 2. Phaser lab sequence
Uniform steering sweep −60…+60°; taper on/off; deliberately mis-phase one element by 30° and watch the sidelobes rise; calibrate with on/off toggling or REV ([array calibration](../12-phased-arrays/array-calibration.md)); then FMCW with the Phaser's ADF4159 ([FMCW recipe](fmcw-radar-build.md)). Source: an HB100 Doppler module at 10.525 GHz (a legal 10.50–10.55 GHz radio-determination device in Singapore) — check that the Phaser tunes to it (its nominal range is 10.0–10.5 GHz).

### 3. Would an array make a better telemetry ground station?
| | 11-el crossed Yagi + tablet/rotator | 433 MHz digital array, 14 dBi |
|---|---|---|
| Elements / channels | 1 feed (2 for CP) | ≈ 7 (6 dBi elements; ≈ 17 with 3 dBi dipoles per [DIY arrays](../12-phased-arrays/diy-phased-array-projects.md)) |
| Size | 1.72 m boom | ≈ 0.9–1.4 m square |
| Steering | 2.7°/s rotator or a person | instantaneous, multiple beams |
| Calibration | none | every session (cables, LO phases) |
| Interference nulling | none | possible (another team's pad transmitter) |
| Cost | ≈ US$100–800 | ≈ US$1500+ (coherent SDRs) |
| Link margin needed? | 30–50 dB available ([telemetry recipe](lora-rocket-telemetry-link.md)) | same |
Verdict: the Yagi wins at 433/915 MHz for this flight profile. An array is justified if you need simultaneous beams on several vehicles, adaptive nulling of a strong nearby transmitter, or a 2.4/5.8 GHz high-rate link where 14–20 dBi fits in 7–31 cm.

## Part selection
| Item | Choice | Price (est., USD) | Notes |
|---|---|---|---|
| Coherent receiver | KrakenSDR | ≈ 750 | 5 × R820T2, shared clock, noise source |
| DF antennas | 5 × λ/4 whips with ground plane (or magmounts on a car roof) | 50 | identical, same orientation |
| Cables | 5 × matched SMA cables | 40 | match to ≤ 2–3 mm electrical length |
| Host | Raspberry Pi 4/5 or laptop | — | KrakenSDR software |
| Beacon | the flight radio at legal power, or a 10 mW SX126x board | 20 | for site calibration |
| Beamforming lab | ADI EVAL-CN0566-RPIZ (Phaser) + HB100 source | ≈ 2875 + 5 | university lab purchase |

## Block diagram
```
 5 whips (UCA r = 23.6 cm @433) --matched cables--> KrakenSDR [noise source switch -> 5 x R820T2 -> shared clock]
   --> USB --> host: per-channel sample-delay + phase/gain calibration (auto) -> burst gate on LoRa packets
   --> covariance R (per packet) -> Bartlett / MUSIC azimuth spectrum -> bearing + quality metric
   --> map with station GNSS position, compass/true-north reference -> triangulation with station 2
```

## Layout notes
The "layout" is mechanical: rigid, symmetric element geometry (±2 mm), a ground plane (car roof or a 1 m aluminium disc) under λ/4 whips, nothing metallic within ≈ λ of the array except the intended ground, array north marked and aligned with a compass/GNSS heading, cables of identical type and routing.

## Simulation plan
| Step | Tool | Pass |
|---|---|---|
| Geometry, DOA Monte-Carlo, triangulation | `proj_phased_array.py` | P2–P3 met with ≤ 3° residual phase and ≤ −10 dB multipath |
| Mutual coupling of the real elements | NEC-2 model of 5 whips over the car roof ([NEC](../16-simulation-tools/nec-antenna-modelling.md)) | steering-vector error ≤ 5° per element, or calibrate |
| Phaser AF and taper | `proj_phased_array.py` §5; `tools/verify/array_factor.py`, `array_taper.py`, `array_calibration.py` (domain 12) | match bench measurements within 2 dB |

## Build, bring-up and test plan (pass/fail fixed in advance)
| # | Test | Method | Pass |
|---|---|---|---|
| A-T1 | Cable matching | NanoVNA electrical length (TDR/phase at 433 MHz) | all five within ±3 mm (±2.4°) |
| A-T2 | Receiver calibration | KrakenSDR auto-cal, repeated after retunes | phase residual ≤ 1° channel-to-channel |
| A-T3 | Bearing accuracy | beacon at 8 surveyed bearings, 200–500 m, open field | rms error ≤ 2°, no ambiguity |
| A-T4 | Multipath sensitivity | repeat A-T3 near a building | document the degradation (expect 3–7°) |
| A-T5 | Localisation rehearsal | hidden beacon 3–5 km away (a "fox hunt"), two stations | position within 500 m |
| A-T6 | Phaser steering | steer the beam across an HB100 source, measure received power vs steer angle | HPBW 13 ± 2° broadside, sidelobes ≈ −13 dB uniform |

## Regulatory check
- KrakenSDR and the Phaser *receiving* need no licence. The beacons are transmitters: 433 MHz ≤ 10 mW e.r.p. (10 % duty), 868 MHz ≤ 500 mW e.r.p. in Singapore ([IMDA](../19-regulations-safety/singapore-imda-rules.md)).
- The Phaser's own TX at 10.0–10.5 GHz is outside Singapore's SRD allocations (10.50–10.55 GHz radio determination) — use conducted tests or a shielded room, or a legal HB100 source.
- DF of other people's transmissions is fine technically; do not publish decoded content.

## Pre-registered predictions
| ID | Prediction | Tolerance | If outside |
|---|---|---|---|
| Y1 | Beacon bearings in an open field: rms error 0.7–1.5° with cables matched to ±3 mm | ±0.5° | residual phase or coupling larger than modelled |
| Y2 | Near a building (−6 dB reflection): 3–5° rms | — | reflection stronger; move the station |
| Y3 | Fox hunt at 3–5 km with two stations: position error ≤ 500 m (90 %) | — | bearing errors > 2°: recalibrate |
| Y4 | Phaser broadside HPBW 13.3°, first sidelobe −12.8 dB uniform, −25 dB with the cos² taper | ±2° / ±3 dB | element errors; run REV calibration |

## Risks and common failure modes
| Failure | Symptom | Fix |
|---|---|---|
| Unmatched cables | constant bearing bias, frequency-dependent | match lengths; beacon calibration |
| Coherent multipath | bearing jumps between true and reflection | higher, clearer site; multiple fixes |
| Processing noise between bursts | random bearings | burst gating |
| ULA used for DF | front/back ambiguity | UCA |
| Polarisation mismatch with a lying rocket | weak, multipath-dominated bearings | dual-polarised elements, or get closer |
| North reference error | all bearings rotated | GNSS heading or compass with declination |

## Cost estimate
| Item | Cost (USD, est.) |
|---|---|
| KrakenSDR kit (receiver, whips, cables, mount, Pi) | ≈ 900 |
| Second station (optional) | ≈ 900 |
| ADI Phaser lab (optional, departmental) | ≈ 2900 |

## Practical notes
- Record the raw IQ during DF sessions (as in the [SDR recipe](sdr-receiver-build.md)) so bearings can be recomputed after calibration fixes.
- Use the landed-mode LoRa schedule (SF11/125, last fix every 5 s) — long packets give high SNR per bearing.
- A single DF station plus the last GNSS fix and the descent wind drift is often enough; DF earns its keep when the GNSS fix is stale or missing.

## Common mistakes & misconceptions
- **"MUSIC is more accurate."** For one source it is not; it only helps resolve several. It also fails on coherent multipath without spatial smoothing.
- **"The KrakenSDR calibrates everything."** Only from its noise-source switch onward; cables and antennas are yours.
- **"An array gives more gain than a Yagi of the same size."** At UHF a Yagi of the same aperture is cheaper and simpler; arrays win on agility, not gain.
- **"More elements fix multipath."** A coherent reflection is still a second source; geometry and site choice matter more.

## How to simulate / verify
- `python3 tools/verify/proj_phased_array.py` — all tables above (≈ 3 s).
- `python3 tools/verify/array_factor.py`, `array_taper.py`, `array_calibration.py`, `array_steering.py` (domain 12).

## Open questions / gaps
- Measured mutual-coupling distortion of a 5-whip UCA on a car roof at 433 MHz.
- Phaser tuning range vs the HB100's 10.525 GHz (not verified).
- KrakenSDR performance at 868 MHz (R820T2 is spec'd to 1766 MHz; not measured here).

## Sources
1. This KB, [DIY phased-array projects](../12-phased-arrays/diy-phased-array-projects.md) — KrakenSDR/Kerberos, Phaser, rocket DF numbers, ground-station array sizing, steering rates. (internal)
2. This KB, [Array calibration](../12-phased-arrays/array-calibration.md) — noise-source calibration, cable matching, REV, self-calibration. (internal)
3. This KB, [Adaptive beamforming & DOA](../12-phased-arrays/adaptive-beamforming-doa.md) — Bartlett/MUSIC, CRB, coherent sources, UCA vs ULA ambiguity. (internal)
4. This KB, [Array factor](../12-phased-arrays/array-factor-linear-arrays.md), [beam steering](../12-phased-arrays/beam-steering-grating-lobes.md), [tapering](../12-phased-arrays/tapering-sidelobe-control.md). (internal)
5. KrakenSDR documentation (KrakenRF) — 5 coherent channels, noise-source auto-calibration, cable-matching guidance — via [1], [2]. (vendor docs)
6. Analog Devices, CN0566 circuit note / EVAL-CN0566-RPIZ; M. Lichtman, *PySDR*, "Hands-on with Phaser" — via [1]. (vendor / online textbook)
7. This KB, [Ground-station recipe](ground-station-tracking-yagi.md), [telemetry recipe](lora-rocket-telemetry-link.md), [SDR recipe](sdr-receiver-build.md). (internal)
