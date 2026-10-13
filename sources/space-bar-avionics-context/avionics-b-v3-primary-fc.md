Avionics B V3.1 — Space Bar's **retired primary** flight computer (only V3.1 was ever built). Repo: `Avionics-B-V3-Flight-Computer-Hardware` (KiCad; README.md + KNOWN_ISSUES.md there are the authoritative docs). Deliberately recorded at feature level only, no circuitry. Part of the fleet in [[space-bar-flight-computer-capabilities]]; companion board [[avionics-c-secondary-fc]]; lessons in [[flight-computer-design-lessons]].

**Architecture:** two processors on a 6-layer board.
- Teensy 4.1 (Cortex-M7 600 MHz) = flight processor: guidance/navigation/control, state estimation, pyro and servo actuation.
- ESP32-S3 module (16 MB flash, 8 MB PSRAM, external antenna) = coprocessor: datalogging and telemetry. Fed flight data from the Teensy over a fast UART link.
- GPS on a snap-off daughterboard so the receiver can be swapped.

**Sensors (redundancy by range, not duplication — overlapping ranges so the estimator can blend through boost without saturating):**
- 6-DoF IMU ICM-45686 (±32 g / ±4000 dps)
- High-g accel ADXL375 (±200 g)
- Very-high-g accel H3LIS331DL (±400 g) — footprint present, not fitted
- Barometer MS5611 (10–1200 mbar)
- Magnetometer MMC5983MA (±8 G)
- Pyro-bus current sensor (INA219)
- GNSS u-blox ZED-F9P (L1/L2, RTK-capable) with active antenna; flown antenna was L1-only. RTK corrections came via a separate transparent LoRa bridge straight into the GPS, not through either processor.

**Actuation:**
- 4 pyro channels (low-side fire, one shared software-controlled high-side arm, shared current sensing). Flight firmware used channels 1–2 (drogue/main). Pyro power from battery only.
- 10 servo/GPIO outputs (PWM-capable) plus a dedicated switched ~5 A servo rail, selectable 5 V or 6 V, enabled by firmware.

**Data & comms:**
- Dual datalogging written in parallel: microSD + 64 MB NOR flash on separate buses (NOR backlog dumped to SD on next boot).
- Telemetry: downlink-only LoRa, EBYTE E22-400T33D (433 MHz band, 2 W), on a breakout header that also exposes spare UART/SPI/I²C/GPIO.
- CAN FD transceiver fitted — never tested, not used by firmware.
- USB-C to the ESP32; Teensy programmed via its own USB.

**Power & protection:** 2S Li-ion/LiPo input (7.0–8.4 V) or USB. TVS transient clamp, reverse-polarity ideal diode, eFuse (UVLO/OVLO/~10 A current limit/soft-start, latch-off on fault). Three independently controlled load domains (logic, pyro, servo). Separate 3.3 V rails for sensors vs coprocessor. Momentary button powers on and self-latches — board can't be turned off in flight except by unplugging the battery (deliberate).

**Firmware boot flow as flown:** init sensors → pyro continuity check (bus disarmed) → arm pyro bus → enable servo rail. Bench build mode never arms.
