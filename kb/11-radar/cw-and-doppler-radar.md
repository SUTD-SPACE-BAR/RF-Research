---
title: CW and Doppler radar — the Doppler equation, homodyne I/Q receivers, micro-Doppler, HB100/CDM324 modules, speed guns and rocket-velocity measurement
domain: 11-radar
slug: cw-and-doppler-radar
tags: [doppler, cw-radar, homodyne, iq, quadrature, image-rejection, micro-doppler, vital-signs, hb100, cdm324, ipm-165, speed-gun, cosine-error, rocket-velocity, doppler-rate, phase-noise, range-correlation, leakage, fsk-radar, 10.525ghz, 24ghz]
prerequisites:
  - radar-range-equation.md
  - ../00-math-foundations/complex-numbers-and-phasors.md
  - ../00-math-foundations/fourier-series-and-transform.md
related:
  - fmcw-radar.md
  - diy-radar-hardware.md
  - radar-cross-section.md
  - detection-theory-cfar.md
  - clutter-and-mti.md
  - ../07-noise-linearity/phase-noise-and-jitter.md
  - ../07-noise-linearity/shot-and-flicker-noise.md
  - ../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md
  - ../14-sdr-dsp/iq-complex-baseband.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# CW and Doppler radar

## Questions this page answers
- Where does the two-way Doppler shift $2v/\lambda$ come from, and when is it not accurate?
- How many hertz of Doppler do I get per km/h at 10.525, 24 and 77 GHz?
- How does a CW homodyne radar work, and why do I need I and Q to know if a target approaches or recedes?
- How much I/Q imbalance can I tolerate?
- Why does my HB100 "see nothing" on the oscilloscope?
- What is micro-Doppler, and how can a radar see propellers, walking legs, breathing and heartbeats?
- Can I measure my rocket's velocity off the pad with a 24 GHz Doppler module? For how long and how far?
- Why can't a CW radar measure range, and how does two-frequency (FSK) CW fix that?
- What limits the dynamic range of a CW radar (leakage, phase noise, 1/f noise)?
- What is the "cosine error" of a speed gun?
- Which Doppler frequencies and powers are legal in Singapore?

## TL;DR
- **Doppler:** echo phase $\phi(t) = -4\pi R(t)/\lambda$, so $f_d = -\frac{2}{\lambda}\frac{dR}{dt} = \frac{2v_r}{\lambda}$ ($v_r$ > 0 approaching). The exact (relativistic) two-way result differs by < 3.4 × 10⁻⁶ relative at 1 km/s — irrelevant for any radar you will build.
- **Hz per km/h (per m/s):** 10.525 GHz **19.50 (70.2)**; 24.125 GHz **44.71 (160.9)**; 60.5 GHz 112.1 (403.6); 77 GHz **142.7 (513.7)**; 5.8 GHz 10.75 (38.7); 2.45 GHz 4.54 (16.3).
- **Homodyne CW radar** = oscillator + mixer that multiplies the echo by the transmit signal: output is a tone at $f_d$ with phase $-4\pi R/\lambda$. **A single mixer (HB100, CDM324/IPM-165 "mono") gives a real signal — it cannot tell approaching from receding** and cannot see stationary objects. An I/Q (quadrature, "stereo") front end gives the sign. I/Q imbalance of 0.5 dB / 3° still gives 28 dB image rejection; 0.1 dB / 1° gives 40 dB.
- **HB100** (ST Engineering Electronics, Singapore): 10.525 GHz DRO, EIRP 20 dBm typ, 80° × 40° beam, single balanced mixer, bistatic patch arrays, FCC 15.245 [1]. **IPM-165 / CDM324** (24.050–24.250 GHz): EIRP 16 dBm typ, 9.5 dBi, 80° × 35°, mono output [2]. Both need **70–80 dB of low-noise audio gain** and a band-pass filter (6–600 Hz for people) before you see anything [3].
- **Micro-Doppler:** a scatterer rotating at radius $r$ and angular rate Ω produces a sinusoidal Doppler of peak $2\Omega r/\lambda$ — a 24 cm drone propeller at 6000 rpm: **±12.1 kHz at 24 GHz**, with blade "flashes" at N_blades × rev/s (even N). Breathing (4 mm) at 24 GHz swings the phase by **4 rad** — use arctangent (phase) demodulation, not the small-angle approximation.
- **Rocket off the pad (24.125 GHz):** 250 m/s → 40.2 kHz Doppler; 10 g acceleration sweeps the Doppler at 16.1 kHz/s, limiting coherent FFTs to **≈ 7.9 ms** (127 Hz bins, 0.79 m/s). A bare module sees a −20 dBsm rocket only to **~20–25 m**; adding ~10 dB lens/horn gain on TX and RX gives ~70 m, and a low-noise IF chain ~130 m (assumed noise figures) — enough for rail-exit velocity, not for the whole flight.
- **CW has no range** (no timing mark). Two-frequency FSK CW measures range from the phase difference: $R = c\,\Delta\phi/(4\pi\Delta f)$, unambiguous to $c/(2\Delta f)$ (60 m for 2.5 MHz).
- **Range correlation** saves CW radars from oscillator phase noise: the IF phase noise is the oscillator's times $4\sin^2(\pi f\tau)$ (−88 dB at 100 Hz offset for a 10 m target). What limits them instead is TX→RX leakage amplitude noise, 1/f mixer and op-amp noise, supply ripple and microphonics.

## Intuition (no math)
Shine a steady tone at a target and listen to the echo. If the target is still, the echo is the same tone, delayed. If it approaches, every successive wave crest has a slightly shorter trip, so crests arrive more often: the echo's pitch is raised. Because the shift happens twice — once as the moving target "receives" the wave and once as it "re-transmits" it — the shift is twice what a moving listener would hear: $2v/\lambda$. At 24 GHz a walking person (1 m/s) shifts the 24 000 000 000 Hz carrier by only 161 Hz — right in the audio band.

To hear that tiny shift you mix (multiply) the echo with the transmitted tone. Mixing produces the difference frequency: an audio tone at the Doppler frequency. That is all a HB100 or CDM324 module is: an oscillator, two little patch antennas and a mixer diode pair. What comes out of its IF pin is a microvolt-level audio signal that needs a big, quiet amplifier.

A single mixer output is a real cosine: it cannot tell +161 Hz from −161 Hz, i.e. approaching from receding. Add a second mixer driven with the oscillator shifted by 90° and you get I and Q — a complex signal whose rotation direction gives the sign of the velocity.

Moving parts of a target — propellers, arms and legs, a beating heart — add their own tiny, time-varying Doppler shifts on top of the body's. Their "signature" in a time–frequency plot (spectrogram) is called micro-Doppler and is how radars tell a drone from a bird.

## The math

### Level 1 — the Doppler shift and the homodyne output
Transmit $s_T(t) = \cos(2\pi f_0t)$. A point target at range $R(t)$ returns $s_R(t) = A\cos\!\big(2\pi f_0(t - 2R(t)/c)\big)$. The phase of the echo relative to the transmitter is
$$\phi(t) = -\frac{4\pi f_0R(t)}{c} = -\frac{4\pi R(t)}{\lambda}\ \text{rad}.$$
The instantaneous frequency offset is $f_d = \frac{1}{2\pi}\frac{d\phi}{dt} = -\frac{2}{\lambda}\frac{dR}{dt}$. Writing the radial (closing) speed $v_r = -dR/dt$:
$$\boxed{f_d = \frac{2v_r}{\lambda} = \frac{2v_rf_0}{c}}\qquad(v_r>0 \text{ approaching} \Rightarrow f_d>0).$$
If the target moves at angle θ to the line of sight, only $v\cos\theta$ counts (**cosine effect**: a speed gun 10° off the road reads 98.5 %; 20° reads 94 %).

The homodyne mixer output (low-pass filtered) is
$$v_{IF}(t) = \tfrac12 A\cos\!\big(2\pi f_dt + \phi_0\big),\qquad \phi_0 = -4\pi R_0/\lambda,$$
with I/Q: $z(t) = I + jQ = \tfrac12 Ae^{\,j(2\pi f_dt + \phi_0)}$.

### Level 2 — derivations and receiver details

**Exact Doppler.** For a mirror receding at speed $v$ (β = v/c), Lorentz transformation twice gives $f_r = f_0(1-\beta)/(1+\beta)$; approaching gives $f_0(1+\beta)/(1-\beta) \approx f_0(1 + 2\beta + 2\beta^2)$. The relative error of $2v/\lambda$ is ≈ β: 3.3 × 10⁻⁶ at 1000 m/s (computed). The first-order formula is exact enough for everything except precision space tracking.

**Why I and Q.** A real signal $\cos(2\pi f_dt + \phi_0) = \tfrac12(e^{j(\cdot)} + e^{-j(\cdot)})$ has equal spectral lines at $+f_d$ and $-f_d$ (simulated ratio exactly 1). The quadrature channel removes one of them: $I + jQ$ contains only $e^{+j2\pi f_dt}$ for an approaching target and $e^{-j2\pi f_dt}$ for a receding one (simulated). See [I/Q and complex baseband](../14-sdr-dsp/iq-complex-baseband.md).

**Image rejection with imperfect I/Q.** If $Q = g\sin(2\pi f_dt + \varphi)$ (gain ratio $g$, phase error φ), the complex signal contains a wanted line and an image at $-f_d$ with power ratio
$$\mathrm{IRR} = \frac{1 + 2g\cos\varphi + g^2}{1 - 2g\cos\varphi + g^2}.$$
0.5 dB / 3° → 28.2 dB; 1 dB / 5° → 22.8 dB; 0.1 dB / 1° → 39.6 dB (simulation matches to 0.01 dB). Imbalance creates "ghost" targets of the opposite velocity; they can be calibrated out (Gram–Schmidt orthogonalisation or ellipse fitting of a moving reflector's I/Q trace).

**Doppler processing.** Sample $z(t)$ at $f_s > 2|f_{d,max}|$ (complex) and FFT $N$ samples ($T = N/f_s$): bin width $1/T$ → velocity resolution $\Delta v = \lambda/(2T)$. The FFT is a coherent integrator: SNR gain $N$, so the noise bandwidth in the [radar equation](radar-range-equation.md) is $1/T$, not the analogue filter bandwidth. Detection in the Doppler spectrum uses [CFAR](detection-theory-cfar.md).

**Doppler rate and coherent time.** A target accelerating at $a$ sweeps its Doppler at $\dot f_d = 2a/\lambda$. Over an FFT of length $T$ the drift is $\dot f_dT$; keeping it within one bin ($\dot f_dT \le 1/T$) gives
$$T_{max} = \sqrt{\frac{\lambda}{2a}} .$$
10 g at 24.125 GHz: $\dot f_d$ = 16.1 kHz/s, $T_{max}$ = 7.9 ms. Longer integration needs acceleration compensation (de-chirping the Doppler with a trial rate — a search over $a$).

**Micro-Doppler of rotation [4].** A scatterer at radius $r$ on a rotor spinning at Ω in a plane containing the line of sight has $R(t) = R_0 + r\cos(\Omega t + \theta_0)$, so
$$f_{d,\mu}(t) = \frac{2r\Omega}{\lambda}\sin(\Omega t + \theta_0),\qquad f_{max} = \frac{2\Omega r_{tip}}{\lambda} = \frac{2v_{tip}}{\lambda}.$$
The echo of the whole blade is the sum over $r$; when the blade is perpendicular to the line of sight all its scatterers have the same range and add coherently — a broadband **blade flash**. A blade is perpendicular twice per revolution; for an even number of blades the flashes coincide in pairs (flash rate = N·rev/s), for an odd number they interleave (2N·rev/s) [4]. Simulated: 24 cm, 2-blade, 6000 rpm propeller at 24 GHz → micro-Doppler extent ±12.1 kHz (12.5 kHz observed including window width) and flashes at 195 Hz (theory 200 Hz). The echo can also be viewed as sinusoidal phase modulation: $e^{j\beta\sin\Omega t}$ with $\beta = 4\pi r/\lambda$, i.e. Bessel-function sidebands at multiples of Ω — the same mathematics as [FM](../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md).

**Vital signs.** Chest displacement $d(t)$ produces $\phi(t) = -4\pi(R_0 + d(t))/\lambda$. At 24 GHz a 4 mm breathing excursion is 4.04 rad of phase — far outside the small-angle regime where the real IF voltage is proportional to $d$. The robust method: (1) remove the static offset (TX leakage and clutter) by fitting a circle to the I/Q arc and moving its centre to the origin; (2) take $\arg(z)$ and unwrap; (3) $d = -\lambda\phi/(4\pi)$. Simulation recovers breathing plus a 0.3 mm, 1.2 Hz heartbeat with rms error equal to the noise limit $\frac{\lambda}{4\pi}\frac{\sigma}{A}$ (σ = noise per quadrature, A = echo amplitude): 49 µm and 4.9 µm for SNR per sample of 26 and 46 dB.

### Level 3 — what really limits CW radars

**Leakage and dynamic range.** In a CW radar the transmitter is always on. Some of it leaks into the receiver (antenna coupling, board coupling, reflections from a radome or the launch rail), often 20–40 dB below the transmit power — far stronger than any echo (Dürr et al. report best-case TX–RX isolation of ~30 dB in monostatic FMCW designs [5]). In a homodyne the leakage becomes a DC voltage; the problem is the *noise* it carries:
- **Phase noise and range correlation.** Leakage and echo carry the same oscillator phase noise, delayed by τ. Mixing subtracts them, leaving $\mathcal L_{IF}(f) = \mathcal L_{osc}(f)\cdot 4\sin^2(\pi f\tau) = 2\mathcal L_{osc}(f)(1-\cos 2\pi f\tau)$ [5], [6]. For small $f\tau$ this is $(2\pi f\tau)^2\mathcal L_{osc}$: 10 m and 100 Hz → −87.6 dB; 100 m and 10 kHz → −27.6 dB (computed). Short-range CW radars are therefore surprisingly tolerant of a noisy oscillator (a free-running DRO or VCO is fine). See [phase noise](../07-noise-linearity/phase-noise-and-jitter.md).
- **AM noise** of the oscillator on the leakage is *not* cancelled; balanced mixers suppress it partly.
- **1/f noise** of Schottky mixer diodes and op-amps rises at audio frequencies — the reason the implied effective noise figure of a mono 24 GHz module in a 6–600 Hz band is ~30–35 dB ([radar equation example A](radar-range-equation.md); [flicker noise](../07-noise-linearity/shot-and-flicker-noise.md)).
- **Microphonics and supply ripple.** Vibration of the module or of nearby metal modulates the leakage phase, producing spurious "Doppler" lines — a real problem on a launch rail or inside a vibrating rocket. Supply ripple frequency-pushes the oscillator (≈ 6 MHz per 5 % of Vcc for the IPM-165 [3]); fluorescent/LED lighting produces 100 Hz (Singapore mains 50 Hz) lines.

**Ranging with CW: FSK.** Alternate between $f_1$ and $f_2 = f_1 + \Delta f$. The Doppler lines of the two channels have phases $-4\pi f_{1,2}R/c$; their difference
$$\Delta\phi = \frac{4\pi\Delta f\,R}{c}\ \Rightarrow\ R = \frac{c\,\Delta\phi}{4\pi\Delta f},\qquad R_u = \frac{c}{2\Delta f}.$$
With Δf = 2.5 MHz (the FSK step InnoSenT demonstrates by pulsing the supply [3]) $R_u$ = 60 m. Only moving targets are ranged, and targets in the same Doppler bin cannot be separated. The simulated estimate refers to the target's range at the middle of the observation (35.76 m for a target moving from 37.3 m at −3 m/s over 1 s). FMCW generalises this idea; see [FMCW](fmcw-radar.md).

## Design equations & rules of thumb

| Equation | When valid | Typical numbers |
|---|---|---|
| $f_d = 2v_r/\lambda$ | $v \ll c$ | 44.71 Hz per km/h at 24.125 GHz |
| $\Delta v = \lambda/(2T)$ | FFT length T | 24 GHz, 0.25 s → 2.5 cm/s |
| $f_{s} > 2f_{d,max}$ (complex) | Doppler sampling | 250 m/s @24 GHz → > 80.5 kHz |
| $T_{max} = \sqrt{\lambda/(2a)}$ | accelerating target | 10 g: 7.9 ms @24 GHz, 11.9 ms @10.5 GHz |
| $f_{\mu,max} = 2v_{tip}/\lambda$ | rotors | 75 m/s tip → 12.1 kHz @24 GHz |
| Flash rate $N\cdot$rev/s (even N), $2N\cdot$rev/s (odd N) | blades | 2 blades, 6000 rpm → 200 Hz |
| $d = -\lambda\,\phi_{unwrapped}/(4\pi)$ | vital signs | 1 rad = 0.99 mm at 24 GHz |
| IRR formula | I/Q imbalance | 0.5 dB/3° → 28 dB |
| $\mathcal L_{IF} = 4\sin^2(\pi f\tau)\mathcal L_{osc}$ | range correlation | ≈ $(2\pi f\tau)^2$ |
| $R_u = c/(2\Delta f)$ | FSK CW | 2.5 MHz → 60 m |
| Cosine effect $v\cos\theta$ | speed guns | 20° → reads 94 % |

## Worked examples

**Example 1 — Making an HB100 detect people.** Walking speed 1–1.5 m/s → 70–105 Hz Doppler at 10.525 GHz. The IF output (into ≈ 12 kΩ [1]) is microvolts for a person at 10 m. Build: AC-coupled low-noise op-amp chain with ~70–80 dB total gain [3] split in two stages (to avoid op-amp saturation by the DC offset), band-pass ~6–600 Hz, a 100 Hz notch if lamps are nearby, then an ADC (an MCU ADC at 1–2 kS/s is enough) and a 0.25 s FFT (4 Hz bins, 5.7 cm/s). Expect ~15–20 m on a person with a simple analogue detector [3]; FFT processing extends this ([radar-equation example A](radar-range-equation.md)). No direction information — the module is single-channel.

**Example 2 — Rail-exit and boost velocity of a rocket with a 24 GHz module.** Module at the pad pointing up the rail (cosine error negligible when the rocket flies along the beam axis). At 250 m/s: $f_d$ = 40.2 kHz → sample the IF at ≥ 96 kS/s real (a 192 kS/s audio ADC, or a Teensy-class MCU ADC) — with a mono module the sign is known anyway (the rocket recedes). 10 g boost → 16.1 kHz/s Doppler rate → FFT length ≤ 7.9 ms (127 Hz bins, 0.79 m/s resolution) — use a spectrogram with 8 ms windows and track the ridge. Detection range for σ = 0.01 m² (−20 dBsm, tail-on estimate; see [RCS](radar-cross-section.md)), SNR 13 dB: ≈ 23 m with the bare module and an assumed 20 dB effective NF at a 40 kHz IF, ≈ 72 m with ~10 dB lens gain on each antenna, ≈ 128 m with the lenses and a quieter IF (10 dB). Useful for rail-exit velocity and early boost (compare with the flight computer's accelerometer integration and GNSS velocity); for the whole flight you need a tracking radar ([DIY hardware](diy-radar-hardware.md)). Watch for spurious lines from pad vibration and the motor plume.

**Example 3 — Drone vs bird with micro-Doppler.** A 24 GHz I/Q radar sees a hovering target with ±12 kHz sidebands and 200 Hz periodic flashes → rotor (24 cm, 6000 rpm, 2 blades). A bird's wing-beat micro-Doppler is a few Hz to ~20 Hz of modulation with Doppler spreads of tens to hundreds of Hz — two to three orders of magnitude slower [4]. Sample at ≥ 25 kS/s complex and use 256-sample Hann windows (10 ms) for the spectrogram.

**Example 4 — Breathing monitor at 24 GHz.** Person at 1 m, chest motion 4 mm: phase swing 4.04 rad — a real-only module produces a heavily distorted waveform (and "null points" where sensitivity vanishes depending on $R_0$). With an I/Q module plus circle-fit DC removal and arctangent demodulation the displacement is recovered to the noise limit (≈ 50 µm at 26 dB per-sample SNR); a 1.2 Hz heartbeat line of 0.3 mm appears in the displacement spectrum.

## Practical notes
- **Monostatic CW with a circulator**: TX→RX leakage is set mainly by the antenna's reflection, not the circulator's isolation (33 dBm TX, antenna RL 15 dB → up to +21.5 dBm at the RX port); budget it like the bistatic leakage above and protect the mixer/LNA ([circulators](../06-rf-circuits/circulators-isolators.md)).
- **Legal operation in Singapore (IMDA TS SRD Issue 1 Rev 3, Sep 2023 [7]):** 10.50–10.55 GHz radio-determination devices ≤ 117 dBµV/m at 10 m (≈ +32 dBm EIRP equivalent; an HB100 at 20 dBm EIRP produces ≈ 105 dBµV/m at 10 m); 24.00–24.25 GHz ≤ 100 mW EIRP, but **radar guns are not allowed under the non-specific SRD provision** (sub-band 38c). Check with [19 regulations](../19-regulations-safety/singapore-imda-rules.md) before building a speed gun.
- **ESD:** the mixer diodes on the IF pin are the most fragile part; the InnoSenT note warns they fail before any external protection can act [3].
- **Unit-to-unit frequency spread:** DRO/LC modules vary by several MHz; two identical modules near each other beat against each other and produce false Doppler — detune them (IPM-165 frequency pushing via Vcc) or pulse them alternately.
- **Pulsed operation for battery life:** HB100 recommends 2 kHz / 2 % duty [1]; IPM-165 starts in < 100 ns, pulse ≥ 1 µs [3]. The IF then becomes a sampled signal: add a sample-and-hold or sample synchronously, and respect Nyquist on the pulse rate.
- **Mechanics:** mount the module rigidly, keep metal (screws, rails) out of the near field, and put a radome ≥ a few mm away (or at λ/2 thickness in its material) to avoid a strong leakage reflection.
- **Speed guns:** police bands are X (10.525 GHz), K (24.150 GHz) and Ka (33.4–36 GHz, ≈ 64 Hz per km/h at 34.7 GHz); they report the strongest or fastest Doppler line, and need a cosine-effect correction.
- **Ballistic chronographs** use the same principle at 24 GHz to measure bullet velocity along the bore line — the rocket-rail case is the same problem at lower speed.

## Common mistakes & misconceptions
- **"My HB100 sees nothing."** The IF is µV-level: you need 70–80 dB of low-noise gain, AC coupling, a band-pass, and a *moving* target. A stationary object gives only a DC shift; direction cannot be told with a single output.
- **"CW radar measures distance."** It measures only radial velocity. Range needs modulation (FSK, FMCW, pulses).
- **Using the small-angle approximation for vital signs at mm-wave.** At 24–77 GHz, millimetre motions are radians of phase.
- **Forgetting the factor of 2.** Two-way Doppler is $2v/\lambda$, not $v/\lambda$.
- **Ignoring Doppler rate.** A long FFT on an accelerating rocket smears the line into many bins and loses the coherent gain.
- **Sampling the IF with a 44.1 kHz sound card for a 40 kHz Doppler** — aliasing. Use ≥ 96 kS/s, or a higher-rate ADC.
- **Blaming the oscillator's phase noise at short range** when the real culprit is leakage AM noise, 1/f noise or vibration (range correlation suppresses phase noise by 60–130 dB at typical offsets and ranges).
- **Assuming I/Q modules have perfect quadrature** — calibrate the gain and phase imbalance or accept ~25–30 dB ghosts.

## How to simulate / verify
- `tools/verify/radar_cw_doppler.py` (~1 s, **ALL PASS**): exact vs approximate Doppler and the per-km/h table; I/Q direction and image-rejection formula; rotor micro-Doppler spectrogram (extent and flash rate); arctangent vital-sign demodulation vs noise limit; rocket Doppler/Doppler-rate/coherent-time and range estimates; range-correlation factor; FSK ranging simulation; cosine effect.
- Bench test: a trihedral on a pendulum or a fan with a metal-taped blade gives a known Doppler/micro-Doppler source ([RCS example 2](radar-cross-section.md)).
- Record I/Q with any audio interface (≥ 96 kS/s for fast targets) and plot `scipy.signal.spectrogram(I + 1j*Q, fs, return_onesided=False)`.

## Open questions / gaps
- Effective low-IF noise figures of HB100/CDM324 modules are not published; measure with a calibrated moving reflector (17-test-measurement).
- Plume and vibration signatures of a rocket at 10/24 GHz not characterised.
- Bird wing-beat micro-Doppler numbers are qualitative (Chen [4]); no Singapore-specific bird data.
- CDM324 is sold as an IPM-165 equivalent; the clone's actual EIRP and frequency tolerance were not verified.

## Sources
1. ST Engineering Electronics (AgilSense), "HB100 X-band Microwave Sensor Module" product data sheet V2.02, 2022: 10.525 GHz (10.52–10.53), EIRP 20 dBm typ, spurious −7.3 dBm, 5 V 30–40 mA, pulse 2 kHz/2 %, 80° × 40°, DRO + single balanced mixer, FCC 15.245, 12 kΩ load. https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6360/HB100.pdf (datasheet)
2. InnoSenT GmbH, IPM-165 data sheet v8.5 (2014): 24.050–24.250 GHz, output 16 dBm typ/20 max (EIRP), 9.5 dBi, 80° × 35°, split TX/RX antennas, mono output, 5 V 30 mA. https://media.digikey.com/pdf/Data%20Sheets/InnoSenT/IPM-165_V8.5_DS.pdf (datasheet)
3. W. Weidmann (InnoSenT), "Application Note III — IPM-165, a universal low cost K-band transceiver": 70–80 dB LF gain, 6–600 Hz for humans, 100 Hz lamp line, 44 Hz per km/h, 15–20 m on a person, pulse ≥ 1 µs, frequency pushing ≈ 6 MHz per 5 % Vcc, FSK ≈ 2.5 MHz, ESD warning, mono = no direction. https://www.innosent.de/fileadmin/media/dokumente/Downloads/Application_Note_III_-_web.pdf (app note)
4. V. C. Chen, F. Li, S.-S. Ho, H. Wechsler, "Micro-Doppler effect in radar: phenomenon, model, and simulation study," *IEEE Trans. AES*, vol. 42, no. 1, pp. 2–21, 2006; and V. C. Chen, *The Micro-Doppler Effect in Radar*, Artech House, 2011 — rotor/blade-flash model, human and bird micro-Doppler. (peer-reviewed / textbook)
5. A. Dürr, B. Schweizer, C. Waldschmidt, "Leakage phase noise mitigation for monostatic FMCW radar sensors using carrier transmission," IEEE IMS 2019 — range correlation $2\mathcal L(1-\cos2\pi f\tau)$, isolation ~30 dB at best. https://mwt-www.e-technik.uni-ulm.de/public/papers/2019/2019_IMS_Duerr_Leakage_Phase_Noise_Mitigation_For_Monostatic_FMCW_Radar_Sensors_Using_Carrier_Transmission.pdf (peer-reviewed)
6. M. C. Budge, M. P. Burt, "Range correlation effects in radars," *Proc. IEEE National Radar Conference*, 1993. (peer-reviewed; via [5])
7. IMDA, "Technical Specification — Short Range Devices" (IMDA TS SRD Issue 1 Rev 3), September 2023 (radar rows unchanged from the April 2023 printing), Table 1 sub-bands 37 and 38a–c. (regulation)
8. M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed., 2001 — CW/FM-CW and Doppler material (the chapter number given earlier, ch. 3, is the 2nd-edition layout; 3rd-ed. ch. 3 is "MTI and Pulse Doppler Radar" — W5-S18 check 2026-10-13, see 11/_sources T1). (textbook)
9. G. L. Charvat, *Small and Short-Range Radar Systems*, CRC Press, 2014 — CW Doppler and FMCW hobby-scale designs (the MIT coffee-can radar lineage). (textbook)
10. `tools/verify/radar_cw_doppler.py` — all computed values. (verification script)
