#!/usr/bin/env python3
"""
W5-S4 verification for kb/04-real-components-hf/crystals-and-resonators.md (#32768-hz-watch-crystals-...):
  1. Why 32 768 Hz: 2^15 divider chain, AT-cut plate thickness at that frequency (frequency constant).
  2. Tuning-fork parabolic tempco: df/f = B (T - T0)^2 -> ppm and seconds/day vs temperature,
     incl. tolerance, B max and turnover spread (Epson FC-135: B -0.04 ppm/C^2 max, T0 25 +-5 C,
     +-20 ppm at 25 C; typical B -0.034).
  3. Daily temperature cycle at a launch site -> mean error.
  4. MCU internal RC oscillators vs crystal (STM32F412 HSI, STM32F417 LSI, ESP32-S3 RC) in ppm and s/day,
     against UART / USB-FS / CAN clock-tolerance needs.
  5. BVD numbers of a 32.768 kHz crystal (FC-135: C1 3.4 fF, C0 1.0 pF, R1 70 k max) -> L1, Q, pulling.
Run: python3 tools/verify/s4_rtc_crystal.py
"""
import numpy as np

DAY = 86400.0
print("=== 1. Why 32 768 Hz ===")
print(f"2^15 = {2**15} -> 15 divide-by-2 stages give exactly 1 Hz")
N_AT = 1.661  # MHz*mm, AT-cut thickness-shear frequency constant (standard quartz value, from knowledge)
print(f"AT-cut plate for 32.768 kHz would be {N_AT/0.032768:.1f} mm thick (vs ~0.05 mm for 32 MHz: {N_AT/32*1e3:.0f} um)")
print("-> 32 kHz uses a flexural tuning fork (f ~ w/L^2), a few mm long")

print("\n=== 2. Parabolic tempco of a tuning-fork crystal ===")
def err_ppm(T, B=-0.034, T0=25.0):
    return B * (T - T0) ** 2
print(" T (C)   typ ppm  typ s/day   worst ppm (B -0.04, T0 20/30, -20 ppm tol)  worst s/day")
for T in (35, 25, 15, 5, 0, -10, -20, -40, 60, 85):
    e = err_ppm(T)
    worst = min(err_ppm(T, -0.04, T0) for T0 in (20.0, 30.0)) - 20.0
    print(f"{T:5.0f}  {e:9.1f}  {e*1e-6*DAY:9.2f}   {worst:10.1f}  {worst*1e-6*DAY:12.2f}")
print(f"1 s/day = {1/DAY*1e6:.2f} ppm; 1 min/month (30 d) = {60/(30*DAY)*1e6:.1f} ppm")

print("\n=== 3. Launch-day temperature cycles (sinusoidal day, mean error) ===")
for lab, Tmin, Tmax in (("tropical (Singapore) 25-33 C", 25, 33), ("desert spring 5-30 C", 5, 30),
                        ("cold-soak winter -10-10 C", -10, 10), ("pad in direct sun 20-55 C", 20, 55)):
    t = np.linspace(0, 1, 10001)
    T = (Tmin + Tmax) / 2 + (Tmax - Tmin) / 2 * np.sin(2 * np.pi * t)
    e = np.mean(err_ppm(T))
    print(f"{lab:32s}: mean {e:6.1f} ppm = {e*1e-6*DAY:6.2f} s/day; over a 4 h pad wait {e*1e-6*4*3600*1e3:6.0f} ms")

print("\n=== 4. MCU internal RC vs crystal ===")
cases = [("STM32F412 HSI16, 25 C (factory trim)", 1.0), ("STM32F412 HSI16, -40..125 C (-8/+5.5 %)", 8.0),
         ("STM32F417 LSI 32 kHz (17-47 kHz)", 47.0), ("ESP32-S3 RC_SLOW 90-150 kHz, uncalibrated", 25.0),
         ("ESP32-S3 RC after calibration: 'several s/day' (3 s/day)", 3 / DAY * 100),
         ("32.768 kHz crystal at -10 C (typ)", abs(err_ppm(-10)) * 1e-4),
         ("+-20 ppm crystal tolerance", 20e-4), ("+-2.5 ppm TCXO", 2.5e-4)]
for lab, pct in cases:
    print(f"{lab:58s}: {pct:8.4f} %  = {pct*1e4:9.0f} ppm = {pct/100*DAY:9.1f} s/day")
print("needs: UART ~ +-2 % per side (8N1, 16x oversampling, Maxim AN2141), CAN ~ <=0.5 % (bit-timing dependent),"
      " USB full speed +-0.25 % (USB 2.0: 12 Mb/s +-0.25 %)")

print("\n=== 5. BVD of a 32.768 kHz tuning fork (Epson FC-135 typical) ===")
f, C1, C0, R1, CL = 32768.0, 3.4e-15, 1.0e-12, 70e3, 12.5e-12
w = 2 * np.pi * f
L1 = 1 / (w**2 * C1)
Q = 1 / (w * R1 * C1)
S = -C1 / (2 * (C0 + CL) ** 2)
print(f"L1 = {L1/1e3:.2f} kH, Q (R1 70 k max) = {Q:,.0f}, pulling = {S*1e-12*1e6:.1f} ppm/pF at CL 12.5 pF")
for cl in (6e-12, 7e-12, 9e-12, 12.5e-12):
    print(f"   CL {cl*1e12:4.1f} pF: pulling {-C1/(2*(C0+cl)**2)*1e-12*1e6:6.1f} ppm/pF;"
          f" equal caps for 2 pF stray = {2*(cl*1e12-2):4.1f} pF")
gm = 4 * R1 * w**2 * (C0 + CL) ** 2
print(f"g_m,crit (AN2867) at CL 12.5 pF = {gm*1e6:.2f} uA/V ; at 6 pF = {4*R1*w**2*(C0+6e-12)**2*1e6:.2f} uA/V")
