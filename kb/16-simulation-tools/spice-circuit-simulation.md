---
title: SPICE circuit simulation for RF — ngspice, LTspice, Qucs-S, Xyce; AC, noise, transient, .four, S-parameters; vendor models and RF limits
domain: 16-simulation-tools
slug: spice-circuit-simulation
tags: [spice, ngspice, ltspice, qucs-s, xyce, kicad, libngspice, ac-analysis, noise-analysis, transient, fourier, sp-analysis, s-parameters, vendor-models, touchstone, l-match, butterworth, colpitts, mna]
prerequisites: [../01-circuit-theory/lumped-elements-impedance-admittance.md, ../01-circuit-theory/passive-filter-design-prototypes.md, ../07-noise-linearity/noise-figure-and-friis.md]
related: [rf-circuit-simulators-harmonic-balance.md, python-rf-toolkit.md, installing-tools-macos.md, simulation-validation.md, ../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md, ../05-analog-electronics/_index.md, ../04-real-components-hf/_index.md]
level: mixed
confidence: high
last_updated: 2026-09-29
---

# SPICE circuit simulation for RF

## Questions this page answers
- Can I simulate an RF matching network or filter in SPICE, and how do I get S-parameters out of it?
- What is the difference between AC, noise, transient and `.four` analyses, and which one answers my question?
- How do I run ngspice from the command line or from Python on a Mac (with or without KiCad)?
- Why does my SPICE noise figure come out wrong by a fraction of a dB (or by 3 dB)?
- How do I use a vendor's SPICE model or S-parameter file for an LNA or transistor?
- Where does SPICE stop being trustworthy at RF (distributed effects, parasitics, harmonic balance)?
- How do I simulate an oscillator start-up, and why does my oscillator not start in simulation?

## TL;DR
- **SPICE solves lumped circuits** (Kirchhoff + device models) by modified nodal analysis. It is exact for the idealised circuit you draw; at RF the errors come from what you did *not* draw — pad/trace parasitics, component SRF, distributed lines, radiation.
- **Analyses**: `.op` (bias), `.ac` (small-signal linear sweep), `.noise` (small-signal noise referred to input/output), `.tran` (large-signal time domain; oscillators, PA clipping, start-up), `.four`/`fft` (harmonics from a transient), and in ngspice ≥ 34 `.sp` (small-signal S-, Y-, Z-parameters of a multi-port) [1].
- **Tested on this Mac** (`tools/verify/sim_ngspice_examples.py`, all pass): L-match 12.5→50 Ω at 433 MHz ($|S_{11}|$ 1.3×10⁻⁷, RL ≥ 10 dB from 323–520 MHz); 5th-order Butterworth 600 MHz LPF (matches the analytic response to < 0.001 dB); Colpitts oscillator at 18.80 MHz vs 18.17 MHz tank formula (+3.5 %); 6 dB pad NF 6.000 dB at 290 K.
- **ngspice traps found**: `.sp` needs **≥ 2 ports** (make the load a port); `meas sp … WHEN …` **segfaults** in ngspice-47 (use `wrdata` + Python); SPICE's default temperature is **27 °C, not 290 K** (NF +0.11–0.15 dB on a 6 dB pad); the load resistor's noise is counted unless you write `noisy=0`.
- Free engines: **ngspice** (brew; also bundled inside KiCad as a library), **LTspice** (native macOS app, free), **Qucs-S** (GUI front end for ngspice/Xyce/QucsatorRF), **Xyce** (Sandia, has harmonic balance). Commercial RF simulators are covered in [harmonic balance and RF simulators](rf-circuit-simulators-harmonic-balance.md).
- Use SPICE for **matching networks, filters, bias networks, oscillators, PA supply transients, ADC front ends**; use [openEMS](openems-workflow.md) or measured S-parameters for layout-dominated structures above ~1 GHz.

## Intuition (no math)
SPICE is a very patient bookkeeper. You give it a list of parts and where they connect; it writes down "current in = current out" at every node and "voltage across = what the part's model says" for every branch, and solves the whole set. For an **AC analysis** it pretends every signal is tiny, linearises every transistor around its bias point and solves the circuit once per frequency with complex numbers — exactly like doing phasor analysis by hand, but for thousands of nodes. For **transient** it marches forward in time, re-solving the nonlinear equations at every step — slow but able to show clipping, start-up and settling.

At 433 MHz a 0402 capacitor is not "a capacitor": it is a capacitor in series with ~0.5 nH of mounting inductance, a few tens of mΩ of ESR, and a pad with ~0.1–0.3 pF to ground. SPICE will happily give you a perfect answer for the idealised schematic. Most "SPICE doesn't work at RF" complaints are really "the schematic didn't include the parasitics". Put them in (from [component models](../04-real-components-hf/_index.md) or vendor S-parameter files) and SPICE remains an excellent RF tool up to the point where the *wiring itself* becomes a transmission line or antenna — then you need a field solver.

## The math

### Level 1 — what each analysis computes
- **AC**: phasor voltages $V_k(\omega)$ for a small sinusoidal excitation; results are complex, ratios give gain and phase. Units: V (or V/V with a 1 V source).
- **Noise**: at each frequency, the power spectral density of every noise source (resistor $4kTR$ V²/Hz, shot noise $2qI$ A²/Hz, flicker $K_f I^{A_f}/f$) is propagated to a chosen output node by the AC transfer function and summed in power: `onoise_spectrum` [V/√Hz] and the input-referred `inoise_spectrum` (output noise divided by the gain from the named source).
- **Noise figure** from SPICE: with a source resistance $R_s$ at temperature $T_0$, $F = \overline{v_{n,in}^2}/(4kT_0R_s)$ where $v_{n,in}$ is the input-referred noise voltage *including* $R_s$'s own noise — see [noise figure and Friis](../07-noise-linearity/noise-figure-and-friis.md).
- **Transient**: $v(t)$, $i(t)$ by numerical integration (trapezoidal or Gear) with adaptive time step.
- **.four / fft**: Fourier coefficients of a (periodic, settled) transient waveform → THD, harmonic levels in dBc.
- **.sp**: port $n$ is a source with internal impedance $Z_{0,n}$; SPICE computes the $N\times N$ scattering matrix $S_{ij}$ from AC solutions with one port excited at a time.

### Level 2 — modified nodal analysis (MNA)
For a linear circuit at angular frequency $\omega$, every element stamps entries into a sparse complex matrix:
$$\begin{bmatrix} \mathbf G + j\omega\mathbf C & \mathbf B\\ \mathbf B^T & \mathbf D\end{bmatrix}\begin{bmatrix}\mathbf v\\ \mathbf i_V\end{bmatrix}=\begin{bmatrix}\mathbf i_s\\ \mathbf v_s\end{bmatrix}$$
where $\mathbf G$ collects conductances, $\mathbf C$ capacitances, inductors and voltage sources add extra unknown branch currents $\mathbf i_V$ (rows $\mathbf B$, $\mathbf D$, with $-j\omega L$ on the diagonal for an inductor). A resistor $R$ between nodes $a,b$ adds $+1/R$ at $(a,a),(b,b)$ and $-1/R$ at $(a,b),(b,a)$. ngspice solves this with a sparse LU factorisation (KLU in the Homebrew build).

For **transient**, capacitors and inductors are replaced by companion models from the integration rule (trapezoidal: $i_{n+1} = \frac{2C}{h}(v_{n+1}-v_n) - i_n$), and nonlinear devices by their Newton–Raphson linearisation at each iteration. The **local truncation error** controls the time step; for RF waveforms you must still cap the step (`tran tstep tstop 0 tmax`) at ≲ 1/50 of the carrier period, or a high-Q oscillator's frequency and amplitude are wrong.

**Noise** is a linear analysis: each independent noise source $k$ with PSD $S_k(f)$ gives output PSD $|H_k(f)|^2 S_k(f)$; uncorrelated sources add in power. Temperature enters through $4kTR$ with the *circuit* temperature (default 27 °C = 300.15 K unless `.options temp=` or a per-instance `temp=` is set).

**S-parameters** in `.sp`: with port $j$ driven by $V_j$ behind $Z_{0j}$ and all other ports terminated, $S_{ij} = \frac{b_i}{a_j} = \frac{V_i - Z_{0i}I_i}{2\sqrt{R_{0i}}}\Big/\frac{V_j + Z_{0j}I_j}{2\sqrt{R_{0j}}}$ (power waves, as in [S-parameters](../03-transmission-lines-matching/s-parameters.md)); ngspice outputs `S_i_j`, `Y_i_j`, `Z_i_j` vectors [1].

### Level 3 — where SPICE's assumptions break at RF
- **Lumped assumption**: valid while every wire is ≪ λ/10 (≈ 35 mm in FR-4 at 433 MHz, 6 mm at 2.45 GHz). Beyond that include transmission lines: ngspice has the lossless `T` element and lossy `O` (LTRA) and `.model … txl`; better, import measured or EM-simulated Touchstone data.
- **Frequency-dependent parts**: skin-effect resistance ∝ √f, dielectric loss ∝ f, inductor Q curves — a constant-R SPICE model is right at one frequency only. Vendor S-parameter files (Murata SimSurfing, Coilcraft) are the accurate route; SPICE can import them via XSPICE or by fitting RLC networks (see [python toolkit](python-rf-toolkit.md) — scikit-rf's vector fitting exports SPICE subcircuits).
- **Large-signal periodic steady state** (mixers, PAs, oscillator phase noise, IP3 with many tones): transient + FFT works but needs long settling and tiny time steps; **harmonic balance** solves the periodic steady state directly in the frequency domain ([HB page](rf-circuit-simulators-harmonic-balance.md)).
- **Radiation and coupling through fields** are not in SPICE at all.

## Design equations & rules of thumb

| Item | Rule | Why |
|---|---|---|
| Transient max step | $t_{max} \le T_{RF}/50$ (433 MHz: ≤ 46 ps) | integration phase/amplitude error |
| Transient settling | run ≥ 5 τ of every bias RC before measuring | oscillators, PA bias |
| FFT window | ≥ 20–50 carrier cycles of settled data, Hann window, integer cycles if possible | leakage |
| `.sp` ports | ≥ 2 ports; give each its own `z0` | ngspice requirement |
| Noise temperature | `.options temp=16.85` or source-resistor `temp=16.85` | NF is defined at 290 K |
| Noiseless load | `RL out 0 50 noisy=0` | otherwise load noise is in your "NF" |
| Lumped validity | longest interconnect < λ/10 in the medium | otherwise use T-lines or EM |
| Parasitics to add (0402) | L_mount ≈ 0.3–0.7 nH, pad C ≈ 0.1–0.3 pF | see [04-real-components-hf](../04-real-components-hf/_index.md) |

## Worked examples
All four netlists are run by `python3 tools/verify/sim_ngspice_examples.py` (Homebrew ngspice-47 CLI; the L-match also through KiCad's ngspice-44.2 library). Component values come from `tools/rfcalc` (`python3 -m rfcalc lmatch …`).

### A — 433 MHz L-match, 12.5 Ω PA-side load to 50 Ω, S-parameters
From [matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md) Example 1: $Q_n = \sqrt{50/12.5-1} = 1.732$, series L = 7.96 nH, shunt C = 12.73 pF at the 50 Ω side.
```spice
* 433 MHz L-match: 12.5 ohm load is port 2, 50 ohm source is port 1
V1 in 0 dc 0 ac 1 portnum 1 z0 50
C1 in 0 12.733p
L1 in mid 7.958n
RLS mid out 1e-6          ; inductor ESR (set to X/Q = 0.541 ohm for Q = 40)
V2 out 0 dc 0 ac 1 portnum 2 z0 12.5
.control
sp lin 2601 250meg 616meg
let s11m = mag(s_1_1)
let s21m = mag(s_2_1)
wrdata out.dat s11m s21m     ; post-process in Python (meas ... WHEN crashes, see below)
quit
.endc
.end
```
Results: $|S_{11}(433\text{ MHz})| = 1.3\times10^{-7}$; return loss ≥ 10 dB from 323 to 520 MHz (46 % — the L-network's bandwidth ≈ $1/Q_n$ = 58 % is the right order). With an inductor Q of 40 the loss is **0.186 dB** vs the estimate $10\log_{10}(1+Q_n/Q_L)$ = 0.184 dB. Making the 12.5 Ω load a *port* (not a resistor) is what lets `.sp` report the transducer gain directly.

### B — 5th-order Butterworth low-pass, $f_c$ = 600 MHz (harmonic filter for a 433 MHz PA)
Prototype $g_k = 2\sin\frac{(2k-1)\pi}{10}$ = 0.618, 1.618, 2.000, 1.618, 0.618; $C = g/(\omega_c R)$, $L = gR/\omega_c$ → C1 = C5 = 3.279 pF, L2 = L4 = 21.46 nH, C3 = 10.61 pF.
```spice
V1 in 0 dc 0 ac 1 portnum 1 z0 50
C1 in 0 3.279p
L2 in n2 21.460n
C3 n2 0 10.610p
L4 n2 out 21.460n
C5 out 0 3.279p
V2 out 0 dc 0 ac 1 portnum 2 z0 50
.control
sp lin 1001 1meg 1500meg
let s21db = db(s_2_1)
wrdata out.dat s21db
quit
.endc
.end
```
SPICE vs $10\log_{10}(1+(f/f_c)^{10})$: 3.01/3.01 dB at 600 MHz, **16.14/16.14 dB at the 2nd harmonic (867.8 MHz)**, 33.64/33.64 dB at the 3rd (1301.8 MHz). The ideal filter is exact; the real one is limited by 21 nH inductor SRF (typically 2–4 GHz for 0402/0603 parts) and capacitor ESL — add those and the 3rd-harmonic rejection is what changes. (Filter design: [passive filter prototypes](../01-circuit-theory/passive-filter-design-prototypes.md).)

### C — Colpitts oscillator start-up (transient + FFT)
```spice
* common-collector Colpitts (generic NPN model with own parameters - not a vendor model)
VCC vcc 0 PULSE(0 5 0 20n 20n 1 2)
R1 vcc b 10k
R2 b 0 10k
Q1 vcc b e QGEN
RE e 0 1k
C1 b e 100p
C2 e 0 330p
L1 b t 1u
CB t 0 1n
.model QGEN NPN (IS=1e-16 BF=100 VAF=50 CJE=1p CJC=0.5p TF=20p RB=10 RE=0.5 RC=2)
.options reltol=1e-4
.control
tran 1n 30u 0 1n
linearize v(e)
wrdata out.dat v(e)
quit
.endc
.end
```
Tank formula: $f = 1/(2\pi\sqrt{L\,C_1C_2/(C_1+C_2)})$ = 18.17 MHz. SPICE (FFT of the last 10 µs): **18.80 MHz (+3.5 %)**, 2.3 V p-p at the emitter, 2nd harmonic −21.8 dBc. The +3.5 % is physics, not error: the transistor's junction capacitances and the loading of RE/R1‖R2 are in parallel with C1/C2. A lesson learned while building this example: with a 10 nF bypass capacitor the bias network's time constant (R1‖R2 × CB = 50 µs) delayed start-up beyond a 40 µs run and the FFT "found" 31 kHz — always check that the waveform is actually oscillating in the analysis window.

### D — noise analysis of a 6 dB π attenuator (does SPICE give NF = loss?)
```spice
.options temp=16.85            ; 290 K for the whole circuit
VS src 0 dc 0 ac 1
RS src in 50                   ; source resistance (its noise defines kT0)
RP1 in 0 150.476
RSER in out 37.35
RP2 out 0 150.476
RL out 0 50 noisy=0            ; the load is not part of the DUT
.control
noise v(out) VS lin 3 100meg 300meg
setplot noise1
wrdata out.dat inoise_spectrum
quit
.endc
.end
```
$F = v_{n,in}^2/(4kT_0R_s)$:

| Setup | SPICE | Theory |
|---|---|---|
| all at 290 K, noiseless load | **6.000 dB** | NF = loss = 6.000 dB |
| default 27 °C (source also at 300 K) | 6.149 dB | $L\,T/T_0$ = 6.149 dB — not an IEEE NF |
| circuit 27 °C, `RS … temp=16.85` | 6.112 dB | $1+(L-1)T/T_0$ = 6.112 dB |
| 290 K, **noisy** load | 9.010 dB | Friis with the load as a 2nd stage: 9.010 dB |

The 3 dB error from a noisy load and the 0.15 dB error from the default temperature are the two classic SPICE-NF mistakes.

## Practical notes
- **Running**: `ngspice -b file.cir` (batch, no GUI). Put analyses and `wrdata` in a `.control … .endc` block; read the ASCII columns with `numpy.loadtxt` (frequency, then real/imag or value pairs per vector).
- **From Python without installing anything**: KiCad's bundled library (`from analog_ngspice import run_netlist` in `tools/verify/`) — used for every netlist on the [05-analog-electronics](../05-analog-electronics/_index.md) pages.
- **KiCad schematic → simulation**: KiCad's simulator is ngspice; symbols need a SPICE model assignment. Good for checking the exact schematic you will fabricate.
- **LTspice** (Analog Devices, free, native macOS app): excellent for power/analog, fast transient, large library of ADI parts; S-parameter support is limited (`.net` analysis for 2-ports). macOS install is a `.pkg` needing an administrator password (not tested here).
- **Qucs-S**: a schematic GUI that drives ngspice, Xyce or QucsatorRF (the last two add harmonic balance). On macOS the Homebrew cask is unsigned and not notarized; Gatekeeper blocks first launch and the owner decides whether to allow it. Nothing on this page depends on it.
- **Xyce**: Sandia's parallel SPICE with harmonic balance and large-circuit solvers; no Homebrew formula (build from source).
- **Vendor models**: transistor SPICE models (e.g. for BFP/BFR, ATF-54143 — see [LNA design](../06-rf-circuits/_index.md)) are usually valid only in a stated bias/frequency range; RF vendors increasingly give **S-parameter + noise-parameter files** instead, which are exact at the measured bias but linear only. Use SPICE models for bias/stability/large signal, S-parameter files for gain/NF/matching.
- **Encrypted/PSpice-only models** may not load in ngspice; ngspice has `set ngbehavior=ps` (PSpice compatibility) and `=lt` (LTspice) modes.

## Common mistakes & misconceptions
- **"SPICE is not accurate at RF."** The *solver* is exact for the circuit; the *circuit* lacks parasitics and distributed effects. Add 0402 mounting inductance and pad capacitance and a 433 MHz matching network agrees with measurement within component tolerance.
- **Using the default 27 °C for noise figure** — gives 0.1–0.2 dB high NF for lossy networks. NF is defined with the source at 290 K.
- **Leaving the load resistor noisy** — adds the load's noise to the DUT (3 dB on a 6 dB pad).
- **Measuring an oscillator's frequency during start-up** or with too coarse a time step — the frequency and amplitude are wrong; check the envelope has settled.
- **Expecting `.ac` to show clipping or harmonics** — it is linear. Use `.tran` + `fft`/`.four`, or harmonic balance.
- **Ideal transmission line between ideal components at 2.4 GHz and calling it a layout simulation.** Discontinuities (pads, vias, bends, the connector launch) are missing; use [openEMS](openems-workflow.md) or measured data.
- **Trusting `.meas` in `.sp` analyses** — in ngspice-47 `meas sp … WHEN …` crashes (segmentation fault); export and post-process instead.

## How to simulate / verify
- `python3 tools/verify/sim_ngspice_examples.py` — runs examples A–D and compares with closed forms (`tools/rfcalc`).
- Cross-check SPICE S-parameters against a scikit-rf cascade of the same ideal parts (`rf.media.DefinedGammaZ0(...).shunt_capacitor(...) ** ... .inductor(...)`, see [python toolkit](python-rf-toolkit.md)) — two independent network solvers.
- For real parts: replace ideal L/C with the vendor's S-parameter files in scikit-rf, then compare with the SPICE RLC-parasitic model; the difference is your model error.
- For oscillators: check start-up (loop gain > 1 at the operating point) with an AC analysis of the broken loop before running the transient ([oscillators](../05-analog-electronics/_index.md)).

## Open questions / gaps
- LTspice and Xyce were not run on this machine; their `.net`/HB features are described from documentation only.
- Whether the ngspice `meas sp … WHEN` crash is fixed in ngspice ≥ 48 is unknown (KiCad's 44.2 library was not tested for this).
- A worked comparison of a vendor SPICE model vs the same vendor's S-parameter file for a real LNA transistor would quantify "SPICE model error" at 433/915 MHz.

## Sources
1. H. Vogt, G. Atkinson, P. Nenzi et al., *Ngspice User's Manual*, version 41+ (2023–2026), ch. 11–15 (analyses: `.ac`, `.noise`, `.tran`, `.four`, `.sp`), ch. 17 (control language: `wrdata`, `meas`, `fft`), port syntax `portnum`/`z0` for `.sp`. https://ngspice.sourceforge.io/docs.html (tool documentation)
2. L. W. Nagel, *SPICE2: A Computer Program to Simulate Semiconductor Circuits*, UC Berkeley ERL Memo M520, 1975 — MNA formulation, companion models, Newton–Raphson, truncation-error time-step control. (thesis / primary)
3. C.-W. Ho, A. E. Ruehli, P. A. Brennan, "The modified nodal approach to network analysis," *IEEE Trans. Circuits and Systems*, 22(6):504–509, 1975. (peer-reviewed)
4. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — sec. 5.1 (L-networks), sec. 8.3 (filter prototypes), sec. 10.1 (noise). (textbook)
5. G. Matthaei, L. Young, E. M. T. Jones, *Microwave Filters, Impedance-Matching Networks, and Coupling Structures*, Artech House, 1980 — Butterworth prototype values. (textbook)
6. Qucs-S project, https://ra3xdh.github.io/ — engines (ngspice, Xyce, QucsatorRF, SpiceOpus) and analyses (AC, DC, transient, S-parameter, HB via Xyce/QucsatorRF). (tool documentation)
7. This repository: `tools/verify/sim_ngspice_examples.py` (examples A–D), `tools/verify/analog_ngspice.py` (KiCad libngspice runner, W2-B1), `tools/rfcalc/matching.py`, `tools/rfcalc/noise.py`. (verification)
