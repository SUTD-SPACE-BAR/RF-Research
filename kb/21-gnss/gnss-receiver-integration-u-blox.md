---
title: Integrating u-blox ZED-F9P and MAX-M10S — UBX vs NMEA, CFG-VALSET, update rate vs constellations, UART/I²C/SPI throughput, antenna supervision, backup power, resets and layout
domain: 21-gnss
slug: gnss-receiver-integration-u-blox
tags: [u-blox, zed-f9p, max-m10s, ubx, nmea, cfg-valset, configuration-layers, ram, bbr, flash, otp, nav-pvt, rxm-rawx, uart, baud-rate, i2c, fast-mode, ddc, spi, tx-ready, update-rate, dynamic-model, antenna-supervisor, ant-detect, vcc-rf, bias-tee, v-bckp, reset-n, safeboot, timepulse, extint, layout, esd]
prerequisites: [gnss-receiver-architecture-acquisition-tracking.md, ../08-antennas/gnss-antennas.md]
related: [gnss-on-rockets-dynamics-and-limits.md, gnss-timing-1pps.md, ttff-agps-almanac-ephemeris.md, rtk-ppp-and-corrections.md, gnss-interference-jamming-spoofing.md, ../18-components-parts/rf-modules.md, ../13-pcb-rf-layout-emc/rf-layout-rules.md, ../13-pcb-rf-layout-emc/connectors-and-launches.md]
level: intermediate
confidence: high
last_updated: 2026-10-02
---

# Integrating the u-blox ZED-F9P and MAX-M10S

## Questions this page answers
- Should I use UBX or NMEA, and which messages should a flight computer read?
- How do I configure a u-blox F9/M10 receiver (CFG-VALSET, layers, key IDs) and make it survive power cycles?
- How fast can it update, and why does the rate drop when I enable more constellations?
- What baud rate / I²C speed / SPI do I need, and why did my GPS stop talking after a baud-rate change?
- Why does u-blox say its I²C does not support Standard mode — is 100 kHz wrong?
- How do I power an active antenna and use the antenna supervisor?
- What does V_BCKP do, and why does RESET_N give me a cold start?
- What are the layout rules for the RF input?

## TL;DR
- **Read UBX, not NMEA**: one `UBX-NAV-PVT` (92-byte payload, 100 bytes on the wire) carries time, fix type, `gnssFixOK`, lat/lon/height, NED velocity, accuracies, numSV and pDOP [3]. Disable the default NMEA set (GGA, GLL, GSA, GSV, RMC, VTG, TXT) — with multi-GNSS GSV it is ≈ 1 kB per epoch.
- **Defaults differ**: ZED-F9P UART1 **38 400 baud**, MAX-M10S UART **9 600 baud** [1][2]. At 9600 baud (960 B/s) the M10S's default NMEA output already fills the link at 1 Hz. Raise the baud (115 200–921 600) and/or switch to UBX before raising the rate.
- **Configuration** is key–value: `UBX-CFG-VALSET` (class 0x06, ID 0x8A) with up to 64 pairs, written to RAM / BBR / Flash layers [3]. Same key IDs on F9 and M10 (e.g. `CFG-NAVSPG-DYNMODEL` 0x20110021 = 8 for Airborne <4g; `CFG-RATE-MEAS` 0x30210001 in ms; `CFG-UART1-BAUDRATE` 0x40520001) [3][6]. **The M10S has no flash** (RAM, BBR, OTP only) — without V_BCKP your host must re-send the configuration at every boot.
- **I²C is Fast-mode only** (400 kHz max, "Standard-mode not supported", clock stretching up to 20 ms) on both modules [1][2] — this is the root of the Space Bar lesson "I²C left at 100 kHz; GPS I²C port doesn't support that speed": design a Fast-mode-compliant bus (≤ 300 ns rise time, ≈ 2–3 kΩ pull-ups) or use UART. ZED-F9P SPI: ≤ 5.5 MHz, ≤ 125 kB/s [1].
- **Rates fall with constellations**: M10S default 10 Hz (GPS+GAL) → 3 Hz (GPS+GAL+BDS B1I); 18 Hz single GNSS; "high performance" configuration up to 25 Hz [2]. ZED-F9P PVT 25 Hz GPS-only → 9 Hz four GNSS; RTK 20 → 7 Hz [1].
- **Power and resets**: V_BCKP 1.65–3.6 V (F9P 45 µA, M10S 28 µA) keeps RTC + BBR (ephemeris, almanac, position, config) for hot starts [1][2]. **RESET_N clears BBR and forces a cold start on both** [4][5] — use `UBX-CFG-RST` (hot/warm/cold, software reset) in your recovery ladder instead.
- **RF input**: ZED-F9P needs an active antenna (17–50 dB external gain; supply via VCC_RF and a bias-T with a high-impedance-at-L-band inductor; ESD protection mandatory) [1][4]; MAX-M10S has DC block + LTE B13 notch + LNA + SAW internally, accepts passive antennas, use LNA bypass mode with ≥ 10–15 dB external gain [2][5]. Antenna supervisor: F9P has ANT_DETECT/ANT_SHORT_N/ANT_OFF pins; M10S needs external parts and reassigned PIOs [4][5].

## Intuition (no math)
A u-blox module is a complete receiver with its own CPU; your flight computer is a client. The integration work is (1) a clean RF input (antenna, bias, filtering, ESD), (2) clean power with a backup domain so the receiver remembers the sky, (3) a data link fast enough for the messages you enable, and (4) a configuration that is applied reliably every boot. Most field failures are in (3) and (4): a baud-rate change that the host and receiver disagree on, an overflowing UART buffer that silently drops messages, an I²C bus that doesn't meet Fast-mode timing, or a configuration lost because it was only written to RAM.

## The math

### Level 1 — message sizes and link budgets
**UBX frame**: `0xB5 0x62 | class | id | length (2 B, little-endian) | payload | CK_A CK_B` — 8 bytes of overhead; checksum is the 8-bit Fletcher algorithm over class…payload [3]:
$$CK_A \leftarrow CK_A + b_i,\qquad CK_B \leftarrow CK_B + CK_A \pmod{256}.$$

| Message | Payload (B) | Wire bytes | Use |
|---|---|---|---|
| NAV-PVT | 92 | 100 | primary flight message [3] |
| NAV-SAT | 8 + 12·N_sv | 8 + 12·40 + 8 ≈ 500 | C/N₀, elevation, health per satellite |
| NAV-SIG | 8 + 16·N_sig | ≈ 1.3 kB (80 signals) | per-signal quality (F9) |
| RXM-RAWX | 16 + 32·N_meas | ≈ 2.6 kB (80 meas.) | raw pseudorange/carrier/Doppler |
| TIM-TP | 16 | 24 | qErr for the next pulse [3] |
| MON-RF | 4 + 24·N_blocks | 36–60 | jamming/AGC/antenna status [3] |

**UART capacity** (8N1, 10 bits/byte): 9600 baud → 960 B/s; 38 400 → 3.84 kB/s; 115 200 → 11.5 kB/s; 921 600 → 92 kB/s (ZED-F9P and M10S range 9600–921 600 [1][2]). Required: Σ (bytes per message × rate) ≤ 0.7 × capacity (headroom for bursts — the receiver sends everything right after the epoch, so latency also matters: a 1.2 kB burst takes 312 ms at 38 400 baud but 13 ms at 921 600; `gnss_timing_pps.py`).

**I²C capacity**: at 400 kHz, ≈ 9 bit-times per byte plus addressing → ≈ 40 kB/s raw; polling overhead (read 0xFD/0xFE byte count, then stream 0xFF) and clock stretching (≤ 20 ms) reduce it [1][4]. A `NAV-PVT` at 25 Hz (2.5 kB/s) is easy; `RXM-RAWX` at 10 Hz (≈ 26 kB/s) is not.

### Level 2 — configuration model, rates and the RF interface
**Configuration layers.** RAM (active), BBR (survives while V_BCKP is supplied), Flash (F9P; permanent), defaults (ROM) and, on M10, OTP (one-time, permanent) [3][5]. At start-up the receiver builds RAM from defaults → Flash/OTP → BBR. `UBX-CFG-VALSET` payload: `version (0x00) | layers bitfield (bit0 RAM, bit1 BBR, bit2 Flash) | 2 reserved | key (U4, LE) value (size from key) …`; returns ACK-ACK or ACK-NAK (unknown key, invalid configuration) [3]. Version 0x01 adds transactions (apply several messages atomically).

Example frames (checksums computed and checked against the well-known `MON-VER` poll `B5 62 0A 04 00 00 0E 34`):

| Purpose | Frame (hex) |
|---|---|
| Dynamic model = Airborne <4g (8), RAM | `B5 62 06 8A 09 00 00 01 00 00 21 00 11 20 08 F4 51` |
| same, RAM + BBR | `B5 62 06 8A 09 00 00 03 00 00 21 00 11 20 08 F6 61` |
| Measurement period 100 ms (10 Hz), RAM | `B5 62 06 8A 0A 00 00 01 00 00 01 00 21 30 64 00 51 B9` |
| NAV-PVT on UART1 every epoch, RAM | `B5 62 06 8A 09 00 00 01 00 00 07 00 91 20 01 53 48` |
| UART1 baud 921 600, RAM | `B5 62 06 8A 0C 00 00 01 00 00 01 00 52 40 00 10 0E 00 4E A9` |

Key IDs from the F9 HPG 1.32 and M10 SPG 5.10 interface descriptions (identical) [3][6]. Dynamic-model constants: 0 Portable (default), 2 Stationary, 3 Pedestrian, 4 Automotive, 5 Sea, 6 Airborne <1g, 7 <2g, **8 <4g**, 9 Wrist, 10 Bike, 11 Mower, 12 E-scooter [3].

**Navigation rate.** `CFG-RATE-MEAS` (ms between measurements) and `CFG-RATE-NAV` (navigation solutions per measurement) set the rate. The maximum depends on the signal set because each epoch costs baseband and CPU time (u-blox tables):

| Receiver | Configuration | Max rate |
|---|---|---|
| MAX-M10S | GPS+GAL / +GLO / +BDS B1I (default) / +BDS B1C / +B1C+GLO | 10 / 6 / 3 / 8 / 4 Hz (default mode); 20 / 16 / 12 / 16 / 10 Hz (high-performance config) [2] |
| MAX-M10S | single GNSS | 18 Hz default, 25 Hz high-performance [2] |
| ZED-F9P | 4 GNSS / GPS only — PVT | 9 / 25 Hz [1] |
| ZED-F9P | 4 GNSS / GPS only — RTK | 7 / 20 Hz [1] |
| ZED-F9P | RAW measurements | 15–25 Hz [1] |

**Interfaces and pins.**
- UART: no hardware flow control; RX disabled for the rest of a second after > 100 framing errors in one second (e.g. wrong baud, grounded RX) [5]; wait ≈ 100 ms after a baud-rate change before sending at the new rate [4][5]. Don't use F9P UART2 as the only host port (no firmware update/safeboot) [1]; UART2 is the natural **RTCM corrections input** (the Avionics-B LoRa bridge fed corrections straight into the GPS).
- I²C (u-blox "DDC"): address 0x42; registers 0xFD/0xFE = bytes available, 0xFF = data stream (0xFF = no data) [4]. Fast-mode timing; internal pull-ups 7–30 kΩ (F9P) are too weak for 400 kHz on a real bus — u-blox's example: 100 pF bus, $R_p$ = 1.5–3.5 kΩ, add 3 kΩ externally; place 68 pF filter capacitors on SCL/SDA against radiated emissions near GNSS frequencies [4].
- SPI (F9P, D_SEL = 0): peripheral only, mode 0, ≤ 5.5 MHz, 125 kB/s; idle reads return 0xFF; 50 × 0xFF writes reset the parser [1][4].
- TX_READY (F9P): a PIO that goes active when the output buffer exceeds a threshold — lets the host read I²C/SPI without polling [4].
- TIMEPULSE (both), EXTINT (time-mark input) — [timing page](gnss-timing-1pps.md). On the M10S the SAFEBOOT_N pin is internally tied to TIMEPULSE through 1 kΩ: anything that holds TIMEPULSE low at power-up puts the module into safeboot [2].

**RF input and supervision.**
- ZED-F9P: active antenna mandatory; external gain 17–50 dB (ideal 30–40 dB), total NF ≈ 3 dB, group delay variation ≤ 10 ns per band; RF_IN abs. max 10 dBm CW; VCC_RF = VCC − 0.1 V, ≤ 50 mA; bias-T inductor resonant/high-impedance at L-band (u-blox uses ≈ 120 nH-class parts) with a current-limit resistor; ESD protection mandatory [1][4]. Antenna supervisor: ANT_OFF (output), ANT_SHORT_N, ANT_DETECT inputs; enable with `CFG-HW-ANT_CFG_VOLTCTRL`, `…SHORTDET`, `…OPENDET`, `…PWRDOWN`, `…RECOVER`; status in `UBX-MON-RF.antStatus` (INIT/DONTKNOW/OK/SHORT/OPEN) and `$GNTXT,…,ANTSTATUS=…` [3][4].
- MAX-M10S: internal DC block, LTE Band 13 notch, LNA, SAW; NF 1.5 dB; external gain ≤ 30 dB in low-gain mode (default), 10–40 dB in bypass; "normal" gain mode not recommended; `CFG-HW-RF_LNA_MODE` in RAM/BBR (needs a reset) or OTP; RF_IN abs. max **0 dBm**; LNA_EN output switches an external LNA/active antenna off in standby; VCC_RF ≤ 50 mA [2][5]. Antenna supervisor needs external components and 2–3 reassigned PIOs [5].

### Level 3 — robust start-up, recovery and data integrity
**Start-up sequence that survives resets** (host side):
1. Open the UART at the module's *default* baud (M10S 9600, F9P 38 400) *and* at your flight baud — try both; poll `UBX-MON-VER` (`B5 62 0A 04 00 00 0E 34`) until a reply arrives.
2. Send `CFG-VALSET` (RAM + BBR, plus Flash on the F9P if you want it permanent) in one transaction: UART baud, protocol in/out masks (UBX only), message rates, `RATE-MEAS`, dynamic model, constellation enables (`CFG-SIGNAL-*`), timepulse.
3. After a baud change, wait ≥ 100 ms, reopen at the new rate, poll `MON-VER` again, then poll a few `CFG-VALGET` items to confirm.
4. Check each `ACK-ACK`/`ACK-NAK`; never assume.
This is the non-blocking "recovery ladder" the Space Bar firmware lessons call for ("GPS init failure after baud switch must not disable the peripheral for the whole flight").

**Resets** (`UBX-CFG-RST`): navBbrMask selects hot (0x0000), warm (0x0001) or cold (0xFFFF) start; resetMode selects hardware/software/GNSS-only. RAM settings are cleared by RESET_N and most CFG-RST modes; BBR is cleared by RESET_N and hardware-reset modes [5]. RESET_N on the M10S "clears the FW image in the code RAM and the BBR content including receiver configuration, real-time clock (RTC), and GNSS orbit data, triggering a cold start"; on the F9P "will delete all information and trigger a cold start" [4][5]. Use RESET_N only as the last rung of the ladder.

**Backup domain.** V_BCKP 1.65–3.6 V keeps RTC (32 kHz crystal) and BBR; without it the module cold-starts at every power-up [4]. Add ≈ 2 µF at V_BCKP and avoid series resistance (current step when switching from VCC) [4]; if unused, tie V_BCKP to VCC (F9P) or leave open (M10S) [4][5]. A 1S flight battery through a diode/LDO, a supercapacitor (a 0.22 F cap from 3.0 V to 1.65 V at 45 µA lasts ≈ 1.8 h) or a coin cell all work. In hardware backup mode the module's PIOs must not be driven — the Avionics-C buffered UART ("so the GPS isn't back-powered when off") is exactly what u-blox asks for [2][4].

**Data integrity.** Gate every fix on `NAV-PVT.flags.gnssFixOK` (fix within DOP/accuracy masks) and `fixType` ≥ 3; check `valid.validTime` before using UTC; use `iTOW` to match messages of the same epoch [3][4]. Treat `carrSoln` (0/1/2 = none/float/fixed) as the RTK state.

## Design equations & rules of thumb

| Item | Rule / value | Source |
|---|---|---|
| Flight message | NAV-PVT, 100 B/epoch | [3] |
| UART load | Σ bytes·rate ≤ 0.7 × baud/10 | rule of thumb |
| Default baud | F9P 38 400; M10S 9600 | [1][2] |
| I²C | Fast-mode only, ≤ 400 kHz, R_p ≈ 1.5–3.5 kΩ for 100 pF | [1][2][4] |
| SPI (F9P) | ≤ 5.5 MHz, 125 kB/s | [1] |
| Baud change | wait ~100 ms | [4][5] |
| UART RX lock-out | > 100 frame errors/s → RX disabled for the second | [5] |
| V_BCKP | 1.65–3.6 V; 45 µA (F9P), 28 µA (M10S) | [1][2] |
| RESET_N | cold start (clears BBR) | [4][5] |
| F9P external gain | 17–50 dB, ideal 30–40 dB | [1][4] |
| M10S LNA mode | low-gain default; bypass if ≥ 10–15 dB external gain | [5] |
| RF_IN abs. max | F9P 10 dBm, M10S 0 dBm (CW) | [1][2] |

## Worked examples
**1 — Why the M10S "drops messages" at 5 Hz.** Default NMEA with GPS+GAL+BDS: GGA 75 B, GLL 50, RMC 70, VTG 40, GSA ≈ 3 × 65, GSV ≈ 8 × 70 (≈ 30 satellites, 4 per sentence) → ≈ 990 B/epoch. At 9600 baud = 960 B/s, even 1 Hz is at 103 % — the receiver buffers then drops. Fix: `CFG-UART1-BAUDRATE = 115200`, disable NMEA output (`CFG-UART1OUTPROT-NMEA = 0`), enable `NAV-PVT` (100 B) → 500 B/s at 5 Hz, 4 % of the link.

**2 — I²C at 100 kHz on the Avionics-B bus.** At 100 kHz, a 100-byte `NAV-PVT` read (+ address + byte-count read) is ≈ 1 ms of bus time per poll — throughput isn't the problem. The problem is electrical: u-blox specifies Fast-mode timing (t_r ≤ 300 ns at 400 pF, t_LOW ≥ 1.3 µs, …) and explicitly does not support Standard-mode bus operation [1][2]. A bus designed for Standard mode (weak pull-ups, long rise times up to 1 µs) violates that. Fix: pull-ups ≈ 2.2 kΩ to 3.3 V for a ≤ 100 pF bus, run at 400 kHz, keep the GPS on its own bus or segment if other devices need slower timing, or use UART.

**3 — Choosing rate and constellations for the ZED-F9P rover.** For RTK at 10 Hz you need ≤ 3 constellations (GPS+GLO+GAL: 10 Hz RTK) [1]; with all four you get 7 Hz. For a rocket, 10 Hz GPS+GAL+GLO RTK on the pad/descent and the Airborne <4g model is a reasonable start; output NAV-PVT + NAV-RELPOSNED (if moving base) + RXM-RAWX at 1–5 Hz for post-processing over 921 600 baud.

**4 — Backup supply sizing for a long pad wait.** M10S hardware backup current 28 µA at 3.3 V [2]. A CR1220 (≈ 35 mAh) lasts ≈ 1250 h; a 0.1 F supercap discharging from 3.3 V to 1.65 V gives Q = 0.165 C → 0.165/28×10⁻⁶ ≈ 98 min. For a rocket, simplest is to feed V_BCKP from the flight battery through a diode and keep main power on during the pad wait.

## Practical notes
- **Placement & layout** (u-blox checklists [4][5]): 50 Ω grounded coplanar line from the antenna connector to RF_IN, short, with stitching vias; solid ground under the module and RF line; keep switching regulators, MCU clocks, SD cards and displays away from the antenna and RF trace; VCC series resistance < 0.2 Ω, 1 µF at VCC; no capacitor on RESET_N; route I/O lines (> 3 mm act as antennas) over ground and away from board edges ([RF layout rules](../13-pcb-rf-layout-emc/rf-layout-rules.md)).
- **U.FL on a rocket**: U.FL is rated for few mating cycles and can unmate under vibration; use a retention clip or adhesive, or SMA/MMCX ([connectors](../13-pcb-rf-layout-emc/connectors-and-launches.md)). The Avionics-C has ESD protection at its U.FL — keep it (SAW filters are ESD-sensitive [4]).
- **Firmware versions matter**: operational limits and supported messages differ between HPG 1.12/1.13/1.32 (F9P) and SPG 5.x (M10) — read `MON-VER` at boot and log it ([rocket page](gnss-on-rockets-dynamics-and-limits.md)).
- **Logging for analysis**: `NAV-PVT` (state), `NAV-SAT` (C/N₀ per satellite), `MON-RF` (AGC/jamming/antenna), `RXM-RAWX` + `RXM-SFRBX` (raw data and navigation bits for RTKLIB post-processing), `TIM-TP` (timepulse qErr).
- **Spectrum view**: u-center's spectrum analyser (from `MON-SPAN`) shows in-band interference at the receiver; a peak near the centre frequency is internal and harmless [5].

## Common mistakes & misconceptions
- **"Configuration persists."** Only if saved to BBR (needs V_BCKP) or Flash (F9P); the M10S has no flash.
- **"Toggle RESET_N to recover a stuck GPS."** That's a cold start (≈ 25–30 s TTFF) and erases configuration; use software reset/`CFG-RST` first.
- **"Run I²C at 100 kHz to be safe."** u-blox modules do not support Standard-mode bus operation; use a Fast-mode-compliant bus.
- **"Higher nav rate is free."** Rate is limited by constellations and costs link bandwidth; the receiver may silently drop output messages if the port is too slow.
- **"Any active antenna will do."** Too much gain overloads (F9P max 50 dB; M10S ≤ 30 dB low-gain/≤ 40 dB bypass); too little loses NF; check the LNA mode.

## How to simulate / verify
- Checksums/frames above computed with a 10-line Python Fletcher routine (embedded in the page's derivation; reproduces the documented `MON-VER` poll frame).
- `python3 tools/verify/gnss_timing_pps.py` — UART latency of message bursts vs baud.
- Bench: u-center 2 or a Python UBX parser (pyubx2) — verify ACKs, measure UART loading, and test the recovery ladder by power-cycling and changing baud deliberately.

## Open questions / gaps
- MAX-M10S `CFG-HW-RF_LNA_MODE` default: the M10 interface description lists NORMAL as the chip-level default while the MAX-M10S integration manual says the module defaults to low-gain (module-level configuration); trust the module manual and read the value back.
- Measured `NAV-SAT`/`RXM-RAWX` sizes depend on firmware and satellites tracked; figures above are formula-based.

## Sources
1. u-blox, *ZED-F9P-04B Data sheet*, UBX-21044850 R05, 2024 — UART 9600–921 600, defaults (38 400, NMEA set), SPI 5.5 MHz/125 kB/s, I²C Fast-mode only, V_BCKP 45 µA, RF_IN 10 dBm, external gain 17–50 dB, VCC_RF, max rates, active antenna mandatory, UART2 limitations. https://content.u-blox.com/sites/default/files/ZED-F9P-04B_DataSheet_UBX-21044850.pdf (manufacturer)
2. u-blox, *MAX-M10S Data sheet*, UBX-20035208 R08 — defaults (9600 baud, NMEA set, I²C 0x42), I²C Fast-mode only, V_BCKP 28 µA, RF_IN 0 dBm, NF 1.5 dB, LNA gain modes, rate tables, SAFEBOOT_N–TIMEPULSE tie, PIO back-drive caution. https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf (manufacturer)
3. u-blox, *u-blox F9 HPG 1.32 Interface Description*, UBX-22008968 R01, 2022 — UBX framing/checksum, NAV-PVT, TIM-TP, MON-RF, CFG-VALSET, key IDs and constants. https://content.u-blox.com/sites/default/files/documents/u-blox-F9-HPG-1.32_InterfaceDescription_UBX-22008968.pdf (manufacturer)
4. u-blox, *ZED-F9P Integration manual*, UBX-18010802 R16 — UART/I²C/SPI behaviour, I²C pull-up calculation and EMI capacitors, TX_READY, RESET_N cold start, antenna supervisor, V_BCKP guidance, design checklists. https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf (manufacturer)
5. u-blox, *MAX-M10S Integration manual*, UBX-20053088 R05 — memory permanence table, RESET_N clears BBR, UART baud table and RX lock-out, LNA modes, front-end chain, antenna supervisor, backup modes, spectrum analyser note. https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf (manufacturer)
6. u-blox, *u-blox M10 SPG 5.10 Interface Description*, UBX-21035062 — key IDs identical to F9 (DYNMODEL 0x20110021, RATE-MEAS 0x30210001, UART1-BAUDRATE 0x40520001, MSGOUT NAV_PVT_UART1 0x20910007). https://content.u-blox.com/sites/default/files/u-blox-M10-SPG-5.10_InterfaceDescription_UBX-21035062.pdf (manufacturer)
7. Space Bar avionics knowledge base (user's notes) — Avionics-B I²C lesson, RTK corrections into the GPS via LoRa bridge, Avionics-C buffered UART/timepulse/U.FL+ESD, GPS recovery-ladder lesson. (internal)
