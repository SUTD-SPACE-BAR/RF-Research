---
title: Antenna matching and baluns — common-mode current, chokes, sleeve and coax baluns, Guanella/Ruthroff, ferrite mixes, measuring CM current
domain: 08-antennas
slug: antenna-matching-and-baluns
tags: [balun, common-mode, choke, ferrite, mix-31, mix-43, mix-61, sleeve-balun, bazooka, coax-balun, guanella, ruthroff, current-balun, voltage-balun, gamma-match, hairpin, feedline-radiation, smd-common-mode-choke, bifilar-choke, coax-choke, choke-placement]
prerequisites: [antenna-fundamentals.md, dipoles-and-monopoles.md, ../03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md, ../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md]
related: [../06-rf-circuits/baluns-and-rf-transformers.md, ../04-real-components-hf/ferrites-and-beads.md, yagi-uda-and-log-periodic.md, pcb-and-chip-antennas.md, antennas-on-rockets.md, antenna-measurement.md, ../13-pcb-rf-layout-emc/emc-emi-fundamentals.md, wire-antennas-hf-random-wire-fan-dipole.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Antenna matching and baluns (antenna side)

## Questions this page answers
- Why does my antenna's SWR change when I touch or move the coax?
- What is common-mode current on a coax, and where does it come from?
- Do I need a balun on a dipole? On a Yagi? On a monopole?
- Current balun vs voltage balun — what is the difference, and which is better?
- How does a λ/4 sleeve ("bazooka") balun work, and how long should it be at 433 or 915 MHz?
- How does a λ/2 coax 4:1 balun match a folded dipole?
- Which ferrite mix should I use (31, 43, 61) and how much choking impedance is "enough"?
- How do I measure common-mode current or the impedance of a choke?
- How are Yagi driven elements matched (gamma, hairpin, T-match)?
- Can I use an SMD common-mode choke (USB-type) on a 433/915 MHz antenna feed?
- Coax wound on a toroid, bifilar wire on a toroid, or coiled coax in air: which choke is best?
- Where along the feeder should the choke(s) go?

## TL;DR
- Coax is really **three conductors** at RF: the centre, the *inside* of the shield, and the *outside* of the shield (skin effect separates the two shield surfaces). Differential (wanted) current flows on the centre and inside of the shield. Connect a balanced antenna (dipole) directly, and the shield-side arm's current partly returns via the **outside of the shield** — **common-mode (CM) current**. The coax then radiates, its length and routing become part of the antenna, and touching it changes the SWR.
- A **current balun / CM choke** puts a large impedance in series with the outside-of-shield path. Rule of thumb (W1HIS): ≥ 1 kΩ, preferably *resistive* (lossy ferrite), and often 3–6 kΩ to cure HF noise problems [2]. Simple divider model: CM fraction ≈ Z_arm/(Z_arm + Z_path + Z_choke) → 500 Ω ≈ 6 %, 1 kΩ ≈ 3.5 % for Z_arm ≈ 36 Ω.
- **Ferrites**: mix 31 (MnZn) best for 1–≈ 300 MHz CM suppression (strongest at HF), mix 43 (NiZn) ≈ 20–250 MHz, mix 61 for VHF/UHF (2 m / 70 cm) [3], [4]. At 433–915 MHz a single snap-on bead gives only ~100–300 Ω; stack several, or use a **λ/4 sleeve**.
- **λ/4 sleeve (bazooka) balun**: a metal sleeve over the coax, shorted to the shield at the top (feed) end and open at the bottom, a quarter-wave long *in the sleeve-to-shield line's medium*: its open end presents a very high impedance to outside-shield current. 433 MHz, air-filled: ≈ 173 mm; over the coax jacket (VF ≈ 0.66–0.8) ≈ 115–140 mm. Narrowband (a few %).
- **λ/2 coax 4:1 balun**: a λ_coax/2 loop of coax between the two sides of a balanced load gives 180° phase and a 4:1 impedance step — the classic feed for a ≈ 200 Ω folded-dipole driven element.
- **Guanella (current) vs Ruthroff (voltage)** transmission-line transformers: current baluns force equal and opposite currents (what an antenna needs); voltage baluns force equal voltages and do *not* suppress CM current into an imbalanced antenna/feed geometry.
- **SMD common-mode chokes** (USB-class, 0805): e.g. Murata DLW21SN211XK2 has Zc = 210 Ω at its 100 MHz rating, ≈ 350–400 Ω at 433 MHz and ≈ 500 Ω at 915 MHz. Its differential-mode series impedance is ≈ 25–60 Ω, which detunes a 50 Ω feed, so they are marginal antenna chokes. Use stacked ferrite, a sleeve, or a printed balun at UHF.
- **Choke construction at HF** (G3TXQ measurements): coax wound on a big 31/43 toroid gives > 2–8 kΩ and stays resistive across HF. Bifilar on stacked 61 cores is comparable at low HF. Air-wound coax coils exceed 4 kΩ only in a narrow band near self-resonance and are reactive.
- **Placement (NEC)**: on a 433 MHz dipole, a 1 kΩ resistive choke *at the feed* cuts shield current by 20 dB. The same choke λ/4 down is worse than no choke, and λ/2 down only partly works. For end-fed wires, see [RF in the shack](wire-antennas-hf-random-wire-fan-dipole.md#rf-in-the-shack-and-where-the-chokes-go-end-fed-wires).
- **Measure**: VNA series-through: Z_choke = 2Z₀(1/S₂₁ − 1); CM current with a clamp-on current probe; quick test — S11 should not change when you grab the coax a metre from the antenna.

## Intuition (no math)
Imagine a dipole fed by coax. The centre conductor drives one arm, the shield drives the other. Inside the coax, the currents on the centre and the inner shield surface are equal and opposite — that is what coax guarantees. But when the shield's inner current reaches the end of the cable, it can go two ways: out onto the dipole arm, or back down the *outside* surface of the shield, which to the RF is just another wire hanging from the feed point. How the current divides depends on the impedances of those two paths. The dipole arm is ≈ 36 Ω-ish (half of 73 Ω); the outside of the shield, running off to the radio and the rest of the world, may present tens to thousands of ohms depending on its electrical length. Wherever that path is low-impedance, a sizeable fraction of the current flows on the feedline: the feedline radiates, the pattern skews, and anything that changes the feedline's path — your hand, a table, the rocket harness — changes the antenna.

A choke is anything that makes the outside-shield path high-impedance without touching the wanted differential current: ferrite around the coax (acts only on the net current through the core, which is the CM current), coiling the coax (an inductor for CM only), or a λ/4 sleeve (a transmission-line trap that looks like an open circuit to outside-shield current).

## The math

### Level 1 — the current divider model (simplified)
Model the feed point as a node where the shield-inner current I_s must split into the arm (impedance Z_arm, roughly half the balanced antenna's input impedance) and the outside-shield path (impedance Z_path, a monopole-like wire of whatever length, plus a choke Z_ch):
$$\frac{I_\text{cm}}{I_s}\approx\frac{Z_\text{arm}}{Z_\text{arm}+Z_\text{path}+Z_\text{ch}} .$$
With Z_arm ≈ 36 Ω and a worst-case (resonant, low-impedance) path Z_path ≈ 20–40 Ω: no choke → ≈ 50 % of the current on the feedline; Z_ch = 500 Ω → ≈ 6 %; 1 kΩ → ≈ 3.5 %; 3 kΩ → ≈ 1.2 %. This is a crude lumped model (the outside-shield path is really a distributed antenna with its own resonances), but it explains why ≈ 1 kΩ is a sensible target and why a *resistive* choke is safer than a high-Q inductive one: a reactive choke can *resonate* with a capacitive feedline path and make things worse, while a resistive one always adds impedance [2].

**Series-through measurement of a choke** (two-port VNA, choke in series between port 1 and port 2, CM path = the cable shield through the ferrite):
$$Z_\text{DUT}=2Z_0\Big(\frac{1}{S_{21}}-1\Big),\quad |S_{21}| = -20\ \text{dB} \Rightarrow |Z| \approx 900\ \Omega,\quad -30\ \text{dB}\Rightarrow \approx 3.1\ \text{k}\Omega .$$

### Level 2 — transmission-line baluns
**λ/4 sleeve (bazooka).** The sleeve and the outer surface of the coax shield form a coaxial line of characteristic impedance Z_s = (η/2π√εr) ln(D_sleeve/D_shield), shorted at the feed end. At the open end the input impedance seen by outside-shield current is
$$Z_\text{in}=jZ_s\tan\beta\ell\;\to\;\infty\ \text{at}\ \ell=\lambda_s/4,\qquad \lambda_s=\frac{\lambda_0}{\sqrt{\varepsilon_{r,\text{fill}}}} .$$
In practice losses and end effects cap it at a few kΩ, and the bandwidth over which |Z_in| > 1 kΩ is a few percent (larger Z_s → wider). The same idea appears as the sleeve of a [sleeve dipole](dipoles-and-monopoles.md#sleeve-coaxial-dipole) and as the printed "λ/4 choke" on some PCB dipoles.

**λ/2 coax 4:1 balun.** Connect the balanced load terminals A and B: A to the coax centre at the feed, and B via an extra length of coax of electrical length λ/2 (so its voltage is inverted). The two halves of the load see voltages +V and −V (total 2V) from a coax at V: the load sees 4× the coax impedance — 50 Ω coax feeds a 200 Ω balanced load. Length: λ₀/2 × VF (e.g. 433 MHz, solid PE RG-58/RG-316 VF ≈ 0.66–0.70: ≈ 229–242 mm). Narrowband; widely used on UHF Yagis with folded-dipole driven elements.

**Pawsey stub / split-sleeve baluns** are variants for 1:1 at a single frequency; **Marchand baluns** (coupled λ/4 lines) are the printed-circuit broadband equivalent — see [baluns and RF transformers](../06-rf-circuits/baluns-and-rf-transformers.md).

### Level 3 — Guanella vs Ruthroff and ferrite physics
- **Guanella (1944) current balun**: one or more transmission lines (bifilar windings or coax) wound on a core; the winding impedance acts only on CM current, the differential mode is a transmission line. A 1:1 Guanella is simply a CM choke; a 1:4 Guanella uses two lines in series/parallel. Equal and opposite currents are forced regardless of load symmetry, up to the limit set by the CM impedance.
- **Ruthroff (1959) voltage balun**: a 1:4 bootstrapped transmission-line transformer that forces equal *voltages* to ground at the balanced port; with a real, imperfectly symmetric antenna and feedline, it lets CM current flow. For antenna feeding, current baluns are preferred (Counselman [2]; Sevick [5]).
- **Ferrite physics**: a ferrite core's complex permeability μ' − jμ'' makes the winding impedance Z = jωL₀(μ' − jμ'') = ωL₀μ'' + jωL₀μ'. Above the material's resonance μ'' dominates — the choke becomes mostly *resistive*, which is what you want for suppression. Mix 31 has high μ (MnZn) and is resistive over most of HF; 43 (NiZn, μi ≈ 800) is lossy from ≈ 20 to 250 MHz; 61 (μi ≈ 125) keeps usable impedance into the UHF range [3], [4]. Details and data: [ferrites and beads](../04-real-components-hf/ferrites-and-beads.md).
- **Power**: a lossy choke dissipates I_cm²R; with a good match and decent balance I_cm is small, but a poor choke on a badly unbalanced antenna at high power overheats (W1HIS reports commercial chokes failing below 1500 W) [2]. At 2 W (E22) this is irrelevant; at 100 W HF it is not.

## Matching the antenna itself (brief)
- **Lumped L/pi networks** at the feed: see [impedance matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md) and the worked example on [pcb-and-chip-antennas](pcb-and-chip-antennas.md#worked-examples).
- **Quarter-wave transformer**: Z_t = √(Z₀Z_A), e.g. 75 Ω coax matches a ≈ 110 Ω antenna to 50 Ω; 60–62 Ω lines match a 72 Ω dipole ([quarter-wave transformers](../03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md)).
- **Yagi driven-element matches**: *hairpin* (shunt inductor across a slightly short, capacitive split dipole; raises a 12–25 Ω feed to 50 Ω; needs a balun), *gamma* (a rod parallel to one half of an unsplit DE, fed from coax via a series capacitor; unbalanced — some CM current is inherent), *T-match* (balanced gamma, needs a balun), *folded dipole* (×4 step-up, [dipoles-and-monopoles](dipoles-and-monopoles.md#level-2--derivations)). The DL6WU designs in our MoM had ≈ 50 Ω with a plain dipole DE (≈ 200 Ω folded), so a 1:1 choke or a 4:1 coax balun respectively ([yagi](yagi-uda-and-log-periodic.md)).

## SMD, coax-wound and bifilar chokes compared

**SMD common-mode chokes (CMCs).** These are two coupled windings on a ferrite chip, sold for USB/HDMI lines. They pass the differential signal and present Zc to common-mode current. Murata DLW21SN series datasheet (typical curves, read from the chart ± 20 %) [8]:

| Part (0805) | Zc rating @ 100 MHz | Zc @ 433 MHz | Zc @ 915 MHz | Peak Zc | DM series Zd @ 433 / 915 MHz |
|---|---|---|---|---|---|
| DLW21SN211XK2 | 210 Ω ± 25 % | ≈ 350–400 Ω | ≈ 500 Ω | ≈ 700 Ω near 2.5 GHz | ≈ 25–30 / ≈ 50–60 Ω |
| DLW21SN491XQ2 | 490 Ω | ≈ 1 kΩ | ≈ 1.2–1.3 kΩ | ≈ 1.3 kΩ near 1 GHz | rises faster than the 211 |

Ratings: 0.36 A and 20 V DC, 0.33 Ω DCR. Using one on an antenna feed:
1. **Choking.** Zc of 0.4–1.3 kΩ at 433–915 MHz is at the bottom of the useful range. The divider model above gives 3–9 % residual CM current. That is about as good as 2–4 large NiZn beads, in 2 × 1.2 mm.
2. **Differential path.** The DM path is not free. Zd (leakage inductance plus the short coupled-line section) is a 25–60 Ω series reactance at UHF, which can turn a 50 Ω match into VSWR 1.5–2.5 at 915 MHz unless it is included in the matching network. Measure the part's S21 in DM, or use the vendor's S-parameter model.
3. **Power and linearity.** At 2 W (E22) the RF voltage is ≈ 14 V peak in 50 Ω, under the part's 20 V DC rating but not by much. Ferrite chips also heat and can generate intermodulation at high power. Do not use them on a PA output above ≈ 1 W without a measurement.
4. **Uses.** They fit naturally on a PCB dipole fed from a differential radio output (no balun needed), or between a board and an off-board balanced antenna. For a coax-fed whip or dipole, a λ/4 sleeve or a printed balun ([06 baluns](../06-rf-circuits/baluns-and-rf-transformers.md)) is more predictable.

**Coax-wound vs bifilar vs air-wound (HF).** From G3TXQ's measured chart [9] (|Z| bands > 0.5/1/2/4/8 kΩ; "resistive" means R > |X|):

| Construction | Where it is a good choke | Character |
|---|---|---|
| 12 turns RG-58 on FT240-31 | > 2 kΩ from ≈ 1.5 to 28 MHz; > 4 kΩ ≈ 3–11 MHz | resistive above ≈ 4 MHz: broadband and safe |
| 17 turns RG-58 on FT240-43 | > 8 kΩ ≈ 3–9 MHz; > 4 kΩ ≈ 2–16 MHz | resistive over most of it; best for 80–20 m |
| 14 turns bifilar on 4 × FT240-61 | > 4 kΩ ≈ 3.5–7.5 MHz; > 1 kΩ to ≈ 28 MHz | partly reactive |
| 6–10 × FB-31 beads on RG-213 | 0.5–2 kΩ across 2–30 MHz | resistive, but low |
| 10 turns RG-58 air-wound on 4.25" | > 4 kΩ only ≈ 16–20 MHz | almost purely reactive; narrow |

- **Coax wound through a ferrite core** keeps the differential signal inside the coax at its own Z₀, so there is no DM impedance error and no voltage-breakdown issue at the winding. The core acts only on the outside-shield (CM) current. It is the default.
- **A bifilar winding** (two insulated wires) makes the DM path a twisted-pair line whose impedance (often 50–100 Ω) and length now matter. It is compact and fine for 1:1 or Guanella 4:1 at HF, but it adds DM loss and mismatch at the upper end, and a voltage-breakdown limit at high power.
- **Air-wound coax coils** ("ugly baluns") are inductors that resonate with their inter-turn capacitance. They only choke near that resonance, and below it they are reactive. A reactive choke can *resonate* with a reactive CM path and increase the CM current. The NEC end-fed model shows exactly this: an inductive 1 kΩ choke made CM 4.5 dB worse.
- **At 433–915 MHz** none of the HF toroids applies. Use NiZn (61, or vendor UHF mixes) beads stacked on thin coax, a λ/4 sleeve, or a printed balun.

## Where to put chokes: a placement rule from NEC

Model: a 433 MHz horizontal dipole (2 mm, 327.9 mm). The coax outer surface is a 5 mm wire hanging vertically from the shield-side feed terminal, the standard "feedline as a third wire" model (`tools/verify/s12_hf_wire_chokes.py` §6).
- **No choke.** The worst coax length (≥ 0.4 m) was 0.50 m (0.72λ). Peak shield current is −9.3 dB relative to the feed current, and the cross-polar (vertical) field at broadside is −14 dB. A 0.15 m coax was as bad (−7.6 dB), while 0.35 m (≈ λ/2 path) and 0.75 m gave −19 dB. CM current depends on cable length, which is why "it worked on the bench" proves little.

Chokes on that 0.50 m coax (peak shield current re feed / cross-pol):

| Choke Z | At the feed | λ/4 down | λ/2 down |
|---|---|---|---|
| 300 Ω resistive | −22.4 / −27.1 dB | −8.2 / −16.0 | −19.7 / −19.4 |
| 1 kΩ resistive | **−29.6 / −33.4** | −6.9 / −15.7 | −19.4 / −19.4 |
| 3 kΩ resistive | −34.3 / −37.2 | −5.8 / −12.2 | −19.3 / −19.3 |
| j1 kΩ (inductive) | −31.5 / −36.2 | −5.2 / −19.8 | −19.0 / −19.9 |
| −j1 kΩ (capacitive) | −30.8 / −36.0 | −8.1 / −10.7 | −19.1 / −18.7 |

The 1 kΩ choke at the feed changes Z_in only from 73.0 + j3.4 to 72.1 + j3.6 Ω, because the dipole itself is undisturbed.

**Placement rule.**
1. **Balanced antennas** (dipoles, Yagi driven elements, loops): the first choke goes **at the feed point**, within ≈ λ/20 of it. A choke λ/4 down the line sits where the shield-current standing wave puts a high-impedance (voltage-maximum) point. It barely changes anything there, and the λ/4 of shield above it is a resonant radiator: in the table, a bigger choke at λ/4 was *worse* (−5.8 dB for 3 kΩ). A choke λ/2 down only partly helps (≈ −19 dB). Where one choke is not enough, add the next ≈ λ/4 further along. On long HF feeders, add one where the coax enters the building, to stop house noise and RF in the shack [2].
2. **Monopoles fed against radials or a counterpoise**: the choke goes just below the ground plane or counterpoise junction, so that the radials, not the coax, are the return path ([dipoles](dipoles-and-monopoles.md#finite-ground-planes-and-small-boards)).
3. **End-fed wires** (EFHW, random wire), where the feed current *is* the counterpoise current: do not choke at the transformer. Define a counterpoise (≈ 0.05–0.1λ of wire, or that length of coax), put a **resistive** choke of several kΩ (≫ the counterpoise's own impedance) where it should end, and a second at the building entry. NEC: the entry choke alone gave −24 dB at the radio ([HF wire page](wire-antennas-hf-random-wire-fan-dipole.md#rf-in-the-shack-and-where-the-chokes-go-end-fed-wires)).
4. **Prefer resistive chokes** (lossy ferrite below and around its μ″ peak) to reactive ones (air coils, ferrite well below its loss region). A resistive choke always reduces the CM current, while a reactive one can resonate with the CM path [2], [9].

## Design equations & rules of thumb

| Item | Rule / value | Note |
|---|---|---|
| Choke target | ≥ 1 kΩ, resistive; 3–6 kΩ for stubborn HF noise | W1HIS [2] |
| CM fraction (lumped) | Z_arm/(Z_arm + Z_path + Z_ch) | order-of-magnitude |
| Series-through | Z = 2Z₀(1/S₂₁ − 1) | VNA two-port |
| λ/4 sleeve length | λ₀/(4√εr,fill) | 173 mm air @433 MHz; 82 mm @915 MHz |
| λ/2 coax 4:1 balun | λ₀·VF/2 | 433 MHz, VF 0.66: 229 mm |
| Ferrite mix | 31: HF (1–300 MHz); 43: 20–250 MHz; 61: VHF/UHF | [3], [4] |
| UHF bead | ~100–300 Ω each at 433–915 MHz (material-dependent) | stack or use sleeve |
| Where | at the antenna feed first (within ≈ λ/20); never a lone choke λ/4 down; more ≈ λ/4 apart or at the building entry | [2], NEC §6 |
| SMD CMC (0805, USB class) | Zc ≈ 0.35–1.3 kΩ at 433–915 MHz; Zd 25–60 Ω (include it in the match) | Murata DLW21SN [8] |
| HF choke | ≥ 10–17 turns coax on FT240-31/43: 2–8 kΩ, resistive | G3TXQ [9] |
| Monopole on a small board | counterpoise/radials *and* a choke on the cable at λ/4 from the feed | [dipoles-and-monopoles](dipoles-and-monopoles.md) |

## Worked examples

**Example 1 — "My 433 MHz dipole's SWR changes when I touch the coax."** Dipole fed directly with RG-316, cable 1.5 m to the radio. The outside of the shield is a 1.5 m (2.2λ) wire; at some points along it there are current maxima, so a hand there (a lossy, grounded-ish dielectric) changes the path impedance and the feedpoint impedance. Fix: 4–6 NiZn (mix 61 or 43) beads right at the feed (≈ 0.6–1.5 kΩ total at 433 MHz, check with the series-through test), or a 173 mm air-spaced (or ≈ 120 mm jacket-filled) λ/4 sleeve. Verify: S11 now stays put when you grab the cable.

**Example 2 — Sleeve balun for a 915 MHz ground-station dipole.** Brass tube 8 mm ID over RG-316 (2.5 mm OD) with the jacket removed under the sleeve and air/PTFE spacing: Z_s ≈ 60 ln(8/2.5) ≈ 70 Ω (air); ℓ = 327.6/4 = 82 mm. Short the sleeve to the shield at the feed end; leave the far end open. Expected |Z| > 1 kΩ over ≈ ±3–5 % (use the MoM or measure).

**Example 3 — 4:1 coax balun for the DL6WU folded-dipole driven element at 433 MHz.** Folded-dipole DE in the array ≈ 200 Ω. Balun: RG-316 (PTFE, VF ≈ 0.69) λ/2 = 346 × 0.69 ≈ 239 mm loop; 50 Ω × 4 = 200 Ω. Tune the DE length for minimum SWR with the balun in place.

**Example 4 — Choke measurement.** Fair-Rite-type mix-61 split bead on RG-58, three passes (a "binocular" arrangement): measured S₂₁ = −18 dB at 433 MHz → |1/S₂₁| = 7.94 → Z ≈ 2·50·(7.94 − 1) ≈ 694 Ω (magnitude; the complex S₂₁ gives R and X). Adding a second bead in series → ≈ 1.4 kΩ.

**Example 5 — Rocket harness.** A 915 MHz whip on the avionics sled fed by 30 cm of coax from the E220 module, with pyro, battery and USB wiring alongside. CM current on the coax and on neighbouring wires couples RF into pyro lines and distorts the pattern. Fix: counterpoise radials (or a sleeve dipole), ferrite at the antenna base, route the coax along the axis away from pyro leads, twist pyro leads, and test the pyro channels with the transmitter keyed ([antennas-on-rockets](antennas-on-rockets.md)).

## Practical notes
- **Put the choke at the feed point.** A choke far down the line leaves the section between feed and choke radiating.
- **Coiled coax chokes** work at HF (a few turns, 10–20 cm diameter) but are poorer at UHF: inter-turn capacitance makes them self-resonate; at 433 MHz a coil can become capacitive — prefer ferrite or a sleeve.
- **Beads on small cable at UHF**: use NiZn material specified for the band (61, or the vendor's UHF suppression mixes); MnZn mix 31 is optimised for HF–low VHF.
- **Monopoles also need care**: an "unbalanced" antenna still drives CM current onto the cable if its ground/counterpoise is inadequate.
- **Balun ratio labels lie**: "1:1 balun" can mean current or voltage type; check the construction.
- **Loss**: a balun adds a few tenths of a dB; a poorly chosen ferrite transformer at high power can add much more and heat.

## Common mistakes & misconceptions
- **"Coax is shielded, so it can't radiate."** The *outside* of the shield carries CM current and radiates like any wire.
- **"A dipole works fine without a balun."** It radiates, but the pattern skews, the feedline radiates and picks up noise, and the impedance depends on the cable routing.
- **"A balun is only for impedance transformation."** Its main job at the antenna is CM suppression; impedance ratio is secondary.
- **"More turns on the ferrite = better at every frequency."** Inter-turn capacitance creates a self-resonance above which the choke impedance falls; choose turns for the band.
- **"Voltage baluns balance the antenna."** They balance voltages, not currents; use current baluns for antennas.
- **"Touching the cable changes the SWR, so the cable is bad."** The cable is fine; the antenna system is using it as a radiator.

- **"Any choke anywhere on the coax helps."** A lone choke λ/4 from the feed can make things worse; the feed point comes first (NEC table above).
- **"A coiled-coax choke is as good as a ferrite one."** It is a narrow, reactive resonator; ferrite-wound coax is broadband and resistive (G3TXQ).
- **"A USB common-mode choke is a UHF balun."** It chokes 0.4–1.3 kΩ but adds 25–60 Ω of DM series reactance at 433–915 MHz; include it in the match or use a sleeve or printed balun.

- **"'Braid breaker', common-mode choke and DC block are the same thing."** A *common-mode choke* (coax through ferrite, coiled coax, bifilar winding) presents high impedance to current on the outside of the shield but passes the differential signal and DC. A *braid breaker* is the TV/EMC term for a device that interrupts the shield path at RF — usually a choke, sometimes a capacitively coupled break. A *DC block* is a series capacitor (inner, outer or both) that stops DC and low-frequency current but does nothing for RF common-mode current. Use chokes for antenna CM problems; place one at the feed point and, if RF still appears in the shack, a second where the line enters the building (D3 #37, #514).

## How to simulate / verify
- `python3 tools/verify/s12_hf_wire_chokes.py` §5–6: choke impedance and position vs CM current and cross-pol, for a 433 MHz dipole and a 40 m end-fed wire (NEC-2, `ld_card` type 4 = fixed R + jX).
- NEC: model the feedline outer surface as a wire from the feed to "ground"/the radio; add a load of the choke's impedance on that wire and compare patterns and CM current with/without the choke ([simulation](antenna-simulation-nec-openems.md)). Our `tools/verify/ant_mom_general.py` supports wires with junctions and series loads (`loads=` argument) for this kind of study.
- VNA: series-through Z of chokes; S11 with/without a hand on the cable; CM current with a clamp-on current probe (a ferrite toroid with a few turns and a detector, calibrated against a known current).
- Field: compare received signal with the ground-station coax moved or rerouted; any change indicates CM current.

## Open questions / gaps
- Quantitative impedance of specific UHF ferrite beads (Fair-Rite 61/44 part numbers) at 433 and 915 MHz should be added from manufacturer curves (domain 04).
- The NEC third-wire models (§6 of `s12_hf_wire_chokes.py`) treat the shield as a bare wire in free space; a real cable run, a radio chassis and a mast shift the worst-case lengths. Measure with a clamp-on probe.

## Sources
1. C. A. Balanis, *Antenna Theory*, 4th ed., 2016 — §9.7 baluns and transformers (bazooka, λ/2 balun), §9.x folded dipole; ARRL *Antenna Book*, 24th ed., ch. on transmission-line coupling and baluns. (textbook / handbook)
2. C. Counselman (W1HIS), "Common-Mode Chokes," YCCC draft, 2006 — ≥ 1 kΩ (often 3–6 kΩ) resistive chokes, ferrite binocular designs, placement, heating of commercial chokes. https://remoteqth.com/img/ZAW-WIKI/cmcc/CommonModeChokesW1HIS.pdf (expert article)
3. Fair-Rite Products, *43 Material Data Sheet* (and 31/61 data sheets) — NiZn/MnZn classes, recommended suppression ranges. https://fair-rite.com/43-material-data-sheet/ (manufacturer data)
4. Palomar Engineers, *Ferrite Mix Selection* — 31/43 for HF chokes, 61 for 2 m/70 cm. https://palomar-engineers.com/ferrite-cores-for-rfi-emi-noise-suppression-mix-31-43-61-75-palomar-engineers/ferrite-cores/ferrite-mix-selection (vendor — practice)
5. J. Sevick, *Transmission Line Transformers*, 4th ed., Noble, 2001; G. Guanella, "Novel matching systems for high frequencies," *Brown-Boveri Rev.* 31, 1944; C. L. Ruthroff, "Some broad-band transformers," *Proc. IRE* 47, 1959. (book / peer-reviewed; cited from general knowledge)
6. TI AN043 — coax placement changes a small antenna's resonance by 5–10 MHz (an example of cable effects). https://www.ti.com/lit/pdf/swra117 (app note)
7. This repository: `tools/verify/ant_mom_general.py` (junction/load-capable wire MoM), `tools/verify/ant_mom_wire.py`, `tools/verify/s12_hf_wire_chokes.py`. (verification)
8. Murata, *DLW21SN211XK2# Product Search Data Sheet* (updated 2026-02-02, DigiKey copy) — Zc 210 Ω ± 25 % at 100 MHz, 0.36 A, 20 V DC, 0.33 Ω; Zc/Zd vs frequency curves for DLW21SN181/211/261/491. https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8880/DLW21SN211XK2L.pdf (manufacturer data; curves read ± 20 %)
9. S. Hunt (G3TXQ), "Common-mode choke impedances" chart, 1–30 MHz (originally karinya.net/g3txq/chokes; PDF mirror https://www.hellschreiber.com/radio/pdf-ant/article-G3TXQ-chokes.pdf) — coax-on-FT240-31/43/61, bifilar on 4 × FT240-61, bead stacks, air-wound coax; resistive vs reactive warning. (expert measurement; READ, values from the chart image)
