---
title: Frequency multipliers and dividers (class-C multipliers, push-push, diode/varactor/SRD, 20 log N, prescalers)
domain: 06-rf-circuits
slug: frequency-multipliers-dividers
tags: [frequency-multiplier, doubler, tripler, push-push, class-c, conduction-angle, varactor, step-recovery-diode, comb-generator, apdp, phase-noise-multiplication, 20logn, carrier-collapse, frequency-divider, prescaler, dual-modulus, injection-locked-divider, regenerative-divider]
prerequisites:
  - power-amplifiers.md
  - vco-and-pll-synthesizers.md
  - ../07-noise-linearity/phase-noise-and-jitter.md
related:
  - mixers.md
  - ../05-analog-electronics/diodes-schottky-pin-varactor.md
  - ../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md
  - ../11-radar/fmcw-radar.md
  - ../11-radar/diy-radar-hardware.md
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Frequency multipliers and dividers

## Questions this page answers
- How does a transistor or diode multiply a frequency, and how efficient can it be?
- What conduction angle maximises the 2nd or 3rd harmonic of a class-C multiplier?
- Why does a push-push doubler cancel the fundamental?
- Why does multiplying a frequency by N raise phase noise by 20 log N, and what is "carrier collapse"?
- Why does dividing a frequency lower phase noise, and where does it stop?
- How does a dual-modulus prescaler reach every divide ratio, and why do PLLs have a minimum N?
- What are step-recovery-diode comb generators, varactor multipliers and injection-locked dividers used for?

## TL;DR
- A nonlinear device driven at $f_0$ produces harmonics $nf_0$; a filter selects one. For a transistor as a truncated-cosine current source, the $n$th harmonic is maximised at a conduction angle of roughly $240°/n$ — **120° for doublers ($I_2/I_{max}$ = 0.276, 5.2 dB below class-B fundamental), 80° for triplers (0.185, −8.7 dB), 60° for ×4 (0.139, −11.1 dB)**, each with ≈ 63 % collector efficiency at that angle if the load is tuned to $nf_0$ (verified closed form vs FFT). Conversion gain falls quickly with $n$: ×2 and ×3 per stage are the norm.
- **Push-push** (two devices in antiphase, outputs combined) cancels all odd harmonics and doubles the even ones — a clean doubler without a sharp filter. An **anti-parallel diode pair** does the reverse (only odd harmonics): a balun-free tripler (verified).
- **Efficiency limits**: resistive (nonlinear-resistance) multipliers are bounded by $1/n^2$ (Page): ≤ 25 % (×2), 11 % (×3), 6.25 % (×4); an ideal lossless varactor (nonlinear reactance) can reach 100 % (Manley–Rowe) — why varactor and step-recovery-diode multipliers dominate high-order, high-power multiplication.
- **Phase noise ×N**: an ideal multiplier multiplies phase deviations, so sidebands rise **20 log N** (×10: +20 dB; ×240: +47.6 dB). Beyond small indices the carrier itself shrinks as $J_0(N\beta)$ ("carrier collapse", first zero at Nβ = 2.405) — multiplying a noisy source to mm-wave can destroy the carrier. A 100 MHz OCXO at −150 dBc/Hz becomes −102.4 dBc/Hz at 24 GHz.
- **Dividers** reduce phase noise by 20 log M until their own floor: a 3.47 GHz VCO at −134 dBc/Hz (1 MHz) ÷8 → −152.1 ideal, −150.3 with a −155 dBc/Hz divider floor.
- **Dual-modulus prescaler** P/P+1 with counters A, B: $N=PB+A$ ($A<P$, $A\le B$) reaches every $N\ge P(P-1)$ (12 for 4/5, 56 for 8/9, 240 for 16/17 — verified by enumeration); the ADF4351 specifies INT ≥ 23 (4/5) and ≥ 75 (8/9, required above 3.6 GHz) [4].
- **Comb generators** (step-recovery/impulse): pulses of width τ at rate $f_0$ give harmonics with envelope $2f_0\tau\,|\mathrm{sinc}(nf_0\tau)|$ — 100 ps pulses at 100 MHz: flat-ish to a few GHz, first null at 10 GHz.

## Intuition (no math)
Distort a sine wave and you create harmonics. A transistor biased off (class C) and driven hard conducts only on the peaks: it produces a train of current pulses at $f_0$ that is rich in harmonics; tune the output to $2f_0$ or $3f_0$ and you have a multiplier. The shorter the pulses, the more even the harmonic content, but the less total current — so each harmonic has a best pulse width, roughly one "slot" of the harmonic's period.

Multiplying frequency also multiplies any wobble in phase. If the input's phase jitters by 1°, the doubled output's phase jitters by 2° — twice the phase deviation, four times the phase-noise power: +6 dB per doubling, 20 log N overall. Dividing does the opposite, until the divider's own electronic noise takes over. This is why low-noise microwave sources start from an ultra-clean low-frequency crystal (and why a PLL's in-band noise rises with 20 log N).

Symmetry cleans up the spectrum: two identical devices driven in opposite phase produce outputs whose odd harmonics cancel when summed (push-push) — the same trick as a balanced mixer.

## The math

### Level 1
- Harmonic content of a truncated cosine of peak $I_{max}$, conduction angle α (half-angle $h$):
$$\frac{I_n}{I_{max}}=\frac{2}{\pi}\,\frac{\sin nh\cos h-n\cos nh\sin h}{n(n^2-1)(1-\cos h)}\qquad(n\ge2)$$
(derived by integrating $\cos n\theta$ against the pulse; verified vs FFT). Output power at $nf_0$ into a tuned load $R$: $\frac12I_n^2R$; efficiency $\eta_n=\frac{1}{2}\frac{V_n}{V_{DC}}\frac{I_n}{I_{DC}}$.
- Phase modulation index multiplies: $\beta\to N\beta$; small-index sidebands $\approx\beta/2$ → +20 log N; exact carrier and sidebands $J_0(N\beta)$, $J_1(N\beta)$.

### Level 2
**(a) Optimum conduction angle.** Maximising $I_n/I_{max}$ over $h$ gives α ≈ 120°, 80°, 60° for n = 2, 3, 4 (≈ 240°/n) (check A). At those angles the "collector efficiency" with a tuned load and full swing is ≈ 63 %; smaller α raises efficiency further but lowers output and gain.

**(b) Push-push.** The two devices' currents are $i(\theta)$ and $i(\theta+\pi)$; harmonic $k$ picks up a factor $1+e^{jk\pi}$ → 0 for odd $k$, 2 for even $k$ (check B: fundamental $10^{-16}$, 2nd doubled).

**(c) APDP.** $i=2I_s\sinh(v/nV_T)$ is odd → only odd harmonics (check H: 2nd at −314 dB relative, 3rd −2.5 dB at 0.4 V drive) [see also [mixers](mixers.md#level-2--derivations) for harmonic mixing].

**(d) Page and Manley–Rowe bounds.** For any nonlinear *resistor*, the conversion efficiency to the $n$th harmonic is at most $1/n^2$ (Page, 1958) [2]. For a lossless nonlinear *reactance*, the Manley–Rowe power relations permit all input power to appear at one harmonic, so a varactor multiplier's efficiency is limited only by the diode's series resistance and the idler/harmonic terminations [2][3]. Step-recovery diodes store charge during forward conduction and snap off abruptly, producing picosecond-edge impulses rich in harmonics (comb generators, high-order ×N).

**(e) Phase noise.** For $x(t)=\cos(\omega_0t+\varphi(t))$, an ideal ×N produces $\cos(N\omega_0t+N\varphi(t))$: $S_\varphi\to N^2S_\varphi$, $L\to L+20\log N$ (check C: +6.02, +20.01 dB for ×2, ×10 at small index). When $N\beta$ is not small, power moves out of the carrier: $|J_0(N\beta)|^2$ — at ×100 with β = 0.01 rad the sideband is only 4.8 dB below the carrier and the 20 log N rule overestimates by 1.2 dB; at Nβ = 2.405 the carrier vanishes. For broadband noise the equivalent condition is integrated $N\varphi_{rms}\gtrsim1$ rad.
Division by M: $L\to L-20\log M$, plus the divider's additive floor (edge jitter), typically −150 to −165 dBc/Hz for good logic families (check D).

**(f) Dual-modulus counting.** A P/P+1 prescaler divides by P+1 for A cycles and by P for B−A cycles: $N=A(P+1)+(B-A)P=PB+A$. All integers are reachable once consecutive B values' ranges $[PB,PB+P-1]$ overlap without gaps, requiring $B\ge P-1$ so that $A$ can span $0…P-1$ with $A\le B$: $N\ge P(P-1)$ (check E). Chips impose somewhat higher minima for timing reasons [4].

**(g) Comb spectra.** A train of rectangular pulses of width τ at $f_0$ has harmonic amplitudes $2Af_0\tau|\mathrm{sinc}(nf_0\tau)|$ (check F); impulse-like SRD pulses give a slowly falling comb used as a harmonic reference or in sampling phase detectors.

### Level 3 — injection-locked and regenerative dividers
- **Injection-locked frequency dividers (ILFD)**: an oscillator free-running near $f_{in}/M$ locks when injected with $f_{in}$ through a nonlinearity; lock range ∝ $\frac{f_0}{2Q}\frac{V_{inj}}{V_{osc}}$ (Adler-type) — very low power at mm-wave but narrow range.
- **Regenerative (Miller) dividers**: a mixer with feedback through a filter: $f_{out}=f_{in}-f_{out}$ → $f_{in}/2$; broadband, no free-running oscillation, needs sufficient loop gain.
- **Digital dividers** (CML/ECL flip-flops): broadband, highest power at mm-wave; their jitter sets the divider floor.
- **Multiplier chains** for mm-wave radar (e.g. 12 GHz × 2 = 24 GHz, or 19.25 GHz × 4 = 77 GHz in automotive transceivers) trade source complexity against 20 log N noise and spurious sub-harmonics that must be filtered.

## Design equations & rules of thumb

| Quantity | Equation / value | Notes |
|---|---|---|
| Optimum conduction angle | ≈ 240°/n | 120°, 80°, 60° for ×2, ×3, ×4 |
| Harmonic current | $I_n/I_{max}$ formula above | 0.276, 0.185, 0.139 at optimum |
| Resistive multiplier limit | $\eta\le1/n^2$ | ×2: −6 dB, ×3: −9.5 dB |
| Varactor multiplier | up to 100 % (ideal) | real: 50–80 % for ×2 at UHF/microwave |
| Phase noise multiplication | $+20\log N$ | ×2 +6.0, ×3 +9.5, ×8 +18.1, ×240 +47.6 dB |
| Carrier collapse | $J_0(N\beta)=0$ at 2.405 | keep $N\varphi_{rms}\ll1$ rad |
| Division | $-20\log M$ to the floor | floor −150…−165 dBc/Hz |
| Prescaler contiguity | $N\ge P(P-1)$ | 4/5: 12; 8/9: 56 |
| Comb envelope | $2f_0\tau\lvert\mathrm{sinc}(nf_0\tau)\rvert$ | null at $1/\tau$ |

## Worked examples

### Example 1 — 433.92 MHz from a 144.64 MHz source (×3)
Class-C tripler, conduction angle ≈ 80°: $I_3/I_{max}$ = 0.185. For 100 mW output at 433.92 MHz from 5 V with ≈ 4.5 V swing: $R_{L3}=V^2/(2P)$ = 101 Ω, $I_3$ = 44 mA → $I_{max}$ = 240 mA; the truncated-cosine DC coefficient at 80° is 0.147, so $I_{DC}$ ≈ 35 mA and η = 0.1 W/(5 V × 35 mA) ≈ 57 % (63 % would need the full 5 V swing). Output filtering must reject 144.64 MHz (−1 order) and 289.28/578.56 MHz (2nd/4th) by ≥ 60 dB for regulatory compliance — a 2–3 section band-pass after the tripler. Phase noise +9.5 dB relative to the 144.64 MHz source.

### Example 2 — Doubler with push-push for a 2.4 GHz LO from 1.2 GHz
Two identical transistors driven in antiphase (from a balun) with collectors tied: fundamental and 3rd harmonic cancel (limited by device/balun matching — see [baluns](baluns-and-rf-transformers.md#level-1--definitions-and-mixed-mode-quantities): 1 dB/5° imbalance leaves the fundamental only ≈ 23 dB down), leaving 2.4 GHz and 4.8 GHz; a simple low-pass removes 4.8 GHz. Phase noise +6 dB.

### Example 3 — 24 GHz radar LO from a 100 MHz OCXO
×240 raises the −150 dBc/Hz floor to −102.4 dBc/Hz and a −130 dBc/Hz @ 1 kHz close-in value to −82.4 dBc/Hz. Multiplying a PLL-stabilised 12 GHz VCO by 2 instead (+6 dB) is usually quieter and cheaper. Check carrier-collapse: the integrated phase error of the 100 MHz source × 240 must remain ≪ 1 rad.

### Example 4 — Why the ADF4351 needs the 8/9 prescaler above 3.6 GHz and INT ≥ 75
The 4/5 prescaler core is limited to 3.6 GHz [4]; with 8/9, the theoretical contiguity limit is 56, the chip specifies 75. With a 25 MHz PFD, INT ≥ 75 means VCO ≥ 1.875 GHz — always satisfied in the 2.2–4.4 GHz VCO range; with a 100 MHz PFD (integer mode) N ≥ 75 → VCO ≥ 7.5 GHz: impossible, so high PFD frequencies force the 4/5 prescaler and < 3.6 GHz operation.

## Practical notes
- **Drive level** sets the conduction angle of a class-C multiplier: document it and keep it constant (temperature, supply); use a self-biasing emitter/source resistor with bypass for stable operation.
- **Filtering** after multipliers is essential and often the largest part of the design — include the fundamental and adjacent harmonics in the rejection mask.
- **Stability:** multipliers are prone to parametric oscillations (especially varactor designs); check with harmonic-balance stability analysis ([stability](amplifier-stability-and-biasing.md#level-3--invariants-hidden-instabilities-and-limits-of-the-two-port-view)).
- **Dividers:** feed with sufficient slew rate; a square-wave output is rich in odd harmonics — low-pass filter if used as an LO or reference.
- **Frequency plans** with multipliers must include sub-harmonic leakage (e.g. 12 GHz leakage from a 24 GHz doubler).

## Common mistakes & misconceptions
- *"Multiplying by N raises phase noise by 10 log N."* It is 20 log N (phase deviation scales by N, power by N²).
- *"A multiplier is just an amplifier with a harmonic filter."* The optimum bias/conduction angle differs for each harmonic, and gain drops sharply with n.
- *"Division is free."* It reduces phase noise only down to the divider's own floor, and the output is a square wave with harmonics.
- *"Push-push needs no filter."* Imbalance leaves residual fundamental (≈ 20–30 dB down typically) and the 4th harmonic remains.
- *"Any N is available from a dual-modulus prescaler."* Only $N\ge P(P-1)$ contiguously; chips add their own minimum.

## How to simulate / verify
- `tools/verify/rfckt_multipliers.py`: harmonic currents and optimum conduction angles (closed form vs FFT), push-push and APDP symmetry, phase-noise multiplication vs Bessel functions, divider floors, prescaler contiguity enumeration, comb-generator envelope, efficiency bounds.
- SPICE transient or harmonic balance with real device models for multiplier design; spectrum analyser for harmonic/sub-harmonic levels; phase-noise measurement before/after multiplication to confirm 20 log N.

## Open questions / gaps
- Varactor-multiplier design equations (Burckhardt tables, idler circuits) are not covered; add if a varactor multiplier project arises.
- Divider floors quoted as a typical range; part-specific values belong in domain 18.
- Example 1's efficiency uses the ideal truncated-cosine model (no knee, perfect harmonic terminations).

## Sources
1. S. C. Cripps, *RF Power Amplifiers for Wireless Communications*, 2nd ed., 2006, ch. 3 (truncated-cosine analysis used for harmonic currents). (textbook)
2. C. H. Page, "Frequency conversion with positive nonlinear resistors," *J. Res. NBS*, 56(4), pp. 179–182, 1956; J. M. Manley, H. E. Rowe, "Some general properties of nonlinear elements — Part I," *Proc. IRE*, 44(7), pp. 904–913, 1956. (peer-reviewed)
3. S. A. Maas, *Nonlinear Microwave and RF Circuits*, 2nd ed., Artech House, 2003 — multipliers (varactor, SRD, transistor), dividers. (textbook)
4. Analog Devices, *ADF4351* data sheet rev. 0: dual-modulus prescaler 4/5 (≤ 3.6 GHz) or 8/9; INT 23–65 535 (4/5) and 75–65 535 (8/9); MOD 2–4095. (datasheet; read via pdftotext)
5. B. Razavi, "A study of injection locking and pulling in oscillators," *IEEE J. Solid-State Circuits*, 39(9), pp. 1415–1424, Sept. 2004 (injection-locked dividers, lock range). (peer-reviewed)
6. R. L. Miller, "Fractional-frequency generators utilizing regenerative modulation," *Proc. IRE*, 27(7), pp. 446–457, 1939. (peer-reviewed; regenerative divider)
