---
title: Active filters — Sallen-Key, MFB, state-variable/biquads, design tables, sensitivity, op-amp requirements, anti-alias design
domain: 05-analog-electronics
slug: active-filters
tags: [active-filter, sallen-key, multiple-feedback, mfb, biquad, state-variable, tow-thomas, butterworth, bessel, chebyshev, q-factor, sensitivity, monte-carlo, gbw-requirement, anti-alias, adc, stopband-feedthrough]
prerequisites:
  - op-amps-real-limitations.md
  - ../01-circuit-theory/passive-filter-design-prototypes.md
  - ../00-math-foundations/laplace-transfer-functions-bode.md
related:
  - data-converters-adc-dac.md
  - low-noise-analog-design.md
  - analog-signal-conditioning.md
  - feedback-and-stability.md
  - ../14-sdr-dsp/digital-filters-fir-iir.md
  - ../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Active filters — Sallen-Key, MFB, state-variable/biquads, design tables, sensitivity, op-amp requirements, anti-alias design

## Questions this page answers
- How do I design a 2nd-order low-pass with an op-amp, and what sets its $f_0$ and Q?
- Sallen-Key or multiple-feedback (MFB) — which should I use?
- How do I build a 4th-, 5th- or 6th-order Butterworth, Bessel or Chebyshev filter from 2nd-order sections?
- How sensitive is my filter to 1 % resistors and 5 % capacitors?
- How fast must the op-amp be (GBW) for a given filter?
- Why does my Sallen-Key low-pass "stop filtering" at high frequency?
- What order of anti-alias filter do I need in front of an ADC?
- When should I use a state-variable or biquad filter?

## TL;DR
- Every even-order all-pole filter = cascade of 2nd-order sections $H = K\omega_0^2/(s^2 + (\omega_0/Q)s + \omega_0^2)$ (+ one real pole for odd orders). Order sections from **low Q to high Q** along the chain (headroom).
- **Unity-gain Sallen-Key LP** (R1, R2 in series; C1 from their junction to the output; C2 to ground): $\omega_0 = 1/\sqrt{R_1R_2C_1C_2}$, $Q = \sqrt{R_1R_2C_1C_2}/[C_2(R_1+R_2)]$. Equal R → $C_1/C_2 = 4Q^2$ (sympy-derived, `tools/verify/analog_active_filters.py` §1).
- **MFB LP** (R1 in, R2 feedback, R3 to inverting input, C1 to ground, C2 feedback): gain $-R_2/R_1$, $\omega_0^2 = 1/(R_2R_3C_1C_2)$, $\omega_0/Q = (1/C_1)(1/R_1+1/R_2+1/R_3)$. Inverting; all-R-equal → $C_1/C_2 = 9Q^2$.
- **Design tables** (per-section $f_0/f_c$ and Q) for Butterworth (all $f_0 = f_c$; Q = 0.707 | 0.541, 1.307 | 0.618, 1.618 | 0.518, 0.707, 1.932), Bessel and Chebyshev are in the table below (computed from scipy prototypes, §2).
- **Sensitivity (Monte Carlo, 1 % R, 5 % C):** unity-gain SK and MFB: σ($f_0$) ≈ 3.6 %, σ(Q) ≈ 3.6 % at *any* Q. The equal-component SK (gain K = 3 − 1/Q) is fine at Q = 0.707 but at Q = 2 42 % of builds are > 20 % off in Q, and at Q = 5 76 % are off or unstable (§4) — avoid it for Q > 1.
- **Op-amp GBW:** a single-pole op-amp with GBW = 10 × $f_0$ lowers a Q = 5 section's peak frequency by 30 % and adds 1 dB of peaking; GBW = 100 × $f_0$ still shifts it 5 % (§7). Rule: **GBW ≥ 100 × G × f₀** for high-Q sections (≥ 20–50× for Q ≲ 1).
- **SK stop-band rebound:** at high frequency C1 feeds the input straight to the op-amp output, whose impedance rises with frequency — with a 1 MHz op-amp ($R_o$ = 100 Ω) a 1 kHz SK low-pass bottoms out at ≈ −40 dB above ~1 MHz instead of −120 dB; an MFB with the same op-amp reaches −103 dB at 1 MHz (§5, §7). Use MFB (or a passive RC after the SK) when stop-band depth at far-out frequencies matters (RF pickup, SMPS noise).
- **Anti-alias order:** Butterworth attenuation at $f_s - f_{pass}$ is $10\log[1+(f_{stop}/f_c)^{2n}]$; 12-bit (74 dB) with $f_s$ = 10 kHz and 1 kHz passband needs n = 4 (76 dB at 9 kHz) (§6). Oversampling + digital decimation usually beats a steep analog filter.

## Intuition (no math)
A capacitor is a frequency-dependent resistor: open at DC, short at high frequency. An RC gives one pole: 6 dB/octave roll-off with a gentle knee. To get a sharp knee (a *resonance*), you need two reactive elements and some gain: an active filter uses the op-amp's feedback to create the equivalent of an LC resonance without inductors. In the Sallen-Key circuit the op-amp output drives a capacitor back into the middle of the input RC ladder: near the cutoff frequency that positive feedback props the response up, sharpening the knee. The ratio of the two capacitors sets how much it is propped up — the Q. In the MFB circuit the op-amp is an inverting integrator whose output feeds back through both a resistor and a capacitor, doing the same with negative feedback.

Higher-order filters are built by cascading sections, each tuned to one pair of poles of the chosen response (Butterworth: flattest; Bessel: best step response; Chebyshev: sharpest, with ripple). A filter "family" is just a recipe for those pole positions.

The op-amp is not perfect: it needs spare loop gain at the section's frequency to behave ideally, and above its own bandwidth the Sallen-Key's feedback capacitor becomes a direct path from input to output.

## The math

### Level 1 — the standard 2nd-order sections

Normalised low-pass biquad: $H(s) = \dfrac{K\omega_0^2}{s^2 + \frac{\omega_0}{Q}s + \omega_0^2}$; $|H(j\omega_0)| = KQ$; peaking for Q > 0.707 with maximum $KQ/\sqrt{1-1/4Q^2}$.

**Unity-gain Sallen-Key low-pass:**
$$H(s) = \frac{1}{s^2R_1R_2C_1C_2 + sC_2(R_1+R_2) + 1},\quad \omega_0 = \frac{1}{\sqrt{R_1R_2C_1C_2}},\quad Q = \frac{\sqrt{R_1R_2C_1C_2}}{C_2(R_1+R_2)}.$$
Equal resistors R: $Q = \tfrac12\sqrt{C_1/C_2}$ → $C_2 = 1/(2Q\omega_0R)$, $C_1 = 4Q^2C_2$.

**Sallen-Key with gain K** ($K = 1 + R_b/R_a$): denominator $s^2R_1R_2C_1C_2 + s[C_2(R_1+R_2) + R_1C_1(1-K)] + 1$; equal R and C → $Q = 1/(3-K)$.

**MFB low-pass:**
$$H(s) = \frac{-R_2/R_1}{s^2R_2R_3C_1C_2 + sC_2\left(R_2+R_3+\frac{R_2R_3}{R_1}\right) + 1},\quad \omega_0^2 = \frac{1}{R_2R_3C_1C_2},\quad \frac{\omega_0}{Q} = \frac{1}{C_1}\left(\frac{1}{R_1}+\frac{1}{R_2}+\frac{1}{R_3}\right).$$
(Both derived by nodal analysis in sympy, §1.) High-pass versions swap R ↔ C; MFB band-pass uses one capacitor in each of the two positions.

**State-variable / Tow–Thomas biquads:** two integrators and a summer (or lossy integrator) in a loop give simultaneous LP, BP and HP outputs with $\omega_0 = 1/RC$ and Q set by one resistor ratio — independently tunable, low sensitivity, three op-amps. Good for tunable filters and high-Q (Q > 10) band-pass sections; ICs (universal active filters) package them.

### Level 2 — design, derivations and sensitivities

**Design tables** (normalised so that the filter's cutoff $f_c$ = 1; Butterworth and Bessel at −3 dB, Chebyshev at the ripple-band edge; computed from `scipy` prototypes, §2):

| Response | n | Section $f_0/f_c$ (Q) | Real pole $f/f_c$ |
|---|---|---|---|
| Butterworth | 2 | 1.000 (0.7071) | — |
| | 3 | 1.000 (1.0000) | 1.000 |
| | 4 | 1.000 (0.5412); 1.000 (1.3066) | — |
| | 5 | 1.000 (0.6180); 1.000 (1.6180) | 1.000 |
| | 6 | 1.000 (0.5176); 1.000 (0.7071); 1.000 (1.9319) | — |
| Bessel (−3 dB) | 2 | 1.272 (0.5774) | — |
| | 3 | 1.448 (0.6910) | 1.323 |
| | 4 | 1.430 (0.5219); 1.603 (0.8055) | — |
| | 5 | 1.556 (0.5635); 1.755 (0.9165) | 1.502 |
| | 6 | 1.604 (0.5103); 1.689 (0.6112); 1.905 (1.0233) | — |
| Chebyshev 0.5 dB | 2 | 1.231 (0.8637) | — |
| | 3 | 1.069 (1.7062) | 0.627 |
| | 4 | 0.597 (0.7051); 1.031 (2.9406) | — |
| | 5 | 0.691 (1.1778); 1.018 (4.5450) | 0.362 |
| | 6 | 0.396 (0.6836); 0.768 (1.8104); 1.011 (6.5128) | — |
| Chebyshev 1 dB | 2 | 1.050 (0.9565) | — |
| | 4 | 0.529 (0.7845); 0.993 (3.5590) | — |
| | 6 | 0.353 (0.7609); 0.747 (2.1980); 0.995 (8.0037) | — |

These agree with standard published tables (e.g. TI's *Active Low-Pass Filter Design* and Williams & Taylor) [1][2]. Note how Chebyshev Q grows quickly with order — sensitivity and op-amp demands grow with it.

**Sensitivity.** The classical sensitivity $S_x^Q = (\partial Q/Q)/(\partial x/x)$: for unity-gain SK, $|S_{R,C}^Q| = 1/2$ for each element and $S^{\omega_0} = -1/2$, independent of Q; the equal-component SK has $S_K^Q = KQ = 3Q - 1$, which explodes at high Q. Monte Carlo with 1 % resistors and 5 % capacitors (20 000 trials, §4):

| Topology | Q = 0.707 | Q = 2 | Q = 5 |
|---|---|---|---|
| Unity-gain SK, equal R: σ(Q) | 3.6 % | 3.5 % | 3.5 % |
| Equal-component SK (K = 3 − 1/Q): robust σ(Q) / % builds > 20 % off or unstable | 6.4 % / 0.5 % | 25 % / 42 % | 55 % / 76 % |
| MFB (gain −1): σ(Q) | 3.6 % | 3.6 % | 3.6 % |

σ($f_0$) ≈ 3.6 % in all cases — dominated by the 5 % capacitors ($\sqrt{2}\times5\%/2$). Use C0G/NP0 1–2 % capacitors when $f_0$ accuracy matters; X7R has voltage and temperature coefficients (and microphonics) that make it unsuitable for filter capacitors in signal paths.

**Finite op-amp GBW.** Modelling the op-amp as an integrator $A(s) = \omega_t/s$ (§5, §7):
- Q = 0.707 section: GBW = 10 × $f_0$ → $f_{-3dB}$ 1.6 % low; 3 × $f_0$ → 11 % low and 0.3 dB peaking.
- Q = 1.307: GBW 10 × $f_0$ → peak 0.7 dB higher, peak frequency 9 % low.
- Q = 5: GBW 100 × $f_0$ → peak frequency 5 % low, +0.4 dB; 10 × $f_0$ → 30 % low, +1.1 dB.
Hence the rule GBW ≥ 100 × G × $f_0$ for high-Q sections (common in app notes [1][3]) and more relaxed (20–50×) for low-Q ones. Also check slew rate ($SR > 2\pi f_{max}V_{pk}$) and, for SK with gain, the op-amp's noise gain.

**Stop-band rebound (derivation sketch).** Well above $f_0$, the SK's C1 is a short from node a to the op-amp output, and C2 shorts node m to ground; the input current through R1 now flows into the op-amp output. The output voltage is that current times the op-amp's *closed-loop output impedance*, which rises with frequency as loop gain falls ($Z_{out} \approx R_o\,f/GBW$ for a follower until it reaches $R_o$). So the response flattens at roughly $Z_{out}/R_1$: for $R_o$ = 100 Ω, R1 = 10 kΩ → −40 dB — exactly the §5 floor. In the MFB the input side is shunted to ground by C1 and the output is inside the feedback loop, so no such path exists (−103 dB at 1 MHz vs −43 dB, §7) [3]. Fixes: choose MFB, add a passive RC pole after the SK, or use an op-amp with much higher GBW and lower $R_o$.

**Anti-alias order selection.** For a Butterworth with cutoff $f_c$ (at the passband edge), attenuation at $f$ is $A(f) = 10\log_{10}[1+(f/f_c)^{2n}]$ ≈ $20n\log_{10}(f/f_c)$ dB. Aliases land in the passband from inputs at $f_s - f_{pass}$ and above; for an N-bit converter aim for $A(f_s - f_{pass}) \ge 6.02N+1.76$ dB (or at least below the expected interference level, which is often the real criterion). Example (§6): $f_s$ = 10 kHz, 1 kHz passband, 12-bit → 74 dB at 9 kHz → n = 4 (76.3 dB). Oversampling ×8 ($f_s$ = 80 kHz) would need only 74 dB at 79 kHz → n = 2 (75.8 dB), with the rest done in DSP (→ [data converters](data-converters-adc-dac.md), [multirate DSP](../14-sdr-dsp/multirate-dsp-decimation-cic.md)).

### Level 3 — choices and limits
- **Bessel vs Butterworth for measurement data:** Bessel's near-linear phase gives almost no step overshoot (useful for accelerometer/pressure transients in flight logs); Butterworth overshoots ~11 % (4th order) but is flatter. Chebyshev rings more.
- **Dynamic range:** a high-Q section has internal gain ≈ Q at $f_0$; put it last, and check for clipping at the internal nodes (SK: op-amp output = filter output; MFB and state-variable internal nodes can exceed the output).
- **Noise:** resistor noise in an active filter is shaped by the filter; larger R means more thermal noise but smaller (cheaper, more accurate) C. For low noise, scale impedances down to 1–5 kΩ and let the op-amp's $e_n$ dominate (→ [low-noise design](low-noise-analog-design.md)).
- **Switched-capacitor filters** (clock-tunable, steep elliptic responses in one IC) sample their input — they need their own continuous-time anti-alias filter and leak clock feedthrough.
- **Beyond ~10 MHz** active RC filters become impractical (op-amp GBW); use passive LC (→ [passive prototypes](../01-circuit-theory/passive-filter-design-prototypes.md), [RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)).

## Design equations & rules of thumb

| Quantity | Equation | Notes |
|---|---|---|
| SK unity gain | $\omega_0 = 1/\sqrt{R_1R_2C_1C_2}$, $Q = \sqrt{R_1R_2C_1C_2}/[C_2(R_1+R_2)]$ | C1 = feedback cap |
| SK equal R | $C_1/C_2 = 4Q^2$, $C_2 = 1/(2Q\omega_0R)$ | spread 1.7:1 at Q = 0.65, 100:1 at Q = 5 |
| SK equal component | $Q = 1/(3-K)$ | avoid for Q > 1 |
| MFB LP | $\omega_0^2 = 1/(R_2R_3C_1C_2)$, $\omega_0/Q = (1/C_1)\sum 1/R_i$, gain $-R_2/R_1$ | inverting |
| MFB all-R-equal | $C_1/C_2 = 9Q^2$ | — |
| Section order | low Q → high Q along the chain | headroom |
| Op-amp GBW | ≥ 100 × G × $f_0$ (high Q); 20–50× (Q ≲ 1) | §7 |
| Slew rate | ≥ $2\pi f_{max}V_{pk}$ | — |
| Butterworth attenuation | $10\log[1+(f/f_c)^{2n}]$ | ≈ 20n dB/decade |
| AAF requirement | $A(f_s - f_{pass}) \ge 6.02N + 1.76$ dB | or interference-based |
| SK stop-band floor | ≈ $Z_{out,op-amp}(f)/R_1$ | MFB avoids it |
| Capacitor dielectric | C0G/NP0 (or film) | never X7R in filter paths |

## Worked examples

### 1. 4th-order Butterworth 1 kHz anti-alias filter (two unity-gain SK sections)
Sections Q = 0.5412 and 1.3066, both $f_0$ = 1 kHz. With R = 10 kΩ throughout (§3):
- Section 1: C1 = 17.23 nF, C2 = 14.70 nF (E12: 18 nF, 15 nF).
- Section 2: C1 = 41.59 nF, C2 = 6.09 nF (E12: 39 nF, 5.6 nF).
Exact values reproduce the ideal Butterworth to 0.001 dB (−3.010 dB at 1 kHz, −24.1 at 2 kHz, −80.0 at 10 kHz). With the E12 capacitors: −2.62 dB at 1 kHz and −79.2 dB at 10 kHz — use E24/E96 C0G values or trim R to recover the corner. Op-amp: GBW ≥ 100 × 1 kHz × 1 → ≥ 100 kHz with margin; a 1 MHz CMOS RRIO part (MCP6002 class) is adequate; for the far stop band add an RC after the last section.

### 2. Choosing the order for a 12-bit ADC at 10 kSa/s
(§6) 1 kHz passband → n = 4 Butterworth. Alternative: sample at 80 kSa/s with a 2nd-order analog filter and decimate by 8 digitally — cheaper analog, same alias protection, better phase.

### 3. Anti-alias for an ESP32/Teensy ADC reading a slow sensor
For slow signals (battery voltage, pyro-current sense, thermistors) a single RC at the ADC pin (e.g. 1 kΩ + 100 nF, $f_c$ = 1.6 kHz) plus digital averaging is usually right; the capacitor also supplies the ADC's sampling charge (→ [data converters](data-converters-adc-dac.md)). Reserve active filters for signals with real content near Nyquist.

### 4. Why the SK filter let RF through
A 1 kHz SK low-pass on a flight computer shows 433 MHz-packet-synchronous glitches. The SK floor (≈ $Z_{out}/R_1$) is ≈ −40 dB at high frequency, and the op-amp itself rectifies RF (→ [op-amps](op-amps-real-limitations.md)). Fix: an RC or ferrite + capacitor ahead of the op-amp input, or an MFB topology.

## Practical notes
- **Component choice:** C0G/NP0 up to ~100 nF (0805/1206), film above; thin-film 0.1–1 % resistors; keep impedances 1–100 kΩ for general work.
- **Layout:** keep the high-impedance nodes (SK node m, MFB inverting input) short and guarded; ground-plane under filter.
- **Tools:** TI's filter-design tool and ADI's filter wizard generate SK/MFB values including op-amp limitations; always verify with SPICE using a real op-amp macromodel.
- **Testing:** sweep with a signal generator + scope or a USB scope's Bode mode; for deep stop-band measurements use a spectrum analyser with a tracking generator.

## Common mistakes & misconceptions
- **Cascading identical 2nd-order Butterworth sections to get a 4th-order Butterworth.** Two Q = 0.707 sections give a −6 dB, droopy corner; each section needs its own Q from the table.
- **Using the equal-component SK at high Q.** Hypersensitive to component tolerances (Monte Carlo above).
- **Forgetting that a Bessel/Chebyshev table is normalised differently** (−3 dB vs ripple edge).
- **Ignoring op-amp GBW at the section's Q** — high-Q sections shift and peak.
- **Trusting an SK filter's stop band at MHz frequencies.**
- **X7R capacitors in filter paths** — capacitance changes with DC bias (tens of %) and temperature; distortion and microphonics.
- **Anti-alias filter placed after a gain stage that already clipped or rectified an out-of-band signal.** Filter first, or make sure early stages are linear at the interference level.

## How to simulate / verify
- **Python:** `tools/verify/analog_active_filters.py` — sympy derivations of SK and MFB; the design tables above; worked 4th-order Butterworth vs ideal (also with E12 values); Monte Carlo sensitivities; finite-GBW behaviour (single-pole op-amp model); SK vs MFB stop-band with op-amp output impedance; AAF order selection; ngspice check of an SK section (0.0000 dB error vs analytic).
- **ngspice netlist of one SK section (ideal op-amp as a high-gain VCVS):**
```spice
* unity-gain Sallen-Key low-pass section (Butterworth 4th-order section 1), ideal op-amp as VCVS
Vin in 0 AC 1
R1 in a 10k
R2 a m 10k
C1 a out 17.227n
C2 m 0 14.704n
E1 out 0 m out 1e6
.ac dec 100 10 100k
.end
```
  Replace `E1` with a vendor op-amp macromodel to see finite-GBW effects and the stop-band floor.
- **scipy:** `signal.butter/bessel/cheby1(..., analog=True, output='sos')` gives the section parameters directly; `signal.freqs` evaluates responses.

## Open questions / gaps
- Band-pass/notch active filter design tables (MFB band-pass, twin-T, state-variable Q tuning) summarised only; a dedicated worked example would help.
- Group-delay tables for Bessel filters not reproduced.
- The GBW rule "≥ 100 × G × f₀" appears in vendor notes; here it is supported by simulation of a single-pole op-amp model, not by a vendor table.

## Sources
1. Texas Instruments (T. Kugelstadt), *Active Filter Design Techniques*, ch. 16 of *Op Amps for Everyone* (SLOD006B), 2002; and *Active Low-Pass Filter Design*, SLOA049. https://www.ti.com/lit/an/slod006b/slod006b.pdf — SK/MFB equations, coefficient tables, op-amp requirements. (app note)
2. A. B. Williams, F. J. Taylor, *Electronic Filter Design Handbook*, 4th ed., McGraw-Hill 2006 — normalised pole tables (Butterworth, Bessel, Chebyshev), active realisations, sensitivity. (textbook)
3. J. Karki, *Analysis of the Sallen-Key Architecture*, Texas Instruments SLOA024B, 2002 — SK equations, sensitivity, high-frequency feedthrough (via output impedance). https://www.ti.com/lit/an/sloa024b/sloa024b.pdf (app note; cited for the known high-frequency behaviour, reproduced here by simulation)
4. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015 — ch. 6 (active filters, SK/MFB/state-variable, filter tables). (textbook)
5. R. Schaumann, M. E. Van Valkenburg, *Design of Analog Filters*, Oxford 2001 — biquads, sensitivity theory. (textbook)
6. SciPy signal-processing documentation (buttap, besselap, cheb1ap) — prototypes used to compute the tables. https://docs.scipy.org/doc/scipy/reference/signal.html (software documentation)
