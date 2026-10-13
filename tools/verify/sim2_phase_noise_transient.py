#!/usr/bin/env python3
"""sim2_phase_noise_transient.py — oscillator phase noise end to end: a noisy transient simulation of a
433.92 MHz LC (van der Pol) oscillator -> phase extraction -> L(f) -> Leeson fit, compared with the KB's
canonical Leeson form. W5-S11, gap G-16-03. Page: kb/16-simulation-tools/rf-circuit-simulators-harmonic-balance.md
("Example 4 — phase noise from a noisy transient run").

Model (state v = tank voltage, iL = inductor current):
    C dv/dt = -v/R - iL + (G1 v - G3 v^3) + i_n(t)          L diL/dt = v
  * tank: L = 10 nH, C from f0 = 433.92 MHz, R = Q w0 L with Q = 30 (R = 817.9 ohm)
  * sustaining element: noiseless negative conductance G1 = 1.5/R with cubic limiting G3, chosen so the
    describing-function amplitude is A = 1 V peak:  A^2 = 4 (G1 - 1/R) / (3 G3)
  * noise current i_n: white, one-sided PSD 4 k T F / R (tank resistor at T = 290 K, plus active-device noise
    expressed as a noise factor F: F = 1 -> resistor only, F = 2 -> device adds as much again)
  * optional observation noise: white voltage, one-sided PSD 4 k T F R added to the observed v (the sustaining
    amplifier's own broadband noise seen at its input) — this produces Leeson's far-out floor
  * integrator: stochastic Heun (additive noise), 64 steps per carrier period; 16 independent realisations
    of 20 us each; phase from the analytic signal (FFT Hilbert), S_phi by Welch, L = S_phi / 2 (IEEE 1139)

PRE-REGISTERED EXPECTATIONS (written 2026-10-13 before the first run; addenda only below)
  E1  Tank-noise-only (F = 1, no observation noise): L(fm) follows 1/fm^2 with
        L = (2 k T F / P_sig) (f0 / (2 Q fm))^2,   P_sig = A^2 / (2R) = power dissipated in R   (Lee–Hajimiri)
      i.e. -131.6 dBc/Hz at 100 kHz offset for this tank; the simulation must agree within +-1.0 dB over
      0.3-30 MHz offsets (Welch scatter ~ +-0.3 dB after averaging, plus integrator error).
  E2  The same number in the KB's canonical Leeson form  L = (F k T0 / (2 P_s)) (1 + (f0/(2 Q_L fm))^2)
      holds with P_s = A^2 / (8 R) = P_sig / 4 = the AVAILABLE signal power of the tank seen by the amplifier
      input (6 dB below P_sig) — the "6 dB by definition" noted on 00/canonical-values-and-conventions.
  E3  F = 2 raises L by 3.0 +- 0.3 dB at every offset.
  E4  With observation noise: the curve flattens to F k T0 / (2 P_s) = -165.8 dBc/Hz (F = 2) above the Leeson
      corner f0 / (2 Q) = 7.23 MHz; a 2-parameter Leeson fit (floor, Q_L) returns Q_L within 10 % of 30
      and the floor within 0.5 dB.
  E5  The full voltage spectrum (AM + PM) sits ~3 dB above L far from the carrier where amplitude
      restoration no longer suppresses AM; close in it converges to L (AM suppressed by the limiter).

ADDENDUM 1 (2026-10-13, after the first run; expectations E1-E5 unchanged, only the read-out fixed):
  * First run: Welch segments of 2^17 samples gave 212 kHz bins, so the 0.3 MHz band was EMPTY (E1 printed
    MISS with nan) and 1 MHz had only two bins. Fix: segments of 2^18 (106 kHz bins) and every comparison is
    now a band average of the simulation against the band average of the model over the SAME bins (the first
    run compared a band mean with the model at the band centre: +0.6 dB bias at 1 MHz in the floor case).
  * E5 first run compared a Welch spectrum of v(t) with L: at 1 MHz the Hann leakage of the 0 dBc carrier
    (-108 dBc/Hz) swamped the -150 dBc/Hz noise, so that read-out is useless. Fix: AM noise is read from the
    analytic-signal envelope |z|, L_AM = S_(dA/A)/2, and E5 compares (L_AM + L)/L.
  First-run numbers that were valid are kept in the log (1/f^2 part within 0.3 dB at 1-30 MHz; E3 3.09 dB;
  E4 Q_L 29.1, floor -165.88 vs -165.86 dBc/Hz).

Run: python3 tools/verify/sim2_phase_noise_transient.py      (~1-2 min)   -> sim2_phase_noise_results.txt
"""
import os
import time

import numpy as np
from scipy.signal import hilbert, welch
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
K_B, T0 = 1.380649e-23, 290.0
F0, Q, L_T, A_TARGET = 433.92e6, 30.0, 10e-9, 1.0
W0 = 2 * np.pi * F0
C_T = 1 / (W0 ** 2 * L_T)
R_T = Q * W0 * L_T
G1 = 1.5 / R_T
G3 = 4 * (G1 - 1 / R_T) / (3 * A_TARGET ** 2)
SPP = 64                                   # steps per period
DT = 1 / (F0 * SPP)
T_REC = 20e-6
N_REAL = 16


def simulate(F=1.0, obs_noise=False, seed=1, n_real=N_REAL, t_rec=T_REC, settle=2e-6):
    rng = np.random.default_rng(seed)
    n_settle = int(settle / DT)
    n = int(t_rec / DT)
    v = np.full(n_real, A_TARGET)          # start on the limit cycle (amplitude settles in ~2Q/w0 ~ 22 ns)
    il = np.zeros(n_real)
    s_i = np.sqrt(2 * K_B * T0 * F / R_T / DT)   # two-sided PSD 2kTF/R -> per-step std of the mean current

    def f(v, il):
        dv = (-v / R_T - il + G1 * v - G3 * v ** 3) / C_T
        di = v / L_T
        return dv, di

    out = np.empty((n_real, n))
    for k in range(n_settle + n):
        noise = s_i * rng.standard_normal(n_real) / C_T
        dv1, di1 = f(v, il)
        vp, ip = v + DT * (dv1 + noise), il + DT * di1
        dv2, di2 = f(vp, ip)
        v = v + 0.5 * DT * (dv1 + dv2) + DT * noise
        il = il + 0.5 * DT * (di1 + di2)
        if k >= n_settle:
            out[:, k - n_settle] = v
    if obs_noise:                          # white voltage noise, one-sided PSD 4kTFR
        s_v = np.sqrt(4 * K_B * T0 * F * R_T * (1 / DT) / 2)
        out = out + s_v * rng.standard_normal(out.shape)
    return out


def phase_psd(vrec, nper=2 ** 18):
    fs = 1 / DT
    psds = []
    amps = []
    apsds = []
    for x in vrec:
        z = hilbert(x)
        ph = np.unwrap(np.angle(z))
        t = np.arange(ph.size) * DT
        p = np.polyfit(t, ph, 1)           # remove carrier frequency and phase
        fr, s = welch(ph - np.polyval(p, t), fs=fs, window="hann", nperseg=nper, detrend="linear")
        a = np.abs(z)
        _, sa = welch(a / np.mean(a), fs=fs, window="hann", nperseg=nper, detrend="linear")
        psds.append(s)
        apsds.append(sa)
        amps.append(np.mean(a))
    phase_psd.am = np.mean(apsds, axis=0)          # relative-amplitude PSD of the last call
    return fr, np.mean(psds, axis=0), float(np.mean(amps)), p[0] / (2 * np.pi)


def voltage_ssb(vrec, nper=2 ** 17):
    """Single-sideband noise of the full voltage (AM + PM) relative to the carrier, per Hz, upper side."""
    fs = 1 / DT
    fr, s = welch(vrec, fs=fs, window="hann", nperseg=nper, axis=-1, scaling="density")
    s = s.mean(axis=0)
    pc = np.mean(vrec ** 2)                # carrier mean-square (noise is negligible)
    return fr, s / pc


def leeson(fm, F, ps, ql, f0=F0):
    return F * K_B * T0 / (2 * ps) * (1 + (f0 / (2 * ql * fm)) ** 2)


def main():
    t_start = time.time()
    lines = [f"Tank L {L_T*1e9:.1f} nH, C {C_T*1e12:.3f} pF, R {R_T:.1f} ohm (Q {Q:.0f}), G1 {G1*1e3:.3f} mS, "
             f"G3 {G3*1e3:.4f} mA/V^3, target A {A_TARGET} V; dt = T0/{SPP}; {N_REAL} x {T_REC*1e6:.0f} us"]
    p_sig = A_TARGET ** 2 / (2 * R_T)
    p_s = A_TARGET ** 2 / (8 * R_T)
    lines.append(f"P_sig (dissipated in R) {10*np.log10(p_sig/1e-3):.2f} dBm; P_s (available) "
                 f"{10*np.log10(p_s/1e-3):.2f} dBm; Leeson corner f0/2Q {F0/(2*Q)/1e6:.2f} MHz")
    offs = np.array([0.3e6, 1e6, 3e6, 10e6, 30e6])  # pre-registered range 0.3-30 MHz
    res = {}
    for F in (1.0, 2.0):
        v = simulate(F=F, obs_noise=False, seed=int(F))
        fr, sphi, amp, fosc = phase_psd(v)
        Lsim = sphi / 2
        res[F] = (fr, Lsim)
        pred = 2 * K_B * T0 * F / (amp ** 2 / (2 * R_T)) * (F0 / (2 * Q * fr[1:])) ** 2
        lines.append(f"F = {F:.0f}, no observation noise: measured amplitude {amp:.4f} V, f_osc {fosc/1e6:.3f} MHz "
                     f"(integrator shift {100*(fosc-F0)/F0:+.3f} %)")
        errs = []
        for fo in offs:
            band = (fr > fo / 1.25) & (fr < fo * 1.25)
            fb = fr[band]
            lsim = 10 * np.log10(np.mean(Lsim[band]))
            lpred_lh = 10 * np.log10(np.mean(2 * K_B * T0 * F / (amp ** 2 / (2 * R_T)) * (F0 / (2 * Q * fb)) ** 2))
            lpred_ls = 10 * np.log10(np.mean(F * K_B * T0 / (2 * amp ** 2 / (8 * R_T)) * (F0 / (2 * Q * fb)) ** 2))
            errs.append(lsim - lpred_lh)
            lines.append(f"   fm {fo/1e6:5.1f} MHz: sim {lsim:7.2f} dBc/Hz | Lee-Hajimiri 2FkT/P_sig "
                         f"{lpred_lh:7.2f} | Leeson FkT/(2P_s), P_s = P_sig/4 (1/f^2 part) {lpred_ls:7.2f} | "
                         f"diff {lsim-lpred_lh:+.2f} dB")
        lines.append(f"   E1 {'PASS' if max(abs(e) for e in errs) <= 1.0 else 'MISS'}: max |sim - theory| "
                     f"{max(abs(e) for e in errs):.2f} dB over 0.3-30 MHz")
        at100k = 10 * np.log10(2 * K_B * T0 * F / (amp ** 2 / (2 * R_T)) * (F0 / (2 * Q * 1e5)) ** 2)
        lines.append(f"   theory at 100 kHz (below the record's resolution, extrapolated 1/f^2): {at100k:.2f} dBc/Hz")
    fr = res[1.0][0]
    band = (fr > 0.3e6) & (fr < 30e6)
    d = 10 * np.log10(np.mean(res[2.0][1][band] / res[1.0][1][band]))
    lines.append(f"E3 {'PASS' if abs(d-3.01) <= 0.3 else 'MISS'}: F=2 vs F=1 mean ratio {d:.2f} dB (expect 3.01)")

    # observation noise -> Leeson floor + fit
    v = simulate(F=2.0, obs_noise=True, seed=7)
    fr, sphi, amp, _ = phase_psd(v)
    Lsim = sphi / 2
    sel = (fr > 0.3e6) & (fr < 150e6)
    fit = least_squares(lambda p: 10 * np.log10(leeson(fr[sel], 1.0, 10 ** p[0], p[1])) - 10 * np.log10(Lsim[sel]),
                        x0=[-4.0, 10.0])
    ps_fit, ql_fit = 10 ** fit.x[0], fit.x[1]
    floor_fit = 10 * np.log10(K_B * T0 / (2 * ps_fit))         # F absorbed into P_s by the fit
    floor_th = 10 * np.log10(2.0 * K_B * T0 / (2 * amp ** 2 / (8 * R_T)))
    lines.append(f"F = 2 with observation noise: Leeson fit Q_L {ql_fit:.1f} (true {Q:.0f}), floor {floor_fit:.2f} "
                 f"dBc/Hz (theory FkT0/(2P_s) {floor_th:.2f}) -> E4 "
                 f"{'PASS' if abs(ql_fit-Q)/Q <= 0.10 and abs(floor_fit-floor_th) <= 0.5 else 'MISS'}")
    for fo in (1e6, 7.23e6, 30e6, 100e6):
        b = (fr > fo / 1.2) & (fr < fo * 1.2)
        lines.append(f"   fm {fo/1e6:6.2f} MHz: sim {10*np.log10(np.mean(Lsim[b])):7.2f} dBc/Hz, Leeson "
                     f"{10*np.log10(np.mean(leeson(fr[b], 2.0, amp**2/(8*R_T), Q))):7.2f} dBc/Hz (same bins)")

    # AM + PM vs PM only (no observation noise, F = 1): AM read from the analytic-signal envelope
    v = simulate(F=1.0, obs_noise=False, seed=11, n_real=8)
    fr, sphi, amp, fosc = phase_psd(v)
    lam = phase_psd.am / 2
    for fo in (0.3e6, 1e6, 10e6, 50e6, 200e6):
        bp = (fr > fo / 1.25) & (fr < fo * 1.25)
        lpm, lamv = np.mean(sphi[bp] / 2), np.mean(lam[bp])
        lines.append(f"E5 at fm {fo/1e6:5.1f} MHz: L_PM {10*np.log10(lpm):7.2f}, L_AM {10*np.log10(lamv):7.2f} dBc/Hz, "
                     f"(AM+PM)/PM {10*np.log10((lpm+lamv)/lpm):+.2f} dB")
    lines.append("   amplitude-restoring bandwidth (cubic limiter, 2Q/w0 envelope time constant x gain margin): "
                 f"~{(G1 - 1/R_T) / (2*np.pi*C_T) / 1e6:.1f} MHz")
    lines.append(f"runtime {time.time()-t_start:.0f} s")
    txt = "\n".join(lines)
    print(txt)
    with open(os.path.join(HERE, "sim2_phase_noise_results.txt"), "w") as fh:
        fh.write(f"=== sim2_phase_noise_transient.py {time.strftime('%Y-%m-%d %H:%M')} ===\n{txt}\n")


if __name__ == "__main__":
    main()
