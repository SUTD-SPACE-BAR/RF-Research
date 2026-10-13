# W5-E9 deferred and residual items (D6 consistency fixes, 2026-10-03)

Log: `research-logs/W5-E9-consistency-fixes.md`. Canonical page: `kb/00-math-foundations/canonical-values-and-conventions.md`.
Everything in D6 that was not provisional has been fixed. W3-C1's width table appeared and W3-C6 finished, so D6 #11, #12 and #21 were also
handled. The items below are what remains, grouped by who should pick them up.

## For W3-C1 (13-pcb-rf-layout-emc; not edited by W5-E9)
- No D6 value in 13 needed correction: 13 is now the canonical source for 50 Ω widths, and 03, 04, 08, 16 and 20 link to its table.
- Still open (measurement, D6 §4.9): cite the source of the JLC0216A 1.43 mm core (calculator template), and run a TDR measurement on a JLC 50 Ω coupon.

## For W3-C6 / Wave 6 (20-projects-recipes; surgical edits were made, pre-registered rows left alone)
- `20/gnss-front-end-design.md` test row G5 still says "On CH 0–6 (test only)", and `20/lna-design-walkthrough.md` L-T5 still says "≈ 7 dB est." for the RTL-SDR at L1. These are pre-registered predictions, so they were annotated but not rewritten. LSF measured 11.9 dB at 1280 MHz on a V3.
- `20/lora-rocket-telemetry-link.md` §3 table: the "433 MHz, 10 mW e.r.p." rows assume 10.5 dBm conducted. The E22-400T33D's lowest UART step is 24 dBm, so state how this is reached (≥ 13.5 dB pad, or the SPI module's power register).
- The default primary is now CH 24 (434.125 MHz) on line 54. The other tables still pair CH 23 with E220 CH 18, which is valid, but check that each table states its pairing.

## For agents still running (their pages are not yet in tools/taxonomy.md or link to planned pages)
- Slugs missing from `tools/taxonomy.md`: 06/agc-loops-and-receiver-gain-control and 06/oscillator-phase-noise-ltv-isf (W5-E7); 12/array-pattern-synthesis and 12/conformal-and-cylindrical-arrays (W5-E8); 11/radar-applications-gpr-through-wall-sensing, 15/lora-mesh-capacity-and-congestion and 21/gnss-receiver-integration-u-blox (W5-E10/E11).
- `build_index.py --check` (2026-10-03) shows 8 broken body links, all from those pages to pages they have planned but not yet written: 06 co-site/PA-control/duplexers, 19/regulatory-faq-misc and 12/stacking-and-arraying-yagis. A one-off front-matter check found 5 broken front-matter links to the same planned pages.

## For Wave 6 (second audit / tooling)
- Extend `tools/build_index.py --check` to validate front-matter `prerequisites`/`related` paths and `#anchor` fragments (D6 #23). W5-E9 ran a one-off scratch check, and the only anchor mismatches are pre-existing: `04/_index.md → ferrites-and-beads.md#level-3--the-bead-capacitor-resonance-and-damping` and `16/_index.md → spice-circuit-simulation.md#a--433-mhz-l-match-125--load-to-50--s-parameters`. The second one probably drops an "Ω" from the slug.
- `18/lna-pa-gain-block-mmics.md`: the MAX2659 and AT2659 IIP3/IP1dB cells (−5/−12, −5/−14 dBm) have not been checked against their electrical tables. They may be feature-list values too, the same issue BGA524 had (D6 #13).
- Lee–Hajimiri equation numbers (JSSC 2000, eqs. 11–12) were read only from surrounding text. Recheck them from a rendered PDF. The new 06/oscillator-phase-noise-ltv-isf page cites "eq. (12)".
- `gaps/AGENT_REPORTED_GAPS.md` still calls harris' Hamming 1.78 dB a "misprint". The KB now explains it as the 25/46 "exact Hamming" value (D6 #9), so the gap text should be updated when the register is next merged.
- D6 §4.9 measurement gaps remain open: RTL-SDR V4 (R828D), HackRF and Pluto NF at 915/1575 MHz; a measured landed-rocket path loss on Space Bar hardware; measured e.r.p. of the E220 at 21 dBm plus a pad.
- Optional: build a concrete Colpitts example that maps the Leeson definitions onto the Lee–Hajimiri ones (D6 §4.1).
