# 20-projects-recipes — End-to-end worked designs

Scope: build recipes that stitch the rest of the KB together for the reader's actual projects — Space Bar
rocket telemetry (EBYTE E22-400T33D at 433 MHz, E220-900T30D at 868 MHz in Singapore / 905 MHz at IREC), GNSS on the vehicle
(ZED-F9P, MAX-M10S), ground stations, filters, LNAs, antennas, SDR receivers, radar and arrays. Every
recipe follows the same path: **requirements → architecture options & trade study → design calculations
(scripted in `tools/verify/proj_*.py`) → part selection → block diagram → layout notes → simulation plan →
build & bring-up/test plan with pass/fail fixed in advance → regulatory check (Singapore first) →
pre-registered predictions → risks → cost**. The physics is not re-derived here; each step links to the
page that derives it. Pre-registration follows the team's ethos: predicted numbers with tolerances and
an interpretation of each possible outcome, written before testing.

**New to RF hands-on work? Start with the [beginner project ladder](beginner-project-ladder.md)** (RTL-SDR
reception → a dipole → NanoVNA measurements → a LoRa point-to-point link → an HB100 Doppler radar), then
come back to the recipes below.

## Reading order (beginner → advanced)
0. [beginner-project-ladder](beginner-project-ladder.md) — eleven graded first projects, from an RTL-SDR to direction finding (W5-E6).
1. [lora-rocket-telemetry-link](lora-rocket-telemetry-link.md) — the anchor recipe: the whole downlink for a 10 km flight.
2. [ground-station-tracking-yagi](ground-station-tracking-yagi.md) — the receiving end: Yagis, CP, masthead LNA, tracking, diversity.
3. [sdr-receiver-build](sdr-receiver-build.md) — recording and decoding the downlinks with SDRs; gain staging; Doppler.
4. [bandpass-filter-design-walkthrough](bandpass-filter-design-walkthrough.md) — harmonic low-pass after a 2 W PA; SAW vs LC for RX.
5. [patch-antenna-design-walkthrough](patch-antenna-design-walkthrough.md) — GNSS L1 RHCP patch on JLC FR-4 with openEMS and a mesh-convergence lesson.
6. [lna-design-walkthrough](lna-design-walkthrough.md) — GNSS L1 LNA: MMIC vs pHEMT, stability, SAW-first trade.
7. [gnss-front-end-design](gnss-front-end-design.md) — GNSS on a rocket with 2 W of LoRa: blocking, TX noise, harmonics, channel plan.
8. [fmcw-radar-build](fmcw-radar-build.md) — TI mmWave FMCW radar, corner-reflector calibration, rail-exit velocity.
9. [phased-array-starter-build](phased-array-starter-build.md) — KrakenSDR direction finding for recovery, Phaser lab, array-vs-Yagi verdict.
10. [design-review-checklists](design-review-checklists.md) — schematic / layout / bring-up / pre-flight gates and the automated pre-flight tool.
11. [validation-test-campaign](validation-test-campaign.md) — the pre-registered measurement campaign that tests the KB's predictions (W6-F2).

## Pages
| Page | What it covers | Level | Confidence | Script(s) |
|---|---|---|---|---|
| [beginner-project-ladder](beginner-project-ladder.md) | 11 graded first projects with kit/cost, steps, predictions and KB links: RTL-SDR FM + ADS-B, AIS/APRS, Meteor-M LRPT (NOAA APT ended 2025), NanoVNA 433 MHz dipole, cable loss/velocity factor, tinySA on a LoRa TX, LoRa range test (two-ray prediction ≈ 3.3 km at 10 mW e.r.p.), gr-lora_sdr monitor, HB100 Doppler, 2.4 GHz JLC FR-4 patch, KrakenSDR/two-channel DOA | intro | medium | `e6_beginner_numbers.py`, `e6_lora_antennas.py`, `e6_gain_staging.py` |
| [lora-rocket-telemetry-link](lora-rocket-telemetry-link.md) | 10 km trajectory → Doppler-rate check per SF/BW (SF9/125 fails at 868–905 MHz), air time (SF7/250 51 %), station placement (cross-range 5 km), budgets at legal and licensed power (433 MHz 10 mW e.r.p. 18.8 dB, 2 W 41.3 dB margin at 15 km), landed range, channel plan (band edges, 2f vs secondary, 3f vs GNSS L2), legal attenuator range test | intermediate | medium | `proj_lora_link.py` |
| [ground-station-tracking-yagi](ground-station-tracking-yagi.md) | MoM-checked DL6WU 6/11-el Yagis at 433/868/905 MHz, crossed-Yagi CP harness (and its unequal-split trap), coax/NF cascades, blockers, fixed/hand/rotator tracking losses, diversity, IQ storage | intermediate | medium | `proj_ground_station.py` |
| [sdr-receiver-build](sdr-receiver-build.md) | offset tuning, gr-lora_sdr rates, gain staging by noise rise, 8-bit clip at ≈ −71 dBm → high/low SDR pair, SigMF, timing, pad-referenced Doppler, EBYTE air-rate identification, spectrum survey | intermediate | medium | `proj_sdr_receiver.py` |
| [bandpass-filter-design-walkthrough](bandpass-filter-design-walkthrough.md) | spurious requirement (69/63 dBc at 33 dBm), Chebyshev N=5/7 vs elliptic traps on 2f/3f, real-part models, zero-targeted snapping, 2- vs 4-layer, Monte-Carlo, power dissipation, 905/920 MHz versions, SAW vs LC for RX | intermediate | medium | `proj_harmonic_filter.py` |
| [patch-antenna-design-walkthrough](patch-antenna-design-walkthrough.md) | truncated-corner RHCP patch (cut rule derived by cavity perturbation), openEMS sweeps, handedness, mesh-convergence trap and fix, FR-4 Dk tolerance, tuning, C/N0 | intermediate | medium | `proj_patch_gnss.py`, `proj_openems_gnss_patch.py` |
| [lna-design-walkthrough](lna-design-walkthrough.md) | BGA524N6 vs ATF-54143, K/μ of the bare device, noise vs conjugate match, six cascades with C/N0, own-transmitter blocking, data-sheet disagreement, Y-factor planning | intermediate | medium | `proj_lna_gnss.py` |
| [gnss-front-end-design](gnss-front-end-design.md) | antenna coupling, blocking budgets (48 dB for MAX-M10S vs 2 W), PA wideband-noise desense (needs 40–60 dB TX filtering at 1.5 GHz), 3f jamming of L2, gain windows, logging | intermediate | medium | `proj_gnss_frontend.py` |
| [fmcw-radar-build](fmcw-radar-build.md) | IWR6843/AWR1843 chirp configs (TDM-MIMO v_max/N_TX), SNR for reflectors/people/drones/rocket, rail-exit config (±124 m/s), Singapore 60 GHz SRD and 77–81 GHz UWB-only rule | intermediate | medium | `proj_fmcw.py` |
| [phased-array-starter-build](phased-array-starter-build.md) | KrakenSDR UCA geometry, DOA error vs calibration/multipath, triangulation, Phaser steering/taper, array-vs-Yagi sizing | intermediate | medium | `proj_phased_array.py` |
| [design-review-checklists](design-review-checklists.md) | four gated checklists with IDs/severities/evidence; pre-flight automation | intermediate | medium | `proj_preflight_rf.py` |
| [validation-test-campaign](validation-test-campaign.md) | 40 pre-registered tests (calibration, antennas, transmit, receive, link, rocket-specific, materials/PCB, environment, flight scoring) with predictions, acceptance bands, decision rules (confirmed/refuted/inconclusive, guarded limits), equipment tiers, results-record schema + validator, sequencing and the KB-update protocol (W6-F2) | mixed | medium | `f2_campaign_predictions.py` |

## Domain FAQ (top questions → page#section)
- *Which LoRa SF/BW should my rocket use during boost?* → [telemetry recipe, Level 2 Doppler-rate table](lora-rocket-telemetry-link.md)
- *Is 10 mW e.r.p. enough for a 10 km flight?* → [telemetry recipe, worked examples 3–4](lora-rocket-telemetry-link.md)
- *Is 433.125 MHz legal in Singapore?* → only at ≤ 125 kHz under the 10 mW exemption; use 434.125 MHz for 250 kHz → [telemetry recipe, frequency plan](lora-rocket-telemetry-link.md), [checklists example](design-review-checklists.md)
- *Where should the ground station stand?* → [telemetry recipe, station table](lora-rocket-telemetry-link.md)
- *Which Yagi and how do I make it CP?* → [ground-station recipe](ground-station-tracking-yagi.md)
- *Do I need a harmonic filter after my 2 W module?* → [filter recipe](bandpass-filter-design-walkthrough.md)
- *Why does GPS die when telemetry transmits?* → [GNSS front end](gnss-front-end-design.md)
- *SAW before or after the GNSS LNA?* → [LNA recipe](lna-design-walkthrough.md), [GNSS front end](gnss-front-end-design.md)
- *Can I make my own GNSS patch on JLC FR-4?* → [patch recipe](patch-antenna-design-walkthrough.md)
- *How do I record and decode LoRa with an SDR?* → [SDR recipe](sdr-receiver-build.md)
- *Can a radar measure my rocket's rail-exit speed?* → [FMCW recipe](fmcw-radar-build.md)
- *Should my ground station be a phased array?* → [phased-array starter, example 3](phased-array-starter-build.md)
- *What must be checked before flight?* → [design-review checklists](design-review-checklists.md)

## Key references for this domain (→ [_sources.md](_sources.md))
The recipes rest on the KB's domain pages (01–19, 21) and their verification scripts; external primary
sources (Semtech, EBYTE, Infineon, TI, u-blox, IMDA, Sharma & Gupta, gr-lora_sdr, Yaesu, TDK/Murata,
Mini-Circuits) are listed in `_sources.md`.

## Known gaps
- Hardware evidence: none of the pre-registered predictions has been tested yet; every recipe lists its tests.
- EBYTE air-rate → SF/BW mapping and PA wideband noise at 1.2–1.6 GHz are unmeasured (SDR and GNSS recipes).
- Airframe antenna coupling and installed null depth are assumptions (telemetry, GNSS recipes).
- Rocket/plume RCS at mm-wave unknown (FMCW recipe).
- Venue table of the pre-flight tool covers Singapore and IREC only.
