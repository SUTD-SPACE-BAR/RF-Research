#!/usr/bin/env python3
"""
lora_css_sim.py — chirp-spread-spectrum (LoRa-like) modulator/demodulator simulation.

Used by: kb/15-lora-ism-radios/lora-phy-css-math.md, lora-sensitivity-and-link-budget.md,
         lora-impairments-doppler-drift-timing.md

What it does
 1. Builds baseband LoRa symbols at 1 sample/chip (fs = BW):
        x_s[n] = exp(j 2π ( n²/(2N) + (s/N − 1/2) n )),  N = 2^SF, s ∈ {0..N−1}
    (frequency wraps from +BW/2 to −BW/2 automatically by aliasing at fs = BW).
 2. Demodulates by de-chirping (multiply by conj of base up-chirp x_0) and taking an N-point FFT;
    decision = argmax |FFT|  (the optimum non-coherent receiver, Vangelista 2017).
 3. Checks orthogonality numerically (Gram matrix = N·I).
 4. Monte-Carlo symbol-error rate (SER) in AWGN, SNR defined in the full bandwidth BW
    (Semtech convention), and compares with the exact non-coherent orthogonal M-ary SER
    computed by numerical integration  P_c = ∫ f_Rice(r) (1 − e^{−r²})^{M−1} dr, γ = N·SNR.
 5. Converts SER to packet error rate for Semtech's datasheet test packet (64-byte payload,
    CR4/5, explicit header, CRC; PER = 1 %) and prints the required SNR per SF next to the
    Semtech "typical demodulator SNR" table (−2.5 dB at SF5 … −20 dB at SF12).
 6. Impairments: fractional-bin CFO (peak loss), and a linear frequency drift (Doppler rate)
    across a packet with only a start-of-packet CFO correction (no tracking), giving the
    critical drift rate for each SF — used for the rocket Doppler-rate discussion.

Run:  python3 tools/verify/lora_css_sim.py          (≈ 1–3 min; set QUICK=1 env for faster)
"""
import os
import math
import numpy as np
from scipy import integrate, special, optimize

RNG = np.random.default_rng(20260927)
QUICK = os.environ.get("QUICK", "0") == "1"


# ----------------------------------------------------------------------------- modem
def chirp(sf, s=0):
    N = 2 ** sf
    n = np.arange(N)
    return np.exp(2j * np.pi * (n * n / (2 * N) + (s / N - 0.5) * n))


def modulate(sf, symbols):
    """Return array (len(symbols), N) of LoRa symbols."""
    N = 2 ** sf
    n = np.arange(N)
    s = np.asarray(symbols)[:, None]
    return np.exp(2j * np.pi * (n[None, :] ** 2 / (2 * N) + (s / N - 0.5) * n[None, :]))


def demodulate(sf, rx):
    """De-chirp + FFT; rx shape (K, N). Returns hard decisions and |FFT|^2."""
    base_conj = np.conj(chirp(sf, 0))
    spec = np.fft.fft(rx * base_conj[None, :], axis=1)
    mag2 = np.abs(spec) ** 2
    return np.argmax(mag2, axis=1), mag2


def check_orthogonality(sf=7):
    X = modulate(sf, np.arange(2 ** sf))
    G = X @ X.conj().T
    off = np.max(np.abs(G - np.diag(np.diag(G))))
    return np.allclose(np.diag(G), 2 ** sf), off


# ----------------------------------------------------------------------------- theory
def ser_theory(sf, snr_db):
    """Exact SER of non-coherent orthogonal M-ary detection, M = N = 2^SF, γ = N·SNR."""
    M = 2 ** sf
    g = M * 10 ** (snr_db / 10)
    sg = math.sqrt(g)

    def integrand(r):
        # Rice pdf for |Y| with unit-variance complex noise: 2r exp(-(r²+γ)) I0(2 r √γ)
        rice = 2 * r * np.exp(-(r - sg) ** 2) * special.i0e(2 * r * sg)
        # P(all M-1 noise bins below r²) computed in log domain
        log_cdf = (M - 1) * np.log1p(-np.exp(-r * r)) if r > 0 else -np.inf
        return rice * np.exp(log_cdf)

    lo, hi = max(0.0, sg - 12), sg + 12
    pc, _ = integrate.quad(integrand, lo, hi, limit=400, points=[sg])
    return max(1.0 - pc, 0.0)


# ----------------------------------------------------------------------------- Monte-Carlo
def ser_mc(sf, snr_db, n_sym, batch=None, cfo_bins=0.0):
    N = 2 ** sf
    batch = batch or max(64, int(4e6 // N))
    sigma2 = 10 ** (-snr_db / 10)
    errs = 0
    done = 0
    n = np.arange(N)
    rot = np.exp(2j * np.pi * cfo_bins * n / N)  # CFO of cfo_bins bins = cfo_bins·BW/N Hz
    while done < n_sym:
        k = min(batch, n_sym - done)
        s = RNG.integers(0, N, k)
        x = modulate(sf, s) * rot[None, :]
        w = np.sqrt(sigma2 / 2) * (RNG.standard_normal((k, N)) + 1j * RNG.standard_normal((k, N)))
        shat, _ = demodulate(sf, x + w)
        if cfo_bins:
            # an ideal receiver that knows the integer part of the CFO removes it
            shat = (shat - int(round(cfo_bins))) % N
        errs += np.count_nonzero(shat != s)
        done += k
    return errs / n_sym


def payload_symbols(pl, sf, cr=1, crc=True, explicit=True, de=False):
    ih = 0 if explicit else 1
    num = 8 * pl - 4 * sf + 28 + 16 * int(crc) - 20 * ih
    if sf <= 6:  # SX126x SF5/6 form
        num = 8 * pl + 16 * int(crc) - 4 * sf + (20 if explicit else 0)
    return 8 + max(math.ceil(num / (4 * (sf - 2 * int(de)))) * (cr + 4), 0)


def snr_for_per(sf, per=0.01, pl=64, de=None):
    """SNR [dB] at which an ideal receiver reaches PER for Semtech's test packet.
    CR4/5 only detects errors, so any symbol error kills the packet:
      PER = 1 − (1 − SER)^Nsym.
    With LDRO the alphabet is 2^(SF−2) (only every 4th bin used) — modelled as M = 2^(SF−2)
    orthogonal symbols with the same symbol energy (γ = 2^SF · SNR)."""
    if de is None:
        de = sf >= 11  # 125 kHz rule
    nsym = payload_symbols(pl, sf, de=de)
    ser_target = 1 - (1 - per) ** (1 / nsym)

    def f(snr_db):
        if de:
            return math.log10(max(ser_theory_ldro(sf, snr_db), 1e-300)) - math.log10(ser_target)
        return math.log10(max(ser_theory(sf, snr_db), 1e-300)) - math.log10(ser_target)

    return optimize.brentq(f, -30, 5, xtol=1e-3), nsym, ser_target


def ser_theory_ldro(sf, snr_db):
    """LDRO: M' = 2^(SF-2) candidate bins, each with full symbol energy γ = 2^SF·SNR."""
    Mp = 2 ** (sf - 2)
    g = 2 ** sf * 10 ** (snr_db / 10)
    sg = math.sqrt(g)

    def integrand(r):
        rice = 2 * r * np.exp(-(r - sg) ** 2) * special.i0e(2 * r * sg)
        log_cdf = (Mp - 1) * np.log1p(-np.exp(-r * r)) if r > 0 else -np.inf
        return rice * np.exp(log_cdf)

    pc, _ = integrate.quad(integrand, max(0.0, sg - 12), sg + 12, limit=400, points=[sg])
    return max(1.0 - pc, 0.0)


# ----------------------------------------------------------------------------- impairments
def fractional_cfo_loss_db(delta_bins, sf=9):
    """Peak magnitude loss when the de-chirped tone falls delta bins off an FFT bin."""
    N = 2 ** sf
    n = np.arange(N)
    tone = np.exp(2j * np.pi * delta_bins * n / N)
    spec = np.abs(np.fft.fft(tone))
    return 20 * np.log10(spec.max() / N)


def drift_symbol_errors(sf, bw_hz, rate_hz_s, n_sym, snr_db=None, de=False):
    """Linear frequency drift (Doppler rate) across n_sym payload symbols; the receiver has
    removed the CFO present at the start of the payload but does NOT track afterwards.
    Returns fraction of symbols in error (noise-free if snr_db is None)."""
    N = 2 ** sf
    Ts = N / bw_hz
    n = np.arange(N)
    t_in = n / bw_hz
    errs = 0
    step = 4 if de else 1
    s = RNG.integers(0, N // step, n_sym) * step
    for k in range(n_sym):
        t = k * Ts + t_in
        phase = 2 * np.pi * 0.5 * rate_hz_s * t * t  # ∫ rate·t dt
        x = modulate(sf, [s[k]])[0] * np.exp(1j * phase)
        if snr_db is not None:
            sig2 = 10 ** (-snr_db / 10)
            x = x + np.sqrt(sig2 / 2) * (RNG.standard_normal(N) + 1j * RNG.standard_normal(N))
        shat, mag2 = demodulate(sf, x[None, :])
        if de:
            # LDRO-style decision: fold to nearest multiple of 4 bins
            shat = (np.round(shat / 4).astype(int) * 4) % N
        errs += int(shat[0] != s[k])
    return errs / n_sym


def critical_drift_rate(sf, bw_hz, n_sym, de=False):
    """Analytic estimate: first error when accumulated drift reaches half a bin (or 2 bins with
    LDRO folding): rate_crit ≈ (0.5·BW/N or 2·BW/N) / (n_sym·Ts)."""
    N = 2 ** sf
    bin_hz = bw_hz / N
    margin_bins = 2.0 if de else 0.5
    return margin_bins * bin_hz / (n_sym * N / bw_hz)


# ----------------------------------------------------------------------------- main
def main():
    ok, off = check_orthogonality(7)
    print(f"[1] Orthogonality SF7: diag == N: {ok}; max |off-diagonal| = {off:.2e}")

    x = chirp(8, 37)
    shat, _ = demodulate(8, x[None, :])
    print(f"[2] Noise-free round trip SF8 symbol 37 -> {int(shat[0])}")

    print("\n[3] SER: Monte-Carlo vs exact non-coherent M-ary theory (SNR in full BW)")
    cases = [(7, [-10, -8, -6]), (9, [-15, -13, -11]), (12, [-23, -21.5, -20])]
    if QUICK:
        cases = [(7, [-10, -8]), (9, [-14])]
    for sf, snrs in cases:
        for snr in snrs:
            th = ser_theory(sf, snr)
            nsym = int(min(4e5, max(2e3, 200 / max(th, 1e-6))))
            if sf == 12:
                nsym = min(nsym, 30000)
            mc = ser_mc(sf, snr, nsym)
            print(f"    SF{sf:2d} SNR {snr:6.1f} dB: theory {th:.3e}   MC {mc:.3e}   (n={nsym})")

    print("\n[4] Required SNR for PER = 1 % (64-byte payload, CR4/5, explicit hdr, CRC),")
    print("    ideal receiver, vs Semtech 'typical demodulator SNR' (SX1261/2 DS Table 6-1):")
    semtech = {5: -2.5, 6: -5, 7: -7.5, 8: -10, 9: -12.5, 10: -15, 11: -17.5, 12: -20}
    print("     SF  Nsym  SER_target   SNR_ideal[dB]  Semtech[dB]  margin[dB]  Eb/N0_ideal[dB]")
    for sf in range(5, 13):
        snr, nsym, st = snr_for_per(sf)
        de = sf >= 11
        # Eb/N0 = SNR * BW / Rb = SNR * 2^SF / ((SF-2DE) * 4/5)
        ebn0 = snr + 10 * math.log10(2 ** sf / ((sf - 2 * de) * 0.8))
        print(f"     {sf:2d}  {nsym:4d}  {st:.2e}     {snr:7.2f}        {semtech[sf]:6.1f}     "
              f"{semtech[sf]-snr:5.2f}      {ebn0:6.2f}")
    print("    (margin = Semtech value − ideal; positive = Semtech needs more SNR, i.e. "
          "implementation loss incl. sync/CFO estimation)")

    print("\n[5] SNR at fixed SER targets (theory):")
    for target in (1e-2, 1e-3, 1e-5):
        row = []
        for sf in range(7, 13):
            f = lambda s: math.log10(max(ser_theory(sf, s), 1e-300)) - math.log10(target)
            row.append(optimize.brentq(f, -35, 5, xtol=1e-3))
        print(f"    SER {target:.0e}: " + "  ".join(f"SF{sf}:{v:6.2f}" for sf, v in zip(range(7, 13), row)))
    diffs = []
    for sf in range(7, 12):
        f1 = lambda s: math.log10(max(ser_theory(sf, s), 1e-300)) + 3
        f2 = lambda s: math.log10(max(ser_theory(sf + 1, s), 1e-300)) + 3
        diffs.append(optimize.brentq(f1, -35, 5) - optimize.brentq(f2, -35, 5))
    print(f"    Gain per SF step at SER 1e-3: " + ", ".join(f"{d:.2f}" for d in diffs) + " dB")

    print("\n[6] Fractional-bin frequency offset -> de-chirped peak loss (no compensation):")
    for d in (0.1, 0.25, 0.5):
        print(f"    offset {d:4.2f} bin: {fractional_cfo_loss_db(d):6.2f} dB")
    if not QUICK:
        for cfo in (0.0, 0.5):
            print(f"    SF9 SER at −12 dB with CFO {cfo} bin: {ser_mc(9, -12, 20000, cfo_bins=cfo):.3e}")

    print("\n[7] Doppler-rate (linear drift) tolerance, no tracking after start-of-payload CFO fix:")
    print("    Packet = 32-byte payload, CR4/5, explicit, CRC; BW125; numbers are the drift rate")
    print("    at which the last payload symbol reaches the decision boundary.")
    bw = 125e3
    for sf in range(7, 13):
        de = sf >= 11
        nsym = payload_symbols(32, sf, de=de)
        rc = critical_drift_rate(sf, bw, nsym, de)
        a433 = rc * 299792458 / 433.125e6
        a915 = rc * 299792458 / 915e6
        print(f"    SF{sf:2d} (LDRO={de!s:5}) Nsym={nsym:3d}: rate_crit ≈ {rc:9.1f} Hz/s  ->  "
              f"LOS accel {a433/9.80665:7.1f} g @433 MHz, {a915/9.80665:7.1f} g @915 MHz")
    if not QUICK:
        nsym = payload_symbols(32, 12, de=True)
        print(f"    Simulation check (noise-free) SF12 BW125 LDRO on, {nsym}-symbol payload "
              "(errors begin at 1.0 x crit):")
        rc = critical_drift_rate(12, bw, nsym, True)
        for mult in (0.5, 1.0, 1.5, 2.0):
            e = drift_symbol_errors(12, bw, mult * rc, nsym, de=True)
            print(f"      rate = {mult:3.1f} × crit ({mult*rc:6.1f} Hz/s): fraction of symbols wrong = {e:.3f}")
        print("    Simulation check (noise-free) SF12 BW125 LDRO OFF:")
        rc0 = critical_drift_rate(12, bw, nsym, False)
        for mult in (0.5, 1.0, 2.0):
            e = drift_symbol_errors(12, bw, mult * rc0, nsym, de=False)
            print(f"      rate = {mult:3.1f} × crit ({mult*rc0:6.1f} Hz/s): fraction of symbols wrong = {e:.3f}")


if __name__ == "__main__":
    main()
