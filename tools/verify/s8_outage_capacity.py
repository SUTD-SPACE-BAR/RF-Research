#!/usr/bin/env python3
"""s8_outage_capacity.py — checks for the fading-capacity / adaptive-modulation section of
kb/10-comms-modulation/ber-ebn0-and-shannon.md (W5-S8, gap G-10-05).

1. Outage capacity of flat Rayleigh fading: P_out(R) = 1 - exp(-(2^R - 1)/rho); C_eps = log2(1 - rho ln(1 - eps)).
   L-branch MRC: C_eps = log2(1 + rho * Ginv_L(eps)). Monte Carlo vs closed forms.
2. Ergodic capacities at the same mean SNR: AWGN; receiver CSI (closed form e^{1/rho} E1(1/rho) log2 e);
   transmitter + receiver CSI (water-filling in time, Goldsmith-Varaiya); channel inversion (= 0 for Rayleigh);
   truncated channel inversion (optimised cutoff).
3. Adaptive M-QAM (Goldsmith-Chua): BER bound 0.2 exp(-1.5 g/(M-1)) -> continuous-rate efficiency and the
   SNR gap K; discrete-rate {0, BPSK, QPSK, 16, 64, 256-QAM} with constant power vs fixed modulation.
4. LoRa spreading-factor adaptation as the reader's analogue: Rayleigh packet outage per SF, best-goodput SF vs
   mean SNR, and a Semtech-style ADR step count.

Run: python3 tools/verify/s8_outage_capacity.py   (~10 s)
"""
import numpy as np
from scipy import special, optimize, integrate

rng = np.random.default_rng(5)
RES = []


def check(name, ok, detail=""):
    RES.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")


db = lambda x: 10 * np.log10(x)
un = lambda d: 10 ** (d / 10)
LOG2E = np.log2(np.e)

# ---------------------------------------------------------------- 1. outage capacity
print("1. Outage capacity, flat Rayleigh")
rho = un(10)
n = 2_000_000
g1 = rng.exponential(1.0, n)
for eps in (0.01, 0.1):
    cf = np.log2(1 - rho * np.log(1 - eps))
    mc = np.log2(1 + rho * np.quantile(g1, eps))
    check(f"1x1, 10 dB, eps={eps}: C_eps = log2(1 - rho ln(1-eps))", abs(cf - mc) < 0.01, f"CF {cf:.3f} vs MC {mc:.3f} b/s/Hz")
c_awgn = np.log2(1 + rho)
c_erg = LOG2E * np.exp(1 / rho) * special.exp1(1 / rho)
c01 = np.log2(1 - rho * np.log(0.99))
check("10 dB: AWGN 3.46, ergodic 2.91, 1 % outage capacity only 0.14 b/s/Hz", abs(c_awgn - 3.46) < 0.01 and
      abs(c_erg - 2.91) < 0.01 and abs(c01 - 0.138) < 0.002, f"{c_awgn:.2f}/{c_erg:.2f}/{c01:.3f}")
c01_20 = np.log2(1 - un(20) * np.log(0.99))
check("20 dB: 1 % outage capacity ~1.0 b/s/Hz (Rayleigh costs ~20 dB at 1 % vs AWGN)", abs(c01_20 - 1.004) < 0.005,
      f"{c01_20:.3f}")
# SNR needed for 1 b/s/Hz at 1 % outage vs AWGN: rho = 1/ (-ln 0.99) -> 19.98 dB vs 0 dB
need = db(1 / -np.log(0.99))
check("1 b/s/Hz with 1 % outage needs 20.0 dB mean SNR (AWGN: 0 dB)", abs(need - 19.98) < 0.02, f"{need:.2f} dB")
P_out = lambda R, r: 1 - np.exp(-(2 ** R - 1) / r)
check("P_out(1 b/s/Hz) at 10 dB = 9.5 % (same as the KB's 10 dB fade-margin figure)", abs(P_out(1, rho) - 0.0952) < 0.0005,
      f"{P_out(1, rho):.4f}")
for L in (2, 4):
    gL = rng.gamma(L, 1.0, n)
    cf = np.log2(1 + rho * special.gammaincinv(L, 0.01))
    mc = np.log2(1 + rho * np.quantile(gL, 0.01))
    check(f"{L}-branch MRC, 10 dB, 1 %: C_eps = log2(1 + rho Ginv_L(0.01))", abs(cf - mc) < 0.02, f"{cf:.2f} vs {mc:.2f}")
c2 = np.log2(1 + rho * special.gammaincinv(2, 0.01)); c4 = np.log2(1 + rho * special.gammaincinv(4, 0.01))
check("diversity lifts 1 % outage capacity 0.14 -> 1.31 (L=2) -> 3.21 b/s/Hz (L=4) at 10 dB", abs(c2 - 1.31) < 0.01 and abs(c4 - 3.21) < 0.01)

sel2 = np.log2(1 + rho * -np.log(1 - np.sqrt(0.01)))
check("Example 6: 125 kHz at 10 dB -> ergodic 364 kb/s, 1 % outage 17 kb/s, 2-branch MRC 164 kb/s, selection 130 kb/s",
      abs(c_erg * 125 - 363.5) < 1 and abs(c01 * 125 - 17.3) < 0.2 and abs(c2 * 125 - 164) < 1 and abs(sel2 * 125 - 130) < 1,
      f"{c_erg * 125:.0f}/{c01 * 125:.1f}/{c2 * 125:.0f}/{sel2 * 125:.0f} kb/s")
c01_13 = np.log2(1 - un(13) * np.log(0.99))
check("+3 dB power only raises C_1% from 0.14 to 0.26 b/s/Hz", abs(c01_13 - 0.264) < 0.003, f"{c01_13:.3f}")

# ---------------------------------------------------------------- 2. ergodic variants
print("\n2. Ergodic capacities at 10 dB mean SNR")
mc_erg = np.mean(np.log2(1 + rho * g1))
check("receiver-CSI ergodic closed form = MC", abs(mc_erg - c_erg) < 0.005, f"{c_erg:.3f} vs {mc_erg:.3f}")


def wf_time(rho):
    """Goldsmith-Varaiya: find g0 with int_{g0}^inf (1/g0 - 1/g) p(g) dg = 1 (unit mean power); g = rho*x."""
    f = lambda g0: integrate.quad(lambda g: (1 / g0 - 1 / g) * np.exp(-g / rho) / rho, g0, np.inf)[0] - 1
    g0 = optimize.brentq(f, 1e-4, 10 * rho)
    C = integrate.quad(lambda g: np.log2(g / g0) * np.exp(-g / rho) / rho, g0, np.inf)[0]
    return g0, C


g0, c_wf = wf_time(rho)
check("water-filling in time (Tx CSI) at 10 dB: ~2.9-3.0 b/s/Hz, within 0.1 of Rx-CSI ergodic", 0 < c_wf - c_erg < 0.1,
      f"{c_wf:.3f} vs {c_erg:.3f}, cutoff g0 = {db(g0):.2f} dB")
g0l, c_wf0 = wf_time(un(0))
check("water-filling helps more at 0 dB mean SNR", (c_wf0 - LOG2E * np.exp(1) * special.exp1(1)) > (c_wf - c_erg),
      f"0 dB: {c_wf0:.3f} vs {LOG2E * np.exp(1) * special.exp1(1):.3f}")
# truncated channel inversion: C(g0) = log2(1 + 1/E_{g>g0}[1/g]) * P(g>g0); E[1/x; x>x0] = E1(x0)
def tci(g0):
    x0 = g0 / rho
    e_inv = special.exp1(x0) / rho          # int_{x0}^inf (1/(rho x)) e^{-x} dx
    return np.log2(1 + 1 / e_inv) * np.exp(-x0)


res = optimize.minimize_scalar(lambda g: -tci(g), bounds=(1e-3, 3 * rho), method="bounded")
c_tci = -res.fun
check("truncated channel inversion at 10 dB ~2.66 b/s/Hz, 0.25 below Rx-CSI ergodic (plain inversion: 0)", abs(c_tci - 2.66) < 0.02,
      f"{c_tci:.3f} b/s/Hz, cutoff {db(res.x):.1f} dB, outage {1 - np.exp(-res.x / rho):.1%}")

# ---------------------------------------------------------------- 3. adaptive modulation
print("\n3. Adaptive M-QAM, BER target 1e-3, Rayleigh, mean SNR 20 dB")
BER = 1e-3
K = -1.5 / np.log(5 * BER)
check("Goldsmith-Chua K = -1.5/ln(5 BER) = 0.283 (5.5 dB SNR gap) at 1e-3", abs(K - 0.283) < 0.001, f"K={K:.3f} ({-db(K):.2f} dB)")
# bound check vs exact-ish M-QAM BER at the rate's SNR
for M in (16, 64):
    g = (M - 1) / K * np.log(1 / (5 * BER)) / np.log(1 / (5 * BER))  # SNR where bound = BER
    k = np.log2(M)
    pb = 4 / k * (1 - 1 / np.sqrt(M)) * 0.5 * special.erfc(np.sqrt(3 * g / (M - 1)) / np.sqrt(2))
    check(f"bound is conservative for {M}-QAM (exact BER at the bound's SNR <= 1e-3)", pb <= BER, f"{pb:.1e}")
rho20 = un(20)
x = rng.exponential(1.0, 1_000_000) * rho20
# continuous rate, optimal power (water-filling on K g)
f = lambda g0: np.mean(np.maximum(1 / g0 - 1 / (K * x), 0)) - 1
gk0 = optimize.brentq(f, 1e-4, 10)
se_cont = np.mean(np.where(K * x > gk0, np.log2(K * x / gk0), 0))
c_erg20 = LOG2E * np.exp(1 / rho20) * special.exp1(1 / rho20)
check("continuous-rate adaptive QAM ~ Shannon ergodic minus the 5.5 dB gap", 0 < c_erg20 - se_cont < 2.2,
      f"{se_cont:.2f} vs ergodic {c_erg20:.2f} b/s/Hz")
# discrete rate, constant power: largest M with bound BER <= target
levels = [(1, 2), (2, 4), (4, 16), (6, 64), (8, 256)]
thr = {b: (M - 1) / K for b, M in levels}
thr[1] = special.erfcinv(2 * BER) ** 2          # BPSK exact: Q(sqrt(2g)) = BER -> g = 4.77 (6.8 dB)
rate = np.zeros_like(x)
for b, M in levels:
    rate = np.where(x >= thr[b], b, rate)
se_disc = rate.mean()
p_off = np.mean(x < thr[1])
check("discrete-rate adaptive (constant power) at 20 dB mean: ~3.25 b/s/Hz, off 4.7 % of the time", abs(se_disc - 3.25) < 0.05 and abs(p_off - 0.047) < 0.002,
      f"{se_disc:.2f} b/s/Hz, off {p_off:.2%}")
avg_bpsk = 0.5 * (1 - np.sqrt(rho20 / (1 + rho20)))
check("fixed BPSK cannot meet 1e-3 average BER at 20 dB mean SNR (2.5e-3)", avg_bpsk > BER, f"{avg_bpsk:.1e}")
need_bpsk = optimize.brentq(lambda r: 0.5 * (1 - np.sqrt(r / (1 + r))) - BER, 1, 1e4)
check("fixed BPSK needs 24 dB mean SNR for 1e-3 average BER", abs(db(need_bpsk) - 24.0) < 0.1, f"{db(need_bpsk):.2f} dB")

# ---------------------------------------------------------------- 4. LoRa SF adaptation
print("\n4. LoRa SF adaptation (125 kHz, CR 4/5) on slow Rayleigh fading")
SFs = np.arange(7, 13)
req = -7.5 - 2.5 * (SFs - 7)                         # canonical SX126x SNR thresholds
Rb = SFs * 125e3 / 2.0 ** SFs * 0.8
check("thresholds -7.5 ... -20 dB, 2.5 dB/SF", req[0] == -7.5 and req[-1] == -20.0)
best = {}
for mean_snr in (-20, -15, -10, -5, 0):
    pout = 1 - np.exp(-un(req) / un(mean_snr))      # packet lost if instantaneous SNR < threshold
    good = Rb * (1 - pout)
    i = np.argmax(good)
    best[mean_snr] = (SFs[i], good[i], good[-1], pout[i])
    print(f"   mean SNR {mean_snr:4d} dB: best SF{SFs[i]} goodput {good[i]:7.0f} b/s (P_out {pout[i]:.1%}); "
          f"SF12 always: {good[-1]:5.0f} b/s (P_out {pout[-1]:.1%})")
check("adaptation picks lower SF as mean SNR rises (SF12 at -20 dB, SF7 at 0 dB)", best[-20][0] == 12 and best[0][0] == 7)
check("at 0 dB mean SNR adaptation gives > 10x the goodput of fixed SF12", best[0][1] > 10 * best[0][2],
      f"{best[0][1]:.0f} vs {best[0][2]:.0f} b/s")
check("but the throughput-optimal SF runs at a high packet-loss rate (> 20 %) — telemetry wants reliability",
      best[-10][3] > 0.2, f"{best[-10][3]:.1%}")
# reliability-constrained choice: highest-rate SF with P_out <= 1 %  -> needs ~20 dB margin
marg = db(-1 / np.log(0.99))
check("P_out <= 1 % in Rayleigh needs mean SNR 20 dB above threshold", abs(marg - 19.98) < 0.02, f"{marg:.2f} dB")
# Semtech-style ADR step count: NStep = floor((SNRmax - SNRreq(SF) - margin)/3)
snrmax, sf, margin = -5.0, 12, 10.0
nstep = int(np.floor((snrmax - (-20.0) - margin) / 3))
check("ADR example: SNRmax -5 dB at SF12, margin 10 dB -> NStep 1 (SF12 -> SF11)", nstep == 1, f"NStep={nstep}")
fspl_slope = 20 * np.log10(2)
check("doubling range costs 6.0 dB = 2.4 SF steps of 2.5 dB", abs(fspl_slope / 2.5 - 2.41) < 0.01)

print(f"\n{sum(RES)}/{len(RES)} checks PASS")
