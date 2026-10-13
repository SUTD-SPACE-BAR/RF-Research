#!/usr/bin/env python3
"""Verification for kb/06-rf-circuits/circulators-isolators.md

 A. Polder permeability tensor of a magnetised ferrite (YIG-like): mu, kappa, mu+-, mu_eff vs bias
 B. Faraday rotation per length: exact tensor result vs high-frequency limit sqrt(er)*wm/(2c)
 C. Ideal circulator S-matrix: lossless (unitary), matched, NON-reciprocal - the only way around the
    three-port theorem; isolator = circulator + load
 D. Non-ideal circulator (finite isolation, IL, termination RL): what VSWR the PA really sees with a bad antenna
 E. Radar/half-duplex T/R: TX leakage into RX = isolation path + antenna reflection path
 F. Junction-circulator disk size (Fay-Comstock first-mode estimate) at 433 MHz / 915 MHz / 2.45 GHz / 10 GHz
Run: python3 tools/verify/rfckt_circulators.py
"""
import numpy as np, sys

ok_all = True
c0 = 299792458.0; mu0 = 4e-7 * np.pi; eps0 = 8.8541878128e-12
gamma = 1.76086e11          # gyromagnetic ratio, rad/s/T


def check(name, cond):
    global ok_all
    ok_all &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


def polder(f, B0, muMs):
    """Relative Polder components (lossless) for internal bias field B0 = mu0*H0 (T) and saturation mu0*Ms (T)."""
    w = 2 * np.pi * f; w0 = gamma * B0; wm = gamma * muMs
    mu = 1 + w0 * wm / (w0 ** 2 - w ** 2)
    ka = w * wm / (w0 ** 2 - w ** 2)
    return mu, ka


# ---------------------------------------------------------------- A. Polder tensor
muMs = 0.178            # YIG 4piMs = 1780 G
print("A: YIG (mu0 Ms = 0.178 T), f = 10 GHz:  B0 (T)  FMR (GHz)   mu      kappa    mu+     mu-     mu_eff")
for B0 in (0.05, 0.2, 0.30, 0.45):
    mu, ka = polder(10e9, B0, muMs)
    print(f"                                        {B0:4.2f}   {gamma*B0/2/np.pi/1e9:6.2f}   {mu:7.3f} {ka:7.3f} {mu+ka:7.3f} {mu-ka:7.3f} {(mu**2-ka**2)/mu:7.3f}")
print(f"   gyromagnetic ratio gamma/2pi = {gamma/2/np.pi/1e9:.2f} GHz/T (= 2.80 MHz/Oe); YIG FMR at 0.1 T internal field: {gamma*0.1/2/np.pi/1e9:.2f} GHz")
check("A1 gamma/2pi = 28.0 GHz/T", abs(gamma / 2 / np.pi / 1e9 - 28.02) < 0.05)

# ---------------------------------------------------------------- B. Faraday rotation
er = 15.0
for f in (5e9, 10e9, 20e9):
    mu, ka = polder(f, 0.01, muMs)       # weak bias (just saturating), below resonance region far away
    k0 = 2 * np.pi * f / c0
    if mu - abs(ka) < 0:
        print(f"B: {f/1e9:4.1f} GHz, weak bias: one circular polarisation is cut off (mu -/+ kappa < 0: 'low-field loss' "
              f"region for f < ~ gamma*mu0*Ms/2pi = {gamma*muMs/2/np.pi/1e9:.1f} GHz)")
        continue
    bp = k0 * np.sqrt(er * (mu + ka)); bm = k0 * np.sqrt(er * (mu - ka))
    theta = abs(bp - bm) / 2
    hf = np.sqrt(er) * gamma * muMs / (2 * c0)
    print(f"B: {f/1e9:4.1f} GHz, weak bias: Faraday rotation {np.degrees(theta)/1e3:.2f} deg/mm (high-frequency limit "
          f"sqrt(er) wm/(2c) = {np.degrees(hf)/1e3:.2f} deg/mm)")
mu, ka = polder(20e9, 0.01, muMs)
k0 = 2 * np.pi * 20e9 / c0
theta20 = abs(k0 * np.sqrt(er * (mu + ka)) - k0 * np.sqrt(er * (mu - ka))) / 2
check("B1 Faraday rotation approaches the frequency-independent limit sqrt(er)*wm/(2c) at high frequency",
      abs(theta20 / (np.sqrt(er) * gamma * muMs / (2 * c0)) - 1) < 0.05)

# ---------------------------------------------------------------- C. ideal circulator
S = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], complex)
check("C1 ideal circulator is lossless (unitary) and matched", np.allclose(S.conj().T @ S, np.eye(3)) and np.allclose(np.diag(S), 0))
check("C2 ...and non-reciprocal (S != S^T)", not np.allclose(S, S.T))
# isolator: terminate port 3 in a matched load -> two-port S between 1 and 2
Siso = S[:2, :2]
print(f"C: isolator (port 3 terminated): forward |S21| = {abs(Siso[1,0]):.0f}, reverse |S12| = {abs(Siso[0,1]):.0f}")

# ---------------------------------------------------------------- D. non-ideal circulator with a bad antenna
def circ(IL_db=0.4, iso_db=20.0, rl_db=20.0):
    a = 10 ** (-IL_db / 20); b = 10 ** (-iso_db / 20); r = 10 ** (-rl_db / 20)
    # clockwise 1->2->3->1 transmission a, reverse leakage b, port match r
    return np.array([[r, b, a], [a, r, b], [b, a, r]], complex)


def reduce_with_load(S3, port, GL):
    """Terminate 'port' of a 3-port with reflection GL; return the remaining 2-port."""
    idx = [i for i in range(3) if i != port]
    Spp = S3[np.ix_(idx, idx)]; Spk = S3[np.ix_(idx, [port])]; Skp = S3[np.ix_([port], idx)]; Skk = S3[port, port]
    return Spp + Spk @ Skp * GL / (1 - Skk * GL)


print("D: PA on port 1, antenna on port 2, termination on port 3 (IL 0.4 dB, isolation 20 dB, port RL 20 dB):")
for Gant_db, lab in ((-20, "good antenna (RL 20 dB)"), (-6, "VSWR 3"), (0, "open / broken antenna")):
    GL_ant = 10 ** (Gant_db / 20)
    for term_rl in (30, 15):
        S3 = circ()
        two = reduce_with_load(S3, 2, 10 ** (-term_rl / 20))       # termination on port 3
        Gin = two[0, 0] + two[0, 1] * two[1, 0] * GL_ant / (1 - two[1, 1] * GL_ant)
        vswr = (1 + abs(Gin)) / (1 - abs(Gin))
        print(f"   {lab:26s} termination RL {term_rl} dB: PA sees |Gamma| = {abs(Gin):.3f} (RL {-20*np.log10(abs(Gin)):.1f} dB, VSWR {vswr:.2f})")
S3 = circ(); two = reduce_with_load(S3, 2, 10 ** (-30 / 20))
Gin_open = two[0, 0] + two[0, 1] * two[1, 0] * 1.0 / (1 - two[1, 1] * 1.0)
check("D1 with an open antenna the PA sees VSWR < 2 (vs infinite without the circulator); limited by isolation and port RL",
      (1 + abs(Gin_open)) / (1 - abs(Gin_open)) < 2.0)
print(f"   power into the port-3 load with an open antenna and 2 W PA: {2*abs(two[1,0])**2 * 10**(-0.8/10):.2f} W -> size the load for full PA power")

# ---------------------------------------------------------------- E. T/R leakage
Ptx = 33.0
for iso_db, ant_rl in ((20, 15), (25, 10), (30, 20)):
    S3 = circ(0.4, iso_db, 20)
    # port 1 TX, port 2 antenna (reflection G), port 3 RX (matched)
    G = 10 ** (-ant_rl / 20)
    two = reduce_with_load(S3, 1, G)     # remaining ports 1 (TX) and 3 (RX) -> indices 0,1
    leak = abs(two[1, 0]) ** 2
    print(f"E: (worst-case in-phase addition) TX {Ptx:.0f} dBm, isolation {iso_db} dB, antenna RL {ant_rl} dB -> power at RX port {Ptx + 10*np.log10(leak):.1f} dBm "
          f"(isolation path alone {Ptx - iso_db:.0f} dBm, antenna-reflection path ~{Ptx - ant_rl - 0.8:.1f} dBm)")
S3 = circ(0.4, 30, 20); two = reduce_with_load(S3, 1, 10 ** (-10 / 20))
check("E1 antenna reflection, not circulator isolation, usually dominates T/R leakage", 10 * np.log10(abs(two[1, 0]) ** 2) > -25)

# ---------------------------------------------------------------- F. junction circulator size
print("F: Y-junction disk radius (first circulation mode, kR ~ 1.84, eps_f 15, mu_eff ~ 1):")
for f in (433.92e6, 915e6, 2.45e9, 10e9):
    k = 2 * np.pi * f / c0 * np.sqrt(15 * 1.0)
    R = 1.84 / k
    print(f"   {f/1e9:6.3f} GHz: R ~ {R*1e3:6.1f} mm")
R433 = 1.84 / (2 * np.pi * 433.92e6 / c0 * np.sqrt(15))
check("F1 distributed junction circulators at 433 MHz would be ~5 cm radius -> lumped-element designs used at UHF", R433 > 0.04)

print("\nALL PASS" if ok_all else "\nSOME CHECKS FAILED")
sys.exit(0 if ok_all else 1)
