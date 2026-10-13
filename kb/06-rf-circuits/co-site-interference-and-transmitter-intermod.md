---
title: Co-site interference and transmitter intermodulation — reverse IMD, desense by nearby transmitters, antenna isolation, launch-site frequency planning, and on-board 433/915 MHz + GNSS + Wi-Fi coexistence
domain: 06-rf-circuits
slug: co-site-interference-and-transmitter-intermod
tags: [co-site, co-location, transmitter-intermodulation, reverse-imd, turnaround-loss, intermodulation-attenuation, etsi-en-300-086, desensitisation, blocking, transmitter-noise, antenna-isolation, itu-r-m2244, vertical-separation, circulator, isolator, cavity-filter, frequency-planning, golomb-ruler, launch-site, multiple-teams, coexistence, gnss, wifi, esp32, e22, e220, rocket]
prerequisites:
  - ../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md
  - ../07-noise-linearity/dynamic-range-sfdr-blocking.md
  - ../09-propagation-link-budget/friis-free-space-path-loss.md
  - power-amplifiers.md
related:
  - circulators-isolators.md
  - duplexers-diplexers-and-crystal-filters.md
  - pa-control-protection-and-sequencing.md
  - agc-loops-and-receiver-gain-control.md
  - oscillator-phase-noise-ltv-isf.md
  - ../21-gnss/gnss-interference-jamming-spoofing.md
  - ../08-antennas/antennas-on-rockets.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../15-lora-ism-radios/rocket-telemetry-radio-design.md
  - ../00-math-foundations/canonical-values-and-conventions.md
  - ../13-pcb-rf-layout-emc/shielding-and-isolation.md
level: mixed
confidence: medium
last_updated: 2026-10-12
---

# Co-site interference and transmitter intermodulation

## Questions this page answers
- Why does a transmitter produce intermodulation products when another transmitter is nearby ("reverse" or transmitter IMD)?
- How does a circulator or isolator at the transmitter output reduce that intermodulation?
- How far apart must two antennas be for a given isolation, horizontally and vertically?
- Another team at the launch site is transmitting 1 W a few hundred kHz from my channel. How far away must they be, and what can I do?
- Why can't a filter at my receiver remove a nearby transmitter's noise?
- How should several teams choose LoRa channels so that their intermodulation products don't land on each other?
- On one rocket with a 433 MHz LoRa, a 915 MHz LoRa, GNSS and an ESP32 with Wi-Fi, which combinations are dangerous?

## TL;DR
- **Co-site problems come in three kinds.** (1) *Receiver desense or blocking:* a strong transmitter overloads a nearby receiver. (2) *Transmitter noise and spurs:* these land in the victim's channel and only the *transmitter* can filter them. (3) *Intermodulation:* in either radio's nonlinear parts, or in rusty joints (PIM), products land on a third frequency.
- **Antenna isolation (ITU-R M.2244 [1]):** side by side, $I_H=22+20\log(d/\lambda)-(G_t+G_r)$, which is Friis free-space loss. Stacked vertically, $I_V=28+40\log(d/\lambda)$ (dipoles in each other's pattern nulls, d > 10λ). The report's 465 MHz numbers are reproduced: 30/45/60 dB need 1.62/9.11/51.2 m horizontally but only 0.72/1.72/4.07 m vertically. Two 2 dBi whips 5 m apart give only **35 dB at 434 MHz**.
- **Transmitter (reverse) IMD:** a signal entering a PA's output mixes with the PA's own carrier. In simulation the $2f_1-f_2$ product tracked the interferer at **1 dB/dB** and $2f_2-f_1$ at 2 dB/dB. A hard-saturated device converts the interferer into the $2f_1-f_2$ product with only **≈ 6 dB loss** ("turnaround loss"); a lightly driven one with ≈ 25 dB. ETSI EN 300 086 base stations, with the interferer about 30 dB below the carrier, must reach 40 dB (general) or **70 dB** (shared sites, circulators allowed) intermodulation attenuation [2]. The 70 dB class needs ≈ 34 dB of isolation in front of a saturated PA.
- **Desense at a launch site:** take an SX1262 at SF12/125 kHz with blocking of 88 dB at 1 MHz offset. A 1 W, 2 dBi neighbour must then be **≥ 550 m** away in free space before your receiver loses 3 dB of sensitivity. If the neighbour's transmitter noise in your channel is −120 dBc/Hz, it takes **1.4 km**. Receive filtering cannot help with that noise. A notch cavity cannot reject a neighbour 0.58 MHz away by more than about 10 dB ([duplexers](duplexers-diplexers-and-crystal-filters.md)).
- **Frequency planning:** five teams on a 250 kHz-spaced grid produce 20 third-order IM coincidences on used channels. Channels chosen on a **Golomb ruler** (0, 1, 4, 9, 11 × 125 kHz from 433.175 MHz) produce **none** and fit inside 433.05–434.79 MHz (verified).
- **On the rocket:** with the E22 on CH 24 (434.125 MHz) and the E220 on 920.125 MHz, no LoRa-only product of order ≤ 5 falls in a GNSS band. However, **Wi-Fi channel 6 minus 2 × 434.125 MHz** (3rd order) lands at 1558–1580 MHz, on top of **GPS L1**, and channel 11 lands on GLONASS G1. Keep the ESP32 on Wi-Fi channel 1 or off in flight, and keep 433 MHz out of the Wi-Fi PA and the GNSS LNA ([21 GNSS interference](../21-gnss/gnss-interference-jamming-spoofing.md)).

## Intuition (no math)
Put two radios close together and each sees the other at enormous power: the path loss between antennas a few metres apart is only 30–50 dB, against 120–150 dB for the link you care about. Three things then go wrong.
1. **The receiver hears too much.** Its LNA and mixer were designed for microvolts. A neighbour's watt arriving at milliwatt level compresses them, so your signal is quieter (desense). Or the neighbour mixes with your LO's phase noise (reciprocal mixing).
2. **The neighbour isn't clean.** Every transmitter emits a little noise, sidebands and spurs well outside its channel. Some of that lands on your frequency, and once it is at your frequency no filter in your receiver can tell it from your wanted signal. It must be removed at the neighbour's output, or by distance.
3. **Things mix.** Any nonlinear element (your PA, the neighbour's PA, an LNA, even a corroded bolt) that carries two strong signals creates new ones at $2f_1-f_2$, $f_1+f_2-f_3$ and so on. A transmitter's output stage is a mixer for signals coming *backwards* from its antenna. That is transmitter intermodulation, and it is why shared radio sites put isolators on every transmitter.

The cures, in order of power: frequency separation and planning, physical separation (especially vertical), antenna pattern nulls and polarisation, filtering at the *transmitter* (for noise and spurs) and at the *receiver* (for blocking), and isolators on transmitters (for IMD).

## The math

### Level 1 — budgets
- **Isolation between antennas:** $I=P_{TX}-P_{RX,in}$ (dB), including both antenna gains in each other's direction, cable losses and filters.
- **Blocking:** keep $P_{TX}-I\le P_{block}$, the receiver's tolerable out-of-channel level at that offset. For SX126x data-sheet blocking specs, $P_{block}=(S+3\text{ dB})+B_{dB}$, where S is the sensitivity.
- **Transmitter noise:** $P_{TX}+\mathcal L_{TX}(\Delta f)+10\log B-I\le N_{floor}-m$, with $N_{floor}=-174+NF+10\log B$ and a margin m (6 dB keeps desense below 1 dB).
- **Transmitter IMD:** with an interferer $P_i$ arriving at the PA output, the product level is $P_{IM}=P_i-L_{ta}$ for $2f_{own}-f_i$ ($L_{ta}$ = turnaround/conversion loss), falling 1 dB per dB of $P_i$. The product $2f_i-f_{own}$ falls 2 dB per dB.
- **Isolation formulas** [1]: $I_H=22+20\log_{10}(d_h/\lambda)-(G_{Tx}+G_{Rx})$ (dBi toward each other, far field $d\ge2D^2/\lambda$, ≥ 10λ suggested); $I_V=28+40\log_{10}(d_v/\lambda)$ (vertical dipoles, $d_v>10\lambda$); slant $I_s=(I_V-I_H)\,\alpha/90°+I_H$.

### Level 2 — derivations
**(a) Where the "22" and "28 + 40 log" come from.** Friis gives $P_r/P_t=G_tG_r(\lambda/4\pi d)^2$, so $I=20\log(4\pi)+20\log(d/\lambda)-G_t-G_r$, and $20\log4\pi$ = 21.98 dB. Two vertical dipoles stacked on one axis see each other along their pattern nulls, where the far-field ($1/r$) terms vanish. The coupling then comes from the $1/r^2$ induction fields, so power falls as $1/r^4$, i.e. 40 dB per decade [1]. That is why vertical separation on one mast is so effective, *if* the nulls are real. Tilt, mounting structure, feed-cable radiation and the rocket airframe all fill them in. The report itself warns that this prerequisite is hard to guarantee and recommends falling back on Friis with conservative gains [1]. Script §A reproduces the report's 465 MHz tables and gives:

| Arrangement (2 dBi antennas) | 434 MHz | 920 MHz |
|---|---|---|
| side by side, 5 m | 35.2 dB | 41.7 dB |
| side by side, 20 m | 47.2 dB | 53.8 dB |
| stacked, 2 m (formula; below its 10λ validity) | 46.5 dB | 59.5 dB |

**(b) Transmitter (reverse) intermodulation.** A PA's output network is passive and bidirectional. A signal $P_i$ arriving from the antenna reaches the drain or collector and sees the device's nonlinear output characteristic, which is being swung hard by the PA's own carrier. Model the device as a memoryless nonlinearity $y=f(x_1+x_2)$ with $x_1=A_1\cos\omega_1t$ (own carrier) and a small $x_2=A_2\cos\omega_2t$. Expanding to first order in $A_2$, the product at $2\omega_1-\omega_2$ is proportional to $A_2$ times a coefficient fixed by $A_1$, so it falls **1 dB per dB** of interferer. $2\omega_2-\omega_1$ needs $A_2^2$ and falls **2 dB per dB**. Script §B uses a tanh device:
- Lightly driven (tanh drive 0.5): with the interferer at −30 dBc, $2f_1-f_2$ is at −54.9 dBc, a turnaround of 24.9 dB.
- Hard-saturated (drive 5): −36.3 dBc, a turnaround of **6.3 dB**. This is the limiter result: a hard limiter suppresses a weak signal by 6 dB and creates an equal-amplitude product at $2f_1-f_2$ [5].

A saturated LoRa/FM PA (class C/E) is thus nearly the worst case for transmitter IMD. In real PAs the output matching network and harmonic filter attenuate the interferer on its way in when it is out of band, which is why measured turnaround losses range from about 5 to 20 dB.

**ETSI EN 300 086 test** [2]: an equal-power interfering transmitter is coupled through a 20 dB pad and a directional coupler into the line behind a 10 dB pad. That puts the interferer roughly 30 dB below the carrier at the transmitter's port, offset 50–100 kHz above and below. The largest third-order product relative to the carrier is then the "intermodulation attenuation". Limits: **≥ 40 dB** in general; **≥ 70 dB** for base stations at shared sites or where the licence demands it, and then any isolating devices (circulators) must be fitted during the test. With a −30 dBc interferer, 40 dB means a total conversion loss ≥ 10 dB, which a moderately driven PA meets. 70 dB means ≥ 40 dB: ≈ 34 dB of isolation in front of a saturated stage, one or two circulator stages ([circulators](circulators-isolators.md)).

**(c) Why an isolator helps twice as much for one product.** An isolator with reverse isolation $I_{iso}$ attenuates the incoming interferer by $I_{iso}$. The IM product generated in the PA travels *forward* through the isolator with only its insertion loss. So $2f_{own}-f_i$ falls by $I_{iso}$ (1:1) and $2f_i-f_{own}$ by $2I_{iso}$ (2:1). The isolator's own ferrite is slightly nonlinear: high-power co-site installations specify the isolator's IMD as well.

**(d) Receiver desense from a nearby transmitter.** The SX1261/2 data sheet gives blocking of 88/90/99 dB at 1/2/10 MHz offset for SF12/BW125, referred to sensitivity + 3 dB ([07 dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md)). With sensitivity −137 dBm, the tolerable blocker is −46 dBm at 1 MHz. A 1 W neighbour with 2 dBi antennas each way must then be ≥ 549 m away in free space (436 m at 2 MHz, 155 m at 10 MHz; §C). This is the worst case: the blocking spec is defined for a wanted signal only 3 dB above sensitivity. A link with 20 dB of margin can tolerate a blocker about 20 dB stronger, i.e. 10× closer, before it fails. Blocking is a *margin* problem, not a binary one.

**(e) Transmitter noise wins at close range.** If the neighbour's transmitter has noise $\mathcal L_{TX}$ in your channel, the isolation needed for ≤ 1 dB desense (6 dB below a −117 dBm floor in 125 kHz, NF 6 dB) is $I\ge P_{TX}+\mathcal L_{TX}+10\log B-(N_{floor}-6)$:

| Neighbour's noise in your channel | Isolation needed (1 W) | Free-space distance (2+2 dBi, 434 MHz) |
|---|---|---|
| −110 dBc/Hz | 94 dB | 4.4 km |
| −120 dBc/Hz | 84 dB | 1.4 km |
| −130 dBc/Hz | 74 dB | 440 m |
| −140 dBc/Hz | 64 dB | 140 m |

(§C; the noise level is a parameter. Semtech does not specify SX126x transmitter noise at these offsets, so measure a neighbour's module with a spectrum analyser if it matters.) Nothing you do at your receiver helps, because the noise is in your channel. The neighbour's own band-pass filter after their PA, distance, terrain and antenna pattern are the only remedies.

**(f) Third-order coincidences in a channel plan.** A third-order product of transmitters at $f_a,f_b,f_c$ lands on a used channel $f_d$ when $2f_a-f_b=f_d$ or $f_a+f_b-f_c=f_d$. Both conditions mean two channel *differences* are equal ($f_a-f_b=f_d-f_a$, or $f_a-f_c=f_d-f_b$). A channel set whose pairwise differences are all distinct, a **Golomb ruler**, therefore has no on-channel third-order hits. Script §D: five channels on a 250 kHz-spaced grid have 20 coincidences; the Golomb set {0, 1, 4, 9, 11} × 125 kHz from 433.175 MHz has none and fits inside 433.05–434.79 MHz. Products that miss a channel centre by less than about half a bandwidth still interfere. Use a grid at least as wide as the occupied bandwidth, and check fifth-order products for very strong sites.

**IM3-free channel sets (optimal Golomb rulers)** on a channel grid $g$; the span includes half a channel at each end (§D):

| Channels | Ruler (grid slots) | Span at 125 kHz | Span at 250 kHz | Fits 433.05–434.79 MHz (1.74 MHz)? |
|---|---|---|---|---|
| 3 | 0, 1, 3 | 0.50 MHz | 1.00 MHz | yes / yes |
| 4 | 0, 1, 4, 6 | 0.875 MHz | 1.75 MHz | yes / no (by 10 kHz) |
| 5 | 0, 1, 4, 9, 11 | 1.50 MHz | 3.00 MHz | yes / no |
| 6 | 0, 1, 4, 10, 12, 17 | 2.25 MHz | 4.50 MHz | no / no |
| 7 | 0, 1, 4, 10, 18, 23, 25 | 3.25 MHz | 6.50 MHz | no / no |

The 1.74 MHz 433 MHz band therefore holds at most five IM3-free 125 kHz LoRa channels. Beyond that, teams must share in time or use other bands, e.g. the 866–869 / 917–925 MHz windows under the rules in [canonical values](../00-math-foundations/canonical-values-and-conventions.md).

**Co-site analysis procedure** (for a launch site or a vehicle):
1. List every emitter and receiver: frequency, bandwidth, power, antenna gain and position, duty cycle and timing.
2. Estimate the isolation for every pair (formulas above for separated antennas; measure on the vehicle).
3. For each receiver, check against each transmitter: (i) blocking at that offset, (ii) the transmitter's noise in the receiver channel, (iii) reciprocal mixing ([07 phase noise](../07-noise-linearity/phase-noise-and-jitter.md)).
4. Enumerate harmonics and IM products to order 5 and mark those landing within ±BW/2 of any receiver (script §D–E pattern).
5. For each hit, find where the nonlinearity is: a transmitter output (reverse IMD), a receiver front end, or passive hardware. Pick the mitigation from the toolbox below.
6. Verify on the integrated system with everything running, and log receiver health (RSSI, SNR, GNSS C/N₀, MON-RF) against transmitter activity.

### Level 3 — on-board coexistence (one rocket, several radios)
Take a typical Space Bar stack: E22-400T33D (2 W, 434.125 MHz, the canonical Singapore channel), E220-900T30D (1 W, 920.125 MHz), a GNSS receiver (L1, plus L2/L5 on dual-band parts) and an ESP32 with 2.4 GHz Wi-Fi/BLE. Antennas sit 0.2–1 m apart on the airframe, i.e. in each other's *near field* at 434 MHz (λ = 0.69 m). There the Friis formula is invalid, and isolation is typically only 10–30 dB; measure it with a VNA between the installed antennas ([antennas on rockets](../08-antennas/antennas-on-rockets.md)). The script enumerates products of order ≤ 5 that land in GNSS bands (§E):

| Product | Order | Lands at | Band hit |
|---|---|---|---|
| Wi-Fi ch 6 (2426–2448 MHz) − 2 × 434.125 | 3 | 1558–1580 MHz | **GPS L1, Galileo E1, BeiDou B1** |
| Wi-Fi ch 11 (2451–2473) − 2 × 434.125 | 3 | 1583–1605 MHz | **GLONASS G1** |
| Wi-Fi ch 11 − 3 × 434.125 | 4 | 1149–1171 MHz | edge of L5/E5 |
| 434.125 / 920.125 MHz combinations | ≤ 5 | — | none in GNSS bands |
| 3 × 434.125 | 3 (harmonic) | 1302.4 MHz | just clears the 1215–1300 MHz RNSS band ([canonical values](../00-math-foundations/canonical-values-and-conventions.md)) |

Where the mixing happens matters:
- **In the GNSS LNA:** it sees both the 433 MHz and the Wi-Fi signal, each attenuated by its antenna's out-of-band rejection. A SAW ahead of the LNA kills both.
- **In the ESP32's Wi-Fi PA:** 433 MHz picked up on the board enters the PA output. This is reverse IMD, radiated by the Wi-Fi antenna at L1.
- **In airframe joints (PIM):** possible, but rarely checked ([07 nonlinearity](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md)).

The other on-board mechanisms are covered elsewhere: harmonic and clock-harmonic hits on GNSS ([21](../21-gnss/gnss-interference-jamming-spoofing.md)), the E22's 2nd harmonic near 868 MHz and channel pairing ([canonical values](../00-math-foundations/canonical-values-and-conventions.md)), and LoRa self-desense through a shared antenna ([duplexers Ex. 2](duplexers-diplexers-and-crystal-filters.md#example-2--rocket-with-e22-433-and-e220-915-on-one-antenna)).

### Level 3 — passive intermodulation (PIM) on the vehicle and at the station
- **What it is.** Metal–oxide–metal contacts, ferromagnetic materials (steel hardware, nickel-plated connectors) and loose joints have a weakly nonlinear I–V curve. With two strong carriers flowing through them they generate third-order products just as an amplifier does, but at levels typically 100–160 dB below the carriers ([07 nonlinearity](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md)).
- **Why it matters here.** The products are *radiated* from wherever the joint is, outside any filter. They are serious for systems that receive weak signals near strong transmitters on shared hardware: cell sites, and potentially a rocket with a 2 W telemetry transmitter and a GNSS antenna on the same airframe.
- **Scaling:** a 3rd-order PIM product rises 3 dB per 1 dB of both carriers together (2:1 in one, 1:1 in the other), so halving transmit power on the pad cuts it by 9 dB.
- **Practice:** use stainless or brass rather than nickel-plated steel hardware near antennas, torque connectors, avoid dissimilar-metal contacts in the antenna's near field, and bond airframe sections through clean conductive surfaces or isolate them deliberately.

### Level 3 — mitigation toolbox

| Mitigation | Helps with | Typical gain | Notes |
|---|---|---|---|
| Frequency separation / planning (Golomb, ≥ several MHz) | blocking, TX noise, IMD | decisive | coordinate at the launch-site briefing |
| Time sharing (TDMA between teams or radios) | everything | decisive | LoRa is half-duplex; schedule on-board TX bursts |
| Vertical separation on one mast | all | 40 dB/decade (if nulls hold) | far better than horizontal for collinear antennas |
| Cross-polarisation | all | 10–20 dB in practice | multipath depolarises it |
| Transmitter band-pass/cavity filter | TX noise and spurs at the victim | 20–80 dB | only the transmitter's owner can fit it |
| Receiver preselector (SAW, cavity) | blocking, reciprocal mixing, LNA IMD | 20–60 dB out of band | useless for in-channel noise |
| Isolator/circulator on the PA | transmitter IMD, PA load-pull | 20–30 dB per stage | 1:1 and 2:1 reductions (c) |
| Lower power, higher antenna gain toward the wanted path | all | dB for dB | rocket telemetry can often use less power on the pad |
| Shielding and filtering on board | PIM, coupling to digital | 10–40 dB | [13 shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md) |

## Design equations & rules of thumb

| Quantity | Equation | Typical numbers |
|---|---|---|
| Horizontal isolation | $22+20\log(d/\lambda)-G_t-G_r$ | 434 MHz, 5 m, 2+2 dBi: 35 dB |
| Vertical isolation | $28+40\log(d/\lambda)$, $d>10\lambda$ | 465 MHz, 45 dB: 1.72 m |
| Reverse-IMD product | $P_i-L_{ta}$ (1:1); $2f_i-f_o$ 2:1 | saturated PA: $L_{ta}$ ≈ 6 dB |
| ETSI TX IM attenuation | ≥ 40 dB; ≥ 70 dB shared sites | interferer ≈ −30 dBc |
| Isolator effect | −$I_{iso}$ on $2f_o-f_i$; −2$I_{iso}$ on $2f_i-f_o$ | 25 dB isolator: −25 / −50 dB |
| Blocking-limited distance | $d=\lambda10^{(P_{TX}-P_{block}-22+G)/20}$ | 1 W, 1 MHz, SF12: 550 m |
| TX-noise isolation | $P_{TX}+\mathcal L+10\log B-(N_{floor}-6)$ | −120 dBc/Hz: 84 dB |
| IM3-free channel set | Golomb ruler on the channel grid | 5 channels in 12 slots |

Rules of thumb:
- Ask every team for frequency, power, bandwidth and antenna position before the launch window. Allocate channels on a Golomb ruler and leave guard bands near the band edges.
- Ground stations at a shared site: aim for ≥ 50 dB antenna isolation between transmitters and others' receivers. That means tens of metres horizontally, a few metres vertically, or both.
- On the rocket: no two transmitters keyed at the same time unless measured. Wi-Fi off, or on channel 1, during flight. A SAW ahead of every GNSS LNA.

## Worked examples

### Example 1 — Three teams' ground stations on one pad
Team A (you) receives 434.125 MHz. Team B transmits 1 W uplink bursts at 434.55 MHz from 10 m away. Team C transmits 0.5 W at 433.30 MHz from 30 m away.
- **Isolation:** $I_H$(10 m) = 22 + 23.2 − 4 = 41.2 dB, so B arrives at **−11 dBm**. $I_H$(30 m) = 50.8 dB, so C arrives at about −24 dBm.
- **Blocking:** both are far above the −46 dBm SF12 blocking tolerance at 1 MHz, and they are *closer* than 1 MHz, so your receiver loses tens of dB of margin while they transmit (§C, d).
- **IMD:** $2f_B-f_C$ = 435.80 MHz is not on your channel, but $2f_C-f_B$ = 432.05 MHz and $f_B+f_C-f_A$ = 433.725 MHz land on other teams' channels.
- **Fixes:** move B and C several MHz away (another band, or a licensed allocation), time-share uplink windows, separate the stations by ≥ 100 m, and stack antennas vertically where possible.

### Example 2 — A repeater-style shared mast
Mount two 434 MHz dipoles on one mast, 4 m apart vertically (5.8λ, a little inside the 10λ validity). The formula gives about 58 dB. Expect 45–55 dB once the mast and feed cables fill the nulls. Measure with a VNA before relying on it. For 70 dB, add a cavity band-pass on the transmitter and a preselector on the receiver ([duplexers §(b)](duplexers-diplexers-and-crystal-filters.md#level-2--derivations)).

### Example 3 — Transmitter IMD between the rocket's E22 and E220
Both transmit at once through antennas with about 25 dB mutual isolation (near-field, airframe-mounted).
- **Inside the E220's PA** (own carrier 920.125 MHz, +30 dBm): the E22's +33 dBm arrives at about +8 dBm, i.e. −22 dBc. With a saturated-PA turnaround of about 6 dB, the 1:1 product $2f_o-f_i$ = 2 × 920.125 − 434.125 = **1406.1 MHz** comes out at about −28 dBc ≈ +2 dBm. The second-order sum $f_o+f_i$ = 1354.25 MHz is of similar order.
- **Inside the E22's PA** (own 434.125 MHz): the E220's signal arrives at about +5 dBm (−28 dBc). Its 1:1 product $|2f_o-f_i|$ = 51.9 MHz is far below the band and is stopped by the output network. The 2:1 product $2f_i-f_o$ = 1406.1 MHz again is lower by roughly another 28 dB.

Neither 1354 nor 1406 MHz lies in a GNSS band. Both are spurious emissions, however, and the limit above 1 GHz is −30 dBm ([PA harmonic limits](power-amplifiers.md#design-equations--rules-of-thumb)), so +2 dBm is about 30 dB too high. Fixes: low-pass/band-pass filters at each module output (they also attenuate the incoming interferer, for 1:1 and 2:1 benefit), time-interleaved transmission, or more antenna separation.

### Example 4 — ESP32 Wi-Fi and GPS on one avionics bay
The ESP32 runs Wi-Fi on channel 6 for pad-side telemetry while the E22 transmits. In any shared nonlinearity, the third-order product $f_{WiFi}-2f_{434}$ covers 1558–1580 MHz, i.e. GPS L1 (§E). Even a −100 dBm product at the GNSS antenna is near the ≈ −95 dBm tracking-loss threshold of [21](../21-gnss/gnss-interference-jamming-spoofing.md). Fixes: Wi-Fi channel 1 (product at 1533–1555 MHz, below the L1 band); Wi-Fi off after arming; separate the boards; filter the 434 MHz pickup into the ESP32 (keep the E22's coax and antenna away from the ESP32's PCB antenna). Log UBX-MON-RF to see whether it happens.

### Example 5 — A five-team LoRa plan at a competition
The organisers allow 433.05–434.79 MHz and five teams use 125 kHz LoRa. Take the Golomb set {0, 1, 4, 9, 11} × 125 kHz from 433.175 MHz: **433.175, 433.300, 433.675, 434.300, 434.550 MHz**. No third-order product of any two or three of them lands on a used channel (§D). Products still fall *between* channels, so leave the unused slots empty. Give each team a fixed time slot as well if two ground stations are within about 100 m. Under Singapore rules a 433 MHz SRD is limited to 10 mW e.r.p. and 10 % duty; higher powers need a licence ([canonical values](../00-math-foundations/canonical-values-and-conventions.md)). Lower power also shrinks every distance in (d)–(e) by about 20 dB.

### Example 6 — Turning a measured on-board isolation into limits
Connect a NanoVNA between the E22's and the GNSS antenna's coax ends with the rocket assembled. It reads $S_{21}$ = −28 dB at 434 MHz, the GNSS patch's out-of-band rejection included. The 2 W E22 then delivers +5 dBm to the GNSS RF input, against a MAX-M10S out-of-band immunity of about −15 dBm at 400–500 MHz ([21](../21-gnss/gnss-interference-jamming-spoofing.md)): 20 dB short. The options, combined to make up 20 dB plus margin:
- a 1575 MHz SAW ahead of the LNA (≥ 30–40 dB at 434 MHz);
- moving the antennas apart, or putting the GNSS patch on the opposite side of the airframe (often 10 dB);
- reducing E22 power to 27 dBm on the pad (−6 dB).

Re-measure after each change. The installed number is the only one that counts.

## Practical notes
- **Measure isolation, don't assume it.** Put a VNA (or a NanoVNA) between the two installed antennas, on the rocket and at the ground station. $S_{21}$ *is* the isolation.
- **Find IMD on the bench:** two signal generators, or two modules into dummy loads through a coupler (as in the ETSI arrangement), plus a spectrum analyser. Vary the interferer level by 10 dB: a product that changes 10 dB is $2f_o-f_i$ (1:1); 20 dB is $2f_i-f_o$; 0 dB means it is not that IMD.
- **PIM hunting:** if an IM product persists with both radios on good dummy loads but appears with the real antennas, suspect connectors, ferrous hardware, corroded joints or rocket body seams. Tap-test while watching the analyser.
- **Launch-day protocol:** keep a frequency table on the briefing sheet; switch off pad-side Wi-Fi and Bluetooth near GNSS antennas; agree TX time slots with teams sharing a band.
- **Ground-station layout at a shared pad:**
  - Put your receive antenna where the other teams' transmit antennas are in its pattern *null*. A Yagi's back lobe is 15–25 dB down ([Yagi](../08-antennas/yagi-uda-and-log-periodic.md)).
  - Put the LNA and SAW at the antenna, so cable loss does not raise the system NF while the preselector still protects the LNA.
  - Keep the generator, laptops and switching supplies away from the antenna; they add impulse and broadband noise ([AGC/noise blanker](agc-loops-and-receiver-gain-control.md#level-3--receiver-dsp-features)).
- **Logging for diagnosis:** time-stamp every transmission (yours and, if possible, others') and every receiver health metric. Desense shows up as SNR drops correlated with someone's TX.
- **Regulatory:** shared-site rules (ETSI EN 300 086's 70 dB class) apply to licensed base stations, not to licence-exempt SRDs. At a competition site, coordination is the practical tool ([19 competitions](../19-regulations-safety/international-rules-for-competitions.md)).

## Common mistakes & misconceptions
- *"A filter on my receiver will remove the other team's interference."* It removes out-of-channel *blocking*, not noise or spurs that are already in your channel.
- *"IM products come from the receiver."* They can just as well come from a transmitter's output stage driven by a signal entering backwards, or from rusty hardware.
- *"Doubling the distance gives 12 dB."* That holds only in the vertical-null case (40 dB/decade). Side by side in free space it is 6 dB per doubling.
- *"Equal channel spacing is the tidiest plan."* It maximises third-order coincidences; use distinct differences.
- *"LoRa's processing gain makes interference irrelevant."* Co-channel rejection helps against *in-channel* signals, but blocking and TX noise still set the floor.
- *"An isolator removes all transmitter IMD."* It removes the part generated by signals entering the PA output; IMD generated in the isolator itself, in PIM joints or in the *other* transmitter is unaffected.
- *"On-board radios are fine because each passed its own tests."* Combinations (Wi-Fi × 433 → L1) only appear when everything runs together. Test the integrated vehicle.

## How to simulate / verify
- `python3 tools/verify/rf2_cosite.py` (≈ 2 s, ALL PASS) covers: §A ITU-R M.2244 isolation formulas and tables; §B reverse-IMD slopes and turnaround loss (tanh device), ETSI class arithmetic; §C blocking- and TX-noise-limited separation; §D IM3 coincidences for equal vs Golomb channel plans; §E harmonic and IM search into GNSS bands for the on-board frequency set.
- For a specific site, extend §D with the real channel list and §E with each radio's channel and bandwidth. For antenna coupling on the airframe use NEC or openEMS ([16](../16-simulation-tools/em-solvers-fdtd-mom-fem.md)), then confirm with a VNA.

## Open questions / gaps
- MIL-HDBK-237 (EMC management) and ITU-R SM.1446 (transmitter IMD measurement) were not retrieved; ETSI EN 300 086 and ITU-R M.2244 were read instead.
- The tanh model ignores the output network's selectivity and memory effects; real turnaround losses (5–20 dB) depend on the interferer's offset and the PA's harmonic filter.
- SX126x/LLCC68 transmitter noise at 0.5–10 MHz offsets is unpublished. The TX-noise table is parametric; one spectrum-analyser measurement of an E22 would anchor it.
- Installed antenna isolation on the Space Bar airframe has not been measured.
- PIM levels of rocket airframe joints at 433/915 MHz are unknown (also noted in [07](../07-noise-linearity/nonlinearity-p1db-ip3-intermod.md)).
- The Golomb-ruler plan treats only exact on-grid coincidences; off-grid products and fifth-order terms need a site-specific check.
- The Wi-Fi × 433 MHz → L1 product has been identified by frequency arithmetic only. Its level depends on the unknown nonlinearity (ESP32 PA or GNSS LNA) and needs an integrated-vehicle test.
- Blocking distances assume free space; at a launch site, ground reflection (two-ray) and terrain usually *increase* the isolation beyond ~100 m ([two-ray](../09-propagation-link-budget/two-ray-ground-reflection.md)).

## Sources
1. ITU-R, *Report M.2244 (11/2011): Isolation between antennas of IMT base stations in the land mobile service*, §6 (horizontal, vertical, slant isolation; validity; Tables 1–2). https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-M.2244-2011-PDF-E.pdf (standard/report; read)
2. ETSI EN 300 086 V2.1.2 (2016-08), *Land Mobile Service; Radio equipment with an internal or external RF connector intended primarily for analogue speech*, §7.7 Intermodulation attenuation (definition, test arrangement, 40/70 dB limits). https://www.etsi.org/deliver/etsi_en/300001_300099/300086/02.01.02_60/en_300086v020102p.pdf (standard; read)
3. Semtech, *SX1261/2 data sheet*, blocking table (88/90/99 dB at 1/2/10 MHz, SF12/BW125) — as used in [07 dynamic range](../07-noise-linearity/dynamic-range-sfdr-blocking.md). (datasheet)
4. ARRL, *The ARRL Handbook*, interference and repeater chapters (transmitter intermodulation, circulators at shared sites, desense). (handbook; background)
5. W. B. Davenport, "Signal-to-noise ratios in band-pass limiters," *J. Appl. Phys.* 24(6), 720–727, 1953 (weak-signal suppression in hard limiters; the 6 dB result). (peer-reviewed; cited)
6. U.S. DoD, MIL-HDBK-237D, *Electromagnetic Environmental Effects and Spectrum Supportability Guidance for the Acquisition Process*, 2005 (co-site analysis framework). (standard; cited, not read)
7. ITU-R Recommendation SM.337, *Frequency and distance separations* (≥ 10λ validity of the free-space isolation formula, as cited in [1]). (standard; via [1])
8. `tools/verify/rf2_cosite.py` (this KB).
