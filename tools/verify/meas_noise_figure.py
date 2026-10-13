#!/usr/bin/env python3
"""
meas_noise_figure.py -- numerical checks for kb/17-test-measurement/noise-figure-measurement.md

1. Y-factor method end to end (AN 57-2 eqs 2-10..2-18): simulate noise powers for a DUT
   (T1, G1) followed by an instrument (T2); recover T1 with second-stage correction; show the
   error if second-stage correction is skipped.
2. Sensitivity of NF to Y-factor error and ENR error vs DUT NF for ENR = 6 and 15 dB
   (why AN 57-2 says: 6 dB ENR up to NF ~16-18 dB, 15 dB ENR above).
3. Noise-source physical temperature T_off != 290 K: error if uncorrected.
4. Cold-source / gain method with a spectrum analyzer: NF = N_out + 174 - G; SA-floor correction;
   uncertainty budget (gain error, SA level error) -> why a tinySA gives +/-2 dB unless calibrated.
5. Loss before the DUT (cable/adaptor) and after it.
6. Receiver NF inferred from a LoRa sensitivity measurement, and the conducted sensitivity test:
   attenuator plan, required isolation, and number of packets for a 1 % PER estimate.
7. Hot/cold load (77 K LN2 vs 290 K) Y-factor without a calibrated noise source.

Run: python3 tools/verify/meas_noise_figure.py
"""
import numpy as np

k = 1.380649e-23
T0 = 290.0


def nf_db(T):
    return 10 * np.log10(1 + T / T0)


def T_of_nf(nf):
    return T0 * (10 ** (nf / 10) - 1)


# ---------------------------------------------------------------- 1. Y-factor end to end
print("=== 1. Y-factor measurement with second-stage correction ===")
ENR_dB = 15.0
Tsoff = 290.0
Tson = Tsoff + T0 * 10 ** (ENR_dB / 10)      # ENR = (Tson - Tsoff)/T0 (current definition)
B = 4e6
T1_true, G1_true = T_of_nf(1.2), 10 ** (18 / 10)     # LNA: NF 1.2 dB, gain 18 dB
T2 = T_of_nf(12.0)                                    # instrument (e.g. SA + preamp) NF 12 dB
G2 = 1.0
# calibration: noise source -> instrument
N2on, N2off = k * B * G2 * (Tson + T2), k * B * G2 * (Tsoff + T2)
Y2 = N2on / N2off
T2_meas = (Tson - Y2 * Tsoff) / (Y2 - 1)
# measurement: noise source -> DUT -> instrument
N12on = k * B * G2 * G1_true * (Tson + T1_true + T2 / G1_true)
N12off = k * B * G2 * G1_true * (Tsoff + T1_true + T2 / G1_true)
Y12 = N12on / N12off
T12 = (Tson - Y12 * Tsoff) / (Y12 - 1)
G1 = (N12on - N12off) / (N2on - N2off)
T1 = T12 - T2_meas / G1
print(f"Y2 = {10*np.log10(Y2):.3f} dB -> T2 = {T2_meas:.1f} K (true {T2:.1f}); Y12 = {10*np.log10(Y12):.3f} dB")
print(f"G1 = {10*np.log10(G1):.3f} dB (true 18); T1 = {T1:.2f} K -> NF = {nf_db(T1):.3f} dB (true 1.200)")
print(f"without 2nd-stage correction: NF = {nf_db(T12):.3f} dB (error {nf_db(T12)-1.2:+.3f} dB)")
for g_db, nf2 in [(10, 12), (18, 25), (30, 25), (18, 6)]:
    T12x = T1_true + T_of_nf(nf2) / 10 ** (g_db / 10)
    print(f"  DUT gain {g_db} dB, instrument NF {nf2} dB: uncorrected reading {nf_db(T12x):.2f} dB vs 1.20 dB")

# ---------------------------------------------------------------- 2. sensitivity to Y and ENR errors
print("\n=== 2. NF uncertainty from a 0.05 dB Y-factor error and a 0.1 dB ENR error ===")
def nf_from_Y(Y_db, enr_db, tsoff=290.0):
    Y = 10 ** (Y_db / 10)
    tson = tsoff + T0 * 10 ** (enr_db / 10)
    return nf_db((tson - Y * tsoff) / (Y - 1))

def Y_of(nf, enr_db, tsoff=290.0):
    T = T_of_nf(nf)
    tson = tsoff + T0 * 10 ** (enr_db / 10)
    return 10 * np.log10((tson + T) / (tsoff + T))

print(f"{'DUT NF':>7} | {'ENR 6: Y (dB)':>13} {'dNF/dY*0.05':>12} {'dNF(ENR+0.1)':>13} | {'ENR 15: Y':>9} {'dNF/dY*0.05':>12} {'dNF(ENR+0.1)':>13}")
for nf in [0.5, 1, 2, 5, 10, 15, 20, 25]:
    row = f"{nf:7.1f} |"
    for enr in (6.0, 15.0):
        y = Y_of(nf, enr)
        dy = nf_from_Y(y + 0.05, enr) - nf
        de = nf_from_Y(y, enr + 0.1) - nf
        row += f" {y:13.3f} {dy:12.3f} {de:13.3f} |" if enr == 6.0 else f" {y:9.3f} {dy:12.3f} {de:13.3f}"
    print(row)
print("  -> dNF from ENR error ~ ENR error (dB) at any NF above ~2 dB; Y-error sensitivity explodes when NF >> ENR")

# ---------------------------------------------------------------- 3. T_off != 290 K
print("\n=== 3. Noise source at 300 K (not 290 K), ENR 15 dB, uncorrected ===")
for nf in [0.5, 1.0, 3.0]:
    y = Y_of(nf, 15.0, tsoff=300.0)     # physics at 300 K
    nf_wrong = nf_from_Y(y, 15.0, tsoff=290.0)
    print(f"  true NF {nf:.1f} dB -> computed assuming 290 K: {nf_wrong:.3f} dB (error {nf_wrong-nf:+.3f} dB)")

# ---------------------------------------------------------------- 4. gain / cold-source method with an SA
print("\n=== 4. Gain (cold-source) method with a spectrum analyzer ===")
def gain_method(nf_dut, g_dut, nf_sa, rbw=100e3, log_avg=True):
    n_dut = -174 + nf_dut + g_dut                   # DUT output noise density with 290 K input termination (dBm/Hz)
    n_sa = -174 + nf_sa                              # SA's own floor, input-referred density
    tot = 10 * np.log10(10 ** (n_dut / 10) + 10 ** (n_sa / 10))
    corr = tot + 10 * np.log10(1 - 10 ** ((n_sa - tot) / 10))   # subtract SA floor (measured with DUT removed)
    return n_dut, n_sa, tot, corr + 174 - g_dut
for nf_dut, g_dut, nf_sa, label in [(1.5, 20, 6.0, "LNA 20 dB into tinySA Ultra with LNA on (NF~6)"),
                                    (1.5, 20, 28.0, "LNA 20 dB into tinySA without LNA (NF~28)"),
                                    (1.5, 40, 28.0, "two LNAs (40 dB) into tinySA (NF~28)"),
                                    (1.5, 20, 16.0, "LNA 20 dB into Siglent with preamp (NF~16)")]:
    n_dut, n_sa, tot, nf_est = gain_method(nf_dut, g_dut, nf_sa)
    margin = n_dut - n_sa
    print(f"  {label}: DUT noise {n_dut:.1f} dBm/Hz, SA floor {n_sa:.1f} -> margin {margin:+.1f} dB; "
          f"NF after floor subtraction {nf_est:.2f} dB")
print("  uncertainty: dNF = dG (gain error, dB) + dP (SA absolute noise-level error, dB) + floor-subtraction error")
for dg, dp in [(0.2, 2.0), (0.2, 0.7), (0.1, 0.3)]:
    print(f"    gain error {dg} dB, SA level error {dp} dB -> NF worst-case +/- {dg+dp:.1f} dB, RSS {np.hypot(dg,dp):.2f} dB")
# floor subtraction sensitivity: if the SA floor is only 3 dB below, a 0.5 dB error in the floor reading:
for margin in [-6, 0, 3, 6, 10, 15]:
    tot = 10 * np.log10(1 + 10 ** (-margin / 10))
    true = 0.0
    est_err = 10 * np.log10(10 ** (tot / 10) - 10 ** ((-margin + 0.5) / 10)) - true
    print(f"    DUT noise {margin} dB above SA floor, floor mis-read by 0.5 dB -> NF error {est_err:+.2f} dB")

# ---------------------------------------------------------------- 5. losses
print("\n=== 5. Losses before and after the DUT (at 290 K) ===")
for L_in in [0.2, 0.5, 1.0]:
    print(f"  {L_in} dB of cable/adaptor BEFORE the DUT adds {L_in} dB to the measured NF -> subtract it (at T0)")
L_out, g = 3.0, 15.0
T_after = T_of_nf(L_out) + T_of_nf(12.0) * 10 ** (L_out / 10)   # loss then instrument, referred to loss input
print(f"  {L_out} dB after a {g} dB DUT: becomes part of 'stage 2'; if calibrated out (in cal loop) no correction; "
      f"if not, reading rises by {nf_db(T_of_nf(1.2) + T_after/10**(g/10)) - nf_db(T_of_nf(1.2) + T_of_nf(12)/10**(g/10)):.2f} dB")

# ---------------------------------------------------------------- 6. LoRa sensitivity
print("\n=== 6. LoRa receiver: NF from sensitivity, and the conducted sensitivity test ===")
BW = 125e3
for sf, snr_req, sens in [(7, -7.5, -124), (9, -12.5, -129), (12, -20.0, -137)]:
    nf = sens + 174 - 10 * np.log10(BW) - snr_req
    print(f"  SF{sf}: sensitivity {sens} dBm, required SNR {snr_req} dB -> implied NF = {nf:.1f} dB")
p_gen = -30.0
for target in [-110, -124, -137]:
    att = p_gen - target
    print(f"  generator {p_gen} dBm -> DUT at {target} dBm needs {att:.0f} dB attenuation; leakage paths must be "
          f"> {att+20:.0f} dB down (20 dB margin)")
for p_hat, tol in [(0.01, 0.005), (0.01, 0.003), (0.1, 0.03)]:
    n = 1.96 ** 2 * p_hat * (1 - p_hat) / tol ** 2
    print(f"  PER {p_hat*100:.0f} % +/- {tol*100:.1f} % (95 %): N ~ {n:.0f} packets")

# ---------------------------------------------------------------- 7. hot/cold load
print("\n=== 7. Hot/cold load (290 K room load vs 77 K LN2 load) ===")
Th, Tc = 290.0, 77.0
for nf in [0.5, 1.0, 2.0, 5.0]:
    T = T_of_nf(nf)
    Y = (Th + T) / (Tc + T)
    Te = (Th - Y * Tc) / (Y - 1)
    dY = 0.02   # dB
    Y2 = Y * 10 ** (dY / 10)
    Te2 = (Th - Y2 * Tc) / (Y2 - 1)
    print(f"  NF {nf} dB: Y = {10*np.log10(Y):.2f} dB -> recovered {nf_db(Te):.3f} dB; 0.02 dB Y error -> {nf_db(Te2)-nf:+.3f} dB")
print("  (needs the cold load's true temperature incl. cable loss/warming; small Y -> needs careful averaging)")
