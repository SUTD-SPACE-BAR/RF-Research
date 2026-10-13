# CFD methods (Claude CFD repo + rocket fin campaign)

The team ran OpenFOAM CFD (local Apple Silicon Mac or NSCC ASPIRE2A HPC via SUTD, PBS) to get fin/aileron control authority for Avionics B's active control. The methodology was packaged as a reusable "cfd" skill; a separate propeller wind-tunnel project also uses it. Ethos: [[engineering-ethos]]; consumer side: [[simulation-validation-methods]].

## Verification, then validation

- Verification (numerics: grid and iterative convergence) and validation (vs experiment) are separate; a number is quotable only after both. An unconverged run that matches experiment is a coincidence.
- **Grid Convergence Index** on every production number (3+ meshes, constant refinement ratio). Check apparent order against the scheme's formal order; if it's off, the family isn't asymptotic — refine rather than quote. A 3-point GCI can lie; buy a 4th point for decisions. Declare Richardson extrapolation invalid when the data says so.
- **Convergence judged on integral quantities being flat**, not residuals alone; plus residual drop, mass imbalance, and "no oscillation masquerading as steady" (unsteady → URANS, report time-mean with amplitude).
- **Validation ladder** before production: reproduce published measured cases of increasing relevance (flat plate, sphere, NACA 0012, ONERA M6, Basic Finner). A missed rung can establish a *bias law* (e.g. low-Re fin lift over-read) that becomes a flag column on production rows.
- **A licence from a rung carries its preconditions** (y+ range, mesh limits, correctors), and production must assert them. Four defects came from applying a licence where its conditions quietly didn't hold (e.g. a laminar boundary layer produced by the wrong wall function, invisible to screens that compared runs against each other).
- Pre-registration: each rung has a write-once expected-answers file (known answers, pass criteria, pre-declared diagnostics and their interpretations) written before any solver iteration; results go in a VERDICT; follow-ups get addenda. Failed rungs grant no licence but can still license the machinery.
- Re-anchor a rung when the solver version or machine changes before trusting numbers there.
- Cheap external anchors first (a 6-minute flat plate answered what hours of production could only hint at). Test a planned fix on a case where it can be shown to matter before applying it.

## Production practice

- CAD → geometry prep (tessellation, patch partition, all reference quantities *measured from the geometry*, never typed) → case generator → restart-safe scheduler → per-case screens → collector (one evidence-rich row per case) → reports + manifest.
- Mesh quality gates enforced and **fail on missing metrics** (a segfaulted checker yields empty metrics). Mesh quality columns travel with the data. Refinement set per feature, not per body.
- Per-case screens use **exact invariants** (symmetry zeros, closure against solver totals), with floors on a fixed physical scale; per-part oscillation gated separately from totals.
- Measure mesher realisation scatter (the mesher isn't symmetry-preserving and is stochastic); never compare single cases more finely than the scatter.
- Every anomaly gets an ID and disposition in a CONSISTENCY_LOG.
- Success = the solver's end marker in the log, never the exit code. Tools refuse partial/unfinished data.
- Traps get fixed inside tools (restart file naming, time-dir lexical sort, silent no-op restarts, etc.).

## Delivery contract (between CFD producer and flight-software consumer)

- Deliver a machine-readable manifest (reference quantities measured from geometry, campaign name correct), a cases table with convergence evidence, oscillation %, residuals, mesh band and bias flags per row, QUALITY/VERDICT reports, and the consistency log.
- Explicit **"not delivered"** list: quantities proven irreproducible (e.g. per-fin windward/leeward split, absolute drag without prism layers, a Mach band with an asymmetric wake state).
- Bands on vehicle-level numbers: mesh band + configuration band, cross-checked against closed-form theory (Barrowman, Prandtl-Glauert) and an **independent reduction** in a different codebase/session.
- Consumer side: re-derive every consumer quantity from the raw cases table (not the producer's derived files); drop non-converged rows rather than averaging them; record the delivery path in the generated table; keep superseded deliveries as an audit trail; watch sign/mirror conventions between CFD and firmware (settle physical sense on the bench).
- Consumer requests are written as briefings: what's needed in one sentence, why (which model assumption is false), the exact grid of cases, a priority order if not all affordable, requirements on the rows, and what is NOT being asked for.
- Honest residual risk: bias common to all RANS on a configuration is only retired by wind tunnel or instrumented flight — say so.

## Compute

- Ask which backend (local Mac or HPC) at session start if not stated. HPC: modules, batch scheduler, site MPI; reduction stays local; Claude can't SSH so jobs are handed over as scripts.
- macOS toolchain traps (bundled shell, library paths, MPI teardown signals) are fenced in a wrapper tool.
