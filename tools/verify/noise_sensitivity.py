#!/usr/bin/env python3
"""
noise_sensitivity.py — verification for kb/07-noise-linearity/sensitivity-and-mds.md

1. Sensitivity S = -174 + 10 log10(B) + NF + SNR_min  (T0 = 290 K source) and the general form with
   an antenna temperature Ta: S = 10 log10(k (Ta + Te) B) + SNR_min.
2. LoRa: reproduce the Semtech SX1261/2 sensitivity table from NF and the demodulator SNR table,
   solve for the implied NF, and compute the implied Eb/N0 = SNR - 10 log10(Rb/B).
3. Physical sanity check of module datasheet claims (EBYTE E22/E220: "-147 dBm at 2.4 kbps"):
   the Shannon bound Eb/N0 >= -1.59 dB and the LoRa-typical Eb/N0 ~ 6 dB give a sensitivity floor
   at a given bit rate independent of SF/BW.
4. MDS (SNR = 0 dB in a stated bandwidth) and the "tangential" / 3 dB-above-floor variants.
5. LoRa time-on-air helper (Semtech formula) used by prop_doppler_fading.py.

Run: python3 noise_sensitivity.py
"""
import numpy as np

kT0 = -173.975  # dBm/Hz

def sensitivity(B, NF, snr_min, Ta=None):
    if Ta is None:
        return kT0 + 10*np.log10(B) + NF + snr_min
    k = 1.380649e-23
    Te = 290.0*(10**(NF/10) - 1)
    return 10*np.log10(k*(Ta+Te)*B/1e-3) + snr_min

LORA_SNR = {5: -2.5, 6: -5.0, 7: -7.5, 8: -10.0, 9: -12.5, 10: -15.0, 11: -17.5, 12: -20.0}

def lora_rb(SF, BW, CR=1):
    """Raw information bit rate (bit/s) for coding rate 4/(4+CR)."""
    return SF*BW/2**SF*4/(4+CR)

def lora_toa(PL, SF, BW, CR=1, npre=8, explicit=True, crc=True, ldro=None):
    """Semtech time-on-air (s). PL payload bytes, CR in 1..4 for 4/5..4/8.
    SX127x-style formula (SX126x differs slightly for SF5/6)."""
    Ts = 2**SF/BW
    if ldro is None:
        ldro = Ts > 16e-3
    DE = 1 if ldro else 0
    IH = 0 if explicit else 1
    num = 8*PL - 4*SF + 28 + 16*(1 if crc else 0) - 20*IH
    nsym = 8 + max(int(np.ceil(num/(4*(SF - 2*DE))))*(CR + 4), 0)
    return (npre + 4.25)*Ts + nsym*Ts

if __name__ == "__main__":
    print("=== 1. Generic sensitivity examples ===")
    for (name, B, NF, snr) in [("FSK 4.8 kb/s, 20 kHz, NF 6, SNR +10", 20e3, 6, 10),
                               ("LoRa SF12 BW125, NF 6", 125e3, 6, -20),
                               ("LoRa SF7 BW125, NF 6", 125e3, 6, -7.5),
                               ("GPS C/A tracking, 1 Hz loop-equivalent, NF 2", 1.0, 2, 0),
                               ("Wi-Fi 20 MHz MCS0 (SNR ~ 4 dB), NF 5", 20e6, 5, 4)]:
        print(f"  {name:45s}: {sensitivity(B, NF, snr):7.1f} dBm")

    print("\n=== 2. Semtech SX1261/2 LoRa table (Rx boosted, datasheet Rev 1.2/2.2) ===")
    ds = {(10.4e3, 7): -134, (10.4e3, 12): -148, (125e3, 7): -124, (125e3, 12): -137,
          (250e3, 7): -121, (250e3, 12): -134, (500e3, 7): -117, (500e3, 12): -129}
    print(f"  {'BW':>8s} {'SF':>3s} {'SNR':>6s} {'DS sens':>8s} {'impl. NF':>8s} {'NF=6 pred':>9s} {'Rb(4/5)':>9s} {'Eb/N0':>6s}")
    for (B, SF), s in ds.items():
        snr = LORA_SNR[SF]
        nf_impl = s - (kT0 + 10*np.log10(B) + snr)
        rb = lora_rb(SF, B)
        ebn0 = snr - 10*np.log10(rb/B)
        print(f"  {B/1e3:8.1f} {SF:3d} {snr:6.1f} {s:8.0f} {nf_impl:8.2f} {sensitivity(B,6,snr):9.1f} {rb:9.1f} {ebn0:6.2f}")
    print("  -> implied NF 5.8-7.3 dB for BW <= 250 kHz (~6 dB typical), 7.5-8 dB at 500 kHz; Eb/N0 ~ 6.1-6.3 dB at CR 4/5.")

    print("\n=== 3. Sensitivity floor at a given bit rate (independent of SF/BW choice) ===")
    for rb in (18.3, 293, 1000, 2400, 4800, 9600, 19200, 62500):
        s_lora = kT0 + 6 + 10*np.log10(rb) + 6.1      # NF 6, Eb/N0 6.1 dB
        s_shan = kT0 + 6 + 10*np.log10(rb) - 1.59     # NF 6, Shannon limit (infinite bandwidth)
        print(f"  Rb={rb:8.1f} b/s: LoRa-typical S ~ {s_lora:7.1f} dBm; absolute Shannon floor (NF 6) = {s_shan:7.1f} dBm")
    print("  EBYTE E22-400T33D / E220-900T30D datasheets: '-147 dBm at air data rate 2.4 kbps'.")
    need = -147 - (kT0 + 6 + 10*np.log10(2400))
    print(f"  -> would require Eb/N0 = {need:.1f} dB with NF 6 dB (Shannon limit is -1.59 dB): physically impossible.")
    need_nf0 = -147 - (kT0 + 0 + 10*np.log10(2400))
    print(f"     even with NF = 0 dB it would need Eb/N0 = {need_nf0:.1f} dB. Treat -147 dBm as the chip's best-case"
          f" (SF12, narrowest BW, ~20-300 b/s), not the 2.4 kbps figure.")
    print("  Candidate LoRa settings giving ~2.4 kb/s and their sensitivity (NF 6):")
    for SF in range(7, 13):
        for B in (62.5e3, 125e3, 250e3, 500e3):
            rb = lora_rb(SF, B)
            if 1800 <= rb <= 3200:
                print(f"    SF{SF} BW{B/1e3:.1f}k CR4/5: Rb={rb:6.0f} b/s, S={sensitivity(B,6,LORA_SNR[SF]):6.1f} dBm")

    print("\n=== 4. MDS variants ===")
    for NF in (2, 6, 10):
        for B in (1e3, 125e3, 1e6):
            mds = kT0 + 10*np.log10(B) + NF
            print(f"  NF={NF:2d} dB B={B/1e3:7.1f} kHz: MDS (S=N) = {mds:7.1f} dBm; '3 dB above floor' = {mds+3:7.1f} dBm")

    print("\n=== 5. Time on air (for Doppler-rate check) ===")
    for SF, B in ((7, 125e3), (9, 125e3), (10, 125e3), (11, 125e3), (12, 125e3), (11, 250e3), (12, 62.5e3)):
        print(f"  SF{SF:2d} BW{B/1e3:6.1f}k, 30 B payload CR4/5: ToA = {lora_toa(30, SF, B)*1e3:8.1f} ms, "
              f"Tsym = {2**SF/B*1e3:6.2f} ms, LDRO {'on' if 2**SF/B > 16e-3 else 'off'}")
