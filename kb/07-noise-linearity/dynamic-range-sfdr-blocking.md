---
title: Dynamic range, SFDR, blocking, desensitisation, selectivity and AGC
domain: 07-noise-linearity
slug: dynamic-range-sfdr-blocking
tags: [dynamic-range, SFDR, blocking, desensitization, selectivity, adjacent-channel-rejection, ADC-noise-figure, processing-gain, AGC, co-site-interference, superposition, preselection, RMDR, reciprocal-mixing]
prerequisites: [nonlinearity-p1db-ip3-intermod.md, noise-figure-and-friis.md, phase-noise-and-jitter.md]
related: [receiver-cascade-analysis.md, sensitivity-and-mds.md, ../06-rf-circuits/receiver-architectures.md, ../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md, ../05-analog-electronics/data-converters-adc-dac.md, ../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md, ../15-lora-ism-radios/ground-station-design.md, ../13-pcb-rf-layout-emc/shielding-and-isolation.md]
level: intermediate
confidence: high
last_updated: 2026-10-13
---

# Dynamic range, SFDR, blocking, desensitisation, selectivity and AGC

## Questions this page answers
- What is spurious-free dynamic range (SFDR) and why is it "two-thirds of IIP3 minus the noise floor"?
- What is the difference between blocking, desensitisation, adjacent-channel rejection and selectivity?
- Why can a transmitter on the same mast stop my receiver even though it is on a different channel?
- How does an ADC's SNR translate into a noise figure, and how much gain do I need in front of an SDR's ADC?
- What does "processing gain" of an oversampling ADC mean?
- What is AGC for, and what does it cost?
- How do I read the SX1262 blocking and ACR numbers?
- How can billions of radio signals share the air without interfering with each other?
- Why does a nearby transmitter on a completely different frequency still knock out my receiver?
- What does a classic communications receiver have that a cheap SDR does not?

## TL;DR
- **Noise floor** (input-referred) $N = -174 + \text{NF} + 10\log_{10}B$ dBm. **SFDR** (third order) $= \tfrac23(\text{IIP3} - N)$: the range of input levels from the noise floor up to where IM3 just reaches the noise floor. Examples (`tools/verify/noise_dynamic_range.py`): SX1262 alone (NF 6, IIP3 −5 dBm, 125 kHz) **74.7 dB**; with a masthead LNA (NF 2.55, IIP3 −18.9) **67.7 dB** — the LNA buys 3.5 dB of sensitivity but costs 7 dB of SFDR.
- **Compression dynamic range** = IP1dB − N (≈ 92–102 dB for the chains above): the largest single signal the receiver handles cleanly.
- **Blocking** = the level of an off-channel signal that degrades sensitivity by a stated amount (Semtech specifies it relative to sensitivity +3 dB: SX1262 88/90/99 dB at 1/2/10 MHz for SF12/BW125). **ACR** (adjacent-channel rejection) is the same idea one channel away (60 dB SF7, 72 dB SF12). Mechanisms: gain compression, reciprocal mixing, IM products, spurious responses.
- **Desensitisation** from reciprocal mixing adds $P_b + \mathcal{L}(\Delta f) + 10\log B$ of noise: −44 dBm at 1 MHz with −122 dBc/Hz LO noise costs **4.1 dB** in a 125 kHz channel.
- **ADC as a receiver stage:** $\text{NF}_\text{ADC} = P_\text{FS} - \text{SNR} - 10\log_{10}(f_s/2) + 174$ (ADI MT-052 method). A 14-bit, 100 MS/s ADC with SNR 74 dB and +10 dBm full scale has **NF ≈ 33 dB**; it needs ≈ 40 dB of low-noise gain in front to add < 0.5 dB. Oversampling gives processing gain $10\log_{10}(f_s/2B)$ (26 dB for 100 MS/s → 125 kHz).
- **Co-sited transmitters** (a second link, an RTK-correction uplink, another team) at 1 W with 30 dB antenna isolation put ~0 dBm into your front end — far above any LNA's P1dB. Only frequency separation + pre-selection filters + antenna separation/cross-polarisation fix it.
- **AGC** keeps the strongest signals below compression by reducing gain early, trading NF for headroom only when signals are strong.

## Intuition (no math)
A receiver has a floor (its own noise) and a ceiling (where it starts to distort). **Dynamic range** is the distance between them. The subtlety is that there are several ceilings:
- the level at which a *single* strong signal compresses the gain (compression-limited),
- the level at which *two* strong signals create intermodulation products as big as the noise (spurious-free, IM-limited),
- the level at which a strong signal *in another channel* makes the wanted weak signal undetectable (blocking/selectivity).

IM3 products grow three times faster than the signals that create them, so the IM-limited ceiling is reached much earlier than the compression ceiling. That is why SFDR is always smaller than the compression range, and why it uses the funny factor of two-thirds.

**Blocking** is the practical question: "how strong can the neighbour be before my weak signal is lost?" A strong blocker hurts in several ways at once: it compresses the LNA and mixer (less gain for the wanted signal), it mixes with the LO's phase-noise skirt to put noise in your channel (reciprocal mixing), it combines with other signals into IM products, and it may leak through imperfect channel filters. **Selectivity** is the receiver's ability to *reject* off-channel signals: filters before the nonlinear parts protect against compression and IM; filters after the mixer (the channel filter) reject what gets through.

An **ADC** is a receiver stage with a very high noise figure (it is designed for big signals) but a huge ceiling. Put enough gain in front so its noise does not matter, but not so much that big signals clip it — AGC manages that trade dynamically.

> **Plain-language box 1: why billions of signals share the air.** Radio waves in air (and in any linear circuit) obey **superposition**: fields simply add, and two signals pass through each other without interacting. Every antenna therefore delivers the sum of everything at once. A receiver picks one signal out by **selectivity**: by frequency (filters), by direction (antenna pattern), by time (bursts, duty cycle) and by code (spreading, LoRa chirps). The only place signals *do* interact is inside a **nonlinear** stage, which is the subject of this page. **One number:** a 50 kW e.r.p. FM broadcaster 10 km away delivers about −11 dBm to a dipole, **126 dB** more than the −137 dBm LoRa packet you can still decode. Both coexist because filters keep the broadcaster away from the nonlinear stages (`tools/verify/s7_receiver_numbers.py` §1a).

> **Plain-language box 2: too close means saturation.** Selectivity only works while every stage ahead of the filter stays linear. A transmitter close by overloads the front end however far away its frequency is: the LNA compresses, the mixer intermodulates, and the AGC turns the gain down for everyone. **One number:** 1 W at 434 MHz between two 2 dBi antennas 1 m apart gives about **+9 dBm** at the receiver (a free-space estimate; at 1 m you are in the near field, so treat it as an order of magnitude). That is 38 dB above the masthead chain's input P1dB (−28.9 dBm). It falls to the SX1262's 10 MHz blocking level (−35 dBm) only at about **155 m**, and to its 1 MHz level (−46 dBm) at 550 m (§1b). This is why a team's own ground-station transmitter, or a neighbouring team at the launch rail, can blank a receiver on a "different channel".

> **Plain-language box 3: a cheap SDR is not a communications receiver.** A classic communications receiver spends its money on three things a USB SDR mostly lacks. (1) **Preselection**: switched or tracking band-pass filters ahead of the first active stage, so that off-band giants never reach it. An RTL-SDR has essentially none, so the whole 25–1750 MHz world hits its LNA. (2) **High IIP3** front ends and roofing filters, which keep two-tone intermodulation below the noise. (3) **A clean local oscillator**, measured as reciprocal-mixing dynamic range $\text{RMDR} = -\mathcal L(\Delta f) - 10\log_{10}B$. **One number:** with an LO of −90 dBc/Hz at 10 kHz (an illustrative cheap tuner PLL) the RMDR in a 2.4 kHz channel is **56 dB**; with −130 dBc/Hz (a low-noise synthesiser, also illustrative) it is 96 dB. An 8-bit ADC adds a hard ceiling: 49.9 dB ideal SQNR over 2.4 MHz, at most ≈ 80 dB in a 2.4 kHz channel after processing gain (§1c). An SDR is excellent for *looking*. In a crowded band, add an external preselector or SAW filter ([SDR front-end protection](../14-sdr-dsp/sdr-front-end-protection-and-filtering.md)) before trusting it as a receiver.

## The math

### Level 1 — key formulas
- Input-referred noise floor: $N = -173.98 + \text{NF} + 10\log_{10}B$ dBm (source at 290 K; replace by $10\log_{10}(k(T_a+T_e)B)$ + 30 in general).
- Third-order SFDR: $\text{SFDR}_3 = \tfrac23(\text{IIP3} - N)$ dB. Second-order: $\text{SFDR}_2 = \tfrac12(\text{IIP2} - N)$.
- Compression DR: $\text{IP1dB} - N$.
- Reciprocal-mixing noise: $N_{RM} = P_b + \mathcal{L}(\Delta f) + 10\log_{10}B$; total noise $N_\text{tot} = 10\log_{10}(10^{N/10} + 10^{N_{RM}/10} + \dots)$; desensitisation $= N_\text{tot} - N$.
- Ideal ADC SNR (full-scale sine, Nyquist band): $6.02\,n + 1.76$ dB. Processing gain for a channel $B$ in a Nyquist band $f_s/2$: $10\log_{10}(f_s/(2B))$ (real sampling; for complex IQ sampling at $f_s$ the noise spreads over $f_s$ and the gain is $10\log_{10}(f_s/B)$, 3 dB more — [sampling](../14-sdr-dsp/sampling-aliasing-bandpass-sampling.md#level-3--the-real-sampler-jitter-aperture-reconstruction-and-edge-cases)).
- ADC noise figure (sampling rate $f_s$, full-scale sine power $P_\text{FS}$ dBm into the input impedance, SNR in the full Nyquist band): $\text{NF} = P_\text{FS} - \text{SNR} - 10\log_{10}(f_s/2) + 174$ dB.

### Level 2 — derivations
**SFDR.** Input-referred IM3 power for two equal tones of power $P$: $P_{IM3} = 3P - 2\,\text{IIP3}$. The largest $P$ for which the IM3 does not exceed the floor satisfies $3P - 2\,\text{IIP3} = N$, i.e. $P_\text{max} = (2\,\text{IIP3} + N)/3$. The minimum usable signal is at the floor, so
$$\text{SFDR} = P_\text{max} - N = \tfrac23(\text{IIP3} - N).$$
Some authors define the lower limit as "floor + required SNR" and so quote SFDR minus $\text{SNR}_\text{min}$; LoRa's negative SNR requirement would *raise* that version. The script finds $P_\text{max}$ numerically and matches the closed form (e.g. SX1262 alone: floor −117.0 dBm, $P_\text{max}$ = −42.3 dBm, SFDR 74.7 dB). The same argument with $P_{IM2} = 2P - \text{IIP2}$ gives $\tfrac12(\text{IIP2} - N)$.

**ADC noise figure (after MT-052 [2]).** An ADC with SNR measured with a full-scale sine over the Nyquist band $f_s/2$ has a noise power $P_\text{FS} - \text{SNR}$ (dBm) spread over $f_s/2$, i.e. a density $P_\text{FS} - \text{SNR} - 10\log_{10}(f_s/2)$ dBm/Hz. Compared with $kT_0$ (−174 dBm/Hz) that is its noise figure: $\text{NF} = P_\text{FS} - \text{SNR} - 10\log_{10}(f_s/2) + 174$. Examples (script): 14-bit class (SNR 74 dB, 100 MS/s, +10 dBm FS) → 33 dB; 12-bit (65 dB, 61.44 MS/s, +4 dBm) → 38 dB; 8-bit RTL-SDR-class (≈45 dB, 2.4 MS/s, ~0 dBm FS, illustrative) → 68 dB — the reason RTL-SDRs need their internal tuner gain, or an external LNA, to be useful. Caveats: the SNR at the actual input frequency and clock jitter apply (see [phase-noise-and-jitter](phase-noise-and-jitter.md)); the input impedance used to define $P_\text{FS}$ (often 200 Ω or 50 Ω via a transformer) must be the one the preceding stage drives; and wideband noise from the front end aliases from all Nyquist zones unless anti-alias filtered.

**How much gain before the ADC?** By Friis, with a front end of NF 2 dB, the ADC adds ≤ 0.5 dB if $G \ge$ 32 dB (ADC NF 25 dB), 40 dB (33 dB) or 47 dB (40 dB) (script §2). But the same gain lowers the input-referred clipping level by $G$ — so the ADC's full scale referred to the antenna becomes $P_\text{FS} - G$ (e.g. +10 − 40 = −30 dBm). The overall dynamic range cannot exceed the ADC's own (SNR + processing gain) without AGC.

**Desensitisation.** A blocker at $P_b$ and offset $\Delta f$ adds reciprocal-mixing noise; compression of early stages by the blocker reduces their gain, making later stages' noise more important (Friis with reduced $G_1$); some LNAs also show an increased noise figure under large-signal drive. For $P_b$ = −44 dBm and $\mathcal{L}$ = −122 dBc/Hz at 1 MHz, $N_{RM}$ = −115.0 dBm vs the −117.0 dBm thermal floor: 4.1 dB desense (script §3).

### Level 3 — how datasheet selectivity numbers are built, and limits
**Reading the SX1262 table [3].** Semtech specifies co-channel rejection, ACR and blocking with a single CW interferer while the wanted signal is 3 dB above sensitivity, and quotes the interferer-to-wanted ratio that degrades PER to 1 %. For SF12/BW125 (sensitivity −137 dBm, wanted at −134 dBm):
- ACR 72 dB at ±1.5 BW (±187.5 kHz): tolerable interferer ≈ −62 dBm.
- Blocking 88 dB at ±1 MHz → −46 dBm; 90 dB at ±2 MHz → −44 dBm; 99 dB at ±10 MHz → −35 dBm.
- Co-channel rejection 19 dB (SF12) / 5 dB (SF7): with the same test convention, a CW interferer on the *same* frequency can be up to ~19 dB (SF12) or ~5 dB (SF7) *stronger* than the wanted LoRa signal before PER exceeds 1 % — a consequence of LoRa's spreading/processing gain. For FSK the table gives −9 dB, i.e. the FSK wanted signal must be 9 dB *above* the interferer. Note the opposite practical meaning of the two signs.
These figures include all mechanisms (compression, reciprocal mixing, spurious responses) for that chip alone. **Adding an LNA in front divides the blocker tolerance by the LNA gain** (the chip sees a bigger blocker) unless the LNA is preceded by filtering; in the SFDR example the masthead LNA cut SFDR by 7 dB.

**Filter selectivity budget.** To keep a blocker $P_b$ at least 10 dB below the chain's input P1dB, a pre-selector must provide rejection $R \ge P_b - (\text{IP1dB} - 10)$: a −5 dBm co-site blocker into a chain with −28.9 dBm IP1dB needs ≥ 33.9 dB of rejection at the blocker frequency (script §5). SAW filters give 30–50 dB a few MHz away from a sub-GHz passband; cavity filters give more, with less loss, at larger size ([06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)). Filter loss adds directly to NF if placed first — the fundamental noise/linearity trade.

**AGC.** An AGC loop measures signal (or total in-band) power and reduces gain — ideally in the stage *just before* the first stage that would overload, and in steps that keep NF low when signals are weak. Considerations: attack time must be fast enough for bursty signals (a LoRa preamble of 8 symbols at SF7 lasts ~8 ms), decay slow enough not to pump; AGC driven by a strong *out-of-channel* signal reduces the gain for your weak in-channel signal (a form of desensitisation). Transceivers like the SX126x select LNA gain steps automatically; the "Rx boosted gain" mode trades current for ~4 dB better sensitivity (−137 vs −133 dBm at SF12/BW125 in the datasheet table) [3].

**Limits of the simple formulas.** SFDR uses equal two-tone IM3 at the band edge; real interference is broadband (digital modulation), for which IM3 spreads as spectral regrowth and "noise-like" intermodulation, and the relevant metric is the noise-power ratio or the ACLR of the interferer. Spurious responses of superheterodynes (image, half-IF, LO harmonics) are separate "holes" in selectivity that the IIP3 model does not capture.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $\text{SFDR}_3 = \tfrac23(\text{IIP3} - N)$ | two-tone IM3-limited | 65–80 dB for LoRa-class receivers in 125 kHz |
| $\text{SFDR}_2 = \tfrac12(\text{IIP2} - N)$ | zero-IF, wideband | IIP2 +40 dBm → 78.5 dB (125 kHz, NF 6) |
| DR$_\text{comp}$ = IP1dB − N | single strong signal | ~90–100 dB |
| $\text{NF}_\text{ADC} = P_\text{FS} - \text{SNR} - 10\log(f_s/2) + 174$ | ADC used as receiver | 25–40 dB (12–16 bit); ~60–70 dB for 8-bit |
| Processing gain $10\log(f_s/2B)$ | oversampled narrowband channel, real ADC (complex IQ at $f_s$: $10\log(f_s/B)$) | 100 MS/s → 125 kHz: 26 dB |
| Blocking level = sensitivity + 3 dB + BI | Semtech convention | SX1262 SF12: −46 dBm @1 MHz |
| Required pre-selection $R \ge P_b - \text{IP1dB} + 10$ | keep blocker 10 dB below compression | co-site 1 W: 20–40 dB |
| Every dB of LNA gain lowers IIP3 by ~1 dB when later stage dominates | cascade | trade 1:1 |

## Worked examples
**1 — SFDR with and without a masthead LNA (915 MHz station).**
- Module alone at the end of 10 m of coax: NF 8.6 dB, IIP3 −2.4 dBm → $N$ = −114.4 dBm, SFDR = 74.7 dB (`noise_cascade.py` A1).
- SAW + LNA at the mast: NF 2.55 dB, IIP3 −18.9 dBm → $N$ = −120.5 dBm, SFDR = 67.7 dB (A2).
The LNA gains 6.1 dB of sensitivity and loses 7 dB of SFDR. In a quiet field site that is a good trade; at a crowded launch event with several teams on 433/868/915 MHz it may not be.

**2 — A second transmitter at the ground station.** Suppose the ground station also transmits (for example an RTK-correction uplink or a command link) at 1 W with its antenna 2–3 m from the telemetry Yagi, and assume 30 dB of antenna-to-antenna isolation (an assumption: depends strongly on patterns, polarisation and spacing). The blocker at the telemetry front end is 30 − 30 = **0 dBm** — ~29 dB above the masthead chain's input P1dB (−28.9 dBm) and 46 dB above the SX1262's 1 MHz blocking tolerance. Even 50 dB of isolation (−20 dBm) still compresses the chain. With the transmitter in a *different band* and a cavity/SAW filter giving 40 dB of extra rejection, the blocker falls to −40 dBm, ≥ 10 dB below compression (script §4). Practical fixes: put the uplink in a different band from the downlink, space and cross-polarise the antennas, add pre-selection, time-share (don't transmit while expecting critical downlink packets).

**3 — Choosing an SDR front-end gain.** A 12-bit SDR (NF ≈ 38 dB by the MT-052 method, full scale +4 dBm) behind an LNA of NF 2 dB needs ≈ 45 dB of total gain for the ADC to add ≤ 0.5 dB — at which point the ADC clips at an antenna-referred −41 dBm. A nearby 1 W transmitter will clip it; set gain for the environment, not for the datasheet noise floor.

**4 — Reciprocal-mixing desense.** From [phase-noise-and-jitter](phase-noise-and-jitter.md) Example 2: another team's 1 W at 0.9 MHz offset, 1 km away, arriving at −44 dBm with −122 dBc/Hz LO noise → 4.1 dB desense of a 125 kHz channel. Pointing the Yagi off that team (−15 dB sidelobe) reduces it to about 0.2 dB.

## Practical notes
- **Survey the RF environment at the launch site** with an SDR before the flight: note every strong signal within ±10 MHz of your channels and within the passband of any wideband LNA (a 400–1000 MHz LNA with no filter "sees" everything, including cellular and broadcast).
- **Band planning between the team's own links:** the primary (433 MHz) and secondary (900 MHz) links are well separated, but the E22's 2nd harmonic (866 MHz) falls near the 868/915 MHz band; if both receivers share a mast, check the 900 MHz receiver's blocking and the 433 MHz transmitter's harmonic level (relevant when a ground station also transmits at 433 MHz).
- **Filters before LNAs** are standard in GNSS (SAW–LNA–SAW) precisely because cellular and 2 W telemetry transmitters are nearby; a GNSS LNA with ~−15 dBm input P1dB is compressed by an out-of-band signal of that level unless the pre-filter rejects it.
- **Watch the AGC during bench tests:** a receiver that "works" on the bench with an attenuated signal may behave differently when its AGC is pulled down by a strong local interferer at the field.
- **AGC loop dynamics, RSSI and receiver DSP features (NB/NR/ANF):** see [06 AGC loops](../06-rf-circuits/agc-loops-and-receiver-gain-control.md#level-3--agc-in-real-receivers).

## Common mistakes & misconceptions
- **Quoting SFDR without the bandwidth** — SFDR depends on $B$ through the noise floor ($\tfrac23\cdot10\log B$).
- **"More LNA gain = better receiver."** Better NF, worse blocking/SFDR; beyond the gain needed to bury later-stage noise, extra gain only hurts.
- **Using the ADC's SNR as the receiver's dynamic range** without processing gain (too pessimistic) or without clock jitter and front-end noise (too optimistic).
- **Assuming a different channel means no interference.** Blocking, reciprocal mixing and IM3 all come from off-channel signals.
- **Misreading LoRa co-channel rejection** as the same sign convention as FSK (see Level 3).
- **Forgetting the filter's loss adds to NF** when placing a SAW before the LNA.
- **"Different frequency, so no interference."** Selectivity acts only after every stage before it stays linear. A 1 W transmitter needs ≈ 155 m of free-space separation before it drops to the SX1262's 10 MHz blocking level (box 2).
- **"My SDR's spec says 8-bit, so 48 dB dynamic range."** Processing gain lifts that in a narrow channel (≈ 80 dB ideal in 2.4 kHz), but without preselection the whole tuner range shares the ADC's headroom, and LO noise limits RMDR (box 3).

## How to simulate / verify
- `tools/verify/noise_dynamic_range.py` — SFDR closed form vs numerical solution, second-order SFDR, compression DR, ADC NF (MT-052 method), processing gain, gain-before-ADC calculator, desensitisation budget, co-site blocking and required pre-selection.
- `tools/verify/noise_cascade.py` — prints cascade NF, IIP3, P1dB and SFDR per stage.
- `tools/verify/s7_receiver_numbers.py` §1 — the plain-language box numbers (FM broadcaster vs LoRa, 1 W at 1 m and the blocking distances, RMDR and 8-bit ADC ceiling).
- Bench: two-signal blocking test — wanted LoRa signal at sensitivity + 3 dB from one generator, CW blocker from a second through a combiner; raise the blocker until PER reaches 1 %; compare with the datasheet table.
- In an SDR, compute a histogram of ADC codes with the antenna connected at the field to check headroom (how close to full scale the strongest signals get).

## Open questions / gaps
- Actual antenna-to-antenna isolation for co-located ground-station antennas (Yagi–Yagi, Yagi–whip) at 433/915 MHz was assumed (30–50 dB); an NEC/openEMS coupling model or a VNA S21 measurement would replace the assumption (cross-domain 08, 17).
- The MT-052 PDF could not be re-read this session (timeouts); the ADC NF formula was re-derived here and matches the method as commonly cited.
- EBYTE module blocking performance with their integrated LNA is unknown.

## Sources
1. B. Razavi, *RF Microelectronics*, 2nd ed., 2011, §2.2.4–2.2.6 (desensitisation, cross-modulation, cascaded nonlinearity), §2.4 (sensitivity and dynamic range, SFDR). (textbook)
2. W. Kester, "ADC Noise Figure — An Often Misunderstood and Misinterpreted Specification," Analog Devices Tutorial MT-052, https://www.analog.com/media/en/training-seminars/tutorials/MT-052.pdf; and *Data Conversion Handbook* (Newnes 2005) ch. 2 (SNR, processing gain). (app note / textbook) — ADC NF method. *Cited; fetch timed out this session.*
3. Semtech, *SX1261/2 Data Sheet* Rev 1.2 (2019) / Rev 2.2 (2024), Table 3-8: blocking, ACR, CCR test conditions and values; Rx boosted vs power-saving sensitivity. (datasheet)
4. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012, §10.3 (dynamic range and intermodulation). (textbook)
5. `tools/verify/noise_dynamic_range.py`, `tools/verify/noise_cascade.py`, `tools/verify/s7_receiver_numbers.py` (this KB). The RMDR definition $-\mathcal L(\Delta f) - 10\log B$ follows from the reciprocal-mixing formula of Level 1: it is the blocker-to-noise-floor ratio at which the reciprocal-mixing noise equals the floor (total noise up 3 dB). This is the convention of ham-receiver test reports; the two phase-noise values in box 3 are illustrative, not measurements of a named tuner.
