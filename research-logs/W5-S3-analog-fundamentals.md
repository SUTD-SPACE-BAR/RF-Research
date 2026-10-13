# Research log W5-S3: analog fundamentals in 05 (gap slice S3)
Status: complete (2026-10-13)
Owner scope: surgical additions (Edit tool) to kb/05-analog-electronics/{op-amps-real-limitations, analog-signal-conditioning,
power-supplies-for-rf-and-analog, diodes-schottky-pin-varactor, bjt-fundamentals-small-signal, amplifier-topologies}.md and
kb/01-circuit-theory/lumped-elements-impedance-admittance.md (DC primer only); tools/verify/s3_*.py; gaps/GAP_REGISTER.md (§3 → §5
for my rows only); this log. NOT oscillators.md, NOT any _index.md.

Pre-check (2026-10-03): research-logs/W5-E9-consistency-fixes.md Status = complete; its 05 edits were oscillators, low-noise,
op-amps (290 K wording l.141,168), data-converters. No pending E9 edits on my files.

## Plan
- [x] G-05-01 — DONE 2026-10-12 (05/op-amps#Practical recipes; 05/analog-signal-conditioning#Current loops (4-20 mA)…; s3_opamp_recipes.py) — practical op-amp recipes → 05/op-amps-real-limitations (new section: resistor-value choice noise vs bias vs load;
      bias-return path in AC-coupled non-inverting; noise-gain < 1 attenuator stability trap; MOSFET inside the loop; summing-amp
      noise gain) + 05/analog-signal-conditioning (4–20 mA loop receiver; differential long sensor lines; link 13/emc rectification).
      Script tools/verify/s3_opamp_recipes.py (ngspice).
- [x] G-09-02 — DONE 2026-10-12 (05/diodes#Rectennas; s3_rectenna.py) — far-field RF energy harvesting (rectenna efficiency vs Pin; ambient budget via Friis; exposure-limit cap) →
      05/diodes-schottky-pin-varactor (new rectenna section). Script tools/verify/s3_rectenna.py (ngspice HB-free transient + Friis).
- [x] G-05-03 — DONE 2026-10-13 (05/analog-signal-conditioning#Comparators, Schmitt triggers and timers; output stages in 05/amplifier-topologies#Output stages — allowed S3 file; s3_lines_comparators.py, s3_bw_extension.py §7) — comparators, Schmitt triggers (hysteresis equations + example), output stages (open-drain/push-pull), 555 timer →
      05/analog-signal-conditioning. Script tools/verify/s3_comparator_schmitt.py (ngspice).
- [x] G-05-05 — DONE 2026-10-12 (01/lumped#Level 0; 05/diodes#Level 0; 05/bjt#Level 0; s3_primer.py) — day-one primer: Ohm's law, DC power, SI prefixes (01/lumped-elements); doping, depletion, typical VF
      (Si/Ge/Schottky/LED), failure mechanisms (05/diodes); VBE, fα/fβ vs fT (05/bjt). Script tools/verify/s3_primer.py.
- [x] G-05-04 — DONE 2026-10-13 (05/power-supplies#Mains supply fundamentals + Worked ex. 5; s3_rectifier_battery.py) — rectifiers half/full/bridge ripple derivation; series vs shunt regulators; SMPS vs linear for a transmitter;
      worked bench supply for a 2 W PA → 05/power-supplies. Script tools/verify/s3_rectifier_supply.py (ngspice).
- [x] G-05-02 — DONE 2026-10-13 (05/amplifier-topologies#Bandwidth extension…; s3_bw_extension.py) — bandwidth extension: shunt/series/T-coil peaking, distributed amplifiers, balanced amps with 90° hybrids,
      resistive-feedback wideband LNA, why an LNA is a poor TX driver → 05/amplifier-topologies. Script tools/verify/s3_bw_extension.py.
- [x] G-05-06 — DONE 2026-10-13 (05/power-supplies#Batteries + Worked ex. 6; s3_rectifier_battery.py) — batteries: chemistry table, internal resistance vs pulse current, Ah → runtime, cold, Peukert; cold-launch worked
      example → 05/power-supplies. Script tools/verify/s3_battery.py.
- [x] Close rows in GAP_REGISTER §5 (C80–C86), §3 rows marked closed (register convention); final report.

## Log (append-only)
- 2026-10-03 — Step 0: read CONVENTIONS, GAP_REGISTER §3 rows (G-05-01/02/03/04/05/06, G-09-02), §6 S3 row, orchestrator note,
  canonical-values page (300 K labelled for 05 analog budgets; 4kT0R = 4.00 nV/√Hz/√kΩ at 290 K). Confirmed W5-E9 complete.
- 2026-10-03 — Read all 7 target pages in full (none edited). Findings for the design of the additions:
  - op-amps page has no resistor-choice / AC-coupled bias-return / summing-NG / MOSFET-in-loop material; feedback-and-stability.md
    already covers R_ISO, dual feedback, noise-gain shaping, decompensated parts → link to it, don't duplicate.
  - D1 row 387 (SE q/544404, "mistake in Op Amps for Everyone about attenuators"): OAFE warns against inverting attenuators; correct
    statement: NG = 1 + R_F/R_in ≥ 1 always (→ 1 from above), so an inverting attenuator is *more* stable than a follower for a
    unity-gain-stable part; the real trap is decompensated parts (fix: noise-gain shaping). SE/E2E/AAC fetches blocked (403) → mark
    the forum claim "(forum — anecdotal)", physics derived.
  - RF-rectification anchor to link: ../13-pcb-rf-layout-emc/emc-emi-fundamentals.md#level-3--susceptibility-rectification-pyro-circuits-esd
  - G-09-02: 08/inductive-coupling-rfid-nfc-wpt.md:132–133 already has a far-field harvesting paragraph (efficiency only cited, Valenta &
    Durgin 2014). 05/diodes section must *derive* efficiency vs Pin (ngspice/Python HSMS-285x rectifier) and add exposure cap
    P_max = S_lim·A_e (ICNIRP 2020 public f/200 W/m² → 4.58 W/m² at 915 MHz, from 19/rf-exposure-safety.md:40); link back to 08 section.
  - G-05-03 source rows: D4#38 (AoE 2.4/7.2/12.3: comparators, Schmitt, push-pull/class-AB output stages, 555), D5#22 (E6C01/02).
    Plan: Schmitt equations + ngspice threshold sweep; 555 via ngspice switch-with-hysteresis model (VT=Vcc/2, VH=Vcc/6).
  - G-05-04/06 source D5#19/#20: rectifier ripple I/(fC) half-wave, I/(2fC) full-wave; series vs shunt (Zener + ripple-bypass cap,
    E7D07); bench linear vs buck supply for E22 5 V/1.2 A; battery table (LiPo, LiFePO4, NiMH, alkaline, lead-acid), Peukert, cold.
    Team context: Avionics B 2S (7.0–8.4 V), Avionics C 1S on XT60 with 5 V buck-boost for radio.
  - G-05-02 sources D4#19, D5#14: shunt/series/T-coil peaking (Lee ch. 9), distributed amp, balanced amp with 90° hybrids
    (link 06/couplers-dividers-combiners.md), resistive-feedback LNA, why an LNA is a poor TX driver.

- 2026-10-12 — Resumed. Wrote tools/verify/s3_spice.py (batch ngspice helper), s3_opamp_recipes.py (ALL PASS: 100k/1M + 10 pF
  peaks +7.8 dB, C_F 1 pF fixes; AC-coupled .op 1.635 V vs rail when R_G to ground; attenuator NG 1.1 peaking 0.04 dB (unity-stable)
  vs +4.9 dB decompensated, 0.10 dB with 256 Ω + 10 nF shaping; MOSFET sink 58 % → 3.5 % overshoot with 100 Ω/220 pF/1 k; 4-input
  summer −3 dB 200 kHz). Edited 05/op-amps (new 'Practical recipes' subsection, TL;DR, questions, rules rows, mistakes, sources 11–12).
- 2026-10-12 — s3_lines_comparators.py (ALL PASS): 4–20 mA 150 Ω levels, ngspice compliance collapse at +600 Ω (17.6 mA); 1 % diff
  amp 19.8 mV/1 V; Schmitt 3.507/3.316 V sim vs 3.512/3.312 calc; chatter 27 → 1; 555 1387.3 Hz vs 1387.2. Searched NAMUR NE 43
  (secondary summaries agree: 3.8–20.5 valid, ≤3.6/≥21 fault), TI TIDU020A (R_h > 100 R_p). Edited 05/analog-signal-conditioning
  (two new subsections + TL;DR + questions + rules + mistakes + sources 8–11).

- 2026-10-12 — s3_rectenna.py (ALL PASS, ~40 s): ngspice 915 MHz HSMS-2850 tank-matched rectenna, Q_L 50: 3.2/16/31/51/58/30 % at
  −40…+10 dBm; ideal 4.5/20/41/61/70 %; HSMS-282x 42/57/67 % at 0/10/20 dBm; resistive-source ceiling 4/π² (38.0 % quasi-static,
  38.1 % ngspice); exposure cap 131/62/19 mW (433/915/2450 MHz, 2 dBi). First attempt (resistive source only) gave a ≤ 40 % curve
  — recognised as the no-harmonic-termination limit, kept as §2. Edited 05/diodes (Level 0 primer + Rectennas subsection, TL;DR,
  questions, rules, mistakes, sources 13–16).
- 2026-10-12 — s3_primer.py (ALL PASS): LED/divider .op; φ 0.776 V, W 0.33/0.91 µm; LED hc/qλ floors; ngspice V_F 1N4148 0.589/0.698,
  HSMS-282x 0.311/0.429; BJT f_β 2.25 MHz, f_T 477, f_α 500 MHz. Edited 01/lumped (Level 0 DC basics) and 05/bjt (Level 0).

- 2026-10-13 — s3_rectifier_battery.py (ALL PASS): ngspice bridge 9 V rms/4700 µF/1.2 A: 9.04 V pk, 1.54 V p-p (I/2fC 2.55 V,
  conservative), 4.3 A pulses; half-wave 3.82 V p-p; LDO headroom at −10 % mains 6.6 V; 3.9 W, θ_SA ≤ 18 K/W; Zener 220 Ω: ripple
  100 mV, 82 mV with 100 µF, 14 mV with 1000 µF; Peukert; runtime 2.45 h; cold droop table; collapse at V_oc < √(4RP) = 3.10 V;
  ngspice battery RC model 3.49 → 3.36 V. Edited 05/power-supplies (two subsections, worked ex. 5–6, TL;DR, questions, rules,
  mistakes, sources 7–11, gap note).

- 2026-10-13 — s3_bw_extension.py (ALL PASS): shunt peaking 1.57/1.72/1.80/1.85 × at m 0.32/0.414/0.5/0.71 (ngspice 1.722); series
  peaking 3.68 × (C1/C 0.55, m 0.32); T-coil Z_in = 1000.0 Ω flat, 2.83 × at k = 1/3 (2.72 at 0.5) — NOTE: my prior expectation
  was 2√2 at k = 0.5; numerics put it at k = 1/3, recorded as found; DA 4 × 20 mS: |S21| 2.00 = n gm Z0/2, −3 dB 12.8 GHz vs lumped
  4.0/1.33 GHz; balanced |S11| −122 dB centre, ≤ −15.8 dB ±10 %, S21 10.00 dB; gain-block NF 1.77 dB @ 433 MHz (.noise, 290 K);
  class B THD 22 %, AB 0.42 %. Edited 05/amplifier-topologies (two subsections, TL;DR, questions, rules, mistakes, gaps, sources
  8–10; adjusted the gain-block-as-LNA mistake bullet to reflect the 1.77 dB result).

- 2026-10-13 — Register: C80–C86 appended to §5, §3 rows marked "closed → §5 Cxx", change-log line added; all page#anchor
  references checked against headings. `tools/build_index.py --check` (rebuilds INDEX/FAQ): 0 broken links, 0 pages missing
  template sections. All six s3_*.py scripts re-run: ALL PASS; outputs in tools/verify/s3_*_output.txt. TASK COMPLETE.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | Web search summaries of NAMUR NE 43 (lesman.com, romilly.co.uk, others) | secondary | 4–20 mA fault levels | consistent; NAMUR text not read |
| 2 | TI TIDU020A comparator with hysteresis (search snippet) | app note | R_h > 100 R_p | snippet only |
| 3 | Energizer E91 datasheet (pdf, text extracted) | datasheet | alkaline IR 150–300 mΩ, −18…55 °C | primary |
| 4 | Zhang, Xu, Jow, Electrochim. Acta 49 (2004) 1057 (search) | peer-reviewed | R_ct dominates Li-ion resistance below −20 °C | abstract-level |
| 5 | Forum threads on 'op-amp attenuators' (search snippets; SE/E2E/AAC 403) | forum | the misconception only | anecdotal |

## Contradictions / discrepancies found
- 'Op Amps for Everyone' warns against inverting op-amp attenuators [via forum summaries]; derivation + ngspice show NG = 1 + R_F/R_in ≥ 1,
  so the warning applies only to decompensated parts / capacitive loads. Recorded in 05/op-amps recipe 3.
- 05/amplifier-topologies said resistive-feedback gain blocks have NF 3–5 dB; ngspice on the page's own single-SiGe stage gives 1.77 dB.
  Both hold (Darlington MMICs vs single high-fT device); wording qualified.
- Rectifier ripple I/2fC overestimates the simulated ripple by ~40 % at 76° conduction (conservative) — stated on the page.

## Knowledge gaps noticed (for later gap-filling)
- Battery cold-temperature resistance multipliers and usable-capacity fractions are assumptions bracketed by Zhang 2004 / a DOE
  report; the team's 1S/2S packs should be measured cold (pulsed ΔV/ΔI at 10 ms and 1 s) — candidate for GAP §7 (real-world data).
- Rectenna curve is an ngspice upper bound (no package/PCB loss); a measured HSMS-285x rectenna at 915 MHz would calibrate it.
- Distributed-amplifier line loss / optimum n and T-coil derivation not done (numerical only).
- NAMUR NE 43 and Valenta & Durgin 2014 cited via secondary summaries, not read in full.

## Cross-domain notes (things other domains should cover/link)
- 08/inductive-coupling-rfid-nfc-wpt far-field harvesting paragraph could link back to 05/diodes#rectennas (derived curve + exposure cap).
- 05/_index.md (not edited by S3): could list the new subsections (practical op-amp recipes, comparators/555, rectennas, batteries,
  bandwidth extension, output stages) in its domain FAQ.

## Resume instructions (what the next agent should do if this one is interrupted)
- State at pause: Step 0 done (all reading done, findings in Log above). Nothing written to kb/, gaps/ or tools/ yet. All 7 Plan
  items still open.
- Resume: (1) set Status back to in-progress; (2) load WebSearch/WebFetch (ToolSearch `select:WebSearch,WebFetch`) and get the few
  datasheet numbers still needed (battery chemistries/IR/cold: Energizer E91, Eneloop, A123 LiFePO4, a small LiPo; 4–20 mA NAMUR NE 43
  limits); (3) for each item in Plan order write tools/verify/s3_<topic>.py first (ngspice = /opt/homebrew/bin/ngspice, or
  tools/verify/analog_ngspice.py run_netlist), then Edit the target page (re-read first, add a new subsection + TL;DR bullet +
  Questions bullet + rules-table rows + Common-mistakes entries + sources; bump last_updated to the edit date); (4) after each item,
  move its row from GAP_REGISTER §3 to §5 (next free C-number, page#section, date) and tick the Plan box here; (5) final report.
- Before each edit grep the page for the new heading, in case a partial edit landed.
