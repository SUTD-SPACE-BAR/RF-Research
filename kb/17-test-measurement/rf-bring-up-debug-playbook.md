---
title: RF board bring-up and debug playbook — step-by-step bring-up of a new radio/GNSS board (power, clocks, conducted TX, RX sensitivity, antenna match, OTA, integration) with symptom → cause → test tables, stage-by-stage receiver signal tracing and IF alignment, and amplifier/RF-switch failure modes with a safe test set-up
domain: 17-test-measurement
slug: rf-bring-up-debug-playbook
tags: [bring-up, debug, playbook, lora, e22, sx1262, sx1278, gnss, zed-f9p, tx-power, harmonics, sensitivity, desense, self-interference, antenna, matching, range, troubleshooting, checklist, pre-registration]
prerequisites: [vna-fundamentals-calibration.md, spectrum-analyzers.md, rf-power-measurement.md]
related: [basic-bench-instruments.md, bench-measurement-recipes.md, ../06-rf-circuits/receiver-architectures.md, ../06-rf-circuits/amplifier-stability-and-biasing.md, ../06-rf-circuits/rf-switches-attenuators-limiters.md, ../19-regulations-safety/lab-safety-esd-high-power.md, nanovna-librevna-practical.md, noise-figure-measurement.md, antenna-range-ota-testing.md, oscilloscopes-and-probing-for-rf.md, fixtures-and-deembedding.md, sdr-as-test-equipment.md, signal-generators-and-sources.md, lab-setup-by-budget.md, ../13-pcb-rf-layout-emc/rf-pcb-review-checklist.md, ../13-pcb-rf-layout-emc/mixed-signal-layout.md, ../15-lora-ism-radios/rocket-telemetry-radio-design.md, ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md, ../08-antennas/gnss-antennas.md, ../09-propagation-link-budget/link-budget-methodology.md]
level: intermediate
confidence: medium
last_updated: 2026-10-13
---

# RF board bring-up and debug playbook

## Questions this page answers
- In what order should I bring up a new LoRa/GNSS flight board so that a fault is found at the cheapest step?
- What should I measure, with which instrument, and what are the pass criteria?
- My telemetry range is 10× shorter than the link budget — what do I check first?
- GNSS loses fix only when the flight computer is running — how do I find the culprit?
- The radio resets or drops packets when transmitting — why?
- How do I prove the fix worked?
- How do I trace a weak signal stage by stage through a receiver, and what level should I see at each stage?
- How do I align the IF of a superhet, and why does peaking the IF cans seem to do nothing?
- How do I know my SDR's LNA is actually working?
- Why do amplifiers and RF switches die on the bench, and how do I set up a safe test?
- Why do people split 40 dB of gain into two stages with a pad between them?

## TL;DR
- **Order**: plan & pre-register → inspect → power (current-limited) → clocks/PLL lock → conducted TX (into pads: power, frequency, OBW, harmonics, droop) → conducted RX (sensitivity with step attenuator, RSSI calibration) → antenna match in situ (VNA) → self-interference (desense with every subsystem on/off, one at a time) → OTA (near-field sniff, attenuation range test, drone test) → repeated battery power-up trials.
- **Measure conducted before radiated**: a conducted test isolates the radio from the antenna and propagation; almost every "bad range" is resolved by one of: wrong/detuned antenna, low TX power (brown-out, wrong register/module variant), cable/connector loss, receiver desense, wrong radio settings, or an unrealistic ground-level test.
- **Translate symptoms into dB**: "range 10× short" = 20 dB missing in free space (40 dB under ground-level d⁴ propagation); 3× = 9.5 dB; 2× = 6 dB. Desense by interference at the noise floor = 3 dB, 10 dB above it = 10.4 dB.
- **Protect the instruments**: the flown EBYTE E22-400T33D is a **2 W (33 dBm)** module — use ≥ 40 dB of attenuation (first pad ≥ 5 W) before a tinySA, and never key it into an open or a VNA port.
- **Receiver tracing** (§F): predict signal and noise at every node, then inject back-to-front (or measure front-to-back with a Z0 probe); a working 433 MHz superhet keeps ≈ 30 dB SNR in 10 kHz from the LNA onward for −100 dBm in. Align IF cans with the signal **below the limiter/AGC threshold**, or nothing appears to change. An SDR's floor should rise ≈ 15 dB when its LNA is switched in.
- **Amplifiers and switches** (§G): check DC current before RF, look for oscillation with the ports terminated, DC-block every instrument, pad the input (a bare NanoVNA at −13 dBm drives a BGA524N6 3 dB past IP1dB), never hot-switch at high power, and keep any one shielded section ≤ 20–30 dB of gain (40 dB with −50 dB coupling already ripples 5.7 dB).
- **One variable per test**, pass criteria written *before* measuring, every run logged with a config line (module, firmware, SF/BW/CR, power setting, pads, instrument settings) — the team's standing tenets [9].

## Intuition (no math)
An RF chain fails in one of a handful of ways: it doesn't make the power it should, the power doesn't get to the antenna, the antenna doesn't radiate it in the right direction, the receiver is deaf because something on the same board is shouting in its band, or the two ends aren't speaking the same language (settings, frequency). Bring-up is organised so that each step removes one of those possibilities with a measurement whose answer you already predicted. Start with the least integrated configuration (a radio into a dummy load on a bench supply) and add one thing at a time, so the step at which the numbers go wrong points at the cause.

## The math
### Level 1 — the numbers you need
- Link shortfall: ΔdB = 20 log N (free space) or 40 log N (beyond the two-ray breakpoint), N = expected/observed range (script §1).
- Desense: sensitivity loss = 10 log(1 + 10^{X/10}), X = in-band interference relative to the receiver noise floor (script §2).
- Frequency error: Δf = f·ppm·10⁻⁶ (10 ppm at 915 MHz = 9.15 kHz, 7.3 % of a 125 kHz LoRa channel; 20 ppm at 433 MHz = 8.7 kHz) (script §3).
- Receiver NF from sensitivity: NF = S + 174 − 10 log BW − SNR_req ([noise-figure page](noise-figure-measurement.md)).
- Supply droop: ΔV = I·(R_source + ESR); bridging capacitance C ≥ I·t/ΔV (1 A for 100 µs within 100 mV → 1 000 µF) (script §5).

### Level 2 — the link-budget identity used for diagnosis
P_rx = P_tx − L_cable,tx + G_tx(θ, φ) − PL(d) − L_pol + G_rx − L_cable,rx; margin = P_rx − S_eff, with S_eff = S_cond + desense. Every term is separately measurable: P_tx (power meter, conducted), L_cable (VNA S21), G(θ, φ) (range, relative), L_pol (rotate an antenna), S_eff (conducted sensitivity with the whole system running). A shortfall is found by measuring terms until the sum matches the observation — not by guessing ([link budget](../09-propagation-link-budget/link-budget-methodology.md)).

### Level 3 — self-interference arithmetic
A clock or switching harmonic at the receive frequency of −130 dBm (in the LoRa channel) against a receiver noise floor of −174 + 6 + 51 = −117 dBm (NF 6 dB, 125 kHz) is 13 dB below the floor → 0.2 dB desense; at −110 dBm it is 7 dB above → 7.8 dB lost. For GNSS (signals at ≈ −130 dBm, below the noise), any spur near 1575.42 MHz above ≈ −150 dBm in the 2 MHz band shows up as lost C/N₀ on the ZED-F9P/MAX-M10S. Harmonic candidates (script §6): at 433.175 MHz the 9th harmonic of 48 MHz (USB), 18th of 24 MHz, 27th of 16 MHz, 36th of 12 MHz and 54th of 8 MHz all land on 432.0 MHz (within 1.2 MHz); across 902–928 MHz dozens land (e.g. 40 MHz ×23 = 920 MHz, 48 MHz ×19 = 912 MHz, 25 MHz ×37 = 925 MHz); near L1, 25 MHz ×63 = 1575.0 MHz and 8 MHz ×197 = 1576 MHz.

## Design equations & rules of thumb

| Quantity | Rule | Example |
|---|---|---|
| Range shortfall → dB | 20 log N (free space), 40 log N (ground-level d⁴) | 10× short = 20 dB / 40 dB |
| Desense | 10 log(1 + 10^{X/10}) | interference at the floor = 3.0 dB; +10 dB → 10.4 dB |
| Frequency error | f · ppm · 10⁻⁶ | 10 ppm @ 915 MHz = 9.15 kHz |
| Pads for a 2 W radio | ≥ 43 dB before a tinySA; first pad ≥ 5 W | E22-400T33D |
| TX burst droop | ΔV = I(R + ESR); C ≥ I·t/ΔV | 1 A, 100 µs, 100 mV → 1 000 µF |
| Desense pass criterion | ≤ 1–2 dB with all subsystems on | pre-register your own |
| Antenna pass criterion | RL ≥ 10 dB across used channels, in the final structure | touch test passes |

## Step-by-step bring-up

| Step | Configuration | Measure | Instrument | Typical pass criterion (pre-register your own) |
|---|---|---|---|---|
| 0. Plan | — | write the test plan: predicted values & limits | — | limits fixed before any measurement [9] |
| 1. Inspect | unpowered | module variant (E22-**400** vs **900**, T22 vs T33), orientation, U.FL fully clicked, matching parts populated as designed, DNP positions, solder under module shield | microscope, BOM | matches the as-ordered BOM (documentation drift is a known team failure [8]) |
| 2. Power | bench supply, current limit ~1.5× expected | idle current per rail; rail noise (20 MHz BW limit, spring ground); TX burst current and droop | supply, scope, current probe/shunt | idle within ±20 % of prediction; droop during TX < regulator/module spec |
| 3. Clocks | powered, radio idle | TCXO/crystal frequency; PLL lock flag; CW frequency error | SA locked to GPSDO, register read | error within the radio's allowance (e.g. ≤ ±10 ppm → ±4.3 kHz at 433 MHz) |
| 4. Conducted TX | radio → pads (≥ 40 dB for 2 W) → SA/power meter | power at each setting; OBW; 2f/3f/spurious; power vs time (thermal droop over 60 s) | power meter, SA (zero span + channel power), scope on TX-enable | power ±1 dB of setting; harmonics below the regulatory limit with margin; OBW inside the channel |
| 5. Conducted RX | generator/2nd radio → pads → step attenuator → DUT, shielded | PER vs level; RSSI vs known level; sensitivity at the flight settings | step attenuator, shielded boxes, packet counter | within ~2 dB of datasheet (SX1262 SF7/125 kHz: −124 dBm at 1 % PER, 64-byte payload [7]) |
| 6. Antenna | antenna on the flight structure, VNA at the feed | S11 in situ, resonance, bandwidth; touch test | NanoVNA/LiteVNA with chokes | RL ≥ 10 dB (VSWR ≤ 2) across the used channels in the final enclosure |
| 7. Self-interference | whole avionics running, radio RX (or GNSS) | noise floor/RSSI with antenna replaced by 50 Ω load and with antenna; GNSS C/N₀; toggle each subsystem | SDR/SA + near-field probes; GNSS u-center logs | desense ≤ 1–2 dB with everything on |
| 8. OTA | full system | near-field sniff of spurs; attenuation range test; drone/kite test with flight orientation | H-loop + SA; step attenuator; ground station logs | margin at max flight range ≥ your fade + null + roll allowance (see [antenna range](antenna-range-ota-testing.md)) |
| 9. Robustness | battery power, repeated cycles | N power-ups on **battery**, not just USB; TX/RX at temperature extremes | logs | e.g. 22/22 clean power-ups [10] |

## Symptom → cause → test tables

### A. "Range is 10× shorter than expected" (≈ 20 dB missing in free space)

| Likely cause | How big | Test that decides it |
|---|---|---|
| Test geometry (both ends near the ground, blocked Fresnel zone) | 20–50 dB | two-ray/Fresnel check; repeat with a mast or drone ([antenna range](antenna-range-ota-testing.md)) |
| Antenna detuned by airframe/enclosure, or wrong-band antenna (433 whip on a 915 module) | 3–20 dB | VNA S11 in situ at the used frequency |
| Connector not mated / damaged U.FL / wrong cable | 3–30 dB | VNA S21 or TDR of the cable; wiggle test |
| Low TX power: brown-out on burst, wrong power register, wrong module variant, PA damaged by open-antenna TX | 3–20 dB | conducted power with a power meter at each setting; scope on supply during TX |
| Receiver desense (clock harmonics, switcher, SD card, Wi-Fi/BLE of the ESP32) | 3–30 dB | RSSI noise floor with RX antenna replaced by a 50 Ω load, subsystems toggled one at a time |
| Polarization mismatch/roll (linear–linear) | 3–20+ dB | rotate one antenna 90° at a fixed point; compare |
| Radio settings mismatch (SF, BW, CR, sync word, CRC, LDRO, IQ inversion, preamble) | total failure / intermittent | conducted test with both ends at known-good settings; print a boot config line |
| Frequency offset (cold TCXO/crystal, wrong XO load caps) | intermittent at high SF | CW frequency error vs temperature on an SA with GPSDO |
| Cable loss at the ground station (long RG-58 at 915 MHz) | 3–10 dB | VNA S21; move the LNA to the antenna |
| Interference at the launch site (other teams on 433 MHz) | variable | SDR waterfall recording at the site before/while flying |

### B. GNSS problems (no fix, low C/N₀, fix lost when something turns on)

| Likely cause | Test |
|---|---|
| Active antenna not powered (bias missing/short) | DC voltage at the antenna port; current draw ~10–30 mA |
| Board clocks/regulators radiating near 1575.42 MHz (e.g. 25 MHz ×63 = 1575.0 MHz) | C/N₀ with subsystems toggled; SA + near-field probe at 1575 MHz with a preamp |
| LoRa TX desensing GNSS (blocking/intermod from 433/915 MHz, especially 2 W) | C/N₀ and jamming indicator with LoRa TX on/off; add a GNSS SAW filter or a notch at the LoRa frequency |
| LNA oscillation in an active antenna or on-board LNA | SA sweep with antenna terminated; look for a line that moves with supply voltage |
| Ground plane/antenna placement (patch on a small ground, near the airframe wall) | C/N₀ vs a reference antenna on a large ground plane ([GNSS antennas](../08-antennas/gnss-antennas.md)) |
| Bench artefact: indoor, no sky view | test outside; the team's bench practice already notes indoor fix cadence must be forced [10] |

### C. Radio resets, locks up or drops packets while transmitting

| Likely cause | Test |
|---|---|
| Supply droop / ground bounce on TX burst (2 W modules draw large bursts) | scope on the module supply and MCU rail during TX (spring ground!); try a bigger local bulk capacitor |
| RF coupling into MCU reset/SPI/UART lines (worse with the antenna close to the board) | compare antenna vs dummy load; ferrite/RC filter on reset; near-field probe on the lines |
| Thermal: PA heating over long packets or high duty cycle | power and current vs time over 60 s; IR thermometer |
| UART/SPI timing to the module (E22 AUX pin handshake) | logic analyser on AUX/TX/RX during bursts |
| USB vs battery behaviour differs | repeat on battery; the team saw a GPS-UART failure only on battery power-ups (3/11) [10] |

### D. Harmonics or spurious emissions too high
Pass criterion for a Singapore licence-exempt SRD (IMDA TS SRD Table 1-a, ITU-R SM.329 Category B): spurious/harmonics ≤ −36 dBm below 1 GHz (≤ −54 dBm inside 47–74, 87.5–118, 174–230 and 470–862 MHz) and ≤ −30 dBm from 1 GHz up — e.g. a 433 MHz transmitter at 10 dBm needs 2f (866 MHz) ≥ 46 dBc and 3f (1299 MHz) ≥ 40 dBc down; at the licensed 33 dBm the same absolute limits mean ≥ 69 / 63 dBc ([19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md), [certification](../19-regulations-safety/certification-fcc-ce-imda.md)). Use RBW 100 kHz below 1 GHz and 1 MHz above.

| Likely cause | Test |
|---|---|
| Low-pass/harmonic filter not populated or wrong values | BOM check; VNA S21 of the filter section |
| PA driving a mismatched load (harmonics rise into a bad antenna) | harmonics into 50 Ω dummy vs into antenna (through a coupler) |
| Analyzer-generated harmonics | add 10 dB attenuation: a real harmonic drops 10 dB, an internal one drops 20–30 dB ([spectrum analyzers](spectrum-analyzers.md)) |
| Digital clocks and their harmonics | near-field probe + SA; switch clocks off |

### E. Measurements disagree or drift

| Symptom | Cause | Fix |
|---|---|---|
| S11 changes when the cable is touched | common-mode current | chokes/sleeve balun; route cable as in flight |
| S11 at radio differs from S11 at antenna | cable loss/rotation | measure at the antenna or de-embed |
| Power reading 10–20 dB low | averaging meter on packets | duty-cycle correction or CW mode ([RF power](rf-power-measurement.md)) |
| Sensitivity better than datasheet | leakage around the attenuator | verify with attenuator at max; shield |
| Noise-floor readings differ between screenshots | different RBW/gain/detector | fix settings and log them |

### F. Receiver stage-by-stage signal tracing and IF alignment
When a receiver is deaf or noisy, find the stage where the measured level departs from the prediction. Write the expected levels *first* (pre-register them), then inject and measure.

**Expected levels** for the 433 MHz superhet of [receiver architectures](../06-rf-circuits/receiver-architectures.md) (SAW 2.4 dB → LNA 20 dB/NF 0.8 → SAW 3 dB → passive DBM −6.5 dB/NF 7 → IF amp 20 dB/NF 3 → IF filter 4 dB), a −100 dBm CW at the antenna port, and noise with the input terminated in a 290 K load, both in a 10 kHz RBW (`s10_rx_tracing.py` §A):

| After stage | Cumulative gain | Cumulative NF | Signal | Noise in 10 kHz | SNR |
|---|---|---|---|---|---|
| SAW (433) | −2.4 dB | 2.40 dB | −102.4 dBm | −134.0 dBm | 31.6 dB |
| LNA | 17.6 | 3.20 | −82.4 | −113.2 | 30.8 |
| SAW | 14.6 | 3.24 | −85.4 | −116.1 | 30.7 |
| Mixer (DBM) | 8.1 | 3.51 | −91.9 | −122.4 | 30.5 |
| IF amp | 28.1 | 3.80 | −71.9 | −102.1 | 30.2 |
| IF filter | 24.1 | 3.81 | −75.9 | −106.1 | 30.2 |

**Signal tracing procedure**
1. *Back to front*: inject at the demodulator/ADC input at its expected level, then at the IF input (at the IF frequency), the mixer RF port, the LNA input and finally the antenna port, each time at the level the table predicts for that node. The first injection point that fails isolates the faulty stage downstream of it — this is the classic radio-repair method, and it works for SDR front ends too.
2. *Front to back*: inject −100 dBm at the antenna port and measure at each node with a Z0 (resistive, 450–950 Ω) probe or a short coax pigtail into the SA ([probing](oscilloscopes-and-probing-for-rf.md)); subtract the probe's 20–26 dB divider loss. A stage whose gain differs from its datasheet by > 2–3 dB is suspect (bias, a missing DC block, a wrong part, oscillation).
3. *Noise tracing* (no generator): power the chain with the input terminated and look at the noise floor at each node. A plain tinySA (NF ≈ 27 dB, DANL ≈ −110 dBm in 10 kHz) cannot see the LNA-output noise (floor rises < 1 dB) but sees the IF-amp output (+6 dB); with a 20 dB, 5 dB-NF preamp in front (≈ 7 dB NF overall) the LNA output raises the floor by ≈ 14 dB (§B). A stage that *adds* far more noise than this, or a floor that moves with supply voltage or hand position, points to oscillation.
4. *SDR front end check*: with the antenna replaced by a 50 Ω load, switching a SAW + 20 dB/0.8 dB LNA in front of an RTL-SDR (NF 5.4 dB at 437 MHz) should raise the SDR's displayed floor by ≈ 15.5 dB; a rise ≥ 10 dB proves the LNA noise dominates (the SDR then adds < 0.5 dB; system NF 3.3 dB) (§C). No rise: the LNA is unpowered, bypassed or broken. A much larger rise or a sloping floor: oscillation or gain far above design.
5. *Selectivity*: sweep the generator across the channel and image (f_RF − 2f_IF) at a fixed level and compare with the filter specs; a weak image rejection points at the pre-selector or the LO side.

**IF alignment (tuned IF transformers, discriminators)**
- Classic single- and double-tuned IF cans (10.7 MHz, 455 kHz) are peaked with a generator at the IF injected at the mixer: tune each can for maximum output with the signal **well below the AGC/limiter threshold** — a limiting IF amplifier 15 dB above its knee shows *no* change for a 10 dB misalignment (§D). Use the weakest signal that gives a readable output (or read the RSSI/AGC voltage) and reduce the level as the alignment improves.
- Detuning cost of a single-tuned can: 10 log[1 + (2Q δf/f₀)²] — for Q = 50 at 10.7 MHz (214 kHz bandwidth) 0.86 dB at 50 kHz, 2.7 dB at 100 kHz, 6.5 dB at 200 kHz (§D).
- Wideband or stagger-tuned IFs are aligned for a flat passband with a sweep (SA + tracking generator), not by peaking each can; ceramic and crystal IF filters are not aligned at all, but their source/load terminations must be correct (a mismatched 10.7 MHz ceramic filter shows ripple and extra loss).
- FM quadrature/discriminator coils are set for zero DC output (the S-curve centre) at the IF centre frequency.
- Integrated low-IF receivers (SX126x, R820T) have nothing to align; their equivalent is the **frequency-offset calibration** (crystal ppm, SDR ppm correction) checked against a GPSDO-referenced source ([basic bench instruments](basic-bench-instruments.md)).

### G. Amplifier and RF-switch bring-up: failure modes and a safe test set-up
**Failure modes**

| Failure | Mechanism | How it shows | Prevention / test |
|---|---|---|---|
| Wrong bias | bias resistor/choke wrong, regulator not on, gate bias missing on a depletion-mode FET | current far from datasheet; low gain; overheating | measure DC current before any RF; bias sequencing (negative gate first for depletion pHEMT/GaN) ([stability & biasing](../06-rf-circuits/amplifier-stability-and-biasing.md)) |
| Oscillation | K < 1 somewhere (often far out of band), ground/via inductance, output-to-input coupling | current changes with no input; spurs that move with supply voltage or hand position; "gain" that varies with cable length | SA sweep with the input terminated, 10 kHz–3× f_max; stability circles; resistive loading out of band |
| ESD | antenna and SMA ports are the entry points; pHEMT LNAs can be HBM Class 1B (500–1000 V) | dead or noisy LNA after handling | wrist strap, discharge cables before mating, TVS/shunt-L at the antenna port ([lab safety](../19-regulations-safety/lab-safety-esd-high-power.md)) |
| RF overdrive | input above the absolute maximum (BGA524N6: 0 dBm); a 2 W transmitter centimetres away | permanent NF increase or gain loss | input pads in test; limiter/SAW in the system; never key the TX into the RX chain |
| Missing DC block | bias tee or collector voltage on the RF port | DC into the SA/VNA (tinySA Ultra ±5 V max), shorted bias, wrong gain | DC-block every instrument port; check with a DMM before connecting |
| Hot switching | RF applied while an FET/SOI switch changes state | switch damage, transients | switch with RF off or within the hot-switch rating (many parts specify a lower hot-switch power) ([switches](../06-rf-circuits/rf-switches-attenuators-limiters.md)) |
| Mismatch / open load | PA into an open or a detuned antenna; 33 dBm is 14.1 V peak into 50 Ω and up to 28.3 V peak with full reflection | PA or switch breakdown, harmonics up | test into a dummy load; switch voltage rating ≥ 2× the matched peak |
| Out-of-band mismatch | filters are reflective outside their passband; a broadband gain block sees |Γ| → 1 there and may oscillate | spurs outside the band; instability that appears only with the filter fitted | 3–6 dB pads between filter and amplifier: an n dB pad bounds the reflection seen to RL ≥ 2n dB (6 dB → 12 dB) (`s10_construction_amp.py` §C) |
| Too much gain in one place | loop gain = gain × output-to-input coupling | ripple, then oscillation | split into stages with filters/pads, shield walls and separate decoupling (below) |

**Why high gain is split into stages.** Any output-to-input coupling k (board, enclosure, supply, ground) closes a feedback loop of gain G·k. 40 dB of gain with −50 dB of coupling gives a loop gain of −10 dB: already **5.7 dB peak-to-peak gain ripple** with frequency; 60 dB with the same coupling oscillates. Cutting the coupling to −70 dB (shield walls between stages, separate decoupling with RC/ferrite isolation, input and output at opposite ends) brings the 40 dB chain to < 0.6 dB ripple (§D). Practical consequence: no more than ≈ 20–30 dB per stage/shielded section, with pads or filters between stages so each block sees a broadband termination.

**Bring-up checklist (amplifier or switch board)**
1. Inspect: part orientation, DC-block capacitors fitted, bias resistor value (Mini-Circuits-style gain blocks need R_bias + choke; the resistor sets the current [11]).
2. DC only, current-limited supply: current within ±10–20 % of the datasheet; no RF connected; check for DC on each RF port with a DMM.
3. Stability: input and output terminated in 50 Ω; SA (through a DC block and pad) across 10 kHz to ≥ 3× the top frequency; touch-test the board and vary the supply ±10 % — nothing must appear.
4. Small-signal gain: generator → 10 dB pad → DUT → DC block → pad → SA (or VNA at reduced power). For the **BGA524N6** (19.6 dB, IP1dB −16 dBm, abs max 0 dBm): −40 dBm from the generator + 10 dB pad puts −50 dBm at the input (34 dB below IP1dB) and −30.4 dBm at the output (§C). A bare NanoVNA port (−13 dBm) already drives it 3 dB past IP1dB — always pad the VNA for LNAs.
5. Compression: step the input up in 1 dB steps to the P1dB point, never above the absolute maximum; keep the analyzer below its own linear limit (a 20 dB block at +20 dBm OP1dB needs ≥ 30–40 dB of rated attenuation before a tinySA Ultra: −10/−20 dBm).
6. Switches: measure insertion loss/isolation in each state with RF ≤ the hot-switch rating; toggle only with RF off at high power; check the control-voltage logic levels and timing.
7. Record: bias current, gain, P1dB, spurs (none) and the exact set-up (pads with their measured values) in the test log.

**Safe test set-up (receive or gain block)**: current-limited supply → bias tee (or on-board bias); signal generator → 10 dB pad → DUT → DC block → 20–40 dB rated pad → SA/power meter. The input pad protects the DUT from generator mistakes and gives it a broadband 50 Ω source; the output pad protects the analyzer and gives the DUT a broadband load.

## Worked examples
**Example 1 — the "1 km" ground test of the 433 MHz downlink.** Budget: E22-400T33D 33 dBm, 2.15 dBi whips, 1 km: FSPL = 85.2 dB → P_rx = 33 + 2.15 + 2.15 − 85.2 = −47.9 dBm, ~90 dB above SF12 sensitivity. Observed: packets stop at 1 km with both people holding the radios at 1.5 m. Diagnosis by dB: two-ray at 1.5 m heights ≈ +28 dB; trees/terrain 20–40 dB; body loss 5–10 dB. Conducted checks: TX power 32.6 dBm into pads ✓; RX sensitivity −136 dBm ✓; antenna RL 14 dB in the nose cone ✓ → no hardware fault; redo the test as an attenuation range test from a drone ([antenna range](antenna-range-ota-testing.md)). *Licence note:* radiating 33 dBm at 433 MHz in Singapore needs an amateur licence (with IMDA consent) or a permit — the licence-exempt limit is 10 mW e.r.p.; for an unlicensed range test step the module down and add a pad to ≤ 10 dBm conducted into a dipole (the budget still leaves ≈ 66 dB above SF12 sensitivity at 1 km) ([19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md)).

**Example 2 — desense from the flight computer.** Ground-station-style RSSI measurement on the flight board (RX on 433.175 MHz, antenna replaced by a 50 Ω load): noise floor −120 dBm with only the radio powered; −113 dBm with the Teensy running; −112 dBm with the SD card logging. That is ≈ 7–8 dB of desense (a 7 dB floor rise means the interference sits ≈ 6 dB above the receiver's own noise: 10 log(1 + 10^0.6) = 7.0 dB). Near-field probe finds a 432.0 MHz line (48 MHz ×9 or 24 MHz ×18) over the USB/MCU clock area → move the channel (e.g. 434.5 MHz), add filtering/shielding, or re-route the clock; re-measure (pass: ≤ 1–2 dB desense).

**Example 3 — TX power low after an "antenna-off" test.** Conducted power at the highest setting reads 29.1 dBm instead of 33 dBm, and current is lower than the datasheet. History: the module was keyed with no antenna. Likely PA damage → replace the module, then enforce "never transmit without a load" (software interlock in bench builds).

**Example 4 — GNSS C/N₀ drops 8 dB when the LoRa module transmits at 2 W.** The 433 MHz carrier is far from L1, but 2 W at a few centimetres overloads the GNSS LNA (blocking/compression) or its bias network. Tests: (1) C/N₀ with TX into a dummy load (conducted, no radiation) vs into the antenna; (2) add a 1575 MHz SAW before the GNSS LNA; (3) increase antenna separation/orientation. Pass criterion pre-registered: ≤ 2 dB C/N₀ loss during TX.

## Practical notes
- **Pre-register** the test plan (expected currents, powers, frequencies, sensitivities, limits) in a write-once file; append, never edit [9].
- **Log a config line** at boot with every radio parameter and firmware hash; a filename is a claim, the config line is evidence [9].
- **One variable per test**; for suspected interactions (e.g. SD logging × Wi-Fi) use a 2×2 matrix.
- **Never transmit into an open**; keep a 50 Ω dummy load on every idle radio; interlock TX in bench builds.
- **Keep a "golden" reference unit** (known-good radio + antenna) to swap in — the fastest fault isolation.
- **Test on battery, repeatedly**, and at temperature extremes if you can (TCXO drift, PA power droop).
- **Photograph cable routing** for every antenna/OTA test — it changes results.
- Cross-check pass/fail thresholds with the domain 13 [RF PCB review checklist](../13-pcb-rf-layout-emc/rf-pcb-review-checklist.md) before the next board spin.

## Common mistakes & misconceptions
- **Starting with a field range test** — confounds antenna, propagation, radio and settings in one number.
- **Changing two things between runs** and attributing the improvement to one.
- **Believing the module's RSSI and power registers** without a conducted measurement.
- **Declaring "no interference" after testing with USB power and the flight computer idle.**
- **Treating a clean boot on USB as proof it works on battery** [10].
- **Peaking an IF with a strong signal** — the limiter/AGC flattens the response and the alignment looks perfect at any setting.
- **Probing receiver nodes with a 10× passive probe** at UHF — it loads the node (15 Ω at 915 MHz); use a Z0 probe or a pigtail.
- **Connecting an amplifier output with bias on it straight to an analyzer**, or driving an LNA from a bare VNA port.
- **Blaming a gain block for "bad gain flatness"** when the ripple is feedback through the board or enclosure.
- **Narrating a mechanism before measuring it** — eight plausible hypotheses can all be wrong [9].

## How to simulate / verify
- `python3 tools/verify/meas_bringup.py` — (1) range-shortfall ↔ dB; (2) desense formula; (3) ppm → Hz; (4) pad chain for the 33 dBm E22-400T33D; (5) supply droop and bridging capacitance; (6) clock-harmonic search near 433/868/915/1575 MHz.
- `python3 tools/verify/s10_rx_tracing.py` §A–D — per-stage signal/noise/SNR of the 433 MHz superhet, noise tracing vs SA DANL, SDR LNA floor-rise test, IF-can detuning and limiter masking. `python3 tools/verify/s10_construction_amp.py` §C–D — pad plans for the BGA524N6 and a gain block, pad-bounded return loss, PA peak voltage into an open, loop-gain ripple vs stage gain and coupling. ALL PASS.
- The per-step measurement methods are verified on their own pages (VNA, SA, power, NF, antenna-range scripts).

## Open questions / gaps
- The E22-400T33D's burst current and recommended supply decoupling were not taken from its datasheet here — check the EBYTE manual (domain 15) before sizing the bulk capacitor.
- Pass criteria are examples; the team should set its own in the pre-registered plan.
- No team measurements yet of flight-computer desense at 433 MHz or of GNSS C/N₀ vs LoRa TX; the examples are illustrative.
- The stage-level table (§F) and the coupling figures in §G are model values; replace them with measured levels from the first ground-station receiver build. The limiter knee in the IF-alignment check is illustrative.

## Sources
1. This KB, domain 17 pages: [VNA calibration](vna-fundamentals-calibration.md), [NanoVNA practical](nanovna-librevna-practical.md), [spectrum analyzers](spectrum-analyzers.md), [RF power](rf-power-measurement.md), [noise figure & sensitivity](noise-figure-measurement.md), [antenna range/OTA](antenna-range-ota-testing.md), [probing](oscilloscopes-and-probing-for-rf.md). (internal; each sourced there)
2. Keysight AN 150 — internal-distortion test, detectors. (app note; read)
3. Keysight AN 1449-2 — power sensors. (app note; read)
4. Keysight AN 57-2 — Y-factor/NF. (app note; read)
5. Agilent AN 1287-3 — VNA error correction. (app note; read)
6. Tektronix ABCs of Probes — ground-lead effects. (vendor primer; read)
7. Semtech SX1261/2 datasheet — sensitivity definition (PER 1 %, 64 bytes). (datasheet; read)
8. Space Bar avionics knowledge base, "flight-computer-design-lessons" — documentation drift (as-ordered BOM/stackup), other board defects. (internal team notes)
9. Space Bar avionics knowledge base, "engineering-ethos" — pre-registration, one variable per test, record everything, measure before narrating. (internal team notes)
10. Space Bar avionics knowledge base, "hil-bench-testing-methods" and "avionics-b-v3-primary-fc" — battery vs USB power-up failures (GPS-UART 3/11 on battery), gating on repeated power-ups, E22-400T33D 433 MHz 2 W telemetry, ZED-F9P active antenna. (internal team notes)
11. This repository: `tools/verify/meas_bringup.py`, `tools/verify/s10_rx_tracing.py`, `tools/verify/s10_construction_amp.py`. (verification)
12. Mini-Circuits, AN-60-010 *Biasing MMIC Amplifiers* — bias resistor + RF choke from Vcc, DC-blocking capacitors at input and output, supply turn-on transient protection. https://www.minicircuits.com/app/AN60-010.pdf (app note; search summary)
13. This KB: [receiver architectures](../06-rf-circuits/receiver-architectures.md) (433 MHz superhet stage list), [amplifier stability & biasing](../06-rf-circuits/amplifier-stability-and-biasing.md), [RF switches](../06-rf-circuits/rf-switches-attenuators-limiters.md), [lab safety/ESD](../19-regulations-safety/lab-safety-esd-high-power.md), [canonical values](../00-math-foundations/canonical-values-and-conventions.md) (BGA524N6, RTL-SDR NF). (internal; each sourced there)
