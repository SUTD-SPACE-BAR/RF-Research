# CONVENTIONS — how this knowledge base is written

Every research agent and every future session MUST follow this file. It is the contract that
keeps ~20 domains written by different agents coherent and machine-navigable.

## 1. Purpose and reader

The reader is Marcus (SUTD Space Bar avionics: rocketry flight computers, LoRa telemetry at
433/900 MHz, GNSS) who wants to design custom radios, radars, LoRa links, phased arrays,
antennas and analog/RF circuits. The knowledge base (KB) must let a future Claude session answer
*any* question in this space accurately, at *any* level of expertise — from "what is a decibel"
to deriving the noise figure of a cascaded receiver or the array factor of a steered planar array.

## 2. Directory layout

```
RF Physics/
  README.md            entry point for humans
  HANDOFF.md           state of the project + what to do next (for future sessions)
  CONVENTIONS.md       this file
  INDEX.md             master topic tree (auto-built by tools/build_index.py + hand edits)
  FAQ.md               master question tree (auto-built from "Questions this page answers")
  GLOSSARY.md          acronyms and terms
  kb/NN-domain/        one folder per domain; one Markdown page per topic
    _index.md          domain overview, reading order, page list, domain FAQ
    _sources.md        domain bibliography (full citations + URLs)
    topic-slug.md      topic pages
  research-logs/       one append-only log per agent task (crash-safe progress record)
  gaps/                gap-analysis and consistency-audit outputs
  sources/             consolidated bibliography
  tools/               runnable calculators/simulations (Python); tools/verify/ = checks
```

Domain ownership (who may create pages where) is assigned per agent task. Do not write pages
inside another agent's domain folder while that agent is running; instead, note the needed
cross-link in your research log under "Cross-domain notes".

## 3. Topic page template

File name: `kebab-case-slug.md`. One concept cluster per page; split pages > ~900 lines.

```markdown
---
title: <Human title>
domain: <NN-domain>
slug: <kebab-case-slug>
tags: [tag1, tag2]
prerequisites: [<relative paths to pages the reader should know first>]
related: [<relative paths>]
level: intro | intermediate | advanced | mixed
confidence: high | medium | low        # how well-sourced/verified the page is overall
last_updated: YYYY-MM-DD
---

# <Title>

## Questions this page answers
- <Plain-English question 1>?
- <Question 2>?
(These bullets are harvested automatically into FAQ.md — write them the way a person would
actually ask, e.g. "Why does my antenna's SWR change when I touch the cable?")

## TL;DR
3–8 bullets with the key facts and numbers.

## Intuition (no math)
Physical picture, analogies, what is really going on.

## The math
Derive from first principles in layers:
- Level 1: algebra-level statement of the result and what each symbol means (with units).
- Level 2: derivation with calculus/complex numbers; state every assumption.
- Level 3: advanced/general form, limits of validity, where approximations break.
Use LaTeX-style math in $...$ / $$...$$. Define every symbol and its SI unit.

## Design equations & rules of thumb
Quick-reference table: equation | when valid | typical values.

## Worked examples
At least one numeric example with realistic component values; show every step and the
final number with units. Prefer examples relevant to the reader (433/868/915 MHz LoRa,
1575.42 MHz GNSS, 2.4/5.8 GHz, 24/60/77 GHz radar, rocket telemetry ranges of 1–30 km).

## Practical notes
Parts, layout, measurement, what goes wrong in real hardware.

## Common mistakes & misconceptions
What people get wrong (harvested from forums) and the correct statement.

## How to simulate / verify
Which tool (SPICE, openEMS, NEC, scikit-rf, Python snippet) and how. Link tools/ scripts.

## Open questions / gaps
Anything not yet resolved or only single-sourced.

## Sources
Numbered list; cite inline as [1], [2]. Each entry: author, title, edition/year, section
or page, URL if public, and what it supports. Mark reliability: (textbook), (peer-reviewed),
(standard), (app note), (lecture notes), (forum — anecdotal), (video).
```

## 4. Quality rules (non-negotiable)

1. **Peer-reviewed / textbook first.** Prefer textbooks, IEEE/IET/arXiv papers, ITU-R/IEEE
   standards, university lecture notes, and manufacturer application notes/datasheets.
   Forums and videos are for *what people ask and what goes wrong*, not for physics claims.
   A physics claim sourced only from a forum must be marked `(unverified — forum)`.
2. **Verify, don't copy.** Where an equation can be checked numerically, check it (Python is
   available: numpy, scipy, sympy, matplotlib, scikit-rf). Put non-trivial check scripts in
   `tools/verify/<domain>_<topic>.py` and state in the page "verified by tools/verify/...".
   Cross-check key formulas against at least two independent sources where possible.
3. **Faithful reporting.** If sources disagree, say so explicitly in the page and in your
   research log under "Contradictions". Never paper over a discrepancy.
4. **No copyright reproduction.** Write everything in your own words. Derive math yourself.
   Never paste passages from textbooks/papers/web pages. Direct quotes: at most one short
   quote (< 15 words) per page, in quotation marks with attribution. Tables of *facts/numbers*
   (e.g. dielectric constants) are fine when re-typed and cited.
5. **Units and conventions.** SI units. Time-harmonic convention $e^{j\omega t}$ (engineering,
   $j=\sqrt{-1}$); note when a source uses the physics $e^{-i\omega t}$ convention. Powers in
   dBm referenced to 1 mW; noise at $T_0 = 290$ K ($kT_0 = -174$ dBm/Hz). Reflection
   coefficient $\Gamma$, S-parameters referenced to 50 Ω unless stated. Antenna gain in dBi
   unless stated (dBd = dBi − 2.15).
   **Canonical constants, design values and all sign/unit conventions (with the factor-of-2 traps) are in
   [kb/00-math-foundations/canonical-values-and-conventions.md](kb/00-math-foundations/canonical-values-and-conventions.md) — match it or state why not.**
6. **Numbers must be traceable.** Every typical value (e.g. "FR-4 εr ≈ 4.3–4.7 at 1 GHz") needs
   a source or a derivation.
7. **Cross-link generously** using relative Markdown links, e.g.
   `[Smith chart](../03-transmission-lines-matching/smith-chart.md)`. It is OK to link to a page
   that does not exist yet if it is in the planned page list (INDEX.md); otherwise note it.
8. **WebFetch returns a model-written summary, not the raw page** — it has produced wrong facts
   (reported by W2-B3). When a number or equation matters, ask WebFetch for the exact text/table
   around it, and cross-check against a second source or a derivation before recording it.
9. **Be concrete for the builder.** Always include practical consequences: what part, what
   value, what tolerance, what layout, what test.

## 5. Research-log protocol (crash safety — mandatory)

Each agent task owns exactly one log: `research-logs/<task-id>-<domain-short>.md`.
Create it FIRST, before any research. Update it at least after every page written and after
every ~3 sources read, so that if the session dies the next agent can resume.

```markdown
# Research log <task-id>: <domain>
Status: in-progress | complete | interrupted
Owner scope: <list of domain folders this task may write>

## Plan
- [ ] page-slug-1 — one line of intended content
- [x] page-slug-2 — done (link)

## Log (append-only)
- YYYY-MM-DD HH:MM — searched "<query>"; read <URL>; key facts: ...; used in <page>

## Sources consulted
| # | Source | Type | Used for | Reliability notes |

## Contradictions / discrepancies found
## Knowledge gaps noticed (for later gap-filling)
## Cross-domain notes (things other domains should cover/link)
## Resume instructions (what the next agent should do if this one is interrupted)
```

## 6. Domain `_index.md` template

```markdown
# <NN-domain> — <Domain name>
One-paragraph scope statement.
## Reading order (beginner → advanced)
## Pages
| Page | What it covers | Level | Confidence |
## Domain FAQ (top questions → page#section)
## Key textbooks and references for this domain (→ _sources.md)
## Known gaps
```

## 6b. No nested agents
Research agents must not spawn sub-agents (it breaks the 10-agent cap and the pause protocol). Do the work
yourself or record it in your log for the orchestrator. Do not spawn sub-agents.

## 7. Final report of an agent task

When finished, reply to the orchestrator in ≤ 250 words: pages written (count + slugs),
verification scripts written, top contradictions, top gaps, and anything left undone.
All detail belongs in the files, not in the reply.
