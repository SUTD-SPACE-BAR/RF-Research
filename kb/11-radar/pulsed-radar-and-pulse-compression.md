---
title: Pulsed radar and pulse compression — resolution, PRF and ambiguities, duty cycle, LFM, Barker and polyphase codes, sidelobes and Doppler tolerance
domain: 11-radar
slug: pulsed-radar-and-pulse-compression
tags: [pulsed-radar, prf, pri, unambiguous-range, unambiguous-velocity, duty-cycle, blind-range, eclipsing, pulse-compression, matched-filter, lfm, chirp, barker, frank-code, p4-code, polyphase, golay, sidelobes, taylor-window, hamming, range-doppler-coupling, stretch-processing]
prerequisites:
  - radar-range-equation.md
  - ../10-comms-modulation/matched-filter-detection.md
  - ../00-math-foundations/fourier-series-and-transform.md
related:
  - ambiguity-function-waveforms.md
  - fmcw-radar.md
  - detection-theory-cfar.md
  - clutter-and-mti.md
  - cw-and-doppler-radar.md
  - diy-radar-hardware.md
  - ../10-comms-modulation/spread-spectrum-dsss-fhss-css.md
  - ../15-lora-ism-radios/lora-phy-css-math.md
  - ../14-sdr-dsp/fft-spectral-analysis-windows.md
level: mixed
confidence: high
last_updated: 2026-10-03
---

# Pulsed radar and pulse compression

## Questions this page answers
- What sets a pulsed radar's range resolution — the pulse length or the bandwidth?
- How do I choose the PRF, and why can't I have both unambiguous range and unambiguous velocity?
- What are duty cycle, average power and blind (eclipsed) range?
- What is pulse compression and why do solid-state radars need it?
- Why does a matched-filtered chirp have −13 dB sidelobes, and what does a Hamming or Taylor window cost?
- What are Barker codes, and why is 13 the longest?
- Frank, P4, polyphase codes — when do I use them instead of a chirp?
- What is "range–Doppler coupling" and why is a chirp called Doppler-tolerant?
- How does stretch processing relate to FMCW radar?
- How many samples per resolution cell do I need to avoid straddle loss?

## TL;DR
- **Range resolution is set by bandwidth:** $\Delta R = c/(2B)$ (1 MHz → 150 m, 10 MHz → 15 m, 1 GHz → 15 cm). A simple unmodulated pulse has $B \approx 1/\tau$, so resolution and energy are tied together; pulse compression breaks the tie.
- **PRF trade-off:** unambiguous range $R_u = c/(2\,\mathrm{PRF})$, unambiguous velocity $v_u = \pm\lambda\,\mathrm{PRF}/4$; their product $R_uv_u = c\lambda/8$ is fixed by the wavelength (3.7 × 10⁶ m²/s at 3 GHz). Low-PRF radars are range-unambiguous, high-PRF radars velocity-unambiguous, medium-PRF radars are neither and resolve ambiguities with several PRFs (Chinese-remainder method).
- **Duty cycle** $d = \tau\,\mathrm{PRF}$, $P_{av} = dP_{pk}$; the transmitter's energy per dwell, not its peak power, sets SNR ([radar equation](radar-range-equation.md)). A monostatic pulsed radar cannot receive while transmitting: **blind range $c\tau/2$** (150 m per µs of pulse).
- **Pulse compression:** transmit a long pulse of duration $T$ with a wide bandwidth $B$ (chirp or phase code); the matched filter compresses it to ≈ $1/B$. Gain in peak SNR = **time–bandwidth product $TB$** over an uncompressed pulse of equal peak power.
- **LFM (chirp):** −3 dB width **0.88–0.89/B**, peak sidelobe **−13.3 dB** (unweighted, verified). Hamming weighting: **−41 to −43 dB**, main lobe × 1.48, **1.34 dB SNR loss**; Taylor (n̄ = 5, −35 dB): −35 dB, × 1.35, 0.93 dB loss. Chirps are **Doppler-tolerant** (TB = 100 loses < 0.2 dB at $f_dT$ = 2) but the peak shifts by $f_dT/B$ seconds (**range–Doppler coupling**).
- **Phase codes:** Barker-13 PSL **−22.3 dB** (the best binary code; no longer Barkers are known for odd lengths and none are believed to exist); Frank/P4 polyphase codes give PSL ≈ 1/(πM) (**−34 dB for 256 chips**). Phase codes are **Doppler-intolerant**: Barker-13 loses **3.9 dB at $f_dT$ = 0.5** and 7 dB at $f_dT$ = 1.
- **Sample the compressed output at ≥ 2 samples per 1/B**: one sample per 1/B risks up to **3.92 dB** straddle loss (1.38 dB average); two samples cut the worst case to 0.93 dB.

## Intuition (no math)
A pulsed radar is an echo-sounder: shout, then listen. The time until the echo returns gives the range ($R = c\,t/2$). Two targets are separable if their echoes do not overlap, so a short shout gives fine resolution. But a short shout carries little energy, and detection depends on energy. You could shout louder (more peak power), but transistor amplifiers are limited in peak power; tubes (magnetrons) are not, which is why old radars used kilowatt-to-megawatt short pulses.

Pulse compression is the trick of shouting a long, *distinctive* sound — a rising whistle (chirp) or a Morse-like pattern of phase flips — and then listening with a filter that recognises exactly that pattern. The filter adds up all parts of the long pulse into one sharp peak whose width is set by how much bandwidth the pattern spans, not by how long it lasted. You get the energy of a long pulse and the resolution of a short one. Every GPS receiver, LoRa demodulator and bat does the same thing.

The price: the filter's output has small "echoes of the echo" beside the main peak (range sidelobes), which can hide a weak target next to a strong one. Tapering the filter (windowing) lowers those sidelobes at the cost of a slightly wider peak and a little SNR.

Pulsing also samples the target's motion. From one pulse to the next, the target moves, and the echo phase rotates by $4\pi\,\Delta R/\lambda$. Measuring that rotation across many pulses gives the velocity (Doppler), but only unambiguously if the phase turns by less than half a cycle between pulses — which needs a high PRF. A high PRF, though, means the next pulse leaves before echoes from far targets return, so range becomes ambiguous. You can't have both: this is the pulsed radar's fundamental dilemma.

## The math

### Level 1 — timing, resolution and ambiguity
- Pulse width τ (s), pulse repetition interval PRI = 1/PRF (s).
- Echo delay $t_d = 2R/c$ ⇒ $R = ct_d/2$.
- **Range resolution** $\Delta R = c/(2B)$, where $B$ is the waveform bandwidth (for an unmodulated pulse $B \approx 1/\tau$ ⇒ $\Delta R \approx c\tau/2$).
- **Unambiguous range** $R_u = c\,\mathrm{PRI}/2 = c/(2\,\mathrm{PRF})$. A target at $R > R_u$ appears at $R \bmod R_u$ ("second-time-around" echo).
- **Doppler sampling:** pulse-to-pulse phase change $\Delta\phi = 4\pi v_r\,\mathrm{PRI}/\lambda$ (radial velocity $v_r$, positive approaching gives a positive Doppler $f_d = 2v_r/\lambda$). With complex (I/Q) samples, unambiguous for $|\Delta\phi| < \pi$: $|f_d| < \mathrm{PRF}/2$ ⇒ **$v_u = \pm\lambda\,\mathrm{PRF}/4$**.
- **Ambiguity product:** $R_u\,v_u = \dfrac{c}{2\,\mathrm{PRF}}\cdot\dfrac{\lambda\,\mathrm{PRF}}{4} = \dfrac{c\lambda}{8}$.
- **Duty cycle** $d = \tau\cdot\mathrm{PRF}$; $P_{av} = d\,P_{pk}$; energy per pulse $E = P_{pk}\tau$.
- **Blind (eclipsed) range:** echoes arriving while transmitting (and during T/R switch recovery $t_{rec}$) are lost: $R_{min} \approx c(\tau + t_{rec})/2$. Targets at multiples of $R_u$ are also eclipsed (the next pulse is being sent).

| Radar (illustrative) | f | τ | B | PRF | ΔR | $R_u$ | $v_u$ | duty | blind R |
|---|---|---|---|---|---|---|---|---|---|
| DIY S-band tracker | 3 GHz | 1 µs | 1 MHz | 1 kHz | 150 m | 150 km | ±25 m/s | 0.1 % | 150 m |
| X-band marine (short pulse) | 9.41 GHz | 80 ns | 12.5 MHz | 3 kHz | 12 m | 50 km | ±24 m/s | 0.024 % | 12 m |
| X-band high-PRF pulse-Doppler | 10 GHz | 1 µs | 10 MHz | 100 kHz | 15 m | 1.5 km | ±750 m/s | 10 % | 150 m |

### Level 2 — the matched filter and the chirp

**Why bandwidth sets resolution.** The matched filter output for a point target is the waveform's autocorrelation $R_s(t) = \int s(t')s^*(t'-t)\,dt'$, whose Fourier transform is $|S(f)|^2$ (Wiener–Khinchin). The width of $R_s$ is ≈ 1/(spectral width), independent of how the energy is distributed in time. Two targets are resolved if their autocorrelation peaks are separated by more than about one width: $\Delta t \approx 1/B$ ⇒ $\Delta R = c/(2B)$ [1], [2]. (Matched-filter derivation and the 2E/N₀ result: [matched filter](../10-comms-modulation/matched-filter-detection.md).)

**Compression gain.** For a pulse of peak power $P$ and duration $T$ the matched-filter output SNR is $2E/N_0 = 2PT/N_0$ (the real-passband peak ratio of the [matched filter](../10-comms-modulation/matched-filter-detection.md); it equals $E/N_0 = PT/N_0$ in the complex-envelope bookkeeping used by the [radar equation](radar-range-equation.md), and detection thresholds such as 13.2 dB are in $E/N_0$ — do not mix the two). An uncompressed pulse with the same peak power and the same resolution would last only $1/B$, giving $2P/(BN_0)$. The ratio is **$TB$** — the pulse-compression ratio.

**LFM chirp.** $s(t) = \mathrm{rect}(t/T)\,e^{j\pi\mu t^2}$ with sweep rate $\mu = B/T$ (Hz/s); instantaneous frequency $f_i(t) = \mu t$ sweeps $-B/2 \dots B/2$. Its autocorrelation, for lag $|t| < T$:
$$R_s(t) = \int e^{j\pi\mu t'^2}e^{-j\pi\mu(t'-t)^2}dt' = e^{-j\pi\mu t^2}\!\int_{\text{overlap}} e^{j2\pi\mu t\,t'}dt' \;\Rightarrow\; |R_s(t)| = (T - |t|)\left|\mathrm{sinc}\big(Bt\,(1 - |t|/T)\big)\right|,$$
(sinc(x) = sin(πx)/(πx)). Near the peak ($|t| \ll T$) this is $T\,|\mathrm{sinc}(Bt)|$: a sinc of width ~1/B. The sinc's first sidelobe is **−13.26 dB** and its −3 dB width **0.886/B**. The script finds 0.878–0.879/B and −13.4 to −13.5 dB for TB = 100–1000 (the finite-TB spectrum is not exactly rectangular: Fresnel ripples).

**Weighting (windowing).** A taper $w(t)$ on the receive filter (or equivalently on the spectrum, since for large TB time and frequency map one-to-one along the chirp) lowers the sidelobes of $|S(f)|^2$'s transform — exactly as in [FFT windowing](../14-sdr-dsp/fft-spectral-analysis-windows.md). The filter is then no longer matched, costing SNR:
$$L_{mis} = \frac{|\int w\,|s|^2|^2}{\int |w s|^2\int|s|^2}\ (\le 1).$$

| Receive weighting | PSL (TB = 1000) | −3 dB width | SNR loss |
|---|---|---|---|
| none (matched) | −13.4 dB | 0.88/B | 0 |
| Taylor n̄ = 5, −35 dB | −35.1 dB | 1.18/B (×1.35) | 0.93 dB |
| Hamming | −42.7 dB | 1.30/B (×1.48) | 1.34 dB |

(At TB = 100, Fresnel ripple limits Hamming to −40.9 dB.) Non-linear FM (NLFM) — a chirp whose sweep rate is slowed at the band edges — shapes the spectrum instead of the filter and obtains low sidelobes without mismatch loss [3].

**Range–Doppler coupling.** A Doppler shift $f_d$ moves every frequency of the chirp up by $f_d$; since frequency and time are locked together by $f_i = \mu t$, the received chirp looks like the transmitted chirp *advanced* in time by $f_d/\mu = f_dT/B$. The matched-filter peak therefore appears shifted by
$$\Delta t = \frac{f_dT}{B},\qquad \Delta R = \frac{c\,f_dT}{2B},$$
with only a small loss of peak height (the overlap shrinks by $f_d/B$). Verified: TB = 100, $f_dT$ = 1 → shift exactly 1/B, loss 0.09 dB; $f_dT$ = 2 → 0.18 dB. This is why chirps are called **Doppler-tolerant**: one filter works for all Doppler shifts, at the cost of a known range bias (for an up-chirp, an approaching target appears closer). The ambiguity-function view of the same fact is on [ambiguity function](ambiguity-function-waveforms.md).

**Stretch processing (dechirp-on-receive).** Instead of a matched filter at full bandwidth, mix the received chirp with a replica chirp started at a reference delay. A target at delay $t_0 + \delta$ produces a tone at $\mu\delta$ Hz; an FFT then gives range. The ADC only needs the bandwidth $\mu\,\Delta t_{window}$ of the range window, not $B$ — e.g. a 10 MHz/100 µs chirp gives 667 Hz per metre, so a 1 km window needs only 0.67 MHz of IF bandwidth. **This is exactly how an FMCW radar works** (with the reference delay at zero and the chirp repeated continuously) — see [FMCW radar](fmcw-radar.md).

### Level 3 — phase codes, Doppler sensitivity, sampling and ambiguity resolution

**Binary phase codes.** Divide the pulse into $N$ chips of duration $t_c = 1/B$, each with phase 0 or π. The compressed width is ≈ $t_c$, compression ratio $N$.
- **Barker codes** have aperiodic autocorrelation sidelobes of magnitude ≤ 1 (peak $N$), i.e. PSL = $20\log_{10}(1/N)$. Known lengths: 2, 3, 4, 5, 7, 11, 13 (all verified). Barker-13: PSL **−22.28 dB**, ISL −11.5 dB. No odd-length Barker code longer than 13 exists, and none of even length longer than 4 has been found (a long-standing conjecture) [4], [5].
- **Combined (nested) Barker**, e.g. 13 × 13 = 169 chips: compression 169 but PSL only −22.3 dB (the sidelobes of the outer code repeat).
- **Minimum-peak-sidelobe (MPS)** binary codes found by search give PSL ≈ −20 log N + small; **m-sequences** (maximal-length LFSR codes, as in [spread spectrum](../10-comms-modulation/spread-spectrum-dsss-fhss-css.md)) have ideal *periodic* autocorrelation (−1/N) — ideal for CW/periodic radars — but aperiodic PSL ≈ 1/√N. Random binary codes: PSL ≈ 1/√N or a few dB worse (script: −10 to −18 dB for N = 16–256).
- **Complementary (Golay) pairs:** two codes whose autocorrelation sidelobes cancel exactly when summed — zero sidelobes, but only if the target does not change between the two transmissions (very Doppler-sensitive).

**Polyphase codes** (derived from sampled chirps, so they inherit chirp-like behaviour):
- **Frank code** ($N = M^2$): phase $\phi_{i,k} = 2\pi ik/M$, $i,k = 0\ldots M-1$. PSL ≈ $1/(\pi M)$: computed −21.1 / −27.8 / −34.0 dB for N = 16 / 64 / 256 vs $20\log(1/\pi M)$ = −22.0 / −28.0 / −34.0 dB.
- **P3, P4** (Lewis & Kretschmer): $\phi_n = \pi n(n-N)/N$ for P4 — a sampled LFM with good tolerance to bandwidth limitation; computed PSL −18.8 / −24.4 / −30.4 dB for N = 16/64/256 [6], [3].
- Polyphase codes need an I/Q modulator (or DDS/SDR) rather than a simple BPSK switch.

**Doppler sensitivity (computed, peak searched over delay).**

| $f_dT$ | LFM (TB = 100) | Barker-13 | P4-64 |
|---|---|---|---|
| 0.10 | −0.02 dB | −0.14 dB | −0.14 dB |
| 0.25 | −0.02 | −0.91 | −0.91 |
| 0.50 | −0.04 | −3.92 | −3.92 |
| 1.00 | −0.09 | −6.99 | −0.14 |
| 2.00 | −0.18 | −9.12 | −0.29 |

Rule: a phase-coded pulse needs $f_dT \lesssim 0.25$ (< 1 dB) or a bank of Doppler-shifted matched filters. For a 77 GHz radar with a 50 µs waveform and a 30 m/s target, $f_d$ = 15.4 kHz and $f_dT$ = 0.77 — too much for a Barker code without Doppler compensation, trivial for a chirp. P4/Frank recover near integer $f_dT$ because, like a chirp, their peak slides along the delay axis (with grating-like ambiguities at half-integers).

**Sampling the compressed output.** Sampling at exactly one sample per $1/B$ can put the target half a sample off the peak: $|\mathrm{sinc}(0.5)|^2$ = **−3.92 dB** worst case, −1.38 dB on average — the time-domain twin of FFT scalloping. Two samples per $1/B$: worst −0.93 dB, average −0.45 dB.

**Resolving PRF ambiguities.** With two PRFs whose unambiguous ranges are $N_1$ and $N_2$ range cells (coprime), an echo's apparent cells $m_1 = n \bmod N_1$, $m_2 = n \bmod N_2$ determine the true cell $n$ uniquely up to $N_1N_2$ (Chinese remainder theorem; e.g. 7 and 8 cells → 56). Medium-PRF airborne radars use 3–8 PRFs and an "M-of-N PRFs must detect" rule, also to fill the blind zones of each PRF [7].

## Design equations & rules of thumb

| Equation | When valid | Typical numbers |
|---|---|---|
| $\Delta R = c/2B$ | any waveform, matched filtering | 1 MHz → 150 m; 1 GHz → 15 cm |
| $R_u = c/(2\,\mathrm{PRF})$ | pulsed | 1 kHz → 150 km; 10 kHz → 15 km |
| $v_u = \pm\lambda\,\mathrm{PRF}/4$ | complex (I/Q) Doppler sampling | 3 GHz, 10 kHz → ±250 m/s |
| $R_uv_u = c\lambda/8$ | fundamental | 3.74 × 10⁶ m²/s at 3 GHz |
| $P_{av} = \tau\,\mathrm{PRF}\,P_{pk}$ | — | 100 W, 1 µs, 1 kHz → 0.1 W |
| Blind range $\approx c(\tau + t_{rec})/2$ | monostatic, single antenna | 150 m per µs |
| Compression ratio = TB | matched filter | 100 µs × 1 MHz = 100 (20 dB) |
| LFM PSL −13.3 dB; Hamming −42 dB, ×1.48 width, 1.34 dB loss | TB ≳ 100 | Taylor −35 dB: 0.93 dB |
| LFM coupling $\Delta R = cf_dT/(2B)$ | — | see example 2 |
| Barker-N PSL = −20 log N | N ≤ 13 | −22.3 dB |
| Frank PSL ≈ 1/(π√N) | N = M² | −34 dB @ 256 |
| Phase codes: keep $f_dT \lesssim 0.25$ | < 1 dB loss | otherwise Doppler filter bank |
| ≥ 2 samples per 1/B | straddle < 0.93 dB | 1 sample: up to 3.92 dB |

## Worked examples

**Example 1 — Pulsed S-band radar to follow a rocket to 10 km.** Requirements: 15 m resolution, 10 km range, rocket radial speed up to 300 m/s, f = 3 GHz (λ = 0.1 m).
- Bandwidth: $B = c/(2\cdot15\text{ m})$ = 10.0 MHz.
- Range-unambiguous PRF: $\mathrm{PRF} < c/(2\cdot10\text{ km})$ = 15.0 kHz. Choose 10 kHz ($R_u$ = 15.0 km, margin for the listening window).
- Velocity: $v_u = \lambda\,\mathrm{PRF}/4$ = ±250 m/s < 300 m/s ⇒ ambiguous (the 300 m/s rocket's Doppler 6.0 kHz aliases). Options: raise PRF to 12 kHz ($v_u$ = ±300 m/s, $R_u$ = 12.5 km — just works), or keep 10 kHz and unfold the Doppler using the rate of change of measured range, or use two PRFs. The product $R_uv_u = c\lambda/8$ = 3.74 × 10⁶ m²/s makes it clear why: 10 km × 300 m/s = 3 × 10⁶ fits, barely.

**Example 2 — Pulse compression for a 1 W solid-state PA.** You want the energy of a 100 W × 1 µs pulse (100 µJ) from a 1 W amplifier: use a 100 µs pulse. To keep 150 m resolution, chirp it over 1 MHz (TB = 100, 20 dB compression). Consequences:
- **Blind range $c\tau/2$ = 15.0 km** — a monostatic radar with a 100 µs pulse cannot see anything closer than 15 km. Remedies: a short "fill" pulse for near range, pulse-width diversity, separate TX/RX antennas with enough isolation to receive while transmitting, or give up pulses and use FMCW (which is what most hobby and automotive radars do).
- Range–Doppler coupling for the 300 m/s rocket at 3 GHz: $f_d$ = 6.0 kHz, shift $f_dT/B$ = 0.60 µs ⇒ **90 m** apparent range error — tolerable for detection, but a tracker must correct it (use up- and down-chirps: the errors have opposite signs and cancel in the average).

**Example 3 — Choosing a code for an SDR radar.** An SDR (Pluto/B210) with 20 MHz of bandwidth transmits a 13-chip Barker at 20 Mchip/s (T = 0.65 µs, ΔR = 7.5 m). Doppler tolerance: a drone at 20 m/s at 5.8 GHz has $f_d$ = 774 Hz, $f_dT$ = 5 × 10⁻⁴ — negligible. PSL −22.3 dB is limited: a car at 30 m can hide a drone within ±13 chips at > 22 dB weaker. A 256-chip Frank code (T = 12.8 µs, blind range 1.9 km!) gives −34 dB but is too long for a short-range monostatic SDR radar. For short range with one SDR, CW waveforms (FMCW or periodic m-sequence with continuous correlation) are the practical choice; see [DIY hardware](diy-radar-hardware.md).

## Practical notes
- **T/R switching:** a single-antenna pulsed radar needs a circulator plus a receiver protector (limiter) or a fast T/R switch; recovery time adds to the blind range. Separate TX and RX antennas relax this but leakage still saturates the receiver during transmission.
- **STC (sensitivity time control):** receiver gain ramped up with time after each pulse compensates the $R^{-4}$ law so near echoes do not saturate. FMCW radars get the same effect from a high-pass IF filter.
- **Coherence:** Doppler processing and pulse compression need a phase-coherent transmitter (MOPA: master oscillator + power amplifier). A magnetron is non-coherent — "coherent-on-receive" designs sample each transmitted pulse's phase to compensate.
- **Distortion of the transmit chirp** (PA AM/PM, filter group delay) raises sidelobes; record the actual transmitted pulse through a coupler and use it as the matched-filter reference ("loop-back calibration").
- **Digital generation:** a DDS or SDR can produce LFM and polyphase codes; stretch processing lets a narrowband ADC handle a wideband chirp over a limited range window.
- **Time sidelobes vs dynamic range:** a strong target's sidelobes set the floor for weak nearby targets. For −40 dB you need weighting *and* a clean, linear transmit chain.

## Common mistakes & misconceptions
- **"Shorter pulses give better resolution."** Bandwidth gives resolution. A long chirp resolves as well as a short pulse of the same bandwidth.
- **"Pulse compression gives free SNR."** It gives the SNR of the pulse's *energy*; the energy still has to be transmitted (long pulse × power), and a long pulse creates a long blind range.
- **Forgetting that Doppler aliases.** At low PRF, a fast target's Doppler wraps; a 300 m/s rocket at 3 GHz (f_d = 6.0 kHz) needs PRF ≥ 12 kHz with complex (I/Q) sampling. With a single real channel the same PRF still aliases above PRF/2 *and* you lose the sign of the velocity.
- **Confusing real and complex Doppler sampling.** With only I (no Q), you cannot tell approaching from receding and the unambiguous interval halves to 0…PRF/2.
- **Using a Barker code on a fast target with a long code.** Keep $f_dT < 0.25$.
- **Ignoring range–Doppler coupling of chirps** when fusing range from different sensors: a 90 m bias (example 2) is not noise.
- **Sampling at one sample per resolution cell** and then wondering why SNR fluctuates by up to 4 dB with target position.

## How to simulate / verify
- `tools/verify/radar_pulse_compression.py` (~1 s, **ALL PASS**): timing table, LFM compression width/PSL, Hamming/Taylor weighting (PSL, broadening, loss), Barker 2–13 sidelobes, Frank/P4/random-code PSL, Doppler-loss table, range–Doppler coupling shift, straddle loss, CRT ambiguity resolution.
- Python recipe: `s = np.exp(1j*np.pi*(B/T)*(t-T/2)**2)`; matched filter `np.convolve(rx, np.conj(s[::-1]))`; add `np.hamming(len(s))` to the reference for low sidelobes.
- Hardware: loop the TX output through an attenuator (−60 dB or more) and a delay cable into the RX; the compressed output should show the designed PSL. Any extra sidelobes come from the hardware.

## Open questions / gaps
- Mismatched (sidelobe-suppression) filters for phase codes (e.g. least-squares inverse filters that push Barker-13 sidelobes below −40 dB) are not covered numerically.
- NLFM design procedure (stationary-phase spectral shaping) described only qualitatively.
- The Barker even-length conjecture is stated from textbooks, not checked against recent literature.

## Sources
1. M. I. Skolnik, *Introduction to Radar Systems*, 3rd ed., McGraw-Hill, 2001 — ch. 1 (pulse timing, PRF, ambiguities), ch. 6 (pulse compression). (textbook)
2. M. A. Richards, *Fundamentals of Radar Signal Processing*, 2nd ed., McGraw-Hill, 2014 — ch. 4 (waveforms, LFM, matched filter, range–Doppler coupling), ch. 5 (sampling/straddle). (textbook)
3. N. Levanon, E. Mozeson, *Radar Signals*, Wiley-IEEE Press, 2004 — LFM, NLFM, Barker, Frank, P1–P4, complementary codes, Doppler sensitivity. (textbook)
4. R. H. Barker, "Group synchronizing of binary digital systems," in *Communication Theory* (W. Jackson, ed.), Butterworths, 1953 — Barker sequences. (peer-reviewed/proceedings)
5. M. A. Richards, J. A. Scheer, W. A. Holm, *Principles of Modern Radar, Vol. I*, SciTech, 2010, ch. 20 (fundamentals of pulse compression waveforms). (textbook)
6. B. L. Lewis, F. F. Kretschmer, "Linear frequency modulation derived polyphase pulse compression codes," *IEEE Trans. AES*, vol. 18, no. 5, pp. 637–641, 1982 — P3/P4 codes. (peer-reviewed)
7. G. W. Stimson, *Introduction to Airborne Radar*, 2nd ed., SciTech, 1998 — low/medium/high PRF modes, ambiguity resolution. (textbook)
8. R. L. Frank, "Polyphase codes with good nonperiodic correlation properties," *IEEE Trans. Information Theory*, vol. 9, no. 1, pp. 43–45, 1963. (peer-reviewed)
9. `tools/verify/radar_pulse_compression.py` — all computed numbers. (verification script)
