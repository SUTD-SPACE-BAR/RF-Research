#!/usr/bin/env python3
"""
prop_margin.py — verification for kb/09-propagation-link-budget/link-margin-availability.md

1. Lognormal shadowing: margin for a given edge-of-coverage reliability, M = sigma * Q^-1(1 - p).
2. Composite shadowing + Rayleigh (Suzuki): outage vs margin, Monte-Carlo; compare with the naive
   "add the two margins" rule.
3. Combining independent impairment margins: linear sum (worst case) vs root-sum-square of the
   standard deviations (statistical) — and why RSS is only valid for Gaussian-in-dB terms.
4. Packet-level reliability: P(at least one of N packets) = 1 - (1-p)^N (only if packets are
   independent, i.e. spaced by more than the fade decorrelation time) and the correlated case
   (two-state Gilbert–Elliott channel) to show how burst fades defeat repetition.
5. Availability over a flight profile: margin vs time for the 433 MHz link with a rolling dipole
   (toy model) — fraction of packets lost.
"""
import numpy as np
from scipy import stats
rng = np.random.default_rng(11)

print("=== 1. Lognormal shadowing margin ===")
for sigma in (4.0, 6.0, 8.0, 10.0):
    row = []
    for p in (0.5, 0.9, 0.95, 0.99, 0.999):
        row.append(sigma*stats.norm.ppf(p))
    print(f"  sigma={sigma:4.1f} dB: margin for reliability 50/90/95/99/99.9 % = " + " / ".join(f"{m:5.1f}" for m in row) + " dB")

print("\n=== 2. Suzuki (lognormal x Rayleigh) outage vs margin (Monte-Carlo) ===")
print("  Reference: margin is measured from the MEDIAN local-mean power predicted by a path-loss model")
print("  (lognormal shadowing with 0 dB median; Rayleigh fading with unit mean around the local mean).")
print("  Note: the linear MEAN of a lognormal exceeds its median by sigma^2 ln(10)/20 dB (4.1 dB at sigma=6).")
N = 2_000_000
for sigma in (0.0, 4.0, 6.0, 8.0):
    sh = 10**(rng.normal(0, sigma, N)/10)
    g = sh*rng.exponential(1.0, N)
    row = [np.mean(g < 10**(-m/10)) for m in (10, 15, 20, 25, 30)]
    req = [-10*np.log10(np.quantile(g, p)) for p in (0.1, 0.01, 0.001)]
    print(f"  sigma={sigma:3.0f} dB: outage at margin 10/15/20/25/30 dB = " + "  ".join(f"{x:8.2e}" for x in row)
          + f" | margin for 10/1/0.1 % outage = {req[0]:.1f}/{req[1]:.1f}/{req[2]:.1f} dB")
sigma = 8.0
sh = 10**(rng.normal(0, sigma, N)/10); g = sh*rng.exponential(1.0, N)
m_true = -10*np.log10(np.quantile(g, 0.01))
print(f"  sigma=8 dB, 1 % outage: true composite margin {m_true:.1f} dB vs naive 20 + 2.33*8 = {20 + 2.33*8:.1f} dB "
      "(adding the two single-mechanism margins over-designs)")
print(f"  mean-vs-median offset for sigma = 4/6/8 dB: " + ", ".join(f"{s_**2*np.log(10)/20:.1f}" for s_ in (4.0, 6.0, 8.0)) + " dB")

print("\n=== 3. Combining independent impairments ===")
terms = {'shadowing (sigma)': 6.0, 'antenna pattern/attitude (sigma)': 5.0, 'polarisation (sigma)': 3.0,
         'Tx power/temperature (sigma)': 1.0}
lin = sum(2.33*s for s in terms.values())
rss = 2.33*np.sqrt(sum(s**2 for s in terms.values()))
print(f"  99 % margin: linear sum of 2.33 sigma_i = {lin:.1f} dB; RSS 2.33*sqrt(sum sigma_i^2) = {rss:.1f} dB")
# MC check with Gaussian-in-dB terms
tot = sum(rng.normal(0, s, N) for s in terms.values())
print(f"  Monte-Carlo 1 % point of the summed dB-normal terms = {-np.quantile(tot, 0.01):.1f} dB (matches RSS)")

print("\n=== 4. Packet repetition: independent vs bursty fading ===")
p_loss = 0.2
for Nrep in (1, 2, 3, 5, 10):
    print(f"  per-packet loss {p_loss:.0%}, need >=1 of {Nrep:2d} packets: independent P(fail) = {p_loss**Nrep:.2e}")
# Gilbert-Elliott: good state loss 1 %, bad state loss 90 %, mean bad dwell = 20 packets, stationary bad prob 0.2
pg, pb = 0.01, 0.9
Pb = 0.2; dwell_b = 20.0
q = 1/dwell_b                 # P(bad->good)
pbg = q; pgb = q*Pb/(1 - Pb)  # P(good->bad) for stationary Pb
def ge_sim(n_steps):
    st = rng.random() < Pb
    out = np.empty(n_steps, bool)
    for i in range(n_steps):
        out[i] = rng.random() < (pb if st else pg)
        st = (rng.random() > pbg) if st else (rng.random() < pgb)
    return out
losses = ge_sim(400000)
print(f"  Gilbert-Elliott channel: average loss {losses.mean():.1%} (bad-state share {Pb:.0%}, mean burst {dwell_b:.0f} packets)")
for Nrep in (1, 2, 3, 5, 10):
    w = np.lib.stride_tricks.sliding_window_view(losses, Nrep)
    print(f"    need >=1 of {Nrep:2d} consecutive packets: P(fail) = {np.mean(w.all(axis=1)):.2e} "
          f"(independent model would say {losses.mean()**Nrep:.2e})")

print("\n=== 5. Toy flight: rolling dipole + slow lobing, 433 MHz link at 2.4 kb/s ===")
t = np.arange(0, 200, 0.5)                          # 2 packets/s for 200 s
slant = np.interp(t, [0, 10, 40, 90, 200], [0.5e3, 3e3, 12e3, 20e3, 8e3])
c = 299792458.0; f = 433.125e6
fspl = 20*np.log10(4*np.pi*slant*f/c)
# base budget items from prop_link_budget example A (EIRP 32.5 dBm, Rx gain 11 - 3 pol - 1 point - 0.45 feeder - 0.1 gas)
base = 32.5 + 11 - 3 - 1 - 0.45 - 0.1
# attitude: angle between rocket axis and line of sight; dipole power pattern sin^2 psi (floored at -25 dB)
psi = np.radians(np.interp(t, [0, 10, 40, 90, 120, 200], [80, 8, 4, 60, 90, 70]))  # ascent: GS near pad sees the rocket almost end-on (dipole null)
patt = 10*np.log10(np.maximum(np.sin(psi)**2, 10**(-2.5)))
lobing = 10*np.log10(np.maximum(np.abs(1 - 0.7*np.exp(1j*2*np.pi*0.12*t)), 1e-3)**2)
pr = base - fspl + patt + lobing
margin = pr - (-128.0)
print(f"  minimum margin {margin.min():.1f} dB at t = {t[np.argmin(margin)]:.1f} s; "
      f"packets with margin < 0: {np.mean(margin < 0):.1%}; < 10 dB: {np.mean(margin < 10):.1%}")
