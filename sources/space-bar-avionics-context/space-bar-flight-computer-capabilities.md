The user (Marcus Quek) is on the Space Bar avionics team (SUTD, GitHub org SUTD-SPACE-BAR), which designs rocketry flight computers in KiCad, fabbed/assembled at JLCPCB. Past boards: [[avionics-b-v3-primary-fc]] (primary) and [[avionics-c-secondary-fc]] (redundant/secondary), both retired. Only features are recorded in memory — for circuit detail, open those repos.

**What the team's flight computers do in flight:**
- Sense: 6-DoF IMU, high-g accelerometry for boost, barometric altitude, magnetometer, GNSS position/velocity (primary had RTK).
- Estimate state and detect flight events (launch, burnout, apogee, descent) for recovery.
- Fire recovery pyros (drogue + main; boards carry 4 channels for spares/airstarts/separation), with continuity checking intended before arming.
- Active control (primary only): up to 10 PWM servo outputs with a dedicated servo power rail — e.g. canards/fins.
- Log everything at high rate to two stores (microSD + onboard NOR flash) so a lost/corrupted card doesn't lose the flight.
- Downlink live telemetry over long-range LoRa (EBYTE modules; 433 MHz on primary, 900 MHz on secondary).
- Run as a primary + independent secondary pair for recovery redundancy (separate MCU, sensors, radio, and optionally pyro battery).

**Recurring hardware patterns:**
- MCUs: Teensy 4.1 for heavy GNC; ESP32-S3 (with PSRAM) for logging/telemetry or as a single all-in-one MCU on the backup.
- Sensor redundancy by overlapping range (low-g IMU + high-g accel) rather than duplicate parts.
- Pyro: low-side FET per channel; the primary adds a firmware-controlled high-side arm and pyro-current sensing, the secondary uses jumper-selected pyro supply with optional dedicated pyro battery.
- Power: battery (2S on primary B, 1S on XT60 on secondary C) plus USB bench power; buck/buck-boost regulators; primary adds TVS + reverse-polarity + eFuse protection and a latching power button (cannot be turned off in flight except by unplugging).
- Expansion: breakout headers exposing spare UART/SPI/I²C/GPIO; GPS on a swappable daughterboard (primary); CAN FD available but never exercised.

See [[flight-computer-design-lessons]] for hardware lessons, [[flight-software-lessons]] for firmware lessons, and [[engineering-ethos]] plus the methods files for how the team simulates, tests and characterises.
