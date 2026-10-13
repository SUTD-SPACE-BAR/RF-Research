---
title: The ambiguity function and radar waveform choice — definition, properties, rectangular pulse, LFM, codes, pulse trains, accuracy vs resolution
domain: 11-radar
slug: ambiguity-function-waveforms
tags: [ambiguity-function, woodward, volume-invariance, range-doppler-coupling, lfm, barker, costas, pulse-train, bed-of-nails, thumbtack, cross-ambiguity, passive-radar, cramer-rao, rms-bandwidth, waveform-design]
prerequisites:
  - pulsed-radar-and-pulse-compression.md
  - ../10-comms-modulation/matched-filter-detection.md
  - ../00-math-foundations/fourier-series-and-transform.md
related:
  - fmcw-radar.md
  - cw-and-doppler-radar.md
  - diy-radar-hardware.md
  - sar-and-imaging.md
  - ../10-comms-modulation/spread-spectrum-dsss-fhss-css.md
level: advanced
confidence: high
last_updated: 2026-10-13
---

# The ambiguity function and radar waveform choice

## Questions this page answers
- What is the radar ambiguity function and what does it tell me about a waveform?
- Why can't a waveform have perfect range and Doppler resolution at the same time?
- Why does a chirp show a diagonal ridge, and what does that mean physically?
- What do "thumbtack", "ridge" and "bed of nails" ambiguity functions look like, and which waveforms produce them?
- How does a coherent pulse train get its fine Doppler resolution, and where do its ambiguities come from?
- What is a Costas code?
- How accurately can a radar measure range compared with its resolution?
- What is the cross-ambiguity function used in passive radar?
- Which waveform should I pick for my radar?

## TL;DR
- **Definition** (this KB, following Levanon & Mozeson [1]): $\chi(\tau,\nu) = \int s(t)\,s^*(t-\tau)\,e^{j2\pi\nu t}dt$ — the output of a filter matched to $s$ when the echo has delay error τ and Doppler error ν. $|\chi(0,0)| = E$ (the energy) is the maximum.
- **Volume invariance:** $\iint|\chi(\tau,\nu)|^2d\tau\,d\nu = E^2$ for *every* waveform (verified to 10⁻⁶ for rectangular, LFM, Barker-13 and Costas-6). You cannot remove ambiguity, only move it — the radar uncertainty principle.
- **Cuts:** zero-Doppler cut $\chi(\tau,0)$ = autocorrelation (range response); zero-delay cut $\chi(0,\nu)$ = Fourier transform of $|s(t)|^2$ (Doppler response, width ≈ 1/T).
- **Shapes:** rectangular pulse — a ridge-free "blob" $1/B \approx T$ wide in delay and $1/T$ in Doppler; **LFM — a diagonal ridge $\nu = -\mu\tau$** (range–Doppler coupling; one matched filter works for all Dopplers, with a range bias); binary/polyphase codes and **Costas** codes — "thumbtack" (Costas-6 sidelobes exactly 1/N on the chip grid); **coherent pulse train — "bed of nails"** at $\tau = k\,\mathrm{PRI}$, $\nu = m/\mathrm{PRI}$, with Doppler resolution $1/(N\,\mathrm{PRI})$.
- **Accuracy ≪ resolution at high SNR:** the delay Cramér–Rao bound is $\sigma_\tau \ge 1/(2\pi B_{rms}\sqrt{2\,\mathrm{SNR}})$ with SNR the matched-filter output SNR and $B_{rms} = B/\sqrt{12}$ for a flat spectrum. Verified by Monte-Carlo (ratio 0.93–1.05): a 10 MHz chirp (15 m resolution) measures range to **54 cm at 20 dB and 19 cm at 30 dB SNR**.

## Intuition (no math)
Imagine you built a matched filter for "an echo at exactly range R and velocity v". Now feed it echoes from other ranges and velocities and plot how strongly it responds. That map — response versus (range error, velocity error) — is the ambiguity function. Wherever it is large away from the centre, the radar cannot tell the true target from a phantom at that offset: it is "ambiguous". The width of the central peak along each axis is the resolution.

A waveform is like a fingerprint. A plain short pulse has a fat, simple fingerprint. A chirp's fingerprint is stretched along a diagonal: if the target moves (shifting all frequencies up), the chirp looks the same as if it arrived a little earlier, so the radar confuses "moving" with "slightly closer" — harmless if you know it, useful because one filter catches every speed. A random-looking code has a spiky fingerprint with one sharp central peak and low "grass" everywhere else — a thumbtack — good for separating targets in both range and speed but fragile if the Doppler is not known. A train of pulses has a repeating pattern of spikes, a bed of nails: each nail is an ambiguity at a multiple of the pulse interval in range and of the PRF in Doppler.

The total "amount" of ambiguity (volume) is fixed. Designing a waveform means deciding where to put it: in a ridge, in a low pedestal, or in distant nails that you can place outside the region where targets can exist.

## The math

### Level 1 — definition and cuts
For a complex-envelope waveform $s(t)$ with energy $E = \int|s|^2dt$:
$$\chi(\tau,\nu) = \int_{-\infty}^{\infty}s(t)\,s^*(t-\tau)\,e^{j2\pi\nu t}\,dt .$$
- τ (s) = delay mismatch, ν (Hz) = Doppler mismatch between the echo and the filter's assumed values. Range error $c\tau/2$, velocity error $\lambda\nu/2$.
- **Zero-Doppler cut** $\chi(\tau,0) = R_s(\tau)$: the compressed-pulse shape; width ≈ $1/B$ ⇒ range resolution $c/2B$.
- **Zero-delay cut** $\chi(0,\nu) = \int|s(t)|^2e^{j2\pi\nu t}dt$: the Fourier transform of the power envelope; width ≈ $1/T$ ⇒ Doppler resolution $1/T$, velocity resolution $\lambda/(2T)$.

*Convention warning:* Woodward's original form and many books use $s(t)s^*(t+\tau)$ or $e^{-j2\pi\nu t}$; the shapes are identical but ridges and offsets flip sign. Always check which one a figure uses.

### Level 1½ — the same ideas with algebra only
You can use the integral without evaluating it. Three algebra rules carry most of the information:
- **Range cell = $c/(2B)$.** The filter output peak is about $1/B$ seconds wide, and a delay of $1/B$ is a range of $c/(2B)$. Only the bandwidth matters, not the pulse length.
- **Velocity cell = $\lambda/(2T)$.** A Doppler error ν turns the phase of the echo by $2\pi\nu T$ across a pulse of length $T$. Once that reaches one full turn ($\nu = 1/T$) the echo no longer adds up coherently. Since $f_d = 2v/\lambda$, that is a velocity of $\lambda/(2T)$.
- **A chirp trades Doppler for delay.** An up-chirp sweeps $B$ hertz in $T$ seconds, a slope of $\mu = B/T$. A Doppler shift $f_d$ looks exactly like the chirp arriving $\tau = f_d/\mu = f_dT/B$ seconds early. That is the diagonal ridge. The target appears closer by $c\tau/2$, and the peak drops only by the factor $(1-\tau/T)$.
- **Fixed volume.** The central peak covers about $(1/B)\times(1/T)$ of the delay–Doppler plane, and the total "volume" is the same for every waveform. A large time–bandwidth product $BT$ only makes the central peak small. The rest of the volume has to go somewhere: into the ridge, a low pedestal or distant nails.

*Worked number (verified, `tools/verify/s18_level15_numbers.py`).* Take a 10 GHz pulse radar (λ = 3 cm) with a 10 µs chirp of 10 MHz ($BT$ = 100):
- **Range cell:** $c/2B$ = 15 m.
- **Velocity cell:** the Doppler cell is $1/T$ = 100 kHz, which is λ/(2T) ≈ 1.5 km/s. One pulse therefore says almost nothing about speed, which is why radars integrate pulse trains (Example 2).
- **Range bias:** a target closing at 300 m/s has $f_d$ = 20 kHz. That shifts the peak by $\tau = 20\,\text{kHz}\times10\,\mu\text{s}/10\,\text{MHz}$ = 20 ns, a **3.0 m** range bias (0.2 of a cell) with only 0.017 dB of peak loss.

### Level 2 — properties and the canonical shapes

**(1) Maximum at the origin.** By Cauchy–Schwarz, $|\chi(\tau,\nu)| \le \sqrt{\int|s|^2\int|s|^2} = E = \chi(0,0)$. The matched filter responds most strongly to the echo it was designed for.

**(2) Volume invariance (Woodward).** Write $\chi(\tau,\nu)$ as the Fourier transform over $t$ of $g_\tau(t) = s(t)s^*(t-\tau)$. Parseval in ν gives $\int|\chi(\tau,\nu)|^2d\nu = \int|s(t)|^2|s(t-\tau)|^2dt$; integrating over τ then gives $\left(\int|s|^2dt\right)^2 = E^2$. Hence
$$\iint|\chi(\tau,\nu)|^2\,d\tau\,d\nu = E^2 = |\chi(0,0)|^2 .$$
The squared AF has unit volume after normalisation, whatever the waveform [2], [1].

**(3) Symmetry.** $|\chi(-\tau,-\nu)| = |\chi(\tau,\nu)|$ (substitute $t \to t+\tau$). Verified to machine precision for four waveforms.

**Rectangular pulse** of duration $T$: for $|\tau| < T$ the overlap has length $T - |\tau|$ and constant integrand phase, giving
$$|\chi(\tau,\nu)| = \big|(T-|\tau|)\,\mathrm{sinc}\big(\nu(T-|\tau|)\big)\big| .$$
A triangle in delay (width $2T$, resolution ≈ $T$) and a sinc in Doppler (first null $1/T$). Good Doppler resolution needs a long pulse, good range resolution a short one — the dilemma pulse compression solves.

**LFM pulse** $s(t) = \mathrm{rect}(t/T)e^{j\pi\mu t^2}$, $\mu = B/T$: the product $s(t)s^*(t-\tau)$ is a tone at $\mu\tau$ Hz over the overlap, so
$$|\chi(\tau,\nu)| = \big|(T-|\tau|)\,\mathrm{sinc}\big((\nu + \mu\tau)(T-|\tau|)\big)\big| .$$
The peak for each Doppler ν sits at $\tau = -\nu/\mu = -\nu T/B$: a **diagonal ridge** (sign by this convention; verified numerically, e.g. at τ = 16 samples the peak is at ν = −μτ = −5 MHz). Physically: a Doppler-shifted chirp is indistinguishable from a time-shifted one — the range–Doppler coupling derived on the [pulse-compression page](pulsed-radar-and-pulse-compression.md). Along the ridge the response falls only as $(1 - |\nu|/B)$, which is why chirps are Doppler-tolerant.

**Coherent pulse train** of $N$ pulses (width $t_p$) at interval PRI: $\chi$ is the single-pulse AF repeated at $\tau = k\,\mathrm{PRI}$, multiplied in Doppler by the array-factor-like term $\left|\sin(\pi\nu N\,\mathrm{PRI})/\sin(\pi\nu\,\mathrm{PRI})\right|$ (the same "array factor" as in [phased arrays](../12-phased-arrays/array-factor-linear-arrays.md), with time in place of space). Result: a **bed of nails** — main peaks at $\nu = m/\mathrm{PRI}$ (Doppler ambiguity = PRF) with widths $1/(N\,\mathrm{PRI})$, and delay-ambiguity peaks at $k\,\mathrm{PRI}$ of height $(N - |k|)/N$. Verified: nails at 1/PRI = 250 kHz, first Doppler null at 1/(N PRI) = 31.25 kHz for 8 pulses of 4 µs PRI (vs 1 MHz for one 1 µs pulse), delay nail height 7/8.

### Level 3 — codes, thumbtacks, accuracy, cross-ambiguity

**Thumbtack waveforms.** Pseudo-random phase codes (Barker, MPS, m-sequences, polyphase) and frequency-hopped codes spread the volume into a low pedestal of height of order $1/\sqrt{TB}$ (in $|\chi|/E$) around a single narrow spike. They resolve range and Doppler independently (no ridge), at the price of Doppler sensitivity: a phase code designed for zero Doppler loses its compression when $\nu T$ approaches 0.5 (Barker-13 zero-delay response −4.1 dB at $\nu T$ = 0.5 and a null near $\nu T$ = 1). Receivers therefore use a **bank of Doppler-shifted matched filters** — which is just sampling the AF on a grid.

**Costas codes** [3]: $N$ contiguous sub-pulses of length $t_c$, each at a different frequency $f_i = a_i/t_c$, where the permutation $(a_i)$ has all difference vectors distinct (the "Costas property"). Then any shift in (time, frequency) by whole chips overlaps at most one sub-pulse, so the AF sidelobes on the chip grid are at most $1/N$. The Welch construction (prime $p$, primitive root $g$: $a_i = g^i \bmod p$) gives length $p-1$; the script builds Costas-6 from $p = 7, g = 3$, confirms the distinct-difference property and finds off-origin grid peaks of exactly 1/6.

**Accuracy vs resolution.** Resolution is the peak width; accuracy is how precisely a single isolated peak can be located in noise. For complex-baseband samples with white noise of variance σ² and echo amplitude $a$, the Fisher information for delay is $J = 2\,\mathrm{SNR}\,(2\pi B_{rms})^2$, with $\mathrm{SNR} = |a|^2\sum|s|^2/\sigma^2$ (the matched-filter output SNR) and $B_{rms}^2 = \int f^2|S(f)|^2df/\int|S(f)|^2df$ (spectrum centred on zero). Hence
$$\sigma_\tau \ge \frac{1}{2\pi B_{rms}\sqrt{2\,\mathrm{SNR}}},\qquad \sigma_R = \frac{c}{2}\sigma_\tau,\qquad B_{rms} = B/\sqrt{12}\ \text{(flat spectrum)} .$$
With the passband convention this is the textbook $\sigma_\tau = 1/(2\pi B_{rms}\sqrt{2E/N_0})$ [4] (the complex-baseband SNR above equals $E/N_0$ of the real passband signal; see the convention note on the [matched-filter page](../10-comms-modulation/matched-filter-detection.md)). By Fourier duality the Doppler accuracy is $\sigma_\nu \ge 1/(2\pi T_{rms}\sqrt{2\,\mathrm{SNR}})$ with $T_{rms}$ the rms duration ($T/\sqrt{12}$ for a flat envelope). **Monte-Carlo (LFM, B = 10 MHz, T = 10 µs, peak interpolation):** measured $B_{rms}$ = 2.93 MHz (B/√12 = 2.89); std/CRLB = 0.93 at 20 dB and 1.05 at 30 dB — i.e. range precision of 54 cm and 19 cm with a 15 m resolution cell. This is why FMCW radars quote mm-level "accuracy" with cm-level "resolution".

**Cross-ambiguity function (CAF) — passive and bistatic radar.** With a reference copy $x_{ref}(t)$ of the illuminator (e.g. an FM or DVB-T broadcast) and the surveillance channel $x_{surv}(t)$, compute
$$\chi_{ref,surv}(\tau,\nu) = \int x_{surv}(t)\,x_{ref}^*(t-\tau)\,e^{j2\pi\nu t}dt$$
over a coherent integration time $T$ (0.1–1 s). Targets appear as peaks at their bistatic delay and Doppler. The achievable resolution and sidelobes are those of the broadcast signal's own (self-)ambiguity function — FM radio's depends on programme content (poor during silence), DVB-T's is noise-like with pilot-induced ambiguities that must be suppressed [5]. See [DIY hardware — passive radar](diy-radar-hardware.md).

**Where the narrowband AF breaks.** The definition assumes Doppler is a frequency *shift*. For $TB$ very large or targets very fast (ratio $2v/c \cdot TB$ not ≪ 1) the echo is actually time-*compressed* (scaled) and the wideband ambiguity function $\int s(t)s^*(\alpha(t-\tau))dt$ must be used — relevant to sonar and to very wideband radar, rarely to hobby RF radar.

## Design equations & rules of thumb

| Waveform | AF shape | Range resolution | Doppler resolution | Doppler tolerance | Sidelobes | Hardware |
|---|---|---|---|---|---|---|
| Rect pulse ($T$) | blob | $c/2B \approx cT/2$ | $1/T$ | tolerant | triangle (none) | simplest (switch) |
| LFM ($T, B$) | diagonal ridge | $c/2B$ | $1/T$ | very tolerant; bias $f_dT/B$ | −13 dB; −35 to −43 dB weighted | VCO/PLL ramp, DDS; dechirp (FMCW) |
| NLFM | tilted ridge | $c/2B$ | $1/T$ | moderate | low without mismatch loss | DDS/AWG |
| Binary code (Barker-13, MPS) | thumbtack | $c\,t_c/2$ | $1/T$ | poor ($\nu T \lesssim 0.25$) | −22 dB (B13) | BPSK switch |
| Polyphase (Frank, P4) | ridge-like thumbtack | $c\,t_c/2$ | $1/T$ | better than binary | ≈ 1/(π√N) | I/Q modulator |
| Costas / FH | thumbtack | $c/2B$ | $1/T$ | moderate | ≤ 1/N on grid | fast-hopping synth |
| Coherent pulse train | bed of nails | per pulse | $1/(N\,\mathrm{PRI})$ | per pulse | ambiguities at PRI, PRF | coherent TX |
| Noise / broadcast (passive) | thumbtack + pedestal | $c/2B$ | $1/T$ | poor (needs CAF grid) | pedestal ~$1/\sqrt{TB}$ | receiver only |

| Rule | Value |
|---|---|
| Volume invariance | $\iint|\chi|^2 = E^2$ |
| LFM coupling | $\Delta\tau = f_dT/B$, $\Delta R = cf_d/(2\mu)$ |
| Delay CRLB | $\sigma_\tau = 1/(2\pi B_{rms}\sqrt{2\,\mathrm{SNR}})$; flat spectrum $B_{rms} = B/\sqrt{12}$ |
| Pulse-train Doppler resolution | $1/(N\,\mathrm{PRI})$ = 1/(dwell) |

## Worked examples

**Example 1 — FMCW chirp coupling at 77 GHz.** A TI-style chirp with slope 30 MHz/µs and a target at 30 m/s: $f_d$ = 15.41 kHz. In FMCW the beat frequency is $S\tau \pm f_d$, so the range FFT places the target off by $f_dc/(2S)$ = **7.7 cm** — 0.77 range bins for a 1.5 GHz sweep (10 cm resolution). The Doppler FFT across chirps measures $f_d$ separately, so the bias can be corrected; most TI demos ignore it because it is below one bin (see [FMCW](fmcw-radar.md)).

**Example 2 — Doppler resolution of a pulse train.** 8 coherent 1 µs pulses at 4 µs PRI (the script's case): single-pulse Doppler resolution 1 MHz (15 km/s at 10 GHz — useless), train resolution 31.25 kHz (468 m/s), Doppler ambiguity every 250 kHz (3.75 km/s). Velocity resolution is set by the *dwell*: 1 m/s at 10 GHz needs a Doppler resolution of 66.7 Hz, i.e. a coherent dwell $N\,\mathrm{PRI}$ ≈ 15 ms. Blind speeds and staggered PRFs are covered in [clutter and MTI](clutter-and-mti.md).

**Example 3 — Range precision for a rocket-tracking radar.** A 10 MHz chirp (15 m cells) at 30 dB SNR locates the rocket to ≈ 19 cm rms per measurement (MC-verified). With a Kalman filter over 10 measurements per second, the smoothed track is better still — the resolution cell size is not the accuracy limit.

*Track filters (α-β, Kalman), gating and angle (monopulse) accuracy for the same rocket: [radar tracking](radar-tracking-monopulse-and-trackers.md); the general delay/frequency CRB derivation: [estimation theory](../00-math-foundations/estimation-theory-ml-map-crb.md).*

**Example 4 — Why FM-radio passive radar has poor resolution.** In bistatic radar the delay measures the range *sum* $R_t + R_r$, so its resolution is $c/B$ (not $c/2B$). An FM broadcast occupies ~100–200 kHz when modulated (Carson's rule; see [analog modulation](../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md)), giving 1.5–3.0 km of range-sum resolution, degrading further during quiet passages when the instantaneous bandwidth collapses. DVB-T's 7.6 MHz gives ≈ 39 m (≈ 20 m monostatic-equivalent near the baseline extension). With 1 s integration the Doppler resolution is 1 Hz: at 100 MHz that is 3 m/s of bistatic range rate $d(R_t+R_r)/dt$.

## Practical notes
- Plot the AF of your actual transmitted waveform (captured through a coupler), not the ideal one — PA nonlinearity and filter ripple fill in sidelobes.
- For TDM-MIMO or chirp-sequence FMCW, the frame is a pulse train of chirps: expect Doppler ambiguities at the chirp repetition frequency (divided by $N_{TX}$ for TDM-MIMO; see [MIMO](mimo-radar-virtual-arrays.md)).
- In passive radar, clean the reference channel first (direct-path and multipath cancellation, e.g. with an adaptive filter such as ECA/NLMS) and suppress deterministic pilot ambiguities of DVB-T before computing the CAF.
- Computing the AF numerically: for each delay τ, multiply $s(t)s^*(t-\tau)$ and take an FFT over t — the script's `af()` function does this in a few lines.

## Common mistakes & misconceptions
- **"A good waveform has a thumbtack AF, so it has no ambiguity."** The volume is conserved; a thumbtack spreads it into a pedestal that raises the floor for weak targets near strong ones.
- **Treating the LFM ridge as a flaw.** It is a feature (Doppler tolerance); correct the known bias with up/down chirps or with the measured Doppler.
- **Confusing resolution with accuracy.** Resolution = separating two targets (≈ c/2B); accuracy = locating one target (≪ c/2B at high SNR).
- **Mixing AF sign conventions** between references — ridges appear to slope the "wrong" way.
- **Forgetting the pulse-train nails** when choosing PRF: the Doppler ambiguity at PRF and the range ambiguity at PRI are properties of the waveform, not of the processing.

## How to simulate / verify
- `tools/verify/radar_ambiguity.py` (~5 s, **ALL PASS**): numerical AF vs closed forms (rect, LFM), volume invariance and symmetry for four waveforms, bed-of-nails properties, Costas construction and thumbtack sidelobes, Barker Doppler cut, Monte-Carlo delay accuracy vs Cramér–Rao bound.
- To visualise: compute `A, nu = af(s, fs, range(-L+1, L), 4096)` and plot `20*log10(abs(A)/E)` with `plt.imshow` (delay × Doppler).

## Open questions / gaps
- Wideband (scale) ambiguity function not treated numerically.
- Waveform optimisation for low range–Doppler sidelobes (e.g. cyclic algorithms, mismatched filters) not covered.
- DVB-T pilot-ambiguity suppression procedure only referenced, not verified.

## Sources
1. N. Levanon, E. Mozeson, *Radar Signals*, Wiley-IEEE Press, 2004 — ch. 3 (AF definition and properties), ch. 4–6 (LFM, codes, Costas), ch. 7 (pulse trains). (textbook)
2. P. M. Woodward, *Probability and Information Theory, with Applications to Radar*, Pergamon, 1953 — original AF and volume invariance. (textbook)
3. J. P. Costas, "A study of a class of detection waveforms having nearly ideal range–Doppler ambiguity properties," *Proc. IEEE*, vol. 72, no. 8, pp. 996–1009, 1984. (peer-reviewed)
4. M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed., 2001, ch. 6 (AF, pulse compression) and §6.3/ch. 5 on measurement accuracy (rms bandwidth). Also M. A. Richards, *Fundamentals of Radar Signal Processing*, 2nd ed., 2014, ch. 4 & 7 (AF, CRLB for delay). (textbook)
5. H. D. Griffiths, C. J. Baker, *An Introduction to Passive Radar*, Artech House, 2017 — CAF, broadcast-signal ambiguity functions (FM, DAB, DVB-T), direct-path cancellation. (textbook)
6. L. R. Welch / S. W. Golomb, "Constructions and properties of Costas arrays," *Proc. IEEE*, vol. 72, no. 9, pp. 1143–1163, 1984 (Golomb & Taylor) — Welch construction. (peer-reviewed)
7. `tools/verify/radar_ambiguity.py` — all numerical claims. (verification script)
