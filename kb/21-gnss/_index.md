# 21-gnss — satellite navigation receivers and their use on rockets

Scope: how GNSS signals are built (GPS, Galileo, BeiDou, GLONASS, QZSS, NavIC, SBAS; BPSK/BOC; codes,
messages, received power), how receivers acquire and track them and compute position, velocity and
time, what limits accuracy (orbit/clock, ionosphere incl. equatorial scintillation over Singapore,
troposphere, multipath, noise, DOP), how carrier-phase RTK/PPK/PPP and correction streams work
(including sizing a LoRa RTCM bridge), how fast a receiver gets a fix (almanac, ephemeris, AssistNow),
how to use the 1PPS for timing and data timestamping, interference/jamming/spoofing and self-interference
from the flight computer's own radios and clocks, the specific behaviour of GNSS on rockets (export
limits, u-blox dynamic models, loss of lock under jerk, oscillator g-sensitivity, antennas, roll), the
practical integration of the u-blox ZED-F9P and MAX-M10S, and software-defined/DIY receivers.
GNSS *antennas* live in [08-antennas/gnss-antennas](../08-antennas/gnss-antennas.md); ionospheric
physics in [09-propagation-link-budget/ionospheric-hf-propagation](../09-propagation-link-budget/ionospheric-hf-propagation.md);
spread-spectrum/Gold-code theory in [10-comms-modulation/spread-spectrum-dsss-fhss-css](../10-comms-modulation/spread-spectrum-dsss-fhss-css.md);
GNSS modules and front-end parts in [18-components-parts](../18-components-parts/rf-modules.md);
LoRa links in [15-lora-ism-radios](../15-lora-ism-radios/_index.md).

Reader context: Space Bar primary FC (Avionics B) uses a **ZED-F9P** (L1/L2 RTK, flown with an L1-only
active antenna; RTK corrections via a separate LoRa bridge straight into the receiver); the secondary
(Avionics C) uses a **MAX-M10S** (L1, U.FL, timepulse to the MCU). Every key number is verified by a
runnable script in `tools/verify/gnss_*.py`.

## Reading order (beginner → advanced)
1. [gnss-signals-and-codes](gnss-signals-and-codes.md) — what the satellites send, how strong it is, why "below the noise" works.
2. [ttff-agps-almanac-ephemeris](ttff-agps-almanac-ephemeris.md) — why the first fix takes ~30 s and how to make it ~1 s.
3. [gnss-receiver-architecture-acquisition-tracking](gnss-receiver-architecture-acquisition-tracking.md) — front end, acquisition, DLL/PLL/FLL, least squares, Kalman.
4. [gnss-error-sources-dop](gnss-error-sources-dop.md) — the error budget, equatorial ionosphere, DOP over Singapore.
5. [gnss-receiver-integration-u-blox](gnss-receiver-integration-u-blox.md) — UBX, CFG-VALSET, rates, UART/I²C, antenna, backup power, resets.
6. [gnss-timing-1pps](gnss-timing-1pps.md) — timepulse, qErr, timestamping flight data, disciplining.
7. [gnss-interference-jamming-spoofing](gnss-interference-jamming-spoofing.md) — J/S, blocking, self-interference tables (E22 channels!), spoofing.
8. [gnss-on-rockets-dynamics-and-limits](gnss-on-rockets-dynamics-and-limits.md) — 500 m/s / 80 km limits (AND/OR), dynamic models, jerk, oscillators, antennas, flight evidence.
9. [rtk-ppp-and-corrections](rtk-ppp-and-corrections.md) — carrier phase, ambiguities, RTCM sizes, LoRa bridge, NTRIP/SiReNT, PPP, PPK.
10. [sdr-gnss-and-diy-receivers](sdr-gnss-and-diy-receivers.md) — GNSS-SDR, Pocket SDR, RTL-SDR, MAX2771, gps-sdr-sim (cabled only).

## Pages
| Page | What it covers | Level | Confidence |
|---|---|---|---|
| [gnss-signals-and-codes](gnss-signals-and-codes.md) | signal table (frequencies, modulations, chip rates, code lengths, messages, minimum powers) for GPS L1 C/A/L1C/L2C/L5, Galileo E1/E5/E6, BeiDou B1I/B1C/B2, GLONASS FDMA, QZSS, SBAS, NavIC; C/A Gold codes; correlation gain; BPSK vs BOC/MBOC spectra; nav-message structures; F9P/M10S signal sets | mixed | high |
| [gnss-receiver-architecture-acquisition-tracking](gnss-receiver-architecture-acquisition-tracking.md) | front-end cascade, ADC quantisation loss, search space, FFT acquisition and P_d/P_fa statistics, coherent vs non-coherent, discriminators, PLL/FLL/DLL jitter and thresholds, dynamic stress, measurements, least squares with clock bias, Kalman filter, update rates, vector tracking | mixed | high |
| [gnss-on-rockets-dynamics-and-limits](gnss-on-rockets-dynamics-and-limits.md) | EAR 7A105/MTCR/USML, u-blox limits per firmware (50 → 80 km) and AND/OR evidence, dynamic models, PLL ± FLL simulation through ignition/burnout, oscillator g-sensitivity and vibration, roll/phase wind-up, antennas, DLR sounding-rocket results, amateur reports | mixed | medium |
| [gnss-receiver-integration-u-blox](gnss-receiver-integration-u-blox.md) | UBX framing and example CFG-VALSET frames, configuration layers (M10S has no flash), defaults (9600 vs 38 400 baud), rates vs constellations, UART/I²C (Fast-mode only)/SPI, recovery ladder, RESET_N cold start, V_BCKP, active-antenna bias and supervisor, layout | intermediate | high |
| [gnss-interference-jamming-spoofing](gnss-interference-jamming-spoofing.md) | J/S tolerance, MAX-M10S immunity curve, isolation budgets, harmonic/intermod tables for E22/E220/2.4 GHz and MCU clocks, E22 channel advice, required harmonic suppression, spoofing types and detection, OSNMA, jamming at altitude | mixed | medium |
| [rtk-ppp-and-corrections](rtk-ppp-and-corrections.md) | carrier-phase model, double differences, float/fixed, LAMBDA, GLONASS biases, RTCM MSM layout and sizes, base-stream budgets, LoRa air-time table, correction age, base set-up, moving base, PPP/PPP-RTK/SBAS/NTRIP/SiReNT, PPK with RTKLIB | mixed | high |
| [gnss-error-sources-dop](gnss-error-sources-dop.md) | UERE budget, SISRE by constellation, ionosphere and equatorial plasma-bubble scintillation (Singapore), Saastamoinen troposphere, multipath error envelopes, receiver noise, DOP derivation and analytic example, synthetic multi-GNSS DOP over Singapore, antenna-tilt effect | mixed | high |
| [ttff-agps-almanac-ephemeris](ttff-agps-almanac-ephemeris.md) | start types, ephemeris/almanac validity, ephemeris-collection-time distributions per system, TTFF budgets, AssistNow Live/Predictive/Autonomous, BBR/RTC, pad and landing procedures | intro | high |
| [gnss-timing-1pps](gnss-timing-1pps.md) | timepulse accuracy, sawtooth and qErr, time bases/leap seconds, PPS-based MCU timestamping (drift, hold-over), disciplining loops, time marks (EXTINT/TIM-TM2) | intermediate | high |
| [sdr-gnss-and-diy-receivers](sdr-gnss-and-diy-receivers.md) | SDR front-end cascades, sample/data rates, oscillator offsets, software pipeline, GNSS-SDR/SoftGNSS/Pocket SDR, MAX2769B/MAX2771, raw-IF recording on rockets, gps-sdr-sim conducted testing and legality | mixed | medium |

## Verification scripts (tools/verify/)
| Script | What it checks | Runtime |
|---|---|---|
| `gnss_signals_link.py` | C/A codes vs IS-GPS-200 table, auto/cross-correlation, chip lengths, BPSK/BOC/MBOC spectra, C/N₀ from minimum powers, sensitivity ↔ C/N₀ | < 5 s |
| `gnss_acquisition.py` | FFT acquisition, P_d vs C/N₀ (Monte Carlo vs non-central χ²), Doppler-bin loss, 1-/2-bit quantisation loss, search time | ≈ 5 s |
| `gnss_tracking_loops.py` | PLL/FLL/DLL jitter and thresholds, dynamic stress, Allan/g-sensitivity/vibration terms, 3rd-order PLL ± FLL through rocket boost profiles | ≈ 2 s |
| `gnss_dop_errors.py` | analytic/numeric DOP, LSQ + clock bias, DOP×UERE Monte Carlo, synthetic constellations over Singapore, tilt masks, troposphere, iono-free, multipath envelopes | ≈ 3 s |
| `gnss_rtcm_bandwidth.py` | MSM4/MSM7 sizes (vs published example), base-stream budgets, LoRa occupancy (uses `lora_toa.py`), wavelengths, ppm budget | < 1 s |
| `gnss_self_interference.py` | clock and radio harmonics vs GNSS bands, E22 channel table, intermod, required harmonic suppression, J/S, jammer distances, M10S isolation | < 1 s |
| `gnss_ttff.py` | ephemeris-collection times (GPS/GLONASS/Galileo), TTFF budgets, almanac times, oscillator search width | ≈ 1 s |
| `gnss_timing_pps.py` | sawtooth/qErr, MCU timestamping with drift/steps/gaps, UART latency, PI disciplining | ≈ 2 s |
| `gnss_sdr_frontend.py` | SDR front-end cascades, sample/data rates, oscillator offsets, simulator attenuation | < 1 s |

## Domain FAQ (top questions → page#section)
- Will my u-blox stop working above 500 m/s or 18/50/80 km? Is it AND or OR? → [rockets#level-3](gnss-on-rockets-dynamics-and-limits.md#level-3--export-controls-and-how-u-blox-implements-limits)
- Why does GNSS lose lock during motor boost and come back after burnout? → [rockets#level-2](gnss-on-rockets-dynamics-and-limits.md#level-2--tracking-loop-stress-oscillators-vibration-roll)
- Which dynamic model should a rocket use? → [rockets#design-equations](gnss-on-rockets-dynamics-and-limits.md#design-equations--rules-of-thumb)
- Which E22 channel won't jam my ZED-F9P? → [interference#level-2](gnss-interference-jamming-spoofing.md#level-2--the-front-end-under-strong-signals)
- How much isolation does a 2 W LoRa transmitter need from a MAX-M10S? → [interference](gnss-interference-jamming-spoofing.md#worked-examples)
- Can LoRa carry RTK corrections? At which air rate? → [RTK#level-3](rtk-ppp-and-corrections.md#level-3--rtcm-3-msm-sizes-link-sizing-latency-ppp)
- Why does u-blox I²C at 100 kHz misbehave? → [integration#worked-examples](gnss-receiver-integration-u-blox.md#worked-examples)
- Why does my GPS cold-start after a reset / battery swap? → [TTFF](ttff-agps-almanac-ephemeris.md#worked-examples), [integration#level-3](gnss-receiver-integration-u-blox.md#level-3--robust-start-up-recovery-and-data-integrity)
- How do I timestamp IMU data with the PPS? → [timing#worked-examples](gnss-timing-1pps.md#worked-examples)
- Why is the GPS signal below the noise yet usable? → [signals#level-2](gnss-signals-and-codes.md#level-2--correlation-processing-gain-and-why-below-the-noise-works)
- How bad is the ionosphere in Singapore; what is scintillation? → [errors#level-3](gnss-error-sources-dop.md#level-3--the-error-sources-in-detail)
- Can I receive GPS with an RTL-SDR? Is gps-sdr-sim legal? → [SDR](sdr-gnss-and-diy-receivers.md)

## Key textbooks and references for this domain (→ [_sources.md](_sources.md))
Kaplan & Hegarty *Understanding GPS/GNSS* 3e; Misra & Enge *Global Positioning System* 2e; Teunissen &
Montenbruck *Springer Handbook of GNSS*; Borre et al. *A Software-Defined GPS and Galileo Receiver*;
IS-GPS-200N/705J/800J; Galileo OS SIS ICD 2.1; BDS B1I/B1C ICDs; u-blox ZED-F9P and MAX-M10S data
sheets, integration manuals and interface descriptions; DLR sounding-rocket GNSS papers (Markgraf,
Montenbruck, Braun et al.); US export-control summary (Office of Space Commerce).

## Known gaps
- u-blox AND/OR logic of the velocity/altitude limits and time-pulse behaviour above 500 m/s are undocumented — needs a cabled simulator test.
- u-blox tracking-loop parameters and TCXO g-sensitivity are unpublished; rocket-dynamics conclusions rest on generic loop models plus DLR flight evidence.
- No quantitative TEC/S4 climatology for Singapore itself; EBYTE harmonic levels unpublished (measure).
- Galileo HAS / MADOCA SSR compatibility with the ZED-F9P not checked; GLONASS ICD minimum power only via search summary.
- Planned project page [gnss-front-end-design](../20-projects-recipes/gnss-front-end-design.md) (domain 20) not yet written.
