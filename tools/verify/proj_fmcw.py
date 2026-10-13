#!/usr/bin/env python3
"""
proj_fmcw.py -- design calculations for kb/20-projects-recipes/fmcw-radar-build.md

TI IWR6843 (60-64 GHz) / AWR1843 (76-81 GHz) EVM-based FMCW radar, with a 24 GHz and ADI Phaser comparison.
 1. Chirp configurations for three jobs: corner-reflector calibration (2-20 m), people/drone tracking (to 60 m),
    and rail-exit/early-boost velocity of a rocket (to ~100 m, up to ~150 m/s) -- with device limits
    (slope <= 100 MHz/us, IF bandwidth ~10 MHz, ADC <= 25 Msps complex per kb/11).
 2. SNR (radar equation in FFT form: SNR = Pr * T_int / (k Ts)) for trihedral reflectors, a person,
    a drone, a rocket seen from behind, per chirp and per frame (N chirps x M virtual channels).
 3. Singapore compliance: 57-64 GHz SRD 100 mW e.i.r.p. (39b); 77-81 GHz only as UWB: 10-dB bandwidth
    >= 500 MHz and mean e.i.r.p. density <= -3 dBm/MHz (IMDA TS UWB Table 1, via kb/19);
    24.00-24.25 GHz 100 mW e.i.r.p. (radar guns excluded).
 4. Data rates (raw ADC capture via DCA1000-class LVDS) and processing (cube size, FFT ops).
 5. Rail-exit kinematics from the proj_lora_link.py trajectory: speed at the end of a 6 m rail and at 100 m.
Run: python3 tools/verify/proj_fmcw.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from rfcalc.radar import fmcw_params, radar_snr_db, rcs_trihedral_m2  # noqa: E402

C0 = 299_792_458.0
G0 = 9.80665


IF_MAX = 10e6   # usable IF bandwidth of IWR6843/AWR1843-class devices (assumption from TI product pages; AWR2944 ~15 MHz)


def cfg_report(name, f0, B, t_ramp, t_idle, fs, n_samp, n_loops, n_tx, n_rx=4, if_max=IF_MAX):
    """TDM-MIMO aware: each loop transmits one chirp per TX, so the per-TX repetition is n_tx * Tc."""
    tc = t_ramp + t_idle
    s = B / t_ramp
    t_adc = n_samp / fs
    b_eff = s * t_adc                       # bandwidth actually sampled
    lam = C0 / f0
    rres = C0 / (2 * b_eff)
    rmax = min(0.9 * fs, if_max) * C0 / (2 * s)          # TI: f_IF,max = 0.9 fs (complex), capped by the IF filter
    vmax = lam / (4 * n_tx * tc)
    t_frame = n_loops * n_tx * tc
    vres = lam / (2 * t_frame)
    n_virt = n_tx * n_rx
    print(f"   {name}: f0 {f0/1e9:.2f} GHz, sweep {B/1e6:.0f} MHz in {t_ramp*1e6:.1f} us (S {s/1e12:.1f} MHz/us), idle "
          f"{t_idle*1e6:.1f} us, ADC {fs/1e6:.1f} Msps x {n_samp} -> sampled BW {b_eff/1e6:.0f} MHz; {n_tx} TX x {n_rx} RX")
    print(f"      range res {rres*100:.1f} cm, R_max (IF) {rmax:.1f} m, v_max +-{vmax:.1f} m/s, v_res {vres:.3f} m/s, "
          f"frame {t_frame*1e3:.2f} ms ({n_loops} loops), virtual channels {n_virt}")
    return dict(tc=tc, t_adc=t_adc, t_frame=t_frame, b=b_eff, sweep=B, lam=lam, n=n_loops, nv=n_virt, f0=f0,
                rmax=rmax, vmax=vmax, t_ramp=t_ramp, n_tx=n_tx, n_rx=n_rx, n_samp=n_samp, fs=fs)


def main():
    print("=" * 92)
    print("5) Rocket kinematics near the pad (proj_lora_link.py trajectory, 3500 N, 31.8 kg)")
    import proj_lora_link as pl
    tr = pl.tune_apogee(10000.0)
    v = np.hypot(tr["vx"], tr["vz"])
    z = tr["z"]
    for zz in (6.0, 20.0, 50.0, 100.0, 200.0):
        i = np.searchsorted(z[: np.argmax(z)], zz)
        print(f"   altitude {zz:5.0f} m: t {tr['t'][i]:.2f} s, speed {v[i]:6.1f} m/s")

    print("\n1) Chirp configurations (complex IF, TI relations; device: slope <= 100 MHz/us, IF <= ~10 MHz)")
    cfgs = {}
    cfgs["A cal 60G"] = cfg_report("A  corner-reflector calibration, IWR6843, 1 TX", 60.25e9, 3.5e9, 60e-6, 7e-6, 5e6, 256, 64, 1)
    cfgs["B track 60G"] = cfg_report("B  people/drone tracking, IWR6843, TDM 3 TX", 60.25e9, 0.6e9, 25e-6, 5e-6, 10e6, 240, 64, 3)
    cfgs["C rail 60G"] = cfg_report("C  rail exit / early boost, IWR6843, 1 TX fast chirps", 60.25e9, 0.6e9, 8e-6, 2e-6, 25e6, 192, 256, 1)
    cfgs["D track 77G"] = cfg_report("D  tracking, AWR1843 77-81 GHz (UWB: sweep >= 500 MHz), TDM 3 TX", 77.0e9, 0.6e9, 25e-6, 5e-6, 10e6, 240, 64, 3)
    cfgs["E 24G"] = cfg_report("E  24.00-24.25 GHz module (BGT24-class), 250 MHz", 24.125e9, 0.25e9, 100e-6, 20e-6, 2e6, 200, 64, 1, n_rx=2)
    cfgs["F Phaser"] = cfg_report("F  ADI Phaser 10 GHz (ramp assumed 500 MHz / 500 us)", 10.25e9, 0.5e9, 500e-6, 0.1e-3, 0.6e6, 256, 64, 1, n_rx=8)

    print("\n2) SNR (FFT form, T_int = ADC window x chirps x virtual channels; NF and power from kb/11 device table)")
    dev = {"A cal 60G": (12, 12.0, 8.0), "B track 60G": (12, 12.0, 8.0), "C rail 60G": (12, 12.0, 8.0),
           "D track 77G": (12, 14.5, 8.0), "E 24G": (12, 12.0, 13.0), "F Phaser": (12, 8.0, 17.0)}
    # (Pt dBm, NF dB, antenna gain dBi each way)
    targets = [("trihedral 5 cm edge", None, 0.05), ("trihedral 10 cm edge", None, 0.10), ("person", 1.0, None),
               ("small drone", 0.01, None), ("rocket, tail-on (130 mm body)", 0.01, None)]
    for key, c in cfgs.items():
        pt, nf, g = dev[key]
        t1 = c["t_adc"]
        tint = t1 * c["n"] * c["nv"]
        rows = []
        for name, rcs, edge in targets:
            sig = rcs if rcs is not None else rcs_trihedral_m2(edge, c["f0"])
            for r in (10.0, 50.0, 100.0):
                if r > c["rmax"] * 1.05:
                    continue
                snr = radar_snr_db(10 ** (pt / 10) / 1e3, g, g, c["f0"], sig, r, nf, t_int_s=tint, losses_db=6.0)
                rows.append(f"{name} {10*math.log10(sig):+.1f} dBsm @{r:.0f} m: {snr:5.1f} dB")
        print(f"   {key} (Pt {pt} dBm, NF {nf} dB, G {g} dBi, T_int {tint*1e3:.2f} ms, 6 dB losses):")
        for rr in rows:
            print("      " + rr)

    print("\n3) Singapore compliance")
    for key in ("A cal 60G", "B track 60G", "C rail 60G"):
        c = cfgs[key]
        eirp = 12 + 8.0 + 10 * math.log10(3)   # up to 3 TX simultaneously (worst case, beamforming adds)
        print(f"   {key}: 57-64 GHz SRD (39b) limit 100 mW = 20 dBm e.i.r.p.; 1 TX: {12+8.0:.1f} dBm, 3 TX coherent worst "
              f"case {eirp:.1f} dBm -> {'OK' if 12+8.0 <= 20 else 'over'} with 1 TX / TDM-MIMO; reduce TX backoff for BPM/beamforming")
    c = cfgs["D track 77G"]
    eirp = 12 + 8.0
    duty = c["t_ramp"] * c["n"] / (c["t_frame"] if False else 0.1)   # frame period 100 ms
    for frame_period in (0.1, 0.033):
        duty = c["t_ramp"] * c["n"] * c["n_tx"] / frame_period
        dens = eirp - 10 * math.log10(c["sweep"] / 1e6) + 10 * math.log10(duty)
        print(f"   77-81 GHz UWB: EIRP {eirp:.0f} dBm, sweep {c['sweep']/1e6:.0f} MHz (>= 500 required), chirp duty "
              f"{100*duty:.1f} % at {1/frame_period:.0f} frames/s -> mean density {dens:.1f} dBm/MHz (limit -3)")
    for sweep in (300e6, 500e6, 1e9, 4e9):
        dens = eirp - 10 * math.log10(sweep / 1e6)
        print(f"      continuous chirping over {sweep/1e6:.0f} MHz: {dens:.1f} dBm/MHz -> "
              f"{'meets' if dens <= -3 and sweep >= 500e6 else 'FAILS'} UWB condition")
    print("   24.00-24.25 GHz: 100 mW e.i.r.p.; 'radar gun devices are not allowed' under 38c (interpretation needed for")
    print("   speed-measuring a rocket; ask IMDA). 10.50-10.55 GHz (Phaser is 10.0-10.5 GHz -> NOT in that band: conducted / shielded tests only)")

    print("\n4) Data and processing")
    for key, c in cfgs.items():
        if key in ("E 24G", "F Phaser"):
            continue
        bytes_frame = c["n_samp"] * c["n"] * c["n_tx"] * c["n_rx"] * 4    # complex int16 per RX sample
        rate = bytes_frame / c["t_frame"]
        print(f"   {key}: cube {c['n_samp']} samples x {c['n']} loops x {c['nv']} virtual -> {bytes_frame/2**20:.2f} MiB per frame, "
              f"{rate/1e6:.0f} MB/s during the frame (DCA1000 capture over 1 GbE needs inter-frame idle time)")
    print("   range FFT per chirp: N log2 N ~ 256*8; Doppler FFT per range bin; 2-D CA-CFAR; angle FFT per detection (kb/11)")


if __name__ == "__main__":
    main()
