---
title: FMCW radar — beat frequency, range/velocity/angle resolution, chirp design, range–Doppler processing, phase noise and leakage, VCO nonlinearity, TI/Infineon/ADI devices
domain: 11-radar
slug: fmcw-radar
tags: [fmcw, chirp, beat-frequency, dechirp, range-fft, doppler-fft, angle-fft, range-doppler-map, radar-cube, chirp-design, if-bandwidth, adc, idle-time, range-migration, range-doppler-coupling, phase-noise, range-correlation, leakage, vco-nonlinearity, predistortion, ti-mmwave, awr1843, iwr6843, bgt60tr13c, adi-phaser, coffee-can, pulsed-vs-fmcw, complex-baseband, real-if, image-noise, iq-imbalance, bistatic-fmcw, radar-altimeter, step-error, fast-time, slow-time, a-scope, b-scope, ppi, video]
prerequisites:
  - radar-range-equation.md
  - cw-and-doppler-radar.md
  - pulsed-radar-and-pulse-compression.md
  - ../14-sdr-dsp/fft-spectral-analysis-windows.md
related:
  - detection-theory-cfar.md
  - ambiguity-function-waveforms.md
  - mimo-radar-virtual-arrays.md
  - clutter-and-mti.md
  - sar-and-imaging.md
  - diy-radar-hardware.md
  - ../07-noise-linearity/phase-noise-and-jitter.md
  - ../06-rf-circuits/vco-and-pll-synthesizers.md
  - ../12-phased-arrays/array-factor-linear-arrays.md
  - ../20-projects-recipes/fmcw-radar-build.md
  - pulse-doppler-data-cube-and-prf-regimes.md
  - diy-radar-hardware.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# FMCW radar

## Questions this page answers
- How does an FMCW radar turn distance into a frequency, and where does $f_b = 2SR/c$ come from?
- What sets range resolution, maximum range, velocity resolution and maximum velocity?
- Why is maximum range limited by the IF bandwidth / ADC rate as well as by SNR?
- How do I design a chirp (bandwidth, slope, ramp time, idle time, number of chirps) for a given job?
- How do the range FFT, Doppler FFT and angle FFT build a range–Doppler map and a point cloud?
- Why do approaching targets show up at *negative* Doppler bins in TI data?
- How are TI's AWR/IWR chirp parameters (idle time, ADC start, ramp end, slope) chosen?
- Why does TX leakage raise the noise floor near zero range, and what is the range-correlation effect?
- What does VCO chirp nonlinearity do to the range profile, and how do I fix it?
- What do the Infineon BGT60TR13C and the ADI Phaser (CN0566) offer?
- Can I build an FMCW radar with a sound card like the MIT coffee-can radar?
- Should my radar be pulsed or FMCW?
- Why does a complex (I/Q) IF give up to 3 dB better SNR than a real IF, and what does I/Q imbalance do?
- Can FMCW work bistatically, with the transmitter and receiver in different places?
- How accurate is an FMCW radar altimeter, and what are the step (fixed) error and the Doppler bias?
- What do fast time, slow time, A-scope, B-scope, PPI and "video" mean?

## TL;DR
- **Principle:** transmit a linear chirp of slope $S = B/T$ (Hz/s); mix the echo with the transmit signal. A target at range $R$ gives a **beat tone $f_b = S\tau = 2SR/c$** with phase $4\pi R/\lambda$ (plus a tiny residual-video-phase term). An FFT of the beat signal (the "range FFT") is the range profile.
- **Range resolution $c/(2B)$** (4 GHz → 3.75 cm; 1 GHz → 15 cm). **Max range from the IF:** $R_{max} = f_{IF,max}c/(2S)$ — TI allows $f_{IF,max}$ = 0.9 $f_s$ for complex and 0.45 $f_s$ for real sampling [1]. SNR limits range separately ([radar equation](radar-range-equation.md)).
- **Velocity** from the phase change $4\pi v T_c/\lambda$ between chirps: **$v_{max} = \pm\lambda/(4T_c)$** ($T_c$ = chirp repetition period *including idle time*), **$\Delta v = \lambda/(2NT_c)$** (frame time). **Angle** from the phase step across RX antennas: FoV $\pm\sin^{-1}(\lambda/2d)$, resolution ≈ $2/N$ rad at boresight for $d = \lambda/2$ (4 RX ≈ 29°) [1], [2].
- **Processing chain:** ADC cube [RX × chirp × sample] → window + range FFT → window + Doppler FFT → non-coherent sum over RX → 2-D CFAR → angle FFT per detection. The script detects four synthetic targets with correct range (±0.1 m), velocity (±0.2 m/s) and angle (±0.1°).
- **Convention trap:** with IF = TX · conj(RX) (TI's mixer model), approaching targets have *decreasing* IF phase → **negative Doppler bins** (Rao: "movement towards the radar ⇒ ω < 0") [2].
- **Leakage + phase noise:** TX→RX leakage (isolation ~30 dB at best [3]) appears as a huge near-zero-range tone carrying LO phase noise reduced by the **range-correlation factor $4\sin^2(\pi f\tau)$** (verified by simulation). A −95 dBc/Hz (1 MHz) LO leaves −145 dBc/Hz for a 0.5 ns leakage path but −125 dBc/Hz for 5 ns — a radome or bumper reflection can lift the near-range floor above thermal noise.
- **VCO nonlinearity** smears targets in proportion to range: a real Mini-Circuits ZX95-2536C+ VCO driven by a linear 1.5–3.5 V ramp (the coffee-can architecture) broadens the −3 dB range width from 1.5 m to **3.9 m at 100 m and 12.4 m at 300 m**; predistorting the tuning voltage with the inverse tuning curve restores 1.5 m. PLL-generated ramps (TI, Infineon, ADF4159) avoid the problem.
- **Pulsed vs FMCW** at equal average power is a tie; at equal *peak* power (a cheap PA or an e.i.r.p. cap) FMCW wins by $-10\log(\text{duty})$ (20 dB at 1 %), has no blind range and needs only a MHz ADC, but is isolation-limited at long range ([decision table](#choosing-a-waveform-pulsed-vs-fmcw-real-vs-complex-if-bistatic-fmcw)). A **real IF** costs up to 3 dB (image-noise fold-back; Monte Carlo 3.03 dB) and halves $R_{max}$; I/Q imbalance of 0.5 dB / 5° leaves a mirror ghost at −25.6 dB. **Bistatic FMCW** turns a 1 ppm offset at 24 GHz into a 28.9 m range-sum bias with slow ramps; reference to the direct path.
- **Altimeters:** a cycle-counting FMCW altimeter has a step (fixed) error $c/(4\Delta F)$ (0.30 m at 250 MHz); a single ramp has a Doppler bias $f_Dc/2S$ (2.4 m at 25 m/s on a 250 MHz/1 ms ramp) that up/down pairing cancels; track the leading edge, not the centroid ([error budget](#fmcw-radio-altimeters-error-budget)).
- **Worked chirp (77 GHz drone radar, 100 m / 0.5 m / ±30 m/s / 0.25 m/s):** B = 300 MHz, $T_c$ ≤ 32.4 µs, S = 12 MHz/µs over a 25 µs ADC window, $f_{IF,max}$ = 8 MHz (10 Msps complex, 250 samples), 256 chirps, frame 8.2 ms, 1 MiB radar cube (1 TX × 4 RX).

## Intuition (no math)
An FMCW radar transmits a tone whose frequency rises steadily — a chirp — for tens of microseconds to milliseconds, again and again. The echo is the same chirp, delayed by the round-trip time. At any instant, the echo is therefore at a slightly lower frequency than what is being transmitted *now*, and the difference is proportional to the delay: far targets are "further behind" on the frequency ramp. Mixing the echo with the current transmit signal produces this difference frequency — the beat — which is low (kHz to MHz) and easy to digitise. A Fourier transform of the beat separates the targets by frequency, i.e. by range. It is like measuring distance with a musical scale being played continuously: the note you hear back tells you how long ago it was sung.

Resolution comes from the total frequency span of the chirp (bandwidth): the longer you observe two nearly equal beat tones, the better you can tell them apart, and a longer observation of a given slope sweeps more bandwidth. The maximum distance is set by how high a beat frequency your ADC can digitise, and by whether the echo is still above the noise.

Velocity is measured from chirp to chirp. A target moving by a fraction of a millimetre between chirps barely changes its beat frequency, but it changes its *phase* noticeably (a full cycle per half-wavelength of motion — 1.95 mm at 77 GHz). An FFT across the chirps turns that phase rotation into a velocity. The same trick across several receive antennas (the echo reaches each at a slightly different phase) gives the direction.

The big practical enemy is the transmitter itself: it is always on, and some of it leaks into the receiver right next to it. That leakage looks like an enormous target at almost zero range, and it drags the transmitter's own noise along with it.

## The math

### Level 1 — the core relationships
Chirp: start frequency $f_c$, sweep bandwidth $B$ over ramp (ADC) time $T$, slope $S = B/T$ (Hz/s); chirp repetition period $T_c$ (ramp + idle); $N$ chirps per frame; $N_{RX}$ receivers spaced $d$.

| Quantity | Formula | Symbols |
|---|---|---|
| Beat frequency | $f_b = S\tau = 2SR/c$ | τ round-trip delay |
| Beat phase | $\phi = 4\pi R/\lambda$ (mod 2π) | λ = c/f_c |
| Range resolution | $\Delta R = c/(2B)$ | B = sampled sweep |
| Max range (IF) | $R_{max} = f_{IF,max}c/(2S)$ | $f_{IF,max}$ ≤ 0.9 $f_s$ (complex), 0.45 $f_s$ (real) [1] |
| Max unambiguous velocity | $v_{max} = \pm\lambda/(4T_c)$ | $T_c$ incl. idle |
| Velocity resolution | $\Delta v = \lambda/(2NT_c) = \lambda/(2T_f)$ | $T_f$ = frame (active) time |
| Angle | $\theta = \sin^{-1}\!\big(\lambda\omega/(2\pi d)\big)$ | ω = phase step between RX |
| Field of view | $\pm\sin^{-1}(\lambda/2d)$ | d = λ/2 → ±90° |
| Angle resolution | $\theta_{res} = \lambda/(Nd\cos\theta)$ → $2/N$ rad | N receive (or virtual) channels |

### Level 2 — derivations

**The beat signal.** Transmit phase $\varphi_T(t) = 2\pi(f_ct + \tfrac12St^2)$ for $0 \le t \le T$. The echo is $\varphi_T(t-\tau)$. An ideal mixer producing TX × conj(RX) gives
$$\varphi_{IF}(t) = \varphi_T(t) - \varphi_T(t-\tau) = 2\pi\left(f_c\tau + S\tau\,t - \tfrac12S\tau^2\right)$$
(verified exactly in the script). Three terms:
- $S\tau\,t$ → the beat frequency $f_b = S\tau = 2SR/c$;
- $f_c\tau$ → the phase $2\pi f_c\tau = 4\pi R/\lambda$ that carries velocity and angle information;
- $-\pi S\tau^2$ → the **residual video phase** (RVP). It is constant within a chirp for a static target and identical across chirps and antennas, so it does not affect range, Doppler or angle FFTs; it matters in SAR/stretch processing with long ranges (it reached 15 rad at 60 m with 30 MHz/µs — large but harmless here) [4].

For a moving target $R = R_0 - v_r t$ (closing speed $v_r$): within one chirp, the beat picks up the Doppler term, $f_{IF} = 2SR/c - 2v_r/\lambda$ (range–Doppler coupling: a range bias $-v_r\lambda^{-1}c/S$; 7.7 cm at 30 m/s with 30 MHz/µs); across chirps, the phase changes by $\Delta\phi = -4\pi v_rT_c/\lambda$ per chirp.

**Range resolution.** Two beat tones separated by $\Delta f$ are resolved by an FFT of length $T$ if $\Delta f \gtrsim 1/T$ [2]. With $\Delta f = 2S\Delta R/c$: $\Delta R \ge c/(2ST) = c/(2B)$. Resolution depends only on the swept (and sampled) bandwidth — not on slope or duration separately. Windowing widens the main lobe: for a 1 dB dip between equal targets (incoherent) the script finds **1.02 bins (rectangular), 1.50 (Hamming), 1.66 (Hann)**. Coherent targets can merge (in phase) or show a notch (anti-phase) regardless — resolution is statistical.

**Maximum range from the IF.** The ADC must digitise $f_{b,max} = 2SR_{max}/c$. With complex (I/Q) sampling of TX·conj(RX), all beats are positive, so the whole band 0…$f_s$ is usable; with real sampling only 0…$f_s/2$. TI's anti-alias/decimation filters leave ≈ 90 % usable [1]. Example: $f_s$ = 10 Msps complex, S = 30 MHz/µs → 45 m; real → 22.5 m; S = 10 MHz/µs → 135 m. (Sampling a 12 MHz beat at 20 Msps complex aliases it to −8 MHz — the script's first run did exactly that.)

**Velocity.** Across chirps the phase advances by $\omega = 4\pi vT_c/\lambda$ per chirp; it is unambiguous for $|\omega| < \pi$ ⇒ $v_{max} = \lambda/(4T_c)$ [2]. An $N$-point FFT across chirps resolves $\Delta\omega = 2\pi/N$ ⇒ $\Delta v = \lambda/(2NT_c)$. (TI's SWRA553 prints the latter under the heading "max velocity" — a typo; its formula is the resolution [1].) The Doppler FFT is coherent integration: SNR gain $N$.

**Angle.** A plane wave from angle θ reaches adjacent RX antennas with a path difference $d\sin\theta$, i.e. phase step $\omega = 2\pi d\sin\theta/\lambda$. An FFT across the $N$ antennas (the "angle FFT") finds ω; unambiguous for $|\omega| < \pi$ ⇒ FoV $\pm\sin^{-1}(\lambda/2d)$. Two angles are separated if $\Delta\omega > 2\pi/N$; since $d\omega/d\theta = 2\pi d\cos\theta/\lambda$, $\theta_{res} = \lambda/(Nd\cos\theta)$, i.e. $2/N$ rad at boresight for $d = \lambda/2$ (4 RX: 28.6°, 8 RX: 14.3°) [2], [5]. This is the array factor of a uniform linear array (see [12 array factor](../12-phased-arrays/array-factor-linear-arrays.md)); MIMO multiplies $N$ ([MIMO](mimo-radar-virtual-arrays.md)).

**The radar cube and the processing chain.** Store samples as `cube[rx, chirp, sample]`.
1. Range FFT along `sample` (window, e.g. Hann) → `[rx, chirp, range_bin]`.
2. Optional static-clutter removal: subtract the mean over chirps for each range bin (a zero-Doppler notch — removes leakage and stationary clutter; an MTI, see [clutter](clutter-and-mti.md)).
3. Doppler FFT along `chirp` (window) → range–Doppler map per RX.
4. Non-coherent sum of $|\cdot|^2$ over RX (or beamform) → detection map.
5. 2-D CFAR ([detection](detection-theory-cfar.md)) → detections.
6. For each detection, angle FFT across RX (after TDM-MIMO Doppler compensation) → (range, velocity, angle) point cloud.

The script runs this chain on four targets (5 m / 0 m/s / 0°; 12.3 m / −4.2 m/s / +20°; 12.3 m / +6.0 m/s / −30°; 31.7 m / +10.5 m/s / +10°) with 256 samples × 128 chirps × 4 RX at 77 GHz: all four detected, estimates within one bin (e.g. 31.62 m, +10.55 m/s, +9.9°), no false detections. Note the two targets at the same range separated only in Doppler, as Rao's slides stress [2].

**Slow FMCW with up/down ramps (triangular).** Classic single-ramp radars (coffee can, level sensors, early automotive) measure one beat per ramp: $f_{up} = f_R - f_d$, $f_{down} = f_R + f_d$ (signs depend on convention) ⇒ $f_R = (f_{up} + f_{down})/2$, $f_d = (f_{down} - f_{up})/2$. With several targets the pairing of up and down peaks becomes ambiguous — the reason automotive radars moved to fast chirp sequences with a Doppler FFT.

### Level 3 — what limits real FMCW radars

**TX leakage, phase noise and range correlation.** Leakage (on-chip coupling, antenna coupling, radome reflection — and, in a monostatic design with a circulator, mostly the *antenna's* reflection rather than the circulator's isolation: 33 dBm TX into an antenna with 15 dB return loss puts up to +21.5 dBm at the RX port, [circulators](../06-rf-circuits/circulators-isolators.md)) appears in the IF as a strong beat at $f_{b,L} = S\tau_L$ (near zero range). Its LO phase noise is partly cancelled because TX and leakage share the same oscillator with a tiny delay:
$$\mathcal L_{IF}(f) = 2\mathcal L_{LO}(f)\,\big(1 - \cos 2\pi f\tau_L\big) = 4\sin^2(\pi f\tau_L)\,\mathcal L_{LO}(f) \approx (2\pi f\tau_L)^2\mathcal L_{LO}(f),$$
the range-correlation effect (Budge & Burt, quoted in [3]). The script synthesises LO phase noise with a −95 dBc/Hz at 1 MHz (1/f²) profile (an AWR1843-class figure [6]) and confirms the IF skirt equals this formula (median ratio 1.00). Consequences:
- A 0.5 ns leakage path (7.5 cm) reduces the LO noise at 1 MHz offset to −145 dBc/Hz; 5 ns (75 cm) only to −125 dBc/Hz.
- With 12 dBm TX and 30 dB isolation (−18 dBm leakage) the skirt at a 1 MHz beat offset is −163 dBm/Hz for 0.5 ns (below the −159 dBm/Hz thermal floor of a 15 dB NF receiver) but −151 dBm/Hz for 2 ns — **8 dB above thermal**: weak targets near a strong reflector (radome, bumper, a launch rail) are masked [3].
- Echoes from *distant* strong targets are poorly correlated ($f\tau$ not small) and carry their full phase-noise skirt into neighbouring range bins — a strong car can raise the floor around itself.
Remedies: short leakage paths, good isolation (separate TX/RX antennas, absorber), radome at a range bin that can be notched, low-phase-noise synthesiser, digital leakage cancellation.

**Sensitivity-time control by IF high-pass filtering.** Echo power falls as $R^{-4}$ while $f_b \propto R$, so a second-order high-pass IF filter (+40 dB/decade below its corner) flattens the dynamic range across range and suppresses leakage/DC — a built-in STC. TI devices include programmable IF high-pass corners [1]; ADC dynamic range (12-bit ≈ 74 dB) otherwise sets the near/far limit.

**Chirp nonlinearity.** If $f(t)$ deviates from linear by $\delta f(t)$, the beat frequency varies within the chirp as $\tau\,\dot f(t)$, and the phase error grows with τ: range peaks broaden and spurious sidelobes appear, **worse at long range** [7]. Using the measured tuning table of a Mini-Circuits ZX95-2536C+ (sensitivity falls from 82 to 36 MHz/V across 0–5 V [8]) with a linear 1.5–3.5 V, 20 ms ramp (143 MHz, slope varying 6.35–7.49 GHz/s):

| Target range | −3 dB width (Hann), linear V_tune | vs ideal chirp (1.52 m) |
|---|---|---|
| 20 m | 1.62 m | 1.1× |
| 100 m | 3.92 m | 2.6× |
| 300 m | 12.4 m | 8.1× |

Remedies, from simplest: (1) **predistort** the tuning voltage with the inverse tuning curve (restores 1.52 m at 300 m in simulation; needs a DAC and temperature tracking); (2) **resample** the IF on a uniform-phase grid derived from a reference delay line (or a known target) — "reference-based linearisation"; (3) generate the ramp with a **fractional-N PLL** (ADF4159 in the Phaser, integrated synthesisers in TI/Infineon chips), which locks the chirp to a crystal [4], [7]. Periodic vs random nonlinearities affect accuracy differently [7].

**Range migration.** During a frame a target moves $vNT_c$; if that exceeds ≈ $\Delta R$ the Doppler FFT smears across range bins. With the simulated chirp (4.4 ms frame, 19.5 cm bins) 30 m/s moves 13.3 cm (0.68 bins) — acceptable; long frames or fine resolution need keystone/migration correction [4].

**TDM-MIMO and velocity.** Time-multiplexing $N_{TX}$ transmitters stretches the effective chirp period to $N_{TX}T_c$, cutting $v_{max}$ by $N_{TX}$, and adds a velocity-dependent phase between TX slots that must be corrected before the angle FFT [5] — see [MIMO](mimo-radar-virtual-arrays.md).

**Interference.** Two FMCW radars with different slopes produce a brief wideband chirp-crossing burst in each other's IF, raising the noise floor over the whole range profile; identical slopes can produce ghost targets. Mitigations: detect and zero (or interpolate) the corrupted samples, randomise start frequency/idle times (TI supports per-chirp dithers [1]).

**TI chirp timing parameters [1].** Per profile: start frequency, slope, idle time, ADC start time, ramp end time (plus TX start time). Minimum idle time is set by synthesiser ramp-down settling: **2 µs (< 1 GHz ramp), 3.5 µs (1–2 GHz), 5 µs (2–3 GHz), 7 µs (> 3 GHz)**; ADC start time allows PLL ramp-up, IF high-pass and DFE filter settling; ramp end = ADC start + sampling time + excess ramp for DFE latency (0.1–1 µs depending on mode and rate). Up to 4 profiles and 512 chirp definitions per frame with small per-chirp dithers; up to 4 sub-frames for multi-mode (short + long range) operation. TI's example configurations (all reproduced by the script from the formulas; `tools/verify/radar_fmcw.py`):

| TI example [1] | Slope | Chirp (ADC) | Idle | Chirps | BW | ΔR | $R_{max}$ (IF) | $v_{max}$ |
|---|---|---|---|---|---|---|---|---|
| LRR | 10 MHz/µs | 30 µs | 8 µs | 256 | 300 MHz | 0.50 m | 225 m | 92 km/h |
| MRR | 12 | 45 | 10 | 128 | 540 MHz | 0.28 m | 125 m | 64 km/h |
| SRR | 15 | 50 | 12 | 128 | 750 MHz | 0.20 m | 45 m | 57 km/h |
| USRR | 30 | 50 | 50 | 128 | 1500 MHz | 0.10 m | 22.5 m | 35 km/h |

(Computed $v_{max}$ agrees with TI to < 0.2 % except USRR: 35.04 vs the published 35.3 km/h — a rounding difference in TI's wavelength or timing.)

## Design equations & rules of thumb

| Step | Rule | Example (77 GHz) |
|---|---|---|
| 1. Resolution → B | $B = c/(2\Delta R)$ | 0.5 m → 300 MHz |
| 2. $v_{max}$ → $T_c$ | $T_c \le \lambda/(4v_{max})$ (÷ $N_{TX}$ for TDM) | ±30 m/s → 32.4 µs |
| 3. ADC window & slope | $T_{ADC} < T_c$ − idle − ADC start; $S = B/T_{ADC}$ | 25 µs → 12 MHz/µs |
| 4. $R_{max}$ → IF & $f_s$ | $f_{IF,max} = 2SR_{max}/c \le 0.9f_s$ (complex) | 8 MHz ≤ 9 MHz @10 Msps |
| 5. Δv → N | $N \ge \lambda/(2\Delta v\,T_c)$ | 0.25 m/s → 243 → 256 |
| 6. Memory | $N_s \times N \times N_{RX} \times$ 4 B | 250 × 256 × 4 × 4 B = 1000 KiB |
| 7. SNR check | radar equation with $T_{coh} = NT_{ADC}$ | [range-equation page](radar-range-equation.md) |
| 8. Angle | $\theta_{res} \approx 2/N_{virt}$ rad | 12 virtual → 9.5° |

Other rules: 1 mm of radial motion at 77 GHz = 3.2 rad of phase (4πd/λ); complex sampling doubles $R_{max}$ over real; windowing costs ~1.5 bins of resolution and 1.3–1.8 dB SNR ([radar-equation losses](radar-range-equation.md)); keep $vNT_c < \Delta R$ to avoid range migration.

## Worked examples

**Example 1 — Chirp design for a 77 GHz drone radar** (requirements 100 m, 0.5 m, ±30 m/s, 0.25 m/s; single TX). From the table: B = 300 MHz; $T_c$ ≤ 32.4 µs → choose 32 µs (v_max ±30.4 m/s) with a 25 µs ADC window (7 µs for idle + settling: TI's 2 µs minimum idle for < 1 GHz ramps plus ADC start time); S = 12 MHz/µs; $f_{IF,max}$ = 8.0 MHz → 10 Msps complex (0.9 $f_s$ = 9 MHz), 250 samples/chirp (FFT 256); N ≥ 243 → 256 chirps (frame 8.19 ms, Δv = 23.8 cm/s); cube 1000 KiB for 4 RX — fits a TI xWR1843 (2 MB). If you switch to 3-TX TDM-MIMO for angle resolution, $v_{max}$ drops to ±10 m/s unless $T_c$ is cut to ~11 µs (then S rises, $R_{max}$ falls): the classic FMCW trade-off.

**Example 2 — Why TI's LRR profile uses a *small* slope.** The LRR profile's ≈ 15 MHz maximum IF (16.67 Msps) [1] must hold beats out to 225 m: $S = f_{IF}c/(2R)$ = 10 MHz/µs. Over a 30 µs chirp that is only 300 MHz of bandwidth → 0.5 m resolution. The short-range USRR profile uses 30 MHz/µs × 50 µs = 1.5 GHz → 10 cm. With the same 15 MHz IF it would reach $R_{max} = f_{IF}c/(2S)$ = 15 MHz × 3×10⁸/(2 × 30 MHz/µs) = **75 m**; TI's USRR profile actually samples at 5 Msps with a 4.5 MHz maximum IF [1], which gives the tabulated **22.5 m** (`radar_fmcw.py` §2). Either way, $R_{max}/\Delta R = f_{IF}T_{ADC}$ (the number of usable range bins: 450 for LRR, 750 for USRR at 15 MHz, 225 at TI's 4.5 MHz), so at a fixed IF bandwidth tripling the slope cuts the range 3× (225 → 75 m) even though the resolution gets 5× finer. Long range and fine resolution fight over the IF bandwidth.

**Example 3 — Coffee-can FMCW with a sound card.** ~90 MHz swept in 20 ms (S = 4.5 GHz/s) at 2.4 GHz, IF digitised at 44.1 kHz (real): $R_{max}$ = 22.05 kHz × c/(2S) = 734 m, ΔR = 1.67 m. The ZX95-2536C+ VCO driven by a linear ramp broadens a 100 m target by 2.6× and a 300 m target by 8× — the coffee-can's ranging is only sharp at short range unless you predistort or calibrate [8], [9].

**Example 4 — Leakage-limited near range.** 12 dBm TX, 30 dB isolation, −95 dBc/Hz LO at 1 MHz: with the leakage path at 0.5 ns the skirt is 4 dB below the 15 dB-NF thermal floor; move the radome to 30 cm (2 ns round trip) and the skirt is 8 dB above thermal near the radome bin. Keep radomes close and thin (or at a notched range bin), and use separate TX/RX antennas with absorber between them.

**Example 5 — Infineon BGT60TR13C.** 58.0–63.5 GHz, 1 TX / 3 RX antennas in package, > 5 GHz bandwidth, 12-bit ADCs up to 4 MSps [10]: the full 5.5 GHz sweep gives 2.7 cm resolution. With a 5 GHz sweep in 64 µs (78 MHz/µs) and 2 MSps real sampling, $R_{max}$ (IF) ≈ 1.9 m — a gesture/presence sensor. For more range use a gentler slope (e.g. 1 GHz over 128 µs, 7.8 MHz/µs → ~19 m) at the cost of resolution. Oxygen absorption at 60 GHz (≈ 15 dB/km) is negligible indoors.

## Practical notes
- **TI mmWave workflow:** the CLI config line `profileCfg` sets start frequency, idle time, ADC start time, ramp end time, TX power backoff, slope, TX start, ADC samples, sample rate, HPF corners and RX gain; `chirpCfg` assigns TX antennas per chirp (TDM-MIMO); `frameCfg` sets chirps per frame and frame period. Use TI's mmWave Sensing Estimator/Radar Studio timing calculator to get legal idle/ADC-start values [1]. Raw ADC capture needs the DCA1000 board (LVDS) or the device's own DSP chain.
- **Device summary (TI product pages [6]):** IWR6843: 60–64 GHz, 3 TX / 4 RX, 12 dBm, NF 12 dB, −93 dBc/Hz @ 1 MHz, 25 Msps, C674x DSP + R4F + HWA. AWR1843: 76–81 GHz, 3/4, 12 dBm, NF 14–15 dB, −95/−93 dBc/Hz. AWR2944: 76–81 GHz, 4/4, 13.5 dBm, NF 12 dB, −96/−95 dBc/Hz, 37.5 Msps, R5F + C66x + HWA2.1.
- **ADI Phaser (CN0566):** 8-element 10.0–10.5 GHz patch array, two ADAR1000 beamformers, ADF4159 PLL + HMC735 VCO (10.5–12.7 GHz LO) capable of sawtooth/triangular FMCW ramps, LTC5548 mixers to a ~2.2 GHz IF digitised by an ADALM-Pluto; element spacing 14 mm ≈ 0.48λ [11]. A good platform to learn FMCW + beamforming together (PySDR chapter [11]); the chirp parameters of ADI's FMCW example scripts were not verified here.
- **Regulatory (Singapore, IMDA TS SRD Issue 1 Rev 3, Sep 2023):** 24.00–24.25 GHz (only 250 MHz → 60 cm resolution) and 57–64 GHz at ≤ 100 mW EIRP; 76–77 GHz for vehicle/fixed-infrastructure radar [12]. **77–81 GHz is not in TS SRD but is licence-exempt as an Ultra-Wideband device** (Exemption Notification First Schedule item 17; IMDA TS UWB 2016 Table 1): mean e.i.r.p. density ≤ −3 dBm/MHz, peak ≤ 55 dBm/50 MHz, sweep ≥ 500 MHz, not a fixed outdoor installation — a 4 GHz TI chirp is ≈ 10 dB under the density limit ([DIY radar Example 4](diy-radar-hardware.md#worked-examples); [19 IMDA](../19-regulations-safety/singapore-imda-rules.md)).
- **Mounting:** radome thickness a multiple of λ/2 in the material (λ/(2√ε_r) ≈ 1.1 mm for polycarbonate, ε_r ≈ 2.9, at 77 GHz) and close to the antenna; no metal screws in the antenna near field; absorber between TX and RX patches.
- **DIY discrete FMCW:** use a PLL chirp generator (ADF4159, or an MCU-controlled fractional-N synth), a mixer and a low-noise IF amplifier with a high-pass for STC, and an audio or USB ADC; see Forstén's 6 GHz designs for a complete open project [13] and [DIY hardware](diy-radar-hardware.md).

## Choosing a waveform: pulsed vs FMCW, real vs complex IF, bistatic FMCW

*Added 2026-10-13 (W5-S9, gap G-11-01). Numbers verified by `tools/verify/s9_fmcw_if_bistatic.py` (ALL PASS).*

### Pulsed or FMCW? (intuition first)
Detection depends on the **energy** put on the target during the dwell, $E = P_{avg}T_{dwell}$, not on the peak power: the [radar equation](radar-range-equation.md) budgets $E/N_0$ ([canonical convention](../00-math-foundations/canonical-values-and-conventions.md)). With the same average power and dwell, a pulsed radar and an FMCW radar detect equally well. The choice therefore comes down to hardware. Can you make high peak power, or only modest continuous power? Can you isolate the receiver from your own transmitter? How close in must you see? How fast an ADC can you afford?

| Criterion | Pulsed (incl. pulse compression) | FMCW | Numbers (script) |
|---|---|---|---|
| Energy at a **fixed peak power** (an EIRP cap or a small PA) | duty $d$ ≈ 0.1–1 % → $E$ falls by $10\log d$ | 100 % duty | 100 mW, 5.8 GHz, 20 dBi, 0.01 m² drone at 1 km, NF 6 dB, 6 dB loss, 10 ms: **E/N0 = −16.7 dB pulsed (1 %) vs +3.3 dB FMCW**. FMCW reaches 13.2 dB with a 98 ms dwell. The pulsed radar would need 100× the peak power (cf. W5-E8: a 100 mW SDR pulsed radar is ≈ 30 dB short) |
| Transmitter | kW peak from magnetrons, TWTs or GaN, with modulators ([DIY hardware: tubes](diy-radar-hardware.md#microwave-tubes-and-pulse-modulators)) | mW–W of CW from a VCO/PLL plus PA: cheap, single-chip | — |
| Minimum range | **blind (eclipsed) range** $c\tau/2$ = 150 m per µs of pulse, plus T/R-switch recovery; a 10 µs coded pulse is blind to 1.5 km | no eclipse; the minimum is set by leakage, the IF high-pass and resolution (cm) | — |
| Maximum range | km to hundreds of km (peak power is easy) | limited by **TX→RX isolation** and leakage phase noise | 100 mW with 60 dB isolation leaves −40 dBm of leakage against a −139 dBm echo: 99 dB that the IF/ADC must hold |
| Range resolution and ADC | ADC rate ≥ B (1 m → 150 MS/s complex) | dechirping ("stretch") makes the ADC need only $f_b$ | 150 MHz swept in 1 ms out to 1.5 km → $f_b$ = 1.5 MHz |
| Antennas | one antenna plus a T/R switch or duplexer | usually separate TX/RX antennas (or a circulator, whose isolation is limited by antenna match) | — |
| Doppler | PRF sets range/Doppler ambiguity ([pulse-Doppler](pulse-doppler-data-cube-and-prf-regimes.md)) | chirp period sets $v_{max}$; range–Doppler coupling (Level 2 above) | — |
| Mutual interference | asynchronous pulses are easy to blank | chirp crossings raise the noise floor (Level 3 above) | — |

**Rule of thumb.** Below about 1–3 km, with cm-to-m resolution and solid-state power below a watt, choose **FMCW**: drones, people, cars, rocket launch phase, altimeters, level sensors. Choose **pulsed** when high peak power is available and the range is long (marine, ATC and weather radars), when one antenna must do both jobs, or for very short impulse/pulsed-coherent sensors (GPR, the Acconeer A121: [DIY hardware](diy-radar-hardware.md)). Under a regulatory **e.i.r.p. cap** (Singapore 24.00–24.25 GHz: 100 mW), a continuous waveform puts the most energy on the target.

### Real vs complex (I/Q) IF
**Level 1.** With an up-chirp the echo always lags the transmit frequency, so with TX·conj(RX) every target beat is a *positive* frequency. The *image band* (negative frequencies) contains only noise and interference [15]. A **real** mixer outputs a cosine and cannot tell $+f$ from $-f$. That costs two things: (1) $R_{max}$ is halved for a given $f_s$ (already in Level 1 above); (2) RF noise from the image side folds onto the signal, costing **up to 3 dB of SNR**. A **quadrature** (I/Q) mixer keeps the halves apart. The effective noise figure becomes the DSB value instead of the SSB value, and the empty image half can be used to monitor interference and the noise floor [15].

**Level 2 — the 3 dB, and why it shrinks in practice.** Write the dechirped input as $x(t) = Ae^{j2\pi f_bt} + n(t)$, with $n$ complex white noise of variance $\sigma^2$. A real IF keeps $\mathrm{Re}\,x$. Its FFT bin holds signal power $A^2N^2/4$ and noise $N\sigma^2/2$, so $\mathrm{SNR_{real}} = A^2N/(2\sigma^2)$. The complex IF gives $A^2N/\sigma^2$: **exactly 2×**. A quadrature mixer splits the RF signal between the I and Q paths, and each path adds its own IF noise. With $r$ = IF-stage noise ÷ RF noise (both referred to a real IF output), the advantage is
$$\frac{\mathrm{SNR_{complex}}}{\mathrm{SNR_{real}}} = \frac{2(1+r)}{1+2r}.$$
Monte Carlo results (256-point FFT, 4000 trials): $r$ = 0 → **3.03 dB** (theory 3.01); 0.25 → 2.20 (2.22); 1 → 1.33 (1.25); 4 → 0.44 (0.46). This matches TI's statement: up to 3 dB in theory, less in practice because of the I/Q split. The full 3 dB appears when a **TX noise skirt** from leakage or a bumper/radome reflection dominates, because that noise is RF-side ($r$ → 0) [15]. A real IF also folds leakage intermodulation products ($2f_1 - f_2$, which land near $-f_2$) back onto genuine ranges as ghosts [15].

**Level 3 — I/Q imbalance and the mirror ghost.** Gain ratio $g$ and phase error φ between I and Q leak a fraction of each target into the image bin at $-f_b$. The image-rejection ratio is
$$\mathrm{IRR} = \frac{1+2g\cos\varphi+g^2}{1-2g\cos\varphi+g^2}$$
(simulated exactly): 0.1 dB / 1° → **39.6 dB**; 0.5 dB / 5° → 25.6 dB; 1 dB / 10° → 19.6 dB. If you fold or display both halves, a strong reflector, or the leakage itself, creates a mirror ghost that many dB down. Calibrate digitally on a corner reflector.

**What a real IF does *not* lose.** In fast-chirp FMCW the positive range-FFT bins are complex, so the Doppler FFT across chirps still recovers the **sign** of velocity: the script gets ±5.07 m/s for ±5 m/s with a real IF. Only a pure CW Doppler radar with one mixer loses direction ([CW Doppler](cw-and-doppler-radar.md); HB100). Data handling is also a wash: real samples at $2f_{b,max}$ versus complex at $f_{b,max}$, and a 2N-point real FFT versus an N-point complex FFT with the same memory [15].

### Bistatic FMCW
Put the transmitter and receiver at different sites, baseline $L_b$, and the radar measures the **range sum** $R_t + R_r$: an ellipse with the two sites as foci [16]. The receiver must dechirp against a copy of the transmitted chirp, and how it gets that copy decides the errors:
- **A frequency offset Δf** between the two synthesisers adds Δf to every beat, a range-sum bias of $c\,\Delta f/S$. At 24 GHz, 1 ppm (24 kHz) gives **28.9 m** with a slow 250 MHz / 1 ms ramp and 0.72 m with 10 MHz/µs. At 77 GHz with a 0.1 ppm disciplined reference and 30 MHz/µs it is 8 cm.
- **A chirp-start timing offset Δt** adds $c\,\Delta t$: **300 m per µs, 3 m per 10 ns**. Independent nodes need ns-class synchronisation.
- **Direct-path referencing** is the robust fix. Measure the beat of the direct TX→RX signal (known baseline) and express targets relative to it. In simulation (110 m range sum, 30 m baseline, 24 kHz offset, 0.37 µs skew) the naive estimate is 249.7 m and the referenced one is **110.02 m**. Track the direct-path phase chirp by chirp to keep Doppler coherent.
- **Range correlation is lost.** Monostatic leakage enjoys the $4\sin^2(\pi f\tau)$ cancellation of LO phase noise (−24 dB at 1 MHz offset for 10 ns). Two free-running sources instead *add* their phase noise (+3 dB for equal sources). Dechirping the echo against the *received* direct path restores correlation for the differential delay only.
- **Geometry** [16]: range resolution $c/(2B\cos(\beta/2))$ for bistatic angle β. At 250 MHz that is 0.60 / 0.69 / 0.85 / 1.20 m for β = 0 / 60 / 90 / 120°. Doppler is $f_D = (2v/\lambda)\cos\delta\cos(\beta/2)$, where δ is the angle between the target velocity and the bistatic bisector. Near the baseline (β → 180°, forward scatter) both range and Doppler resolution collapse.
- **Why bother:** distance gives isolation, so leakage vanishes. Bistatic operation also allows receive-only nodes and multistatic networks, and the same mathematics underlies [passive radar](diy-radar-hardware.md). On a single board, "separate TX and RX antennas" is quasi-monostatic ($\beta \approx 0$) and needs none of this.

## FMCW radio altimeters: error budget

*Added 2026-10-13 (W5-S9, gap G-11-02). Verified by `tools/verify/s9_radar_altimeter.py` (ALL PASS).*

**Intuition.** An altimeter looks straight down at a huge target, the ground. SNR is plentiful and falls only as $1/h^2$ ([DIY hardware, ground return](diy-radar-hardware.md#level-2--the-budgets-that-decide-feasibility)), so the errors are **systematic**: how the beat is measured, motion, attitude, the spread of ranges inside the beam, and the installation. Classic aviation altimeters (4.2–4.4 GHz) use triangular FMCW and a **cycle counter**. Modern sensors (24/60 GHz, TI/Infineon chips) take an FFT.

**Level 1 — the step (fixed, quantisation) error.** A triangular sweep of excursion ΔF at modulation rate $f_m$ has slope $S = 2\Delta F f_m$, so $f_b = 4\Delta F f_m h/c$. A counter that counts whole beat cycles per modulation period reads $N = f_b/f_m = 4\Delta F h/c$, so
$$h = \frac{cN}{4\Delta F}, \qquad \delta h_{step} = \frac{c}{4\Delta F},$$
independent of height and of $f_m$ [17]. That is 0.75 m for ΔF = 100 MHz, 0.50 m for 150 MHz and **0.30 m for the 250 MHz Singapore 24 GHz band**. A simulated zero-crossing counter (10–12 m, 250 MHz) reads a staircase of exactly 0.300 m steps with a maximum error of 0.143 m (half a step). The error is fixed in metres, so it matters most at touchdown. Remedies: dither ΔF or $f_m$ so that successive counts straddle the steps and average out; measure the fractional cycle (phase); or use an FFT with peak interpolation. **Turn-around error:** near each sweep reversal the transmit and echo frequencies cross and the beat passes through zero for about $2h/c$. Practical counters gate out the turn-arounds and gate over an integer number of cycles [18].

**Level 2 — the other terms (24.125 GHz, 250 MHz ramps of 1 ms).**

| Error | Formula | Size | Fix |
|---|---|---|---|
| Doppler bias of one ramp | $\delta h = f_Dc/(2S)$, sign flips up/down | **0.58 m** at 6 m/s (main chute), **2.41 m** at 25 m/s (drogue), 5.79 m at 60 m/s | average up + down ramps (cancels exactly; the difference gives $v$); fast chirps (30 MHz/µs): 2 cm |
| FFT/estimation noise | bin $c/2B$ = 0.60 m; $\sigma_h = (c/2B)\sqrt{6/\mathrm{SNR}}/(2\pi)$ (CRB, post-FFT SNR) | 7.4 / 2.3 / 0.7 cm at 10 / 20 / 30 dB; interpolated estimator 1.03 × CRB (Monte Carlo) | — (SNR is high) |
| Narrow beam tilted θ | reads $h/\cos\theta$ | at 50 m: +0.19 / +0.77 / +1.76 / +3.21 m for 5 / 10 / 15 / 20° (parachute swing) | wide beam + leading edge, or IMU tilt correction |
| Wide beam, spectrum centroid | echoes spread from $h$ to $h/\cos(\theta_b/2)$ | centroid +1.7 / +5.9 / +9.1 % for 30 / 60 / 80° beams (flat-ground model) | track the **leading edge** (first bin above threshold), as aviation altimeters do |
| Installation delay | $(L_{tx}+L_{rx})/(2v_f)$ | 0.43 m for 0.3 + 0.3 m of coax at $v_f$ = 0.70; 1.52 m for 1 + 1 m at 0.66 | calibrate zero on the ground (aviation: "installation delay" set to read 0 at touchdown) |
| Leakage / IF high-pass | the leakage beat near 0 Hz and the HPF set a minimum height | about one bin (≈ 0.6 m) plus the HPF corner | short leakage paths; separate antennas |
| Double bounce | ground → vehicle → ground gives a line at $2h$ | weaker by the vehicle's reflection and extra spreading | leading-edge logic ignores it |
| Terrain | grass, crops and trees return from their tops; water is specular and strong | site-dependent | know what "ground" means for your use |

Aviation altimeters share 4.2–4.4 GHz with nothing else, but their receivers proved vulnerable to strong out-of-band C-band (3.7–3.98 GHz) 5G signals. That is a reminder to filter an altimeter front end hard [19].

**Worked example — 24 GHz recovery/landing altimeter.** Budget: 100 mW e.i.r.p. (TS SRD limit), 15 dBi receive, NF 12 dB, 30° beam, ground $\sigma^0$ = −10 dB (assumed). $P_r$ = −72.6 dBm at 10 m, −92.6 at 100 m and −102.1 at 300 m, so E/N0 per 1 ms ramp is 59 / 39 / 30 dB: SNR is not the issue below a few hundred metres. Error budget under a drogue (25 m/s, ±15° swing, 50 m): a single-ramp Doppler bias of 2.41 m (cancelled by up/down pairing), tilt +1.76 m with a narrow beam (removed by a wide beam plus leading edge), cable offset 0.43 m (calibrated out), and estimation of a few cm. The residual is set by the leading-edge threshold and terrain, about 0.1–0.3 m. The same chirp counted the old way would add a ±0.15 m step. Pre-register the expected error terms before a drop test, and compare against a surveyed tape or pole-mounted reflector heights ([validation test campaign](../20-projects-recipes/validation-test-campaign.md)).

## Radar timing and display vocabulary

*Added 2026-10-13 (W5-S9; vocabulary gap flagged by the W6-F1 glossary pass).*

| Term | Meaning | On an FMCW board |
|---|---|---|
| **Fast time** | time within one pulse repetition interval (or one chirp); its samples map to **range** | the `sample` axis of `cube[rx, chirp, sample]` → range FFT |
| **Slow time** | pulse-to-pulse (chirp-to-chirp) time; phase changes along it give **Doppler** | the `chirp` axis → Doppler FFT |
| PRI / PRF | pulse repetition interval / frequency | chirp period $T_c$ (including idle) |
| CPI, dwell | coherent processing interval: the block of pulses processed together; dwell = time on target | one frame of N chirps ($NT_c$) |
| Range gate / bin / cell | a time slot in fast time (pulsed) or an FFT bin (FMCW) | bin width $c/2B$ |
| **Video** | the detected or baseband receiver output that historically drove the display (it has "video" bandwidth). *Raw video* = unprocessed detector output; *synthetic video* = symbols drawn from detections and tracks; *bipolar video* = coherent I or Q | the IF/beat signal ("video amplifier" in the coffee-can radar) |
| **A-scope** | amplitude versus range along one line, like an oscilloscope trace | a plot of \|range FFT\| |
| **B-scope** | rectangular range (vertical) versus azimuth (horizontal) | the range–azimuth heat map before polar conversion |
| **PPI** | plan position indicator: a polar map with range outward and azimuth around the centre, the classic rotating sweep | the same heat map scan-converted to x–y, or a point cloud viewed from above |
| RHI | range–height indicator: range versus elevation for an elevation scan | an elevation-angle FFT display |
| Range–Doppler map | range versus radial velocity (not a classic scope name) | output of the 2-D FFT before CFAR |

## Common mistakes & misconceptions
- **"More chirp duration gives better range resolution."** Only more *bandwidth* does. Duration at fixed slope adds bandwidth; duration at fixed bandwidth changes only the beat frequencies.
- **Confusing sweep bandwidth with IF bandwidth.** Sweep bandwidth (GHz) sets resolution; IF bandwidth (MHz) sets maximum range for a given slope.
- **Forgetting idle time in $T_c$** when computing $v_{max}$, and forgetting the ÷$N_{TX}$ of TDM-MIMO.
- **Assuming real sampling gives the same range as complex** — it halves $R_{max}$.
- **Reading TI's "max velocity" Eq. 5 in SWRA553 as a maximum** — it is the resolution formula.
- **Expecting to separate a weak target just beyond the radome/bumper.** Leakage phase noise and window sidelobes of the leakage peak mask the first metre or so.
- **Getting the sign of velocity wrong.** With TX·conj(RX), approaching → negative Doppler bin. Check with a walking test.
- **Ignoring VCO nonlinearity** in discrete designs — targets at long range smear and the SNR drops.
- **"Pulsed radars see further because they have more power."** Detection follows energy (average power × dwell); at the same peak power a 1 %-duty pulsed radar is 20 dB *worse*. Pulsed wins when kW-class peak power is cheap and isolation would cripple FMCW.
- **"A complex IF doubles the data and the DSP load."** Real samples at $2f_{b,max}$ and complex samples at $f_{b,max}$ are the same rate, and the memory is the same [15]; the I/Q receiver gains up to 3 dB of SNR.
- **"A real IF loses the direction of motion."** Only in pure CW Doppler; in fast-chirp FMCW the Doppler FFT of the complex range bins keeps the sign.
- **Running two FMCW boards as a bistatic pair without a shared or direct-path reference** — 1 ppm and a µs of start skew put the target hundreds of metres off.
- **Reading an altimeter's spectrum centroid instead of its leading edge** — biased high by several per cent with a wide beam; and forgetting the cable (installation) delay and the single-ramp Doppler bias during a fast descent.
- **"FMCW can't see stationary targets."** It can (range FFT); only the Doppler/MTI step removes them. CW Doppler radars cannot.
- **Windowing to hide sidelobes and then being surprised that two close targets merge** (Hann needs ~1.7 bins).
- **Writing the chirp as $\cos[2\pi(f_c + St)\,t]$.** Phase is the *integral* of instantaneous frequency: if $f_i(t) = f_c + St$, then $\varphi(t) = 2\pi\int_0^t f_i\,dt' = 2\pi(f_ct + \tfrac12St^2)$ (as in Level 2 above). Plugging $f_i(t)$ in as if it were constant gives $\varphi = 2\pi(f_ct + St^2)$, whose instantaneous frequency $\tfrac{1}{2\pi}\,d\varphi/dt = f_c + 2St$ sweeps **twice** the intended bandwidth — the classic "my chirp covers 2B" bug (also doubles the beat frequency and halves the computed range). Numerical check: generate both versions, take the spectrogram (or `np.diff(np.unwrap(np.angle(x)))·f_s/2π`) and the wrong one ends at $f_c + 2B$. The same rule applies to any FM/sweep synthesis: accumulate phase (an NCO, [14 NCO/DDC](../14-sdr-dsp/nco-ddc-duc.md)), never multiply a time-varying frequency by $t$. (Myth flagged by W4-D1, dsp.stackexchange.com/q/93704.)

## How to simulate / verify
- `tools/verify/radar_fmcw.py` (~2 s, **ALL PASS**): exact dechirp phase and beat frequency; TI Table 1 re-derivation; a full range–Doppler–angle simulation with 2-D CFAR; two-target resolution for rect/Hamming/Hann; IF-limited range; range migration and coupling; phase-noise synthesis and range-correlation skirt; ZX95-2536C+ nonlinearity and predistortion; chirp design.
- `tools/verify/s9_fmcw_if_bistatic.py` (< 1 s, **ALL PASS**): real vs complex IF Monte Carlo, IRR formula, velocity sign with a real IF, pulsed-vs-FMCW energy example, bistatic bias/referencing/resolution. `tools/verify/s9_radar_altimeter.py` (< 2 s, **ALL PASS**): cycle-counter staircase, Doppler bias, CRB, tilt/leading-edge, installation delay, 24 GHz ground-return budget.
- Extend the simulation: add TDM-MIMO (see `tools/verify/radar_mimo.py`), static clutter, and an interfering radar; feed real DCA1000 captures into the same processing chain.
- Measure your hardware: a corner reflector on a rail at known ranges checks the beat-frequency slope (calibrates S) and the phase-vs-range slope (calibrates λ); a reflector swinging on a pendulum checks Doppler sign and scale.

## Open questions / gaps
- ADI Phaser FMCW ramp parameters (bandwidth, ramp time) from ADI's example code were not checked.
- Interference mitigation (zeroing/interpolation, CAMP) is described, not simulated.
- TI's log-domain CFAR and angle-estimation (e.g. zoom-FFT, Capon) implementations are not detailed; MUSIC/Capon belong to 12-phased-arrays.
- Radome design is only a rule of thumb here; see 02-electromagnetics for the Fresnel treatment.
- Measured phase-noise profiles (not just the 1 MHz point) for TI/Infineon parts were not collected.
- Altimeter: the step-error formula is cited from Skolnik from memory (wording not re-checked; the old "3rd ed. §3.3" pointer was wrong, see ref. 17); the σ⁰ = −10 dB ground value and flat-ground centroid model are assumptions; no hobby drop-test data exist yet (a pre-registered drop test is the obvious next experiment).
- Bistatic FMCW: synchronisation accuracy of GNSS-disciplined hobby nodes was not researched (only the ns-class requirement is derived).

## Sources
1. V. Dham, "Programming Chirp Parameters in TI Radar Devices," TI SWRA553A, May 2017 rev. Feb 2020 — Eq. 1–8, Tables 1–4. https://www.ti.com/lit/pdf/swra553 (app note)
2. S. Rao, "Introduction to mmwave Sensing: FMCW Radars," TI training slides — IF signal, $f_b = S2d/c$, phase, $d_{res} = c/2B$, $d_{max} = F_sc/2S$, $v_{max} = \lambda/4T_c$, $v_{res} = \lambda/2T_f$, angle FoV and $2/N$ resolution, sign of ω vs direction, chirp design procedure. https://www.ti.com/content/dam/videos/external-videos/ko-kr/2/3816841626001/5415203482001.mp4/subassets/mmwaveSensing-FMCW-offlineviewing_0.pdf (app note/training)
3. A. Dürr, B. Schweizer, C. Waldschmidt, "Leakage phase noise mitigation for monostatic FMCW radar sensors using carrier transmission," IEEE IMS 2019 — range correlation $2\mathcal L(1-\cos2\pi f\tau)$ (after Budge & Burt 1993), ~30 dB isolation, radome leakage. (peer-reviewed)
4. M. A. Richards, *Fundamentals of Radar Signal Processing*, 2nd ed., 2014 — stretch processing / RVP, range migration; M. I. Skolnik, *Introduction to Radar Systems* (FM-CW radar; see ref. 17 for the edition/section caveat). (textbook)
5. S. Rao, "MIMO Radar," TI SWRA554A, 2017/2018 — angle FFT, $\theta_{res} = 2/N$, TDM/BPM MIMO. https://www.ti.com/lit/an/swra554a/swra554a.pdf (app note)
6. Texas Instruments product pages IWR6843, AWR1843, AWR2944 (accessed 2026-09-27) — frequency range, TX/RX count, TX power, NF, phase noise, ADC rate, processors. (datasheet)
7. S. Ayhan, S. Scherr, A. Bhutani, B. Fischbach, M. Pauli, T. Zwick, "Impact of frequency ramp nonlinearity, phase noise, and SNR on FMCW radar accuracy," *IEEE Trans. MTT*, vol. 64, no. 10, pp. 3290–3301, 2016. (peer-reviewed; metadata/abstract)
8. Mini-Circuits, ZX95-2536C+ VCO data sheet rev. A — 2315–2536 MHz, 0.5–5 V tuning, sensitivity table (81.9 → 36.3 MHz/V), phase noise −105 dBc/Hz @ 10 kHz. https://www.minicircuits.com/pdfs/ZX95-2536C+.pdf (datasheet)
9. G. L. Charvat, A. J. Fenn, B. T. Perry, MIT IAP 2011 "Build a small radar system…" (MIT OCW RES.LL-003) and student build reports (coffee-can parts list: XR-2206 ramp, ZX95-2536C+, ZX60-272LN-S+, ZX05-43MH-S+, audio ADC). (lecture notes / project report)
10. Infineon, BGT60TR13C data sheet (v2.4x) — 58.0–63.5 GHz, 1 TX / 3 RX AiP, > 5 GHz BW, 12-bit ADCs up to 4 MSps, 6.5 × 5 × 0.9 mm. https://www.infineon.com/part/BGT60TR13C (datasheet; via distributor copies)
11. M. Lichtman, *PySDR*, ch. "Hands-on with Phaser" — CN0566 architecture (2 × ADAR1000, ADF4159 + HMC735, LTC5548, Pluto IF ≈ 2.2 GHz, 14 mm spacing); ADI CN0566 circuit note. https://pysdr.org/content/phaser (online textbook / circuit note)
12. IMDA, "Technical Specification — Short Range Devices," IMDA TS SRD Issue 1 Rev 3, September 2023, Table 1 (77–81 GHz is instead in IMDA TS UWB Issue 1, Oct 2016, Table 1). (regulation)
13. H. Forstén, "6 GHz frequency modulated radar" and fmcw3 design files — https://hforsten.com/6-ghz-frequency-modulated-radar.html, https://github.com/Ttl/fmcw3 (project report)
14. `tools/verify/radar_fmcw.py` — all simulated/computed values. (verification script)
15. K. Ramasubramanian, "Using a complex-baseband architecture in FMCW radar systems," TI white paper SPYY007, May 2017 — image band holds only noise, up-to-3 dB NF (SSB→DSB) advantage, reduced by I/Q split, full benefit when a TX noise skirt dominates; image-band interference monitoring; 2f1−f2 fold-back; data-rate/FFT/memory comparison (Table 1). https://www.ti.com/lit/pdf/spyy007 (white paper; read in full)
16. N. J. Willis, *Bistatic Radar*, 2nd ed., SciTech, 2005 — range-sum ellipses, bistatic range resolution $c/(2B\cos(\beta/2))$, bistatic Doppler. (textbook; cited from standard formulas, not re-read)
17. M. I. Skolnik, *Introduction to Radar Systems* — FM-CW altimeter: cycle counting, $h = cN/4\Delta f$, step/fixed error $c/4\Delta f$. (textbook; cited from memory, derivation re-done here.) **Section number corrected by W5-S18 (2026-10-13):** in the 3rd ed. (2001), ch. 3 is "MTI and Pulse Doppler Radar" and §3.3 is "Staggered Pulse Repetition Frequencies" (catalogue ToC via search, gbv.de hebis-darmstadt 195384067). "§3.3 FM-CW radar" is the 2nd-edition (1980) numbering, as recalled. The 3rd-ed. location of the altimeter material was not found, because the full ToC returned HTTP 429.
18. Bendix Corp., US Patent 4,435,708, "Means for eliminating step error in FM/CW radio altimeters" (1984) — turn-around beat collapse, gating over integer beat cycles. (patent)
19. RTCA, "Assessment of C-Band Mobile Telecommunications Interference Impact on Low Range Radar Altimeter Operations," RTCA Paper 274-20/PMC-2073, Oct 2020. (industry report; cited from memory)
20. `tools/verify/s9_fmcw_if_bistatic.py`, `tools/verify/s9_radar_altimeter.py` — numbers in the W5-S9 sections. (verification scripts)
