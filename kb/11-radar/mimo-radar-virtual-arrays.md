---
title: MIMO radar and virtual arrays — virtual-array construction, TDM/BPM/DDM multiplexing, angle resolution, TI cascade radars, calibration
domain: 11-radar
slug: mimo-radar-virtual-arrays
tags: [mimo-radar, virtual-array, tdm-mimo, bpm-mimo, ddm-mimo, doppler-division, hadamard, angle-fft, angle-resolution, elevation, cascade, awr2243, awr1843, calibration, doppler-compensation, sparse-array]
prerequisites:
  - fmcw-radar.md
  - ../12-phased-arrays/array-factor-linear-arrays.md
related:
  - ../12-phased-arrays/beam-steering-grating-lobes.md
  - ../12-phased-arrays/array-calibration.md
  - ../12-phased-arrays/adaptive-beamforming-doa.md
  - ../12-phased-arrays/diy-phased-array-projects.md
  - detection-theory-cfar.md
  - diy-radar-hardware.md
  - sar-and-imaging.md
level: intermediate
confidence: high
last_updated: 2026-09-27
---

# MIMO radar and virtual arrays

## Questions this page answers
- What is a MIMO radar "virtual array", and why does 3 TX × 4 RX behave like 12 receivers?
- How are the virtual element positions computed, and how do I get elevation as well as azimuth?
- What angle resolution does an N-element virtual array give?
- What are TDM, BPM and DDM MIMO, and what does each cost (velocity range, SNR, complexity)?
- Why is my angle estimate wrong for fast targets in TDM-MIMO, and how do I fix it?
- How do TI's 4-chip cascade radars reach ~1.4° azimuth resolution?
- Why do I need to calibrate the channels, and how?
- Where does MIMO radar stop and phased-array beamforming begin?

## TL;DR
- **Virtual array:** with TX antennas at positions $\mathbf p_m$ and RX at $\mathbf q_n$, the two-way phase for an angle depends only on $\mathbf p_m + \mathbf q_n$ — the system behaves like a single TX with receivers at all $N_{TX}N_{RX}$ **sum positions** (a spatial convolution of the two arrays) [1]. TX spaced $N_{RX}d$ apart makes the virtual array contiguous.
- **AWR1843/1443-style layout** (TX1 and TX3 2λ apart, TX2 raised λ/2, 4 RX at λ/2): **8 contiguous azimuth + 4 elevated** virtual elements (verified) — azimuth *and* elevation from one chip.
- **Resolution** of an N-element λ/2 virtual ULA at boresight: Rayleigh (first null) **2/N rad**; −3 dB beamwidth ≈ **0.886 × 2/N**. 4 → 28.6°, 8 → 14.3°, 12 → 9.5°, TI 4-chip cascade (86 uniform virtual azimuth elements of 192) → **1.33°** (TI quotes ~1.4°) [2].
- **TDM-MIMO** (one TX per chirp): simple, but **$v_{max}$ divided by $N_{TX}$**, and a moving target's phase advances between TX slots — uncompensated, a target at 15° moving at 8 m/s (40 µs chirps, 77 GHz) is estimated at **18.7°**; compensating with the measured Doppler restores **15.0°** [1].
- **BPM-MIMO** (all TX on, ±1 Hadamard coding across chirps): **+10 log₁₀ N_TX dB** SNR over TDM (verified 2.97 dB for 2 TX); decode after the Doppler FFT with Doppler correction [1].
- **DDM-MIMO** (each TX gets its own slow-time phase ramp): all TX transmit every chirp (full power); TX signals separate as Doppler-shifted copies — velocity range shrinks to $\pm\lambda/(4T_cN_{sub})$ and an empty sub-band resolves which copy is which (verified).
- **Calibration matters:** 1 dB / 10° rms channel errors raised a Hamming-weighted 12-element array's sidelobes from −37 dB to **−17 dB**; a boresight corner-reflector calibration restored −37 dB.

## Intuition (no math)
A receive array estimates direction from the tiny differences in arrival phase across its antennas: more antennas spread over a wider aperture give sharper angle discrimination. Each receiver costs a full chain (LNA, mixer, filter, ADC). The MIMO trick is to move some of that aperture to the transmit side. If a second transmitter sits a few wavelengths away, the echo of its signal reaches every receiver with an extra phase offset — exactly as if the receivers themselves were displaced by that amount. So transmitting first from TX1 and then from TX2 (or simultaneously with a code that lets the receivers tell them apart) produces two copies of the receive array, side by side. Three transmitters and four receivers make a 12-element "virtual" array with only 4 receive chains.

The catch is that the receivers must know which transmitter each echo came from. Transmitting in turns (TDM) is simplest, but the target moves between turns, which adds a phase error that looks like an angle shift. Transmitting all at once with codes (BPM, DDM) uses the full power but needs decoding.

## The math

### Level 1 — virtual positions and resolution
A far-field target in direction $\hat{\mathbf u}$ contributes phase $-\frac{2\pi}{\lambda}\hat{\mathbf u}\cdot(\mathbf p_m + \mathbf q_n)$ (plus range and Doppler terms common to all channels) to the TX$_m$ → RX$_n$ channel. So channel $(m,n)$ is equivalent to a single receiver at
$$\mathbf v_{mn} = \mathbf p_m + \mathbf q_n .$$
For a uniform linear virtual array of $N = N_{TX}N_{RX}$ elements with spacing $d$:
- phase step $\omega = 2\pi d\sin\theta/\lambda$, estimated by an FFT across the virtual elements (angle FFT);
- field of view $\pm\sin^{-1}(\lambda/2d)$ (±90° for $d = \lambda/2$);
- Rayleigh resolution $\theta_{res} = \lambda/(Nd\cos\theta)$ = $2/N$ rad at boresight for $d = \lambda/2$ [1], [3].

### Level 2 — derivations and multiplexing schemes

**Contiguous virtual arrays.** RX at $0, d, \ldots, (N_{RX}-1)d$; TX at $0, N_{RX}d, 2N_{RX}d, \ldots$ ⇒ virtual positions $0\ldots(N_{TX}N_{RX}-1)d$ with no gaps or overlaps [1]. Other layouts synthesise the same virtual array (TI SWRA554 Fig. 7); overlapping virtual elements are redundant (useful for calibration and TDM motion estimation), gaps create grating lobes or require sparse-array processing. For elevation, offset one TX vertically: in the AWR1843-like layout (units of λ/2: RX at 0–3, TX1 at 0, TX3 at 4, TX2 at x = 2 raised by 1) the virtual array is 8 azimuth elements at 0–7 plus 4 elevated ones at 2–5 (computed).

**Beamwidth vs 2/N.** The array factor of a uniform N-element λ/2 array is $|\sin(N\pi u/2)/(N\sin(\pi u/2))|$ with $u = \sin\theta$; its first null is at $u = 2/N$ (the "2/N resolution") and its −3 dB full width is ≈ 0.886 × 2/N rad for large N (computed ratios 0.917, 0.892, 0.888, 0.885 for N = 4, 8, 12, 86). The array-factor theory, tapering and grating lobes are on the [phased-array pages](../12-phased-arrays/array-factor-linear-arrays.md). Windowing across elements (Hamming/Taylor) lowers angle sidelobes at the cost of beamwidth, exactly as in range/Doppler.

**TDM-MIMO [1].** Chirp $k$ uses TX $k \bmod N_{TX}$. Each TX–RX pair gets its own range–Doppler map (Doppler sampled at $N_{TX}T_c$), so $v_{max} = \lambda/(4N_{TX}T_c)$ (24.3 → 12.2 → 8.1 m/s for 1/2/3 TX at 40 µs, 77 GHz). A target of radial velocity $v$ adds phase $4\pi vT_c/\lambda$ per chirp slot, so the virtual elements from TX$_m$ carry an extra $m\cdot4\pi vT_c/\lambda$ — a phase step between the sub-arrays that the angle FFT misreads as angle. Correction: after the Doppler FFT, multiply the TX$_m$ channels by $e^{-jm\hat\phi}$ with $\hat\phi = 2\pi\hat f_dT_c$ from the detected Doppler bin. The script: 2 TX × 4 RX, 15°, 8 m/s receding, 40 µs → 59° slot phase, uncompensated 18.74°, compensated 15.00°. Aliased Doppler (|v| > $v_{max}$) makes $\hat f_d$ wrong by a multiple of $1/(N_{TX}T_c)$ and the compensation wrong by $2\pi m/N_{TX}$ — a coarse angle error that can be used to *resolve* the Doppler ambiguity (test the $N_{TX}$ hypotheses and pick the one whose overlapping virtual elements agree).

**BPM-MIMO [1].** In each block of $N_{TX}$ chirps all TX transmit, with signs from a Hadamard matrix: slot a sends $S_1 + S_2$, slot b sends $S_1 - S_2$; decoding $S_1 = (S_a + S_b)/2$, $S_2 = (S_a - S_b)/2$ recovers the channels. Each decoded channel averages $N_{TX}$ transmissions, so its noise variance is $1/N_{TX}$ of TDM's at the same per-TX power — an SNR gain of $10\log_{10}N_{TX}$ (script: 2.97 dB for 2 TX). Motion between the slots breaks the orthogonality, so decode after the Doppler FFT and apply the same slot-phase correction as TDM first. $v_{max}$ is still reduced by $N_{TX}$ (a block spans $N_{TX}$ chirps).

**DDM-MIMO (Doppler-division).** Every TX transmits every chirp, TX$_m$ with an extra phase $2\pi m\,k/N_{sub}$ on chirp $k$. In the Doppler FFT, TX$_m$'s contribution appears shifted by $mN/N_{sub}$ bins. With $N_{sub} > N_{TX}$ (e.g. 3 TX in 4 sub-bands, one left empty — "empty-band DDM"), the pattern of occupied/empty sub-bands tells which copy belongs to which TX; picking the $N_{TX}$ copies and concatenating them gives the virtual snapshot (script: angle −12.01°, true −12°; velocity 5.07 m/s, true 5.0). Unambiguous velocity becomes $\pm\lambda/(4T_cN_{sub})$ but all TX power is used on every chirp. Needs per-chirp TX phase shifters (present on newer TI parts such as the AWR2944 family, used for DDMA — device capability stated from TI marketing, not verified here).

### Level 3 — cascades, sparse arrays, calibration, limits

**Cascaded chips.** TI's imaging-radar reference design (TIDEP-01012) cascades four AWR2243s driven from a common, distributed LO (one chip acts as master): 12 TX × 16 RX = 192 virtual channels, of which **86 uniformly spaced azimuth elements** are used, giving ~1.4° azimuth resolution in TDM-MIMO, plus beamforming modes that tracked targets beyond 350 m [2]. The LO distribution and chip-to-chip synchronisation (frame triggers, sample clocks) are the hard parts.

**Sparse / non-uniform virtual arrays.** Minimum-redundancy or nested placements give a larger aperture (finer resolution) with fewer elements, at the price of higher sidelobes or the need for super-resolution/compressive estimators (MUSIC, ESPRIT, IAA — see [12 adaptive beamforming & DOA](../12-phased-arrays/adaptive-beamforming-doa.md)).

**Calibration.** Each TX–RX chain has its own gain and phase (PCB trace lengths, chip-to-chip LO skew, antenna tolerances), plus mutual coupling between elements. Uncalibrated errors act like random amplitude/phase tapering: with 1 dB / 10° rms errors on a Hamming-weighted 12-element array the peak sidelobe rose from −37.4 dB to −17.2 dB (one random draw; the script). Standard procedure: place a corner reflector at boresight in the far field, measure the complex response of every virtual channel at its range–Doppler cell, and store the inverse as a calibration vector (restores −37.4 dB in simulation). TI's SDK uses the same idea ("range bias and RX channel phase compensation" measured on a reflector). Repeat over temperature for precision work; see [12 array calibration](../12-phased-arrays/array-calibration.md).

**Limits of the virtual-array picture.**
- It assumes the target is in the far field of the *whole* virtual aperture ($R > 2D_{virt}^2/\lambda$) and point-like; extended targets decorrelate across the aperture.
- MIMO gives the *receive-side* resolution of the virtual array but not the two-way *gain* of a same-size phased array: each TX still illuminates the full field of view. For long range, cascaded systems switch to transmit beamforming (all TX coherently phased) [2].
- Doppler, range migration and multipath (ground bounce) all bias angle estimates.

## Design equations & rules of thumb

| Rule | Formula | Example |
|---|---|---|
| Virtual positions | $\mathbf v_{mn} = \mathbf p_m + \mathbf q_n$ | 3 TX × 4 RX → 12 |
| Contiguous layout | TX pitch = $N_{RX}d$ | 4 RX at λ/2 → TX 2λ apart |
| Resolution (first null) | $2/N$ rad at boresight, $d = \lambda/2$ | N = 12 → 9.5° |
| −3 dB beamwidth | ≈ 0.886 × 2/N | N = 12 → 8.5° |
| Off-boresight | ÷ cos θ | 60° → 2× worse |
| TDM $v_{max}$ | $\lambda/(4N_{TX}T_c)$ | 3 TX, 40 µs, 77 GHz → 8.1 m/s |
| TDM slot phase | $4\pi vT_c/\lambda$ per slot | 8 m/s, 40 µs → 59° |
| BPM SNR gain vs TDM | $10\log_{10}N_{TX}$ | 3 TX → 4.8 dB |
| DDM $v_{max}$ | $\lambda/(4T_cN_{sub})$ | 4 sub-bands, 30 µs → 8.1 m/s |
| Calibration target | corner reflector at boresight, far field | [RCS page](radar-cross-section.md) |

## Worked examples

**Example 1 — Angle resolution budget for separating two drones at 50 m.** Required cross-range separation 2 m → angle 2/50 rad = 2.3°. A 12-virtual-element single-chip radar gives 9.5° (Rayleigh) — it cannot separate them in angle; they must be separated in range (ΔR = c/2B) or Doppler instead. An 86-element cascade (1.33°) can. This is why single-chip radars rely on range/Doppler first and angle last.

**Example 2 — TDM-MIMO on a fast target.** A 77 GHz radar with 3 TX and 40 µs chirps has $v_{max}$ = 8.1 m/s. A car at 20 m/s aliases (its measured Doppler is wrong by one or two ambiguity intervals), so the TDM phase compensation is wrong by $2\pi/3$ steps and the angle estimate jumps. Options: shorten $T_c$ (≤ 16 µs for 20 m/s with 3 TX), use the overlapping virtual elements to test the three Doppler-unfolding hypotheses, or switch to DDM/BPM.

**Example 3 — Choosing BPM over TDM.** For a range-limited application with 3 TX, BPM gives 4.8 dB more SNR → $10^{4.8/40}$ = 1.32× range for the same frame time, at the cost of decoding and sensitivity to motion within a block.

## Practical notes
- In TI's CLI, TDM-MIMO is configured by defining one `chirpCfg` per TX (each enabling a single TX bit mask) and looping them in `frameCfg`; BPM uses the `bpmCfg` command and requires chirps with phase inversion [1].
- Verify your virtual-array ordering empirically: put a corner reflector at a known angle and check the phase progression across the concatenated channels before trusting the angle FFT.
- Elevation from the one raised TX gives only 4 elevated elements — coarse elevation (~30°) but enough to reject ground and overhead clutter.
- The ADI Phaser is a phased array (analog beamformer + 2 digital channels), not a MIMO radar; the two approaches can be combined (hybrid beamforming) — see [12 DIY phased arrays](../12-phased-arrays/diy-phased-array-projects.md).

## Common mistakes & misconceptions
- **"MIMO gives the gain of a big array."** It gives the angular resolution of the virtual aperture; transmit gain is still that of one TX element (unless you beamform on transmit).
- **Forgetting TDM Doppler compensation** — angle errors of several degrees for fast targets (3.7° in the example).
- **Ignoring the $v_{max}$ reduction** of TDM (÷$N_{TX}$).
- **Assuming the virtual array is uniform** when TX spacing ≠ $N_{RX}d$ — overlaps or gaps give redundancy or grating lobes.
- **Skipping calibration** — sidelobes rise by ~20 dB with modest channel errors.
- **Quoting 2/N as the −3 dB beamwidth** — it is the null-to-peak (Rayleigh) spacing; −3 dB is ~11 % narrower.

## How to simulate / verify
- `tools/verify/radar_mimo.py` (~2 s, **ALL PASS**): virtual-array construction, beamwidth vs 2/N, TDM phase error and compensation, BPM SNR gain, DDM separation with an empty sub-band, calibration effect on sidelobes.
- Combine with `tools/verify/radar_fmcw.py` for full range–Doppler–angle cubes; MATLAB's phased toolbox example "Increasing angular resolution with virtual arrays" is an independent cross-check.

## Open questions / gaps
- DDMA support and implementation details on AWR2944-class devices not verified from TI documents.
- Mutual coupling compensation (beyond per-channel gain/phase) not simulated.
- Doppler-ambiguity resolution using overlapping virtual elements described, not implemented.
- Super-resolution angle estimation (MUSIC/ESPRIT) deferred to 12-phased-arrays.

## Sources
1. S. Rao, "MIMO Radar," TI application report SWRA554A, May 2017 rev. July 2018 — virtual positions $p_m + q_n$, 2/N resolution, TDM processing with Doppler correction, BPM with $S_1 = (S_a+S_b)/2$ and $10\log N_{TX}$ SNR benefit, Hadamard for 4 TX. https://www.ti.com/lit/an/swra554a/swra554a.pdf (app note)
2. Texas Instruments, TIDEP-01012 / TIDUEN5A "Imaging radar using cascaded mmWave sensor reference design" (June 2019, rev. March 2020) — 4 × AWR2243, 12 TX × 16 RX, 192 virtual, 86 uniform azimuth elements, ~1.4° azimuth resolution, > 350 m tracking. https://www.ti.com/tool/TIDEP-01012 (reference design; via summary)
3. V. Dham, "Programming Chirp Parameters in TI Radar Devices," TI SWRA553A — angle FoV and resolution formulas, MIMO 3 TX × 4 RX = 12 virtual. https://www.ti.com/lit/pdf/swra553 (app note)
4. J. Li, P. Stoica (eds.), *MIMO Radar Signal Processing*, Wiley, 2009 — virtual-aperture theory, waveform orthogonality. (textbook)
5. F. C. Robey, S. Coutts, D. Weikle, J. C. McHarg, K. Cuomo, "MIMO radar theory and experimental results," *Proc. 38th Asilomar Conf.*, 2004. (peer-reviewed)
6. H. Sun, F. Brigui, M. Lesturgie, "Analysis and comparison of MIMO radar waveforms," *Proc. Int. Radar Conf.*, 2014 — TDM/BPM/DDM comparison. (peer-reviewed)
7. `tools/verify/radar_mimo.py` — all computed values. (verification script)
