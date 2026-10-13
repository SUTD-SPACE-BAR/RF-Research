---
title: DIY radar hardware — coffee-can radar, HB100/CDM324, TI mmWave EVMs, Infineon BGT60, ADI Phaser, Acconeer, SDR radar, passive radar, rocket tracking, legal bands
domain: 11-radar
slug: diy-radar-hardware
tags: [diy-radar, coffee-can-radar, hb100, cdm324, ipm-165, ti-mmwave, iwr6843, awr1843, awr2944, dca1000, bgt60tr13c, adi-phaser, cn0566, acconeer, a121, sdr-radar, adalm-pluto, b210, hackrf, passive-radar, krakensdr, rtl-sdr, rocket-tracking, radar-altimeter, imda, legal-bands, magnetron, klystron, twt, pulse-modulator, pfn, microwave-oven-safety]
prerequisites:
  - radar-range-equation.md
  - cw-and-doppler-radar.md
  - fmcw-radar.md
related:
  - radar-cross-section.md
  - detection-theory-cfar.md
  - mimo-radar-virtual-arrays.md
  - sar-and-imaging.md
  - ambiguity-function-waveforms.md
  - ../14-sdr-dsp/sdr-hardware-survey.md
  - ../12-phased-arrays/diy-phased-array-projects.md
  - ../19-regulations-safety/singapore-imda-rules.md
  - ../19-regulations-safety/spectrum-allocation-ism-bands.md
  - ../20-projects-recipes/fmcw-radar-build.md
  - ../15-lora-ism-radios/ground-station-design.md
level: intro
confidence: medium
last_updated: 2026-10-13
---

# DIY radar hardware

## Questions this page answers
- What is the cheapest way to start building radars, and what can each option actually do?
- What is the MIT coffee-can radar and how does it work?
- HB100 vs CDM324 vs an I/Q Doppler module — which should I buy?
- Which TI mmWave board (IWR6843, AWR1843, AWR2944) should I use, and how do I get raw data?
- What are the Infineon BGT60TR13C, the ADI Phaser (CN0566) and the Acconeer A121 good for?
- Can I build a radar with an SDR (Pluto, B210, HackRF)? What limits it?
- How does passive radar with a KrakenSDR or RTL-SDRs and FM/DVB-T transmitters work, and what does it need?
- Can a DIY radar track my rocket? What are the geometry, range and pointing problems?
- Which radar frequencies and powers are legal in Singapore?
- How do magnetrons, klystrons and TWTs work, and what is a pulse-forming-network modulator?
- Is it safe to use a microwave-oven magnetron (or a surplus marine radar) for a radar project?

## TL;DR
- **Start here:** a 24 GHz or 10.5 GHz Doppler module + a 70–80 dB audio amplifier + a laptop teaches Doppler and micro-Doppler for a few dollars; a **TI mmWave EVM** (IWR6843/AWR1843 class, 3 TX × 4 RX FMCW with on-chip DSP) is the best-value "real" radar; the **ADI Phaser** is the best way to learn beamforming + FMCW together at 10 GHz.
- **Module facts:** HB100 — 10.525 GHz, EIRP 20 dBm, 80° × 40°, *single* mixer output (no direction), made by ST Engineering Electronics in Singapore [1]. IPM-165 (CDM324 is sold as its equivalent) — 24.05–24.25 GHz, EIRP 16 dBm, 9.5 dBi, 80° × 35°, mono [2], [3].
- **MIT coffee-can radar (2011):** 2.4 GHz FMCW from coaxial Mini-Circuits parts (ZX95-2536C+ VCO ramped by an XR-2206, ZX60-272LN amplifiers, ZX05-43MH mixer), coffee-can antennas, audio-card ADC: Doppler, ranging (~1.7 m resolution, audio-limited ~700 m) and rail SAR [4], [5].
- **SDR radars** are limited by bandwidth (Pluto AD9363: 20 MHz → **7.5 m** resolution; AD9361/B210: 56 MHz → 2.7 m), by **TX→RX leakage** (with separate antennas and 40 dB isolation a person at 20 m is 46 dB below the leakage, a drone at 100 m 91 dB below), and by duplex: **HackRF is half-duplex** (no monostatic CW/FMCW) [6].
- **Passive radar** (KrakenSDR: 5 coherent R820T2 receivers, 24–1766 MHz [7]): an aircraft echo is ≈ **81 dB below the direct signal** (10 m², 20/20/10 km geometry); the cross-ambiguity integration gives 52 dB (FM, 1 s) or 59 dB (DVB-T, 0.1 s), so the direct path must be cancelled by **> 30–40 dB**. Range-sum resolution: FM ≈ 2 km, DVB-T ≈ 39 m.
- **Rocket tracking:** SNR is achievable (S-band 1 W with 1.2 m dishes: ~5 km for 0.01 m²), but **pointing** is the problem — from 500 m off the pad a 250 m/s rocket sweeps **28.6°/s** in elevation, crossing a 5.8° beam in 0.2 s. Practical DIY options: (1) a Doppler module looking up the rail (rail-exit and early-boost velocity, tens of m); (2) a 77 GHz FMCW board near the pad; (3) a dish on a mount slaved to the rocket's own GNSS telemetry. The radar's value is **independent** truth for the flight computer's velocity estimate.
- **Singapore (IMDA TS SRD Issue 1 Rev 3, Sep 2023) [8]:** 2.4 GHz radio-determination ≤ 25 mW EIRP; 5.725–5.875 GHz ≤ 100 mW; 10.50–10.55 GHz ≤ 117 dBµV/m at 10 m (≈ 32 dBm EIRP); 24.00–24.25 GHz ≤ 100 mW (radar guns excluded under the non-specific provision); 57–64 GHz ≤ 100 mW; 76–77 GHz vehicle/infrastructure radar (sub-band 41). **77–81 GHz is not in TS SRD, but it *is* licence-exempt as an "Ultra-Wideband Device"** (Exemption Notification First Schedule item 17; IMDA TS UWB Issue 1, Oct 2016, Table 1): mean e.i.r.p. density ≤ −3 dBm/MHz, peak ≤ 55 dBm/50 MHz, 10 dB bandwidth ≥ 500 MHz, not a fixed outdoor installation [18][19]. A TI 77–81 GHz board sweeping ≥ 1 GHz is typically ≈ 10–15 dB under the density limit (Example 4). Anything like a 1 W S-band tracker needs a licence.

- **Tubes and modulators:** magnetron = non-coherent crossed-field oscillator, klystron = narrowband coherent amplifier, TWT = broadband amplifier; a line-type modulator's PFN gives τ = 2√(LC) (1 µs into 50 Ω: 10 nF, 25 µH). Oven parts are lethal: HV capacitor ≈ 4 J at ≈ 3 kV, and a bare 800 W magnetron gives ≈ 104 W/m² at 1 m — 10× the public exposure level ([tubes and modulators](#microwave-tubes-and-pulse-modulators)). Use solid-state.

## Intuition (no math)
Every radar needs four things: something that transmits a known signal, an antenna, a receiver that compares the echo with what was sent, and signal processing. Hobby radars differ in how much of that is already integrated:
- **Doppler modules** integrate oscillator, antennas and mixer; you add an audio amplifier and a computer. They only see motion.
- **Discrete builds** (coffee-can, Forstén's 6 GHz radar) assemble oscillator, amplifiers, mixer and antennas from modules — the best way to *understand* each block, and to meet non-idealities (VCO nonlinearity, leakage) head-on.
- **Radar-on-chip EVMs** (TI, Infineon, Acconeer) integrate everything up to the FFTs and CFAR; you configure chirps and read point clouds or raw data.
- **SDRs** give you a flexible transmitter and receiver but none of the radar-specific plumbing (isolation, wide bandwidth, timing).
- **Passive radar** uses someone else's transmitter (FM, DVB-T) and needs only receivers — no licence, but hard signal processing.
- GPR, through-wall, Wi-Fi/CSI sensing, harmonic radar, RCWL-0516 and LD2410: see [radar applications](radar-applications-gpr-through-wall-sensing.md).

For a rocket, the physics is easy (the rocket moves fast, so Doppler separates it from clutter) but the geometry is hard: it is small, far and moving across the sky quickly.

## The math

### Level 1 — what each platform can resolve
| Platform | f | Waveform | TX/RX | Sweep/IF BW | ΔR = c/2B | Notes |
|---|---|---|---|---|---|---|
| HB100 [1] | 10.525 GHz | CW Doppler (pulsable) | 1/1 (mono) | — | — | 70.2 Hz per m/s |
| IPM-165 / CDM324 [2] | 24.05–24.25 GHz | CW Doppler (FSK possible) | 1/1 (mono) | — | (FSK: $R_u = c/2\Delta f$) | 160.9 Hz per m/s |
| MIT coffee-can [4] | 2.3–2.5 GHz | FMCW, ~20 ms ramps | 1/1 | ~90 MHz / 22 kHz audio | ~1.7 m | also Doppler & rail SAR |
| TI IWR6843 [9] | 60–64 GHz | fast FMCW | 3/4 | 4 GHz / 25 Msps | 3.75 cm | DSP + HWA on chip |
| TI AWR1843 [9] | 76–81 GHz | fast FMCW | 3/4 | 4 GHz / 25 Msps | 3.75 cm | NF 14–15 dB, 12 dBm |
| TI AWR2944 [9] | 76–81 GHz | fast FMCW (DDMA-capable) | 4/4 | 4 GHz / 37.5 Msps | 3.75 cm | NF 12 dB, 13.5 dBm |
| Infineon BGT60TR13C [10] | 58–63.5 GHz | FMCW | 1/3 (AiP) | 5.5 GHz / 4 Msps | 2.7 cm | gesture/presence |
| Acconeer A121 [11] | 60 GHz | pulsed coherent | 1/1 (AiP) | — | mm accuracy | ≤ 20 m |
| ADI Phaser CN0566 [12] | 10–10.5 GHz | FMCW (ADF4159) + beamforming | 1 TX / 8-el. RX array | ~0.5 GHz / Pluto | ~0.3 m | 2 × ADAR1000 |
| ADALM-Pluto [6] | 0.325–3.8 GHz | anything (SDR) | 1/1 full duplex | 20 MHz | 7.5 m | hackable to 70 MHz–6 GHz, 56 MHz |
| KrakenSDR [7] | 24–1766 MHz | passive (receive only) | 0/5 coherent | ~2.4 MHz | FM ~2 km, DVB-T needs wider | DF + passive radar |

(The Phaser's sweep bandwidth depends on the ADF4159 ramp programmed; ~0.5 GHz is typical of its examples but was not verified here.)

### Level 2 — the budgets that decide feasibility

**SDR monostatic radar.** With separate TX and RX antennas, leakage $P_L = P_t - I$ (isolation $I$) sits at near-zero range and must fit in the ADC together with the echoes. At 2.4 GHz, 5 dBm, 10 dBi antennas, 40 dB isolation (computed in `tools/verify/radar_diy.py`): leakage −35 dBm; person (0.5 m², 20 m) −81 dBm (46 dB below); car (10 m², 50 m) −84 dBm; drone (0.01 m², 100 m) −126 dBm (91 dB below). A 12-bit ADC has ≈ 74 dB instantaneous SQNR plus FFT processing gain — enough for people and cars, marginal for small drones unless the leakage is cancelled (the same phase-noise/leakage physics as [FMCW](fmcw-radar.md)). Range resolution is set by the SDR's instantaneous bandwidth (7.5 m at 20 MHz); **stepped-frequency** operation (retune the LO in, e.g., 50 × 20 MHz steps) synthesises 1 GHz → 15 cm, at the cost of retuning time and phase coherence between steps.

**Passive (bistatic) radar.** For transmitter–receiver baseline $L_b$ and target ranges $R_t, R_r$ (same antenna gains assumed), echo-to-direct power ratio
$$\frac{P_e}{P_d} = \frac{\sigma L_b^2}{4\pi R_t^2R_r^2},$$
which is −81 dB for σ = 10 m², $L_b$ = 20 km, $R_t$ = 20 km, $R_r$ = 10 km. The cross-ambiguity function ([ambiguity page](ambiguity-function-waveforms.md)) integrates coherently with gain $BT$: 51.8 dB (FM, 150 kHz, 1 s) or 58.8 dB (DVB-T, 7.6 MHz, 0.1 s). The direct signal's own CAF pedestal lies about $BT$ below its peak, i.e. 29 dB (FM) / 22 dB (DVB-T) *above* the echo — so the direct path (and its multipath) must be removed by adaptive cancellation by more than ~39 / 32 dB (10 dB margin) before targets appear. Bistatic range-sum resolution is $c/B$ (FM ≈ 2 km, DVB-T ≈ 39 m); Doppler resolution $1/T$. The KrakenSDR's per-channel sample rate (≈ 2.4 MS/s, RTL2832U-class) is enough for FM and a single DAB block (DAB occupies ≈ 1.5 MHz) but not the full 7.6 MHz of DVB-T.

**Rocket-tracking geometry.** For a vertical climb at speed $v$ seen from a radar at horizontal offset $d$ from the pad, elevation θ = atan(h/d) changes at
$$\dot\theta = \frac{vd}{d^2 + h^2}\quad(\text{max } v/d \text{ at } h = 0),\qquad v_r = v\frac{h}{\sqrt{d^2+h^2}} .$$
d = 500 m, v = 250 m/s: 28.6°/s near the pad, 5.7°/s at 1 km altitude, radial velocity 89 % of v at 1 km. d = 50 m: 287°/s near the pad (the rocket leaves any narrow beam immediately) but at altitude the motion is almost purely radial — ideal for a *fixed, upward-looking* Doppler radar. d = 2 km: slow angular rates (7°/s max) but only 45 % of the speed is radial at 1 km and the range is longer.

**Radar altimeter (ground return).** Looking straight down at flat ground from height $h$, image theory turns the ground into a mirror: the echo is the transmitter's own signal travelling $2h$, so $P_r = P_tG^2\lambda^2|\Gamma|^2/(4\pi\cdot2h)^2$ — falling as $h^{-2}$, not $h^{-4}$. At 60 GHz, 0 dBm, 10 dBi, |Γ| = 1: −60 dBm at 2 m, −74 dBm at 10 m, −80 dBm at 20 m (then × |Γ|² for real ground). This is why tiny 60 GHz sensors (Acconeer, BGT60) make good landing-altitude/ground-proximity sensors for recovery systems, where a barometer is unreliable near the ground.

### Level 3 — platform details and gotchas

**MIT coffee-can radar [4], [5].** Built in 2011 at MIT Lincoln Laboratory's IAP course for undergraduate teams: an XR-2206 function generator ramps a ZX95-2536C+ VCO (tuning sensitivity varies 82 → 36 MHz/V over 0–5 V [13]), amplified by ZX60-272LN modules, split to a TX coffee-can antenna and a ZX05-43MH mixer LO; the RX can feeds an LNA and the mixer; op-amp video amplifiers feed a laptop's audio input; eight AA batteries. Modes: CW Doppler (fixed Vtune), FMCW ranging (ramp; sync on the second audio channel) and rail SAR (range-migration algorithm). Its weak points are exactly the textbook ones: VCO nonlinearity broadening far targets (2.6× at 100 m, 8× at 300 m in the [FMCW simulation](fmcw-radar.md)), leakage between cans, and the ~22 kHz audio limit on beat frequency.

**TI mmWave EVMs.** IWR6843/AWR1843 (3 TX, 4 RX) and AWR2944 (4 TX, 4 RX) include the synthesiser (PLL-linear chirps up to 4 GHz), ADCs, a hardware FFT/CFAR accelerator, a DSP and an Arm core [9]. Out of the box they output point clouds (range, velocity, angle) over UART using TI's demo firmware; for raw ADC data you need a DCA1000EVM capture card and mmWave Studio. Chirp design rules and limits are on the [FMCW page](fmcw-radar.md) (TI SWRA553). 60 GHz parts suffer ~15 dB/km oxygen absorption — irrelevant indoors, noticeable outdoors beyond ~100 m.

**Infineon BGT60TR13C [10].** 1 TX / 3 RX antennas in a 6.5 × 5 mm package, > 5 GHz sweep, three 12-bit ADCs to 4 MS/s, an FSM-driven chirp sequencer and FIFO read over SPI — very easy to put on a custom PCB (antennas included). Short-range: 2.7 cm resolution, IF-limited ranges of a few to ~20 m depending on slope.

**Acconeer A121 [11].** A pulsed coherent radar (not FMCW) at 60 GHz with antennas in package: absolute range to ~20 m with mm-level accuracy and µm-level relative (phase) accuracy; very low power. Use for level sensing, presence, vital signs, and short-range altimetry.

**ADI Phaser (CN0566) [12], [14].** An 8-element 10.0–10.5 GHz patch array (14 mm ≈ 0.48λ spacing) with two 4-channel ADAR1000 beamformers (phase/gain per element), an ADF4159 fractional-N PLL + HMC735 VCO generating the LO and FMCW ramps, LTC5548 mixers down to ≈ 2.2 GHz, digitised by an ADALM-Pluto's two RX channels, controlled from a Raspberry Pi. It includes (in the kit) an HB100 as a test source — whose frequency varies unit to unit, so ADI's scripts search for it first. Ideal for learning array factors, tapering, monopulse and FMCW ([12 DIY phased arrays](../12-phased-arrays/diy-phased-array-projects.md)).

**SDRs.** ADALM-Pluto: AD9363, 325 MHz–3.8 GHz, up to 20 MHz bandwidth, 12-bit, 1 TX + 1 RX full duplex (a well-known firmware setting unlocks AD9364-like 70 MHz–6 GHz / 56 MHz operation, outside ADI's specification) [6]. USRP B210: AD9361, 70 MHz–6 GHz, 56 MHz, 2 × 2 full duplex. HackRF One: 1 MHz–6 GHz, 20 MS/s, **half duplex** — cannot receive while transmitting, so it cannot be a monostatic CW/FMCW radar on its own. Practical SDR-radar tips: use separate TX/RX antennas pointed apart with absorber between; record a loop-back reference of the transmitted waveform (the SDR's internal filters distort it); synchronise TX and RX sample streams (the same device's clock); expect latency jitter from USB — process in blocks with a known reference.

**Passive radar in practice [7], [15].** Two antennas (reference towards the transmitter, surveillance towards the area) on coherent receivers (KrakenSDR, or two RTL-SDRs sharing a clock and calibrated with a noise source), adaptive direct-path/multipath cancellation (e.g. extensive cancellation algorithm, NLMS), then the CAF over 0.1–1 s. FM illuminators are strong (tens of kW) and ubiquitous but give km-scale range-sum resolution; DAB (≈ 1.5 MHz) gives ≈ 200 m and DVB-T (7.6 MHz) ≈ 40 m, but needs wider receivers. Hobbyists routinely see aircraft; drones are much harder (small σ, slow).

**Rocket tracking options (with the avionics context).** The flight computers already measure velocity with high-g accelerometers and GNSS and downlink it over LoRa; a radar's most valuable role is **independent validation** (the team's first engineering tenet is to validate against independent truth, not against the estimator itself).
1. **Upward-looking Doppler at the pad** (HB100/IPM-165-class or a TI board): measures rail-exit and early-boost velocity along the beam with no pointing; range tens of metres for a −20 dBsm tail (see [CW example](cw-and-doppler-radar.md)); FFT windows ≤ 8 ms at 10 g (Doppler rate). A reflector carried inside a radar-transparent (fibreglass) section raises σ: a 5 cm triangular trihedral is −7.7 dBsm at 24 GHz and +2.4 dBsm at 77 GHz (≈ 12–22 dB above a −20 dBsm tail), but it must *face aft* (towards the pad) and only works within ~±20° of its axis; a Luneburg-lens reflector has a much wider acceptance angle (see [RCS](radar-cross-section.md)).
2. **77 GHz FMCW board near the pad:** range + velocity of the first ~20–40 m of flight, and a check of rail-exit timing.
3. **Dish tracker:** a narrow-beam radar on the same kind of az/el mount used for the telemetry Yagi ([15 ground station](../15-lora-ism-radios/ground-station-design.md)), slaved to the rocket's own GNSS position from telemetry, with the radar providing independent range/Doppler. SNR is feasible ([range equation example D](radar-range-equation.md)) but the power levels and S-band frequencies involved need licensing, and slew rates of tens of °/s near the pad are demanding.
   *Monopulse accuracy, GNSS-cued pointing with latency prediction and track filters for this option: [radar tracking](radar-tracking-monopulse-and-trackers.md).*
4. **Cooperative (transponder/beacon) tracking** — as used on sounding rockets — turns the $R^{-4}$ radar link into two $R^{-2}$ one-way links; with LoRa telemetry already on board this is effectively what GNSS + telemetry provides.

## Design equations & rules of thumb

| Rule | Value / formula | Notes |
|---|---|---|
| Doppler per m/s | 70.2 Hz (10.525 GHz), 160.9 (24.125), 513.7 (77 GHz) | [CW page](cw-and-doppler-radar.md) |
| SDR range resolution | c/2B: 20 MHz → 7.5 m; 56 MHz → 2.7 m | stepped frequency for more |
| Leakage budget | echo/leakage must fit ADC DR (~74 dB at 12 bit + FFT gain) | isolation ≥ 40 dB with separate antennas |
| Passive echo/direct | $\sigma L_b^2/(4\pi R_t^2R_r^2)$ | −81 dB example |
| CAF gain | $BT$ | FM 1 s: 52 dB |
| Rocket elevation rate | $v/d$ max | 250 m/s, 500 m → 28.6°/s |
| Ground return | ∝ $1/(2h)^2$ | altimeters: 6 dB per height doubling |
| PFN line-type modulator | $Z_0=\sqrt{L/C}$, $\tau = 2\sqrt{L_{tot}C_{tot}}$, load gets $V_0/2$ | 1 µs, 50 Ω → 10 nF, 25 µH |
| Pulsed average power | $P_{pk}\tau\,\mathrm{PRF}$ | 4 kW, 0.08 µs, 3 kHz → 0.96 W |
| Singapore EIRP limits | 25 mW (2.4 GHz radio-determination), 100 mW (5.8, 24, 60 GHz); 77–81 GHz: mean ≤ −3 dBm/MHz, peak ≤ 55 dBm/50 MHz (UWB) | IMDA TS SRD Sep 2023 [8]; TS UWB 2016 [19] |

## Worked examples

**Example 1 — Choosing a first radar for the club.** Goal: see people and drones in a courtyard, learn range–Doppler–angle. Options: (a) CDM324 + audio amp (~US$10): Doppler only, no range, no direction; (b) BGT60TR13C board: 60 GHz, excellent resolution but short range (IF-limited metres to ~20 m); (c) TI IWR6843/AWR1843 EVM: 3 × 4 MIMO, 4 GHz, tens to ~100 m for cars and ~20–40 m for small drones per virtual channel ([range example B](radar-range-equation.md)) — the best all-rounder; (d) ADI Phaser: for beamforming labs. Pick (c) for radar and (d) for arrays; (a) as a first soldering project.

**Example 2 — Can a Pluto be a drone radar?** At 2.4 GHz with 5 dBm, 10 dBi antennas and 40 dB isolation, a 0.01 m² drone at 100 m is 91 dB below the leakage — beyond a 12-bit ADC's instantaneous range unless the leakage is cancelled or the antennas are separated much further (60+ dB isolation), and with 20 MHz the range cell is 7.5 m. At 25 mW EIRP (Singapore radio-determination limit at 2.4 GHz), $P_tG_t$ = 14 dBm leaves little margin. Verdict: great for learning waveforms and pulse compression at short range; not a practical drone detector.

**Example 3 — Passive radar in Singapore.** A KrakenSDR with a reference Yagi towards an FM transmitter and a surveillance array towards the airport approach: aircraft (σ ~ 10–100 m²) at 10–20 km give echoes ~80 dB below the direct path; after ~40 dB of adaptive cancellation and 52 dB of 1 s CAF gain they stand out with km-scale range and ~3 m/s bistatic-range-rate resolution. Receive-only: no transmitter licence needed.

**Example 4 — Is a TI 77–81 GHz EVM legal to switch on in Singapore?** 77–81 GHz is covered only by the UWB exemption [18][19], whose limit is a *mean e.i.r.p. density*. Take TX = 12 dBm per transmitter, 2 TX on at once (+3 dB), 10 dBi antenna → peak e.i.r.p. ≈ 25 dBm (limit 55 dBm/50 MHz: fine). The chirp spreads that power over its sweep B; with chirps active a fraction $d$ of the frame, the mean density is ≈ $P_{\mathrm{EIRP}} + 10\log_{10} d - 10\log_{10}(B/1\,\mathrm{MHz})$. For B = 4 GHz, d = 0.5: 25 − 3 − 36 = **−14 dBm/MHz** (11 dB under −3 dBm/MHz); for B = 1 GHz: −8 dBm/MHz (5 dB under). A sweep narrower than 500 MHz is *not* UWB (TS UWB §1.2) and has no Singapore exemption above 77 GHz; confine it to 76–77 GHz (TS SRD sub-band 41) instead. The measured mean depends on the detector/averaging procedure of the test standard (ITU-R SM.1754), and §4.1 excludes fixed outdoor installations — a permanent pad-side mount needs IMDA's view. (Arithmetic only; not a conformity test.)

## Practical notes
- **Amplifier for Doppler modules:** two AC-coupled op-amp stages (≈ 20 + 50–60 dB), 6–600 Hz for people or up to tens of kHz for fast targets, low-noise op-amps (e.g. the MC33078 used in InnoSenT's reference circuit [3]), ESD care on the IF pin.
- **Raw data matters:** choose platforms that give raw ADC samples (DCA1000 for TI; BGT60 FIFO; Phaser via Pluto; SDRs) if you want to learn processing — point-cloud-only firmware hides everything.
- **Antenna isolation:** separate TX/RX antennas, absorber (carbon-loaded foam) between them, and a radome placed so its reflection falls in a range bin you can ignore.
- **Frequency accuracy:** DRO/LC modules drift and vary by MHz; PLL-based chips are crystal-accurate.
- **Safety & legality:** all EIRP limits above apply to the *radiated* power including antenna gain; adding a dish to a module changes its legal status. Check [19 IMDA rules](../19-regulations-safety/singapore-imda-rules.md) and, for amateur operation, licence conditions.

## Microwave tubes and pulse modulators

*Added 2026-10-13 (W5-S9, gap G-11-03). Numbers verified by `tools/verify/s9_pfn_tubes.py` (ALL PASS). Tube performance ranges are textbook-typical [20], [21], not datasheet values.*

**Why this still matters.** Surplus marine radars, oven magnetrons and most of the classic radar literature are built around vacuum tubes and high-voltage pulse modulators. For a student radar, the right choice is almost always solid-state (the modules and chips above). Recognise the tube hardware, and know why it is dangerous before anyone opens a microwave oven.

**Intuition.** A few kilovolts accelerate electrons in vacuum to 6–20 % of the speed of light. If that beam is made to interact with a resonant or slowed electromagnetic wave, its kinetic energy turns into RF. A **magnetron** is an oscillator in which electrons circle under crossed electric and magnetic fields. A **klystron** is an amplifier in which an input cavity speeds up some electrons and slows others, so that they bunch while drifting and hand the RF to an output cavity. A **travelling-wave tube (TWT)** is a broadband amplifier in which the beam travels alongside a wave slowed to its own speed. A pulsed radar adds a **modulator**: a circuit that stores energy slowly and dumps it into the tube within a microsecond.

| Device | Principle | Coherent? | Bandwidth / gain (typical) | Where you meet it |
|---|---|---|---|---|
| Cavity magnetron | crossed-field oscillator: radial E, axial B; electron "spokes" lock to the π-mode of the anode cavities; frequency set by the cavities | **no**: each pulse starts at a random phase (MTI uses *coherent-on-receive*: sample the TX pulse and lock or correct the reference) | fixed frequency; efficiency ≈ 50–80 %; **pushing** (frequency moves with current) and **pulling** (frequency moves with load VSWR) | ovens (2.45 GHz, ≈ 1 kW CW), marine/X-band radars (≈ 9.4 GHz, 4–25 kW peak) |
| Klystron | linear beam; velocity modulation → drift bunching → output cavity | yes (amplifier) | a few %; 40–60 dB gain; up to MW pulsed | coherent pulse-Doppler radars, accelerators, transmitters; *reflex klystron* = old single-cavity local oscillator |
| TWT (helix or coupled-cavity) | continuous interaction with a slow-wave circuit whose axial phase velocity ≈ beam velocity | yes | up to an octave; 30–50 dB | EW, satellite TWTAs (Ku/Ka), wideband radars |
| GaN HEMT PA (the modern replacement) | solid-state | yes | 10–100 W-class devices to X-band, combined in T/R modules | new radars, AESA arrays ([12 architectures](../12-phased-arrays/beamforming-architectures.md)) |

**Level 2 — beam velocity and the slow wave.** A beam accelerated through $V$ has $\gamma = 1 + eV/(m_ec^2)$ and $v = c\sqrt{1 - 1/\gamma^2}$. That is 0.062c at 1 kV, **0.108c at 3 kV**, 0.195c at 10 kV and 0.33c at 30 kV. A TWT must slow the RF wave's axial velocity to match. On a helix the wave runs along the wire at about c, so the axial speed is about $c\sin\psi$, a pitch angle of only ≈ 6° for a 3 kV tube. That continuous synchronism, with no resonance needed, is why TWTs are broadband.

**Pulse modulators.**
- **Line-type (PFN) modulator.** A pulse-forming network, an LC ladder that imitates a transmission line of impedance $Z_0 = \sqrt{L/C}$, is resonantly charged to $V_0$ (the charging choke doubles a $V_0/2$ supply). A switch (thyratron, SCR or IGBT stack) then discharges it through a pulse transformer into the tube. A matched load sees a flat pulse of $V_0/2$ lasting $\tau = 2\sqrt{L_{tot}C_{tot}}$. **Worked:** τ = 1 µs into 50 Ω needs $C_{tot} = \tau/2Z_0$ = **10 nF** and $L_{tot} = Z_0\tau/2$ = **25 µH**. A magnetron running at 12 kV and 10 A (1.2 kΩ) needs a 1 : 4.90 transformer and a PFN charged to 4.90 kV. Each pulse carries $\tfrac12CV_0^2$ = 0.120 J = $V I \tau$. A simulated 5-section ladder gives a 2.46 kV flat top (±2 % ripple) and a 1.06 µs width at 50 %. Pulse width is fixed by the network. A mismatched load reflects energy and leaves an inverse voltage on the PFN, removed by an end-of-line clipper diode.
- **Hard-switch ("hard-tube" / solid-state) modulator.** A storage capacitor is switched on *and off*, so the pulse width is programmable. Droop is $\Delta V = I\tau/C$: 10 A for 1 µs from 1 µF droops 10 V (0.08 % of 12 kV).
- **Average power is small.** 4 kW × 0.08 µs × 3 kHz = **0.96 W**; 4 kW × 1 µs × 750 Hz = 3 W; 25 kW × 1.2 µs × 750 Hz = 22.5 W. Detection follows *average* power, so a 100 mW-class FMCW radar with a long dwell can match a small marine magnetron at short range ([FMCW: pulsed vs FMCW](fmcw-radar.md#choosing-a-waveform-pulsed-vs-fmcw-real-vs-complex-if-bistatic-fmcw)). The magnetron's range resolution and blind range are both $c\tau/2$: 12 m at 0.08 µs, 150 m at 1 µs.

**Surplus-magnetron and oven-parts hazards** (expands [19 lab safety](../19-regulations-safety/lab-safety-esd-high-power.md#other-bench-and-station-hazards)):
- **High voltage first.** An oven transformer secondary is about 2 kV rms (repair-literature figure). The half-wave doubler puts up to ≈ 5.7–5.9 kV on the cathode unloaded (≈ 4 kV in operation). The ≈ 0.9–1.1 µF HV capacitor holds **3.6–4.4 J** at its 2.8–3.0 kV peak and can stay charged if its internal bleeder has failed. The transformer can deliver hundreds of mA, so a contact is not survivable. Unplug, discharge each capacitor terminal to the chassis through an insulated resistor probe, and verify with an HV-rated meter. Never run an oven with the case open.
- **RF.** A bare 800 W magnetron (stub antenna ≈ 2.15 dBi) gives ≈ **104 W/m² at 1 m**, ten times the ICNIRP 2020 general-public reference level of 10 W/m² (2–300 GHz) ([RF exposure](../19-regulations-safety/rf-exposure-safety.md)). It stays above that level out to ≈ 3.2 m (far-field estimate; much higher in the near field). For comparison, an oven in service may leak at most 50 W/m² (5 mW/cm²) at 5 cm [22]. The eye lens and metal objects (arcs, burns) are at risk. It would also wipe out 2.4 GHz Wi-Fi and Bluetooth nearby, and radiating it is not covered by any SRD exemption.
- **Materials and X-rays.** Some magnetron insulators are beryllium oxide: never crush or grind them ([BeO row](../19-regulations-safety/lab-safety-esd-high-power.md#other-bench-and-station-hazards)). The ferrite magnets are strong and brittle, and the filament leads sit at cathode HV. Tubes operated at tens of kV (klystrons, large pulsed magnetrons) produce X-rays when run outside their shielding.
- **Surplus marine radars.** The modulator PFN and HV supply hold charge. The 4–25 kW peak is radiated from the open array, so respect the manual's safe distance and never look into or stand in front of an operating waveguide. Transmitting needs an IMDA licence: marine radar bands are licensed services, not SRD bands ([19 IMDA](../19-regulations-safety/singapore-imda-rules.md)).

## Common mistakes & misconceptions
- **"An HB100 can measure distance."** It is CW Doppler only (and single-channel: no direction).
- **"Any SDR can be a radar."** Half-duplex SDRs (HackRF) cannot do monostatic CW/FMCW; all SDRs are limited by instantaneous bandwidth and TX→RX isolation.
- **"Passive radar needs no signal processing skill."** Direct-path cancellation and CAF computation are the whole problem.
- **"A 77 GHz chip can track my rocket to apogee."** It sees tens of metres on a small rocket; use it for launch-phase measurements.
- **"77–81 GHz is legal everywhere."** In Singapore the SRD specification lists only 76–77 GHz (vehicle/infrastructure radar); 77–81 GHz is exempt only as a UWB device (mean ≤ −3 dBm/MHz, ≥ 500 MHz bandwidth, not fixed outdoors) under TS UWB [18][19]. (Corrected 2026-09-29 by W5-E1: the earlier "not listed" statement was true for TS SRD only.)
- **"An oven magnetron is a free 1 kW radar transmitter."** It is a non-coherent CW oscillator at 2.45 GHz with a lethal HV supply, it radiates illegally and dangerously outside its cavity (≈ 104 W/m² at 1 m), and it has no modulator for ranging.
- **"The oven is unplugged, so it is safe."** The HV capacitor can hold ≈ 4 J at ≈ 3 kV; discharge and verify.
- **Ignoring the pointing problem** in rocket tracking — beam width and slew rate, not SNR, usually decide.

## How to simulate / verify
- `tools/verify/radar_diy.py` (~1 s, **ALL PASS**): SDR leakage/echo budget, SDR and stepped-frequency resolution, passive-radar echo-to-direct ratio and CAF gain, rocket-tracking angular rates, IMDA field-strength ↔ EIRP conversion, image-theory ground return.
- `tools/verify/s9_pfn_tubes.py` (< 1 s, **ALL PASS**): PFN sizing and a 5-section ladder transient, pulsed duty/average power, beam velocity vs voltage, oven HV-capacitor energy and bare-magnetron power density.
- Budgets for specific radars: `tools/verify/radar_range_equation.py` (edit the parameters); detection thresholds: `tools/verify/radar_detection_cfar.py`; waveform/processing prototypes: `radar_fmcw.py`, `radar_pulse_compression.py`, `radar_ambiguity.py`.

## Open questions / gaps
- ADI Phaser FMCW ramp parameters and the KrakenSDR maximum sample rate were not confirmed from primary documents.
- 77–81 GHz in Singapore: **resolved 2026-09-29** — licence-exempt as UWB (Notification item 17; TS UWB Table 1) [18][19]. Still open: how IMDA measures "mean" density for FMCW chirps, and whether a hobby sensor at a fixed pad-side mount counts as a "fixed outdoor installation" (TS UWB §4.1) — ask IMDA.
- No hobby-rocket radar measurements were found; a pad-side Doppler experiment would be a valuable first data set (record config, raw IF, and compare against the flight computer's accelerometer-integrated velocity).
- Effective noise figures of Doppler modules at audio IF remain unmeasured.
- Tube performance ranges (magnetron efficiency, klystron/TWT gain and bandwidth) are textbook-typical, cited from memory, not from specific datasheets; oven transformer voltages are repair-literature figures.

## Sources
1. ST Engineering Electronics (AgilSense), HB100 X-band Microwave Sensor Module data sheet V2.02 (2022). https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6360/HB100.pdf (datasheet)
2. InnoSenT, IPM-165 data sheet v8.5 (2014). https://media.digikey.com/pdf/Data%20Sheets/InnoSenT/IPM-165_V8.5_DS.pdf (datasheet)
3. W. Weidmann, InnoSenT Application Note III (IPM-165). https://www.innosent.de/fileadmin/media/dokumente/Downloads/Application_Note_III_-_web.pdf (app note)
4. G. L. Charvat, A. J. Fenn, B. T. Perry, "The MIT IAP radar course: Build a small radar system capable of sensing range, Doppler, and synthetic aperture (SAR) imaging," IEEE Radar Conf. 2012; MIT OCW RES.LL-003 (IAP 2011). https://ocw.mit.edu/courses/res-ll-003-build-a-small-radar-system-capable-of-sensing-range-doppler-and-synthetic-aperture-radar-imaging-january-iap-2011/ (lecture notes / course)
5. Coffee-can radar student build reports (e.g. "Coffee Can Radar Junior Projects", 2017; Union College capstone reports, 2020) — parts list and ramp settings. (project report)
6. Analog Devices, ADALM-PLUTO detailed specifications (wiki): AD9363, 325 MHz–3.8 GHz, 200 kHz–20 MHz, 1 TX/1 RX, full duplex. https://wiki.analog.com/university/tools/pluto/devs/specs (vendor documentation)
7. KrakenRF, KrakenSDR product page and Crowd Supply campaign: five R820T2/RTL2832U receivers on a common LO, 24–1766 MHz, automatic coherence calibration (noise source and switches), DF and passive radar. https://www.krakenrf.com/product-page/krakensdr (vendor)
8. IMDA, "Technical Specification — Short Range Devices," IMDA TS SRD Issue 1 Rev 3, September 2023 (same Table 1 radar rows as the April 2023 printing), Table 1 (sub-bands 32a–e, 36a, 37, 38a–c, 39a–b, 40, 41); Table 2 has no radar rows. https://www.imda.gov.sg/-/media/imda/files/regulation-licensing-and-consultations/ict-standards/telecommunication-standards/radio-comms/imdatssrd.pdf (regulation)
9. Texas Instruments product pages IWR6843, AWR1843, AWR2944 (accessed 2026-09-27); V. Dham, SWRA553A. (datasheet / app note)
10. Infineon, BGT60TR13C data sheet. https://www.infineon.com/part/BGT60TR13C (datasheet)
11. Acconeer, A121 Pulsed Coherent Radar data sheet (v1.x): 60 GHz, AiP, up to 20 m, mm absolute / µm relative accuracy, 5.5 × 5.2 × 0.88 mm. (datasheet; via distributor copies)
12. Analog Devices, CN0566 circuit note and EVAL-CN0566-RPIZ user guide. https://www.analog.com/en/resources/reference-designs/circuits-from-the-lab/cn0566.html (circuit note)
13. Mini-Circuits, ZX95-2536C+ data sheet. https://www.minicircuits.com/pdfs/ZX95-2536C+.pdf (datasheet)
14. M. Lichtman, *PySDR*, "Hands-on with Phaser." https://pysdr.org/content/phaser (online textbook)
15. H. D. Griffiths, C. J. Baker, *An Introduction to Passive Radar*, Artech House, 2017. (textbook)
16. H. Forstén, 6 GHz FMCW radar and SAR projects. https://hforsten.com/ (project report)
17. `tools/verify/radar_diy.py` — computed values on this page. (verification script)
18. *Telecommunications (Exemption from sections 53, 54(1)(b) and 55) Notification* (N 1), First Schedule items 13, 15 (Short Range Radar System 76.00–77.00 GHz: 55 dBm peak e.i.r.p.; 23.5 dBm average pulse / 50 dBm average other) and 17 (Ultra-Wideband Devices; 77.00–81.00 GHz −3 dBm/MHz) — Singapore Statutes Online, current version as at 2026-09-29, read in a browser. https://sso.agc.gov.sg/SL/TA1999-N1 (legislation)
19. IMDA, *Technical Specification — Ultra-Wideband (UWB) Devices*, IMDA TS UWB Issue 1 (1 October 2016) — §1.2 (UWB definition: 10 dB bandwidth ≥ 500 MHz or fractional > 0.2), §4.1 (not for fixed outdoor installations/externally mounted antennas), Table 1 (77–81 GHz: mean e.i.r.p. density −3 dBm/MHz, peak 55 dBm/50 MHz; automotive SRR column cites ECC/DEC/(04)03). https://www.imda.gov.sg/-/media/imda/files/regulation-licensing-and-consultations/ict-standards/telecommunication-standards/radio-comms/imda-ts-uwb.pdf (regulator standard)
20. M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed., McGraw-Hill, 2001, ch. 10 (radar transmitters: magnetron, klystron, TWT, line-type and hard-tube modulators, PFN). (textbook; cited from memory; the chapter number and scope were confirmed against the chapter map in gaps/D4-curriculum.md §3.19 by W5-S18, 2026-10-13, but the section content was not re-read)
21. A. S. Gilmour Jr., *Klystrons, Traveling Wave Tubes, Magnetrons, Crossed-Field Amplifiers, and Gyrotrons*, Artech House, 2011 — tube physics and typical performance. (textbook; cited from memory)
22. US 21 CFR 1030.10 — microwave-oven leakage limits: 1 mW/cm² before purchase, 5 mW/cm² thereafter, at 5 cm. (regulation)
23. `tools/verify/s9_pfn_tubes.py` — numbers in the tubes/modulators section. (verification script)
