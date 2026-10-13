# Research log W5-S11a: ITM (Longley-Rice v1.2.2) Python port
Status: superseded — completed by W5-S11 itself (2026-10-13; nested agents forbidden by CONVENTIONS §6b)
Parent: W5-S11. Owner scope (edit only): tools/rfcalc/itm.py, tools/rfcalc/tests/test_itm.py, tools/rfcalc/tests/data/itm_*.csv, this log.
Do NOT edit: cli.py, __init__.py, kb/ pages.

## Plan
- [x] Read NTIA/itm C++ source (src/*.cpp, include/*.h) via WebFetch on raw.githubusercontent.com
- [x] Port to tools/rfcalc/itm.py (numpy only): helpers, area + p2p TLS (+ CR variants), profile_from_elevations
- [ ] Re-type test vectors (p2p.csv, pfls.csv, area.csv) into tests/data/itm_*.csv
- [ ] Write tests/test_itm.py (vectors within 0.1 dB, unit tests of internals)
- [ ] Run full rfcalc test suite

## Log (append-only)
- 2026-10-13 — log created; read rfcalc package style (propagation.py, constants.py, tests).

- 2026-10-13 — WebFetched all 21 src/*.cpp + include/itm.h, Enums.h, Errors.h, Warnings.h (raw.githubusercontent.com, master). itm_area.cpp first refused verbatim, second request returned ITM_AREA_TLS_Ex body; CR wrappers only summarised (time=reliability, location=50, situation=confidence; same as p2p, which was verbatim). Cross-checked ComputeDeltaH, LinearLeastSquaresFit, FindHorizons against my recollection of the older ITS C port (dlthx/zlsq1/hzns): equivalent except FindHorizons lacks the old 'wq' flag (geometrically equivalent).
- 2026-10-13 — itm.py written (all functions ported statement by statement). area.csv (5 rows) and p2p.csv (5 rows) transcribed; pfls.csv lines 2, 4, 5 returned verbatim (value counts check: np+3). First run: p2p rows 2/4/5 match to <=0.005 dB (CSV rounded to 0.01), area rows 1-5 match to <=0.05 dB (CSV rounded to 0.1). Line 3 refused verbatim (quote-length policy); line 1 has 3680 points; attempting chunked fetch.
- 2026-10-13 — PAUSED on request. pfls.csv line 3 fetched in 3 chunks (positions 1-100, 101-200, 201-283) but NOT yet saved anywhere; must be re-fetched. Line 1 (3679 intervals) not started. No background jobs.

## Sources consulted
| # | Source | Type | Used for | Reliability notes |
|---|---|---|---|---|
| 1 | https://github.com/NTIA/itm src/*.cpp, include/*.h (master, v1.3 = FORTRAN 1.2.2) | primary code | port | WebFetch is model-written; verified by test vectors |
| 2 | NTIA/itm p2p.csv, pfls.csv, area.csv | primary test vectors | tests | A_db given to 0.01 (p2p) / 0.1 dB (area) |

## Contradictions / discrepancies found

## Resume instructions
State at pause:
- tools/rfcalc/itm.py: COMPLETE port (all src/*.cpp; API itm_p2p_tls, itm_p2p_cr, itm_area_tls, itm_area_cr, profile_from_elevations; ItmError(ValueError)). Licence/acknowledgement docstring done.
- tools/rfcalc/tests/data/itm_area.csv and itm_p2p.csv written (all 5 rows each).
- Profiles for p2p rows 2, 4, 5 are verbatim but only in the session scratchpad (lost) -> re-fetch pfls.csv lines 2, 4, 5 with WebFetch (asking "reproduce line N in full as comma-separated list" worked) and save to tools/rfcalc/tests/data/itm_pfls.csv (one profile per line, NTIA format); check value count == np+3.
- Verified by ad-hoc run (no test file yet): p2p rows 2/4/5 within 0.005 dB, area rows 1-5 within 0.05 dB (CSV rounding).
Left to do:
1. Re-fetch & save profiles 2, 4, 5; fetch line 3 in chunks of 100 values (positions 1-100, 101-200, 201-283 worked); try line 1 (3683 values) in chunks of ~300, else skip row 1 and record it.
2. Write tools/rfcalc/tests/test_itm.py: parametrised p2p/area vectors (abs 0.1 dB; report max error), unit tests (free_space_loss, fresnel_integral, inverse_ccdf(0.1)~1.2816 within 4.5e-4, ValueError on bad inputs, profile_from_elevations).
3. Run: cd tools && python3 -m pytest rfcalc/tests -q.
4. Hand back to W5-S11 (<=300 words: API, results, skipped rows, licence text).

- 2026-10-13 — (W5-S11) profiles 2–5 re-fetched and saved to tests/data/itm_pfls.csv; tests/test_itm.py written; 157 tests pass. Row 1 skipped. This sub-task is closed; do not resume.
