Functional lessons from [[avionics-b-v3-primary-fc]]'s KNOWN_ISSUES.md (as of 2026-09). Use when advising on requirements for a new board; see [[space-bar-flight-computer-capabilities]].

- **Pyro continuity sensing never worked** (result was effectively random), yet firmware used it to decide arming. Future boards need a continuity measurement that actually resolves an igniter, and arming shouldn't hinge on an unverified check.
- **Pyro bus not truly cold on USB power** (backfeed put a few volts on the battery/pyro rail). Design so pyro rails are provably dead unless battery is connected and armed.
- **Under-rated TVS parts on the pyro bus** for the pack voltage — check protection ratings against max pack voltage.
- **Magnetometer offset during flight loop** (~18% of samples) — suspected noise from sharing the processor's own regulator with sensors, and no supply filtering on the mag. Give sensors a clean, dedicated, filtered rail.
- **Dual-USB boot-order sensitivity** on a two-processor board — multiple 5 V sources (incl. the Teensy's own USB) need proper ORing.
- **Indicator LEDs driven straight from MCU pins over their current rating**; pyro FET gates driven at 3.3 V with no characterised on-resistance — use proper gate drive / logic-level FETs.
- **No SD card-detect** — add one.
- **I²C left at 100 kHz**; GPS I²C port doesn't support that speed.
- **Inter-processor UART dropped frames in periodic bursts** (cause unknown).
- **CAN fitted but never tested** — don't count features that were never exercised.
- **Documentation drift**: KiCad stackup didn't match the fabbed stackup; BOM/schematic didn't name the exact module variant. Keep the as-ordered truth in the repo.
- Deliberate (not defects): no off-switch in flight; eFuse latches off after a fault (an overload ends the flight); servo rail voltage jumper-selected.

Design-review methods learned on Avionics B V4 (2026-09-29, from the V4 power review; the board is still a plan, see the V4 repo's V4-POWER.md):

- **Check every rail MLCC against the manufacturer's DC-bias curve at its operating voltage.** Small X5R parts can keep under half their value (a 0402 1 µF keeps ~0.4–0.7 µF at 3.3–5 V). Regulator, LDO and USB limits are stated as *effective* capacitance, so a nominally compliant BOM can sit below the minimum. A higher voltage rating is not a reliable proxy; only the curve tells. TDK, Samsung and Murata publish curves; many small Chinese brands don't.
- **Choose ferrites by impedance-vs-frequency curve, not the 100 MHz figure.** A GHz-type bead can be near zero ohms at buck-noise frequencies. Rate current 3–5× the load, since impedance falls with DC current. Always damp a low-resistance bead that feeds a ceramic cap (a series resistor where current is small), or it resonates and amplifies noise.
- **Check the JLC part-number field name.** The fabrication plugin silently ignores unrecognised field names (e.g. "Supplier Part"), leaving JLC to pick the part.
- **Verify schematic edits by diffing exports**, not by eye: netlist connectivity, BOM, ERC, DRC with schematic parity, and per-symbol properties before and after. Raw DRC reports differ between runs (random IDs, arbitrary choice between stacked pads), so compare them normalised.

Added 2026-10-02, from the V4 Teensy re-pin and socket change (V4 repo's V4-TEENSY.md):

- **When re-pinning a board, check what every existing firmware build would drive onto each new net.** On V4 an unchanged V3.1 build would have armed the pyro bus (an idle-high chip select landed on the arm line) and fired a channel at boot (the servo-arm output landed on a fire line). Either choose a map that old builds cannot arm, or treat "old firmware on the new board" as a hazard that every branch must close before bring-up.
- **SMD module sockets cannot be butted end to end**, so plan one-pin gaps and keep those module pins unassigned. **A socketed module can be inserted rotated 180°**: silkscreen its outline and the USB end.
- **Check a module's socket placement against the last flown footprint**, not against a pinout read from memory; the old board file carries the proven geometry.
- **Keep every project library inside the project (`${KIPRJMOD}`).** An absolute library path broke silently when the project folder moved, and the affected part dropped off the board at the next update. Footprints from a library that only existed on one machine can be recovered from an old board file, which embeds them.
- **Docs drift from the schematic quickly**: a sweep against the netlist found a jumper safety rule, a capacitor count, a USB capacitance figure and several "open" items that no longer matched. Re-check docs against a fresh netlist export after each batch of edits.
