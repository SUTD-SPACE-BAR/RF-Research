#!/usr/bin/env python3
"""Numbers for kb/10-comms-modulation/modulation-choice-guide.md

Run:  python3 tools/verify/comms_choice_guide.py      (< 1 s)

Builds the comparison table (required Eb/N0, C/N0, sensitivity, bandwidth, spectral efficiency,
PA back-off) and an illustrative free-space range comparison at 433 MHz. Eb/N0 values come from
the verified scripts in this folder (comms_ber_awgn.py, comms_coding.py, comms_lora_cr.py) or,
for LoRa, from the SX127x datasheet demodulator SNR (see ber-ebn0-and-shannon.md); the
short-block LDPC/polar entry uses the finite-length normal approximation + 1 dB practical gap
(an ESTIMATE, flagged on the page).

The range model is deliberately simple (free space, fixed margin) - see
kb/09-propagation-link-budget for real link budgets.
"""
import numpy as np

ok_all = True


def check(name, got, want, tol):
    global ok_all
    ok = abs(got - want) <= tol
    ok_all &= ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: got {got:.4g}, expected {want:.4g} (tol {tol})")


c = 299_792_458.0
f = 433e6
kT = -173.98
NF = 2.0            # ground station with LNA
Pt = 30.0           # dBm (1 W)
Gt, Gr = 0.0, 10.0  # rocket whip/dipole with nulls ~0 dBi; ground Yagi 10 dBi
margin = 10.0       # fade / pattern-null margin

lora_rb = lambda sf, bw=125e3, cr=4 / 5: sf * bw / 2 ** sf * cr
lora_snr = {7: -7.5, 8: -10.0, 9: -12.5, 10: -15.0, 11: -17.5, 12: -20.0}

rows = []
# name, info bit rate, required Eb/N0 incl. implementation loss (dB), occupied BW (Hz), PAPR (dB), notes
for sf in (7, 9, 12):
    rb = lora_rb(sf)
    ebn0 = lora_snr[sf] + 10 * np.log10(125e3) - 10 * np.log10(rb)
    rows.append((f"LoRa SF{sf}/125k CR4/5", rb, ebn0, 125e3, 0.0))
rb = 10e3
rows += [
    ("GFSK h=1 non-coherent", rb, 13.35 + 2.0, rb * (1 + 1.0), 0.0),
    ("GMSK BT0.5 coherent-ish", rb, 9.59 + 1.0 + 2.0, 1.03 * rb, 0.0),
    ("BPSK uncoded (RRC 0.35)", rb, 9.59 + 2.0, 1.35 * rb, 3.8),
    ("BPSK + K7 r1/2 soft", rb, 4.17 + 2.0, 2 * 1.35 * rb, 3.8),
    ("BPSK + RS(255,223)+K7", rb, 2.25 + 2.0, 2 * 255 / 223 * 1.35 * rb, 3.8),
    ("QPSK + short LDPC/polar r1/2 (est.)", rb, 1.6 + 1.0 + 2.0, 1.35 * rb, 3.8),
    ("16-QAM uncoded (RRC 0.35)", rb, 13.43 + 2.0, 1.35 * rb / 4, 5.6),
    ("OFDM 64-sc QPSK r1/2 + CP", rb, 4.17 + 2.0 + 0.97, 1.3 * rb, 10.5),
]

print(f"{'scheme':38s} {'Rb':>7s} {'Eb/N0':>6s} {'C/N0':>6s} {'Sens.':>7s} {'BW':>8s} {'eta':>6s} {'PAPR':>5s} {'range*':>7s}")
res = {}
for nm, rb, e, bw, papr in rows:
    cn0 = e + 10 * np.log10(rb)
    sens = kT + NF + cn0
    ptx_avg = Pt - papr                  # same PA: average power reduced by back-off
    fspl_max = ptx_avg + Gt + Gr - sens - margin
    d = c / (4 * np.pi * f) * 10 ** (fspl_max / 20)
    res[nm] = (cn0, sens, d)
    print(f"{nm:38s} {rb:7.0f} {e:6.1f} {cn0:6.1f} {sens:7.1f} {bw/1e3:7.1f}k {rb/bw:6.3f} {papr:5.1f} {d/1e3:6.0f} km")
ref = res["GFSK h=1 non-coherent"][2]
print("  relative free-space range (GFSK h=1 NC at 10 kb/s = 1.00):")
for nm in res:
    print(f"    {nm:38s} {res[nm][2]/ref:5.2f}")
print("  radio horizon (4/3 Earth) rocket 10 km, ground antenna 5 m: "
      f"{4.12*(np.sqrt(10000)+np.sqrt(5)):.0f} km")
print("  *free-space range at 433 MHz, 1 W PA (average power reduced by PAPR back-off), 0 dBi TX, 10 dBi RX,")
print("   NF 2 dB, 10 dB margin; ignores horizon, polarisation and pattern effects (see domain 09).")

# spot checks used on the page
check("LoRa SF7 Eb/N0 [dB]", rows[0][2], 6.09, 0.02)
check("LoRa SF12 Eb/N0 [dB]", rows[2][2], 6.30, 0.02)
check("BPSK+K7 sensitivity at 10 kb/s, NF 2 dB [dBm]", res["BPSK + K7 r1/2 soft"][1], -125.8, 0.1)
check("LoRa SF12 sensitivity (NF 2 dB) [dBm]", res["LoRa SF12/125k CR4/5"][1], -141.0, 0.1)
ratio = res["BPSK + K7 r1/2 soft"][2] / res["GFSK h=1 non-coherent"][2]
check("range ratio BPSK+K7 (3.8 dB PA back-off) vs NC-GFSK at same 10 kb/s", ratio, 10 ** ((15.35 - 6.17 - 3.8) / 20), 0.01)
# same-rate comparison: LoRa SF7 (5.47 kb/s) vs BPSK+K7 at 5.47 kb/s
d_eb = rows[0][2] - (4.17 + 2.0)
print(f"  at equal bit rate, LoRa SF7 needs {d_eb:+.1f} dB Eb/N0 vs BPSK+K7 (incl. 2 dB impl. loss) -> range ratio {10**(-d_eb/20):.2f}")
print("\nOVERALL:", "PASS" if ok_all else "FAIL")
