# Engineering ethos and tenets — Space Bar avionics & CFD

Distilled from the Avionics B flight software repo and the Claude CFD repo (2026-07 to 2026-09). These are the rules the team worked under; apply them to any future flight computer, simulation, or test campaign. Related: [[simulation-validation-methods]], [[hil-bench-testing-methods]], [[sensor-calibration-methods]], [[cfd-methods]], [[flight-software-lessons]].

## Core tenets (ordered — earlier beats later)

1. **Validate against independent truth, never against yourself.** Compare against published measured data, exact invariants (symmetry zeros, closure identities, conservation), closed-form theory, or an independently written tool — never against a previous run of the same pipeline. Run-to-run agreement is blind to any error every run shares. "Two runs agree" proves nothing about a flaw they both have.
2. **Fix pass criteria before looking at the result.** Pre-register expected answers, limits, and even the interpretation of each outcome in a write-once file before running. Later ideas go in a dated addendum, never an edit.
3. **Research and test; don't trust memory, handoffs, or general knowledge.** Every load-bearing fact gets looked up, checked on the filesystem, or tested with a small experiment. Every handoff has carried at least one stale claim — including ones warning about stale claims. Verify a flag by reading the file, not the issue tracker.
4. **Measure before narrating a mechanism.** In one HIL session, eight plausible hypotheses for an oscillation were proposed and all eight died on measurement. What finally localised problems was structural facts ("amplitude does not scale with gain"), not stories.
5. **The recurring root cause is a premise nobody measured.** Assumed operating temperature, inherited "immunity" from a result whose conditions didn't match, axis maps reasoned from a diagram, an unstated right-handedness filter. Before quoting an effect, ask: what would this have to be compared against to be falsifiable? Then compute what it would actually do.
6. **One variable per test.** Use 2×2 factorials when two things may interact. Matched pairs that differ in exactly one thing isolate cost.
7. **Uncertainty travels with every number**, as data columns, not prose. "Not converged" and "not deliverable" are real results. Simulated is never "measured" — say "CFD-predicted" / "sim-predicted".
8. **Record everything in files immediately.** Nothing lives only in conversation. Anomalies get an ID and a written disposition (explained / banded / open / superseded). Corrections are appended, never silently edited — how a wrong answer was reached is often the most useful part. Keep "conclusions drawn and withdrawn" sections.
9. **Report faithfully.** Failures with their output, skipped steps declared, negative results at the top when they change what a consumer may do. Refusing to ship an irreproducible number is evidence for everything you do ship.
10. **Tools manage themselves; the human/Claude reviews and decides.** One command per intent; tools gate their own output, fail on *absent* evidence (a crashed checker must not read as a pass), refuse partial data, and print evidence. A trap discovered once is fixed in the tool at the source, with a comment saying what it cost — never left as a convention to remember.

## Documentation house style

- Dense, opinionated, tables over prose, traps called out by name.
- Every doc splits **"verified by running it"** vs **"NOT verified — do not assume"**. Compiling is not running.
- Confidence vocabulary on findings: Measured / Observed / Suspected / Untested / Derived.
- Findings get stable IDs carried forward across reviews (never renumbered), severity tiers (flight-blocking / high / medium / low), and a flat "everything still open" list at the top.
- Substantial sessions end by **updating the existing handoff doc** (per subsystem: protocol, estimator, calibration, simulation, HIL, code review), not writing a new one. Handoffs say where everything lives and end with "verify these claims against the filesystem before building on them."
- Record deliberate design decisions that look like defects, so they aren't re-raised.
- Every log/run says what it flew: a boot-time config line with every knob. A filename is a claim; the log's config line is evidence.
- ASCII-only in written technical files (a converter once destroyed minus signs across documents).

## Analysis habits

- Look at the distribution, not just the summary statistic ("13.6% at the stop" and "68.8% within ±10°" were the same run).
- A correlation across cases is not a mechanism.
- Check which signal the loop actually consumes (tilt is the integral of rate and hides the band an inner rate loop works in).
- Instrument the whole signal chain, not the symptom.
- A perfect-estimator (truth-fed) test cannot find an estimator bug.
- Report settled *and* all-sample figures, never just the flattering one; split launch transients from steady state.
- Never normalise by a quantity a symmetry can send to zero.
- Three decimal places imply a confidence the method must actually support; know when a number is a bound, not a measurement.
