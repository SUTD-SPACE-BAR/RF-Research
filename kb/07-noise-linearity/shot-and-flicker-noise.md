---
title: Shot noise, flicker (1/f) noise and other non-thermal noise
domain: 07-noise-linearity
slug: shot-and-flicker-noise
tags: [shot-noise, flicker-noise, 1/f, corner-frequency, zero-IF, direct-conversion, mixer-noise, oscillator-noise, allan-deviation, popcorn-noise]
prerequisites: [thermal-noise-and-noise-temperature.md, ../00-math-foundations/probability-random-processes-and-psd.md]
related: [noise-figure-and-friis.md, phase-noise-and-jitter.md, ../05-analog-electronics/low-noise-analog-design.md, ../05-analog-electronics/bjt-fundamentals-small-signal.md, ../05-analog-electronics/fets-mosfet-jfet-gaas-gan.md, ../06-rf-circuits/mixers.md, ../06-rf-circuits/receiver-architectures.md, ../06-rf-circuits/vco-and-pll-synthesizers.md]
level: intermediate
confidence: high
last_updated: 2026-09-27
---

# Shot noise, flicker (1/f) noise and other non-thermal noise

## Questions this page answers
- What is shot noise and why is it $2qI$?
- Does a resistor carrying DC have shot noise?
- What is 1/f (flicker) noise, and what is a "flicker corner frequency"?
- Why do zero-IF (direct-conversion) receivers struggle with narrow channels like LoRa?
- Why does an oscillator's phase noise get steeper (1/f³) close to the carrier?
- Why does integrated 1/f noise never "settle", and what is the link to the bias-instability floor of an IMU?
- What are popcorn (burst) noise and generation–recombination noise?

## TL;DR
- **Shot noise** (Schottky 1918): a DC current $I$ made of independent charge crossings has white current noise $\overline{i_n^2} = 2qIB$ (one-sided): **17.9 pA/√Hz at 1 mA**, 0.57 pA/√Hz at 1 µA. A Poisson simulation reproduces $2qI$ to 0.1 % (`tools/verify/noise_shot_flicker.py`).
- It exists where carriers cross a barrier independently (diode and BJT junctions, photodiodes, tunnel junctions, gate leakage). Ordinary metallic resistors carrying DC show essentially only thermal noise (plus excess 1/f noise in some resistor types).
- Shot noise of a current $I$ through $R$ exceeds that resistor's thermal noise when $IR > 2kT/q$ ≈ **50 mV** (290 K).
- In a BJT, collector shot noise referred to the input equals the thermal noise of a resistor $1/(2g_m)$ = $r_e/2$: at $I_C$ = 5 mA, 0.21 nV/√Hz; base spreading resistance usually dominates.
- **Flicker (1/f) noise**: $S(f) \approx K/f^{\alpha}$, $\alpha\approx 1$. Equal noise power in every decade; below the **corner frequency** $f_c$ it exceeds the white floor. Typical corners (device- and geometry-dependent): SiGe/Si BJTs ~0.1–10 kHz; MOSFETs ~10 kHz–1 MHz (small short-channel devices worse); GaAs MESFET/HEMT often 1–100 MHz.
- Consequences: (i) **zero-IF receivers** see 1/f noise in-band — for a LoRa BW125 baseband (±62.5 kHz), a 100 kHz corner raises baseband noise by ~10 dB; (ii) **oscillators** up-convert device 1/f noise into the 1/f³ region of phase noise (Leeson's $f_c$); (iii) **precision sensors/clocks** have an Allan-deviation "flicker floor" (bias instability).

## Intuition (no math)
**Shot noise** is the graininess of charge. A current of 1 mA is $6.2\times10^{15}$ electrons per second; if they arrive independently, like raindrops on a roof, the count in any short interval fluctuates randomly (Poisson statistics). The average is the DC current; the fluctuation is shot noise. Its size grows with the square root of the current: more raindrops, bigger absolute fluctuation, smaller *relative* fluctuation. It needs independence: in a metal wire, electrons repel and push each other along, so the arrival of one makes the next more regular and the shot noise is suppressed; what is left is thermal noise.

**Flicker noise** is slow wandering. In semiconductors, carriers get trapped and released by defects (e.g. in the gate oxide of a MOSFET) with a huge spread of time constants — microseconds to hours. Each trap alone produces a "telegraph" signal with a Lorentzian spectrum; the sum of many traps with log-uniformly distributed time constants produces a spectrum close to $1/f$. Because it has equal power per decade, there is always more wandering if you wait longer: there is no averaging time that makes it go away. That is exactly the "bias instability" floor you see when you compute the Allan deviation of a gyro or an oscillator.

Why RF engineers care about a low-frequency effect: RF circuits are nonlinear in places (mixers, oscillators). Nonlinearity **moves** low-frequency noise up next to the carrier or down into a zero-IF baseband. A radio designer's two classic 1/f battlefields are direct-conversion receivers and oscillator phase noise.

## The math

### Level 1 — formulas
- Shot noise current (one-sided PSD): $S_i(f) = 2qI$ A²/Hz; $i_{n,\text{rms}} = \sqrt{2qIB}$. $q = 1.602\times10^{-19}$ C.
- Flicker noise: $S(f) = K/f$ (voltage or current), corner frequency $f_c$ defined by $K/f_c = S_\text{white}$, so $S(f) = S_\text{white}(1 + f_c/f)$.
- Integrated flicker noise between $f_1$ and $f_2$: $\int_{f_1}^{f_2} K/f\,df = K\ln(f_2/f_1)$ — the same for every decade (2.303 K per decade).
- MOSFET gate-referred flicker voltage (common model): $\overline{v_n^2} = \frac{K_f}{C_{ox}WL}\frac{1}{f}\Delta f$ — larger devices (bigger $WL$) are quieter at low frequency.
- BJT: base shot noise $2qI_B$, collector shot noise $2qI_C$; input-referred noise voltage from collector shot noise $e_n = \sqrt{2qI_C}/g_m = V_T\sqrt{2q/I_C}$, equivalent to the thermal noise of $1/(2g_m)$; plus $4kTr_b$ from base resistance.
- MOSFET channel thermal noise (for comparison, not shot noise): $\overline{i_d^2} = 4kT\gamma g_m\Delta f$, $\gamma = 2/3$ for long-channel devices, larger for short channels (see [05-analog-electronics/fets-mosfet-jfet-gaas-gan](../05-analog-electronics/fets-mosfet-jfet-gaas-gan.md)).

### Level 2 — derivations
**Shot noise from a Poisson impulse train (Campbell/Carson).** Model the current as $i(t) = \sum_k q\,\delta(t - t_k)$ with arrival times forming a Poisson process of rate $\lambda = I/q$. For a Poisson process the autocorrelation of the impulse train is $R(\tau) = \lambda^2q^2 + \lambda q^2\delta(\tau)$: the first term is the DC power $I^2$, the second is white. Its Fourier transform gives a two-sided PSD $I^2\delta(f) + \lambda q^2$; the fluctuating part is $\lambda q^2 = qI$ per hertz two-sided, or **$2qI$ one-sided**. If each carrier transit has a finite duration $\tau_t$ (a pulse $h(t)$ of area $q$), the PSD is multiplied by $|H(f)/q|^2$ and rolls off above $\sim1/\tau_t$ — far above RF for junction devices. The script generates Poisson counts at 2 MS/s for $I$ = 10 pA and measures 3.204×10⁻³⁰ A²/Hz against $2qI$ = 3.204×10⁻³⁰.

**Shot vs thermal crossover.** Set $2qI = 4kT/R$ ⇒ $IR = 2kT/q$ = 50.0 mV at 290 K. A forward-biased junction's small-signal resistance is $r_d = V_T/I$; its shot noise $2qI$ expressed as a voltage across $r_d$ is $2qI r_d^2 = 2kT r_d$ — *half* the thermal noise of a real resistor $r_d$. A junction is therefore "a half-noisy resistor", which is why a BJT's collector noise refers back as $1/(2g_m)$.

**Flicker spectra from traps (McWhorter-type argument).** One trap switching randomly with characteristic time $\tau$ gives a Lorentzian $S(f) \propto \tau/(1 + (2\pi f\tau)^2)$. If traps are distributed with $\tau$ uniformly distributed in $\ln\tau$ between $\tau_1$ and $\tau_2$ (as happens when trapping requires tunnelling a uniformly distributed distance into the oxide), integrating the Lorentzians gives $S(f) \propto 1/f$ for $1/(2\pi\tau_2) \ll f \ll 1/(2\pi\tau_1)$. The alternative Hooge model attributes 1/f to mobility fluctuation; both appear in real devices.

**Why 1/f noise has no stable mean.** The variance of a 1/f process measured over an observation time $T$ grows as $K\ln(T/\tau_\text{min})$ — logarithmically, but without bound. In Allan-variance terms, white noise gives $\sigma_y(\tau)\propto\tau^{-1/2}$ while flicker gives a flat $\sigma_y(\tau)$ = constant, the "flicker floor" (verified by synthesising 1/f noise: ADEV ≈ 0.31 from $\tau$ = 10 to 10 000 samples while white noise falls from 0.32 to 0.011).

### Level 3 — where each matters in RF, and limits
**Zero-IF / direct-conversion receivers.** The RF signal is mixed straight to 0 Hz, so the baseband occupies DC to BW/2. Any 1/f noise of the mixer switches, baseband amplifiers and filters lands in-band. For a baseband from $f_1$ to $f_2$ with white density $S_0$ and corner $f_c$:
$$\frac{N_\text{total}}{N_\text{white}} = 1 + \frac{f_c\ln(f_2/f_1)}{f_2 - f_1}.$$
For LoRa BW125 (baseband 100 Hz–62.5 kHz): $f_c$ = 10 kHz → +3.1 dB; 100 kHz → +10.5 dB; 1 MHz → +20.2 dB of baseband noise (`noise_shot_flicker.py` §5). How much of that shows up in the receiver NF depends on the RF gain before the baseband: with RF NF 3 dB, baseband NF 15 dB (white), and 20 dB of RF gain, a 100 kHz corner degrades the total NF from 3.6 to 7.4 dB; with 35 dB of RF gain the damage is only 0.2 dB. Mitigations: high RF/LNA gain, large baseband devices, passive (current-mode) mixers with no DC in the switches, chopping, or **low-IF** architectures that put the wanted signal a few hundred kHz away from DC. The SX126x datasheet specifies image attenuation (35 dB, 54 dB with IQ calibration) and an automatically applied IF offset in RX mode, consistent with a low-IF IQ architecture (datasheet [7]; architecture detail belongs to [15-lora-ism-radios/semtech-chip-family](../15-lora-ism-radios/semtech-chip-family.md)). Zero-IF is fine for wideband signals (LTE/5G, Wi-Fi) where the 1/f region is a tiny fraction of the channel and a few centre subcarriers can be left empty.

**DC offsets and even-order distortion** are zero-IF's other problems (LO self-mixing, IIP2) — see [nonlinearity-p1db-ip3-intermod](nonlinearity-p1db-ip3-intermod.md) and [06-rf-circuits/receiver-architectures](../06-rf-circuits/receiver-architectures.md).

**Mixers.** Active (Gilbert) mixers have DC bias in the switching pair, so their switches contribute 1/f noise at the IF (directly for zero-IF, and via the LO-switching "slope" mechanism). Passive FET-switch mixers carry little DC and have much lower 1/f noise, one reason they dominate modern zero-/low-IF receivers.

**Oscillators.** The active device's 1/f noise modulates the oscillator's phase (through bias-dependent capacitances and amplitude-to-phase conversion). Close to the carrier this appears as a $1/f^3$ slope in $\mathcal{L}(f)$ below the device's flicker corner — Leeson's $(1 + f_c/f_m)$ factor. The $1/f^3$ corner of the phase noise is *not necessarily equal* to the device's 1/f corner; it depends on the up-conversion mechanism (Hajimiri–Lee impulse sensitivity function theory relates it to the symmetry of the oscillation waveform). See [phase-noise-and-jitter](phase-noise-and-jitter.md).

**Baseband/instrumentation.** Op-amps specify $e_n$ at 1 kHz plus a 1/f corner (often 1–100 Hz for precision bipolar/JFET parts, 1–10 kHz for general CMOS). Chopper/auto-zero amplifiers remove 1/f at the cost of chopping artefacts. For Marcus's sensor front ends, the IMU "bias instability" figure is the flicker floor of the Allan deviation.

**Other non-thermal noise.**
- *Generation–recombination (g-r) noise*: a single trap level produces a Lorentzian spectrum (flat then $1/f^2$).
- *Popcorn/burst (random telegraph) noise*: discrete jumps between two levels from a single dominant trap, audible as "popcorn" in audio; a sign of contaminated or small-geometry devices.
- *Avalanche noise*: very large in reverse-breakdown diodes (Zener diodes above ~6 V break down by avalanche and are noisy — used deliberately in noise sources with ENR of 5–15 dB and more).
- *Partition noise*: random division of current between two electrodes (e.g. base/collector, or two anodes in a vacuum tube).
- *Excess (current) noise in resistors*: carbon composition and thick-film resistors carrying DC show 1/f noise specified as a "noise index" in dB (µV per volt per decade); thin-film/metal-foil resistors are much quieter.
- *Quantum and thermal limits in photodetectors*: photocurrent shot noise $2qI_\text{ph}$ versus the load resistor's $4kT/R$ — the same 50 mV crossover logic sets whether an optical receiver is shot- or thermal-noise limited.

**Limits of the $2qI$ law.** It fails when carriers are correlated (space-charge-limited vacuum tubes suppress it; metallic conductors suppress it almost entirely; ballistic nanostructures show a Fano factor between 0 and 1) and at frequencies comparable to the inverse transit time.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $i_n = \sqrt{2qI}$ | independent carrier crossings (junctions) | 1 µA: 0.57 pA/√Hz; 1 mA: 17.9 pA/√Hz; 10 mA: 56.6 pA/√Hz |
| shot > thermal when $IR > 2kT/q$ | same $R$ | 50 mV at 290 K |
| $e_{n,\text{BJT}} \approx \sqrt{4kT(r_b + 1/(2g_m))}$ | BJT, white region | 5 mA, $r_b$ = 5 Ω: 0.35 nV/√Hz |
| $S = S_0(1 + f_c/f)$ | flicker + white | CMOS $f_c$ 10 kHz–1 MHz; BJT 0.1–10 kHz; GaAs 1–100 MHz |
| $\int K/f = K\ln(f_2/f_1)$ | 1/f region | 2.303 K per decade |
| $\overline{v_n^2} \propto 1/(C_{ox}WLf)$ | MOSFET flicker | ×4 area → −6 dB flicker |
| Zero-IF penalty $1 + f_c\ln(f_2/f_1)/(f_2-f_1)$ | baseband noise | LoRa BW125, $f_c$ = 100 kHz: +10.5 dB (baseband) |

## Worked examples
**1 — Diode detector noise.** A Schottky detector biased at 10 µA: $i_n = \sqrt{2\cdot1.6\times10^{-19}\cdot10^{-5}} = 1.8$ pA/√Hz; its video resistance $V_T/I \approx 2.6$ kΩ gives a noise voltage of 4.7 nV/√Hz — half the $4kT$ of a 2.6 kΩ resistor in power terms (6.5 nV/√Hz for the resistor). Zero-bias detectors avoid DC shot noise but still have the thermal noise of their video resistance.

**2 — BJT LNA input noise.** $I_C$ = 5 mA ($g_m$ = 193 mS at 300 K): collector-shot contribution 0.207 nV/√Hz (= thermal noise of 2.6 Ω); with $r_b$ = 20 Ω the total is 0.61 nV/√Hz — the base resistance dominates. Raising $I_C$ to 20 mA barely helps (0.59 nV/√Hz) because $r_b$ still dominates; this is why RF BJTs/HBTs are designed for low $r_b$ and why noise optimisation also involves emitter area (script §3).

**3 — Would a zero-IF LoRa receiver work?** Baseband ±62.5 kHz, CMOS baseband with 100 kHz flicker corner: baseband noise ×11.3 (+10.5 dB). If the front end provides 20 dB of gain at NF 3 dB and the baseband has 15 dB (white) NF, the receiver NF becomes 7.4 dB instead of 3.6 dB — a 3.8 dB sensitivity loss, plus DC-offset problems at the very centre of a chirp. A low-IF design avoids this, which is why narrowband sub-GHz transceivers commonly use low-IF.

**4 — Choosing a reference oscillator for a PLL.** A TCXO whose phase noise has a $1/f^3$ region below 100 Hz offset will set the close-in phase noise of any PLL locked to it (multiplied by $20\log_{10}N$ — see [phase-noise-and-jitter](phase-noise-and-jitter.md)). Close-in noise matters for narrowband FSK and for LoRa at the narrowest bandwidths (7.8/10.4 kHz), where Semtech recommends a TCXO for frequency stability anyway.

## Practical notes
- **Measure 1/f corners with a low-noise preamp and an FFT analyzer or a sound card** (for audio-range corners); for RF devices use a phase-noise analyzer to see up-converted flicker.
- **Choose resistors for bias networks carrying DC in low-frequency signal paths** by noise index: thin-film ≪ thick-film < carbon composition.
- **Layout and bias:** larger-area input devices, higher bias current and passive mixers reduce 1/f contributions; supply noise and ground bounce at low frequency are often mistaken for device 1/f noise.
- **For sensors (IMU/baro on the flight computer):** long averaging does not remove flicker; model it as bias instability (a random-walk-like drift over mission timescales) in the estimator rather than expecting averaging to help. (Cross-reference: the team's sensor-calibration methods.)

## Common mistakes & misconceptions
- **"A resistor with DC through it has shot noise $2qI$."** Metallic resistors show thermal noise (plus possible excess 1/f noise); $2qI$ applies to barrier-crossing currents.
- **Using $2qI$ with the two-sided convention inconsistently.** $2qI$ is one-sided (0 to ∞); the two-sided density is $qI$.
- **"Averaging longer always reduces noise."** Only for white noise. For 1/f noise the Allan deviation is flat; for random-walk noise it grows.
- **Assuming the oscillator 1/f³ corner equals the transistor's 1/f corner.** It depends on the up-conversion mechanism; it can be much lower (symmetric waveforms) or higher.
- **Ignoring 1/f for "RF" designs.** Any mixer, detector, AGC loop, PLL loop filter or zero-IF baseband turns it into an RF problem.
- **Believing GaAs is always quietest.** GaAs/HEMT devices have excellent RF noise figures but poor (high-corner) 1/f noise, making them poor choices for low-phase-noise oscillators compared with SiGe/Si BJTs.

## How to simulate / verify
- `tools/verify/noise_shot_flicker.py` — Poisson simulation of shot noise vs $2qI$; shot/thermal crossover; BJT $e_n$; per-decade integration of 1/f; zero-IF penalty calculator; synthesis of 1/f noise and Allan deviation.
- SPICE: diode/BJT models include shot noise automatically and flicker noise through the `KF`/`AF` parameters; a `.noise` analysis from 1 Hz to 10 MHz shows the corner. Many vendor models omit or misstate `KF` — treat simulated corners with caution.
- Phase-noise simulators (harmonic-balance / periodic steady-state noise) are needed to predict up-conversion of 1/f noise in oscillators and mixers ([16-simulation-tools/rf-circuit-simulators-harmonic-balance](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)).

## Open questions / gaps
- Typical flicker-corner ranges above are textbook-level generalities (Razavi, Lee); device-specific values should be taken from measured data in [18-components-parts](../18-components-parts/lna-pa-gain-block-mmics.md). They vary by more than an order of magnitude with geometry and process.
- The internal architecture of SX126x (exact IF) is inferred from datasheet specs, not confirmed by Semtech documentation — domain 15 should confirm.

## Sources
1. W. Schottky, "Über spontane Stromschwankungen in verschiedenen Elektrizitätsleitern," *Annalen der Physik* 362(23), 541–567 (1918). (peer-reviewed) — shot effect.
2. B. Razavi, *RF Microelectronics*, 2nd ed., 2011, §2.3 (noise in devices, flicker noise), §4.2–4.3 (direct-conversion receivers: flicker noise, DC offsets). (textbook)
3. T. H. Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., 2004, ch. 11 (noise: shot, flicker, popcorn; MOSFET noise models) and ch. 18 (phase noise, Hajimiri–Lee model). (textbook)
4. A. L. McWhorter, "1/f noise and germanium surface properties," in *Semiconductor Surface Physics*, Univ. Pennsylvania Press, 1957. (peer-reviewed/monograph) — trap-distribution model of 1/f.
5. F. N. Hooge, "1/f noise," *Physica B+C* 83(1), 14–23 (1976). (peer-reviewed) — mobility-fluctuation model.
6. D. W. Allan, "Statistics of atomic frequency standards," *Proc. IEEE* 54(2), 221–230 (1966). (peer-reviewed) — Allan variance; flicker floor.
7. Semtech, *SX1261/2 Data Sheet*, Rev 1.2 (2019) Table 3-8 (image attenuation 35/54 dB) and §13 (SetRfFrequency IF offset in RX). (datasheet)
8. `tools/verify/noise_shot_flicker.py` (this KB).
