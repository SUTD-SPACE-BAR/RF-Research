Avionics C V1.1 — Space Bar's **retired redundant/secondary** flight computer. Repo: `Avionics-C-Flight-Computer-Hardware` (KiCad, 4-layer JLC board, shrunk ~25% during design; team-designed). Recorded at feature level only, no circuitry. Flown alongside a primary like [[avionics-b-v3-primary-fc]]; overview in [[space-bar-flight-computer-capabilities]].

**Architecture:** single processor — ESP32-S3 module (with PSRAM) does everything: sensing, flight logic, pyro firing, logging, telemetry. Simpler and smaller than the primary; purpose is an independent backup recovery path.

**Sensors:**
- IMU ST LSM6DSV80X (6-DoF, includes a high-g accelerometer channel, ~80 g, alongside the low-g one — one chip covers both ranges)
- Barometer Bosch BMP390
- Magnetometer MMC5983MA
- GNSS u-blox MAX-M10S (L1, no RTK) with U.FL antenna connector and ESD protection; buffered UART so the GPS isn't back-powered when off; timepulse to MCU.

**Actuation:** 4 pyro channels, low-side logic-level FET per channel, each on its own 2-pin connector. No servo outputs. Pyro bus has **no firmware-controlled arm switch** — the pyro supply is selected by a header/jumper: from the main battery or from a **separate second pyro battery** (VBAT1/VBAT2), so pyro power can be isolated from logic power.

**Data & comms:**
- microSD + 8 MB SPI NOR flash for logging (shared SPI bus with multiple chip selects, spare CS available).
- LoRa telemetry: EBYTE E220-900T30D (900 MHz band, 1 W), with M0/M1/AUX to the MCU (mode pins also jumper-strappable). LoRa powered from a dedicated 5 V buck-boost, header-selectable to USB VBUS for bench testing.
- Micro-USB with ESD protection; BOOT/EN (reset) jumpers; spare UART/I²C headers.

**Power:** 1S battery on XT60; 3.3 V buck-boost main rail (1.5 A), 5 V buck-boost for the radio, plus an LDO so the board can run from USB alone. Power LED. **Powered by a 1S Li-ion/LiPo pack** (confirmed by the user).

**Contrast with the primary:** no second processor, no RTK, no servos, no CAN, no eFuse/ideal-diode protection chain, no software arming, lower-power radio in a different band (900 MHz vs 433 MHz — useful for running both links without interference).
