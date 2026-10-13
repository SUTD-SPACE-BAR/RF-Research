---
title: Link budget methodology (with the 433 MHz and 915 MHz rocket downlinks)
domain: 09-propagation-link-budget
slug: link-budget-methodology
tags: [link-budget, EIRP, G/T, C/N0, Eb/N0, fade-margin, LoRa, rocket-telemetry, E22-400T33D, E220-900T30D, ground-station, plume-attenuation]
prerequisites: [friis-free-space-path-loss.md, ../07-noise-linearity/sensitivity-and-mds.md, ../07-noise-linearity/noise-figure-and-friis.md]
related: [link-margin-availability.md, polarization-mismatch-loss.md, two-ray-ground-reflection.md, fresnel-zones-los-radio-horizon.md, multipath-fading-doppler.md, ../07-noise-linearity/receiver-cascade-analysis.md, ../15-lora-ism-radios/lora-sensitivity-and-link-budget.md, ../15-lora-ism-radios/rocket-telemetry-radio-design.md, ../20-projects-recipes/lora-rocket-telemetry-link.md, ../08-antennas/antennas-on-rockets.md]
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Link budget methodology (with the 433 MHz and 915 MHz rocket downlinks)

## Questions this page answers
- How do I write a link budget line by line, and what belongs in each line?
- How far will my E22-400T33D (433 MHz, 2 W) downlink reach to a ground Yagi at 30 km?
- How does the 915 MHz 1 W E220-900T30D secondary link compare?
- What is G/T and how does the C/N0 / Eb/N0 form relate to the dBm form?
- How much fade margin should I leave, and for what?
- Why do my "10 000 km" free-space ranges not match reality?
- Does the rocket's exhaust plume block the signal?

## TL;DR
- **Budget = transmitter side (EIRP) − path − receiver side losses + receive gain, compared with a sensitivity built from the receiver's noise.** In dB: $P_r = P_t - L_{ft} + G_t - L_\text{path} - L_\text{pol} - L_\text{point} - L_\text{atm} + G_r - L_{fr}$; margin $M = P_r - S$.
- **433 MHz primary link at 30 km slant range** (33 dBm, 0 dBi on the rocket, 11 dBic crossed Yagi, 3 dB linear→circular, 1 dB pointing): $P_r$ = **−75.8 dBm**; against a physics-based 2.4 kb/s sensitivity of −128 dBm, **margin ≈ 52 dB** (`tools/verify/prop_link_budget.py`, example A).
- **915 MHz secondary link at 30 km** (30 dBm, 12 dBi linear Yagi, 30° polarisation misalignment): **−83.0 dBm, margin ≈ 45 dB** (example B).
- **Licence caveat.** Examples A, B and E use the modules' full power (2 W / 1 W). In Singapore that is **not licence-exempt**: the 433 MHz SRD limit is 10 mW e.r.p. (12.15 dBm EIRP, ≤ 10 % duty) and 917–925 MHz LoRa end devices are limited to 100 mW e.r.p. with ≤ 1 % duty; 2 W at 433 MHz needs an amateur licence (≤ 10 W ERP, IMDA consent) or a permit ([19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md)). At the licence-exempt 433 MHz power, Example A's margin drops by 20.35 dB to **≈ +32 dB** — still ample for LOS flight, but the landed case (Example E) runs out of margin at ≈ 3.5 km at 2.4 kb/s (≈ 6 km at SF12) instead of ≈ 11.5 km / ≈ 19 km. Side-by-side exempt vs licensed budgets: [LoRa link budget Example 3](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md#worked-examples).
- Free-space "maximum ranges" come out at hundreds to thousands of km — the ascent link is **not power-limited**. It is limited by **impairments**: antenna-pattern nulls (rocket seen end-on: −15 dB or worse), polarisation, ground-reflection lobing, plume attenuation at small look angles (tens of dB possible for large solid motors), Doppler-rate limits at high SF, and — above all — **the landed rocket**, where plane-earth + terrain/vegetation losses remove 30–60 dB.
- Use the **C/N0 form** to cross-check: $C/N_0 = \text{EIRP} - L + G/T - k$ ($k$ = −228.6 dBW/K/Hz); for link A, G/T = −19.6 dB/K and $C/N_0$ = 92.7 dB-Hz, identical to $P_r - N_0$.
- **Never use the EBYTE "−147 dBm @ 2.4 kbps"** in a budget; it overstates the margin by 19 dB (see [07-noise-linearity/sensitivity-and-mds](../07-noise-linearity/sensitivity-and-mds.md)).

## Intuition (no math)
A link budget is an accounting sheet for decibels. Start with the power the transmitter produces. Subtract what the cables eat, add what the antenna's focusing gains you in the direction of the receiver. Subtract the spreading loss of the path, and any extra losses (polarisation mismatch, pointing error, atmosphere, obstructions). Add the receive antenna's gain, subtract the receive cable. What arrives is compared with what the receiver needs — its sensitivity, which comes from its own noise and the modulation's SNR requirement. The difference is the **margin**: the amount of bad luck the link can absorb.

The trap is that the average case is easy and the rare cases kill links. A rocket link at 30 km has huge margin *on average*, but at the moment the rocket points its tail at the ground station, is spinning its antenna null past you, flies behind its own exhaust flame, or lands behind a hill, the margin can vanish. So a good budget has two parts: the **nominal** line-by-line calculation, and an **impairment allocation** listing each fade mechanism and how much it can cost.

## The math

### Level 1 — the template
| # | Line item | Symbol | Unit | Notes |
|---|---|---|---|---|
| 1 | Transmitter output power | $P_t$ | dBm | at the module's RF pin (datasheet ± tolerance, supply-dependent) |
| 2 | Tx feeder + connector loss | $L_{ft}$ | dB | cable (dB/m × m), each connector ~0.1–0.2 dB at UHF |
| 3 | Tx antenna gain toward Rx | $G_t$ | dBi | pattern value in that direction, not peak |
| = | **EIRP** | | dBm | $P_t - L_{ft} + G_t$ |
| 4 | Free-space path loss | $L_\text{FS}$ | dB | $32.45 + 20\log f_\text{MHz} + 20\log d_\text{km}$ |
| 5 | Excess path loss | $L_\text{ex}$ | dB | ground reflection/plane earth, diffraction, vegetation, buildings |
| 6 | Atmospheric/rain | $L_\text{atm}$ | dB | negligible at UHF ([atmospheric-rain-attenuation](atmospheric-rain-attenuation.md)) |
| 7 | Polarisation mismatch | $L_\text{pol}$ | dB | 3 dB linear↔circular; $-20\log\cos\Delta\tau$ linear↔linear |
| 8 | Pointing loss | $L_\text{point}$ | dB | Rx (and Tx) off-boresight |
| 9 | Rx antenna gain | $G_r$ | dBi | |
| 10 | Rx feeder loss (before the first LNA) | $L_{fr}$ | dB | anything after a good LNA is in the NF instead |
| = | **Received power** | $P_r$ | dBm | |
| 11 | Receiver sensitivity at the same reference point | $S$ | dBm | $10\log(k(T_a+T_e)B) + 30 + \text{SNR}_\text{min}$ |
| = | **Link margin** | $M$ | dB | $P_r - S$ |
| 12 | Required fade margin | $M_\text{req}$ | dB | from the availability target ([link-margin-availability](link-margin-availability.md)) |

**Equivalent forms.** With $N_0 = kT_\text{sys}$: $C/N_0 = P_r - 10\log_{10}(kT_\text{sys})$ (dB-Hz); $E_b/N_0 = C/N_0 - 10\log_{10}R_b$; $\text{SNR} = C/N_0 - 10\log_{10}B$. The receive side is summarised by **G/T** $= G_r - L_{fr} - 10\log_{10}T_\text{sys}$ (dB/K), with $T_\text{sys}$ referred to the same point as $G_r - L_{fr}$:
$$C/N_0 = \text{EIRP} - L_\text{path} - L_\text{misc} + G/T - 10\log_{10}k,\qquad 10\log_{10}k = -228.6\ \text{dBW/K/Hz}.$$

### Level 2 — the receive-side noise reference
The sensitivity must be referred to the **same point** as $P_r$. If $P_r$ is at the receiver input (after the feeder), then $T_\text{sys} = T_a/L_{fr} + T_p(1 - 1/L_{fr}) + T_e$ (antenna temperature seen through the feeder, plus the receiver's $T_e$). The datasheet sensitivity assumes $T_a = T_0$ = 290 K at the chip pin; a sky-pointing antenna is often colder (better), a city site hotter (worse) — derivation in [07-noise-linearity/thermal-noise-and-noise-temperature](../07-noise-linearity/thermal-noise-and-noise-temperature.md). For link A, $T_a$ = 150 K through 0.45 dB of LMR-400 gives 164 K at the module; with $T_e$ = 865 K (NF 6 dB), $T_\text{sys}$ = 1028 K and the 125 kHz floor is −117.5 dBm.

### Level 3 — what the nominal budget leaves out
- **Pattern and attitude** (the largest effect for rockets): an axial dipole's gain toward the ground station is $\approx$ 2.15 dBi + $10\log_{10}\sin^2\psi$, where $\psi$ is the angle between the rocket axis and the line of sight. A ground station 0.5 km from the pad watching a vertical ascent to 3 km sees $\psi$ ≈ 9.5°: **−15.7 dB** (`prop_polarization.py` §3). Put the ground station several km to the side of the flight path, or use an antenna that fills the aft direction (e.g. a wrap-around or quadrifilar/turnstile arrangement — [08-antennas/antennas-on-rockets](../08-antennas/antennas-on-rockets.md)).
- **Plume attenuation.** A rocket's exhaust contains free electrons (especially from aluminised solid propellant with alkali impurities); when the line of sight passes through or close to the plume (small "look angle" from the tail), the plasma absorbs, refracts and diffracts the signal. For a large solid launcher stage (M-V second stage at 85 km), in-flight 300 MHz data and FEM modelling showed ~20–30 dB attenuation at the smallest look angles, falling below ~5 dB beyond the first diffraction minimum at $\tau_\text{min} \approx 21.0 - 19.0\log_{10}f_\text{GHz}$ degrees (≈ 28° at 433 MHz, 22° at 915 MHz) [5]. Student-scale motors are much smaller and the effect is unquantified here; treat a 5–15 dB allocation for the tail-on geometry as a placeholder and test (static-fire through-plume measurement is feasible with two SDRs).
- **Ground reflection at the ground station** produces elevation lobing with nulls at $\sin\theta_n = n\lambda/2h$ (h = antenna height) — slow fades lasting seconds as the rocket climbs ([two-ray-ground-reflection](two-ray-ground-reflection.md)).
- **Doppler rate** during boost can exceed the LoRa demodulator's drift tolerance at high SF regardless of power ([multipath-fading-doppler](multipath-fading-doppler.md)).
- **Horizon.** Free-space "maximum range" is meaningless beyond the radio horizon $4.12(\sqrt{h_1} + \sqrt{h_2})$ km (h in m): 233 km for a rocket at 3 km and a 3 m mast; 721 km at 30 km altitude ([fresnel-zones-los-radio-horizon](fresnel-zones-los-radio-horizon.md)).
- **Landing.** Once the rocket is on the ground the path is a ground-level link: use plane-earth/two-ray plus diffraction and vegetation, not FSPL (Example E).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| EIRP = $P_t - L_{ft} + G_t$ | | E22 + 0.5 dB + 0 dBi: 32.5 dBm |
| $M = P_r - S$ | any | ascent at 30 km: ~45–52 dB nominal |
| $d_\text{max} = d\cdot10^{(M - M_\text{req})/20}$ | free space only | limited in practice by horizon/impairments |
| $d_\text{max}\propto 10^{\Delta M/40}$ | plane-earth regime (landed) | +6 dB margin → ×1.41 range |
| G/T $= G_r - L_{fr} - 10\log T_\text{sys}$ | | 11 dBi Yagi + NF 6 dB module: −19.6 dB/K |
| $C/N_0 = \text{EIRP} - L + G/T + 228.6$ (dBW units) | | link A: 92.7 dB-Hz |
| $E_b/N_0 = C/N_0 - 10\log R_b$ | | 2.4 kb/s: 58.9 dB available vs ~6 dB needed |
| linear↔circular 3 dB; linear↔linear $-20\log\cos\Delta\tau$ | | 30°: 1.25 dB; 60°: 6 dB; 85°: 21 dB |

## Worked examples
All numbers printed by `python3 tools/verify/prop_link_budget.py`.

### Example A — 433 MHz E22-400T33D downlink, 30 km slant range, crossed-Yagi ground station
*Licensed case*: 33 dBm at 433 MHz is legal in Singapore only under an amateur licence or permit (licence-exempt limit 10 mW e.r.p.; see the caveat in the TL;DR).
| Line | Value | Note |
|---|---|---|
| Tx power (E22-400T33D) | +33.0 dBm | datasheet 33 ± 0.5 dBm (needs ≥ 3.3 V supply at full current) |
| Tx feeder + connectors | −0.5 dB | ~30 cm RG-316 + 2 SMA |
| Rocket antenna gain toward GS | 0.0 dBi | dipole-like; 2.15 dBi broadside; nulls handled as impairments |
| **EIRP** | **32.5 dBm** | |
| Free-space path loss (433.125 MHz, 30 km) | −114.7 dB | |
| Atmospheric gases | −0.1 dB | P.676-11: 0.0025 dB/km at sea level |
| Polarisation (linear → circular) | −3.0 dB | fixed, independent of rocket roll/tilt |
| Pointing loss | −1.0 dB | tracking within ~⅓ beamwidth |
| Ground antenna gain (crossed Yagi, RHCP) | +11.0 dBic | assumed 2 × 7-element |
| Rx feeder (5 m LMR-400) | −0.45 dB | ~9 dB/100 m |
| **Received power** | **−75.8 dBm** | |
| Noise ($T_a$ 164 K at module, NF 6 dB, 125 kHz) | −117.5 dBm | SNR 41.7 dB |
| Sensitivity at ~2.4 kb/s (physics-based, SNR −10 dB) | −127.5 to −128 dBm | not the EBYTE −147 dBm |
| **Margin** | **≈ +52 dB** | |

Free-space distance at which margin falls to 20 dB (2.4 kb/s): ≈ 1 200 km — far beyond the 233 km horizon for a 3 km-high rocket. At SF12/BW125 (−137 dBm) the free-space figure is 3 500 km; with the EBYTE claim it would be 11 000 km (meaningless). Range table vs LoRa setting at 20 dB margin (free space, km):

| BW | SF7 | SF8 | SF9 | SF10 | SF11 | SF12 |
|---|---|---|---|---|---|---|
| 500 kHz | 410 | 547 | 729 | 972 | 1296 | 1729 |
| 250 kHz | 580 | 773 | 1031 | 1375 | 1833 | 2445 |
| 125 kHz | 820 | 1093 | 1458 | 1944 | 2593 | 3458 |
| 62.5 kHz | 1160 | 1546 | 2062 | 2750 | 3667 | 4890 |

**Impairment allocation** (illustrative, not additive worst cases in practice): antenna null/body shadowing 15 dB; ground-reflection lobing 6 dB; plume at small look angles 10 dB (uncertain — see Level 3); detuning/temperature/ageing 2 dB. Even the sum (33 dB) leaves ~19 dB at 30 km. **Conclusion:** during ascent/descent the 433 MHz link is robust; SF7–SF9 is enough, and lower SF keeps packets short (less Doppler-rate trouble, more telemetry rate).

**Same link at the Singapore licence-exempt power** (10 mW e.r.p. = 12.15 dBm EIRP instead of 32.5 dBm): every received level above drops by 20.35 dB → $P_r$ ≈ −96.2 dBm, margin ≈ **+32 dB** at 2.4 kb/s (+41 dB at SF12/125). The full 33 dB impairment stack would then leave ≈ −1 dB at 2.4 kb/s (≈ +8 dB at SF12) — so at legal power the worst-case stack no longer closes at 30 km, although the realistic (non-additive) case does. Duty is also capped at 10 % (a 32-byte SF7/125 frame every 0.72 s).

### Example B — 915 MHz E220-900T30D secondary link, 30 km
*Regulatory note*: 30 dBm conducted at 902–928 MHz is licence-free in the US only as a §15.247 FHSS or ≥ 500 kHz DTS signal (a fixed-channel 125 kHz LoRa link is not compliant); 915 MHz is outside Singapore's SRD bands, and in Singapore's 917–925 MHz band a LoRa end device is limited to 100 mW e.r.p. and 1 % duty (≈ 7 dB less EIRP than here) or 500 mW e.r.p. at 866–869 MHz ([band plans](../15-lora-ism-radios/ism-band-plans-duty-cycle.md)).
| Line | Value |
|---|---|
| Tx power | +30.0 dBm |
| Tx feeder | −0.7 dB |
| Rocket antenna | 0 dBi |
| FSPL (915 MHz, 30 km) | −121.2 dB |
| Gases | −0.15 dB |
| Polarisation (linear–linear, 30° misalignment) | −1.25 dB |
| Pointing | −1.0 dB |
| Ground Yagi (linear, ~10 elements) | +12.0 dBi |
| Rx feeder (5 m LMR-400 at 915 MHz) | −0.7 dB |
| **Received power** | **−83.0 dBm** |
| Margin vs −128 dBm | **≈ +45 dB** |

At equal antenna gains the 915 MHz link is 6.5 dB (path) + 3 dB (power) = 9.5 dB weaker than 433 MHz; the linear Yagi's polarisation loss varies from 0 dB (aligned) to > 20 dB (near-crossed) as the rocket rolls/tilts — a circularly polarised ground antenna trades a fixed 3 dB for immunity to this ([polarization-mismatch-loss](polarization-mismatch-loss.md)).

### Example C — same budget in G/T form (link A)
EIRP = 2.5 dBW; $G_r - L_{fr}$ = 10.55 dB; $T_\text{sys}$ = 1028 K ⇒ G/T = 10.55 − 30.1 = **−19.6 dB/K**. $C/N_0$ = 2.5 − 114.7 − 3.0 − 1.0 − 0.1 − 19.6 + 228.6 = **92.7 dB-Hz**, identical to $P_r - 10\log(kT_\text{sys})$ computed from the dBm budget. At 2.4 kb/s, $E_b/N_0$ = 58.9 dB available against ≈ 6 dB required.

### Example D — what an LNA buys on this link
A masthead LNA (NF 0.6 dB) lowers $T_\text{sys}$ from ~1030 K to ~200 K: +7 dB of margin ([07-noise-linearity/receiver-cascade-analysis](../07-noise-linearity/receiver-cascade-analysis.md) Example B). On the ascent link this is unnecessary; for the landed-rocket case it is worth ×1.5 in range (plane-earth regime, $10^{7/40}$).

### Example E — landed rocket (the case that actually limits recovery)
The rocket lies on the ground, antenna ~0.1 m up and horizontal (dipole along the body ⇒ horizontal polarisation), 5 km away, ground-station mast 5 m. Two-ray loss over medium-dry ground at 433 MHz: 153.6 dB — **54 dB more than FSPL** (99.2 dB). With 33 dBm, 0 dBi, 11 dBic, −3 dB polarisation and −1 dB feeder: $P_r$ = −113.6 dBm, margin +14 dB (2.4 kb/s) or +23 dB (SF12). At 10 km: +2 dB / +11 dB; at 20 km: −10 dB / −1 dB. (That is the licensed 2 W case; at Singapore's licence-exempt 10 mW e.r.p. subtract 20.35 dB: −6 dB / +3 dB at 5 km — recovery then relies on SF12, a higher mast or walking toward the last fix.) A vertically polarised whip 0.3 m up does ~14 dB better (`prop_two_ray.py` §5). Add a 25 m ridge (−15 dB, [diffraction-knife-edge](diffraction-knife-edge.md)) or 100 m of woodland (−9 dB at 466 MHz, P.833) and even 5 km fails. Design consequences: log/transmit the last good GPS fix during descent; switch to a high-SF beacon mode after landing; raise the ground antenna (hilltop, mast, drone relay); consider a vertical ground-plane beacon antenna that deploys on landing.

**Canonical landed-rocket assumption set (W5-E9, D6 #16).** "The landed range" is a scenario number, not a property of the radio. This example is the KB's reference set: rocket antenna 0.1 m above ground, horizontal (H-pol), 0 dBi; ground-station mast 5 m with an 11 dBic Yagi, −3 dB polarisation, −1 dB feeder; medium-dry ground (εr 15, σ 10⁻³ S/m, ITU-R P.527 legacy category) in the full two-ray model of `prop_two_ray.py` §5; 433 MHz, 33 dBm; **no fade or terrain margin**. Other pages use other sets; quote the set with the number:

| Scenario (page) | Rocket antenna | Station | Path model | TX / mode | Margin kept | Range where margin = 0 |
|---|---|---|---|---|---|---|
| **Canonical (this example)** | 0.1 m, H-pol, 0 dBi | 5 m mast, 11 dBic | two-ray, medium-dry ground | 33 dBm; 2.4 kb/s (−128 dBm) / SF12 (−137 dBm) | 0 dB | **≈ 11.5 km / ≈ 19 km** |
| same, licence-exempt 10 mW e.r.p. | same | same | same | −20.35 dB | 0 dB | ≈ 3.5 km / ≈ 6 km |
| same, vertical whip 0.3 m up | 0.3 m, V-pol | same | same | 33 dBm | 0 dB | ≈ 14.5 dB more margin (`prop_two_ray.py` §5) |
| [15 LoRa link budget, Example 4](../15-lora-ism-radios/lora-sensitivity-and-link-budget.md) | 0.2 m | 2 m (6 m) | $40\log d-20\log(h_th_r)$ | 33 dBm SF9/125 | 13 dB | ≈ 5.6 km (≈ 9.8 km) |
| [20 telemetry recipe](../20-projects-recipes/lora-rocket-telemetry-link.md) | 0.2 m | 2 m tripod (6 m mast) | flat-earth two-ray | 33 dBm SF9/125, masthead LNA / bare module | recipe's | 7.5 km (13 km) / 5.6 km |

In the 40 dB/decade regime every 6 dB of margin is a factor 1.41 in range, so these sets differ by factors of 2–3 for the same radio. Terrain and vegetation (−9 to −15 dB above) come on top of all of them.

## Practical notes
- **Measure the transmitter power at the flight supply voltage**; 2 W modules drop output at low supply and when hot.
- **Include the cable/connector losses you actually have**, especially at 915 MHz and GNSS frequencies; U.FL pigtails and 1.13 mm cable are lossy.
- **Spreadsheet or script, not head arithmetic** — use `prop_link_budget.Link`:
  ```python
  from prop_link_budget import Link
  L = Link(433.125e6, 30e3, "my link")
  for name, v in [("Tx", 33), ("Tx feeder", -0.5), ("pol", -3), ("Yagi", 11), ("point", -1), ("Rx feeder", -0.45)]:
      L.add(name, v)
  L.report(sens_dbm=-128, NF=6, Ta=160, B=125e3, snr_min=-10)
  ```
- **Validate on the ground before flight:** a range test with the rocket's actual antenna and airframe at a few km, measuring RSSI and SNR, calibrates the antenna/feeder lines; a drone-lifted transmitter emulates altitude.
- **Record everything:** log RSSI/SNR per packet on the ground station, with rocket attitude from the flight log, to reconstruct the real antenna pattern and plume effect after the flight (consistent with the team's record-everything ethos).

## Common mistakes & misconceptions
- **Using datasheet sensitivity at a different data rate/SF than the one flown** (or the EBYTE −147 dBm).
- **Peak antenna gains instead of gains toward the other end.**
- **Ignoring polarisation** (0–30 dB between linear antennas) or double-counting it with a circular antenna.
- **Treating margin as range headroom beyond the horizon.**
- **Using FSPL for the landed or pad case.**
- **Adding every worst-case impairment linearly and concluding the link cannot work** — independent random impairments combine statistically (RSS of their standard deviations), while systematic ones (pattern null during boost) must be handled deterministically ([link-margin-availability](link-margin-availability.md)).
- **Forum myth: "my 1 W LoRa should reach 100 km so SF12 is pointless."** Both statements depend entirely on geometry; for elevated paths, 100 km is easy; for ground-level paths a few km can be hard.

## How to simulate / verify
- `tools/verify/prop_link_budget.py` — `Link` class; examples A–E; range tables; G/T and C/N0 cross-check.
- `tools/verify/prop_margin.py` — toy flight time-series (pattern + lobing) to estimate packet loss fraction.
- For terrain-specific landing-zone predictions use ITM (Longley–Rice) or ITU-R P.1812/P.452 with a DEM, or ITU-R P.528 for the airborne phase ([empirical-path-loss-models](empirical-path-loss-models.md)).
- Post-flight: overlay logged RSSI on the predicted $P_r(t)$ from the trajectory; discrepancies isolate antenna pattern and plume effects.

## Open questions / gaps
- Plume attenuation for student-scale solid and hybrid motors at 433/915 MHz is unquantified; large-launcher data (M-V) suggest tens of dB at small look angles.
- The rocket antenna's installed pattern (with airframe, fins, nose-cone material) should come from simulation/measurement (domain 08) — here 0 dBi nominal and a sin²ψ dipole model are used.
- EBYTE air-rate mapping (thus exact sensitivity) unknown; −128 dBm is a physics-based estimate.

## Sources
1. H. T. Friis, "A note on a simple transmission formula," *Proc. IRE* 34(5), 254–256 (1946). (peer-reviewed)
2. ITU-R P.525-5 (11/2024), free-space attenuation. https://www.itu.int/rec/R-REC-P.525/en (standard)
3. Semtech, *SX1261/2 Data Sheet* Rev 1.2/2.2 — sensitivity and SNR tables. (datasheet)
4. Chengdu Ebyte, E22-400TXXX data sheet (2022) and E220-900T30D user manual — Tx power 33 ± 0.5 dBm / 29.5–30 dBm, frequency ranges. (datasheet; sensitivity claim not used)
5. É. Dieudonné, A. Kameni, L. Pichon, D. Monchaux, "Radio frequency attenuation by a rocket plume using diffraction theory and finite element modeling," 7th EUCASS, 2017, doi:10.13009/EUCASS2017-21, https://www.eucass.eu/doi/EUCASS2017-021.pdf — uses in-flight 300 MHz data of the M-V 2nd stage (Kinefuchi et al.). (conference paper)
6. T. S. Rappaport, *Wireless Communications: Principles and Practice*, 2nd ed., Prentice Hall 2002, §4.2–4.3 (Friis, link budget). (textbook)
7. B. Sklar, *Digital Communications*, 2nd ed., Prentice Hall 2001, ch. 5 (link analysis, G/T, C/N0, margin). (textbook)
8. ITU-R P.676-11 (gases), P.372-13 (noise). (standards)
9. `tools/verify/prop_link_budget.py`, `prop_two_ray.py`, `prop_polarization.py` (this KB).
