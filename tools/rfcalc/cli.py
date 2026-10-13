"""Command-line front end:  python -m rfcalc <command> [args]   (run from the tools/ directory,
or with PYTHONPATH pointing at tools/).  Values use SI units; frequencies accept suffixes k/M/G
(e.g. 433.125M), lengths accept mm/um/km suffixes (e.g. 1.51mm, 30km).
"""
import argparse
import math
import re

from . import arrays, itm, link, lora, matching, noise, propagation, radar, resonance, skin, tline, units

_SI = {"T": 1e12, "G": 1e9, "M": 1e6, "k": 1e3, "K": 1e3, "m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15}
_LEN = {"km": 1e3, "m": 1.0, "cm": 1e-2, "mm": 1e-3, "um": 1e-6, "mil": 25.4e-6}


def num(s):
    """Parse '433.125M', '12p', '1.51mm', '30km', '2.4G', '1e-3'."""
    s = s.strip()
    for suf, mul in sorted(_LEN.items(), key=lambda kv: -len(kv[0])):
        if s.endswith(suf) and re.fullmatch(r"[-+0-9.eE]+", s[: -len(suf)] or "x"):
            return float(s[: -len(suf)]) * mul
    for suf in ("Hz", "hz", "F", "H", "ohm"):
        if s.endswith(suf) and len(s) > len(suf):
            s = s[: -len(suf)]
    if s and s[-1] in _SI and re.fullmatch(r"[-+0-9.eE]+", s[:-1] or "x"):
        return float(s[:-1]) * _SI[s[-1]]
    return float(s)


def eng(x, unit=""):
    if x == 0 or not math.isfinite(x):
        return f"{x} {unit}".strip()
    for p, sym in ((1e12, "T"), (1e9, "G"), (1e6, "M"), (1e3, "k"), (1, ""), (1e-3, "m"), (1e-6, "u"),
                   (1e-9, "n"), (1e-12, "p"), (1e-15, "f")):
        if abs(x) >= p:
            return f"{x/p:.4g} {sym}{unit}"
    return f"{x:.4g} {unit}"


def cmd_fspl(a):
    L = float(link.fspl_db(a.f, a.d))
    print(f"FSPL({eng(a.f,'Hz')}, {eng(a.d,'m')}) = {L:.2f} dB")


def cmd_link(a):
    lb = link.LinkBudget(f_hz=a.f, d_m=a.d)
    lb.add("Tx power [dBm]", a.pt).add("Tx feeder", -a.tx_loss).add("Tx antenna", a.gt)
    lb.add("Rx antenna", a.gr).add("Rx feeder", -a.rx_loss).add("Other losses", -a.other)
    sens = a.sens
    if sens is None and a.sf is not None:
        sens = lora.sensitivity_dbm(a.sf, a.bw, a.nf)
    print(lb.report(sens))
    if sens is not None:
        print(f"  Free-space range at {a.margin:.0f} dB margin: {lb.range_for_margin_m(sens, a.margin)/1e3:.1f} km")


def cmd_fresnel(a):
    d1 = a.d / 2 if a.d1 is None else a.d1
    d2 = a.d - d1
    r = float(propagation.fresnel_radius(a.f, d1, d2, a.n))
    b = float(propagation.earth_bulge(d1, d2, a.k))
    print(f"Fresnel zone {a.n} radius at d1={eng(d1,'m')}, d2={eng(d2,'m')}: {r:.2f} m "
          f"(60 %: {0.6*r:.2f} m); earth bulge (k={a.k:.3f}) {b:.2f} m")


def cmd_horizon(a):
    d = float(propagation.radio_horizon_m(a.h, a.k))
    print(f"Radio horizon from {a.h:g} m (k={a.k:.3f}): {d/1e3:.2f} km")
    if a.h2 is not None:
        print(f"Max LOS range to a {a.h2:g} m target: {float(propagation.max_los_distance_m(a.h, a.h2, a.k))/1e3:.2f} km")


def cmd_cascade(a):
    stages = []
    for spec in a.stage:
        parts = spec.split(":")
        name = parts[0]
        g = float(parts[1])
        nf = float(parts[2]) if len(parts) > 2 and parts[2] != "" else None
        iip3 = float(parts[3]) if len(parts) > 3 and parts[3] != "" else None
        stages.append(noise.Stage(name, g, nf, iip3))
    print(noise.format_cascade(stages, a.bw, a.snr, a.ta))


def cmd_sens(a):
    s = noise.sensitivity_dbm(a.bw, a.nf, a.snr, a.ta)
    print(f"Sensitivity (B={eng(a.bw,'Hz')}, NF={a.nf} dB, SNR={a.snr} dB"
          f"{'' if a.ta is None else f', Ta={a.ta} K'}) = {s:.2f} dBm")


def cmd_lmatch(a):
    zl = complex(a.zl.replace("i", "j"))
    for s in matching.l_match(zl, a.z0, a.f):
        c = s.components()
        ser = c["series"]
        sh = c["shunt"]
        fmt = lambda t: f"{t[0]} = {eng(t[1], 'H' if t[0] == 'L' else 'F')}"
        print(f"{s.topology:15s} series X = {s.x_series:+8.2f} ohm ({fmt(ser)}), "
              f"shunt B = {s.b_shunt*1e3:+8.3f} mS ({fmt(sh)})  -> Zin = {s.zin(zl, a.z0):.3f}")


def cmd_microstrip(a):
    if a.z0 is not None:
        w = tline.microstrip_width(a.z0, a.h, a.er, a.t)
        print(f"W for {a.z0} ohm (H-J, t={eng(a.t,'m')}): {w*1e3:.4f} mm")
        a.w = w
    z, ee = tline.microstrip_hj(a.w, a.h, a.er, a.t)
    print(f"Microstrip W={a.w*1e3:.4g} mm h={a.h*1e3:.4g} mm er={a.er} t={a.t*1e6:.0f} um: "
          f"H-J Z0={z:.2f} ohm eps_eff={ee:.3f}; Wheeler77 Z0={tline.microstrip_wheeler77(a.w, a.h, a.er, a.t):.2f}")
    if a.f:
        zf, eef = tline.microstrip_kj(a.w, a.h, a.er, a.f, a.t)
        print(f"  at {eng(a.f,'Hz')} (Kirschning-Jansen): Z0={zf:.2f} ohm eps_eff={eef:.3f}, "
              f"lambda_g/4 = {tline.quarter_wave_length(a.f, eef)*1e3:.2f} mm")


def cmd_cpwg(a):
    if a.z0 is not None:
        a.w = tline.cpwg_width(a.z0, a.s, a.h, a.er)
        print(f"W for {a.z0} ohm: {a.w*1e3:.4f} mm")
    z, ee = tline.cpwg(a.w, a.s, a.h, a.er)
    print(f"CPWG W={a.w*1e3:.4g} mm gap={a.s*1e3:.4g} mm h={a.h*1e3:.4g} mm er={a.er}: Z0={z:.2f} ohm "
          f"eps_eff={ee:.3f} (zero-thickness conformal mapping; 35 um Cu lowers Z0 by ~2-4 ohm)")


def cmd_coax(a):
    print(f"Coax d={a.d*1e3:.4g} mm D={a.D*1e3:.4g} mm er={a.er}: Z0={tline.coax_z0(a.d, a.D, a.er):.2f} ohm, "
          f"TE11 cutoff ~ {eng(tline.coax_te11_cutoff_hz(a.d, a.D, a.er),'Hz')}")


def cmd_skin(a):
    d = float(skin.skin_depth(a.f, a.sigma))
    rs = float(skin.surface_resistance(a.f, a.sigma))
    print(f"Skin depth at {eng(a.f,'Hz')} (sigma={a.sigma:.3g} S/m): {d*1e6:.3f} um; Rs = {rs*1e3:.3f} mohm/sq")


def cmd_lc(a):
    if a.l and a.c:
        print(f"f0 = {eng(resonance.f_res(a.l, a.c),'Hz')}, X0 = {resonance.char_reactance(a.l, a.c):.2f} ohm")
    elif a.l and a.f:
        print(f"C for {eng(a.f,'Hz')} with L={eng(a.l,'H')}: {eng(resonance.c_for_f(a.f, a.l),'F')}")
    elif a.c and a.f:
        print(f"L for {eng(a.f,'Hz')} with C={eng(a.c,'F')}: {eng(resonance.l_for_f(a.f, a.c),'H')}")
    else:
        raise SystemExit("give two of --l, --c, --f")


def cmd_radar(a):
    snr = radar.radar_snr_db(a.pt, a.g, a.g, a.f, a.rcs, a.r, a.nf, t_int_s=a.tint, losses_db=a.loss)
    rmax = radar.radar_max_range_m(a.pt, a.g, a.g, a.f, a.rcs, a.snr_min, a.nf, t_int_s=a.tint, losses_db=a.loss)
    print(f"SNR at {eng(a.r,'m')} = {snr:.1f} dB; range for SNR {a.snr_min} dB = {eng(rmax,'m')}")


def cmd_fmcw(a):
    p = radar.fmcw_params(a.f0, a.bw, a.tc, a.fs, a.n, complex_if=not a.real_if)
    for k, v in p.items():
        print(f"  {k:22s} {v:.6g}")


def cmd_array(a):
    print(f"N={a.n}, d={a.d} lambda, steer {a.steer} deg: HPBW ~ {arrays.hpbw_deg(a.n, a.d, a.steer):.2f} deg, "
          f"phase step {arrays.steering_phase_deg(a.d, a.steer):.1f} deg, "
          f"D = {10*math.log10(arrays.directivity_ula(a.n, a.d, a.steer)):.2f} dBi (isotropic elements), "
          f"no-grating spacing limit {arrays.max_spacing_no_grating(a.steer):.3f} lambda")


def cmd_lora(a):
    toa = lora.time_on_air(a.pl, a.sf, a.bw, a.cr, a.preamble, chip=a.chip)
    print(f"SF{a.sf}/BW{a.bw/1e3:g}k CR4/{4+a.cr}, {a.pl} B: ToA = {toa*1e3:.2f} ms "
          f"({lora.n_symbols(a.pl, a.sf, a.cr, a.preamble, bw_hz=a.bw, chip=a.chip):.2f} symbols), "
          f"Rb = {lora.bitrate(a.sf, a.bw, a.cr, lora.ldro_auto(a.sf, a.bw)):.0f} b/s, "
          f"sensitivity (NF {a.nf} dB) = {lora.sensitivity_dbm(a.sf, a.bw, a.nf):.1f} dBm")


def cmd_db(a):
    v = a.value
    if a.kind == "dbm2w":
        print(f"{v} dBm = {eng(float(units.dbm_to_w(v)),'W')} = {float(units.dbm_to_vrms(v)):.4g} V rms in 50 ohm")
    elif a.kind == "w2dbm":
        print(f"{eng(v,'W')} = {float(units.w_to_dbm(v)):.2f} dBm")
    elif a.kind == "vswr":
        g = float(units.gamma_from_vswr(v))
        print(f"VSWR {v}: |Gamma| = {g:.4f}, RL = {float(units.return_loss_db(g)):.2f} dB, "
              f"mismatch loss = {float(units.mismatch_loss_db(g)):.3f} dB")
    elif a.kind == "rl":
        g = float(units.gamma_from_rl(v))
        print(f"RL {v} dB: |Gamma| = {g:.4f}, VSWR = {float(units.vswr_from_gamma(g)):.3f}, "
              f"mismatch loss = {float(units.mismatch_loss_db(g)):.3f} dB")


def cmd_itm(a):
    """ITM (Longley-Rice) basic transmission loss: area mode (--d, --dh) or point-to-point (--profile)."""
    common = dict(climate=a.climate, N_0=a.n0, f_mhz=a.f / 1e6, pol=a.pol, epsilon=a.er, sigma=a.sigma,
                  mdvar=a.mdvar, time_pct=a.time, location_pct=a.location, situation_pct=a.situation)
    if a.profile:
        with open(a.profile) as fh:
            z = [float(v) for v in fh.read().replace(",", " ").split()]
        pfl = itm.profile_from_elevations(z, a.spacing)
        r = itm.itm_p2p_tls(a.htx, a.hrx, pfl, **common)
        what = f"point-to-point, {len(z)} points at {a.spacing:g} m"
    else:
        if a.d is None:
            raise SystemExit("itm: give --d (area mode) or --profile FILE --spacing M (point-to-point)")
        r = itm.itm_area_tls(a.htx, a.hrx, a.siting, a.siting, a.d / 1e3, a.dh, **common)
        what = f"area mode, delta_h {a.dh:g} m, siting {a.siting}"
    print(f"ITM {what}: f {eng(a.f,'Hz')}, d {r['d_km']:.2f} km, h_tx {a.htx:g} m, h_rx {a.hrx:g} m")
    print(f"  basic transmission loss {r['A_db']:.2f} dB = FSPL {r['A_fs_db']:.2f} dB + {r['A_db']-r['A_fs_db']:.2f} dB "
          f"(mode {r['mode_name']}; time/location/situation {a.time:g}/{a.location:g}/{a.situation:g} %)")
    if r["warning_names"]:
        print("  warnings: " + ", ".join(r["warning_names"]))


def build_parser():
    p = argparse.ArgumentParser(prog="rfcalc", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("fspl", help="free-space path loss");
    s.add_argument("f", type=num); s.add_argument("d", type=num); s.set_defaults(fn=cmd_fspl)

    s = sp.add_parser("link", help="link budget (Friis + LoRa sensitivity)")
    s.add_argument("--f", type=num, required=True); s.add_argument("--d", type=num, required=True)
    s.add_argument("--pt", type=float, required=True, help="Tx power dBm")
    s.add_argument("--gt", type=float, default=0.0); s.add_argument("--gr", type=float, default=0.0)
    s.add_argument("--tx-loss", type=float, default=0.0); s.add_argument("--rx-loss", type=float, default=0.0)
    s.add_argument("--other", type=float, default=0.0, help="other losses dB (positive)")
    s.add_argument("--sens", type=float, help="receiver sensitivity dBm")
    s.add_argument("--sf", type=int, help="LoRa SF (computes sensitivity)"); s.add_argument("--bw", type=num, default=125e3)
    s.add_argument("--nf", type=float, default=6.0); s.add_argument("--margin", type=float, default=0.0)
    s.set_defaults(fn=cmd_link)

    s = sp.add_parser("fresnel", help="Fresnel zone radius and earth bulge")
    s.add_argument("f", type=num); s.add_argument("d", type=num, help="path length")
    s.add_argument("--d1", type=num, help="distance from one end (default mid-path)")
    s.add_argument("--n", type=int, default=1); s.add_argument("--k", type=float, default=4 / 3)
    s.set_defaults(fn=cmd_fresnel)

    s = sp.add_parser("horizon", help="radio horizon distance")
    s.add_argument("h", type=num); s.add_argument("--h2", type=num); s.add_argument("--k", type=float, default=4 / 3)
    s.set_defaults(fn=cmd_horizon)

    s = sp.add_parser("cascade", help="receiver cascade; --stage name:gain_dB[:NF_dB[:IIP3_dBm]] ...")
    s.add_argument("--stage", action="append", required=True)
    s.add_argument("--bw", type=num); s.add_argument("--snr", type=float); s.add_argument("--ta", type=float, default=290.0)
    s.set_defaults(fn=cmd_cascade)

    s = sp.add_parser("sens", help="receiver sensitivity")
    s.add_argument("--bw", type=num, required=True); s.add_argument("--nf", type=float, required=True)
    s.add_argument("--snr", type=float, required=True); s.add_argument("--ta", type=float)
    s.set_defaults(fn=cmd_sens)

    s = sp.add_parser("lmatch", help="L-network to match ZL (e.g. 32.1-18.5j) to Z0")
    s.add_argument("zl"); s.add_argument("--f", type=num, required=True); s.add_argument("--z0", type=float, default=50.0)
    s.set_defaults(fn=cmd_lmatch)

    s = sp.add_parser("microstrip", help="microstrip Z0 (or --z0 to synthesise W)")
    s.add_argument("--w", type=num); s.add_argument("--h", type=num, required=True)
    s.add_argument("--er", type=float, required=True); s.add_argument("--t", type=num, default=35e-6)
    s.add_argument("--z0", type=float); s.add_argument("--f", type=num)
    s.set_defaults(fn=cmd_microstrip)

    s = sp.add_parser("cpwg", help="grounded CPW Z0 (or --z0 to synthesise W)")
    s.add_argument("--w", type=num); s.add_argument("--s", type=num, required=True)
    s.add_argument("--h", type=num, required=True); s.add_argument("--er", type=float, required=True)
    s.add_argument("--z0", type=float); s.set_defaults(fn=cmd_cpwg)

    s = sp.add_parser("coax", help="coax Z0 from diameters")
    s.add_argument("d", type=num); s.add_argument("D", type=num); s.add_argument("--er", type=float, default=1.0)
    s.set_defaults(fn=cmd_coax)

    s = sp.add_parser("skin", help="skin depth and surface resistance")
    s.add_argument("f", type=num); s.add_argument("--sigma", type=float, default=5.8e7); s.set_defaults(fn=cmd_skin)

    s = sp.add_parser("lc", help="LC resonance (give two of L, C, f)")
    s.add_argument("--l", type=num); s.add_argument("--c", type=num); s.add_argument("--f", type=num)
    s.set_defaults(fn=cmd_lc)

    s = sp.add_parser("radar", help="radar range equation (monostatic, coherent integration time)")
    s.add_argument("--pt", type=float, required=True, help="W"); s.add_argument("--g", type=float, required=True, help="dBi")
    s.add_argument("--f", type=num, required=True); s.add_argument("--rcs", type=float, required=True, help="m^2")
    s.add_argument("--r", type=num, required=True); s.add_argument("--nf", type=float, default=10.0)
    s.add_argument("--tint", type=float, required=True, help="coherent integration time s")
    s.add_argument("--loss", type=float, default=0.0); s.add_argument("--snr-min", type=float, default=13.0)
    s.set_defaults(fn=cmd_radar)

    s = sp.add_parser("fmcw", help="FMCW chirp parameters")
    s.add_argument("--f0", type=num, required=True); s.add_argument("--bw", type=num, required=True)
    s.add_argument("--tc", type=float, required=True, help="chirp time s"); s.add_argument("--fs", type=num, required=True)
    s.add_argument("--n", type=int, default=128); s.add_argument("--real-if", action="store_true")
    s.set_defaults(fn=cmd_fmcw)

    s = sp.add_parser("array", help="uniform linear array summary")
    s.add_argument("n", type=int); s.add_argument("d", type=float, help="spacing in wavelengths")
    s.add_argument("--steer", type=float, default=0.0); s.set_defaults(fn=cmd_array)

    s = sp.add_parser("lora", help="LoRa time on air / bit rate / sensitivity")
    s.add_argument("--sf", type=int, required=True); s.add_argument("--bw", type=num, default=125e3)
    s.add_argument("--pl", type=int, required=True, help="payload bytes"); s.add_argument("--cr", type=int, default=1)
    s.add_argument("--preamble", type=int, default=8); s.add_argument("--nf", type=float, default=6.0)
    s.add_argument("--chip", choices=["sx127x", "sx126x"], default="sx127x"); s.set_defaults(fn=cmd_lora)

    s = sp.add_parser("itm", help="ITM / Longley-Rice terrain loss (area mode, or --profile for point-to-point)")
    s.add_argument("--f", type=num, required=True); s.add_argument("--d", type=num)
    s.add_argument("--htx", type=float, default=2.0); s.add_argument("--hrx", type=float, default=2.0)
    s.add_argument("--dh", type=float, default=90.0, help="terrain irregularity delta_h [m] (area mode)")
    s.add_argument("--siting", type=int, default=0, choices=[0, 1, 2])
    s.add_argument("--profile", help="file of equally spaced elevations [m], TX first")
    s.add_argument("--spacing", type=float, default=100.0, help="profile spacing [m]")
    s.add_argument("--climate", type=int, default=1, help="1 equatorial (Singapore) .. 7; NTIA codes")
    s.add_argument("--n0", type=float, default=360.0, help="surface refractivity N_0 [N-units]")
    s.add_argument("--pol", type=int, default=1, choices=[0, 1], help="0 horizontal, 1 vertical")
    s.add_argument("--er", type=float, default=15.0); s.add_argument("--sigma", type=float, default=0.005)
    s.add_argument("--mdvar", type=int, default=12, help="12 = single-message, no location variability")
    s.add_argument("--time", type=float, default=50.0); s.add_argument("--location", type=float, default=50.0)
    s.add_argument("--situation", type=float, default=50.0); s.set_defaults(fn=cmd_itm)

    s = sp.add_parser("db", help="conversions: dbm2w | w2dbm | vswr | rl")
    s.add_argument("kind", choices=["dbm2w", "w2dbm", "vswr", "rl"]); s.add_argument("value", type=num)
    s.set_defaults(fn=cmd_db)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.fn(args)
    return 0
