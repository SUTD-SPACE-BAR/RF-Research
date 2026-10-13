#!/usr/bin/env python3
"""
f2_campaign_predictions.py -- predicted values, uncertainty budgets and pre-registered acceptance bands
for the KB validation test campaign (kb/20-projects-recipes/validation-test-campaign.md, task W6-F2).

What it does (one section per test group of the page):
  S0  GUM helpers, acceptance-band rule, decision rule (confirmed / refuted / inconclusive), guarded
      acceptance for regulatory limits.
  S1  Antennas: dipole free-space and installed-shift bands; F2 quasi-static bracket for nose-cone /
      body-tube detuning (on-axis vs wall-taped); 2.45 GHz FR-4 patch prediction as a function of the
      measured er (openEMS -2.2 % result transported by the TL model) and its discrimination power;
      axial-ratio error from stray reflections; Yagi gain-transfer budget.
  S2  Transmit: conducted-power budgets; saturated-PA supply model; burst-current model; harmonic limits
      in dBc at each test power; analyser self-distortion with/without a high-pass; LoRa 99 % OBW and
      6 dB bandwidth (simulated chirp PSD + RBW models); crystal vs TCXO frequency-error bands;
      EBYTE air-rate candidate signatures.
  S3  Receive: LoRa sensitivity table (Semtech SNR rule, NF 6 dB chip vs ~3 dB with module LNA);
      isolation budget; precision of a PER-waterfall fit (Fisher information, ideal LoRa PER shape);
      Y-factor readings and NF uncertainty; RTL-SDR NF-vs-gain structural model.
  S4  Link: attenuator range test numbers; ground range test (two-ray exact, plane-earth, Egli); landed
      path loss and the PL excess that corresponds to the recipe's -50 %/+0 % range band.
  S5  Rocket-specific: Doppler-rate thresholds per SF/BW (Semtech rule and no-tracking model); GNSS
      PLL jerk error; L2 C/N0 vs CW jammer level; HERO test-level scaling; RF-rectification scaling.
  S6  Materials/PCB: ring-resonator design and Monte-Carlo er uncertainty; impedance-coupon prediction,
      TDR plateau requirement, quarter-wave ripple cross-check; via-fence isolation (FDFD vs textbook).
  S7  Environment: antenna-vs-load noise rise for P.372 425 MHz environments; survey threshold.
  CHECKS: reproduces KB numbers that the page quotes (exit code 1 if any check fails).

Optional:  --schema            print the CSV header and JSON schema of the results record
           --validate FILE.csv check a results file against the schema (fails on missing evidence)

Reuses: tools/rfcalc (tline), tools/verify/lora_toa.py, lora_css_sim.py, prop_two_ray.py,
        prop_empirical.py (all import-safe).  Run: python3 tools/verify/f2_campaign_predictions.py (~20 s)
"""
import csv
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))

from rfcalc import tline                                    # noqa: E402
from lora_toa import toa_sx126x                             # noqa: E402
from lora_css_sim import critical_drift_rate, payload_symbols, ser_theory  # noqa: E402
from prop_two_ray import two_ray_loss, GROUNDS              # noqa: E402
from prop_empirical import egli_ratio, plane_earth          # noqa: E402

C0 = 299792458.0
RNG = np.random.default_rng(20261003)
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"   [{'PASS' if ok else 'FAIL'}] {name} {detail}")


def db(x):
    return 10 * math.log10(x)


# ------------------------------------------------------------------------------------------- S0
def rss(*u):
    return math.sqrt(sum(x * x for x in u))


def rect(halfwidth):          # rectangular limits -> standard uncertainty
    return halfwidth / math.sqrt(3)


def ushape(halfwidth):        # U-shaped (mismatch) limits -> standard uncertainty
    return halfwidth / math.sqrt(2)


def band(U_pred, U_meas):
    """Pre-registered two-sided acceptance half-width (k = 2): prediction and measurement uncertainty
    combined in quadrature."""
    return rss(U_pred, U_meas)


def decide(meas, U_meas, pred, U_pred, separation=None):
    """CONFIRMED / REFUTED / INCONCLUSIVE.
    separation = distance between the KB prediction and the nearest competing hypothesis; a test whose
    U_meas exceeds separation/2 cannot discriminate and is INCONCLUSIVE even when inside the band."""
    B = band(U_pred, U_meas)
    if abs(meas - pred) > B:
        return "REFUTED"
    if separation is not None and U_meas > separation / 2:
        return "INCONCLUSIVE"
    return "CONFIRMED"


def guarded(meas, U_meas, limit):
    """Regulatory/safety limits (upper limit): PASS only if meas + U <= limit; FAIL if meas - U > limit."""
    if meas + U_meas <= limit:
        return "PASS"
    if meas - U_meas > limit:
        return "FAIL"
    return "INDETERMINATE"


def s0():
    print("\nS0  Decision rules")
    print("   band B = sqrt(U_pred^2 + U_meas^2) (k = 2). Examples:")
    for m, Um, p, Up, sep in ((2.38, 0.01, 2.397, 0.02, 0.053), (2.45, 0.01, 2.397, 0.02, 0.053),
                              (2.40, 0.04, 2.397, 0.02, 0.053)):
        print(f"     meas {m} +- {Um}, pred {p} +- {Up}, competing-hypothesis separation {sep}: "
              f"{decide(m, Um, p, Up, sep)}")
    check("decide(): far miss is REFUTED", decide(2.45, 0.01, 2.397, 0.02, 0.053) == "REFUTED")
    check("decide(): imprecise measurement is INCONCLUSIVE", decide(2.40, 0.04, 2.397, 0.02, 0.053) == "INCONCLUSIVE")
    check("guarded(): -37.0 +- 1.5 vs -36 dBm limit is INDETERMINATE", guarded(-37.0, 1.5, -36.0) == "INDETERMINATE")
    check("guarded(): -40.0 +- 1.5 vs -36 dBm limit is PASS", guarded(-40.0, 1.5, -36.0) == "PASS")


# ------------------------------------------------------------------------------------------- S1
def shell_fraction_axis(a, r_in, t, R_ext):
    """Quasi-static log-partition: fraction of the near-field electric energy of a thin wire (radius a)
    on the axis of a dielectric tube (inner radius r_in, wall t) that lies in the wall, counting energy
    out to R_ext (lambda/2pi .. lambda/4). Heuristic -- an F2 bracket, not a field solution."""
    r_out = min(r_in + t, R_ext)
    if r_in >= R_ext:
        return 0.0
    return math.log(r_out / r_in) / math.log(R_ext / a)


def shell_fraction_wall(a, t, R_ext):
    """Wire lying on the inner wall surface: half of the field within distance t is in the wall."""
    return 0.5 * math.log((t + a) / a) / math.log(R_ext / a)


def detune_pct(F, er):
    eeff = 1 + (er - 1) * F
    return 100 * (1 / math.sqrt(eeff) - 1)


def patch_tl_freq(L, W, er, h):
    """TL-model resonance of a rectangular patch (Balanis/Hammerstad fringing), dims in m."""
    eeff = (er + 1) / 2 + (er - 1) / 2 / math.sqrt(1 + 12 * h / W)
    dL = 0.412 * h * (eeff + 0.3) * (W / h + 0.264) / ((eeff - 0.258) * (W / h + 0.8))
    return C0 / (2 * (L + 2 * dL) * math.sqrt(eeff))


def s1():
    print("\nS1  Antennas")
    # A1 dipole in free space (KB: beginner ladder rung 4, 327.9 mm tip-to-tip for 2 mm wire, 433 MHz)
    L0, f0 = 327.9, 433.125
    U_model = 1.0          # % (k=2): thin-wire end effect / feed gap / wire diameter model form
    U_cut = 100 * 1.0 / L0  # % for +-1 mm cutting (k=2 taken as the limit)
    U_vna = 0.05           # % sweep step + interpolation
    Ua = rss(U_model, U_cut, U_vna)
    print(f"   A1a dipole {L0} mm: f_res = {f0} MHz, band +-{Ua:.2f} % = +-{Ua/100*f0:.1f} MHz (k=2)")
    # A1b installed sleeve dipole (link recipe P9): 2-5 % low, tolerance +-2 % -> 0-7 % low
    print(f"   A1b installed: 2-5 % low (P9) -> accept {f0*(1-0.07):.0f}-{f0:.0f} MHz before trimming")

    # A2 detuning bracket (F2): 433 MHz in a 130 mm body tube; 915 MHz whip in a 100 mm nose cone (08 ex. 3)
    rows = []
    for lab, f, r_in, t in (("433 MHz, 130 mm tube, 2.5 mm wall", 433.125e6, 65e-3, 2.5e-3),
                            ("915 MHz, 100 mm cone, 3 mm wall", 915e6, 50e-3, 3e-3)):
        lam = C0 / f
        for Rlab, R in (("lam/2pi", lam / (2 * math.pi)), ("lam/4", lam / 4)):
            for er in (4.2, 5.2):
                for a in (0.5e-3, 1.0e-3):
                    Fa = shell_fraction_axis(a, r_in, t, R)
                    Fw = shell_fraction_wall(a, t, R)
                    rows.append((lab, Rlab, er, a, detune_pct(Fa, er), detune_pct(Fw, er)))
    for lab in sorted(set(r[0] for r in rows)):
        ax = [r[4] for r in rows if r[0] == lab]
        wl = [r[5] for r in rows if r[0] == lab]
        print(f"   A2 {lab}: on-axis {max(ax):.1f} .. {min(ax):.1f} %; wire taped to wall {max(wl):.1f} .. {min(wl):.1f} %")
    ax433 = [r[4] for r in rows if r[0].startswith("433")]
    wl433 = [r[5] for r in rows if r[0].startswith("433")]
    check("F2 bracket: on-axis detuning in a fibreglass tube is small (< 3 %) -- consistent with 08 'a few %'",
          max(abs(x) for x in ax433) < 3.0)
    check("F2 bracket: wall-taped wire detunes several times more than on-axis (> 3x)",
          min(abs(x) for x in wl433) > 3 * max(abs(x) for x in ax433))

    # A3 2.45 GHz FR-4 patch: openEMS 2.397 GHz at er 4.4, h 1.6 (sim_openems_patch.py)
    Lp, Wp = 28.81e-3, 37.23e-3
    fTL_ref = patch_tl_freq(Lp, Wp, 4.4, 1.6e-3)
    print(f"   A3 TL model of the reference patch: {fTL_ref/1e9:.4f} GHz (design 2.45 GHz); openEMS 2.397 GHz")
    check("TL model reproduces the 2.45 GHz design within 0.5 %", abs(fTL_ref / 2.45e9 - 1) < 0.005,
          f"({fTL_ref/1e9:.4f} GHz)")
    ratio_sim = 2.397e9 / fTL_ref

    def f_pred(er, h):
        return ratio_sim * patch_tl_freq(Lp, Wp, er, h)

    for er in (4.3, 4.4, 4.5, 4.6):
        print(f"      er {er}: h 1.43 / 1.51 / 1.60 mm -> openEMS-transported "
              + " / ".join(f"{f_pred(er, h)/1e9:.4f}" for h in (1.43e-3, 1.51e-3, 1.6e-3)) + " GHz")
    # uncertainty of the prediction with er measured by the ring resonator (S6 gives U(er) ~ 0.05-0.07)
    d_er = (f_pred(4.45, 1.51e-3) - f_pred(4.35, 1.51e-3)) / 0.1 / f_pred(4.4, 1.51e-3) * 100   # %/unit er
    d_h = (f_pred(4.4, 1.56e-3) - f_pred(4.4, 1.46e-3)) / 0.1 / f_pred(4.4, 1.51e-3) * 100      # %/mm
    print(f"      sensitivity: {d_er:.2f} % per unit er, {d_h:.2f} % per mm of h")
    for lab, Uer in (("er unknown (4.3-4.7 -> +-0.2)", 0.2), ("er from ring (U 0.06)", 0.06)):
        Up = rss(abs(d_er) * Uer, abs(d_h) * 0.05, 0.1, 0.5, 0.17)   # er, h, numerical, model-form, etch
        sep = 2.2
        print(f"      {lab}: prediction band +-{Up:.2f} % vs TL-vs-openEMS separation {sep} % "
              f"-> discrimination ratio {sep/Up:.1f}")
    Up_unk = rss(abs(d_er) * 0.2, abs(d_h) * 0.05, 0.1, 0.5, 0.17)
    Up_ring = rss(abs(d_er) * 0.06, abs(d_h) * 0.05, 0.1, 0.5, 0.17)
    check("without a measured er the patch test cannot separate TL from openEMS (band >= separation/2)", Up_unk >= 1.1)
    check("with a ring-measured er it can (band < separation/2)", Up_ring < 1.1, f"(+-{Up_ring:.2f} %)")

    # A4 AR error from a stray reflection (rotating-linear-source method)
    print("   A4 AR measurement error from a stray wave rho (relative amplitude):")
    for rho_db in (-15, -20, -25, -30, -35):
        rho = 10 ** (rho_db / 20)
        print(f"      stray {rho_db} dB -> AR reading error up to +-{20*math.log10((1+rho)/(1-rho)):.2f} dB")
    check("stray -30 dB gives <= 0.6 dB AR error (needed to test AR <= 1.5 dB)",
          20 * math.log10((1 + 10 ** -1.5) / (1 - 10 ** -1.5)) <= 0.6)

    # A5 Yagi gain transfer: predicted P_Yagi - P_dipole = 11.2 - 2.15 dB
    comps = {"reference dipole gain (2.15 dBi, matched, mismatch-corrected)": 0.2 / 2,
             "mismatch of each antenna (|G| <= 0.1 vs instrument 0.1)": ushape(0.09),
             "ground-reflection range field taper (+-0.4 dB)": rect(0.4),
             "re-positioning repeatability (+-0.3 dB)": rect(0.3),
             "receiver linearity over 9 dB (SDR/tinySA, +-0.2 dB)": rect(0.2),
             "RSSI averaging, sigma 1 dB, N=100": 1.0 / math.sqrt(100),
             "different ground illumination of Yagi vs dipole (+-1 dB)": rect(1.0)}
    uc = rss(*comps.values())
    print(f"   A5 Yagi gain transfer: predicted dP = {11.2-2.15:.2f} dB; U_meas = +-{2*uc:.2f} dB (k=2)")
    for k, v in comps.items():
        print(f"      u = {v:.3f} dB  {k}")
    print(f"      acceptance band vs Q2 (+-1 dB): +-{band(1.0, 2*uc):.2f} dB")
    return {"A5_Umeas": 2 * uc}


# ------------------------------------------------------------------------------------------- S2
def lora_iq(sf, n_sym, osr, rng):
    """Phase-continuous LoRa baseband (random symbols), fs = osr*BW, BW normalised to 1."""
    N = 2 ** sf
    spc = N * osr
    tau = np.arange(spc) / spc                               # fraction of a symbol
    f_all, = [np.empty(n_sym * spc)]
    for k, s in enumerate(rng.integers(0, N, n_sym)):
        f_all[k * spc:(k + 1) * spc] = ((s / N + tau) % 1.0) - 0.5   # instantaneous freq / BW
    ph = 2 * np.pi * np.cumsum(f_all) / osr
    return np.exp(1j * ph), osr


def s2():
    print("\nS2  Transmit")
    # T1 power: GUM numbers from e3_bench.py section 6 (sensor +-0.33 dB, tinySA +-1.5 dB, k=2)
    for lab, Um in (("power sensor", 0.33), ("tinySA only", 1.5)):
        print(f"   T1 33 dBm +- 0.5 dB (datasheet) with {lab} (U {Um} dB): accept +-{band(0.5, Um):.2f} dB")
    print("   T1 supply model (saturated PA on the supply rail, P ~ V^2): "
          + ", ".join(f"{v} V {20*math.log10(v/5.0):+.2f} dB" for v in (4.5, 5.0, 5.5))
          + "; regulated-PA hypothesis: 0 dB. Relative U (same set-up) ~ +-0.2 dB -> separable.")
    # T3 burst current: class-B-like I_dc - I_idle ~ sqrt(P_out)
    for lab, Imax, Pmax, I0 in (("E22-400T33D", (0.85, 1.2), 33, 0.1), ("E220-900T30D", (0.62, 0.62), 30, 0.05)):
        txt = []
        for p in (Pmax - 9, Pmax - 6, Pmax - 3, Pmax):
            lo = I0 + (Imax[0] - I0) * 10 ** ((p - Pmax) / 20)
            hi = I0 + (Imax[1] - I0) * 10 ** ((p - Pmax) / 20)
            txt.append(f"{p} dBm {lo:.2f}-{hi:.2f} A" if hi > lo else f"{p} dBm {lo:.2f} A")
        print(f"   T3 {lab} burst-current model (sqrt-P, idle {I0} A assumed): " + "; ".join(txt))
    for R in (0.05, 0.1, 0.2):
        print(f"      droop at 1.2 A through {R*1000:.0f} mOhm source+ESR: {1.2*R*1000:.0f} mV ({1.2*R/5*100:.1f} % of 5 V)")
    # T2 harmonic limits in dBc at each conducted test power (TS SRD: -36 dBm < 1 GHz, -30 dBm >= 1 GHz)
    print("   T2 harmonic suppression needed at the antenna port (2f < 1 GHz, 3f > 1 GHz for 433 MHz):")
    for lab, p in (("E22 33 dBm (licensed)", 33.0), ("E22 24 dBm + 13.5 dB pad (10 mW e.r.p. test)", 10.5),
                   ("E220 24 dBm 868 MHz (2f/3f both > 1 GHz)", 24.0)):
        if "E220" in lab:
            print(f"      {lab}: 2f, 3f >= {p+30:.1f} dBc")
        else:
            print(f"      {lab}: 2f >= {p+36:.1f} dBc, 3f >= {p+30:.1f} dBc")
    check("2f requirement at 33 dBm is 69 dBc (KB 17/bench R6)", abs(33 + 36 - 69) < 1e-9)
    # analyser self-distortion (e3_bench assumptions: IP2 +35 dBm)
    IP2 = 35.0
    for lab, pin in (("no HPF, -7 dBm at analyser", -7.0), ("HPF 40 dB at f0, -47 dBm", -47.0)):
        h2 = 2 * pin - IP2
        print(f"      analyser own H2 with {lab}: {h2:.0f} dBm")
    check("analyser H2 without HPF ~ -49 dBm (e3_bench R6)", abs((2 * -7 - IP2) + 49) < 0.5)
    # T4 occupied bandwidth by simulation
    from scipy import signal as sg
    x, osr = lora_iq(7, 600, 16, RNG)
    f, P = sg.welch(x, fs=osr, nperseg=2 ** 14, return_onesided=False, scaling="density")
    o = np.argsort(f)
    f, P = f[o], P[o]
    cP = np.cumsum(P) / P.sum()
    obw99 = f[np.searchsorted(cP, 0.995)] - f[np.searchsorted(cP, 0.005)]
    print(f"   T4 simulated 99 % OBW = {obw99:.3f} x BW  -> 125 kHz: {obw99*125:.0f} kHz, 250: {obw99*250:.0f}, 500: {obw99*500:.0f} kHz")
    check("99 % OBW of SF7/125 ~ 133 kHz (meas_sa.py)", abs(obw99 * 125 - 133) < 4, f"({obw99*125:.1f} kHz)")
    # 6 dB bandwidth with a 100 kHz Gaussian RBW at BW 500 kHz: (a) averaging detector = PSD * |H|^2,
    # (b) peak/max-hold of a sweeping chirp ~ max over in-band f of |H(fc - f)|^2
    rbw = 100e3 / 500e3
    df = f[1] - f[0]
    k = np.arange(-int(1.5 * rbw / df), int(1.5 * rbw / df) + 1) * df
    H2 = np.exp(-4 * math.log(2) * (k / rbw) ** 2)
    Pc = np.convolve(P, H2 / H2.sum(), mode="same")
    m = Pc.max()
    inband = f[Pc >= m / 4]
    bw6_avg = inband.max() - inband.min()
    d6 = rbw * math.sqrt(math.log(4) / (4 * math.log(2)))
    bw6_pk = 1.0 + 2 * d6
    print(f"   T4 6 dB BW at 500 kHz with 100 kHz RBW: averaging {bw6_avg*500:.0f} kHz, peak max-hold model "
          f"{bw6_pk*500:.0f} kHz (>= 500 kHz needed for IREC Mode A / DTS)")
    check("6 dB bandwidth of a 500 kHz LoRa signal exceeds 500 kHz under both detector models",
          bw6_avg * 500 > 500 and bw6_pk * 500 > 500)
    # T5 frequency error
    print("   T5 static frequency-error bands (one end):")
    for fc in (433.125e6, 868.125e6, 920.125e6):
        print(f"      {fc/1e6:.3f} MHz: crystal +-10 ppm typ {fc*10e-6/1e3:.2f} kHz, +-30 ppm max "
              f"{fc*30e-6/1e3:.1f} kHz; TCXO +-2.5 ppm {fc*2.5e-6/1e3:.2f} kHz; LoRa window +-25 % of 125 kHz = 31.25 kHz")
    print("      thermal discriminator (AN1200.37 via KB 15): crystal ~2.2 kHz over a 48 K swing at 868 MHz "
          f"({2.2/48:.3f} kHz/K) vs TCXO ~0.2 kHz -> over a 25 K self-heat: crystal ~{2.2/48*25:.1f} kHz, TCXO ~{0.2/48*25:.2f} kHz")
    # T6 EBYTE air-rate candidates
    print("   T6 EBYTE air-rate candidates (KB 15 / sdr recipe D5): symbol time, chirp slope, bit rate (CR4/5)")
    for code, cands in (("2.4k", ((9, 125e3), (10, 250e3), (11, 500e3))), ("4.8k", ((7, 125e3), (8, 250e3), (9, 500e3))),
                        ("9.6k", ((7, 250e3), (8, 500e3))), ("19.2k", ((7, 500e3),))):
        for sf, bw in cands:
            ts = 2 ** sf / bw
            print(f"      {code}: SF{sf}/{bw/1e3:.0f} kHz  Ts {ts*1e3:.3f} ms  slope {bw/ts/1e9:.3f} GHz/s  "
                  f"Rb {sf*bw/2**sf*0.8:.0f} b/s")
    check("all three 2.4k candidates share Ts = 4.096 ms (so BW, not symbol time, identifies them)",
          all(abs(2 ** sf / bw - 4.096e-3) < 1e-9 for sf, bw in ((9, 125e3), (10, 250e3), (11, 500e3))))


# ------------------------------------------------------------------------------------------- S3
SNR_REQ = {5: -2.5, 6: -5.0, 7: -7.5, 8: -10.0, 9: -12.5, 10: -15.0, 11: -17.5, 12: -20.0}


def sens(sf, bw, nf):
    return -174 + 10 * math.log10(bw) + nf + SNR_REQ[sf]


def per_curve(sf, snr_db, pl=64):
    nsym = payload_symbols(pl, sf, de=(sf >= 11))
    s = ser_theory(sf, snr_db)
    return 1 - (1 - s) ** nsym


def s3():
    print("\nS3  Receive")
    print("   R1 predicted conducted sensitivity (dBm, 1 % PER) = -174 + 10logBW + NF + SNR_req:")
    print("      SF   125k(NF6) 125k(NF3) 250k(NF6) 500k(NF6)")
    for sf in range(7, 13):
        print(f"      {sf:2d}  {sens(sf,125e3,6):8.1f} {sens(sf,125e3,3):8.1f} {sens(sf,250e3,6):8.1f} {sens(sf,500e3,6):8.1f}")
    check("SF12/125 NF 6 dB = -137 dBm (SX1262 datasheet, KB 15)", abs(sens(12, 125e3, 6) + 137.0) < 0.1)
    print("   R1 isolation budget (leakage >= attenuation + 20 dB):")
    for lab, psrc in (("SX1262 dev board at -9 dBm", -9.0), ("same + 40 dB pad inside the TX box", -49.0)):
        for sf in (7, 12):
            a = psrc - sens(sf, 125e3, 6)
            print(f"      {lab}, SF{sf}/125: attenuation {a:.0f} dB, leakage suppression >= {a+20:.0f} dB")
    # PER-waterfall precision (Fisher information, ideal SF7 PER shape, location unknown)
    sf = 7
    grid = np.linspace(-9.5, -5.0, 91)
    pc = np.array([per_curve(sf, s) for s in grid])
    s0 = float(np.interp(0.01, pc[::-1], grid[::-1]))
    dP = np.gradient(pc, grid)
    print(f"   R1 ideal SF7 (64 B) PER = 1 % at SNR {s0:.2f} dB; slope there {np.interp(s0, grid, dP)*100:.1f} %/dB")
    steps = [1.0, 0.5, 0.0, -0.5, -1.0]           # dB relative to the 1 % point (signal above/below)
    for n in (100, 300, 1000):
        info = 0.0
        for st in steps:
            s = s0 + st
            p = float(np.interp(s, grid, pc))
            d = float(np.interp(s, grid, dP))
            p = min(max(p, 1e-6), 1 - 1e-6)
            info += n * d * d / (p * (1 - p))
        sig = 1 / math.sqrt(info)
        print(f"      5 steps x {n:4d} packets: sigma(S_1%) = {sig:.3f} dB (shape known); ~{sig*math.sqrt(2):.3f} dB if slope fitted too")
    U_level = 2 * rss(0.33 / 2, 0.2 / 2, 0.1 / 2, 0.1 / 2, ushape(0.1))   # source, step att, 2 pads, mismatch
    U_R1 = rss(U_level, 2 * 0.1)
    print(f"   R1 level uncertainty (sensor-referenced source, VNA-calibrated attenuator): U = +-{U_level:.2f} dB; "
          f"with the waterfall fit U_R1 = +-{U_R1:.2f} dB (k=2)")
    check("R1 can separate a 3 dB-NF module from a 6 dB-NF bare chip (U_R1 < 1.5 dB)", U_R1 < 1.5)
    print(f"      acceptance vs datasheet (+-2 dB): +-{band(2.0, U_R1):.2f} dB")

    # R5 Y-factor readings, ENR 15 dB, T_hot = 290 (1 + ENR)
    Th = 290 * (1 + 10 ** 1.5)
    print(f"   R5 Y-factor readings, ENR 15 dB (T_hot {Th:.0f} K), DUT alone (no second stage):")
    for nf in (0.45, 0.8, 1.0, 2.2, 5.4, 12.0):
        te = 290 * (10 ** (nf / 10) - 1)
        print(f"      NF {nf:4.2f} dB -> Y = {db((Th + te)/(290 + te)):.2f} dB")
    te_c = 290 * (10 ** (0.97 / 10) - 1)
    Y = db((Th + te_c) / (290 + te_c))
    check("Y for a 0.97 dB chain = 14.20 dB (LNA recipe, T_hot 9461 K)", abs(Y - 14.20) < 0.05, f"({Y:.2f} dB)")
    print("      NF uncertainty = ENR uncertainty (1:1, KB 17/NF): uncalibrated cheap source (+-1 dB assumed) "
          "-> +-1 dB; calibrated (+-0.2 dB) -> +-0.25 dB with Y noise. N2 band +-0.4 dB needs the calibrated source.")
    # R3 RTL-SDR NF vs gain: two-parameter structural model NF(G) = NFa + 10log(1 + 10^((Gx - G)/10))
    print("   R3 RTL NF(G) model: NF_a + 10log10(1 + 10^((G_x - G)/10)); KB anchor NF 5.4 dB @437 MHz (V3, LSF)")
    for G in (-15, -10, -5, 0, 5, 10):
        print(f"      G - G_x = {G:+3d} dB -> NF = NF_a + {db(1 + 10 ** (-G / 10)):.2f} dB")
    return {"U_R1": U_R1}


# ------------------------------------------------------------------------------------------- S4
def s4():
    print("\nS4  Link")
    null = 2.15 - (-14.0)
    for d in (1.0, 2.0):
        aeq = 20 * math.log10(15.0 / d) + null
        print(f"   L1 15-km-equivalent attenuation at {d:.0f} km: {aeq:.1f} dB")
    check("A_eq(1 km) = 39.7 dB (link recipe ex. 7)", abs(20 * math.log10(15) + null - 39.7) < 0.05)
    eirp = 10.5 - 0.5 + 2.15
    prx = eirp - 20 * math.log10(4 * math.pi * 1e3 * 433.125e6 / C0) + 10.0 - 3.0
    print(f"   L1 free-space P_rx(1 km, 0 dB inserted) = {prx:.1f} dBm -> A_fail = {prx+125.5:.1f} dB (SF7/250, S -125.5 dBm)")
    check("A_fail(1 km) ~ 59.5 dB (link recipe ex. 7)", abs(prx + 125.5 - 59.5) < 0.3)
    for dA in (0.5, 1, 2, 3):
        print(f"      attenuation error {dA} dB -> range error +{(10**(dA/20)-1)*100:.0f} % / -{(1-10**(-dA/20))*100:.0f} %")
    # L2 ground range test, 10 mW e.r.p. (EIRP 12.15 dBm), 1.5 m dipoles, SF9/125 module S = -129.5 dBm
    f = 433.125e6
    er, sig = GROUNDS["medium dry"]
    print("   L2 ground range test, both dipoles 1.5 m, 10 mW e.r.p.; P_rx (dBm) vs model:")
    print("      d(km)  two-ray V   two-ray H   plane-earth  Egli(+20log(f/40))  free space")
    dist = [0.2, 0.5, 1.0, 2.0, 3.0]
    for d in dist:
        lv = float(two_ray_loss(d * 1e3, 1.5, 1.5, f, er, sig, "V"))
        lh = float(two_ray_loss(d * 1e3, 1.5, 1.5, f, er, sig, "H"))
        pe = float(plane_earth(d, 1.5, 1.5))
        eg = float(egli_ratio(433.125, 1.5, 1.5, d))
        fs = 20 * math.log10(4 * math.pi * d * 1e3 * f / C0)
        g = 2 * 2.15
        print(f"      {d:4.1f}  {12.15-lv+2.15:9.1f} {12.15-lh+2.15:10.1f} {12.15-pe+2.15:11.1f} "
              f"{12.15-eg+2.15:14.1f} {12.15-fs+2.15:15.1f}")
    # range with 10 dB fade margin, plane-earth: P_rx = EIRP + G_r - PL >= S + 10
    pl_max = 12.15 + 2.15 - (-129.5 + 10)
    d_pe = 10 ** ((pl_max + 20 * math.log10(1.5 * 1.5)) / 40) / 1e3
    print(f"   L2 plane-earth range with 10 dB margin (SF9/125, S -129.5 dBm): {d_pe:.2f} km")
    check("ground range ~3.3 km (beginner ladder rung 7)", abs(d_pe - 3.3) < 0.2, f"({d_pe:.2f} km)")
    lv1, lv2 = (float(two_ray_loss(x, 1.5, 1.5, f, er, sig, "V")) for x in (500.0, 2000.0))
    print(f"   L2 two-ray (V) slope 0.5-2 km: n = {(lv2-lv1)/(10*math.log10(4)):.2f} (pre-register n = 4 +- 0.5)")
    # L3 landed: rocket antenna 0.2 m, mast 2 m / 6 m
    print("   L3 landed path loss (dB), rocket 0.2 m above ground:")
    for d in (0.5, 1.0, 2.0, 3.0):
        print(f"      {d:3.1f} km: plane-earth 2 m {plane_earth(d,0.2,2.0):.1f}, 6 m {plane_earth(d,0.2,6.0):.1f}; "
              f"two-ray V 2 m {float(two_ray_loss(d*1e3,0.2,2.0,f,er,sig,'V')):.1f}")
    print(f"   L3 recipe band '-50 %/+0 %' in range == PL excess 0 .. +{40*math.log10(2):.1f} dB over plane-earth")


# ------------------------------------------------------------------------------------------- S5
def s5():
    print("\nS5  Rocket-specific")
    print("   K1 Doppler-rate thresholds, 40 B frame CR4/5, 8-sym preamble, explicit header:")
    print("      setting    ToA(ms) limit(Hz) Semtech(Hz/s) no-track(Hz/s)  g@433  g@868  g@905 (Semtech rule)")
    out = {}
    for sf, bw in ((7, 125e3), (8, 125e3), (9, 125e3), (10, 125e3), (12, 125e3), (9, 250e3), (10, 250e3),
                   (9, 500e3), (11, 500e3)):
        de = (2 ** sf / bw) >= 16.38e-3
        toa, _ = toa_sx126x(40, sf, bw, de=de)
        lim = bw / (3 * 2 ** sf) * (16 if de else 1)
        r_s = lim / toa
        n_sym = payload_symbols(40, sf, de=de)
        r_nt = critical_drift_rate(sf, bw, n_sym, de=de)
        g = [r_s / (f / C0 * 9.80665) for f in (433.125e6, 868.125e6, 905e6)]
        out[(sf, bw)] = (toa, lim, r_s, r_nt)
        print(f"      SF{sf:2d}/{bw/1e3:3.0f}k {toa*1e3:8.1f} {lim:8.1f} {r_s:12.1f} {r_nt:13.1f} {g[0]:7.1f} {g[1]:6.1f} {g[2]:6.1f}")
    check("SF9/125 40 B ToA = 288 ms (link recipe)", abs(out[(9, 125e3)][0] * 1e3 - 288) < 2, f"({out[(9,125e3)][0]*1e3:.1f})")
    check("SF9/125 drift limit = 81 Hz", abs(out[(9, 125e3)][1] - 81.4) < 0.5)
    # K2 PLL jerk error (3rd-order loop, w0 = Bn/0.7845)
    lam = C0 / 1575.42e6
    print("   K2 3rd-order PLL steady-state error to jerk J (deg) = 360 J / (lambda w0^3):")
    for bn in (10, 15, 25):
        w0 = bn / 0.7845
        print(f"      Bn {bn:2d} Hz: " + ", ".join(f"{J} g/s {360*J*9.80665/(lam*w0**3):.0f} deg" for J in (10, 50, 100, 300)))
    w0 = 15 / 0.7845
    check("26.5 deg per 10 g/s at Bn 15 Hz (21/gnss-on-rockets)", abs(360 * 98.0665 / (lam * w0 ** 3) - 26.5) < 0.3)
    # K3 L2 C/N0 vs CW jammer (Kaplan-Hegarty, Q = 1, Rc = 1.023 Mchip/s), S = -130 dBm, C/N0 45 dB-Hz
    cn0 = 10 ** 4.5
    print("   K3 L2 C/N0_eff vs CW jammer power J at the GNSS input (S = -130 dBm, 45 dB-Hz clean):")
    jlist = (-120, -110, -105, -100, -98, -95, -90)
    for J in jlist:
        js = 10 ** ((J + 130) / 10)
        eff = 1 / (1 / cn0 + js / 1.023e6)
        print(f"      J {J} dBm: {db(eff):.1f} dB-Hz")
    jt = -130 + db((1 / 10 ** 2.5 - 1 / cn0) * 1.023e6)
    print(f"      J for 25 dB-Hz (tracking lost): {jt:.1f} dBm; for 28 dB-Hz: {-130 + db((1/10**2.8 - 1/cn0)*1.023e6):.1f} dBm")
    check("loss-of-L2 threshold ~ -95 dBm (GNSS front-end recipe G5)", abs(jt + 95) < 1.0, f"({jt:.1f} dBm)")
    print("      E22 3rd harmonics: " + ", ".join(f"CH{c} {3*(410.125+c):.3f}" for c in (0, 2, 3, 5, 6, 23, 24)) + " MHz")
    # K4 HERO: current scales with sqrt(P); test at 10 mW e.r.p. (10.5 dBm conducted) vs flight 33 dBm
    sc = 10 ** ((33 - 10.5) / 20)
    print(f"   K4 HERO: induced current scales sqrt(P): flight/test = x{sc:.1f} (+{33-10.5:.1f} dB in power)")
    for lab, i_flt in (("pass threshold 15 % of 130 mA", 0.15 * 0.130), ("spread leads 0.2 m upper bound", 0.145),
                       ("twisted pair 0.2 m", 0.0004)):
        it = i_flt / sc
        v = it * 1.0                                  # across a 1 ohm dummy bridge
        print(f"      {lab}: flight {i_flt*1e3:.2f} mA -> test {it*1e3:.3f} mA -> {v*1e3:.3f} mV on 1 ohm "
              f"-> {db(v*v/50/1e-3):.1f} dBm into a 50 ohm SA (high-Z tap)")
    # K5 rectification scales with P (V^2)
    print(f"   K5 RF-rectification offset ~ V^2 ~ P: flight/test = x{10**((33-10.5)/10):.0f} (+22.5 dB); a 10 mW test "
          "bounds flight only if its detection floor is 22.5 dB below the allowed offset")


# ------------------------------------------------------------------------------------------- S6
def ring_freqs(r, W, h, er, nmax=4, t=35e-6):
    out = []
    for n in range(1, nmax + 1):
        f = n * C0 / (2 * math.pi * r * math.sqrt(3.4))
        for _ in range(30):
            _, ee = tline.microstrip_kj(W, h, er, f, t)
            f = n * C0 / (2 * math.pi * r * math.sqrt(ee))
        out.append(f)
    return out


def er_from_ring(fn, n, r, W, h, t=35e-6):
    lo, hi = 3.0, 6.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if ring_freqs(r, W, h, mid, n, t)[n - 1] > fn:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def s6():
    print("\nS6  Materials and PCB")
    r, W, h, er = 35e-3, 2.9e-3, 1.51e-3, 4.5
    fr = ring_freqs(r, W, h, er)
    print(f"   M1 ring r_mean {r*1e3:.0f} mm, W {W*1e3:.1f} mm, h {h*1e3:.2f} mm, er {er}: f_n = "
          + ", ".join(f"{x/1e9:.4f}" for x in fr) + " GHz (Kirschning-Jansen dispersion)")
    # Monte-Carlo of the extracted er for mode n = 2 (~1.5 GHz) and n = 3 (~2.2 GHz)
    for n in (2, 3):
        fmeas = fr[n - 1]
        ers = []
        for _ in range(300):
            hh = h + RNG.normal(0, 0.015e-3)            # micrometer-measured thickness minus copper
            WW = W + RNG.normal(0, 0.01e-3)             # microscope-measured width
            rr = r + RNG.normal(0, 0.01e-3)
            ff = fmeas * (1 + RNG.normal(0, 0.00025))   # peak reading (0.05 % at k=2)
            ff *= 1 + RNG.uniform(0, 0.003)             # remove a gap-loading bias of 0..0.3 % (unknown)
            ff *= 1 + RNG.normal(0, 0.0025)             # model form of HJ/KJ eps_eff (0.5 %, k=2)
            ers.append(er_from_ring(ff, n, rr, WW, hh))
        ers = np.array(ers)
        print(f"      mode {n}: extracted er = {ers.mean():.3f}, U(k=2) = +-{2*ers.std():.3f} "
              f"(bias from gap loading included as a uniform 0..0.3 %)")
    for hh in (1.43e-3, 1.6e-3):
        print(f"      if h were {hh*1e3:.2f} mm but analysed as 1.51 mm: er error = {er_from_ring(ring_freqs(r, W, hh, er, 2)[1], 2, r, W, h) - er:+.3f}")
    # M2 impedance coupon
    print("   M2 JLC04161H-7628 masked 0.359 mm: FD 49.5 ohm; with impedance control ~98 % in 45-55 ohm "
          f"(sigma ~{5/2.33:.1f} ohm); 2-layer 2.692 mm: FD 49.2 ohm")
    for lab, span in (("NanoVNA-H4 1.5 GHz", 1.5e9), ("LiteVNA 6.3 GHz", 6.3e9)):
        rise = 0.99 / span
        dist = rise * C0 / math.sqrt(3.3) / 2
        print(f"      TDR {lab}: normal-window rise {rise*1e12:.0f} ps -> {dist*1e3:.0f} mm of microstrip (eps_eff 3.3); "
              f"a flat plateau needs a coupon >= {2*dist*1e3:.0f} mm")
    print("      quarter-wave ripple check: peak |S11| of a Z0 line between 50 ohm ports:")
    for z in (45, 47.5, 52.5, 55):
        g = abs(z * z - 2500) / (z * z + 2500)
        print(f"         Z0 {z} ohm -> |G|max {g:.3f} (RL {-20*math.log10(g):.1f} dB)")
    # M3 via fence: FDFD Lambda vs textbook ln(a/2 pi r)
    LAM = {0.05: 1.25, 0.075: 0.84, 0.10: 0.59, 0.15: 0.276}
    print("   M3 via-fence single-row isolation, 0.3 mm drill (r 0.15 mm), FR-4 er 4.4:")
    for a in (1e-3, 2e-3):
        roa = 0.15e-3 / a
        for f in (1.575e9, 2.45e9):
            lam_d = C0 / f / math.sqrt(4.4)
            iso = []
            for Lam in (LAM[round(roa, 3)], math.log(a / (2 * math.pi * 0.15e-3))):
                x = 2 * (a / lam_d) * Lam
                iso.append(-20 * math.log10(x / math.sqrt(1 + x * x)))
            print(f"      pitch {a*1e3:.0f} mm (r/a {roa:.3f}) at {f/1e9:.3f} GHz: FDFD {iso[0]:.1f} dB, textbook {iso[1]:.1f} dB, "
                  f"difference {iso[1]-iso[0]:+.1f} dB")
            if a == 1e-3 and f == 2.45e9:
                check("1 mm pitch at 2.45 GHz: FDFD ~41 dB, textbook ~13 dB higher (13/vias page)",
                      abs(iso[0] - 41) < 1.0 and abs(iso[1] - iso[0] - 13.4) < 1.0)
            if a == 2e-3 and f == 2.45e9:
                check("2 mm pitch at 2.45 GHz: FDFD ~25 dB", abs(iso[0] - 25) < 1.0)


# ------------------------------------------------------------------------------------------- S7
def s7():
    print("\nS7  Environment")
    for nf in (0.8, 2.0, 6.0):
        te = 290 * (10 ** (nf / 10) - 1)
        row = []
        for lab, ta in (("sky/ground 100 K", 100), ("rural 580 K", 580), ("residential 730 K", 730), ("city 1150 K", 1150)):
            row.append(f"{lab} {db((ta + te)/(290 + te)):+.1f} dB")
        print(f"   E2 noise rise antenna vs 50 ohm load, chain NF {nf} dB (Te {te:.0f} K): " + "; ".join(row))
    print("      (P.372-13 Table 3 values exist only at 425 MHz; 868/915 MHz: no KB prediction -- measurement fills it)")
    from scipy import stats
    for K in (10, 100, 1000):
        thr = stats.gamma.ppf(1 - 1e-3, K, scale=1 / K)
        print(f"   E1 survey threshold, K = {K}: {db(thr):.2f} dB above the mean floor (P_fa 1e-3)")
    check("K = 100 threshold = 1.3 dB (14/signal-ID page)", abs(db(stats.gamma.ppf(1 - 1e-3, 100, scale=0.01)) - 1.3) < 0.1)


# ------------------------------------------------------------------------------------------- schema
FIELDS = [
    ("test_id", "F2 catalogue ID, e.g. F2-A3", True),
    ("prereg_file", "path of the write-once pre-registration file", True),
    ("prereg_sha256", "hash of that file at the time of the run", True),
    ("run_id", "unique run identifier (date + sequence)", True),
    ("date_utc", "ISO 8601 start time", True),
    ("operator", "who ran it", True),
    ("witness", "second person present (optional)", False),
    ("location", "lab/site + coordinates for field tests", True),
    ("dut_id", "board/module serial or MAC; antenna ID", True),
    ("firmware", "git hash + build flags; boot CONFIG line copied verbatim", True),
    ("radio_config", "f, SF, BW, CR, power setting, preamble, sync word, LDRO, LBT (or n/a)", True),
    ("instruments", "model/serial/firmware of every instrument", True),
    ("cal_state", "VNA cal type/plane/kit + verification result; SA level check vs sensor; ENR table; "
                  "SDR ppm calibration; pad/cable S21 values used", True),
    ("setup", "pads, attenuator settings, cables, geometry, photos (file names)", True),
    ("environment", "temperature, humidity, supply voltage, weather for field tests", True),
    ("validity_checks", "e.g. leakage/load test, containment check, 'real vs analyser' 10 dB test; PASS/FAIL", True),
    ("raw_files", "paths of raw data (touchstone, CSV, IQ, logs)", True),
    ("raw_sha256", "hashes of raw files", True),
    ("quantity", "what was measured", True),
    ("measured", "value", True),
    ("unit", "unit", True),
    ("u_c", "combined standard uncertainty", True),
    ("k", "coverage factor (2 unless stated)", True),
    ("budget", "uncertainty components (name=value;...)", True),
    ("predicted", "copied from the pre-registration (never edited)", True),
    ("band", "pre-registered acceptance half-width or limit", True),
    ("outcome", "CONFIRMED|REFUTED|INCONCLUSIVE|VOID|MEASURED|PASS|FAIL|INDETERMINATE", True),
    ("anomalies", "anomaly IDs raised (F2-AN-nn) with disposition", False),
    ("kb_pages", "pages whose Measured section must be updated", True),
    ("notes", "anything else", False),
]
OUTCOMES = {"CONFIRMED", "REFUTED", "INCONCLUSIVE", "VOID", "MEASURED", "PASS", "FAIL", "INDETERMINATE"}


def print_schema():
    print(",".join(f[0] for f in FIELDS))
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "F2 validation result record",
              "type": "object", "required": [f[0] for f in FIELDS if f[2]],
              "properties": {f[0]: {"type": "string", "description": f[1]} for f in FIELDS}}
    schema["properties"]["outcome"]["enum"] = sorted(OUTCOMES)
    for k in ("measured", "u_c", "k"):
        schema["properties"][k] = {"type": "number", "description": dict((f[0], f[1]) for f in FIELDS)[k]}
    print(json.dumps(schema, indent=1))


def validate(path):
    bad = 0
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        print(f"FAIL: {path} has no records (absent evidence is a failure)")
        return 1
    for i, r in enumerate(rows, 1):
        for name, _, req in FIELDS:
            if req and not (r.get(name) or "").strip():
                print(f"record {i} ({r.get('test_id','?')}): missing {name}")
                bad += 1
        if (r.get("outcome") or "").strip() not in OUTCOMES:
            print(f"record {i}: outcome '{r.get('outcome')}' not in {sorted(OUTCOMES)}")
            bad += 1
        for num in ("measured", "u_c", "k"):
            try:
                float(r.get(num, ""))
            except ValueError:
                if (r.get("outcome") or "") != "VOID":
                    print(f"record {i}: {num} is not a number")
                    bad += 1
    print(f"{len(rows)} records, {bad} problems")
    return 1 if bad else 0


def main():
    if "--schema" in sys.argv:
        print_schema()
        return 0
    if "--validate" in sys.argv:
        return validate(sys.argv[sys.argv.index("--validate") + 1])
    s0()
    s1()
    s2()
    s3()
    s4()
    s5()
    s6()
    s7()
    n_ok = sum(ok for _, ok in RESULTS)
    print(f"\nCHECKS: {n_ok}/{len(RESULTS)} PASS")
    return 0 if n_ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
