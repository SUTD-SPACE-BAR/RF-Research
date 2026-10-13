---
title: The radar range equation — monostatic, bistatic, pulsed, FMCW, search and track forms, losses and worked examples
domain: 11-radar
slug: radar-range-equation
tags: [radar-equation, snr, monostatic, bistatic, rcs, noise-temperature, integration-gain, losses, search-radar, power-aperture, fmcw, pulsed, 24ghz, 77ghz, s-band, passive-radar, rocket-tracking]
prerequisites:
  - ../00-math-foundations/decibels-and-log-units.md
  - ../08-antennas/antenna-fundamentals.md
  - ../09-propagation-link-budget/friis-free-space-path-loss.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
  - ../07-noise-linearity/noise-figure-and-friis.md
related:
  - radar-cross-section.md
  - detection-theory-cfar.md
  - pulsed-radar-and-pulse-compression.md
  - fmcw-radar.md
  - cw-and-doppler-radar.md
  - diy-radar-hardware.md
  - clutter-and-mti.md
  - ../09-propagation-link-budget/atmospheric-rain-attenuation.md
  - ../09-propagation-link-budget/two-ray-ground-reflection.md
  - ../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md
  - ../07-noise-linearity/sensitivity-and-mds.md
level: mixed
confidence: high
last_updated: 2026-10-03
---

# The radar range equation

## Questions this page answers
- How far can my radar see a given target, and how do I derive the radar equation from scratch?
- Why does radar range grow only as the fourth root of transmit power?
- How does the radar equation differ from the Friis equation for a communication link?
- What is the "energy" form of the radar equation, and why do pulsed and FMCW radars obey the same law?
- How do I write the radar equation for a TI mmWave FMCW chip (the SWRA553 form)?
- What losses should I budget (window, straddle, beam shape, CFAR, atmosphere, rain), and how big are they?
- What is the search-radar (power–aperture) equation, and when do I use it instead of the track form?
- How does the bistatic / passive-radar equation work?
- How far can a 24 GHz HB100/CDM324-type module see a person, and why does an FFT extend it?
- Can a DIY S-band radar track a small rocket to apogee?
- Why does a 60 GHz radar lose range outdoors, and how much does tropical rain hurt 77 GHz?

## TL;DR
- **Monostatic radar equation** (derived below): $P_r = \dfrac{P_t G_t G_r \lambda^2 \sigma}{(4\pi)^3 R^4 L}$. Two spreading losses (out and back) give $R^{-4}$: **+12.04 dB of SNR is needed per doubling of range**, and range scales as the fourth root of power, gain², σ and integration time.
- **Energy form (use this):** $\mathrm{SNR} = \dfrac{P_t\,T_{coh}\,G_tG_r\lambda^2\sigma}{(4\pi)^3R^4\,kT_s\,L}$ where $P_tT_{coh}$ is the transmitted energy that is coherently integrated (pulse width × number of pulses, or chirp sampling time × number of chirps). Pulsed, CW and FMCW radars all obey it; TI's SWRA553 Eq. 2 and Rao's training form are this equation (verified identical to machine precision).
- **Noise:** $kT_0$ = −174 dBm/Hz; $T_s = T_a + T_0(L_r-1) + L_rT_e$ (antenna + line loss + receiver). SNR needed: 13 dB (steady target, Pd 0.9, Pfa 10⁻⁶), 21 dB for a Swerling 1 fluctuating target ([detection theory](detection-theory-cfar.md)).
- **Losses to budget:** Hann window 1.76 dB (Hamming 1.34, Blackman 2.37), straddle up to 1.42 dB (Hann; average 0.46 dB), scanning beam-shape ≈ 1.6–1.7 dB per scanned dimension, CFAR ≈ 1–2 dB, plus two-way atmosphere: **60 GHz ≈ 15 dB/km one way (oxygen)**, 24 GHz 0.17–0.43 dB/km, 77 GHz 0.34–0.77 dB/km, and rain at 77 GHz ≈ 11 dB/km at 25 mm/h and ≈ 31 dB/km at 100 mm/h (see [09 atmospheric](../09-propagation-link-budget/atmospheric-rain-attenuation.md)).
- **Search radar:** $\mathrm{SNR} = \dfrac{P_{av}A_e\,\sigma\,t_s}{4\pi\,\Omega\,R^4\,kT_sL}$ — only the **power–aperture product** and the frame time $t_s$ over solid angle Ω matter, not the beamwidth.
- **Worked numbers (this page):** 77 GHz TI-class chip (12 dBm, NF 15 dB, 10 dBi, 128 × 40 µs): car ≈ 94 m, person ≈ 40 m, small drone ≈ 22 m, small rocket (−20 dBsm) ≈ 17 m per virtual channel (× 1.86 with 12-channel beamforming). 24 GHz Doppler module vs a person: vendor's 15–20 m implies an effective noise figure of 30–35 dB in a 6–600 Hz band — an FFT with 1 Hz bins stretches that to ~90 m for a steady mover. DIY 3 GHz, 1 W, two 1.2 m dishes: ≈ 5 km for a 0.01 m² rocket, 9 km for 0.1 m² — pointing a 5.8° beam at the rocket is harder than getting the SNR.

## Intuition (no math)
A communication link loses power once: the signal spreads out from the transmitter and a small part is caught by the receiving antenna, so received power falls as $1/R^2$. A radar pays this twice. The transmitted wave spreads out to the target ($1/R^2$), the target intercepts a tiny part and re-radiates it in all directions like a new, weak transmitter, and that echo spreads out again on the way back ($1/R^2$ again). Hence $1/R^4$: moving a target twice as far away makes its echo 16 times (12 dB) weaker, and doubling your range requires 16 times more power — or 4 times more antenna gain, since gain helps on both transmit and receive.

What sets the detection limit is not the echo power alone but the echo *energy* compared to the noise per hertz. A receiver that listens for longer, and adds the echoes up coherently (a matched filter, an FFT over many chirps), collects more signal energy while the noise per resolution cell stays fixed. That is why a milliwatt FMCW radar chip listening for 5 ms can do what a pulsed radar with a 1 µs pulse needs watts for: both deliver the same energy.

The target's "size" in the equation is its radar cross section σ (m²), which is not its physical area: it is the area of an imaginary perfect isotropic reflector that would return the same echo — see [radar cross section](radar-cross-section.md).

## The math

### Level 1 — the result and its symbols
$$P_r = \frac{P_t G_t}{4\pi R^2}\cdot\sigma\cdot\frac{1}{4\pi R^2}\cdot\frac{G_r\lambda^2}{4\pi}\cdot\frac{1}{L} = \frac{P_tG_tG_r\lambda^2\sigma}{(4\pi)^3R^4L}$$

| Symbol | Meaning | Unit |
|---|---|---|
| $P_t$ | transmit power at the antenna port (peak power for a pulse, CW power for FMCW) | W |
| $G_t, G_r$ | transmit/receive antenna gains towards the target (linear, not dBi) | — |
| $\lambda = c/f$ | wavelength | m |
| $\sigma$ | radar cross section of the target | m² |
| $R$ | range (monostatic: same for TX and RX) | m |
| $L \ge 1$ | total system losses (linear) | — |
| $P_r$ | received echo power at the receiver input | W |

Noise power in bandwidth $B$: $N = kT_sB$, with $k = 1.380649\times10^{-23}$ J/K and system noise temperature $T_s$ (K). If the receiver is characterised only by its noise figure $F$ and the antenna sees a 290 K scene, $T_s = T_0F$ with $T_0$ = 290 K ($kT_0$ = −174 dBm/Hz). See [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md) and [noise figure](../07-noise-linearity/noise-figure-and-friis.md).

$$\mathrm{SNR} = \frac{P_r}{kT_sB},\qquad R_{max} = \left[\frac{P_tG_tG_r\lambda^2\sigma}{(4\pi)^3 kT_sB\,L\,\mathrm{SNR}_{min}}\right]^{1/4}.$$

In dB (energy form of Level 2, $R$ in m, $T_{coh}$ in s): SNR [dB] $= P_t$[dBW] $+ G_t + G_r + 20\log_{10}\lambda + \sigma$[dBsm] $- 32.98 - 40\log_{10}R + 10\log_{10}T_{coh} + 203.98 - F - L$, where 32.98 dB $= 30\log_{10}4\pi$ and 203.98 dB $= -10\log_{10}(kT_0)$ in dBW/Hz.

### Level 2 — derivation and the energy form

**Step 1 — power density at the target.** An isotropic radiator spreads $P_t$ over a sphere of area $4\pi R^2$; an antenna of gain $G_t$ concentrates it by $G_t$ in its main beam: $S_1 = P_tG_t/(4\pi R^2)$ W/m² (the same step as the [Friis equation](../09-propagation-link-budget/friis-free-space-path-loss.md)).

**Step 2 — definition of RCS.** The target is replaced by a fictitious object that collects power $\sigma S_1$ and re-radiates it isotropically. This is the *definition* of σ: whatever the physics (specular reflection, edges, resonances), σ is the area that makes this bookkeeping give the correct echo. Formally $\sigma = \lim_{R\to\infty}4\pi R^2|E_s|^2/|E_i|^2$ ([RCS page](radar-cross-section.md)).

**Step 3 — power density back at the radar.** $S_2 = \sigma S_1/(4\pi R^2) = P_tG_t\sigma/[(4\pi)^2R^4]$.

**Step 4 — power captured.** A receiving antenna of effective aperture $A_e$ captures $P_r = S_2A_e$, and reciprocity gives $A_e = G_r\lambda^2/(4\pi)$ ([antenna fundamentals](../08-antennas/antenna-fundamentals.md)). Multiplying out gives the Level-1 result. Nothing else is involved; all remaining effects (propagation, losses, polarisation, multipath) are corrections to these four steps.

**Step 5 — from power to energy (why integration time appears).** A matched filter maximises output SNR at $2E/N_0$ (real passband) or $E/N_0$ in complex-baseband bookkeeping, where $E$ is the received echo energy ([matched filter](../10-comms-modulation/matched-filter-detection.md)). For a pulse of width τ and power $P_r$, $E = P_r\tau$; the matched filter's noise bandwidth is ≈ $1/\tau$, so $P_r/(kT_sB) = P_r\tau/(kT_s)$ — the classic "$B\tau \approx 1$" form. Coherently integrating $N$ pulses multiplies the energy by $N$ ([coherent gain = N](detection-theory-cfar.md)). In general, for any waveform coherently processed over a time $T_{coh}$ during which the transmitter delivers average power $P_t$ to the target:
$$\boxed{\mathrm{SNR} = \frac{P_t\,T_{coh}\,G_tG_r\lambda^2\sigma}{(4\pi)^3R^4\,kT_s\,L}}$$
- *Pulsed radar:* $P_tT_{coh} = P_{peak}\,\tau\,N_p$ (= $P_{av}$ × dwell time).
- *FMCW radar:* $P_tT_{coh} = P_t\,N_c\,T_{ADC}$ — the CW power times the total *sampled* chirp time over the frame (idle time and discarded ramp portions do not count).
- *CW Doppler radar:* $T_{coh}$ = FFT length; equivalently $B = 1/T_{coh}$ is the FFT bin width.

**The TI form.** TI's SWRA553 writes the maximum range as $\big[P_tG_{Rx}G_{Tx}c^2\sigma NT_r/(f_c^2(4\pi)^3kT\,NF\,\mathrm{SNR_{det}})\big]^{1/4}$ [1] and Rao's training writes $T_{meas}$ for $NT_r$ with λ² instead of $c^2/f_c^2$ [2]. Both are exactly the energy form with $L = 1$ (checked numerically in `tools/verify/radar_range_equation.py`). The losses they omit must be added by the designer.

**Noise temperature.** For an antenna with temperature $T_a$ (≈ 290 K looking at the ground or buildings; 10–100 K looking at clear sky at microwave frequencies, higher near the horizon), a lossy line of loss $L_r$ at 290 K, and a receiver of effective input noise temperature $T_e = T_0(F-1)$, the system temperature referred to the antenna terminals is
$$T_s = T_a + T_0(L_r - 1) + L_rT_e .$$
Example: $T_a$ = 100 K, 1 dB of cable, 3 dB receiver NF → $T_s$ = 538 K (2.7 dB above 290 K). At low IF frequencies (CW Doppler modules, FMCW at short range) the "receiver" includes 1/f noise of mixer diodes and op-amps and the phase-noise skirt of TX leakage, which can raise the effective $T_s$ by tens of dB (see Example A and [FMCW — phase noise](fmcw-radar.md)).

**Bistatic radar equation.** Transmitter and receiver separated (e.g. a KrakenSDR listening to an FM broadcast tower; see [DIY hardware](diy-radar-hardware.md)). Steps 1–4 with separate ranges $R_t$ (TX → target) and $R_r$ (target → RX) and the bistatic RCS $\sigma_b$:
$$P_r = \frac{P_tG_tG_r\lambda^2\sigma_b}{(4\pi)^3R_t^2R_r^2L},\qquad \mathrm{SNR}\propto\frac{1}{(R_tR_r)^2}.$$
Contours of constant SNR are **ovals of Cassini** ($R_tR_r$ = const), not circles. The range measured is the bistatic range sum $R_t + R_r - L_{baseline}$ (ellipses with the two sites as foci). In passive radar the direct-path signal is typically 60–90+ dB stronger than the echoes and must be cancelled before the cross-ambiguity function is computed; that, not thermal noise, usually limits performance.

### Level 3 — search vs track, losses, propagation factor, limits

**Track (dwell) form.** With $A_e = G_r\lambda^2/4\pi$ and average power $P_{av}$ over a dwell $t_d$ on the target:
$$\mathrm{SNR} = \frac{P_{av}\,G_t\,A_e\,\sigma\,t_d}{(4\pi)^2R^4kT_sL}.$$

**Search (power–aperture) form.** A search radar must cover a solid angle Ω (sr) every $t_s$ seconds. Its beam has solid angle $\Omega_b \approx 4\pi/G_t$, so the time spent on each beam position is $t_d = t_s\Omega_b/\Omega = 4\pi t_s/(G_t\Omega)$. Substituting:
$$\mathrm{SNR} = \frac{P_{av}\,A_e\,\sigma\,t_s}{4\pi\,\Omega\,R^4\,kT_s\,L}.$$
The transmit gain cancels: a narrow beam gets more SNR per look but has to make more looks. For surveillance, **only the power–aperture product $P_{av}A_e$ buys range** (verified identical to the track form with the substituted dwell). Wavelength does not appear either, which is why long-range surveillance radars use lower frequencies (cheap big apertures, less weather loss) and trackers use higher ones (narrow beams, accuracy).

**Loss budget (typical values, with sources).**

| Loss | Typical value | Notes |
|---|---|---|
| TX/RX line & connector loss | 0.5–3 dB total | include radome (0.5–2 dB at mm-wave) |
| Window (processing) loss, per FFT dimension | rect 0 / Hamming 1.34 / Hann 1.76 / Blackman 2.37 dB | $10\log_{10}(\mathrm{ENBW})$ [3]; verified |
| Straddle (scalloping), per FFT dimension | worst: rect 3.92 / Hamming 1.75 (harris lists 1.78 dB, which is the scalloping of the "exact" Hamming $a_0$ = 25/46; 0.54/0.46 gives 1.75 dB) / Hann 1.42 / Blackman 1.10 dB; Hann average ≈ 0.46 dB | target between bins [3]; verified |
| Range-gate straddle (pulsed) | ~0.5–1 dB average | sampling not at the matched-filter peak |
| Beam-shape (scanning) loss | ≈ 1.6–1.7 dB per scanned dimension | Gaussian beam, pulses across the 3-dB width; 1.67 dB computed, Blake 1.6 dB [4] |
| CFAR loss | 1–2 dB (N = 16–32) | [detection page](detection-theory-cfar.md) |
| Fluctuation loss | 0–17 dB | Swerling 1 vs 0 at Pd 0.9 → 8 dB |
| Polarisation mismatch | 0–3 dB (or more for cross-pol) | [09 polarisation](../09-propagation-link-budget/polarization-mismatch-loss.md) |
| Atmosphere, two-way | 2 × γ × R | 60 GHz: γ ≈ 13–15 dB/km (O₂); 24 GHz 0.17–0.43; 77 GHz 0.34–0.77 dB/km [5] |
| Rain, two-way | 2 × γ_R × R | 77 GHz: 11.4 dB/km @ 25 mm/h, ≈ 31 dB/km @ 100 mm/h; 24 GHz 3.7 dB/km @ 25 mm/h [5] |

**Propagation factor.** Over a reflecting surface (ground, sea, a launch-rail pad) the direct and reflected rays interfere; the one-way field factor $F$ (0 to 2) enters the radar equation as $F^4$ (two-way). Near the lobe peaks SNR is up to 12 dB higher than free space, in the nulls it collapses — relevant for low-elevation tracking of a rocket just after launch ([two-ray model](../09-propagation-link-budget/two-ray-ground-reflection.md)).

**Where the equation stops being right.**
- *Near field of the antenna / target:* the far-field assumptions need $R > 2D^2/\lambda$ for both the antenna and the target. A 1.2 m dish at 3 GHz: 29 m. A 2 m rocket seen broadside at 24 GHz: 640 m — closer than that the RCS is not the far-field value.
- *Extended targets:* rain, sea and ground fill the beam or the range cell; their echo scales as $R^{-2}$ (volume) or $R^{-3}$ (surface), not $R^{-4}$ ([clutter](clutter-and-mti.md)).
- *Dynamic range / leakage limited radars:* a CW or FMCW radar is often limited by TX→RX leakage, its phase-noise skirt and ADC dynamic range rather than thermal noise ([FMCW](fmcw-radar.md), [CW](cw-and-doppler-radar.md)).
- *Integration assumptions:* $T_{coh}$ must be shorter than the time the target stays in one range–Doppler cell and than the coherence time of the target and of the oscillator.
- *Horizon:* with standard refraction ($4/3$ Earth), the radar horizon distance is ≈ $4.12\sqrt{h}$ km for antenna height $h$ in m ([radio horizon](../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md)) — irrelevant for a rocket overhead, relevant for a low-flying drone.

## Design equations & rules of thumb

| Equation / rule | When valid | Typical numbers |
|---|---|---|
| $P_r = P_tG_tG_r\lambda^2\sigma/[(4\pi)^3R^4L]$ | far field, point target, monostatic | $(4\pi)^3$ = 32.98 dB |
| $\mathrm{SNR} = P_tT_{coh}G_tG_r\lambda^2\sigma/[(4\pi)^3R^4kT_sL]$ | any coherently processed waveform | $kT_0$ = −174 dBm/Hz = −204 dBW/Hz |
| $R \propto (P_tT_{coh}G_tG_r\sigma)^{1/4}\lambda^{1/2}$ at fixed gains | — | +12.04 dB per range doubling; 2× range needs 16× energy |
| $R \propto (P_tT_{coh}A_e^2\sigma)^{1/4}\lambda^{-1/2}$ at fixed apertures | fixed antenna size | higher f → more range per aperture (if atmosphere allows) |
| Search: $\mathrm{SNR} = P_{av}A_e\sigma t_s/(4\pi\Omega R^4kT_sL)$ | volume search | power–aperture product |
| Bistatic: $\mathrm{SNR}\propto (R_tR_r)^{-2}$ | separated TX/RX | ovals of Cassini |
| $T_s = T_a + T_0(L_r-1) + L_rT_e$ | lossy feed at 290 K | 538 K for 100 K / 1 dB / NF 3 dB |
| MIMO/array coherent gain $N_{virt}$ | beamforming towards target | 12 channels → +10.8 dB → range × 1.86 |
| Doppler per km/h: $2f/(3.6c)$ | radial motion | 19.50 Hz @ 10.525 GHz; 44.71 Hz @ 24.125 GHz; 142.7 Hz @ 77 GHz |

## Worked examples
All numbers from `tools/verify/radar_range_equation.py`. Assumed parameters are marked.

**A — 24 GHz Doppler module (InnoSenT IPM-165 / its CDM324 clone) looking for a walking person.** Datasheet: EIRP $P_tG_t$ = 16 dBm typ, antenna gain 9.5 dBi, 80° × 35° beam, single-channel output; the vendor's application note says a person is seen at 15–20 m with a 6–600 Hz audio amplifier [6], [7]. Take σ = 0.3 m² (−5.2 dBsm, inside the −7.7 to −3.0 dBsm azimuth-averaged range measured for humans at 24/77 GHz [8]), λ = 12.43 mm, SNR = 13 dB, B = 600 Hz. Solving the radar equation for the noise figure that reproduces 15–20 m gives **30–35 dB** effective NF. That is not a mistake: a zero-IF diode mixer at audio frequencies suffers 1/f noise, oscillator AM/FM noise on the leakage, and op-amp noise; vendors also quote conservative ranges. The lesson is the scaling, not the absolute number: with the same front end, replacing the 600 Hz analog filter with an FFT of $T$ seconds reduces $B$ to $1/T$:
- 0.1 s FFT (10 Hz bins): 49 m; 0.25 s (4 Hz): 61 m; 1 s (1 Hz): 87 m — as long as the target's Doppler stays within one bin for $T$ (a walking person's limbs spread the spectrum over ~±100 Hz, so real gains are smaller; see [micro-Doppler](cw-and-doppler-radar.md)).

**B — 77 GHz TI AWR1843-class FMCW radar.** Datasheet: TX 12 dBm, NF 15 dB (77–81 GHz) [9]. Assumed: $G_t = G_r$ = 10 dBi (patch array on an EVM), 128 chirps with 40 µs ADC sampling each ($T_{coh}$ = 5.12 ms), losses 3 dB (Hann in range and Doppler plus margin), SNR$_{min}$ = 15 dB (Rao's 15–20 dB [2]). λ = 3.89 mm.

| Target | σ | R_max, one TX–RX pair | R_max with 12-channel coherent beamforming |
|---|---|---|---|
| car | 10 dBsm | 94 m | 175 m |
| person | −5 dBsm | 40 m | 74 m |
| small drone | −15 dBsm | 22 m | 41 m |
| small hobby rocket, tail-on (assumed) | −20 dBsm | 17 m | 31 m |
| 10 cm triangular trihedral reflector | 14.4 dBsm | 121 m | 225 m |

(Rocket σ is an assumption; see [RCS page](radar-cross-section.md). The drone value sits inside the −8 to −19 dBsm measured at 24 GHz [10].) A chip like this is a short-range sensor: it will see a rocket leave the pad, not follow it to apogee.

**C — MIT coffee-can radar at 2.4 GHz** [11]. Assumed: $P_t$ = 10 dBm, can antennas ≈ 7 dBi each, NF 6 dB, one 20 ms up-chirp coherently processed, L = 3 dB, SNR 13 dB → SNR-limited range ≈ 880 m for a car (10 m²), ≈ 420 m for a person (0.5 m²). But the IF is digitised by a laptop audio input: with ≈ 90 MHz swept in 20 ms (slope 4.5 × 10⁹ Hz/s) and 22.05 kHz Nyquist, the beat-frequency limit is $R = f_bc/(2S)$ ≈ **734 m**, and the range resolution is $c/2B$ ≈ 1.7 m. Two different limits — always compute both (see [FMCW](fmcw-radar.md)).

**D — DIY S-band (3 GHz) rocket tracker.** Assumed: 1 W CW/FMCW, separate 1.2 m TX and RX dishes (aperture efficiency 0.55 → 28.9 dBi, beamwidth ≈ 70λ/D = 5.8°), NF 2 dB, 10 ms coherent processing, SNR 15 dB, L 3 dB. Maximum range: **5.3 km for 0.01 m², 9.4 km for 0.1 m², 16.7 km for 1 m²**. A 3 km-apogee hobby rocket is therefore within SNR reach, but the 5.8° beam is only ~100 m wide at 1 km: a rocket moving at 200 m/s across the line of sight at 1 km sweeps 11.5°/s and crosses the beam in about 0.5 s. The engineering problems are acquisition and pointing (a mount that can slew at tens of °/s, or a GNSS-fed pointing loop from the rocket's own telemetry), plus TX–RX isolation for CW, not the SNR budget. Doppler-only velocity tracking along the beam axis is the easiest first project (see [CW and Doppler](cw-and-doppler-radar.md)).

**E — Search radar for drones (power–aperture form).** X-band, $P_{av}$ = 10 W, $A_e$ = 0.1 m² (a ~35 cm square array), cover 90° × 20° (Ω = 0.548 sr) every second, $T_s$ = 500 K, L = 6 dB, SNR 13 dB, σ = 0.01 m² → **R ≈ 7.2 km**. Halving the frame time or doubling Ω costs 16 % of range; doubling $P_{av}A_e$ gains 19 %.

**F — Passive bistatic radar with an FM broadcast illuminator.** Assumed: 10 kW ERP (16.4 kW EIRP, since ERP is referenced to a dipole: +2.15 dB) at 98 MHz, 5 dBi receive antenna, bistatic σ = 10 m² (aircraft), 1 s coherent integration, external noise figure $F_a$ = 15 dB (man-made/galactic noise dominates at VHF; ITU-R P.372), SNR 13 dB, L 6 dB → $R_tR_r \approx 1.6\times10^4$ km², e.g. $R_t$ = 20 km allows $R_r$ up to ~780 km on thermal noise alone. Real systems are limited by direct-path and multipath interference cancellation and by the illuminator's ambiguity function (FM programme content varies), which is why hobby passive radar sees aircraft at tens of km, not hundreds.

## Practical notes
- **Measure $P_t$, $G$ and $T_s$ rather than trusting datasheets.** A calibrated corner reflector ([RCS page](radar-cross-section.md)) at a known range gives a direct check of the whole budget: measured SNR vs predicted SNR = your unknown loss.
- **EIRP vs conducted power.** Module datasheets (HB100, IPM-165) quote EIRP ($P_tG_t$); do not add the antenna gain again.
- **Use energy, not power, when comparing waveforms.** An FMCW chip with 12 dBm and 5 ms frames delivers 80 µJ per frame — equivalent to a 80 W, 1 µs pulse.
- **Atmosphere matters at mm-wave.** A 60 GHz radar (IWR6843, BGT60, Acconeer A121) outdoors loses ≈ 3 dB two-way per 100 m to oxygen alone; use 60 GHz for short range (< ~30 m) and 24/77 GHz for longer outdoor ranges. Singapore's humid air roughly doubles gaseous loss at 24 and 77 GHz versus the ITU standard atmosphere, and tropical downpours can cost 10+ dB at 150 m for 77 GHz [5].
- **SNR is per cell after processing.** State where it is measured (after range FFT? after Doppler FFT? after beamforming?) and which losses are already included.
- **Close-range saturation.** $R^{-4}$ means a target at 1 m is 80 dB stronger than at 100 m — the receiver/ADC dynamic range, not sensitivity, sets the near limit (FMCW radars use a high-pass IF filter as an $R^2$ "sensitivity time control"; see [FMCW](fmcw-radar.md)).
- **Regulatory EIRP caps** set $P_tG_t$ in practice: in Singapore 24.00–24.25 GHz and 57–64 GHz SRDs are limited to 100 mW EIRP (IMDA TS SRD, Sep 2023) [12], and 77–81 GHz sensors to a mean e.i.r.p. density of −3 dBm/MHz as UWB devices (IMDA TS UWB 2016; see [DIY radar](diy-radar-hardware.md)); more range must then come from receive gain and integration time.

## Common mistakes & misconceptions
- **Using Friis ($R^{-2}$) for a radar.** Radar is two-way: $R^{-4}$ for point targets.
- **Using the IF filter bandwidth as B when an FFT follows.** The relevant bandwidth is the FFT bin width (1/T), not the anti-alias filter bandwidth — processing gain is real.
- **Treating TI's "max range" formula as the answer.** It omits all losses and assumes one TX–RX pair; add window, straddle, CFAR, radome and propagation losses, and decide whether the SNR is per virtual channel or after beamforming.
- **Confusing σ with physical area.** A 10 cm corner reflector has 14 dBsm (27 m²) at 77 GHz; a 2 m car can be 10–20 dBsm; a person is ~−5 dBsm.
- **Forgetting that the target fluctuates.** Budget 21 dB, not 13 dB, for Pd 0.9 on a single look at a Swerling 1 target — or use several looks ([detection](detection-theory-cfar.md)).
- **"More power doubles the range."** Four times the power gives only 1.41 times the range.
- **Ignoring integration-time limits.** You cannot integrate a rocket echo for 1 s if it accelerates through many Doppler bins in that time (the echo smears; see [CW and Doppler](cw-and-doppler-radar.md) for Doppler rate).
- **Mixing peak and average power.** Pulsed-radar SNR depends on energy = peak power × pulse width × number of pulses = average power × dwell time.

## How to simulate / verify
- `tools/verify/radar_range_equation.py` (~5 s, **ALL PASS**): form equivalence (TI/Rao/energy/pulsed), dB budget, window & scalloping losses (Harris), Gaussian beam-shape loss, noise temperature, and all worked examples A–F (edit the parameter block for your radar).
- Required SNR for given Pd/Pfa/Swerling/N: `tools/verify/radar_detection_cfar.py` (functions `req_snr_exact`, `albersheim`, `shnidman`).
- Atmospheric and rain losses: `tools/verify/prop_atmospheric.py` (domain 09).
- Bench check: measure a corner reflector at 3–5 ranges; fit $P_r \propto R^{-4}$ on a log–log plot — the slope checks the far-field/free-space assumption, the offset checks $P_tG_tG_r$.

## Open questions / gaps
- The effective noise figure of zero-IF Doppler modules at audio frequencies (1/f corner of the mixer diodes) is only inferred here from the vendor's range claim, not measured; a measurement recipe belongs in 17-test-measurement.
- Antenna gains of TI EVMs were assumed (10 dBi) rather than taken from the EVM user guides.
- The coffee-can transmit power and sweep bandwidth are approximate (from the course parts list and VCO datasheet, not a measured unit).
- Clear-sky antenna temperatures for a tracking radar at low elevation in the tropics were not quantified.

## Sources
1. V. Dham, "Programming Chirp Parameters in TI Radar Devices," TI application report SWRA553A, May 2017, rev. Feb 2020, §2.1, Eq. 1–2 — https://www.ti.com/lit/pdf/swra553 (app note)
2. S. Rao, "Introduction to mmwave Sensing: FMCW Radars," TI mmWave training (offline slides) — radar range equation with $T_{meas}$, SNR$_{min}$ 15–20 dB typical. https://www.ti.com/content/dam/videos/external-videos/ko-kr/2/3816841626001/5415203482001.mp4/subassets/mmwaveSensing-FMCW-offlineviewing_0.pdf (app note/training)
3. F. J. Harris, "On the use of windows for harmonic analysis with the discrete Fourier transform," *Proc. IEEE*, vol. 66, no. 1, pp. 51–83, 1978 — ENBW, processing and scalloping losses (reproduced numerically; Hamming scalloping 1.78 dB in the paper vs 1.75 dB computed for 0.54/0.46; 1.78 dB is the scalloping of the 25/46 "exact" Hamming, while the paper's ENBW and PSL are the 0.54 values). (peer-reviewed)
4. L. V. Blake, *Radar Range-Performance Analysis*, Munro, 1986 (orig. NRL reports) — beam-shape loss ≈ 1.6 dB; system noise temperature bookkeeping. Also M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed., 2001, ch. 2. (textbook)
5. KB page [atmospheric and rain attenuation](../09-propagation-link-budget/atmospheric-rain-attenuation.md) — ITU-R P.676-11, P.838-3, P.840 values verified in `tools/verify/prop_atmospheric.py`. (standard, via KB)
6. InnoSenT GmbH, IPM-165 data sheet v8.5 (2014): 24.050–24.250 GHz, EIRP 16 dBm typ/20 dBm max, 9.5 dBi, 80° × 35°. https://media.digikey.com/pdf/Data%20Sheets/InnoSenT/IPM-165_V8.5_DS.pdf (datasheet)
7. W. Weidmann, InnoSenT "Application Note III — IPM-165": 70–80 dB LF gain, 6–600 Hz filter, person at 15–20 m, 44 Hz per km/h. https://www.innosent.de/fileadmin/media/dokumente/Downloads/Application_Note_III_-_web.pdf (app note)
8. EC JRC / EMSL, "Radar cross section measurements of pedestrian dummies and humans in the 24/77 GHz frequency bands," 2013 (JRC78619) — human RCS −16.6 to 0 dBsm vs azimuth at 77 GHz; azimuth/frequency averages −7.7 to −3.0 dBsm. https://publications.jrc.ec.europa.eu/repository/handle/JRC78619 (report; abstract)
9. Texas Instruments, AWR1843 product page/datasheet summary: 76–81 GHz, 3 TX/4 RX, 12 dBm, NF 14/15 dB, PN −95/−93 dBc/Hz @ 1 MHz. https://www.ti.com/product/AWR1843 (datasheet)
10. R. Nakamura, K. Suzuki, H. Hadama, "RCS measurements of various drones at 24 GHz," *IEICE Communications Express*, vol. 9, no. 7, 2020 — mean RCS −8.1 to −19.1 dBsm. (peer-reviewed letter; abstract)
11. G. L. Charvat, A. J. Fenn, B. T. Perry, "The MIT IAP radar course: Build a small radar system capable of sensing range, Doppler, and synthetic aperture (SAR) imaging," IEEE Radar Conf. 2012; MIT OCW RES.LL-003 (IAP 2011). https://ocw.mit.edu/courses/res-ll-003-build-a-small-radar-system-capable-of-sensing-range-doppler-and-synthetic-aperture-radar-imaging-january-iap-2011/ (lecture notes / course)
12. IMDA, "Technical Specification — Short Range Devices," IMDA TS SRD Issue 1 Rev 3, September 2023, Table 1 (sub-bands 37–41). (standard/regulation)
13. M. A. Richards, J. A. Scheer, W. A. Holm, *Principles of Modern Radar, Vol. I*, SciTech 2010, ch. 2 (radar equation, search/track forms, loss budgets). (textbook)
14. B. R. Mahafza, *Radar Systems Analysis and Design Using MATLAB*, 3rd ed., CRC 2013, ch. 2 (radar equation forms, search equation, bistatic equation). (textbook)
15. H. D. Griffiths, C. J. Baker, *An Introduction to Passive Radar*, Artech House, 2017 — bistatic geometry, direct-path interference. (textbook; qualitative use)
16. `tools/verify/radar_range_equation.py` — all numeric results on this page. (verification script)
