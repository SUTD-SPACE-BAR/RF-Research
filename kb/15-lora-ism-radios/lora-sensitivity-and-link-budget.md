---
title: LoRa sensitivity, link budget and realistic range
domain: 15-lora-ism-radios
slug: lora-sensitivity-and-link-budget
tags: [lora, sensitivity, link-budget, noise-figure, snr, range, eirp, erp, e22-400t33d, e220-900t30d, singapore, range-records]
prerequisites:
  - lora-phy-css-math.md
  - ../07-noise-linearity/thermal-noise-and-noise-temperature.md
  - ../07-noise-linearity/noise-figure-and-friis.md
  - ../09-propagation-link-budget/friis-free-space-path-loss.md
related:
  - ../09-propagation-link-budget/link-budget-methodology.md
  - ../09-propagation-link-budget/two-ray-ground-reflection.md
  - ../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md
  - ../07-noise-linearity/sensitivity-and-mds.md
  - ../08-antennas/antennas-on-rockets.md
  - lora-impairments-doppler-drift-timing.md
  - lora-modules-ebyte-rfm-heltec.md
  - rocket-telemetry-radio-design.md
  - ground-station-design.md
  - ism-band-plans-duty-cycle.md
level: mixed
confidence: high
last_updated: 2026-10-14
---

# LoRa sensitivity, link budget and realistic range

## Questions this page answers
- How do I calculate the sensitivity of a LoRa receiver for a given SF and bandwidth?
- Why does LoRa work below the noise floor, and what SNR does each SF need?
- What noise figure do Semtech chips really have?
- Is EBYTE's "−147 dBm sensitivity at 2.4 kbps" believable?
- What range can my E22-400T33D (433 MHz, 2 W) or E220-900T30D (900 MHz, 1 W) actually reach from a rocket?
- If LoRa's link budget is 160+ dB, why do rockets lose telemetry after landing?
- Would a Singapore-legal 10 mW (433 MHz) or 100 mW (920 MHz) radio still reach 10–30 km?
- Are the "LoRa world records" (700–1300 km) real, and what do they mean for me?
- How much does urban noise and interference in Singapore cost me?

## TL;DR
- **Sensitivity** $S = -174 + 10\log_{10}BW + NF + \text{SNR}_{req}$ dBm, with Semtech's $\text{SNR}_{req}$ = −7.5 dB (SF7) … −20 dB (SF12) in 2.5 dB steps [1][2]. With NF ≈ 6 dB this reproduces the SX1262 table (−124 dBm SF7/125, −137 dBm SF12/125) within 0 to 2 dB (`tools/verify/lora_link_budget.py`).
- Implied chip NF: SX1262 5.8–8.0 dB (mean 6.7); SX1276 433 MHz port 4–10 dB (mean 5.9); SX1276 868/915 MHz port 5.3–11 dB (mean 7.4). Worst at wide BW / low SF.
- **EBYTE's −147/−148 dBm "at 2.4 kbps" is not physical**: at 2.4 kb/s LoRa needs $E_b/N_0\approx6$ dB, giving ≈ −128 dBm; −147 dBm would need $E_b/N_0 = -12.8$ dB, below the Shannon limit (−1.6 dB). It is the SX1268's best setting (SF12 at 7.8 kHz, ~15 b/s). For the **E220 (LLCC68)** it is impossible at any setting: the LLCC68 has no SF10–12 at 125 kHz and bottoms out near −129 dBm (SF9/125) [3][4].
- Rocket in flight = line of sight: E22 at SF9/125 (MAPL ≈ 171 dB) has free-space range of thousands of km even after 13 dB of polarisation + fade margin. **Range is limited by geometry** (antenna nulls, landed-rocket ground loss, terrain, horizon) and interference, not by transmit power.
- Landed rocket (antenna 0.2 m above ground, station 2 m): two-ray loss ≈ 40 log d − 20 log(h_t h_r) gives only ≈ 5.6 km for the same E22 link (≈ 9.8 km with a 6 m mast) — for this assumption set (0.2 m/2 m, SF9 with 13 dB margin); the KB's canonical set in [09 Example E](../09-propagation-link-budget/link-budget-methodology.md#example-e--landed-rocket-the-case-that-actually-limits-recovery) (5 m mast, 11 dBic, no margin) gives ≈ 11.5 km. Real terrain is worse — Featherweight reports routinely losing LoRa after landing [9].
- Singapore SRD limits are **10 mW e.r.p. at 433.05–434.79 MHz (≤ 10 % duty)**, **500 mW e.r.p. at 866–869 MHz (no duty stated)** and **100 mW e.r.p. (1 % duty) for LoRa/LPWAN end devices at 917–925 MHz** [5]; the 2 W E22 and 1 W E220 exceed the 433/917–925 MHz limits by ≈ 22.5 dB and ≈ 9.5 dB, so **Examples 1–2 are the *licensed* case** (amateur licence + IMDA consent at 430–440 MHz, or a temporary/experimental permit) and Example 3 the *licence-exempt* case. Even the legal powers give > 100 km free-space LOS range at SF9 with a Yagi; the binding legal constraint is **update rate** (1 % duty at 923 MHz = one 32-byte SF7/125 frame per 7.2 s), not range — see [band plans](ism-band-plans-duty-cycle.md) and [19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md).
- Records: 832 km (balloon, 25 mW, 2020) and 1336 km (sea level, 2023) LoRaWAN single-packet receptions [8]; Meshtastic 331 km mountain-to-mountain [10]; Featherweight tracker 44.5 km slant range to a 41.8 km-apogee rocket with stub antennas [9]. They show what LOS allows, not what a typical ground link gives.

## Intuition (no math)
A receiver is a listener in a noisy room. The room noise grows with how wide a band you listen to (thermal noise, kTB) and with how noisy your own ear is (noise figure). A normal radio needs the voice to be louder than the noise. LoRa is special: it spends time (long chirps) to collect energy, so it can pick a voice out even when it is 20 dB *quieter* than the noise in the channel — but the price is a very low data rate. Every doubling of symbol length (+1 SF) lets you hear a voice about 2.5 dB quieter, which in open air means about 33 % more distance.

A **link budget** is bookkeeping: start with the transmit power, add antenna gains, subtract every loss (cable, path, polarisation, body shadowing, a safety margin), and compare with the sensitivity. In free space the path loss grows only 6 dB per doubling of distance, so a 170 dB budget reaches absurd distances; that is why balloon records are hundreds of km. Near the ground, the direct wave and the ground-reflected wave cancel and the loss grows 12 dB per doubling — a rocket lying in grass is almost invisible a few km away.

## The math

### Level 1 — the sensitivity equation
Thermal noise in bandwidth $B$ at 290 K is $kT_0B$, i.e. $-174$ dBm/Hz $+10\log_{10}B$ (see [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md)). The receiver adds its noise figure $NF$. The minimum received power for the target packet error rate is
$$S\,[\text{dBm}] = -174 + 10\log_{10}BW + NF + \text{SNR}_{req}(SF).$$
For LoRa the noise bandwidth is the LoRa BW (Semtech defines SNR over the full channel bandwidth, "double-sideband" [2]). Semtech's typical demodulator SNR [1][2]:

| SF | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|
| SNR$_{req}$ (dB) | −2.5 | −5 | −7.5 | −10 | −12.5 | −15 | −17.5 | −20 |

Example: SF12, BW 125 kHz, NF 6 dB: $S = -174 + 51.0 + 6 - 20 = -137$ dBm — exactly the SX1262 datasheet value [2].

**Link budget** (all in dB/dBm; see [link-budget methodology](../09-propagation-link-budget/link-budget-methodology.md)):
$$P_{rx} = P_{tx} - L_{tx} + G_{tx} - L_{path} - L_{pol} - L_{misc} + G_{rx} - L_{rx},\qquad \text{margin} = P_{rx} - S .$$
Maximum allowable path loss $MAPL = P_{tx} - L_{tx} + G_{tx} + G_{rx} - L_{rx} - S$. Free-space loss $L_{fs} = 20\log_{10}(4\pi d f/c)$ (433 MHz: 85.2 dB at 1 km; 923 MHz: 91.8 dB at 1 km; +6 dB per doubling).

### Level 2 — where the SNR table comes from, and implied noise figures
LoRa at critical sampling is non-coherent orthogonal $M$-ary signalling with $M=2^{SF}$ ([PHY page](lora-phy-css-math.md)). The ideal receiver's SER is an exact integral; converting to packet error rate for Semtech's test packet (64-byte payload, CR4/5, explicit header, CRC; PER 1 % [2 §3.5]) with $\text{PER} = 1-(1-\text{SER})^{N_{sym}}$ (CR4/5 cannot correct, so any symbol error kills the packet) gives, from `tools/verify/lora_css_sim.py`:

| SF | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|
| Ideal SNR for 1 % PER (dB) | −1.2 | −4.0 | −6.9 | −9.7 | −12.6 | −15.4 | −18.6 | −21.4 |
| Semtech table (dB) | −2.5 | −5.0 | −7.5 | −10.0 | −12.5 | −15.0 | −17.5 | −20.0 |
| $E_b/N_0$ ideal (dB) | 7.9 | 7.2 | 6.7 | 6.3 | 6.0 | 5.7 | 6.0 | 5.7 |

The ideal step is 2.8 dB per SF; Semtech's rule is 2.5 dB; the measured SX1262 sensitivities drop 13 dB from SF7 to SF12 (2.6 dB/step). Bor et al. measured on SX127x steps of 0–4 dB (average 2 dB) per SF [11]. At SF10–12 real chips are 0.4–1.4 dB worse than ideal (implementation loss in synchronisation and tracking); at SF5–8 the Semtech table is 0.3–1.3 dB *better* than our ideal uncoded model, so treat the low-SF table entries as optimistic by up to ~1 dB.

Inverting the sensitivity equation with Semtech's SNR table gives the **noise figure implied by each datasheet entry** (`lora_link_budget.py` §1):

| Chip / port | Mean NF | Range | Best | Worst |
|---|---|---|---|---|
| SX1261/2, Rx boosted [2] | 6.7 dB | 5.8–8.0 | SF12/10.4 kHz | SF12/500 kHz |
| SX1276 LF port (band 3, 433 MHz) [1] | 5.9 dB | 4.0–10.0 | SF10/250 | SF6/500 |
| SX1276 HF port (band 1, 868/915) [1] | 7.4 dB | 5.3–11.0 | SF11/10.4 | SF6/500 |

The 500 kHz entries are consistently worse (the SX126x uses a single zero-IF conversion at 500 kHz [2]; an SX1262 500-kHz TX erratum also degrades *other* receivers — see [chip family](semtech-chip-family.md)).

### Level 3 — system noise, external noise and modules with LNAs
The sensitivity equation assumes the antenna delivers 290 K of noise. The real **system noise temperature** is $T_{sys} = T_a + T_e$ (antenna temperature plus receiver equivalent temperature $T_e = T_0(10^{NF/10}-1)$; with NF 6 dB, $T_e\approx 865$ K). ITU-R P.372-13 gives measured median man-made noise at 425 MHz of $F_a$ = 6 dB (city), 4 dB (residential), 3 dB (rural) for an omni antenna near the ground, i.e. $T_a\approx$ 1150/730/580 K [12, via the 07 page]. For a city site with a bare 6 dB-NF module: $T_{sys} = 1150 + 865 = 2015$ K vs the datasheet's 1155 K → **2.4 dB desense**. With a masthead LNA ($T_e\approx 43$ K) the external noise dominates completely, so an LNA cannot recover what the environment takes; a directional antenna pointing above the horizon (seeing mostly 20–170 K sky) can. On top of this Gaussian floor, **in-band interference** — 433 MHz car keys and remotes, 920–925 MHz LoRaWAN, RFID readers — raises the effective noise; LoRa's processing gain helps against narrowband and impulsive interference but not against another strong LoRa signal on the same SF ([impairments](lora-impairments-doppler-drift-timing.md)).

**Modules with PA + LNA** (E22-400T33D, E220-900T30D, E22-xxxM30S) put an LNA (and RF switch, filter) ahead of the chip. By Friis, an LNA with NF$_1$ and gain $G_1$ in front of a 6 dB chip gives $F = F_1 + (F_{chip}-1)/G_1$; with 1.5 dB of switch/filter loss, a 1 dB LNA and 15 dB gain, NF$_{sys}$ ≈ 3.0 dB — up to ~3 dB better sensitivity than the bare chip. EBYTE does not publish the NF or the chain, so this is an estimate (see [noise figure & Friis](../07-noise-linearity/noise-figure-and-friis.md)).

**What the EBYTE numbers mean.** For any digital modulation $S = -174 + NF + 10\log_{10}R_b + E_b/N_0$. With LoRa's best case $E_b/N_0 \approx 5.7$ dB and NF 6 dB, 2.4 kb/s gives −128.5 dBm; the E22 "−147 dBm at 2.4 kbps" would need $E_b/N_0 = -12.8$ dB, which violates Shannon ($-1.59$ dB for any code at vanishing rate). The SX1268 can reach −148/−149 dBm only at SF12 with 7.8–10.4 kHz BW (15–40 b/s) [2]. The LLCC68 inside the E220 is limited to SF≤9 at 125 kHz, SF≤10 at 250 kHz, SF≤11 at 500 kHz, and its datasheet best is −129 dBm at SF9/125 kHz (1.76 kb/s) [4] — **the E220's −147/−148 dBm claim is off by ~18 dB** [3]. The same issue was flagged independently in the 07/09 domain research (W1-A5 log, contradiction C1).

## Design equations & rules of thumb
| Equation / rule | Validity | Typical |
|---|---|---|
| $S = -174 + 10\log BW + NF + \text{SNR}_{req}$ | chip sensitivity | SX1262 SF12/125: −137 dBm |
| NF ≈ 6 dB (bare SX126x/SX127x) | 125–250 kHz | 7–8 dB at 500 kHz |
| +1 SF ≈ +2.5 dB (2.6 measured, 2.8 ideal) | fixed BW | range ×1.33 free space |
| ×2 BW ≈ −3 dB | fixed SF | range ×0.71 |
| $L_{fs} = 32.45 + 20\log f_{MHz} + 20\log d_{km}$ | far field, free space | 433 MHz 10 km: 105.2 dB |
| Two-ray: $L \approx 40\log d - 20\log(h_th_r)$ | $d \gg 4h_th_r/\lambda$ | 5 km, 0.2 m/2 m: 156 dB |
| Radio horizon $d \approx 4.12(\sqrt{h_t}+\sqrt{h_r})$ km | 4/3-earth | 3 km altitude: 231 km |
| Margin to keep | rocket LOS | ≥ 10 dB fade + 3 dB polarisation + pattern nulls (10–20 dB) |
| External noise, city 425 MHz | omni near ground | +2.4 dB desense for NF 6 dB |

## Worked examples
All numbers from `python3 tools/verify/lora_link_budget.py` (assumptions in its `ASSUMPTIONS` dict: rocket antenna 0 dBi, rocket cable 0.5 dB, ground Yagi 10 dBi at 433 / 12 dBi at 923 MHz, ground cable 1 dB, NF 6 dB, polarisation 3 dB, fade 10 dB, pattern null 10 dB).

**1. Primary FC: E22-400T33D at 433.125 MHz, 33 dBm — *licensed case*.** In Singapore this power is legal only under an amateur licence (≤ 10 W ERP, IMDA consent), a temporary permit or an experimental licence; the licence-exempt equivalent is Example 3. EIRP = 33 − 0.5 + 0 = 32.5 dBm.

| Setting | $R_b$ | Sensitivity | MAPL | Free-space range after pol+fade | … and in a 10 dB null |
|---|---|---|---|---|---|
| SF7/125 | 5469 b/s | −124.5 dBm | 166.0 dB | 2470 km | 780 km |
| SF9/125 | 1758 b/s | −129.5 dBm | 171.0 dB | 4390 km | 1390 km |
| SF12/125 | 244 b/s | −137.0 dBm | 178.5 dB | 10 400 km | 3290 km |
| SF7/500 | 21 875 b/s | −118.5 dBm | 160.0 dB | 1230 km | 390 km |

Interpretation: a rocket at 30 km slant range needs only $L_{fs}$ = 114.7 dB. Even SF7 at 500 kHz (22 kb/s!) has ≈ 45 dB spare after margins and a null. For flight telemetry the right move is **lower SF / wider BW for higher update rate and better Doppler robustness**, not SF12.

**2. Secondary FC: E220-900T30D at 923 MHz, 30 dBm — *not licence-exempt in Singapore* (needs a temporary permit/experimental licence; 100 mW e.r.p. + 1 % is the exempt limit at 917–925 MHz).** EIRP 29.5 dBm, 12 dBi Yagi. LLCC68 limits: best is SF9/125 (MAPL 170 dB), SF10/250 (169.5 dB) or SF11/500 (169 dB) — all ≈ −129 dBm class. SF7/500 gives 159 dB MAPL, i.e. 516 km after pol+fade in free space. At 923 MHz the path loss is 6.6 dB higher than at 433 MHz for the same antenna *gains*, which the higher-gain Yagi of the same boom length partly recovers.

**3. Singapore-legal powers — licence-exempt vs licensed, side by side.** 10 mW e.r.p. at 433 MHz = 12.15 dBm EIRP: SF9/125 still has MAPL 150.7 dB → 422 km free space after 13 dB margin, 133 km in a null. 100 mW e.r.p. at 923 MHz (22.15 dBm EIRP) at SF9/125: MAPL 162.7 dB. So *for the in-flight LOS phase a legal-power LoRa link with a tracking Yagi closes comfortably at SF7–SF9*. From `tools/verify/fix_legal_vs_licensed_link_budgets.py` (same assumptions; margin = SF9/125 margin at 30 km after 23 dB of polarisation + fade + null):

| Case | Legal basis in SG | EIRP | MAPL SF9/125 | Margin @ 30 km | Max rate, 32 B SF7/125 |
|---|---|---|---|---|---|
| 433 MHz, 10 mW e.r.p. | licence-exempt (26a, ≤ 10 %) | 12.2 dBm | 150.7 dB | **+13.0 dB** | 1.4 Hz |
| 433 MHz, E22 at 33 dBm | **amateur licence** + IMDA consent (≤ 10 W ERP) | 32.5 dBm | 171.0 dB | +33.3 dB | 13.9 Hz (no SRD duty) |
| 868 MHz, 500 mW e.r.p. (limit) | licence-exempt (29, no duty stated) | 29.2 dBm | 169.7 dB | +25.9 dB | 13.9 Hz |
| 868 MHz, E220 CH 18 at 24 dBm | licence-exempt (29) | 23.5 dBm | 164.0 dB | +20.3 dB | 13.9 Hz |
| 923 MHz, 100 mW e.r.p. | licence-exempt (30c, ≤ 1 %) | 22.2 dBm | 162.7 dB | +18.4 dB | **0.14 Hz** |
| 923 MHz, E220 at 30 dBm | **not exempt** — temporary permit / experimental licence | 29.5 dBm | 170.0 dB | +25.7 dB | 13.9 Hz |

The licence buys ≈ 20 dB of margin at 433 MHz — valuable after landing (Example 4), irrelevant for LOS flight. **The best licence-exempt option is 866–869 MHz**: 7 dB more EIRP than 917–925 MHz and no duty-cycle cap (but the band is under IMDA's refarm review). Licence routes and caveats: [19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md); duty-cycle arithmetic: [band plans](ism-band-plans-duty-cycle.md).

**4. Why the link dies after landing.** Rocket antenna 0.2 m above flat ground, station antenna 2 m: the two-ray breakpoint $4h_th_r/\lambda$ is only 2.3 m at 433 MHz, so beyond a few metres $L\approx 40\log_{10}d - 20\log_{10}(0.4)$: 128 dB at 1 km, 156 dB at 5 km, 168 dB at 10 km. With the E22 at SF9/125 and 13 dB margin (MAPL 158 dB — the *licensed* 33 dBm case), **range ≈ 5.6 km** (0.2 m/2 m, SF9 with 13 dB margin; see [09 Example E](../09-propagation-link-budget/link-budget-methodology.md#example-e--landed-rocket-the-case-that-actually-limits-recovery) for the canonical set: 5 m mast, no margin, ≈ 11.5 km); raising the station antenna to 6 m gives ≈ 9.8 km. At the licence-exempt 10 mW e.r.p. the MAPL after margin is 20.35 dB lower (137.7 dB), and since two-ray loss grows 40 dB/decade the range shrinks by $10^{20.35/40}$ ≈ 3.2× to **≈ 1.7 km** (≈ 3.0 km with the 6 m mast) — the one phase where the licence really matters. Any hill, tree line or building takes most of the rest. Mitigations: a high mast or drone/balloon relay, a higher SF *after landing* (the Doppler constraint is gone), repeaters on other rockets (Featherweight's "lost rocket relay" [9]), and logging the last good GNSS fix. See [two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md).

**5. Near-pad overload (licensed 33 dBm case).** 33 dBm EIRP into a 10 dBi Yagi 1 m away: $L_{fs}$ = 25.2 dB → +17 dBm at the receiver, above EBYTE's 10 dBm "blocking power" rating ("less chance of burning when used at close range") [3]. At 10 m: −2.7 dBm; at 100 m: −22.7 dBm. Keep ground receivers tens of metres from the pad, point Yagis away during pad checks, or add a switchable attenuator ([ground station](ground-station-design.md)).

**6. Sanity-checking EBYTE's "16 km tested range".** The E22-400T33D datasheet quotes 16 km with 5 dBi antennas at 2.5 m height at 2.4 kb/s [3]. With an *honest* 2.4 kb/s sensitivity of −128.5 dBm the MAPL is 33 + 5 + 5 + 128.5 = 171.5 dB. Two-ray with $h_t=h_r=2.5$ m: $d = 10^{(MAPL + 20\log_{10}6.25)/40}$ = 48466 km with zero margin, 15326 km with 20 dB of excess loss (terrain, clutter, Fresnel-zone obstruction, fading). So the 16 km claim is consistent with physics *without* needing the −147 dBm figure — ground links are height-limited, and doubling both antenna heights would roughly double the range (each height enters as 20 log h).

## Practical notes
- **Measure your own noise floor.** EBYTE E22/E220 can report ambient-channel RSSI (register 0x00 via `C0 C1 C2 C3`, dBm = −(256 − value)) and per-packet RSSI [3]; SX127x packet RSSI is $-157 + \text{Rssi}$ (HF port) or $-164 + \text{Rssi}$ (LF port), adding SNR/4 when SNR < 0 [1]. Log these on the pad and during flight; an elevated floor at your launch site is invisible otherwise.
- **SNR report is the better margin indicator** at low signal levels: LoRa RSSI saturates near the noise floor, while packet SNR goes negative down to the demodulation limit.
- **Supply voltage matters**: SX1262 loses 2/3/6 dB of output at 2.7/2.4/1.8 V [2]; EBYTE says ≥3.3 V (E22) and ≥5.0 V (E220-T30D) to guarantee rated power [3].
- **Antenna gains on a rocket** are not 0 dBi everywhere: an axial dipole seen from 10° off-axis is ~16 dB down (W1-A6, [antennas on rockets](../08-antennas/antennas-on-rockets.md)); carbon-fibre airframes block RF entirely.
- **Polarisation**: a linearly polarised rocket antenna that rolls produces cos² fades against a linear ground antenna (deep nulls at 90°); a circular ground antenna costs a steady 3 dB but removes the nulls ([polarisation mismatch](../09-propagation-link-budget/polarization-mismatch-loss.md)).
- **Comparison with other near-limit modes:** LoRa SF12 vs FT8 at the same bit rate is worked in [10 weak-signal modes § Example 2](../10-comms-modulation/weak-signal-digital-modes.md#example-2--ft8-versus-lora-sf12-at-the-same-bit-rate); fading-channel capacity and SF adaptation are in [10 BER § Level 3c](../10-comms-modulation/ber-ebn0-and-shannon.md#level-3c--capacity-of-fading-channels-ergodic-outage-and-adaptive-modulation-w5-s8).

## Common mistakes & misconceptions
- **"LoRa range is 15 km."** Range is set by geometry. Ground-to-ground with 2 m masts: ~5–20 km. Air-to-ground LOS: hundreds of km possible. A single "range" figure without heights and margins is meaningless.
- **"SF12 always gives more range."** It gives ~12.5 dB more budget than SF7, but in flight you rarely need it, and it is the most fragile to Doppler rate, drift and collisions ([impairments](lora-impairments-doppler-drift-timing.md)); on the E220 (LLCC68) it doesn't exist.
- **Trusting module sensitivity claims.** EBYTE's −147/−148 dBm "at 2.4 kbps" is ~18–19 dB optimistic (see Level 3).
- **"2 W is 3 dB more than 1 W, so it doubles range."** +3 dB = ×1.41 range in free space, ×1.19 in the two-ray region.
- **dBm vs mW / ERP vs EIRP vs conducted.** 33 dBm = 2 W conducted; with a 2.15 dBi dipole that is 35.15 dBm EIRP = 33 dBm e.r.p. Regulators in Singapore/EU specify e.r.p.; FCC specifies conducted power + antenna-gain rule.
- **Adding the processing gain to the link budget twice.** The negative SNR in the sensitivity equation *already contains* the processing gain.
- **Treating "RSSI = −120 dBm" as the signal level near sensitivity.** Below the noise floor the reported RSSI is mostly noise; use packet SNR.
- **Ignoring the environment**: a city site can add ~2–3 dB of man-made noise at 433 MHz, plus interference.
- **Fitting a path-loss exponent to received packets only** (TTN Mapper, Meshtastic range-test maps, a receiver log without the transmitter's log). The packets that failed are missing, so the fit is biased to the lucky fades. In the KB's simulation (true n = 3.5, σ = 8 dB) least squares on the received points gave **n = 1.7** and a median range 2.4× too long; a censored (Tobit) fit that includes the failed attempts recovered n = 3.6 ([tool landscape Example 5](../16-simulation-tools/tool-landscape-overview.md), `tools/verify/sim2_coverage_itm.py`). An exponent below 2 near the ground is a selection-bias symptom. Log every transmission at the transmitter, mark which were heard, and fit the censored model before using n in a budget.
- **Trusting a terrain tool's landed-rocket range.** For an antenna < 1 m above ground, ITM on a real profile gave 10–50 dB less loss than flat-earth two-ray in the KB's run (`rfcalc itm`; [09 two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md#worked-examples)). Budget the landed case with two-ray; use terrain only to find shadows.
- **"Meshtastic showed a node 500–5 000 km away, so that is an RF range record."** Meshtastic gateways can
  *uplink* mesh packets to an MQTT broker over the internet and *downlink* other meshes' packets back onto
  LoRa. A downlinked packet is then heard over your local RF hop — with a real RSSI/SNR from a nearby
  gateway — but carries the distant node's position, so the app computes an impossible "range". The
  firmware marks such packets: `MeshPacket.via_mqtt` ("passed via MQTT somewhere along the path") and
  `NodeInfo.via_mqtt`; `LoRaConfig.ignore_mqtt` drops them [13]. Before quoting a range, check the flag, the
  hop count and the line-of-sight geometry; genuine long single hops need elevated line of sight (the 331 km
  record [10] was mountain-to-mountain) or tropospheric ducting
  ([radio horizon and ducting](../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md)). For your
  own range tests, disable MQTT on both nodes ([beginner ladder rung 7](../20-projects-recipes/beginner-project-ladder.md),
  [choosing antennas](choosing-and-judging-lora-antennas.md); mesh behaviour in [LoRa mesh capacity](lora-mesh-capacity-and-congestion.md)). (Myth flagged by W4-D2, gaps/D2-reddit.md §3a.)

## How to simulate / verify
- `python3 tools/verify/lora_link_budget.py` — implied NF per datasheet entry, model vs SX1262 table, EBYTE-claim check against Shannon, full budgets for E22/E220/SG-legal cases, near-pad received power, landed two-ray range and radio horizon. Edit `ASSUMPTIONS` for your antennas.
- `python3 tools/verify/lora_css_sim.py` — ideal SNR thresholds per SF (Monte-Carlo validated).
- `python3 tools/verify/fix_legal_vs_licensed_link_budgets.py` — the Example 3 side-by-side table (SG licence-exempt vs licensed powers, duty-limited packet rates).
- Field test: fix TX power, step an attenuator (or use the module's power steps 33/30/27/24 dBm) and record PER vs RSSI/SNR at a known distance; the SNR at 1 % PER is your real demodulation limit. Compare with the table above.
- Link-budget cross-checks with the generic 09-domain tools (`tools/verify/prop_link_budget.py`, if present).

## Open questions / gaps
- Real NF of EBYTE E22-400T33D and E220-900T30D receive chains (LNA part, switch loss) is undocumented; measure with a signal generator + attenuator sensitivity test.
- LR1110/LR1120/LR1121 datasheet sensitivity tables were not read (only product pages); LR2021 claims −141.5 dBm at SF12/125 kHz [6], ~4.5 dB better than SX1262 — unverified.
- Modern man-made noise measurements at 433/920 MHz in Singapore do not exist in the KB (P.372 data are from the 1970s).
- Meshtastic record entries are self-reported (no verification method stated); the Meshtastic docs also disagree with themselves on the LongFast coding rate (4/5 on the settings page, 4/8 on the range-test page) [10].

## Sources
1. Semtech, *SX1276/77/78/79 Datasheet* Rev 7 (2020) — RF sensitivity tables per SF/BW for band 1 (HF) and band 3 (LF), SNR table, RSSI formulas (−157/−164 + Rssi, +SNR/4). https://cdn.sparkfun.com/assets/7/7/3/2/2/SX1276_Datasheet.pdf (datasheet)
2. Semtech, *SX1261/2 Datasheet* Rev 1.2 (2019) — Table 3-8 sensitivities (Rx boosted), Table 6-1 SNR, test conditions (PER 1 %, 64 B, CR4/5), TX power drop vs VBAT, 500 kHz zero-IF. https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf (datasheet)
3. EBYTE, *E22-400TXXX Data Sheet* (2022) and *E220-900T30D User Manual* (2020) — sensitivity claims, tested ranges, blocking power, RSSI registers, supply requirements. https://www.cdebyte.com/pdf-down.aspx?id=2179 ; https://www.cdebyte.com/pdf-down.aspx?id=349 (module datasheets — claims contradicted, see text)
4. DreamLNK, *DL-LLCC68-S datasheet* — LLCC68 SF/BW limits, −129 dBm SF9/125. (module datasheet)
5. IMDA, *TS SRD* Issue 1 Rev 3 (**September 2023**; 433/866/917 MHz rows unchanged from the April 2023 printing), Table 1 sub-bands 26a/26b, 29, 30a–d. https://www.imda.gov.sg/-/media/imda/files/regulation-licensing-and-consultations/ict-standards/telecommunication-standards/radio-comms/imdatssrd.pdf (regulator standard); licence routes and the Exemption-Notification 500 mW conflict at 917–925 MHz in [19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md).
6. Semtech, LR2021 product page (accessed 2026-09-27) — −141.5 dBm SF12/125 claim. https://www.semtech.com/products/wireless-rf/lora-plus/lr2021 (vendor web)
7. W1-A5 (this KB), `research-logs/W1-A5-noise-propagation.md` contradiction C1 — independent check of the EBYTE sensitivity claim. (internal)
8. The Things Network: "Ground breaking world record! LoRaWAN packet received at 702 km"; "LoRa World Record Broken: 832 km/517 mi using 25 mW" (T. Telkamp, 16 Apr 2020); "New LoRa world record: 1336 km / 830 mi" (2023, sea level). https://www.thethingsnetwork.org/article/ (community news — single-packet events, not peer-reviewed)
9. Featherweight Altimeters, *GPS Tracker User's Manual* (20 Feb 2025) — 915 MHz LoRa; >137 000 ft altitude and 145 900 ft range with stub antennas (Sept 2017); signal commonly lost after landing; Yagi +6–8 dB. (manufacturer manual — anecdotal)
10. Meshtastic docs, "Range Tests" and "Radio Settings" (accessed 2026-09-27) — 331 km ground record (RAK4631, SF12/62.5 kHz, 868 MHz), 254 km, 206 km air. https://meshtastic.org/docs/overview/range-tests/ (project docs — self-reported)
11. M. Bor, U. Roedig, T. Voigt, J. Alonso, "Do LoRa Low-Power Wide-Area Networks Scale?", ACM MSWiM 2016 — measured sensitivity steps per SF. (peer-reviewed)
12. ITU-R P.372-13 (2016) *Radio noise*, Table 3 (425 MHz measured man-made noise) — as summarised in [thermal noise](../07-noise-linearity/thermal-noise-and-noise-temperature.md). (standard)
13. Meshtastic protobufs, `meshtastic/mesh.proto` (`MeshPacket.via_mqtt`, `NodeInfo.via_mqtt`) and `meshtastic/config.proto` (`LoRaConfig.ignore_mqtt`, `config_ok_to_mqtt`), https://github.com/meshtastic/protobufs (read 2026-10-02); Meshtastic docs, "MQTT" (gateways uplink/downlink raw mesh packets to a broker), https://meshtastic.org/docs/software/integrations/mqtt/ (project source + docs)
