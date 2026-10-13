---
title: AGC loops and receiver gain control — loop dynamics, attack/decay, digital AGC, gain plans, RSSI, and receiver DSP features (noise blanker, noise reduction, auto-notch)
domain: 06-rf-circuits
slug: agc-loops-and-receiver-gain-control
tags: [agc, automatic-gain-control, vga, linear-in-db, log-detector, rms-detector, attack-time, decay-time, hang-agc, delayed-agc, loop-stability, digital-agc, gain-plan, take-over-point, rssi, sx1276, sx1262, ad9361, rtl-sdr, noise-blanker, noise-reduction, lms, adaptive-line-enhancer, auto-notch, spectral-subtraction]
prerequisites:
  - ../07-noise-linearity/dynamic-range-sfdr-blocking.md
  - ../07-noise-linearity/receiver-cascade-analysis.md
  - detectors-and-power-meters.md
  - ../00-math-foundations/laplace-transfer-functions-bode.md
  - ../00-math-foundations/z-transform-and-discrete-time-systems.md
related:
  - receiver-architectures.md
  - rf-switches-attenuators-limiters.md
  - pa-control-protection-and-sequencing.md
  - ../14-sdr-dsp/software-demodulation.md
  - ../14-sdr-dsp/sdr-front-end-protection-and-filtering.md
  - ../14-sdr-dsp/digital-filters-fir-iir.md
  - ../15-lora-ism-radios/semtech-chip-family.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../18-components-parts/rf-switches-attenuator-parts.md
level: mixed
confidence: medium
last_updated: 2026-10-03
---

# AGC loops and receiver gain control

## Questions this page answers
- How does an AGC loop work, and how do I choose its attack and decay times?
- Why do AGC designs use "linear-in-dB" VGAs and log detectors?
- Why does my AGC oscillate or "pump", and how do I make it stable?
- How fast must an AGC be to catch a LoRa preamble?
- In a receiver with an LNA step and an IF VGA, which gain should I turn down first?
- How does a digital AGC in an SDR work, and how large can its step size be?
- How do AD9361, RTL-SDR and SX127x/SX126x chips control gain?
- How do I turn SX1276/SX1262 RSSI and SNR registers into a signal level in dBm, and how accurate is it?
- What do a noise blanker, noise reduction (NR) and an auto-notch (ANF) actually do, and why must the blanker come before the narrow filter?

## TL;DR
- **AGC is a feedback loop:** a variable-gain amplifier (VGA), a power detector, a comparison with a reference, and a loop filter (usually an integrator).
- **With a linear-in-dB VGA (gain $G_{dB}=G_0+K_vV_c$) and a log detector ($V_d=K_d P_{dB}$)**, the loop is linear in decibels. It is first order with **τ = 1/(K_v K_d K_I)**, the same for a 10 dB or a 60 dB step. Settling to within ε dB after a step ΔP takes $t_s=\tau\ln(\Delta P/\varepsilon)$: 20 dB/V, 25 mV/dB and K_I = 400 s⁻¹ give τ = 5 ms, and a 40 dB step settles to 1 dB in 18.4 ms (simulated).
- **With a linear-gain VGA and a linear detector**, loop gain is proportional to signal amplitude: 40 dB more signal makes the loop **100× faster** (simulated). Such loops are sluggish on weak signals and unstable on strong ones.
- **The detector ripple filter adds a pole** ($\tau_f$) and makes the loop second order with $\zeta=\tfrac12\sqrt{\tau/\tau_f}$. Use $\tau_f\le\tau/2$ for ζ ≥ 0.707 (4.3 % overshoot, matches simulation). A digital AGC with $D$ samples of loop delay is stable only for $\mu<2\sin\big(\pi/(2(2D+1))\big)$: 2, 1, 0.618, 0.347 for D = 0, 1, 2, 4 (verified).
- **Attack fast, decay slow.** To settle 40 dB to 1 dB within a quarter of a LoRa 8-symbol preamble, attack τ must be ≤ 0.56 ms at SF7/125 kHz and ≤ 17.8 ms at SF12. With a 300 ms decay, a receiver needs about 0.9 s to recover 60 dB after a strong burst.
- **Take gain out late, at the back of the chain first.** In the cascade example, reducing IF gain first holds NF at 1.6–1.9 dB up to −80 dBm. Bypassing the LNA first costs 11.3 dB of NF at −80 dBm for no linearity benefit.
- **RSSI:** SX127x LoRa gives Packet Strength = −157 + PacketRssi (HF port), plus PacketSnr/4 when SNR < 0 [3]. That rule is within 0.4 dB below −10 dB SNR but 3 dB off at 0 dB SNR. An N-sample noise-power estimate has σ ≈ 4.34/√N dB.
- **DSP features (simulated):** blanking impulses *before* a 200 Hz CW filter restored SNR from 2.6 to 41.1 dB (clean 42.5 dB); blanking after the filter gave only 4.3 dB. An LMS line enhancer raised a tone's SNR by 7 dB. An LMS auto-notch removed a heterodyne by 77 dB while changing broadband audio by only +0.5 dB.

## Intuition (no math)
A receiver must handle signals from below its noise floor to a few milliwatts, more than 100 dB. No ADC, mixer or demodulator covers that range at once. The AGC is a thermostat for signal level: it measures how strong the signal is after some gain, compares it with a target, and turns the gain up or down to hold the target.

Three design questions follow.
1. **What does it measure?** Measure after the channel filter and the loop protects the demodulator from your own signal's level changes. Measure wideband, before the filter, and it also protects the front end from strong neighbours. Many receivers do both: a fast wideband overload detector and a slower in-channel level loop.
2. **How fast?** Too slow and the start of a packet (or a fading peak) overloads the ADC. Too fast and the AGC follows the signal's own amplitude modulation, flattening AM, distorting SSB and QAM. Slow decay with fast attack is the classic compromise.
3. **Where is the gain taken out?** Gain at the front sets noise figure; gain at the back sets how much drive the last stages see. Reduce the back-end gain first, and touch the LNA only when the signal is so strong that noise no longer matters.

Why "linear in dB"? Received power changes multiplicatively (path loss, fading), so a loop that thinks in decibels behaves the same at −110 dBm and at −30 dBm. A loop that thinks in volts is effectively a different loop at every signal level.

The DSP extras are small cousins of the AGC. A **noise blanker** spots impulses (ignition, switching) while they are still short and silences them. Once a narrow filter has stretched them into long ringing bursts it is too late. **Noise reduction** and the **auto-notch** use an adaptive predictor. Periodic things (a CW tone, a heterodyne whistle) are predictable from the recent past; noise and speech are much less so. Keep the predictable part to get NR; subtract it to get ANF.

## The math

### Level 1 — the blocks and their laws
- **VGA gain law.** *Linear-in-dB* (exponential): $G_{dB}=G_0+K_vV_c$, with $K_v$ in dB/V. *Linear*: $G=aV_c$.
- **Detector law.** *Log*: $V_d=K_d(P_{dB}-P_{int})$, with $K_d$ in V/dB, e.g. AD8307 25 mV/dB ([detectors](detectors-and-power-meters.md)). *RMS*: $V_d\propto\sqrt{\overline{v^2}}$. *Peak/envelope*: $V_d\propto\max|v|$.
- **Loop filter.** Integrator $\dot V_c=K_I(V_{ref}-V_d)$, with $K_I$ in s⁻¹ (an op-amp $1/RC$ or a charge-pump current into a capacitor), usually followed by a ripple filter $\tau_f$.
- **Figures of merit.** Attack time (settling after a level increase), decay or release time (after a decrease), hang time (hold before decay), static regulation (output change per input change, ideally 0 dB/dB with an integrator), AGC range (dB of gain control), and threshold. In a *delayed AGC* the loop does nothing below the threshold, so weak-signal NF is untouched.

### Level 2 — derivations
**(a) The dB-domain loop is first order and level-independent.** Write everything in dB: $P_{out}=P_{in}+G_0+K_vV_c$, and $\dot V_c=-K_IK_d(P_{out}-P_{tgt})$. Differentiating the first equation and substituting the second gives
$$\dot P_{out}=\dot P_{in}-K_vK_dK_I\,(P_{out}-P_{tgt})\quad\Rightarrow\quad \tau=\frac{1}{K_vK_dK_I}.$$
The input level appears nowhere in τ. After a step of ΔP dB the output error is $\Delta P\,e^{-t/\tau}$, so settling within ε dB takes $t_s=\tau\ln(\Delta P/\varepsilon)$. Simulation with $K_v$ = 20 dB/V, $K_d$ = 25 mV/dB and $K_I$ = 400 s⁻¹ gave τ = 5.000 ms for 10, 40 and 60 dB steps, and 1-dB settling of 11.5 / 18.4 / 20.5 ms, equal to the formula (script §A). The loop's closed-loop response to input-level changes is a high-pass $s\tau/(1+s\tau)$ in dB. Slow fading is removed; fast amplitude modulation passes.

**(b) The linear loop's gain scales with the signal.** With $y=aV_cx$ (VGA), an envelope detector and $\dot V_c=K(r-y)$: $\dot y=ax\dot V_c=axK(r-y)$, so $\tau=1/(aKx)$. A 40 dB stronger input gives a 100× faster loop: 10 ms vs 1000 ms in §B. If $K$ is set for good settling at weak signals, the loop will ring or oscillate at strong ones once the ripple pole and delays are included. This is the main reason commercial AGC parts pair an exponential VGA with a log or RMS-in-dB detector.

**(c) The detector filter makes it second order.** A detector filter $1/(1+s\tau_f)$ (needed to remove ripple at $2f_{IF}$, or the envelope of noise-like signals) gives the characteristic equation $\tau\tau_fs^2+\tau s+1=0$:
$$\omega_n=\frac{1}{\sqrt{\tau\tau_f}},\qquad \zeta=\frac12\sqrt{\frac{\tau}{\tau_f}}.$$
$\tau_f=\tau/2$ gives ζ = 0.707 and 4.3 % overshoot; $\tau_f=2\tau$ gives ζ = 0.354 and 30.5 % overshoot. Both match simulation (§C). The trade-off: ripple suppression needs a large $\tau_f$, but stability needs $\tau\ge2\tau_f$, so loop speed and ripple are tied. A 455 kHz IF with $\tau_f$ = 2.5 ms suppresses $2f_{IF}$ ripple by 83 dB, far more than needed. A baseband (zero-IF or audio) AGC has no such easy separation, so it uses envelope/RMS estimates over a window and accepts the delay.

**(d) Attack, decay and hang.** Use separate integrator rates for "too loud" ($\tau_a$) and "too quiet" ($\tau_d$). After a strong burst ends, recovery to within ε of target takes $\tau_d\ln(\Delta P/\varepsilon)$. For 300 ms decay and a 60 dB burst that is 899 ms (§D, simulated). A slow decay makes the receiver deaf after every nearby keying. That matters at a launch site with other teams' transmitters (see [co-site interference](co-site-interference-and-transmitter-intermod.md)). *Hang AGC* (SSB voice) holds the gain for a hang time (≈ 0.5–2 s) after the signal drops, then decays fast; this avoids noise "breathing up" between syllables. *Pumping:* an AGC with τ comparable to the period of the modulation removes part of the modulation. A 1 ms AGC strips 1.1 dB from a 300 Hz AM envelope; a 50 ms AGC leaves it intact (§D). AM broadcast AGCs therefore use τ ≥ about 50 ms. Constant-envelope signals (FM, FSK, LoRa) can use fast AGC with no such penalty.

**(e) Peak vs RMS vs log detection.** For a constant-envelope signal all three agree. For noise-like signals (OFDM, multiple channels, or the noise floor itself), a log detector reads 2.5 dB below RMS, and a peak detector reads the crest factor above it (8–12 dB for OFDM). Use RMS (or a mean-square digital estimate) where the ADC must not clip on peaks while the average is regulated. Then set the target back-off from full scale ≥ crest factor plus headroom for the loop's overshoot ([detectors](detectors-and-power-meters.md#level-2--derivations)).

**(f) Digital AGC.** In an SDR, the gain update in dB is $g[n+1]=g[n]+\mu(p_{ref}-p[n-D])$, where $p[n]=p_{in}[n]+g[n]$ and $D$ is the pipeline delay (FIFO, filter group delay, register write latency). The error obeys $z^{D+1}-z^D+\mu=0$. With $D=0$ the loop is stable for 0 < μ < 2 and its time constant is ≈ 1/μ updates. Delay tightens the bound to
$$\mu_{max}=2\sin\!\frac{\pi}{2(2D+1)}$$
(D = 1: 1.0; 2: 0.618; 4: 0.347; 8: 0.184; numerical roots agree to 10⁻³, §E). In practice choose μ ≤ μ_max/4 for a well-damped response. For a gain applied *in the analog domain* (a tuner register), D includes the I²C/SPI write and settling time, often milliseconds, so the analog AGC of an SDR must be slow or must use a separate fast overload detector.

**(g) The take-over point: where to reduce gain.** The script uses a cascade of LNA (18 dB, NF 1.2 dB, IIP3 −8 dBm, with a −2 dB bypass mode), mixer (8 dB, 9 dB, +12 dBm), IF VGA (50 dB max, NF and IIP3 each worsening 1 dB per dB of reduction) and ADC (NF 28 dB). It regulates the ADC input to −15 dBm (§F):

| Input | IF-first: LNA, IF red. → NF / IIP3 | LNA-first: → NF / IIP3 |
|---|---|---|
| −110 dBm | on, 0 dB → 1.6 dB / −51 dBm | same |
| −80 dBm | on, 11 dB → **1.9 dB** / −40 dBm | bypass, 0 dB → **11.3 dB** / −31 dBm |
| −60 dBm | on, 31 dB → 11.5 dB / −20.5 dBm | bypass, 11 dB → 14.0 dB / −20 dBm |
| −40 dBm | bypass, 31 dB → 31 dB / −0.3 dBm | same |
| −30 dBm | bypass, 41 dB → 41 dB / +8.2 dBm | same |

In both policies the IIP3 stays 37–59 dB above the wanted signal, because the wanted signal is regulated. NF rising with a strong wanted signal is harmless: SNR = $P_{in}$ − (−174 + NF + 10 log B) stays huge. The one case where early (LNA) gain reduction is right is a **strong blocker** that would compress the LNA or mixer while the wanted signal is weak. That needs a wideband detector, because the in-channel detector cannot see the blocker, and it is exactly the case [07 dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md) calls AGC desensitisation.

### Level 3 — AGC in real receivers
- **Two-loop receivers.** Fast *wideband overload* detection (peak detectors after the LNA/mixer, ADC overrange flags) cuts RF gain in large steps within microseconds. A slower *in-channel power* loop then trims the remaining gain for the demodulator. The AD9361 offers manual, *slow attack* (a second-order loop with hysteresis that keeps average power in a window, measured after the first half-band decimator, while still reacting quickly to large overloads), *fast attack* (for bursty TDD/GSM: settle within the first part of a burst, then lock) and *hybrid* (slow attack with gain updates triggered by a control pin) [5].
- **RTL-SDR.** The R820T tuner has its own analog AGC and the RTL2832U has a digital AGC, both tuned for DVB-T. For measurement and weak-signal work they are usually disabled and a fixed gain is set ([SDR survey](../14-sdr-dsp/sdr-hardware-survey.md)). An SDR's software AGC acts only on the digitised band. It cannot see a blocker that the tuner's filter removes after the LNA has already compressed ([14 front-end protection](../14-sdr-dsp/sdr-front-end-protection-and-filtering.md)).
- **SX127x (FSK/OOK).** The AGC runs packet by packet at receiver start-up. It is triggered by an RSSI threshold and/or preamble detection (RxTrigger). It chooses one of six LNA gains: G1 (max) to G6 (−48 dB). NF runs from about 4–7 dB at G1 to about 44 dB at G6 and IIP3 from about −22..−11 dBm to +11..+14 dBm, band-dependent. The gain is held until a restart. A receiver whose AGC was set on a strong packet must be restarted (RestartRxWithoutPllLock) to receive a weak one [3]. With AgcAutoOn = 0 the LNA gain is manual.
- **SX127x LoRa and SX126x.** Gain control is internal and automatic (the SX126x has a "boosted" Rx gain mode that trades extra current for a few dB of sensitivity: −137 vs −133 dBm at SF12/BW125 in the data-sheet table; [07](../07-noise-linearity/dynamic-range-sfdr-blocking.md)). Because the AGC acts on the total power in the front end, a strong out-of-channel signal present at packet start reduces gain and desensitises the receiver for that packet.
- **Analog AGC ICs.** VGAs with built-in detectors (e.g. AD8367/AD8368-class parts) set the loop time constant with one external capacitor against an internal resistance. Their exponential gain law gives level-independent dynamics [6]. Log detectors in "controller mode" (AD8318-class) integrate the error on a capacitor and drive a VGA or PA gain pin directly; this is the same loop as an ALC ([PA control](pa-control-protection-and-sequencing.md)).

**AGC settings by signal type** (starting points; derived from §D's pumping and burst arguments and common receiver practice [2]):

| Signal | Detector | Attack | Decay / hang | Why |
|---|---|---|---|---|
| CW / Morse | peak | 1–5 ms | 100–500 ms, or hang 0.2–1 s | keep the noise from rising between dits |
| SSB voice | peak | 1–2 ms | hang 0.5–2 s, then fast | syllabic envelope must not pump |
| AM broadcast | average (carrier) | ≥ 50 ms | ≥ 50 ms | τ ≫ 1/(2π·50 Hz) keeps audio AM |
| FM / FSK / LoRa (constant envelope) | any | as fast as the preamble needs (SF7: ≤ 0.5 ms) | short, or freeze per packet | no amplitude information to lose |
| QAM / OFDM | RMS | per frame (preamble), then freeze | per frame | gain changes inside a symbol corrupt EVM |
| GNSS (signal below noise) | noise power (ADC level statistics) | slow (≫ ms) | slow | regulates noise, not the satellites; a jump flags interference |

**Gain control in chips you are likely to use:**

| Device | What is controlled | How | What to watch |
|---|---|---|---|
| SX127x FSK/OOK | LNA G1–G6 (0 to −48 dB) | AGC at Rx start (RSSI and/or preamble trigger), held until restart | restart Rx after a strong packet [3] |
| SX127x LoRa | LNA + internal | AgcAutoOn; internal algorithm | blocker at packet start sets low gain |
| SX126x | internal, plus "boosted" Rx option | automatic | RSSI constants need calibration [4] |
| AD9361 / Pluto | LNA/mixer/TIA/LPF gain table | manual / slow / fast / hybrid modes [5] | choose fast attack for bursty LoRa |
| RTL-SDR (R820T + RTL2832U) | tuner LNA/mixer/VGA, digital gain | tuner AGC + DVB-T digital AGC | turn off for measurement; set fixed gain |
| u-blox GNSS | front-end gain to hold ADC statistics | automatic; reported as an AGC count in UBX-MON-RF | AGC drop with C/N₀ drop = interference ([21](../21-gnss/gnss-interference-jamming-spoofing.md)) |

### Level 3 — RSSI
**What RSSI measures.** RSSI is the total power (signal + noise + interference) in the receiver bandwidth, referred to the antenna port through a calibration constant. For FSK on the SX127x, $\text{RSSI}=-\text{RssiValue}/2$ dBm. It is smoothed over 2–256 samples (RssiSmoothing; Semtech quotes ±6 dB at 2 samples, ±3 dB at 16 and ±1.1 dB at 256 for 10 dB SNR). The response time is $2^{\text{RssiSmoothing}+1}/(4\,\text{RxBw[kHz]})$ ms, e.g. 0.385 ms for 16 samples at 10.4 kHz [3].

**LoRa packet strength.** Semtech (SX127x) gives Packet Strength = −157 + PacketRssi on the HF port (−164 on the LF port). For SNR < 0 add PacketSnr × 0.25, since the SNR register is in quarter dB [3]. The SX126x reports $-\text{RssiPkt}/2$, $\text{SnrPkt}/4$ and a despread "SignalRssiPkt" [4]. *Why add the SNR?* Below the noise floor the measured power is mostly noise. The signal is exactly
$$S=P_{tot}+\text{SNR}_{dB}-10\log_{10}(1+\text{SNR}),$$
and Semtech's rule drops the last term: the error is +0.14, +0.41, +1.19 and +3.01 dB at SNR −15, −10, −5 and 0 dB (§G). Semtech also notes that the constants change with the front end (LNA boost, external LNA, mismatch), recommends a single-point calibration, and states that PacketRssi loses linearity above about −100 dBm (a 16/15 slope correction is offered) [3].

**Statistics.** The power of N independent noise samples estimated in dB has σ ≈ 4.34/√N dB: 3.5 dB at N = 2, 1.1 dB at 16, 0.27 dB at 256 (§G). Semtech's table is consistent with about 2–3σ plus a calibration floor. One packet's RSSI is therefore ±1–3 dB. Average many packets before drawing link-budget conclusions ([link margin](../09-propagation-link-budget/link-margin-availability.md)).

### Level 3 — receiver DSP features
- **Noise blanker (NB).** An impulse of width $t_p$ through a filter of bandwidth B becomes a ringing burst lasting about 1/B. Its peak falls by about $Bt_p$, so its energy now overlaps the wanted signal for 1/B. Detect and blank (zero or interpolate) the impulses in a **wide** path, *before* the narrow channel filter. In §H, 0.1 ms impulses at 100 per second wrecked a CW tone in a 200 Hz filter: 2.6 dB SNR against 42.5 dB clean. Blanking 2.7 % of samples ahead of the filter restored 41.1 dB; blanking after the filter gave 4.3 dB. The cost: strong *wanted* signals in the wide path can trigger the blanker and cause intermodulation-like artefacts. That is why ham receivers make the NB threshold adjustable.
- **Noise reduction (NR).**
  - *LMS adaptive line enhancer* (ALE) [8]: an adaptive FIR predicts $x[n]$ from $x[n-D-k]$. Periodic components are predictable and appear at the predictor output; white noise is not. A 64-tap normalised-LMS ALE lifted a tone in white noise from −1.1 to +6.0 dB SNR in a 0–4 kHz band (§H).
  - *Spectral subtraction* [9]: estimate the noise spectrum in pauses, subtract it frame by frame in the FFT domain, and accept some "musical noise" artefacts.
- **Auto-notch (ANF).** Use the same LMS predictor but output the prediction *error*. Steady tones (heterodynes, carriers, birdies) are removed; less predictable signals (speech, data) pass. The decorrelation delay must exceed the wanted signal's correlation time, and the notch width is about $f_s/N_{taps}$. With 128 taps and a 1 ms delay the heterodyne fell by 77 dB and broadband audio changed by +0.5 dB. With 32 taps the response ripple was +1.6 dB (§H).
- **IF shift / passband tuning and roofing filters** move or narrow the selectivity ahead of the AGC detector, so a strong neighbour no longer controls the gain. In analog receivers that means crystal roofing filters at the first IF ([crystal filters](duplexers-diplexers-and-crystal-filters.md)).

## Design equations & rules of thumb

| Quantity | Equation | Typical numbers |
|---|---|---|
| dB-loop time constant | $\tau=1/(K_vK_dK_I)$ | 20 dB/V, 25 mV/dB, 400 s⁻¹ → 5 ms |
| Settling within ε dB | $t_s=\tau\ln(\Delta P/\varepsilon)$ | 40 dB → 1 dB: 3.7τ |
| Linear-loop τ | $1/(aKx)$ | ∝ 1/amplitude: 40 dB → 100× |
| Ripple-pole damping | $\zeta=\frac12\sqrt{\tau/\tau_f}$ | τ_f = τ/2 → 0.707 |
| Digital step bound with delay D | $\mu<2\sin(\pi/(2(2D+1)))$ | D = 4: 0.347 |
| Digital τ (D = 0, small μ) | ≈ 1/μ updates | μ = 0.01 → 100 updates |
| LoRa attack budget | $\tau\le T_{pre}/(4\ln40)$ | SF7: 0.56 ms; SF12: 17.8 ms |
| AM depth kept | $|s\tau/(1+s\tau)|$ at $f_m$ | τ 1 ms, 300 Hz: −1.1 dB |
| Packet strength (SX127x, SNR<0) | −157 + PacketRssi + PacketSnr/4 | error 3 dB at SNR 0 dB |
| RSSI estimate spread | σ ≈ 4.34/√N dB | N = 16: 1.1 dB |
| ANF notch width | ≈ $f_s/N_{taps}$ | 48 kHz/128 = 375 Hz |

Rules of thumb:
- Regulate the ADC to a target set back from full scale by crest factor + 3–6 dB (QPSK/LoRa: 6–8 dB; OFDM: 12–15 dB).
- Make attack 10–100× faster than decay. Use hang AGC for SSB voice.
- Detect after the channel filter for level control. Add a separate wideband overload detector for blockers.
- Reduce gain from the back of the chain first. Step the LNA only above the take-over point, with 3–6 dB of hysteresis so it does not chatter.

**Design procedure (analog or digital AGC).**
1. List the signals: the weakest and strongest wanted level, crest factor, burst structure (preamble length) and modulation (constant envelope or not).
2. Set the regulation point at the ADC or demodulator: full scale − crest factor − 3–6 dB.
3. Choose the gain law (exponential VGA or digital dB gain) and detector (RMS for noise-like signals, log for range, peak for overload).
4. Choose τ from the burst budget ($\tau\le T_{avail}/\ln(\Delta P/\varepsilon)$) and from the modulation (τ ≫ 1/(2π f_m,min) for AM-type signals).
5. Choose the ripple filter with $\tau_f\le\tau/2$ (analog), or the averaging window and update rate with μ ≤ μ_max/4 (digital).
6. Plan the gain distribution: IF/baseband first, then RF steps above the take-over point, with hysteresis.
7. Add a wideband overload path if strong out-of-channel signals are expected.
8. Verify with stepped and pulsed inputs at the extremes of level and frequency offset.

## Worked examples

### Example 1 — An analog AGC for a 433 MHz ground-station IF that must catch LoRa SF7
Spec: 40 dB step settled to 1 dB within a quarter of the 8-symbol SF7 preamble (2.05 ms). Then $\tau\le2.05\,\text{ms}/\ln40$ = 0.555 ms (§D). Use a VGA with $K_v$ = 20 dB/V and an AD8307-class log detector at 25 mV/dB. Choose τ = 0.5 ms: $K_I=1/(K_vK_d\tau)$ = 4000 s⁻¹, which an op-amp integrator with R = 10 kΩ and C = 25 nF provides. The detector ripple filter must have $\tau_f\le\tau/2$ = 0.25 ms. At a 10.7 MHz IF a single pole of 0.25 ms attenuates the 21.4 MHz ripple by about 90 dB. The 40 dB step then settles in τ ln 40 = 1.84 ms. Check the slowest case too: SF12 has a 262 ms preamble, so the same loop is comfortably fast. Because it is a constant-envelope signal, there is no pumping penalty.

### Example 2 — The linear-VGA trap
A designer uses a multiplier-type VGA (gain ∝ $V_c$) with a diode envelope detector and tunes the loop to 10 ms at a −30 dBm test signal. At −70 dBm the same loop has τ ≈ 1 s (§B): packets are over before the gain arrives. At −10 dBm, τ ≈ 1 ms, close enough to the ripple-filter time constant to ring. Fix it with an exponential (dB-linear) VGA, or by putting a log converter in the detector path.

### Example 3 — Digital AGC in a GNU Radio / FPGA receiver
Gain is applied as a multiplier after the channel filter, the power estimate is a 16-sample moving average, and the update rate is once per 16 samples. The effective delay is D ≈ 2 updates, so μ_max = 0.618. Pick μ = 0.1: τ ≈ 10 updates = 160 samples, 160 µs at 1 MS/s, which is fast enough for any LoRa SF. If the gain is instead written to the SDR's tuner over USB (10 ms latency, i.e. D ≈ 100 updates at 100 µs per update), μ must fall below 0.016. That is why tuner gain is normally left fixed and the AGC is done in software.

### Example 4 — Turning a ground-station log line into dBm
An SX1276 on the HF port reports PacketRssi = 40 and PacketSnr = −40 (−10 dB). Semtech's rule gives −157 + 40 − 10 = −127 dBm; the exact correction gives −127.4 dBm (§G). At SNR ≈ 0 dB the rule over-reads by 3 dB. For link-budget fits, use $S=P_{tot}+\text{SNR}-10\log(1+\text{SNR})$ and calibrate the −157 constant once with a signal generator and attenuator ([17 bench recipes](../17-test-measurement/bench-measurement-recipes.md)).

### Example 5 — An impulse-noise problem at the launch site
A generator or ignition system produces 0.1 ms clicks at 100 Hz. A narrow (200 Hz) CW/beacon receiver drops from 42.5 dB SNR to 2.6 dB. A blanker in the wide (48 kHz) path, triggered at 6× the RMS level of the clean signal plus noise, restores 41.1 dB. The same blanker after the narrow filter gives 4.3 dB (§H). In an SDR, put the blanker on the decimated-but-still-wide stream, before the channel filter.

### Example 6 — Take-over point and hysteresis for the LNA bypass
Use the §F cascade with 76 dB of total gain (LNA on) and a −15 dBm ADC target. The IF VGA's 50 dB of range is used up at $P_{in}$ = −15 − 76 + 50 = **−41 dBm**: that is the natural take-over point. Bypassing the LNA there removes 20 dB, so the IF reduction falls from 50 to 30 dB. Restore the LNA only below −46 dBm (5 dB hysteresis) to avoid toggling on fading. At the switch-over the NF jumps from about 21 to 31 dB. The SNR is still above 100 dB for a 125 kHz channel at −41 dBm, so the jump is invisible to the demodulator. Linearity improves by about 20 dB, just when a nearby launch-site transmitter might push the mixer toward compression.

### Example 7 — How many packets to average for a trustworthy RSSI
Single-packet RSSI scatter comes from estimator noise (σ ≈ 1 dB for the short averages typical of packet RSSI) and fading (σ of several dB on a moving rocket; see [multipath](../09-propagation-link-budget/multipath-fading-doppler.md)). To quote a mean level to ±0.5 dB (1σ) with a combined 3 dB scatter, average $(3/0.5)^2$ = 36 packets. At one packet per second during a 60 s flight, a single "link margin" number therefore has about ±0.5 dB of statistical uncertainty before calibration error. Report the spread, not just the mean.

## Practical notes
- **Measure loop dynamics:** feed a pulsed or stepped-attenuator signal (PIN switch or DSA; [18 switches](../18-components-parts/rf-switches-attenuator-parts.md)) and scope the VGA control voltage. You should see a clean exponential with the designed τ for every step size if the loop really is dB-linear.
- **Glitch-free gain steps:** DSAs that change several bits at once can produce momentary attenuation spikes. Use "glitch-less" parts or Gray-code the steps. An LNA bypass switch transient can corrupt a symbol, so step only between packets where possible.
- **Hysteresis on discrete steps:** if an LNA step is 20 dB, set thresholds 3–6 dB apart up and down, or the AGC will toggle on fading.
- **Temperature:** log-detector intercepts drift (tenths of a dB per 10 °C); a VGA's dB/V slope drifts too. The loop holds the *detector* reading constant, so accuracy depends on the detector, not on the VGA.
- **Freeze the AGC during a packet** if the demodulator needs a stable amplitude (QAM, OOK thresholds). Many chips do this automatically after the preamble.
- **Logging for flight analysis:** record RSSI, SNR and the LNA gain step (if available) with each packet. A gain step correlated with your own transmitter's bursts shows self-desense.

- **Bench test recipe for any AGC:**
  1. Signal generator → step attenuator or PIN switch → DUT, with the generator modulated as the real signal (LoRa from a second module, or AM/FSK).
  2. Step the level by 10, 20 and 40 dB, up and down. Log the gain-control voltage or register and the demodulated output.
  3. Repeat at the strongest expected level with a second, off-channel generator present (a blocker test).
  4. Pass criteria: the τ is the same for all step sizes, the overshoot is below the design ζ value, and there is no packet loss at the step for the slowest expected preamble.

## Common mistakes & misconceptions
- *"Faster AGC is always better."* It removes amplitude information (AM, SSB, QAM) and follows noise; match it to the signal.
- *"The AGC protects my receiver from blockers."* Only if its detector sees them. An in-channel detector after the IF filter is blind to a strong neighbour that is compressing the LNA.
- *"Turn down the LNA first to improve linearity."* For a strong *wanted* signal, IF-first keeps NF low with ample IIP3 margin. LNA steps are for blockers and for signals near the front end's own compression.
- *"RSSI is the signal power."* It is total in-band power. Below 0 dB SNR it is mostly noise, which is why LoRa adds the SNR.
- *"A single RSSI reading is accurate to 0.5 dB."* An N-sample estimate has σ ≈ 4.34/√N dB plus calibration error.
- *"The noise blanker can go anywhere."* After a narrow filter the impulses are already smeared and below threshold.
- *"ALC and AGC are different physics."* They are the same control loop: ALC regulates a transmitter's output, AGC a receiver's.

- *"The AGC time constant is set by the integrator capacitor alone."* It is $1/(K_vK_dK_I)$: the VGA slope and detector slope count too, and both drift with temperature.
- *"A digital AGC can use any step size if the loop is slow enough."* Loop delay (FIFOs, register latency) sets a hard stability bound on μ; a loop that is stable in simulation without delay can oscillate in hardware.

## How to simulate / verify
- `python3 tools/verify/rf2_agc.py` (≈ 3 s, ALL PASS) covers: §A dB-loop step responses at 10/40/60 dB; §B linear-loop τ ∝ 1/x; §C ripple-pole damping and overshoot; §D LoRa preamble budget, AM pumping, attack/decay recovery; §E digital-AGC stability with delay; §F gain-policy cascade; §G SX127x RSSI arithmetic and estimator statistics; §H noise blanker, LMS ALE and ANF.
- In GNU Radio, the AGC2/AGC3 blocks have separate attack and decay rates. Test them with a *Signal Source* stepped by a *Multiply Const* driven from a *Vector Source*, and plot gain versus time. In ngspice, model an exponential VGA with a B-source ($v_{out}=v_{in}\cdot10^{K_vV_c/20}$) and a log detector with a B-source on the envelope.

## Open questions / gaps
- AD9361 AGC details are from a search-result summary of UG-570; the PDF could not be fetched. Thresholds and the gain-table structure are not reproduced.
- ADI's AGC tutorial chapter and the AD8367/AD8368 data sheets could not be fetched (timeout/403). The level-independence argument is derived here, and the AD8367 time-constant statement comes from a search summary.
- Semtech does not publish the SX126x LoRa AGC algorithm (thresholds, timing). Its behaviour with mid-packet blockers is untested here.
- The spectral-subtraction NR is described, not simulated.
- The "AGC settings by signal type" table gives practice-derived starting points (ARRL-style receiver practice plus the §D arguments), not values from a standard; tune against the bench recipe.
- The LoRa attack budget assumes the AGC must settle within a quarter of the preamble. Semtech does not state how much preamble its own AGC consumes.

## Sources
1. B. Razavi, *RF Microelectronics*, 2nd ed., Prentice Hall, 2011, §5.4 (gain switching), §13.2.3 (AGC). (textbook; not re-read this session)
2. ARRL, *The ARRL Handbook for Radio Communications*, receiver chapters (AGC attack/decay/hang, noise blankers, DSP NR/ANF). (handbook; background, not re-read)
3. Semtech, *SX1276/77/78/79 data sheet*, rev. 4, Mar. 2015: §4.2.6 receiver start-up (AGC/AFC triggers), §5.5.3 Table 38 LNA gain/NF/IIP3, §5.5.4 FSK RSSI and RssiSmoothing table, §5.5.5 LoRa RSSI/packet strength formulas and notes. https://cdn-shop.adafruit.com/product-files/3179/sx1276_77_78_79.pdf (datasheet; read)
4. Semtech, *SX1261/2 data sheet* (§13.5.3 GetPacketStatus RssiPkt/SnrPkt/SignalRssiPkt, §13.5.4 GetRssiInst). https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf (datasheet; read)
5. Analog Devices, *AD9361 Reference Manual* UG-570, gain control chapter (manual, slow attack, hybrid, fast attack). (app note; **via search summary only**)
6. Analog Devices, *AD8367* and *AD8368* data sheets (linear-in-dB VGA with integrated detector; AGC time constant from an external capacitor). (datasheets; via search summary only)
7. Analog Devices, *AD8307* and *AD8318* data sheets (log-detector slope and controller mode) — as summarised in [detectors](detectors-and-power-meters.md). (datasheets)
8. B. Widrow et al., "Adaptive noise cancelling: principles and applications," *Proc. IEEE* 63(12), 1692–1716, 1975 (adaptive line enhancer, notch). (peer-reviewed; cited)
9. S. F. Boll, "Suppression of acoustic noise in speech using spectral subtraction," *IEEE Trans. ASSP* 27(2), 113–120, 1979. (peer-reviewed; cited)
10. R. G. Lyons, *Understanding Digital Signal Processing*, 3rd ed., Prentice Hall, 2011, §13.30 (digital AGC). (textbook; cited)
11. `tools/verify/rf2_agc.py` (this KB).
