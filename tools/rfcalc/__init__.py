"""rfcalc — small, tested RF/analog calculators consolidated from the RF Physics knowledge base.

Modules
  units        dB / dBm / dBuV / field strength / VSWR / return loss / mismatch loss
  link         FSPL, Friis, EIRP/ERP, aperture, noise floor, LinkBudget
  propagation  Fresnel zones, earth bulge, radio horizon, LOS altitude, elevation angle
  noise        kTB, NF <-> Te, receiver cascade (NF/G/IIP3/P1dB), sensitivity, MDS, SFDR, C/N0
  matching     L / pi / T networks, component values, finite-Q loss, shunt stub, quarter-wave
  tline        microstrip (H-J, Wheeler, K-J dispersion), stripline, CPW/CPWG, coax
  skin         skin depth, surface resistance, roughness, round-wire AC resistance
  resonance    LC resonance, Q, bandwidth, loaded Q, resonator insertion loss
  radar        radar range equation, Albersheim, pulse & FMCW parameters, Doppler, RCS
  arrays       ULA array factor, steering phase, HPBW, grating lobes, directivity
  lora         LoRa symbol time, time on air (SX127x/SX126x), bit rate, sensitivity

Every module credits the tools/verify/ script it was ported from; tests in rfcalc/tests take their
expected values from the KB pages' worked examples. CLI: `python -m rfcalc --help` (run from tools/).
"""
__version__ = "0.1.0"

from . import (arrays, constants, link, lora, matching, noise, propagation, radar,  # noqa: F401
               resonance, skin, tline, units)
