---
title: RF power amplifiers (classes A–F, load line, load-pull, Doherty, ET, DPD, thermal, ruggedness)
domain: 06-rf-circuits
slug: power-amplifiers
tags: [power-amplifier, pa, class-ab, class-c, class-e, class-f, load-line, cripps, load-pull, harmonic-filter, doherty, envelope-tracking, dpd, papr, back-off, ldmos, gan, thermal, vswr]
prerequisites:
  - amplifier-stability-and-biasing.md
  - ../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md
  - ../03-transmission-lines-matching/s-parameters.md
  - ../00-math-foundations/fourier-series-and-transform.md
  - ../05-analog-electronics/fets-mosfet-jfet-gaas-gan.md
related:
  - transmitter-architectures.md
  - rf-filters-lc-saw-baw-cavity-microstrip.md
  - couplers-dividers-combiners.md
  - circulators-isolators.md
  - detectors-and-power-meters.md
  - ../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md
  - ../10-comms-modulation/digital-modulation-psk-qam-fsk.md
  - ../13-pcb-rf-layout-emc/thermal-management-rf.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../19-regulations-safety/certification-fcc-ce-imda.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# RF power amplifiers

## Questions this page answers
- Why can a class A amplifier never exceed 50 % efficiency, and where does class B's 78.5 % come from?
- What do the class letters A, AB, B, C, D, E, F and inverse-F actually mean?
- Why is a PA not conjugately matched? What is the Cripps load line?
- What is load-pull, and why are the contours shaped like that?
- How do I pick the output matching network and harmonic filter for a 2 W 433 MHz transmitter?
- How do broadband (multi-octave) PAs work: resistive feedback gain blocks and transformer-coupled push-pull?
- What collector-to-collector load and transformer ratio does a push-pull HF PA need, and why does push-pull cancel even harmonics?
- How much harmonic suppression does a LoRa transmitter need to be legal?
- What is back-off, PAPR, and why does a QAM/OFDM PA run so inefficiently?
- How does a Doherty amplifier keep its efficiency at 6 dB back-off?
- What are envelope tracking and digital predistortion?
- Can a LoRa PA run saturated? (Yes — constant envelope.)
- How hot will my PA get, and what happens when the antenna breaks off (VSWR)?
- What sets the class-E component values, and why does the switch see 3.6 × Vcc?
- What is a Doherty offset line, and what happens if I get it wrong?
- What is class J, and why does it give class-B efficiency over an octave?
- How do I do load-pull on the bench without an automatic tuner?
- How do AM/AM and AM/PM turn into EVM, and why are my upper and lower IM3 products different?
- How much emitter ballast does a BJT PA need to avoid thermal runaway, and why does LDMOS quiescent current drift with temperature?
- What does neutralisation actually do to the transistor's two-port (stability, U)?
- Besides DPD, how else can a PA be linearised (feedforward, Cartesian feedback, LINC/outphasing, EER, envelope feedback), and when does each make sense?

## TL;DR
- **Efficiency** $\eta_D=P_{out}/P_{DC}$; **PAE** $=(P_{out}-P_{in})/P_{DC}$. For a transistor acting as a current source with conduction angle $\alpha$, the maximum drain efficiency is $\eta=\dfrac{\alpha-\sin\alpha}{4[\sin(\alpha/2)-(\alpha/2)\cos(\alpha/2)]}$: class A (360°) 50 %, class B (180°) π/4 = 78.5 %, class C (e.g. 120°) 89.7 % but −2.1 dB power and needing more drive (verified by FFT).
- **Switching/harmonic-tuned classes** shape voltage and current so they don't overlap: class F with a maximally flat 3rd-harmonic voltage and an ideal half-sine current (all even current harmonics present, i.e. even harmonics shorted) reaches 90.7 %; if only the 2nd (current) and 3rd (voltage) harmonics are controlled, the maximum is 81.6 % (Raab's table reproduced by LP optimisation; $\eta=\tfrac12(V_1/V_{dc})(I_1/I_{dc})$ = ½·1.155·π/2 or ½·1.155·√2); class E reaches 100 % ideally with one switch, a shunt capacitor and a detuned series resonator: $R=0.5768\,V_{CC}^2/P$, $\omega C_{sh}R=0.1836$, $X=1.1525R$, peak switch voltage ≈ 3.56 $V_{CC}$ (time-domain simulation confirms).
- **PAs are load-line matched, not conjugate matched**: $R_{opt}\approx(V_{DD}-V_k)^2/(2P)$. For a 7.5 V, 3.2 W LDMOS (NXP AFT05MS003N) this is 7.7 Ω; resonating its 23 pF output capacitance gives a required drain load ≈ 6.2 + j3.0 Ω vs the data sheet's measured 5.9 + j6.0 Ω at 430 MHz.
- **Load-pull contours** (Cripps): constant-R segments on the current-limited side, constant-G arcs on the voltage-limited side; the −1 dB contour is broad — power match is forgiving, efficiency and linearity contours are tighter.
- **Harmonics are a legal requirement**: under ETSI EN 300 220 a +33 dBm 433 MHz transmitter needs 2f₀ ≤ −36 dBm (−69 dBc) and 3f₀ ≤ −30 dBm (−63 dBc) [10]. A 7th-order Chebyshev LPF (fc 520 MHz) gives 44 dB at 866 MHz and 73 dB at 1299 MHz — enough together with a class-AB drain's own harmonic level.
- **Back-off kills efficiency**: at 6 dB back-off class A gives 12.6 %, class B 39.4 %, an ideal Doherty 78.5 %. LoRa/FSK are **constant envelope** (PAPR ≈ 0 dB) so they can run a saturated/class-E PA near peak efficiency; 16-QAM with 0.25 roll-off has ≈ 7 dB PAPR.
- **DPD** (memoryless 7th-order polynomial, indirect learning) on a Rapp model PA improved ACLR from −43 to −63 dBc and EVM from 2.5 % to 0.2 % in the verification script.
- **Thermal and ruggedness**: $T_j=T_a+P_{diss}\theta_{ja}$; a 1 W FEM (Skyworks SKY66122-11 at 5 V, 640 mA) dissipates 2.2 W in a 6 × 6 mm package. Rocket antennas can break or detune → design for high VSWR (AFT05MS003N: no degradation at > 65:1 [8]; SKY66122-11: no damage at 10:1 [9]).

- **Linearisation beyond DPD** (verified by `rf2_pa_linearisation.py`, two-tone Rapp + 15° AM/PM model):
  - *Feedforward:* the IM3 improvement equals the loop-2 cancellation $-20\log|1-ge^{j\varphi}|$, e.g. 0.1 dB / 1° → 34 dB, at about 1 dB of output-coupler loss.
  - *Cartesian feedback:* reduction ≈ loop gain at the IM offset (19 dB measured vs 21 dB predicted); the loop goes unstable once the loop-phase misalignment exceeds 90°.
  - *LINC with a Wilkinson combiner:* efficiency = 1/PAPR (21.5 % for 16-QAM).
  - *EER:* the envelope bandwidth must be several times the signal's (3× tone spacing gave only −30 dBc).
  - *Envelope (amplitude-only) feedback:* barely helps when AM/PM dominates (−34.6 → −35.4 dBc).

- **Broadband and practice (W5-S15, verified):**
  - *Feedback gain block:* $R_fR_E=Z_0^2$ gives a matched gain of exactly $(Z_0-R_f)/Z_0$.
  - *Push-pull:* $R_{cc}=2(V-V_k)^2/P$ (12.5 V, 20 W → 13.2 Ω, a 1:4 TLT), and even harmonics cancel to −28 dBc at 0.5 dB/5° imbalance.
  - *Doherty offset lines:* a 90° error costs ≈ 17 efficiency points at −6 dB.
  - *Class J:* $Z_1=R_{opt}(1+j\alpha)$, $Z_2=-j\frac{3\pi}{8}\alpha R_{opt}$ keeps 78.5 % for |α| ≤ 1, at the cost of a 2.91 V_dc peak.
  - *IM3 asymmetry* needs memory.
  - *Ballast* for a loop gain of ≈ 0.3, not merely < 1.
  - *Neutralisation* zeroes y12 without changing U.

## Intuition (no math)
A power amplifier is a valve controlling the flow of DC energy into the load. The energy that doesn't reach the load becomes heat in the transistor, and the heat produced at any instant is (transistor voltage) × (transistor current). To be efficient the transistor must never have large voltage and large current *at the same time*.

In class A the transistor conducts all the time, carrying a steady DC current with the signal riding on it; half the DC power is always heat, even at full swing. In class B the transistor conducts only during the half-cycle when current is needed and is off otherwise, so less time is spent in the "voltage and current both present" state. Class C shortens the conduction even further: the current flows in brief pulses at the moment the voltage is lowest. Efficiency rises, but the pulses contain less fundamental, so you get less power for a given peak current, and the output amplitude no longer follows the input amplitude — class C is only for constant-envelope signals.

Switching classes (D, E) treat the transistor as a switch: on (current, no voltage) or off (voltage, no current). The only loss is in the transition. Class E adds a clever load network that makes the switch voltage fall to zero *by itself* just before the switch closes, so even the transition is lossless. Class F instead adds harmonics — a tuned network that is open at the 3rd harmonic and short at the 2nd — so the voltage flattens into something like a square wave while the current is a half sine: they "take turns".

Why not conjugate-match the output for maximum power transfer? Because a transistor is not a signal generator with an internal resistance that must be matched — it is a current source limited by *peak current* and *peak voltage*. The load that uses both limits fully is the "load line" resistance $R_{opt}$, typically a few ohms for a few watts at a few volts, much lower than the transistor's output resistance. Matching to the output resistance would saturate the voltage long before the current is used, and deliver much less power.

## The math

### Level 1 — definitions
- Drain efficiency $\eta_D=P_{out}/P_{DC}$; power-added efficiency $\text{PAE}=(P_{out}-P_{in})/P_{DC}=\eta_D(1-1/G)$.
- Output back-off (OBO) = $P_{max}/P_{avg}$ in dB; peak-to-average power ratio PAPR = $\max|x|^2/\overline{|x|^2}$.
- Load-line resistance (class A/AB/B, voltage swing $V_{DD}-V_k$ where $V_k$ is the knee voltage):
$$R_{opt}=\frac{V_{DD}-V_k}{I_{max}/2},\qquad P_{out}=\frac{(V_{DD}-V_k)^2}{2R_{opt}}$$
- Class definitions by conduction angle $\alpha$ (portion of the RF cycle during which the device conducts, in a current-source model): A 360°, AB 180–360°, B 180°, C < 180°. Switching classes: D (voltage-switching pair, square voltage), E (single switch + load network with zero-voltage and zero-slope switching), F (harmonic-tuned: odd voltage harmonics, even current harmonics), inverse F (roles swapped).

### Level 2 — derivations

**(a) Reduced conduction angle.** Let the drain current be a truncated cosine of peak $I_{max}$ and conduction angle $\alpha$ (half-angle $h=\alpha/2$):
$$i(\theta)=I_{max}\frac{\cos\theta-\cos h}{1-\cos h}\ \ (|\theta|<h),\qquad 0\ \text{otherwise}.$$
Its Fourier coefficients are
$$I_{DC}=\frac{I_{max}}{2\pi}\frac{2\sin h-\alpha\cos h}{1-\cos h},\qquad I_1=\frac{I_{max}}{2\pi}\frac{\alpha-\sin\alpha}{1-\cos h}.$$
With a tuned load (all harmonics shorted) the voltage is sinusoidal with amplitude up to $V_{DD}$ (ignoring the knee), so $\eta=\frac{1}{2}\frac{V_1I_1}{V_{DD}I_{DC}}=\frac{1}{2}\frac{I_1}{I_{DC}}$, which gives the TL;DR formula [1 ch.3][2]. Results (verified to $10^{-9}$ against an FFT, check A1):

| α | η max | $P_1$ vs class A (same $I_{max}$) | 2nd harmonic $I_2/I_1$ | 3rd $I_3/I_1$ |
|---|---|---|---|---|
| 360° (A) | 50.0 % | 0 dB | — | — |
| 270° (AB) | 60.2 % | +0.55 dB | −21.7 dB | −24.7 dB |
| 240° (AB) | 66.1 % | +0.61 dB | −15.3 dB | −21.3 dB |
| 180° (B) | 78.5 % | 0 dB | −7.4 dB | 0 (no odd harmonics) |
| 150° (C) | 84.4 % | −0.82 dB | −4.9 dB | −16.7 dB |
| 120° (C) | 89.7 % | −2.14 dB | −3.0 dB | −9.1 dB |

Notice that class AB gives *slightly more* fundamental than class A for the same peak current, and that the current harmonics become large as α shrinks — they must be shorted by the output network, or they appear as voltage harmonics (distortion, lost efficiency, regulatory trouble). The harmonic content also sets how much filtering you need.

**(b) Class F and inverse F.** If the drain voltage may contain harmonics, efficiency is $\eta=\frac12\frac{V_1}{V_{DD}}\frac{I_1}{I_{DC}}$ subject to $v(\theta)\ge0$ (device cannot swing below zero/knee) and $i(\theta)\ge0$. Maximising the fundamental of a non-negative waveform using only a given set of harmonics is a linear program; solving it (check B) reproduces Raab's classical results [3]:

| Voltage harmonics ↓ / current harmonics → | {1} | {1,2} | {1,2,4} | half-sine (∞) |
|---|---|---|---|---|
| {1} ($V_1/V_{DD}$ = 1) | 50.0 % | 70.7 % | 75.0 % | 78.5 % |
| {1,3} (2/√3 = 1.155) | 57.7 % | 81.6 % | 86.6 % | 90.7 % |
| {1,3,5} (1.207) | 60.4 % | 85.4 % | 90.5 % | 94.8 % |
| square (4/π = 1.273) | 63.7 % | 90.0 % | 95.5 % | 100 % |

Key facts: the optimum third-harmonic-peaked voltage has $V_1/V_{DD}=2/\sqrt3$ (not the "maximally flat" 9/8); the optimum two-harmonic current has $I_1/I_{DC}=\sqrt2$. Output power also rises (by the same factors) for a given $V_{DD}$ and $I_{max}$. Inverse class F swaps the roles (even voltage harmonics, odd current harmonics) and has the same table. In practice only the 2nd and 3rd harmonics are controlled because package parasitics make higher-harmonic terminations uncontrollable [1][2].

**(c) Class E.** Topology: DC feed choke → switch with shunt capacitance $C_{sh}$ (the transistor's $C_{oss}$ can be part of it) → series inductor + series resonator ($L_0C_0$ tuned to $f_0$ with loaded Q $Q_L$) with an **excess inductive reactance $X$** → load $R$. Conditions (Sokal & Sokal [4]): when the switch closes, the switch voltage is zero (no $\frac12CV^2$ discharge loss) *and* its slope is zero (tolerant of timing/parasitics). For 50 % duty cycle and $Q_L\to\infty$, Raab's exact analysis [5] gives
$$R=\frac{8}{\pi^2+4}\frac{V_{CC}^2}{P}=0.5768\frac{V_{CC}^2}{P},\quad \omega C_{sh}R=\frac{8}{\pi(\pi^2+4)}=0.1836,\quad X=\frac{\pi(\pi^2-4)}{16}R=1.1525R,$$
with peak switch voltage $3.56V_{CC}$ and peak switch current $2.86I_{DC}$. Because the shunt capacitance is fixed by $R$ and $\omega$, a device's own $C_{oss}$ sets a **maximum class-E frequency** for a given power and supply: $f_{max}=0.1836/(2\pi C_{oss}R)$. Sokal gives polynomial corrections for finite $Q_L$ [4]. The verification script simulates the ideal circuit (433 MHz, 7.5 V, 2 W, $Q_L=10$): $P_{out}$ 2.09 W, efficiency 99.9 %, switch voltage at turn-on 4 % of $V_{CC}$, peak $3.74V_{CC}$ (the 5 % excess vs 3.56 is the finite-$Q_L$ effect).

**(d) Cripps load-pull contours.** Model the device as a current source limited to fundamental current $I_m=I_{max}/2$ and fundamental voltage $V_m=V_{DD}-V_k$. With load $Z=R+jX$, the fundamental current is $I=\min(I_m,V_m/|Z|)$, so
$$P(Z)=\tfrac12R\min\!\left(I_m^2,\ \frac{V_m^2}{|Z|^2}\right).$$
Inside the circle $|Z|<R_{opt}=V_m/I_m$ the device is current-limited and $P=\frac12I_m^2R$: constant power ⇔ **constant R** (a vertical segment). Outside it is voltage-limited and $P=\frac12V_m^2\,\mathrm{Re}(1/Z)$: constant power ⇔ **constant conductance G** (an arc). The −1 dB contour for the 3.2 W example is the R = 6.1 Ω segment (|X| < 4.7 Ω) joined to the G = 104 mS (1/G = 9.6 Ω) arc (checks D2–D3) [1 ch.2]. Real load-pull contours are ellipse-like because of knee softness and device parasitics, but this construction explains their shape and orientation, and why a PA's optimum load has nothing to do with $S_{22}^*$.

**(e) Back-off efficiency.** For class A the DC power is constant, so $\eta=0.5\,P/P_{max}$. For class B $I_{DC}\propto V_1$, so $\eta=\frac{\pi}{4}\sqrt{P/P_{max}}$ (= 39.4 % at 6 dB back-off). With a signal of PAPR $p$, the average efficiency is the efficiency curve averaged over the envelope distribution, roughly the value at $P_{max}/p$ when the PA is set so that peaks just reach saturation.

**(f) Doherty.** Two devices: a main (carrier) PA biased class B and a peaking PA biased class C that turns on at half the input amplitude, combined through a quarter-wave line of impedance $Z_0=R_{opt}$ into a common load $R_{opt}/2$. The λ/4 line is an impedance inverter: as the peaking PA injects current, the load node voltage rises and the impedance seen by the main PA through the inverter falls from $2R_{opt}$ to $R_{opt}$ — **active load modulation** — keeping the main PA at full voltage swing (maximum efficiency) over the top 6 dB. With normalised drive $x$:
$$\eta(x)=\frac{\pi}{2}x\ \ (x\le\tfrac12),\qquad \eta(x)=\frac{\pi}{2}\frac{x^2}{3x-1}\ \ (x>\tfrac12)$$
giving 78.5 % at full power and at 6 dB back-off, dipping to 69.8 % at $x=2/3$ (verified by an explicit current-source/inverter model, checks E1–E3) [6][2]. Asymmetric Doherty (larger peaking device) moves the second peak to 9–12 dB back-off.

### Level 3 — linearity, memory, and system-level techniques
- **AM/AM and AM/PM.** A PA's gain compresses and its phase shifts with envelope amplitude (Saleh/Rapp models). For constant-envelope signals (FM, FSK, GFSK, LoRa CSS — whose amplitude is constant by construction, see [LoRa PHY](../15-lora-ism-radios/lora-phy-css-math.md)) neither matters: the PA can run saturated. For QAM/OFDM they create spectral regrowth (ACLR) and EVM. Link to [nonlinearity](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md) for P1dB/IP3 definitions.
- **Digital predistortion (DPD):** precede the PA with the inverse nonlinearity. Memoryless polynomial $z=\sum_ka_kx|x|^{k-1}$ (odd orders), or the **memory polynomial** $z(n)=\sum_{k}\sum_m a_{km}x(n-m)|x(n-m)|^{k-1}$ that also corrects thermal/bias-network memory effects [7]. Coefficients are learnt from the PA output via a feedback receiver, commonly with **indirect learning** (fit a post-inverse, copy it in front). Bias networks with long time constants create memory; wideband bias decoupling ("video bandwidth") reduces it (see the GaN bias notes in [stability & biasing](amplifier-stability-and-biasing.md)).
  Theory behind the memory polynomial (Volterra kernels, behavioural models, when memory DPD pays): [Volterra series](../07-noise-linearity/volterra-series-and-nonlinear-analysis.md).
- **Envelope tracking (ET) / envelope elimination and restoration (EER, Kahn):** modulate the supply with the envelope so the PA is always near saturation. System efficiency = PA efficiency × supply-modulator efficiency; the modulator needs bandwidth several times the signal bandwidth. Polar transmitters are the limit case (see [transmitter architectures](transmitter-architectures.md)).
- **Outphasing (Chireix/LINC)**: two constant-envelope PAs whose phase difference encodes amplitude, combined with a reactive (Chireix) combiner.
- **Load-line vs harmonic-tuned vs switching in real devices:** above ~1–2 GHz the output capacitance and package inductance dominate; "continuous" class B/J modes trade harmonic reactance against fundamental reactance for broadband operation [1].
- **Large-signal stability:** PAs can oscillate parametrically or at low frequency under drive even when small-signal stable; see [stability](amplifier-stability-and-biasing.md#level-3--invariants-hidden-instabilities-and-limits-of-the-two-port-view).
- **Ruggedness:** into a mismatch the drain voltage peak can reach $V_{DD}(1+|\Gamma|)$-scaled values and the current or dissipation can rise; LDMOS/GaN devices specify survival at stated VSWR/phase/drive. Protection: isolators/circulators ([circulators](circulators-isolators.md)), reflected-power detection with power foldback ([detectors](detectors-and-power-meters.md)), drain-current limiting, thermal shutdown.

### Level 3 — linearisation beyond DPD
All the results below come from `tools/verify/rf2_pa_linearisation.py`. It uses a complex-baseband two-tone test on a Rapp PA (p = 2) with 15° of AM/PM at saturation: −26.7 dBc IM3 at 0.45 per tone and −34.6 dBc at 0.30 per tone open loop.

**(a) Feedforward** (Black 1928; Seidel 1971 [14][15]).
- *Loop 1* samples the main PA output, scales it by 1/G, delays the input to match, and subtracts the two. What remains is only the PA's distortion (the error signal).
- *Loop 2* amplifies the error in a clean, class-A *error amplifier*, delays the main output to match, and subtracts the amplified error at the output coupler.
- If loop 2's gain and phase match to within g (linear ratio) and φ, the distortion is reduced by the cancellation
$$C=-20\log_{10}|1-g\,e^{j\varphi}|,$$
i.e. 0.1 dB / 1° → 33.5 dB, 0.3 dB / 3° → 23.9 dB, 1 dB / 10° → 13.1 dB. The simulation gave 34.3 / 24.7 / 14.0 dB.
- Feedforward is open-loop, so it is unconditionally stable and wideband (it corrects memory effects and wide signals). But it needs matched delays, temperature-tracking gain/phase (usually with pilot-tone or adaptive control), and it costs efficiency. The output coupler and delay line cost about 1 dB of main-path power (a 10 dB coupler plus 0.5 dB of line: ×0.80 efficiency), and the error amplifier draws class-A power. Its niche is multi-carrier base-station PAs that need 25–35 dB of IM suppression over tens of MHz [16].

**(b) Cartesian feedback** (Petrovic & Smith [17]; Johansson & Sundström [18]).
- Down-convert a sample of the PA output with the *same* LO as the up-converter, compare I and Q with the input in baseband, and integrate the error into the modulator.
- Distortion inside the loop bandwidth falls by $|1/(1+L(j\omega))|$. For a first-order loop of crossover $f_c$ that is $\approx f/f_c$ at offset f: 50 kHz crossover, IM3 at 4.6 kHz → 20.8 dB predicted, 19.2 dB simulated.
- The demodulator's LO phase must be aligned with the forward path. A misalignment θ rotates the loop gain, and the real part of the closed-loop pole becomes $-K\cos\theta$. The loop is stable at 80° and **diverges at 100°** (small-signal simulation), so practical loops align to within about ±30–45° and re-calibrate.
- Near saturation the PA's incremental gain falls, and so does the loop gain. At 0.45 per tone the improvement dropped to 14 dB. Feedback cannot make the PA exceed its saturated power.
- It suits narrowband (≤ ~100 kHz) linear transmitters (TETRA-era PMR, SSB) where DPD's feedback receiver would be no simpler.

**(c) LINC / outphasing** (Chireix 1935; Cox 1974 [19][20]).
- Split $s=Ae^{j\phi}$ into two constant-envelope signals $\frac{A_{max}}2e^{j(\phi\pm\theta)}$ with $\cos\theta=A/A_{max}$. The decomposition is exact (simulation error < 10⁻⁹). Each branch can then use a saturated, efficient PA.
- *Matched (Wilkinson) combiner:* linear, but the combining efficiency is $(A/A_{max})^2$ (25 % at half amplitude), so the average efficiency is the PA efficiency × **1/PAPR**: 21.5 % for 16-QAM with 6.7 dB PAPR ([combiners](couplers-dividers-combiners.md#level-3--the-non-ideal-wilkinson-and-incoherent-combining)).
- *Chireix (lossless) combiner:* compensating reactances make the outphasing load-modulate both PAs, as in a Doherty. Efficiency peaks at chosen back-off angles, but the combiner is no longer linear, so it is usually paired with DPD.
- The branch signals need several times the original bandwidth, and the branches must match in gain and phase: an imbalance leaks an un-cancelled "quadrature" error at low amplitudes.

**(d) EER (Kahn) and envelope tracking.**
- *EER* limits the RF path (phase only) and restores the envelope through the supply. Reconstruction is exact only if the envelope path has enough bandwidth and the right delay. Simulated two-tone IM3: −50 dBc at an envelope bandwidth of 10× the tone spacing, −30 dBc at 3×. A 2 µs delay with unlimited bandwidth gave −73 dBc at 3 kHz spacing. The error scales with (delay × envelope bandwidth), as in [polar transmitters](transmitter-architectures.md#level-2).
- *Envelope tracking* relaxes both requirements by keeping the PA linear and only shaving supply headroom, and it is usually combined with DPD [2].

**(e) Envelope (amplitude) feedback and adaptive bias.**
- A detector compares the output envelope with the input envelope and corrects the gain. This removes AM/AM only. With 15° AM/PM the IM3 improved from −34.6 to only −35.4 dBc; the same correction on a PA without AM/PM reached −179 dBc (numerical floor). Envelope feedback therefore suits PAs whose distortion is mostly AM/AM (BJT/LDMOS well below saturation). Polar loops add a phase loop to handle AM/PM.
- *Adaptive bias* (raise the quiescent current with the envelope) improves back-off efficiency and can reduce a class-AB "gain expansion" bump, at the cost of bias-network memory ([biasing](amplifier-stability-and-biasing.md)).

**(f) Which to choose.**

| Technique | Corrects | Bandwidth | Efficiency impact | Complexity | Typical use |
|---|---|---|---|---|---|
| DPD (memory polynomial) | AM/AM, AM/PM, memory | wide (sample rate) | best | DSP + feedback Rx | almost everything modern |
| Feedforward | everything in loop 2 | very wide | −1 to −3 dB | RF, delay lines, adaptation | multi-carrier BTS (legacy) |
| Cartesian feedback | AM/AM, AM/PM | narrow (loop BW) | small | analog, phase alignment | narrowband PMR, SSB |
| LINC (Wilkinson) | — (linear by construction) | needs wide branch BW | 1/PAPR × PA η | two PAs, balance | research, mm-wave |
| Chireix outphasing | needs DPD | moderate | high in back-off | as LINC + combiner design | base stations, CMOS PAs |
| EER / polar | AM restored via supply | envelope BW ≥ 5–10× | high | fast supply modulator | polar transmitters |
| Envelope feedback | AM/AM only | moderate | small | detectors | older linear amps |

For Space Bar radios (LoRa/FSK, constant envelope) none of this is needed: run the PA saturated and filter the harmonics. It becomes relevant for a QAM/OFDM video downlink or a wideband SDR transmitter.

### Level 3 — broadband PAs: resistive feedback and transformer-coupled push-pull
The PAs above are tuned: their matching networks and harmonic filters cover 10–20 %. HF/VHF transmitters, test amplifiers and drivers for wideband SDRs instead use two classic multi-octave techniques. Numbers are from `tools/verify/s15_tlt_splitter.py` §D–E.

**(a) Shunt-series feedback gain block.** A transistor has an emitter resistor R_E (series feedback) and a collector-to-base resistor R_f (shunt feedback). Model it as a transconductance $g'=g_m/(1+g_mR_E)$. The two-port then has $y_{11}=y_{22}=1/R_f$, $y_{12}=-1/R_f$ and $y_{21}=g'-1/R_f$. Converting to S-parameters shows that both ports are matched when $g'=R_f/Z_0^2$, i.e. **$R_fR_E=Z_0^2$** in the high-g_m limit, and the gain is then **exactly** $S_{21}=(Z_0-R_f)/Z_0$ (derived here; checked to 0.01 dB in ngspice with a VCCS, check D1).
- R_f = 250/500/1000 Ω with total R_E = 10/5/2.5 Ω gives 12.0/19.1/25.6 dB, with reverse isolation S12 of −15.6/−20.8/−26.4 dB.
- With a BJT model (12 V, I_C ≈ 36 mA, R_f 500 Ω, R_E 4.5 Ω + r_e) the gain is 17.2 dB at 10 MHz. It is lower than ideal because of finite β and f_T. It stays flat within 1 dB from 0.89 to 95 MHz (> 6 octaves), with S11/S22 of −18.5/−16 dB (check D2).
- The gain, match and bandwidth are all set by resistors, which is why MMIC gain blocks and the classic HF "feedback amplifiers" use this topology [25].
- The cost is noise: R_f adds noise, so NF is typically a few dB. Power is class-A limited, ≈ $I_C^2(R_L\|R_f)/2$ = +14.6 dBm at 36 mA. For power, scale the current up and use a transformer-coupled output.
- Norton's "lossless" (transformer) feedback replaces the resistors with transformer windings. It keeps the matched broadband behaviour without the resistor noise and loss, giving very high dynamic range [24].

**(b) Transformer-coupled push-pull.** Two devices in antiphase drive a centre-tapped output transformer, usually a TLT/balun ([baluns](baluns-and-rf-transformers.md)). Each half sees half the collector-to-collector resistance. With a swing of $V-V_k$ per side, the full primary swings $2(V-V_k)$ peak, so
$$R_{cc}=\frac{2(V-V_k)^2}{P}.$$
- 12.5 V, 1 V knee, 20 W → 13.2 Ω, so a 1:4 transformer (12.5 Ω) to 50 Ω.
- 13.8 V, 50 W → 6.55 Ω (≈ 1:9 with a 3:1 turns ratio, or 1:6.25 if the knee margin allows).
- 28 V, 100 W → 13.5 Ω (1:4).

Benefits:
- **Even harmonics cancel** by symmetry. A class-B half-sine has a 2nd harmonic of −7.4 dBc single-ended. Push-pull leaves −42.2/−28.2/−22.2 dBc for 0.1 dB/1°, 0.5 dB/5° and 1 dB/10° of device imbalance (check E1). The output low-pass filter then mostly has to remove the 3rd harmonic.
- The virtual ground at the centre tap removes the need for a low-inductance source/emitter ground at RF.
- The impedance per side is 4× that of two paralleled devices.

The bandwidth limits are those of the transformer: magnetising inductance at the bottom, line length at the top ([TLT hybrids](couplers-dividers-combiners.md#level-3--broadband-transformer-hybrids-0180-multi-octave-splitters-and-receiver-multicouplers)). The usual HF–VHF arrangement is a pair of LDMOS or bipolar devices with a 1:4 or 1:9 TLT, a 1.8–54 MHz switched low-pass bank, and negative feedback (an R–C from drain to gate) to flatten gain across the band.

### Level 3 — PA practice: Doherty offset lines, class J, DIY load-pull, distortion → EVM, thermal stability, neutralisation
Numbers are from `tools/verify/s15_pa_practice.py`. Class D (voltage- and current-mode, and why $CV^2f$ rules it out at UHF) is covered in [PA control & class D](pa-control-protection-and-sequencing.md) and is not repeated here.

**(a) Practical Doherty: offset lines.** Level 2(f) assumed the *off* peaking amplifier is an open circuit at the combining node. A real device behind its output match is not: its off-state reflection Γ_off has some phase, often close to a short for a C_oss-dominated device seen through a low-pass match. A length of line at the combiner impedance (the **offset line**) rotates Γ_off to an open: $\theta_{off}=\angle\Gamma_{off}/2$ (mod 180°). For example, Γ_off ∠140° needs θ = 70°, which is 89 mm of vf-0.66 coax or 74 mm of FR-4 microstrip at 433.92 MHz. A matching offset on the main branch aligns its load-modulation trajectory with the device plane, and a phase-compensation line at the peaking input keeps the two currents in phase [1 ch. 10][12].

The script uses a normalised current-source model (λ/4 inverter, peaking current with its off-state admittance in parallel, voltage-limited class-B main). It reproduces 78.5/69.8/78.5 %. Efficiency at the −6 dB power point, with the change in full power in brackets:

| residual angle from an open | 0° | 30° | 60° | 90° | 180° (uncorrected short) |
|---|---|---|---|---|---|
| \|Γ_off\| = 0.98 | 77.6 % (−0.0 dB) | 76.5 % (−0.2) | 71.6 % (−0.7) | 60.9 % (−2.0) | collapses (−34 dB) |
| \|Γ_off\| = 0.9 | 74.5 % (−0.2) | 73.1 % (−0.4) | 68.0 % (−0.9) | 57.3 % (−2.2) | collapses (−20 dB) |
| \|Γ_off\| = 0.8 | 70.6 % (−0.5) | 69.2 % (−0.6) | 63.8 % (−1.2) | 53.3 % (−2.4) | collapses (−15 dB) |

So **±30° of offset error is tolerable, while 90° costs 17 points**. The off-state *loss* (|Γ_off| < 1) costs efficiency even when perfectly rotated, so choose a peaking device and match whose off-state is low-loss.

**(b) Class J and continuous modes.** Keep the class-B half-sine current but let the drain voltage be
$$v(\theta)=V_{dc}(1-\cos\theta)(1+\alpha\sin\theta),\qquad -1\le\alpha\le1 .$$
With $e^{j\omega t}$ and $Z_n=-V_n/I_n$, the FFT gives **$Z_1=R_{opt}(1+j\alpha)$ and $Z_2=-j\tfrac{3\pi}{8}\alpha R_{opt}$**, with all higher harmonics shorted. The efficiency is **π/4 and the power constant for every α**, and v ≥ 0 holds exactly up to |α| = 1. At α = 1.2 the waveform dips to −0.215 V_dc, which would drive the device into the knee (check B1). Some references write the waveform with (1 − α sin θ), which flips the sign of α. The physics is the same: an inductive fundamental goes with a capacitive 2nd harmonic.
- The point is **bandwidth**. A whole continuum of (Z1, Z2) pairs gives class-B efficiency, so a broadband match only has to stay on the locus. Real class-J/continuous-mode designs reach roughly octave bandwidth at 60–70 % [27], [28].
- The price is a peak drain voltage that rises from 2.00 to **2.91 V_dc** at |α| = 1, so check the breakdown margin.
- Extending the idea to the 3rd harmonic gives continuous class F.
- Class J is also why the C_oss-loaded load lines in Example 1 work. A device whose output capacitance makes the fundamental reactive is not necessarily inefficient, provided the 2nd harmonic sees the matching reactance.

**(c) DIY load-pull.**
1. **Reach is limited by loss.** A tuner or stub with |Γ|max 0.9 behind 0.5 dB (one way) of cable/fixture loss reaches only |Γ| = 0.80 at the device: VSWR 9.1, so R ≥ 5.5 Ω. With 1 dB of loss the limit is 8.3 Ω. A 3 W LDMOS that wants 5.9 + j6 Ω is out of reach.
2. **Pre-match.** Put a fixed λ/4 of 25 Ω (4:1) or an L-section at the device so the tuner works around 12.5 Ω; reach then extends to 1.4 Ω (check C1). De-embed the pre-match with a VNA.
3. **Correct for loss, and for its dependence on Γ.** Behind 0.5 dB of line, the fraction of device power that reaches the meter is −0.50 dB matched but −0.89 dB at |Γ| = 0.5 and −3.18 dB at |Γ| = 0.8. The standing wave raises the dissipation, so uncorrected "power contours" are distorted near the edge.
4. **Poor-man's load-pull by cable rotation.** Put a fixed mismatch (e.g. a 2:1 pad-and-stub) after the PA and insert cable lengths between them. At 433.92 MHz (vf 0.70) Γ turns a full circle per 24.2 cm, so 30° steps are 2.0 cm. Record P_out, I_DD and harmonics at each step. Remember that the 2f₀ impedance rotates twice as fast, so the harmonic termination changes too, and the steps are not a clean fundamental-only sweep.
5. **Safety.** Watch drain voltage and current, and never sweep through a short at full drive.

**(d) AM/AM and AM/PM → EVM; IM3 asymmetry.** For 16-QAM (RRC 0.25) through a Rapp (p = 2) PA with 15° of AM/PM at saturation:

| input back-off (rms re saturation) | total EVM | AM/AM only | AM/PM only |
|---|---|---|---|
| 12 dB | 0.71 % | 0.13 % | 0.70 % |
| 8 dB | 1.63 % | 0.79 % | 1.43 % |
| 6 dB | 2.64 % | 1.83 % | 1.90 % |
| 4 dB | 4.58 % | 3.90 % | 2.36 % |

AM/PM dominates in deep back-off and AM/AM near saturation (check D1). An AM/PM-heavy PA (GaN, class AB near pinch-off) therefore needs phase correction, which envelope feedback cannot provide (Level 3 linearisation (e)).
- **IM3 asymmetry.** A memoryless PA, even with complex (AM/PM) coefficients, gives equal upper and lower IM3. Unequal IM3 is the signature of **memory**: the envelope at the tone spacing Δ re-enters through, for example, the bias-network impedance H(Δ). Model it as $y=a_1x+a_3x|x|^2+b\,x\,(h*|x|^2)$. The upper IM3 is then ∝ $a_3+bH(\Delta)$ and the lower ∝ $a_3+bH^*(\Delta)$, so
$$|a_3+bH|^2-|a_3+bH^*|^2=-4\,\mathrm{Im}H(\Delta)\,\mathrm{Im}(a_3^*b).$$
  Asymmetry needs **both** a reactive H at Δ and a phase difference between the static and memory terms. With a3 and b 90° apart and the bias-network corner at Δ, the simulated asymmetry is 4.15 dB, matching the closed form. It is 0.00 dB when they are in phase or memoryless, and 0.07 dB when the corner is 100× Δ (check D2) [29].
- *Practical fix:* make the drain/gate bias networks low-impedance across the whole envelope (video) bandwidth: large low-ESR decoupling close to the device, and a small series inductance in the feed. Then use memory-polynomial DPD for what remains.

**(e) Thermal runaway and ballasting.** In a BJT, $V_{BE}$ falls by φ ≈ 2 mV/K at fixed $I_C$, i.e. $I_C$ rises ≈ 7–8 %/K at fixed $V_{BE}$ ([BJT](../05-analog-electronics/bjt-fundamentals-small-signal.md)). The electro-thermal loop gain is
$$L=\frac{\theta V\varphi}{R_E+V_T/I},$$
so the marginal ballast is $R_E>\theta V\varphi-V_T/I$. **Design for L ≲ 0.3–0.5, not L < 1.** Temperature drift is amplified by 1/(1 − L), and L grows as the device heats and I rises. The script uses a fixed-base-voltage bias, the worst case (check E1):
- 2 W stage, θ 30 K/W, 7.5 V, 0.3 A: runs away with no ballast, and also with 0.5 Ω (cold L = 0.77); settles with 1.5 Ω (L ≈ 0.29, 120 °C).
- One finger of a ten-finger device (θ 300 K/W, 30 mA): needs ≈ 10 Ω per finger (4 Ω, cold L = 0.93, still runs away).

This is why RF power BJTs have per-finger emitter ballast resistors on the die, and why discrete stages use a few-ohm emitter resistor, RF-bypassed if gain matters, or a bias source with a temperature-tracking V_BE (diode on the heatsink).
- **LDMOS/GaN**: below the zero-temperature-coefficient bias point, threshold drift dominates and $I_{DQ}$ *rises* with temperature. A square-law model with dV_th/dT ≈ −2.5 mV/K and mobility ∝ T^−1.5 (illustrative values) puts the ZTC overdrive near 1 V, and class-AB quiescent points sit below that. Use a temperature-tracking gate bias (thermistor/diode network or a bias controller) where I_DQ matters (linear modes). Above the ZTC point, at high current, the drain current falls with temperature, so LDMOS does not hot-spot like a BJT.

**(f) Neutralisation, in two-port terms.** Feedback capacitance gives $y_{12}=-j\omega C_{gd}$. A neutralising capacitor $C_n$ from the gate to an *inverted* drain (a centre-tapped or 1:−1 transformer) adds the lossless, reciprocal embedding $j\omega C_n\begin{bmatrix}1&1\\1&1\end{bmatrix}$. With $C_n=C_{gd}$ this makes **$y_{12}=0$**. For a FET (g_m 0.5 S, C_gs 20 pF, C_gd 1 pF, R_ds 200 Ω, 2 mS input loss) at 433.92 MHz:

| C_n | \|y12\| | Rollett K | Mason's U |
|---|---|---|---|
| 0 | 2.73 mS | 0.02 (potentially unstable) | 37.96 dB |
| 0.5 pF | 1.36 mS | 0.03 | 37.96 dB |
| 1.0 pF | 0 | ∞ (unilateral) | 37.96 dB |

U is unchanged in every case (check F1). Neutralisation does not create gain: it converts a potentially unstable device into a unilateral one, whose matched gain is U. Its weaknesses are that it works at one frequency (the transformer and C_n are frequency-dependent) and that C_gd varies with drain voltage. That is why modern solid-state PAs prefer resistive stabilisation and low-C_rss devices, while tube and HF push-pull amplifiers still neutralise ([PA control](pa-control-protection-and-sequencing.md), [stability](amplifier-stability-and-biasing.md)).

## Design equations & rules of thumb

| Quantity | Equation / value | Notes |
|---|---|---|
| Load line | $R_{opt}=(V_{DD}-V_k)^2/(2P)$ | 3.3 V, 1 W, $V_k$ 0.3 V → 4.5 Ω; 7.5 V, 3 W → 8 Ω; 28 V, 10 W → 36 Ω |
| Class A / B / C efficiency | 50 % / 78.5 % / ↑ with smaller α | ideal, no knee |
| Class F (V{1,3}, I half-sine) | 90.7 % | Raab |
| Class E | $R=0.5768V_{CC}^2/P$, $C_{sh}=0.1836/(\omega R)$, $X=1.1525R$ | 50 % duty, $Q_L\to\infty$; $V_{pk}=3.56V_{CC}$ |
| Class E max frequency | $f_{max}=0.1836/(2\pi C_{oss}R)$ | $C_{oss}$ must not exceed $C_{sh}$ |
| Back-off efficiency | A: $0.5P/P_{max}$; B: $0.785\sqrt{P/P_{max}}$ | |
| Doherty | 78.5 % at 0 and −6 dB | ideal symmetric |
| Knee loss | $\eta\to\eta(1-V_k/V_{DD})$ | why low-voltage PAs are less efficient |
| PAE | $\eta_D(1-1/G)$ | low-gain stages hurt PAE |
| Junction temp | $T_j=T_a+P_{diss}(\theta_{jc}+\theta_{cs}+\theta_{sa})$ | $P_{diss}=P_{DC}+P_{in}-P_{out}$ |
| Harmonic limit (ETSI SRD) | −36 dBm < 1 GHz (−54 dBm in broadcast bands), −30 dBm > 1 GHz | [10] |
| FCC restricted-band limit | 500 µV/m at 3 m above 960 MHz ≈ −41 dBm EIRP | 915 MHz: 3f₀ = 2745 MHz is in the 2690–2900 MHz restricted band [11] |
| Feedback gain block | $R_fR_E=Z_0^2$ → $S_{11}=S_{22}=0$, $S_{21}=(Z_0-R_f)/Z_0$ | 500 Ω/5 Ω → 19.1 dB, multi-octave |
| Push-pull load | $R_{cc}=2(V-V_k)^2/P$ | 12.5 V, 20 W → 13.2 Ω → 1:4 TLT |
| Push-pull 2H | imbalance 0.5 dB/5° → −28 dBc (vs −7.4 single-ended class B) | |
| Doherty offset line | $\theta_{off}=\angle\Gamma_{off}/2$ | ±30° error → −2 points; 90° → −17 points at −6 dB |
| Class J | $Z_1=R_{opt}(1+j\alpha)$, $Z_2=-j\frac{3\pi}{8}\alpha R_{opt}$, \|α\| ≤ 1 | η = 78.5 % constant; v_pk up to 2.91 V_dc |
| Load-pull reach | $|\Gamma_{dev}|\le|\Gamma_{tuner}|\,10^{-2L_{dB}/20}$ | 0.9 & 0.5 dB → R ≥ 5.5 Ω; pre-match 4:1 |
| IM3 asymmetry | $\propto\mathrm{Im}H(\Delta)\,\mathrm{Im}(a_3^*b)$ | needs memory and a phase difference |
| Thermal stability | $L=\theta V\varphi/(R_E+V_T/I)\lesssim0.3$–0.5 | φ ≈ 2 mV/K |
| Neutralisation | $C_n=C_{gd}$ via inverted drain → $y_{12}=0$, U unchanged | single-frequency |

Rules of thumb:
- Choose supply voltage first: power ∝ $V^2/R_{opt}$; at low voltage $R_{opt}$ becomes tiny, matching Q rises and loss grows.
- Present the right *harmonic* impedances too: at least short (class AB/B) or open (class F) the 2nd and 3rd harmonics at the device plane.
- Put the harmonic filter after the matching network and before the antenna; measure harmonics conducted into 50 Ω *and* radiated.
- Design with the device's data-sheet or load-pull $Z_{load}$ where available (it already includes parasitics); use the load-line estimate to sanity-check it.

## Worked examples

### Example 1 — A 2 W, 433 MHz PA with an LDMOS transistor
Device: NXP AFT05MS003N (SOT-89, 7.5 V, 1.8–941 MHz): 350–520 MHz broadband reference circuit gives 3.2 W, 15.1 dB gain, 73 % drain efficiency; $C_{oss}$ = 23.2 pF (at $V_{DS}$ 7.5 V, $V_{GS}$ 0 V, 1 MHz); $V_{GS(th)}$ 2.2 V; $R_{\theta JC}$ 4.1 °C/W; survives > 65:1 VSWR at 9 V [8].
1. **Load line:** $V_k\approx0.5$ V, $P=3.2$ W: $R_{opt}=(7.0)^2/6.4=7.66\ \Omega$, $I_{max}=1.83$ A.
2. **Absorb $C_{oss}$:** $X_C=1/(2\pi\cdot430\text{ MHz}\cdot23.2\text{ pF})=16.0\ \Omega$. The load network must present $R_{opt}\,\|\,(+j16\ \Omega)=6.22+j2.99\ \Omega$ to the drain. The data-sheet test circuit presents $5.86+j5.95\ \Omega$ at 430 MHz [8] — real part within 6 %, imaginary part larger because package inductance and the voltage-dependent $C_{oss}$ are not in the simple model. **Use the data-sheet value**, use the load line to understand it.
3. **Output network:** a low-pass L-section from the drain — series 7.2 nH then 19.6 pF shunt at the 50 Ω side ($Q=2.65$) — presents 6.22 + j2.99 Ω (script D4). In practice use two cascaded L-sections (lower Q each, broader band, more harmonic rejection) and include the drain bias feed choke (≥ 5 × 7.7 Ω reactance is trivial here — but it must carry 0.6 A DC).
4. **Harmonic filter:** requirement from ETSI EN 300 220 for +33 dBm: 2f₀ (866 MHz) ≤ −69 dBc and 3f₀ (1299 MHz) ≤ −63 dBc at the antenna port [10]. (Cross-check: IMDA TS SRD Table 1-a / ITU-R SM.329 Category B gives the same absolute limits, −36 dBm below 1 GHz and −30 dBm above, hence the same dBc figures — [19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md). Note that +33 dBm at 433 MHz is itself a *licensed* power in Singapore and the EU, whose licence-exempt limit is 10 mW e.r.p.) A class-AB drain current has 2nd harmonic at roughly −15 to −25 dB (table above), partly shorted by the output network. Add a 7th-order 0.1 dB-ripple Chebyshev LPF, $f_c$ = 520 MHz (g = 1.1811, 1.4228, 2.0966, 1.5733, …): **0.0 dB at 433 MHz, −44 dB at 866 MHz, −73 dB at 1299 MHz** (ideal parts, script G). With finite-Q parts expect 0.2–0.4 dB passband loss; an elliptic design with a zero at 866 MHz gives more margin. See [RF filters](rf-filters-lc-saw-baw-cavity-microstrip.md).
5. **Bias:** enhancement LDMOS → positive gate from a divider/DAC, $I_{DQ}$ ≈ 100 mA (data-sheet test condition); gate resistor for stability; temperature-compensate if linearity matters (LoRa: not needed).
6. **Thermal:** $P_{diss}=3.2/0.73-3.2+0.1\approx1.3$ W. With $\theta_{jc}$ 4.1 °C/W plus ≈ 25 °C/W through a 4-layer board with a via array under the tab, $T_j\approx50+1.3\times29=87$ °C at 50 °C ambient — acceptable, but duty cycle and enclosure matter (see [thermal](../13-pcb-rf-layout-emc/thermal-management-rf.md)).

### Example 2 — 915 MHz, 1 W with a front-end module
Skyworks SKY66122-11 (863–928 MHz FEM: PA + LNA + T/R switch): +30 dBm at 5 V with 640 mA total supply current, 33 dB small-signal gain, 2f₀ −22 dBc and 3f₀–10f₀ −72 dBc (maximum, data-sheet test setup), no damage into 10:1 VSWR, TX input abs. max +16 dBm [9].
- Efficiency: 1 W / (5 V × 0.64 A) = 31 % overall → 2.2 W of heat in a 6 × 6 mm module. The data sheet's absolute-maximum ratings are qualified at 30 % duty cycle at +30 dBm [9] — LoRa packets at SF7–SF9 are short, but continuous-carrier testing at full power needs a good thermal pad and ground copper.
- Harmonics: +30 − 22 = +8 dBm of 2f₀ at 1830 MHz is far above the −30 dBm (ETSI) or 15.209-level limits; the 3rd harmonic at 2745 MHz falls in the FCC restricted band 2690–2900 MHz where ≈ −41 dBm EIRP applies [11]. An external low-pass/harmonic filter after the FEM is required unless the module's TX-filter loop is populated (see data sheet [9]). The E220-900T30D and similar modules integrate this; a custom board must add it.
- LNA of the same FEM: 16 dB gain, 2.6 dB NF — good enough for most LoRa links, though a separate 0.5 dB LNA (see [LNA design](lna-design.md)) would buy ≈ 2 dB.

### Example 3 — Class E at 433 MHz: component values
$V_{CC}$ = 7.5 V, P = 2 W: $R=0.5768\times56.25/2=16.2\ \Omega$; $C_{sh}=0.1836/(2\pi\cdot433\text{ MHz}\cdot16.2)=4.2$ pF; $X=1.1525R=18.7\ \Omega$ → $L_x=6.9$ nH; with $Q_L=10$, $L_0=59.6$ nH, $C_0=2.27$ pF; then match 16.2 Ω to 50 Ω. Check: the AFT05MS003N's $C_{oss}$ (23 pF) is **5× larger** than the required 4.2 pF, so this device cannot run textbook class E at 433 MHz and 2 W from 7.5 V — its $f_{max}$ for that R is ≈ 78 MHz. Options: lower $R$ (lower $V_{CC}$, higher current), class-E with finite DC-feed inductance ("parallel-circuit class E"), or accept class AB/F operation. This is why UHF handheld PAs are usually "class AB with harmonic tuning" rather than true class E.

### Example 4 — Average efficiency with PAPR
16-QAM, raised-cosine 0.25: PAPR ≈ 7 dB (script H). If peaks reach saturation, average output is 7 dB below peak: class B ≈ 0.785 × 10^(−7/20) = 35 %; ideal symmetric Doherty (π/2)·10^(−7/20) = 70 % (−7 dB is just below its 6 dB transition point); class A 0.5 × 10^(−0.7) = 10 %. In practice, envelope statistics spread the operating point, so average efficiency is somewhat lower than these single-point values. LoRa (PAPR ≈ 0 dB) runs at the peak-efficiency point of any class.

### Example 5 — What DPD buys (simulation)
Rapp model (smoothness p = 2) with AM/PM, 16-QAM at 0.45 input drive: ACLR −43.1 dBc, EVM 2.5 %. A 7th-order odd memoryless polynomial predistorter learnt by indirect learning (4 iterations): ACLR −62.8 dBc, EVM 0.2 % (script H). Real PAs have memory; expect 10–20 dB ACLR improvement with memory-polynomial DPD.

## Practical notes
- **Measure what matters:** output power with a calibrated power meter or a spectrum analyser plus a known attenuator (30–40 dB, rated for the power); drain current for efficiency; harmonics with a high-pass/notch in front of the analyser (analyser-generated harmonics otherwise mask the DUT's). See [RF power measurement](../17-test-measurement/rf-power-measurement.md).
- **Never run a PA without a load**; a VNA port or spectrum analyser input is not a 2 W dummy load. Use a rated 50 Ω termination or attenuator.
- **Supply and decoupling:** the PA draws pulsed/modulated current (hundreds of mA); a low-ESR bulk capacitor near the drain choke prevents supply droop and AM on the carrier; put ferrite + RC in the gate line for low-frequency stability.
- **Layout:** the source/emitter (tab) is both ground and heat path — many vias directly under it; short, wide drain traces (the matching network impedances are a few ohms); keep the harmonic filter physically after the match, with its own ground vias; avoid coupling from the PA output to its input.
- **Rocket specifics:** antenna VSWR changes with flight (plume, separation, broken whip, ground proximity on the pad). Choose PAs/modules with a ruggedness spec, or add an isolator or reflected-power detection with power foldback.
- **Regulatory:** harmonic and spurious limits (ETSI EN 300 220, FCC Part 15, IMDA TS SRD) apply to conducted *and* radiated emissions; test with the real antenna. See [certification](../19-regulations-safety/certification-fcc-ce-imda.md).

## Common mistakes & misconceptions
- *"Conjugate-match the PA output to $S_{22}^*$."* A PA's optimum load is the load line (plus parasitic absorption), found from load-pull or the data sheet, not $S_{22}^*$ — the small-signal output impedance is irrelevant at saturation.
- *"Class C is more efficient, so use it for everything."* Only for constant-envelope signals; it needs more drive (lower gain) and gives less power per device. Fine for LoRa/FSK, wrong for QAM/OFDM.
- *"Efficiency is the same at all power levels."* It falls rapidly in back-off (class B 39 % at −6 dB); running a 2 W PA at 100 mW wastes most of the DC power.
- *"Datasheet PAE is what my board will get."* Knee voltage, matching-network loss (a few-ohm network with Q ≈ 3 and inductor Q 50 loses 0.2–0.5 dB), and harmonic filter loss all subtract.
- *"The LPF will fix any harmonic."* Only if the harmonic power doesn't couple around it (radiated from the PA/matching area, via the supply); shielding and layout matter.
- *"Class E values from the formula work with any transistor."* Only if the device's $C_{oss}$ ≤ the required shunt capacitance at your R and f.
- *"A PA that is stable into 50 Ω is stable."* Check stability into mismatched loads (the antenna) and under drive.
- *"Harmonics at −30 dBc are fine."* For a 2 W ISM transmitter the typical limit is −63 to −69 dBc.
- *"A Doherty is just two PAs and a λ/4 line."* Without offset lines that rotate the off peaking branch to an open, the back-off efficiency peak can vanish; a 90° error costs ≈ 17 points.
- *"A reactive fundamental load means wasted efficiency."* Class J shows that $R_{opt}(1+j\alpha)$ with the matching 2nd-harmonic reactance keeps 78.5 %, and that is the basis of octave-band PAs.
- *"Upper and lower IM3 differ because of AM/PM."* A memoryless PA (with any AM/PM) gives symmetric IM3. Asymmetry means memory, usually the bias network at the tone spacing.
- *"R_E just above the marginal ballast value is enough."* Drift is amplified by 1/(1 − L), and L rises as the device heats; aim for L ≈ 0.3.
- *"Neutralisation increases gain."* It removes feedback (y12 → 0) but leaves Mason's U unchanged; it buys stability, not gain.
- *"My load-pull shows the device can't deliver power at low impedance."* Often the tuner simply cannot reach it through the fixture loss; use a pre-match and de-embed.

## How to simulate / verify
- `tools/verify/rfckt_pa.py`: conduction-angle Fourier table (vs FFT), class-F efficiency table by LP optimisation, class-E time-domain ODE simulation, Cripps contours, AFT05MS003N load estimate and L-match, Doherty efficiency curve, back-off, ETSI harmonic budget + Chebyshev LPF (scikit-rf), DPD on a Rapp PA model (ACLR/EVM), thermal arithmetic. Runtime ≈ 2 min.
- `tools/verify/s15_tlt_splitter.py` §D–E (W5-S15, ngspice): feedback gain block (VCCS exact, BJT model), push-pull R_cc and even-harmonic cancellation vs imbalance.
- `tools/verify/s15_pa_practice.py` (W5-S15): Doherty with off-state peaking admittance and offset-line error, class-J FFT continuum, DIY load-pull reach/loss/cable rotation, 16-QAM EVM from AM/AM and AM/PM, IM3 asymmetry from bias-network memory (closed form vs simulation), electro-thermal BJT loop with ballasting, LDMOS ZTC illustration, neutralisation and Mason's U. ALL PASS.
- `tools/verify/rf2_pa_linearisation.py` (W5-E7): feedforward cancellation, Cartesian loop gain/stability, LINC decomposition and Wilkinson efficiency, EER bandwidth/delay, envelope feedback vs AM/PM. ALL PASS.
- Circuit simulation: ngspice/Qucs-S transient with a vendor nonlinear model (NXP and others provide ADS/AWR models; some provide SPICE) for waveforms; harmonic balance for load-pull and harmonic tuning (see [HB simulators](../16-simulation-tools/rf-circuit-simulators-harmonic-balance.md)).
- Bench: spectrum analyser for harmonics/spurs, power meter, drain-current monitor; a stub tuner or cable-length variations for poor-man's load-pull; thermal camera or thermocouple on the tab.

## Open questions / gaps
- Raab's class-F paper citation: search results list "vol. 47"; my reading is *IEEE T-MTT* 49(6), June 2001, pp. 1162–1166 — to be confirmed (logged).
- Sokal's finite-$Q_L$ class-E polynomials (QEX 2001) could not be fetched; only the $Q_L\to\infty$ constants (Raab 1977) are given, confirmed by simulation.
- No real load-pull data at 433/915 MHz were obtained beyond the AFT05MS003N data-sheet impedances.
- GaN PA specifics (drain-lag, trapping memory effects) are only touched on; a dedicated GaN PA page would help.
- The Doherty offset-line table uses an idealised current-source model with a fixed off-state admittance (no change in the peaking device's admittance as it turns on), so the numbers are trends, not a design.
- The LDMOS zero-TC numbers use assumed square-law parameters (illustrative); use the device data sheet's I_DQ-vs-temperature curve.
- The neutralisation example is a lumped intrinsic FET. Real packages add source inductance and drain-voltage-dependent C_rss.

## Sources
1. S. C. Cripps, *RF Power Amplifiers for Wireless Communications*, 2nd ed., Artech House, 2006 — ch. 2 (load line, load-pull contour construction), ch. 3 (reduced conduction angle), ch. 6–7 (class F, switching), ch. 10 (Doherty). (textbook)
2. F. H. Raab, P. Asbeck, S. Cripps, P. B. Kenington, Z. B. Popović, N. Pothecary, J. F. Sevic, N. O. Sokal, "Power amplifiers and transmitters for RF and microwave," *IEEE Trans. MTT*, 50(3), pp. 814–826, Mar. 2002 — review of classes, Doherty, ET, linearisation. (peer-reviewed)
3. F. H. Raab, "Maximum efficiency and output of class-F power amplifiers," *IEEE Trans. MTT*, 49(6), pp. 1162–1166, June 2001 (efficiency table; reproduced numerically here). (peer-reviewed; volume number flagged in Open questions)
4. N. O. Sokal, A. D. Sokal, "Class E — a new class of high-efficiency tuned single-ended switching power amplifiers," *IEEE J. Solid-State Circuits*, SC-10(3), pp. 168–176, June 1975; N. O. Sokal, "Class-E RF power amplifiers," *QEX*, Jan./Feb. 2001, pp. 9–20. (peer-reviewed / magazine)
5. F. H. Raab, "Idealized operation of the class E tuned power amplifier," *IEEE Trans. Circuits Syst.*, CAS-24(12), pp. 725–735, Dec. 1977 (exact constants 0.5768, 0.1836, 1.1525, 3.56). (peer-reviewed)
6. W. H. Doherty, "A new high efficiency power amplifier for modulated waves," *Proc. IRE*, 24(9), pp. 1163–1182, 1936. (peer-reviewed; classic)
7. L. Ding, G. T. Zhou, D. R. Morgan, Z. Ma, J. S. Kenney, J. Kim, C. R. Giardina, "A robust digital baseband predistorter constructed using memory polynomials," *IEEE Trans. Commun.*, 52(1), pp. 159–165, 2004; D. R. Morgan et al., "A generalized memory polynomial model for digital predistortion of RF power amplifiers," *IEEE Trans. Signal Process.*, 54(10), 2006. (peer-reviewed)
8. NXP/Freescale, *AFT05MS003N* data sheet rev. 0, 2015: 3.2 W 350–520 MHz broadband (15.1 dB, 73 %), $R_{\theta JC}$ 4.1 °C/W, $C_{oss}$ 23.2 pF, $V_{GS(th)}$ 2.2 V, Z_load table (430 MHz: 5.86 + j5.95 Ω), ruggedness > 65:1. https://www.nxp.com/docs/en/data-sheet/AFT05MS003N.pdf (datasheet)
9. Skyworks, *SKY66122-11 863–928 MHz Front-End Module* data sheet 204782G: +30 dBm at 5 V/640 mA, 33 dB gain, harmonics, ruggedness 10:1, abs. max ratings, LNA 16 dB/2.6 dB. https://www.skyworksinc.com/-/media/SkyWorks/Documents/Products/2901-3000/SKY66122-11_204782G.pdf (datasheet)
10. ETSI EN 300 220-1 V3.1.1 (2017-02), Short Range Devices 25–1000 MHz: spurious-domain limits (−54 dBm in 47–74, 87.5–118, 174–230, 470–790 MHz; −36 dBm other < 1 GHz; −30 dBm > 1 GHz), summarised in ST AN4305. https://www.etsi.org/deliver/etsi_en/300200_300299/30022001/03.01.01_60/en_30022001v030101p.pdf (standard)
11. 47 CFR §15.205 (restricted bands, incl. 2690–2900 MHz) and §15.209 (500 µV/m at 3 m above 960 MHz). https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C (regulation)
12. A. Grebennikov, *RF and Microwave Power Amplifier Design*, 2nd ed., McGraw-Hill, 2015 (class E with finite feed inductance, harmonic tuning). (textbook)
13. G. L. Matthaei, L. Young, E. M. T. Jones, *Microwave Filters, Impedance-Matching Networks, and Coupling Structures*, Artech House, 1980, Table 4.05-2 (Chebyshev g-values). (textbook)
14. H. S. Black, "Translating system," US Patent 1,686,792, 1928 (feedforward). (patent; cited)
15. H. Seidel, "A microwave feed-forward experiment," *Bell Syst. Tech. J.* 50(9), 2879–2916, 1971. (peer-reviewed; cited)
16. P. B. Kenington, *High-Linearity RF Amplifier Design*, Artech House, 2000 (feedforward, Cartesian loop, envelope feedback, LINC, error budgets). (textbook; cited, not re-read)
17. V. Petrovic, C. N. Smith, "Reduction of intermodulation distortion by means of modulation feedback," IEE Conf. on Radio Spectrum Conservation Techniques, 1983 (Cartesian feedback). (conference; cited)
18. M. Johansson, L. Sundström, "Linearisation of RF multicarrier amplifiers using Cartesian feedback," *Electronics Letters* 30(14), 1110–1112, 1994, doi:10.1049/el:19940763 (four parallel loops at 880 MHz, 30 dB IM suppression). (peer-reviewed; citation checked via the IET listing)
19. H. Chireix, "High power outphasing modulation," *Proc. IRE* 23(11), 1370–1392, 1935. (peer-reviewed; classic)
20. D. C. Cox, "Linear amplification with nonlinear components," *IEEE Trans. Commun.* COM-22(12), 1942–1945, 1974 (LINC). (peer-reviewed)
21. L. R. Kahn, "Single-sideband transmission by envelope elimination and restoration," *Proc. IRE* 40(7), 803–806, 1952 (EER). (peer-reviewed)
22. B. Razavi, *RF Microelectronics*, 2nd ed., 2011, §12.6 (feedforward, Cartesian feedback, envelope feedback); S. C. Cripps, *RF Power Amplifiers for Wireless Communications*, 2nd ed., 2006, ch. 14 (linearisation). (textbooks; cited)
23. `tools/verify/rf2_pa_linearisation.py` (this KB).
24. D. E. Norton, "High dynamic range transistor amplifiers using lossless feedback," *Microwave Journal*, May 1975; US Patents 3 426 298 (1969), 3 624 536 (1971), 3 891 934 (1975) (transformer "lossless/noiseless" feedback). (magazine/patents; bibliographic details via secondary sources)
25. W. Hayward, R. Campbell, B. Larkin, *Experimental Methods in RF Design*, ARRL, 2003, ch. 2 (feedback amplifiers, R_f·R_E design). (textbook; cited, not re-read — the matching condition and gain were derived independently here)
26. `tools/verify/s15_tlt_splitter.py` §D–E and `tools/verify/s15_pa_practice.py` (this KB; W5-S15).
27. P. Wright, J. Lees, J. Benedikt, P. J. Tasker, S. C. Cripps, "A methodology for realizing high efficiency class-J in a linear and broadband PA," *IEEE Trans. MTT*, 57(12), pp. 3196–3204, Dec. 2009, doi:10.1109/TMTT.2009.2033295 (class-J design with a 10 W GaN HEMT; bibliographic details verified via the Cardiff ORCA record). (peer-reviewed)
28. S. C. Cripps, P. J. Tasker, A. L. Clarke, J. Lees, J. Benedikt, "On the continuity of high efficiency modes in linear RF power amplifiers," *IEEE Microwave Wireless Compon. Lett.*, 19(10), pp. 665–667, 2009, doi:10.1109/LMWC.2009.2029754 (verified via the Cardiff ORCA record). (peer-reviewed; continuous modes)
29. J. Vuolevi, T. Rahkonen, *Distortion in RF Power Amplifiers*, Artech House, 2003 (memory effects, bias-network envelope impedance, IM3 asymmetry). (textbook; cited, not re-read)
