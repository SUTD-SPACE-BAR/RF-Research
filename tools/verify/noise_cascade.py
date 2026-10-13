#!/usr/bin/env python3
"""
noise_cascade.py — receiver cascade budget (gain / NF / IIP3 / P1dB) + verification.
Used by kb/07-noise-linearity/receiver-cascade-analysis.md, noise-figure-and-friis.md,
dynamic-range-sfdr-blocking.md, sensitivity-and-mds.md.

Library use:
    from noise_cascade import Stage, cascade, print_cascade
    stages = [Stage('cable', -1.0), Stage('LNA', 18, nf=0.8, iip3=5, ip1db=-7), ...]
    res = cascade(stages); print_cascade(stages)

Conventions:
  * gain in dB (available/transducer gain assumed equal: all interfaces matched to 50 ohm)
  * nf in dB. For a passive stage with nf=None, NF = loss (valid when physical temperature = 290 K)
  * iip3, ip1db are INPUT-referred, dBm. None = "perfectly linear" (e.g. cable).
  * Cascade IIP3 uses the worst-case (in-phase / coherent voltage addition) formula
        1/IIP3_tot = 1/IIP3_1 + G1/IIP3_2 + G1 G2/IIP3_3 + ...   (all linear, mW)
    Power-addition variant (random phase of IM3 contributions) also printed for comparison.
  * Cascade input P1dB uses the same form (rough; compression points do not combine exactly).

Verification included (run as script):
  1. Monte-Carlo: complex Gaussian noise injected at each stage input with temperature Te_i,
     propagated through the gains; measured output noise vs Friis prediction.
  2. Time-domain two-tone through two cubic stages; measured IM3 vs cascaded-IIP3 prediction.
  3. Worked examples: 915 MHz LoRa ground receiver (LNA at masthead vs at receiver),
     433 MHz ground receiver, GNSS L1 active-antenna chain, and the "attenuator before LNA" lesson.
"""
import numpy as np

T0 = 290.0
kT0_dBm = 10*np.log10(1.380649e-23*T0/1e-3)   # -173.975 dBm/Hz

def db2lin(x):
    return 10**(np.asarray(x)/10)

def lin2db(x):
    return 10*np.log10(x)

class Stage:
    def __init__(self, name, gain, nf=None, iip3=None, ip1db=None):
        self.name = name
        self.gain = float(gain)
        self.nf = float(-gain) if (nf is None and gain <= 0) else (0.0 if nf is None else float(nf))
        self.iip3 = iip3
        self.ip1db = ip1db

def cascade(stages, coherent=True):
    """Return list of per-stage cumulative dicts."""
    out = []
    G_cum = 1.0        # linear gain before current stage
    F_tot = 1.0
    inv_iip3 = 0.0     # 1/mW
    inv_iip3_pw = 0.0  # power-addition variant: sum of (G_before/IIP3_i)^2 then sqrt
    inv_p1 = 0.0
    for i, s in enumerate(stages):
        F = db2lin(s.nf)
        F_tot = F_tot + (F - 1.0)/G_cum if i > 0 else F
        if s.iip3 is not None:
            term = G_cum/db2lin(s.iip3)
            inv_iip3 += term
            inv_iip3_pw += term**2
        if s.ip1db is not None:
            inv_p1 += G_cum/db2lin(s.ip1db)
        G_cum *= db2lin(s.gain)
        out.append(dict(
            name=s.name,
            G_cum_dB=lin2db(G_cum),
            NF_cum_dB=lin2db(F_tot),
            Te_cum_K=T0*(F_tot-1.0),
            IIP3_cum_dBm=(lin2db(1.0/inv_iip3) if inv_iip3 > 0 else np.inf),
            IIP3_cum_pw_dBm=(lin2db(1.0/np.sqrt(inv_iip3_pw)) if inv_iip3_pw > 0 else np.inf),
            IP1dB_cum_dBm=(lin2db(1.0/inv_p1) if inv_p1 > 0 else np.inf),
        ))
    return out

def noise_contributions(stages):
    """Fraction of total excess noise temperature (input-referred) contributed by each stage."""
    G_cum = 1.0
    contrib = []
    for s in stages:
        Te_i = T0*(db2lin(s.nf) - 1.0)
        contrib.append(Te_i/G_cum)
        G_cum *= db2lin(s.gain)
    tot = sum(contrib)
    return [c/tot for c in contrib], tot

def print_cascade(stages, title="", B=None, snr_min=None, Ta=T0):
    res = cascade(stages)
    fr, Te_tot = noise_contributions(stages)
    print(f"\n--- {title} ---")
    print(f"{'stage':22s} {'G':>6s} {'NF':>5s} {'IIP3':>6s} | {'Gcum':>6s} {'NFcum':>6s} {'Te,cum':>8s} "
          f"{'IIP3cum':>8s} {'(pwr)':>7s} {'P1dBin':>7s} {'%noise':>6s}")
    for s, r, f in zip(stages, res, fr):
        iip3 = f"{s.iip3:6.1f}" if s.iip3 is not None else "   inf"
        print(f"{s.name:22s} {s.gain:6.1f} {s.nf:5.2f} {iip3} | {r['G_cum_dB']:6.1f} {r['NF_cum_dB']:6.2f} "
              f"{r['Te_cum_K']:8.1f} {r['IIP3_cum_dBm']:8.1f} {r['IIP3_cum_pw_dBm']:7.1f} "
              f"{r['IP1dB_cum_dBm']:7.1f} {100*f:6.1f}")
    last = res[-1]
    if B is not None:
        Tsys = Ta + last['Te_cum_K']
        N = 10*np.log10(1.380649e-23*Tsys*B/1e-3)
        print(f"  Ta={Ta:.0f} K, Tsys={Tsys:.0f} K; noise floor in {B/1e3:.1f} kHz = {N:.1f} dBm "
              f"(T0-referred: {kT0_dBm + 10*np.log10(B) + last['NF_cum_dB']:.1f} dBm)")
        if snr_min is not None:
            print(f"  Sensitivity (SNRmin {snr_min:+.1f} dB) = {N + snr_min:.1f} dBm")
        if np.isfinite(last['IIP3_cum_dBm']):
            sfdr = 2/3*(last['IIP3_cum_dBm'] - N)
            print(f"  SFDR (IM3-limited, in B) = 2/3 (IIP3 - N) = {sfdr:.1f} dB")
    return res


def level_diagram(stages, P_sig, P_blk, B, Ta=T0, title=""):
    """Print, at the INPUT of each stage: cumulative gain before it, wanted-signal level, blocker level,
    total noise in B (source + all previous stages' added noise), and blocker headroom to the stage's
    input P1dB (if given)."""
    kB = 1.380649e-23
    print(f"\n--- level diagram: {title} (wanted {P_sig} dBm, blocker {P_blk} dBm, B {B/1e3:.0f} kHz) ---")
    print(f"{'at input of':22s} {'G_before':>8s} {'signal':>8s} {'blocker':>8s} {'noise':>8s} {'SNR':>6s} {'headroom':>9s}")
    G_cum = 1.0
    Tn = Ta            # noise temperature referred to the current point / G_cum
    for i, s in enumerate(stages):
        Gdb = lin2db(G_cum)
        noise = 10*np.log10(kB*Tn*G_cum*B/1e-3)
        head = (s.ip1db - (P_blk + Gdb)) if s.ip1db is not None else None
        hs = f"{head:9.1f}" if head is not None else "        -"
        print(f"{s.name:22s} {Gdb:8.1f} {P_sig+Gdb:8.1f} {P_blk+Gdb:8.1f} {noise:8.1f} {P_sig+Gdb-noise:6.1f} {hs}")
        Tn = Tn + T0*(db2lin(s.nf) - 1.0)/G_cum     # stage i adds Te_i at its input; refer to chain input
        G_cum *= db2lin(s.gain)
    print(f"{'(output)':22s} {lin2db(G_cum):8.1f} {P_sig+lin2db(G_cum):8.1f} {P_blk+lin2db(G_cum):8.1f} "
          f"{10*np.log10(kB*Tn*G_cum*B/1e-3):8.1f} {P_sig - 10*np.log10(kB*Tn*B/1e-3):6.1f}")
    print(f"  input-referred system noise temperature {Tn:.0f} K -> SNR at output = SNR of wanted vs k*Tsys*B")

# ------------------------------------------------------------------------------------------------
def mc_friis_check(stages, n=400000, seed=1):
    """Monte-Carlo check of the Friis formula. Each stage adds white complex Gaussian noise of
    power k*Te_i (per Hz, unit bandwidth) at its INPUT, then multiplies by its voltage gain.
    Input source noise = k*T0. Compare output SNR degradation to Friis F."""
    rng = np.random.default_rng(seed)
    kB = 1.380649e-23
    def cgauss(p):
        return np.sqrt(p/2)*(rng.standard_normal(n) + 1j*rng.standard_normal(n))
    x = cgauss(kB*T0)            # source noise
    for s in stages:
        Te = T0*(db2lin(s.nf) - 1.0)
        x = (x + cgauss(kB*Te))*np.sqrt(db2lin(s.gain))
    Gtot = db2lin(sum(s.gain for s in stages))
    F_meas = np.mean(np.abs(x)**2)/(kB*T0*Gtot)
    F_friis = db2lin(cascade(stages)[-1]['NF_cum_dB'])
    return lin2db(F_meas), lin2db(F_friis)

def twotone_cascade_check():
    """Two memoryless cubic stages y = a1 x + a3 x^3 (a3<0). Measure IM3 at the output with a two-tone
    input and infer cascade IIP3; compare with 1/IIP3 = 1/IIP3_1 + G1/IIP3_2 (coherent)."""
    R = 50.0
    def stage_coeffs(G_dB, iip3_dBm):
        a1 = 10**(G_dB/20)
        A_iip3 = np.sqrt(2*R*1e-3*10**(iip3_dBm/10))   # peak volts of each tone at IIP3
        a3 = -4*a1/(3*A_iip3**2)
        return a1, a3
    s1 = stage_coeffs(15.0, -5.0)
    s2 = stage_coeffs(10.0, 0.0)
    fs, N = 1024.0, 1 << 16
    t = np.arange(N)/fs
    f1, f2 = 100.0, 110.0          # bins exactly periodic
    Pin_dBm = -45.0                 # well below compression
    A = np.sqrt(2*R*1e-3*10**(Pin_dBm/10))
    x = A*np.cos(2*np.pi*f1*t) + A*np.cos(2*np.pi*f2*t)
    y = s1[0]*x + s1[1]*x**3
    z = s2[0]*y + s2[1]*y**3
    Z = np.fft.rfft(z)/N*2
    fbin = lambda f: int(round(f*N/fs))
    P = lambda amp: 10*np.log10(np.abs(amp)**2/(2*R)/1e-3)
    Pfund = P(Z[fbin(f1)]); Pim3 = P(Z[fbin(2*f1 - f2)])
    G = Pfund - Pin_dBm
    oip3 = Pfund + (Pfund - Pim3)/2
    iip3_meas = oip3 - G
    pred = cascade([Stage('s1', 15, nf=1, iip3=-5), Stage('s2', 10, nf=1, iip3=0)])[-1]['IIP3_cum_dBm']
    return iip3_meas, pred

# ------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Verification 1: Monte-Carlo vs Friis ===")
    test = [Stage('cable', -2.0), Stage('LNA', 15, nf=1.0), Stage('filter', -3.0), Stage('mixer', 8, nf=10.0),
            Stage('IF amp', 20, nf=4.0)]
    nf_mc, nf_fr = mc_friis_check(test)
    print(f"  MC NF = {nf_mc:.3f} dB, Friis NF = {nf_fr:.3f} dB  (agree within MC error ~0.01 dB)")

    print("\n=== Verification 2: two-tone through two cubic stages ===")
    meas, pred = twotone_cascade_check()
    print(f"  measured cascade IIP3 = {meas:.2f} dBm, coherent-formula prediction = {pred:.2f} dBm")

    print("\n=== Lesson: loss BEFORE vs AFTER the LNA (all numbers at 290 K) ===")
    lna = Stage('LNA', 20, nf=0.8, iip3=0)
    rx = Stage('receiver', 0, nf=6.0, iip3=-5)
    print_cascade([Stage('3 dB cable', -3.0), lna, rx], "3 dB cable then LNA")
    print_cascade([lna, Stage('3 dB cable', -3.0), rx], "LNA then 3 dB cable")
    print_cascade([Stage('3 dB cable', -3.0), rx], "3 dB cable, no LNA")

    B = 125e3
    print("\n=== Example A: 915 MHz LoRa ground station, SX1262-class receiver (NF 6 dB, IIP3 -5 dBm) ===")
    # Assumptions (see page): LMR-240-class cable 10 m at 915 MHz ~ 2.6 dB; SAW ~1.5 dB; LNA NF 0.7 dB, G 18 dB,
    # IIP3 +8 dBm, IP1dB -5 dBm (typical of GaAs pHEMT/SiGe LNA MMICs in the sub-GHz band).
    rxA = Stage('SX1262 (NF6,IIP3-5)', 0, nf=6.0, iip3=-5.0, ip1db=-15.0)
    chainA1 = [Stage('10 m coax', -2.6), rxA]
    chainA2 = [Stage('SAW', -1.5, iip3=35), Stage('LNA', 18, nf=0.7, iip3=8, ip1db=-5), Stage('10 m coax', -2.6), rxA]
    chainA3 = [Stage('10 m coax', -2.6), Stage('SAW', -1.5, iip3=35), Stage('LNA', 18, nf=0.7, iip3=8, ip1db=-5), rxA]
    for ch, t in ((chainA1, "A1: antenna - 10 m coax - module (no LNA)"),
                  (chainA2, "A2: masthead SAW+LNA, then coax, then module"),
                  (chainA3, "A3: coax, then SAW+LNA at the module")):
        print_cascade(ch, t, B=B, snr_min=-20.0, Ta=T0)

    level_diagram(chainA2, P_sig=-140.5, P_blk=-40.0, B=B, title="A2 masthead chain, wanted at SF12 sensitivity, -40 dBm blocker")

    print("\n=== Example B: 433 MHz ground station, sky-pointing Yagi (Ta ~ 150 K assumed) ===")
    rxB = Stage('SX1268 (NF6,IIP3-5)', 0, nf=6.0, iip3=-5.0)
    print_cascade([Stage('5 m LMR-400', -0.45), rxB], "B1: 5 m LMR-400 to module", B=B, snr_min=-20.0, Ta=150.0)
    print_cascade([Stage('LNA', 20, nf=0.6, iip3=10), Stage('5 m LMR-400', -0.45), rxB],
                  "B2: masthead LNA", B=B, snr_min=-20.0, Ta=150.0)

    print("\n=== Example C: GNSS L1 active antenna (patch -> LNA1 -> SAW -> LNA2 -> 3 m cable -> receiver) ===")
    # Receiver-internal NF 3 dB is an ASSUMPTION for illustration; C/A min received power -128.5 dBm (IS-GPS-200).
    chainC = [Stage('patch/feed loss', -0.3), Stage('LNA1', 17, nf=0.8, iip3=-5, ip1db=-15),
              Stage('SAW', -1.2, iip3=30), Stage('LNA2', 12, nf=1.5, iip3=0, ip1db=-10),
              Stage('3 m RG-174 (~1.4 dB/m)', -4.2), Stage('GNSS RF front end', 20, nf=3.0, iip3=-20)]
    res = print_cascade(chainC, "C: GNSS active antenna chain", B=1.0, Ta=100.0)
    Te = res[-1]['Te_cum_K']
    for Ta in (50.0, 100.0, 150.0):
        N0 = 10*np.log10(1.380649e-23*(Ta+Te)/1e-3)
        print(f"  Ta={Ta:.0f} K: N0={N0:.2f} dBm/Hz; C/N0 at -128.5 dBm = {-128.5 - N0:.1f} dB-Hz; "
              f"at typical open-sky -125 dBm = {-125 - N0:.1f} dB-Hz")
    chainC_noLNA = [Stage('patch/feed loss', -0.3), Stage('3 m RG-174', -4.2), Stage('GNSS RF front end', 20, nf=3.0)]
    res2 = cascade(chainC_noLNA)
    print(f"  Passive patch + 3 m RG-174 + receiver: NF = {res2[-1]['NF_cum_dB']:.2f} dB "
          f"(vs {res[-1]['NF_cum_dB']:.2f} dB active); C/N0 penalty at Ta=100 K = "
          f"{10*np.log10((100+res2[-1]['Te_cum_K'])/(100+Te)):.1f} dB")
