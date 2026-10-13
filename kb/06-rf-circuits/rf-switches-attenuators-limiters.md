---
title: RF switches, attenuators and limiters (PIN, FET/SOI, T/R switching, Pi/T pads, DSAs, LNA protection)
domain: 06-rf-circuits
slug: rf-switches-attenuators-limiters
tags: [rf-switch, pin-diode, soi, fet-switch, ron-coff, spdt, tr-switch, quarter-wave-switch, attenuator, pi-pad, t-pad, digital-step-attenuator, limiter, schottky, flat-leakage, spike-leakage, lna-protection]
prerequisites:
  - ../05-analog-electronics/diodes-schottky-pin-varactor.md
  - ../03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md
  - ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md
related:
  - lna-design.md
  - power-amplifiers.md
  - transmitter-architectures.md
  - receiver-architectures.md
  - ../12-phased-arrays/phase-shifters-ttd-components.md
  - ../18-components-parts/rf-switches-attenuator-parts.md
  - ../17-test-measurement/rf-power-measurement.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# RF switches, attenuators and limiters

## Questions this page answers
- How does a PIN diode act as an RF switch, and why does it need milliamps of bias?
- Series or shunt switch — which gives better isolation, and at what cost?
- What does "Ron × Coff" mean for a CMOS/SOI switch, and how does it set insertion loss and isolation?
- How does a quarter-wave T/R switch protect a receiver when transmitting?
- Which switch should go between a LoRa transceiver's PA and LNA and the antenna?
- How do I calculate Pi and T attenuator resistor values, and how much power does each resistor take?
- Why does an attenuator improve return loss?
- What is a digital step attenuator (DSA) good for?
- How do I protect an LNA from a nearby transmitter, and what are flat leakage and spike leakage?
- Why is an anti-parallel diode pair a poor limiter for a 0 dBm-rated GNSS LNA?

## TL;DR
- **Element formulas** (verified against a circuit solver): a series element $Z$ in a $Z_0$ line loses $20\log|1+Z/2Z_0|$; a shunt element $Z$ loses $20\log|1+Z_0/2Z|$. PIN at 1 Ω on / 0.3 pF off: series switch IL 0.09 dB, isolation 21.8 dB at 434 MHz but only 7.6 dB at 2.45 GHz; shunt switch isolation 28.3 dB (Rs-limited), IL 0.002–0.06 dB. **Series-shunt** arms combine them: > 60 dB isolation at 434 MHz.
- **PIN physics**: forward-biased, the I-region is flooded with stored charge $Q=I_F\tau$ and behaves as a *linear resistor* $R\approx W^2/[(\mu_n+\mu_p)Q]$ at frequencies $f\gg1/(2\pi\tau)$ (W = 50 µm, τ = 1 µs: 13.7/1.4/0.27 Ω at 1/10/50 mA); reverse-biased it is a small capacitance $\varepsilon A/W$. Switching speed is limited by τ (µs).
- **FET/SOI switches**: FoM $R_{on}C_{off}$ ≈ 80–250 fs in RF-SOI; IL $\approx20\log(1+R_{on}/2Z_0)$, isolation $\approx10\log[1+(1/(2\omega C_{off}Z_0))^2]$. Power handling comes from **stacking** FETs: +33.5 dBm into 50 Ω is 15 V peak (up to 30 V into an open antenna) → 6–12 devices in series. Example: pSemi PE4259 SPDT (10–3000 MHz): 0.35 dB IL and 30 dB isolation at 1 GHz, IP1dB +33.5 dBm at 3 V [5].
- **λ/4 T/R switch**: series PIN in the TX arm, shunt PIN a quarter-wave down the RX arm. In TX both conduct; the shorted shunt diode appears as an open at the junction (TX IL 0.17 dB, RX protected by 34 dB at 434 MHz); in RX both are off (RX IL 0.01 dB). Narrowband but handles high power.
- **Attenuators**: with $K=10^{A/20}$, Pi: $R_{sh}=Z_0\frac{K+1}{K-1}$, $R_{se}=Z_0\frac{K^2-1}{2K}$; T: $R_{se}=Z_0\frac{K-1}{K+1}$, $R_{sh}=\frac{2Z_0K}{K^2-1}$. 10 dB Pi: 96.3/71.2 Ω (E24 100/68 → 9.63 dB, RL 49.6 dB). With 1 W in, the input shunt resistor of a 10 dB Pi takes 52 % of the power. An A-dB pad improves a load's return loss by 2A dB; its NF equals its loss.
- **Limiters**: a shunt anti-parallel Schottky pair (HSMS-286x-class model) is transparent below −10 dBm (< 0.01 dB) but a **soft** clamp: 0 dBm in → −0.5 dBm out, +20 dBm → +10 dBm (series resistance lets it creep up ≈ 0.5 dB/dB), and it has an IIP3 of only ≈ +27 dBm. PIN limiters self-bias from rectified RF, have "flat leakage" ≈ +10 to +20 dBm depending on I-region thickness and a short "spike leakage" at the start of fast pulses [6][7]. A 0 dBm-rated GNSS MMIC (BGA524N6) is **not** protected by a simple diode pair; choose an LNA with a higher input rating or a multi-stage limiter.

## Intuition (no math)
A switch in an RF line is either a small series resistance (on) or a small series capacitance (off). A small capacitance is not an open circuit at RF: at 2.45 GHz a 0.3 pF "off" diode is only 217 Ω — the signal leaks through. That is why isolation falls with frequency for series switches and why real switches combine a series element with a shunt element that shorts the leakage to ground.

A PIN diode is a controllable resistor. Forward current fills its thick undoped (intrinsic) middle layer with electrons and holes; as long as the RF period is much shorter than the time those carriers take to recombine, the RF cannot sweep them out, and the diode behaves like a plain resistor whose value is set by the DC bias — few ohms with tens of mA. Reverse bias empties the layer and leaves a small capacitor. Because the stored charge is large, a PIN can handle large RF voltages without rectifying them — which is exactly why PINs dominate high-power switching.

FET switches (GaAs pHEMT, SOI CMOS) are voltage-controlled: no bias current, fast, integrated with logic. Their weakness is voltage: a single thin-oxide FET breaks down at a few volts, so high-power switches stack many in series. Their figure of merit is how small the on-resistance and off-capacitance can simultaneously be (Ron × Coff, in femtoseconds).

Attenuators are resistive dividers designed to keep 50 Ω at both ends. They trade signal for match and linearity — useful in test setups, to tame an overload, and in front of a mixer that needs a clean termination. A limiter is a switch that closes by itself when the signal gets too big: a diode (or PIN) that conducts during large peaks, shorting the line and reflecting the excess power.

## The math

### Level 1 — element and attenuator formulas
- Series impedance $Z$ in a matched line: $S_{21}=\frac{2Z_0}{2Z_0+Z}$ → loss $=20\log\left|1+\frac{Z}{2Z_0}\right|$.
- Shunt impedance $Z$: $S_{21}=\frac{2Z}{2Z+Z_0}$ → loss $=20\log\left|1+\frac{Z_0}{2Z}\right|$.
- PIN on-resistance $R_s$, off-capacitance $C_T$; FET $R_{on}$, $C_{off}$; switch cutoff frequency $f_c=1/(2\pi R_{on}C_{off})$.
- Attenuator K-factor $K=10^{A/20}$ with the Pi/T formulas in the TL;DR [1 §4][2].

### Level 2 — derivations

**(a) Series and shunt loss.** A series $Z$ between source $Z_0$ and load $Z_0$: the load voltage is $V_sZ_0/(2Z_0+Z)$ against $V_s/2$ with a direct connection, hence $S_{21}=2Z_0/(2Z_0+Z)$. A shunt $Z$ across the junction: the load sees $Z_0\|Z$, load voltage $V_s(Z_0\|Z)/(Z_0+Z_0\|Z)$, giving $S_{21}=2Z/(2Z+Z_0)$. Numbers for $R_s$ = 1 Ω, $C_T$ = 0.3 pF (check A):

| f | Series IL | Series isolation | Shunt IL | Shunt isolation |
|---|---|---|---|---|
| 434 MHz | 0.086 dB | 21.8 dB | 0.002 dB | 28.3 dB |
| 915 MHz | 0.086 dB | 15.4 dB | 0.008 dB | 28.3 dB |
| 2.45 GHz | 0.086 dB | 7.6 dB | 0.058 dB | 28.3 dB |

Series isolation depends on $C_T$ (falls 6 dB/octave); shunt isolation depends on $R_s$ (flat) and its insertion loss on $C_T$. Package inductance (≈ 0.5–1 nH) resonates with $C_T$ and must be tuned out or included.

**(b) PIN stored-charge resistance.** In high injection the I-region conductivity is $\sigma=q(\mu_n+\mu_p)n$ with total stored charge $Q=qnAW$; the resistance of a slab of length $W$ and area $A$ is $R=W/(\sigma A)=W^2/[(\mu_n+\mu_p)Q]$. In steady state $Q=I_F\tau$ (charge-control model). For RF linearity, the charge must not follow the RF: $f\gg1/(2\pi\tau)$ (τ = 1 µs → ≫ 160 kHz) [3][4]. Thicker I-regions handle more reverse voltage and give lower $C_T$, but need more current for the same $R_s$ and switch more slowly.

**(c) Quarter-wave T/R switch.** A λ/4 line of $Z_0$ terminated in a short (the forward-biased shunt PIN, a few ohms) presents $Z_0^2/R_s$ — kilohms — at the junction, so the TX power continues to the antenna while the RX input, at the shorted end, is protected by the shunt isolation $20\log(1+Z_0/2R_s)$ (plus reflection). In RX both diodes are reverse biased: the series TX diode isolates the PA, and the shunt RX diode's small capacitance barely loads the line. Check B: TX IL 0.17 dB, TX→RX −34.3 dB, RX IL 0.01 dB at 434 MHz; TX IL is still ≤ 0.2 dB at ±10 %. At UHF the λ/4 line can be a lumped π (series L, shunt C) as in the Wilkinson page.

**(d) FET switch trade-off.** For a series FET switch, $IL\approx20\log(1+R_{on}/2Z_0)$ and isolation $\approx10\log[1+(1/2\omega C_{off}Z_0)^2]$. Scaling the device width by $m$ divides $R_{on}$ by $m$ and multiplies $C_{off}$ by $m$ — the product $R_{on}C_{off}$ is a process constant, the FoM. At 915 MHz: 150 fs with $R_{on}$ = 1 Ω → 0.086 dB, 21 dB; with 2 Ω → 0.17 dB, 27 dB (check C). Practical switches add shunt FETs on the off arm for isolation, like the PIN series-shunt arm. RF-SOI processes are ≈ 100–200 fs in production [8]; phase-change-material switches have demonstrated < 10 fs in research [9].

**(e) Attenuator derivation.** Require matched input with matched output: for a symmetric Pi, $R_{sh}\,\|\,(R_{se}+R_{sh}\|Z_0)=Z_0$, and voltage ratio $V_2/V_1=1/K$. Solving gives the TL;DR expressions (T is the dual). Power dissipation in a Pi pad fed with $P_{in}$: input shunt $P_{in}Z_0/R_{sh}$, series $(V_1-V_2)^2/R_{se}$, output shunt $V_2^2/R_{sh}$ — for 10 dB and 1 W: 519/329/52 mW, 100 mW to the load (check D2). Return-loss improvement: a reflection passes the pad twice, so $RL_{in}=RL_{load}+2A$.

**(f) Diode limiter.** A shunt anti-parallel diode pair across the line clamps each half-cycle at roughly the diode's turn-on voltage. With a Schottky pair, clamping begins near 0.2–0.3 V (−5 to 0 dBm in 50 Ω, since $P=V_{pk}^2/2R$ with the line at $Z_0/2$ seen by the diodes); beyond that the output rises slowly, set by the diode series resistance (check E: +20 dBm → +10 dBm). Because the diode conducts only on peaks, the limiter is also a mild distortion source below its knee (IIP3 ≈ +27 dBm in the model). A PIN limiter behaves differently: RF rectification builds charge in the I-region, which lowers its resistance until the line is shorted; flat leakage depends on I-region thickness (thin → lower leakage, faster turn-on; thick → higher power, lower capacitance), and a fast-rising pulse sees a brief "spike leakage" before the charge builds [6][7]. Two-stage designs (thick-I PIN first, thin-I PIN or Schottky second) combine high power handling with low flat leakage.

### Level 3 — practical and system-level issues
- **Linearity of switches:** PIN switches are very linear when $f\gg1/2\pi\tau$ and the bias current is large compared with RF current; FET switches generate harmonics/IMD from the nonlinear $C_{off}$ and body effects — SOI processes specify harmonics (e.g. 2f₀/3f₀ at +35 dBm) for cellular. For a LoRa T/R switch the key numbers are IP1dB (> PA output + margin) and harmonic generation (it sits after the harmonic filter in some designs!).
- **Switching time:** PIN: µs (charge removal); FET: 0.1–10 µs including logic; for TDD systems check both the switching time and any maximum toggle rate (PE4259 lists a 25 kHz maximum switching rate [5]).
- **Hot switching:** switching with RF applied can damage FET switches or cause transients; many parts specify a lower "hot-switch" power.
- **Termination:** reflective vs absorptive (terminated) switches — an absorptive switch presents 50 Ω on the off port, protecting a PA or keeping a VCO load constant.
- **DSAs** use cascaded switched Pi/T sections (e.g. 16, 8, 4, 2, 1, 0.5 dB): the PE4302 is 6-bit, 31.5 dB in 0.5 dB steps, DC–4 GHz (discontinued; PE4312 successor) [10]. Phase changes between states matter in phased arrays.

## Design equations & rules of thumb

| Quantity | Equation | Typical |
|---|---|---|
| Series element loss | $20\log\lvert1+Z/2Z_0\rvert$ | 1 Ω → 0.086 dB |
| Shunt element loss | $20\log\lvert1+Z_0/2Z\rvert$ | 1 Ω → 28.3 dB isolation |
| PIN resistance | $W^2/[(\mu_n+\mu_p)I_F\tau]$ | ohms at 10 mA |
| PIN linear operation | $f\gg1/(2\pi\tau)$ | τ 1 µs → ≫ 160 kHz |
| FET switch FoM | $R_{on}C_{off}$ | 80–250 fs (RF-SOI) |
| Voltage on an off switch | $V_{pk}=\sqrt{2PZ_0}$, ×2 into an open | 2 W: 14 V, up to 28 V |
| Pi pad | $R_{sh}=Z_0\frac{K+1}{K-1}$, $R_{se}=Z_0\frac{K^2-1}{2K}$ | 3 dB: 292/17.6; 6 dB: 150/37.4; 10 dB: 96.3/71.2; 20 dB: 61.1/248 |
| T pad | $R_{se}=Z_0\frac{K-1}{K+1}$, $R_{sh}=\frac{2Z_0K}{K^2-1}$ | 3 dB: 8.55/142; 6 dB: 16.6/66.9; 10 dB: 26.0/35.1; 20 dB: 40.9/10.1 |
| RL through a pad | $RL_{in}=RL_L+2A$ | 10 dB pad hides a short: RL 20 dB |
| Pad noise figure | NF = A (at 290 K) | |

## Worked examples

### Example 1 — T/R switching for a custom LoRa board
A Semtech SX1262 has separate RX (differential RFI) and TX (RFO) pins; boards combine them onto one antenna with an SPDT switch (EBYTE modules do this internally). Choosing an SPDT for +22 dBm (SX1262 native) or +30…+33 dBm (with an external PA):
- IP1dB ≥ PA output + ~3 dB: the PE4259 (IP1dB +33.5 dBm at 3 V, 0.35 dB IL and 30 dB isolation at 1 GHz, 10–3000 MHz, 2 kV HBM) [5] fits a +30 dBm system at 915 MHz with little margin; for 2 W at 433 MHz choose a higher-power switch or a PIN λ/4 design.
- Isolation 30 dB: with +30 dBm TX, ≈ 0 dBm leaks toward the (off) receiver — fine because the SX126x RX is off during TX, but check its absolute-maximum RF input.
- IL 0.35 dB appears in both TX (power) and RX (NF) paths.

### Example 2 — PIN λ/4 T/R switch for a 433 MHz 2 W ground-station transceiver
Series PIN in the TX line, shunt PIN λ/4 down the RX line (≈ 95 mm of 50 Ω microstrip on FR-4 with εeff ≈ 3.3, or a lumped π equivalent: series $L=Z_0/\omega$ = 18.3 nH with $C=1/(\omega Z_0)$ = 7.3 pF to ground at each end); bias both through RF chokes with ≈ 20–50 mA in TX, reverse-bias (−5 to −30 V for high power) in RX. With 1 Ω / 0.3 pF diodes: TX IL 0.17 dB, RX isolation 34 dB, RX IL 0.01 dB (check B). +33 dBm TX → ≈ −1 dBm at the RX port: add a limiter or ensure the LNA is also switched off/survives.

### Example 3 — Attenuator for measuring a 2 W transmitter with a NanoVNA/SDR
Goal: +33 dBm → ≤ −10 dBm (SDR front end): 43 dB. Use a 30 dB, ≥ 5 W coaxial attenuator first (its input resistor takes most of the power), then a 10 dB and 3 dB SMA pad. Never make the first stage a tiny SMD pad: a 10 dB Pi's input shunt resistor would take 52 % of 2 W (≈ 1 W) — far beyond an 0603's 0.1 W. For a board-level 10 dB pad at low power: 100 Ω / 68 Ω / 100 Ω (E24) gives 9.63 dB and 49.6 dB RL (check D).

### Example 4 — Protecting a GNSS LNA on a rocket with a 433 MHz 2 W transmitter
On the rocket, the 433 MHz antenna may be 0.3–1 m from the GNSS patch. With ≈ 20–30 dB of antenna-to-antenna isolation, +33 dBm TX can put +3 to +13 dBm into the GNSS LNA input — above a BGA524N6's 0 dBm absolute maximum [11]. Options, in order of preference: (1) a GNSS SAW **before** the LNA (a 1575 MHz SAW attenuates 433 MHz by tens of dB; costs ≈ 1.5–2 dB NF); (2) an LNA with a higher input rating; (3) a limiter — but the Schottky-pair example shows ≈ −0.5 dBm output at 0 dBm input and +4.7 dBm at +10 dBm: too soft to protect a 0 dBm part, and it adds loss and IMD. See [LNA design](lna-design.md#example-6--protect-the-lna-from-your-own-rocket).

### Example 5 — DSA in a receiver AGC or test chain
A 6-bit, 0.5 dB-step DSA (PE4302/PE4312 class, DC–4 GHz [10]) after the LNA gives 31.5 dB of gain control without degrading NF much (it comes after the gain) and without the distortion of a variable-gain amplifier. Each attenuation state has a slightly different phase and match; calibrate if used in an array.

## Practical notes
- **Bias networks for PIN switches** need RF chokes and DC blocks; the bias current (tens of mA) is significant for battery devices. The negative reverse bias must exceed the RF peak voltage to keep the diode off at high power.
- **Layout:** shunt elements need very low-inductance grounds (multiple vias) or isolation collapses; series elements' pads add capacitance that reduces isolation at GHz.
- **ESD:** FET/SOI switches at the antenna port are ESD-exposed; many include protection, but an external low-capacitance TVS or a shunt inductor to ground is common.
- **Attenuator resistors** at GHz: use thin-film, small-size parts; their parasitic capacitance changes high-value shunt arms; pads above ~20 dB in one section are sensitive to leakage around the pad — cascade sections and shield.
- **Limiter placement:** as close to the antenna as possible but after any DC path to ground (the diode must see the RF); its loss adds to NF directly.
- **Bench bring-up of switches and amplifiers** (safe test set-up): [17 bring-up playbook § G](../17-test-measurement/rf-bring-up-debug-playbook.md#g-amplifier-and-rf-switch-bring-up-failure-modes-and-a-safe-test-set-up).

## Common mistakes & misconceptions
- *"An off switch is an open circuit."* 0.3 pF is only 217 Ω at 2.45 GHz; isolation of simple series switches collapses at GHz.
- *"A PIN diode is a rectifier like any other diode."* Above ≈ 10/(2πτ) it is a bias-controlled linear resistor — that is its whole point.
- *"The switch's IP1dB is the PA power it can take."* Into a mismatched antenna the voltage can double; derate, and check hot-switching limits.
- *"Any attenuator will do for measuring a transmitter."* Power rating of the first resistor/element is what matters.
- *"Adding a 6 dB pad in front of an LNA fixes its input match"* — and adds 6 dB to the NF.
- *"Two back-to-back diodes protect any LNA."* They clamp softly (≈ 0.5 dB/dB above the knee in the model), add IMD, and may not meet a 0 dBm rating.
- *"Switch isolation = receiver protection."* Also consider leakage through the power supply, coupling on the PCB, and the LNA's own off-state rating.

## How to simulate / verify
- `tools/verify/rfckt_switches.py`: series/shunt element formulas vs nodal solver, series-shunt SPDT, quarter-wave T/R switch, FET FoM trade-off and stacking estimate, Pi/T attenuator equations (with E24 rounding and power split), time-domain anti-parallel Schottky limiter (compression curve and two-tone IIP3), PIN stored-charge resistance. Uses `tools/verify/rfckt_netsolve.py`.
- SPICE: PIN diode models with charge-control (e.g. vendor models) for transient/large-signal behaviour; harmonic balance for switch harmonics.
- Bench: VNA for IL/isolation per state; power sweep with a signal generator + amplifier and a power meter to find a limiter's flat leakage; a fast pulse to see spike leakage (oscilloscope with a detector).

## Open questions / gaps
- No measured PIN-limiter data (flat/spike leakage vs part) was obtained beyond the MACOM statement of ≈ +15 dBm flat leakage for one design [7]; a table of real limiter parts belongs in domain 18.
- The Schottky model parameters are generic HSMS-286x-class SPICE values, not a specific datasheet extraction.
- SX1262 RF-pin absolute-maximum input power not checked here (domain 15).

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — ch. 10 (PIN diodes and control circuits: series/shunt switches, λ/4 switches); ch. 4 (two-port loss formulas). (textbook)
2. Attenuator Pi/T design equations as in standard references, e.g. *Reference Data for Engineers*, 9th ed., Newnes, 2002, ch. on attenuators; re-derived here. (handbook)
3. G. Hiller, *Design with PIN Diodes*, Alpha Industries (Skyworks) application note APN1002; Microsemi/Unitrode, *The PIN Diode Circuit Designers' Handbook*, 1998 — stored-charge resistance, switch and limiter design. (app notes)
4. S. M. Sze, K. K. Ng, *Physics of Semiconductor Devices*, 3rd ed., Wiley, 2007 — p-i-n diode high-injection conductivity, charge control. (textbook)
5. pSemi, *PE4259 UltraCMOS SPDT RF Switch, 10–3000 MHz* data sheet DOC-03694: 0.35 dB IL/30 dB isolation at 1 GHz, IP1dB +33.5 dBm at 3 V, 25 kHz max switching rate, 2 kV HBM. https://www.psemi.com/pdf/datasheets/pe4259ds.pdf (datasheet; via vendor summary)
6. PIN diode limiter spike leakage, recovery time and damage — IEEE conference paper (IEEE Xplore document 22029); patent literature on multi-I-region limiters (thin I for low flat leakage, thick I for power). (peer-reviewed / patent; summary level)
7. MACOM silicon PIN limiter diodes (e.g. MA4L062-134; limiter modules LM-series): design with flat leakage ≈ +15 dBm typical and spike leakage ≈ 0.5 erg. https://www.macom.com/products/product-detail/MA4L062-134 (datasheet/vendor)
8. pSemi, "What is Ron Coff?" (FoM definition); Marki Microwave, "Why SOI?"; industry reports of RF-SOI Ron·Coff decreasing from > 300 fs to < 200 fs and research sub-120 fs (130 nm RF-SOI). (app notes / conference)
9. Tower Semiconductor press release, 3 Aug 2020 — RF switch technology with Ron×Coff < 10 fs (phase-change material). (press release — treat as vendor claim)
10. pSemi PE4302 (6-bit, 31.5 dB, 0.5 dB steps, DC–4 GHz; discontinued) and PE4312 data sheets. (datasheet)
11. Infineon, *BGA524N6* data sheet rev. 3.5 (RF input absolute maximum 0 dBm). (datasheet)
