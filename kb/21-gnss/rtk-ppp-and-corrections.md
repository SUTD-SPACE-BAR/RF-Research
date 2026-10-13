---
title: RTK, PPP and corrections — carrier phase, integer ambiguities, RTCM 3 MSM messages and bandwidth, sizing a LoRa corrections link, NTRIP, SBAS, PPP/PPP-RTK, moving base, PPK and RTK under high dynamics
domain: 21-gnss
slug: rtk-ppp-and-corrections
tags: [gnss, rtk, ppk, ppp, ppp-rtk, ppp-ar, carrier-phase, integer-ambiguity, double-difference, lambda, wide-lane, rtcm3, msm4, msm7, rtcm-1005, rtcm-1230, rtcm-4072, ntrip, sirent, sbas, spartn, clas, madoca, galileo-has, moving-base, zed-f9p, lora-bridge, e22, correction-age, rtklib]
prerequisites: [gnss-receiver-architecture-acquisition-tracking.md, gnss-error-sources-dop.md, gnss-signals-and-codes.md]
related: [gnss-receiver-integration-u-blox.md, gnss-on-rockets-dynamics-and-limits.md, ../15-lora-ism-radios/rocket-telemetry-radio-design.md, ../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md, ../15-lora-ism-radios/ism-band-plans-duty-cycle.md, ../19-regulations-safety/singapore-imda-rules.md, ../09-propagation-link-budget/ionospheric-hf-propagation.md]
level: mixed
confidence: high
last_updated: 2026-10-02
---

# RTK, PPP and GNSS corrections

## Questions this page answers
- How does RTK get centimetre accuracy when GNSS code ranges are good to metres?
- What is an integer ambiguity, "float" vs "fixed", and why does dual frequency make fixing faster?
- Which RTCM 3 messages does a ZED-F9P base send, and how many bytes per second is that?
- Can a LoRa link (E22/E220) carry RTK corrections to a rocket? At which air rate?
- What happens when corrections arrive late or get lost?
- What are NTRIP, SBAS, PPP, PPP-RTK (SPARTN/CLAS), Galileo HAS and MADOCA, and which are usable in Singapore?
- What is moving-base RTK?
- Does RTK work on a rocket during boost? Is post-processed kinematic (PPK) better?

## TL;DR
- **RTK** differences the rover's carrier phase (λ ≈ 19 cm at L1, mm-level noise) against a nearby **base** with a known position. Double differences cancel satellite and receiver clocks and most orbit/atmosphere errors over short baselines; the unknown integer cycle counts (**ambiguities**) are estimated as real numbers (**float**, dm-level) and then fixed to integers (**fixed**, cm-level). ZED-F9P: 0.01 m + 1 ppm CEP, convergence < 10 s with multi-GNSS dual-band (< 30 s GPS-only) [1].
- **Corrections stream (base → rover)**: RTCM 3 **1005** (base position) + **MSM4** per constellation (1074 GPS, 1084 GLONASS, 1094 Galileo, 1124 BeiDou) + **1230** (GLONASS biases; needed to fix GLONASS) — u-blox's recommended list; all observation messages at the same rate, don't mix MSM4/MSM7 [2]. The rover drops corrections older than **60 s** by default (`CFG-NAVSPG-CONSTR_DGNSSTO`) [2].
- **Size** (field layout verified against RTKLIB and a published 16-SV × 4-signal example: 3593/5929 bits): with Singapore-like counts (GPS 10, GLO 7, GAL 9, BDS 16), dual-frequency MSM4 at 1 Hz ≈ **710 B/s**; MSM7 ≈ 1130 B/s; **L1-only** MSM4 ≈ 466 B/s; GPS+GAL dual ≈ 322 B/s; GPS+GAL L1-only ≈ 216 B/s (`tools/verify/gnss_rtcm_bandwidth.py`). A u-blox forum user measured 700–750 B/s for a full F9P MSM4 set [6].
- **LoRa bridge**: in 240-byte packets the full dual-frequency stream occupies ≈ **10 %** of air time at SF5/500 kHz (EBYTE "62.5k"), 28 % at SF7/500, 56 % at SF7/250, 112 % at SF7/125 and 352 % at SF9/125 — so a LoRa corrections link must use **≥ 250–500 kHz bandwidth and SF5–7**, or shed constellations/frequencies (script). The EBYTE default 2.4k air rate (≈ 300 B/s ceiling) cannot carry it.
- **On a rocket**: carrier-phase slips at ignition/burnout force float; the F9P's RTK rate drops to 7 Hz with 4 GNSS (20 Hz GPS-only) [1]; an L1-only antenna slows fixing. For trajectory reconstruction, **log raw data (RXM-RAWX/SFRBX) on rocket and base and post-process (PPK, e.g. RTKLIB)** — no radio link, forward-backward smoothing, cycle-slip repair.
- **Other corrections**: SBAS (≈ 1 m, regional — none covers Singapore), PPP (no base, dm–cm after 20–30 min convergence; PPP-RTK SPARTN < 45 s, CLAS < 70 s on F9P [1]), NTRIP (internet RTCM; Singapore's **SiReNT** network by the Singapore Land Authority, subscription) [7].

## Intuition (no math)
Code pseudoranges are like measuring distance with a ruler marked every 300 m and reading it to a few metres. The carrier is a ruler marked every 19 cm that you can read to a millimetre — but you don't know how many whole marks lie between you and the satellite. If a base station a few kilometres away measures the same satellites, almost every error (satellite clock and orbit, ionosphere, troposphere) is the same for both of you; subtracting removes them. What is left is your relative position plus a set of unknown whole numbers of wavelengths. With enough satellites, geometry change and dual frequencies, there is only one set of integers that makes everything consistent — finding it is "fixing", after which you know your position relative to the base to about a centimetre.

The catch: you need the base's measurements in real time (a radio link) and you must keep continuous phase lock. Every cycle slip (a jump of whole wavelengths) on a satellite breaks its ambiguity, and if many slip at once (motor ignition, roll, plume) the solution falls back to float until the integers are found again.

## The math

### Level 1 — the measurements and the error budget
Carrier phase in metres for satellite $s$, receiver $r$, frequency $f$ ($\lambda = c/f$):
$$\Phi_r^s = \rho_r^s + c(\delta t_r - \delta t^s) + T_r^s - I_r^s + \lambda N_r^s + \epsilon_\Phi,\qquad \sigma_{\epsilon_\Phi}\approx 1\text{–}3\text{ mm}$$
versus code $P_r^s = \rho_r^s + c(\delta t_r - \delta t^s) + T_r^s + I_r^s + \epsilon_P$, $\sigma_{\epsilon_P}$ ≈ 0.3–3 m ([receiver page](gnss-receiver-architecture-acquisition-tracking.md)). Wavelengths: L1 19.03 cm, L2 24.42 cm, L5 25.48 cm; wide-lane L1–L2 86.2 cm; narrow-lane 10.7 cm (script).

**Relative accuracy** after fixing: u-blox specifies 0.01 m + 1 ppm (CEP horizontal) for baselines ≤ 20 km [1]: 1.1 cm at 1 km, 2 cm at 10 km. The ppm term is the decorrelation of orbit and atmospheric errors with distance.

### Level 2 — differencing and ambiguity resolution
**Single difference** between receivers $r$ (rover) and $b$ (base) for satellite $s$: $\Delta\Phi^s = \Phi_r^s - \Phi_b^s$ removes the satellite clock $\delta t^s$ and, for short baselines, most of $I$, $T$ and orbit error. **Double difference** with a reference satellite $k$: $\nabla\Delta\Phi^{sk} = \Delta\Phi^s - \Delta\Phi^k$ also removes the receiver clocks:
$$\nabla\Delta\Phi^{sk} = \nabla\Delta\rho^{sk} + \lambda\nabla\Delta N^{sk} + \nabla\Delta\epsilon,\qquad \nabla\Delta\rho^{sk} \approx -(\hat{\mathbf u}^s - \hat{\mathbf u}^k)\cdot\mathbf b + \dots$$
with $\mathbf b$ the base-to-rover baseline vector. With $n$ satellites on two frequencies there are $2(n-1)$ DD equations per epoch, 3 baseline unknowns and $2(n-1)$ constant integers.

**Float solution**: a Kalman filter estimates $\mathbf b$ and the ambiguities as reals from code + phase. **Integer fixing**: search for the integer vector minimising $(\hat{\mathbf a} - \mathbf a)^T\mathbf Q_{\hat a}^{-1}(\hat{\mathbf a}-\mathbf a)$; the LAMBDA method decorrelates $\mathbf Q_{\hat a}$ first so the search is fast; the fix is accepted if the second-best candidate is sufficiently worse (ratio test, typically ≥ 2–3) [8]. **Why dual frequency helps**: the wide-lane combination ($\lambda_{WL}$ = 86 cm) is easy to fix from code; then the remaining ambiguities follow; the ionosphere, which differs between frequencies, can be estimated. That's why the ZED-F9P is specified with an L1/L2 antenna and why fixing with the team's L1-only antenna is slower and less reliable.

**GLONASS FDMA**: different wavelengths per satellite make the DD ambiguities non-integer unless the inter-frequency (code–phase) biases between different receiver brands are known — the purpose of RTCM 1230 (or 1033 descriptors); without it the F9P keeps GLONASS ambiguities float [2].

### Level 3 — RTCM 3 MSM sizes, link sizing, latency, PPP
**RTCM 3 framing**: preamble 0xD3, 6 reserved bits, 10-bit length, payload ≤ 1023 bytes, 24-bit CRC-24Q — 6 bytes of overhead per message.

**MSM (Multiple Signal Message) layout** (from the RTKLIB encoder [5]):
- Header 169 bits = 12 type + 12 station ID + 30 epoch + 1 multiple-message + 3 IODS + 7 reserved + 2 clock steering + 2 external clock + 1 smoothing + 3 smoothing interval + 64-bit satellite mask + 32-bit signal mask, followed by an $N_{sat}\times N_{sig}$ cell mask.
- **MSM4**: 18 bits per satellite (integer + modulo-1 ms rough range) and 48 bits per cell (15 fine pseudorange, 22 fine phase, 4 lock-time, 1 half-cycle, 6 C/N₀).
- **MSM7**: 36 bits per satellite (adds extended info and rough phase-range rate) and 80 bits per cell (20 + 24 + 10 + 1 + 10 + 15 incl. fine phase-range rate).
- Check: 16 satellites × 4 signals → MSM4 3593 bits, MSM7 5929 bits — matches the published example (script).
- 1005: 152 bits (19 B + 6 = 25 B); 1230 with four biases: 96 bits (18 B framed).

**Base stream** (1 Hz MSM; 1005 and 1230 every 10 s; satellites GPS 10 (8 with L2C), GLO 7, GAL 9, BDS 16):

| Stream | B/s | Bytes per epoch |
|---|---|---|
| GPS+GLO+GAL+BDS dual-band MSM4 (u-blox list) | 712 | 708 |
| same, MSM7 | 1134 | 1130 |
| 4 GNSS, L1-only MSM4 | 466 | 462 |
| GPS+GAL dual MSM4 | 322 | 319 |
| GPS+GAL L1-only MSM4 | 216 | 214 |
| GPS only, L1-only MSM4 | 114 | 111 |

**LoRa air time** (SX126x formula from `tools/verify/lora_toa.py`, 240-byte packets, CR 4/5, 8-symbol preamble, explicit header + CRC):

| Setting | ToA of 240 B | Full 4-GNSS dual | GPS+GAL dual | GPS+GAL L1 |
|---|---|---|---|---|
| SF5 / 500 kHz (EBYTE "62.5k") | 32.5 ms | 10 % | 4 % | 3 % |
| SF7 / 500 kHz | 94.8 ms | 28 % | 13 % | 9 % |
| SF7 / 250 kHz | 190 ms | 56 % | 26 % | 17 % |
| SF7 / 125 kHz | 379 ms | 112 % (impossible) | 53 % | 34 % |
| SF9 / 125 kHz | 1189 ms | 352 % | 165 % | 108 % |

Packet loss matters too: an epoch split over 3–4 packets is useless if any one is lost (MSM for a constellation is self-contained, but the rover needs all constellations' messages of the *same* epoch for best results). Options: one constellation per packet; send at 0.5 Hz (the F9P tolerates older corrections, at some accuracy cost); compress (a forum user reports 15–17 % by stripping u-blox slack and ≈ 36 % with delta-XOR + zlib [6] — unvalidated); or prefer PPK.

**Correction age.** Rover processing extrapolates the base observations; errors grow with age through satellite clock dither and atmospheric change. u-blox drops corrections > 60 s old (configurable) [2]; practical RTK wants 1 Hz with ≤ 1–2 s latency. The flag `UBX-NAV-PVT.carrSoln` (0 none / 1 float / 2 fixed) and the reported correction age tell you what is happening [2].

**Base set-up** (u-blox [2]): survey-in (`CFG-TMODE-MODE = SURVEY_IN` with minimum duration and accuracy limit) or fixed coordinates (`…FIXED`, ECEF/LLH with mm HP fields). An error in base coordinates shifts the rover's absolute position one-for-one (relative vector unaffected). The base must not receive corrections during survey-in. Station ID in 1005 must match the MSM messages. A warning is issued if the baseline exceeds 100 km (50 km on HPG 1.12) [2].

**Moving base** (ZED-F9P, not in the L1/L5 HPG 1.40 firmware): both antennas move; the base outputs RTCM including **4072.0/4072.1** (u-blox proprietary), the rover outputs `NAV-RELPOSNED` — heading 0.3–0.4° at 1 m baseline; identical antennas with identical orientation recommended [1][2]. On a rocket two antennas a body-length apart could in principle give attitude, but antenna placement, roll and cycle slips make this a research project.

**PPP and SSR.** Precise Point Positioning uses precise orbits/clocks/biases (state-space representation, SSR) instead of a base: float convergence typically 20–30 min to dm-level; with ambiguity resolution (PPP-AR) and atmospheric corrections (**PPP-RTK**) convergence drops to seconds–minutes. The ZED-F9P-04B accepts **SPARTN 2.0.1** (u-blox PointPerfect; < 0.06 m H, convergence < 45 s) and **CLAS** via a NEO-D9C L6 receiver (Japan; 0.04 m, < 70 s) [1]. Other SSR sources: Galileo **HAS** (free, E6-B and internet) and QZSS **MADOCA-PPP** (L6E and internet, Asia-Oceania) — the F9P cannot receive E6/L6 directly (gap: compatibility with the F9P's SPARTN/RTCM-SSR inputs not checked).

**SBAS** broadcasts orbit/clock corrections and an ionospheric grid from GEO satellites (L1, 250 b/s) for its service region: ZED-F9P 1.0 m CEP with SBAS vs 1.5 m without [1]. Singapore lies outside WAAS/EGNOS/MSAS/GAGAN/KASS/SouthPAN coverage; GEOs may be in view but their ionospheric grid does not describe the local equatorial ionosphere.

**NTRIP** (Networked Transport of RTCM via Internet Protocol): an HTTP-like protocol — a *server* (base) pushes RTCM to a *caster*, *clients* (rovers) request a *mountpoint* from the caster's source table with credentials. In Singapore the SLA's **SiReNT** CORS network provides RTK and DGNSS streams (RTCM 2.3/3.1/3.2, CMR) via NTRIP to subscribers, with free short-term trials [7]; an NTRIP client on the ground station can forward the stream over the LoRa bridge (but launch sites abroad need a local base).

## Design equations & rules of thumb

| Item | Value | Source |
|---|---|---|
| RTK accuracy (F9P) | 0.01 m + 1 ppm CEP, ≤ 20 km | [1] |
| RTK convergence (F9P) | < 10 s multi-GNSS; < 30 s GPS-only | [1] |
| Max RTK rate (F9P) | 7 Hz (4 GNSS), 10 Hz (3), 20 Hz (GPS) | [1] |
| Base message set | 1005 + 1074/1084/1094/1124 + 1230 | [2] |
| Correction cut-off | 60 s default | [2] |
| MSM4 size | 169 + N_sat·N_sig + 18 N_sat + 48 N_cell bits | [5], script |
| Full F9P base stream | ≈ 700 B/s (MSM4) | script, [6] |
| LoRa for corrections | SF5–7 at 250–500 kHz | script |
| Wide-lane L1–L2 | 86.2 cm | script |
| PPP-RTK (SPARTN) convergence | < 45 s | [1] |

## Worked examples
**1 — Sizing the Avionics-B LoRa RTK bridge.** The base is a ZED-F9P with an L1/L2 antenna; the rover flew an L1-only antenna. Sending dual-frequency observations to an L1-only rover wastes bandwidth: configure the base for the rover's signals. GPS+GAL+BDS L1-only MSM4 ≈ 420 B/s (subset of the 466 B/s 4-GNSS figure). In 240-byte packets that is 2 packets/s: 6.5 % air time at SF5/500, 19 % at SF7/500. At the E22's default 2.4k air rate (ceiling ≈ 300 B/s even at 100 % occupancy) it cannot work; choose the 62.5k air rate (SF5/BW500) or a bare SX126x at SF7/500 and verify the regulatory duty-cycle limits for a *continuously transmitting ground transmitter* in the band used ([Singapore rules](../19-regulations-safety/singapore-imda-rules.md), [band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md)). Never put the corrections receiver in the same band as the 2 W telemetry transmitter on the rocket ([telemetry design](../15-lora-ism-radios/rocket-telemetry-radio-design.md)).

**2 — How long is the baseline during flight?** At 300 m/s for 10 s the rover is 3 km from the base; at 500 m/s for 20 s, 10 km. The ppm term adds 0.3–1 cm — negligible. RTK is limited by phase continuity and antenna quality, not distance.

**3 — Correction latency on the rocket.** If the bridge delivers each epoch 400 ms late and the rocket moves at 250 m/s, the rover is extrapolating the base data by 0.4 s — fine; the rover's own position is computed at its own epoch. Loss of 3 consecutive epochs (link fade during roll) leaves 3 s old corrections — still usable; a 60 s outage drops to standalone.

**4 — PPK instead of RTK.** Log `RXM-RAWX` + `RXM-SFRBX` at 5–10 Hz on the rocket (≈ 2.6 kB per epoch with 80 measurements → 13–26 kB/s to the SD card) and at 1 Hz on a base on the pad; convert with RTKLIB `convbin` to RINEX, process with `rnx2rtkp` (kinematic, forward + backward combined). Backward processing re-fixes ambiguities after boost-phase slips using post-burnout data; no corrections radio needed. This is the recommended route to cm–dm trajectory reconstruction for coast and descent.

## Practical notes
- **Rover messages**: `NAV-PVT` (carrSoln, correction age), `NAV-RELPOSNED` (relative vector to the base), `NAV-HPPOSLLH` (mm resolution), `NAV-SAT` flags (`rtcmCorrUsed`) [2].
- **Antenna**: RTK needs good phase centre stability and multipath rejection: u-blox asks for C/N₀ > 40 dB-Hz average for optimal RTK and a ≥ 100–150 mm ground plane for patches [2] — hard on a rocket ([GNSS antennas](../08-antennas/gnss-antennas.md)).
- **Datum**: the rover's coordinates are in the base's datum (survey-in = WGS84-ish standalone accuracy, a few m absolute); for absolute cm accuracy, survey the base with PPP or tie it to a SiReNT/CORS mark.
- **Same rate rule**: all MSM observation messages at the same rate; 1005 can be slower but the rover needs one before it can compute [2].
- **Testing the bridge**: measure end-to-end throughput and latency with the RTCM stream itself (count 1005/MSM messages and CRC failures at the rover's UART2), with the rocket's telemetry transmitter keyed.

## Common mistakes & misconceptions
- **"RTK float is almost as good as fixed."** Float is dm-level and can drift; only fixed is cm-level.
- **"More constellations always help RTK over a thin link."** They cost bandwidth; a fixed solution with GPS+GAL L1/L2 beats a starved four-constellation stream.
- **"Corrections can be sent at any rate."** The F9P wants all observation messages at the same rate and matched to its GNSS configuration [2].
- **"GLONASS will fix without 1230."** It stays float [2].
- **"SBAS is free accuracy anywhere."** Only inside its service region; elsewhere it may hurt.

## How to simulate / verify
- `python3 tools/verify/gnss_rtcm_bandwidth.py` — MSM sizes (checked vs published example), base-stream budget, LoRa occupancy (imports `lora_toa.py`), wavelengths, ppm budget. ALL PASS.
- RTKLIB (`rtknavi`/`rtkpost`/`str2str`) to replay recorded RAWX data, test float/fix behaviour, and simulate correction dropouts; `str2str` also bridges NTRIP ↔ serial for the ground station.

## Open questions / gaps
- Actual satellite counts above Singapore with the real constellations (vs the assumed 10/7/9/16) — log `NAV-SAT` at the launch site.
- The EBYTE 2.4k–38.4k air-rate SF/BW mapping is unknown ([LoRa modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)); only 62.5k is identified (SF5/500).
- Fixing performance of an L1-only F9P rover on a rocket: no data; PPK recommended until measured.
- Whether Galileo HAS / MADOCA SSR can be converted for the F9P's inputs was not checked.

## Sources
1. u-blox, *ZED-F9P-04B Data sheet*, UBX-21044850 R05 (HPG 1.32), 2024 — RTCM in/out tables, SPARTN/CLAS, accuracies (RTK 0.01 m + 1 ppm; SBAS 1.0 m; PVT 1.5 m), convergence, max RTK rates, moving-base heading. https://content.u-blox.com/sites/default/files/ZED-F9P-04B_DataSheet_UBX-21044850.pdf (manufacturer)
2. u-blox, *ZED-F9P Integration manual*, UBX-18010802 R16 — §3.1.5 RTK configuration: RTCM 10403.4, rover requirements (MSM + 1005/1006; 1230/1033 for GLONASS), 60-s correction timeout, RTK modes, NAV-PVT carrSoln, survey-in/fixed base, recommended base messages, same-rate/no-mixing rules, moving base; checklist (C/N₀ > 40 for RTK). https://content.u-blox.com/sites/default/files/ZED-F9P_IntegrationManual_UBX-18010802.pdf (manufacturer)
3. RTCM Special Committee 104, *RTCM Standard 10403.3/10403.4 — Differential GNSS Services Version 3* (not read; paywalled). https://rtcm.myshopify.com/ (standard — cited via [2], [5])
4. NovAtel, "RTCMV3 standard logs" documentation — MSM size example (16 SVs × 4 signals: MSM4 3593 bits, MSM7 5929 bits) (via search summary). https://docs.novatel.com/OEM7/Content/Logs/RTCMV3_Standard_Logs.htm (manufacturer documentation)
5. T. Takasu, RTKLIB `src/rtcm3e.c` (RTCM 3 encoder, GitHub master) — MSM header, satellite and signal field widths; 1005/1230 encoders. https://github.com/tomojitakasu/RTKLIB/blob/master/src/rtcm3e.c (open-source code)
6. u-blox Support Community, "What is your real experience of sending RTCM messages over LORA?" (Jan 2026) — measured ≈ 700–750 B/s MSM4 from a ZED-F9P base; EBYTE UART module limitations; compression attempts. https://portal.u-blox.com/s/question/0D5Oj00001MIoH3KAL/what-is-your-real-experience-of-sending-rtcm-messages-over-lora (forum — anecdotal)
7. Singapore Land Authority, "SiReNT — Our Services" and Customer Handbook v1.33 — RTK/DGNSS via NTRIP, RTCM 2.3/3.1/3.2 and CMR, subscription and short-term trial (via search summary). https://app.sla.gov.sg/sirent/About/OurServices (government service page)
8. P. J. G. Teunissen, O. Montenbruck (eds.), *Springer Handbook of GNSS*, Springer, 2017 — ch. 23 (carrier-phase integer ambiguity resolution, LAMBDA), ch. 25–26 (PPP, RTK). (textbook; general reference)
9. P. Misra, P. Enge, *Global Positioning System*, 2nd ed., 2006 — ch. 7 (differential GNSS, carrier-phase positioning). (textbook; general reference)
10. Space Bar avionics knowledge base (user's notes) — RTK corrections via a separate transparent LoRa bridge into the ZED-F9P; L1-only flown antenna. (internal)
