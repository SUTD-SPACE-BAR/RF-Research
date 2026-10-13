#!/usr/bin/env python3
"""
proj_phased_array.py -- design calculations for kb/20-projects-recipes/phased-array-starter-build.md

Starter coherent receive array for the Space Bar context:
 (a) KrakenSDR 5-element uniform circular array (UCA) direction finding on the rocket's 433.125 / 868.125 MHz
     LoRa beacon (recovery DF), and
 (b) the ADI Phaser 8-element 10.25 GHz ULA as the beamforming lab,
 plus an honest phased-array-vs-tracked-Yagi comparison for the telemetry ground station.

 1. UCA geometry for spacing 0.4 lambda; ambiguity check (max sidelobe of the Bartlett spectrum).
 2. Monte-Carlo DOA (Bartlett and MUSIC) vs SNR, snapshots, residual channel phase error (after KrakenSDR
    noise-source calibration: uncalibrated antenna-cable mismatch remains), and a coherent ground multipath.
 3. Two-station triangulation error at 5 km (bearing sigma 1-5 deg).
 4. LoRa burst snapshot budget (SF9/SF11 packets, 2.4 MS/s -> decimated).
 5. Phaser ULA: array factor, beamwidth, grating-lobe-free scan range at d = 0.48 lambda; 8-element taper.
 6. Array vs Yagi at 433 / 2440 / 5800 MHz: elements for a target gain, aperture size, cost class.
Run: python3 tools/verify/proj_phased_array.py   (~10 s)
"""
import math

import numpy as np

C0 = 299_792_458.0
RNG = np.random.default_rng(42)


def uca_positions(n, r):
    ang = 2 * np.pi * np.arange(n) / n
    return np.stack([r * np.cos(ang), r * np.sin(ang)], axis=1)


def steer(pos, az, lam):
    """Azimuth-only steering (elevation 0): phase = k (x cos az + y sin az)."""
    k = 2 * np.pi / lam
    az = np.atleast_1d(az)
    ph = k * (np.outer(np.cos(az), pos[:, 0]) + np.outer(np.sin(az), pos[:, 1]))
    return np.exp(1j * ph)        # (n_az, n_el)


def music_and_bartlett(X, A_scan, n_src=1):
    R = X @ X.conj().T / X.shape[1]
    w, V = np.linalg.eigh(R)
    En = V[:, : X.shape[0] - n_src]
    pb = np.real(np.einsum("ij,jk,ik->i", A_scan.conj(), R, A_scan))
    pm = 1.0 / np.real(np.sum(np.abs(A_scan.conj() @ En) ** 2, axis=1))
    return pb, pm


def main():
    print("=" * 92)
    print("1) KrakenSDR UCA geometry (5 elements, spacing s = 0.4 lambda)")
    n = 5
    for f in (433.125e6, 868.125e6):
        lam = C0 / f
        r = 0.4 * lam / (2 * math.sin(math.pi / n))
        pos = uca_positions(n, r)
        az = np.radians(np.arange(0, 360, 0.25))
        A = steer(pos, az, lam)
        a0 = steer(pos, np.radians(37.0), lam)[0]
        bp = np.abs(A.conj() @ a0) ** 2 / n ** 2
        main_mask = np.abs(((np.degrees(az) - 37.0 + 180) % 360) - 180) > 40
        print(f"   {f/1e6:.3f} MHz: lambda {lam*100:.1f} cm, radius {r*100:.1f} cm, diameter {2*r*100:.1f} cm; "
              f"Bartlett max sidelobe {10*np.log10(bp[main_mask].max()):.1f} dB (unambiguous 360 deg)")

    print("\n2) Monte-Carlo DOA, 433.125 MHz UCA, true bearing 37 deg, 200 trials each")
    f = 433.125e6
    lam = C0 / f
    r = 0.4 * lam / (2 * math.sin(math.pi / n))
    pos = uca_positions(n, r)
    az_scan = np.radians(np.arange(0, 360, 0.1))
    A_scan = steer(pos, az_scan, lam)
    true = np.radians(37.0)
    a_true = steer(pos, true, lam)[0]

    def trial(snr_db, K, sig_phase_deg, multipath_db=None, mp_az=200.0):
        cal = np.exp(1j * np.radians(RNG.normal(0, sig_phase_deg, n))) if sig_phase_deg > 0 else np.ones(n)
        s = (RNG.normal(size=K) + 1j * RNG.normal(size=K)) / np.sqrt(2)
        X = np.outer(a_true * cal, s)
        if multipath_db is not None:   # coherent reflection from another azimuth (same waveform, delayed phase)
            a_mp = steer(pos, np.radians(mp_az), lam)[0] * cal
            X = X + 10 ** (multipath_db / 20) * np.exp(1j * RNG.uniform(0, 2 * np.pi)) * np.outer(a_mp, s)
        noise = (RNG.normal(size=(n, K)) + 1j * RNG.normal(size=(n, K))) / np.sqrt(2) * 10 ** (-snr_db / 20)
        pb, pm = music_and_bartlett(X + noise, A_scan)
        eb = (np.degrees(az_scan[np.argmax(pb)] - true) + 180) % 360 - 180
        em = (np.degrees(az_scan[np.argmax(pm)] - true) + 180) % 360 - 180
        return eb, em

    for snr, K, sp, mp in [(10, 1000, 0, None), (0, 1000, 0, None), (10, 1000, 2, None), (10, 1000, 5, None),
                           (10, 1000, 10, None), (10, 1000, 2, -10.0), (10, 1000, 2, -6.0), (20, 1000, 2, -3.0)]:
        res = np.array([trial(snr, K, sp, mp) for _ in range(200)])
        rms_b = np.sqrt(np.mean(res[:, 0] ** 2))
        rms_m = np.sqrt(np.mean(res[:, 1] ** 2))
        out_b = np.mean(np.abs(res[:, 0]) > 10) * 100
        mp_s = "none" if mp is None else f"{mp:+.0f} dB @200 deg"
        print(f"   SNR/element {snr:3d} dB, K {K}, residual phase {sp:2d} deg rms, multipath {mp_s:16s}: "
              f"Bartlett rms {rms_b:5.2f} deg (outliers>10 deg {out_b:4.1f} %), MUSIC rms {rms_m:5.2f} deg")
    # cable mismatch -> phase
    for dl_cm in (0.5, 1.0, 2.0):
        for vf in (0.66, 0.85):
            ph = 360 * dl_cm / 100 / (vf * lam)
            print(f"   uncalibrated cable length error {dl_cm} cm (VF {vf}): {ph:4.1f} deg at 433 MHz, "
                  f"{360*dl_cm/100/(vf*C0/868.125e6):4.1f} deg at 868 MHz")

    print("\n3) Two-station triangulation (stations 2 km apart, target 5 km away, roughly broadside)")
    for sig_deg in (1.0, 2.0, 5.0):
        errs = []
        s1, s2 = np.array([0.0, 0.0]), np.array([2000.0, 0.0])
        tgt = np.array([1000.0, 5000.0])
        b1 = math.atan2(tgt[1] - s1[1], tgt[0] - s1[0])
        b2 = math.atan2(tgt[1] - s2[1], tgt[0] - s2[0])
        for _ in range(4000):
            t1 = b1 + np.radians(RNG.normal(0, sig_deg))
            t2 = b2 + np.radians(RNG.normal(0, sig_deg))
            M = np.array([[math.cos(t1), -math.cos(t2)], [math.sin(t1), -math.sin(t2)]])
            try:
                l = np.linalg.solve(M, s2 - s1)
            except np.linalg.LinAlgError:
                continue
            p = s1 + l[0] * np.array([math.cos(t1), math.sin(t1)])
            errs.append(np.linalg.norm(p - tgt))
        errs = np.array(errs)
        print(f"   bearing sigma {sig_deg:.0f} deg: position error median {np.median(errs):6.0f} m, 90th pct "
              f"{np.percentile(errs, 90):6.0f} m (cross-range 1 sigma at 5 km = {5000*np.radians(sig_deg):.0f} m)")

    print("\n4) Snapshot budget from one LoRa packet (KrakenSDR 2.4 MS/s per channel, decimate to 2 x BW)")
    for sf, bw, pl in ((9, 125e3, 32), (11, 125e3, 32), (7, 250e3, 40)):
        from math import ceil
        ts = 2 ** sf / bw
        nsym = 8 + 4.25 + 8 + ceil((8 * pl - 4 * sf + 28 + 16) / (4 * (sf - (2 if sf >= 11 else 0)))) * 5
        toa = nsym * ts
        k = toa * 2 * bw
        print(f"   SF{sf}/{bw/1e3:.0f}k {pl} B: ToA {toa*1e3:6.1f} ms -> {k:8.0f} snapshots at 2xBW "
              f"(processing gain of the covariance estimate >> needed; DOA SNR limited by per-sample SNR {10*math.log10(2):.0f} dB below channel SNR)")

    print("\n5) ADI Phaser: 8-element ULA at 10.25 GHz, d = 14 mm")
    f = 10.25e9
    lam = C0 / f
    d = 0.014
    print(f"   d/lambda = {d/lam:.3f}; grating-lobe-free scan |theta_s| <= {math.degrees(math.asin(lam/d - 1)) if lam/d - 1 < 1 else 90:.1f} deg")
    th = np.radians(np.linspace(-90, 90, 3601))
    for steer_deg, taper in ((0, "uniform"), (30, "uniform"), (0, "taylor-ish (cos^2 on pedestal 0.3)"), (60, "uniform")):
        nn = np.arange(8)
        w = np.ones(8) if taper == "uniform" else 0.3 + 0.7 * np.cos(np.pi * (nn - 3.5) / 8) ** 2
        u = np.sin(th) - math.sin(math.radians(steer_deg))
        af = np.abs(np.exp(1j * 2 * np.pi * d / lam * np.outer(u, nn)) @ w) / w.sum()
        afdb = 20 * np.log10(af + 1e-12)
        imax = np.argmax(af)
        half = th[af >= 1 / math.sqrt(2)]
        hp = half.max() - half.min()
        # main lobe = from the peak out to the first local minimum on each side
        lo = imax
        while lo > 0 and af[lo - 1] <= af[lo]:
            lo -= 1
        hi = imax
        while hi < len(af) - 1 and af[hi + 1] <= af[hi]:
            hi += 1
        mask = np.ones_like(af, bool)
        mask[lo:hi + 1] = False
        print(f"   steer {steer_deg:3d} deg, {taper:32s}: peak at {math.degrees(th[imax]):5.1f} deg, HPBW "
              f"{math.degrees(half.max()-half.min()):5.1f} deg, max sidelobe/grating {afdb[mask].max():6.1f} dB")

    print("\n6) Array vs Yagi for the telemetry ground station")
    for f, g_el, lab in ((433.125e6, 6.0, "433 MHz (patch/dipole-over-ground element ~6 dBi)"),
                         (2440e6, 6.0, "2.44 GHz FR-4 patch element"), (5800e6, 5.0, "5.8 GHz FR-4 patch element")):
        lam = C0 / f
        for g_target in (14.0, 20.0):
            n_el = math.ceil(10 ** ((g_target - g_el) / 10))
            side = math.sqrt(n_el) * lam / 2
            print(f"   {lab}: {g_target:.0f} dBi needs ~{n_el} elements (lambda/2 grid, {side*100:.0f} cm square)")
    print("   433 MHz 11-el DL6WU Yagi: 14.2 dBi on a 1.72 m boom (ground-station recipe) -> one connector, no calibration")


if __name__ == "__main__":
    main()
