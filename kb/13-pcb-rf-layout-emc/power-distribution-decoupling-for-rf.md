---
title: Power distribution and decoupling for RF — target impedance, anti-resonances, bead + capacitor filters, PA burst current, supply isolation for PAs/VCOs/LNAs, star vs daisy-chain feeding
domain: 13-pcb-rf-layout-emc
slug: power-distribution-decoupling-for-rf
tags: [PDN, power-integrity, target-impedance, decoupling, anti-resonance, ESL, plane-capacitance, ferrite-bead, LC-filter, peaking, damping, LDO, PSRR, buck, ripple, VCO-pushing, spur, PA-burst, droop, brown-out, LoRa-module, E22-400T33D, star-feed, ground-bounce]
prerequisites:
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
  - ../04-real-components-hf/ferrites-and-beads.md
  - grounding-and-return-paths.md
related:
  - mixed-signal-layout.md
  - emc-emi-fundamentals.md
  - thermal-management-rf.md
  - rf-layout-rules.md
  - ../05-analog-electronics/power-supplies-for-rf-and-analog.md
  - ../07-noise-linearity/phase-noise-and-jitter.md
  - ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md
level: mixed
confidence: medium
last_updated: 2026-10-02
---

# Power distribution and decoupling for RF

## Questions this page answers
- What is "target impedance", and what does it mean for a 2 W LoRa module's supply?
- Why can adding a 100 pF "RF capacitor" next to a 100 nF make decoupling worse at UHF?
- Why does my ferrite bead + capacitor supply filter amplify noise at some frequency, and how do I damp it?
- How much bulk capacitance does an EBYTE E22-400T33D need so its 1.2 A TX bursts don't brown out the board?
- Should the PA, LNA and VCO share a supply trace, or be fed in a star?
- How much supply ripple can a VCO or PLL tolerate before it shows spurs?
- How do I filter a buck converter's ripple for an RF front end?

## TL;DR
- **Target impedance** $Z_t=\Delta V_{allowed}/\Delta I$: the 5 V rail of a 2 W LoRa module (1.2 A burst, 5 % ripple) needs **≈ 0.21 Ω**; an SX1262's 3.3 V VBAT at +22 dBm (118 mA, 3 %) ≈ 0.84 Ω; an ESP32-S3's Wi-Fi bursts ≈ 0.28 Ω; a GNSS module (30 mA, 1 %) ≈ 1.1 Ω (script §1). These must hold from DC up to the bandwidth of the load's current steps (µs edges → ≈ 1 MHz); above that, local decoupling only needs to serve the IC's own fast currents.
- **Anti-resonance**: 22 µF + 100 nF + 100 pF (ESL 1.0/0.5/0.4 nH) has a **≈ 14 Ω peak at ≈ 590 MHz** and is **worse at 433 MHz (1.4 Ω) than 22 µF + 2 × 100 nF (0.54 Ω)** (script §2). At UHF what decouples is the lowest-inductance path (short mounting, via-in-pad, an L2/L3 plane pair), not the capacitance value. Mixed values need their anti-resonances checked ([capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md)).
- **Bead + cap filters resonate**: a bead's low-frequency inductance (≈ 1 µH) with 10 µF of MLCC resonates at ≈ 50 kHz with **+15 dB of peaking** (1 µF: +25 dB at 160 kHz) — right where buck converters and PA burst envelopes put energy. **Damp** with ≈ $\sqrt{L/C}$ (0.3 Ω) of ESR in the bulk branch (polymer/tantalum, or a series resistor): peak drops to +2 dB (script §3).
- **PA bursts**: a 1.2 A step on 5 V with a regulator that needs ≈ 50 µs to respond droops by $I\cdot ESR+L\,dI/dt+I\,t_{resp}/C$ — **≥ ≈ 265 µF of low-ESR bulk at the module** keeps it under 5 %; 22 µF alone droops ≈ 55 % (script §4). EBYTE asks for ≥ 30 % supply margin and low ripple [1].
- **Feed PA and sensitive rails in a star from the bulk/plane**: a 20 mm × 1 mm shared trace couples a ≈ 14 mV step into an LNA/VCO rail during a PA burst; a star from the bulk cap ≈ 7 mV; plane-fed with local caps ≈ 1 mV (script §5).
- **VCO pushing**: ripple $V_r$ at $f_m$ on a VCO with pushing $K_p$ (Hz/V) gives FM sidebands at $20\log(K_pV_r/2f_m)$ dBc — 1 mV of 1 MHz ripple on a 2 MHz/V VCO = −60 dBc; low-frequency ripple is worse (50 kHz: −34 dBc) (script §6). A buck → RF LDO (≈ 40 dB PSRR at 1 MHz) → bead + cap (≈ 30 dB) chain takes 20 mV of ripple to ≈ 6 µV.

## Intuition (no math)
An RF chip draws current in pulses — a PA switching on for a LoRa packet, a VCO and PLL charge pump, a digital core clocking. The supply has to deliver those pulses without its voltage moving, and it can only do that if the impedance looking back into the supply, *from the chip's pins*, is low at every frequency the pulses contain. The regulator handles slow changes (its feedback loop is fast only up to tens of kHz); bulk capacitors handle the next decade or two; small ceramic capacitors close to the pins handle MHz; and above ≈ 100 MHz only the **inductance of the mounting** (pads, vias, the distance to the plane) and the **capacitance of the planes themselves** matter. Each stage hands over to the next — and where the hand-over is clumsy (one capacitor has turned inductive while the next is still capacitive) the network has a **parallel resonance**, an impedance peak.

For RF circuits there is a second job: **keeping noise out**. A supply rail is a wire that connects the PA, the LNA, the synthesiser and the MCU. Ripple from a buck converter, or the voltage step that a PA burst creates on a shared trace, modulates the oscillator (spurs, phase noise), the LNA gain (AM), or the PA output (spectral regrowth). Filtering (LDO + LC/bead stages) and **topology** (star feeding, separate regulators, solid planes) are the tools.

The classic trap is the **ferrite bead**. Below its resistive range a bead is just an inductor; together with the decoupling capacitor after it, it forms an LC low-pass filter with a resonance — and an *undamped* LC amplifies noise at its resonance. That resonance often sits at tens to hundreds of kHz, exactly where a switching converter's ripple and a LoRa packet's envelope live.

## The math

### Level 1 — target impedance and droop
$$Z_t=\frac{\Delta V_{allowed}}{\Delta I_{step}}\qquad\text{(e.g. }0.05\times5\text{ V}/1.2\text{ A}=0.21\ \Omega).$$
For a step $\Delta I$ with rise time $t_r$ into a node held up by bulk capacitance $C$ (ESR $R$, mounting/trace inductance $L$) until the regulator responds after $t_{resp}$:
$$\Delta V\approx\Delta I\,R+L\frac{\Delta I}{t_r}+\frac{\Delta I\,t_{resp}}{C}.$$
Script §4: with 30 nH of trace, 1.2 A in 2–10 µs:

| Bulk | ESR | t_resp 10 µs | t_resp 50 µs |
|---|---|---|---|
| 22 µF MLCC | 5 mΩ | 0.57 V (11 %) | 2.75 V (55 %) |
| 100 µF | 20 mΩ | 0.16 V (3 %) | 0.64 V (13 %) |
| 220 µF | 30 mΩ | 0.11 V (2 %) | 0.33 V (6.5 %) |
| 470 µF | 40 mΩ | 0.09 V (2 %) | 0.19 V (4 %) |

The response time is the regulator's (buck-boost converters on a 1S cell are often slow: tens of µs); the bulk must bridge it.

### Level 2 — anti-resonance and plane capacitance
Each capacitor is $Z=R+j\omega L+1/(j\omega C)$ with self-resonance $1/(2\pi\sqrt{LC})$. In parallel, between two SRFs one branch is inductive and the other capacitive → parallel resonance; with equal ESL $L$, $\omega_{ar}^2\approx(1/C_1+1/C_2)/(2L)$ and the peak height ≈ $X^2/(R_1+R_2)$ — large when ESRs are small ([04 capacitors page](../04-real-components-hf/capacitors-at-rf-mlcc.md)). Script §2:

| Bank | 10 MHz | 100 MHz | 433 MHz | 915 MHz | peaks |
|---|---|---|---|---|---|
| 22 µF + 100 nF + 100 pF | 115 mΩ | 205 mΩ | 1.39 Ω | 0.44 Ω | 0.27 Ω @ 13 MHz, **13.9 Ω @ 587 MHz** |
| 22 µF + 2 × 100 nF | 267 mΩ | 121 mΩ | 0.54 Ω | 1.15 Ω | 0.27 Ω @ 10 MHz |

So the 100 pF part helps near its own SRF (≈ 800 MHz–1 GHz) but *hurts* below it. Above a few hundred MHz the best decoupling is a **plane pair**: $C_{plane}=\varepsilon_0\varepsilon_rA/h$ — for the 1.065 mm JLC core (εr 4.6) 3.8 pF/cm², for a 0.0994 mm 3313 prepreg (εr 4.1) 37 pF/cm² — i.e. a 50 × 50 mm L2/L3 pair across the core is only ≈ 96 pF — with almost no inductance, but with cavity resonances that must be damped ([cavity page](../02-electromagnetics/waveguides-and-cavity-resonators.md)). At UHF the chip's own on-die/package capacitance plus a small (0201/0402, 10–100 pF) capacitor with its ground via *in or at the pad* is what works; follow the reference design's values and placement (TI: power into the capacitor, then into the pin; one via per capacitor [2]).

### Level 3 — bead + capacitor filters, PSRR chains and pushing
**Bead filter.** Model the bead below its resistive region as $L_b$ (≈ 0.5–2 µH for 600 Ω@100 MHz parts) plus $R_{dc}$, and the capacitor after it as $C$ with ESR. The transfer function $H=Z_C/(Z_b+Z_C)$ has a resonance at $f_r=1/(2\pi\sqrt{L_bC})$ with peak ≈ $Q=\sqrt{L_b/C}/(R_{dc}+R_{ESR})$ (script §3):

| Bead (1 µH, 50 mΩ) + | f_r | Q | peak | at 1 MHz |
|---|---|---|---|---|
| 10 µF MLCC (3 mΩ) | 50 kHz | 6 | +15.5 dB | −52 dB |
| 10 µF + 0.3 Ω damping | 50 kHz | 0.9 | +2.4 dB | −26 dB |
| 1 µF MLCC | 159 kHz | 19 | +25.5 dB | −32 dB |

Damping costs high-frequency attenuation but removes the peak; put the damping resistance in a *separate* bulk branch (e.g. 10 µF MLCC ∥ [47 µF polymer, ESR 0.1–0.3 Ω]) so the MLCC keeps its HF performance. Beads also lose inductance with DC bias (check the saturation curve at the PA's current) ([ferrites and beads](../04-real-components-hf/ferrites-and-beads.md)).

**Supply noise into a VCO.** A VCO with supply pushing $K_p$ (Hz/V) driven by ripple $V_r\cos(2\pi f_mt)$ is frequency-modulated with index $\beta=K_pV_r/f_m$; for $\beta\ll1$ each sideband is $20\log(\beta/2)$ dBc. With $K_p$ = 0.2/2/20 MHz/V (well-regulated integrated VCO … bare discrete VCO; assumed range) and 1 mV at 1 MHz: −80/−60/−40 dBc; at 50 kHz the same ripple is 26 dB worse (script §6). Inside a PLL loop bandwidth the loop suppresses this; outside it does not ([phase noise](../07-noise-linearity/phase-noise-and-jitter.md)).

**Filter chain.** Buck ripple (≈ 10–50 mV at 0.5–2 MHz) → RF LDO (PSRR ≈ 40–60 dB at 1 MHz for RF-grade parts; many generic LDOs have < 20 dB there) → bead + damped cap (≈ 30 dB): 20 mV → ≈ 6 µV (script §6).

## Design equations & rules of thumb

| Item | Equation / value | Notes |
|---|---|---|
| Target impedance | $Z_t=\Delta V/\Delta I$ | E22 5 V rail ≈ 0.2 Ω |
| Burst droop | $IR+L\,dI/dt+It_{resp}/C$ | ≥ 250 µF low-ESR bulk at a 2 W module |
| Capacitor SRF | $1/(2\pi\sqrt{LC})$ | 100 nF/0.5 nH: 22 MHz; 100 pF/0.4 nH: 800 MHz |
| Anti-resonance (equal L) | $\omega^2=(1/C_1+1/C_2)/(2L)$ | 100 nF ∥ 100 pF ≈ 0.5–0.6 GHz |
| Plane capacitance | $\varepsilon_0\varepsilon_rA/h$ | 3.8 pF/cm² (1.065 mm core), 37 pF/cm² (0.0994 mm) |
| Bead + C resonance | $1/(2\pi\sqrt{L_bC})$, peak ≈ Q | damp with $R\approx\sqrt{L_b/C}$ |
| VCO pushing spur | $20\log(K_pV_r/2f_m)$ dBc | 2 MHz/V, 1 mV, 1 MHz → −60 dBc |
| Feeding topology | star from bulk/plane; separate LDO for VCO/LNA | §5 |

## Worked examples

### 1. Supplying an EBYTE E22-400T33D (433 MHz, 2 W) from a 2S pack
TX current 0.85–1.2 A at 5 V, burst rise of a few µs ([LoRa modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)). Design: a 5 V buck rated ≥ 2–3 A (EBYTE: ≥ 30 % margin [1]); at the module pins **≥ 220–330 µF low-ESR polymer + 22 µF MLCC + 100 nF**, connected by a wide pour (≤ 10 nH to the module) and many GND vias; the module's GND tied to L2. Check with a scope at the module pins during a 1 s packet: droop < 250 mV, no regulator oscillation. If the buck is shared with the rest of the board, put a damped bead/LC between the module branch and everything else so the burst doesn't step the 5 V that feeds sensors. Undersizing this is the "module resets mid-packet / AUX stuck low" failure mode.

### 2. SX1262 on a 3.3 V rail shared with an ESP32-S3
Chip-down LoRa at +22 dBm: ≈ 118 mA during TX (Semtech ref. design [3]); ESP32-S3 Wi-Fi bursts ≈ 0.3–0.35 A. Both on one 3.3 V buck: give the SX1262 its own branch from the bulk capacitor (star), a bead + 4.7–10 µF (damped by a polymer or 1 Ω in a parallel branch) and the reference-design decoupling at VBAT/VR_PA (Semtech's AN1200.66 shows 47 pF + 47 nF on VR_PA [4]); keep the DC-DC inductor of the SX1262 (DCC_SW) close to its pin and away from the RF path.

### 3. A GNSS LNA bias-T fed from a noisy 3.3 V
An active GNSS antenna takes 3.3 V through the coax via an inductor (bias-T). Buck ripple at 1 MHz and its harmonics modulate the LNA; switching edges at hundreds of MHz radiate from the coax. Feed the bias-T from an LDO (or the GNSS module's own antenna-supply output), add a 10 Ω + 1 µF RC or a bead + cap before the bias inductor, and put the bias-T's RF choke (e.g. 47–100 nH, SRF well above 1.6 GHz) and DC-block close to the module ([GNSS antennas](../08-antennas/gnss-antennas.md)).

### 4. Why the magnetometer offset correlated with flight-loop activity
The Space Bar primary FC's magnetometer showed a periodic offset; the suspected cause was a sensor sharing the processor's regulator with no supply filtering (lessons file). The PDN view: the processor's current steps × the shared regulator's output impedance at the step frequencies → ripple on the magnetometer supply → offset. Fix in the next board: dedicated LDO for sensors, star-fed from the battery-side bulk, bead + damped cap at each sensor, and the sensor's own ground returning to the plane next to it, not through the MCU's return path.

## Practical notes
- **Placement order for decoupling**: smallest value / lowest ESL closest to the pin, with its ground via at its pad (via-in-pad if possible); route power *into* the capacitor pad, then to the IC pin [2].
- **Use the planes**: on a 4-layer board with L2 GND, use L3 as a power pour under the RF/ IC region (thin prepreg between L3 and L4 if the stackup allows) and stitch decoupling vias directly into it.
- **Don't blindly add "RF caps"** (10/100 pF) to every rail — check for anti-resonances in the band you care about; same-value parallel caps are safe.
- **Beads**: choose by impedance *at the noise frequency* and DC-bias derating; avoid beads in PA supply lines at full current unless the vendor curve says L holds at that current.
- **Regulator stability**: LDOs and bucks have ESR/C windows for stability; very-low-ESR MLCC banks can make some LDOs ring — check the datasheet.
- **Brown-out**: set MCU brown-out thresholds and sequence the radio after the rails settle; log brown-out resets in flight software.
- **Measure**: scope (short ground spring) at the pins during a TX burst; spectrum analyser with a DC-block on the rail for ripple spectra; VNA "two-port shunt-thru" for PDN impedance down to mΩ ([test & measurement](../17-test-measurement/_index.md)).

## Common mistakes & misconceptions
- **"More capacitor values = broader decoupling."** Mixed values create anti-resonance peaks; at UHF the value hardly matters, the mounting does.
- **Bead + MLCC without damping** — a 15–25 dB peak at 50–200 kHz.
- **22 µF at a 2 W module** — browns out on every packet.
- **Daisy-chaining the VCO/LNA supply after the PA.**
- **Assuming an LDO removes MHz ripple** — PSRR falls with frequency; many LDOs have < 20 dB at 1 MHz.
- **Thermal-relief connections on decoupling capacitor pads** — added inductance.

## How to simulate / verify
- `python3 tools/verify/pcb_pdn.py` (instant): target impedances, decoupling-bank |Z(f)| with anti-resonance search, bead + cap peaking and damping, burst droop table, star vs daisy-chain coupling, VCO-pushing spurs and filter chain.
- Vendor tools for real parts: Murata SimSurfing / TDK SEAT / KEMET K-SIM (capacitor and bead S-parameters with DC bias); LTspice/ngspice with the regulator model for burst transients ([SPICE](../16-simulation-tools/spice-circuit-simulation.md)).
- Bench: burst-load test (MOSFET + resistor driven by a function generator) before connecting the radio.

## Open questions / gaps
- VCO pushing figures (0.2–20 MHz/V) are an assumed range; datasheet values for the SX126x synthesiser and GNSS LO are not published as such — measure spur vs injected ripple if needed.
- Regulator response times (10–50 µs) are typical, not for a specific part; take the actual load-transient plot from the chosen regulator datasheet.
- ADI MT-101 (decoupling techniques) could not be fetched (timeout); rules here follow TI SWRA640 and the KB's capacitor page.

## Sources
1. EBYTE, E22-400T33D and E220-900T30D user manuals — TX current 0.85–1.2 A (E22) and 620 mA (E220), supply 3.3–5.5 V (≥ 5 V for full power on E220), ≥ 30 % supply margin, low ripple, no traces under the module (as summarised in [LoRa modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)). (datasheet)
2. Texas Instruments, SWRA640H (2024) §3.1.6, §4.5, §4.8 — decoupling capacitor placement (same layer, power into the cap first, one via per cap), DC/DC component placement and short ground. (app note)
3. Semtech, AN1200.40 *SX1261/2 Reference Design Explanation* (2018) — E449 +22 dBm ≈ 118 mA at 3.3 V; LDO vs DC-DC trade-off. (app note)
4. Semtech, AN1200.66 *PCB Design Guidelines for LR11xx & SX126x* — VR_PA decoupling 47 pF + 47 nF (search summary only). (app note)
5. E. Bogatin, *Signal and Power Integrity — Simplified*, 3rd ed., 2018, ch. 13–14 (PDN, target impedance, plane capacitance, anti-resonance). (textbook; from knowledge)
6. B. Archambeault, *PCB Design for Real-World EMI Control*, Kluwer 2002 — decoupling effectiveness, mixed-value banks (as cited on the 04 capacitors page). (textbook)
7. H. W. Ott, *Electromagnetic Compatibility Engineering*, 2009, ch. 11 (digital circuit power distribution). (textbook; from knowledge)
8. Space Bar avionics knowledge base, flight-computer design lessons (magnetometer offset with shared regulator, no supply filtering). (internal)
9. Verification script `tools/verify/pcb_pdn.py` (this page).
