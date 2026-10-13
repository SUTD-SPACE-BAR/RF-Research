---
title: Low-noise analog design — the en–in model, optimum source resistance, noise figure of op-amp circuits, resistor and 1/f noise, noise bandwidth
domain: 05-analog-electronics
slug: low-noise-analog-design
tags: [noise, en-in-model, voltage-noise, current-noise, optimum-source-resistance, noise-figure, noise-matching, transformer, paralleling, resistor-noise, excess-noise, noise-index, flicker-noise, ktc-noise, noise-bandwidth, enbw, tia-noise, preamp]
prerequisites:
  - op-amps-real-limitations.md
  - bjt-fundamentals-small-signal.md
  - fets-mosfet-jfet-gaas-gan.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
related:
  - analog-signal-conditioning.md
  - data-converters-adc-dac.md
  - active-filters.md
  - ../07-noise-linearity/noise-figure-and-friis.md
  - ../07-noise-linearity/shot-and-flicker-noise.md
  - ../06-rf-circuits/lna-design.md
  - ../04-real-components-hf/resistors-at-rf.md
  - ../17-test-measurement/noise-figure-measurement.md
level: mixed
confidence: high
last_updated: 2026-10-02
---

# Low-noise analog design — the en–in model, optimum source resistance, noise figure of op-amp circuits, resistor and 1/f noise, noise bandwidth

## Questions this page answers
- How do I predict the noise of an amplifier from its $e_n$ and $i_n$ and the source resistance?
- What is the optimum source resistance, and can I "noise-match" by adding a resistor? (No — why?)
- What noise figure does an op-amp give with a 50 Ω source, and how do transformers or paralleled devices improve it?
- Why do my thick-film resistors make low-frequency noise when there is DC across them?
- What is kT/C noise and why does it limit sampling circuits?
- What is noise bandwidth and how do I convert a filter's −3 dB bandwidth into it?
- Why is a photodiode transimpedance amplifier's noise dominated by the op-amp's voltage noise, not the feedback resistor?
- Which amplifier (bipolar, JFET, CMOS) should I use for a 50 Ω, 1 kΩ, 100 kΩ or 10 MΩ source?

## TL;DR
- Model any amplifier as noiseless with a voltage-noise source $e_n$ in series and a current-noise source $i_n$ in parallel at its input. With a source resistance $R_s$: total input noise $e_{ni}^2 = e_n^2 + i_n^2R_s^2 + 4kTR_s$ (uncorrelated).
- **Noise factor** $F = 1 + (e_n^2 + i_n^2R_s^2)/(4kT_0R_s)$; minimised at $R_{opt} = e_n/i_n$ with $F_{min} = 1 + e_ni_n/(2kT_0)$ (correlation C shifts it to $1+e_ni_n(1+C)/2kT_0$). Verified by brute force in `tools/verify/analog_noise.py` §1.
- OPA1612 (1.1 nV/√Hz, 1.7 pA/√Hz): $R_{opt}$ = 647 Ω, NF$_{min}$ 0.91 dB; at 50 Ω NF = 4.0 dB; at 1 MΩ 22.6 dB. BF862 JFET: $R_{opt}$ ≈ 400 kΩ, 2.6 dB at 50 Ω but ≈ 0 dB from 1 kΩ up. MCP6002 CMOS: $R_{opt}$ ≈ 47 MΩ, 30 dB at 50 Ω (§2).
- **Change the source, not the resistor:** a lossless transformer with turns ratio $\sqrt{R_{opt}/R_s}$ (3.6:1 for 50 Ω → 647 Ω) takes the OPA1612 from 4.0 to 0.91 dB; paralleling N devices divides $R_{opt}$ by N (8 × OPA1612 → 1.0 dB at 50 Ω) (§2–3). Adding series or shunt resistance always adds noise.
- **Resistors:** thermal noise $\sqrt{4kTR}$ = 4.00 nV/√Hz per √kΩ at $T_0$ = 290 K (4.07 at 300 K), independent of type. *Excess* (current) noise is 1/f, proportional to DC voltage across the resistor, and type-dependent: noise index NI in dB re 1 µV/V per decade — thin/metal film ≲ −35 to −40 dB, foil/wirewound near zero excess, thick film much higher and variable (spread of ~3 orders of magnitude between types) [1][2]. At 2.5 V DC and NI = 0 dB: 0.52 µV/√Hz at 10 Hz, 40× a 10 kΩ's thermal noise (§4).
- **kT/C:** a capacitor sampled through any resistance holds $\sqrt{kT/C}$ rms: 64 µV at 1 pF, 2 µV at 1 nF (§5) — the floor for switched-capacitor and SAR front ends.
- **Noise bandwidth** = ∫|H|² df / |H(0)|²: 1.571 × $f_{-3dB}$ (1-pole), 1.111 (2-pole Butterworth), 1.047 (3), 1.026 (4) [3] (§6).
- **TIA:** input capacitance makes the noise gain rise to $1 + C_{in}/C_F$ above $1/(2\pi R_F(C_{in}+C_F))$; with 20 pF/1.8 pF/100 kΩ and a 7 nV/√Hz op-amp, $e_n$ contributes 93 µV rms vs 46 µV from $R_F$ (§7) — pick a low-$e_n$, low-$C_{in}$ op-amp and minimise stray C.

## Intuition (no math)
Every resistor at temperature T is a tiny noise generator: its electrons jiggle thermally, producing a white noise voltage whose power is proportional to resistance and temperature. An ideal amplifier would only amplify the source's own thermal noise; a real one adds two things at its input: a noise *voltage* (that appears regardless of the source) and a noise *current* (that becomes a voltage by flowing through the source resistance). For a small source resistance, the voltage noise dominates; for a large one, the current noise does. In between there is a sweet spot — $R_{opt} = e_n/i_n$ — where the amplifier's contribution is smallest *relative to* the source's own noise. Different device types sit at wildly different sweet spots: bipolar ≈ hundreds of Ω to kΩ, JFET ≈ 100 kΩ–MΩ, CMOS ≈ tens of MΩ.

Noise figure is always relative to the source's thermal noise, which is why adding a resistor in series with the input can *improve* the noise figure number while making the actual signal-to-noise ratio worse — the reference got noisier. The right way to "noise match" is to transform the source impedance (transformer, or LC network at RF) or to change the amplifier (paralleling devices, changing bias current), never to add resistance.

Resistors also make excess noise when current flows: conduction through a granular material (thick-film pastes, carbon) fluctuates, giving 1/f noise proportional to the DC voltage. Metal films and foils are nearly free of it. At audio frequencies and DC this can swamp everything.

## The math

### Level 1 — the noise model and its figures of merit

**Input-referred noise with source $R_s$** (all densities per √Hz, rms quantities add in quadrature if uncorrelated):
$$e_{ni}^2 = \underbrace{4kTR_s}_{\text{source}} + e_n^2 + i_n^2R_s^2$$

**Noise factor and figure** (source at $T_0$ = 290 K):
$$F = \frac{e_{ni}^2}{4kT_0R_s} = 1 + \frac{e_n^2 + i_n^2R_s^2}{4kT_0R_s},\qquad NF = 10\log_{10}F.$$
Noise temperature $T_e = T_0(F-1)$.

**Optimum source resistance and minimum noise factor:**
$$R_{opt} = \frac{e_n}{i_n},\qquad F_{min} = 1 + \frac{e_ni_n}{2kT_0}.$$

**Thermal noise of a resistor:** $e_R = \sqrt{4kTR}$ (V/√Hz) = 4.00 nV/√Hz for 1 kΩ at $T_0$ = 290 K (4.07 at 300 K, the temperature this page's op-amp budgets use); equivalently a parallel current $\sqrt{4kT/R}$.

**Noise bandwidth:** $B_n = \frac{1}{|H(0)|^2}\int_0^\infty|H(f)|^2df$. rms noise = density × $\sqrt{B_n}$ (white noise).

### Level 2 — derivations and design consequences

**Deriving $R_{opt}$.** Minimise $g(R_s) = e_n^2/R_s + i_n^2R_s$: $dg/dR_s = -e_n^2/R_s^2 + i_n^2 = 0$ → $R_s = e_n/i_n$, and then $g_{min} = 2e_ni_n$, giving $F_{min} = 1 + 2e_ni_n/(4kT_0)$. With correlation coefficient C between the two sources (real, for simplicity), a term $2Ce_ni_nR_s$ adds to the numerator: $R_{opt}$ unchanged, $F_{min} = 1 + e_ni_n(1+C)/(2kT_0)$ (script §1; C = ±0.5 moves NF$_{min}$ from 0.91 dB to 0.48/1.30 dB for the OPA1612 numbers). At RF the correlation is complex and the optimum source becomes an impedance $Z_{opt}$ — the four noise parameters of [LNA design](../06-rf-circuits/lna-design.md).

**Why not add a resistor.** Put $R_x$ in series with $R_s$ to reach $R_{opt}$: the source's *signal* is unchanged but the total thermal noise now includes $4kTR_x$, so SNR falls, even though F (computed relative to the new, noisier "source") may look better. Minimise *total input-referred noise* for your actual source, not NF against a fictitious one.

**Transformer noise matching.** An ideal n:1 (secondary:primary) transformer multiplies source voltage and its noise by n and the source impedance by n². The amplifier's $e_n$ and $i_n$ are unchanged, so the effective $R_s$ becomes $n^2R_s$; choose $n = \sqrt{R_{opt}/R_s}$. For 50 Ω and the OPA1612: n = 3.6 → NF 4.0 → 0.91 dB (script §2; winding resistance and core loss add back a little). Transformers are the classic route for very-low-impedance sources (moving-coil cartridges, magnetic sensors, 50 Ω RF baseband at audio).

**Paralleling N devices.** N identical uncorrelated amplifiers in parallel: $e_n \to e_n/\sqrt N$ (averaging voltage noise), $i_n \to \sqrt Ni_n$ (currents add). $R_{opt}$ scales as $1/N$ while $F_{min}$ is unchanged. 8 × OPA1612 → $R_{opt}$ ≈ 81 Ω and 1.0 dB at 50 Ω (script §3). Same principle inside ICs: large-area input transistors or many parallel BJTs lower $e_n$ at the expense of $i_n$ and capacitance.

**Bipolar noise vs current.** For a BJT, $e_n^2 = 4kT(r_b + 1/2g_m)$ and $i_n^2 = 2qI_C/\beta$; for a given $R_s$ the noise-optimal current is $I_C = V_T\sqrt\beta/R_s$ (derived on the [BJT page](bjt-fundamentals-small-signal.md)): ≈ 5–8 mA for 50 Ω, ≈ 37 µA for 10 kΩ. Discrete low-noise preamps use this to tailor $R_{opt}$ to the source.

**NF of an op-amp gain stage with its feedback network.** The feedback resistors contribute $4kT(R_F\|R_G)$ and $i_n^2(R_F\|R_G)^2$ at the inverting input. For a 50 Ω source with an OPA1612: $R_F/R_G$ = 1 k/100 → NF 6.4 dB; 100/10 → 4.3 dB (close to the op-amp limit, but the op-amp now drives a 110 Ω feedback load); 10 k/1 k → 13.7 dB (script §8). Keep $R_F\|R_G \ll R_s$ for low-impedance sources.

**Resistor excess noise (noise index).** Excess noise has a 1/f power spectrum $e^2(f) = K/f$, so every decade carries the same rms voltage. The noise index NI (dB re 1 µV/V) is the rms noise in one decade per volt of DC across the resistor [1]: $v_{decade} = 10^{NI/20}\,\mu V/V\times V_{DC}$. Hence $K = v_{decade}^2/\ln 10$ and
$$e_{excess}(f) = \frac{10^{NI/20}\times10^{-6}\,V_{DC}}{\sqrt{f\ln10}}.$$
(Script §4 checks the one-decade integral.) For NI = −40 dB (metal film) at 2.5 V: 5.2 nV/√Hz at 10 Hz — below a 10 kΩ's 12.9 nV/√Hz thermal noise; for NI = 0 dB: 521 nV/√Hz. Measurements on 60+ resistor types found excess noise in all of them, varying by nearly three orders of magnitude with type, size, power rating and maker; foil and wirewound were essentially free of it above 1 Hz, metal/thin film low, thick film high, with popcorn noise in some thick-film parts [1]. Vishay gives thin film < −35 dB and metal film ≈ −40 dB [2]. Resistors with no DC across them (AC-coupled paths, feedback resistors in AC amplifiers with no offset) make only thermal noise.

**kT/C noise.** A resistor R in parallel with C: total noise voltage $\int_0^\infty 4kTR/(1+(2\pi fRC)^2)\,df = kT/C$ — independent of R (larger R: more density, less bandwidth). When a switch opens, this voltage is frozen: 64 µV rms on 1 pF at 300 K (script §5). A 16-bit SAR ADC with a 5 V range (76 µV LSB) therefore needs tens of pF of sampling capacitance; this sets ADC input capacitance and hence driver requirements (→ [data converters](data-converters-adc-dac.md)).

**Noise bandwidth of filters.** For an n-pole Butterworth, $B_n/f_{-3dB} = (\pi/2n)/\sin(\pi/2n)$: 1.571, 1.111, 1.047, 1.026 for n = 1…4 — matching TI's table [3] (script §6). For a white-noise integration, a 4th-order filter is almost a brick wall; a single RC is 57 % wider than its −3 dB bandwidth.

**TIA noise (noise-gain peaking).** In a transimpedance amplifier the op-amp's $e_n$ sees noise gain $1 + Z_F/Z_{in}$ with $Z_{in} = 1/(j\omega C_{in})$. Above the zero at $1/[2\pi R_F(C_{in}+C_F)]$ it rises to $1 + C_{in}/C_F$ until the loop gain runs out near crossover. The signal bandwidth is only ≈ $1/(2\pi R_FC_F)$, so there is a band where noise is amplified but signal is not. Example (§7: $R_F$ = 100 kΩ, $C_F$ = 1.8 pF, $C_{in}$ = 20 pF, 10 MHz GBW, $e_n$ = 7 nV/√Hz, $i_n$ = 2 fA/√Hz): noise-gain plateau 12.1; integrated 1 Hz–100 MHz: $e_n$ term 93 µV rms, $R_F$ 46 µV, $i_n$ 0.2 µV, total 103 µV. Cures: op-amp with low $e_n$ *and* low input capacitance; reduce photodiode capacitance with reverse bias; post-filter at the signal bandwidth.

### Level 3 — limits and subtleties
- **1/f noise cannot be averaged away** by longer measurements beyond a point; chopper stabilisation or AC modulation (lock-in, bridge AC excitation) moves the signal above the corner.
- **Popcorn (burst) noise** — random telegraph steps from single traps in semiconductors and thick-film resistors — is not described by a density; screen parts if it matters.
- **Shot noise vs thermal noise:** a forward-biased diode or BJT junction at current I has $2qI$ current noise — equivalent to "half" the thermal noise of its $r_d$ ($2qI\,r_d^2 = 2kTr_d$). This is why cooled or feedback-lowered "cold" resistances can have less noise than a physical resistor of the same value (active termination, "cold resistor" — used in RF LNA input terminations and electronic cooling). See [shot & flicker noise](../07-noise-linearity/shot-and-flicker-noise.md).
- **Interference is not noise** — mains pickup, ground loops, SMPS ripple and RF rectification usually dominate real systems; they must be fixed by shielding, layout and filtering, not by lower $e_n$ (→ [mixed-signal layout](../13-pcb-rf-layout-emc/mixed-signal-layout.md)).
- **Noise temperature view** is more natural for cooled or antenna-fed systems: an amplifier with $T_e$ adds $kT_eB$ referred to its input (→ [thermal noise & noise temperature](../07-noise-linearity/thermal-noise-and-noise-temperature.md)).

## Design equations & rules of thumb

| Quantity | Equation | Typical |
|---|---|---|
| Resistor thermal noise | $\sqrt{4kTR}$ | 4.00 nV/√Hz @ 1 kΩ, 0.895 @ 50 Ω (290 K); 4.07 / 0.910 at 300 K |
| Input-referred total | $\sqrt{4kTR_s + e_n^2 + i_n^2R_s^2}$ | — |
| Noise factor | $1 + (e_n^2+i_n^2R_s^2)/(4kT_0R_s)$ | — |
| Optimum source R | $e_n/i_n$ | bipolar 0.3–10 kΩ; JFET 0.1–10 MΩ; CMOS > 10 MΩ |
| Minimum F | $1 + e_ni_n/(2kT_0)$ | — |
| Transformer ratio | $n = \sqrt{R_{opt}/R_s}$ | 3.6 for 50 Ω → 647 Ω |
| N paralleled devices | $e_n/\sqrt N$, $i_n\sqrt N$ | $R_{opt}$/N |
| BJT optimum current | $V_T\sqrt\beta/R_s$ | 5–8 mA @ 50 Ω |
| Excess noise density | $10^{NI/20}\mu V\cdot V_{DC}/\sqrt{f\ln10}$ | NI: metal film ≈ −40 dB |
| kT/C | $\sqrt{kT/C}$ | 64 µV @ 1 pF |
| Noise bandwidth | 1.571, 1.111, 1.047, 1.026 × $f_{-3dB}$ | Butterworth n = 1–4 |
| TIA HF noise gain | $1 + C_{in}/C_F$ | often 5–20 |
| p-p ≈ 6.6 × rms | Gaussian | 0.1 % exceedance |

**Device choice by source resistance** (first cut, from the §2 numbers):

| Source | Best amplifier type | Why |
|---|---|---|
| < 100 Ω (antenna/mixer baseband, MC cartridges, thermocouples, strain bridges) | low-$e_n$ bipolar, paralleled or transformer-coupled | $e_n$ dominates |
| 100 Ω–10 kΩ (most sensors, audio) | bipolar low-noise op-amp, or JFET | near bipolar $R_{opt}$ |
| 10 kΩ–10 MΩ (piezo, condenser mics, high-Z sensors) | JFET or CMOS input | $i_n$ must be tiny |
| > 10 MΩ, photodiodes, electrometers | CMOS/JFET with fA bias, low $C_{in}$ | $i_n$, leakage, $C_{in}$ |

## Worked examples

### 1. Audio/baseband preamp for a 50 Ω source (e.g. mixer IF at kHz, SDR baseband)
OPA1612 direct: NF 4.0 dB. Options: (a) a 1:3.6 transformer → 0.91 dB; (b) 4 × OPA1612 in parallel (outputs summed through small resistors) → 1.5 dB; (c) a discrete bipolar pair biased at $V_T\sqrt\beta/50$ ≈ 5–8 mA with $r_b$ of a few Ω → ≈ 0.5–1 dB. Keep the gain-setting network at ≲ 10 Ω || (script §8) or it dominates.

### 2. Piezo accelerometer (1 nF, ~10⁸ Ω leakage) charge/voltage amplifier
At 100 Hz the source reactance is 1.6 MΩ: JFET or CMOS input. MCP6002 ($i_n$ 0.6 fA/√Hz, $e_n$ 28 nV/√Hz): $i_n$ × 1.6 MΩ = 1 nV/√Hz, negligible; $e_n$ dominates → 28 nV/√Hz. A BJT op-amp with 1.7 pA/√Hz would give 2.7 µV/√Hz — 100× worse.

### 3. Resistor choice in a bridge or DC-coupled gain stage
A 10 kΩ gain resistor with 2.5 V across it in a 0.1–10 Hz measurement: a thick-film part with NI around 0 dB contributes ≈ 1 µV per decade × 2 decades → 1.4 µV rms — larger than a zero-drift op-amp's own 1.1 µV p-p. A thin-film (NI < −35 dB) part: ≈ 25 nV rms. Use thin-film (or foil) resistors wherever DC flows and low frequencies matter (bridges, references, precision gain).

### 4. Photodiode receiver (TIA)
From §7: $e_n$ × noise gain is the biggest term. Halving $C_{in}$ (reverse-bias the photodiode, choose a smaller op-amp input capacitance) roughly halves that term; choosing $R_F$ larger improves signal-to-$R_F$-noise ($\propto\sqrt{R_F}$) but narrows bandwidth.

## Practical notes
- **Measure the noise floor first:** short the input (through $R_s$-equivalent resistor), measure the output spectrum, divide by gain; compare to the prediction. A mismatch usually means interference, not "bad op-amp".
- **Spectrum-analyser measurements** need the noise marker (dBm/Hz) or RBW normalisation and an LNA ahead of the analyser if the DUT output is below its floor (→ [spectrum analysers](../17-test-measurement/spectrum-analyzers.md)).
- **Thermal EMFs** (µV/K at dissimilar-metal junctions, including solder joints and relay contacts) look like 1/f noise in DC measurements; keep input pairs symmetric and isothermal.
- **Batteries and references:** power low-noise front ends from a clean LDO or reference-derived rail; the reference's noise adds directly to ratiometric measurements (→ [power supplies](power-supplies-for-rf-and-analog.md)).
- **Capacitor dielectrics:** high-k ceramics (X7R/X5R) are piezoelectric (microphonic) — in a vibrating rocket they generate signals; prefer C0G/film in sensitive signal paths.

## Common mistakes & misconceptions
- **"Lower $e_n$ is always better."** Only if $e_n$ dominates at your source resistance; at high $R_s$, $i_n$ rules.
- **Adding a resistor to reach $R_{opt}$.** It improves the NF number, worsens SNR.
- **Computing NF of an op-amp stage without the feedback resistors' noise.**
- **Integrating noise over the −3 dB bandwidth** instead of the noise bandwidth (57 % error for one pole).
- **Assuming all 1 kΩ resistors are equally noisy.** Thermal noise yes; excess noise with DC across them differs by orders of magnitude between thick film and thin film/foil.
- **Treating kT/C as a design choice of R.** It depends only on C and T.
- **Ignoring noise-gain peaking in TIAs** — the op-amp's $e_n$, multiplied by $1 + C_{in}/C_F$, is often the dominant term.
- **Using X7R capacitors in low-noise signal paths on vibrating vehicles** — microphonics.

## How to simulate / verify
- **Python:** `tools/verify/analog_noise.py` — F(R_s), $R_{opt}$, $F_{min}$ brute-force and correlated case; transformer and paralleling; excess-noise conversion and one-decade check; kT/C; Butterworth ENBW (numeric vs closed form); full TIA noise integration with a single-pole op-amp; NF of an op-amp stage with its feedback resistors.
- **SPICE:** `.noise V(out) Vin dec 50 1 10Meg` gives output and input-referred noise density per element; integrate (ngspice prints `onoise_total`). Vendor op-amp macromodels include $e_n$/$i_n$ with 1/f; resistor excess noise must be added manually (a noise current source with 1/f PSD, or `KF`/`AF` on resistors in simulators that support it).
- **Bench:** shorted-input output noise with a spectrum analyser or a sound-card/SDR FFT; 0.1–10 Hz p-p with a band-pass and a scope; resistor excess noise with a DC-biased bridge (as in [1]).

## Open questions / gaps
- Quantitative noise-index values for specific thick-film chip series (0402/0603, 1 k–1 M) were not collected; the LIGO study gives plots rather than a table. Needs a datasheet sweep (Yageo/Panasonic/Vishay thick film).
- ADI MT-047/-048 noise tutorials timed out; equations here are derived and cross-checked with TI SLVA043B.
- Motchenbacher & Connelly's treatment of correlated noise and transformer loss is cited from memory of the book's scope, not re-read.

## Sources
1. F. Seifert, *Resistor Current Noise Measurements*, LIGO technical note T0900200-v1, 2009. https://dcc.ligo.org/public/0002/T0900200/001/current_noise.pdf — noise-index definition (0 dB = 1 µV/V per decade), linearity with voltage drop, 60+ resistor types, spread of ~3 orders of magnitude, foil/wirewound lowest, thick film highest, popcorn noise. (technical report)
2. Vishay, *Basics of Linear Fixed Resistors* and thin-film technology notes. https://www.vishay.com/docs/28771/basics.pdf , https://www.vishay.com/docs/49562/49562.pdf — thin film NI < −35 dB, metal film ≈ −40 dB (via search summary). (app note)
3. Texas Instruments (T. Kugelstadt et al.), *Noise Analysis in Operational Amplifier Circuits*, SLVA043B, 2007. https://www.ti.com/lit/an/slva043b/slva043b.pdf — noise types, op-amp noise model, resistor noise, ENB table 1.57/1.11/1.05/1.025. (app note)
4. C. D. Motchenbacher, J. A. Connelly, *Low-Noise Electronic System Design*, Wiley 1993 — $e_n$–$i_n$ model, optimum source resistance, noise figure, transformer coupling, resistor excess noise. (textbook)
5. H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley 2009 — ch. 9 (intrinsic noise sources, noise factor, $e_n$–$i_n$ measurement). (textbook)
6. P. Horowitz, W. Hill, *The Art of Electronics*, 3rd ed., Cambridge 2015 — ch. 8 (low-noise techniques, noise matching, transformers, paralleling, BJT/JFET choice). (textbook)
7. J. G. Graeme, *Photodiode Amplifiers: Op Amp Solutions*, McGraw-Hill 1996 — TIA noise gain and $e_n$C noise. (textbook)
8. Datasheets used for numbers: OPA1612, MCP6002, BF862 (see [op-amps](op-amps-real-limitations.md) and [FETs](fets-mosfet-jfet-gaas-gan.md) pages). (datasheet)
