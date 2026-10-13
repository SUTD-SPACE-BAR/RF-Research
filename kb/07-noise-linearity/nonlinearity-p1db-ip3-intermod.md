---
title: Nonlinearity — harmonics, compression (P1dB), intercept points (IP2/IP3) and intermodulation
domain: 07-noise-linearity
slug: nonlinearity-p1db-ip3-intermod
tags: [nonlinearity, P1dB, IP3, IIP3, OIP3, IP2, intermodulation, IMD, harmonics, cross-modulation, AM-PM, cascaded-IIP3, two-tone-test, volterra, memory-effects, IM3-asymmetry, memory-polynomial, GMP]
prerequisites: [../00-math-foundations/decibels-and-log-units.md, ../00-math-foundations/complex-numbers-and-phasors.md, noise-figure-and-friis.md]
related: [volterra-series-and-nonlinear-analysis.md, dynamic-range-sfdr-blocking.md, receiver-cascade-analysis.md, ../06-rf-circuits/lna-design.md, ../06-rf-circuits/power-amplifiers.md, ../06-rf-circuits/mixers.md, ../06-rf-circuits/receiver-architectures.md, ../17-test-measurement/spectrum-analyzers.md, ../05-analog-electronics/data-converters-adc-dac.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Nonlinearity — harmonics, compression (P1dB), intercept points (IP2/IP3) and intermodulation

## Questions this page answers
- What is the 1 dB compression point, and why does gain drop at high input power?
- What is IP3 (third-order intercept point), and why do IM3 products rise 3 dB for every 1 dB of input?
- Is IIP3 always P1dB + 9.6 dB? Why do datasheets disagree with that rule?
- What is the difference between input-referred (IIP3) and output-referred (OIP3) figures?
- Which frequencies do intermodulation products land on — and can two other teams' transmitters create a signal on *my* channel?
- How do I compute the IIP3 of a chain of LNA + filter + mixer + ADC?
- What are IP2, cross-modulation and AM–PM conversion, and when do they matter?
- How do I measure IP3 without measuring my test setup instead?
- Why does IM3 change with tone spacing, and why are the lower and upper IM3 products sometimes different?
- What is a Volterra series, and how is the DPD memory polynomial related to it?

## TL;DR
- Model a weakly nonlinear, memoryless block as $y = a_1x + a_2x^2 + a_3x^3 + \dots$. With $a_3 < 0$ (compressive) the gain for a large tone falls as $a_1 + \tfrac34 a_3A^2$.
- **Pure cubic:** $A_\text{1dB} = \sqrt{0.145\,|a_1/a_3|}$, $A_\text{IIP3} = \sqrt{\tfrac43|a_1/a_3|}$ ⇒ **IIP3 − IP1dB = 9.64 dB** (single-tone P1dB vs per-tone two-tone IIP3). Verified symbolically and by FFT (`tools/verify/noise_ip3_twotone.py`).
- **The 9.6 dB rule is only a rule of thumb.** A tanh (differential-pair-like) characteristic gives 8.96 dB; a device biased near an IM3 "sweet spot" (cubic partly cancelled, compression set by higher orders) gave 13.5 dB; a characteristic with no cubic term (e.g. a Rapp-type limiter on the instantaneous voltage) has IM3 growing at 5 dB/dB and no meaningful IP3 at all. Always check the IM slope before extrapolating.
- **Two-tone measurement:** IIP3 = $P_\text{in} + \Delta/2$, where $\Delta$ = (fundamental − IM3) at the output in dB and $P_\text{in}$ is the per-tone input power. OIP3 = IIP3 + G.
- **IM3 frequencies:** $2f_1 - f_2$ and $2f_2 - f_1$ — close to the tones, inside the band, unfilterable. Two interferers at 433.500 and 433.875 MHz produce IM3 exactly on **433.125 MHz** (the EBYTE default channel).
- **Cascade (coherent, worst case):** $\frac{1}{IIP3_\text{tot}} = \frac{1}{IIP3_1} + \frac{G_1}{IIP3_2} + \frac{G_1G_2}{IIP3_3} + \dots$ (linear mW). Late stages dominate linearity — the mirror image of Friis for noise. Verified by a two-stage two-tone simulation to 0.01 dB.
- Other effects: IP2 ($f_2 - f_1$, 2:1 slope; critical in zero-IF), **cross-modulation** (a strong AM interferer's envelope transfers onto the wanted signal), **blocking/desensitisation** (a single strong tone reduces small-signal gain), **AM–PM** (phase shift vs drive; the dominant PA distortion in many amplifiers).

## Intuition (no math)
An ideal amplifier is a straight line: output = gain × input. Real devices bend: a transistor runs out of current or voltage swing, a diode conducts exponentially. Near the origin the bend is gentle and can be described by adding small squared and cubed terms to the straight line.

A **squared term** produces signals at twice the input frequency and at the sum and difference of any two input frequencies. The difference frequency ($f_2 - f_1$) is low; in a normal superheterodyne receiver it falls far outside the band and is filtered, but in a zero-IF receiver it lands right in the baseband.

A **cubed term** produces the third harmonic, but — more importantly — it produces products at $2f_1 - f_2$ and $2f_2 - f_1$. If $f_1$ and $f_2$ are two signals 375 kHz apart, these products are another 375 kHz either side: still inside the receive band, perhaps inside your channel. No filter after the nonlinearity can remove them. The cubed term also *reduces the gain* for large inputs (with the usual negative sign), which is compression.

Because the cubic products depend on input amplitude cubed, in dB they rise three times as fast as the input: 1 dB more input → 3 dB more IM3. Draw the output fundamental (slope 1) and the IM3 (slope 3) on a dB–dB plot; the straight-line extensions meet at the **third-order intercept point**. The real device compresses long before it reaches that point — IP3 is a *fictitious* extrapolation that summarises how strong the cubic coefficient is. A bigger IP3 means weaker intermodulation.

In a chain, nonlinearity accumulates at the *output* end: a stage late in the chain sees signals that have already been amplified by everything in front of it, so it is driven harder. The first stage dominates noise; the last stages usually dominate linearity. Receiver design is a negotiation between the two (see [dynamic-range-sfdr-blocking](dynamic-range-sfdr-blocking.md)).

## The math

### Level 1 — results
Symbols: $a_n$ polynomial coefficients (V¹⁻ⁿ); $A$ peak amplitude of each input tone (V); powers in dBm referred to a stated impedance.

| Quantity | Pure cubic ($a_3<0$) result |
|---|---|
| Gain of a single large tone | $a_1 + \tfrac34a_3A^2$ |
| 1 dB compression amplitude | $A_\text{1dB}^2 = \tfrac43(1-10^{-1/20})\,|a_1/a_3| = 0.145\,|a_1/a_3|$ |
| IIP3 amplitude (per tone) | $A_\text{IIP3}^2 = \tfrac43|a_1/a_3|$ |
| IIP3 − IP1dB | $10\log_{10}(\tfrac43/0.145) = 9.64$ dB |
| IM3 relative to fundamental | $\tfrac34|a_3|A^2/a_1$ |
| HD3 relative to fundamental | $\tfrac14|a_3|A^2/a_1$ (IM3 is 9.54 dB above HD3 at equal per-tone power) |
| IIP2 amplitude | $|a_1/a_2|$; IM2 ($f_2\pm f_1$) amplitude $a_2A^2$; HD2 $a_2A^2/2$ |

In log form (per-tone input $P_\text{in}$, dBm):
- $P_\text{IM3,out} = 3P_\text{in} - 2\,\text{IIP3} + G$, equivalently input-referred $P_\text{IM3,in} = 3P_\text{in} - 2\,\text{IIP3}$.
- $\text{IIP3} = P_\text{in} + \frac{P_\text{fund,out} - P_\text{IM3,out}}{2}$; $\text{OIP3} = \text{IIP3} + G$.
- $\text{IIP2} = P_\text{in} + (P_\text{fund,out} - P_\text{IM2,out})$; $P_\text{IM2,in} = 2P_\text{in} - \text{IIP2}$.

### Level 2 — derivation of the two-tone products
Put $x = A\cos\omega_1t + A\cos\omega_2t$ into $y = a_1x + a_2x^2 + a_3x^3$ and expand with $\cos^2\theta = \tfrac12(1+\cos2\theta)$, $\cos^3\theta = \tfrac14(3\cos\theta + \cos3\theta)$ and product-to-sum identities. The complete set of cosine amplitudes (from the symbolic expansion in the script, sympy) is:

| Frequency | Amplitude |
|---|---|
| DC | $a_2A^2$ |
| $\omega_1$ (and $\omega_2$) | $a_1A + \tfrac94a_3A^3$ |
| $2\omega_1$ | $\tfrac12a_2A^2$ |
| $\omega_2 \pm \omega_1$ | $a_2A^2$ |
| $3\omega_1$ | $\tfrac14a_3A^3$ |
| $2\omega_1 \pm \omega_2$ | $\tfrac34a_3A^3$ |

*Fundamental and compression.* The $\tfrac94a_3A^3$ term includes $\tfrac34a_3A^3$ (self-compression) and $\tfrac32a_3A^3$ (compression by the *other* tone). For a single tone only the $\tfrac34$ part exists, so the single-tone gain is $a_1 + \tfrac34a_3A^2$; setting $20\log_{10}(1 + \tfrac34a_3A^2/a_1) = -1$ gives $A_\text{1dB}^2 = \tfrac43(1 - 10^{-0.05})|a_1/a_3| = 0.145|a_1/a_3|$.

*Intercept.* Extrapolating the small-signal lines, IM3 amplitude equals the fundamental when $\tfrac34|a_3|A^3 = a_1A$, i.e. $A_\text{IIP3}^2 = \tfrac43|a_1/a_3|$. The ratio gives 9.64 dB. The same algebra with $a_2$ gives $A_\text{IIP2} = |a_1/a_2|$ (IM2 at $\omega_2-\omega_1$ has amplitude $a_2A^2$).

*Two-tone compression.* With both tones present the fundamental gain is $a_1 + \tfrac94a_3A^2$, so a two-tone test compresses by 1 dB at a per-tone amplitude 4.77 dB below the single-tone P1dB.

*Blocking / desensitisation.* A small wanted signal $A_w$ with a large blocker $A_b$: the wanted fundamental becomes $(a_1 + \tfrac32a_3A_b^2)A_w$. The small-signal gain drops by 1 dB when the blocker is 12.65 dB below $A_\text{IIP3}$ (= P1dB − 3.0 dB for the pure cubic), and goes to zero ("blocked") at $A_b^2 = \tfrac23|a_1/a_3|$, 3.0 dB below the IIP3 amplitude.

*Cross-modulation.* If the blocker is amplitude-modulated, $A_b(1 + m\cos\omega_mt)$, the wanted signal's gain acquires a term $\tfrac32a_3A_b^2\cdot2m\cos\omega_mt$: the wanted signal inherits a modulation index of about $(3a_3/a_1)A_b^2m$. This is the classic mechanism by which a strong AM (or pulsed, or TDMA) transmitter imprints its envelope on everything else in the front end — CDMA/LTE receivers suffer it from their own transmitter leakage.

### Level 3 — cascades, reality and limits of the model
**Cascaded IIP3.** Two stages, $y_1 = a_1x + a_3x^3$, $y_2 = b_1y_1 + b_3y_1^3$. Keeping third-order terms: $y_2 \approx a_1b_1x + (a_3b_1 + b_3a_1^3)x^3$. Because $A_\text{IIP3}^2 \propto |\text{linear}/\text{cubic}|$,
$$\frac{1}{A_\text{IIP3,tot}^2} = \frac{3}{4}\left|\frac{a_3b_1 + b_3a_1^3}{a_1b_1}\right| \le \frac{1}{A_\text{IIP3,1}^2} + \frac{a_1^2}{A_\text{IIP3,2}^2}.$$
In power terms (with $G_1 = a_1^2$):
$$\frac{1}{IIP3_\text{tot}} = \frac{1}{IIP3_1} + \frac{G_1}{IIP3_2} + \frac{G_1G_2}{IIP3_3} + \cdots\quad(\text{linear, e.g. mW}).$$
This is the **coherent worst case** (the cubic terms of each stage add in phase, as they do for memoryless real-coefficient stages). With reactive interstage networks and memory the IM3 phases differ and the contributions can partly cancel; some texts use a power-sum (RMS) variant $1/IIP3^2 = \sum(G/IIP3_i)^2$, which is less pessimistic. `noise_cascade.py` prints both; its time-domain two-tone simulation of two cubic stages (15 dB/−5 dBm and 10 dB/0 dBm) measures −15.42 dBm against −15.41 dBm predicted by the coherent formula. Second-order terms of the first stage interacting with second-order terms of the second stage also generate third-order products (neglected in the formula; usually small when interstage filtering removes $2f$ and $f_2-f_1$ components).

**Why "IIP3 ≈ P1dB + 9.6 dB" fails.** The derivation assumes the *same* cubic coefficient sets both compression and IM3 and that higher orders are negligible. Real devices violate this:
- Smooth saturating characteristics (tanh of a bipolar differential pair) include a compressive quintic that adds to compression: gap 8.96 dB (script).
- Class-AB and "sweet-spot" biased FETs have a small net cubic term (the $g_m''$ of the device crosses zero at some bias) while compression comes from the quintic and from clipping: gap 13.5 dB in the script's example; real amplifiers with feedback, derivative superposition or predistortion commonly show gaps well above 10 dB (general observation; verify per datasheet).
- Hard limiters / characteristics with no cubic term produce IM3 through fifth-order terms (5 dB/dB slope). The script's Rapp-type limiter shows a 5:1 slope — any "IP3" extrapolated from it with a 3:1 line is meaningless.
- Devices with memory (bias-network time constants, thermal effects, trapping in GaN) show IM3 that depends on tone spacing and asymmetric upper/lower IM3.
  Volterra kernels, the method of nonlinear currents and IIP3 vs tone spacing: [Volterra series](volterra-series-and-nonlinear-analysis.md).

**AM–AM and AM–PM.** For bandpass signals it is often more natural to describe the nonlinearity by its effect on the complex envelope: output amplitude vs input amplitude (AM–AM, compression) and output phase vs input amplitude (AM–PM). AM–PM arises from amplitude-dependent capacitances and conduction angle; it produces IM products and spectral regrowth even when AM–AM is benign, and it is why PAs for OFDM/QAM need digital predistortion. Saleh's model is a classic two-parameter fit for both. LoRa (constant envelope chirps) is immune to AM–AM/AM–PM in its own transmitter: its PA can run saturated, one reason LoRa modules like the E22 can deliver 2 W efficiently.

**Volterra series, memory effects and AM–PM — the theory under the power series and under DPD.** The power series above is memoryless: each output sample depends only on the same input sample. A real amplifier has reactances (bias networks, matching, junction capacitances), so its nonlinearity "remembers". The general weakly nonlinear, time-invariant model is the **Volterra series**
$$y(t)=\sum_{n\ge1}\int\!\!\cdots\!\!\int h_n(\tau_1,\ldots,\tau_n)\prod_{i=1}^{n}x(t-\tau_i)\,d\tau_i,$$
with frequency-domain kernels $H_n(f_1,\ldots,f_n)$. The power series is the special case $H_n = a_n$, constant. The full treatment is on [Volterra series and weakly nonlinear analysis](volterra-series-and-nonlinear-analysis.md) (W5-E11): kernel derivation, the method of nonlinear currents, the sweet spot, Saleh/Rapp, and DPD. Here are the three results this page's formulas need, each checked by `tools/verify/s7_volterra_memory.py`:
- *IM3 with memory.* Two tones of amplitude $A$ give $2f_1-f_2$ at $\tfrac34A^3H_3(f_1,f_1,-f_2)$, which reduces to $\tfrac34a_3A^3$ when memoryless. A common physical case is a second-order product $x^2$ that flows through an impedance $P(\omega)$ (bias network at the envelope frequency Δ, termination at 2ω) and is re-mixed with $x$. For $y=a_1x+a_3x^3+c\,x\,\{P*x^2\}$ the lower and upper IM3 phasors are
  $$L=\tfrac34a_3A^3+\tfrac c2A^3P^*(\Delta)+\tfrac c4A^3P(2\omega_1),\qquad U=\tfrac34a_3A^3+\tfrac c2A^3P(\Delta)+\tfrac c4A^3P(2\omega_2),$$
  which match an FFT simulation to < 0.05 dB (§1). Consequences: IM3 **depends on tone spacing** through $P(\Delta)$. In the script it went from −71.7 dB (narrow spacing, near cancellation) to −56.4 dB (wide) at A = 0.3, so an IIP3 measured at one spacing does not transfer to another. IM3 becomes **asymmetric** only when $P(\Delta)$ is complex *and* a $P(2\omega)$ term is present: with a pure one-pole envelope filter both sidebands stayed within 0.01 dB, while adding a 2ω-reactive path gave up to 20 dB asymmetry near the filter corner. A measured lower/upper difference therefore points at bias or supply decoupling and harmonic terminations, not at the device's static curve.
- *AM–PM.* For a single tone the fundamental gain is the describing function $G(A)=H_1+\tfrac34A^2H_3(f,f,-f)$. A memoryless real polynomial has real $H_3/H_1$, so it produces AM–AM and no AM–PM (verified to 10⁻⁹ rad). A complex $H_3$ makes the phase move with drive. For $y=a_1x+a_3x^2(g*x)$ with $g$ a 2-sample delay, $G=a_1+a_3A^2(\tfrac12G_g+\tfrac14G_g^*)$ gives +0.33°, +1.39° and +3.44° at A = 0.4, 0.8 and 1.2, with AM–AM of −0.15, −0.61 and −1.42 dB (§2, exact).
- *Memory polynomial = diagonal Volterra.* The DPD workhorse $\tilde y(n)=\sum_k\sum_m a_{km}\tilde x(n-m)|\tilde x(n-m)|^{k-1}$ keeps only the diagonal of the baseband Volterra kernels ($\tau_1=\tau_2=\tau_3$). It cannot represent envelope cross-memory such as $\tilde x(n)|\tilde x(n-m)|^2$, which is exactly what a bias network produces. Fitted to such a model with an OFDM-like drive, a 12-coefficient MP reached −40.8 dB NMSE, while the GMP with 6 lagging cross terms (18 coefficients) was exact (−291 dB) (§3). For third order and memory 4 the full Volterra needs 40 coefficients against MP's 4. MP and GMP are pruned Volterra series chosen to stay linear in their coefficients, so least squares fits them.

**Harmonics of a transmitter.** A saturated PA generates harmonics limited only by its output filter. For Marcus's systems: the E22-400T33D's 2nd harmonic (866 MHz) sits in the 868 MHz ISM band and near the 900 MHz link's band; its 3rd harmonic (1299 MHz at 433.125 MHz) is clear of GPS L2, but channels at 410.1–412.6 MHz put the 3rd harmonic at 1230–1238 MHz, inside the GPS L2 band (1227.60 MHz ± ~10 MHz), relevant to an L1/L2 receiver such as the ZED-F9P. The KB's canonical avoid-list with an F9P is **CH 0–9** (CH 0–3 → GPS L2, CH 4–6 → GLONASS L2 edge/inside, CH 7–9 → filter skirts); use **CH 24 = 434.125 MHz**, whose 3f (1302.4 MHz) clears the whole 1215–1300 MHz RNSS band and which also meets the Singapore band-edge rule ([21 interference](../21-gnss/gnss-interference-jamming-spoofing.md)). Check the module's spurious-emission spec and add a low-pass filter if the GNSS antenna is close.

**Passive intermodulation (PIM).** Connectors, ferromagnetic materials (nickel plating, steel), corroded joints and loose contacts are weakly nonlinear. PIM is the limiting IM3 source in systems that transmit and receive on one antenna (duplexers at cell sites). For a rocket with a 2 W transmitter and a GNSS receiver sharing a small airframe, PIM in the airframe's metal joints is a possible, rarely checked, interference source.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $P_\text{IM3,in} = 3P_\text{in} - 2\,\text{IIP3}$ | both tones equal, weakly nonlinear (≥ ~10 dB below P1dB) | −50 dBm tones, IIP3 −19 dBm → −112 dBm |
| IIP3 = $P_\text{in} + \Delta/2$ | two-tone test | measure at 2–3 levels to confirm 3:1 slope |
| OIP3 = IIP3 + G | small-signal gain | |
| IIP3 − IP1dB = 9.64 dB | pure cubic only | real: ~9–15 dB, device dependent |
| $1/IIP3 = \sum_i G_\text{before}/IIP3_i$ | coherent cascade, linear units | SAW + LNA(18 dB, +8 dBm) + SX1262(−5 dBm) → −18.9 dBm |
| $P_\text{IM2,in} = 2P_\text{in} - \text{IIP2}$ | 2nd order | zero-IF: IIP2 of +40…+60 dBm typical requirement (architecture dependent) |
| Desense 1 dB at IIP3 − 12.65 dB (pure cubic) | single strong blocker | ≈ P1dB − 3 dB |
| Two-tone 1 dB compression 4.77 dB below single-tone P1dB (per tone) | pure cubic | set test levels ≥ 10 dB below P1dB |

## Worked examples
**1 — Two other teams create a signal on my channel.** You receive at 433.125 MHz. Two other transmitters are on 433.500 and 433.875 MHz and arrive at your receiver at −50 dBm each. IM3 frequencies: $2(433.500) - 433.875 = 433.125$ MHz and $2(433.875) - 433.500 = 434.250$ MHz. The first lands on your channel. Input-referred IM3 level:
- Masthead LNA ahead of the module (cascade IIP3 ≈ −19 dBm, `noise_cascade.py` A2): $3(-50) - 2(-19) = -112$ dBm — 25 dB above SF12/BW125 sensitivity (−137 dBm): your weak rocket signal is wiped out.
- Module alone (IIP3 −5 dBm): −140 dBm — just below SF12 sensitivity (marginal).
- A front end with +5 dBm IIP3: −160 dBm — harmless.
Countermeasures: channel planning (avoid $2f_a - f_b$ coincidences), a narrow SAW/cavity filter before the LNA, less LNA gain, or a higher-IIP3 LNA. LoRa's co-channel rejection (5–19 dB depending on SF, SX1262) gives some tolerance to a CW-like IM3 product, but not 25 dB.

**2 — Cascade IIP3 of the 915 MHz station.** SAW (1.5 dB loss, IIP3 +35 dBm) → LNA (18 dB, IIP3 +8 dBm) → 10 m coax (2.6 dB) → SX1262 (IIP3 −5 dBm). Linear: $1/IIP3 = 1/3162 + 0.708/6.31 + 0.708\cdot63.1\cdot0.550/0.316$ ⇒ dominated by the last term ⇒ IIP3 ≈ −18.9 dBm (`noise_cascade.py`). The receiver chip's −5 dBm is pushed down by the ~13.9 dB of net gain in front of it: cascade IIP3 ≈ IIP3_last − G_before.

**3 — Measuring an LNA's IP3.** Two tones at −30 dBm each (well below P1dB), spaced 1 MHz. The analyzer shows fundamentals at −12 dBm and IM3 at −78 dBm: $\Delta$ = 66 dB, IIP3 = −30 + 33 = +3 dBm, OIP3 = +21 dBm (G = 18 dB). Repeat at −25 dBm: IM3 should rise to −63 dBm (3:1). If it rises by less, the measurement is limited by the analyzer's or the source's own IMD.

**4 — Pure-cubic numbers.** With $a_1 = 10$ (20 dB) and $a_3$ chosen for IIP3 = +10 dBm (in 50 Ω), the simulation gives IP1dB = +0.36 dBm, IIP3 = +10.00 dBm — the 9.64 dB gap — and the 1 dB desensitisation blocker level −2.65 dBm.

## Practical notes
- **Two-tone test hygiene:** combine two independent generators through a hybrid or a combiner with isolators/attenuators so the generators do not intermodulate each other; verify the setup's own IM3 by replacing the DUT with a through; use analyzer input attenuation changes (IM products that change when you add 10 dB of analyzer attenuation are generated *in the analyzer*). See [17-test-measurement/spectrum-analyzers](../17-test-measurement/spectrum-analyzers.md).
- **Tone spacing matters** for devices with memory and for bandwidth-limited interstage networks; measure at the spacings relevant to your interference scenario (e.g. 200 kHz–2 MHz for LoRa channel plans).
- **Report input or output referred explicitly.** Amplifier datasheets usually quote OIP3 and output P1dB; mixers and receivers usually quote IIP3 and input P1dB.
- **Filtering before the nonlinearity is the only cure** for out-of-band blockers; after the nonlinearity, in-band IM products are permanent.
- **LoRa modules** (E22, E220) with built-in LNAs do not publish their IIP3; assume ≤ the chip's −5 dBm (SX126x IIP3 is quoted for unwanted tones 1 and 1.96 MHz above the LO).

## Common mistakes & misconceptions
- **"IP3 is the power where the amplifier makes IM3 equal to the signal."** It is a fictitious extrapolation; the device compresses long before. Never drive a device to IP3.
- **Measuring IP3 too close to compression** (gives optimistic or pessimistic numbers and non-3:1 slopes) or too close to the noise floor.
- **Assuming IIP3 = P1dB + 10 dB** for design. Use measured IP3; the gap varies from under 9 to over 15 dB.
- **Mixing per-tone and total power.** IIP3 is defined with the *per-tone* input power; total two-tone power is 3 dB higher (and PEP 6 dB higher).
- **Using dB in the cascade IIP3 formula.** Linear mW only.
- **Forgetting that more LNA gain lowers system IIP3** one-for-one when a later stage dominates.
- **Ignoring IM2 in zero-IF / wideband receivers.** Any pair of strong signals separated by a frequency within the baseband creates IM2 at baseband directly.
- **Quoting one IIP3 for all tone spacings.** With memory (bias networks, harmonic terminations) IM3 varies by > 10 dB with spacing and the two sidebands can differ. Measure at the spacings of your interference scenario and report lower and upper IM3 separately (Level 3, Volterra).
- **"A memory polynomial is a full Volterra model."** It is the diagonal only. Envelope cross-memory needs GMP cross terms (−40.8 dB vs exact in the script).
- **Believing constant-envelope signals cause no intermodulation.** A single constant-envelope signal passes through a saturated PA cleanly, but *two* signals (two LoRa transmitters, or a LoRa signal plus a blocker) in one nonlinear front end still intermodulate.

## How to simulate / verify
- `tools/verify/noise_ip3_twotone.py` — sympy two-tone expansion; closed forms; FFT measurements on cubic, tanh, cubic+quintic and a limiter (no cubic term); IM2 slope and IIP2.
- `tools/verify/noise_cascade.py` — cascaded IIP3 (coherent and power-sum), and a two-stage time-domain check.
- `tools/verify/s7_volterra_memory.py` (≈ 3 s, ALL PASS) — closed-form envelope-memory IM3 phasors vs simulation, spacing dependence and asymmetry; AM–PM describing function; memory polynomial vs GMP least-squares fit. The full Volterra checks are in W5-E11's scripts listed on the [Volterra page](volterra-series-and-nonlinear-analysis.md).
- Harmonic-balance simulation (Qucs-S, ADS, AWR) with real transistor models gives IP3 vs bias; sweep bias to find sweet spots ([16-simulation-tools/rf-circuit-simulators-harmonic-balance](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)).
- SDR bench test: feed two generator tones into your receiver chain, record IQ, FFT and read the IM3 at $2f_1 - f_2$; step the input and check the slope.

## Open questions / gaps
- No manufacturer data for IIP3/P1dB of EBYTE E22/E220 receive paths; measure (two-tone test) before relying on channel-planning margins.
- Typical real-device IIP3 − P1dB gaps are stated qualitatively; a survey of MMIC LNA datasheets (domain 18) would quantify them.
- PIM of rocket airframe joints at 433/915 MHz is unexplored.

## Sources
1. B. Razavi, *RF Microelectronics*, 2nd ed., 2011, §2.2 (nonlinearity: harmonics, gain compression, cross-modulation, intermodulation, cascaded nonlinear stages). (textbook) — power-series derivations, 9.6 dB result, cascade formula.
2. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012, §10.3 (nonlinear distortion, IP3, dynamic range). (textbook)
3. T. H. Lee, *The Design of CMOS Radio-Frequency Integrated Circuits*, 2nd ed., 2004, ch. 13 (distortion, IP3, sweet spots). (textbook)
4. A. Jha, "3rd-order intercept point," Columbia Integrated Systems Lab notes (2006), http://www.columbia.edu/~ky2181/EE6314/iip3AJ.pdf. (lecture notes) — two-tone expansion, IIP3 = √(4a₁/3a₃).
5. Mini-Circuits, "RF Signal Quality Measurements: Third-Order Intercept Point (IP3) and Power at 1 dB Compression (P1dB)," Mini-Circuits blog; and AN-00-009 "Understanding Mixers – Terms Defined, and Measuring Performance." https://www.minicircuits.com/app/AN00-009.pdf (app note) — definitions, extrapolation method, mixer IP3.
6. A. A. M. Saleh, "Frequency-independent and frequency-dependent nonlinear models of TWT amplifiers," *IEEE Trans. Commun.* 29(11), 1715–1720 (1981). (peer-reviewed) — AM–AM/AM–PM model.
7. Semtech, *SX1261/2 Data Sheet*, Rev 1.2 (2019), Table 3-8: IIP3 −5 dBm (tones 1 and 1.96 MHz above LO), co-channel rejection 5 dB (SF7)/19 dB (SF12). (datasheet)
8. `tools/verify/noise_ip3_twotone.py`, `tools/verify/noise_cascade.py`, `tools/verify/s7_volterra_memory.py` (this KB).
9. M. Schetzen, *The Volterra and Wiener Theories of Nonlinear Systems*, Wiley (1980); P. Wambacq, W. Sansen, *Distortion Analysis of Analog Integrated Circuits*, Kluwer (1998). (textbooks; cited, not re-read) — Volterra kernels, method of nonlinear currents.
10. J. H. K. Vuolevi, T. Rahkonen, J. P. A. Manninen, "Measurement technique for characterizing memory effects in RF power amplifiers," *IEEE Trans. MTT* 49(8):1383–1389 (2001). (peer-reviewed; cited, not re-read) — envelope- and 2nd-harmonic-impedance memory, IM3 asymmetry.
11. J. Kim, K. Konstantinou, "Digital predistortion of wideband signals based on power amplifier model with memory," *Electronics Letters* 37(23):1417–1418 (2001); D. R. Morgan, Z. Ma, J. Kim, M. G. Zierdt, J. Pastalan, "A generalized memory polynomial model for digital predistortion of RF power amplifiers," *IEEE Trans. Signal Processing* 54(10):3852–3860 (2006). (peer-reviewed; cited as on the W5-E11 Volterra page) — MP and GMP.
