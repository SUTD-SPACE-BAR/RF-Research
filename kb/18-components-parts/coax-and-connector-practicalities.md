---
title: Coax and connector practicalities — torque, mating cycles, cleaning, adapter loss, SMA vs RP-SMA, U.FL fragility and retention, weatherproofing, crimp vs solder, bend radius, phase-stable and phase-matched cables, NanoVNA cable testing, 75 Ω on 50 Ω, and fake or poor connectors
domain: 18-components-parts
slug: coax-and-connector-practicalities
tags: [coax, connector, sma, rp-sma, u.fl, ipex, mhf-lk, n-type, torque, mating-cycles, connector-care, cleaning, adapter, weatherproofing, self-amalgamating-tape, crimp, solder, semi-rigid, bend-radius, phase-matching, nanovna, tdr, velocity-factor, 75-ohm, rg-6, counterfeit, ground-station, av-bay]
prerequisites:
  - connectors-and-cables-parts.md
  - ../03-transmission-lines-matching/coax-and-cables.md
related:
  - ../13-pcb-rf-layout-emc/connectors-and-launches.md
  - ../03-transmission-lines-matching/time-domain-reflectometry.md
  - ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md
  - ../17-test-measurement/nanovna-librevna-practical.md
  - ../17-test-measurement/vna-fundamentals-calibration.md
  - ../15-lora-ism-radios/ground-station-design.md
  - ../08-antennas/antennas-on-rockets.md
  - sourcing-and-eval-boards.md
level: intro
confidence: medium
last_updated: 2026-10-12
---

# Coax and connector practicalities

> **Scope.** The [connectors-and-cables selection guide](connectors-and-cables-parts.md) says *which* connector and cable to buy, and [coax and cables](../03-transmission-lines-matching/coax-and-cables.md) gives the physics and loss tables. This page covers *handling*: tightening, cleaning, adapting, sealing, assembling, routing, matching and testing, plus the mistakes that cost dB or wreck connectors.

## Questions this page answers
- How tight should an SMA be, and do I really need a torque wrench?
- How many times can I plug a U.FL or an SMA before it wears out?
- How do I clean RF connectors without damaging them?
- How much do adapters cost me?
- Why doesn't my Wi-Fi antenna work on my LoRa module (SMA vs RP-SMA)?
- Why did my U.FL fall off, and how do I keep it on in a rocket?
- How do I waterproof an outdoor SMA or N connection?
- Crimp or solder: which is better for RF connectors? How do I fit an SMA to semi-rigid coax?
- How tightly can I bend coax?
- How do I make two cables phase-matched with a VNA?
- How do I test a cable (loss, velocity factor, faults) with a NanoVNA?
- Can I use 75 Ω TV coax (RG-6) for a 50 Ω scanner or SDR?
- How do I tell good coax and connectors from bad or fake ones?
- How do I mount a LoRa module in a weatherproof box with the antenna outside?

## TL;DR
- **Torque**:
  - SMA brass 0.57 N·m (5 in-lb); stainless SMA and 3.5/2.92 mm 0.9 N·m (8 in-lb); N 1.4–1.7 N·m ([selection guide](connectors-and-cables-parts.md)).
  - Hold the body and **turn only the nut** [2].
  - Finger-tight is not repeatable above about 1 GHz. Over-torque deforms SMA interfaces, especially brass ones, and clone parts.
- **Mating cycles**: U.FL is rated for **30** [1]; SMA, N and BNC for about 500. A U.FL is an *assembly* connector. If every integration test re-plugs it, 30 tests use up its rated life.
- **Cleaning** [2]: low-pressure dry air first. Then, only if needed, a lint-free swab *moistened* (not soaked) with ≥ 99 % IPA, kept off the plastic bead, threads included. Let it dry and inspect. Never use abrasives or water-based cleaners.
- **Adapters**: each costs about 0.05 dB insertion loss plus its mismatch. Three VSWR-1.2 adapters can add **0.34 dB worst-case** mismatch (0.12 dB RSS) (`e10_coax.py`). Every adapter is also a wear point and a phase uncertainty. Calibrate *through* the adapters you will use.
- **RP-SMA** swaps the pin and the socket. Mating an SMA plug to an RP-SMA jack, or the reverse, gives **no centre contact**: the antenna "works" at a metre and fails at range. Look for the centre *pin* vs centre *hole*.
- **U.FL retention** [1]:
  - After mating, the cable tolerates only **2–4 N** of pull (1.13 mm assemblies).
  - Shock rating 735 m/s² (75 g, 11 ms).
  - A 3 g unsupported pigtail at 50 g already loads it with 1.5 N.
  - Remove only with the U.FL-LP-N-2 extraction tool, pulling vertically.
  - In flight: tie the cable down within about 20 mm of the plug and prefer **MHF-LK** locking versions.
- **Weatherproofing**:
  - Use N-type (gasketed) connectors outdoors where you can.
  - Wrap with electrical tape, then butyl/self-amalgamating tape, then UV-stable electrical tape, each layer overlapped by half, with the outer layer shingled so water runs off.
  - Add a **drip loop**, and point connectors downwards.
  - Never leave a bare SMA outdoors.
- **Bend radius**: about 10× OD for repeated flexing, as low as ~2.5× OD once (LMR-400: 102 mm and 25 mm [5]). Kinks show up on TDR as local impedance bumps.
- **75 Ω on 50 Ω**: one interface gives Γ = 0.2, SWR 1.5 and **0.18 dB**. With 50 Ω at both ends the loss ripples between 0 and **0.69 dB** with length (`e10_coax.py`). Cable loss usually matters more, so RG-6 is fine for a receiver.
- **Phase matching**: 1° is **1.27 mm** of VF-0.66 coax at 433 MHz, but only 0.22 mm at 2.45 GHz. Trim using the VNA's S21 phase or delay, at operating temperature, with the cables laid out as installed.

## Intuition (no math)
A coaxial connector is a precision piece of transmission line that you assemble by hand, every time. Its 50 Ω impedance depends on the centre pin sitting at the right depth, the outer contacts touching all the way round, and the dielectric staying centred. Too loose, and contact is intermittent: readings wander and the phase jumps. Too tight, or twisted, and the mating faces deform permanently. Dirt, metal flakes from worn threads, and skin oil sit exactly where the current flows.

Small connectors are small in every sense. A U.FL's grip is a few newtons, and its life is tens of insertions. Treat it as a part that is soldered once and mated a few times, not a test port. Big connectors such as SMA and N are tougher, but each extra adapter adds a reflection, a little loss, another interface that can loosen, and more phase uncertainty.

Outdoors, water is the enemy. A connector that lets water in becomes a lossy, drifting, eventually corroded mess, and water wicks along the braid for metres. Sealing is cheap and reliable. Replacing a cable on a mast is not.

## The math

### Level 1 — the numbers you budget
- Mismatch loss of one interface: $ML = -10\log_{10}(1-|\Gamma|^2)$, with $|\Gamma| = (s-1)/(s+1)$.
- Several small reflections: worst case $|\Gamma| \le \sum|\Gamma_i|$; random phases $|\Gamma| \approx \sqrt{\sum|\Gamma_i|^2}$ ([launch budgets](../13-pcb-rf-layout-emc/connectors-and-launches.md)).
- Length per electrical degree: $\ell_{1°} = VF\,\lambda_0/360$; delay per metre $= 1/(VF\,c)$ (5.05 ns/m at VF 0.66).
- Velocity factor from an open stub: the first S11 resonance (quarter-wave) at $f_1$ gives $VF = 4\ell f_1/c$.
- One-way cable loss from an open- or short-terminated S11: $A = RL/2$.

### Level 2 — derivations

**75 Ω cable between 50 Ω ends.** One interface: $\Gamma = (75-50)/125 = 0.2$, $ML$ = 0.177 dB. With a 50 Ω source and a 50 Ω load the cable is a transformer whose effect depends on its electrical length θ. Its ABCD matrix is $[\cos\theta,\ jZ_c\sin\theta;\ j\sin\theta/Z_c,\ \cos\theta]$:
- At θ = nπ it is transparent: 0 dB.
- At θ = π/2 + nπ it transforms 50 Ω into $75^2/50$ = 112.5 Ω: $|\Gamma|$ = 0.385, 0.69 dB.
- The script sweeps θ and finds a maximum of 0.695 dB, matching the analytic value.

Over a wide receive band the loss ripples between these limits. Compare the cable loss itself: typical RG-6 (foam, 6.9 mm OD) has roughly half the UHF loss of RG-58 (manufacturer tables; not in the KB's fit table). A long run of RG-6 is therefore often *better* for a scanner than a long run of RG-58, despite the mismatch.

**Adapter chains.** Each adapter of VSWR $s$ contributes $|\Gamma_i| = (s-1)/(s+1)$: 0.048 at 1.1, 0.091 at 1.2, 0.111 at 1.25.
- Three VSWR-1.2 adapters: worst case $|\Gamma|$ = 0.27 (0.34 dB mismatch), RSS 0.16 (0.11 dB).
- Insertion loss adds about 0.03–0.1 dB each at UHF (typical quality adapters).
- For a link budget this is small. For measurements it is not: an adapter added *after* calibration shifts S11 phase and magnitude and is not corrected. Calibrate at the plane you use ([VNA calibration](../17-test-measurement/vna-fundamentals-calibration.md)).

**Measuring loss with only one port.** Leave the far end open (or shorted). The wave travels out and back, so $|S_{11}|$ (dB) = −2A. The measurement error comes from the VNA's residual directivity $D$: the measured $|\Gamma_m| = |\Gamma| \pm D$. With $D$ = −30 dB:
- RL 2 dB (A = 1 dB): uncertainty ±0.34 dB in RL, i.e. ±0.17 dB in A.
- RL 20 dB (A = 10 dB): ±2.4 dB.
- Low-loss cables are measured well this way; very lossy or very long ones are better measured on two ports (S21).

**TDR resolution and range on a NanoVNA.** Frequency-domain TDR with span $F$ and $N$ points has time resolution about $1/F$ and an alias-free window of $(N-1)/F$. In cable length that is resolution $VF\,c/(2F)$ and range $VF\,c(N-1)/(2F)$:
- 900 MHz span, 401 points, VF 0.66: 11 cm resolution (before windowing widens it), 44 m range.
- 6 GHz, 1024 points, VF 0.70: 1.7 cm, 18 m.
- Use lowpass mode with a DC-extrapolated sweep for impedance-vs-distance plots ([TDR](../03-transmission-lines-matching/time-domain-reflectometry.md)).

**Phase matching.** Two cables are phase-matched at frequency $f$ when their electrical lengths agree within the tolerance $\delta\phi$, i.e. their physical lengths agree within $VF\lambda_0\,\delta\phi/360$:
- ±1° at 433 MHz on VF-0.66 coax is ±1.27 mm.
- ±1° at 2.45 GHz is ±0.22 mm, finer than you can cut. Trim, then fine-tune with connector selection, or correct in software (a calibration phase offset per channel, [array calibration](../12-phased-arrays/array-calibration.md)).
- Temperature matters: solid-PTFE cables have a phase "knee" near 19 °C ([coax](../03-transmission-lines-matching/coax-and-cables.md)). Match at operating temperature, with the cables laid out the way they will be installed.

### Level 3 — what degrades connectors and cables
- **Wear and contamination.** Plating wears through, and metal flakes from threads collect on the mating face. Contact resistance rises: the U.FL spec allows the centre contact to go from 20 to 25 mΩ over 30 cycles [1]. Above a few GHz, a scratched or dented mating face shows up as a few tenths of a dB of ripple.
- **Pin depth.** If an SMA's centre pin sits too far forward, it can damage the mating jack. Precision 3.5 mm and 2.92 mm instrument ports are routinely *gauged*. A cheap marketplace SMA plug on a VNA port can damage it, so use a "connector saver" adapter on instrument ports and replace the saver, not the port.
- **Water ingress.** Water in foam dielectric raises εr and loss. Wicked into braid it corrodes copper. The symptoms are slow loss increase, SWR drift with weather, and eventually intermittent faults that show on TDR as a lossy region.
- **Flexing.** Repeated bending tighter than the dynamic radius work-hardens the braid and shifts the dielectric. Phase and loss then change with cable position: "the reading changes when I move the cable".

## Design equations & rules of thumb

| Quantity | Rule | Typical value |
|---|---|---|
| SMA torque | brass 0.57 N·m (5 in-lb); stainless 0.9 N·m (8 in-lb) | 8 in-lb wrench for stainless and test ports |
| N torque | 1.4–1.7 N·m | finger-tight is often *under* this; use a wrench outdoors |
| Mating cycles | U.FL 30 [1]; SMA/N/BNC ≈ 500 | plan U.FL re-plugs |
| U.FL pull after mating | 2–4 N (1.13 mm), 1–3 N (0.81 mm) [1] | tie down within ~20 mm |
| U.FL shock | 735 m/s², 11 ms [1] | ≈ 75 g |
| U.FL VSWR | ≤ 1.3 to 3 GHz; ≤ 1.4 (1.13 mm) to 6 GHz [1] | RL ≥ 17.7 dB / 15.6 dB |
| Adapter | ≈ 0.05 dB IL + VSWR 1.1–1.25 | three in a chain: ≤ 0.34 dB mismatch |
| 75 Ω on 50 Ω | one interface 0.18 dB; between 50 Ω ends 0–0.69 dB | cable loss dominates |
| Bend radius | ≈ 10× OD repeated, ≈ 2.5× OD once | LMR-400: 102 / 25 mm [5] |
| Phase per degree | $VF\lambda_0/360$ | 1.27 mm (433 MHz, VF 0.66) |
| VF from open stub | $4\ell f_1/c$ | 1 m RG-58: $f_1$ ≈ 49.5 MHz |
| One-port loss | $A = RL/2$ | accurate when RL ≲ 10 dB |
| NanoVNA TDR | $\Delta d = VF c/2F$; range $= VF c (N-1)/2F$ | 11 cm / 44 m (900 MHz, 401 pts) |

**Connector identification at a glance**:

| You see | It is | Mates with |
|---|---|---|
| Threaded body inside the nut, **pin** in the centre | SMA plug (male) | SMA jack (female) |
| Threaded body inside the nut, **hole** in the centre | RP-SMA plug | RP-SMA jack (pin in the centre) |
| Threads on the outside, **hole** in the centre | SMA jack (female) | SMA plug |
| Threads on the outside, **pin** in the centre | RP-SMA jack | RP-SMA plug |
| 2 mm round snap-on, no threads | U.FL / MHF1 (or W.FL, MHF4 — *not* intermateable) | check height: U.FL 2.4/1.9 mm mated, MHF4 ≤ 1.7 mm |

## Worked examples

**1. Ground-station feeder through a weatherproof box (LoRa 915 MHz).**
- Layout: radio in an IP65 box on the mast, a bulkhead N or SMA jack with an O-ring through the box wall, a 0.5 m LMR-240 jumper to the antenna.
- Loss: LMR-240 is 2.5 dB/10 m at 915 MHz ([coax table](../03-transmission-lines-matching/coax-and-cables.md)), so 0.5 m costs 0.13 dB. Two N connectors add ≈ 0.1 dB.
- Sealing:
  1. Torque the connectors.
  2. Wrap one layer of electrical tape, half-lapped. It protects the connector from the mastic, so the mastic peels off later.
  3. Wrap one layer of butyl/self-amalgamating tape, stretched and half-lapped, extending 25 mm onto the cable jacket on each side.
  4. Finish with two layers of UV-stable electrical tape, half-lapped, the last layer wound *upwards* so its laps shed water downwards.
- Then: drip loop below the connector, box drain hole at the lowest point, and a cable gland (not just a hole) for power.
- Kit vendors sell exactly this butyl-plus-tape system [6]. Avoid acetic-cure (vinegar-smelling) silicone on connectors: it corrodes copper.

**2. Is RG-6 OK for an RTL-SDR ADS-B or scanner antenna?** At 1090 MHz a 15 m run of RG-58 loses about 7.5 dB (extrapolated from the fit in the [coax table](../03-transmission-lines-matching/coax-and-cables.md)). RG-6 has roughly half that. The 75/50 Ω mismatch adds 0–0.7 dB of ripple. RG-6 wins by several dB. Use F-to-SMA adapters, and keep the LNA at the antenna if possible.

**3. Phase-matching four 433 MHz cables for a small array.** Four 1.5 m RG-316 cables (VF ≈ 0.69), target ±2°, i.e. ±2.7 mm.
1. Calibrate the NanoVNA (SOLT) at the ends of its own test cables.
2. Measure S21 phase (or delay) of each cable at 433 MHz.
3. The longest electrically sets the target. Cut the others long, re-terminate, and re-measure. Each 1° is 1.35 mm, and an SMA re-termination itself varies by about a millimetre, so expect two iterations.
4. Record the residual phases and enter them as calibration offsets in software ([array calibration](../12-phased-arrays/array-calibration.md)).

**4. Velocity factor and loss of an unknown reel with a NanoVNA.**
1. Cut exactly 2.00 m and leave the far end open.
2. The first S11 phase crossing through −180° (series resonance, the quarter-wave dip of |Z|) sits at 24.7 MHz, so $VF = 4 \times 2.00 \times 24.7\times10^6/c$ = 0.66: solid PE.
3. With 10 m of the same cable, open-ended, S11 = −8.6 dB at 433 MHz gives A = 4.3 dB, i.e. 43 dB/100 m. Genuine RG-58 (28.7 dB/100 m, [coax table](../03-transmission-lines-matching/coax-and-cables.md)) would read −5.7 dB. The sample is ≈ 1.5× lossier than real RG-58, which suggests copper-clad-steel or aluminium "RG-58-style" cable, or water ingress. Keep the sample short enough that RL stays below about 10 dB, or the directivity error (±0.5 dB at RL 6 dB, ±2.4 dB at 20 dB) swamps the result.
4. Check with TDR for a lossy or wet section.

**5. Fitting an SMA to UT-141 (RG-402) semi-rigid.**
1. Cut square with a tube cutter or fine saw and deburr.
2. Remove the jacket and dielectric to the connector's stated strip lengths. The centre pin must protrude by exactly the specified length.
3. Seat the body on the outer conductor and solder it all the way round (semi-rigid connectors are solder-type), using a heat sink so the PTFE does not swell.
4. Solder or capture the centre contact per the instructions, then check the pin depth with a gauge or against a known-good mate.
5. Verify RL ≥ 20–25 dB up to the use frequency on the VNA, and look for a capacitive dip at the connector on TDR.
- Pre-made hand-formable cables (RG-402HF) avoid most of this.

**6. A U.FL in the av-bay.**
- The GNSS module's U.FL feeds a 100 mm 1.13 mm pigtail to a bulkhead SMA. Pigtail loss: 0.27 dB/100 mm at L1 ([launch page](../13-pcb-rf-layout-emc/connectors-and-launches.md)).
- Retention: 3 g of cable at 50 g of deployment shock is ≈ 1.5 N, against a 2 N limit [1]. Plus harness tension, and the plug comes off.
- Fixes:
  - an MHF-LK locking plug and receptacle pair;
  - a cable tie-down (adhesive pad or cable clamp) within 20 mm of the plug;
  - a strain-relief loop;
  - a drop of approved RTV *beside* (not into) the mated pair, if the vendor allows it;
  - never unplug by pulling the cable: use the U.FL-LP-N-2 tool, pulling vertically [1].

## Practical notes
- **Torque technique**: start the thread by hand (it should spin freely; cross-threading is the usual killer), hold the body still, and turn only the coupling nut to the wrench's break point.
- **Spin, don't twist**: twisting the body grinds the mating faces.
- **Connector savers**: keep a stainless SMA–SMA adapter on every VNA, spectrum-analyser and SDR port you use often. Replace the saver when it wears.
- **Dust caps** on unused ports and cable ends. Store cables coiled loosely, wider than the minimum bend radius.
- **Crimp vs solder**:
  - Crimp connectors with the *right die* for the cable are fast and consistent, and they are the factory standard for RG-58/RG-316/LMR.
  - Solder is better for semi-rigid, and for centre pins in some designs.
  - Problems come from wrong dies, braid strands shorting to the pin, a melted dielectric (too much heat), or a pin set at the wrong depth. Test every self-made cable on the VNA.
- **Judging coax quality**:
  - read the jacket print (type, manufacturer, impedance);
  - look for copper vs copper-clad aluminium or steel (scrape the centre conductor);
  - check braid coverage (visible gaps mean poor shielding);
  - check that foam is uniform and centred;
  - then measure loss and VF of a sample (example 4).
  - Fake or underspec "LMR-400-type" and "RG-58" cable is common on marketplaces ([sourcing](sourcing-and-eval-boards.md)).
- **Fake or poor connectors**: light weight, nickel flashing over brass instead of gold or passivated stainless, loose or off-centre pins, no or rough PTFE bead, thin threads that gall. Buy test-port adapters from reputable distributors, and keep cheap ones for non-critical use.
- **Rotating an edge-launch or right-angle connector** changes nothing electrically if it is a rated part. Do not bend semi-rigid near the connector to "rotate" it.

**Launch-day RF connector checklist** (av-bay and ground station):
1. Every SMA/N joint is torqued and witness-marked with a paint pen, so a loosened nut shows.
2. RP vs standard checked on every antenna-to-radio pair (pin vs hole).
3. U.FL/MHF joints are locked (LK) or tied down within 20 mm. Note the cycle count for each U.FL since assembly.
4. No adapter chains on the flight path: one bulkhead at most between the module and the antenna.
5. Ground-station outdoor joints taped and sealed, with drip loops, and the feeder routed above the bend radius.
6. Quick S11 sweep of each antenna system *as installed*, saved for comparison with the next launch ([NanoVNA](../17-test-measurement/nanovna-librevna-practical.md)).
7. Spare pigtails, a U.FL extraction tool, an 8 in-lb wrench and a roll each of self-amalgamating and electrical tape in the field kit.

## Common mistakes & misconceptions
- **"My antenna fits, so it's the right connector."** RP-SMA and SMA thread together with no centre contact. The system "works" at short range through capacitive leakage, then fails in the field (D3 #412, nRF24 range drop).
- **"Finger-tight is fine."** Not above about 1 GHz for measurements, and not outdoors, where vibration and thermal cycling loosen it.
- **"75 Ω TV coax ruins a 50 Ω scanner"** (D3 #184/#187). The mismatch costs 0.18–0.69 dB, which is usually less than the loss difference in favour of foam RG-6.
- **"U.FL connectors are for testing."** They are rated for 30 cycles [1] and come off with a few newtons of pull. Use an SMA test port or a U.FL-to-SMA adapter, and note that Hirose says that adapter's U.FL side has *lower* retention and is for measurements only [1].
- **"Calibrate at the SMA, then add a BNC/UHF/U.FL adapter for the measurement."** The adapter is not corrected. Calibrate at the final plane ([VNA calibration](../17-test-measurement/vna-fundamentals-calibration.md)).
- **"Silicone sealant makes a connector waterproof."** Acetic-cure RTV corrodes. Silicone over a connector can also *trap* condensation. Use butyl/self-amalgamating tape with an electrical-tape overwrap, or a boot designed for the purpose.
- **"Coiling the excess coax changes the SWR."** A coil changes only the common-mode behaviour (it can act as a weak choke) ([reflections](../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md)). Tight coils below the bend radius, however, can damage the cable.
- **"Phase-matched cables stay matched."** Only at the temperature and layout where they were matched; PTFE has a phase knee near 19 °C.
- **"A multimeter shows a cable is fine."** DC continuity misses water, crushed dielectric and impedance bumps. Use TDR and loss measurements.

## How to simulate / verify
- `python3 tools/verify/e10_coax.py` (output `tools/verify/e10_coax_output.txt`, all checks pass). It covers 75-on-50 Ω single and two-ended mismatch (ABCD sweep), adapter-chain budgets, mm per degree, VF from an open stub, one-port loss with directivity error, TDR resolution and range, the bend-radius ratios, and the U.FL shock and pull checks.
- NanoVNA recipes for cable loss, VF and TDR: [NanoVNA practical](../17-test-measurement/nanovna-librevna-practical.md) and [TDR](../03-transmission-lines-matching/time-domain-reflectometry.md).
- scikit-rf: model a cable plus adapters as cascaded lines with small $Z_0$ deviations, and compare the predicted S11 ripple with the measurement.

## Open questions / gaps
- No calibrated measurement of the KB's own adapters or cables yet. The 0.05 dB/adapter figure is typical, not measured.
- RG-6 loss is not yet in the KB's coax fit table, so the "about half RG-58" figure is a manufacturer-typical value.
- Weatherproofing layer order and direction follow practitioner and kit-vendor practice [6][7]. A primary installation sheet (CommScope/Times) was not retrieved.
- The torque values are from the selection guide's sources (Taoglas, Times, Anritsu, via extracts).
- Not covered: SMP/SMPM blind-mate and board-to-board RF connectors (D2 #413/#439), which belong on the [selection guide](connectors-and-cables-parts.md).

## Sources
1. Hirose Electric, *U.FL Series — Ultra Small Surface Mount Coaxial Connectors* (catalogue/datasheet), via https://media.digikey.com/pdf/Data%20Sheets/Hirose%20PDFs/UFL%20Series.pdf — DC–6 GHz; VSWR per cable; 30-cycle durability; vibration and shock (735 m/s², 11 ms); cable pull limits after mating (2/4/2 N for 1.13 mm, 1/3/1 N for 0.81 mm); extraction with U.FL-LP-N-2, pull vertically; "click" confirms mating; adapter retention note. (datasheet)
2. Keysight, "Connector Care" and "Cleaning RF Connectors" help pages — low-pressure air, ≥ 99.5 % IPA on a moistened (not saturated) lint-free swab, keep alcohol off the bead, clean threads, dry and re-inspect; turn only the nut. https://helpfiles.keysight.com/csg/m9485a/tutorials/connector_care.htm (manufacturer guidance)
3. Anritsu, *RF and Microwave Connector Care* (10100-00031D); Times Microwave, "Connector torque requirements" — torque values as cited in [connectors-and-cables-parts](connectors-and-cables-parts.md). (application notes)
4. This KB: [connectors-and-cables-parts](connectors-and-cables-parts.md) (torque, cycles, RP-SMA, MHF-LK retention 35 N), [coax-and-cables](../03-transmission-lines-matching/coax-and-cables.md) (loss fits, PTFE knee, bend radius), [connectors-and-launches](../13-pcb-rf-layout-emc/connectors-and-launches.md) (U.FL return loss, pigtail loss). (internal)
5. Times Microwave Systems, *LMR-400* datasheet — minimum bend radius 25.4 mm installation / 101.6 mm repeated, OD 10.29 mm (as cited in [coax-and-cables](../03-transmission-lines-matching/coax-and-cables.md)). (datasheet)
6. Times Microwave WK-U and CommScope 221213 universal weatherproofing kits — butyl mastic plus electrical tape multi-layer seal for feeder and antenna connectors (kit descriptions from distributors). (manufacturer product data, secondary)
7. OnAllBands (DX Engineering), "How to Make Your Coaxial Connectors and Cables Weather-Resistant" — stretch-wrap self-amalgamating tape with 50 % overlap, starting before the connector, electrical-tape overwrap. https://www.onallbands.com/how-to-make-your-coaxial-connectors-and-cables-weather-resistant/ (practitioner guide)
8. Forum demand: EEVblog (SMA on UT-141; waterproof SMA; coax quality), groups.io nanovna-users (twisted-pair TDR; phase-matching), RadioReference (TV coax on scanners; RG-6), TTN forum (LoRa module in a weatherproof box), Arduino forum (nRF24 range drop after adding an antenna) — `gaps/D3-forums-youtube.md` rows 68, 69, 72, 148, 150, 152, 184, 187, 315, 412. (forum — anecdotal)
