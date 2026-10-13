---
title: Mixed-signal layout for radio boards — ADC grounding, digital noise into LoRa and GNSS (desense), clock and bus routing, keeping USB/SD/switchers away from receivers, SPI/clock termination and crosstalk budgets (NEXT/FEXT, saturation length, guard traces)
domain: 13-pcb-rf-layout-emc
slug: mixed-signal-layout
tags: [mixed-signal, ADC, AGND, DGND, partitioning, desense, self-interference, clock-harmonics, GNSS-jamming, C/N0, SPI, UART, I2C, SD-card, USB, switching-regulator, series-termination, edge-rate, flight-computer, ESP32-S3, Teensy, termination, series-termination, AC-termination, Thevenin, crosstalk, NEXT, FEXT, saturation-length, guard-trace, 3W-rule, multi-drop]
prerequisites:
  - grounding-and-return-paths.md
  - emc-emi-fundamentals.md
related:
  - power-distribution-decoupling-for-rf.md
  - shielding-and-isolation.md
  - rf-layout-rules.md
  - vias-stitching-fencing.md
  - rf-pcb-review-checklist.md
  - ../05-analog-electronics/data-converters-adc-dac.md
  - ../07-noise-linearity/dynamic-range-sfdr-blocking.md
  - ../08-antennas/gnss-antennas.md
  - digital-termination-and-crosstalk.md
  - ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Mixed-signal layout for radio boards

## Questions this page answers
- Should my flight computer have separate analog, digital and RF ground planes?
- How do I connect an ADC's AGND and DGND pins, and where does the converter go?
- Which digital clocks and buses put harmonics into 433 MHz, 915/920 MHz or GNSS L1?
- How weak does a spur have to be to not desensitise my LoRa or GNSS receiver?
- How much isolation do I need between a clock trace and the receiver, and how do I get it?
- How should SPI/UART lines to a radio module be routed?
- Where should USB, the SD card and switching regulators go relative to the GNSS antenna?
- How do I tell if my GNSS is being jammed by my own board?
- Does my SPI clock need a termination resistor, and what value?
- Why does my SPI bus double-clock when I add a second sensor on the same SCK line?
- How much crosstalk does an SPI clock put on the trace next to it, and what is "saturation length"?
- Do guard traces actually help, and does the 3W rule hold on a 4-layer JLC board?

## TL;DR
- **One solid ground plane; partition by placement and routing, not by splitting the plane** (Ott, ADI, TI) [1][2][3]. Group RF, analog-sensor and digital areas so that no digital return current has a reason to flow under RF or sensitive analog parts ([grounding](grounding-and-return-paths.md)).
- **ADC AGND/DGND**: tie both to the (single) ground plane right at the converter; the names describe the chip's internals [2]. Decouple the converter's digital supply to the same plane, and buffer/series-terminate its digital outputs so their edge currents stay small.
- **Desense thresholds** (script §1): LoRa 125 kHz noise floor ≈ −117 dBm (NF 6 dB); GNSS L1 C/A ≈ −109 dBm (NF 2 dB, 2 MHz). For ≤ 1 dB desense a spur must be ≤ ≈ −123 dBm (LoRa) / −115 dBm (GNSS) **at the receiver input**. GNSS tolerates jammers only ≈ 6–12 dB above thermal noise before tracking suffers (1–2-bit quantisation) [4].
- **Required isolation from digital harmonics** (script §2): a 40 MHz clock's 23rd harmonic at 920 MHz with 1 ns edges (≈ −20 dBm source) needs **≈ 103 dB** to the LoRa input; an SD 25 MHz clock's 63rd harmonic at 1575 MHz (1 ns edges, ≈ −33 dBm) ≈ 82 dB to the GNSS input — 68 dB with 5 ns edges.
- **What layout gives** (script §3): fringing-field decoupling on 0.21 mm prepreg ≈ 39/55/67 dB at 2/5/10 mm (only 9/22/33 dB on a 2-layer board); one via-fence row ≈ 29 dB at 1.575 GHz; a can seam ≈ 26 dB; antenna-to-antenna free-space loss only 10–36 dB at 5–100 cm. **100 dB needs several measures in series.**
- **Known collisions** ([EMC](emc-emi-fundamentals.md) script §4): 40 MHz × 23 = 920.000 MHz (ESP32 crystal/APB) inside SG 920–925 MHz; 25 MHz × 63 = 1575.000 MHz (SD, Ethernet) and 8 MHz × 197 = 1576 MHz inside L1 C/A; 12 MHz × 77 = 924 MHz (USB PHY); many clocks × n = 1600 MHz (GLONASS) and 1560 MHz (BeiDou).
- **Bus edges**: SPI at 40 MHz puts ≈ 78 dBµV (envelope) at L1 with 1 ns edges; 10 ns edges are ≈ 20 dB quieter (script §5). Use the slowest drive strength the MCU allows and 22–47 Ω series resistors at the driver.
- **Termination and crosstalk** ([§ budgets](#termination-and-crosstalk-budgets-for-spi-and-clocks), `s16_crosstalk.py`): with 1 ns edges any trace longer than **29 mm** is a transmission line (0.2 mm on JLC-7628 L1: Z0 67 Ω, v 0.576 c). An unterminated 100 mm SCK overshoots by **+1.18 V**; **33–39 Ω at the driver** removes it. Saturated NEXT is **9.0 / 4.2 / 2.3 / 1.0 %** at 0.2 / 0.4 / 0.6 / 1.0 mm gaps, reached beyond **$L_{sat}=vt_r/2$ = 86 mm** (1 ns). Microstrip FEXT is negative and grows with length. A *stitched* guard cuts NEXT 2.4×; a floating one does nothing.
- **Placement**: GNSS antenna and module at one end, away from the MCU, SD, USB and switchers; switcher hot loops tiny, inductors shielded; digital buses on inner layers between planes; a remote active GNSS antenna (> 1 m from electronics) largely removes the problem [4].

## Intuition (no math)
A flight computer is a radio receiver sharing a small board with a computer. The computer's clocks are square waves with nanosecond edges, so their harmonics extend to several GHz; every fast trace, every IC's power pins and every cable carries a little of that energy. GNSS signals arrive ≈ 15 dB *below* the thermal noise floor, and LoRa works down to ≈ 20 dB below it — so even harmonics far too weak to fail an EMC test can **desensitise your own receivers**. EMC regulations mostly stop at 1 GHz, so a "compliant" board can still jam its own GNSS [4].

Mixed-signal layout is the art of keeping three kinds of current from meeting: **large, fast digital currents** (MCU, memory, SD, USB, switchers), **sensitive analog currents** (sensors, ADC references, crystals) and **RF** (LNA inputs, antennas). The tools are: (1) a solid ground plane so every current returns under its own trace; (2) placement, so the currents' paths don't overlap; (3) slow edges and filtered I/O, so less energy is generated; (4) distance, fences and cans, so less of it couples; (5) frequency planning, so the remaining harmonics fall between the receive channels.

## The math

### Level 1 — desense: how weak is weak enough?
Receiver noise floor $N=-174+10\log_{10}B+NF$ dBm. An in-band interferer of power $I$ that behaves like noise raises the floor by $10\log_{10}(1+I/N)$: −10 dB → 0.4 dB, −6 dB → 1.0 dB, 0 dB → 3.0 dB, +10 dB → 10.4 dB (script §1). A CW spur inside a LoRa channel is partly rejected by the chirp despreading, but for a design budget treat it as noise.

| Receiver | B | NF | Noise floor | spur for ≤ 1 dB desense |
|---|---|---|---|---|
| LoRa (SX126x / LLCC68) | 125 kHz | 6 dB | −117 dBm | ≤ −123 dBm |
| GNSS L1 C/A | 2.046 MHz | 2 dB (system) | −109 dBm | ≤ −115 dBm |

### Level 2 — isolation needed from a clock harmonic
Harmonic envelope of a trapezoidal clock ([EMC page](emc-emi-fundamentals.md)): $|c_n|\le2Ad\cdot\min(1,1/\pi nd)\cdot\min(1,T/\pi nt_r)$. Expressed as an equivalent 50 Ω source power, the required isolation is source minus allowed spur (script §2):

| Source (3.3 V, 1 ns unless noted) | at | source | isolation needed |
|---|---|---|---|
| 40 MHz × 23 | 920 MHz (LoRa) | −20 dBm | 103 dB |
| 40 MHz × 39 | 1560 MHz (BeiDou/near L1) | −29 dBm | 86 dB |
| 25 MHz SD × 63 | 1575 MHz (L1) | −33 dBm | 82 dB |
| same, 5 ns edges | 1575 MHz | −47 dBm | 68 dB |

"Isolation" here is everything between the trace and the receiver input: trace-to-antenna coupling, plane and fence attenuation, can seams, the LNA input match, filters.

**Fringing-field coupling** between parallel traces over a plane falls as $1/(1+(D/h)^2)$ ([grounding](grounding-and-return-paths.md)); on JLC-7628 that is 39 dB at 2 mm and 67 dB at 10 mm, but on a 2-layer board only 9 and 33 dB (script §3). Coupling to an *antenna* is near-field and geometry-dependent; free-space path loss at 1575 MHz is just 10 dB at 5 cm and 36 dB at 1 m.

### Level 3 — shared impedance under converters, and frequency planning
**Shared ground impedance.** A digital or PA return current $I$ through a shared ground segment of resistance $R$ (and inductance $L$) adds $I(R+j\omega L)$ to the analog reference. A 10 × 2 mm 1-oz trace is 2.5 mΩ: 100 mA → 246 µV, which is 6.4 LSB of a 16-bit/2.5 V converter and 1600 LSB of a 24-bit one (script §4). With a solid plane and good placement the digital return current doesn't flow under the converter at all — that is the real meaning of "partitioning".

**Frequency planning.** For each clock $f_c$ and receive band $[f_1,f_2]$, harmonics $n\in[\lceil f_1/f_c\rceil,\lfloor f_2/f_c\rfloor]$ land in band. The [EMC page](emc-emi-fundamentals.md) script tabulates 17 clocks against 8 bands. Options when a harmonic lands: move the receive channel (LoRa channels are free to choose within the band plan), change the clock (SD at 20/40 MHz instead of 25; SPI divider), enable spread-spectrum clocking (≈ 11–16 dB at 0.9–1.6 GHz in a 125 kHz LoRa bandwidth, less in GNSS bandwidth), or isolate.

## Design equations & rules of thumb

| Rule | Value / equation | Note |
|---|---|---|
| Noise floor | −174 + 10 log B + NF | LoRa −117, GNSS −109 dBm |
| Desense (noise-like) | 10 log(1 + I/N) | spur 6 dB below N → 1 dB |
| GNSS jammer tolerance | ≈ 6–12 dB above thermal noise | u-blox [4] |
| Isolation need | source harmonic − allowed spur | 70–105 dB typical |
| Trace coupling | ∝ 1/(1+(D/h)²) | 4-layer ≫ 2-layer |
| Edge control | 10× slower edges → −20 dB above both corners | series R 22–47 Ω |
| ADC grounding | AGND & DGND to one plane at the part | [2] |
| Remote GNSS antenna | > 1 m from electronics: interference "should not be an issue" | u-blox [4] |
| GSM-class TX near GNSS | plan ≥ 40 dB antenna isolation; GNSS max input ≈ −5 dBm typ. | u-blox [4] |
| Needs termination | $\ell > \ell_{crit}=vt_r/6$ | 29 mm at 1 ns on JLC-7628 L1 |
| Series termination | $R_s=Z_0-R_{out}$ at the driver | 33–39 Ω for a 67 Ω trace, $R_{out}$ ≈ 30 Ω |
| Saturation length | $L_{sat}=vt_r/2$ ($t_r$ = 0–100 % ramp) | 86 mm at 1 ns |
| NEXT | $k_b\min(1,\ell/L_{sat})$, $k_b=(k_C+k_L)/4$ | 2.3 % at 3h gap |
| FEXT | $k_f(\ell/v)/t_r$, $k_f=(k_C-k_L)/2$ (< 0 on microstrip) | −2.6 % × TD/$t_r$ at 3h |
| Guard trace | stitched only; ≈ 2.4× less NEXT at fixed pitch | floating: no benefit |

## Worked examples

### 1. Floor-planning a 4-layer flight computer (ESP32-S3 + SX1262/E22 + MAX-M10S + sensors)
- **Board ends**: GNSS module + U.FL (or chip antenna keep-out) at one end; LoRa module/front end and its SMA at the other; the MCU, flash and SD in the middle; the switchers next to the battery connector, on the LoRa side (the LoRa PA can tolerate supply noise better than GNSS).
- **Stackup**: L1 parts + RF; L2 solid GND; L3 GND (or power pour) — no splits; L4 slow signals. Route SD, SPI and the inter-MCU UART on L4 or L3 *between* GND layers if the stackup allows, never along board edges.
- **Sensors** (IMU, baro, mag) near the MCU but on the opposite side from the switchers and the LoRa antenna feed, each with its own bead/LDO-filtered supply ([PDN](power-distribution-decoupling-for-rf.md)).
- **Clocks**: ESP32 40 MHz crystal ≥ 2 mm from the chip's clock pin with a GND guard [5]; pick the LoRa channel ≥ 0.5 MHz away from 920.000 MHz; SD clock 20 or 40 MHz; SSC on the buck converters if offered.
- **Check**: with the board running flight firmware (SD writes, telemetry, sensor polling), compare GNSS C/N0 against the same antenna on a quiet reference receiver, and read the u-blox jamming indicator (UBX-MON-HW jamInd / jammingState / MON-RF) [4][6]; read the LoRa module's ambient RSSI with TX off.

### 2. SPI from MCU to an SX1262 across the board
SPI at 8–16 MHz, 30 mm long: route on L3/L4 over solid GND, with 33 Ω series resistors at the MCU end (sets edge rate ≈ 1–2 ns into ≈ 10 pF and damps ringing); keep the SPI and BUSY/DIO lines out of the RF section (enter the radio from its digital side); add a GND via next to each layer change. For the EBYTE UART modules, the UART lines are slow — the risk is the opposite direction: 2 W of 433 MHz RF coupling into the UART and AUX lines; small RC filters (100 Ω + 100 pF) at the MCU pins prevent glitches ([EMC](emc-emi-fundamentals.md)).

### 3. Converter grounding for a pyro-current or battery-voltage ADC
An INA219-style current monitor or an MCU ADC measuring pack voltage through a divider: the measurement return must be the ground at the shunt/divider, not a ground point 30 mm away through which the pyro current returns. Route the sense pair as a pair (Kelvin connection), put the RC anti-alias filter at the ADC pin, and keep the high-current return path (battery → FETs → igniter → battery) compact and away from the converter.

### 4. "My GNSS loses fix when the SD card logs"
Symptom from the KB's harmonic table: 25 MHz SD clock × 63 = 1575.000 MHz. Required isolation ≈ 82 dB with 1 ns edges. Fixes, in order of cost: change the SD clock (20/40 MHz); add 33–47 Ω series at the SD clock driver (≈ −14 dB at L1 with 5 ns edges); move the SD socket and its traces to the far end of the board and to inner layers; ground pour + via fence between SD and GNSS sections; a shield can over the GNSS module; use an active GNSS antenna on a short cable placed away from the board.

## Termination and crosstalk budgets for SPI and clocks
*Added 2026-10-13 (W5-S16, G-13-02). Numbers from `tools/verify/s16_crosstalk.py` (2-D field solver `tline_fd2d.py` plus a multiconductor FDTD). The general theory of reflections, termination and NEXT/FEXT is on [digital termination and crosstalk](digital-termination-and-crosstalk.md) (W5-E11; its $K_b$ values for 0.4 and 0.6 mm pitch, 0.092 and 0.042, agree with this section to < 2 %; it quotes $\ell_{sat}$ = 83 mm vs 86 mm here, a 4 % difference in the assumed v). This section is the flight-computer budget layer on the JLC04161H-7628 stackup.*

**Geometry used.** 0.2 mm traces on L1 over the L2 plane: h = 0.2104 mm, εr 4.4, 35 µm copper, no mask (canonical stackup, [00 §B](../00-math-foundations/canonical-values-and-conventions.md)). The solver gives **Z0 = 67 Ω and v = 0.576 c** for an isolated trace (172 mm/ns, 5.8 ps/mm). On the JLC 4-layer stackup, L2 and L3 are planes, so every digital trace is microstrip (L1 or L4). That matters for far-end crosstalk (FEXT) below.

**Edge time convention.** $t_r$ here is the duration of a *linear 0–100 % ramp*. A measured 10–90 % rise time is ≈ 0.8 $t_r$. The FDTD check confirms the closed forms only with this definition: with the 10–90 % value plugged in, they read ≈ 20 % high below saturation.

### Level 1 — when does a trace need termination?
A trace behaves as a lumped wire when its one-way delay is below $t_r/6$, i.e. its length is below $\ell_{crit}=v\,t_r/6$ (canonical lumped criterion):

| $t_r$ | 0.5 ns | 1 ns | 2 ns | 5 ns | 10 ns |
|---|---|---|---|---|---|
| $\ell_{crit}$ on L1 | 14 mm | 29 mm | 58 mm | 144 mm | 288 mm |

An ESP32-S3 or Teensy GPIO at high drive strength produces ≈ 1 ns edges into a few pF (assumed; neither data sheet gives output impedance or edge rate per drive setting). So **almost every SPI clock that crosses a flight computer (50–150 mm) is a transmission line**. Lowering the drive strength (5–10 ns edges) makes most of them lumped again. That is usually the cheapest fix, and it also lowers harmonics ([Level 2](#level-2--isolation-needed-from-a-clock-harmonic)).

### Level 2 — termination options for a 100 mm SPI clock (simulated)
Driver $R_{out}$ = 30 Ω (assumed), 1 ns ramp, 3.3 V, receiver 5 pF, Z0 = 67 Ω, TD = 0.58 ns:

| Scheme | Far-end overshoot / ring-back | Settles (± 5 %) | DC cost | Notes |
|---|---|---|---|---|
| none | **+1.18 V / −0.43 V** | 4.8 ns | 0 | 4.5 V peak is beyond the 3.6 V-class absolute maximum: current flows into the receiver's ESD diodes, and ring-back near the threshold can double-clock |
| series $R_s = Z_0 - R_{out}$ ≈ 37 Ω (use 33–39 Ω) | 0 / 0 | 2.2 ns | 0 | the default for point-to-point SPI; place it at the driver |
| parallel $Z_0$ to GND | +0.14 V | 1.7 ns | 34 mA when high; high level only 2.28 V | unusable at 3.3 V CMOS |
| Thevenin 2 × 134 Ω (VDD/2) | +0.12 V | 1.7 ns | 12 mA in either state | for long multi-drop lines only |
| AC: 67 Ω + 100 pF | 0 | 7.9 ns (RC tail) | 0 DC; $CV^2f$ = 22 mW at 20 MHz | RC must be ≫ 2TD but ≪ the bit time |

**Multi-drop SCK.** An SPI bus to IMU + baro + flash + SD is the usual case, and series termination has a catch. The wave launched down the line is only *half* amplitude, and it reaches full amplitude only when the reflection from the open far end comes back. A receiver tapped at a distance $x$ from the far end therefore sees a half-voltage shelf lasting $2x/v$, sitting right at its logic threshold. That is a classic double-clock. Fixes, in order:
1. Slow the edges until the line is lumped.
2. Daisy-chain the devices and cluster them at the far end.
3. Use separate SCK lines (the MCU has several SPI hosts).
4. Use a short stub to each device, with the series R at the driver.

### Level 3 — NEXT, FEXT and saturation length
For two coupled lines, the per-unit-length matrices give $k_C=C_m/C_{11}$ and $k_L=L_m/L_{11}$. From these:
$$\text{NEXT}_{sat}=k_b=\tfrac14(k_C+k_L),\qquad \text{NEXT}(\ell)=k_b\min\!\left(1,\frac{\ell}{L_{sat}}\right),\quad L_{sat}=\frac{v\,t_r}{2},$$
$$\text{FEXT}(\ell)=k_f\,\frac{\ell/v}{t_r},\qquad k_f=\tfrac12(k_C-k_L).$$
These are Bogatin's and Johnson & Graham's forms [9][10], valid for weak coupling with both ends matched.
- NEXT grows with coupled length until the line is long enough to hold the whole edge (round trip ≥ $t_r$), then stops: **$L_{sat}$ = 86 mm at 1 ns, 43 mm at 0.5 ns, 430 mm at 5 ns**.
- FEXT grows without limit and, on microstrip, is *negative*, because $k_L > k_C$: the field is partly in air. In a homogeneous stripline $k_C=k_L$ and FEXT vanishes.
- **Check.** Paul's multiconductor FDTD of the matched pair gives NEXT 15.77 mV against 15.77 mV from the closed form (30 mm, 0.5 V launch), and FEXT −23.4 mV against −22.8 mV (150 mm).

Field-solver coefficients, 0.2 mm traces on L1 of JLC04161H-7628:

| Edge gap | $k_C$ | $k_L$ | NEXT$_{sat}$ $k_b$ | $k_f$ |
|---|---|---|---|---|
| 0.2 mm (= 1 w; pitch 0.4) | 12.8 % | 23.3 % | **9.0 % (−20.9 dB)** | −5.2 % |
| 0.4 mm (pitch 0.6 = "3W") | 4.7 % | 12.1 % | 4.2 % (−27.6 dB) | −3.7 % |
| 0.6 mm (≈ 3h) | 2.1 % | 7.2 % | 2.3 % (−32.7 dB) | −2.6 % |
| 1.0 mm | 0.7 % | 3.3 % | 1.0 % (−40.0 dB) | −1.3 % |
| 0.6 mm + floating 0.2 mm guard | — | — | 2.4 % | −2.3 % |
| 0.6 mm + guard stitched to GND | — | — | **0.97 %** | −1.0 % |

From 0.2 mm to 0.6 mm gap, $k_b$ falls by 3.9×. The [Johnson–Graham](grounding-and-return-paths.md) $1/(1+(D/h)^2)$ rule predicts 3.4×, close enough for layout decisions. What controls coupling is **spacing relative to h**, not relative to trace width. On a 2-layer board (h = 1.43 mm) a "3W" gap couples almost as strongly as touching traces do on 4-layer. A **floating guard does nothing** (2.4 % vs 2.3 %). A guard stitched to the plane at both ends and along its length (vias every ≤ λ/20 of the highest harmonic of concern, and ≤ $L_{sat}/4$; [vias](vias-stitching-fencing.md)) cuts NEXT 2.4× at the same pitch. That is about what widening the gap to 1 mm achieves, so a guard is worth it only where space is fixed.

### Worked example — SPI clock beside other lines on the flight computer
3.3 V SCK, 1 ns ramp, matched-end approximation, voltage on the victim:

| Victim run alongside SCK | Gap | NEXT | FEXT | Verdict |
|---|---|---|---|---|
| 30 mm of MISO / interrupt line | 0.2 mm | 104 mV | −30 mV | harmless for CMOS logic (ESP32-S3 thresholds ≈ 0.25/0.75 VDD, i.e. ≈ 0.8 V noise margin; from knowledge) |
| 100 mm of a slow GPIO (PPS, pyro-arm sense) | 0.2 mm | 298 mV (saturated) | −100 mV | logic still fine; a glitch filter in firmware is cheap insurance on any line that *fires* something |
| 100 mm of an analog line (battery or pyro-continuity divider into the ADC) | 0.6 mm | 77 mV spikes | −49 mV | **not fine**: 77 mV is 95 LSB of a 12-bit/3.3 V ADC if sampled on an edge. Route analog away (≥ 2–5 mm), add an RC at the ADC pin ([Example 3](#3-converter-grounding-for-a-pyro-current-or-battery-voltage-adc)) |
| any length of GNSS/LoRa RF line | any | — | — | use the spectral budget in [Level 2](#level-2--isolation-needed-from-a-clock-harmonic) (82–103 dB needed): saturated NEXT of −21 to −40 dB is nowhere near enough. Keep clocks ≥ 5 mm away and on the other side of a plane |

**Rules that follow for Space Bar boards.**
1. Series-terminate every clock and SPI SCK/MOSI at the driver: 33 Ω for ESP32/Teensy-class drivers, then confirm on a scope with a short-ground probe.
2. Use the lowest drive strength that meets timing.
3. Keep SCK edge-to-edge gaps ≥ 3h (≥ 0.6 mm on JLC-7628) to other signals, and ≥ 2–5 mm to analog inputs.
4. Keep parallel runs well under $L_{sat}$ where you can.
5. Use stitched guards only where spacing is impossible, never floating ones ([Common mistakes](#common-mistakes--misconceptions)).

## Practical notes
- **Modules help**: GNSS/LoRa/Wi-Fi modules have their own shields and filtering; the remaining coupling paths are the antenna (and its cable) and the module's supply/IO pins. Filter module IO with small series R or beads (u-blox suggests > 20 Ω, BLM15HD102SN1 or 47 nH on unshielded lines > 3 mm) [7].
- **USB**: 480 Mb/s HS has broadband content to GHz; FS (12 Mb/s) has 12 MHz-related harmonics (924 MHz in SG band). Keep the USB connector and PHY away from antennas; CM choke on the pair; on a flight board USB is for the bench — it can be electrically idle in flight.
- **Switching regulators**: minimise the hot loop (input cap to switch to diode/FET), keep the SW node copper small and on L1 over solid GND, shielded inductors, and keep them ≥ 20–30 mm from GNSS RF and LNA bias networks ([PDN](power-distribution-decoupling-for-rf.md)).
- **Crystals and TCXOs**: guard ring of GND vias, no traces underneath, short loop; they are both victims (pulled by noise) and aggressors (harmonics) [3][5].
- **Firmware levers**: lower MCU drive strength on GPIO/SPI, disable unused clock outputs, avoid bursty SD writes during GNSS cold start, and schedule LoRa TX away from sensitive sensor reads.
- **Two-board solutions**: the Space Bar primary FC put GNSS on a snap-off daughterboard — combined with a remote active antenna it is an effective isolation strategy.

- Termination (series R values), NEXT/FEXT and the 3W rule evaluated: [digital termination and crosstalk](digital-termination-and-crosstalk.md).
## Common mistakes & misconceptions
- **Splitting the ground plane "for analog"** and then routing SPI across the split.
- **Believing EMC compliance means no self-interference** — GNSS lives above the regulated range [4].
- **Choosing LoRa or clock frequencies without a harmonic check.**
- **Routing fast buses on outer layers along board edges** (strong radiators).
- **Running the GNSS antenna coax past the MCU and SD.**
- **Guard traces without stitching** (resonant, see [vias](vias-stitching-fencing.md)). The field solver shows a floating guard gives *no* NEXT reduction (2.4 % vs 2.3 % without it).
- **"SPI is slow, so it doesn't need termination."** What matters is the edge, not the clock rate. A 1 MHz SPI clock with 1 ns edges overshoots like a 100 MHz one.
- **Series-terminating a multi-drop SCK and tapping receivers mid-line.** The half-amplitude shelf sits at the threshold, and the receiver double-clocks.
- **Applying the 3W rule on a 2-layer board.** Coupling scales with spacing/h. A 3W gap on 1.43 mm FR-4 is barely isolated.
- **Plugging the 10–90 % rise time into $L_{sat}=vt_r/2$ and NEXT/FEXT formulas.** They assume the ramp duration (≈ 1.25 × the 10–90 % time). The difference is ≈ 20 % below saturation.
- **Parallel-terminating 3.3 V CMOS lines to ground.** 34 mA per line and a 2.3 V high level. Use series termination, or AC termination for a long clock with a fixed frequency.

## How to simulate / verify
- `python3 tools/verify/pcb_mixed_signal.py` (instant): noise floors and desense, required isolation for specific harmonics, isolation offered by layout features, shared-ground error vs ADC LSB, bus-edge harmonics at L1.
- `python3 tools/verify/pcb_emc_radiation.py` §4: full harmonic-landing table for your clocks (edit the dictionaries).
- `python3 tools/verify/s16_crosstalk.py` (≈ 2 s): L/C matrices of coupled and guarded traces from the 2-D FD solver; NEXT/FEXT/saturation length; multiconductor FDTD check of the closed forms; termination comparison (none/series/parallel/Thevenin/AC) by FDTD; critical length (all checks pass; output `s16_crosstalk_output.txt`).
- Bench: scope the SCK at the *receiver* pin with a ≤ 10 mm ground spring. Look for overshoot beyond the absolute maximum, and for ring-back or shelves that cross the threshold band.
- Bench: SDR or tinySA with a small antenna/probe near the GNSS antenna, max-hold over 1.55–1.61 GHz while toggling subsystems; u-blox u-center MON-RF/MON-HW jamming indicators; C/N0 comparison against a reference receiver.

## Open questions / gaps
- The CW-spur-in-LoRa-channel rejection (processing gain against narrowband interference) is treated as noise-like — a conservative assumption; LoRa CSS can tolerate somewhat stronger CW interferers.
- Isolation values for "trace to antenna" coupling are not computed (geometry-specific); an openEMS model of a clock trace and a chip antenna on the same board would be a valuable addition.
- ADI MT-031 could not be fetched (timeouts); the AGND/DGND guidance follows Zumbahlen and Ott.
- ESP32-S3 / Teensy 4.1 output impedance and edge rate per drive-strength setting are not published. The 30 Ω / 1 ns used for the termination study is an assumption; measure the real edge and adjust $R_s$.
- The crosstalk model ignores solder mask (it raises $k_C$ and makes FEXT less negative), loss and receiver capacitance on the victim, and assumes both victim ends are matched. Unmatched victims (high-impedance CMOS inputs) double the far-end voltage. Use the numbers as a ranking, and check critical runs with the FDTD in the script.

## Sources
1. H. W. Ott, "Partitioning and layout of a mixed-signal PCB," *Printed Circuit Design*, June 2001; "Grounding of mixed signal PCBs," Henry Ott Consultants tech tip. (expert articles)
2. H. Zumbahlen, "Staying well grounded," *Analog Dialogue* 46-06, 2012; ADI MT-031 (Kester) — AGND/DGND pins tied at the converter; single plane. (app notes)
3. Texas Instruments, SWRA640H (2024) — solid ground under RF; crystal load-capacitor layout; decoupling rules. (app note)
4. u-blox, *GNSS Antennas — RF design considerations for u-blox GNSS receivers*, application note UBX-15030289 R03 (pdftotext) — GNSS jammer dynamic range only 6–12 dB above thermal noise (1–2-bit quantisation); CPU-clock harmonics up to 1.5 GHz exceed thermal noise; EMC regulations stop near 1 GHz; ≥ 40 dB GSM–GNSS antenna isolation; max RF input ≈ −5 dBm typical; C/N0 44–50 dBHz in good designs; remote antenna > 1 m avoids interference; solid planes, ground frame on every layer, controlled rise times, terminations, many small decoupling caps. (app note)
5. Espressif, *ESP32-S3 Hardware Design Guidelines — PCB layout* — crystal ≥ 2.0 mm from the clock pin, no high-speed traces under the crystal, USB/UART away from the antenna. (app note)
6. u-blox receiver description/protocol specifications (UBX-MON-HW jamInd, jammingState; MON-RF) — via search summary. (documentation)
7. u-blox, *MAX-M5Q Hardware Integration Manual* UBX-13002460 R06, §5.3.6 (EMI on unshielded lines > 3 mm; series R/ferrite/inductor). (app note)
8. Verification scripts `tools/verify/pcb_mixed_signal.py` (this page) and `tools/verify/pcb_emc_radiation.py` (harmonic table).
9. E. Bogatin, *Signal and Power Integrity — Simplified*, 3rd ed., Pearson 2018, ch. 8 (termination: series/parallel/Thevenin/AC; critical length) and ch. 10 (NEXT/FEXT, $k_b=(C_m/C+L_m/L)/4$, saturation length $vt_r/2$, guard traces). (textbook; from knowledge, re-derived and FDTD-checked here)
10. H. W. Johnson, M. Graham, *High-Speed Digital Design: A Handbook of Black Magic*, Prentice Hall 1993, ch. 4 "Transmission Lines" (§4.3 source and load impedance), ch. 5 "Ground Planes and Layer Stacking" (§5.2 crosstalk in solid ground planes vs spacing/height, §5.7 near- and far-end crosstalk), ch. 6 "Terminations"; the multidrop bus is treated in ch. 9 (textbook; chapter/section numbers checked against the publisher's full ToC, sigcon.com/vault/pdf/HSDD-TOC-full.pdf, by W5-S18 2026-10-13 — the earlier "ch. 4 (terminations, multi-drop)" was corrected).
11. C. R. Paul, *Analysis of Multiconductor Transmission Lines*, 2nd ed., Wiley 2008, ch. 9 (FDTD of MTLs with resistive terminations — the scheme in `s16_crosstalk.py` §C). (textbook; from knowledge)
12. Verification script `tools/verify/s16_crosstalk.py` (W5-S16), using the KB's 2-D solver `tools/verify/tline_fd2d.py`.
