#!/usr/bin/env python3
"""s6_ladder_line.py — open-wire / ladder line and twisted pair vs coax (task W5-S6, gap G-03-09) for
kb/03-transmission-lines-matching/coax-and-cables.md.

1. Two-wire Z0 = (eta0 / (pi sqrt(eeff))) acosh(D/d); check against N7WS's measured 399-ohm home-made line
   (16 AWG, 0.75 in spacing, air) as reported by KB6NU (2016).
2. Conductor loss with the proximity factor: R' = 2 * Rs/(pi d) * (D/d)/sqrt((D/d)^2 - 1); alpha_c = R'/(2 Z0).
   Check against the same measurement (0.30 dB/100 ft at 50 MHz) and against the commercial 450-ohm window-line
   range (0.33-0.41 dB/100 ft dry, 4.8-6.1 wet at 50 MHz), scaled to 14 MHz to test the 0.2 dB/100 ft assumed
   on the ATU page.
3. Matched-loss table (dB/100 m) at 3.6-433 MHz: 600-ohm open wire (#12), the measured 450-ohm window line
   (scaled by sqrt f), 300-ohm twin-lead (model), Cat 6A pair (TIA-568-C.2 limits 19.1 dB @100 MHz, 45.3 dB @500 MHz,
   k1 sqrt f + k2 f fit), home-made 24 AWG PVC twisted pair (model), RG-58 and LMR-400 (KB coax fits).
4. Total loss vs SWR for 30 m at 14 MHz with the standard formula; reproduce the ATU page's ladder row.
"""
import numpy as np

ETA0 = 376.730313
MU0 = 4e-7 * np.pi
SIG = 5.8e7
C0 = 299792458.0
FT100 = 30.48            # m per 100 ft
PASS = []


def check(name, cond, detail=""):
    PASS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")


def z0_two_wire(D, d, eeff=1.0):
    return ETA0 / (np.pi * np.sqrt(eeff)) * np.arccosh(D / d)


def alpha_c_two_wire(f, D, d, eeff=1.0, sigma=SIG):
    Rs = np.sqrt(np.pi * f * MU0 / sigma)
    x = D / d
    Rp = 2 * Rs / (np.pi * d) * x / np.sqrt(x ** 2 - 1)
    return Rp / (2 * z0_two_wire(D, d, eeff))          # Np/m


def alpha_d(f, eeff, q_tand):
    """dielectric loss of a quasi-TEM line: pi f sqrt(eeff) (q tan d) / c, q_tand = filling-weighted tan delta"""
    return np.pi * f * np.sqrt(eeff) * q_tand / C0


def db100m(a_np_per_m):
    return a_np_per_m * 8.686 * 100


def coax_fit(k1, k2):
    return lambda fMHz: k1 * np.sqrt(fMHz) + k2 * fMHz       # dB/100 m


def total_loss_db(A_db, swr):
    a = 10 ** (A_db / 10)
    g2 = ((swr - 1) / (swr + 1)) ** 2
    return 10 * np.log10((a ** 2 - g2) / (a * (1 - g2)))


def main():
    print("=== 1-2. check against N7WS's home-made open-wire line (16 AWG = 1.291 mm, 0.75 in = 19.05 mm, air)")
    d16, D = 1.291e-3, 19.05e-3
    z = z0_two_wire(D, d16)
    a50 = alpha_c_two_wire(50e6, D, d16) * 8.686 * FT100
    print(f"   Z0 = {z:.0f} ohm (measured 399); loss at 50 MHz = {a50:.3f} dB/100 ft (measured 0.30)")
    check("two-wire Z0 within 3 % of the measured 399 ohm", abs(z / 399 - 1) < 0.03)
    check("conductor-loss model within 10 % of the measured 0.30 dB/100 ft", abs(a50 / 0.30 - 1) < 0.10)
    lo, hi = 0.33 * np.sqrt(14 / 50), 0.41 * np.sqrt(14 / 50)
    print(f"   commercial 450-ohm window line, dry, scaled sqrt(f) to 14 MHz: {lo:.3f}-{hi:.3f} dB/100 ft "
          f"(ATU page assumes 0.20)")
    check("the ATU page's 0.2 dB/100 ft at 14 MHz lies in the scaled measured range", lo <= 0.20 <= hi + 0.005)
    print(f"   wet/dry ratio at 50 MHz: {4.8/0.41:.0f}-{6.1/0.33:.0f}x (water film on the web: dielectric loss)")

    print("=== 3. matched loss, dB/100 m")
    freqs = [3.6e6, 14e6, 28e6, 50e6, 144e6, 433e6]
    # 600-ohm open wire: 12 AWG (2.053 mm) at 150 mm, air
    d12, D600 = 2.053e-3, 150e-3
    # 300-ohm twin-lead model: 22 AWG (0.644 mm) at 7.6 mm in PE ribbon, eeff ~ 1.5 (VF 0.82), q*tand ~ 1.5e-4
    d22, D300, ee300 = 0.644e-3, 7.6e-3, 1.0 / 0.82 ** 2
    # home-made twisted pair: 24 AWG (0.511 mm) in 0.25 mm PVC -> centre spacing ~1.0 mm; eeff ~ 2 (half in PVC);
    # PVC tan d at 1-100 MHz ~ 0.02-0.05 (assumption) -> q*tand ~ 0.015; +5 % length for the twist.
    d24, Dtp, eetp, qtp = 0.511e-3, 1.02e-3, 2.0, 0.015
    cat6a_k2 = (45.3 - 19.1 * np.sqrt(5)) / (500 - 100 * np.sqrt(5))
    cat6a_k1 = (19.1 - 100 * cat6a_k2) / 10
    cat6a = coax_fit(cat6a_k1, cat6a_k2)
    rg58 = coax_fit(1.123, 0.0123)
    lmr400 = coax_fit(0.403, 0.00082)
    z600 = z0_two_wire(D600, d12)
    z300 = z0_two_wire(D300, d22, ee300)
    ztp = z0_two_wire(Dtp, d24, eetp)
    print(f"   Z0: 600-ohm open wire {z600:.0f}, twin-lead model {z300:.0f}, 24 AWG PVC twisted pair {ztp:.0f} ohm; "
          f"Cat 6A fit k1 {cat6a_k1:.3f}, k2 {cat6a_k2:.5f}")
    hdr = "   f (MHz) | 600 open | 450 window (meas. scaled) | 300 twin | Cat6A | 24AWG TP | RG-58 | LMR-400"
    print(hdr)
    rows = {}
    for f in freqs:
        fm = f / 1e6
        o600 = db100m(alpha_c_two_wire(f, D600, d12))
        win = np.array([0.33, 0.41]) * np.sqrt(fm / 50) / FT100 * 100
        tw = db100m(alpha_c_two_wire(f, D300, d22, ee300) + alpha_d(f, ee300, 1.5e-4))
        tp = db100m(1.05 * (alpha_c_two_wire(f, Dtp, d24, eetp) + alpha_d(f, eetp, qtp)))
        rows[fm] = (o600, win, tw, cat6a(fm), tp, rg58(fm), lmr400(fm))
        print(f"   {fm:7.1f} | {o600:8.2f} | {win[0]:5.2f}-{win[1]:5.2f}              | {tw:8.2f} | {cat6a(fm):5.1f} | "
              f"{tp:8.1f} | {rg58(fm):5.1f} | {lmr400(fm):7.2f}")
    check("at 14 MHz ladder line is > 5x lower loss than RG-58", rows[14.0][1][1] * 5 < rows[14.0][5])
    check("home-made twisted pair at 433 MHz is lossier than RG-58", rows[433.0][4] > rows[433.0][5],
          f"{rows[433.0][4]:.0f} vs {rows[433.0][5]:.0f} dB/100 m")
    check("Cat 6A at 433 MHz (~42 dB/100 m) is within 2x of RG-58", rows[433.0][3] < 2 * rows[433.0][5])

    print("=== 4. total loss vs SWR, 30 m at 14 MHz")
    for name, A in (("RG-58 (KB fit)", rg58(14) * 0.3), ("LMR-400", lmr400(14) * 0.3),
                    ("450 ladder, 0.20 dB/100 ft (ATU page)", 0.20 * 30 / FT100),
                    ("450 ladder, measured-dry scaled (0.41 high end)", 0.41 * np.sqrt(14 / 50) * 30 / FT100),
                    ("450 ladder, wet (6.1 dB/100 ft @50 MHz scaled by f)", 6.1 * 14 / 50 * 30 / FT100)):
        print(f"   {name:52s}: matched {A:5.2f} dB | SWR 3 {total_loss_db(A,3):5.2f} | 10 {total_loss_db(A,10):5.2f} | "
              f"20 {total_loss_db(A,20):5.2f} dB")
    check("reproduces the ATU page ladder row (0.20 / 0.32 / 0.90 / 1.63 dB)",
          abs(total_loss_db(0.20 * 30 / FT100, 10) - 0.90) < 0.02 and abs(total_loss_db(0.20 * 30 / FT100, 20) - 1.63) < 0.03)
    print("\nALL PASS" if all(PASS) else "\nSOME CHECKS FAILED")


if __name__ == "__main__":
    main()
