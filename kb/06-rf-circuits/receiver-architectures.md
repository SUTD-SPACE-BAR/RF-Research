---
title: Receiver architectures (superheterodyne, dual conversion, zero-IF, low-IF, digital IF, direct RF sampling)
domain: 06-rf-circuits
slug: receiver-architectures
tags: [receiver, superheterodyne, image, half-if, dual-conversion, zero-if, direct-conversion, dc-offset, iip2, flicker, low-if, digital-if, direct-sampling, frequency-planning, reciprocal-mixing, sx1262, ad9361, r820t, rtl-sdr, superregenerative, quench, crystal-set, foxhole-radio, xy-mk-5v, fs1000a, rxb6, cc1101, ook, fm-bug, lnb, ku-band, offset-dish, l-band, qo-100, power-budget, duty-cycling, lo-radiation, receiver-emissions]
prerequisites:
  - mixers.md
  - lna-design.md
  - vco-and-pll-synthesizers.md
  - ../07-noise-linearity/receiver-cascade-analysis.md
  - ../07-noise-linearity/dynamic-range-sfdr-blocking.md
related:
  - rf-filters-lc-saw-baw-cavity-microstrip.md
  - transmitter-architectures.md
  - ../14-sdr-dsp/iq-complex-baseband.md
  - ../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md
  - ../14-sdr-dsp/sdr-hardware-survey.md
  - ../15-lora-ism-radios/semtech-chip-family.md
  - ../05-analog-electronics/data-converters-adc-dac.md
  - modulator-and-detector-circuits.md
  - ../08-antennas/horn-reflector-aperture-antennas.md
  - ../15-lora-ism-radios/other-ism-radios-fsk-2g4.md
  - ../19-regulations-safety/regulatory-faq-misc.md
  - ../20-projects-recipes/beginner-project-ladder.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Receiver architectures

## Questions this page answers
- What is a superheterodyne receiver and how do I choose its IF?
- Why does a low IF make the image and the half-IF spur hard to filter?
- When is dual conversion worth it?
- What goes wrong in a zero-IF (direct-conversion) receiver — DC offset, flicker noise, LO leakage, IQ imbalance, second-order distortion?
- Why do LoRa chips (SX126x) and RTL-SDR tuners use a low IF?
- What does direct RF sampling require from the ADC and its clock?
- How do I check a frequency plan for spurs?
- What is reciprocal mixing and why does a strong nearby signal raise my noise floor?
- How does a superregenerative receiver (the XY-MK-5V 433 MHz module) work, and why is it so unselective?
- How far will a cheap FS1000A / XY-MK-5V OOK pair reach, and what do I gain with an RXB6 or CC1101?
- What should my first home-built radio be: crystal set, superregen, or a Tayloe SDR?
- What is inside a satellite-TV LNB, and can I use one (or the dish) with my SDR?
- Why does an offset dish look as if it points at the ground?
- How much power does a receiver need, and how do LoRa chips listen on microamps?
- Do receivers transmit? Can a transmitter tell whether anyone is listening?

## TL;DR
- **Superhet**: LNA → RF filter → mixer → fixed IF filter/amplifier → demodulator. Selectivity comes from the fixed IF filter; the RF pre-selector must reject the **image** ($f_{RF}\mp2f_{IF}$) and **half-IF** spur ($f_{RF}\mp f_{IF}/2$). With a 5 %-wide 3-pole pre-selector at 433.92 MHz, the image is attenuated only 12.6 dB with a 10.7 MHz IF, 32.5 dB at 21.4 MHz, 54 dB at 45 MHz, 68 dB at 70 MHz; the half-IF spur 0.1/0.1/14/27 dB (computed). High first IF for image rejection, low second IF for selectivity → **dual conversion**.
- **Zero-IF** (direct conversion, e.g. AD9361, 70 MHz–6 GHz, 200 kHz–56 MHz bandwidth [5]): no image filter, easy integration, flexible bandwidth. Problems: **DC offset** from LO self-mixing (−60 dBm of LO leakage ≈ 50 dB above a −110 dBm signal), **second-order IM** of AM blockers at DC (a −30 dBm blocker needs IIP2 ≥ +57 dBm for a 125 kHz channel with 6 dB NF), **flicker noise** (+10.5 dB in a 125 kHz channel with a 100 kHz 1/f corner), **IQ imbalance** (mirror images, [mixers](mixers.md#level-2--derivations)), LO radiation.
- **Low-IF** (IF ≈ one to a few channel bandwidths): keeps the signal away from DC (flicker penalty +1.5 dB instead of +10.5 dB at a 100 kHz corner) and DC offsets, but the image is an adjacent channel — rejected by complex (polyphase) filtering or digital IQ processing (IRR 30–40 dB analogue, more with calibration). Used by the SX1261/2 ("mostly low-IF" [3]) and the R820T tuner (3.57 MHz IF, sampled by the RTL2832U's ADC at 28.8 MS/s [4]).
- **Digital IF / direct RF sampling**: an ADC samples the IF or the RF directly (bandpass/undersampling). SNR is capped by clock jitter: $-20\log(2\pi f\sigma_t)$ → 100 fs gives 71 dB at 434 MHz, 60 dB at 1575 MHz, 56 dB at 2.45 GHz. Plan Nyquist zones (at 3 GS/s, 1575 MHz appears inverted at 1424.6 MHz).
- **Reciprocal mixing**: a blocker $P_b$ at offset Δf deposits $P_b+L(\Delta f)+10\log B$ into the channel: −30 dBm at 1 MHz with −152 dBc/Hz LO noise → −131 dBm in 125 kHz (below the −117 dBm floor); −40 dBm at 100 kHz with −123 dBc/Hz → −112 dBm (5 dB *above* the floor: desensitisation).
- A worked 433 MHz superhet (SAW–LNA–SAW–DBM–IF amp–IF filter) gives NF 3.8 dB and IIP3 −1.9 dBm; removing the front SAW improves NF to 1.4 dB but loses blocker protection — the eternal trade.
- **Superregenerative receivers** (one transistor oscillator, quenched): the selectivity is set by the *quench*, not the tank. With a linear quench ramp the sensitivity window is Gaussian and the RF bandwidth is $B=\sqrt{2\ln2\,\ln K}/(\pi T_g)$ ($K$ regenerative gain, $T_g$ growth time) — **≈ 1.45 MHz at a 500 kHz quench** (a signal 1 MHz off-tune loses only 5.7 dB), 145 kHz at 50 kHz (verified by ODE). Floor ≈ −104 dBm (NF 8 dB), so the seller's "−105 dBm" for an XY-MK-5V is optimistic. Near the ground (two-ray, 40 log d) a 10 dBm FS1000A reaches **≈ 270 m** to a superregen and ≈ 530 m to a CC1101 at 1.2 kBaud: 12 dB of sensitivity is only 2× range near the ground (4× in free space). A bare quenched oscillator on an antenna radiates tens of dB over receiver-emission limits. See [first-radio receivers](#first-radio-receivers-crystal-sets-superregeneration-and-cheap-ook-modules).
- **Ku-band LNB** = feedhorn + HEMT LNA + mixer + LO (9.75/10.6 GHz) → 950–2150 MHz IF. A PLL LNB multiplies a 25 MHz crystal by 390 (30 ppm → ±293 kHz); DRO LNBs drift ±1–2.5 MHz. The IF can feed an SDR directly (but ≈ −36 dBm of broadband noise arrives with it). A 0.8 m TV dish re-fed at 1.69 GHz has ≈ 20 dBi and a 15° beam. See [LNBs and dishes](#satellite-tv-lnbs-offset-dishes-and-l-band-re-feeds).
- **Power and emissions**: SX1262 RX 15 mW vs an RTL-SDR 1.4 W (≈ 90×); duty-cycled RX (3 ms every 100 ms) averages 139 µA but needs a 101-symbol preamble. Receivers radiate their LO: FCC §15.111 allows 2 nW (−57 dBm) at the antenna port, which a +7 dBm-LO superhet with 50 dB of isolation exceeds by 12 dB. A transmitter cannot sense receivers: a matched dipole's echo at 1 km is ≈ −132 dBm, 162 dB below the 1 W carrier. See [power budget and LO radiation](#receiver-power-budget-duty-cycling-and-lo-radiation).

## Intuition (no math)
Every receiver has to do three things: amplify a tiny signal, pick it out from much larger neighbours, and translate it to a frequency where it can be digitised or demodulated. Making a sharp, tunable filter at 433 MHz is hard; making a sharp fixed filter at 10.7 MHz (ceramic) or in software at baseband is easy. The superheterodyne therefore moves whatever you tune to onto a fixed intermediate frequency, where one excellent filter does the selecting. The catch is the image: the mixer also moves a second frequency (on the other side of the LO) onto the same IF, and only an RF filter can stop it. A higher IF puts the image further away and makes that RF filter easier — but makes the IF filter harder. Two conversions give both.

Direct conversion puts the LO right on the signal, so the IF is zero: the image is the signal's own mirror, separated using I and Q. Everything becomes a low-pass filter — perfect for integration and software-defined bandwidth — but anything that produces a DC or low-frequency output (LO leaking and mixing with itself, the envelope of a strong AM interferer through second-order distortion, transistor flicker noise) lands exactly on top of the wanted signal.

Low-IF is the compromise: shift the wanted signal a little off zero (a few hundred kHz) so that DC junk and flicker noise can be filtered, and accept that the image is now a nearby channel, removed with complex (IQ) filtering. Most modern narrowband transceivers (LoRa, FSK, Bluetooth) and TV tuners do this.

Finally, fast ADCs can sample the RF itself. Then the "mixer" is the sampling clock, and the clock's jitter becomes phase noise on every signal — the higher the frequency, the worse.

## The math

### Level 1 — frequency relations
- Superhet with LO $f_{LO}$: wanted $f_{RF}=f_{LO}\pm f_{IF}$; image $f_{im}=2f_{LO}-f_{RF}$ (distance $2f_{IF}$); half-IF $f_{RF}\mp f_{IF}/2$; general spurs $|mf\pm nf_{LO}|=f_{IF}$ ([mixers](mixers.md)).
- Direct conversion: $f_{LO}=f_{RF}$, I and Q outputs at baseband; low-IF: $f_{LO}=f_{RF}\mp f_{IF}$ with $f_{IF}$ ≈ 0.5–2 channel bandwidths.
- Direct sampling: signal in Nyquist zone $z=\lfloor f/(f_s/2)\rfloor+1$ appears at $f\bmod f_s$ (folded into 0…$f_s/2$), inverted in even zones.

### Level 2 — the numbers that set each architecture

**(a) Image rejection by the pre-selector.** With a Chebyshev band-pass of fractional bandwidth FBW and order N, the attenuation at $f$ is $10\log[1+\varepsilon^2T_N^2(\Omega)]$ with $\Omega=\frac1{\text{FBW}}(\frac{f}{f_0}-\frac{f_0}{f})$ (see [filter prototypes](../01-circuit-theory/passive-filter-design-prototypes.md)); the image at $2f_{IF}$ away has $\Omega\approx4f_{IF}/(\text{FBW}f_0)$, so rejection grows ≈ 20N dB/decade of IF. Table from the script (N = 3, 0.1 dB, FBW 5 %):

| IF | Image | Rejection | Half-IF | Rejection |
|---|---|---|---|---|
| 10.7 MHz | 412.52 MHz | 12.6 dB | 428.57 MHz | 0.1 dB |
| 21.4 MHz | 391.12 MHz | 32.5 dB | 423.22 MHz | 0.1 dB |
| 45 MHz | 343.92 MHz | 54.0 dB | 411.42 MHz | 14.0 dB |
| 70 MHz | 293.92 MHz | 67.9 dB | 398.92 MHz | 26.8 dB |

(A 433 MHz SAW does far better — it is only 1.6 MHz wide — which is why a single-conversion 10.7 MHz design with a SAW front end works.)

**(b) Second-order distortion in zero-IF.** A blocker $P_b$ with amplitude modulation produces, through the $a_2v^2$ term, a baseband component at its envelope frequencies with power $P_{IM2}=2P_b-\text{IIP2}$ (dBm). Requiring $P_{IM2}$ below the in-channel noise $P_n=-174+10\log B+NF$ gives $\text{IIP2}\ge2P_b-P_n$: for −30 dBm and $P_n$ = −117 dBm, **+57 dBm** — only achievable with balanced, calibrated mixers [1 ch. 4].

**(c) Flicker noise.** With baseband noise density $N_0(1+f_c/f)$, the average excess over a band $[f_1,f_2]$ is $1+\frac{f_c}{f_2-f_1}\ln\frac{f_2}{f_1}$. For a 125 kHz channel at zero IF (100 Hz–62.5 kHz, i.e. a DC notch) and $f_c$ = 100 kHz: +10.5 dB; at a 250 kHz low IF: +1.5 dB (script C). This is the quantitative reason narrowband CMOS receivers avoid zero IF.

**(d) Self-mixing DC offset.** LO leakage at the LNA input ($P_{leak}$) or a strong in-band signal leaking into the LO port mixes with the LO to DC; input-referred it looks like a signal of ≈ $P_{leak}$ at zero frequency — 30–50 dB above weak signals, and time-varying as the antenna environment changes. Cures: AC coupling (costs the spectrum near DC), DC servo loops, digital DC estimation/cancellation, and choosing modulations with no energy at DC.

**(e) Jitter-limited sampling.** A sinusoid $A\sin2\pi ft$ sampled with timing error $\delta t$ gives error $2\pi fA\,\delta t\cos(\cdot)$; its power relative to the signal is $(2\pi f\sigma_t)^2$, so $\text{SNR}_{jitter}=-20\log(2\pi f\sigma_t)$ [6]. Combined with quantisation ($6.02b+1.76$ dB) and thermal noise it sets the usable dynamic range of direct RF sampling ([data converters](../05-analog-electronics/data-converters-adc-dac.md)).

**(f) Reciprocal mixing.** The LO's phase-noise sidebands $L(\Delta f)$ (dBc/Hz) act as a comb of weak LOs; a blocker at offset Δf mixes with them into the channel, adding $P_b+L(\Delta f)+10\log B$. It is often the limit on blocking performance of narrowband receivers (see [PLL page](vco-and-pll-synthesizers.md#example-3--choosing-the-loop-bandwidth)).

### Level 3 — architecture comparison and modern practice

| Architecture | Image handling | Main impairments | Where used |
|---|---|---|---|
| Single-conversion superhet | RF filter | image, half-IF, IF filter cost | classic FM/AM, ham radios, many ISM receivers with SAW + ceramic IF |
| Dual conversion | 1st high IF (image), 2nd low IF (selectivity) | more spurs, two LOs | communications receivers, scanners, test equipment |
| Up-conversion (IF above RF) | image far above band | high-IF filter (crystal/SAW at 45–70 MHz) | HF receivers (IF above 30 MHz) |
| Zero-IF | IQ (mirror) | DC offset, 1/f, IIP2, IQ imbalance, LO leakage | AD9361, cellular, most SDR transceivers |
| Low-IF | polyphase / digital IQ | image = adjacent channel, IRR limited | SX126x [3], R820T [4], Bluetooth, FSK chips |
| Digital IF | ADC at IF (band-pass sampling) | ADC SFDR, jitter, aliasing | software radios, radar receivers |
| Direct RF sampling | anti-alias filter, Nyquist planning | jitter, ADC NF (often 20–30 dB), interleaving spurs | RF-sampling ADCs (GS/s), phased-array digital receivers |

- **Weaver / Hartley image-reject** front ends and **harmonic-reject mixers** are used where filters are impractical ([mixers](mixers.md)).
- **SAW-less** receivers use high-linearity passive mixers and N-path filters to replace external SAWs [1].
- **Calibration**: modern zero/low-IF chips estimate and correct DC offset, IQ gain/phase imbalance, and LO leakage continuously.

### First-radio receivers: crystal sets, superregeneration and cheap OOK modules

**Crystal (and foxhole) sets.** These are an antenna, a tuned LC circuit, a diode and high-impedance earphones. There is no gain and no power supply. The wartime "foxhole radio" used a razor blade with a pencil-lead point contact as the diode. The detector is the weak point. An unbiased diode into a very high load resistance settles at $V_{dc}=nV_T\ln I_0(V/nV_T)$ ($I_0$ = modified Bessel function). That is ≈ $V^2/4nV_T$ for small $V$ (square law) and approaches the peak for large $V$. A strong station (10 mV/m on a wire with 20 m effective height, 200 mV peak) gives 148 mV DC, 74 % of peak. A weak one (0.5 mV/m × 10 m = 5 mV) gives only 0.23 mV, 5 % of peak (script H). Hence the long wire, the low-threshold germanium or Schottky diode and the 2 kΩ+ phones. It is the [envelope detector](modulator-and-detector-circuits.md) with no help. It works only for AM broadcast where strong MW stations exist.

**Superregeneration (Armstrong, 1922 [7]).** A single transistor oscillator is tuned to the signal and switched repeatedly on and off by a *quench* waveform (separate, or self-quenched by the bias network). Each time the net damping of the tank passes through zero, the oscillation grows exponentially from whatever was in the tank. If a signal was present it started from the signal, otherwise from noise. The growth turns a −100 dBm signal into a volt-level oscillation in a microsecond (regenerative gain $K\approx e^{15}$ to $e^{30}$). The detected average of the bursts is the output.

- *Envelope model* (Level 2). Write the tank voltage as $\mathrm{Re}\{a(t)e^{j\omega_0t}\}$; with net damping $\alpha(t)=\zeta(t)\omega_0$ and an input $b\,e^{j\Delta\omega t}$, $\dot a=-\alpha(t)a+b\,e^{j\Delta\omega t}$. For a linear quench ramp $\alpha=k(t_0-t)$ crossing zero at $t_0$, the solution at the end of growth is $a(t_e)=K\int b\,e^{j\Delta\omega\tau}s(\tau)\,d\tau$ with a **sensitivity curve** $s(\tau)=e^{-k(\tau-t_0)^2/2}$ (Gaussian, $\sigma_t=1/\sqrt k$). The receiver only "listens" during a short window around the zero crossing of the damping [8].
- *Selectivity is the Fourier transform of the window.* $|a|\propto e^{-\Delta\omega^2/2k}$, so the −3 dB RF bandwidth is $B=\sqrt{\ln2\,k}/\pi$. With growth time $T_g$ and gain $K=e^{kT_g^2/2}$: $B=\sqrt{2\ln2\ln K}/(\pi T_g)$. The tank Q hardly appears. For $\ln K$ = 15 and $T_g$ = half the quench period, B = 145 kHz, 290 kHz, 726 kHz, 1.45 MHz and 2.9 MHz at 50 k, 100 k, 250 k, 500 k and 1 MHz quench (effective Q 3000 down to 150 at 433.92 MHz). At 500 kHz, a signal 1 MHz off-tune is rejected by only 5.7 dB and one 2 MHz off by 22.9 dB (ODE vs closed form within 0.1 %, script A–B). The noise bandwidth is $1.064B$, so at a 500 kHz quench and NF 8 dB the floor is ≈ −104 dBm (script C).
- *Quench rate vs data rate.* The SRO samples the input once per quench cycle, so the quench must be ≫ the bit rate (≥ 10× in practice). A faster quench widens the bandwidth. That is the superregen's built-in trade: data rate against selectivity.
- *Linear vs logarithmic mode.* If quenching stops the growth before it saturates (linear mode), the output is proportional to the input amplitude. Most practical SROs saturate (logarithmic mode). The oscillation then reaches its limit earlier for stronger inputs, and the detected average rises by roughly equal steps per dB: in the model, equal output steps (within 1.45:1) per 10 dB over a 100 dB range (script D). That compression is a free AGC and the reason superregens tolerate strong OOK signals, but it destroys AM linearity [8][9].
- *Re-radiation.* The SRO *is* an oscillator at the receive frequency, and its burst spectrum is a comb spaced by the quench frequency across ≈ B. With the tank coupled to an antenna, an order-of-magnitude estimate (20 nH, $Q_L$ 30, 1 V peak, half the power to the antenna, 30 % on-time) is ≈ −13 dBm radiated. That is ≈ 36 dB over the FCC §15.109 Class B limit of 200 µV/m at 3 m (−49.2 dBm EIRP) and far above the 2 nW (−57 dBm) antenna-port limit of §15.111 [10] (script E). This is why WWII superregens were notorious interferers and why usable designs put a buffer RF amplifier between antenna and SRO. On an RTL-SDR waterfall, an XY-MK-5V shows a broad hump around 433.9 MHz while it is powered (a good first measurement).

**Cheap 433 MHz OOK modules.** The **FS1000A** transmitter is a SAW-stabilised one-transistor oscillator keyed on and off by the data pin. Sellers state 10 mW and "about 200 m" [11]. The **XY-MK-5V** receiver is a superregenerative module with an op-amp data slicer; sellers state −105 dBm [11], which is about 1 dB below the thermal floor estimated above, so treat it as optimistic. Superhet replacements (**RXB6**, SYN470R/480R-class single-chip OOK receivers, sellers ≈ −107 dBm [11]) or a real transceiver (**CC1101**: −112 dBm at 1.2 kBaud, −116 dBm at 0.6 kBaud at 433 MHz [12]) add selectivity, lower noise bandwidth and far less re-radiation. Example 7 turns this into range. In Singapore, 433.05–434.79 MHz allows 10 mW e.r.p. at ≤ 10 % duty (or 1 mW e.r.p. continuous) ([canonical values](../00-math-foundations/canonical-values-and-conventions.md)). An FS1000A at 10 dBm on a −5 dBi wire is ≈ 2.9 dBm e.r.p., legal at ≤ 10 % duty, but a continuously keyed beacon is not.

**The one-transistor FM "bug".** A Colpitts oscillator at 88–108 MHz, frequency-modulated by the transistor's bias-dependent capacitance. It needs no receiver theory, but it teaches pulling: 0.1 pF of hand capacitance on a 20 pF tank moves 100 MHz by 250 kHz, more than one 200 kHz FM channel (script G). Legality: the US §15.239 limit (250 µV/m at 3 m ≈ −47.3 dBm EIRP) is ≈ 57 dB below a 10 mW kit on a whip, and Singapore has no licence-exempt broadcast-band provision. See [regulatory FAQ](../19-regulations-safety/regulatory-faq-misc.md). Build it into a dummy load or a shielded box, or skip it.

**Which first radio?** A crystal set teaches resonance and detection. A superregen (kit or module) teaches regeneration, quench, sampling and why selectivity matters, with cheap modules to measure. A **Tayloe/QSD direct-conversion SDR** (4-path sampling mixer + sound card, [mixers: N-path](mixers.md#level-3--lptv-analysis-conversion-matrices-noise-folding-and-n-path-tayloe-mixers)) is the best receiver of the three: < 1 dB conversion loss, image rejection in software and a narrow, clean channel. It is the natural bridge to the [SDR receiver build](../20-projects-recipes/sdr-receiver-build.md). The [beginner ladder](../20-projects-recipes/beginner-project-ladder.md) lists it as rung 0.

### Satellite-TV LNBs, offset dishes and L-band re-feeds

**Inside a universal Ku LNB.** The parts, in signal order:
- a scalar or corrugated feedhorn into circular waveguide;
- two orthogonal probes (vertical/horizontal), selected by the 13 V/18 V supply on the coax;
- two or three GaAs/pHEMT LNA stages and an image-reject band-pass;
- a mixer with a 9.75 GHz LO (10.7–11.7 GHz → 950–1950 MHz), or a 10.6 GHz LO when the receiver adds a 22 kHz tone (11.7–12.75 GHz → 1100–2150 MHz);
- an IF amplifier into 75 Ω F-connector coax.

Typical claims are 0.1–0.8 dB NF and 50–65 dB gain [13]. The "0.1 dB" figures are marketing, so expect 0.5–1 dB. The LO is either a **DRO** (dielectric resonator: Labgear's VK8L is ±1.3 MHz at 25 °C and ±2.5 MHz over −40…70 °C [13]) or a **PLL** locked to a 25 or 27 MHz crystal. The PLL multiplies the crystal error by 9.75 GHz / 25 MHz = 390: a 30 ppm crystal gives ±293 kHz, matching the ±300 kHz quoted for budget PLL LNBs, and a 2 ppm TCXO gives ±19.5 kHz (script A) [13].

**An LNB as an SDR down-converter.** The steps:
- Power it through a bias-tee from a 12–18 V supply and DC-block the SDR. An RTL-SDR's 4.5 V bias-tee is not enough.
- Select the band with 13/18 V and the 22 kHz tone. The 75-on-50 Ω mismatch costs 0.18 dB.
- Tune the 950–2150 MHz IF, or lower for out-of-band signals such as 10489.55 MHz → 739.55 MHz with the 9.75 GHz LO.

The LNB's 55 dB of gain makes the cable and SDR noise irrelevant (cascade NF 0.800 dB vs 0.800 dB) but delivers ≈ −36 dBm of broadband noise over the 1.2 GHz IF into an 8-bit tuner. Use 10–20 dB of pad or low tuner gain ([gain staging](../14-sdr-dsp/sdr-gain-staging-and-reception-recipes.md)). LO drift is the main nuisance for narrowband work. A DRO's ±2.5 MHz is ≈ 1850 SSB channel widths, so narrowband users replace the crystal with a GPS-disciplined or TCXO reference. From Singapore, the amateur geostationary transponder QO-100 (25.9° E) is only ≈ 3° above the horizon (script C), so it is not a practical target there.

**Offset-dish geometry.** A TV dish is an off-axis cut of a parent paraboloid ($y=x^2/4f$) whose focus is the LNB. Taking $f$ = 0.5 m and an aperture from $x$ = 0.05 to 0.85 m: the rim plane is tilted **24.2°** from the beam direction (the *offset angle*). The feed must point 43.2° off the paraboloid axis and sees a half-angle of 37.5°, equivalent to a symmetric dish with f/D ≈ 0.74 (script C). Consequence: the dish face points ≈ 24° *below* the satellite. From Singapore a GEO at 105.5° E is at 87.4° elevation, yet the dish face is tilted only 63° up. At 41° elevation (146° E) the face is nearly vertical (17°). Offset dishes avoid feed blockage ([reflector antennas](../08-antennas/horn-reflector-aperture-antennas.md)).

**Re-feeding a TV dish for L-band (≈ 1.7 GHz weather satellites).** The surface is far better than needed (λ/16 at 1.69 GHz is 11 mm). The limit is the feed, which must be a 1.7 GHz patch, helix or dipole-and-reflector sized to illuminate the 37° half-angle with ≈ −10 dB edge taper. Mount it at the LNB focus with the phase centre on the focus. At 1694.1 MHz a 0.8 m dish is only 4.5 λ across: G ≈ 20.0 dBi at η = 0.5, HPBW ≈ 15.5°. With 60 K antenna and a 0.5 dB NF LNA, T_sys ≈ 95 K and G/T ≈ 0.2 dB/K (script D). NOAA quotes a 1.0 m minimum dish for GOES HRIT/EMWIN (1694.1 MHz, 927 ksps BPSK, 400 kb/s) at ≥ 10° elevation [14]. A 0.8 m dish is therefore 1.9 dB short of that minimum, before pointing and feed losses. The GOES satellites are not visible from Singapore; there the L-band targets are polar orbiters (e.g. Metop AHRPT near 1701 MHz, frequency to confirm per satellite), where the 15° beam makes hand or simple tracking feasible.

### Receiver power budget, duty cycling and LO radiation

**Where receiver power goes.** These components draw power:
- the LNA (mA);
- the LO/PLL (often the largest analogue block: a fractional-N PLL+VCO is tens of mA, e.g. LMX2572 ≈ 75 mA [15]);
- mixers and IF amplifiers;
- the ADC: power rises with bandwidth and dynamic range, roughly $P\approx B\cdot10^{(\mathrm{SNDR}-\mathrm{FOM_S})/10}$ with Schreier FOM_S ≈ 160–185 dB [16];
- the DSP, which scales with sample rate.

That is why a narrowband integrated receiver and an SDR differ by two orders of magnitude. The SX1262 draws 4.6 mA (DC-DC) or 8.8 mA (LDO) in RX, i.e. 15.2 or 29.0 mW at 3.3 V ([Semtech chips](../15-lora-ism-radios/semtech-chip-family.md)). An RTL-SDR Blog V3 draws 270–280 mA at 5 V, 1.38 W, before the host computer [17] (script E).

**Duty cycling.** A sleeping receiver hears nothing, so low-power listening wakes for a short window often enough to catch the preamble. The average current is $\bar I=(I_{rx}t_{rx}+I_{sl}t_{sl})/(t_{rx}+t_{sl})$. With SX126x RX duty-cycle mode, 3 ms on and 97 ms off at 4.6 mA / 0.6 µA averages **139 µA**, 33× lower. A 2000 mAh cell then lasts ≈ 600 days instead of 18, for the chip alone. The transmitter pays: its preamble must span a full sleep period plus two windows, ≥ 101 symbols at SF7/125 (103 ms of extra air time per packet, which counts against duty-cycle limits). The SX126x sleep current (≈ 0.16–0.6 µA chip, 1–3 µA on modules) is from the data sheet family; verify for your board.

**LO radiation: receivers do transmit.** Every superhet's LO (and its harmonics) leaks back through the mixer and LNA to the antenna. Limits are FCC §15.111, 2 nW = −57 dBm at the antenna terminal, and §15.109 radiated limits of 200 µV/m at 3 m in 216–960 MHz (−49.2 dBm EIRP) [10]. European SRD receivers meet similar receiver-spurious limits in EN 300 220-1 clause 8.6 (values not re-read here). Budget: +7 dBm LO, DBM LO–RF isolation 30 dB, LNA reverse isolation 20 dB and a 2 dB SAW give −45 dBm, 12 dB over. A 35 dB-isolation LNA and +4 dBm LO give −63 dBm. A zero-IF chip with −60 dBm LO leakage at the LNA input and 20 dB reverse isolation gives −80 dBm (script F). Superregens are the worst case (see above). In the UK, licence detector vans were said to find TV sets by the radiation of their LO, an IF above the tuned channel. The method was never fully published, so treat this as anecdote.

**A transmitter cannot sense receivers.** A passive receiver's only signature at the transmitter is the tiny echo from its antenna. A conjugate-matched antenna scatters about as much as it absorbs, so its radar cross-section is $\sigma\approx G^2\lambda^2/4\pi$ = 0.10 m² for a 433.92 MHz dipole (shorted: ≈ 0.86 λ² = 0.41 m²). With 1 W into a dipole, the echo at 1 km is −131.8 dBm (−125.8 dBm shorted). That is co-channel with the 30 dBm carrier, i.e. 162 dB of self-interference cancellation is needed. Switching the receiver on or off changes it by ≤ 6 dB amid buildings with σ ≫ 1 m² (script G). Only LO leakage (above) can betray a receiver, and a crystal set or direct-sampling SDR has no LO at a predictable offset.

## Design equations & rules of thumb

| Quantity | Equation | Example |
|---|---|---|
| Image | $2f_{LO}-f_{RF}$ | 433.92 − 21.4 MHz for 10.7 MHz IF low-side |
| Half-IF | $f_{RF}\mp f_{IF}/2$ | 428.57 MHz |
| Required IIP2 (zero-IF) | $2P_b-P_n$ | +57 dBm |
| Flicker excess | $1+\frac{f_c}{f_2-f_1}\ln\frac{f_2}{f_1}$ | zero-IF +10.5 dB vs low-IF +1.5 dB |
| Jitter SNR | $-20\log(2\pi f\sigma_t)$ | 100 fs @ 1575 MHz: 60 dB |
| Reciprocal mixing | $P_b+L(\Delta f)+10\log B$ | −30 − 152 + 51 = −131 dBm |
| Cascade | Friis + $1/IIP3_{tot}=\sum G_{before}/IIP3_i$ | 433 superhet: 3.8 dB, −1.9 dBm |
| IF choice | image ≥ 2·IF away; IF ≥ 2× pre-selector half-bandwidth | |
| Superregen bandwidth | $B=\sqrt{2\ln2\ln K}/(\pi T_g)$ (linear quench ramp) | 500 kHz quench, $\ln K$ = 15: 1.45 MHz |
| Superregen noise bandwidth | $1.064B$ | floor −104 dBm (NF 8 dB, 500 kHz quench) |
| Range vs sensitivity | ×$10^{\Delta/40}$ near the ground (two-ray), ×$10^{\Delta/20}$ in free space | 12 dB → 2× vs 4× |
| LNB IF | $f_{RF}-f_{LO}$, LO 9.75/10.6 GHz | 950–2150 MHz |
| PLL-LNB LO error | 390 × crystal ppm (25 MHz ref) | 30 ppm → ±293 kHz |
| Offset-dish face tilt | elevation − offset angle (≈ 20–28°) | 87.4° GEO → face at 63° |
| Duty-cycled RX current | $(I_{rx}t_{rx}+I_{sl}t_{sl})/T$; preamble ≥ $T+t_{rx}$ | 3/97 ms: 139 µA, 101 symbols at SF7 |
| Receiver LO at the antenna | $P_{LO}-\text{iso}_{mixer}-\text{iso}_{LNA}-L_{filter}$ ≤ −57 dBm | +7 − 30 − 20 − 2 = −45 dBm (over) |
| Matched-antenna RCS | $G^2\lambda^2/4\pi$ | 0.10 m² at 433.92 MHz |

## Worked examples

### Example 1 — Choosing the IF for a 433 MHz telemetry ground receiver
With only an LC pre-selector (5 % bandwidth), a 10.7 MHz IF leaves the image rejected by 12.6 dB and the half-IF spur unfiltered — unacceptable near other 433 MHz users. Options: (i) keep 10.7 MHz but use a SAW pre-selector (≈ 1.6 MHz wide); (ii) first IF 45 or 70 MHz (image rejection 54/68 dB) and a second conversion to 10.7 MHz or 455 kHz for selectivity; (iii) use a LoRa chip (low-IF with on-chip image rejection) and add a SAW for out-of-band blockers.

### Example 2 — The SX126x (low-IF) and why an external SAW still helps
The SX1261/2 receiver amplifies with a differential LNA and down-converts to a low IF ("mostly low-IF, except for specific high-bandwidth settings" [3]); image rejection and channel filtering are done on-chip. Its effective NF (≈ 6 dB, derived in [LNA design](lna-design.md#example-5--lora-ground-station-is-an-lna-worth-it-and-where)) and blocking performance are set by the on-chip LNA/mixer; strong out-of-band signals (cellular, the rocket's own 900 MHz radio) are best removed by a SAW before it.

### Example 3 — RTL-SDR (R820T + RTL2832U)
The R820T tuner converts 24–1766 MHz to a 3.57 MHz low IF; the RTL2832U samples it with an 8-bit ADC at 28.8 MS/s, digitally mixes to baseband (I/Q), filters and decimates to ≤ 2.4–3.2 MS/s for USB [4]. The low IF avoids zero-IF DC offset and IQ-imbalance mirrors; the 8-bit ADC (≈ 45–50 dB SFDR) limits dynamic range — hence overload near strong signals.

### Example 4 — AD9361 (zero-IF, 2×2)
70 MHz–6 GHz tuning, 200 kHz–56 MHz channel bandwidth, 12-bit ADCs, on-chip DC-offset, quadrature and LO-leakage calibration [5]. Excellent for wideband/agile work (PlutoSDR is built on the AD9363 variant), but for a weak narrowband LoRa-like signal its zero-IF DC notch and flicker noise matter — offset-tune (place the signal a few hundred kHz from the LO) and filter digitally: "low-IF in software".

### Example 5 — Direct RF sampling of GNSS L1
A 3 GS/s ADC puts 1575.42 MHz in the 2nd Nyquist zone at 1424.58 MHz (inverted). With 100 fs clock jitter, SNR ≤ 60 dB — fine for GNSS (signals are below the noise anyway; the need is linearity against blockers), but the ADC's NF (typically 20–30 dB) means an LNA with ≥ 30 dB gain is still required in front.

### Example 6 — Reciprocal mixing check for a ground station near a pager/cell transmitter
Blocker −40 dBm at 100 kHz from a 433.92 MHz channel, LO phase noise −123 dBc/Hz at 100 kHz (the 50 kHz-loop ADF4351 example): −112 dBm in 125 kHz — 5 dB above the thermal floor (−117 dBm with 6 dB NF) → ≈ 6 dB desensitisation. Remedies: lower LO noise at 100 kHz (narrower/wider loop depending on which contributor dominates, better VCO), or better filtering of the blocker before the mixer.

### Example 7 — FS1000A to XY-MK-5V vs CC1101: how far?
Assumptions: 10 dBm transmitter, 17.3 cm wire antennas at −5 dBi each end, 10 dB fade/interference margin, both ends 1.5 m above flat ground. The allowed path loss is $10-5-5-S-10$ dB. Beyond $d_c=4\pi h_1h_2/\lambda$ = 41 m the two-ray loss is $40\log d-20\log(h_1h_2)$, so $d=10^{(L+20\log h_1h_2)/40}$:

| Receiver | S (dBm) | Path loss allowed | Ground range | Free-space range |
|---|---|---|---|---|
| superregen (realistic) | −100 | 90 dB | 267 m | 1.7 km |
| superregen (seller claim) | −105 | 95 dB | 356 m | 3.1 km |
| CC1101, 1.2 kBaud | −112 | 102 dB | 532 m | 6.9 km |
| CC1101, 0.6 kBaud | −116 | 106 dB | 670 m | 11.0 km |

12 dB of extra sensitivity doubles the range near the ground but quadruples it in line of sight (script F). Raising both antennas helps the ground case as much ($h_1h_2$ enters directly). Interference matters too: a 1.45 MHz-wide superregen also hears every 433 MHz key fob and weather station in that band, so in town the realistic range is often well below the table.

### Example 8 — An LNB on an SDR
A PLL LNB (25 MHz reference, NF 0.8 dB, 55 dB gain), 20 m of RG-6 (≈ 4 dB at 1.5 GHz) and an RTL-SDR (NF ≈ 12 dB at an L-band IF — the [canonical](../00-math-foundations/canonical-values-and-conventions.md) RTL-SDR V3 measurement is 11.9 dB at 1280 MHz; 30 dB internal gain) give a cascade NF of 0.800 dB (the same with a 6 dB SDR; 0.803 dB even with a 20 dB SDR): the LNB sets everything. With a 50 K sky the broadband IF noise reaching the SDR is ≈ −36 dBm over 1.2 GHz, enough to load an 8-bit tuner, so pad 10–20 dB and keep the tuner gain low. For a narrowband downlink, budget ±293 kHz of LO uncertainty (30 ppm crystal) or replace the reference: 2 ppm → ±19.5 kHz.

### Example 9 — Is a 0.8 m TV dish enough for 1.7 GHz?
D = 0.8 m at 1694.1 MHz: G = 0.5(πD/λ)² → 20.0 dBi; HPBW ≈ 70λ/D = 15.5°; T_sys ≈ 95 K → G/T ≈ 0.2 dB/K. NOAA's 1.0 m minimum for HRIT [14] corresponds to 22.0 dBi at the same efficiency, so the 0.8 m dish starts 1.9 dB short. Suppose the 1 m dish exactly meets the requirement: coded BPSK needs Eb/N0 ≈ 3 dB, plus 2 dB implementation, i.e. C/N0 61 dB-Hz at 400 kb/s, and the slant range is 37 600 km (FSPL 188.5 dB). The implied downlink EIRP is ≈ 48.8 dBm, and the 0.8 m dish then gets C/N0 59.1 dB-Hz. That assumed requirement is not a NOAA figure: it shows the method, not a guarantee (script D). Gain is cheaper from a better LNA (T_sys 95 → 75 K is +1 dB) or a 1.2 m dish (+3.5 dB) than from a perfect feed.

### Example 10 — A LoRa ground node that listens for a year
SX1262 with DC-DC: continuous RX 4.6 mA → 18 days on 2000 mAh. RX duty-cycle 3 ms every 100 ms → 139 µA average → ≈ 600 days (chip only; MCU sleep, regulator quiescent current and self-discharge usually dominate after that). Cost: every packet to it needs a ≥ 101-symbol preamble at SF7/125 (103 ms), and at 10 % duty in 433.05–434.79 MHz that air time counts. For the rocket link (continuous telemetry), do not duty-cycle the ground receiver.

### Example 11 — "Can the rocket tell whether the ground station is listening?"
No, not by radio. A 1 W transmitter into a dipole sees an echo from a matched ground dipole 1 km away at ≈ −132 dBm, 162 dB below its own carrier and co-channel with it, and buildings and terrain scatter far more. The receiver's state changes the echo by ≤ 6 dB. Only an acknowledgement protocol tells a transmitter that it was heard. LoRa has none unless the firmware sends one ([LoRaWAN vs raw LoRa](../15-lora-ism-radios/lorawan-vs-raw-lora.md)).

## Practical notes
- **Frequency planning:** list every LO, reference, clock (MCU, ADC, switching regulators) and their harmonics; check m×n products into the IF and baseband; avoid IFs that are harmonics of on-board clocks (e.g. 10.7 MHz vs a 21.4 MHz MCU clock is a problem).
- **Gain distribution:** enough gain before the mixer to set NF, not so much that the mixer/ADC IIP3 limits blocking; use AGC (DSA or VGA) after the first filter.
- **Shielding and isolation:** LO leakage to the antenna port radiates (regulatory) and self-mixes; route LO lines away from RF inputs.
- **Test:** measure sensitivity with a calibrated generator and attenuators; blocking with a second generator at offsets; image and spurious responses by sweeping a generator while watching the demodulator output.
- **First superregen build (beginner steps).** (1) Buy an FS1000A + XY-MK-5V pair. Solder 17.3 cm (λ/4) wire antennas to both and drive them from an Arduino ASK library at 1–2 kb/s. (2) Before going outdoors, look at the receiver with an RTL-SDR at 433.9 MHz: the powered XY-MK-5V shows its own ≈ 1–2 MHz-wide emission. That is the re-radiation. (3) Range-test on open ground at 1.5 m and predict ≈ 100–300 m first (Example 7). (4) Swap in an RXB6 or a CC1101 board and repeat. (5) If you build a discrete superregen, add a common-base RF stage between antenna and oscillator and adjust the quench while watching both sensitivity and the waterfall width.
- **Superregen tuning:** a quench that is too slow lets bit edges blur (sampling); too fast widens the bandwidth. A hiss with no signal means the SRO is regenerating correctly; silence means it is not oscillating.
- **LNB handling:** never connect a powered LNB line straight to an SDR input. Use a bias-tee with the DC on the LNB side, and switch the supply off before plugging F-connectors (13/18 V shorts are common). Keep the LNB in its weatherproof cover; it is designed for the dish focus, not a bench.
- **Duty-cycled receivers** must agree with their transmitters on preamble length; changing one side's settings silently breaks reception.
- **Bring-up:** stage-by-stage signal tracing and IF alignment of a real receiver: [17 bring-up playbook § F](../17-test-measurement/rf-bring-up-debug-playbook.md#f-receiver-stage-by-stage-signal-tracing-and-if-alignment).

## Common mistakes & misconceptions
- *"Zero-IF has no image."* Its image is the signal's own mirror (negative frequency); IQ imbalance leaks it into the channel.
- *"Low-IF is just a superhet with a small IF."* The image is so close that it can only be rejected by complex (IQ) processing, not by an RF filter.
- *"A good IF filter protects against everything."* Image, half-IF and LO-harmonic responses are converted *onto* the IF — only the RF filter or mixer balance can stop them.
- *"More ADC bits fix direct sampling."* Clock jitter caps SNR at high input frequencies regardless of bits.
- *"The receiver's sensitivity is its NF."* Blocking, reciprocal mixing and spurs often dominate in real RF environments.
- *"DC offset can be removed with a capacitor."* Only if the signal has no content near DC and the offset is static; self-mixing offsets vary with the antenna environment.
- *"A superregen's selectivity comes from its tuned circuit, so a higher-Q coil fixes it."* The bandwidth is set by how fast the quench sweeps the damping through zero. Slower quench is narrower but limits the data rate.
- *"The XY-MK-5V is −105 dBm, so it matches a superhet."* That seller figure sits at the thermal floor of a 1.5 MHz window. A CC1101 at 1.2 kBaud is −112 dBm in a narrow channel and is far more selective.
- *"Double the sensitivity budget, double the range."* Near the ground range grows only as $10^{\Delta/40}$.
- *"Receivers don't transmit."* Superhets leak their LO, superregens radiate outright, and both are regulated (FCC §15.109/§15.111).
- *"My transmitter can tell whether the receiver is on."* No: the echo is ≈ 160 dB below the carrier. Use acknowledgements.
- *"LNB noise figure 0.1 dB."* That is marketing; measured LNBs are typically 0.5–1 dB. The LO error (±hundreds of kHz to ±2.5 MHz) matters more for SDR use.
- *"The dish points where its face points."* An offset dish's beam is ≈ 20–28° above its face normal.

## How to simulate / verify
- `tools/verify/rfckt_rx_tx.py` (receiver sections A–F): image/half-IF rejection vs IF, IIP2 requirement, flicker penalty zero-IF vs low-IF, jitter SNR and Nyquist zones, superhet cascade NF/IIP3, reciprocal mixing.
- `tools/verify/rfckt_mixers.py`: spur finder for any frequency plan.
- System simulation: Python/GNU Radio models of IQ imbalance, DC offset and phase noise; vendor tools (e.g. ADI's AD9361 filter wizard) for real chips.
- `tools/verify/s14_superregen.py` (15/15 PASS, output in `s14_superregen_output.txt`): superregen envelope ODE vs Gaussian closed form (bandwidth, regenerative gain), bandwidth vs quench, noise floor, logarithmic mode, re-radiation estimate vs FCC limits, OOK range table, FM-bug pulling and §15.239, crystal-set diode detection (exact $nV_T\ln I_0$).
- `tools/verify/s14_rx_budget.py` (20/20 PASS, output in `s14_rx_budget_output.txt`): LNB plan and LO error, LNB cascade and IF noise power, offset-dish geometry and Singapore elevations, L-band dish budget, receiver power and duty cycling, LO-leakage budget, receiving-antenna RCS and echo.

## Open questions / gaps
- XY-MK-5V, FS1000A, RXB6 and SYN4x0R figures are seller claims; the XY-MK-5V quench frequency and real sensitivity, and its measured re-radiation, are not in the KB. These are good bench measurements (17/bench-measurement-recipes).
- EN 300 220-1 receiver-spurious values were not re-read (the harmonised -2 part points to clause 8.6 of -1). The GOES HRIT downlink EIRP was not found; Example 9 back-computes it from NOAA's dish size under a stated assumption.
- SX126x sleep currents quoted from the data-sheet family, not re-read for this edit.
- SX126x IF value and on-chip image rejection figure not extracted (domain 15).
- R820T/RTL2832U details are from secondary sources (blogs/community documentation), not Rafael Micro/Realtek data sheets (which are not public).
- ADC NF for specific RF-sampling ADCs not tabulated (domain 18).

## Sources
1. B. Razavi, *RF Microelectronics*, 2nd ed., 2011, ch. 4 (heterodyne, direct-conversion, image-reject, low-IF receivers; DC offsets, IIP2, flicker, IQ mismatch). (textbook)
2. D. M. Pozar, *Microwave and RF Design of Wireless Systems*, Wiley, 2001 — chapters on receiver design and architectures (frequency planning, image, sensitivity). (textbook)
3. Semtech, *SX1261/2 Data Sheet* rev. 1.2 (2019) / 2.1 — receiver description ("mostly low-IF"). https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf (datasheet; via search excerpt)
4. RTL-SDR community documentation (e.g. "Realtek RTL2832U: the mystery chip at the heart of RTL-SDR", Uni Regensburg notes; M. Bavaro, "R820T with 28.8 MHz TCXO", GNSS blog, 2014): R820T 3.57 MHz IF, 28.8 MS/s 8-bit ADC, DDC and resampling. (secondary / community — anecdotal for exact numbers)
5. Analog Devices, *AD9361 RF Agile Transceiver* data sheet: 70 MHz–6.0 GHz, 200 kHz–56 MHz bandwidth, direct conversion, 12-bit ADC/DAC, on-chip calibrations. https://www.analog.com/en/products/ad9361.html (datasheet)
6. B. Brannon, "Sampled systems and the effects of clock phase noise and jitter," Analog Devices AN-756, 2004. (app note)
7. E. H. Armstrong, "Some recent developments of regenerative circuits," *Proc. IRE*, 10(4), pp. 244–260, Aug. 1922 (superregeneration). (peer-reviewed)
8. F. X. Moncunill-Geniz, P. Palà-Schönwälder, O. Mas-Casals, "A generic approach to the theory of superregenerative reception," *IEEE Trans. Circuits Syst. I*, 52(1), pp. 54–67, 2005 (sensitivity curve, regenerative gain, linear/logarithmic modes; abstract read, model re-derived here). (peer-reviewed)
9. J. R. Whitehead, *Super-Regenerative Receivers*, Cambridge Univ. Press, 1950; E. Insam, "Designing super-regenerative receivers," *Electronics World*, April 2002 (classic theory, quench design, log mode). (textbook / magazine; not re-read)
10. 47 CFR §15.109(a) (Class B radiated limits: 100/150/200/500 µV/m at 3 m) and §15.111(a) (receiver antenna-terminal power ≤ 2.0 nW), via law.cornell.edu, read 2026-10-13; §15.239 via [regulatory FAQ](../19-regulations-safety/regulatory-faq-misc.md). (regulation)
11. Seller listings for FS1000A/XY-MK-5V (Tayda Electronics; BerryBase datasheet: 10 mW, −105 dB(m), "about 200 m") and SYN480R modules (≈ −107 dBm), read 2026-10-13. (vendor — unverified)
12. Texas Instruments, *CC1101* data sheet SWRS061I, sensitivity at 433 MHz (via [other ISM radios](../15-lora-ism-radios/other-ism-radios-fsk-2g4.md)). (datasheet)
13. LNB data sheets and listings read 2026-10-13: Goobay universal PLL LNB (9.75/10.6 GHz, 25 MHz ref, ±300 kHz, "0.1 dB"); NISD NJR2841/2843 (±10–100 kHz, 0.8 dB); Labgear VK8L/VK4L DRO (±1.3 MHz at 25 °C, ±2.5 MHz −40…70 °C); Av-Comm L1205 DRO (±1 MHz, 0.7 dB, 65 dB); Othernet Bullseye (2 ppm TCXO). (vendor)
14. NOAA NESDIS, HRIT/EMWIN broadcast characteristics (1694.1 MHz, 927 ksps BPSK, 400 kb/s, 1.205 MHz, linear; minimum antenna 1.0 m at ≥ 10° elevation, 1.2 m at 5°), https://noaasis.noaa.gov/GOES/HRIT/broadcast.html, read 2026-10-13. (agency)
15. TI LMX2572 current via [mixers/PLL parts](../18-components-parts/mixers-plls-vcos-parts.md). (datasheet, secondary)
16. B. Murmann, "ADC Performance Survey 1997–2024," Stanford, https://github.com/bmurmann/ADC-survey (Schreier figure of merit). (survey; the 160–185 dB range was quoted from memory. W5-S18b checked it on 2026-10-13: it is consistent with the reported state-of-the-art envelope of ≈ 186 dB FOM_S, against a theoretical ≈ 192 dB, as summarised from the survey in a University College Cork thesis (cora.ucc.ie). The survey spreadsheet itself was not read.)
17. RTL-SDR Blog, *RTL-SDR Blog V3 Datasheet* (typical current 270–280 mA), via Mouser, read 2026-10-13. (datasheet)
18. W. Hayward, R. Campbell, B. Larkin, *Experimental Methods in RF Design* (EMRFD), ARRL, 2003, chapters on mixers, superheterodyne and direct-conversion receivers (chapter numbers not re-checked); *The ARRL Handbook for Radio Communications* (2023), receivers chapter (regeneration, superregeneration, superhet design). (textbook)
