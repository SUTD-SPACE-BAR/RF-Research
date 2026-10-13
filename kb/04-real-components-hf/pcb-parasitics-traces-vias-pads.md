---
title: PCB parasitics — traces, vias, pads, plane gaps and ground-return inductance
domain: 04-real-components-hf
slug: pcb-parasitics-traces-vias-pads
tags: [pcb-parasitics, trace-inductance, partial-inductance, loop-inductance, via-inductance, goldfarb-pucel, pad-capacitance, return-path, plane-slot, microstrip, jlcpcb-stackup, ground-via]
prerequisites:
  - ../01-circuit-theory/lumped-elements-impedance-admittance.md
  - ../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md
related:
  - package-parasitics-bondwires.md
  - capacitors-at-rf-mlcc.md
  - inductors-at-rf.md
  - resistors-at-rf.md
  - component-models-s2p-spice.md
  - ../02-electromagnetics/inductance-capacitance-from-fields.md
  - ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md
  - ../13-pcb-rf-layout-emc/grounding-and-return-paths.md
  - ../13-pcb-rf-layout-emc/vias-stitching-fencing.md
  - ../13-pcb-rf-layout-emc/stackups-and-materials.md
  - ../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md
level: mixed
confidence: medium
last_updated: 2026-10-03
---

# PCB parasitics — traces, vias, pads, plane gaps and ground-return inductance

## Questions this page answers
- How much inductance does a PCB trace have — is "1 nH per mm" right?
- What is the difference between partial inductance and loop inductance, and which one matters?
- How much inductance does a via have on a 1.6 mm 2-layer board vs a 4-layer JLCPCB board?
- Does putting more ground vias in parallel keep reducing inductance?
- How much capacitance does a component pad add, and why cut the ground plane under an SMA pad?
- What happens when a trace crosses a gap or slot in the ground plane?
- Why should my shunt capacitor's ground via be right at the pad?
- When can I treat a short trace as a lumped inductor?

## TL;DR
- **Inductance is a loop property.** "nH per mm" numbers are *partial* inductances; the loop (signal + return) inductance is what circuits see. An isolated wire/bondwire is ≈0.7–1 nH/mm (25 µm wire: 0.82 nH for 1 mm); a **trace over a nearby ground plane is much less**: 50 Ω microstrip ≈ **0.31–0.33 nH/mm** and **0.11–0.12 pF/mm** on both a 1.6 mm 2-layer and a JLCPCB 4-layer (0.2104 mm 7628 prepreg) board.
- A short high-impedance line is a series inductor: $L\approx Z_0\ell\sqrt{\varepsilon_{eff}}/c$ (0.49 nH/mm for a 0.15 mm/83 Ω trace on 0.21 mm prepreg — 5 mm ≈ 2.4 nH, exact to 0.5 % at 915 MHz).
- **Via to ground (Goldfarb–Pucel):** 1.6 mm through a 2-layer board, 0.3 mm drill: **0.54 nH** (3.1 Ω at 915 MHz, 8.4 Ω at 2.45 GHz) — the KB design value for a via to a solid plane (the isolated-barrel *partial* inductance is 0.69 nH, and the oft-quoted Johnson & Graham $5.08h[\ln(4h/d)+1]$ gives 1.3 nH, ≈ the loop with a distant return — [inductance from fields](../02-electromagnetics/inductance-capacitance-from-fields.md)); on a 4-layer board to L2 at 0.21 mm: **≈0.015–0.023 nH**. Use a 4-layer stackup with an L2 ground for RF.
- **Parallel vias don't divide perfectly** because they couple: 2/4/9 vias (1 mm pitch, 1.6 mm) give ≈0.38/0.29/0.20 nH, not 0.27/0.14/0.06 nH. Spread them out.
- Signal via with one return via between planes (H. Johnson): $L\approx(\mu_0/\pi)h\ln(s/r)$; reproduces his 0.49 nH and 1.29 nH predictions (measured 0.46 and 1.41 nH). **Return vias next to signal vias** are what keep via inductance low.
- **Pad capacitance** (fringing included): 0402 pad on 0.21 mm prepreg ≈0.075 pF (+0.02 pF vs the 50 Ω line); 0603 ≈0.20 pF (+0.10); an SMA edge-launch pad ≈1.0 pF (+0.65 pF) — enough to spoil return loss at GHz, hence the **ground cut-out under wide pads**.
- **A slot in the return plane** acts as a series inductor ≈ $Z_{slot}\ell_s/(4v)$ (≈1.4 nH for a 10 mm slot, a few ohms at UHF) that grows and resonates as the slot approaches λ/2 (≈100 mm at 915 MHz) — and it radiates. Never route RF over plane splits.

## Intuition (no math)
A current can't flow without a return current, and the pair always forms a loop. The loop's inductance depends on the *area* between the go and return paths: a trace right above a solid ground plane has its return current flowing in the plane directly underneath it (the high-frequency return follows the path of least inductance, i.e. hugging the trace), so the loop is tiny. The same trace with the return current forced to take a detour — around a slot, through a distant via, across a connector — encloses a larger area and has more inductance.

Formulas that give "inductance of a wire" are **partial inductances**: bookkeeping pieces that only add up to a physical loop inductance when you include the mutual terms with the return path. That is why the popular "1 nH/mm" is right for a bondwire hanging in air far from its return, and badly wrong for a 50 Ω microstrip (≈0.3 nH/mm).

Vias are short vertical wires. Their inductance matters because they are the connection to ground for shunt capacitors, grounded pins, terminations and exposed pads. On a thin 4-layer prepreg the via to L2 is so short that it hardly matters; through a 1.6 mm 2-layer board, each via is ≈0.5 nH — several ohms at UHF, comparable to the parts it connects.

Pads are small capacitors to the plane beneath. For a 0402 on a thin prepreg the effect is ~0.05–0.1 pF; for a big connector pad it's ~1 pF, which at 2.4 GHz is only 65 Ω — a major discontinuity.

## The math

### Level 1 — per-unit-length parameters of a line over a plane
For any TEM/quasi-TEM line: $L'=Z_0\sqrt{\varepsilon_{eff}}/c$, $C'=\sqrt{\varepsilon_{eff}}/(cZ_0)$ ([telegrapher equations](../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md)). With the quasi-static microstrip formulas (Wheeler/Hammerstad as in Pozar; cross-checked against scikit-rf's Hammerstad–Jensen model within ~5 %, the difference being copper thickness):

| Stackup (script §2) | W | $Z_0$ | $\varepsilon_{eff}$ | L′ | C′ |
|---|---|---|---|---|---|
| 2-layer, h = 1.6 mm FR-4, εr 4.5, bare (model; JLC0216A calculator: 2.69 mm masked on its 1.43 mm core — [canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table)) | 3.0 mm | 50.3 Ω | 3.39 | 0.309 nH/mm | 0.122 pF/mm |
| same | 0.25 mm | 138 Ω | 2.95 | 0.788 nH/mm | 0.042 pF/mm |
| 4-layer JLC04161H-7628, 0.2104 mm to L2, εr 4.4 | 0.36 mm | 53.6 Ω (HJ with 35 µm Cu: 50.9) | 3.30 | 0.325 nH/mm | 0.113 pF/mm |
| same | 0.15 mm | 82.9 Ω | 3.10 | 0.487 nH/mm | 0.071 pF/mm |

A line of length $\ell$ with $\beta\ell\ll1$ is a π of $L'\ell$ in series with $C'\ell/2$ at each end. If $Z_0\gg$ the circuit impedance the capacitive ends are negligible and the line is an **inductor**; if $Z_0\ll$ it, a **capacitor**. The script shows 5 mm of 0.15 mm trace at 915 MHz ($\beta\ell=9.7°$): series reactance 13.93 Ω exact vs 14.00 Ω from $\omega L'\ell$.

### Level 2 — isolated conductors and vias
**Partial self-inductance of a straight round wire** (Grover/Rosa), length $\ell$, radius $r$, $\ell\gg r$:
$$L=\frac{\mu_0\ell}{2\pi}\left[\ln\frac{2\ell}{r}-1+\frac{r}{\ell}\right]\ \ (\text{HF; add }+\tfrac14\text{ for DC internal inductance}).$$
1 mm of 25 µm wire: 0.818 nH (HF), 0.868 nH (DC); 2 mm: 1.91 nH — the log term makes "nH per mm" rise with length. **Flat strip** (Ruehli/Grover): $L=\frac{\mu_0\ell}{2\pi}\left[\ln\frac{2\ell}{w+t}+\frac12+0.2235\frac{w+t}{\ell}\right]$: 10 mm × 0.3 mm → 9.2 nH if no return plane is near.

**Via to a ground plane** (Goldfarb & Pucel 1991, verified against measurement and numerical solutions for $h<0.03\lambda_0$):
$$L_{via}=\frac{\mu_0}{2\pi}\left[h\ln\frac{h+\sqrt{h^2+r^2}}{r}+\frac32\left(r-\sqrt{r^2+h^2}\right)\right].$$

| Via | L | X @ 915 MHz | X @ 2.45 GHz |
|---|---|---|---|
| 1.6 mm, 0.3 mm drill | 0.543 nH | 3.1 Ω | 8.4 Ω |
| 1.6 mm, 0.6 mm drill | 0.362 nH | 2.1 Ω | 5.6 Ω |
| 1.6 mm, 0.2 mm drill | 0.658 nH | 3.8 Ω | 10.1 Ω |
| 1.2 mm, 0.3 mm | 0.349 nH | 2.0 Ω | 5.4 Ω |
| 0.2104 mm (L1→L2), 0.3 mm | 0.015 nH | 0.09 Ω | 0.24 Ω |

(For $h\sim r$ the formula is at the edge of its validity; the point is that the thin-prepreg via is negligible compared with its pads and the part.)

**Signal via between planes with a return via** (Johnson, *HSDD* newsletter): each via contributes $(\mu_0/2\pi)h\ln(s/r)$, so the go-and-return loop is $L\approx(\mu_0/\pi)\,h\ln(s/r)$, $s$ = centre spacing. For $r=0.005''$, $h=0.040''$: $s=0.017''$ → 0.497 nH (Johnson: predicted 0.49, measured 0.46 nH); $s=0.12''$ → 1.29 nH (measured 1.41 nH). Deviations come from via stubs and finite planes.

**Parallel vias.** $N$ vias with mutual inductance $M_{ij}$ (parallel filaments of length $h$): $L_{eff}=1/\sum_{ij}(\mathbf{M}^{-1})_{ij}$. With 1.6 mm, 0.3 mm vias: 2 at 1 mm pitch → 0.383 nH; 2×2 → 0.289; 3×3 at 1 mm → 0.198; 3×3 at 0.7 mm → 0.242 nH (naive $L/N$ = 0.27, 0.14, 0.06 nH). Mutual coupling means clustering vias gives diminishing returns — spacing them apart (and to both sides of the part) helps more than adding more in a tight group. (Filament-mutual model mixed with the Goldfarb–Pucel self term: an estimate.)

### Level 3 — pads, plane slots and where the lumped picture breaks
**Pads as short wide lines.** Treat a pad as a microstrip section of its own width: $C_{pad}=C'(W_{pad})\ell_{pad}$ (fringing included). Excess over the line it interrupts is what matters:

| Pad (script §4) | $C_{pad}$ | Excess vs 50 Ω line | X @ 915 MHz |
|---|---|---|---|
| 0402 (0.55×0.5 mm), 0.21 mm prepreg | 0.075 pF | +0.018 pF | 2.3 kΩ |
| 0402 on 1.6 mm FR-4 (line 3 mm wide) | 0.027 pF | −0.034 pF (a narrow "neck": inductive) | 6.5 kΩ |
| 0603 (0.95×0.9 mm), 0.21 mm | 0.203 pF | +0.10 pF | 0.86 kΩ |
| SMA edge-launch (1.5×3 mm), 0.21 mm | 0.988 pF | +0.65 pF | 176 Ω |
| QFN exposed pad 3×3 mm, 0.21 mm | 1.84 pF | — | 95 Ω |

On a 2-layer 1.6 mm board the 50 Ω line (≈2.7–3 mm) is wider than 0402 pads, so parts cause *inductive* necks; on thin-prepreg 4-layer boards, pads wider than the 0.36 mm line are *capacitive* bumps. Standard fixes: shrink pads to line width, or remove the L2 ground under wide pads (referencing L3) to cut their capacitance — then re-simulate.

**Slots in the return plane.** A trace crossing a slot of length $\ell_s$ at its middle excites the slot as two shorted slotline stubs of length $\ell_s/2$ in parallel, in series with the trace: $Z\approx j\frac{Z_{slot}}{2}\tan\!\left(\beta_s\frac{\ell_s}{2}\right)$, i.e. $L\approx Z_{slot}\ell_s/(4v_s)$ when short. With $Z_{slot}\approx100\ \Omega$ (order of magnitude for a ~0.5 mm slot in FR-4) and $v_s\approx c/\sqrt{(\varepsilon_r+1)/2}$: 10 mm → 1.4 nH (7.9 Ω at 915 MHz); 20 mm → 2.8 nH; the slot resonates (and radiates efficiently) when $\ell_s\approx\lambda_s/2$ ≈ 100 mm at 915 MHz. This is an estimate for teaching; real layouts need EM simulation — but the conclusion "don't cross splits, stitch planes, keep slots ≪ λ/10" is robust ([grounding and return paths](../13-pcb-rf-layout-emc/grounding-and-return-paths.md)).

**When lumped fails.** Once a feature approaches λ/10–λ/20 in the dielectric (≈18 mm at 915 MHz on FR-4, ≈7 mm at 2.45 GHz), treat it as a transmission line or simulate it with an EM solver ([quasi-static vs full-wave](../02-electromagnetics/quasi-static-vs-full-wave.md)).

## Design equations & rules of thumb

| Item | Equation / value | Notes |
|---|---|---|
| Line L′, C′ | $Z_0\sqrt{\varepsilon_{eff}}/c$, $\sqrt{\varepsilon_{eff}}/(cZ_0)$ | 50 Ω FR-4: ≈0.31 nH/mm, 0.12 pF/mm |
| High-Z trace as inductor | $L\approx L'\ell$ for $\beta\ell\lesssim15°$ | 83 Ω: 0.49 nH/mm |
| Isolated wire | $\frac{\mu_0\ell}{2\pi}[\ln(2\ell/r)-1]$ | ≈0.7–1 nH/mm |
| Via to plane | Goldfarb–Pucel | 1.6 mm/0.3 mm: 0.54 nH; 0.21 mm: ≈0.02 nH |
| Via pair loop | $(\mu_0/\pi)h\ln(s/r)$ | keep return via within ~1 mm |
| Parallel vias | $1/\sum(\mathbf M^{-1})$ | 4 vias ≈ 0.29 nH, not 0.14 |
| Pad C | $C'(W_{pad})\ell_{pad}$ | 0402 ≈0.03–0.08 pF; SMA pad ≈1 pF |
| Slot crossing | $\approx Z_{slot}\ell_s/(4v)$ | 10 mm ≈ 1.4 nH; λ/2 resonance |
| Lumped limit | $\ell<\lambda_g/10$ | 18 mm @ 915 MHz |

## Worked examples

### 1. Grounding a shunt capacitor at 915 MHz
A 3.3 pF shunt capacitor (−52.7 Ω ideal) in a matching network, grounded with one 0.3 mm via through a 2-layer 1.6 mm board: via 0.54 nH (+3.1 Ω) plus part ESL ≈0.35 nH (+2.0 Ω) → net −47.6 Ω, i.e. the capacitor behaves like 3.65 pF. With a 4-layer board and a via to L2 (≈0.02 nH), the via term vanishes. At 2.45 GHz the 2-layer via alone is 8.4 Ω against a 1.3 pF (−50 Ω) capacitor — a 17 % error. **Design on 4-layer for ≥ 900 MHz, or include the via in the simulation.**

### 2. Ground pins of an RF module (LoRa module or transceiver) on a 2-layer board
A module with, say, 4 ground pads each tied down by one 1.6 mm via has a ground inductance ≈0.3 nH (coupled vias) — about 0.8 Ω at 433 MHz and 1.7 Ω at 915 MHz. Together with the antenna feed return this can let RF current flow on the board and cables (radiation, desensitisation). Add many vias along all ground pads and a continuous bottom plane ([package parasitics](package-parasitics-bondwires.md), [RF layout](../13-pcb-rf-layout-emc/rf-layout-rules.md)).

### 3. A deliberate inductor from a trace
Need ≈2.4 nH at 915 MHz in series with a 50 Ω path: 5 mm of 0.15 mm trace on the JLC 4-layer prepreg (83 Ω) gives 2.44 nH with ≈0.18 pF at each end (included automatically if you model it as a line). Printed inductors like this are repeatable (JLCPCB width tolerance is the main variable) and avoid a part.

## Practical notes
- **JLCPCB 4-layer (JLC04161H-7628)**: L1–L2 prepreg 0.2104 mm, Dk 4.4 (JLCPCB impedance page) — 50 Ω microstrip ≈0.34–0.36 mm wide depending on the calculator and copper (JLC's calculator: **0.359 mm masked / 0.377 mm bare**, [canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table)); use JLCPCB's own impedance calculator for the order and verify with scikit-rf/openEMS ([JLCPCB RF manufacturing](../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md)).
- **Documentation drift**: the Space Bar primary FC's KiCad stackup did not match the fabbed stackup — for RF this directly changes Z0 and via inductance; keep the as-ordered stackup in the repo.
- **Via stubs**: a through-via used to go from L1 to L2 leaves a stub to L4; at UHF on 1.6 mm boards the stub resonance is far above band (≈ c/(4·1.4 mm·√εr) ≫ 10 GHz), so ignore it below ~6 GHz.
- **Measure** unknown parasitics with a VNA and TDR on a test coupon ([TDR](../03-transmission-lines-matching/time-domain-reflectometry.md)).

## Common mistakes & misconceptions
- **"A trace is 1 nH/mm."** That's an isolated wire. Over a plane, a 50 Ω trace is ≈0.3 nH/mm (and a lot of that is cancelled by its return).
- **"More ground vias always help proportionally."** Coupled vias saturate; place them where they shorten the return loop (next to the part/pin) rather than in a clump.
- **Ignoring the via in a shunt element** on a 1.6 mm 2-layer board at ≥ 900 MHz.
- **Routing RF or fast digital across a plane split or slot** — adds inductance, creates a slot antenna.
- **Big pads on thin prepreg** (SMA, RF module pads) without a ground cut-out — a 0.5–1 pF shunt discontinuity.
- **Mixing partial and loop inductance** in hand calculations; partial inductances only make sense together with their mutual terms.

## How to simulate / verify
- `python3 tools/verify/components_pcb_parasitics.py` — wire/strip partial inductances, microstrip L′/C′ (with scikit-rf HJ cross-check), trace-as-inductor, Goldfarb–Pucel vias, Johnson's loop formula check, coupled parallel vias, pad capacitances, slot estimate.
- EM: openEMS (FDTD) or Sonnet Lite / Qucs-S with EM for via arrays, pads and slots; FastHenry for partial/loop inductance ([EM solvers](../16-simulation-tools/em-solvers-fdtd-mom-fem.md)).
- scikit-rf `media.MLine` / `media.CPW` for line parameters; add vias as series/shunt inductors.

## Open questions / gaps
- Pad capacitance values use a quasi-static microstrip model of the pad (no end effects of the gap between pads, no solder fillet) — confidence medium; EM-simulated values for JLCPCB stackups would be a good addition (cross-link 13-pcb-rf-layout-emc).
- Slotline impedance (100 Ω) is an assumed round number; the slot estimate is qualitative.
- Coupled-via inductance uses filament mutuals with Goldfarb–Pucel self terms (approximate).

## Sources
1. M. E. Goldfarb, R. A. Pucel, "Modeling via hole grounds in microstrip," *IEEE Microwave and Guided Wave Letters*, 1(6), 135–137, 1991 — via inductance formula (as reproduced in Qucs technical documentation, "Microstrip via hole", https://qucs.sourceforge.net/tech/node83.html). (peer-reviewed; software documentation)
2. H. W. Johnson, "Via inductance" and "Via inductance II," *High-Speed Digital Design Online Newsletter*, vol. 6 no. 4 and no. 8 (Signal Consulting). https://www.sigcon.com/Pubs/news/6_04.htm ; https://www.sigcon.com/Pubs/news/6_08.htm — loop formula and measured vs predicted values. (expert newsletter)
3. H. W. Johnson, M. Graham, *High-Speed Digital Design*, Prentice Hall, 1993 — ch. 5–7 (ground planes, vias, return current). (textbook)
4. F. W. Grover, *Inductance Calculations: Working Formulas and Tables*, Van Nostrand 1946 / Dover 2004 — straight-wire and strip formulas, mutual inductance of parallel filaments. (textbook)
5. A. E. Ruehli, "Inductance calculations in a complex integrated circuit environment," *IBM J. Res. Dev.*, 16(5), 470–481, 1972 — partial inductance concept. (peer-reviewed)
6. C. R. Paul, *Inductance: Loop and Partial*, Wiley-IEEE, 2010. (textbook)
7. D. M. Pozar, *Microwave Engineering*, 4th ed., 2012 — §3.8 microstrip formulas. (textbook)
8. JLCPCB, "Controlled impedance PCB layer stackup" (JLC04161H-7628: 7628 prepreg 0.2104 mm, Dk 4.4). https://jlcpcb.com/impedance (manufacturer documentation)
9. scikit-rf `skrf.media.MLine` (Hammerstad–Jensen) documentation. https://scikit-rf.readthedocs.io (software)
10. Verification script `tools/verify/components_pcb_parasitics.py` (this KB).
