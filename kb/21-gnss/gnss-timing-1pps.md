---
title: GNSS timing and the 1PPS time pulse — accuracy, quantisation sawtooth (qErr), time bases and leap seconds, disciplining oscillators, and timestamping flight data
domain: 21-gnss
slug: gnss-timing-1pps
tags: [gnss, timing, 1pps, timepulse, tim-tp, qerr, sawtooth, time-mark, extint, tim-tm2, gps-time, utc, leap-seconds, gpsdo, disciplined-oscillator, pi-loop, mcu-timestamp, input-capture, crystal-drift, holdover, sensor-fusion, multi-processor-sync]
prerequisites: [gnss-receiver-architecture-acquisition-tracking.md, ../04-real-components-hf/crystals-and-resonators.md]
related: [gnss-receiver-integration-u-blox.md, gnss-on-rockets-dynamics-and-limits.md, ttff-agps-almanac-ephemeris.md, ../07-noise-linearity/phase-noise-and-jitter.md, ../10-comms-modulation/synchronization-carrier-timing.md]
level: intermediate
confidence: high
last_updated: 2026-10-02
---

# GNSS timing and 1PPS

## Questions this page answers
- How accurate is the u-blox time pulse, and what is the "sawtooth" error?
- What is qErr in UBX-TIM-TP and how do I use it?
- Which time does the pulse mark — GPS time, UTC, Galileo time? What about leap seconds?
- How do I use the PPS to timestamp IMU/baro data on my flight computer to microseconds?
- What happens to timing when the GNSS loses its fix during boost?
- How do I discipline a local oscillator (GPSDO) and how fast should the loop be?
- Can the GNSS timestamp events (launch detect, pyro fire) for me?

## TL;DR
- **TIMEPULSE**: ZED-F9P and MAX-M10S both specify **30 ns RMS, 60 ns 99 %**, configurable 0.25 Hz–10 MHz (default 1PPS) [1][2]. The edge is placed on a receiver-internal clock grid, so each pulse carries a known **quantisation error** that the receiver reports *in advance* in `UBX-TIM-TP.qErr` (ps) — subtracting it removes the sawtooth (simulation: 7.7 ns → 4.8 ns RMS with an assumed 48 MHz grid and 5 ns other noise; `tools/verify/gnss_timing_pps.py`) [3].
- **Use the PPS, not message arrival**, to timestamp: a NAV-PVT takes 26 ms on the wire at 38 400 baud and the default NMEA burst 312 ms (script); arrival jitter is ms-level.
- **Flight-data timestamping**: capture PPS edges with an MCU timer; map MCU ticks → GNSS time by interpolation between PPS captures. With an 18 ppm crystal: one-time sync drifts **2.2 ms in 2 min**; per-second PPS interpolation **< 0.1 µs**; a 30-s PPS gap held over on the last drift estimate with a 0.3 ppm frequency step (temperature/acceleration) → **≈ 9 µs**; the same gap interpolated post-flight → 0.3 µs (script).
- **Time bases**: choose GPS/Galileo/BeiDou/GLONASS time or a UTC variant (`CFG-TP-TIMEGRID_TP1`); align it with the constellations enabled; UTC parameters are broadcast only every 12.5 min (GPS), so a UTC-aligned pulse can be delayed after a cold start [4]. GPS time − UTC = 18 s since 2017 (check IERS bulletins).
- **Locked vs unlocked**: `CFG-TP-USE_LOCKED_TP1` lets the pulse change or stop when the receiver has no valid time; when the fix drops (e.g. > 500 m/s), decide whether you want free-running pulses (continuity) or none (integrity) and log `TIM-TP` flags/`NAV-PVT.tAcc` [4].
- **Time mark**: an edge on EXTINT is timestamped in GNSS time in `UBX-TIM-TM2` — a free event recorder for launch detect or pyro commands [4].
- **Disciplining**: a PI loop steering a local oscillator to the PPS trades PPS jitter (short time constants copy it) against oscillator wander (long ones let it drift); in the toy model τ ≈ 30 s gave 6 ns vs 25–28 ns at 3 s and 300 s (script).

## Intuition (no math)
The receiver computes GNSS time very precisely (tens of nanoseconds) as a by-product of the navigation solution, but it can only *output* an edge when its own internal clock ticks. So the pulse comes out up to half a tick early or late, and that error walks slowly as the receiver clock drifts relative to GNSS time — a sawtooth. Because the receiver knows where the ideal edge should have been, it tells you the error in a message just before the pulse; you subtract it.

Your flight computer's crystal is off by tens of ppm and changes with temperature. Counting its ticks between PPS edges tells you its true frequency every second, so you can convert any MCU timestamp into GNSS time to well below a microsecond — as long as PPS edges keep coming. When they stop (fix lost), you coast on the last frequency estimate; the error grows with the oscillator's frequency change.

## The math

### Level 1 — numbers to know
- PPS accuracy 30 ns RMS (u-blox, both modules) ≈ 9 m of light travel [1][2].
- Quantisation: a grid of period $T_q$ gives error uniform in $\pm T_q/2$, RMS $T_q/\sqrt{12}$ (6 ns for a 48 MHz grid — the actual grid of u-blox modules is not published; qErr reveals it).
- MCU crystal $\pm\epsilon$ ppm → drift $\epsilon\times10^{-6}\times t$: 20 ppm = 1.2 ms per minute.
- Timer resolution: 1/f_timer (6.7 ns at 150 MHz, 12.5 ns at 80 MHz).

### Level 2 — the timestamp model
MCU tick count $k(t) = \int_0^t f_{nom}(1+y(t'))dt'$ with fractional frequency error $y(t)$ (ppm offset + temperature drift + acceleration steps). PPS edge $n$ occurs at GNSS time $t_n = n$ s (+ qErr-corrected jitter) and is captured as $k_n$. Between edges,
$$\hat t(k) = t_n + \frac{k - k_n}{k_{n+1}-k_n}\,(t_{n+1}-t_n)$$
(piecewise-linear interpolation; post-processing) or, in real time, extrapolation with the last estimated rate $\hat f = (k_n - k_{n-m})/m$. Errors:
- capture jitter: ±1 tick + PPS jitter (30 ns) → tens of ns;
- interpolation error within a second: $\tfrac18\ddot y\,(1\text{ s})^2$ — negligible unless the frequency changes fast;
- real-time hold-over over a gap $\Delta$: $\approx \Delta y\cdot\Delta$ for a frequency step $\Delta y$ at the gap start (0.3 ppm × 30 s = 9 µs), plus $\tfrac12\dot y\Delta^2$ for a drift.

**Script results** (150 MHz timer, 18 ppm + 0.02 ppm/min drift + 0.3 ppm step at t = 40 s, PPS 30 ns rms, ±1 tick capture noise): (a) one sync with nominal frequency 2168 µs max error over 2 min; (b) PPS each second, interpolated: 0.08 µs max; (c) 30-s gap held over in real time: 9.4 µs max; (c′) same gap interpolated post-flight: 0.27 µs [script].

**Sawtooth correction**: if the receiver's pulse is emitted at $t_{PPS} = t_{ideal} + q_n$ with $q_n$ known from TIM-TP (which refers to the *next* pulse), the corrected timestamp is $t_{PPS} - q_n$. u-blox recommends 1 Hz measurement rate and 1 Hz pulse when using TIM-TP so there is exactly one TIM-TP per pulse; at higher pulse rates several TIM-TP messages may fall between pulses and the last one before the pulse is the relevant one [4].

### Level 3 — disciplining, time scales, multi-receiver timing
**Disciplined oscillator (GPSDO).** Phase error $x_n$ between local and PPS time, measured each second with white noise $\sigma_{PPS}$; local oscillator frequency random walk. A PI loop $u_n = k_p x_n + k_i\sum x$ with $k_p = 2/\tau$, $k_i = 1/\tau^2$ (critically damped, time constant τ) steers the oscillator. The optimum τ is where the PPS noise filtered by the loop equals the oscillator's free-running wander over τ — i.e. where the oscillator's Allan deviation crosses the PPS's ($\sigma_y^{PPS}(\tau) \approx \sigma_x\sqrt{3}/\tau$): seconds to tens of seconds for a TCXO, 100–1000 s for an OCXO ([phase noise and jitter](../07-noise-linearity/phase-noise-and-jitter.md)). Toy-model results: τ = 3, 30, 300 s → 25.5, 6.4, 28.0 ns rms (script; depends entirely on the assumed noise levels).

**Time scales.** GPS time is continuous (no leap seconds) and was aligned with UTC on 6 Jan 1980; GPS − UTC = 18 s since 1 Jan 2017 (subject to IERS announcements). Galileo System Time is aligned to GPS time; BeiDou Time started 2006 (BDT = GPST − 14 s); GLONASS time follows UTC(SU) + 3 h including leap seconds. The receiver converts using broadcast parameters; with the "automatic" UTC standard u-blox chooses USNO if GPS is enabled, then SU, NTSC, EU, NPLI [4]. Different UTC realisations differ by up to a few hundred ns [4]. `NAV-PVT.valid` bits (`validDate`, `validTime`, `fullyResolved`) say whether the UTC fields can be trusted [3].

**Cable and user delays.** The pulse can be advanced for antenna-cable delay (≈ 5 ns/m in coax) and offset by a user delay; for absolute timing calibrate the whole setup against a reference [4]. For relative timing between two receivers (e.g. two flight computers), use the same product family or calibrate [4].

**Time mark (EXTINT).** A rising/falling edge on EXTINT is timestamped and reported in `UBX-TIM-TM2` at the next navigation epoch, with time base, validity and accuracy estimate; the same delay settings apply [4].

## Design equations & rules of thumb

| Item | Value | Source |
|---|---|---|
| TP accuracy | 30 ns RMS / 60 ns 99 % | [1][2] |
| TP frequency | 0.25 Hz–10 MHz; high/low ≥ 50 ns | [1][4] |
| Sawtooth RMS | $T_q/\sqrt{12}$; remove with qErr | [3], script |
| TIM-TP usage | 1 Hz nav + 1 Hz TP | [4] |
| Crystal drift | 1.2 ms/min per 20 ppm | arithmetic |
| PPS interpolation error | < 0.1 µs | script |
| Hold-over error | Δy × Δt (0.3 ppm × 30 s = 9 µs) | script |
| UTC broadcast | every 12.5 min (GPS) | [4] |
| Coax delay | ≈ 5 ns/m | physics |

## Worked examples
**1 — Timestamping 1 kHz IMU data on the Avionics-B Teensy 4.1.** Route ZED-F9P TIMEPULSE (4 mA drive [1]) to a GPT/QTimer input-capture pin; run the timer from the 150 MHz IPG clock (6.7 ns ticks). Each PPS: store (k_n, iTOW of the following NAV-PVT/TIM-TP, qErr). Timestamp every IMU sample with the raw tick count. Post-flight: interpolate ticks → GPS time between PPS captures (< 0.1 µs where PPS exists). Real time: extrapolate with the rate from the last 5 PPS (≈ µs-level). Result: IMU, baro and GNSS share one time axis to well below the 1 ms sample period.

**2 — Two processors, one PPS.** The Space Bar notes record that the inter-processor clocks *step*, and TIME_SYNC pairs were used. Feed the same PPS to both the Teensy and the ESP32-S3; each maps its own ticks to GNSS time; the logs then align to < 1 µs without a sync protocol, and steps in either clock are detected as discontinuities in its tick-vs-PPS fit.

**3 — The fix drops above 500 m/s.** For ≈ 5–8 s the receiver may report no valid fix ([rocket page](gnss-on-rockets-dynamics-and-limits.md)). If `USE_LOCKED_TP1` is set with a "locked" configuration and an "unlocked" configuration that keeps 1 Hz, the pulse continues from the receiver's own clock (its accuracy degrades slowly; read `TIM-TP` flags and `NAV-PVT.tAcc`); if the unlocked configuration disables the pulse, your flight computer must hold over (≈ 9 µs per 30 s per 0.3 ppm of frequency change). Either is far better than needed for flight events; just log which happened.

**4 — Recording the launch-detect instant.** Wire the MCU's launch-detect output (or the pyro-fire command line through a buffer) to EXTINT; enable `TIM-TM2`. Each edge is timestamped by the GNSS in GPS time with its accuracy estimate — an independent check on the flight computer's own event log.

## Practical notes
- **MAX-M10S**: TIMEPULSE shares the SAFEBOOT_N function (internal 1 kΩ) — never pull TIMEPULSE low at power-up, and buffer it if it drives long wires or several inputs [5].
- **Back-powering**: don't drive EXTINT or other PIOs while the module is unpowered (hardware backup) — use buffers (as the Avionics-C does for UART) [5].
- **Configure the pulse explicitly**: period 1 s, length 100 ms, aligned to TOW, GPS time grid, locked/unlocked behaviour as decided; save to BBR.
- **Check the polarity and which edge is on time** (rising by default when polarity bit set) [4].
- **SBAS degrades time accuracy** (u-blox note) — disable SBAS if time accuracy matters [1].

## Common mistakes & misconceptions
- **"The NMEA sentence time is the time of the PPS."** The message describes the epoch, but arrives tens to hundreds of ms later; latency varies with load and baud rate.
- **"The PPS is exact."** It has the sawtooth (up to ±T_q/2) unless corrected with qErr, plus ≈ 30 ns noise.
- **"GPS time = UTC."** 18 s apart (and GPS time has no leap seconds).
- **"Once synced, the MCU clock stays synced."** 20 ppm = 1.2 ms/min.

## How to simulate / verify
- `python3 tools/verify/gnss_timing_pps.py` — sawtooth and qErr correction, MCU timestamping with drift/steps/gaps, UART latency, PI disciplining vs time constant. ALL PASS.
- Bench: PPS of the module and of a reference GPSDO into a time-interval counter or oscilloscope with histogram; apply qErr and compare; log the MCU's tick count per PPS over temperature (freezer/heat gun) to measure your crystal's drift.

## Open questions / gaps
- The internal pulse-generation clock period (and hence raw sawtooth amplitude) of the ZED-F9P/MAX-M10S is not published — measure qErr.
- Whether the time pulse keeps running (and with what accuracy) during the u-blox > 500 m/s cut-off is undocumented — test with a simulator.
- The disciplining simulation uses arbitrary noise levels; a real design needs the oscillator's Allan deviation.

## Sources
1. u-blox, *ZED-F9P-04B Data sheet*, UBX-21044850 R05 — TP accuracy 30 ns RMS / 60 ns 99 %, 0.25 Hz–10 MHz, TIMEPULSE 4 mA drive, SBAS degrades time accuracy. https://content.u-blox.com/sites/default/files/ZED-F9P-04B_DataSheet_UBX-21044850.pdf (manufacturer)
2. u-blox, *MAX-M10S Data sheet*, UBX-20035208 R08 — TP accuracy 30/60 ns, default 1PPS, TIMEPULSE/SAFEBOOT_N tie. https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf (manufacturer)
3. u-blox, *u-blox F9 HPG 1.32 Interface Description*, UBX-22008968 — UBX-TIM-TP (towMS, towSubMS, qErr in ps, qErrInvalid, time base/UTC standard), NAV-PVT validity bits and tAcc. https://content.u-blox.com/sites/default/files/documents/u-blox-F9-HPG-1.32_InterfaceDescription_UBX-22008968.pdf (manufacturer)
4. u-blox, *ZED-F9P Integration manual*, UBX-18010802 R16 — §3.13 timing: recommendations (1 Hz TIM-TP), GNSS time bases and UTC variants (automatic preference order; differences of a few hundred ns; UTC every 12.5 min), CFG-TP-* parameters incl. locked/unlocked and delays, 50 ns minimum high/low, example 1PPS configuration, §3.13.2 time mark (TIM-TM2). https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf (manufacturer)
5. u-blox, *MAX-M10S Integration manual*, UBX-20053088 R05 — §3.9 time pulse (grid options, 50 ns rule), §3.8 time mark, PIO back-drive caution. https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf (manufacturer)
6. E. D. Kaplan, C. J. Hegarty (eds.), *Understanding GPS/GNSS*, 3rd ed., 2017 — GNSS time scales, timing receivers. (textbook; general reference)
7. D. W. Allan, N. Ashby, C. C. Hodge, *The Science of Timekeeping*, HP Application Note 1289, 1997 — Allan deviation, disciplined oscillators, GPS time transfer. (app note; general reference)
8. Space Bar avionics knowledge base (user's notes) — Avionics-C timepulse to MCU, inter-processor clock steps and TIME_SYNC pairs. (internal)
