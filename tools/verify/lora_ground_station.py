#!/usr/bin/env python3
"""
lora_ground_station.py — numbers for kb/15-lora-ism-radios/ground-station-design.md

1. Friis cascade: antenna → coax → (filter) → LNA → coax → module, for masthead vs shack LNA
   and filter-before vs filter-after LNA (NF and sensitivity change).
2. First Fresnel-zone radius at mid-path for ground-to-ground links (433 / 923 MHz).
3. Required tracking slew rates for a rising rocket (elevation rate v·D/(D²+h²)).
4. Yagi beamwidth vs pointing error (Gaussian-beam approximation) — hand tracking tolerance.
5. Selection diversity: packet loss with two independent receivers.
6. SDR IQ recording data rates.

Run: python3 tools/verify/lora_ground_station.py
"""
import math

T0 = 290.0


def nf_to_f(nf):
    return 10 ** (nf / 10)


def cascade(stages):
    """stages: list of (name, gain_dB, nf_dB). Returns total NF [dB] (Friis)."""
    f_tot, g_tot = 0.0, 1.0
    for i, (_, g, nf) in enumerate(stages):
        f = nf_to_f(nf)
        f_tot = f if i == 0 else f_tot + (f - 1) / g_tot
        g_tot *= 10 ** (g / 10)
    return 10 * math.log10(f_tot)


def main():
    print("1) Receive-chain noise figure (Friis). Module NF 6 dB assumed.")
    chains = {
        "module only, 1.5 dB coax": [("coax", -1.5, 1.5), ("module", 0, 6.0)],
        "module only, 5 dB coax (20 m RG58 @433)": [("coax", -5.0, 5.0), ("module", 0, 6.0)],
        "masthead: SAW 2 dB -> LNA 0.8 dB/18 dB -> 5 dB coax -> module":
            [("saw", -2.0, 2.0), ("lna", 18.0, 0.8), ("coax", -5.0, 5.0), ("module", 0, 6.0)],
        "masthead: LNA 0.8 dB/18 dB -> SAW 2 dB -> 5 dB coax -> module":
            [("lna", 18.0, 0.8), ("saw", -2.0, 2.0), ("coax", -5.0, 5.0), ("module", 0, 6.0)],
        "shack LNA: 5 dB coax -> LNA -> module":
            [("coax", -5.0, 5.0), ("lna", 18.0, 0.8), ("module", 0, 6.0)],
    }
    for name, st in chains.items():
        nf = cascade(st)
        print(f"   {name:62s}: NF {nf:5.2f} dB")
    print("   (sensitivity improves dB-for-dB with NF until external noise dominates — see 07 pages)")

    print("\n2) First Fresnel-zone radius at mid-path r1 = sqrt(λ d/4):")
    for f in (433.125e6, 923e6):
        lam = 299792458 / f
        cells = []
        for d in (2e3, 5e3, 10e3, 30e3):
            cells.append(f"{d/1e3:4.0f} km: {math.sqrt(lam*d/4):5.1f} m (60 %: {0.6*math.sqrt(lam*d/4):5.1f} m)")
        print(f"   {f/1e6:7.3f} MHz  " + "; ".join(cells))

    print("\n3) Elevation slew rate for a vertical rocket, station at D from pad (max at h→0 = v/D):")
    for v in (100, 300, 600):
        row = []
        for D in (1000, 2000, 5000):
            row.append(f"D={D/1e3:.0f} km: {math.degrees(v/D):5.1f} °/s")
        print(f"   v = {v:3d} m/s: " + ", ".join(row))

    print("\n4) Pointing loss of a Yagi (Gaussian beam: L = 12 (θ/θ3dB)^2 dB):")
    for bw3 in (30, 50, 70):
        row = [f"{e:2d}°: {12*(e/bw3)**2:5.1f} dB" for e in (5, 10, 20, 30)]
        print(f"   θ3dB = {bw3}°: " + ", ".join(row))

    print("\n5) Selection diversity (independent receivers), packet loss p each:")
    for p in (0.05, 0.1, 0.2, 0.4):
        print(f"   p = {p:4.2f}: one RX {p:5.3f}, two RX {p*p:6.4f}, three RX {p**3:7.5f}")

    print("\n6) SDR IQ recording rates:")
    for fs in (0.25e6, 1e6, 2.4e6):
        for bits, name in ((8, "8-bit I/Q (RTL-SDR/HackRF)"), (16, "16-bit I/Q"), (32, "float32 I/Q")):
            rate = fs * 2 * bits / 8
            print(f"   fs {fs/1e6:4.2f} MS/s {name:26s}: {rate/1e6:6.2f} MB/s = {rate*3600/1e9:6.1f} GB/h")


if __name__ == "__main__":
    main()
