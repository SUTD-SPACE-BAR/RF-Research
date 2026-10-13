#!/usr/bin/env python3
"""
s17_leeson_check.py -- W5-S17 orchestrator note (c): re-check of the Leeson worked example in
kb/07-noise-linearity/phase-noise-and-jitter.md §(d): f0 433 MHz, QL 20, F 10 dB, Ps 0 dBm,
fc 10 kHz, Leeson's FkT/(2Ps) prefactor (the canonical one; 00/canonical-values).
Finding: -164 dBc/Hz is L(10 MHz) (= -163.6), not the floor; the floor is -167 dBc/Hz.
Run: python3 tools/verify/s17_leeson_check.py
"""
import math

k, T0 = 1.380649e-23, 290.0
F, Ps, f0, QL, fc = 10.0, 1e-3, 433e6, 20.0, 10e3


def leeson(fm, q=QL):
    return 10 * math.log10(F * k * T0 / (2 * Ps) * (1 + (f0 / (2 * q * fm)) ** 2) * (1 + fc / fm))


floor = 10 * math.log10(F * k * T0 / (2 * Ps))
expect = {1e4: -103, 1e5: -126, 1e6: -146, 1e7: -164}
ok = abs(floor - (-167)) < 0.1
for fm, e in expect.items():
    v = leeson(fm)
    ok &= abs(v - e) < 0.5
    print(f"  L({fm:9.0f} Hz) = {v:8.2f} dBc/Hz  (page: {e})")
print(f"  floor FkT/(2Ps) = {floor:.2f} dBc/Hz; L(100 MHz) = {leeson(1e8):.2f}; corner f0/2QL = {f0/(2*QL)/1e6:.2f} MHz")
print(f"  frequency where L is within 0.5 dB of the floor: "
      f"{next(fm for fm in [x*1e6 for x in range(1, 200)] if leeson(fm) - floor < 0.5)/1e6:.0f} MHz")
print(f"  QL = 50 at 100 kHz: {leeson(1e5, 50):.1f} dBc/Hz (page: -134)")
ok &= abs(leeson(1e5, 50) - (-134)) < 0.5
print("CHECK:", "PASS" if ok else "FAIL")
