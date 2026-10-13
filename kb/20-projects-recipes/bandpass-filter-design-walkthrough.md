---
title: Recipe — Harmonic low-pass and band-pass filters for 433 / 905–920 MHz LoRa links (prototype → real parts → layout → measurement)
domain: 20-projects-recipes
slug: bandpass-filter-design-walkthrough
tags: [recipe, filter, harmonic-filter, low-pass, elliptic, cauer, chebyshev, trap, band-pass, saw, ltcc, finite-q, srf, esl, via-inductance, monte-carlo, tolerance, power-handling, e22-400t33d, e220-900t30d, spurious-emissions, nanovna, tinysa, pre-registration]
prerequisites:
  - ../01-circuit-theory/passive-filter-design-prototypes.md
  - ../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md
  - ../04-real-components-hf/inductors-at-rf.md
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
related:
  - ../04-real-components-hf/pcb-parasitics-traces-vias-pads.md
  - ../18-components-parts/filter-parts-saw-ceramic-ltcc.md
  - ../13-pcb-rf-layout-emc/rf-layout-rules.md
  - ../13-pcb-rf-layout-emc/vias-stitching-fencing.md
  - ../17-test-measurement/spectrum-analyzers.md
  - ../17-test-measurement/nanovna-librevna-practical.md
  - ../17-test-measurement/fixtures-and-deembedding.md
  - ../19-regulations-safety/singapore-imda-rules.md
  - lora-rocket-telemetry-link.md
  - ground-station-tracking-yagi.md
  - gnss-front-end-design.md
level: intermediate
confidence: medium
last_updated: 2026-10-03
---

# Recipe — Harmonic and band-pass filters for 433 / 905–920 MHz LoRa links

Transmit-side harmonic suppression after a 2 W LoRa PA, followed from the ideal prototype to a
board you can order from JLCPCB and measure. The receive-side band-pass choice (SAW vs LC) is covered at
the end. Numbers: `python3 tools/verify/proj_harmonic_filter.py` (prototypes, snapping to standard values,
real-part models, Monte-Carlo, power flow); prototype theory and the original 433.92 MHz example are in
[passive filter design](../01-circuit-theory/passive-filter-design-prototypes.md) (`circuits_filter_prototypes.py`).

## Questions this page answers
- How much harmonic suppression does my 2 W 433 MHz LoRa transmitter need to be legal in Singapore?
- Should I use a Chebyshev or an elliptic low-pass, and how many poles?
- How do I turn ideal g-values into parts I can actually buy, and what do inductor Q, self-resonance and capacitor ESL do to the response?
- Why does my "60 dB" elliptic filter pass 4–6 GHz almost unattenuated?
- Does a 2-layer board ruin a filter compared with a 4-layer one?
- How much do ±2 % parts move a trap that sits on the 2nd harmonic?
- Will 0603 inductors survive 2 W, and how hot do they get?
- Can I buy a ready-made filter instead (Mini-Circuits LFCN)?
- Can I put a SAW filter after the PA?
- How do I measure 60–80 dB of rejection with a NanoVNA or tinySA without fooling myself?

## TL;DR
- **Requirement** (Singapore TS SRD spurious: −36 dBm below 1 GHz, −30 dBm above): at 33 dBm the 2nd harmonic (866.25 MHz) must be ≥ **69 dBc** below the carrier and the 3rd–5th ≥ **63 dBc**; at 24 dBm 60/54 dBc; at 10 dBm 46/40 dBc. The E22's own harmonic level is unpublished — measure it first; the external filter supplies the rest plus ≥ 6 dB margin.
- **Three candidate low-passes (433.125 MHz, real 0603 wire-wound inductors Q ≈ 40, C0G caps, JLC 4-layer):**
  | Design | IL at 433 MHz | 2f / 3f / 4f / 5f rejection | far stop band |
  |---|---|---|---|
  | Chebyshev N=5, 0.1 dB, fc 520 MHz | 0.57 dB | 30 / 59 / 88 / 113 dB | 54 dB at 6 GHz |
  | Chebyshev N=7, 0.1 dB, fc 520 MHz | 1.01 dB | **55 / 96 / 146 / >150 dB** | 76 dB at 6 GHz |
  | **Elliptic N=5, traps on 2f and 3f** | **0.46 dB** | **60 / 76 / 58 / 82 dB** | **collapses: 27 dB at 4 GHz, 14 dB at 5 GHz, 2 dB at 6 GHz** |
- **Monte-Carlo (L ±2 %, C ±0.1 pF):** Chebyshev N=7 is tolerance-proof (2f p5 54.6 dB); the elliptic's 2f notch falls from a median 56.5 to **50.9 dB (p5)** and 3f to 61.5 dB — the notch is real but its depth is a lottery unless you trim.
- **Real parts change the answer.** Inductor self-capacitance (≈ 0.11 pF for 0603CS) and pad capacitance (≈ 0.05 pF) sit across each trap: subtract them from the trap capacitor or the zero lands 1–3 % low. Capacitor ESL plus via inductance make shunt caps inductive above ≈ 2–3 GHz and the elliptic's small trap caps then couple straight through — a parasitic high-pass. On a 2-layer board (via ≈ 0.5–0.8 nH) the collapse starts at 2.5 GHz.
- **Power at 33 dBm**: 9–15 V rms across parts, up to 0.3 A rms through the centre capacitor, **65–112 mW dissipated in each trap inductor** — check 0603 temperature with a thermocouple; 50 V C0G and ≥ 0.6 A inductors are adequate.
- **Buy instead?** Mini-Circuits **LFCN-490+** (DC–490 MHz, 8.5 W, ≈ 40 dB typ. 880–2500 MHz, LCSC C3008205 ≈ US$3.06) is the low-risk drop-in for 433 MHz; LFCN-1000+ gives only ≈ 30 dB above 1.9 GHz — not enough alone for 905–920 MHz at 30 dBm.
- **905 / 920 MHz version** (0402 parts): elliptic with traps on 2f/3f — IL 0.54 / 0.44 dB, 2f ≈ 59–60 dB, 3f 68–81 dB on 4-layer; same far-stop-band caveat.
- **SAW filters are receive parts** — never after a PA. For the ground-station RX a 902–928 MHz SAW (2.2 dB) beats a 3-pole LC (≈ 9 dB for 26 MHz bandwidth at Q ≈ 52).

## Intuition (no math)
A transmitter's power amplifier is efficient because it distorts: the output contains the carrier plus weaker copies at 2×, 3×, 4× the frequency. A low-pass filter lets the carrier through and reflects the copies back into the PA. A Chebyshev filter does it with a smooth, steadily falling stop band; an elliptic filter adds "traps" — parallel L-C resonators that become open circuits exactly at chosen frequencies — so you can drop a deep notch onto the 2nd and 3rd harmonics with fewer parts and less loss. The price is that the traps are narrow (a 2 % part tolerance moves them off the harmonic) and that their small capacitors leak high frequencies straight through. Real inductors are also capacitors and real capacitors are also inductors; above a few GHz a lumped filter on a PCB stops being the circuit you drew.

## Requirements
| ID | Requirement | Value | Why |
|---|---|---|---|
| F1 | Pass band | 425–442 MHz (covers 433.05–434.79 MHz and 70 cm channels), IL ≤ 1 dB, RL ≥ 15 dB | PA efficiency, heat |
| F2 | Harmonic rejection (filter alone) | ≥ 69 − X + 6 dB at 2f, ≥ 63 − X + 6 dB at 3f–5f (X = module's own suppression) | TS SRD Table 1-a ([IMDA](../19-regulations-safety/singapore-imda-rules.md)) |
| F3 | Power | 2 W continuous during TX, ≤ 50 % duty, ≤ 60 °C ambient in the avionics bay | E22-400T33D |
| F4 | Size / assembly | ≤ 12 × 5 mm, JLC-assemblable or hand-solderable 0402/0603 | flight computer |
| F5 | Robustness | ±2 % L, ±0.1 pF C still meets F1–F2 | no trimming on the flight board |
| F6 | Testability | SMA test coupon of the same layout on the panel | measure before flying |
| F7 | Coexistence with onboard GNSS | 3f must not fall in a GNSS band the receiver tracks (E22 CH 0–9 → in or beside GPS/GLONASS L2; CH 10–22 → Galileo E6/BeiDou B3; use CH 24); if unavoidable, ≥ 100 dB total suppression at 3f would be needed | a −30 dBm "legal" harmonic coupled at −20 dB is a −50 dBm jammer ([telemetry recipe](lora-rocket-telemetry-link.md), [GNSS front end](gnss-front-end-design.md)) |

## Architecture options and trade study
| Option | IL | Rejection | Size | Risk | Verdict |
|---|---|---|---|---|---|
| Mini-Circuits LFCN-490+ LTCC | ≤ 1.2 dB | ≈ 40 dB typ. 880–2500 MHz | 3.2 × 1.6 mm | datasheet-backed, 8.5 W | **first choice if X ≥ 35 dB** |
| LC Chebyshev N=5 | 0.6 dB | 30 dB at 2f | 5 parts | low | too weak at 2f alone |
| **LC Chebyshev N=7** | 1.0 dB | 55 dB at 2f, ≥ 96 dB at 3f | 7 parts | lowest (no notch) | **choice when X is small or unknown** |
| **LC elliptic N=5 (traps on 2f/3f)** | 0.46 dB | 51–60 dB at 2f, 60–76 dB at 3f | 7 parts | tolerance + far stop band | best IL/size if 4-layer and far harmonics are weak |
| Cascade LFCN-490+ + Chebyshev N=5 | ≈ 1.7 dB | ≥ 65 dB at 2f (sum) | 6 parts | low | brute force |
| Microstrip stepped-impedance LPF | 0.3–0.8 dB | 30–40 dB | λ/8 sections ≈ 45 mm each at 433 MHz on FR-4 | — | too big at 433 MHz; feasible at 2.4 GHz ([RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)) |
| SAW / BAW after the PA | — | — | — | power rating far below watts ([filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md)) | **never** |

## The math — design calculations

### Level 1 — from requirement to prototype
- Required rejection: $A_n \ge P_{out} - L_{spur}(f_n) - X_n + M$, $L_{spur}$ = −36 dBm (< 1 GHz) or −30 dBm (≥ 1 GHz), margin $M$ ≈ 6 dB.
- Chebyshev order for $A$ dB at $\Omega_s = f_s/f_c$ with ripple $L_r$: $N \ge \cosh^{-1}\sqrt{(10^{A/10}-1)/(10^{L_r/10}-1)}\,/\cosh^{-1}\Omega_s$ ([prototypes](../01-circuit-theory/passive-filter-design-prototypes.md)). With $f_c$ = 520 MHz, 2f at Ω = 1.67: N = 5 gives ≈ 25 dB, N = 7 ≈ 45 dB (ideal).
- Scaling to 50 Ω: shunt $C_k = g_k/(Z_0\omega_c)$, series $L_k = g_kZ_0/\omega_c$.
- Elliptic traps: series branch $L\parallel C$ is an open circuit at $f_z = 1/(2\pi\sqrt{L C})$ → transmission zero. Here the two zeros are *chosen* (2f, 3f) and the five remaining values optimised for pass-band return loss (≥ 26 dB ideal).

### Level 2 — real parts
Element models used (all in the script; values from the KB component pages):

| Element | Model | Values used |
|---|---|---|
| Wire-wound chip inductor (Coilcraft 0603CS / 0402CS class) | $L$ + $R=\omega L/Q(f)$, $Q(f) = Q_{433}\sqrt{f/433\,\mathrm{MHz}}$, in parallel with $C_p$ | $Q_{433}$ = 40, $C_p$ = 0.11 pF (0603CS, from the 10 nH listing's 4.8 GHz SRF); 0402: 0.15 pF, $Q$ 30 ([inductors at RF](../04-real-components-hf/inductors-at-rf.md)) |
| C0G MLCC | ESR + $j\omega$(ESL + via) + $1/j\omega C$ | ESR 0.15 Ω, ESL 0.45 nH (0402/0603 mounted) ([capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md)) |
| Shunt-to-ground via | series inductance | 4-layer, L2 ground 0.21 mm below: ≈ 0.1 nH used (the via barrel alone is ≈ 0.02 nH, Goldfarb–Pucel; the rest is a pad/stub allowance); 2-layer 1.6 mm: one 0.3 mm via ≈ 0.54 nH + pad/stub → 0.8 nH used ([PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md)) |
| Pads | shunt capacitance | 0.05 pF per node |

**Trap placement with real parts.** The hardware zero is $f_z = 1/(2\pi\sqrt{L(C + C_p + C_{pad})})$. Workflow (script `snap_zero_targeted`): pick standard inductors within ±20 % of the prototype, compute the capacitor that puts the zero on target *after* subtracting $C_p + C_{pad}$ = 0.16 pF, snap to 0.1 pF, then re-optimise the three shunt capacitors for return loss with the real models and snap them.

**Finite-Q loss.** $\Delta L \approx 8.686\,(\omega/Q)\,\tau_g$ dB for low-pass elements (verified in the prototype page). The elliptic's loss vs inductor Q: Q 20 → 0.86 dB, 30 → 0.59, 40 → 0.46, 60 → 0.32, 80 → 0.26 dB.

### Level 3 — where the lumped model breaks
- Above the capacitors' self-resonance (5.9 pF with 0.55 nH: ≈ 2.8 GHz) the shunt elements are inductors and the trap capacitors (0.8–2.1 pF) are low-impedance series paths: the ladder turns into a high-pass. This is why the real elliptic passes 4–6 GHz while the ideal one gives ≥ 46 dB everywhere above 2f.
- Inductor SRF (0603CS 15–16 nH: ≈ 3.2–3.5 GHz) adds extra zeros — the Chebyshev's real 2f/3f rejection is *better* than ideal for the same reason.
- Trace lengths between parts (≈ 0.3–0.4 nH/mm for 50 Ω-class traces on 7628) add series inductance; keep the whole filter ≤ 10 mm long or include the traces in an EM model.
- Measurement dynamic range, not the filter, limits what you can verify above ≈ 70 dB (see test plan).

## Design equations & rules of thumb
| Rule | Value |
|---|---|
| Spurious limit to dBc | $P_{out}$ + 36 dB (< 1 GHz), $P_{out}$ + 30 dB (≥ 1 GHz) |
| Chebyshev N=7, fc 1.2 f0 | ≈ 45 dB ideal at 2f; ≈ 55 dB with real parts (SRF zeros) |
| Trap capacitor | $C = 1/(\omega_z^2 L) - C_p - C_{pad}$ |
| Trap zero sensitivity | $\Delta f_z/f_z \approx -\tfrac12(\Delta L/L + \Delta C_{tot}/C_{tot})$: ±2 % L → ±1 %; ±0.1 pF on 0.96 pF → ±5 % |
| Finite-Q loss | $8.686(\omega/Q)\tau_g$ dB |
| Voltage across parts at $P$ | $V_{rms} \approx \sqrt{P Z_0}$ = 10 V at 2 W, up to 1.5× inside the ladder |
| Via inductance | 4-layer (0.21 mm) ≈ 0.1 nH; 2-layer 1.6 mm ≈ 0.5 nH per via |

## Worked examples

### 1. 433.125 MHz elliptic low-pass, step by step
1. **Ideal** (traps exactly on 866.25 / 1299.375 MHz, RL-optimised): C1 4.92 pF | 14.69 nH ∥ 2.30 pF | C3 11.74 pF | 17.11 nH ∥ 0.88 pF | C5 6.51 pF. IL 0.01 dB, RL ≥ 26 dB (425–442 MHz).
2. **Naive snapping** (nearest 0603CS L and 0.1 pF C, ignoring parasitics) puts the zeros at 857 and 1250 MHz and drops 2f rejection to ≈ 47 dB even with ideal parts — a 1–4 % zero error throws away most of the notch.
3. **Zero-targeted snapping**: L 15 nH + C 2.1 pF → 864.4 MHz (incl. 0.16 pF parasitic); L 16 nH + C 0.8 pF → 1284.2 MHz; shunts re-optimised: **C1 5.9 pF, C3 10 pF, C5 4.1 pF**.
4. **Real response** (4-layer, via 0.1 nH): IL 0.46 dB, RL ≥ 25.7 dB; rejection 2f 60.4, 3f 76.4, 4f 58.4, 5f 82.1 dB; 3 GHz 61.4, 4 GHz 26.9, 5 GHz 14.1, 6 GHz 1.5 dB. On 2-layer (via 0.8 nH): 2f 64.6, 3f 92.4, 4f 71.4, 5f 62.5 dB, but 3 GHz 17.3 dB and ≈ 1–4 dB from 4–6 GHz.
5. **Monte-Carlo** (2000 builds): IL median 0.46 dB (p95 0.48); RL p5 22.1 dB; 2f 56.5/50.9 dB (median/p5); 3f 68.1/61.5; 4f 58.3/56.6; 5f 82.1/78.1.
6. **Power at 33 dBm**: C1 10.2 V rms / 169 mA; trap 1 13.5 V rms / 249 mA, **112 mW**; C3 10.4 V / 296 mA, 13 mW; trap 2 10.7 V / 219 mA, **66 mW**; C5 9.5 V / 109 mA; delivered 1.795 W of 1.995 W (0.46 dB).

### 2. Is it enough? (decision with the unknown module suppression X)
| X (module's own 2f / 3f suppression) | Elliptic (p5) 2f total | Required 69 dBc | Chebyshev N=7 2f total |
|---|---|---|---|
| 20 dBc (no internal LPF) | 70.9 dBc | marginal (+1.9 dB) | 74.6 dBc |
| 30 dBc | 80.9 dBc | OK | 84.6 dBc |
| 40 dBc | 90.9 dBc | OK | 94.6 dBc |

So measure X first (T1). If X < 25 dBc or the PA has measurable energy above 3 GHz, use the Chebyshev N=7 or cascade LFCN-490+ with the elliptic.

### 3. 905 MHz (IREC) and 920 MHz (Singapore) versions, 0402 parts
| | 905 MHz | 920.125 MHz |
|---|---|---|
| Snapped values | C 2.7 pF \| 7.5 nH ∥ 0.8 pF (1837.8 MHz) \| C 5.6 pF \| 8.7 nH ∥ 0.2 pF (2697.9 MHz) \| C 3.1 pF | C 2.6 pF \| 7.5 nH ∥ 0.8 pF (1837.8 MHz) \| C 4.6 pF \| 8.2 nH ∥ 0.2 pF (2779 MHz) \| C 1.8 pF |
| 4-layer real: IL / RL | 0.54 dB / ≥ 31.7 dB | 0.44 dB / ≥ 30.8 dB |
| 2f / 3f / 4f | 59.7 / 80.5 / 78.7 dB | 59.2 / 67.5 / 75.9 dB |
| 5 GHz / 6 GHz | 56.8 / 12.7 dB | 62.6 / 26.5 dB |
| 2-layer: 2f / 3f / 4f / 5 GHz | 78.2 / 108 / 38.8 / 12.6 dB | 71.2 / 82.8 / 52.9 / 15.5 dB |
A 0.2 pF trap capacitor is at the limit of what the parts and pads allow — the 3f trap of the 900 MHz filters is essentially the inductor's self-capacitance plus pads; build a coupon and measure.

### 4. Receive-side band-pass (ground station)
Lumped coupled-resonator 3-pole at 915 MHz with Q ≈ 52 parts: ≈ 2.6 dB for a 90 MHz-wide filter but ≈ 9 dB for 902–928 MHz ([prototypes, example 7](../01-circuit-theory/passive-filter-design-prototypes.md)) — useless before an LNA. Use a SAW (B39921B3728U410: 26 MHz, 2.2 dB; B39431B3710U410 for 433.00–434.71 MHz, ≤ 2.7 dB) *after* the LNA, or a helical/cavity filter (< 1 dB) *before* it when blockers are strong ([ground-station recipe](ground-station-tracking-yagi.md), [filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md)).

## Part selection
LCSC qty 1–9 prices from the JLC parts DB snapshot 2026-07-08 (USD); Coilcraft stock on LCSC is thin (tens of pieces) — order spares or source from Coilcraft/DigiKey and hand-place.

| Ref | Value | Part | Price | Notes |
|---|---|---|---|---|
| L (trap 1) | 15 nH ±2 % | Coilcraft 0603CS-15NXGRW (C43824819) or 0603HP-15NXGRW (C41016610, 1.2 A, Q 48 @ 250 MHz) | $0.54 / $0.71 | 112 mW dissipation at 33 dBm |
| L (trap 2) | 16 nH ±2 % | Coilcraft 0402CS-16NXGRW (C40056697, 560 mA, Q 46 @ 900 MHz) or 0603CS-16N via distributor | $1.11 | 66 mW |
| C trap 1 | 2.1 pF ±0.05 pF | Murata GJM1555C1H2R1WB01D (C2220990, high-Q C0G 0402) | $0.05 | |
| C trap 2 | 0.8 pF ±0.05 pF | Murata GJM1555C1HR80WB01D (C88902) | $0.06 | |
| C1 / C5 | 5.9 pF / 4.1 pF | GJM1555C1H5R9WB01D (C2220907) / GJM1555C1H4R1WB01D (C2220852) | $0.05 | |
| C3 | 10 pF ±2 % | GJM1555C1H100GB01D (C85873) | $0.02 | 0.3 A rms — 0402 OK, 0603 for margin |
| Alternative | LTCC LPF | Mini-Circuits LFCN-490+ (C3008205) / LFCN-1000+ (C879868) | $3.06 / $1.72 | datasheet power 8.5 / 10 W ([filter parts](../18-components-parts/filter-parts-saw-ceramic-ltcc.md)) |
| RX SAW | 433 / 915 MHz | B39431B3710U410 (C2649317) / B39921B3728U410 (C2650953) | $0.98 / $1.92 | receive only |

## Block diagram
```
 SX1268 / E22 PA out (50 ohm) --[DC block if needed]--+--C1--+--(L1 || Ct1)--+--C3--+--(L2 || Ct2)--+--C5--+--> antenna / SMA
                                                      |  GND |               | GND  |               | GND  |
                                       (shunt caps: each with its own via(s) straight down to the L2 plane)
 Test coupon on the same panel: SMA -- 50 ohm CPWG -- identical filter layout -- 50 ohm CPWG -- SMA, plus a THRU line of equal length
```

## Layout notes
- Use the 4-layer stackup with L2 solid ground 0.21 mm below L1 (JLC 7628) so shunt-cap vias are ≈ 0.1 nH; two vias per shunt cap, placed at the pad, not at the end of a trace ([vias & stitching](../13-pcb-rf-layout-emc/vias-stitching-fencing.md), [stackups](../13-pcb-rf-layout-emc/stackups-and-materials.md)).
- Keep the parts in a straight line, input and output at opposite ends, ≥ 3 mm between input and output traces; orient the two trap inductors at 90° to each other (mutual coupling between wire-wound parts bypasses the traps); a ground-stitched fence along both sides ([RF layout rules](../13-pcb-rf-layout-emc/rf-layout-rules.md)).
- Pads: the smallest the assembler accepts; remove copper pour from under series parts' pads on L1 (adds pad capacitance) but keep L2 solid.
- Leave 0 Ω / DNP footprints to bypass the filter and to add a 1 pF shunt at the output (tames the far stop band).
- Shield can footprint over PA + filter if the module is chip-down ([shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md)).
- Record the as-ordered stackup and part numbers in the repo (Avionics B's documentation-drift lesson).

## Simulation plan
| Step | Tool | Pass |
|---|---|---|
| Ideal and real-part ladder, Monte-Carlo | `proj_harmonic_filter.py` (ABCD) | F1–F2 met at p5 |
| Vendor S-parameter models of the actual L and C (Coilcraft and Murata publish S2P) | scikit-rf cascade ([Python RF toolkit](../16-simulation-tools/python-rf-toolkit.md), [component models](../04-real-components-hf/component-models-s2p-spice.md)) | within 2 dB of the model at 2f/3f; locate SRF zeros |
| Layout parasitics | openEMS of the coupon (traces, pads, vias) with lumped elements, or Qucs-S/KiCad ngspice with extracted L/C ([openEMS](../16-simulation-tools/openems-workflow.md), [SPICE](../16-simulation-tools/spice-circuit-simulation.md)) | zero positions within ±1 %; 3–6 GHz behaviour |
| Independent check | prototype g-values against the textbook tables ([prototypes](../01-circuit-theory/passive-filter-design-prototypes.md)) | exact |

## Build, bring-up and test plan (pass/fail fixed in advance)
| # | Test | Method | Pass |
|---|---|---|---|
| T1 | Module harmonics without filter (X) | E22 at 24 dBm → 30 dB 5 W attenuator → **high-pass (> 700 MHz) to remove the carrier** → tinySA Ultra; repeat with +10 dB extra attenuation — a real harmonic drops 10 dB, an analyser-generated one 20–30 dB ([spectrum analyzers](../17-test-measurement/spectrum-analyzers.md)) | X recorded for 2f–5f (decides the design) |
| T2 | Coupon S21/S11 | NanoVNA-H4 (> 60 dB to 900 MHz, > 40 dB to 1.5 GHz) or LiteVNA (> 70 dB < 3 GHz), full 2-port cal at the SMA planes, de-embed with the THRU coupon ([NanoVNA](../17-test-measurement/nanovna-librevna-practical.md), [fixtures](../17-test-measurement/fixtures-and-deembedding.md)) | IL ≤ 0.8 dB, RL ≥ 15 dB 425–442 MHz; notches within ±10 MHz of 866/1299 MHz |
| T3 | Deep rejection | rejection beyond the VNA's floor: signal generator/second module at known level + tinySA (RBW 10 kHz), or the T4 method | ≥ F2 at 2f–5f |
| T4 | In-system harmonics | flight radio at 33 dBm → filter → 40 dB attenuator → high-pass → tinySA; sweep 30 MHz–6 GHz | every harmonic ≤ −36 dBm (< 1 GHz) / −30 dBm (≥ 1 GHz) referred to the antenna port |
| T5 | Power soak | 2 W at 50 % duty, 10 min, thermocouple on both trap inductors | ΔT ≤ 40 K; S21 unchanged after cooling |
| T6 | Antenna-load pull | repeat T4 with the real antenna (via a coupler) in the airframe | harmonics within 3 dB of T4 |

## Regulatory check
- Spurious limits are those of TS SRD Table 1-a (ITU-R SM.329 Category B) for licence-exempt operation; amateur and permit conditions carry their own spurious clauses — check the licence text ([IMDA](../19-regulations-safety/singapore-imda-rules.md), [amateur](../19-regulations-safety/amateur-radio-licensing.md)).
- Harmonic of a 433.125 MHz carrier lands at 866.25 MHz — inside the 866–869 MHz SRD band used by the secondary link ([telemetry recipe](lora-rocket-telemetry-link.md)); a legal harmonic is still 60+ dB above the noise of a nearby receiver.
- Keep the T1/T4 plots: competitions ask for measured emissions ([competition rules](../19-regulations-safety/international-rules-for-competitions.md)).

## Pre-registered predictions
| ID | Prediction | Tolerance | If outside |
|---|---|---|---|
| H1 | Coupon IL at 433.125 MHz 0.46 dB (elliptic), 1.0 dB (Chebyshev N=7) | ±0.3 dB | inductor Q at 433 MHz differs from 40 |
| H2 | Trap notches at 864 ± 10 MHz and 1284 ± 15 MHz | as stated | parasitic C differs from 0.16 pF; recompute the trap caps |
| H3 | Elliptic rejection 2f ≥ 51 dB, 3f ≥ 61 dB on 4-layer | 5th percentile | tolerance stack or coupling between inductors |
| H4 | Elliptic stop band degrades to < 30 dB above ≈ 3.8–4 GHz on 4-layer, above ≈ 2.5 GHz on 2-layer | ±0.5 GHz | ESL/via model wrong (good to know) |
| H5 | Trap-inductor temperature rise at 2 W, 50 % duty ≤ 40 K | — | dissipation model or Q wrong; move to 0603HP/0805 |

## Risks and common failure modes
| Failure | Cause | Mitigation |
|---|---|---|
| Notch misses the harmonic | parasitic C not subtracted; part tolerance | zero-targeted values; ±0.05 pF caps; coupon measurement; trim cap footprint |
| "Filter works on the VNA but harmonics still high on air" | radiation from the PA/module bypasses the filter; harmonics on the supply/coax shield | shield can, ferrite on supply, choke on coax, test T6 |
| Far-stop-band leakage | parasitic high-pass above 3–4 GHz | 4-layer; extra 1 pF shunt; Chebyshev N=7 |
| Analyzer-generated harmonics | SA mixer overload | high-pass before the SA; attenuation step test |
| Inductor cracking/heating | 2 W in 0402 | 0603HP; thermal test T5 |
| SAW used after PA | ignorance of power rating | rule: SAW only in RX or before the PA |
| Detuned PA match | filter RL poor at the PA's actual impedance | measure PA output with the filter in place; adjust C1 |

## Cost estimate
| Item | Cost (USD) |
|---|---|
| Filter parts per board (elliptic, high-Q caps + Coilcraft) | ≈ 2.0 |
| Test coupons on the next JLC panel (incremental) | ≈ 0–5 |
| SMA edge connectors for coupons (4) | ≈ 4 |
| High-pass filter for SA tests (e.g. LTCC HPF or DIY LC) | ≈ 5–20 |
| LFCN-490+ alternative | 3.06 each |

## Practical notes
- Measure the module first (T1) — it may already be compliant at 24 dBm and only need a small filter.
- Order capacitors with W (±0.05 pF) tolerance below 5 pF; below 1 pF the pad layout matters as much as the part.
- On a NanoVNA, a filter notch deeper than the instrument floor reads as "−60 dB" — do not record that as the filter's rejection; quote "> 60 dB (instrument floor)".
- Trap inductors interact: orient them at right angles and ≥ 2 mm apart.
- If the module is a UART type with SMA output, the filter coupon with SMAs *is* the flight filter — mount it on the bulkhead.

## Common mistakes & misconceptions
- **"An elliptic filter gives 60 dB everywhere above 2f."** Only between its zeros and only until parasitics take over; the real one here passes 6 GHz with 1.5 dB loss.
- **"Snap to the nearest standard values."** For traps, that moves the zero by 1–4 % and loses ≈ 15 dB of notch; place the zero with the parasitic capacitance included.
- **"More poles means more loss, so use fewer."** With Q ≈ 40 parts N=7 costs ≈ 1 dB (≈ 20 % of 2 W) — usually acceptable for the robustness.
- **"The PA's datasheet harmonic number is what comes out of the antenna."** Load mismatch, supply ripple and radiation from the module can all add.
- **"SAW filters clean up transmitters."** They burn out; use LTCC/LC on TX.
- **"The VNA says −62 dB, so the filter rejects 62 dB."** It may be the VNA's floor.

## How to simulate / verify
- `python3 tools/verify/proj_harmonic_filter.py` — all tables on this page (≈ 2 s).
- `python3 tools/verify/circuits_filter_prototypes.py` — prototype g-values, elliptic fit, original 433.92 MHz example.
- `python3 tools/verify/rfckt_filters.py` — coupled-resonator and microstrip filters (06 domain).

## Open questions / gaps
- The E22-400T33D's intrinsic harmonic levels (X) are not published; T1 will give them.
- Q(f) of the 0603CS/0402CS parts at 433 MHz is extrapolated from the 250/900 MHz listing values; vendor S2P files would replace the model.
- Thermal resistance of 0603 wire-wound inductors on FR-4 not sourced (H5 measures it).
- Mini-Circuits LFCN-490+ rejection at 1299 MHz and above 2.5 GHz should be taken from its S-parameter file before relying on it.

## Sources
1. This KB, [Passive LC filter design from low-pass prototypes](../01-circuit-theory/passive-filter-design-prototypes.md) and `tools/verify/circuits_filter_prototypes.py` — g-values, order formula, elliptic fit, finite-Q loss rule, 433.92 MHz example, 915 MHz coupled-resonator example. (internal; Matthaei/Young/Jones, Pozar)
2. This KB, [RF filter technologies](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md) — Q by technology, SAW/BAW properties, microstrip filters. (internal)
3. This KB, [Inductors at RF](../04-real-components-hf/inductors-at-rf.md), [Capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md), [PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md) — Q, SRF, ESL, via inductance. (internal; Coilcraft/Murata data)
4. This KB, [Filter parts — SAW, ceramic, LTCC](../18-components-parts/filter-parts-saw-ceramic-ltcc.md) — LFCN-490+/1000+ ratings, SAW parts, power-handling rule. (internal; Mini-Circuits datasheets)
5. IMDA TS SRD Issue 1 Rev 3, Table 1-a spurious limits — via [Singapore IMDA rules](../19-regulations-safety/singapore-imda-rules.md). (regulator standard)
6. This KB, [Spectrum analyzers](../17-test-measurement/spectrum-analyzers.md) and [NanoVNA practical](../17-test-measurement/nanovna-librevna-practical.md) — internal-distortion checks, dynamic range by instrument. (internal)
7. JLCPCB/LCSC parts database snapshot 2026-07-08 — Coilcraft 0603CS/0603HP/0402CS, Murata GJM, Mini-Circuits LFCN stock and prices. (distributor data)
8. D. M. Pozar, *Microwave Engineering*, 4th ed., ch. 8 (filter design by the insertion-loss method, Richards/Kuroda) — via [1], [2]. (textbook)
