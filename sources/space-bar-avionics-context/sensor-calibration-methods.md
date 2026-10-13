# Sensor characterisation & calibration methods

From Avionics B's sensor calibration campaign (2026-08/09). Transferable to any IMU/mag/baro stack. Ethos: [[engineering-ethos]].

## What was characterised

- **Gyro**: bias instability and angle random walk (Allan variance, multiple independent runs), white noise per sample, turn-on bias repeatability across power cycles, true output rate, g-sensitivity, and thermal coefficient. Result: bias instability far better than the sim assumed, so the gyro error budget collapsed onto temperature — measure before budgeting.
- **Accelerometers**: bias/scale (six-position), thermal (measured, immaterial).
- **Magnetometer**: hard iron and soft iron **on the assembled airframe** (the vehicle's own metal dominates; bench-board numbers don't transfer), thermal, polarity, axis mapping.
- **Barometer and loop timing.**
- Continuous gyro bias tracking while on the pad; accelerometer self-test at boot.

## Methods that worked

- **Dedicated calibration firmware/mode** (on a separate branch), logging raw data to storage; analysis in a script that produces a report with confidence per quantity.
- **Thermal runs from a genuinely cold start** covering the real operating band (cold boot to hot pad), long duration (hours). Heat-soak the vehicle's actual pad scenario.
- **Mount rigidly (clamped).** A board on a cushion sank as it warmed, creating fake "drift" of up to 10°. Diagnostic: a thermal effect reverses with temperature; creep doesn't. Compute gravity-direction creep per run and withhold fits above a threshold.
- **Dip-angle test** for magnetometer axis/polarity errors: gravity and the geomagnetic field are both world-fixed, so the angle between accel and corrected mag vectors must be constant in every orientation. Try every signed axis permutation; the correct one minimises dip scatter. Cross-check the mean against the local IGRF/WMM inclination. This is the only check that can see an axis error — ellipsoid fits are rotation-invariant and blind to it.
- Sensor handedness: don't assume every sensor's marked axes are right-handed (one magnetometer's marked triad is left-handed); verify from the datasheet figure with vector arithmetic.
- Magnetometer SET/RESET polarity must be known and controlled; sign errors are invisible to magnitude and ellipsoid checks.
- Verify relative orientation of all sensors against the PCB and confirm in firmware.
- Detect power-cycle session boundaries so turn-on bias doesn't contaminate pooled fits.
- Before shipping a correction, simulate whether it matters for flight (e.g. "can we fly with this defect?" answered by simulation).

## Guards against confident wrong numbers (each added after a real mistake)

- Thermal coefficients require a minimum temperature span and R² threshold, else report "none".
- Fit both simple and complex models (3-param vs 9-param ellipsoid); let the residual choose.
- Six-position fits only for sensors with a known reference aligned to the board faces (not the geomagnetic field).
- Bootstrap confidence intervals on every parameter; withhold undetermined ones from flight headers.
- Quadratic-fit linear terms are slopes *at the reference temperature*; always evaluate local slope at a fixed temperature before comparing runs.
- Measure the operating point instead of assuming it — it mattered more than the coefficient size.
- Don't inherit conclusions ("immune to hard iron") from tests whose conditions don't match.
- Clean output folders so stale plots can't sit next to current ones; end reports with a manifest.
- A calibration headline number was wrong three times; each time the fix was checking what the correction would actually be applied to.

## Test-firmware hygiene

- No interactive prompts in long tests (one parked a 75-minute session); no "any key stops the run".
- Long stages must print progress so they're distinguishable from a hang.
- Use a timer that won't wrap during long runs (µs counters wrap at ~71 min).
- Reject implausible first reads (e.g. a zero register decoding to −75 °C).
- Every calibration constant belongs to one board; record which.
