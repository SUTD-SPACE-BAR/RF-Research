# RF Physics — a knowledge base for building radios, radars, antennas and analog/RF circuits

Start here:
- **INDEX.md** — the topic tree (22 domains, from maths foundations to GNSS and end-to-end projects).
- **FAQ.md** — every question the KB answers, grouped by domain, linked to the answering page.
- **[GLOSSARY.md](GLOSSARY.md)** — 1,000+ acronyms and terms in plain English, with ambiguous acronyms flagged (regenerate with `python3 tools/glossary_harvest.py --build`).
- **kb/** — the pages. Each domain folder has `_index.md` (reading order) and `_sources.md`.
- **kb/00-math-foundations/canonical-values-and-conventions.md** — the single source of truth for constants, sign conventions and Singapore regulatory limits.
- **tools/** — runnable Python calculators (`tools/rfcalc/`, e.g. `rfcalc itm`) and verification scripts (`tools/verify/`).
- **kb/20-projects-recipes/validation-test-campaign.md** — pre-registered bench/flight tests to confirm or refute the KB's predictions.
- **gaps/GAP_REGISTER.md** — what is known to be missing or unmeasured.
- **HANDOFF.md** — project status for continuing the research in a new session.
- **CONVENTIONS.md** — how pages are written and sourced.

Every page follows the same layout: questions answered → TL;DR → intuition → maths in levels
(algebra → calculus → general) → design equations → worked examples → practical notes →
common mistakes → how to simulate/verify → sources.

## Why the folder is only ~60 MB

It is plain text, which stores knowledge very densely:

| Part | Size | What it is |
|---|---|---|
| `kb/` (≈290 pages) | ~10 MB | The knowledge itself — about 1.3 million words of Markdown, roughly three or four large textbooks' worth |
| `tools/` | ~7 MB | Python calculators, check scripts and their saved outputs |
| `research-logs/` | ~40 MB | Mostly raw forum / Stack Exchange harvests (~36 MB) kept for auditing — not needed to answer questions |
| `FAQ.md`, `INDEX.md`, `GLOSSARY.md`, `gaps/` | ~2 MB | The navigation layer |

A page that derives, say, the Friis noise cascade with worked 433/915 MHz examples and sources is about 25 KB. Nothing is
a copy of a textbook: the pages are the research agents' own derivations, summaries and checked numbers, with citations
pointing to the originals.

## How Claude uses it

Claude does not load the whole folder — it would not fit in one conversation, and it doesn't need to. Each time you ask a
question in a session opened on this folder:

1. **`CLAUDE.md` loads automatically** and tells Claude this is a knowledge base: look the answer up here first.
2. **Claude searches `FAQ.md` / `INDEX.md`** for your question's keywords to find the right pages (the FAQ maps ~2,900
   questions to pages).
3. **It opens the 1–3 relevant pages** (each roughly 5–10k words), which fits comfortably alongside the conversation.
4. **It answers from those pages at your level.** Pages are layered from plain-English intuition up to full derivations, so
   it can pitch the explanation where you need it, and it cites the page so you can read further.
5. **If you need a number, it computes it** with `tools/rfcalc` or the page's verification script using your inputs,
   rather than doing mental arithmetic.

*Example:* "What spreading factor should I use for 915 MHz telemetry during boost?" → Claude finds the LoRa impairments page
and the canonical values page → answers SF ≤ 8 at 125 kHz for stations near the pad, explains that the rocket's
sweep past the station adds to the Doppler rate (the v⊥²/R term) → offers to re-run the Doppler script with your trajectory.

### Why this beats answering from general knowledge

- **Consistency.** One canonical page fixes constants, conventions and the Singapore limits, so answers don't drift between
  sessions.
- **Checked numbers.** Many common textbook and forum figures turned out to be wrong (e.g. the Kraus helix gain, EBYTE's
  sensitivity claims, the Leeson prefactor). The KB records the corrected values and why.
- **Your context.** The examples use the team's E22/E220 LoRa modules, ZED-F9P / MAX-M10S GNSS, JLCPCB stackups, Singapore
  IMDA rules and rocket flight profiles.
- **Honesty about unknowns.** Pages flag what is unverified or unmeasured, so Claude can say "the KB doesn't know this; here's
  how to measure it" instead of guessing.

### What it isn't

- **Not training.** Claude doesn't permanently learn the KB. Each new session starts fresh and re-reads only the pages it
  needs — the files *are* the memory.
- **Not a copy of every textbook.** Claude still brings its general knowledge; where the two disagree, the KB wins because its
  numbers were checked. If a question isn't covered, Claude should say so, research it, and add or extend a page (following
  `CONVENTIONS.md`) and record it in `gaps/GAP_REGISTER.md` — so the KB grows as you use it.

## Keeping it healthy

After any edit, run:

```bash
python3 tools/build_index.py --check
```

```bash
python3 tools/glossary_harvest.py --build
```

```bash
python3 -m pytest -q tools/rfcalc/tests
```

When bench or flight measurements come back, add them to the relevant page (a "Measured" subsection), mark the matching
prediction in `kb/20-projects-recipes/validation-test-campaign.md` as confirmed or refuted, and update `gaps/GAP_REGISTER.md`.
