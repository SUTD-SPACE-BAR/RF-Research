#!/usr/bin/env python3
"""Verification for the "Non-ideal Wilkinson" section of kb/06-rf-circuits/couplers-dividers-combiners.md (W5-E7)

 A. Lossy quarter-wave arms: the isolation-optimum resistor R_opt ~ 2 Z0 (1 + sqrt2 * alpha*l) and the
    match/isolation trade-off
 B. Unbalanced loads: Gamma_in = -(Gamma2 + Gamma3)/2 exactly; where reflected power goes
 C. Outputs tied together into 25 ohm (S11 = 0) and into 50 ohm (S11 = -1/3)
 D. Combining correlated vs uncorrelated signals and noise; noise-correlation matrix C = kT(I - S S^H):
    resistor noise does not reach port 1; uncorrelated inputs lose half to the resistor; array SNR
 E. Combiner into a mismatched antenna: reflected power returns to the PAs (even mode), resistor sees none
 F. Isolation-resistor parasitic inductance at 2.45 GHz
Run: python3 tools/verify/rf2_wilkinson_nonideal.py   (runtime < 2 s)
"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rf2_common import check, finish, db20
from rfckt_netsolve import Circuit
from scipy.optimize import minimize_scalar

Z0 = 50.0; f0 = 1e9
Zw = np.sqrt(2) * Z0


def wilk(f, R=100.0, alpha_db_wl=0.0, Rl_series=None, L_R=0.0):
    c = Circuit(f)
    c.line('p1', 'p2', Zw, f0, 90, alpha_db_per_wl=alpha_db_wl)
    c.line('p1', 'p3', Zw, f0, 90, alpha_db_per_wl=alpha_db_wl)
    if L_R > 0:
        c.R('p2', 'rm', R); c.L('rm', 'p3', L_R)
    else:
        c.R('p2', 'p3', R)
    return c


print("=== A. lossy arms and the optimum isolation resistor")
for adb in (0.5, 1.0, 2.0):                  # dB per wavelength -> arm loss = adb/4 dB
    al = adb / 8.686 / 4                       # Np over the quarter wave
    iso = lambda R: db20(wilk(np.array([f0]), R, adb).sparams(['p1', 'p2', 'p3'])[0, 2, 1])
    r = minimize_scalar(iso, bounds=(80, 130), method='bounded')
    Ropt = r.x; approx = 2 * Z0 * (1 + np.sqrt(2) * al)
    S100 = wilk(np.array([f0]), 100, adb).sparams(['p1', 'p2', 'p3'])[0]
    Sopt = wilk(np.array([f0]), Ropt, adb).sparams(['p1', 'p2', 'p3'])[0]
    print(f"  arm loss {adb/4:.3f} dB: R_opt {Ropt:.2f} ohm (approx 2Z0(1+sqrt2 al) = {approx:.2f});"
          f" isolation with 100 ohm {-db20(S100[2,1]):.1f} dB -> with R_opt {-db20(Sopt[2,1]):.1f} dB; S22 {db20(Sopt[1,1]):.1f} dB")
    if adb == 1.0:
        okA = abs(Ropt / approx - 1) < 0.01
check("lossy-arm optimum resistor = 2 Z0 (1 + sqrt2 alpha l) within 1 %", okA)

print("\n=== B. unbalanced loads")
S = wilk(np.array([f0])).sparams(['p1', 'p2', 'p3'])[0]
rng = np.random.default_rng(5)
errs = []
for _ in range(50):
    G2, G3 = [0.5 * rng.uniform() * np.exp(2j * np.pi * rng.uniform()) for _ in range(2)]
    # terminate ports 2 and 3 in loads with reflection G2, G3
    Gl = np.diag([0, G2, G3])
    # Gamma_in = S11 + S1L (I - Gl SLL)^-1 Gl SL1, partitioned
    SLL = S[1:, 1:]; S1L = S[0, 1:]; SL1 = S[1:, 0]
    Gin = S[0, 0] + S1L @ np.linalg.solve(np.eye(2) - np.diag([G2, G3]) @ SLL, np.diag([G2, G3]) @ SL1)
    errs.append(abs(Gin - (-(G2 + G3) / 2)))
check("Gamma_in = -(Gamma2 + Gamma3)/2 exactly for an ideal Wilkinson", max(errs) < 1e-9)
# reflected power from a mismatched output: half returns to port 1, half heats the resistor
a = np.array([0, 1, 0])
b = S @ a
print(f"  wave reflected back into port 2: {abs(b[0])**2*100:.0f} % to port 1, {abs(b[2])**2*100:.0f} % to port 3, "
      f"{(1-np.sum(np.abs(b)**2))*100:.0f} % in the resistor")
check("reflection from one output: 50 % to the input, 50 % to the resistor, 0 % to the other output",
      abs(abs(b[0]) ** 2 - 0.5) < 1e-9 and abs(b[2]) < 1e-9)

print("\n=== C. outputs tied together")
for RL in (25.0, 50.0):
    c = wilk(np.array([f0]))
    c.R('p2', 'p3', 1e-9)                    # short the outputs together (resistor bypassed)
    c.R('p2', 0, RL)
    S1 = c.sparams(['p1'])[0, 0, 0]
    print(f"  outputs tied, loaded with {RL:.0f} ohm: S11 = {S1.real:+.4f}{S1.imag:+.4f}j")
    if RL == 25.0:
        s25 = S1
    else:
        s50 = S1
check("tied into 25 ohm: S11 = 0; into 50 ohm: S11 = -1/3", abs(s25) < 1e-6 and abs(s50 - (-1 / 3)) < 1e-6)

print("\n=== D. correlated vs uncorrelated signals and noise")
# coherent equal in-phase inputs
a = np.array([0, 1, 1]) / np.sqrt(2); b = S @ a
print(f"  coherent, equal, in phase (P each): output {abs(b[0])**2/0.5:.2f} P, resistor {(np.sum(np.abs(a)**2)-np.sum(np.abs(b)**2))/0.5:.2f} P")
# uncorrelated inputs (e.g. different frequencies): powers add through |S|^2
Pout = abs(S[0, 1]) ** 2 + abs(S[0, 2]) ** 2
Pres = 2 - Pout - abs(S[1, 2]) ** 2 * 2 - (abs(S[1, 1]) ** 2 + abs(S[2, 2]) ** 2)
print(f"  uncorrelated, P each: output {Pout:.2f} P, resistor {Pres:.2f} P")
check("uncorrelated equal inputs: output P (not 2P), resistor P", abs(Pout - 1) < 1e-9 and abs(Pres - 1) < 1e-9)
# thermal-noise correlation matrix of the (passive, at T) network: C = kT (I - S S^H)
Cn = np.eye(3) - S @ S.conj().T
print(f"  internal-noise (resistor) contribution, units kT: port 1 {Cn[0,0].real:.3f}, port 2 {Cn[1,1].real:.3f}, port 3 {Cn[2,2].real:.3f},"
      f" correlation 2-3 {Cn[1,2].real:+.3f}")
check("resistor noise does not reach port 1 (C11 = 0); half of kT at each output, anti-correlated",
      abs(Cn[0, 0]) < 1e-9 and abs(Cn[1, 1] - 0.5) < 1e-9 and abs(Cn[1, 2] + 0.5) < 1e-9)
# array: two LNAs (independent noise N) + coherent signal S at each, combined in the Wilkinson
Sig, N = 1.0, 1.0
snr_single = Sig / N
out_sig = abs(S[0, 1] + S[0, 2]) ** 2 * Sig
out_noise = (abs(S[0, 1]) ** 2 + abs(S[0, 2]) ** 2) * N
print(f"  two-element array after LNAs: SNR {10*np.log10(out_sig/out_noise/snr_single):+.2f} dB vs one element")
check("coherent signal + independent noise: Wilkinson combining gives +3.01 dB SNR (N=2)", abs(10 * np.log10(out_sig / out_noise) - 3.0103) < 1e-3)

print("\n=== E. combiner into a mismatched load")
a = np.array([1, 0, 0]); b = S @ a      # wave reflected from the antenna enters port 1
print(f"  wave entering port 1: {abs(b[1])**2*100:.0f} % to port 2, {abs(b[2])**2*100:.0f} % to port 3, resistor {(1-np.sum(np.abs(b)**2))*100:.0f} %")
check("antenna reflection returns to both PAs in even mode; nothing reaches the resistor", abs(np.sum(np.abs(b) ** 2) - 1) < 1e-9)

print("\n=== F. isolation-resistor inductance")
for L_R in (0.0, 0.3e-9, 0.6e-9, 1.0e-9):
    c = Circuit(np.array([2.45e9]))
    c.line('p1', 'p2', Zw, 2.45e9, 90); c.line('p1', 'p3', Zw, 2.45e9, 90)
    if L_R > 0:
        c.R('p2', 'rm', 100.0); c.L('rm', 'p3', L_R)
    else:
        c.R('p2', 'p3', 100.0)
    Sx = c.sparams(['p1', 'p2', 'p3'])[0]
    print(f"  2.45 GHz, 100 ohm with {L_R*1e9:.1f} nH in series: isolation {-db20(Sx[2,1]):.1f} dB, S22 {db20(Sx[1,1]):.1f} dB")
    if abs(L_R - 0.6e-9) < 1e-15:
        isoL = -db20(Sx[2, 1])
check("0.6 nH of resistor/pad inductance limits 2.45 GHz isolation to ~33 dB (< 35 dB)", isoL < 35)

finish()
