#!/usr/bin/env python3
"""
gnss_timing_pps.py — verification for kb/21-gnss/gnss-timing-1pps.md

 1. Time-pulse quantisation ("sawtooth"): a receiver that can only place its pulse edge on a
    local clock grid of period Tq has an error uniform in +-Tq/2 that changes slowly (sawtooth);
    the receiver reports it in advance (u-blox UBX-TIM-TP qErr), so the host can remove it.
 2. Timestamping flight data with a PPS: MCU free-running timer with crystal error (+-20 ppm,
    temperature drift) captures PPS edges; linear mapping MCU ticks -> GNSS time.
    Errors for: (a) one-time sync, (b) per-second PPS with linear interpolation,
    (c) PPS lost for 30 s during boost/coast (hold-over on last drift estimate, with a
    frequency step from acceleration/temperature).
 3. Why NMEA/UBX message arrival time is a poor timestamp (latency of UART transfer at
    38400 vs 921600 baud for a typical epoch's output).
 4. Disciplining a local oscillator: first-order frequency-locked loop on PPS phase error; shows
    how loop time constant trades PPS jitter against oscillator wander.
Run: python3 tools/verify/gnss_timing_pps.py
"""
import numpy as np

rng = np.random.default_rng(11)
ok_all = True


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


# ---------------------------------------------------------------- 1. sawtooth
Tq = 1 / 48e6          # assume a 48 MHz pulse-generation clock (illustrative; product-specific)
n = 600
f_rx_err = 0.37e-6     # receiver clock frequency offset (not steered) -> pulse phase walks across grid
true_edges = np.arange(n) * 1.0
ideal = true_edges + 0.0
grid_phase = (np.arange(n) * f_rx_err) % Tq          # where the ideal edge falls relative to the grid
quant = ideal - grid_phase + np.where(grid_phase > Tq / 2, Tq, 0.0)
q_err = quant - ideal                                 # what TIM-TP qErr would report (sign convention aside)
white = rng.normal(0, 5e-9, n)                        # other receiver/antenna noise
pps = quant + white
raw = (pps - ideal) * 1e9
corr = (pps - q_err - ideal) * 1e9
print(f"1) sawtooth: grid {Tq*1e9:.1f} ns -> raw PPS error rms {raw.std():.2f} ns, peak {np.abs(raw).max():.1f} ns; "
      f"after qErr correction rms {corr.std():.2f} ns")
check("quantisation error is uniform within +-Tq/2 (rms ~ Tq/sqrt(12))",
      abs(np.std(q_err) - Tq / np.sqrt(12)) < 0.15 * Tq / np.sqrt(12) and np.abs(q_err).max() <= Tq / 2 + 1e-15)
check("qErr correction removes the sawtooth (rms -> white-noise floor)", abs(corr.std() - 5.0) < 0.6)

# ---------------------------------------------------------------- 2. MCU timestamping
f_nom = 150e6                     # MCU timer clock (Teensy 4.1 can clock its GPT/QTimer at 150 MHz)
ppm0 = 18.0                       # crystal offset
T = 120.0                         # seconds of flight log
t = np.arange(0, T, 1e-3)         # 1 kHz IMU samples, true GNSS time
# crystal: offset + slow temperature drift + frequency step at t = 40 s (ignition/accel, 0.3 ppm)
ppm = ppm0 + 0.02 * t / 60 + np.where(t > 40, 0.3, 0.0)
ticks = np.cumsum(np.r_[0, np.diff(t)] * f_nom * (1 + ppm * 1e-6))
pps_t = np.arange(0, T, 1.0)
pps_ticks = np.interp(pps_t, t, ticks) + rng.normal(0, 1, len(pps_t))   # +-1 tick capture jitter
pps_ticks += rng.normal(0, 30e-9 * f_nom, len(pps_t))                     # 30 ns rms PPS accuracy

# (a) one-time sync at t=0 with nominal frequency
est_a = ticks / f_nom
# (b) piecewise-linear interpolation between PPS captures
est_b = np.interp(ticks, pps_ticks, pps_t)
# (c) PPS missing 40..70 s: extrapolate with the last 5-s drift estimate
mask = (pps_t < 40) | (pps_t > 70)
pt, pk = pps_t[mask], pps_ticks[mask]
est_c = np.interp(ticks, pk, pt)
gap = (ticks > pk[pt < 40][-1]) & (ticks < pk[pt > 70][0])
k = np.where(pt < 40)[0][-5:]
slope = np.polyfit(pk[k], pt[k], 1)
est_c_hold = est_c.copy()
est_c_hold[gap] = np.polyval(slope, ticks[gap])
inside = t <= pps_t[-1]          # evaluate only between the first and last PPS captures
t, ticks, est_a, est_b, est_c, est_c_hold = (v[inside] for v in (t, ticks, est_a, est_b, est_c, est_c_hold))
for lab, e in [("(a) one sync, nominal clock", est_a), ("(b) PPS every second, interpolated", est_b),
               ("(c) 30-s PPS gap, held over (real time)", est_c_hold),
               ("(c') same gap, post-flight interpolation", est_c)]:
    err = (e - t) * 1e6
    print(f"   {lab:42s} max |error| {np.abs(err).max():10.2f} us   rms {err.std():9.3f} us")
err_a = np.abs(est_a - t).max(); err_b = np.abs(est_b - t).max(); err_h = np.abs(est_c_hold - t).max()
check(f"no PPS: 18 ppm crystal drifts {err_a*1e3:.1f} ms in 2 min", 1e-3 < err_a < 3e-3)
check("PPS each second keeps timestamps within ~1 us", err_b < 1e-6)
check("30-s hold-over after a 0.3 ppm step: error ~ 0.3 ppm x 30 s ~ 9 us", 5e-6 < err_h < 15e-6)

# ---------------------------------------------------------------- 3. message latency
for baud in [38400, 115200, 921600]:
    for nbytes, lab in [(100, "NAV-PVT only"), (1200, "default NMEA set (multi-GNSS GSV)")]:
        lat = nbytes * 10 / baud
        print(f"   {lab:34s} at {baud:6d} baud: {lat*1e3:7.1f} ms on the wire")
check("default NMEA load (~1.2 kB) at 38400 baud takes ~0.3 s per epoch -> >3 Hz impossible", 1200 * 10 / 38400 > 0.3)

# ---------------------------------------------------------------- 4. disciplining
def discipline_pi(tau, n_s=4000, pps_jit=30e-9, rw=2e-11):
    """2nd-order (PI) loop with time constant tau seconds; returns phase error history"""
    kp, ki = 2.0 / tau, 1.0 / tau ** 2
    x = 0.0; y = 5e-8; integ = 0.0; xs = []
    for _ in range(n_s):
        y += rw * rng.standard_normal()
        meas = x + pps_jit * rng.standard_normal()
        integ += ki * meas
        steer = kp * meas + integ
        x += (y - steer) * 1.0
        xs.append(x)
    return np.array(xs)


print("\n4) PI-disciplined oscillator, steady-state phase error rms (last 2000 s)")
res = {}
for tau in [3, 30, 300]:
    xs = discipline_pi(tau)
    res[tau] = np.std(xs[2000:]) * 1e9
    print(f"   loop time constant {tau:4d} s -> {res[tau]:7.1f} ns rms")
check("very short time constants copy PPS jitter; very long ones let the oscillator wander (optimum between)",
      res[30] < res[3] or res[30] < res[300])

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
