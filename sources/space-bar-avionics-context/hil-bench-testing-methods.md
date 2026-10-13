# Hardware-in-the-loop and bench testing methods

How Avionics B was tested on real hardware. Transferable to future flight computers. Ethos: [[engineering-ethos]]; sim side: [[simulation-validation-methods]].

## Git discipline: never test on main

- `main` holds flight code only. Test harnesses, capture scripts, logs and debug flags live on `test/<topic>` branches forever.
- Keep the flight change and the scaffolding in **separate commits** so the flight commit can be cherry-picked to main alone.
- Each test branch has a `test/<topic>/VERIFICATION.md` (what was run, what it showed) and gitignored raw logs; commit only excerpts worth reading.
- **Nothing merges to main until hardware logs are clean.** Debug flags flipped for a test must be flipped back.
- **A cherry-pick into the working tree is not a landed change — only a commit is.** After promoting, grep the *committed* tree to confirm.
- Rebuild flight firmware from clean main before a launch and verify the binary hash matches what's flashed.

## HIL injection rig (the key test)

- Before it, every test fed the controller truth, so the real attitude estimator had never been in a closed loop with the controller. Three flight bugs were found within hours of closing that loop.
- Design: on the real board, **all sensor drivers run for real** (real bus transactions, real timing captured), then simulated values replace the readings, then the real estimator, phase machine, pyro logic, control law run, and servos physically move; commands go back into the sim.
- Injection point placement is load-bearing: after timing capture, before attitude estimation, before telemetry send (so what's downlinked is what flight software used).
- State explicitly what is real vs simulated. Force what the bench can't provide (e.g. GPS fix cadence indoors) while still polling the driver for its cost.
- Synthesised magnetometer needed when injecting gyro data — real mag reading a still bench board would contradict injected motion. Its constants are not a heading-accuracy test.
- **Pyro logic runs but the arming line is held off** in bench builds; gate LEDs show when channels would fire. Every fire path must be guarded for bench mode or bench runs fire live igniters. Bounded retry loops only.
- Every run prints a boot **CONFIG line** with every knob (vehicle, tilt, wind, turbulence seed, cant, gains). Comparison plots are generated from that line, never from whatever file happens to sit in an output folder.
- Host sim of the same case runs a perfect estimator with the identical control law, so "HIL vs host" measures what the real estimator and loop timing cost.
- Live dashboard **tails the log file, never opens the port** (only one process can hold a serial port; a second opener silently records nothing).
- Standard end-of-run figures: flight overview, control-active window, HIL vs host comparison, estimate-minus-truth.
- Disturbance matrix (tilts, wind, gusts) × seeds; each case a compile-time config.
- Measure loop tick budget and overruns; bus speed changes (e.g. I²C 100→400 kHz) can halve tick time.

## Capturing and reading bench logs

- Kill anything that might hold the serial ports **immediately before every flash and capture** (IDE serial monitors re-grab ports after flashing; captures then silently record nothing).
- **Capture from reset**, not a running board — the boot log holds the failures. Check the first timestamp to confirm it's a boot. Whether opening a USB-CDC port resets the MCU depends on DTR/RTS state — don't assume.
- Don't analyse a log while it's still being written; wait for the run-complete marker.
- **Grep every warning/error line first, unfiltered, then check what is MISSING**: list the lines a healthy boot must contain and confirm each is present. (Nine boots with no SD card were once declared clean because the reviewer grepped only for happy-path lines.)
- Check **drop counters, not just loss counters** (an SD queue once dropped 100% of frames while loss counters looked clean).
- Compute loss rates against the end-of-run frame count, not an intermediate denominator (inflated rates up to 2.6×).
- Discard physically impossible first reads from sensors (garbage on power-up) before statistics.
- Budget for boot-time work (e.g. a flash-to-SD backlog dump that blocks logging for up to minutes) before timing anything.
- Use `flash`, never full chip erase, when NVS holds persistent state (log pointers, session counters).
- Prefer reading ports directly (pyserial) over interactive monitors in scripts.

## Power and board bring-up testing

- Test power-up on **battery, not just USB** — a GPS-UART failure appeared on 3 of 11 battery power-ups and 0 of ~11 USB ones. Gate merges on repeated battery power-up trials (e.g. 22/22).
- Use fault injection on the bench to confirm or refute a proposed failure mechanism before fixing it.
- Build non-blocking recovery ladders for peripheral init failures rather than giving up for the whole flight.
- With multiple boards, **identify which board you're on** (MAC/serial) before trusting any calibration constant — constants are per-board.
- Document the order-sensitive procedures (e.g. which USB goes in first, when to press the power button) and which power configuration exercises which subsystem.
- SD cards: know the filesystem the firmware supports (FAT32/MBR here; exFAT/GPT fail); never hot-swap; have a card-detect.
- Verify pyro channels on the bench by pulsing triggers with the bus disarmed and watching indicator LEDs; verify igniters with a dedicated tester, not the board's continuity sense unless it's proven.
