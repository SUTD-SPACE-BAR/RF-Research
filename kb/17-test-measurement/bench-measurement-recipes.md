---
title: Bench measurement recipes — is it transmitting, output/source impedance (two-load, four-load, load-pull-lite), SWR-meter calibration and directivity, shield boxes and conducted vs radiated tests, EBYTE module power and harmonics, antenna efficiency on a budget, attenuator range tests, pulsed signals on an SA, ferrite cores, coupled-loop resonance and Q (dip-meter substitute), LCR meter vs VNA, return-loss bridge + SA/TG, resistive taps vs couplers, the NanoVNA as a receiver, why WSPR/RBN antenna comparisons mislead, and RF prototyping (Manhattan, dead-bug, ugly, copper-clad, enclosures)
domain: 17-test-measurement
slug: bench-measurement-recipes
tags: [bench, recipe, output-impedance, source-impedance, two-load-method, load-pull, hot-s22, source-match, swr-meter, directional-coupler, directivity, calibration, antenna-analyzer, shield-box, faraday-cage, conducted-test, radiated-test, tem-cell, waveguide-below-cutoff, aperture-leakage, ebyte, e22-400t33d, e220-900t30d, harmonics, attenuator, uncertainty, gum, wheeler-cap, efficiency, range-test, pulse-desensitization, line-spectrum, ferrite, permeability, al-value, field-strength, dip-meter, coupled-loop, q-factor, lcr-meter, return-loss-bridge, tracking-generator, resistive-tap, wspr, rbn, ab-comparison, manhattan, dead-bug, ugly-construction, copper-clad, prototyping, enclosure]
prerequisites: [rf-power-measurement.md, spectrum-analyzers.md, nanovna-librevna-practical.md, ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md]
related: [basic-bench-instruments.md, vna-fundamentals-calibration.md, noise-figure-measurement.md, antenna-range-ota-testing.md, rf-bring-up-debug-playbook.md, sdr-as-test-equipment.md, signal-generators-and-sources.md, lab-setup-by-budget.md, fixtures-and-deembedding.md, ../08-antennas/antenna-measurement.md, ../06-rf-circuits/power-amplifiers.md, ../06-rf-circuits/couplers-dividers-combiners.md, ../13-pcb-rf-layout-emc/shielding-and-isolation.md, ../02-electromagnetics/waveguides-and-cavity-resonators.md, ../04-real-components-hf/ferrites-and-beads.md, ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md, ../19-regulations-safety/singapore-imda-rules.md, ../14-sdr-dsp/sdr-front-end-protection-and-filtering.md, ../14-sdr-dsp/signal-identification-and-spectrum-survey.md]
level: mixed
confidence: medium
last_updated: 2026-10-12
---

# Bench measurement recipes

## Questions this page answers
- How can I tell quickly whether my transmitter is actually transmitting?
- How do I measure the output impedance of an amplifier, signal generator or radio module?
- Why is a power amplifier's "output impedance" not 50 Ω, and does that matter?
- How do I calibrate an SWR meter, and how far can I trust its 1.1:1?
- How do I read R, X and SWR on an antenna analyser when it doesn't tell me the sign of X?
- How do I build and check a shield box, and when do I test conducted rather than radiated?
- How do I simulate bad reception or long range in the lab?
- How do I measure my EBYTE 2 W module's true output power and harmonics without destroying anything?
- How do I measure an antenna's efficiency without an anechoic chamber?
- How do I turn an attenuator range test into a range prediction, and how accurate is it?
- Why does a pulsed signal read lower on a spectrum analyser than its peak power?
- How do I measure a ferrite core's permeability or A_L?
- How do I find the resonance and Q of a tank, trap or resonator with a NanoVNA instead of a dip meter?
- Should I use an LCR meter or a VNA to measure an RF inductor or capacitor?
- Can I measure return loss with a spectrum analyzer, tracking generator and a return-loss bridge?
- When is a resistor "tap" good enough instead of a directional coupler?
- Can a NanoVNA be used as a receiver or spectrum analyzer?
- Why are WSPR or Reverse Beacon Network comparisons of two antennas so unreliable?
- Should I prototype a 433 MHz circuit Manhattan-style, dead-bug, or just order a JLC board?

## TL;DR
- **Measure the right quantity with the right uncertainty.** Each recipe below gives the procedure, the numbers to expect, and an uncertainty estimate; all numbers marked "script" are from `tools/verify/e3_bench.py` (33/33 PASS).
- **Output impedance**: two resistive loads give $R_s=(V_2-V_1)/(V_1/R_1-V_2/R_2)$; loads far apart (50 Ω and 1 kΩ) give a 3.6 Ω spread for 0.1 dB power errors versus 9.8 Ω for 50/100 Ω (script). A complex $Z_s$ needs at least one reactive load (otherwise the sign of X is invisible) — four loads make the problem linear. For a **power amplifier** the useful quantity is power versus load (load-pull), not a conjugate "output impedance".
- **Load-pull-lite**: rotate a known VSWR-2 mismatch with cable lengths (λ_g/2 = 24 cm of PTFE coax at 433 MHz) and record the power ripple: 1.74 dB of ripple means $|\Gamma_s|$ = 0.3 (script).
- **SWR meters are directivity-limited**: true SWR 1.5 reads 1.22–1.86 with 20 dB directivity, 1.40–1.60 with 30 dB (script). Calibrate by rotating a known mismatch: the reading swings between $|\Gamma|\pm 10^{-D/20}$, which gives both D and |Γ|.
- **Shield boxes**: a slot of length L leaks ≈ $20\log(\lambda/2L)$ — only 24 dB for a 10 mm slot at 915 MHz; feed-throughs as waveguide-below-cutoff tubes give 32 dB per diameter of length. A 300 × 200 × 100 mm box resonates at 901 MHz (script) — radiated tests inside boxes are only relative.
- **EBYTE E22-400T33D (33 dBm)**: 20 dB/10 W + 20 dB/2 W pads (first pad dissipates ≈ 2 W continuous), −7 dBm at the analyser; the 2nd harmonic at 866 MHz must be ≤ −36 dBm, i.e. ≤ −69 dBc — invisible without a high-pass filter in front of the analyser. Power-sensor route ±0.33 dB (k = 2) (script).
- **Antenna efficiency**: Wheeler cap; a cube cap of half-side λ/2π resonates at 2.22 f (safe); uncertainty explodes for R_free < 1 Ω (±14 % at 0.9 Ω, script).
- **Pulses on an SA**: in "pulse" mode the display is $20\log(K\tau B)$ below the peak with K = 1.505 for a Gaussian RBW (AN 150-2 quotes ≈ 1.5) — a 1 µs pulse at 100 kHz RBW reads 16.4 dB low (script).
- **Coupled loops replace the dip meter** (R11): two weak loops on a NanoVNA give a transmission peak; $Q_0=Q_L/(1-|S_{21}|)$ (×1.033 at 30 dB insertion loss). **LCR meter vs VNA** (R12): a 10 nH part is 6.3 mΩ at an LCR meter's 100 kHz and 27 Ω at 433 MHz — measure RF parts at RF. **RLB + SA/TG** (R13): scalar, directivity-limited — a 35 dB bridge reads a 20 dB DUT as 18.6–21.7 dB. **Resistive taps** (R14): a 1 kΩ tap couples −26.6 dB, is not directional, and a 4.95 kΩ "−40 dB" tap reads 13 dB high at 915 MHz because of 0.15 pF (script `s10_bench_instruments.py`).
- **A/B antenna comparisons on fading paths** (R16): a Rayleigh-faded power has a 5.57 dB spread in dB, so resolving 1 dB between two antennas with independent fades needs ≈ 240 paired spots; WSPR/RBN spot lists rarely provide that. **Construction** (R17): a 7-pole 433 MHz harmonic LPF built dead-bug with 2 × 5 mm capacitor leads loses 28 dB *in the passband* until re-tuned and re-opens to −7 dB at 3 GHz; Manhattan or a JLC board with short ground paths keeps the stopband (script `s10_construction_amp.py`).

## Intuition (no math)
Most bench questions are really "what am I actually measuring?" An SWR meter measures a small sample of the reflected wave — plus whatever forward wave leaks into its reflected port; if the leak is as big as the reflection you are trying to see, the reading is meaningless. A power meter measures the power the source delivers *into the meter*, which depends on how well the two are matched. A spectrum analyser measures what gets through its resolution filter, which for a short pulse is only a fraction of the pulse's peak. A metal box screens fields only as well as its worst seam, and it also behaves like a resonant cavity that makes field strength inside depend on where you put things.

The recipes all follow the same pattern: (1) protect the instrument (attenuate, filter, DC-block), (2) calibrate or reference-check the measurement path with something known, (3) make the measurement in a way that cancels what you do not know (rotating a mismatch, swapping loads, comparing with a reference antenna), (4) estimate the uncertainty and write it next to the number. That last step is what turns a screenshot into evidence — the team's record-everything and report-faithfully tenets applied to the bench.

## The math

### Level 1 — the working formulas
- **Two-load (resistive) source resistance**: with rms voltages $V_k=\sqrt{P_kR_k}$ across loads $R_1,R_2$:
  $$R_s=\frac{V_2-V_1}{V_1/R_1-V_2/R_2},\qquad\text{or with an open-circuit reading } R_s=R_L\left(\frac{V_{oc}}{V_L}-1\right).$$
- **Power into a load from a mismatched source** (available power $P_{av}$):
  $$P_L=P_{av}\frac{(1-|\Gamma_s|^2)(1-|\Gamma_L|^2)}{|1-\Gamma_s\Gamma_L|^2}.$$
- **Directivity-limited reflection reading**: $\Gamma_{read}=\Gamma_L+\delta e^{j\theta}$, $\delta=10^{-D/20}$, so $|\Gamma_L|-\delta\le|\Gamma_{read}|\le|\Gamma_L|+\delta$; forward-power error $20\log(1\pm\delta|\Gamma_L|)$.
- **Aperture leakage** (slot of longest dimension L < λ/2): $SE\approx20\log_{10}(\lambda/2L)$, minus ≈ $20\log n$ for n similar holes within ≈ λ/2 of each other [5], [6].
- **Waveguide below cutoff** (tube of length ℓ, f ≪ f_c): circular $A\approx32.0\,\ell/d$ dB, rectangular $A\approx27.3\,\ell/w$ dB.
- **TEM cell field**: $E\approx\sqrt{PZ_0}/h$ (septum-to-wall spacing h) [7].
- **Pulsed signal on an SA**: line spectrum (RBW < 0.3 PRF): central line at $20\log(\tau\cdot PRF)$ relative to the peak; pulse spectrum (RBW > PRF, Bτ < 0.2): peak display at $20\log(K\tau B)$, K ≈ 1.5 [8].
- **Wheeler cap** (series-resonant small antenna): $\eta=1-R_{cap}/R_{free}$ ([antenna measurement](../08-antennas/antenna-measurement.md)).
- **Attenuator range test** (free space): $d_{eq}=d_{test}\cdot10^{A/20}$; each 6 dB doubles range; an error of δA dB is a range error of $10^{\delta A/20}-1$ (5.9 % per 0.5 dB).
- **Toroid**: $A_L=\mu_0\mu_r h\ln(OD/ID)/(2\pi)$ (H/turn²); complex μ from a winding: $\mu'=X/(\omega L_0)$, $\mu''=R/(\omega L_0)$ with $L_0$ the same winding in air.

### Level 2 — derivations
**Two loads → $R_s$.** A linear source is a Thévenin pair $(V_{oc},R_s)$: $V_k=V_{oc}R_k/(R_s+R_k)$. Eliminating $V_{oc}$ between two loads, $V_1(R_s+R_1)/R_1=V_2(R_s+R_2)/R_2$, which is linear in $R_s$ and gives the Level-1 result. Sensitivity: the denominator $V_1/R_1-V_2/R_2$ is small when the loads are similar, so measurement errors are amplified; Monte Carlo with independent 0.1 dB power errors (script §1) gives 16–84 % spreads of 9.6, 16.2, 9.8, 5.4 and 3.6 Ω for second loads of 25, 75, 100, 200 and 1000 Ω (first load 50 Ω, true 50 Ω). Choose loads that bracket $R_s$ widely.

**Four loads → complex $Z_s$.** With complex loads $Z_k=R_k+jX_k$, $|Z_s+Z_k|^2=|V_{oc}|^2R_k/P_k$. Expanding,
$$\underbrace{(R_s^2+X_s^2)}_{u}+2R_kR_s+2X_kX_s-\underbrace{|V_{oc}|^2}_{c}\,\frac{R_k}{P_k}=-|Z_k|^2,$$
which is **linear** in $(u,R_s,X_s,c)$ — four loads (or more, by least squares) solve it. If all loads are real, $X_k=0$ and $X_s$ appears only inside $u$: its sign is unobservable (script §2 shows identical powers for 30 ± j20 Ω). With loads 50, 100, 25 and 50 + j50 Ω and 0.05 dB errors the script recovers $Z_s$ = 30 + j20 Ω with ±7.5 Ω (R) and ±3.7 Ω (X).

**Rotated mismatch → $|\Gamma_s|$ (load-pull-lite).** With $|\Gamma_L|$ fixed and its phase rotated through 360° (cable lengths), the denominator $|1-\Gamma_s\Gamma_L|^2$ swings between $(1\mp|\Gamma_s||\Gamma_L|)^2$, so
$$r=\frac{P_{max}}{P_{min}}=\left(\frac{1+|\Gamma_s||\Gamma_L|}{1-|\Gamma_s||\Gamma_L|}\right)^2\ \Rightarrow\ |\Gamma_s|=\frac{\sqrt r-1}{(\sqrt r+1)|\Gamma_L|}.$$
With a VSWR-2 load ($|\Gamma_L|$ = 1/3): ripple 0.58 / 1.74 / 2.92 / 4.13 dB ↔ $|\Gamma_s|$ = 0.1 / 0.3 / 0.5 / 0.7 (script §3). This is a *linear* model; for a saturated PA the power-versus-load map is not described by a single $\Gamma_s$ (its "hot" output reflection under drive differs from the small-signal S22 [9]), and what you actually want is the load that gives the most power or efficiency — a load-pull contour ([power amplifiers](../06-rf-circuits/power-amplifiers.md)).

**Directivity from a rotated mismatch.** In the reflected arm, the coupler delivers $\Gamma_L$ (rotating as the cable length changes) plus a fixed leak δ of the forward wave. The reading traces a circle of radius $|\Gamma_L|$ centred δ away from the origin, so $\delta=(|\Gamma|_{max}-|\Gamma|_{min})/2$ and $|\Gamma_L|=(|\Gamma|_{max}+|\Gamma|_{min})/2$ (script §4 recovers D = 23.00 dB and |Γ| = 0.3333 exactly). This is the classic sliding-load idea done with a few cables.

**Waveguide below cutoff.** A tube far below cutoff carries only evanescent modes with field decaying as $e^{-\alpha\ell}$, $\alpha=\sqrt{(2\pi/\lambda_c)^2-(2\pi/\lambda)^2}\approx2\pi/\lambda_c$. Circular TE11: $\lambda_c=1.706\,d$ → $\alpha=3.683/d$ Np/m = **31.99 dB per diameter**; rectangular TE10: $\lambda_c=2w$ → **27.29 dB per width** (script §5). A 10 mm hole (cutoff 17.6 GHz) 20 mm deep gives 64 dB at 915 MHz (exact 63.9 dB). ([waveguides](../02-electromagnetics/waveguides-and-cavity-resonators.md))

**Gaussian RBW impulse bandwidth.** With $H(f)=e^{-af^2}$ and a 3 dB (voltage $1/\sqrt2$) bandwidth B, $a(B/2)^2=\tfrac12\ln2$ → $a=2\ln2/B^2$. The impulse response peak is $h(0)=\int H\,df=\sqrt{\pi/a}=B\sqrt{\pi/(2\ln2)}=1.505B$. A short RF pulse of width τ (τB ≪ 1) at the filter centre produces a peak envelope ≈ $\tau h(0)$ relative to a CW of the same amplitude: desensitisation $20\log(1.505\,\tau B)$. Exact integration (script §9): error 0.05 dB at τB = 0.1, 0.20 dB at 0.2, 1.2 dB at 0.5 — hence AN 150-2's τB < 0.2 condition and its empirical K ≈ 1.5 [8].

**Wheeler-cap uncertainty.** $\eta=1-R_c/R_f$ so $\sigma_\eta^2\approx(\sigma_{R_c}/R_f)^2+(R_c\sigma_{R_f}/R_f^2)^2$. With 0.1 Ω + 1 % errors (a good NanoVNA at a calibrated plane): R_f 12 Ω → σ ≈ 1.0 %; 2 Ω → 5.6 %; 0.9 Ω → 13.9 % (script §7). Small, low-resistance antennas need a differential method (measure the *change* with and without cap at the same plane, repeat 10×) or a different technique.

**Cap and box resonances.** A closed rectangular box of sides a, b, d has modes $f_{mnp}=\tfrac c2\sqrt{(m/a)^2+(n/b)^2+(p/d)^2}$ (at least two indices non-zero for TE/TM). A cube with half-side equal to the radiansphere radius $\lambda/2\pi$ (side $\lambda/\pi$) resonates first at $f_{110}=c/(\sqrt2\,\lambda/\pi)=(\pi/\sqrt2)f$ = **2.22 f**; a sphere of radius λ/2π at 2.74 f. So a cap "just big enough" is also safely below its own first resonance; a cap much bigger than 2–3× that size starts to resonate near the test frequency (433 MHz: cube side 220 mm → 962 MHz; 915 MHz: 104 mm → 2033 MHz, script §7).

### Level 3 — uncertainty budgets and where the simple models fail
- **Combining uncertainties (GUM).** Convert each contribution to a standard uncertainty: rectangular limits ÷ √3, U-shaped mismatch limits ÷ √2, calibration certificates ÷ their k; root-sum-square; multiply by k = 2 for ≈ 95 %. For the EBYTE power recipe (pad calibration ±0.10 dB, module-to-pad mismatch ±0.12 dB with an assumed $|\Gamma_s|$ = 0.3 and pad VSWR 1.1, thermal sensor ±0.20 dB, pad drift under 2 W ±0.10 dB) the standard uncertainty is 0.166 dB → **±0.33 dB (k = 2)**; replacing the sensor by a tinySA (±1.5 dB assumed) makes it ≈ ±1.5 dB (script §6) ([power measurement](rf-power-measurement.md)).
- **Hot vs cold source match.** For a linear amplifier, S22 measured by a VNA with no drive equals the output reflection under small-signal drive. For a compressed PA the large-signal output "reflection" depends on drive, bias and load; a hot-S22 measurement (VNA reverse sweep with the drive tone on, offset in frequency) or a power-vs-load map is required [9]. PAs are designed for an optimum *load*, not a conjugate match, so a PA with $|\Gamma_s|$ = 0.7 can still deliver its rated power into 50 Ω.
- **Boxes are cavities.** Inside a closed metal box above its first resonance, field strength varies with position by ±10 dB or more (standing waves); absorber (carbon-loaded foam) lining reduces the Q and the variation. A shielded box is therefore excellent for *isolation* and for conducted tests with a cable through a feed-through, and only suitable for *relative* radiated tests (same position, same objects). TEM cells give a known uniform field only below their first higher-order mode, roughly where the cell's width approaches λ/2 (approximate rule; check the specific cell) [7].
- **Aperture rules are estimates.** $20\log(\lambda/2L)$ is a thin-slot, far-field estimate; app notes use a coefficient between 20 and 40 depending on geometry [6], and enclosure SE is dominated by the worst seam and by cavity resonances, which analytical models handle explicitly [10]. Use the formula to rank seams, then measure.

## Design equations & rules of thumb

| Quantity | Relation / rule | When valid | Typical values (script) |
|---|---|---|---|
| Two-load $R_s$ | $(V_2-V_1)/(V_1/R_1-V_2/R_2)$ | linear source | 50/1000 Ω loads: ±1.8 Ω per 0.1 dB |
| Complex $Z_s$ | four-load linear solve | linear source, ≥ 1 reactive load | ±4–8 Ω for 0.05 dB |
| $\lvert\Gamma_s\rvert$ from ripple | $(\sqrt r-1)/((\sqrt r+1)\lvert\Gamma_L\rvert)$ | linear source | 1.74 dB ripple, VSWR-2 load → 0.3 |
| Cable for 360° of Γ rotation | $\lambda_g/2$ | coax vf | 433 MHz PTFE 24.1 cm; 915 MHz 11.4 cm |
| SWR reading range | $\lvert\Gamma\rvert\pm10^{-D/20}$ | coupler meters | SWR 1.5, D 25 dB → 1.34–1.69 |
| Forward-power error | $20\log(1\pm\delta\lvert\Gamma_L\rvert)$ | coupler meters | D 25, VSWR 2 → ±0.16 dB |
| Required test isolation | attenuation + 20 dB | conducted sensitivity | −10 → −130 dBm: 140 dB |
| Slot leakage | $20\log(\lambda/2L)$ | L < λ/2 | 10 mm @ 915 MHz: 24 dB |
| WBC tube | 32.0 dB per d (round), 27.3 dB per w (rect.) | f ≪ f_c | 10 mm × 20 mm tube: 64 dB |
| Box first resonance | $\tfrac c2\sqrt{a^{-2}+b^{-2}}$ (a, b largest) | closed box | 300 × 200 × 100 mm: 901 MHz |
| TEM cell | $E=\sqrt{PZ_0}/h$ | below first higher mode | 1 W, h 10 cm: 70.7 V/m |
| Pulse desensitisation | $20\log(1.505\,\tau B)$ | B > PRF, τB < 0.2 | 0.5 µs @ 300 kHz: −12.9 dB |
| Line spectrum | $20\log(\tau\,PRF)$ | B < 0.3 PRF | 10 % duty: −20 dB |
| Wheeler cap | $\eta=1-R_c/R_f$; cube cap resonates at 2.22 f | small, single-mode antennas | R_f 12 Ω: ±1 % |
| Range from attenuation | $d_{eq}=d\cdot10^{A/20}$ | free space | 43.5 dB @ 200 m → 29.9 km |
| Toroid $A_L$ | $\mu_0\mu_rh\ln(OD/ID)/2\pi$ | ungapped toroid | FT37 size, μ 800: 353 nH/turn² |
| Field from EIRP | $E=\sqrt{30\,EIRP}/d$ | far field | 100 mW at 1 m: 1.73 V/m |
| Unloaded Q, two-loop | $Q_0=Q_L/(1-\lvert S_{21}\rvert)$ | equal weak couplings | 30 dB IL: ×1.033 |
| RLB reading range | $\lvert\Gamma\rvert\pm10^{-D/20}$ | scalar bridge | D 35 dB, RL 20 dB → 18.6–21.7 dB |
| Resistive tap | $20\log(50/(R+75))$ | matched line, $R\ll1/\omega C_p$ | 1 kΩ: −26.6 dB |
| A/B sample size | $n=(1.96\,\sigma_d/\Delta)^2$ | paired differences | σ_d 7.9 dB, Δ 1 dB: 240 |
| Lead inductance | $(\mu_0l/2\pi)\ln(2h/r)$ | wire over a plane, h ≫ r | 10 mm at 3 mm: 6.4 nH |
| Shunt-arm compensation | $C_{nom}=C/(1+\omega^2L_{gnd}C)$ | below arm resonance | dead-bug LPF: 13.35 → ≈ 8 pF |

## Worked examples
Each recipe: **set-up → steps → expected numbers → uncertainty → pitfalls**.

| Recipe | Question it answers | Minimum kit | Time |
|---|---|---|---|
| R1 | Is it transmitting? | supply ammeter, RTL-SDR, pick-up loop | 1 min |
| R2 | What is the source/output impedance? | power sensor or SA, loads, VNA, cables | 30–60 min |
| R3 | How good is my SWR/wattmeter? | VNA-verified 50/25/100 Ω loads, cables, thermal sensor | 30 min |
| R4 | What do R, X, SWR on my analyser mean? | antenna analyser or NanoVNA | 10 min |
| R5 | Is my box/set-up isolated enough? | metal box, feed-throughs, small TX, SDR | 1–2 h |
| R6 | What is my module's true power and harmonic level? | 5 V/2 A supply, rated pads, sensor/tinySA, HPF | 1 h |
| R7 | How efficient is my antenna? | metal box/tin, VNA; or a range + reference dipole + SDR | 1–3 h |
| R8 | How far will the link reach? | step attenuator, two radios, a 200 m LOS site | half day |
| R9 | What is the peak power of this pulse? | SA with known RBW shape | 15 min |
| R10 | What core is this, and what is its μ? | VNA/LCR, wire | 20 min |
| R11 | Where is this tank/trap/resonator resonant, and what is its Q? | NanoVNA, two small loops | 10 min |
| R12 | LCR meter or VNA for this part? | LCR meter, VNA, fixture | 10 min |
| R13 | Return loss without a VNA | SA + tracking generator (or tinySA pair), return-loss bridge | 20 min |
| R14 | Sampling a line: resistor tap or coupler? | SMD resistor, coupler, VNA | 20 min |
| R15 | Can my NanoVNA receive / act as an SA? | NanoVNA, LibreVNA or tinySA | — |
| R16 | Is antenna A really better than B on the air? | two antennas, a switch, many packets/spots | days |
| R17 | How should I build an RF prototype? | copper-clad board, pads, short-lead parts; or a JLC panel | 1–3 days |

### R1 — "Is it transmitting?" in 60 seconds (D1 #476)
1. **Current**: watch the supply current — an E22-400T33D jumps from ≈ 15 mA to 0.85–1.2 A when it keys ([EBYTE modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)); no jump = no PA activity.
2. **SDR near-field look**: an RTL-SDR with a short whip 1–3 m away. 20 dBm EIRP at 433 MHz gives ≈ 1.7 V/m at 1 m and ≈ −5 dBm into a 0 dBi antenna — too much; at 10 m ≈ −25 dBm (script §11). Use the lowest SDR gain or a pad, and look for the chirps/bursts at the expected frequency ([signal ID](../14-sdr-dsp/signal-identification-and-spectrum-survey.md)).
3. **Field-strength meter / near-field loop**: a diode detector on a small loop near the antenna confirms RF without frequency information; a loop near the PA shield can also reveal oscillation when "off".
4. **Conducted**: if any doubt remains, go to R6 (pads + power sensor).
Pitfall: an SDR overloaded at 1 m "sees" the transmitter everywhere — use distance or a pad ([front-end protection](../14-sdr-dsp/sdr-front-end-protection-and-filtering.md)).

### R2 — Output/source impedance of an amplifier, generator or module (D1 #295)
*Small-signal amplifier*: measure S22 with a VNA (port 1 terminated, DUT biased, input driven only by the VNA's low-level stimulus) — that is the output impedance in the linear regime ([S-parameters](../03-transmission-lines-matching/s-parameters.md)).
*Signal generator or linear driver*: two-load method.
1. Measure power into a calibrated 50 Ω load (power sensor) — $P_1$.
2. Measure power into a known second load far from 50 Ω (a 1 kΩ SMD resistor at the connector measured with a high-impedance probe, or a 200 Ω load measured by voltage) — $P_2$; or use an open-circuit voltage with a high-Z probe.
3. Compute $R_s$; Monte Carlo guidance: 50 & 1000 Ω loads → ±1.8 Ω for 0.1 dB errors; 50 & 100 Ω → ±4.9 Ω (script §1).
4. For a complex $Z_s$, add a reactive load (e.g. 50 Ω behind a series 18 nH inductor ≈ +j50 Ω at 433 MHz — measure it with the VNA first) and two more resistive loads; solve the four-load system (script §2).
*Transmitter / PA module (hot)*: load-pull-lite.
1. Make a VSWR-2 load: a 25 Ω or 100 Ω termination (two 50 Ω loads in parallel via a tee, or a 50 Ω load behind a 50 → 100 Ω resistive network — verify its |Γ| with a VNA).
2. Insert lengths of PTFE coax in 3 cm steps (433 MHz) up to 24 cm (one full rotation of Γ_L) between the module and a coupler/sensor feeding that load, or use a commercial line stretcher.
3. Record forward power (through a calibrated directional coupler) at each length: a ripple of 1.74 dB means $|\Gamma_s|$ ≈ 0.3 (linear model); the *maximum-power* length tells you which load phase the PA prefers.
Uncertainty: dominated by the load's |Γ_L| (measure it) and the coupler's directivity (R3). Pitfall: high-power modules into a VSWR-2 load must be within their mismatch rating; keep transmissions short and watch the current and temperature.

### R3 — Calibrating an SWR/wattmeter and finding its directivity (D1 #638)
1. Verify a good 50 Ω load with a VNA (RL > 35 dB at the frequency) and two mismatch standards (25 Ω and 100 Ω, SWR 2.0, |Γ| = 1/3).
2. Transmit low power (e.g. 1–5 W into the meter's rated range) into the 50 Ω load: the reflected reading is your directivity leak δ (if it reads SWR 1.10, δ ≈ 0.048 → D ≈ 26 dB).
3. Replace with the SWR-2 load and insert 4–8 cable lengths spanning λ_g/2 between meter and load. Record max and min SWR readings: $|\Gamma|_{max,min}=|\Gamma_L|\pm\delta$ → D and the meter's scale error (script §4 recovers D exactly from such data).
4. Forward power: compare with a thermal sensor behind a calibrated pad at two power levels; record the meter's error at each.
Expected: cheap meters 15–25 dB directivity at UHF; a true SWR 1.5 then reads anywhere from 1.22–1.86 (D 20) or 1.34–1.69 (D 25) (script §4). Through-line wattmeters are typically specified as a percentage of *full scale* (e.g. ±5 % FS for Bird 43-class elements — unverified), so read in the upper half of the scale.
Pitfall: "1.1:1 on my meter" is not evidence of a good antenna unless D ≥ RL + 15 dB ([power measurement](rf-power-measurement.md)).

### R4 — Reading an antenna analyser (D1 #671, #608)
1. Calibrate at the end of the cable (SOL) or use port extension; otherwise the cable transforms the impedance ([NanoVNA practical](nanovna-librevna-practical.md)).
2. Read R and X at the operating frequency, not just minimum SWR: R ≈ 50 Ω and X ≈ 0 is the goal; SWR alone hides whether you are too long or too short.
3. **Sign of X**: bridge-type analysers often compute |X| from magnitudes and cannot tell inductive from capacitive. Resolve it by stepping frequency up a little: for an antenna below its series resonance X is negative and rises toward zero (|X| falls); above resonance X is positive and grows. Or add a small known series capacitor: |X| falls if X was inductive.
4. **On-air tuning**: do the adjustment with the analyser/VNA (no transmission), then confirm with a short, low-power transmission into the antenna through a coupler — on a clear frequency, legally identified where required, never into an open feedline ([lab safety](../19-regulations-safety/lab-safety-esd-high-power.md)).

### R5 — Shield boxes, conducted vs radiated tests, "bad reception" in the lab (D1 #173, D2 #213)
*Conducted* (preferred): DUT's antenna port → cable → calibrated pads + step attenuator → receiver; both radios in separate shielded boxes, power by battery or filtered feed-through, data out by optical fibre or filtered lines. Isolation of every leakage path ≥ path attenuation + 20 dB: for −10 dBm → −130 dBm that is 140 dB (script §5; see [noise-figure Example 4](noise-figure-measurement.md)).
*Building a box*:

- a die-cast or folded aluminium box with an overlapping lid, conductive gasket or finger stock, screws every few centimetres;
- seams are slots — at 915 MHz a 10 mm gap leaks ≈ 24 dB, a 1 mm gap ≈ 44 dB (script §5); ten such gaps close together cost another ≈ 20 dB [6].
- feed coax through bulkhead SMA connectors and DC through feed-through capacitors; ventilate through holes that are short waveguides below cutoff (32 dB per diameter of length).

*Checking the box*: put a small battery transmitter (or the SDR-driven signal source) inside at fixed power; measure outside with an SDR + antenna at a fixed position, lid open vs closed: SE = difference. Expect 60–100 dB for a good die-cast box at UHF, 20–40 dB for a cookie tin.
*Radiated inside a box*: the box resonates (300 × 200 × 100 mm: 901, 1249, 1580 MHz; a 100 mm-radius tin: 1148 MHz, script §5) and the field varies with position; line it with absorber and use it only for relative "does it still work" tests. A TEM cell gives a calculable field ($E=\sqrt{PZ_0}/h$, 70.7 V/m for 1 W with h = 10 cm) and is the right fixture for immunity/emission pre-checks, if its S11 is good (≲ −15 dB) up to the test frequency [7].
*Simulating bad reception* (D1 #173): conducted set-up + a programmable step attenuator scripted to follow a fade profile (e.g. Rayleigh fades drawn from [multipath fading](../09-propagation-link-budget/multipath-fading-doppler.md)) — repeatable, unlike walking around a building.

### R6 — EBYTE module true output power and harmonics, safely
For the E22-400T33D (SX1268, 33 ± 0.5 dBm at 410–493 MHz, 0.85–1.2 A) and E220-900T30D (30 dBm, ≥ 5 V for full power) ([EBYTE modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)):
1. **Supply**: 5.0 V bench supply with ≥ 2 A, short thick leads; monitor the voltage *at the module pins* with a scope during a packet. A 5 V supply that sags to 4.65 V through a USB cable reduced output in one published test of a related EBYTE module [11] (blog — anecdotal).
2. **Pads**: never connect the analyser directly. E22: 20 dB rated ≥ 10 W, then 20 dB rated ≥ 2 W → −7 dBm out; the first pad dissipates 1.975 W while transmitting (script §6). Measure both pads' S21 at 433 MHz with a NanoVNA (expect 19.8–20.3 dB each; use the measured values). E220 (30 dBm): the same chain gives −10 dBm.
3. **Mode**: use a continuous-transmission/test mode if the firmware has one; otherwise send back-to-back maximum-length packets and use an RMS/average detector gated to the packet, or a thermal sensor with a duty-cycle correction ([power measurement Example 2](rf-power-measurement.md)).
4. **Power**: thermal/diode sensor after the pads (best), or tinySA Ultra in zero span with RBW ≥ 300 kHz ([spectrum analyzers Example 4](spectrum-analyzers.md)). Add back the measured pad loss. Repeat at each power setting (33/30/27/24 dBm) and at 4.5, 5.0 and 5.5 V. Expected: within ±0.5 dB of the setting if the supply holds; outside that, investigate.
5. **Harmonics**: the Singapore limits are −36 dBm below 1 GHz (2f = 866.25 MHz) and −30 dBm above 1 GHz (3f = 1299.4 MHz) ([IMDA rules](../19-regulations-safety/singapore-imda-rules.md)) → 2f must be ≤ −69 dBc and 3f ≤ −63 dBc. With −7 dBm at the analyser, the analyser's own 2nd harmonic (for an assumed second-order intercept of +35 dBm) is ≈ −49 dBm = −42 dBc: it cannot verify −69 dBc. Insert a high-pass filter (≥ 40 dB at 433 MHz, ≈ 1 dB at 866 MHz) after the pads: the fundamental at the analyser falls to −47 dBm, its own H2 to ≈ −129 dBm, while a DUT harmonic at the limit arrives at −77 dBm — 52 dB clear (script §6). Use RBW 100 kHz below 1 GHz and 1 MHz above, as the limits specify. Confirm "real vs analyser" with the 10 dB attenuator test.
6. **Uncertainty**: ±0.33 dB (k = 2) with a power sensor; ≈ ±1.5 dB with a tinySA alone (script §6). Report both the number and the uncertainty in the test log.
Pitfalls: a stuck-on TX into an under-rated pad; forgetting the DC block if the RF line carries bias; measuring into an antenna (radiates 2 W — only under a licence); comparing harmonics measured into 50 Ω with harmonics into a mismatched antenna (they rise; check through a coupler, [bring-up playbook](rf-bring-up-debug-playbook.md)).

### R7 — Antenna efficiency on a budget
**Wheeler cap** ([antenna measurement recipe D](../08-antennas/antenna-measurement.md)):
1. Build the cap: a closed metal box or tin with inner half-dimension ≥ λ/2π (433 MHz: 110 mm → a 220 mm cube; 915 MHz: 52 mm → 104 mm). Its first resonance is then ≈ 2.2 f (script §7) — check it by sweeping S11 of a small probe inside the empty cap; there must be no resonance within ±20 % of the test frequency.
2. Mount the antenna on its real ground plane (the flight board), cap sealed to the ground plane with copper tape; calibrate the VNA at the antenna feed (port extension or de-embedding — [fixtures](fixtures-and-deembedding.md)).
3. Measure $R_{free}$ (no cap, in a clear space) and $R_{cap}$ at series resonance (for a parallel-resonant antenna use conductances). η = 1 − R_cap/R_free.
4. Repeat 5–10 times with re-seating; report mean and spread.
Expected: a good PCB/chip antenna on an adequate ground plane 50–85 %; uncertainty ±1 % at R_free = 12 Ω, ±6 % at 2 Ω, ±14 % at 0.9 Ω for 0.1 Ω + 1 % resistance errors (script §7).
**Gain comparison (total efficiency incl. mismatch)**: on an outdoor range, compare received power from the antenna under test and from a reference dipole at the same position with an SDR (fixed gain, offset-tuned tone, [SDR as test equipment Example 1](sdr-as-test-equipment.md)); integrate several pattern cuts for an approximate TRP ([antenna range](antenna-range-ota-testing.md)). Expect ±1–3 dB from ground reflections unless the range is designed for it.

### R8 — Range testing with attenuators
1. Conducted path at either end: insert a calibrated step attenuator between the ground-station antenna and receiver (easiest) during a short-range LOS test at distance d (e.g. 200 m).
2. Increase attenuation until the packet error rate reaches the criterion (e.g. 10 %); record A.
3. Free-space equivalent range $d_{eq}=d\cdot10^{A/20}$: 43.5 dB at 200 m → 29.9 km (script §8, as in [antenna range Example 3](antenna-range-ota-testing.md)). If the test geometry is in the two-ray d⁻⁴ regime (low antennas, long ground path), the same 43.5 dB is worth only ×10^{A/40} — the free-space number applies to the rocket link because the flight path is elevated ([two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md)).
4. Uncertainty: attenuator error 0.5 / 1 / 2 dB → range error 5.9 / 12.2 / 25.9 % (script §8); add the PER statistics of a finite packet count ([noise-figure page](noise-figure-measurement.md)).
5. Leakage check: with the attenuator at maximum, the link must fail. If it still works, RF is going around the attenuator (cable braid, radio case) — the leakage must be ≥ A + 20 dB.

### R9 — Pulsed signals on a spectrum analyser (D1 #512)
1. Decide the display mode from RBW vs PRF: **line spectrum** if RBW < 0.3 PRF (preferably < 0.1 PRF) — individual lines spaced at the PRF, central line at $20\log(\tau PRF)$ below the pulse peak; **pulse spectrum** if RBW > PRF — a sinc-envelope traced by the pulses, peak display at $20\log(1.505\,\tau B)$ below the peak power [8].
2. Peak power from the pulse-spectrum display: add the desensitisation back. Example: 1 µs radar pulse at RBW 100 kHz → 16.4 dB; 0.5 µs (ADS-B-like) pulses at RBW 300 kHz → 12.9 dB (script §9). Conditions: τB < 0.2 (error 0.2 dB at 0.2), sweep slow enough, and the peak at the mixer below compression (AN 150-2 suggests ≈ −10 dBm for its analysers [8]).
3. Better: zero span with RBW ≥ 2/τ shows the pulse envelope and its peak directly; or use a peak power sensor.
4. Pulse width from the spectrum: the first nulls of the envelope are at ±1/τ from the carrier.

### R10 — Ferrite cores: A_L and complex permeability (D1 #256, #676)
1. Wind N = 3–10 turns of thin wire evenly around the toroid (few turns keep inter-turn capacitance low).
2. Measure Z = R + jX with a calibrated VNA/LCR at the frequencies of interest, in the impedance range where the VNA is accurate ([NanoVNA accuracy](nanovna-librevna-practical.md)); de-embed the leads (open/short at the fixture).
3. Compute $L_0=\mu_0N^2h\ln(OD/ID)/(2\pi)$ for the same winding in air; then μ' = X/(ωL₀), μ'' = R/(ωL₀). FT37 size (9.5/4.75/3.18 mm): $L_0/N^2$ = 0.44 nH; μ 800 → $A_L$ ≈ 353 nH/turn² (script §10). Synthetic example: 5 turns, Z = 30 + j140 Ω at 10 MHz → μ' ≈ 202, μ'' ≈ 43.
4. Identify an unknown core by comparing μ'(f), μ''(f) with vendor curves (mix 43, 61, 31…), and $A_L$ at low frequency with the catalogue ([ferrites](../04-real-components-hf/ferrites-and-beads.md), [magnetic materials](../02-electromagnetics/magnetic-materials-permeability.md)).
Pitfall: rods and gapped cores have an *effective* permeability far below the material μ; the toroid formula does not apply.

### R11 — Resonance and Q with coupled loops (dip-meter substitute)
The NanoVNA version of the [dip meter](basic-bench-instruments.md): it finds the resonance of an unconnected tank, trap, helical/cavity resonator or antenna element and, unlike a dipper, also gives Q.
1. Make two small loops (10–20 mm diameter, one turn of wire soldered across the end of a short coax pigtail). Calibrate the NanoVNA for S21 (thru) at the loop connectors.
2. **Transmission method**: one loop on CH0, one on CH1, each placed near the resonator's inductor (or its current maximum). Sweep around the expected f₀; the resonance is the S21 peak.
3. **Weak coupling**: move the loops away until the peak is ≤ −20 dB (better −30 dB) and the peak frequency stops moving as you move them further — closer loops pull the frequency (two coupled resonators split as $f_0/\sqrt{1\pm k}$) and load the Q.
4. Read $Q_L=f_0/\Delta f_{3\,dB}$ from the −3 dB points around the peak, then the unloaded Q
   $$Q_0=\frac{Q_L}{1-|S_{21}(f_0)|}$$
   (equal couplings; the correction is ×1.46 at 10 dB insertion loss, ×1.11 at 20 dB, ×1.033 at 30 dB). In a simulated 433.92 MHz resonator with Q₀ = 200 coupled to −18.7 dB, the 3 dB width gives Q_L = 176.7 and the formula returns 200.0 (`s10_bench_instruments.py` §E).
5. **One-loop method** (if you have only CH0): the resonance shows as a small dip in |S11| (or a peak in R). Q from the width of that dip is only approximate; use it for f₀.
6. Use narrow spans and enough points (the 3 dB width of a Q-200 resonator at 434 MHz is 2.2 MHz; at Q 10 000 it is 43 kHz — a 101-point sweep over 10 MHz misses it).
Pitfalls: metal and hands near the resonator detune it; the VNA's frequency reference error (±20 ppm = ±8.7 kHz at 434 MHz) matters for crystal and SAW resonators ([NanoVNA practical](nanovna-librevna-practical.md#calibration-practice--diy-kits-librecal-adapters-reference-and-the-73-ω-myth)).

### R12 — LCR meter or VNA?
| Instrument / method | Frequency | Impedance range where it is accurate | Use it for |
|---|---|---|---|
| Handheld/bench LCR meter (auto-balancing bridge) | typically 100 Hz–100 kHz (bench units to 1–110 MHz) | very wide, mΩ to ~100 MΩ [15] | bulk/decoupling C, bias chokes, DC resistance, electrolytics, D/ESR at low f |
| RF I-V impedance analyzer | ~1 MHz–1.8/3 GHz (edition-dependent) [15] | wide (mΩ–MΩ) | professional RF component characterisation |
| VNA reflection (NanoVNA) | 50 kHz–GHz | ≈ 5–500 Ω for < 10 % ([NanoVNA accuracy map](nanovna-librevna-practical.md)) | RF inductors, small caps at the operating frequency, SRF, Q |
| VNA series/shunt-through | 50 kHz–GHz | 20 Ω–100 kΩ / 0.05–50 Ω | ferrite beads, chokes / large capacitors, ESR, PDN |

The reactance a component shows depends on frequency: a 10 nH inductor is 6.3 mΩ at an LCR meter's 100 kHz (unmeasurable) and 27 Ω at 433 MHz; a 10 pF capacitor is 159 kΩ at 100 kHz and 37 Ω at 433 MHz; a 100 nF decoupling capacitor is 15.9 Ω at 100 kHz and 3.7 mΩ (reactance) at 433 MHz, where its ESL dominates (script §H). **Rule:** an LCR meter tells you the part's nominal value and low-frequency loss; the VNA tells you what the part does in the RF circuit (including the pads, ESL and self-resonance). For RF matching parts, measure at the operating frequency on a fixture ([fixtures](fixtures-and-deembedding.md)).

### R13 — Return loss with a return-loss bridge and an SA + tracking generator
1. Chain: tracking generator (or a tinySA in generator mode feeding a second analyzer, or an SA's TG output) → 6–10 dB pad → bridge input; bridge DUT port → DUT; bridge output → SA input. The pad improves the bridge's source match.
2. **Reference**: leave the DUT port open, store the trace; short it, store; average the two (this removes the first-order port-match error). That trace is 0 dB return loss.
3. **Directivity check**: terminate in your best load: the reading below the reference is the bridge's directivity D (good DIY bridges 30–40 dB at UHF).
4. **DUT**: RL = reference − reading. The true value lies in the band set by the bridge's leak $\delta=10^{-D/20}$: $|\Gamma|\pm\delta$. With D = 35 dB a 20 dB RL DUT reads 18.6–21.7 dB; D = 25 dB: 16.1–27.2 dB (script §F) — the same arithmetic as the SWR meter in R3.
5. It is a *scalar* measurement: no phase, no Smith chart, no error correction beyond the normalisation. Use it for "is this filter/antenna better than 15 dB RL across the band?"; use a VNA for matching.

### R14 — Resistive taps vs directional couplers
A **resistive tap** is a series resistor R from the main line to a 50 Ω instrument. On a matched 50 Ω line (node Thévenin ≈ 25 Ω):
$$C_{tap}\approx20\log_{10}\frac{50}{R+75},\qquad \text{added shunt load }(R+50)\ \Omega\ \text{on the line}.$$
1 kΩ: −26.6 dB coupling, line RL 32.7 dB (≈ 0.02 dB loss). 4.95 kΩ: −40 dB, RL 46 dB (script §G). Limits:
- **Not directional**: it samples the *total* voltage at that point (forward + reflected), so it cannot measure SWR or forward power on a mismatched line; it is fine for monitoring a waveform, spectrum or harmonics of a transmitter into a good load.
- **Parasitic capacitance** of the resistor (≈ 0.1–0.2 pF for 0402–0805) is in parallel with R: 0.15 pF is 1.16 kΩ at 915 MHz, so a "−40 dB" 4.95 kΩ tap couples −33 dB at 433 MHz and −27 dB at 915 MHz. Keep $R\ll1/(\omega C_p)$, use several resistors in series, or calibrate the tap vs frequency with a VNA.
- **Power**: the tap resistor sees the full line voltage (10 V rms at 33 dBm) but dissipates little (20 mW in 4.95 kΩ).
A **directional coupler** separates forward and reflected waves, with coupling flat over its band and directivity 20–40 dB ([couplers](../06-rf-circuits/couplers-dividers-combiners.md), [RF power](rf-power-measurement.md)). Use the coupler for power and SWR, the tap for "look at the signal".

### R15 — The NanoVNA as a receiver or spectrum analyzer
A NanoVNA's receivers are tuned with its own sweep: the internal LO sits a fixed IF away from the stimulus, and the narrow digital IF filter accepts only signals within a few kHz of that offset ([NanoVNA architecture](nanovna-librevna-practical.md)). An external signal is therefore seen only when the sweep passes it (and at its image), at an uncalibrated level, while CH0 keeps putting its −13 dBm stimulus into whatever is connected. Users who have tried SA-style firmware on NanoVNA hardware report poor sensitivity and input range (forum — anecdotal [16]). Conclusions:
- For a receiver/SA use a tinySA, the LibreVNA's specified SA mode ([7] in [VNA page](vna-fundamentals-calibration.md)), or an SDR ([SDR as test equipment](sdr-as-test-equipment.md)).
- The NanoVNA's real "receiver" uses are coherent: S21 through a DUT, coupled-loop resonances (R11), and its CW output as a low-level signal source.
- Never connect a transmitter or an antenna near a transmitter directly to CH1.

### R16 — Why WSPR/RBN (and RSSI) antenna comparisons mislead
WSPR and Reverse Beacon Network spots report an SNR (WSPR: in a 2.5 kHz reference bandwidth, 1 dB steps [17]) at many receivers over time. Comparing two antennas from spot lists mixes in:
- **Fading and propagation changes** of 10–20 dB on HF paths over minutes; even a Rayleigh-faded line-of-sight-free UHF path has a **5.57 dB** standard deviation in dB (script §I), much more than the 1–3 dB differences people try to resolve.
- **Different receivers, times and paths**: each spot depends on the receiver's noise and antenna and on the path's elevation angle; two antennas with different elevation patterns are "better" on different paths.
- **Selection and quantisation**: only decoded spots are reported (weak ones censored), and SNRs are rounded to 1 dB (adds 0.29 dB rms — minor).
**Statistics**: with paired differences of standard deviation σ_d, the 95 % half-width after n pairs is 1.96σ_d/√n. With independent Rayleigh fades (σ_d = 7.9 dB), ±1 dB needs **≈ 240 pairs**, ±3 dB ≈ 27; with rapidly alternating A/B slots (fades partly correlated, σ_d ≈ 3 dB assumed) ±1 dB needs ≈ 35 (script §I).
**Better method**: switch antennas on the *same* transmitter or receiver in rapid alternation (A/B every slot), use many receivers and long runs, analyse paired differences, report mean ± CI — or measure the antennas on a range against a reference ([antenna range](antenna-range-ota-testing.md)). The same trap applies to comparing two rocket telemetry antennas by ground-station RSSI during different flights or drives: orientation, roll and fading dominate; use conducted/attenuator tests (R8) and paired, simultaneous measurements.

### R17 — RF prototyping and construction (Manhattan, dead-bug, ugly, copper-clad, enclosures)
**Techniques** (classic amateur/lab methods, after Hayward, Campbell and Larkin [18]):
- **Ugly / dead-bug construction**: an unetched copper-clad board is the ground plane; components are soldered point-to-point above it, grounded leads straight to the copper, ICs glued upside down ("dead bug") with pins bent to the plane or to the parts. Fastest; excellent ground; parasitics set by lead length and height.
- **Manhattan**: small pads (punched or cut FR-4 squares/discs, or commercial pads) glued to the copper-clad as insulated nodes; parts bridge pad-to-pad or pad-to-plane. Tidier, robust and easy to modify; each pad adds capacitance to ground.
- **Copper-clad islands**: pads isolated by cutting the copper (knife, rotary tool, milling) — electrically similar to Manhattan.
- **Ordered PCB** (JLC 2- or 4-layer): reproducible, SMD-friendly, defined 50 Ω lines (0.359 mm masked microstrip on JLC04161H-7628; 0.918 mm masked CPWG on 2-layer 1.6 mm — [canonical widths](../00-math-foundations/canonical-values-and-conventions.md)); about a week's turnaround.
**Parasitics per technique** (script §A, `s10_construction_amp.py`):

| Element | Value | At 433 MHz |
|---|---|---|
| Wire lead at height h over the plane, $L=(\mu_0 l/2\pi)\ln(2h/r)$ | 10 mm at 3 mm (Ø 0.5 mm): 6.4 nH; 5 mm at 2 mm: 2.8 nH | 17 Ω; 7.5 Ω |
| SMD part flat on a pad, ~2 mm path at 0.5 mm | ≈ 0.55 nH | 1.5 Ω |
| JLC ground via (1.6 mm, to a plane) | 0.54 nH (canonical) | 1.5 Ω |
| 0402 MLCC mounted ESL | ≈ 0.4 nH | 1.1 Ω |
| Manhattan pad (parallel plate, FR-4 εr 4.5, before fringing) | 2.5 mm square on 1.6 mm: 0.16 pF; 5 mm disc on 1.6 / 0.8 mm: 0.49 / 0.98 pF | — |
| 0402 pad pair on a 4-layer board | ≈ 0.1–0.2 pF | — |

Lumped-element sizes: λ/20 at 433 MHz is 35 mm in air (19 mm in ε_eff 3.3 microstrip), so at 433 MHz construction errors are mostly *extra L and C*, not transmission-line effects; at 2.4 GHz every millimetre is a line.

**Worked comparison — the E22 harmonic low-pass** (7-pole 0.1 dB Chebyshev, ripple edge 500 MHz: shunt 7.52/13.35/13.35/7.52 pF, series 22.6/25.0/22.6 nH; script §B):

| Build | S21 at 434 MHz | 868 MHz (2f) | 1302 MHz (3f) | 3 GHz |
|---|---|---|---|---|
| Ideal | −0.08 dB | −47.5 dB | −75.6 dB | −128 dB |
| JLC 4-layer, 0402, one 0.54 nH via per shunt cap | −1.11 (−0.99 re-tuned) | −63.8 | −124 | −128 |
| Manhattan, 0805 caps on pads (1.5 nH ground, 0.6 pF pads) | −0.70 (−0.53 re-tuned) | −78.9 | −131 | −79 |
| Dead-bug, leaded caps with 2 × 5 mm leads (≈ 6.5 nH) | **−28.4** (−0.66 re-tuned) | −69.7 | −59.6 | **−6.5** |

What it shows: (1) series L in each shunt arm makes the capacitor look *larger* below its arm resonance ($C_{eff}=C/(1-\omega^2LC)$) — the dead-bug arms resonate at 0.54–0.72 GHz, which detunes the filter into a 28 dB passband loss until the capacitors are re-chosen as $C/(1+\omega^2LC)$; (2) the same arm resonances put notches in the stopband (here helping 2f/3f on the board builds) but above them the arms turn inductive and the filter **re-opens** — the dead-bug build passes 3 GHz at −7 dB; (3) circuit-model stopbands below ≈ −70 dB are not physical: input–output coupling and the enclosure cap real filters at ≈ 60–80 dB ([shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md)). Hence: at 433 MHz Manhattan with SMD parts soldered flat to the plane works well; leaded through-hole parts need leads cut to 1–2 mm; for anything that will fly, or above ~1 GHz, order the board.

**Construction rules**: ground shunt parts directly to the plane at the shortest path; keep parts within 1–2 mm of the plane; lay the circuit out in a straight line from input to output; mount SMA edge connectors soldered to the clad on both sides; separate high-gain stages with soldered copper or tin-plate partitions; decouple each supply entry with a feed-through capacitor or a 100 pF + 100 nF pair at the pad.
**Enclosures**: soldered tin-plate boxes (walls soldered continuously to the clad), lids with fingers or many screws; check the first box resonance $f_{110}=\tfrac c2\sqrt{a^{-2}+b^{-2}}$ — a 74 × 111 mm box resonates at 2.43 GHz, a 148 × 111 mm box at 1.69 GHz (script §E) — and add absorber or partitions if a mode falls near the operating frequency or its harmonics (R5).

## Practical notes
- **Protect, then calibrate, then measure**: DC block, pads rated for the worst case (stuck-on TX), filters for harmonics; reference-check every chain with a known source at the start and end of a session.
- **Pad calibration**: measure every pad and cable at the test frequency with a VNA and label it; nominal values can be off by 0.3–0.5 dB.
- **Swept-SA quirks** (D2 #205, D1 #514): the large signal at 0 Hz on a swept analyser is its own LO feeding through the first mixer — normal, and a convenient frequency marker; front-panel values step in 1-2-5 or 1-3-10 sequences (scale, RBW) by convention.
- **When "the amplifier doesn't amplify"** (D2 #340): check bias current against the datasheet, input/output DC blocks, supply decoupling, stability (oscillation shows as a line with no input and a current change) and whether the measurement instrument is overloading — then follow the [bring-up playbook](rf-bring-up-debug-playbook.md). Rocket telemetry "doesn't work" (D2 #443): R1 → R6 → R8, in that order.
- **Record everything**: instrument, firmware, settings, pad serials and calibration values, temperature, supply voltage — the uncertainty budget is only meaningful if the set-up can be reproduced.

## Common mistakes & misconceptions
1. **"A PA must have a 50 Ω output impedance to deliver its power."** PAs are designed for an optimum load; their output reflection can be large. Measure power vs load, not a conjugate match.
2. **Two-load measurements with loads close together** — the solution is ill-conditioned; spread the loads.
3. **Only resistive loads for a complex source** — the sign of X is undetermined; include a reactive load.
4. **Trusting an SWR meter below its directivity floor** — a meter with 20 dB directivity cannot distinguish SWR 1.0 from 1.2.
5. **"My box is a Faraday cage"** — one unsealed seam or an unfiltered USB cable sets the isolation; measure it.
6. **Absolute radiated measurements inside a small metal box** — cavity modes make them position-dependent; only relative tests are valid.
7. **Measuring a 2 W module's harmonics without a high-pass filter** — the analyser's own distortion swamps the −69 dBc you need to see.
8. **Under-rated first pad** — a 2 W pad at the output of a 2 W transmitter with a stuck PTT will fail (and change value as it heats).
9. **Reading a pulsed radar's peak power off the SA display directly** — add the desensitisation factor, or use zero span/a peak sensor.
10. **Wheeler cap on a sub-ohm antenna without repeat measurements** — the uncertainty exceeds the answer.
11. **Attenuation range tests with leaky set-ups** — always check that maximum attenuation kills the link.
12. **Coupling the loops (or a dip meter) tightly** to get a big peak — the frequency is pulled and Q_L is far below Q₀.
13. **Using a 100 kHz LCR reading for a UHF matching inductor** — at 433 MHz its value, Q and self-resonance are what matter.
14. **Treating a resistor tap as a directional coupler** — it measures total voltage, and its coupling rises with frequency through the resistor's capacitance.
15. **Expecting a NanoVNA to work as a spectrum analyzer** — its receivers follow its own sweep.
16. **"Antenna B got better WSPR reports, so it is 3 dB better."** Without many simultaneous paired comparisons, fading and path differences dominate.
17. **Dead-bug or leaded construction at UHF without shortening leads** — a few nH in a shunt capacitor detunes a 433 MHz filter and re-opens its stopband.

## How to simulate / verify
- `python3 tools/verify/e3_bench.py` (output `tools/verify/e3_bench_output.txt`, 33/33 PASS): two-load and four-load source impedance with Monte Carlo; ripple → |Γs| and cable lengths; directivity bounds and extraction; isolation rule, slot SE, waveguide-below-cutoff, box/tin resonances, TEM cell; EBYTE pads, harmonic requirement, analyser H2 with/without HPF, RSS and GUM budgets; Wheeler uncertainty and cap resonance; attenuator range; Gaussian-RBW pulse desensitisation vs exact integration; toroid A_L and μ', μ''; field strength.
- `python3 tools/verify/s10_bench_instruments.py` §D–I (R11–R16: coupled-resonator pulling, two-loop Q extraction on a simulated resonator, RLB reading range, resistive tap vs frequency, LCR vs RF reactances, Rayleigh-in-dB spread and A/B sample sizes) and `python3 tools/verify/s10_construction_amp.py` §A, §B, §E (R17: lead inductance, pad capacitance, LPF builds with/without compensation, box resonances) — ALL PASS.
- Related checks: `meas_power.py` (mismatch, pads, coupler directivity), `meas_sa.py` (detectors, LoRa on an SA), `meas_range.py` (range tests), `ant_measurement.py` (Wheeler sensitivity).
- Circuit-level checks of the load-pull-lite and coupler models: scikit-rf networks (load, line of variable length, coupler with finite directivity) reproduce the same ripple and reading circles.

## Open questions / gaps
- No team measurements yet; the first campaign should replace the expected values with measured E22/E220 power vs supply and setting, pad calibrations, box SE, SWR-meter directivity and a Wheeler-cap efficiency of the flight antenna.
- The analyser second-order intercept (+35 dBm), tinySA absolute accuracy (±1.5 dB) and module source match (|Γs| = 0.3) in R6 are assumptions; measure them (R2, R3 and a two-tone/harmonic check of the analyser).
- Bird-43-class accuracy (±5 % FS) and SE expectations for die-cast boxes (60–100 dB) are typical values, not from specific datasheets.
- The aperture rules (20 log(λ/2L), −20 log n) are app-note estimates whose coefficients vary between sources; a measured or simulated (openEMS) box would settle them for our enclosures.
- Hot-S22 and true load-pull of the EBYTE PAs were not attempted; only the linear load-pull-lite model is verified.

## Sources
1. Keysight, *Fundamentals of RF and Microwave Power Measurements* (AN 1449-1/-2/-3) and *Spectrum Analysis Basics* (AN 150) — power sensors, mismatch, uncertainty combination, SA architecture. (app notes; cited via [power](rf-power-measurement.md) and [SA](spectrum-analyzers.md) pages)
2. JCGM 100:2008, *Evaluation of measurement data — Guide to the expression of uncertainty in measurement (GUM)* — standard uncertainties, rectangular/U-shaped distributions, coverage factor. (standard; general use)
3. EBYTE, *E22-400T33D* and *E220-900T30D* user manuals (via [EBYTE modules page](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)) — power, current, supply requirements. (module manuals)
4. IMDA, *TS SRD* Table 1-a spurious-emission limits (via [Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md)). (standard)
5. H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley (2009), ch. 6 (shielding, apertures, waveguide below cutoff) — as summarised in secondary sources; not re-read. (textbook)
6. R. Brewer (Laird Technologies), "Design considerations for minimizing large aperture effects in shielding," *Interference Technology* (2002-04-06), https://interferencetechnology.com/design-considerations-for-minimizing-large-aperture-effects-in-shielding/ — SE = k log(λ/2L) with k 20–40; −20 log n for n holes within ≈ λ/2. (trade article; WebFetch summary)
7. M. L. Crawford, "Generation of standard EM fields using TEM transmission cells," *IEEE Trans. EMC* 16(4):189–195 (1974), doi:10.1109/TEMC.1974.303364 — 50 Ω matched cells, uniform field below the first higher-order mode. (peer-reviewed; abstract/citation)
8. Hewlett-Packard/Keysight, *Spectrum Analysis… Pulsed RF*, Application Note 150-2 (5952-1039), https://www.keysight.com/us/en/assets/7018-06767/application-notes/5952-1039.pdf (pdftotext read 2026-09-29) — line spectrum B < 0.3 PRF, α_L = 20 log(τ·PRF); pulse spectrum B > PRF, α_P = 20 log(τ·K·B), K ≈ 1.5, Bτ < 0.2, peak at mixer ≲ −10 dBm. (app note)
9. Keysight PNA/PNA-X help, "Hot S22 measurement," https://na.support.keysight.com/pna/help/WebHelp9_9/Tutorials/Hot_S22_Measurement.htm — S22 with drive applied. (manufacturer documentation; search summary)
10. M. P. Robinson et al., "Analytical formulation for the shielding effectiveness of enclosures with apertures," *IEEE Trans. EMC* 40(3):240–248 (1998). (peer-reviewed; cited, not re-read)
11. IZ7BOJ, "Power and current characterization on SX1268 LoRa module (E22-400M30S) — bad discoveries," blog (2022-06-07), https://iz7boj.wordpress.com/2022/06/07/power-and-current-characterization-on-sx1268-lora-module-bad-discoveries/ — supply sag 5 → 4.65 V through USB, OCP register wrap, tinySA + 30 dB pad. (blog — anecdotal)
12. H. A. Wheeler, "The radiansphere around a small antenna," *Proc. IRE* 47:1325–1331 (1959) (via [antenna measurement](../08-antennas/antenna-measurement.md)). (peer-reviewed)
13. ARRL, *The ARRL Handbook* (current ed.) — SWR/wattmeter practice, antenna analysers, station test practice. (handbook; general, not re-read)
14. This repository: `tools/verify/e3_bench.py`; `meas_power.py`, `meas_sa.py`, `meas_range.py`, `ant_measurement.py`; `s10_bench_instruments.py`, `s10_construction_amp.py`. (verification)
15. Keysight, *Impedance Measurement Handbook* 5952-1087, and *LCR Meters, Impedance Analyzers* selection guide 5952-1430E — auto-balancing bridge (mΩ to ~100 MΩ, to ~110 MHz), RF I-V (to 1.8–3 GHz by edition), reflection method most accurate near Z0. https://www.keysight.com/us/en/assets/7018-06840/application-notes/5952-1087.pdf (app note; search summary, ranges differ by edition)
16. EEVblog "nano vna" thread and circuitsonline forum threads (2019–2023) on running SA-style firmware on NanoVNA hardware — poor sensitivity/input range. (forum — anecdotal)
17. J. Taylor (K1JT) et al., *WSJT-X User Guide* — WSPR SNR referred to 2500 Hz, 1 dB resolution. https://wsjt.sourceforge.io/wsjtx-doc/wsjtx-main.html (software documentation; not re-read)
18. W. Hayward, R. Campbell, B. Larkin, *Experimental Methods in RF Design*, ARRL, 2003 — ugly/dead-bug and Manhattan construction, enclosures, measurement practice. (textbook; cited, not re-read)
