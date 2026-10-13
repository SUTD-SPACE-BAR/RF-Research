---
title: RF circuit simulators and harmonic balance — HB vs transient, Qucs-S/QucsatorRF, Xyce, QucsStudio, Keysight ADS, Cadence AWR Microwave Office, Sonnet Lite, SimSmith, RFSim99; what each costs and does
domain: 16-simulation-tools
slug: rf-circuit-simulators-harmonic-balance
tags: [harmonic-balance, phase-noise, leeson, noisy-transient, van-der-pol, periodic-steady-state, shooting, circuit-envelope, transient, qucs-s, qucsator, xyce, qucsstudio, keysight-ads, awr-microwave-office, sonnet-lite, simsmith, rfsim99, x-parameters, load-pull, mixer, pa, ip3]
prerequisites: [spice-circuit-simulation.md, ../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md]
related: [em-solvers-fdtd-mom-fem.md, python-rf-toolkit.md, tool-landscape-overview.md, installing-tools-macos.md, ../06-rf-circuits/_index.md, ../05-analog-electronics/_index.md]
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# RF circuit simulators and harmonic balance

## Questions this page answers
- What is harmonic balance, and when is it better than a SPICE transient + FFT?
- Can I simulate PA compression, IP3, mixer conversion gain or oscillator phase noise with free tools?
- What do Keysight ADS and Cadence AWR Microwave Office do that SPICE doesn't, and can a student get them free?
- Which free RF tools run on macOS (Qucs-S, SimSmith) and which need Windows (QucsStudio, RFSim99, Sonnet Lite, AWR, ADS)?
- What is circuit envelope, load-pull, X-parameters — do I need them for a LoRa/GNSS front end?
- Can I get an oscillator's phase noise from a transient simulation, and does it agree with Leeson's formula?
- Is Leeson's $P_s$ the power in the tank or something else (why do two phase-noise formulas differ by 6 dB)?

## TL;DR
- **Harmonic balance (HB)** solves the *periodic steady state* of a nonlinear circuit directly in the frequency domain: unknowns are the harmonic phasors of every node voltage; linear parts are solved per harmonic, nonlinear device currents in the time domain via FFT, and Newton iterations balance them [1], [2]. No start-up transient, exact for high-Q circuits, natural for multi-tone IP3 and mixers.
- **Tested here** (`tools/verify/sim_harmonic_balance.py`, own 15-harmonic HB in Python vs a Radau transient): a 100→300 MHz tripler with a Q = 50 tank — HB converged in **1.2 ms** (49 residual evaluations); the transient needed **≥ 20 drive cycles** (error 1.1 % at 15 cycles, 0.04 % at 20) and 21 s; harmonic amplitudes agree to 10⁻⁶.
- **ngspice has no HB**; its experimental `pss` (shooting) analysis **did not converge** on this KB's Colpitts example (ngspice-47). Free HB: **Xyce** (Sandia, open source) and **QucsatorRF** via **Qucs-S**; **QucsStudio** (freeware, Windows).
- **Commercial**: Keysight **ADS** (HB, circuit envelope, X-parameters, load-pull, Momentum 2.5-D EM) — student licences only through a university's PathWave University Program; Cadence **AWR Microwave Office** (HB, AXIEM/Analyst EM) — **free 6-month academic self-licence on a personal Windows PC, Macs not supported** [4]. Both are Windows/Linux only.
- **Matching/Smith tools**: **SimSmith** (free, Java — runs on macOS), **RFSim99** (1999 Windows freeware, unmaintained), **Sonnet Lite** (free planar EM, Windows, 64 MB limit) [5].
- **Phase noise end to end** (`tools/verify/sim2_phase_noise_transient.py`, Example 4): a noisy transient of a 433.92 MHz LC oscillator (Q 30, 1 V peak), phase taken from the analytic signal, reproduces $\mathcal L = (2FkT/P_{sig})(f_0/2Qf_m)^2$ **within 0.22 dB over 0.3–30 MHz** (F = 1). This equals the KB's canonical Leeson form $FkT_0/(2P_s)$ when **$P_s = P_{sig}/4$, the tank's available power**; a Leeson fit to the run with an amplifier noise floor returns $Q_L$ 29.4 (true 30) and the floor −165.90 dBc/Hz (theory −165.86).
- For Marcus's LoRa/GNSS front ends built from modules and MMICs, **linear S-parameter work (scikit-rf/SPICE) + cascade budgets (rfcalc) covers ~90 %**; HB earns its keep for a discrete PA, a diode mixer/multiplier, or an oscillator you design yourself.

## Intuition (no math)
A transient simulator is like filming a guitar string from the moment it is plucked: to know the steady tone you must wait until the pluck transient dies away, and a high-Q string rings for a long time. Harmonic balance skips the film: it guesses the steady tone as a sum of harmonics, checks whether Kirchhoff's laws hold for that guess (linear parts in the frequency domain, nonlinear parts by converting to a waveform and back), and corrects the guess until they do. For a PA at 433 MHz with a 2nd/3rd-harmonic filter, a crystal oscillator, or two tones 1 kHz apart (IP3), the transient has to integrate millions of RF cycles; HB solves one small nonlinear system.

The price: HB needs a known fundamental frequency (autonomous oscillators need an extra unknown), enough harmonics to represent the waveform (hard clipping needs many), and good convergence aids for strongly driven circuits.

## The math

### Level 1 — the HB equations
Write each node voltage as $v(t) = \mathrm{Re}\sum_{k=0}^{K}V_k e^{jk\omega t}$. Kirchhoff's current law at harmonic $k$:
$$\mathbf Y(k\omega)\,\mathbf V_k + \mathbf I^{NL}_k(\mathbf V) + jk\omega\,\mathbf Q^{NL}_k(\mathbf V) - \mathbf I^{src}_k = 0,\qquad k = 0\ldots K$$
where $\mathbf Y$ is the admittance matrix of the linear part (any linear element, including distributed lines and S-parameter blocks — they are just frequency-dependent $\mathbf Y$), and $\mathbf I^{NL}_k$, $\mathbf Q^{NL}_k$ are the harmonic components of the nonlinear device currents and charges, computed by inverse FFT → evaluate $i(v(t))$, $q(v(t))$ → FFT [1].

### Level 1½ — HB as "N harmonics × M nodes" simultaneous equations, algebra only
- **Unknowns.** Pick how many harmonics K to keep. Each node voltage becomes K + 1 numbers: a DC value and K complex phasors, i.e. 2K + 1 real numbers. A circuit with M nodes has M(2K + 1) unknowns. This is the HB analogue of "N segments → N currents" in MoM.
- **Equations.** At each node and each harmonic, Kirchhoff's current law must hold: the current through the linear parts (easy, one impedance per harmonic) plus the current through the nonlinear device must equal the source current. The device current is found by turning the guessed harmonics into a waveform, applying i(v), and taking the harmonics of the result (an FFT).
- **Solve.** Newton's method adjusts the guess until every residual is zero. There is no start-up transient to wait for: the unknowns *are* the steady state.
- **Truncation.** Harmonics above K are thrown away. If the waveform is strongly distorted, K must grow (check by doubling K).

*Worked number (verified, `tools/verify/sim2_level15_numbers.py`).* One diode (Is = 5 µA, V_T = 25.85 mV) is fed from 50 mV cos ωt through 1 kΩ. With K = 2 there are 5 real unknowns (V₀, V₁, V₂). HB gives V₀ = −2.652 mV, |V₁| = 40.896 mV and |V₂| = 2.661 mV. The exact waveform's harmonics are −2.653 / 40.902 / 2.621 mV (|V₃| = 0.31 mV). So two harmonics already get DC and the fundamental within 1 µV and 6 µV; the 2nd harmonic is 1.5 % off because V₃ was dropped.

### Level 2 — solving it
Newton–Raphson on the residual $\mathbf F(\mathbf V)$: $\mathbf V^{(n+1)} = \mathbf V^{(n)} - \mathbf J^{-1}\mathbf F$, where the Jacobian blocks are harmonic convolutions of the device conductance $g(t) = \partial i/\partial v$ (a Toeplitz structure). Size: nodes × (2K+1) real unknowns; Krylov (GMRES) solvers with block-diagonal preconditioning make thousands of nodes × tens of harmonics practical [2]. **Two-tone** (IP3): frequencies $m\omega_1 + n\omega_2$ with a truncation $|m|+|n| \le$ order; the FFT becomes multi-dimensional or uses artificial frequency mapping. **Oscillators**: the frequency is an extra unknown, fixed by a phase condition on one harmonic.

### Level 3 — relatives
- **Shooting / PSS** (time-domain periodic steady state): find the initial state $x_0$ such that one period of transient integration returns to $x_0$ (Newton on $\Phi_T(x_0) - x_0 = 0$). Good for strongly nonlinear, switching circuits; ngspice's `pss` is an experimental implementation.
- **Circuit envelope**: HB at each time step of a slowly varying modulation — for LoRa chirps through a PA or ACPR of a modulated signal.
- **X-parameters / poly-harmonic distortion models**: large-signal extensions of S-parameters measured on a nonlinear VNA; vendors ship them for PAs.
- **Phase noise**: HB-based small-signal noise around the periodic solution (pnoise). A plain SPICE transient cannot give it because its sources are noiseless; a transient **with explicit white-noise sources** (ngspice `trnoise`, or an SDE as in Example 4) can, if the phase is extracted from the waveform and enough realisations are averaged.

## Design equations & rules of thumb

| Question | Tool | Notes |
|---|---|---|
| Small-signal gain/match/stability, NF | SPICE `.ac/.sp/.noise`, scikit-rf | linear |
| P1dB, AM-AM of a PA at one tone | HB (or transient + FFT if Q low) | 5–9 harmonics |
| IIP3/IM3 with close tones | HB two-tone | transient needs ≥ 1/Δf of simulated time |
| Mixer conversion gain, LO leakage | HB (large LO + small RF) | or periodic AC |
| Oscillator frequency/amplitude | HB-osc, shooting, or long transient | check start-up with loop-gain analysis |
| Oscillator phase noise | HB-based pnoise (ADS, AWR, Xyce?); or a noisy transient + phase extraction (Example 4) | plain SPICE transient has no noise; read $\mathcal L$ from the phase, not from a voltage FFT |
| PA with modulated LoRa/QPSK | circuit envelope | ADS/AWR |
| Number of harmonics | ≥ 7 for mild compression; 15–30 for class-C/switching | check convergence in K |
| Transient settling for a tank of Q | ≳ 5 × 2Q/ω₀ | Q = 50 at 300 MHz: ≈ 27 drive cycles at 100 MHz |

| Tool | Engine / features | Platform | Cost (student) |
|---|---|---|---|
| Qucs-S | GUI for ngspice, Xyce (HB), QucsatorRF (HB, S-param, microstrip models) | Linux/Windows/macOS (unsigned cask on macOS) | free |
| Xyce | Sandia SPICE with HB, parallel | Linux/macOS/Windows (build from source) | free, open source |
| QucsStudio | Qucs-derived; HB "including large-signal AC and noise analysis" (features page), S-param, filter/matching synthesis | Windows (the site's front and features pages do not state the OS; checked 2026-10-14) | free of charge, binary-only (Hackaday's description); v5.9 [10] |
| Keysight ADS | HB, envelope, X-params, load-pull, Momentum, FEM | Windows/Linux | student licence via University Program |
| Cadence AWR MWO | HB (APLAC), AXIEM, Analyst, VSS | Windows | 6-month free academic licence, personal PC |
| Sonnet Lite | 2.5-D planar EM (not HB) | Windows | free (64 MB) |
| SimSmith | Smith chart matching with real components, sweeps | Java: Windows installer with bundled JRE; Linux `.sh` (JRE ≥ 15); macOS universal `.dmg`, no longer code-signed (Gatekeeper prompt) | free download; 18.4 is the long-stable release [11] |
| RFSim99 | linear S-param circuit sim, filter/matching wizards | Windows (1999); AD5GG's standalone repack reported to run on Windows 7/8/10, and on 11 in XP-compatibility mode (blog reports) | freeware, unmaintained [12] |
| LTspice | transient/AC/noise; `.net` 2-port | macOS/Windows | free |

## Worked examples

### 1 — why HB wins for a high-Q multiplier (own Python HB, tested)
Circuit: an ideal cubic transconductor ($i = g_{m3}v_{in}^3$, $g_{m3}$ = 0.02 A/V³) driven by 1 V at 100 MHz injects $\tfrac34 g_{m3}A^3$ at 100 MHz and $\tfrac14 g_{m3}A^3$ = 5 mA at 300 MHz into a parallel tank (10 nH, 28.14 pF, $R_p$ = 942 Ω, Q = 50) with a compressive output nonlinearity ($i = 2\times10^{-4}v^3$).
- Linear estimate of the 300 MHz output: 5 mA × 942 Ω = 4.71 V. HB (K = 15 harmonics, N = 128 samples): **|V₃| = 2.499 V** (compressed by the output nonlinearity), |V₁| = 106.0 mV, |V₅| = 1.75 mV; converged in 1.2 ms.
- Transient (Radau, rtol 10⁻¹⁰): identical harmonics after 80 cycles (21 s); **using only 15 cycles leaves a 1.1 % error in V₃**, 20 cycles 0.04 %. The amplitude time constant $2Q/\omega_0$ = 53 ns = 5.3 drive cycles explains it.
- Lesson: for PAs with harmonic traps, crystal circuits and narrow filters, a transient FFT taken too early silently reports the wrong harmonic levels; HB has no such trap (but check convergence in the number of harmonics).

### 2 — the two-tone IIP3 cost in transient simulation
Tones 1 MHz apart at 433 MHz: the IM3 products at 432/435 MHz are resolved only after ≥ 1 µs of *settled* signal (1/Δf), sampled at ≤ 1/(50 × 435 MHz) = 46 ps → ≥ 22 000 steps after settling, times the settling of every bias network. HB with $|m|+|n| \le 5$ has ~20 frequencies and gives IM3 directly. For a quick estimate without any simulator, use the cascade formula in `rfcalc.noise` (IIP3 of each stage from datasheets, [cascade analysis](../07-noise-linearity/receiver-cascade-analysis.md)).

### 3 — what the free academic licences are worth to Marcus (SUTD)
- AWR Microwave Office: sign up with the university e-mail; 6-month licence, one at a time, personal Windows PC, no support tickets [4]. Worth it for a semester project designing a discrete 433 MHz PA or LNA with vendor S-/X-parameter files, plus AXIEM for the layout.
- Keysight ADS: only if SUTD holds a PathWave University Program agreement (ask the department) [6].
- On the Mac: Qucs-S (owner decides about Gatekeeper) + Xyce for HB, or keep to linear design in scikit-rf and verify large-signal behaviour on the bench (spectrum analyser, [domain 17](../17-test-measurement/_index.md)).

### 4 — oscillator phase noise from a noisy transient run, and the Leeson fit (tested)
**Circuit** (`tools/verify/sim2_phase_noise_transient.py`): a parallel tank L = 10 nH, C = 13.45 pF (f₀ = 433.92 MHz), R = 817.9 Ω (Q = 30), sustained by a noiseless negative conductance with cubic limiting, $i = G_1v - G_3v^3$ with $G_1 = 1.5/R$, sized so that the describing-function amplitude is 1 V peak ($A^2 = 4(G_1 - 1/R)/3G_3$). Noise enters as a white current of one-sided density $4kTF/R$ across the tank (T = 290 K; F = 1 is the resistor alone, F = 2 lets the active device add as much again). Integration: stochastic Heun, 64 steps per period, 16 independent records of 20 µs (8 700 cycles each). The phase comes from the analytic signal (FFT Hilbert transform) with the carrier removed by a linear fit; $S_\varphi$ by Welch; $\mathcal L = S_\varphi/2$ (IEEE 1139, [00 canonical](../00-math-foundations/canonical-values-and-conventions.md)).

**Theory, two ways.** Tank noise current through the tank impedance near resonance, $|Z| \approx R\,f_0/(2Qf_m)$, gives a voltage density $4kTFR(f_0/2Qf_m)^2$, half of it phase noise; relative to the carrier mean square $A^2/2$:
$$\mathcal L(f_m) = \frac{2FkT}{P_{sig}}\left(\frac{f_0}{2Qf_m}\right)^2,\qquad P_{sig} = \frac{A^2}{2R}\ \text{(power dissipated in R)}$$
— the Lee–Hajimiri form. The KB's canonical Leeson form is $\mathcal L = \frac{FkT_0}{2P_s}\left[1 + (f_0/2Q_Lf_m)^2\right]$. The two agree exactly when $P_s = A^2/(8R) = P_{sig}/4$: **$P_s$ is the available signal power of the tank seen as a source of open-circuit amplitude A and source resistance R**, not the power the tank dissipates. That is the "6 dB by definition" on the canonical page, now made concrete for a tank of known R. Here $P_{sig}$ = −2.14 dBm and $P_s$ = −8.16 dBm.

**Pre-registered** (in the script header): (E1) agreement within ±1 dB over 0.3–30 MHz; (E2) the same number from both forms with $P_s = P_{sig}/4$; (E3) F = 2 adds 3.0 ± 0.3 dB; (E4) with the amplifier's own broadband noise added at the observation point, the curve flattens to $FkT_0/2P_s$ above $f_0/2Q$ = 7.23 MHz and a two-parameter Leeson fit returns $Q_L$ within 10 % and the floor within 0.5 dB; (E5) AM noise adds ~3 dB to the voltage spectrum far from the carrier and nothing close in.

| Offset | Simulated $\mathcal L$, F = 1 | Theory (both forms) | Difference |
|---|---|---|---|
| 0.3 MHz | −141.90 dBc/Hz | −141.73 | −0.17 dB |
| 1 MHz | −151.52 | −151.55 | +0.03 dB |
| 3 MHz | −161.43 | −161.21 | −0.22 dB |
| 10 MHz | −171.61 | −171.66 | +0.05 dB |
| 30 MHz | −181.17 | −181.22 | +0.04 dB |
| 100 kHz (extrapolated, 1/f²) | — | −131.7 | — |

Results against the pre-registration: **E1 pass for F = 1** (max 0.22 dB). **E1 missed for F = 2 at the 0.3 MHz point** (+1.94 dB; 1–30 MHz within 0.35 dB). That point rests on a single 106 kHz Welch bin; two post-hoc seeds gave +0.41 and +0.88 dB, so the miss is estimator scatter at the lowest offset, not physics. The tolerance was simply too tight for one bin. **E3 pass**: 3.18 dB. **E4 pass**: fitted $Q_L$ = 29.4 (true 30), floor −165.90 dBc/Hz against $FkT_0/2P_s$ = −165.86. **E5 pass**: AM/PM read from the analytic-signal envelope adds +0.01 dB at 0.3 MHz, +2.2 dB at 10 MHz and +3.0 dB at ≥ 50 MHz. The limiter's amplitude-restoring bandwidth, $(G_1 - 1/R)/2\pi C$ ≈ 7.2 MHz, sets the crossover. Two read-out bugs in the first run (an empty 0.3 MHz band with 212 kHz bins, and a Welch spectrum of v(t) whose carrier leakage, −108 dBc/Hz at 1 MHz, swamped the noise) are recorded in the script's addendum. The same 433 MHz numbers with the canonical example's F = 2, $P_s$ = 0 dBm and $Q_L$ = 20 give the canonical −132.9 dBc/Hz at 100 kHz.

**What this buys and what it doesn't.** The run checks the 1/f² (Leeson skirt) part, the far-out floor, the F scaling and the AM/PM split, and the meaning of $P_s$, all against an independent derivation. It does **not** produce flicker up-conversion ($1 + f_c/f_m$): that needs a 1/f source and a mechanism that converts it (in a real transistor, bias-dependent capacitance). In an HB tool that is the job of pnoise with the device's flicker model; in a transient it needs a 1/f noise generator and records ≫ $1/f_c$. For a real Colpitts, replace the cubic conductance by the transistor model and use ngspice `trnoise` sources. Expect the transient to take hours: offsets of 10 kHz need records of ≥ 1 ms at 64 steps per period, i.e. ≈ 3 × 10⁷ steps per realisation.

## Practical notes
- **Models decide everything**: HB with a poor large-signal transistor model is precise nonsense. For PAs use the vendor's nonlinear model (or X-parameters) validated in its bias range; for modules (EBYTE E22/E220) there is nothing to simulate at circuit level — use the datasheet's output power/harmonics and filter externally.
- **Convergence aids**: source stepping (ramp the drive), start from a DC solution, increase harmonics gradually, oversample the FFT (N ≥ 4K) for sharp nonlinearities.
- **Check harmonic convergence**: rerun with K doubled; the quantities you report should not change.
- **Distributed elements** (microstrip, S-parameter blocks) are natural in HB (they are frequency-domain), unlike in SPICE transient where they need convolution or fitting.

## Common mistakes & misconceptions
- **"SPICE transient + FFT is the same as HB."** Only after full settling, with a fine enough time step and an integer number of periods in the window; high-Q circuits make this slow and error-prone (Example 1).
- **"More harmonics always converge better."** More unknowns can slow or destabilise Newton; increase gradually.
- **Reading IP3 from one input level** — extrapolate from the 1:1 / 3:1 slope region, and confirm the slopes ([nonlinearity](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md)).
- **Reading phase noise from an FFT of the oscillator voltage.** The window's leakage of the 0 dBc carrier sits far above −150 dBc/Hz close in (Hann: −108 dBc/Hz at 1 MHz offset in Example 4's first run), and far out the voltage spectrum contains AM noise as well (+3 dB). Extract the phase (analytic signal or I/Q demodulation) and compute $S_\varphi$.
- **Plugging the tank-dissipated power into Leeson's $FkT/2P_s$.** That is 6 dB optimistic; Leeson's $P_s$ is the available power ($P_{sig}/4$ for a tank of resistance R), or use $2FkT/P_{sig}$ (Example 4).
- **Using HB for an oscillator without an oscillator probe/phase condition** — it will happily converge to the non-oscillating DC solution.
- **Assuming a free academic licence covers commercial or team (Space Bar) product work** — check the licence terms.

## How to simulate / verify
- `python3 tools/verify/sim_harmonic_balance.py` — own HB vs transient on the tripler (≈ 1 min).
- `python3 tools/verify/sim_ngspice_examples.py` — transient + FFT of a Colpitts (example C) showing the settling trap (bias RC).
- `python3 tools/verify/sim2_phase_noise_transient.py` — Example 4: noisy transient of a 433.92 MHz LC oscillator → $\mathcal L(f)$ → Leeson fit, with pre-registered checks (≈ 1 min; results in `sim2_phase_noise_results.txt`).
- `tools/verify/noise_ip3_twotone.py` (W1-A5) — two-tone "measurement" by FFT on memoryless nonlinearities (tanh, Rapp): HB-free IIP3 extraction.

## Open questions / gaps
- Xyce HB and QucsatorRF HB were not run here (no install of Xyce; Qucs-S not launched) — a cross-check of the Python HB against Xyce is an obvious next step.
- Simulator status re-checked on 2026-10-14 from the vendors' pages [10–12]: QucsStudio v5.9 with HB; SimSmith 18.4 with the packaging above; RFSim99 via repacks (blog-level sources only). None was installed or run here, since all three need Windows or an unsigned macOS app. Verify again before recommending one.
- Phase noise is now demonstrated with a noisy transient (Example 4), but **not with HB/pnoise** (no Xyce or Qucs-S run), not with a transistor-level Colpitts, and not for flicker up-conversion. A Xyce `.HB` + noise run on the same tank would be the cross-check.

## Sources
1. K. S. Kundert, J. K. White, A. Sangiovanni-Vincentelli, *Steady-State Methods for Simulating Analog and Microwave Circuits*, Kluwer, 1990 — harmonic balance, shooting, Newton formulations. (textbook)
2. S. A. Maas, *Nonlinear Microwave and RF Circuits*, 2nd ed., Artech House, 2003 — ch. 3 (harmonic-balance analysis, multitone, convergence). (textbook)
3. R. C. Melville, P. Feldmann, J. Roychowdhury, "Efficient multi-tone distortion analysis of analog integrated circuits," *Proc. IEEE CICC*, 1995 — Krylov HB. (peer-reviewed)
4. Cadence, "AWR University Program FAQ" (PDF): 6-month academic Microwave Office licence, personal Windows PC, Macs not supported, academic users cannot file support tickets. https://awr.cadence.com/support/AWR_University_FAQ.pdf (vendor document)
5. Sonnet Software, Sonnet Lite information (help v18): 64 MB memory limit. https://www.sonnetsoftware.com/ (vendor documentation)
6. Keysight PathWave University Program documentation (student licences, node-locked, tied to a university agreement). https://docs.keysight.com/university/ (vendor documentation)
7. Qucs-S project page https://ra3xdh.github.io/ (HB via Xyce and QucsatorRF); Xyce, Sandia National Laboratories, https://xyce.sandia.gov/ (tool documentation)
8. This repository: `tools/verify/sim_harmonic_balance.py` (W3-C2); `tools/verify/sim2_phase_noise_transient.py` (W5-S11). (verification)
9. D. B. Leeson, "A simple model of feedback oscillator noise spectrum," *Proc. IEEE* 54(2), 329–330, 1966; T. H. Lee, A. Hajimiri, "Oscillator phase noise: a tutorial," *IEEE JSSC* 35(3), 326–336, 2000; IEEE Std 1139-2008 ($\mathcal L = S_\varphi/2$). Example 4's theory is derived on this page; these fix the definitions compared. (peer-reviewed / standard)
10. M. Margraf, QucsStudio home and features pages, https://qucsstudio.de/ and https://qucsstudio.de/features/ — "Version 5.9 is now available"; HB with large-signal AC and noise; checked 2026-10-14. (vendor page)
11. W. Ward (AE6TY), SimSmith download page, http://www.ae6ty.com/Smith_Charts.html — 18.4 stable; Windows installer with bundled JRE, Linux `.sh` needing JRE ≥ 15, unsigned macOS `.dmg`; checked 2026-10-14. (author page)
12. rtl-sdr.com, "RFSim99 for modern Windows versions" (pointing to AD5GG's standalone build), and N1FD club blog, 2023-04-23 — Windows 7/8/10 and Windows 11 in XP-compatibility mode. (blog — anecdotal)
