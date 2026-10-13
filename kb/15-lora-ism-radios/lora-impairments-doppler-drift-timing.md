---
title: LoRa impairments — frequency offset, Doppler, drift, timing, capture and interference
domain: 15-lora-ism-radios
slug: lora-impairments-doppler-drift-timing
tags: [lora, doppler, doppler-rate, cfo, tcxo, crystal, ldro, frequency-drift, capture-effect, inter-sf-interference, multipath, rocket]
prerequisites:
  - lora-phy-css-math.md
  - ../04-real-components-hf/crystals-and-resonators.md
  - ../09-propagation-link-budget/multipath-fading-doppler.md
related:
  - lora-sensitivity-and-link-budget.md
  - semtech-chip-family.md
  - rocket-telemetry-radio-design.md
  - ground-station-design.md
  - ../10-comms-modulation/synchronization-carrier-timing.md
  - ../05-analog-electronics/oscillators.md
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# LoRa impairments — frequency offset, Doppler, drift, timing, capture and interference

## Questions this page answers
- How much frequency error between transmitter and receiver can LoRa tolerate?
- Does a Mach 3–5 rocket's Doppler shift break a LoRa link at 433 or 915 MHz?
- Why can acceleration (Doppler *rate*) break LoRa even when the Doppler shift is small?
- Why does a ground station close to the pad see more "acceleration" than the rocket's accelerometer reports?
- Which SF/BW settings survive the boost phase of a high-power rocket?
- Do I need a TCXO, or is a ±10–20 ppm crystal fine?
- What does low-data-rate optimisation (LDRO) protect against, and can I force it on?
- What is the LoRa capture effect, and what happens when two packets collide?
- Are different spreading factors really orthogonal?
- How does multipath affect LoRa?
- Can my 433 MHz radio interfere with my 900 MHz radio on the same rocket?

## TL;DR
- **Static offset**: all Semtech LoRa receivers tolerate a TX–RX carrier offset of **±25 % of BW** with no sensitivity loss (±31.25 kHz at 125 kHz) [1][2][3]. SX127x/SX126x add an SF-dependent limit: ±50 ppm (SF12), ±100 (SF11), ±200 (SF10) [1][2] — numerically this is a constant **0.2 chip of timing slip per symbol**, i.e. a sampling-clock limit (our inference).
- **Doppler shift** $f_D = (v/c)f$: Mach 5 (1715 m/s) = 5.7 ppm = **2.48 kHz at 433 MHz, 5.28 kHz at 923 MHz** — negligible against ±25 % BW for BW ≥ 62.5 kHz. Not a problem.
- **Doppler rate** $\dot f = (a/c)f$: 10 g radial acceleration = **142 Hz/s at 433 MHz, 302 Hz/s at 923 MHz**. Semtech requires the total drift during a packet to stay below $BW/(3\cdot2^{SF})$ (×16 with LDRO) [2][3]. For a 32-byte packet at 125 kHz this allows ≈ 320/86/23/6 g at SF7/8/9/10 (433 MHz) and half that at 923 MHz. **During boost, use SF7–8 at 125 kHz or SF ≤ 9 at 250 kHz / SF ≤ 10 at 500 kHz (SF9/125 is still fine at 433 MHz but fails at 868/915 MHz for stations within a few km of the pad); SF10–12 at 125 kHz can drop packets at a few g.** The acceleration that counts is the range acceleration $\ddot r = \mathbf a\cdot\hat{\mathbf r} + v_\perp^2/R$, not the vehicle's own: the line-of-sight rotation term adds up to ≈ 8 g on the 11 g reference flight, so a station 0.5 km / 2 km from the pad sees **15.3 g / 13.7 g** (`s17_doppler_rate_los.py`, [Level 2](#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)).
- A no-tracking simulation (`lora_css_sim.py`) gives the same order of magnitude (SF12/125 with LDRO: errors start at ~43 Hz/s ≈ 3 g at 433 MHz), so the SF12/125 boost tolerance is **≈ 3 g (simulation, no tracking) to 6 g (Semtech rule, 163 Hz over a 1.81 s packet)** — a factor of 2 between the two estimates. The Norby CubeSat flight found high-SF LoRa failing at high Doppler rate near zenith — consistent [5].
- **Crystals** ([crystals and resonators](../04-real-components-hf/crystals-and-resonators.md)): per-device ±10 ppm typ, ±30 ppm max [6]. With both ends worst-case, a ±20 ppm crystal fits ±25 % BW only for BW ≥ 125 kHz at 433 MHz and BW ≥ 250 kHz at 923 MHz; use a **TCXO** (±0.5–2.5 ppm) for narrower BW. PA self-heating drifts crystals during long packets (SX1276 crystal: ~2.2 kHz over a −20…+28 °C swing vs ~0.2 kHz with a TCXO [7]).
- **Crystal g-sensitivity** (~2 ppb/g [6]): a 20 g ignition/burnout step shifts the carrier 17 Hz at 433 MHz, 37 Hz at 923 MHz — about one FFT bin at SF12/125.
- **Capture**: same-SF packets collide; the stronger survives if it is ≥ 6 dB stronger (Semtech CCR_LL −6 dB [1]) and arrives before the weaker one's last ~5 preamble symbols [8]. Different SFs are only **quasi-orthogonal** (≈ −16 dB SIR threshold [9]).
- **Multipath** with path differences below $c/BW$ (2.4 km at 125 kHz) is flat fading; longer echoes look like a delayed same-SF interferer.

## Intuition (no math)
A LoRa receiver first listens to the preamble — a row of identical up-chirps — and measures where their de-chirped tones land. Any constant frequency error just shifts every tone by the same amount, so the receiver notes the shift and subtracts it for the rest of the packet. That is why a fixed offset (even a big Doppler shift) is harmless as long as it stays inside the window the receiver searches (±25 % of BW).

What the receiver cannot easily handle is an offset that **keeps changing after the preamble**. A rocket accelerating toward or away from you changes its Doppler shift every millisecond; a crystal warming up under the PA drifts slowly; a shock jolts the crystal. If the tone position wanders by a sizeable fraction of one FFT bin during the packet, symbols near the end are decoded as their neighbours. The bin width is $BW/2^{SF}$ — only 30 Hz at SF12/125 kHz — while the packet lasts seconds, so slow modes are fragile. Fast modes (SF7, wide BW) have wide bins (977 Hz at SF7/125, 3.9 kHz at SF7/500) and short packets, so they barely notice.

LDRO is Semtech's built-in remedy: it throws away the two lowest bits of every symbol, so only every fourth bin is a legal symbol and the receiver has room to track the drift.

## The math

### Level 1 — offsets in hertz, bins and ppm
- Frequency bin (after de-chirp + FFT): $\Delta f_{bin} = BW/2^{SF}$ (SF7/125: 977 Hz; SF9/125: 244 Hz; SF12/125: 30.5 Hz).
- Static window: $|f_{err}| \le 0.25\,BW$ [1][2][3].
- Clock error $\varepsilon$ (ppm) at carrier $f_c$: $f_{err} = \varepsilon f_c$; worst-case TX+RX: $2\varepsilon f_c$.
- Doppler: $f_D = \frac{v_r}{c}f_c$; Doppler rate $\dot f_D = \frac{a_r}{c} f_c$ ($v_r = \dot r$, $a_r = \ddot r$: first and second time derivatives of the range $r$ from the ground station). $a_r$ is **not** the vehicle's acceleration projected on the line of sight: it also contains $v_\perp^2/R$ (see [below](#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)). The tables in g are tables of $\ddot r$.

`tools/verify/lora_doppler.py` output:

| Speed | v/c | 433.125 MHz | 868 MHz | 923 MHz | 2.44 GHz |
|---|---|---|---|---|---|
| Mach 1 (343 m/s) | 1.14 ppm | 0.50 kHz | 0.99 kHz | 1.06 kHz | 2.79 kHz |
| Mach 3 (1029 m/s) | 3.43 ppm | 1.49 kHz | 2.98 kHz | 3.17 kHz | 8.37 kHz |
| Mach 5 (1715 m/s) | 5.72 ppm | 2.48 kHz | 4.97 kHz | 5.28 kHz | 13.96 kHz |
| LEO 7.6 km/s | 25.4 ppm | 11.0 kHz | 22.0 kHz | 23.4 kHz | 61.9 kHz |

| Radial accel. | 433 MHz | 923 MHz |
|---|---|---|
| 1 g | 14.2 Hz/s | 30.2 Hz/s |
| 10 g | 142 Hz/s | 302 Hz/s |
| 20 g | 283 Hz/s | 604 Hz/s |
| 50 g | 708 Hz/s | 1510 Hz/s |

(Mach numbers use 343 m/s; the speed of sound falls to 295 m/s at 11 km, so quote speeds in m/s.)

### Level 1½ — ppm to hertz to bins, algebra only
- **Hertz.** $f_{err} = \varepsilon f_c$ with ε in ppm × 10⁻⁶. The two ends add in the worst case.
- **Bins.** Divide by the bin width $BW/2^{SF}$. A whole-bin error would shift every symbol value by one. The preamble measures and removes a static offset anywhere inside the window of ±0.25·BW.
- **The fractional part costs SNR.** An offset of half a bin splits the energy between two bins: $20\log\mathrm{sinc}(0.5)$ = −3.9 dB.
- **What hurts is change during the packet.** The drift or Doppler sweep over the time on air must stay below $BW/(3\cdot2^{SF})$ (×16 with LDRO).

*Worked number (verified, `tools/verify/s18b_level15_numbers.py`).* SF12/125 kHz at 433.125 MHz has a 30.5 Hz bin.
- **Two ±2 ppm TCXOs:** 1.73 kHz = **57 bins**. That is large, but well inside the 1024-bin static window.
- **Mach 1 Doppler:** 0.50 kHz = 16 bins, also static and removed by the preamble.
- **During a 1.81 s packet (32 B):** a steady 3 g sweeps 77 Hz, 6 g 154 Hz and 10 g **256 Hz**, against the **163 Hz** LDRO limit. This is where the canonical boost tolerance of ≈ 3–6 g at SF12/125 comes from ([canonical values](../00-math-foundations/canonical-values-and-conventions.md#d-lora-modules-gnss-and-singapore-regulation)).

### Level 2 — what a frequency error does to the de-chirped spectrum
Add a frequency offset $\delta f$ to symbol $s$: $r[n] = x_s[n]e^{j2\pi \delta f n/BW}$. After de-chirping, the tone is at $s + \delta$ bins with $\delta = \delta f\,2^{SF}/BW$. Write $\delta = L + \lambda$ (integer + fraction):
- The integer part $L$ shifts every symbol equally → estimated from the preamble and removed (if uncorrected it is indistinguishable from a timing offset; the 2.25 down-chirps separate the two — see [PHY page](lora-phy-css-math.md)).
- The fractional part spreads energy across two bins: peak magnitude $= |\sin(\pi\lambda)/(N\sin(\pi\lambda/N))| \approx |\mathrm{sinc}\,\lambda|$. Loss: 0.14 dB at 0.1 bin, 0.91 dB at 0.25 bin, **3.92 dB at 0.5 bin** (script). At 0.5 bin the two neighbouring bins are equal and hard decisions fail half the time (SF9, −12 dB SNR: SER jumps from 0 to 0.50 in simulation).

**Linear drift (Doppler rate).** With $f(t) = f_0 + \dot f t$ and $f_0$ removed at the start of the payload, symbol $k$ sees residual $\dot f\,(k+\tfrac12)T_s$. For a receiver that does *not* track, the last payload symbol fails when the residual reaches the decision boundary — half a bin without LDRO, two bins with LDRO (only every 4th bin legal):
$$\dot f_{crit} \approx \frac{m\,BW/2^{SF}}{N_{sym}T_s},\qquad m = 0.5\ (\text{no LDRO}),\ 2\ (\text{LDRO}).$$
**Semtech's rule** (SX1261/2 §4.1.2 [2], SX1280 §6.2.7.2 [3]): the **total frequency drift over the packet transmission time** must stay below $Freq\_drift\_max = BW\_L/(3\cdot 2^{SF})$ — one third of a bin — relaxed to $16\times$ with LDRO. (The equation is an embedded image; it was read directly from the rendered datasheet page 23 of Rev 1.2, and matches the 10.2 Hz → 160 Hz values Robinson quotes for SF12/125 [7]: 10.17 Hz and 162.8 Hz.) Note it is a limit on drift *per packet*, not per symbol. So the allowed rate is $\dot f_{max} = BW/(3\cdot2^{SF}\,T_{packet})$ (×16 with LDRO). The 16× relaxation (vs 4× from bin folding alone) implies the chip actively tracks frequency when LDRO is on. The same limit, expressed as crystal ppb and °C of allowable warming during a packet, is used in [crystals and resonators](../04-real-components-hf/crystals-and-resonators.md) (SF12/BW125 + LDRO: 163 Hz ≈ 0.18 ppm at 915 MHz ≈ 0.6 K of AT-cut warming); that page's former "medium confidence" caveat on the formula was lifted on the strength of this datasheet reading. The same drift expressed in FFT bins per packet for an SDR decoder (SF9/BW125 at 100 m/s²: ≈ 0.3 bin over a 0.5 s packet) is worked in [14 software demodulation Example 3](../14-sdr-dsp/software-demodulation.md#worked-examples).

Allowed radial acceleration for a 32-byte packet (8-symbol preamble, explicit header, CRC, CR4/5; `lora_doppler.py` §5b, Semtech rule):

| BW | Band | SF7 | SF8 | SF9 | SF10 | SF11 | SF12 |
|---|---|---|---|---|---|---|---|
| 125 kHz | 433 MHz | 319 g | 86 g | 23 g | 6.3 g | 23 g (LDRO) | 6.3 g (LDRO) |
| 125 kHz | 923 MHz | 150 g | 40 g | 11 g | 3.0 g | 11 g (LDRO) | 3.0 g (LDRO) |
| 250 kHz | 433 MHz | 1280 g | 344 g | 93 g | 25 g | 7.0 g | 25 g (LDRO) |
| 250 kHz | 923 MHz | 600 g | 161 g | 44 g | 12 g | 3.3 g | 12 g (LDRO) |
| 500 kHz | 433 MHz | 5110 g | 1380 g | 372 g | 102 g | 28 g | 7.0 g |
| 500 kHz | 923 MHz | 2400 g | 645 g | 175 g | 48 g | 13 g | 3.3 g |

The idealised no-tracking model (`lora_doppler.py` §5) gives ~2× *looser* limits without LDRO (½ bin instead of ⅓) and ~2× *tighter* with LDRO (4× instead of 16×), e.g. SF12/125 LDRO: 3.1 g (433) / 1.4 g (923). Treat the two as a bracket; the design conclusion is the same.

#### Doppler rate seen from the ground — the line-of-sight rotation term
The table above is a limit on the **range acceleration** $\ddot r$, which is what the receiver sees. It is not the acceleration the flight computer measures. With $\mathbf r = \mathbf p - \mathbf s$ (vehicle minus station), $R = |\mathbf r|$, $\hat{\mathbf r} = \mathbf r/R$, differentiate $R^2 = \mathbf r\cdot\mathbf r$ twice:
$$\dot R = \mathbf v\cdot\hat{\mathbf r},\qquad \ddot R = \mathbf a\cdot\hat{\mathbf r} + \frac{|\mathbf v|^2 - \dot R^2}{R} = \mathbf a\cdot\hat{\mathbf r} + \frac{v_\perp^2}{R},$$
where $v_\perp$ is the velocity component across the line of sight and $\mathbf a$ is the kinematic acceleration (thrust + drag + gravity, i.e. $d^2\mathbf p/dt^2$; an accelerometer reads $\mathbf a - \mathbf g$). The second term is never negative. It is the centripetal term of a rotating line of sight. For a straight pass at constant speed $v$ and miss distance $R_0$ it is the whole answer, $\ddot R_{max} = v^2/R_0$ at closest approach. This is why the Norby CubeSat lost high-SF packets near zenith [5]. It is also why the [satellite page](../09-propagation-link-budget/satellite-links-doppler-tracking.md) gets its peak Doppler rate at the top of the pass. (Derived symbolically and checked numerically to < 0.04 m/s² in `tools/verify/s17_doppler_rate_los.py`.)

On the 10 km reference flight of [20/lora-rocket-telemetry-link](../20-projects-recipes/lora-rocket-telemetry-link.md) (11.1 g peak kinematic acceleration, 692 m/s at burnout), both terms are large during the burn:

| Station | max $\ddot R$ | when | $\mathbf a\cdot\hat{\mathbf r}$ + $v_\perp^2/R$ at that instant | max of $v_\perp^2/R$ alone |
|---|---|---|---|---|
| 0.5 km cross-range | **15.3 g** | t = 2.95 s (R 0.67 km, 312 m/s) | 7.2 g + 8.1 g | 8.5 g |
| 2 km cross-range | **13.7 g** | t = 5.86 s (R 2.68 km, 595 m/s) | 6.2 g + 7.5 g | 7.9 g |
| 5 km cross-range | 11.1 g | burnout (R 5.58 km) | 4.0 g + 7.0 g | 7.0 g |

**Effect on the SF limit check** (32-byte frame as in the table above; largest Doppler change across any packet in the ascent; script §3). At 433 MHz the verdicts do not change: SF ≤ 9 at 125 kHz, SF ≤ 10 at 250 kHz and SF ≤ 11 at 500 kHz pass from every station, and SF10/125 and SF12/125 fail. At **868 MHz**, **SF9/125 fails from stations at 0.5 km and 2 km** (107 / 96 Hz against an 81 Hz limit). It would pass if only $\mathbf a\cdot\hat{\mathbf r}$ were counted (63 / 49 Hz). SF10/250 also fails from those stations. SF11/500 fails from the 0.5 km station. So, for the 868 MHz link, keep SF ≤ 8 at 125 kHz (or SF9 at ≥ 250 kHz) during boost if the station is within a few km of the pad. A station under the flight path sees the full along-track acceleration instead, which is what `proj_lora_link.py` §3 labels "AT".

**Timing drift.** The same crystal clocks the chips, so a clock error $\varepsilon$ is also a chip-rate error. Over one symbol the timing slips $\varepsilon\,2^{SF}$ chips; Semtech's SF10/11/12 limits (200/100/50 ppm) all equal **0.205 chip per symbol** (script) — our interpretation of why those limits halve per SF. Doppler compresses time by $v/c$ too, but Mach 5 is only 5.7 ppm, far inside the 50 ppm SF12 limit. The SX127x lets you pre-correct the chip rate: after measuring the frequency error (FEI), retune and write $0.95\times$ppm to `PpmCorrection` (0x27) [1] — Semtech's own acknowledgement that frequency and timing errors are coupled.

### Level 3 — collisions, capture, quasi-orthogonality, multipath
**Same-SF collision and capture.** Two same-SF, same-BW packets overlapping in time add in the de-chirped spectrum as two peaks. The receiver locks to whichever preamble it detects; Semtech specifies LoRa-on-LoRa co-channel rejection of −6 dB — the wanted signal must be ≥ 6 dB above the interferer for 1 % PER [1]. Croce et al. report a 0 dB SIR threshold for same-SF interference in their model [9]. Bor et al. measured on real hardware that a packet only ~1 dB stronger is captured **if it starts no more than 3 symbols after the weaker one** (8-symbol preamble; the receiver needs ~5 preamble symbols to lock), otherwise both are lost [8]. Design with 6 dB.
**Different SFs.** Semtech calls SFs orthogonal [1], but chirps with different slopes are only quasi-orthogonal: a strong other-SF signal leaks energy into many bins. Croce et al. find an average rejection SIR threshold of about **−16 dB** [9] (i.e. an other-SF signal more than ~16 dB stronger than yours causes errors). For a rocket team this matters in the **near-far** case: another team's pad transmitter 1 km from your ground station can be 30–40 dB stronger than your rocket at 30 km.
**CW and adjacent-channel interference (SX1262)** [2]: co-channel CW rejection 5 dB (SF7) to 19 dB (SF12) — i.e. a CW tone up to 19 dB *stronger* than the wanted signal is tolerated at SF12; adjacent-channel (±1.5 BW) rejection 60/72 dB; blocking 88/90/99 dB at ±1/2/10 MHz; IIP3 −5 dBm.
**Multipath.** An echo delayed by $\tau$ appears after de-chirping as a second peak displaced by $\tau\,BW$ bins (time and frequency are coupled in a chirp). If $\tau \ll 1/BW$ (path difference $\ll c/BW$: 2.4 km at 125 kHz, 600 m at 500 kHz), echo and direct wave share a bin and simply add with some phase → **flat fading** (e.g. the two-ray ground reflection near a rocket — [two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md)). Longer echoes (mountains, buildings at km scale) land in other bins and behave like a weaker same-SF interferer; long symbols ($T_s \gg$ delay spread) mean no classic ISI.

## Design equations & rules of thumb
| Rule | Value |
|---|---|
| Static offset window | ±25 % BW (all SX127x/SX126x/SX128x) |
| SF10/11/12 clock limit | ±200/±100/±50 ppm (≡ 0.2 chip slip per symbol) |
| Dynamic drift per packet | $< BW/(3\cdot2^{SF})$; ×16 with LDRO |
| Doppler | 1 ppm per 300 m/s; 0.43 kHz per ppm at 433 MHz, 0.92 kHz at 923 MHz |
| Doppler rate | 14.2 Hz/s per g at 433 MHz; 30.2 Hz/s per g at 923 MHz (28.4 at 868 MHz); per g of **range** acceleration $\ddot R = \mathbf a\cdot\hat{\mathbf r} + v_\perp^2/R$ |
| Crystal (per device) | ±10 ppm typ, ±30 ppm max [6]; TCXO ±0.5–2.5 ppm |
| Crystal g-sensitivity | ~2 ppb/g (low-g crystals) [6] |
| Same-SF capture | ≥ 6 dB and early/≤ 3 symbols late |
| Other-SF tolerance | ≈ −16 dB SIR (avg.) |
| Flat-fading condition | path difference ≪ c/BW |

## Worked examples
**1. Crystal budget for the E220-900T30D link at 923 MHz, BW 125 kHz.** Window: ±31.25 kHz. Mach 3 Doppler: 3.17 kHz. Left for clocks: 28.1 kHz → ±15.2 ppm per side worst case. Two ±20 ppm crystals do **not** fit (worst case 36.9 kHz + Doppler); a TCXO (or BW ≥ 250 kHz) does. At 433 MHz the same BW leaves ±33 ppm per side — crystals fine. At the recommended Singapore channel, 868.125 MHz (see Practical notes), the numbers barely change: Mach 3 Doppler 2.98 kHz, ±16.3 ppm per side, and two ±20 ppm crystals (34.7 kHz) still do not fit. (EBYTE does not state whether the E220-T30D uses a TCXO — see [modules](lora-modules-ebyte-rfm-heltec.md); measure the frequency error with an SDR or the SX127x/SX126x FEI.)

**2. Is SF12/125 usable during a 10 g boost at 433 MHz?** Doppler rate 142 Hz/s; a 32-byte SF12/125 packet lasts 1.81 s → the carrier moves 257 Hz = 8.4 bins (script §6). Semtech's allowance with LDRO is 163 Hz → **fails**; even at 923 MHz it fails worse (547 Hz). SF7/125 in the same boost: 10 Hz of drift in 72 ms, 0.01 bin → fine. A ground station near the pad sees up to ≈ 1.4× the vehicle's acceleration (13.7 g at 2 km on an 11.1 g flight, [line-of-sight term](#doppler-rate-seen-from-the-ground--the-line-of-sight-rotation-term)), so budget with $\ddot R$ rather than the accelerometer reading.

**3. Forcing LDRO as a drift fix.** At SF10/125 (433 MHz) the Semtech rule allows 6.3 g. With LDRO forced on (RadioLib-style `forceLDRO`, both ends), the allowance rises ×16 to ~100 g, while the ToA grows from 453 ms to 535 ms (8 instead of 10 information bits per payload symbol, so the payload grows from 43 to 53 symbols; `lora_toa.py`). Only possible with bare-chip firmware — EBYTE UART modules don't expose LDRO.

**4. Parachute-deployment and ignition transients.** A 20 g step jolts a 2 ppb/g crystal by 17 Hz (433) / 37 Hz (923): 0.6–1.2 bins at SF12/125, 0.02–0.04 bins at SF7/125. A packet straddling ignition or deployment at high SF can be lost even if the average Doppler rate is small.

## Practical notes
- **Prefer SF7–SF9 and BW 125–500 kHz for in-flight telemetry**; you rarely need the budget of higher SFs in LOS ([link budget](lora-sensitivity-and-link-budget.md)). If you want high SF for landed recovery, switch modes after landing (flight state machine already knows).
- **Use a TCXO** for BW < 125 kHz, for 868/915/923 MHz with ±20 ppm-class crystals, or for any high-SF operation with a hot PA. SX126x/LR11xx can power a TCXO from DIO3 (1.6–3.3 V, ≤4 mA, clipped sine ≤1.2 Vpp) [2]; recalibrate after enabling it [2]. LR2021 claims enough offset tolerance to avoid a TCXO [10].
- **Thermal**: keep the crystal away from the PA and the 2 W module's heat; transmit bursts heat the die and pull the crystal (the SX126x DS explicitly warns) [2]. Semtech AN1200.37, as summarised in [crystals and resonators](../04-real-components-hf/crystals-and-resonators.md), found an SX1262 at +22 dBm on a standard PCB exceeding the drift limit within a long packet; thermal isolation kept 400–500 ms packets within limit but not 1 s ones.
- **Measure it**: the receiver's FEI (SX127x `LoRaFeiValue`, SX126x frequency-error readback) logged per packet shows the Doppler and drift history of every flight for free. An SDR at the ground station records the true carrier ([ground station](ground-station-design.md)).
- **Two bands on one rocket**: the E22 at 433.125 MHz has its **2nd harmonic at 866.25 MHz**, inside the E220's range and inside Singapore's 866–869 MHz SRD band. Keep the E220 in **866–869 MHz**, Singapore's best licence-exempt band for it (500 mW e.r.p., no duty limit stated). Pair it with the band-edge-safe E22 CH 24 (434.125 MHz, harmonic 868.25 MHz) by putting the E220 on **CH 17 = 867.125 MHz**, 1.125 MHz from the harmonic. If the E22 must stay on CH 23 (433.125 MHz, only at BW ≤ 125 kHz), use **CH 18 = 868.125 MHz**. Never use CH 16 (866.125 MHz, 125 kHz from the CH 23 harmonic). Also filter the E22 output and separate the antennas ([rocket telemetry design](rocket-telemetry-radio-design.md), [20 telemetry link recipe](../20-projects-recipes/lora-rocket-telemetry-link.md), [canonical values §D](../00-math-foundations/canonical-values-and-conventions.md)). **Do not move the E220 to 917–925 MHz to dodge the harmonic.** There, LPWAN end devices are limited to **100 mW e.r.p. at ≤ 1 % duty** ([19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md)). The E220's lowest step is 21 dBm, so it would also need a ≥ 1 dB pad. The duty arithmetic: a 32-byte SF7/125 frame lasts 71.9 ms (40 bytes: 82.2 ms). At 1 % duty that is ≤ 0.14 Hz (0.12 Hz), about one frame every 7–8 s. 10 Hz telemetry would occupy 72–82 % of the time, 70–80× over the limit.
- **Channel sharing at launches**: agree frequencies with other teams; different SFs on one channel are *not* safe under near-far conditions.

## Common mistakes & misconceptions
- **"Doppler kills LoRa on fast rockets."** The *shift* is harmless (≤ 5.3 kHz at Mach 5, 923 MHz). The *rate* (acceleration) is what hurts, and only at high SF / narrow BW.
- **"LoRa is immune to frequency error."** Only to *static* error within ±25 % BW; drift within a packet is its weakness.
- **"SF12 is the robust mode."** Robust to noise, fragile to drift and Doppler rate.
- **"A TCXO is only for narrow bandwidths."** Also for 900 MHz-band links with cheap crystals at 125 kHz, and for long packets from hot PAs.
- **"Different SFs don't interfere."** Quasi-orthogonal: ~16 dB of power disparity breaks it.
- **"Multipath causes ISI in LoRa like in FSK."** Path differences below c/BW cause flat fading; ISI is negligible because symbols are ms long.

## How to simulate / verify
- `python3 tools/verify/lora_doppler.py` — Doppler, Doppler rate, clock budgets per BW, ppm-limit ↔ chip-slip equivalence, no-tracking and Semtech-rule acceleration limits, per-packet drift in bins, crystal g-sensitivity.
- `python3 tools/verify/s17_doppler_rate_los.py` — symbolic derivation of $\ddot R = \mathbf a\cdot\hat{\mathbf r} + v_\perp^2/R$, numeric check on the 10 km reference trajectory, max $\ddot R$ from stations 0.5/2/5 km from the pad, and the per-packet drift check at 433/868 MHz with and without the rotation term.
- `python3 tools/verify/lora_css_sim.py` — fractional-CFO loss (0.5 bin → −3.9 dB), CFO SER penalty, and a noise-free linear-drift simulation confirming the decision-boundary model (SF12/125 LDRO: no errors at 0.5× critical rate, 12 % of symbols wrong at 1×, 54 % at 2×).
- Bench test: feed a signal generator with linear FM ramp (or an SDR transmitter replaying recorded chirps with a frequency ramp) into the receiver and find the ramp rate at which PER rises; compare with the table. HIL-style Doppler injection matches the team's HIL philosophy.

## Open questions / gaps
- $Freq\_drift\_max = BW/(3\cdot2^{SF})$ is now confirmed from the rendered SX1261/2 datasheet page (Rev 1.2 p. 23); what remains unknown is how much in-packet tracking the chips do beyond this guidance (the 16× LDRO relaxation implies some).
- Doroshkin et al. (IEEE Access 7:75721, 2019) and Zadorozhny et al. (IEEE Access 10:100006, 2022, Norby flight test) contain measured Doppler-rate thresholds for SX127x but were not accessible in full; only secondary summaries were read [5].
- No flight data exist in this KB of LoRa PER vs acceleration on a real rocket; Space Bar's own logs (RSSI/SNR/FEI vs IMU acceleration) would answer this directly.
- Croce et al.'s full SIR matrix (per SF pair) not transcribed.

## Sources
1. Semtech, *SX1276/77/78/79 Datasheet* Rev 7 (2020) — FERR_L ±25 % BW and SF10–12 ppm limits; CCR_LL −6 dB, CCR CW 5–19.5 dB; FEI/AFC and PpmCorrection = 0.95 × ppm; LDRO purpose. (datasheet)
2. Semtech, *SX1261/2 Datasheet* Rev 1.2 (2019) — FERR ±25 % BW & ppm table; §4.1.2 drift rule $Freq\_drift\_max = BW\_L/(3\cdot2^{SF})$ over the packet (read from rendered p. 23) and 16× LDRO relaxation, heat warning; TCXO via DIO3; CCR/ACR/blocking/IIP3. (datasheet)
3. Semtech, *SX1280/81/82 Datasheet* Rev 3.0 (2019) — §6.2.7 static offset ±25 % BW (166/83/42/21 ppm at 1600/800/400/200 kHz) and dynamic drift rule (16× at SF11/12). (datasheet)
4. Characterizing the impact of Doppler effects on body-centric LoRa links with SDR, *Sensors* 2021 (PMC8231252) — ideal-receiver ½-bin criterion, acceleration thresholds, pilot-symbol idea. (peer-reviewed)
5. Doppler estimation & compensation in LoRa direct-to-satellite, arXiv:2506.20858 (2025) — summary of Doroshkin 2019 and Norby (SX1278, 436.703 MHz, 560 km): Doppler shift fails at low elevation, Doppler rate at zenith; LDRO ×4 bin spacing. (preprint)
6. Semtech, *AN1200.14 LoRa Modulation Crystal Oscillator Guidance*, Rev 2.1 (2018) — crystal tolerance ±10/±30 ppm, 2 ppb/g, ±25 % BW tolerance figure, TCXO list. (app note)
7. S. Robinson, "Frequency drift for LoRa devices, is it important?", StuartsProjects blog, 2020 — SX1276 vs SX1262+TCXO temperature drift; 10.2 → 160 Hz values. (blog — anecdotal)
8. M. Bor et al., "Do LoRa Low-Power Wide-Area Networks Scale?", ACM MSWiM 2016 — capture timing experiment. (peer-reviewed)
9. D. Croce et al., "Impact of LoRa Imperfect Orthogonality: Analysis of Link-Level Performance," *IEEE Commun. Lett.* 22(4), 2018 — as summarised in A. Maleki et al., arXiv:2310.10503 (co-SF 0 dB, inter-SF −16 dB). (peer-reviewed, via review)
10. Semtech, LR2021 product page (2026) — "increased frequency offset tolerance obviating TCXO". (vendor web)
11. This KB, [Crystals and resonators](../04-real-components-hf/crystals-and-resonators.md) (W1-A2) — crystal classes, g-sensitivity, LoRa frequency budgets, AN1200.37 thermal-drift findings. (internal)
