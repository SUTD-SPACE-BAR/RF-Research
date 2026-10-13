# >>> NEW SESSION? START HERE <<<  (updated 2026-10-14 — PROJECT COMPLETE; maintenance mode)

**State:** all research waves (1–6) are COMPLETE. Nothing is running or paused.
- 288 pages · ~62.8k lines · 2,913 FAQ questions · 22 domains (`INDEX.md`, `FAQ.md`)
- `GLOSSARY.md` ~1,086 terms (+ ambiguous-acronym list) · `kb/00-math-foundations/canonical-values-and-conventions.md`
- 361 verification scripts in `tools/verify/` · `tools/rfcalc/` calculator package (159 tests pass, incl. NTIA ITM port, `rfcalc itm`)
- Two independent consistency audits done and fixed (`gaps/D6-…`, `gaps/D7-…`); `tools/build_index.py --check`: 0 broken links,
  0 control characters, 0 missing template sections.
- Work queue `gaps/GAP_REGISTER.md`: 90 of 91 ranked items closed. Only open research item: **G-16-06** (CPWG fence distance,
  shield-can coupling, Floquet scan in openEMS). Everything else left is **real-world measurement** — §7 of the register and the
  pre-registered plan `kb/20-projects-recipes/validation-test-campaign.md` (40 tests).

**How to use this KB:** answer questions per `CLAUDE.md` (INDEX/FAQ → kb pages → answer at the user's level, cite pages). When a
question isn't covered or a measurement comes back: extend the page per `CONVENTIONS.md`, add a row to `gaps/GAP_REGISTER.md`, run
`python3 tools/build_index.py --check` and `python3 tools/glossary_harvest.py --build`.

**If you launch new research agents:** max 10 concurrent; no nested sub-agents (CONVENTIONS §6b); each keeps a log in
`research-logs/`; generic prompts in `research-logs/_TASK_SPECS.md`; graceful-pause protocol below.

**Known open questions worth a future pass** (all logged in GAP_REGISTER / agent logs): radial-stub openEMS vs models (10–23 %);
openEMS open-end Δl vs Kirschning–Jansen (11–18 %); openEMS directivity depends on boundary type; P.528 not implemented; Skolnik 3e
section numbers unverified; MIL-STD-461G/DO-160G level tables unverified; EBYTE air-rate→SF/BW mapping, module NF/IIP3, TX burst
current; plume attenuation; u-blox AND/OR export-limit logic; IMDA written rulings (LoRa class at 917–925, LoRa on 70 cm, "data
acquisition" at 866–869).

**Machine-specific things** (absent if the folder is copied elsewhere): openEMS at `~/opt/openEMS`, ngspice (Homebrew/KiCad), PyNEC
(pip), Qucs-S cask via tap `ra3xdh/qucs-s` (unsigned; optional; user may remove). The user's avionics context is snapshotted in
`sources/space-bar-avionics-context/`.

---

# HANDOFF — RF Physics knowledge base

**Read this first in any new session.** Then read CONVENTIONS.md (writing contract) and
INDEX.md (topic tree). Research agents' raw progress is in `research-logs/`.

## The task (from the user, 2026-09-27)

Marcus (SUTD Space Bar avionics — rocketry flight computers, LoRa telemetry, GNSS) wants to
build custom radios, radars, LoRa links, phased arrays, analog electronics and antennas. Analog/RF
is math-heavy and poorly documented, so he asked for:

1. A *huge* research sweep — textbooks, peer-reviewed papers, standards, app notes, lecture notes,
   documentation, forum threads, video transcripts — covering everything needed to design these
   things: physics, math (derivable from any starting level), part selection, design parameters,
   tools & equipment, simulation (RF waveforms, EM effects, HF capacitance/inductance), and
   performance prediction (range, waveforms, energy distribution, link budgets).
   Peer-reviewed/textbook science first; forums are secondary.
2. Record it in this directory as an easy-to-navigate tree (FAQ-style) with documentation and
   linked sources, so future sessions can answer any question consistently with the research,
   framed for the user's level.
3. After the first research passes: sweep RF/radio/analog questions asked on forums/YouTube to
   find knowledge gaps; check the research for internal consistency (inconsistency = gap or
   misconception).
4. Max 10 research agents at a time (user raised the limit from 6 to 10 on 2026-09-27); agents must log work to files as they go.
5. Maintain this HANDOFF.md so future sessions can continue.

## How to answer the user's questions (for future sessions)

1. Find the topic in INDEX.md / FAQ.md → open the kb page(s) → answer consistent with them.
2. Frame for the user's stated level; offer derivations from the page's "The math" layers.
3. If the KB lacks it or is low-confidence: say so, research it, and add/extend the page
   (following CONVENTIONS.md), then log the addition in `gaps/GAP_REGISTER.md`.
4. User context: the Space Bar avionics knowledge base in `~/.claude/knowledge/space-bar-avionics/`
   describes his flight computers (EBYTE E22-400T33D 433 MHz 2 W and E220-900T30D 900 MHz 1 W
   LoRa modules, u-blox ZED-F9P / MAX-M10S GNSS, KiCad + JLCPCB). Use it for rocket-relevant
   examples.

## Plan and status

Up to 10 agents run concurrently (rolling: launch the next task as soon as one finishes). **Full task specs for every wave (and the standard agent
preamble) are in `research-logs/_TASK_SPECS.md`** — use them to (re)launch any task. Each agent task has an ID, owns specific kb/ folders, and writes a
log `research-logs/<ID>-*.md`. Status legend: ⬜ not started · 🔄 running · ✅ done · ⚠️ interrupted.

### Wave 1 — foundations
| ID | Scope (kb folders) | Status |
|---|---|---|
| W1-A1 | 00-math-foundations | ✅ (12 pages, 11 verify scripts) |
| W1-A2 | 01-circuit-theory, 04-real-components-hf | ✅ (16 pages, 16 verify scripts) |
| W1-A3 | 02-electromagnetics | ✅ (13 pages, 13 verify scripts) |
| W1-A4 | 03-transmission-lines-matching | ✅ (11 pages, 13 verify scripts incl. own 2-D FD field solver) |
| W1-A5 | 07-noise-linearity, 09-propagation-link-budget | ✅ (19 pages, 19 verify scripts) |
| W1-A6 | 08-antennas | ✅ (15 pages, 11 verify scripts incl. own thin-wire MoM) |

### Wave 2 — systems and circuits
| ID | Scope | Status |
|---|---|---|
| W2-B1 | 05-analog-electronics | ✅ (12 pages, 12 verify scripts; SPICE via KiCad's ngspice) |
| W2-B2 | 06-rf-circuits | ✅ (14 pages, 16 verify scripts incl. optimised LNAs from real S/noise params) |
| W2-B3 | 10-comms-modulation | ✅ (11 pages, 12 verify scripts) |
| W2-B7 | 14-sdr-dsp | ✅ (10 pages, 10 verify scripts) |
| W2-B4 | 11-radar | ✅ (11 pages, 11 verify scripts) |
| W2-B5 | 12-phased-arrays | ✅ (9 pages, 9 verify scripts) |
| W2-B6 | 15-lora-ism-radios | ✅ (10 pages, 6 verify scripts) |

### Wave 3 — practice
| ID | Scope | Status |
|---|---|---|
| W3-C1 | 13-pcb-rf-layout-emc | ✅ (12 pages, 10 verify scripts; canonical 50 Ω width table) |
| W3-C2 | 16-simulation-tools + tools/ (runnable calculators) | ✅ (10 pages; rfcalc 12 modules, 142 tests pass; ngspice/PyNEC/openEMS installed) |
| W3-C3 | 17-test-measurement | ✅ (13 pages, 12 verify scripts) |
| W3-C4 | 18-components-parts | ✅ (11 pages; LCSC data from local jlcparts snapshot 2026-04) |
| W3-C5 | 19-regulations-safety + GLOSSARY.md | ✅ (7 pages, 3 verify scripts; GLOSSARY deferred to Wave 6) |
| W3-C7 | 21-gnss (new domain) | ✅ (10 pages, 9 verify scripts) |
| W3-C6 | 20-projects-recipes | ✅ (10 recipes, each with proj_* script; preflight RF checker) |

### Wave 4 — gap analysis & consistency (writes only to gaps/)
| ID | Scope | Status |
|---|---|---|
| W4-D1 | Stack Exchange (EE, Ham, DSP) question sweep → gaps/D1-*.md | ✅ (686 classified from 6,792 harvested; 60% covered / 27% partial / 13% missing) |
| W4-D2 | Reddit (r/rfelectronics, r/amateurradio, r/antennas, r/RTLSDR, r/AskElectronics…) → gaps/D2-*.md | ✅ (695 classified from ~90k posts: 43.8% covered / 42.6% partial / 13.5% missing) |
| W4-D3 | EEVblog/ham forums/Hackaday + YouTube (comments & transcripts) → gaps/D3-*.md | ✅ (699 classified from ~6,300: 69% covered / 26% partial / 5% missing) |
| W4-D4 | Textbook ToC / university syllabus coverage check → gaps/D4-*.md | ✅ (28 sources; 1,725 sections: 69% covered / 21% shallow / 10% missing) |
| W4-D5 | RF interview/exam/problem-set question sweep → gaps/D5-*.md | ✅ (1326 Qs: 761 covered/243 partial/321 missing/1 KB-wrong; Extra pool 54% strict, 72% lenient) |
| W4-D6 | Internal consistency audit of all kb pages → gaps/D6-consistency-audit.md | ✅ (24 issues: 1 wrong, 6 inconsistent, 5 ambiguous, 12 cosmetic; canonical-values table) |

### New domain added 2026-09-29: 21-gnss (from W4-D1: GNSS receiver internals unplanned) — pages written in Wave 5

### Wave 5 — gap filling (by domain slices of gaps/GAP_REGISTER.md)
| ID | Scope | Status |
|---|---|---|
| W5-E2 | New 08 antenna pages (slot, HF wire, inductive/RFID/NFC/WPT, lens/reflectarray, multiband/wideband) + forum antenna Q&A | ✅ (6 new pages + Q&A in 10 pages; 45/50 pre-registered checks pass, misses reported) |
| W5-E3 | New 14 pages (signal identification/spectrum survey, SDR front-end protection) + 17 bench-measurement recipes from forum gaps | ✅ (3 pages: signal-ID/survey, SDR front-end protection, bench recipes; 82/82 checks) |
| W5-E4 | Practical HF/VHF propagation pages in 09 (space weather, HF modes/prediction, ducting/Es/TEP/meteor, ground wave) — D5 E3/G3 failures | ✅ (4 pages; E3/G3 self-rescored 100%; ITU/NTIA reference codes matched) |
| W5-E5 | Estimation pack: z-transform, estimation/CRB, Kalman (00); radar tracking/monopulse (11); multiple access/duplexing (10) | ✅ (5 pages, 5 scripts ALL PASS) |
| W5-E6 | Beginner on-ramp: 00 rf-learning-roadmap + rf-concepts-for-beginners; 20 beginner-project-ladder; 14 sdr-gain-staging-and-reception-recipes; 15 choosing-and-judging-lora-antennas; 19 non-ionising section | ✅ (5 pages + 15/19 edits; 90/90 checks) |
| W5-E7 | 06 gap pack: AGC, PA control/ALC/sequencing, duplexers/diplexers/crystal filters, co-site IMD, ISF phase noise + g-sensitivity, modulators/detectors, Wilkinson non-ideal, PA linearisation | ✅ (6 pages + 2 additions, 8 scripts) |
| W5-E8 | 12 array synthesis, conformal/cylindrical arrays, Yagi stacking; 11 pulse-Doppler data cube & PRF regimes | ✅ (4 pages, 4 scripts) |
| W5-G0 | Build gaps/GAP_REGISTER.md (merge D1–D6 + agent gaps + deferred; rank; propose fill slices) | ✅ (gaps/GAP_REGISTER.md: 214 items, 103 open; slices S1–S18) |
| W5-E9 | Apply D6 consistency fixes (not 13/20) + new kb/00 canonical-values-and-conventions page | ✅ (all 24 D6 issues + extras closed; canonical-values-and-conventions page + fix_canonical_values.py) |
| W5-E10 | Practical pack: 15 LoRa mesh capacity; 11 radar applications (GPR/through-wall/Wi-Fi/harmonic/RCWL-0516); 17 interference hunting & RF immunity; 03 antenna tuners/ATUs; 18 coax & connector practicalities; 19 regulatory FAQ misc | ✅ (6 pages, 6 scripts) |
| W5-E11 | Advanced theory pack: 03 microstrip discontinuities; 02 Green's functions/integral equations; 17 cavity perturbation & permittivity measurement; 07 Volterra; 10 MIMO capacity/channel estimation; 13 digital termination & crosstalk | ✅ (6 pages; 92/102 pre-registered checks pass, misses reported) |
| W6-F2 | 20/validation-test-campaign.md (pre-registered test catalogue from KB predictions + §7 needs-data) | ✅ (40 pre-registered tests; f2_campaign_predictions.py 28/28) |
| W5-S1 | GAP_REGISTER slice S1: recovery & rocket-link practice | ✅ (7 items closed, 5 scripts 35/35) |
| W5-S2 | GAP_REGISTER slice S2: station safety, spectrum vocabulary, analogue-mode details | ✅ (6 items closed, 3 scripts) |
| W5-S3 | GAP_REGISTER slice S3: analog fundamentals in 05 | ✅ (7 items closed, 6 ngspice scripts) |
| W5-S10 | GAP_REGISTER slice S10: test & measurement practice | ✅ (6 items closed + new 17/basic-bench-instruments) |
| W5-S12 | GAP_REGISTER slice S12: antenna residuals in 08 | ✅ (7 items closed, 8 pages extended, 6 scripts) |
| W5-E12 | Quick fixes: no radiating at GNSS L1; 905 MHz not SG; 2-layer thickness; LoRa CR notation; G_p in 18 | ✅ (5 fixes, 16 files; register C56–C60) |
| W5-S7 | GAP_REGISTER slice S7: receiver, noise & DSP depth | ✅ (6 items closed, 5 scripts) |
| W5-S11 | GAP_REGISTER slice S11: simulation & coverage prediction (openEMS team hardware, ITM/P.528 rfcalc module) | ✅ (4 items + partial G-16-01; openEMS team-hardware sims; rfcalc itm; 14/42 pre-registered misses reported) |
| W5-S4 | GAP_REGISTER slice S4: components & everyday-EM folklore | ✅ (5 items closed, 5 scripts) |
| W5-S9 | GAP_REGISTER slice S9: radar & array residuals (+ radar display vocabulary) | ✅ (6 items + radar vocabulary closed, 6 scripts) |
| W5-S13 | GAP_REGISTER slice S13: GNSS & parts residuals (+ new 18/rf-passives-and-support-parts) | ✅ (4 items closed + new 18/rf-passives-and-support-parts) |
| W5-S16 | GAP_REGISTER slice S16: 13 EMC residuals | ✅ (4 items closed, 4 scripts) |
| W5-S14 | GAP_REGISTER slice S14: 06 receiver residuals (+ first-radio rung) | ✅ (5 items closed, 3 scripts) |
| W5-S15 | GAP_REGISTER slice S15: 06 synthesiser, filter & PA residuals | ✅ (5 items closed, 5 scripts; corrected PLL BW and LNA NFmin statements) |
| W5-S6 | GAP_REGISTER slice S6: transmission-line & matching practice | ✅ (8 items closed, 6 scripts; radial-stub openEMS miss reported) |
| W5-S8 | GAP_REGISTER slice S8: comms PHY extensions (+ new 10/weak-signal-digital-modes) | ✅ (6 items closed + new 10/weak-signal-digital-modes; 141/141 checks) |
| W5-S5 | GAP_REGISTER slice S5: graduate EM & TL theory (+ new 03/periodic-structures-ebg) | ✅ (4 items closed + new 03/periodic-structures-ebg; 3 pre-registered flange checks fail by design, reported) |
| W5-S17 | GAP_REGISTER slice S17: clean-up (new 09/satellite-links page, SG band fix, Doppler-rate v⊥²/R, P.372, Leeson −167, index chores, glossary rebuild) | ✅ (4 items + notes; new 09/satellite-links-doppler-tracking) |
| W5-S18 | GAP_REGISTER slice S18: quality pass (Level-1½ rungs, citation verification, leftovers) | ✅ (4 items; Level-1½ on 13 pages; citations fixed) |
| W5-S18b | Deferred S18 items in free domains + index to-dos + cross-links + glossary rebuild | ✅ (Level-1½ on 15 more pages; ~45 citations Crossref-checked; index/cross-links; anchor checker) |
| W5-E1 | Corrections: domain-15 regulatory fixes, 77 GHz SG check, crystals caveat, D1 misconceptions, cross-domain notes, broken links (edits only finished domains; defers rest to gaps/W5-E1-deferred.md) | ✅ (6 fixes; 94 cross-domain notes triaged; deferred → gaps/W5-E1-deferred.md) |
### Wave 6 — second consistency audit, FAQ/INDEX rebuild, final handoff
| ID | Scope | Status |
|---|---|---|
| W6-F1 | GLOSSARY.md (≥400 terms, harvest script, ambiguous-acronym list) | ✅ (1,085 terms; 44 ambiguous acronyms; tools/glossary_harvest.py --build) |
| W6-F3 | Second consistency audit → gaps/D7 | ✅ (26 issues; ~140 numbers re-derived) |
| W6-F4 | D7 fixes A (#1, #3–#7) | ✅ (21 pages) |
| W6-F5 | D7 fixes B (#2, #8–#13, scripts) | ✅ (15 pages + 13 tools files) |
| W6-F6 | Apply W5-S11 simulation results to 08/09/12/13/15/20 | ✅ (15 pages) |

## Orchestrator notes / decisions log
- 2026-10-03: **gaps/GAP_REGISTER.md is now the work queue.** Launch remaining slices S2–S18 in the register's suggested
  order as slots free (respect 'start' conditions and the orchestrator overlap note at the end of the register).
- 2026-09-27: Scaffold created (CONVENTIONS.md, INDEX.md, kb/ tree). Python 3 (anaconda) with
  numpy/scipy/sympy/matplotlib/scikit-rf 2.0.1 available; pdftotext available; ngspice/openEMS
  not installed yet (W3-C2 decides/installs).
- 2026-09-29: W3-C2 installed on the user's Mac: ngspice 47 (brew), PyNEC 2.3.4 (pip), openEMS built from
  official source into ~/opt/openEMS (326 MB, no sudo), and Qucs-S 26.1.0 via the maintainer's tap
  `ra3xdh/qucs-s` (unsigned; Gatekeeper warned the user; nothing depends on it — remove with
  `brew uninstall --cask qucs-s && brew untap ra3xdh/qucs-s`). KiCad's bundled ngspice 44.2 also works.
  Rule for future agents: no GUI launches, no casks/taps, no Gatekeeper changes without asking the user.
- 2026-09-27: `tools/build_index.py` regenerates INDEX.md + FAQ.md from `tools/taxonomy.md`
  (the planned-page list — edit it to plan pages) and page front-matter/"Questions this page
  answers". `--check` reports broken relative links and pages missing template sections.
  Run it after every wave.
- 2026-09-27 ~12:00 SGT: all 10 running agents were stopped by the account's API session limit
  (HTTP 429) after ~1 h; 43 pages + ~110 verification scripts were already on disk thanks to the
  logs. Resumed all 10 at 12:11 after the reset. Lesson: with 10 concurrent agents the usage
  limit, not context, is the binding constraint — expect interruptions and always resume from logs.
- 2026-09-27 ~17:10 SGT: second usage-limit stop (9 agents). Resumed via SendMessage at 17:23.
  Resuming a stopped agent with SendMessage (its transcript is retained) works well.
- Graceful-pause protocol (worked well 2026-09-29): SendMessage every running agent "PAUSE NOW … set
  Status paused, exact Resume instructions, stop, reply ≤50 words"; then kill any background jobs they
  left (ps aux | grep tools/verify|harvest|openEMS) so they don't wake; copy scratchpad data worth keeping.
- 2026-09-27 ~22:00 SGT: third usage-limit stop (all 10). Resumed all 10 via SendMessage on
  2026-09-29 01:31 SGT. State at resume: 160 pages, 29.7k lines, 1403 FAQ questions; complete:
  W1-A1..A6, W2-B1, B3, B6; in progress: B2, B4, B5, B7, C1, C2, C3, C4, C5, D1.

## CURRENT STATE: PAUSED (4th graceful pause, user request, 2026-10-03)
Pause sent to: W5-E7 (06 pack), W5-E8 (arrays/pulse-Doppler), W5-E10 (practical pack), W6-F1 (GLOSSARY), W5-E11
(advanced theory), W6-F2 (validation campaign), W5-S1, W5-S2, W5-S3, W5-S10 (register slices). Complete since last
pause: W3-C1, W4-D6, W5-E4, W5-E5, W5-E6, W5-E9, W5-G0. Next slices after these: S12, S7, S11, then S4, S5, S8, S9,
S13 (see GAP_REGISTER §6 + orchestrator note). **All 10 confirmed paused; no background jobs.** State: E7 3 pages (ISF, AGC, PA control); E8 2 pages (synthesis,
conformal) + 3 scripts; E10 3 pages (mesh capacity, radar apps, interference hunting); F1 GLOSSARY.md built (1049 terms;
ambiguous section + README link left); E11 2 scripts, no pages; F2 1 script, no page; S1/S2 research done, no edits;
S3/S10 reading only.
Resume = SendMessage "RESUME" to each.
### (earlier) RESUMED 2026-10-03 (all 10 woken)
### (previous) PAUSED (3rd graceful pause, user request, 2026-10-02 evening)
Pause sent to: W3-C1 (13 finishing + canonical width table), W5-E4 (09 practical propagation), W5-E5 (estimation
pack), W5-E6 (beginner on-ramp), W5-E7 (06 RF-circuit pack), W5-E8 (arrays/pulse-Doppler), W5-G0 (GAP_REGISTER),
W5-E9 (D6 fixes + canonical values page), W6-F1 (GLOSSARY), W5-E10 (practical pack). Complete since last pause:
W3-C6, W3-C7, W4-D3, W4-D6, W5-E2, W5-E3. **All 10 confirmed paused; no background jobs.** State: W3-C1 all writing done incl. canonical 50 Ω width table
(only a ~20–30 min pcb_via_fence.py run + closing left); W5-E4 1/4 pages; W5-E5 2/5 pages (+Kalman script);
W5-E6 2/5 pages; W5-E7 research only; W5-E8 script only; W5-G0 ~190 gaps clustered, register not written;
W5-E9 fixes #1–4, #13, CH24, C2 done; W6-F1 harvester run, no definitions; W5-E10 plan only.
Resume = SendMessage "RESUME" to each, or relaunch from logs.
### (earlier) RESUMED (all 10 woken via SendMessage after the 2026-10-02 pause)
### (previous) PAUSED AGAIN 2026-10-02 at the user's request
**All 10 confirmed paused; no background jobs running.** State at pause: W3-C1 12/12 pages (via-fence re-run +
antenna keep-out + D2 partials left); W3-C6 6/10 recipes (patch page needs mesh-refined numbers); W3-C7 9/10
pages; W4-D3 699 rows classified (summary/top-40 left); W4-D6 issues #1–2 written (Leeson = FkT/(2Ps) per Rubiola →
05/oscillators.md wrong), #3–10 verified not written; W5-E2 3 pages done; W5-E3 2 pages done (bench page left);
W5-E4/E5/E6 research only, no pages.
Pause sent to the 10 running tasks: W3-C1 (13), W3-C6 (20), W3-C7 (21), W4-D3 (forums/YT), W4-D6 (consistency
audit), W5-E2 (08 additions + antenna-ID guide), W5-E3 (14/17 additions), W5-E4 (09 practical propagation),
W5-E5 (estimation/z-transform/tracking/multiple access), W5-E6 (beginner on-ramp). Complete since last pause:
W4-D2, W4-D4, W4-D5, W5-E1. Resume = SendMessage "RESUME" to each (or relaunch from logs in a new session).
After these: merge gaps/D1–D6 + AGENT_REPORTED_GAPS + W5-E1-deferred into gaps/GAP_REGISTER.md; next fill slices
(array synthesis/conformal arrays/Yagi stacking; AGC/PA control/duplexers/crystal filters/co-site IMD; ISF phase
noise; interference hunting/RF immunity; pulse-Doppler data cube; microstrip discontinuities; cavity perturbation);
apply D6 fixes; Wave 6 (second audit, GLOSSARY.md, index rebuild).
### (earlier) RESUMED 2026-10-02 02:45 SGT (all 10 paused tasks woken via SendMessage)
### (previous) 2026-09-29: PAUSED GRACEFULLY at the user's request (usage limit nearly full)
The 10 in-flight tasks were told to finish their current edit, set log Status to "paused", write exact
resume instructions, and stop: W3-C1 (13-pcb), W3-C6 (20-projects), W3-C7 (21-gnss), W4-D2 (Reddit),
W4-D3 (forums/YouTube), W4-D4 (curriculum), W4-D5 (exams/interviews), W5-E1 (corrections), W5-E2 (08
antenna additions), W5-E3 (14/17 additions). To resume in this conversation: SendMessage each agent
"resume". In a NEW session: relaunch each with the standard preamble from research-logs/_TASK_SPECS.md
plus "you are resuming — read your log research-logs/<ID>-*.md first".
All 10 confirmed paused; orchestrator killed their leftover background jobs (Reddit harvesters, openEMS
GNSS-patch sweep, PCB via-fence run) so nothing wakes them. Raw sweep data copied from the session
scratchpad to research-logs/raw-harvest/ (logs may cite the old /private/tmp scratchpad path).
Still to launch after these: W4-D6 consistency audit (after 13/20/21 finish) → merge gaps/*.md into
gaps/GAP_REGISTER.md → further Wave 5 fill slices → Wave 6 (second audit, GLOSSARY.md, index rebuild).

## If you are resuming after an interruption
1. Check the status tables above, then `ls research-logs/` and read the "Status" and
   "Resume instructions" of any log not marked complete.
2. Relaunch interrupted tasks with the same ID and tell the agent to resume from its log.
3. Update this file's tables as tasks finish.
