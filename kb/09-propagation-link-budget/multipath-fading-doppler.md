---
title: Multipath fading, delay spread and Doppler (including rocket Doppler vs LoRa)
domain: 09-propagation-link-budget
slug: multipath-fading-doppler
tags: [multipath, rayleigh, rician, k-factor, delay-spread, coherence-bandwidth, coherence-time, doppler, doppler-rate, lora-frequency-drift, level-crossing-rate, fade-duration, diversity]
prerequisites: [two-ray-ground-reflection.md, ../00-math-foundations/probability-random-processes-and-psd.md]
related: [link-margin-availability.md, empirical-path-loss-models.md, link-budget-methodology.md, polarization-mismatch-loss.md, ../07-noise-linearity/sensitivity-and-mds.md, ../15-lora-ism-radios/lora-phy-css-math.md, ../15-lora-ism-radios/rocket-telemetry-radio-design.md, ../10-comms-modulation/ofdm.md]
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Multipath fading, delay spread and Doppler (including rocket Doppler vs LoRa)

## Questions this page answers
- What are Rayleigh and Rician fading, and what is the K-factor?
- How much fade margin do I need for 99 % or 99.9 % reliability?
- What are delay spread and coherence bandwidth, and is LoRa affected by multipath?
- What Doppler shift does a Mach 3 rocket produce at 433 MHz, and can LoRa handle it?
- Why can the *rate of change* of Doppler during boost break a LoRa link even when the shift itself is fine?
- How often do fades happen and how long do they last?
- How much does diversity (two antennas, two frequencies, two polarisations) help?
- What is "picket fencing" on a mobile VHF signal, and why does moving the antenna a few feet change the signal so much?

## TL;DR
- **Rayleigh fading** (many scattered paths, no dominant one): power is exponential; $P(\text{fade} > M\text{ dB}) = 1 - e^{-10^{-M/10}}$ ⇒ **10 dB margin per decade of outage**: 1 % needs 20 dB, 0.1 % needs 30 dB. **Rician** with a strong line-of-sight component ($K$ = LOS/scattered power) needs far less: at $K$ = 10 dB, 10 dB margin gives 7×10⁻⁴ outage (`tools/verify/prop_doppler_fading.py`, analytic vs Monte-Carlo agree).
- **Delay spread** $\sigma_\tau$ → coherence bandwidth $B_c \approx 1/(5\sigma_\tau)$ (50 % correlation) or $1/(50\sigma_\tau)$ (90 %). Rural σ ~ 0.1–1 µs ⇒ $B_c$ ~ 0.2–2 MHz: a 125 kHz LoRa signal sees mostly *flat* fading. The rocket-to-ground path's ground reflection is delayed by only ns: flat.
- **Doppler shift** $f_d = f v_r/c$: Mach 3 (1029 m/s) radial → **1.49 kHz at 433 MHz, 3.14 kHz at 915 MHz, 5.4 kHz at GPS L1**. LoRa tolerates a static offset of ±25 % of BW (±31 kHz at 125 kHz) — the shift is harmless.
- **Doppler rate** $\dot f_d = f a_r/c$: 10 g of radial acceleration → **142 Hz/s at 433 MHz, 299 Hz/s at 915 MHz**. The SX126x requires the total drift over a packet to stay below $BW/(3\cdot2^{SF})$ (×16 with LowDataRateOptimize) [1]. With 30-byte packets at BW125, **SF10 (LDRO off) and SF12 exceed the limit at 10 g at 433 MHz**; SF7–SF9 stay well inside; at 915 MHz SF10 already fails at 5 g. During boost use **SF7–9 at 433 MHz** and **SF7–8 at 868/915 MHz (125 kHz; SF9 only at ≥ 250 kHz)** for stations within a few km of the pad, or force LDRO on. Here $a_r = \ddot R$ is the **range** acceleration seen by the station, $\mathbf a\cdot\hat{\mathbf r} + v_\perp^2/R$, and it can exceed the rocket's own acceleration: 13.7 g at 2 km from the pad on an 11.1 g flight ([line-of-sight term](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term), `s17_doppler_rate_los.py`).
- **Coherence time** $T_c \approx 0.423/f_d$; **level-crossing rate** and **average fade duration** for Rayleigh fading at 10 dB below RMS: 0.72 crossings/s and 133 ms for $f_d$ = 1 Hz (scale ∝ $f_d$).
- **Diversity** turns 10 dB/decade into much steeper curves: for 0.1 % outage in Rayleigh fading, 30 dB margin (1 branch) → 14.9 dB (2-branch selection) → 7.1 dB (4 branches). The team's independent 433 + 915 MHz links are a frequency-and-pattern diversity pair.

## Intuition (no math)
When a signal reaches the receiver by several paths — direct, off the ground, off hills, trees and buildings — the copies add with different phases. Move the receiver a fraction of a wavelength and the phases change, so the sum rises and falls: **fast fading**. If there are many paths of similar strength, the sum behaves like a random walk and its amplitude is **Rayleigh** distributed — deep fades (20–30 dB below average) happen regularly. If one path (usually line of sight) dominates, the others only jiggle it: **Rician** fading, much milder.

If the paths have very different lengths, the copies are delayed relative to each other (**delay spread**). A signal whose symbols are long compared with the delay spread sees all echoes arrive "at the same time": the channel just scales the whole signal (flat fading). If the bandwidth is wide compared with $1/\text{delay spread}$, different frequency components fade differently (frequency-selective fading) — this is what OFDM and equalisers deal with.

Motion adds **Doppler**. A transmitter moving toward you compresses the waves: the frequency goes up by $v/\lambda$. In a scattering environment, paths from different directions get different Doppler shifts, spreading the spectrum (**Doppler spread**), which is the same thing as the fading changing with time — the faster you move, the faster the fades. For a rocket, the main effect is not scattering but the large, rapidly changing Doppler of the direct path. LoRa copes with a large *fixed* frequency error easily, but its long symbols and packets are sensitive to the frequency *changing during a packet* — exactly what a rocket accelerating at 10–20 g does.

## The math

### Level 1 — definitions
- Rayleigh envelope pdf $p(r) = \frac{r}{\sigma^2}e^{-r^2/2\sigma^2}$; normalised power $x = r^2/\overline{r^2}$ is exponential: $P(x < x_0) = 1 - e^{-x_0}$.
- Rician: LOS amplitude $A$, scattered power $2\sigma^2$, **K-factor** $K = A^2/(2\sigma^2)$. $p(r) = \frac{r}{\sigma^2}e^{-(r^2+A^2)/2\sigma^2}I_0(Ar/\sigma^2)$. Outage: $P(x < x_0) = 1 - Q_1(\sqrt{2K}, \sqrt{2(K+1)x_0})$ (Marcum Q), equivalently a noncentral χ² with 2 degrees of freedom.
- Fade margin $M$ (dB) relative to the mean power: outage $= P(x < 10^{-M/10})$.
- RMS delay spread $\sigma_\tau$ from the power-delay profile; coherence bandwidth $B_c \approx 1/(5\sigma_\tau)$ (correlation 0.5) or $1/(50\sigma_\tau)$ (0.9) (Rappaport [2]).
- Doppler shift $f_d = \frac{v}{\lambda}\cos\alpha = f\frac{v_r}{c}$; maximum Doppler $f_m = v/\lambda$.
- Coherence time $T_c \approx 0.423/f_m$ (geometric mean rule; the stricter $9/(16\pi f_m)$ is also used).
- Doppler rate $\dot f_d = f\,a_r/c$ ($a_r$ = radial acceleration).

### Level 2 — derivations
**Rayleigh from the central limit theorem.** With $N$ paths $\sum a_ie^{j\phi_i}$, random independent phases, the in-phase and quadrature sums are each Gaussian with variance $\sigma^2$ for large $N$; the envelope of two independent zero-mean Gaussians is Rayleigh, and its square is exponential. Adding a deterministic LOS term $A$ gives the Rician distribution.

**Outage vs margin.** Rayleigh: $P_\text{out} = 1 - e^{-1/M_\text{lin}} \approx 1/M_\text{lin}$ for large margins — hence one decade of outage per 10 dB. Script values: margin 10/20/30 dB → 9.5×10⁻², 9.95×10⁻³, 1.0×10⁻³ (Monte-Carlo 9.54×10⁻², 1.00×10⁻², 1.03×10⁻³). Rician, 10 dB margin: $K$ = 3 dB → 4.6×10⁻², 6 dB → 1.65×10⁻² (MC 1.64×10⁻²), 10 dB → 7.4×10⁻⁴, 15 dB → 1.9×10⁻⁸.

**Clarke's model (isotropic scattering around a moving receiver).** Arrival angles uniform in azimuth ⇒ Doppler spectrum $S(f) \propto 1/\sqrt{1 - (f/f_m)^2}$ ("bathtub"), autocorrelation $J_0(2\pi f_m\tau)$. The **level-crossing rate** at normalised threshold $\rho$ (envelope/RMS) is $N_R = \sqrt{2\pi}f_m\rho e^{-\rho^2}$ and the **average fade duration** $\bar\tau = (e^{\rho^2}-1)/(\rho f_m\sqrt{2\pi})$ [2]. At 10 dB below RMS ($\rho$ = 0.316) and $f_m$ = 10 Hz: 7.2 fades/s lasting 13 ms on average; 20 dB below: 2.5/s, 4 ms.

**Rocket Doppler and LoRa's frequency-drift limit.** LoRa demodulation de-chirps and takes an FFT; a static offset $\Delta f$ shifts every symbol's FFT bin identically and is estimated from the preamble (tolerance ±25 % of BW for the SX126x, also bounded in ppm for SF10–12 [1]). A frequency that *changes* during the packet smears the symbol energy across bins and makes the preamble estimate stale. Semtech specifies that the total drift over the packet be below
$$\text{Freq\_drift\_max} = \frac{BW}{3\cdot2^{SF}}\quad(\times16\ \text{with LowDataRateOptimize}),$$
(SX1261/2 Rev 2.2 §4.1.2 [1]). The drift accumulated during a packet of duration $T_\text{pkt}$ in a boost with radial acceleration $a_r$ is $\dot f_dT_\text{pkt} = f a_rT_\text{pkt}/c$. Using the Semtech time-on-air formula (30-byte payload, CR 4/5, 8-symbol preamble, explicit header, CRC; LDRO on when $T_\text{sym}$ > 16 ms), the script tabulates drift/limit (Hz):

| 433 MHz radial accel. | SF7/125 | SF9/125 | SF10/125 | SF11/125 | SF12/125 | SF11/250 | SF12/250 |
|---|---|---|---|---|---|---|---|
| 5 g (71 Hz/s) | 5/326 | 16/81 | 32/41 | 64/326 | 117/163 | 29/41 | 58/326 |
| 10 g (142 Hz/s) | 10/326 | 32/81 | **64/41** | 128/326 | **233/163** | **58/41** | 117/326 |
| 20 g (283 Hz/s) | 20/326 | 64/81 | **128/41** | 257/326 | **467/163** | **117/41** | 233/326 |
| 50 g (708 Hz/s) | 51/326 | **160/81** | **321/41** | **641/326** | **1166/163** | **292/41** | **583/326** |

(bold = exceeds the limit). At 915 MHz the rates double: SF10/125 and SF11/250 fail from 5 g; SF9/125 from ≈ 12 g of range acceleration (68 Hz at 10 g against an 81 Hz limit), which a station near the pad does see (next sentence). Forcing LDRO on for SF10/125 raises its limit to 651 Hz (70 Hz of drift at 10 g: fine). **Meshtastic's LongFast (SF11/BW250) would fail during a 10 g boost at 433 MHz** by this criterion. The rows are values of the range acceleration $\ddot R$, not of the accelerometer reading. A station within a few km of the pad adds the line-of-sight rotation term $v_\perp^2/R$ (up to ≈ 8 g on the 11 g reference flight). The datasheet limit is a "should be kept lower than" condition, not a sharp cliff; exceeding it degrades sensitivity/PER progressively — test with a signal-generator frequency ramp.

### Level 3 — channel classes, K for air-to-ground, and diversity
**Channel classification.** Compare signal bandwidth $B$ with $B_c$ (flat if $B \ll B_c$) and symbol time $T_s$ with $T_c$ (slow if $T_s \ll T_c$). LoRa SF12/BW125 has $T_s$ = 32.8 ms: with a pedestrian at 915 MHz ($f_m$ ≈ 4 Hz, $T_c$ ≈ 100 ms) the channel is slow per symbol but not per packet (1.6 s) — fades during a packet are why long packets at high SF are fragile in mobile use. With $f_d$ = 1.5 kHz of *static* Doppler the rocket's direct path does not decorrelate ($T_c$ refers to Doppler *spread*, which for a single dominant path is small).

**Delay spread values.** Typical RMS delay spreads (Rappaport [2], Parsons [3]): open rural 0.1–0.5 µs; suburban 0.5–2 µs; urban 1–3 µs; hilly terrain up to 5–10 µs (distant reflections). For LoRa BW125 ($1/B$ = 8 µs chip) urban echoes are within a chip or two; the chirp's FFT demodulation tolerates echoes shorter than a few chips, so LoRa is robust to multipath delay but not to deep flat fades.

**K-factor for rocket-to-ground.** An ascending rocket at moderate elevation has a strong LOS path and a specular ground reflection (deterministic two-ray lobing, see [two-ray-ground-reflection](two-ray-ground-reflection.md)) plus weak diffuse scattering: $K$ of order 10 dB or more is typical of air-to-ground measurements at moderate elevations, falling toward low elevations (qualitative statement; ITU-R P.528's time-variability curves and aeronautical channel literature quantify it — not extracted here). The practical fade budget for the ascent is therefore dominated by **deterministic** effects (pattern nulls, lobing, plume) rather than Rayleigh statistics. The **landed** rocket or ground-level LoRa sits in a low-K, often Rayleigh-like environment with lognormal shadowing on top ([link-margin-availability](link-margin-availability.md)).

**Diversity.** $M$ independent Rayleigh branches: selection combining outage $(1 - e^{-1/M_\text{lin}})^M$; maximal-ratio combining $P(\chi^2_{2M}/2 < 1/M_\text{lin})$ (regularised incomplete gamma). Script: 10 dB margin → 9.5×10⁻² (1), 9.1×10⁻³ (2 sel.), 4.7×10⁻³ (2 MRC), 8.6×10⁻⁴ (3 sel.); for 0.1 % outage the selection margin drops from 30.0 to 14.9 (2) and 7.1 dB (4). Independence needs decorrelation: spatial separation ≳ λ/2 for isotropic scattering around a ground terminal (35 cm at 433 MHz), many wavelengths at an elevated station with a narrow angular spread; orthogonal polarisations; frequencies separated by ≫ $B_c$; or times separated by ≫ $T_c$ (repetition/interleaving). The rocket's two links (433 MHz + 915 MHz, different antennas and radios) give frequency *and* pattern diversity — but their failures correlate when both are dominated by the same geometry (landing behind a hill), so diversity helps fades, not blockage.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| Rayleigh outage ≈ $10^{-M/10}$ | $M \gtrsim$ 10 dB | 1 %: 20 dB; 0.1 %: 30 dB |
| Rician outage (Marcum Q) | LOS + scatter | K = 10 dB, M = 10 dB: 7×10⁻⁴ |
| $B_c \approx 1/(5\sigma_\tau)$ | 50 % correlation | σ = 1 µs → 200 kHz |
| $T_c \approx 0.423/f_m$ | Clarke | $f_m$ = 50 Hz → 8.5 ms |
| $f_d = f v_r/c$ | | Mach 3 at 433 MHz: 1.49 kHz |
| $\dot f_d = f a_r/c$ | | 10 g at 433 MHz: 142 Hz/s |
| LoRa drift limit $BW/(3\cdot2^{SF})$ (×16 LDRO) | SX126x, over the packet | SF12/125 LDRO: 163 Hz; SF7/125: 326 Hz |
| LoRa static offset ±25 % BW | SX126x | ±31 kHz at BW125 |
| Selection diversity, 2 branches | independent Rayleigh | 0.1 %: 14.9 dB instead of 30 dB |

## Worked examples
**1 — Doppler budget for the primary link.** A rocket reaching Mach 3 radially: +1.49 kHz at 433.125 MHz (receding: −1.49 kHz). TCXO/XO errors: 10 ppm at each end ≈ ±4.3 kHz each (script §1). Total worst-case static offset ≈ 10 kHz — a third of the ±31 kHz tolerance at BW125, and a problem only at narrow bandwidths (±2.6 kHz tolerance at BW 10.4 kHz). Note that in the SX126x datasheet the SF12 offset limit is also expressed as ±50 ppm (a tighter ppm-based bound at high SF for some bandwidths).

**2 — Which SF survives the boost?** A range acceleration of 10 g at the ground station (a GS well downrange sees a smaller radial component of the motor's acceleration; a GS near the pad sees most of it **plus** the line-of-sight term $v_\perp^2/R$, so its range acceleration can exceed the motor's). At 433 MHz with 30-byte packets: SF7–9 at BW125 pass with ≥ 2.5× margin; SF10/125 without LDRO fails (64 vs 41 Hz); SF12/125 fails (233 vs 163 Hz). At 868/915 MHz keep SF ≤ 8 at 125 kHz (SF9 only at ≥ 250 kHz) during boost if the station is within a few km of the pad, because the range acceleration includes $v_\perp^2/R$ ([15 impairments](../15-lora-ism-radios/lora-impairments-doppler-drift-timing.md#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)). Assumptions: the 10 km reference flight (11.1 g peak), 32-byte frames, stations 0.5–2 km cross-range: SF9/125 at 868 MHz drifts 96–107 Hz against an 81 Hz limit and fails; it passes at 5 km (76 Hz) and at 433 MHz (48–54 Hz) (`s17_doppler_rate_los.py` §3). After burnout, radial acceleration drops to drag + gravity (~1–3 g, decreasing) and higher SFs become usable.

**3 — Fade margin for a ground-level recovery beacon.** Landed rocket in scrub, Rayleigh-like fading plus 6 dB lognormal shadowing: from [link-margin-availability](link-margin-availability.md), a 1 % outage requires ≈ 24 dB above the median predicted level (Rayleigh only: 20 dB; `prop_margin.py` §2). Sending the beacon packet 5 times at intervals longer than the fade duration (seconds for a stationary receiver moved by hand, much longer if nothing moves) helps only if the channel changes between repeats — a *static* landed rocket and a *static* ground station have a quasi-static channel: move the receiving antenna (spatial diversity by walking) or use two receive antennas.

**4 — Fade statistics for a walking recovery team (915 MHz, 1.4 m/s).** $f_m$ = 1.4/0.328 = 4.3 Hz. At 10 dB below the mean: 3.1 fades/s, each ~31 ms; at 20 dB: 1.1/s, ~9 ms. A 1.6 s SF12 packet will contain several 10 dB fades; FEC and interleaving in LoRa (CR 4/8) help; lower SF with shorter packets may do better on the move.

## Practical notes
- **Log frequency error** reported by the LoRa chip (SX126x can report frequency error estimates) along with RSSI/SNR during flight — it gives a Doppler/velocity trace and validates this analysis.
- **Pre-compensate large known Doppler** only if needed (not for LoRa at BW ≥ 62.5 kHz); for narrowband FSK links or GNSS it is standard.
- **GNSS on the rocket**: 5.4 kHz of Doppler at Mach 3 and high dynamics stress the receiver's tracking loops; consumer modules have dynamic-platform settings (u-blox "airborne <4g" etc.) and COCOM-type velocity/altitude limits — see domain 08/20 for GNSS on rockets.
- **Testing:** program a signal generator with a linear frequency ramp (e.g. 150 Hz/s and 300 Hz/s) modulating a LoRa packet stream (or replay a recorded LoRa IQ file with a synthetic Doppler ramp from an SDR) into the ground receiver; measure PER vs SF.

- **"Picket fencing" (ham term).** It is the rapid flutter of a mobile VHF/UHF FM signal as the vehicle drives through the standing-wave pattern of multipath. Fades recur every ~λ/2: 1 m at 144 MHz, 35 cm at 433 MHz. At 50 km/h that is about 2v/λ ≈ 13 deep nulls per second at 144 MHz, of the order of the maximum Doppler frequency $f_d = v/\lambda$ ≈ 6.7 Hz that sets the level-crossing rate in the Clarke model above. The same physics explains why moving a VHF antenna "a few feet" can change the signal by 20 dB, why data error rates rise on multipath channels, and why diversity helps. For ionospheric signals, irregular fading is the random combination of several skywave paths (and o/x modes) ([ionosphere](ionospheric-hf-propagation.md)).

## Common mistakes & misconceptions
- **"Doppler of a few kHz will break LoRa."** The static shift is fine; the *rate* of change during a packet is the issue at high SF.
- **"SF12 is always the most robust setting."** Not during high-acceleration flight phases, and not on a moving receiver where the channel changes during a 1.6 s packet.
- **Using Rayleigh statistics for an elevated LOS link** — gives far too much margin; the dominant effects are deterministic (pattern, lobing).
- **Assuming repetition equals diversity** on a static channel.
- **Confusing coherence time with the Doppler shift of a single path.** $T_c$ describes the decorrelation due to Doppler *spread*.

## How to simulate / verify
- `tools/verify/prop_doppler_fading.py` — rocket Doppler at 433/915/1575 MHz, LoRa tolerances, Doppler-rate vs SX126x drift limit table (uses `noise_sensitivity.lora_toa`), Rayleigh/Rician outage (analytic + Monte-Carlo), LCR/AFD, coherence time/bandwidth, selection/MRC diversity.
- GNU Radio channel model blocks (fading, frequency offset/ramp) with a software LoRa modem (gr-lora_sdr) reproduce PER vs Doppler rate ([14-sdr-dsp](../14-sdr-dsp/software-demodulation.md)).
- HIL: the flight software can log the chip's frequency-error estimate per packet; compare with $f v_r/c$ from the trajectory.

## Open questions / gaps
- No measured PER-vs-Doppler-rate data for SX126x/LLCC68 found; the datasheet drift limit is the only criterion (test needed; cross-domain note to 15/20).
- Air-to-ground K-factor statistics (e.g. from aeronautical channel measurements) not extracted; K ≳ 10 dB is qualitative.
- Delay-spread ranges are textbook generalities, not site measurements.

## Sources
1. Semtech, *SX1261/2 Data Sheet* Rev 1.2 (2019) Table 3-8 (frequency offset tolerance ±25 % BW; SF10–12 ppm limits) and Rev 2.2 (Dec 2024) §4.1.2 (Freq_drift_max = BW_L/(3·2^SF); ×16 with LowDataRateOptimize), §6 (time on air). (datasheet)
2. T. S. Rappaport, *Wireless Communications*, 2nd ed., 2002, ch. 5 (small-scale fading: Rayleigh/Rician, delay spread, coherence bandwidth 1/(5σ) and 1/(50σ), Clarke model, LCR, AFD, coherence time). (textbook)
3. J. D. Parsons, *The Mobile Radio Propagation Channel*, 2nd ed., Wiley 2000, ch. 5–7 (fading statistics, wideband channels, delay spreads). (textbook)
4. A. Goldsmith, *Wireless Communications*, Cambridge 2005, ch. 3 (statistical multipath), ch. 7 (diversity: selection, MRC). (textbook)
5. R. H. Clarke, "A statistical theory of mobile-radio reception," *Bell Syst. Tech. J.* 47(6), 957–1000 (1968). (peer-reviewed)
6. S. O. Rice, "Mathematical analysis of random noise," *Bell Syst. Tech. J.* 23–24 (1944–45). (peer-reviewed) — Rician distribution.
7. Y. A. Doroshkin et al., "Experimental study of LoRa modulation immunity to Doppler effect in CubeSat radio communications," *IEEE Access* 7, 75721–75731 (2019). (peer-reviewed) — LoRa tolerates large static Doppler; dynamic Doppler is the limit (abstract only consulted).
8. `tools/verify/prop_doppler_fading.py`, `tools/verify/noise_sensitivity.py` (this KB).
