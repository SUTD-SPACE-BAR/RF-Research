#!/usr/bin/env python3
"""
pcb_mixed_signal.py — numbers for kb/13-pcb-rf-layout-emc/mixed-signal-layout.md

  1. Desense budget: receiver noise floors (LoRa 125 kHz, NF 6 dB; GNSS L1 2.046 MHz, system NF 2 dB) and the
     allowed level of an in-band spur referred to the receiver input; LoRa sensitivity loss vs spur level (noise-like
     approximation) and the u-blox '6-12 dB above thermal noise' dynamic range for GNSS.
  2. Required isolation from a digital harmonic source (trace voltage from pcb_emc_radiation section 3) to the
     receiver input: source dBm (50-ohm equivalent) minus allowed spur level.
  3. How much isolation layout features give (order of magnitude, from this domain's scripts): fringing-field
     coupling 1/(1+(D/h)^2), one/two via-fence rows, a shield can seam, distance between antennas (Friis, near field).
  4. Shared-impedance error in an ADC ground: digital return current through a shared ground segment vs ADC LSB.
  5. SPI/UART/I2C edge harmonics at GNSS L1 for typical edge rates and the effect of series termination.

Run: python3 tools/verify/pcb_mixed_signal.py    (instant)
"""
import numpy as np

ok_all = True


def check(name, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def dbm_from_dbuv(dbuv):
    return dbuv - 107.0          # 50 ohm


print("=" * 96)
print("1. Receiver noise floors and allowed spur levels")
print("=" * 96)
lora_nf, lora_bw = 6.0, 125e3
lora_floor = -174 + 10 * np.log10(lora_bw) + lora_nf
gnss_nf, gnss_bw = 2.0, 2.046e6
gnss_floor = -174 + 10 * np.log10(gnss_bw) + gnss_nf
print(f"  LoRa 125 kHz, NF {lora_nf} dB: noise floor {lora_floor:.1f} dBm; SF12 sensitivity ~ floor - 20 dB = {lora_floor-20:.1f} dBm")
print(f"  GNSS L1 C/A 2.046 MHz, NF {gnss_nf} dB: noise floor {gnss_floor:.1f} dBm (signals ~15 dB below this)")
for spur_rel in [-10, -6, -3, 0, 3, 10]:
    deg = 10 * np.log10(1 + 10 ** (spur_rel / 10))
    print(f"  in-band interferer {spur_rel:+3d} dB relative to the noise floor -> noise-like desense {deg:4.1f} dB")
check("an interferer equal to the noise floor costs 3 dB of sensitivity", abs(10 * np.log10(2) - 3.01) < 0.01)
lora_allow = lora_floor - 6
gnss_allow = gnss_floor - 6
print(f"  allowed spur (<= 1 dB desense): LoRa {lora_allow:.1f} dBm, GNSS {gnss_allow:.1f} dBm at the receiver input")
print("  u-blox: GNSS tolerates jammers only ~6-12 dB above thermal noise before tracking degrades (1-2 bit ADCs).")

print("\n" + "=" * 96)
print("2. Required isolation from digital harmonics (source levels from pcb_emc_radiation section 3)")
print("=" * 96)
sources = [("40 MHz clock x23 = 920 MHz, 1 ns edges", 87.0), ("40 MHz clock x39 = 1560 MHz, 1 ns", 77.8),
           ("25 MHz SD clock x63 = 1575 MHz, 1 ns", 25.0), ("same, 5 ns edges (series R)", 0.0)]
# compute SD harmonic level with the same envelope model as pcb_emc_radiation
def env_dbuv(n, f0, tr, A=3.3, d=0.48):
    T = 1 / f0
    a = 2 * A * d * min(1, 1 / (np.pi * n * d)) * min(1, T / (np.pi * n * tr))
    return 20 * np.log10(a / np.sqrt(2) / 1e-6)


sd1 = env_dbuv(63, 25e6, 1e-9)
sd5 = env_dbuv(63, 25e6, 5e-9)
sources[2] = ("25 MHz SD clock x63 = 1575 MHz, 1 ns edges", sd1)
sources[3] = ("same, 5 ns edges (series R)", sd5)
for name, dbuv in sources:
    src = dbm_from_dbuv(dbuv)
    target = lora_allow if "920" in name else gnss_allow
    print(f"  {name:44s}: {dbuv:5.1f} dBuV = {src:6.1f} dBm (50-ohm equiv.) -> isolation needed {src-target:5.1f} dB")
need_sd = dbm_from_dbuv(sd1) - gnss_allow
check("an SD clock harmonic at L1 (1 ns edges) needs ~80 dB isolation to the GNSS input", 75 < need_sd < 90, f"({need_sd:.0f} dB)")

print("\n" + "=" * 96)
print("3. What layout features buy (orders of magnitude; see the cited scripts)")
print("=" * 96)
for lab, h in [("JLC7628 h=0.21 mm", 0.2104e-3), ("2L h=1.5 mm", 1.51e-3)]:
    vals = [f"{D*1e3:.0f} mm: {-20*np.log10(1/(1+(D/h)**2)):5.1f} dB" for D in [2e-3, 5e-3, 10e-3, 20e-3]]
    print(f"  trace-to-trace fringing decoupling ({lab}): " + ", ".join(vals))
print("  via fence, 0.3 mm vias at 2 mm (1575 MHz, plane pair): ~29 dB/row (pcb_via_fence.py)")
print("  shield-can seam, solder points 5 mm apart: ~26 dB at 1575 MHz (pcb_cavity_modes.py)")
for d in [0.05, 0.1, 0.3, 1.0]:
    fspl = 20 * np.log10(4 * np.pi * d * 1575.42e6 / 299792458)
    print(f"  free-space loss {d*100:5.0f} cm at 1575 MHz: {fspl:5.1f} dB (near field below ~3 cm: coupling is stronger)")
print("  -> 100+ dB needs several features in series: slow edges + inner-layer routing + distance + fence/can + antenna placement")

print("\n" + "=" * 96)
print("4. Shared ground impedance under an ADC")
print("=" * 96)
for bits, vref in [(12, 3.3), (16, 2.5), (24, 2.5)]:
    lsb = vref / 2**bits
    print(f"  {bits}-bit ADC, Vref {vref} V: LSB = {lsb*1e6:9.3f} uV")
Rseg = 1.72e-8 * 10e-3 / (2e-3 * 35e-6)
for I in [10e-3, 100e-3, 1.0]:
    print(f"  {I*1e3:6.0f} mA of digital/PA return through a 10 mm x 2 mm 1-oz ground trace ({Rseg*1e3:.2f} mOhm): {I*Rseg*1e6:8.1f} uV")
check("100 mA through a 2.5 mOhm shared ground segment exceeds a 16-bit LSB", 0.1 * Rseg > 2.5 / 2**16,
      f"({0.1*Rseg*1e6:.0f} uV vs {2.5/2**16*1e6:.1f} uV)")

print("\n" + "=" * 96)
print("5. Bus edges at GNSS L1")
print("=" * 96)
for name, f0 in [("SPI 10 MHz", 10e6), ("SPI 40 MHz", 40e6), ("I2C 400 kHz", 400e3), ("UART 921.6 kbaud (~460 kHz)", 460.8e3)]:
    n = int(round(1575.42e6 / f0))
    vals = [f"tr {tr*1e9:.0f} ns: {env_dbuv(n, f0, tr):5.1f} dBuV" for tr in [1e-9, 3e-9, 10e-9]]
    print(f"  {name:28s} harmonic {n:5d}: " + ", ".join(vals) + " (envelope; real spectra are lines spaced f0 apart)")
check("10 ns edges are ~20 dB quieter at L1 than 1 ns", abs(env_dbuv(158, 10e6, 1e-9) - env_dbuv(158, 10e6, 10e-9) - 20) < 0.1)

print("\nALL CHECKS PASSED" if ok_all else "\nSOME CHECKS FAILED")
