---
title: Shielding and isolation on RF boards — shield cans and their cavity resonances, seams and apertures, absorbers, compartments, filtering at can walls, isolation budgets, and shielding beyond the board (enclosure doors and gaskets, wire meshes and RF fabrics vs frequency, Faraday boxes, testing a DIY cage with an SDR)
domain: 13-pcb-rf-layout-emc
slug: shielding-and-isolation
tags: [shield-can, board-level-shielding, cavity-resonance, TM110, Q-factor, absorber, gasket, seam, aperture, shielding-effectiveness, compartment, feedthrough, ferrite-bead, pi-filter, isolation-budget, PA-LNA-isolation, GNSS-coexistence, desense, enclosure, gasket, finger-stock, wire-mesh, screen, RF-fabric, sheet-resistance, Faraday-cage, Faraday-bag, microwave-oven, SDR-SE-test]
prerequisites:
  - ../02-electromagnetics/waveguides-and-cavity-resonators.md
  - grounding-and-return-paths.md
  - vias-stitching-fencing.md
related:
  - rf-layout-rules.md
  - emc-emi-fundamentals.md
  - mixed-signal-layout.md
  - power-distribution-decoupling-for-rf.md
  - ../04-real-components-hf/ferrites-and-beads.md
  - ../07-noise-linearity/dynamic-range-sfdr-blocking.md
  - ../17-test-measurement/bench-measurement-recipes.md
  - ../17-test-measurement/interference-hunting-and-rf-immunity.md
  - ../08-antennas/slot-antennas.md
level: mixed
confidence: medium
last_updated: 2026-10-13
---

# Shielding and isolation on RF boards

## Questions this page answers
- When do I need a shield can on an RF board, and what does it really buy me?
- At what frequency does my shield can resonate, and why can a can make coupling worse?
- How many solder points does a can fence need, and how big can holes/slots be?
- What do RF absorber sheets do inside a can?
- How do I get signals and power in and out of a shielded compartment without leaking RF?
- How much isolation do I need between a PA and an LNA, or between my LoRa transmitter and my GNSS receiver?
- Do any LoRa harmonics land in the GNSS L1 band?
- How much does a window screen, hardware cloth or chicken wire shield at 433 MHz, 915 MHz or 2.4 GHz?
- Are RF-shielding fabrics and Faraday bags as good as metal?
- Why does a phone still ring inside my home-made Faraday box (or a microwave oven)?
- How do I gasket an enclosure door or lid, and how many screws does it need?
- How do I measure the shielding of a DIY cage or box with an SDR?

## TL;DR
- **A shield can is a metal box over a ground-plane floor — i.e. a cavity.** Its lowest mode (TM110, E vertical) is at $f_{110}=\frac{c}{2}\sqrt{a^{-2}+b^{-2}}$: **10 × 10 mm ≈ 21 GHz, 30 × 20 mm ≈ 9.0 GHz, 50 × 40 mm ≈ 4.8 GHz, 80 × 50 mm ≈ 3.5 GHz, 100 × 60 mm ≈ 2.9 GHz** (checked with an FD eigen-solver to 0.02 %; script §1). The PCB floor lowers these by only 2–4 %. Keep cans small enough that $f_{110}$ is well above every frequency inside (including harmonics).
- **Q of a can mode is high** (≈ 400–800 for tin-plated/nickel-silver cans; the FR-4 floor limits it) — at resonance any two things inside couple strongly. A lossy absorber sheet drops Q to ≈ 5–30, i.e. ≈ 15–25 dB less coupling at resonance (script §2).
- **Seams and holes set the shielding**: a slot of length ℓ < λ/2 gives $SE\approx20\log_{10}(\lambda/2\ell)$ — solder points 5 mm apart leave ≈ 22 dB at 2.45 GHz, 30 dB at 915 MHz; 1 mm vent holes ≈ 44 dB at 915 MHz, 36 dB at 2.45 GHz (script §3). Commercial two-piece tin-plated cans are specified at up to ≈ 60 dB from 0.5 to 3 GHz [1].
- **The can is only as good as its floor**: the fence must be soldered to a GND ring stitched to L2 with vias at ≤ λ/20 (≈ 2–3 mm at 2.4 GHz); traces leaving the can must run on an inner layer under the fence or pass through filters ([vias](vias-stitching-fencing.md)).
- **Filter every line crossing the wall**: a C–bead–C π gives tens of dB at UHF in a 50 Ω model (practical ceiling ≈ 40–60 dB set by stray coupling); pick the capacitor so its self-resonance sits near the frequency you must block (100 pF near 800 MHz, 10 pF near 2.5 GHz) (script §4).
- **Beyond the board** ([§ enclosures](#enclosures-doors-meshes-and-fabrics), `s16_mesh_shielding.py`):
  - **Material is almost never the limit.** Kitchen foil gives > 114 dB at 433 MHz; a 0.05 Ω/sq fabric 71.5 dB.
  - **Meshes lose ≈ 20 dB/decade.** Insect screen: 53 / 46 / 38 dB at 433 / 915 / 2450 MHz. Chicken wire: 15 / 9 / 3 dB.
  - **Seams and cables set the real SE.** Lid contacts every 50 mm leave only 17 dB at 433 MHz and 4 dB at 1.8 GHz.
  - That is why a phone, which needs 44–74 dB of attenuation to lose its downlink, still rings in a cookie tin.
- **Isolation budgets**: e.g. a 2 W 433 MHz downlink and a GNSS receiver: with ≈ 20 dB antenna-to-antenna coupling and ≈ 40 dB of GNSS front-end rejection at 433 MHz, the 433 MHz carrier reaches the LNA at ≈ −27 dBm — ≈ 17 dB below a −10 dBm P1dB (assumed values; script §5). **No harmonic of 433.125, 868, 915 or 920 MHz falls within ±60 MHz of GNSS L1** — the threats are LNA compression, broadband PA noise and digital harmonics ([mixed-signal](mixed-signal-layout.md)).

## Intuition (no math)
Shielding is about closing the paths that energy uses to get from where it is generated to where it hurts. There are three families of path: **through the air** (near-field coupling between parts, antennas, traces), **through the board** (shared ground impedance, plane-pair cavities, supply lines) and **through wires** (cables, supply rails and signal lines that pass from one region to another). A shield can addresses the air path for everything under it — but only if its floor (the board ground) is continuous and well stitched, and if the wires leaving it are filtered. Otherwise the energy simply walks out along the wires or through the seams.

A metal box also *stores* energy. At the frequencies where the box is half a wavelength across, it becomes a resonator with high Q, and a small amount of energy injected by one circuit can build up a large field that couples into another circuit in the same box. That is why a too-large can over a mixed RF/digital area can make things worse, and why absorber sheets (lossy magnetic/carbon-loaded elastomers) are glued inside lids: they don't block anything, they lower the Q.

**Compartmentalisation** — separate cans (or a multi-cavity can) for PA, LNA/RX, synthesiser/LO and digital — plus distance and via fences on the board, is the standard way to reach 60–80 dB of isolation between blocks.

## The math

### Level 1 — cavity modes of a can
With the can lateral dimensions $a\times b$ and height $d$ (to the ground plane), the modes are
$$f_{mnp}=\frac{c}{2\sqrt{\varepsilon_{eff}}}\sqrt{\left(\frac ma\right)^2+\left(\frac nb\right)^2+\left(\frac pd\right)^2}.$$
For thin cans ($d\ll a,b$) the lowest modes are TM$_{mn0}$ (E vertical, uniform in height), $m,n\ge1$. Script §1:

| Can (mm) | f110 | next modes |
|---|---|---|
| 10 × 10 × 2 | 21.2 GHz | 33.5, 33.5, 42.4 |
| 20 × 15 × 2.5 | 12.5 GHz | 18.0, 21.4, 24.6 |
| 30 × 20 × 3 | 9.01 GHz | 12.5, 15.8, 16.8 |
| 50 × 40 × 4 | 4.80 GHz | 7.07, 8.07, 9.60 |
| 80 × 50 × 5 | 3.54 GHz | 4.80, 6.28, 6.37 |
| 100 × 60 × 20 | 2.91 GHz | 3.90, 5.14, 5.22 |

A 2-D finite-difference eigen-solution of the transverse problem reproduces the analytic values within 0.02 %, and the 50 × 40 mm case matches the [cavity page](../02-electromagnetics/waveguides-and-cavity-resonators.md). The PCB prepreg under the can (E vertical → series mix) gives $\varepsilon_{eff}$ = 1.08 for a 2 mm can over 0.21 mm FR-4 — modes 3.7 % lower; components inside lower them further.

### Level 2 — Q and absorbers
The stored energy of TM110 in an $a\times b\times d$ box is $W=\varepsilon_0E_0^2abd/8$; the wall loss integrates $\tfrac12R_s|H_t|^2$ over lid, floor and side walls with $R_s=\sqrt{\pi f\mu_0/\sigma}$. For a thin box the lid/floor dominate and $Q_{walls}\sim d/\delta_s$ (script: ratio 0.79 for a copper 30 × 20 × 3 mm box). The FR-4 floor adds $1/Q_d\approx q\tan\delta$ with filling fraction $q$ ≈ 0.07–0.1. Script §2:

| Can | f110 | walls | Q_walls | Q_floor | Q |
|---|---|---|---|---|---|
| 30 × 20 × 3 mm | 9.0 GHz | nickel silver (σ ≈ 3.5 MS/m) | 834 | 763 | ≈ 400 |
| 30 × 20 × 3 mm | 9.0 GHz | tin (≈ 8.7 MS/m) | 1315 | 763 | ≈ 480 |
| 50 × 40 × 4 mm | 4.8 GHz | nickel silver | 870 | 1001 | ≈ 465 |

Coupling between two probes (parts, traces) in a cavity near resonance scales ∝ Q; an absorber that brings Q from ≈ 400 to ≈ 20 lowers resonant coupling by ≈ 26 dB, while doing little away from resonance.

### Level 3 — seams, apertures and wall feed-throughs
**Slots.** A slot of length ℓ (the longest dimension matters, not the area) radiates like a slot antenna; for ℓ < λ/2 its shielding effectiveness is ≈ $20\log_{10}(\lambda/2\ell)$ (Ott) [2]; N similar apertures in close proximity reduce SE by between $10\log N$ and $20\log N$. Script §3:

| Slot | 433 MHz | 915 MHz | 1.575 GHz | 2.45 GHz | 5.8 GHz |
|---|---|---|---|---|---|
| 1 mm | 51 dB | 44 dB | 40 dB | 36 dB | 28 dB |
| 5 mm | 37 dB | 30 dB | 26 dB | 22 dB | 14 dB |
| 10 mm | 31 dB | 24 dB | 20 dB | 16 dB | 8 dB |
| 20 mm | 25 dB | 18 dB | 14 dB | 10 dB | 2 dB |

Holes deeper than wide add waveguide-below-cutoff attenuation ≈ 32 dB per unit depth/diameter (circular TE11), negligible for thin can walls (0.2 mm wall, 1 mm hole: +6 dB).

**Feed-throughs.** Every conductor crossing the wall is an antenna that carries RF out (or in). Filter it at the wall: shunt C to the can's ground ring, series ferrite bead or inductor, and optionally a second shunt C (π). In a 50 Ω model (script §4):

| Filter | 433 MHz | 915 MHz | 1.575 GHz | 2.45 GHz |
|---|---|---|---|---|
| shunt 100 pF (ESL 0.4 nH) | 20 dB | 33 dB | 19 dB | 13 dB |
| shunt 10 pF | 2 dB | 6 dB | 13 dB | 37 dB |
| bead 600 Ω @ 100 MHz | 18 dB | 18 dB | 18 dB | 18 dB |
| π 100 pF–bead–100 pF | idealised 68 dB | 95 dB | 66 dB | 55 dB |

Lumped values above ≈ 50–60 dB are not achievable in practice: stray coupling around the filter and the ground via inductance cap real feed-through filtering at ≈ 40–60 dB. Choose capacitor values so their self-resonance (≈ 800 MHz for 100 pF, ≈ 2.5 GHz for 10 pF with 0.4 nH) sits near the frequency to block, or parallel two values (checking the anti-resonance — [capacitors](../04-real-components-hf/capacitors-at-rf-mlcc.md)).

## Design equations & rules of thumb

| Item | Rule | Value |
|---|---|---|
| Can first mode | $f_{110}=\frac c2\sqrt{a^{-2}+b^{-2}}$ | keep > 2× highest internal frequency incl. harmonics |
| Can Q | ≈ 400–800 (bare); 5–30 with absorber | coupling at resonance ∝ Q |
| Slot / seam SE | $20\log(\lambda/2\ell)$, ℓ < λ/2 | solder pitch ≤ λ/20 → ≥ 20 dB/seam |
| Multiple apertures | −10…−20 log N | vents: many small holes |
| Fence ring stitching | vias ≤ λ/20 | 2–3 mm at 2.4 GHz |
| Feed-through filter | C (to ring) + bead/L + C | 40–60 dB practical |
| Commercial two-piece can | up to ≈ 60 dB, 0.5–3 GHz | Würth WE-SHC [1] |
| Antenna–antenna isolation (small device) | ≈ 20 dB with careful placement | u-blox [3] |
| Thin sheet / fabric | $SE=20\log(1+\eta_0/2R_s)$ | 0.05 Ω/sq → 71.5 dB |
| Wire mesh | $\lvert T\rvert\approx(2a/\lambda)\ln(a/2\pi r)$; −20 dB/decade | insect screen 46 dB @ 915 MHz |
| Screw-only lid | $20\log(\lambda/2s)$, 0 for s ≥ λ/2 | 50 mm: 17 dB @ 433 MHz |
| Gasketed, overlapping lid + bulkheads | 60–100 dB | vendor-typical |
| SDR SE test range | $P_{ref}-(N_{bin}+10)$ | 113 dB with 100 Hz bins at 1 m, 0 dBm |

## Worked examples

### 1. Can over an SX1262 +22 dBm front end
The front end (chip, PA match, filters, switch, crystal) fits in 20 × 15 mm; can height 2.5 mm: $f_{110}$ = 12.5 GHz — above the 10th harmonic of 915 MHz (9.15 GHz), fine. A 50 × 40 mm can over the whole radio + MCU would resonate at 4.8 GHz — near the 5th harmonic (4.6 GHz) of 915 MHz and inside the 5.8 GHz band — avoid, or split into compartments / add absorber. TI likewise recommends a fully enclosed shield for 20 dBm 2.4 GHz designs to suppress 2nd/3rd harmonics and suggests EM-simulating the cavity [4].

### 2. How many solder joints on the can fence?
A snap-on can over a two-piece frame soldered at points every 5 mm: 30 dB per seam at 915 MHz, 22 dB at 2.45 GHz. For ≥ 40 dB at 2.45 GHz the seam gap must be ≤ 0.6 mm — i.e. a continuous solder fillet (one-piece, seamless cans) [1]. On the PCB side, the fence's GND ring must be stitched to L2 with vias at ≤ 2–3 mm.

### 3. GNSS coexistence with the 433 MHz 2 W downlink (primary FC architecture)
Carriers: 433.125 MHz × n = 866, 1299, 1733 MHz … — no harmonic within 60 MHz of L1 (1575.42 MHz); 915/920 MHz: 1830/1840 MHz — also clear (script §5). Remaining threats:
1. **Fundamental blocking/compression**: 33 dBm − ≈ 20 dB antenna coupling (on a small rocket the two antennas may be < 0.5 m apart) = +13 dBm at the GNSS antenna port. An active GNSS antenna's pre-filter (often a SAW, tens of dB at 433 MHz — check its data) and the module's own SAW/notch (u-blox MAX-M10S integrates both [3]) must bring this to below the LNA's compression; with 40 dB of rejection: −27 dBm, ≈ 17 dB margin to an assumed −10 dBm P1dB. **Check the actual module/antenna out-of-band immunity table.**
2. **Broadband PA noise and spurs** at 1575 MHz from the transmitter itself (the E22's PA noise floor at 1.1 GHz offset) — needs the TX harmonic/low-pass filter and physical separation.
3. **EOS/damage**: u-blox warns that nearby transmitters can exceed RF_IN's maximum input [3] — keep the GNSS antenna away from the TX antenna's near field.

### 4. Isolation between a PA and its own receiver (TDD LoRa)
A +30 dBm module in TX with the RF switch in TX position; the LNA input sees the switch isolation (≈ 20–30 dB for low-cost switches) — +0 to +10 dBm at the LNA, which is why the switch and LNA are rated for it. For a *separate* receiver on the same board (e.g. a second LoRa radio in another band) the budget is: required isolation = P_TX − (receiver max input or blocking level). EBYTE rates its modules' damage/blocking input at ≈ 10 dBm; to stay 10 dB below that from a 33 dBm neighbour you need ≥ 33 dB of antenna + filter isolation ([LoRa modules](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)).

## Enclosures, doors, meshes and fabrics
*Added 2026-10-13 (W5-S16, G-13-04). Numbers from `tools/verify/s16_mesh_shielding.py`. [Bench R5](../17-test-measurement/bench-measurement-recipes.md) covers building a shielded test box for conducted tests; [slot antennas Example 5](../08-antennas/slot-antennas.md) shows a seam resonating as an antenna.*

### Intuition — three leak paths, and the worst one wins
A box, a cage or a bag leaks through three paths:
- **through the material**: a wall, mesh or fabric;
- **through openings**: seams, doors, vents, the gaps between screws;
- **along penetrations**: every cable, connector and shaft.

The total is roughly set by the leakiest path. Solid metal, even household foil, is a superb shield at radio frequencies. Real enclosures reach only 20–60 dB because of seams and cables, rarely because of the metal. So the design order is: **close the seams, filter the penetrations, and only then worry about the material.**

### Level 1 — solid sheets and fabrics
For a thin conducting sheet (thickness ≪ skin depth) of sheet resistance $R_s$ (Ω/sq), in a plane wave:
$$SE = 20\log_{10}\!\left(1+\frac{\eta_0}{2R_s}\right).$$
This follows from treating the sheet as a shunt resistance $R_s$ across a line of impedance $\eta_0$, which gives $T=2R_s/(2R_s+\eta_0)$. It does not depend on frequency until the sheet becomes thicker than a skin depth (then absorption adds $8.686\,t/\delta$ dB) or its weave openings start to act as apertures.

| Material | $R_s$ | SE (far field) |
|---|---|---|
| Ni/Cu-plated ripstop shielding fabric (good) | 0.01–0.05 Ω/sq | 72–86 dB |
| typical conductive fabric / Faraday-bag cloth | 0.1–0.5 Ω/sq | 52–66 dB |
| poor or worn silver fabric | 1 Ω/sq | 45 dB |
| conductive paint, ITO film | ≈ 10 Ω/sq | 26 dB |
| 16 µm kitchen aluminium foil (σ 3.5 × 10⁷ S/m) | — (thick) | > 114 dB at 433 MHz, > 126 dB at 915 MHz (A + R, Schelkunoff) |

The fabric $R_s$ ranges are typical vendor values (from knowledge). Read the actual sheet resistance or SE curve on the data sheet. Fabrics lose SE where they are folded, abraded or washed. The seam or roll-top closure of a bag usually limits it long before the cloth does.

### Level 2 — wire meshes and screens (derivation and table)
A square mesh of thin wires with pitch $a$ and wire radius $r$, with $a\ll\lambda$ and $r\ll a$, acts on a normally incident wave as a shunt **inductive** sheet. Its reactance is the strip-grating result (Marcuvitz) with strip width $w=4r$ [9][10]:
$$\frac{X}{\eta_0}=\frac a\lambda\ln\csc\frac{\pi w}{2a}\;\approx\;\frac a\lambda\ln\frac{a}{2\pi r},\qquad |T|=\left|\frac{2jX}{\eta_0+2jX}\right|\approx\frac{2a}{\lambda}\ln\frac{a}{2\pi r}.$$
Consequences:
- **SE falls 20 dB per decade of frequency** (script check: 20.0 dB).
- SE improves only logarithmically with thicker wire, but linearly with a finer pitch.
- The log form fails for fat wires: below $a/2\pi r\approx1.5$, use the csc form.

| Mesh (a, wire Ø) | 100 MHz | 433 MHz | 915 MHz | 1.8 GHz | 2.45 GHz | 5.8 GHz |
|---|---|---|---|---|---|---|
| fine brass 100/inch (0.25 mm, 0.1 mm), csc form | 100 dB | 88 | 81 | 75 | 73 | 65 |
| insect screen (1.5 mm, 0.28 mm) | 65 | 53 | 46 | 40 | 38 | 30 |
| ¼-inch hardware cloth (6.35 mm, 0.64 mm) | 46 | 34 | 27 | 21 | 19 | 11 |
| chicken wire (≈ 25 mm, 0.7 mm) | 28 | 15 | 9 | 5 | 3 | 1 |

For one insect-screen *hole*, the KB's single-aperture rule $20\log(\lambda/2g)$ gives 62/49/43/37/34/27 dB, within ≈ 3–4 dB of the sheet formula. These are ideal numbers. Real meshes lose SE in three ways:
1. **Unbonded wire crossings.** Woven, unsoldered meshes corrode at the crossings and then behave like parallel wires for one polarisation, which leaks badly. Use welded, soldered or galvanised-after-weaving mesh.
2. **Edge bonding.** The mesh must be bonded continuously to the frame, by solder, clamp strip or conductive tape. Otherwise the gap around the edge is the aperture.
3. **Low-frequency magnetic fields** (kHz, near a transformer) pass through meshes and thin sheets. That needs steel or mu-metal, and thickness.

### Level 3 — doors, lids and gaskets
A lid that touches only at screws behaves like a row of slots, each as long as the screw pitch $s$: $SE\approx20\log_{10}(\lambda/2s)$, falling to 0 dB when $s\ge\lambda/2$ (Level 3 above; [Ott ch. 6](#sources)).

| Contact spacing | 433 MHz | 915 MHz | 1.8 GHz | 2.45 GHz | 5.8 GHz |
|---|---|---|---|---|---|
| 5 mm | 37 dB | 30 | 24 | 22 | 14 |
| 25 mm | 23 | 16 | 10 | 8 | 0 |
| 50 mm | 17 | 10 | 4 | 2 | 0 |
| 100 mm | 11 | 4 | 0 | 0 | 0 |

Getting ≥ 40 dB at 2.45 GHz from screws alone needs a pitch of < 1 mm, which is impossible. That is what gaskets are for. They turn the seam into a continuous, many-point contact. Typical product classes, with vendor-typical SE ranges (from knowledge, check the data sheet) [11]:

| Gasket | Typical SE | Notes |
|---|---|---|
| beryllium-copper or stainless finger stock | 60–100+ dB | doors and frequently opened lids; wipes oxide; needs a clean, plated land |
| conductive elastomer (Ag/Al-, Ni/C-filled silicone) | 60–120 dB | also an environmental seal; needs the right compression (≈ 10–25 %) and galvanic compatibility |
| fabric-over-foam | 60–100 dB | low closure force; cheap; for covers that are rarely opened |
| knitted wire mesh (Monel, tin-plated steel) | 40–100 dB | robust; poor as a weather seal |
| copper tape with conductive adhesive | 20–60 dB | the DIY fix; the adhesive's contact resistance limits it, so solder or clamp the edges |

**Design rules for a ground-station or test box:**
- Use a lid that **overlaps** the wall by ≥ 10 mm (the overlap acts as a waveguide-below-cutoff seam).
- Put gaskets in a groove, and place screws at ≤ λ/20 of the highest frequency of concern.
- Give the contact faces a conductive finish: tin or nickel plating, or chromate/alodine conversion on aluminium. **Not anodised** (anodising is an insulator) and **not painted**.
- Every cable through the wall needs a **bulkhead connector bonded 360°** to the wall (coax), a **feed-through capacitor or filtered connector** (DC and slow I/O), or **fibre** (data). One unfiltered wire carries common-mode current straight through any SE.
- Vents should be honeycomb or long tubes: waveguide below cutoff, ≈ 32 dB per diameter of depth.

### Why a phone still rings in a "Faraday box" (and sometimes in a microwave oven)
- **What blocking needs.** To lose service, the downlink must fall below the phone's working limit, assumed here ≈ −124 dBm RSRP (handset-dependent, roughly −120 to −130 dBm).
  - In good coverage, RSRP ≈ −60 to −80 dBm, so the box needs **44–64 dB, or 54–74 dB with margin**.
  - On the uplink, the phone raises its power to compensate, up to ≈ 23 dBm.
- **What a box gives.** A biscuit tin whose lid touches every 30–60 mm gives about **17–11 dB at 700 MHz, 9–3 dB at 1.8 GHz and 6–0 dB at 2.6 GHz**. A single long gap gives less. Wrapping in foil fails at the overlap seam for the same reason. A Faraday bag with a sloppy roll-top closure is limited by the closure.
- **Microwave ovens.** The door seal is a resonant λ/4 choke designed for 2.45 GHz. It meets the oven's leakage limit at 2.45 GHz, but it is not designed to block cellular bands at 0.7–2.1 GHz. Some phones keep service inside, so **an oven is not a shielded enclosure** (physical reasoning; not measured here). Never run an oven as a test chamber.
- **The cure is the Level 3 list:** a gasketed overlapping lid, no penetrations, and a measured result.

### Test recipe — measuring a DIY cage or box with an SDR
Equipment: an SDR (RTL-SDR or better) and a small antenna outside; a **battery-powered CW source** inside. Suitable sources:
- an SX126x board in `SetTxContinuousWave` at 0 dBm;
- a NanoVNA's port 1 in zero-span/CW with a short whip;
- a phone, for cellular bands, *receive-only*, read through its field-test-mode RSRP.

Inside a closed box, a low-power CW source is not a radiated emission problem. With the lid open, stay inside the band limits ([Singapore rules](../19-regulations-safety/singapore-imda-rules.md); 433.05–434.79 MHz at ≤ 10 mW e.r.p.), or work at 0 dBm in a short burst.

1. **Geometry.** Put the box on a non-metallic table and the SDR antenna 1 m away. That is far field at 433 MHz, where $\lambda/2\pi$ = 11 cm. Mark the positions. The source runs on its own battery, with **no cable through the wall**.
2. **Reference (lid open).** At 0 dBm the SDR receives ≈ −25 dBm, which overloads an RTL-SDR (≈ −40 dBm). Insert a calibrated **30 dB pad** at the SDR and record the reading.
3. **Closed lid.** Remove the pad, close the lid and record the reading. **SE = (reference − closed) + 30 dB.** This attenuator substitution keeps the SDR in the same gain state for both readings, so its non-linearity cancels.
4. **Dynamic range.** With RTL-SDR NF 5.4 dB at 437 MHz (canonical) and a 10 dB SNR requirement, the measurable SE is ≈ **103 dB in 1 kHz FFT bins and 113 dB in 100 Hz bins**. Do not go below ≈ 100 Hz: a 1 ppm TCXO drifts 434 Hz. Use peak-hold over several sweeps.
5. **Repeat** for 4 orientations of the box (seams are polarised) and at least 3 frequencies (433 MHz, 915/920 MHz, 1.5–2.4 GHz if the source allows). Report the *worst* value. Also measure **with each cable in place**, because the cables usually set the final number.
6. **Sanity check.** Put the source in a known-good die-cast box. If you "measure" 120 dB, you are reading the SDR's own leakage or the noise floor, not the box.
7. **Reverse test (optional).** Put the SDR inside, logging on a Raspberry Pi with its own battery, and use an outside source. By reciprocity the result should agree within a few dB.

Expected results: a cookie tin gives 10–30 dB; a die-cast box with an overlapping lid but no gasket 30–60 dB; the same box gasketed with bulkhead feed-throughs 60–100 dB ([bench R5](../17-test-measurement/bench-measurement-recipes.md) quotes the same ranges).

## Practical notes
- **Choose can size first**, then place parts; two-piece (frame + lid) cans allow rework and probing. Tin-plated steel is solderable and cheap; nickel silver (Cu-Ni-Zn) is more corrosion-resistant. Plastic-cased oscillators and sensors can also sit under cans [1].
- **Keep the fence footprint continuous** on L1 (GND ring, mask-opened), stitched to L2 every 1–3 mm; route signals that must leave the can on L3/L4 under the fence, with a GND via either side of each crossing.
- **Absorber**: magnetic-loaded (ferrite/iron-silicide) silicone sheets 0.1–1 mm glued inside the lid over the noisiest part; they detune a can very little at UHF and damp resonances at GHz.
- **Gaskets and finger stock** are for enclosures with removable lids (ground station boxes), not for board-level cans.
- **Enclosures, meshes and fabrics (ground-station boxes, test cages, Faraday bags)** are covered in [§ enclosures](#enclosures-doors-meshes-and-fabrics): mesh and fabric SE vs frequency, doors and gaskets, why phones still ring, and an SDR test recipe.
- **In a rocket**: the airframe section (carbon fibre is partly conductive and attenuates RF; fibreglass/Blue Tube is transparent) is not a shield you can rely on; consider the av-bay bulkheads and harness as the "enclosure" and filter every wire that leaves it ([EMC](emc-emi-fundamentals.md), [antennas on rockets](../08-antennas/antennas-on-rockets.md)).
- **Measure isolation** with a VNA between two ports (e.g. PA output and LNA input footprints), or with a signal generator and spectrum analyser; near-field probe the seams with the can on ([test & measurement](../17-test-measurement/_index.md)).

## Common mistakes & misconceptions
- **"A bigger can shields more."** It shields the same and resonates lower.
- **Can fence soldered to an isolated copper ring** (not stitched to L2) — the "shield" floats and radiates.
- **Unfiltered lines through the fence** — the can then just relocates the problem to the wires.
- **Assuming absorber blocks energy** — it lowers Q; blocking comes from metal and filters.
- **Worrying about harmonics landing in L1 from 433/915 MHz** — they don't; worry about the MCU/SD/USB/switcher harmonics instead ([mixed-signal](mixed-signal-layout.md)).
- **"Any metal box is a Faraday cage."** The lid seam sets the SE. A lid touching every 50 mm gives 4 dB at 1.8 GHz.
- **"Chicken wire / a garden cage blocks Wi-Fi and cellular."** 25 mm mesh gives ≈ 3–9 dB at 0.9–2.4 GHz. It works only at HF and low VHF.
- **"The thicker the metal, the better the shield."** Above a few MHz, foil already exceeds 100 dB. Thickness matters only for low-frequency magnetic fields.
- **Painting or anodising contact faces**, and leaving gaskets uncompressed or on a galvanically mismatched surface.
- **Running one unfiltered cable through a shielded box** (USB to the SDR inside, a DC lead). The cable's common-mode current re-radiates outside.
- **Using a microwave oven as a shield or test chamber.** Its choke seal is tuned to 2.45 GHz, it is not a defined enclosure, and it is a high-voltage hazard.
- **Measuring box SE with the SDR overloaded in the reference reading.** Use attenuator substitution so both readings are taken in the same receiver state.

## How to simulate / verify
- `python3 tools/verify/pcb_cavity_modes.py` (≈ 10 s): can modes (with FD eigen-check), dielectric loading, Q budget, slot/aperture SE, feed-through filter insertion loss, and the 433 MHz/GNSS budget and harmonic search.
- openEMS: a can over a board with two probes; plot S21 vs frequency with and without an absorber layer ([openEMS workflow](../16-simulation-tools/openems-workflow.md)).
- Bench: transmit into a dummy load and scan seams with an H-probe; measure receiver desense (sensitivity with and without the TX active) — the system-level isolation check.
- `python3 tools/verify/s16_mesh_shielding.py` (instant): mesh SE by the log and Marcuvitz csc forms, compared with the single-aperture rule; fabric and foil SE; seam table; phone blocking budget; SDR cage-test dynamic range (all checks pass; output `s16_mesh_shielding_output.txt`).
- openEMS: a periodic unit cell (one mesh opening with periodic boundaries) gives the mesh $S_{21}$ directly, which would validate the analytic table and include oblique incidence.

## Open questions / gaps
- Ferrite-bead model in script §4 is a crude R–L‖C fit to "600 Ω at 100 MHz"; replace with a vendor S-parameter model for specific beads ([ferrites](../04-real-components-hf/ferrites-and-beads.md)).
- Absorber Q-reduction numbers (5–30) are typical ranges, not computed for a specific material.
- GNSS antenna/module out-of-band rejection at 433 MHz (40 dB assumed) must be taken from the specific module/antenna data sheets.
- Mesh SE is for normal incidence, perfectly bonded crossings and an infinite sheet. Fabric $R_s$ ranges and gasket SE classes are vendor-typical values from knowledge. The microwave-oven choke behaviour at cellular frequencies is physical reasoning, not a measurement.
- The phone service floor (≈ −124 dBm RSRP) is an assumption, and handsets vary. A field-test-mode measurement inside and outside the box is the direct check.

## Sources
1. Würth Elektronik, WE-SHC shielding cabinets (frame + cover, SMT/THT; tin-plated; SE up to ≈ 60 dB from 500 MHz to 3 GHz; "seamless" versions for higher frequencies) — product pages and distributor summaries (Mouser/DigiKey), and Würth *ABC of Shielding* reference guide. (manufacturer)
2. H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley 2009, ch. 6 (shielding: apertures, seams, multiple apertures, waveguide below cutoff). (textbook; from knowledge)
3. u-blox, *MAX-M5Q Hardware Integration Manual* UBX-13002460 R06, §5.3 (EOS near RF emitters; ≈ 20 dB GPS–GSM antenna isolation achievable in handhelds; in-band jamming from harmonics of displays/MCUs/buses) and MAX-M10S integration manual (integrated SAW + notch; out-of-band immunity table). (app notes)
4. Texas Instruments, SWRA640H (2024) §4.3.1 — fully enclosed shield for 20 dBm 2.4 GHz to reduce 2nd/3rd harmonics; EM-simulate the shield cavity. (app note)
5. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012, §6.3 (rectangular cavity modes and Q). (textbook)
6. C. R. Paul, *Introduction to Electromagnetic Compatibility*, 2nd ed., Wiley 2006, ch. 10 (shielding). (textbook; from knowledge)
7. KB: [waveguides and cavity resonators](../02-electromagnetics/waveguides-and-cavity-resonators.md), [capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md), [ferrites and beads](../04-real-components-hf/ferrites-and-beads.md).
8. Verification script `tools/verify/pcb_cavity_modes.py` (this page).
9. N. Marcuvitz, *Waveguide Handbook*, MIT Rad. Lab. Series vol. 10, 1951, §5.18 (inductive strip grating: $X/Z_0=(a/\lambda)\ln\csc(\pi w/2a)$). (textbook; from knowledge, used for the csc form)
10. K. F. Casey, "Electromagnetic shielding behavior of wire-mesh screens," *IEEE Trans. EMC* 30(3), 298–306, 1988 (wire-mesh sheet inductance $\propto a\ln(a/2\pi r)$; bonded vs unbonded junctions). (peer-reviewed; from knowledge)
11. Ott (ref. 2) ch. 6 and gasket manufacturers' design guides (Parker Chomerics, Laird) — gasket classes, compression, galvanic compatibility, overlap seams, typical SE ranges. (textbook / manufacturer; from knowledge — check the specific data sheet)
12. Verification script `tools/verify/s16_mesh_shielding.py` (W5-S16).
