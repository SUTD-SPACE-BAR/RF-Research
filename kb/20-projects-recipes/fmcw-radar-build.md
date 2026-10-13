---
title: Recipe — FMCW radar build with a TI mmWave EVM (60 / 77 GHz), with 24 GHz and ADI Phaser alternatives — chirp design, processing chain, corner-reflector calibration, rail-exit velocity of a rocket
domain: 20-projects-recipes
slug: fmcw-radar-build
tags: [recipe, radar, fmcw, mmwave, iwr6843, awr1843, dca1000, bgt24, adi-phaser, cn0566, chirp-design, tdm-mimo, range-doppler, cfar, corner-reflector, trihedral, rcs, rail-exit-velocity, singapore-uwb, imda, pre-registration]
prerequisites:
  - ../11-radar/fmcw-radar.md
  - ../11-radar/diy-radar-hardware.md
  - ../11-radar/radar-range-equation.md
  - ../11-radar/radar-cross-section.md
related:
  - ../11-radar/detection-theory-cfar.md
  - ../11-radar/mimo-radar-virtual-arrays.md
  - ../11-radar/cw-and-doppler-radar.md
  - ../11-radar/clutter-and-mti.md
  - ../14-sdr-dsp/fft-spectral-analysis-windows.md
  - ../19-regulations-safety/singapore-imda-rules.md
  - ../19-regulations-safety/spectrum-allocation-ism-bands.md
  - phased-array-starter-build.md
  - beginner-project-ladder.md
level: intermediate
confidence: medium
last_updated: 2026-10-02
---

# Recipe — FMCW radar build (TI mmWave EVM), corner-reflector calibration and rocket rail-exit velocity

A first "real" radar: a TI mmWave evaluation module with raw-ADC capture, three chirp configurations, the
range–Doppler–angle processing chain, calibration against home-made corner reflectors, and one rocket
application — independent truth for the flight computer's rail-exit and early-boost velocity. The 24 GHz
module and the ADI Phaser are carried along as alternatives. Theory lives in [FMCW radar](../11-radar/fmcw-radar.md)
and hardware options in [DIY radar hardware](../11-radar/diy-radar-hardware.md); for a Doppler-only first
radar (HB100/CDM324) see the [beginner project ladder](beginner-project-ladder.md). Numbers:
`python3 tools/verify/proj_fmcw.py` (chirp configs, SNR, Singapore compliance, data rates, rail kinematics).

## Questions this page answers
- Which radar should I buy first — TI IWR6843 / AWR1843, a 24 GHz module or the ADI Phaser?
- How do I design a chirp for a given range, resolution and maximum velocity, and what limits the device imposes?
- Why does TDM-MIMO cut my maximum velocity by the number of transmitters?
- Can a mmWave radar beside the pad measure my rocket's rail-exit velocity?
- How strong a return will a person, a drone, a rocket and a corner reflector give?
- How do I build and use a corner reflector to calibrate range and RCS?
- Is a 77–81 GHz radar legal in Singapore, and why does my chirp bandwidth matter for that?
- How much raw data does the radar produce, and how do I process it?

## TL;DR
- **Pick the TI IWR6843 (60–64 GHz) EVM + DCA1000 raw-capture board** for learning: 3 TX × 4 RX, PLL-linear chirps up to 4 GHz, 12 dBm, NF ≈ 12 dB, and **57–64 GHz is a plain SRD band in Singapore (100 mW e.i.r.p.)**. The 76–81 GHz AWR1843 is licence-exempt in Singapore **only as an Ultra-Wideband device**: 10 dB bandwidth ≥ 500 MHz, mean e.i.r.p. density ≤ −3 dBm/MHz, peak ≤ 55 dBm/50 MHz, not a fixed outdoor installation ([IMDA](../19-regulations-safety/singapore-imda-rules.md)).
- **Chirp configurations** (complex IF, IF bandwidth capped at ≈ 10 MHz):
  | Job | Sweep / ramp | ADC | Range res | R_max | v_max | Frame |
  |---|---|---|---|---|---|---|
  | A: corner-reflector calibration (1 TX) | 3.5 GHz / 60 µs | 5 Msps × 256 | **5.0 cm** | 11.6 m | ±18.6 m/s | 4.3 ms |
  | B: people/drones (TDM 3 TX, 12 virtual) | 0.6 GHz / 25 µs | 10 Msps × 240 | 26 cm | 56 m | **±13.8 m/s** | 5.8 ms |
  | C: rail exit / early boost (1 TX, fast) | 0.6 GHz / 8 µs (+2 µs idle) | 25 Msps × 192 | 26 cm | **20 m** (IF-limited) | **±124 m/s** | 2.6 ms |
  | D: as B at 77 GHz (AWR1843) | 0.6 GHz / 25 µs | 10 Msps × 240 | 26 cm | 56 m | ±10.8 m/s | 5.8 ms |
- **TDM-MIMO divides v_max by the number of TX** (each TX repeats every $N_{TX}T_c$): the 12-virtual-channel config B gets ±13.8 m/s, a 1-TX fast config C gets ±124 m/s.
- **Rocket rail exit**: the modelled 10 km rocket leaves a 6 m rail at **35 m/s** and passes 20 m at **64 m/s** (100 m at 145 m/s). Config C covers rail exit to ≈ 20 m above the radar with SNR ≈ 24 dB at 10 m for a −20 dBsm tail-on target (6 dB losses) — a direct check of the flight computer's launch detection and velocity estimate.
- **SNR examples** (config B, frame integration, 6 dB losses): person (0 dBsm) 47.6 dB at 10 m / 19.6 dB at 50 m; small drone (−20 dBsm) 27.6 / −0.4 dB; 10 cm trihedral (+12.3 dBsm at 60 GHz) 59.9 / 31.9 dB.
- **Corner reflectors**: triangular trihedral $\sigma = 4\pi a^4/(3\lambda^2)$: 5 cm edge = +0.2 dBsm, 10 cm = +12.3 dBsm at 60.25 GHz (+2.4 / +14.4 dBsm at 77 GHz); faces orthogonal to ≪ λ/a (≈ 2.5° at 60 GHz for 10 cm) ([RCS](../11-radar/radar-cross-section.md)).
- **Compliance arithmetic**: 1 TX at 12 dBm + 8 dBi = 20 dBm e.i.r.p. — exactly the 60 GHz SRD limit, so use ≥ 3 dB TX back-off (and never transmit 3 TX coherently); at 77 GHz a 600 MHz chirp at 30 frames/s is −16 dBm/MHz mean (limit −3), but **a 300 MHz chirp is not UWB at all** and is not exempt.
- **Raw data**: config B is 0.70 MiB per frame (128 MB/s during the frame); config C 0.75 MiB in 2.6 ms (307 MB/s) — the DCA1000's 1 GbE needs idle time between frames.

## Intuition (no math)
An FMCW radar sends a tone that sweeps up in frequency and listens to its echoes while it is still sweeping. An echo is a delayed copy of the sweep, so at any instant it is a little lower in frequency than what is being transmitted; mixing the two gives a "beat" tone whose frequency is proportional to the distance. One FFT of the beat over a chirp sorts echoes by range. Repeat the chirp many times and a moving target's beat phase advances from chirp to chirp — a second FFT across chirps sorts them by speed. Several receive antennas see the echo with slightly different phases — a third FFT sorts by angle. Everything you design is a trade between how wide a sweep you have (range resolution), how fast you repeat chirps (top speed), how long you listen (speed resolution and sensitivity) and how fast the ADC can sample (maximum range).

## Requirements
| ID | Requirement | Value |
|---|---|---|
| M1 | Learning platform | raw ADC access, ≥ 2 TX × 4 RX, PLL-linear chirps |
| M2 | Calibration | range bias ≤ 2 cm, RCS within ±2 dB on trihedrals at 2–10 m |
| M3 | People/drone tracking | to 50 m, ±10 m/s, angle ±60° |
| M4 | Rocket rail exit | velocity 0–70 m/s to 20 m range, ≥ 10 dB SNR on a −20 dBsm target |
| M5 | Legality (Singapore) | SRD band or UWB conditions met as configured |
| M6 | Field robustness | survives a pad environment at ≥ 3 m from the rail (blast, debris, heat) |

## Architecture options and trade study
| Option | Band | Sweep | Channels | Raw data | Cost (est.) | Verdict |
|---|---|---|---|---|---|---|
| **TI IWR6843ISK/AOP EVM + DCA1000** | 60–64 GHz | ≤ 4 GHz | 3 TX × 4 RX | yes (LVDS → DCA1000) | ≈ US$150–250 + ≈ 600 | **chosen**: SRD band in SG, full learning chain |
| TI AWR1843BOOST + DCA1000 | 76–81 GHz | ≤ 4 GHz | 3 × 4 | yes | similar | automotive band; SG legal only as UWB |
| Infineon BGT60TR13C board | 58–63.5 GHz | 5.5 GHz | 1 × 3 | yes (FIFO) | ≈ US$50–100 | tiny, short range ([DIY radar](../11-radar/diy-radar-hardware.md)) |
| 24 GHz FMCW module (BGT24-class) | 24.00–24.25 GHz | 250 MHz | 1 × 2 | yes | ≈ US$50–150 | longer range, 60 cm resolution; "radar gun" clause in SG |
| ADI Phaser (CN0566) | 10.0–10.5 GHz | ≈ 0.5 GHz (assumed) | 1 × 8 beamformed + Pluto | yes | ≈ US$2000+ | best for beamforming; 10.0–10.5 GHz is **outside** SG's 10.50–10.55 GHz radio-determination band |
| HB100 / CDM324 Doppler | 10.525 / 24.1 GHz | CW | 1 × 1 | audio | ≈ US$5–10 | velocity only — beginner ladder |

## The math — design calculations

### Level 1 — chirp relations (TI form, complex IF)
Slope $S=B/T_{ramp}$; beat $f_b = 2SR/c$; range resolution $c/(2B_{sampled})$ with $B_{sampled} = S\,T_{ADC}$; maximum range $R_{max} = f_{IF,max}c/(2S)$ with $f_{IF,max} = \min(0.9 f_s, \text{IF filter})$; maximum velocity $v_{max} = \lambda/(4 N_{TX} T_c)$ for TDM-MIMO ($T_c$ = ramp + idle); velocity resolution $\lambda/(2T_{frame})$; angle resolution ≈ 2/N_virtual rad at boresight ([FMCW radar](../11-radar/fmcw-radar.md), [MIMO radar](../11-radar/mimo-radar-virtual-arrays.md)).

### Level 2 — configurations and SNR
SNR in FFT form: $\mathrm{SNR} = P_r T_{int}/(kT_s)$ with $T_{int} = T_{ADC}\times N_{loops}\times N_{virtual}$ (coherent range–Doppler FFT plus beamforming gain), $P_r$ from the radar equation, $T_s = 290\,F$ K, 6 dB of processing/window/mismatch losses ([radar equation](../11-radar/radar-range-equation.md)). Device figures from the [DIY radar](../11-radar/diy-radar-hardware.md) table: 12 dBm per TX; NF 12 dB (IWR6843), 14–15 dB (AWR1843); antenna gain ≈ 8 dBi each way (EVM patch arrays; assumption).

| Target (RCS at 60 GHz) | Config A, 10 m | Config B, 10 m / 50 m | Config C, 10 m | Config D (77 GHz), 10 / 50 m |
|---|---|---|---|---|
| trihedral 5 cm (+0.2 dBsm; +2.4 at 77 GHz) | 51.1 dB | 47.8 / 19.9 dB | 44.1 dB | 45.3 / 17.4 dB |
| trihedral 10 cm (+12.3 / +14.4 dBsm) | 63.2 dB | 59.9 / 31.9 dB | 56.2 dB | 57.4 / 29.4 dB |
| person (0 dBsm) | 50.9 dB | 47.6 / 19.6 dB | 43.9 dB | 43.0 / 15.0 dB |
| small drone (−20 dBsm) | 30.9 dB | 27.6 / −0.4 dB | 23.9 dB | 23.0 / −5.0 dB |
| rocket tail-on, 130 mm body (−20 dBsm assumed) | 30.9 dB | 27.6 / −0.4 dB | 23.9 dB | 23.0 / −5.0 dB |

For detection at Pfa 10⁻⁶ with a non-fluctuating target you need ≈ 13–14 dB (Albersheim); fluctuating targets need more ([detection theory](../11-radar/detection-theory-cfar.md)). So drones are a 20–30 m target for these EVMs, people ≈ 60 m+, a 10 cm trihedral > 100 m (limited by IF bandwidth, not SNR).

### Level 2 — the rocket near the pad
From the [telemetry recipe's](lora-rocket-telemetry-link.md) trajectory (3500 N, 31.8 kg): t = 0.35 s at 6 m (rail exit) 35.0 m/s; 0.63 s at 20 m, 64.2 m/s; 0.99 s at 50 m, 102 m/s; 1.40 s at 100 m, 145 m/s. Config C sees the rocket from rail exit until it leaves the 20 m IF-limited range ≈ 0.3 s later — ≈ 100 frames of 2.6 ms, each giving range and radial velocity. Range-rate of the radar track vs the flight computer's integrated accelerometer velocity is an *independent* truth source (team tenet 1). The motor's alumina-laden plume may itself be a radar target at mm-wave (unquantified — see gaps).

### Level 2 — Singapore compliance arithmetic
- **57–64 GHz (TS SRD 39b)**: 100 mW = 20 dBm e.i.r.p.; 1 TX: 12 dBm + 8 dBi = 20.0 dBm (no margin) → ≥ 3 dB TX back-off; three TX transmitting coherently (beamforming/BPM) would be 24.8 dBm — not allowed without back-off. TDM-MIMO transmits one TX at a time.
- **77–81 GHz (UWB, Notification item 17 + IMDA TS UWB)**: mean e.i.r.p. density $= \mathrm{EIRP} - 10\log_{10}(B_{MHz}) + 10\log_{10}(\text{duty})$: config D (600 MHz, chirp duty 4.8 % at 10 frames/s) → −21.0 dBm/MHz; 14.5 % at 30 frames/s → −16.2 dBm/MHz (limit −3). Continuous chirping: 300 MHz → −4.8 dBm/MHz *and* not UWB (< 500 MHz) → **fails**; 500 MHz → −7.0 (meets); 4 GHz → −16.0.
- **24.00–24.25 GHz (38a–c)**: 100 mW e.i.r.p.; "radar gun devices are not allowed" under the non-specific provision — whether a speed-measuring rocket radar counts is an interpretation; ask IMDA.

### Level 3 — what breaks
- TX→RX leakage carries LO phase noise into near-range bins; a radome/bumper reflection at 0.3 m can lift the near-range floor 8 dB above thermal ([FMCW radar](../11-radar/fmcw-radar.md)) — mount the radar without a close reflector, or cover it with a radome designed as a λ/2 window.
- Velocity aliasing: a target faster than v_max wraps; use the expected kinematics (or two interleaved chirp profiles with different $T_c$) to unwrap.
- Range migration: at 124 m/s the rocket moves 0.32 m (≈ 1.2 range bins) during one 2.6 ms frame — tolerable; longer frames smear.
- The −20 dBsm rocket RCS is a guess; the flat motor end can flash far higher near normal incidence ($4\pi A^2/\lambda^2$), and plume returns are unknown.

## Design equations & rules of thumb
| Rule | Value |
|---|---|
| Range resolution | $c/2B$: 3.5 GHz → 4.3 cm (5.0 cm sampled); 600 MHz → 25–26 cm |
| R_max | $f_{IF,max}c/2S$ — the IF filter (≈ 10 MHz), not the ADC, often binds |
| v_max | $\lambda/(4N_{TX}T_c)$: 60 GHz, 10 µs, 1 TX → 124 m/s |
| Trihedral RCS | $4\pi a^4/(3\lambda^2)$; ±20° for < 2 dB |
| Detection threshold | ≈ 13 dB SNR for Pd 0.9, Pfa 10⁻⁶ (steady target) |
| 60 GHz SRD | ≤ 20 dBm e.i.r.p.; one TX at a time; back-off ≥ 3 dB |
| 77–81 GHz SG | UWB only: ≥ 500 MHz, ≤ −3 dBm/MHz mean |

## Worked examples

### 1. Corner-reflector calibration session (config A)
1. Build two triangular trihedrals (5 and 10 cm edges) from copper-clad FR-4 or 1 mm aluminium, faces square to ≪ λ/a (≈ 2.5° for 10 cm at 60 GHz; use a machinist's square).
2. Place on a non-metallic mast 1.5 m high on an open field, radar at the same height, boresight aligned; measure with a tape at 2, 4, 6, 8, 10 m.
3. Range bias = measured − tape (expect a constant offset from the antenna/IF delay; remove it in software); range resolution: two reflectors at 10 m, separated by 5, 7.5, 10 cm across range.
4. RCS calibration: the 10 cm reflector (+12.3 dBsm) sets the system constant; the 5 cm (+0.2 dBsm) checks it (expected difference 12.1 dB).

### 2. Rail-exit measurement (config C)
Radar 3 m from the rail base, behind a blast board, looking up the rail at ≈ 70–80° elevation (the IWR6843ISK's ≈ ±15–20° elevation beam must contain the first 20 m of flight — check the EVM's pattern). Start capture on the launch countdown; the DCA1000 records frames continuously to the laptop. Post-process: per-frame range–Doppler map → strongest target near the expected range → velocity (with aliasing unwrap from the rail kinematics) → compare with the flight computer's launch-detect time and velocity estimate. Pre-registered: rail exit 35 ± 5 m/s at 6 m.

### 3. The same with a 24 GHz module (config E)
250 MHz sweep → 60 cm resolution; R_max 108 m at 2 Msps; v_max ±25.9 m/s with 120 µs chirps — too slow for the rocket unless the chirp period drops to ≤ 25 µs (then v_max ≈ 125 m/s, R_max shrinks with the higher slope). SNR is better (13 dBi antennas assumed): a −20 dBsm target at 100 m gives 4 dB.

## Part selection
| Item | Choice | Price (est., USD) | Notes |
|---|---|---|---|
| Radar | TI IWR6843ISK (or IWR6843AOP) EVM | 150–250 | 60–64 GHz; check current TI EVM lineup |
| Raw capture | TI DCA1000EVM | ≈ 600 | 1 GbE; mmWave Studio / OpenRadar scripts |
| 77 GHz option | TI AWR1843BOOST | ≈ 300 | UWB conditions in SG |
| Corner reflectors | DIY copper-clad FR-4 / aluminium | 10 | 5 and 10 cm edges |
| Mast | non-metallic tripod/mast | 30 | |
| Blast protection | plywood board + polycarbonate window (check mm-wave loss!) | 20 | measure window loss with a reflector |

## Block diagram
```
 [IWR6843 EVM: 3 TX / 4 RX, PLL chirp, ADC 12-bit 25 Msps] --LVDS--> [DCA1000] --1 GbE--> laptop
     raw cube (samples x loops x virtual) per frame
       -> window + range FFT (per chirp) -> window + Doppler FFT (per range bin, per virtual channel)
       -> non-coherent sum over channels -> 2-D CA-CFAR -> peak grouping
       -> angle FFT on the 12-element virtual array (TDM phase correction for moving targets) -> point cloud
       -> tracking (alpha-beta / Kalman) -> CSV with UTC (GNSS-disciplined laptop clock)
```

## Layout notes
No PCB in this recipe (EVM-based). Mechanical/RF notes: mount with nothing metallic within the near field in front of the antennas; any cover must be a low-loss λ/2 radome (PTFE/polycarbonate thickness tuned to 60 GHz, or very thin film) — check its loss and reflection with a corner reflector; keep cables (Ethernet, USB) clear of the radiating face; for a pad installation, a sacrificial window and sandbags.

## Simulation plan
| Step | Tool | Pass |
|---|---|---|
| Chirp configs, SNR, compliance | `proj_fmcw.py` | M2–M5 met on paper |
| Signal-level simulation of the cube | `tools/verify/radar_fmcw.py` (domain 11: synthetic targets, range/Doppler/angle chain) with config C and a moving 35–64 m/s point target | correct velocity after unwrap; range migration < 2 bins |
| Detection | `radar_detection_cfar.py` | Pfa and Pd on synthetic clutter match theory |
| Leakage/phase-noise floor | `radar_fmcw.py` leakage model | near-range floor below thermal for the chosen mounting |

## Build, bring-up and test plan (pass/fail fixed in advance)
| # | Test | Method | Pass |
|---|---|---|---|
| M-T1 | EVM bring-up | TI out-of-box demo, then mmWave Studio raw capture via DCA1000 | frames received, no drops for 5 min |
| M-T2 | Range bias / resolution | worked example 1 | bias stable to ±1 cm; two reflectors 7.5 cm apart resolved (config A) |
| M-T3 | RCS calibration | 10 cm vs 5 cm trihedral | difference 12.1 ± 2 dB |
| M-T4 | Velocity | person walking/running, then a car at known speed (GNSS on the car) | velocity error ≤ 0.3 m/s; aliasing handled |
| M-T5 | Drone detection range | small quadcopter flying away | detected (CFAR) to ≥ 25 m with config B |
| M-T6 | TX power/e.i.r.p. | TI register settings logged; if a 60 GHz power meter is unavailable, rely on documented TX power + back-off | back-off ≥ 3 dB configured |
| M-T7 | Pad rehearsal | throw/drop test of a dummy rocket-sized target in the beam, then a live launch | track begins ≤ 50 ms after rail exit; velocity agrees with the flight log within 5 % |

## Regulatory check
- **60 GHz**: TS SRD 39b (57–64 GHz) ≤ 100 mW e.i.r.p. — with back-off, compliant; TS SRD 39a covers tank-level radar.
- **77–81 GHz**: only under the UWB exemption (≥ 500 MHz, ≤ −3 dBm/MHz mean, ≤ 55 dBm/50 MHz peak, no fixed outdoor installation / externally mounted antenna) — a pad-side tripod for a test day is not a fixed installation; a permanent range installation would be ([IMDA](../19-regulations-safety/singapore-imda-rules.md), [spectrum allocation](../19-regulations-safety/spectrum-allocation-ism-bands.md)).
- **76–77 GHz** (sub-band 41) is for vehicle/infrastructure radar.
- **24.00–24.25 GHz**: ≤ 100 mW e.i.r.p.; the radar-gun exclusion needs interpretation.
- **10 GHz Phaser**: 10.0–10.5 GHz is not an SRD band in Singapore — conducted or shielded tests only, or a permit.
- Abroad: check the venue (FCC Part 15.255 for 57–71 GHz; 15.253 / Part 95 for 76–81 GHz) before travelling ([competitions](../19-regulations-safety/international-rules-for-competitions.md)).
- RF exposure at 12 dBm/20 dBm e.i.r.p. is negligible beyond a few cm ([RF exposure](../19-regulations-safety/rf-exposure-safety.md)).

## Pre-registered predictions
| ID | Prediction | Tolerance | If outside |
|---|---|---|---|
| F1 | Config A resolves two trihedrals 7.5 cm apart in range at 5 m | — | sampled bandwidth or windowing wrong |
| F2 | 10 cm − 5 cm trihedral return difference 12.1 dB | ±2 dB | multipath (ground bounce), misalignment |
| F3 | Config B detects a person walking away to ≥ 50 m (SNR 19.6 dB predicted at 50 m) | ±5 m | antenna gain or losses mis-assumed |
| F4 | Small drone (−20 dBsm) detection range ≈ 25–30 m (13 dB SNR crossing) with config B | ±30 % | drone RCS differs |
| F5 | Rail-exit speed 35 ± 5 m/s for the modelled vehicle (or the real vehicle's sim value) | — | trajectory or launch-detection bias |

## Risks and common failure modes
| Failure | Symptom | Fix |
|---|---|---|
| Velocity aliasing | rocket "slows" or reverses | 1-TX fast chirps; unwrap with kinematics |
| Ground/multipath ghosts | targets below ground, RCS ripple vs range | raise the mast; absorbing ground mat; average |
| Near-range floor raised | weak targets near the radar lost | remove close reflectors; radome design |
| Dropped frames | gaps in the track | idle time between frames; dedicated NIC |
| Illegal configuration at 77 GHz | sweep < 500 MHz | keep ≥ 500 MHz; log the profile |
| Pad damage | dead EVM | distance, blast board, sacrificial window |

## Cost estimate
| Item | Cost (USD, est.) |
|---|---|
| IWR6843 EVM + DCA1000 | ≈ 750–850 |
| Reflectors, mast, mounts, blast protection | ≈ 60 |
| Optional AWR1843BOOST | ≈ 300 |
| **Total (60 GHz path)** | **≈ 810–910** |

## Practical notes
- Start from TI's out-of-box demo (point cloud over UART) to confirm the hardware, then move to raw capture — the learning is in your own FFT/CFAR code.
- Log the full chirp profile (start frequency, slope, idle, ADC rate/samples, TX enables, back-off) with every capture (record-everything; a capture without its config is useless).
- Use the GNSS-disciplined laptop clock to timestamp frames; the radar's own counter drifts.

## Common mistakes & misconceptions
- **"More bandwidth gives more range."** Bandwidth gives *resolution*; range comes from SNR and the IF bandwidth.
- **"12 virtual channels for free."** TDM-MIMO divides v_max by the number of TX and needs motion compensation for angle estimation of fast targets.
- **"The ADC rate sets maximum range."** Often the IF low-pass (≈ 10 MHz) does.
- **"77 GHz radar is licence-free everywhere."** In Singapore only as UWB with ≥ 500 MHz sweep.
- **"A flat plate makes a better calibrator than a corner."** The plate's ±1° acceptance at mm-wave makes it nearly unusable in the field.

## How to simulate / verify
- `python3 tools/verify/proj_fmcw.py` — configs, SNR, compliance, data rates, rail kinematics.
- `python3 tools/verify/radar_fmcw.py`, `radar_rcs.py`, `radar_detection_cfar.py`, `radar_mimo.py` (domain 11).
- Bench/field: M-T1 … M-T7.

## Open questions / gaps
- mm-wave radar returns from an APCP motor plume (and from the flame itself) are not quantified.
- EVM antenna gains/patterns (assumed 8 dBi) should be taken from TI's EVM user's guide.
- IMDA's reading of "radar gun" for 24 GHz speed measurement.
- ADI Phaser ramp parameters (assumed 500 MHz / 500 µs) not verified.

## Sources
1. This KB, [FMCW radar](../11-radar/fmcw-radar.md) — chirp relations, TI device summary (IWR6843 12 dBm/NF 12 dB, AWR1843 NF 14–15 dB), leakage/phase noise, VCO nonlinearity, processing chain. (internal; TI SPYY005/SWRA553A, Rao)
2. This KB, [DIY radar hardware](../11-radar/diy-radar-hardware.md) — device table, Phaser, Doppler modules, rocket tracking, Singapore radar bands. (internal)
3. This KB, [Radar cross section](../11-radar/radar-cross-section.md) — trihedral formula, tolerances, rocket RCS. (internal)
4. This KB, [Radar range equation](../11-radar/radar-range-equation.md), [detection theory & CFAR](../11-radar/detection-theory-cfar.md), [MIMO radar](../11-radar/mimo-radar-virtual-arrays.md). (internal)
5. This KB, [Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md) — TS SRD 38/39/41 and the UWB exemption for 77–81 GHz (Notification item 17, IMDA TS UWB Issue 1 Table 1). (internal; regulator documents)
6. Texas Instruments, IWR6843 / AWR1843 product pages and DCA1000EVM documentation (as summarised in [2]). (datasheet)
7. Coordinator note from W5-E1 (2026-10-02): 77–81 GHz licence-exempt in Singapore only as UWB. (internal)
