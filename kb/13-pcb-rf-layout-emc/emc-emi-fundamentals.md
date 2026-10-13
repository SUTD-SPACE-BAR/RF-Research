---
title: EMC/EMI fundamentals for RF boards and rocket avionics — DM vs CM radiation, cables, filtering, spread-spectrum clocks, edge rates, pre-compliance (near-field, LISN, LPDA), susceptibility (sensors, pyro), ESD, MIL-STD-461/DO-160 test families, EFT/surge, snubbers and inductive-load clamps
domain: 13-pcb-rf-layout-emc
slug: emc-emi-fundamentals
tags: [EMC, EMI, differential-mode, common-mode, cable-radiation, Ott, FCC-part-15, CISPR-32, ferrite, common-mode-choke, pi-filter, spread-spectrum-clocking, edge-rate, near-field-probe, tinySA, pre-compliance, susceptibility, RF-rectification, desense, pyro, electro-explosive-device, HERO, MIL-STD-464, ESD, IEC-61000-4-2, TVS, MIL-STD-461G, DO-160G, CS114, CS115, CS116, RE102, RS103, CE102, IEC-61000-4-4, EFT, IEC-61000-4-5, surge, snubber, flyback-diode, zener-clamp, avalanche, hot-plug, contact-protection, LISN, CISPR-25, antenna-factor, LPDA, conducted-emissions, radiated-pre-scan]
prerequisites:
  - ../02-electromagnetics/radiation-from-currents-hertzian-dipole.md
  - grounding-and-return-paths.md
related:
  - shielding-and-isolation.md
  - mixed-signal-layout.md
  - power-distribution-decoupling-for-rf.md
  - vias-stitching-fencing.md
  - rf-pcb-review-checklist.md
  - ../04-real-components-hf/ferrites-and-beads.md
  - ../08-antennas/antenna-matching-and-baluns.md
  - ../17-test-measurement/spectrum-analyzers.md
  - ../19-regulations-safety/certification-fcc-ce-imda.md
  - ../19-regulations-safety/lab-safety-esd-high-power.md
  - ../17-test-measurement/interference-hunting-and-rf-immunity.md
  - digital-termination-and-crosstalk.md
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# EMC/EMI fundamentals for RF boards and rocket avionics

## Questions this page answers
- Why do cables radiate so much more than the PCB traces that drive them?
- How many microamps of common-mode current on a cable is enough to fail FCC/CISPR limits?
- What are Ott's differential-mode and common-mode radiation formulas, and where do the constants come from?
- Which MCU/SD/USB clock harmonics land in my 433 MHz, 915/920 MHz LoRa or GNSS L1 band?
- Does spread-spectrum clocking help my own receiver, or only the EMC test?
- How much does slowing edges with a series resistor help?
- How do I do pre-compliance testing with a near-field probe and a tinySA?
- Can my 2 W telemetry transmitter upset the barometer, IMU or — worse — fire a pyro channel?
- How do I protect RF and sensor ports against ESD without ruining RF performance?
- Why does an audio amplifier buzz when a phone or my telemetry radio transmits, and how do I fix it?
- What do MIL-STD-461 and DO-160 actually test, and which of those tests are worth copying for a rocket flight computer?
- What are EFT, surge and CS115/CS116 transients, and how much energy does my TVS have to absorb?
- How do I design an RC snubber, and do I need a flyback diode on pyro and servo outputs?
- Why did my regulator die when I flipped the arming switch on a LiPo?
- How do I measure conducted emissions with a LISN, and which LISN (50 µH or 5 µH) do I need?
- How do I turn a spectrum-analyser reading from a log-periodic antenna into dBµV/m, and how trustworthy is a home pre-scan?
- We failed a radiated-emission test — what is the fastest way to find and fix the cause?

## TL;DR
- **Two radiation mechanisms** (far field, maximum direction, Ott's forms over a reflecting ground):
  - differential mode (current loop, area A): $E_{DM}\approx2.63\times10^{-14}\,f^2AI/r$ (V/m; f Hz, A m², I A, r m);
  - common mode (current flowing the same way on a cable/trace of length L): $E_{CM}\approx1.26\times10^{-6}\,fLI_{cm}/r$.
  Both constants follow from the small-loop and Hertzian-dipole fields ×2 for ground reflection; checked by dipole superposition to < 1 % (script §1) [1][2].
- **Consequence**: at 100 MHz a 10 cm² signal loop may carry ≈ 1.7 mA before failing FCC Class B at 3 m, but **1 m of cable only ≈ 3.7 µA of common-mode current** — a ratio of ≈ 300–500 (script §2; Ott's classic "≈ 8 µA at 30 MHz" reproduced). **EMC is mostly about common-mode currents on cables.**
- **Clock harmonics that land in Marcus's bands** (script §4): **40 MHz × 23 = 920 MHz (inside the Singapore 920–925 MHz LoRa band)**, 25 MHz × 37 = 925 MHz, 12 MHz × 77 = 924 MHz, **25 MHz × 63 = 1575.0 MHz and 8 MHz × 197 = 1576 MHz (inside GPS L1 C/A)**, 24/26/40 MHz × n in BeiDou B1, many × n = 1600 MHz in GLONASS G1. These cause self-desense, not just EMC failures.
- **Edge rate**: above the corner $1/(\pi t_r)$ harmonics fall 40 dB/decade; making edges 5× slower cuts all harmonics above both corners by 14 dB (script §3). A 33–220 Ω series resistor into ≈ 10 pF gives 0.7–4.8 ns edges.
- **Spread-spectrum clocking** (triangular, 0.5–1 % down-spread) cuts the peak in a 120 kHz CISPR/125 kHz LoRa bandwidth by ≈ 11–16 dB at 0.9–1.6 GHz — **≈ 4 dB less than the popular 10 log(spread/RBW) estimate** (own FFT, script §5), and only 4–10 dB in a 1–2 MHz GNSS bandwidth.
- **Pyro safety**: MIL-STD-464 requires induced RF in electro-explosive devices to stay **≥ 16.5 dB below the maximum no-fire stimulus (15 % of no-fire current)** [3]. A hobby e-match (no-fire ≈ 130 mA, anecdotal) must then see < 20 mA; leads spread as a resonant dipole 0.2 m from a 2 W 433 MHz antenna could pick up up to ≈ 145 mA (upper bound) — twisted leads pick up < 1 mA (script §6). **Twist and shield pyro leads, short them when disarmed, filter at the board, keep antennas away.**
- **Sensor susceptibility**: RF rectification in pn junctions/ESD structures gives a DC shift ≈ $V_{rf}^2/(4nV_T)$ — ≈ 1 mV for 10 mV of RF (script §7): RC-filter analog inputs and keep sensor wiring away from TX antennas.
- **ESD** (IEC 61000-4-2 level 4: 8 kV contact, ≈ 30 A first peak with ≈ 1 ns rise): on RF ports use TVS parts ≤ 0.2–0.5 pF (0.5 pF → RL 18 dB at 1575 MHz, 14.5 dB at 2.45 GHz) (script §8).
- **Military/aerospace test families as a menu** ([§ standards](#emc-standards-and-transients-for-avionics)): MIL-STD-461G CE102 (power-lead emissions, 50 µH LISN), CS114/CS115/CS116 (harness injection: RF, 30 ns/5 A impulses, damped sines), RE102 and RS103 (fields, ≈ 1–200 V/m by platform); DO-160G §16–22 and §25 do the same for civil aircraft. Space Bar boards are not certified to them, but **your own 2 W transmitter makes ≈ 99 V/m at 10 cm — RS103 territory** — so copy the *tests*, at your own levels.
- **Inductive turn-off is the commonest self-inflicted transient** (`s16_snubber_transients.py`): 6 A of pyro current in 0.8 µH of wiring would ring to ≈ 310 V if unclamped, so a 30 V FET avalanches (≈ 19 µJ, 180 ns); a freewheel diode across the output plus 10 µF at the switch holds it to ≈ +1 V. Hot-plugging a 2S pack into ceramic caps overshoots to **15.6 V (3S: 23.5 V)**; 0.32 Ω + 20 µF of damping holds 10.5 V.
- **Conducted pre-compliance** ([§ pre-compliance](#conducted-and-radiated-pre-compliance)): a bare 2 MHz buck is ≈ 30 dB over CISPR 32 Class B at a LISN; a damped 1 µH + 10 µF input filter puts it ≈ 39 dB under. **Radiated**: E = V + AF + cable loss with AF = 20 log f − G − 29.77 dB/m; a fixed-height home scan reads up to ≈ 4 dB low, so keep ≥ 6 dB margin.

## Intuition (no math)
A pair of wires carrying equal and opposite currents (a signal and its return) radiates very little because the two fields almost cancel; what is left is proportional to the **loop area** and grows with frequency squared. That is **differential-mode** radiation, and you control it by keeping every signal right above its return plane ([grounding](grounding-and-return-paths.md)).

If some current flows the *same way* on all the wires of a cable — because the board's ground is not at the same RF potential as the thing at the other end of the cable — nothing cancels. The cable becomes a monopole/dipole antenna driven at its base. That is **common-mode** radiation, and a few microamps are enough to fail an emission test. Common-mode currents are created by voltage differences across the board ground (return currents crossing slots, ground bounce, poorly decoupled ICs, an antenna's feed current returning on the coax braid) and by asymmetries that convert differential signals to common mode.

The same mechanisms work in reverse (**susceptibility**): a cable or a long trace picks up RF from your own 2 W transmitter a few centimetres away. In sensors, the RF is rectified by semiconductor junctions into DC offsets; in pyro circuits the RF current heats the bridgewire. In receivers, harmonics of your own digital clocks land in the receive band and **desensitise** it — the most common RF problem on flight computers.

## The math

### Level 1 — Ott's emission estimates and the currents they allow
For a small loop of area $A$ and a short wire of length $L$ (far field, maximum direction), with a factor 2 for a ground reflection at a test site:
$$E_{DM}=2\frac{\eta_0\pi}{c^2}\frac{f^2AI_{DM}}{r}\approx263\times10^{-16}\frac{f^2AI_{DM}}{r},\qquad E_{CM}=2\frac{\eta_0}{2c}\frac{fLI_{CM}}{r}\approx1.26\times10^{-6}\frac{fLI_{CM}}{r}$$
($I_{CM}$ = total common-mode current). Free-space values are half: 1.316 × 10⁻¹⁴ and 6.28 × 10⁻⁷ (Paul writes the latter as 1.257 × 10⁻⁶ with $I_C$ = current *per wire*; same physics — see the [radiation page](../02-electromagnetics/radiation-from-currents-hertzian-dipole.md)). The script integrates Hertzian-dipole segments for two 100 mm wires 1 mm apart at r = 100 m and matches both formulas to < 1 % from 30 to 300 MHz.

Against FCC Part 15 Class B limits at 3 m (100/150/200/500 µV/m for 30–88/88–216/216–960/> 960 MHz [4]) (script §2):

| f | DM loop 1 cm² | 10 cm² | CM on 0.3 m | 1 m |
|---|---|---|---|---|
| 30 MHz | 127 mA | 12.7 mA | 26 µA | 7.9 µA |
| 100 MHz | 17 mA | 1.7 mA | 12 µA | 3.7 µA |
| 300 MHz | 2.5 mA | 0.25 mA | 5.3 µA | 5.0 µA* |
| 915 MHz | 0.27 mA | 27 µA | 5.0 µA* | 5.0 µA* |

*Cable length capped at the resonant equivalent $L_{eff}=\lambda/\pi$ (a λ/2 dipole's field), since the short-wire formula over-predicts for long cables.

### Level 2 — clock spectra, edge rates and spread spectrum
A trapezoidal clock (amplitude A, duty d, rise time $t_r$) has harmonic envelope
$$|c_n|\le2Ad\cdot\min\!\left(1,\frac{1}{\pi nd}\right)\cdot\min\!\left(1,\frac{T}{\pi nt_r}\right),$$
flat to $f_1=1/(\pi\tau)$, −20 dB/decade to $f_2=1/(\pi t_r)$, −40 dB/decade above (Ott/Paul) [1][2]. With 1 ns edges a 3.3 V, 40 MHz clock has ≈ 87 dBµV (22 mV) of source voltage at its 23rd harmonic (920 MHz); 5 ns edges → 73 dBµV (script §3). For comparison, the thermal noise kTB in a 125 kHz LoRa channel is ≈ −123 dBm ≈ −16 dBµV in 50 Ω: **you need > 100 dB between a fast clock trace and the receiver input** — distance, planes, fences, filtering and slow edges all contribute ([mixed-signal](mixed-signal-layout.md)).

**Spread-spectrum clocking (SSC)** frequency-modulates the clock by a fraction δ (typ. 0.5–1 % down-spread, 30–33 kHz triangle). The n-th harmonic spreads over $n\delta f_0$; the peak power in a bandwidth RBW ≪ $n\delta f_0$ falls roughly by $10\log_{10}(n\delta f_0/\mathrm{RBW})$. The script computes the actual spectrum of $e^{jn\phi(t)}$ by FFT: for 40 MHz × 23, 0.5 %: **−11.8 dB** in 120 kHz vs −15.8 dB estimated; 1 %: −14.4 vs −18.8 dB; in 1 MHz: −4.5 dB. A triangle profile piles power at the spread edges ("bat ears"), so real gains are ≈ 4 dB below the flat estimate. SSC helps a narrowband LoRa receiver about as much as it helps the CISPR test; it helps GNSS (1–2 MHz wide) much less.

### Level 3 — susceptibility: rectification, pyro circuits, ESD
**RF rectification.** A junction with $I=I_s(e^{v/nV_T}-1)$ driven by $v=V_{rf}\cos\omega t$ produces a DC component; for $V_{rf}\ll nV_T$ the open-circuit DC shift is $\Delta V\approx V_{rf}^2/(4nV_T)$: 1 mV RF → 10 µV, 10 mV → 1 mV, 30 mV → 8.7 mV (script §7). Op-amp inputs, ESD diodes on sensor pins, and bipolar/MOS bias networks all do this; the symptom is a DC offset or noise that correlates with TX bursts (e.g. the LoRa packet rate). Fix: RC filters at the sensor (100 Ω + 100 pF: 29 dB at 434 MHz ideal; 20–40 dB real), short sensor traces over solid ground, keep TX antennas and their coax away from sensors, and don't route I²C/SPI to sensors along the board edge.

**Pyro / electro-explosive devices (HERO).** MIL-STD-464C requires EIDs to keep RF-induced stimulus ≥ 16.5 dB below the **maximum no-fire stimulus** (MNFS: ≤ 0.1 % firing in 5 min at 95 % confidence) for safety — i.e. ≤ 15 % of the no-fire current — and 6 dB for other applications; 1 A/1 W hot-bridgewire EIDs are common in ordnance [3]. Hobby e-matches are far more sensitive (e.g. a Q2G2-class igniter: all-fire ≈ 333 mA/100 ms, no-fire ≈ 130 mA/5 s — anecdotal hobby data [5]). Estimates for a 2 W, 433 MHz transmitter (far-field formula, which is optimistic in the reactive near field r < λ/2π = 11 cm) (script §6):

| distance | E (V/m) | leads spread like a resonant dipole (upper bound) | parallel pair 300 mm | twisted pair |
|---|---|---|---|---|
| 0.1 m | ≈ 99 | ≤ 290 mA | 0.8 mA | < 0.8 mA |
| 0.2 m | ≈ 50 | ≤ 145 mA | 0.4 mA | < 0.4 mA |
| 0.5 m | ≈ 20 | ≤ 58 mA | 0.16 mA | < 0.16 mA |
| 1.0 m | ≈ 10 | ≤ 29 mA | 0.08 mA | < 0.08 mA |

The dangerous mode is the **common-mode (dipole) pickup** of the lead pair plus its conversion to differential current through the bridge by asymmetry — which twisting, shielding and a low-impedance shunt at the bridge end suppress. Practical rules: twisted (and preferably shielded) pyro leads; pyro outputs shorted or clamped when disarmed; an RF bypass capacitor (≈ 1–10 nF) and ferrite at the board connector; no pyro wiring running alongside the telemetry coax or near the antenna; and — cheapest of all — **don't transmit at full power in the minutes when igniters are being connected on the pad**.

**ESD (IEC 61000-4-2).** Contact levels 2/4/6/8 kV (air 2/4/8/15 kV); first peak ≈ 3.75 A/kV with 0.7–1 ns rise — 30 A at 8 kV [6]. On RF ports the TVS capacitance is a shunt discontinuity: 0.1 pF is invisible below 6 GHz (RL 21–43 dB), 0.5 pF gives RL 18 dB at 1575 MHz and 14.5 dB at 2.45 GHz, 3 pF (a generic TVS) destroys UHF matching (RL 8 dB at 915 MHz) (script §8). u-blox recommends < 0.5 pF parts on RF_IN [7]. For LoRa antenna ports a DC-grounded antenna (or a λ/4 shorted stub / shunt inductor) plus a low-C TVS is common.

## Design equations & rules of thumb

| Quantity | Equation / value | Notes |
|---|---|---|
| DM radiation | $2.63\times10^{-14}f^2AI/r$ | ∝ f², loop area |
| CM radiation | $1.26\times10^{-6}fLI_{cm}/r$ | ∝ f, cable length (cap $L\le\lambda/\pi$) |
| Class B CM current, 1 m cable | ≈ 4–8 µA (30–300 MHz) | [1][4] |
| Clock envelope corners | $1/(\pi\tau)$, $1/(\pi t_r)$ | −20, −40 dB/decade |
| Edge slowing | ×k slower → −20 log k above both corners | series R ≈ 33–220 Ω |
| SSC peak reduction | ≈ 10 log(nδf₀/RBW) − 4 dB (triangle) | own FFT |
| Pyro safety margin | ≥ 16.5 dB below MNFS (15 % of no-fire current) | MIL-STD-464C [3] |
| RF rectification | $\Delta V\approx V_{rf}^2/(4nV_T)$ | 10 mV → 1 mV |
| TVS on RF port | $\lvert\Gamma\rvert\approx\omega CZ_0/2$ | ≤ 0.5 pF at GNSS |
| CM choke on cables | ≥ 100–1000 Ω CM impedance at the offending frequency | ferrite mix per band ([ferrites](../04-real-components-hf/ferrites-and-beads.md)) |
| Unclamped turn-off | $V_{pk}=V_{dd}+\sqrt{V_{dd}^2+I^2L/C}$ | 6 A, 0.8 µH, 300 pF → 310 V |
| RC snubber (ring halving) | $C_{par}=C_{add}/((f_0/f_1)^2-1)$, $R=\sqrt{L/C_{par}}$, $C_s$ = 3–4 $C_{par}$, $P=C_sV^2f_{sw}$ | 80 MHz ring → 12 Ω + 680 pF |
| Clamped inductive decay | $t_0=(L/R)\ln(1+IR/V_c)$; switch sees $V_{dd}+V_c$ | Zener ≈ 7–10× faster than a diode |
| FET avalanche energy | $\tfrac12LI^2\,V_{BR}/(V_{BR}-V_{dd})$ | 19 µJ for the pyro example |
| Hot-plug overshoot | $V(1+e^{-\pi\zeta/\sqrt{1-\zeta^2}})$, ζ = (R/2)√(C/L); damp with $R_d≈\sqrt{L/C}$, $C_d≥4C$ | 2S → 15.6 V undamped |
| Surge 1.2/50–8/20 | $I_{pk}≈(V-V_{clamp})/2\,Ω$ | 1 kV → 490 A, 170 mJ |
| LISN | 50 µH: ≈ 50 Ω above 0.5 MHz; 5 µH: ≈ 50 Ω above 5 MHz | CISPR 16/32 vs CISPR 25 |
| Antenna factor | $AF=20\log f_{MHz}-G_{dBi}-29.77$ dB/m; $E=V+AF+L_{cable}$ | 6 dBi LPDA @ 400 MHz: 16.3 dB/m |
| Distance scaling (far field) | +20 log(10/3) = 10.5 dB from 10 m to 3 m | pre-scan only |

## Worked examples

### 1. The flight computer's USB/battery lead as an antenna
A 0.5 m battery harness on a 2-layer board whose ground has a 20 mm slot crossed by a 40 MHz clock ([grounding example 2](grounding-and-return-paths.md)): the slot develops ≈ 10–20 mV at the 5th–25th harmonics, the harness CM impedance is ≈ 150–300 Ω, so $I_{cm}$ ≈ 30–130 µA — at 3 m, $E=1.26\times10^{-6}\cdot f\cdot0.5\cdot I/3$ ≈ 1.3–5.5 mV/m at 200 MHz, ≈ 19–31 dB over the 150 µV/m Class B limit. **On the rocket the "3 m test site" does not exist, but the LoRa and GNSS antennas are 5–30 cm away** — the same current desenses them. Fixes in order: remove the slot; clamp a ferrite (CM choke) on the harness at the board; filter the battery input (bulk + 100 nF + bead + 1 nF).

### 2. Is my ESP32's 40 MHz clock a problem for 920 MHz LoRa in Singapore?
40 MHz × 23 = 920.000 MHz — **inside** the 917–925 MHz band (the KB's preferred exempt E220 band is 866–869 MHz, where 40 MHz harmonics fall at 840/880 MHz, outside), 125 kHz from the 920.125 MHz channel used on the KB's example (script §4). The ESP32 XTAL and APB/SPI clocks derived from it (40/80 MHz) all have harmonics there. Options: choose a LoRa channel away from 920.000 MHz (e.g. 922.5 MHz — 40 MHz × 23.06, the nearest harmonics are 920 and 960 MHz, i.e. 2.5 MHz away, outside a 125–500 kHz LoRa channel); keep the ESP32 and its crystal far from the LoRa antenna/module; SSC on the MCU if available; measure the LoRa module's RSSI noise floor with the MCU running vs off ([ground-station](../15-lora-ism-radios/ground-station-design.md) procedure applies on the rocket too).

### 3. GNSS L1 desense from an SD card
SD bus at 25 MHz: 25 × 63 = 1575.000 MHz — 0.42 MHz from L1, inside the GPS C/A main lobe. With 1 ns edges the 63rd harmonic is still ≈ 70 dBµV at the SD trace. A u-blox receiver reports this as jamming/CW interference (its jamming indicator rises and C/N0 falls). Fix: run SD at 20 or 40 MHz (harmonics at 1580/1560 MHz — outside L1 C/A ±1 MHz, though 1560 MHz is BeiDou B1), series-terminate the SD clock (33–47 Ω), keep the SD socket at the far end of the board from the GNSS antenna and route SD on inner layers.

### 4. Pre-compliance with a tinySA and a near-field probe
A tinySA Ultra (≈ 100 kHz–5.3 GHz, RBW 200 Hz–850 kHz, built-in LNA [8]) plus a home-made or kit H-field loop (5–10 mm shielded loop for 100 MHz–3 GHz): (1) scan the board with everything on, max-hold, 100 kHz RBW, 30 MHz–3 GHz; (2) find the hot spots (slot edges, crystal, SD, switcher inductor, harness exits); (3) clamp the probe around each cable (or use a clamp-on current probe) to read CM current — convert with the probe's transfer impedance and the CM formula above to estimate E at 3 m; (4) make a change and compare with the same probe position ±1 mm. Near-field levels are relative; use them to rank sources and verify fixes, not to predict pass/fail ([spectrum analysers](../17-test-measurement/spectrum-analyzers.md)).

## EMC standards and transients for avionics
*Added 2026-10-13 (W5-S16, G-13-01). Numbers from `tools/verify/s16_snubber_transients.py` unless cited.*

### Why a student team should know the military and aviation test families
No Space Bar board is qualified to MIL-STD-461 or DO-160, and none needs to be. These standards are still the best public list of the ways an airborne electronics box gets hurt. Each test method describes one mechanism, the waveform that represents it, and how to apply it. Treat them as a **menu of tests to copy at your own levels**. The levels that matter are set by your own vehicle: a 2 W telemetry antenna 10 cm from the flight computer, servo and pyro currents in the same harness, a LiPo hot-plugged through an arming switch, and a human touching the board on the pad.

**MIL-STD-461G** (DoD, 11 Dec 2015; superseded by **MIL-STD-461H, 17 Apr 2026**, whose changes were not reviewed here) [11][12]. Letters: C/R = conducted/radiated, E/S = emission/susceptibility.

| Method | What it represents | Range / waveform | What to copy on a flight computer |
|---|---|---|---|
| CE102 | RF noise a box puts on its power leads | 10 kHz–10 MHz, measured at a 50 µH LISN [11] | conducted noise the FC injects into the av-bay battery harness (the harness then radiates in common mode) — [pre-compliance](#conducted-and-radiated-pre-compliance) |
| CE106 / RE103 | transmitter spurious and harmonics at the antenna port / radiated | per transmitter band (from knowledge) | E22/E220 harmonics: [bench R6](../17-test-measurement/bench-measurement-recipes.md) |
| CS101 | audio-frequency ripple on power leads | 30 Hz–150 kHz [11] | PA burst current (≈ 1 A at the LoRa packet rate) and servo current ripple on the shared rail |
| CS114 | RF currents induced on cable bundles (bulk current injection) | 10 kHz–200 MHz [11] | your own TX coupling into the harness; inject with a clamp probe or just key the radio next to it ([av-bay immunity test](../17-test-measurement/interference-hunting-and-rf-immunity.md)) |
| CS115 | fast switching transients on cables | impulse ≈ 5 A, ≈ 30 ns, ≤ 2 ns edges, 30 Hz for 1 min, via an injection probe [12][13] | pyro and servo FET switching, relay contacts, connector breaks |
| CS116 | ringing transients from LC resonances in wiring | damped sinusoids at 10 k, 100 k, 1 M, 10 M, 30 M, 100 MHz, ≤ 1 pulse/s; peak current from a limit curve (value not verified here) [14] | the ring after a pyro or hot-plug event (this section's numbers) |
| CS117, CS118 | lightning indirect effects; personnel ESD (both new in G; CS118 does not apply to ordnance) [12] | CS118 uses an ESD gun (levels not verified here) | IEC 61000-4-2 handling ESD (Level 3 above) |
| RE101 / RS101 | low-frequency magnetic fields | 30 Hz–100 kHz (from knowledge) | PA and servo supply loops next to the magnetometer ([interference hunting](../17-test-measurement/interference-hunting-and-rf-immunity.md): ≈ 10 µT at 2 cm) |
| RE102 | radiated E-field emissions | 10 kHz–18 GHz [11] | the self-desense problem: your GNSS and LoRa antennas are the "test antenna" |
| RS103 | radiated E-field immunity | 2 MHz–40 GHz, ≈ 1 V/m to 200 V/m depending on platform [11][15] | a 2 W 433 MHz dipole gives ≈ 99 V/m at 10 cm and ≈ 10 V/m at 1 m (Level 3 table) |
| RS105 | nuclear EMP transient field | ≥ 50 kV/m [13] | — |

**RTCA DO-160G** (Dec 2010, Change 1 Dec 2014; identical to EUROCAE ED-14G) is the civil-aircraft counterpart [16][17]. Its EMC sections are: **15** magnetic effect (compass safe distance); **16** power input (the only section covering both susceptibility, as surges, dropouts and ripple, and emissions back onto the bus); **17** voltage spikes on power leads; **18** audio-frequency conducted susceptibility on power inputs; **19** induced signal susceptibility (cable-to-cable coupling); **20** RF susceptibility (conducted, like CS114; radiated, like RS103, including a reverberation-chamber option); **21** RF emission (conducted and radiated); **22** lightning-induced transients (pin injection and cable-bundle tests); **23** lightning direct effects; **25** ESD. The Section 22 pin-injection waveforms are **WF3**, a 1 MHz or 10 MHz damped sine; **WF4**, a 6.4/69 µs voltage; and **WF5A**, a 40/120 µs current. They are applied in sets (A = 3 + 4, B = 3 + 5A) at levels 1–5 [18]. The level tables were not verified here.

### Standard transient waveforms and what they deliver
| Waveform | Shape | Source impedance | Energy into a 20 V clamp (script §5) | Where it comes from |
|---|---|---|---|---|
| ESD, IEC 61000-4-2 | 0.7–1 ns rise, ≈ 3.75 A/kV first peak | 150 pF / 330 Ω | µJ | handling, pad work |
| EFT, IEC 61000-4-4 | 5/50 ns pulses in 15 ms bursts every 300 ms at 5 kHz (traditional) or 100 kHz; power ports 0.5/1/2/4 kV, signal ports 0.25–2 kV [19] | 50 Ω | 2 kV: 40 A, ≈ 30 µJ per pulse, ≈ 2.2 mJ per 75-pulse burst | relay and contactor arcing on mains and long lines |
| Surge, IEC 61000-4-5 | 1.2/50 µs open-circuit voltage, 8/20 µs short-circuit current, 0.5/1/2/4 kV classes [20] | 2 Ω effective (12 Ω and 42 Ω coupling networks, from knowledge) | 1 kV: 490 A, ≈ 170 mJ | lightning and mains switching: ground station and launch-controller lines ([lightning](../19-regulations-safety/lab-safety-esd-high-power.md#lightning-surge-and-station-grounding)) |
| CS115 | ≈ 30 ns, 5 A, ≤ 2 ns edges | 50 Ω line | ≈ 3 µJ | switching in harnesses |
| Your own pyro turn-off | ring at $1/(2\pi\sqrt{LC_{oss}})$, ≈ 310 V if unclamped | ≈ $\sqrt{L/C}$ | 19 µJ of avalanche in the FET | this section, Example A |

The script integrates the analytic 8/20 µs current, $i\propto t^3e^{-t/3.911\,\mu s}$. The fitted wave has a front of 8.02 µs and a duration of 19.1 µs (1.18 × the 50 % width). One consequence: a 600 W SMBJ-class TVS is rated for a 10/1000 µs pulse and is **not** a 1 kV surge protector. Mains-connected ground-station gear needs a MOV or GDT primary stage, with the TVS as the secondary.

### The math of clamps and snubbers (layered)
**Level 1 — what an inductor does at turn-off.** A current $I$ in a wiring or load inductance $L$ cannot stop instantly. When a switch opens, the current charges whatever capacitance $C$ sits across the switch (the FET's $C_{oss}$, the trace, the cable), and the result is a ring around the supply $V_{dd}$:
$$V_{pk}=V_{dd}+\sqrt{V_{dd}^2+\left(I\sqrt{L/C}\right)^2}\;\approx\;I\sqrt{L/C}\ \text{ for large }I.$$
Here $\sqrt{L/C}$ is the characteristic impedance of the parasitic resonance. The script's ODE gives 35.1 V against 35.2 V from the formula, for 2 A in 25 nH with 157 pF across the switch.

**Level 2 — the four ways to dispose of the energy $\tfrac12LI^2$.**
1. **Freewheel (flyback) diode across the load.** The current circulates through the diode and decays as $e^{-tR/L}$. The switch sees only $V_{dd}+V_f$, but the current falls slowly. Time to zero: $t_0=\tau\ln(1+IR/V_c)$ with $\tau=L/R$ and $V_c$ the total reverse voltage across the coil.
2. **Diode plus Zener, or a TVS across the switch.** The coil is driven by $-(V_c+IR)$, so the current collapses up to 10× faster. The cost is that the switch must withstand $V_{dd}+V_c$, and the clamp absorbs $V_c\int i\,dt$ (≈ $\tfrac12LI^2$, plus the supply's share when the clamp sits across the switch).
3. **Avalanche in the FET.** This is the implicit clamp when nothing else is fitted. The FET absorbs $E_{AV}=\tfrac12LI^2\,V_{BR}/(V_{BR}-V_{dd})$ and the transition is fast and large: a ground-bounce and radiation event.
4. **RC snubber.** This damps the *parasitic* ring, not the load energy. It is the fix for 50–200 MHz ringing on switch nodes, which is a broadband EMI source ([PDN](power-distribution-decoupling-for-rf.md)).

**Level 2b — RC snubber design by ring halving** (the standard bench method; [transient response](../01-circuit-theory/transient-and-step-response.md) states the rule):
1. Measure the ring frequency $f_0$ with a short-ground scope probe ([probing](../17-test-measurement/oscilloscopes-and-probing-for-rf.md)).
2. Add a test capacitor $C_{add}$ across the switch until the frequency falls to $f_1$ (ideally $f_0/2$).
3. Then $C_{par}=C_{add}/((f_0/f_1)^2-1)$, $L_{par}=1/((2\pi f_0)^2C_{par})$, and the damping resistor is $R=\sqrt{L_{par}/C_{par}}$.
4. Choose $C_s\approx3$–$4\,C_{par}$, so that $R$ dominates the snubber's impedance at $f_0$. The snubber dissipates $P=C_sV^2f_{sw}$, independent of $R$.

Worked numbers: ring 80 MHz; 470 pF brings it to 40 MHz, so $C_{par}$ = 157 pF, $L$ = 25.3 nH and $R$ = 12.7 Ω. Use 12 Ω + 680 pF, which dissipates 0.88 mW at 20 kHz PWM from 8.4 V. The simulated turn-off peak falls from 35.1 V to 19.9 V, and the ring after 100 ns falls from 53 V p-p to nothing.

**Level 3 — hot-plug into ceramic capacitors.** Closing a switch from a stiff battery through wiring inductance $L$ into a low-ESR capacitor $C$ forms a series RLC with $\zeta=\tfrac R2\sqrt{C/L}$, and the peak is $V\,(1+e^{-\pi\zeta/\sqrt{1-\zeta^2}})$. With 0.5 µH of loop, 30 mΩ of total resistance, and 10 µF X7R derated to ≈ 5 µF, ζ = 0.047. A 2S pack (8.4 V) then rings to **15.6 V**, and a 3S pack (12.6 V) to **23.5 V**. Both are dangerous for 16 V and 20 V regulators. LTC AN88 describes the same effect [21]. The fix is a damping branch: a bulk electrolytic or polymer capacitor whose ESR is ≈ $\sqrt{L/C}$ = 0.32 Ω, with $C_d\gtrsim4C$. The simulated peak becomes 10.5 V (2S) or 15.7 V (3S). A TVS at the input and a soft-start load switch are alternatives. Contact bounce in the arming switch repeats the event several times.

### Worked example A — pyro and servo outputs on a 2S flight computer
**Pyro channel.** Assume 8.4 V, a low-side logic FET ($C_{oss}$ ≈ 300 pF, $V_{BR}$ ≈ 35 V), a 1 Ω bridgewire and 1.4 Ω of loop resistance, giving **6 A**. Wiring inductance is 0.3 µH on the battery side and 0.5 µH in the igniter leads.
- **Timed pulse ends while current still flows** (for example, the bridge has not burned open or has welded short). The stored 14.4 µJ would ring to $I\sqrt{L/C_{oss}}$ ≈ 310 V. In practice the FET avalanches at ≈ 35 V and absorbs 19 µJ in 180 ns, a slope of 33 A/µs. The FET survives this (single-pulse ratings are tens of mJ). The problem is a 27 V, 30 A/µs event in the middle of the board, next to the IMU and baro ground returns.
- **The fix.** Put a Schottky freewheel diode across each pyro output connector (cathode to the pyro supply). The lead current then circulates in the diode and the bridge, with τ = L/R ≈ 0.5 µs. Add ≥ 10 µF of bulk at the pyro supply node, beside the FET, so that the battery-side inductance lifts the rail only by $I\sqrt{L_b/C}$ ≈ 1.0 V. If the bridge burns open first, the lead energy is dumped into the igniter's own arc gap. The diode cannot help with that, but by then the igniter has fired.
- **Keep the RF rules separate.** The pyro outputs still need the RF filtering and lead twisting from Level 3 above, plus the HERO margin and test in [lab safety](../19-regulations-safety/lab-safety-esd-high-power.md). Transient clamps do not provide RF safety.

**Servos.** Hobby servos contain their own H-bridge with body diodes. The flight computer's problems are on the supply side:
- stall and start currents of the order of 1–3 A per servo (typical, check the servo data) cause brown-outs;
- a back-driven or decelerating servo **regenerates** into its rail. Through an ideal diode or a regulator that cannot sink current, the rail rises.
- The rule: a separate servo regulator or rail; bulk capacitance plus a unidirectional TVS (or a shunt clamp) on that rail; and an LC or bead filter before any sensor LDO that shares the battery.
- When the flight computer switches servo power with a FET, treat the harness as an inductive load: snubber plus clamp, as above.

**Solenoids, relays and brushed motors** (valves, cutters, deployment motors). Take 10 mH and 12 Ω at 8.4 V (0.70 A):
- With a Schottky diode alone the current takes **1.63 ms** to fall to 10 %. This delays valve closure or relay release.
- A diode plus a 24 V Zener cuts that to **0.22 ms**. The switch then sees 33 V (use a ≥ 40 V FET), and the clamp absorbs ≈ 2 mJ.

### Contact protection, arming switches and separation connectors
Mechanical contacts that break current draw an arc whenever the circuit's voltage and current exceed the contact material's minimum arc voltage and current. For common contact metals that is roughly ≥ 10–12 V and ≥ 0.4 A (from knowledge; check the relay data sheet). The arc is a broadband source and erodes the contacts. Practice on a rocket:
- **Make the arming switch carry logic or gate current, not load current.** It should enable a FET or a load switch, with soft start. This also removes the hot-plug overshoot.
- **Diode across DC inductive loads** switched by relays; an RC across the contacts for AC or bidirectional loads.
- **Umbilicals and separation connectors.** Never let them break a live servo, heater or pyro current. Sequence the loads off in firmware first. Otherwise the break is the inductive turn-off above, through a connector pin.
- **Launch-controller firing lines** (tens of metres to the pad) are long antennas for lightning and switching surges. Clamp them at both ends (GDT/TVS) and twist them ([lightning](../19-regulations-safety/lab-safety-esd-high-power.md#lightning-surge-and-station-grounding)).

### A transient test menu for a Space Bar flight computer (borrowed, own levels)
1. **Hot-plug** the flight battery through the real arming switch 20 times while scoping the input rail (single-shot, 100 MHz bandwidth). Pass if peak < 80 % of the lowest absolute-max rating on the rail.
2. **Pyro fire into a dummy** (1 Ω plus the real leads). Scope the FET drain and the 3.3 V rail, and log sensors at full rate. Pass if there are no resets, no I²C/SPI errors and no IMU/baro step larger than the noise.
3. **Servo stall and slam.** Drive the servos to stops and back-drive them by hand while scoping the servo rail and the MCU rail.
4. **CS114-like pickup.** Key every transmitter at maximum power in flight configuration and log everything ([interference hunting, av-bay test](../17-test-measurement/interference-hunting-and-rf-immunity.md)).
5. **ESD.** Zap the connectors, switch and case with an ESD gun if one can be borrowed, or a 150 pF / 330 Ω RC discharge from a known voltage. The board must keep logging. Fix the pass criteria before testing (pre-registration, as in the [validation test campaign](../20-projects-recipes/validation-test-campaign.md)).

## Conducted and radiated pre-compliance
*Added 2026-10-13 (W5-S16, G-13-03). Numbers from `tools/verify/s16_precompliance.py`. Near-field probing is in Worked example 4 above, and source hunting in [interference hunting](../17-test-measurement/interference-hunting-and-rf-immunity.md); this section adds the LISN, the antenna-factor pre-scan and the failed-test workflow.*

### Conducted emissions with a LISN
A **LISN** (line impedance stabilisation network; CISPR calls it an artificial network, AN) does three things. It gives the device under test (DUT) a defined RF source impedance, whatever the bench supply happens to be. It blocks noise coming from the supply. And it delivers the DUT's noise voltage to a 50 Ω receiver port. Two kinds are in use:

| Network | Used by | Line inductance | Impedance seen by the DUT (script §1) | Use it for |
|---|---|---|---|---|
| 50 µH (+ 5 Ω) V-network | CISPR 16/32 mains, FCC §15.107, MIL-STD-461 CE102 [11][22] | 50 µH | 36 Ω at 150 kHz, 48 Ω at 0.5 MHz, 50 Ω above 1 MHz | mains-powered ground-station supplies and chargers; MIL-style DC tests |
| 5 µH AN | CISPR 25 (vehicle components, 150 kHz–108 MHz voltage method), DO-160 [23][24] | 5 µH | 5.7 Ω at 150 kHz, 25 Ω at 1 MHz, ≈ 50 Ω above 5 MHz | battery-powered boxes on short harnesses, i.e. a flight computer |

**Set-up.**
- Place the DUT and LISN on a ground plane (a copper or aluminium sheet), with the DUT on 50 mm of insulation. Bond the LISN case to the plane.
- Keep the supply leads from LISN to DUT at a fixed length. Under CISPR 25, one LISN in the positive line suffices if the DUT's return to chassis is shorter than 20 cm; otherwise use one per line [24].
- Terminate the unused LISN port in 50 Ω.
- Put a **transient limiter** (and/or a 10–20 dB pad) between the LISN port and the analyser. Switching the DUT on or off dumps a large transient into the port, a classic way to kill a tinySA front end.
- **Mains LISNs leak milliamps to protective earth through their capacitors.** Never defeat the PE connection. Use an RCD-protected outlet, or an isolation transformer feeding the *DUT side* (never "float" the analyser) ([lab safety](../19-regulations-safety/lab-safety-esd-high-power.md)).

**Limits.** CISPR 32 Class B mains conducted limits [22]:

| Band | QP limit | AV limit |
|---|---|---|
| 0.15–0.5 MHz | 66 → 56 dBµV (falling linearly in log f) | 56 → 46 dBµV |
| 0.5–5 MHz | 56 dBµV | 46 dBµV |
| 5–30 MHz | 60 dBµV | 50 dBµV |

CISPR 25 has its own class 1–5 limits for vehicle components (not reproduced here). For the av-bay, the useful comparison is with your own receivers.

**Worked example — a 2 MHz buck on the flight-computer input** (8.4 V → 3.3 V, 1 A, D = 0.39; 10 µF X7R input capacitor ≈ 5 µF at bias; 50 µH LISN):
- The input current is a pulse train. Its fundamental is $\tfrac{2I}{\pi}\sin(\pi D)$ = 0.60 A, and only the fraction $Z_{C_{in}}/(Z_{C_{in}}+Z_{LISN})$ reaches the LISN.
- Result: **76 dBµV at 2 MHz, ≈ 30 dB over** the 46 dBµV Class B average limit. The 10th harmonic is still 9 dB over, because of the capacitor's ESL.
- A 1 µH + 10 µF LC input filter (resonant at 50 kHz) brings the 2 MHz line to **7 dBµV, ≈ 39 dB under**.
- The undamped filter's output impedance peaks at **4.35 Ω**. A 0.5 Ω + 47 µF damping leg reduces that to 0.45 Ω, well below the converter's negative input resistance $V^2/P_{in}$ ≈ 19 Ω. This is Middlebrook's condition for a filter that does not destabilise the converter.
- The model treats the switching current as an ideal pulse train, with no CM path through the inductor's or FET's capacitance to chassis. Real CM noise above ≈ 10 MHz needs a CM choke or Y-capacitors, and shows up when the DM/CM components are measured separately: $V_{CM}=(V_1+V_2)/2$, $V_{DM}=(V_1-V_2)/2$ from two LISNs, or with a DM/CM splitter.

### Radiated pre-scan with an LPDA and its antenna factor
**Antenna factor** (field per volt at the 50 Ω port): $AF = 20\log f_{MHz}-G_{dBi}-29.77$ dB/m. This is the same constant as [decibels](../00-math-foundations/decibels-and-log-units.md) and [antenna measurement](../08-antennas/antenna-measurement.md); the script checks −29.774 dB from $\sqrt{4\pi\eta_0/50}/c$. A 6 dBi log-periodic has AF 13.8 / 17.0 / 24.2 dB/m at 300 / 433 / 1000 MHz. Calibrated antennas come with a measured AF table. Use it rather than the formula, which ignores mismatch and near-field effects at 3 m.

$$E\ [\mathrm{dB\mu V/m}] = V_{rx}\ [\mathrm{dB\mu V}] + AF + L_{cable} - G_{preamp},\qquad V\,[\mathrm{dB\mu V}]=P\,[\mathrm{dBm}]+107.$$

**Example.**
- A tinySA reading of −85 dBm (22 dBµV) at 400 MHz, through 1 dB of cable from a 6 dBi LPDA at 3 m, gives E = 22 + 16.3 + 1 = **39.3 dBµV/m**.
- FCC §15.109 Class B at 3 m is 46.0 dBµV/m for 216–960 MHz [4]: a 6.7 dB margin.
- CISPR 32 Class B is 37 dBµV/m at 10 m [22]. Scaled to 3 m with 20 log(10/3) = +10.5 dB, that is ≈ 47.5 dBµV/m. The scaling assumes the far field; labs use a 3 m limit table where the standard allows it.

**What makes a home pre-scan lie.**
1. **Ground reflection.** Labs scan the antenna height from 1 to 4 m and record the maximum. For an EUT at 0.8 m, 3 m away over metal, a fixed 1 m antenna reads 3.3 dB low at 100 MHz and 4.3 dB low at 500 MHz, but 0 dB at 300 and 900 MHz (script §4). Without a ground plane, the reflection is uncontrolled.
2. **Detector and bandwidth.** CISPR uses 9 kHz (150 kHz–30 MHz), 120 kHz (30–1000 MHz) and 1 MHz above 1 GHz, with quasi-peak and average detectors. Peak ≥ QP ≥ AV, so a peak reading that passes, passes. A 100 kHz analyser RBW under-reads broadband noise by 0.8 dB (impulsive noise by 1.6 dB). CW clock harmonics need no correction.
3. **Ambient signals.** FM, DAB, TV, cellular and Wi-Fi sit above the limits. Sweep with the DUT off first and keep the plot. Unknown peaks that stay when the DUT is off are not yours.
4. **Cables.** The radiator is usually the cable ([Level 1](#level-1--otts-emission-estimates-and-the-currents-they-allow)). Lay out cables as the lab will, and record their routing.
5. **Uncalibrated everything.** Treat absolute results as ±6 dB and aim for ≥ 6 dB margin. Comparisons before and after a change, in the same set-up, are good to ≈ 1 dB.

**Current-probe shortcut.** Clamp a current probe (with transfer impedance $Z_t$ in dBΩ) on each cable. Then $I_{cm} = V - Z_t$ (dBµA) and $E \approx 1.26\times10^{-6}fLI_{cm}/r$. A 10 dBµV reading with $Z_t$ = 0 dBΩ at 100 MHz is 3.2 µA on 1 m, i.e. **42.1 dBµV/m at 3 m against the 43.5 dBµV/m limit**. That matches the ≈ 3.7 µA allowance in the Level 1 table. This is the fastest way to rank cables.

### From a failed test to a fix — workflow
1. **Get the data, not just the verdict.** Ask the lab for the frequency, detector, polarisation, antenna height, turntable angle, cable layout photos and margin of every failing point. Book time to debug on site if you can.
2. **Name the source from the frequency.** Divide the frequency by each clock (MCU crystal, SD, USB, SPI, switcher $f_{sw}$, LoRa TCXO) and look for integer harmonics ([harmonic table](#2-is-my-esp32s-40-mhz-clock-a-problem-for-920-mhz-lora-in-singapore), script `pcb_emc_radiation.py` §4). Broadband humps usually come from switchers or ringing; spaced comb lines from clocks.
3. **Board or cable?** Unplug or ferrite each cable in turn and watch the reading in the same set-up. If the emission follows a cable, it is common mode, and the fix belongs at that connector.
4. **Localise on the board** with near-field probes (Worked example 4), then confirm by slowing or disabling the suspect (firmware: lower drive strength, stop the SD clock, disable SSC or turn it on).
5. **Apply fixes in order of cost**, and re-measure each one *relative to the same baseline*:

| Fix | Typical gain | Note |
|---|---|---|
| clamp-on ferrite / CM choke on the offending cable | 6–20 dB | needs ≥ 100–1000 Ω CM; [ferrites](../04-real-components-hf/ferrites-and-beads.md) |
| filter at the connector (C to chassis/ground + bead) | 10–30 dB | must be at the boundary |
| series R / lower drive strength on the clock | 6–14 dB above the corner | Level 2 |
| spread-spectrum clock on | 4–16 dB (bandwidth-dependent) | Level 2 |
| stitching / closing a slot under the clock | 10–20 dB | [grounding](grounding-and-return-paths.md) |
| move the channel or clock frequency | removes a narrowband hit | Worked example 2 |
| gasket / more screws on the enclosure seam | 10–30 dB | [shielding](shielding-and-isolation.md#enclosures-doors-meshes-and-fabrics) |

6. **Document** the change, the before/after plots and the remaining margin. Retest at the lab with the same cable layout.

### Budget pre-compliance kit (approximate 2026 US retail; check before buying)
| Item | Approx. cost | Notes |
|---|---|---|
| tinySA Ultra (100 kHz–5.3 GHz) | ≈ US$130 | already the team's SA ([lab budget](../17-test-measurement/lab-setup-by-budget.md)) |
| near-field probe set (H loops + E stub), or home-made shielded loops | ≈ US$30–240 (TekBox TBPS01 ≈ US$240) [25] | rank sources, verify fixes |
| 5 µH DC LISN (TekBox TBOH01) | ≈ US$250–300 [25] | flight computer / battery DUTs; two for DM/CM separation |
| transient limiter (TekBox TBFL1) | ≈ US$330–360 [25] | or a 20 dB pad plus "power the DUT before connecting" discipline |
| RF current clamp (TekBox TBCP1) | ≈ US$360–480 [25] | cable CM current |
| PCB log-periodic antennas (e.g. ≈ 400 MHz–1 GHz and 0.85–6.5 GHz boards) | ≈ US$20–60 (from knowledge) | pre-scan, with an AF from a calibration against a known source or the formula |
| ground plane, 50 mm foam, tripod, 3 m tape | ≈ US$50 | repeatable geometry is worth more than calibration |

## Practical notes
- **Filter at the board boundary**: every cable entry gets a filter referenced to the board ground right at the connector (C to ground, bead or CM choke in series). A filter in the middle of the board lets the noise couple around it.
- **CM chokes** on USB, CAN and harness wiring; bifilar-wound or chip CM chokes for differential pairs; clamp-on ferrites (mix 31/43 for 1–300 MHz) on flying leads ([baluns and CM chokes](../08-antennas/antenna-matching-and-baluns.md)).
- **Antenna coax as a CM radiator**: an unbalanced antenna fed without a balun puts current on the braid; that braid then runs past the flight computer. Use a choke/sleeve balun at the antenna and route coax away from sensors.
- **Switching regulators**: small hot loop (input cap–FET–diode), shielded inductor, snubber if ringing, and keep the SW node copper small ([PDN](power-distribution-decoupling-for-rf.md)).
- **Spread spectrum**: many regulators and MCUs offer SSC; check the receiver-in-band benefit with the FFT numbers above.
- **Immunity fixes for analog/audio-band circuits** (the "GSM buzz" problem): a bursty transmitter (GSM's 217 Hz frame rate, a LoRa packet rate, a 2 W telemetry burst) is rectified at the first junction it reaches (op-amp input, ESD diode, transistor base) and appears as its *envelope* — a buzz in audio, an offset or step in a sensor reading, a glitch on a slow digital line. Fixes, in order: keep RF out of the input — series R (100 Ω–1 kΩ) plus a shunt C (100 pF–1 nF, C0G, at the pin, grounded right there) on every input and on long feedback/supply leads; ferrite beads where cables enter; shielded twisted pairs with the shield bonded at the entry; small loop areas; then reduce the source (distance, antenna placement, TX power). Class-D/switching amplifiers and SMPS are emitters as well as victims: output LC filters, short speaker leads, CM chokes and slow edges.
- Field procedures for hunting noise sources, RCD/GFCI trips, Ethernet chokes, proving a fix, and an av-bay immunity test: [interference hunting and RF immunity](../17-test-measurement/interference-hunting-and-rf-immunity.md).
- **Regulatory**: rocket avionics are not usually certified as products, but ground stations and radios must meet band rules (IMDA/FCC) — see [certification](../19-regulations-safety/certification-fcc-ce-imda.md).

## Common mistakes & misconceptions
- **"The PCB radiates"** — mostly the cables do, driven by board ground noise.
- **"A ferrite bead fixes EMI"** — on a low-impedance node a bead does little; it needs a shunt path (capacitor) and a place to put the energy.
- **Assuming SSC gives 10 log(spread/RBW)** — ≈ 4 dB optimistic for triangle modulation.
- **Treating pyro RF safety as a DC problem** — continuity and arming logic don't protect against RF pickup on leads.
- **Using generic 3–30 pF TVS diodes on antenna ports.**
- **Choosing a LoRa channel on a clock harmonic** (e.g. 920.000 MHz with a 40 MHz clock).
- **"A flyback diode protects the FET from the pyro lead's inductance when the bridge opens."** The diode protects against the *board and battery-side* inductance and recirculates the lead current while the bridge is intact. When the bridge burns open, the lead energy goes into the igniter's gap. Put the diode at the connector and the bulk capacitor at the switch.
- **A bare diode on a solenoid or valve "because that's the rule."** It is safe, but release is slow (1.6 ms vs 0.2 ms in the example). Add a Zener and rate the switch for $V_{dd}+V_z$.
- **"Ceramic input capacitors are always better."** Hot-plugged ceramics ring to nearly 2× the battery voltage. Add a lossy bulk capacitor or a soft-start load switch.
- **Using an SMBJ (10/1000 µs-rated) TVS as a mains-surge protector.** A 1 kV, 2 Ω surge delivers ≈ 490 A. That needs a MOV or GDT stage in front.
- **Quoting MIL-STD-461 or DO-160 levels as requirements for a hobby rocket.** They are tied to platform categories and contracts. Borrow the method, and set the level from your own environment (your TX field, your harness currents).
- **Connecting a LISN port straight to an analyser.** Power switching transients destroy front ends. Use a limiter or pad and switch the DUT with the analyser disconnected.
- **Trusting a single-height, uncalibrated radiated scan for pass/fail.** It reads up to ≈ 4 dB low at some frequencies, and the ambient may mask the DUT. Use it for *relative* fixes, and keep ≥ 6 dB margin.
- **Adding an LC input filter without damping.** The undamped filter's impedance peak (4.35 Ω in the example) can destabilise the switcher's control loop.

## How to simulate / verify
- `python3 tools/verify/pcb_emc_radiation.py` (≈ 2 s): DM/CM constants from dipole superposition; allowed currents vs FCC limits; clock-harmonic envelopes and edge rates; harmonic-landing table for 17 clocks and 8 receiver bands; FFT of SSC harmonics; pyro-lead pickup bounds; RF rectification; ESD/TVS return loss.
- NEC or openEMS for a cable driven in common mode by a board ([NEC modelling](../16-simulation-tools/nec-antenna-modelling.md)).
- Bench: near-field probes + tinySA/SDR; CM current clamp; receiver RSSI noise floor with subsystems toggled (the most direct desense test).
- `python3 tools/verify/s16_snubber_transients.py` (seconds): ring-halving snubber design + ODE turn-off with/without snubber; pyro FET turn-off spike, avalanche energy, freewheel + bulk; solenoid decay (diode/Zener/TVS); LiPo hot-plug overshoot and damping (ODE vs closed form); surge/EFT energy with the analytic 8/20 µs wave (all checks pass; output in `s16_snubber_transients_output.txt`).
- `python3 tools/verify/s16_precompliance.py` (instant): 50 µH and 5 µH LISN impedance; buck DM emission vs CISPR 32 Class B, with filter and damping (Middlebrook peak); AF constant and pre-scan arithmetic; two-ray fixed-height error; current-probe → field.
- SPICE alternative: an ngspice `.tran` of the pyro loop with a FET model including $C_{oss}$ and avalanche, to replace the ideal-capacitor model.

## Open questions / gaps
- The pyro pickup model is an order-of-magnitude bound (far-field formula inside the radiating near field; idealised matched dipole). A measured test — thermocouple or RF current probe on a dummy bridge 0.1–0.5 m from the flight antenna — would give Space Bar a real margin number; recommended before flight.
- E-match no-fire data are from a hobby page; get manufacturer specs for the igniters actually flown.
- CISPR 32 limits (30/37 dBµV/m at 10 m for Class B) are quoted from knowledge, not re-fetched.
- The BMP390-telemetry interference thread on the Rocketry Forum could not be fetched (403); the mechanism is inferred, not confirmed.
- MIL-STD-461G and DO-160G texts were not fetched (403 / parse errors). Test-method names, ranges and CS115 parameters come from two or more lab/vendor summaries. The CS116 peak-current curve, RS103 Table XI levels, CS118 levels and DO-160 Section 22 level tables are **not verified**. MIL-STD-461H (Apr 2026) changes were not reviewed. CE101/CE106/RE101/RE103/RS101 ranges are from knowledge.
- IEC 61000-4-5's 12 Ω and 42 Ω coupling impedances and the contact minimum arc voltage and current are from knowledge.
- The buck conducted-emission model is DM only, with an ideal pulse current. Measure CM separately.
- The pyro transient numbers assume an ideal-capacitor FET and lumped wiring inductance. A scope measurement on the real board (100 MHz probe, short ground) is the real test (menu item 2).

## Sources
1. H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley 2009, ch. 12 (digital circuit radiation: DM 263 × 10⁻¹⁶ f²AI/r, CM 12.6 × 10⁻⁷ fLI/r; trapezoid spectra; ~8 µA at 30 MHz example), ch. 3, 15 (grounding, ESD). (textbook; from knowledge, constants re-derived here)
2. C. R. Paul, *Introduction to Electromagnetic Compatibility*, 2nd ed., Wiley 2006, ch. 3 (spectra of digital waveforms), ch. 8 (DM/CM emission models). (textbook; from knowledge)
3. U.S. DoD, MIL-STD-464C, *Electromagnetic Environmental Effects Requirements for Systems*, 1 Dec 2010, §5 and App. A (EIDs: 16.5 dB below MNFS for safety, 6 dB otherwise; MNFS definition; 1 A/1 W EIDs; derivation from 15 % of no-fire current). https://www.ema3d.com/wp-content/uploads/downloads/MIL-STD-464C.pdf (standard)
4. 47 CFR §15.109, radiated emission limits for unintentional radiators (Class B at 3 m: 100/150/200/500 µV/m; Class A at 10 m: 90/150/210/300 µV/m), https://www.law.cornell.edu/cfr/text/47/15.109. (regulation)
5. "Electrical current requirements of model rocket igniters," privatedata.com hobby page (Q2G2 all-fire 333 mA/100 ms, no-fire 130 mA/5 s) — via search summary. (hobby — anecdotal, unverified)
6. IEC 61000-4-2, *Electrostatic discharge immunity test* (levels and current waveform; values as commonly quoted). (standard; from knowledge)
7. u-blox, *MAX-M5Q Hardware Integration Manual* UBX-13002460 R06, §5.3 — ESD protection with < 0.5 pF TVS on RF_IN; EMI: unshielded lines > 3 mm act as antennas, series R > 20 Ω / ferrite BLM15HD102SN1 / 47 nH on lines; in-band jamming from MCU/display/bus harmonics. (app note)
8. "TinySA Ultra: a low-cost spectrum analyzer that fits in your pocket," Test & Measurement Tips (and vendor listings) — 100 kHz–5.3 GHz (6 GHz ultra mode), RBW 200 Hz–850 kHz, built-in LNA. (trade article/vendor)
9. D. Hardin, J. Fessler, D. Bush, "Spread spectrum clock generation for the reduction of radiated emissions," *Proc. IEEE Int. Symp. EMC*, 1994 — SSC principle and modulation profiles. (peer-reviewed conference; from knowledge)
10. Verification script `tools/verify/pcb_emc_radiation.py` (this page).
11. MIL-STD-461G test-method ranges and LISNs as summarised by Com-Power, *Aerospace & Defense MIL-STD-461 EMC* tech note, https://www.com-power.com/uploads/technote/Aerospace_Defense_MIL-STD-461_EMC.pdf; Nemko, TÜV SÜD and ATEC MIL-STD-461 service pages (CE102 10 kHz–10 MHz 50/5 µH LISN; CS101 30 Hz–150 kHz; CS114 10 kHz–200 MHz; RE102 10 kHz–18 GHz; RS103 2 MHz–40 GHz; 200 V/m typical maximum). (test-lab/vendor summaries of a standard)
12. Interference Technology, "Introduction to MIL-STD-461G" (G adds CS117 lightning indirect and CS118 personnel ESD, removes CS106; 11 Dec 2015) and search listing of MIL-STD-461H (17 Apr 2026, supersedes G). https://interferencetechnology.com/introduction-to-mil-std-461g/ (trade article)
13. Interference Technology, "Review of MIL-STD-461 CS115 impulse excitation, CS109, RS105" (2 ns transition, 30 Hz, 1 min, 50 Ω calibration fixture; RS105 ≥ 50 kV/m); Solar 9355-1 pulse generator data sheet (5 A, ≈ 30 ns, 30 p.p.s.); VectorNav MIL-STD primer (5 A for 30 ns at 30 Hz, 1 min). (trade article / vendor)
14. TÜBİTAK UME CS114/CS115/CS116 notes and ATEC MIL-STD-461G CS116 procedure (test frequencies 10 kHz–100 MHz; ≤ 1 pulse/s) — via search summaries. (lab notes; partly unverified)
15. Interference Technology, "Introduction to MIL-STD-461 RS101–RS103" (levels 1–200 V/m by platform; Table XI) — via search summary. (trade article)
16. Wikipedia, "DO-160" (section list; Rev G Dec 2010, Change 1 Dec 2014), https://en.wikipedia.org/wiki/DO-160 (encyclopedia; section titles cross-checked with lab pages)
17. ATEC / TÜV SÜD / Applus DO-160 service pages (§16 unique in covering emissions and susceptibility; §20 ≈ CS114/RS103; §21 conducted 150 kHz–150 MHz, radiated 100 MHz–6 GHz; ED-14G identical). (test-lab summaries)
18. AVI3000 *Indirect lightning testing* note; Holt HI-8450 DO-160G report; Interference Technology DO-160 pin-injection articles (WF3 1/10 MHz, WF4 6.4/69 µs, WF5A 40/120 µs; sets A/B/Z). (vendor/trade)
19. AMETEK CTS, "IEC 61000-4-4 EFT" (5 kHz traditional vs 100 kHz; levels 0.5–4 kV power, 0.25–2 kV signal); TI blog "Get certified, not certi-fried" (5/50 ns, 15 ms bursts every 300 ms). (vendor app notes)
20. Wikipedia "IEC 61000-4-5" and TI AN on surge (1.2/50–8/20 combination wave, 2 Ω effective, classes 0–4 = 25 V–4 kV; 10/700 µs telecom wave). (encyclopedia / app note)
21. Linear Technology Application Note 88, *Ceramic input capacitors can cause overvoltage transients* (hot-plug overshoot to ≈ 2× the supply; damping with an electrolytic). (app note; from knowledge, numbers re-derived here)
22. CISPR 32 / EN 55032 Class B limits as tabulated by TI SLYY202 and I.B.L. glossary (conducted 66–56/56/60 QP, 56–46/46/50 AV dBµV; radiated 30/37 dBµV/m QP at 10 m). (app note / lab summary)
23. TekBox TBL0550-1 5 µH LISN manual and TI SLLA569 (CISPR 25 voltage method 0.15–108 MHz; current probe to 245 MHz; 5 µH + 50 Ω AN). https://ti.com/lit/pdf/slla569 (vendor manual / app note)
24. TekBox 5 µH LISN manual (one LISN if the return to chassis < 20 cm, else two; unused port 50 Ω). (vendor manual)
25. TestEquity and Tequipment TekBox listings (TBOH01 US$249–299, TBFL1 US$329–359, TBCP1 US$359–479, TBPS01 US$239), read 2026-10-13. (retail; prices change)
26. R. D. Middlebrook, "Input filter considerations in design and application of switching regulators," IEEE IAS Annual Meeting, 1976 (filter output impedance ≪ converter negative input resistance). (peer-reviewed conference; from knowledge)
27. Verification scripts `tools/verify/s16_snubber_transients.py` and `tools/verify/s16_precompliance.py` (W5-S16).
