# Flight simulation, estimation & control validation methods

How Avionics B's software was simulated and validated before flight. Transferable to any future flight computer. Ethos: [[engineering-ethos]]. Hardware-side testing: [[hil-bench-testing-methods]].

## Architecture idea: one physics core, two roles

- A 6-DOF rocket simulator lives **in the flight firmware source** and is compiled both on the host and on the flight processor.
- On the bench it is the *plant* (synthesises sensor data, receives actuator commands back); earlier it also served as the estimator's process model. Same physics in both roles means bench-tuned behaviour matches what the estimator assumes. Keep the core free of bench-only assumptions.
- **Bench mode is not a separate program**: it is the real flight loop with exactly two substitutions (sensor frame synthesised; actuator commands fed back to the sim). So a bench run tests the whole *mission* — estimator, phase state machine, pyro decisions, control, telemetry — not just the control law.
- A single compile-time switch file selects flight vs bench vs HIL-injection. Never add a second mode switch. Build scripts refuse to build if the mode is ambiguous.

## Physics model contents (feature level)

Frames/quaternion state, standard atmosphere, thrust curve, axial force from Cd(Mach) lookup, normal force/body lift, restoring moment from CP/CG lookups, pitch/yaw damping (lift-based and crossflow), jet damping, roll damping, per-fin aileron forces from a shared CFD-derived fin-aero table, launch rail, wind + turbulence model, sensor models, parachute recovery. Documented in its own physics doc with parameter sources ("who supplies what").

## Cross-validation against independent simulators

- Fly the *same* vehicle in the in-house sim, **RocketPy**, **OpenRocket** (driven headless), and optionally **RASAero II** (best at transonic/supersonic; manual, Windows-only, file-based leg). Compare trajectory milestones (rail exit, max speed, apogee, impact), derived sensor streams (body specific force, rates, altitude), and control response.
- **Compile the real firmware simulator on the host** with a minimal hardware-API stub so the validated code *is* the flight code.
- **Matched-drag trick**: also run OpenRocket with total Cd overridden to match ours. That isolates dynamics + integrator from drag-model disagreement (8–25% on apogee). Expect ~1% agreement when matched. For transonic vehicles use the reference that shares the full Cd(M) curve.
- **Still air is deliberate** for cross-validation (tools have different wind models). Wind validation is a separate suite that first matches CP across tools.
- **Fleet of test vehicles** spanning the envelope (light min-diameter dart to heavy M-class; subsonic to transonic) plus the real vehicle. Synthetic vehicles exercise the *law* across inertias; only the real vehicle is a statement about real fins.
- Verify the vehicles actually match (wet mass, CG, margin printed by each tool) before trusting a comparison — otherwise you're comparing different rockets.
- Keep one canonical parameter sheet; a new vehicle must be added in every definition site (checklist).
- Watch for frame-convention bugs (ENU vs NED, body↔world transposes) — assert something physical (e.g. positive specific force on the rail) so a wrong transpose can't pass silently.
- Archive runs into dated results folders; regenerable output dirs are gitignored.

## Estimator validation suites (linear EKF and attitude separately)

- Run the **real estimator source** on the host; stub nothing but hardware APIs.
- Truth comes from a **different vehicle than the estimator believes in**.
- Synthetic sensors at exactly the noise sigmas the filter's R claims, plus dropouts, GPS/RTK degradation, sensor clipping, injected attitude error.
- **Deterministic**: fixed-seed PRNG, reruns byte-identical (md5-checked) so regressions are unambiguous.
- **Matched pairs** isolate causes (e.g. identical except for clipping).
- Split errors into launch transient vs steady state; drop artefact ticks (e.g. touchdown freeze).
- Case tables are the single source of truth, parsed by the analysis scripts so they can't drift.
- Linear error stays bounded (GPS measures position/velocity); attitude error grows unbounded (nothing measures attitude directly) — validate them in separate suites.

## Active control validation

- No external reference can fly a control loop, so every case is flown **control-OFF and control-ON against the same disturbance** (build misalignments, rail tilts, kicks, wind, gusts).
- **Derive gains and limits from mass properties** (inertia, fin geometry, measured fin authority). Only dimensionless ratios are hand-tuned; absolute constants tuned on one vehicle broke every other vehicle differently. Supplying the real vehicle's inertias should need no re-tuning.
- Integral terms expressed as time constants, floored by the measured loop dt so a late loop degrades gracefully instead of ringing.
- Authority scales with dynamic pressure; there's a minimum speed below which you can't hold vertical in wind. Control window = the range the fin data actually covers.
- Latching safety abort (e.g. tilt beyond 45° → neutralise surfaces, no re-enable).
- Size disturbances physically — a "disturbance" that is a full-authority command teaches nothing.
- Run many **turbulence seeds** (e.g. 8) before choosing a gain; a choice that wins on one seed may not survive eight.
- Model actuator reality: servo rate limits, slew limiting, PWM rate; check commanded rate vs what the servo can physically do.
- Never compare controlled vs uncontrolled on a case with nothing to correct (vertical launch in still air gives identical results).

## Aero data into flight code

- Fin aero table is **generated** from the CFD delivery by a script, never hand-edited; the header records which delivery it came from; a check mode verifies it's up to date against *that* delivery.
- A test drives the compiled table forward and inverse against the raw CFD rows.
- Refactors must be behaviour-preserving where they should be: verify bit-identical trajectories before/after.
- Know what the table does not cover (e.g. large deflection measured only at α=0) and treat it as flight-blocking until measured.
