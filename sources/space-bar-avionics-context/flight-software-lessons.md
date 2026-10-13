# Flight software architecture & lessons (Avionics B)

Functional lessons from the Avionics B flight software (Teensy flight processor + ESP32-S3 coprocessor), useful when specifying any future flight computer's firmware. No code recorded. Hardware context: [[avionics-b-v3-primary-fc]]. Methods: [[hil-bench-testing-methods]].

## What the flight software did

- Flight processor: sensor drivers, linear EKF (position/velocity, GPS/RTK-quality-weighted), attitude estimation (gyro integration + magnetometer fusion, gravity re-anchoring gated on |a|≈1 g), flight phase state machine (pad → boost → coast → apogee → drogue → main → landed), pyro deployment with continuity checks, 3-axis active control via aileron tabs (roll rate + hold vertical), servo slew limiting and per-fin trim, heartbeat with fault/status bitmask.
- Coprocessor: receives framed packets over a fast UART, logs to SD and NOR flash in parallel, downlinks decimated telemetry over LoRa, auto-configures the radio at boot, keeps a persistent boot log (reset reason, storage status) in NVS.
- Clock sync between processors (TIME_SYNC pairs); the clocks were found to *step*, not drift.
- Ground station parses the same packet format.

## Design lessons

- **Wire protocol has one source of truth**; mirrors (other processor's header, Python parser, docs) must be updated with it — a stale mirror logs plausible garbage that still passes CRC. Bump the protocol version on any wire-format change. Per-packet-type sequence counters and a source field make loss accounting unambiguous.
- **Telemetry downlink-only** by design (half-duplex radio transmits all flight, no ground→rocket commands). Bench operations that would be commands are done by flashing firmware. Downlink bandwidth must be budgeted against the *air rate*, with deterministic decimation rather than time-based rate limiting.
- **Diagnostics must not assert what they never checked** (a "logged to SD+NOR" message printed whether or not the queue accepted the frame). Functions should return which sinks accepted data; alarms should use rolling windows, not "every frame since boot failed".
- **Boot order is load-bearing**: never block between installing a UART driver and starting the task that drains it.
- Blocking boot work (e.g. dumping the flash backlog to SD) creates a **boot blackout** where nothing is logged — dangerous if the motor lights during it.
- Persistent write pointers committed periodically to NVS rewind at reset and can overwrite the previous session's tail — design log pointers to be crash-safe.
- Peripheral init failure (e.g. GPS after baud switch) must not disable the peripheral for the whole flight — use a non-blocking recovery ladder.
- Pyro: bounded retries, never an unbounded loop waiting for continuity to clear; every fire path guarded in bench builds; don't make arming decisions on an unproven continuity measurement.
- Control safety: latched abort beyond a tilt limit; control lockout outside the speed range the aero data covers.
- Separate bench/HIL/flight builds by one switch file; build scripts refuse ambiguous modes; verify the flight build is flag-clean before flashing.
- Calibration constants are per-board; builds should say which board they're for.
- Generated artefacts (aero tables) are never hand-edited, record their source, and have a check mode — but the check must be run against the source the artefact actually names, or its "stale, regenerate" advice can overwrite good data with placeholders.
- Code reviews are regenerated from scratch periodically, re-reading every carried-forward finding at its cited line; stale "open" findings and silently lost fixes were both found this way.
