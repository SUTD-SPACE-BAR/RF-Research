#!/usr/bin/env python3
"""
s5_tdr_lattice.py — lattice (bounce) diagrams with resistive and reactive terminations.

Used by: kb/03-transmission-lines-matching/time-domain-reflectometry.md, section
"Level 2b — lattice (bounce) diagrams" and its worked examples (task W5-S5, gap G-03-05).

Three independent solvers are compared for each case:
  (L) the lattice / bounce-diagram method (waves bookkept at each end; a reactive load is an ODE
      driven by the arriving wave: C dV/dt = (2 v_inc - V)/Z0),
  (F) a 1-D FDTD of the telegrapher equations (Courant number 0.5, half-cell end capacitances,
      semi-implicit terminations),
  (W) the frequency-domain ABCD solution, inverse-FFT'd (edge with finite rise time).

Sections
  §1  Resistive: Rs = 10 ohm, Z0 = 50 ohm, T = 1 ns, RL = 200 ohm and open; steady state V RL/(Rs+RL).
  §2  Capacitive load, matched source: v_r(t) = v1 (1 - 2 exp(-t/Z0C)); unmatched source (CMOS-like).
  §3  Inductive loads: L to ground (v_r = v1(2e^{-tZ0/L} - 1)); series L + Z0 (TDR bump area L/2Z0).
  §4  Digital/SI example: 3.3 V driver (Rs 15 ohm) -> 150 mm 50 ohm microstrip (JLC 2-layer, eeff 3.40)
      -> 5 pF input. Overshoot and ringing; series termination Rs = Z0 removes them.
  §5  TDR "ghosts": a 75 ohm, 0.5 m section inside a 50 ohm cable; lattice amplitudes of the first
      re-reflection vs the IFFT of S11 (what a NanoVNA low-pass TDR would show).

Run:  python3 tools/verify/s5_tdr_lattice.py     (about 10 s)
"""
import numpy as np

C0 = 299_792_458.0
checks = []


def check(name, ok, detail=""):
    checks.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}  {detail}")


def edge(t, V, tr):
    """step of height V with a raised-cosine 0-100 % edge of duration tr (tr = 0 -> ideal step)."""
    if tr == 0:
        return np.where(t >= 0, V, 0.0)
    x = np.clip(t / tr, 0, 1)
    return V * 0.5 * (1 - np.cos(np.pi * x))


# ---------------------------------------------------------------- (L) lattice solver
def lattice(V, Rs, Z0, T, load, t_end, dt=1e-12, tr=0.0):
    """Bounce-diagram bookkeeping on a time grid. load = ('R', RL) | ('C', C) | ('L', L) | ('RC', R, C) | ('LR', L, R)
    (L in series with R). Returns t, V_source_end, V_load."""
    n = int(round(t_end / dt)) + 1
    t = np.arange(n) * dt
    nT = int(round(T / dt))
    Gs = (Rs - Z0) / (Rs + Z0)
    vs = edge(t, V, tr) * Z0 / (Rs + Z0)          # wave launched by the source into the line
    a_src = np.zeros(n)        # forward wave leaving the source end
    b_ld = np.zeros(n)         # backward wave leaving the load end
    VL = np.zeros(n)
    state = 0.0                # capacitor voltage or inductor current
    for i in range(n):
        back_at_src = b_ld[i - nT] if i >= nT else 0.0
        a_src[i] = vs[i] + Gs * back_at_src
        vin = a_src[i - nT] if i >= nT else 0.0   # forward wave arriving at the load
        kind = load[0]
        if kind == "R":
            G = (load[1] - Z0) / (load[1] + Z0) if np.isfinite(load[1]) else 1.0
            b_ld[i] = G * vin
            VL[i] = vin + b_ld[i]
        elif kind == "C":
            C = load[1]
            # C dV/dt = (2 vin - V)/Z0 , exact exponential update over dt (vin held)
            tau = Z0 * C
            state = 2 * vin + (state - 2 * vin) * np.exp(-dt / tau) if i > 0 else 0.0
            VL[i] = state
            b_ld[i] = VL[i] - vin
        elif kind == "RC":     # R parallel C
            R, C = load[1], load[2]
            Rth = 1 / (1 / Z0 + 1 / R)
            Vth = 2 * vin * Rth / Z0
            tau = Rth * C
            state = Vth + (state - Vth) * np.exp(-dt / tau) if i > 0 else 0.0
            VL[i] = state
            b_ld[i] = VL[i] - vin
        elif kind == "L":      # L to ground: L dI/dt = V, V = 2 vin - Z0 I
            L = load[1]
            tau = L / Z0
            Iinf = 2 * vin / Z0
            # V = 2vin - Z0 I, dI/dt = (2vin - Z0 I)/L -> I -> 2vin/Z0
            state = Iinf + (state - Iinf) * np.exp(-dt / tau) if i > 0 else 0.0
            VL[i] = 2 * vin - Z0 * state
            b_ld[i] = VL[i] - vin
        elif kind == "LR":     # L in series with R to ground
            L, R = load[1], load[2]
            tau = L / (Z0 + R)
            Iinf = 2 * vin / (Z0 + R)
            state = Iinf + (state - Iinf) * np.exp(-dt / tau) if i > 0 else 0.0
            VL[i] = 2 * vin - Z0 * state
            b_ld[i] = VL[i] - vin
    back = np.concatenate([np.zeros(nT), b_ld[:-nT]])
    Vsrc = a_src + back
    return t, Vsrc, VL


# ---------------------------------------------------------------- (F) FDTD
def fdtd(V, Rs, Z0, T, load, t_end, N=400, courant=0.5, tr=0.0):
    v = 1.0                         # normalised: length = T * v
    ell = T * v
    Lp = Z0 / v
    Cp = 1 / (Z0 * v)
    dz = ell / N
    dt = courant * dz / v
    nsteps = int(t_end / dt) + 1
    Vn = np.zeros(N + 1)
    In = np.zeros(N)
    t_out = np.arange(nsteps) * dt
    v0 = np.zeros(nsteps)
    vN = np.zeros(nsteps)
    IL = 0.0
    Cl = load[1] if load[0] in ("C",) else (load[2] if load[0] == "RC" else 0.0)
    for n in range(nsteps):
        v0[n], vN[n] = Vn[0], Vn[N]
        In -= dt / (Lp * dz) * (Vn[1:] - Vn[:-1])
        Vn[1:N] -= dt / (Cp * dz) * (In[1:] - In[:-1])
        tn = (n + 0.5) * dt
        Vsrc = edge(np.array([tn]), V, tr)[0]
        c0 = Cp * dz / 2
        # c0 (V' - V)/dt = (Vs - (V'+V)/2)/Rs - I0
        Vn[0] = ((c0 / dt - 0.5 / Rs) * Vn[0] + Vsrc / Rs - In[0]) / (c0 / dt + 0.5 / Rs)
        cN = Cp * dz / 2 + Cl
        kind = load[0]
        if kind == "R":
            RL = load[1]
            if np.isfinite(RL):
                Vn[N] = ((cN / dt - 0.5 / RL) * Vn[N] + In[-1]) / (cN / dt + 0.5 / RL)
            else:
                Vn[N] = Vn[N] + dt / cN * In[-1]
        elif kind == "C":
            Vn[N] = Vn[N] + dt / cN * In[-1]
        elif kind == "RC":
            RL = load[1]
            Vn[N] = ((cN / dt - 0.5 / RL) * Vn[N] + In[-1]) / (cN / dt + 0.5 / RL)
        elif kind in ("L", "LR"):
            L = load[1]
            R = load[2] if kind == "LR" else 0.0
            # cN dV/dt = I_line - IL ; L dIL/dt = V - R IL   (trapezoidal, solved jointly)
            A = np.array([[cN / dt, 0.5], [-0.5, L / dt + 0.5 * R]])
            rhs = np.array([cN / dt * Vn[N] + In[-1] - 0.5 * IL, (L / dt - 0.5 * R) * IL + 0.5 * Vn[N]])
            Vn[N], IL = np.linalg.solve(A, rhs)
    return t_out, v0, vN


# ---------------------------------------------------------------- (W) frequency domain
def freq_domain(V, Rs, Z0, T, load, t_end, tr, dt=2e-12, pad=8):
    n = int(2 ** np.ceil(np.log2(pad * t_end / dt)))
    f = np.fft.rfftfreq(n, dt)
    w = 2 * np.pi * f
    s = 1j * w + 1e-30
    kind = load[0]
    if kind == "R":
        ZL = np.full_like(s, load[1]) if np.isfinite(load[1]) else np.full_like(s, 1e18)
    elif kind == "C":
        ZL = 1 / (s * load[1])
    elif kind == "RC":
        ZL = 1 / (1 / load[1] + s * load[2])
    elif kind == "L":
        ZL = s * load[1]
    else:
        ZL = s * load[1] + load[2]
    th = w * T
    A, B, Cc, D = np.cos(th), 1j * Z0 * np.sin(th), 1j * np.sin(th) / Z0, np.cos(th)
    HL = ZL / (A * ZL + B + Rs * (Cc * ZL + D))
    Zin = (A * ZL + B) / (Cc * ZL + D)
    H0 = Zin / (Zin + Rs)
    tt = np.arange(n) * dt
    x = edge(tt, V, tr)
    dx = np.diff(np.concatenate([[0.0], x]))          # derivative of the input (compact support)
    DX = np.fft.rfft(dx)
    vL = np.cumsum(np.fft.irfft(DX * HL, n))
    v0 = np.cumsum(np.fft.irfft(DX * H0, n))
    m = int(t_end / dt) + 1
    return tt[:m], v0[:m], vL[:m]


def compare(name, V, Rs, Z0, T, load, t_end, tr, tol=0.01):
    tl, v0l, vLl = lattice(V, Rs, Z0, T, load, t_end, dt=1e-12, tr=tr)
    tf, v0f, vLf = fdtd(V, Rs, Z0, T, load, t_end, N=800, tr=tr)
    tw, v0w, vLw = freq_domain(V, Rs, Z0, T, load, t_end, tr)
    grid = np.linspace(0.02 * t_end, 0.98 * t_end, 400)
    L = np.interp(grid, tl, vLl)
    F = np.interp(grid, tf, vLf)
    W = np.interp(grid, tw, vLw)
    eLF = np.max(np.abs(L - F)) / V
    eLW = np.max(np.abs(L - W)) / V
    check(f"{name}: lattice = FDTD = frequency-domain at the load (max error / V)", eLF < tol and eLW < tol,
          f"L-F {eLF:.1e}, L-W {eLW:.1e}")
    return tl, v0l, vLl


# ---------------------------------------------------------------- §1
def part1():
    print("§1 resistive terminations")
    V, Rs, Z0, T = 1.0, 10.0, 50.0, 1e-9
    tr = 0.1e-9
    for RL in [200.0, 1e9]:
        t, v0, vL = compare(f"Rs 10, RL {RL:g}", V, Rs, Z0, T, ("R", RL), 40e-9, tr)
        final = V * RL / (Rs + RL)
        check(f"  steady state V RL/(Rs+RL) = {final:.4f} V", abs(vL[-1] - final) < 2e-3, f"lattice {vL[-1]:.4f}")
    # explicit bounce table, ideal step, open load
    Gs = (Rs - Z0) / (Rs + Z0)
    v1 = Z0 / (Rs + Z0)
    levels = [v1 * 2 * sum(Gs ** j for j in range(m + 1)) for m in range(5)]
    t, v0, vL = lattice(V, Rs, Z0, T, ("R", 1e30), 12e-9, dt=1e-12, tr=0)
    sampled = [vL[int((2 * m + 1.5) * 1000)] for m in range(5)]
    print("     open load, ideal step: load levels after T, 3T, 5T, ...: " + ", ".join(f"{x:.4f}" for x in sampled)
          + f"  (Gs = {Gs:.4f}, v1 = {v1:.4f})")
    check("  open-load bounce levels = 2 v1 (1 + Gs + Gs^2 + ...)", np.allclose(sampled, levels, atol=1e-9))


# ---------------------------------------------------------------- §2
def part2():
    print("§2 capacitive loads")
    V, Z0, T, C = 1.0, 50.0, 1e-9, 2e-12
    t, v0, vL = lattice(V, Z0, Z0, T, ("C", C), 6e-9, dt=1e-13, tr=0)
    v1 = 0.5
    # reflected wave seen back at the (matched) source end: v1 + v1(1 - 2 exp(-(t-2T)/tau)) for t > 2T
    tau = Z0 * C
    tt = t[t > 2 * T + 1e-12]
    pred = v1 + v1 * (1 - 2 * np.exp(-(tt - 2 * T) / tau))
    err = np.max(np.abs(np.interp(tt, t, v0) - pred))
    check("matched source, C load: v_src = v1 + v1(1 - 2 e^{-(t-2T)/Z0C}) (TDR of a capacitor)", err < 1e-3, f"max err {err:.1e} V")
    compare("Rs 15, C 5 pF", 1.0, 15.0, 50.0, 1e-9, ("C", 5e-12), 30e-9, 0.2e-9)
    compare("Rs 50, R 1k || C 3 pF", 1.0, 50.0, 50.0, 1e-9, ("RC", 1e3, 3e-12), 20e-9, 0.2e-9)


# ---------------------------------------------------------------- §3
def part3():
    print("§3 inductive loads")
    V, Z0, T, L = 1.0, 50.0, 1e-9, 10e-9
    t, v0, vL = lattice(V, Z0, Z0, T, ("L", L), 6e-9, dt=1e-13, tr=0)
    tau = L / Z0
    tt = t[t > 2 * T + 1e-12]
    pred = 0.5 + 0.5 * (2 * np.exp(-(tt - 2 * T) / tau) - 1)
    err = np.max(np.abs(np.interp(tt, t, v0) - pred))
    check("matched source, L to ground: v_src = v1 + v1(2 e^{-(t-2T)Z0/L} - 1)", err < 1e-3, f"max err {err:.1e} V")
    compare("Rs 50, L 10 nH to ground", 1.0, 50.0, 50.0, 1e-9, ("L", 10e-9), 20e-9, 0.2e-9)
    # series L + Z0: bump area L/(2 Z0) in rho(t) = (v_src - v1)/v1
    Ls = 3e-9
    t, v0, vL = lattice(1.0, 50.0, 50.0, 1e-9, ("LR", Ls, 50.0), 6e-9, dt=1e-13, tr=0)
    rho = (v0 - 0.5) / 0.5
    area = np.trapezoid(rho, t)
    check("series L + matched R: TDR bump area = L/(2 Z0) (03 TDR area rule)", abs(area / (Ls / 100) - 1) < 3e-3,     # 0.2 % = one-sample lag of the exponential update
          f"{area*1e12:.2f} ps vs {Ls/100*1e12:.2f} ps")
    compare("Rs 25, 3 nH + 50 ohm", 1.0, 25.0, 50.0, 1e-9, ("LR", 3e-9, 50.0), 20e-9, 0.2e-9)


# ---------------------------------------------------------------- §4
def part4():
    print("§4 digital line: 3.3 V driver -> 150 mm 50 ohm microstrip -> 5 pF")
    eeff = 3.40                      # JLC 2-layer 50 ohm microstrip, openEMS/H-J (16/openems-workflow)
    T = 0.150 * np.sqrt(eeff) / C0
    V = 3.3
    out = {}
    for Rs, lab in [(15.0, "unterminated (Rs 15)"), (50.0, "series-terminated (Rs = Z0)")]:
        t, v0, vL = lattice(V, Rs, 50.0, T, ("C", 5e-12), 40e-9, dt=1e-12, tr=0.5e-9)
        pk = vL.max()
        # settling: last time |vL - V| > 5 %
        bad = np.where(np.abs(vL - V) > 0.05 * V)[0]
        ts = t[bad[-1]] if len(bad) else 0
        print(f"     {lab}: T = {T*1e9:.3f} ns, peak {pk:.2f} V ({(pk/V-1)*100:+.0f} %), settles to 5 % at {ts*1e9:.1f} ns;"
              f" source-end plateau ~{v0[int(1.5*T/1e-12)]:.2f} V")
        out[lab] = (pk, ts)
    check("unterminated line rings with > 25 % overshoot; series termination keeps overshoot < 5 %",
          out["unterminated (Rs 15)"][0] > 1.25 * V and out["series-terminated (Rs = Z0)"][0] < 1.05 * V,
          f"{out['unterminated (Rs 15)'][0]:.2f} V vs {out['series-terminated (Rs = Z0)'][0]:.2f} V")
    compare("SI case Rs 15 / 5 pF / tr 0.5 ns", V, 15.0, 50.0, T, ("C", 5e-12), 30e-9, 0.5e-9)
    return T, out


# ---------------------------------------------------------------- §5
def part5():
    print("§5 TDR ghosts: 75 ohm, 0.5 m section inside 50 ohm cable (VF 0.66)")
    Z0, Z2 = 50.0, 75.0
    vf = 0.66
    T1 = 1.0 / (vf * C0)          # 1 m of 50 ohm before the section
    T2 = 0.5 / (vf * C0)
    r = (Z2 - Z0) / (Z2 + Z0)
    # step response rho(t): +r at 2T1; at 2(T1+T2): + (1-r^2)(-r); ghost at 2(T1+2T2): (1-r^2)(-r)(r)(-r)... = +(1-r^2) r^3? sign:
    # wave inside section reflects at exit with -r, returns, at entry it reflects back with -r (seen from inside: (Z0-Z2)/(Z0+Z2) = -r)
    first = r
    second = (1 - r ** 2) * (-r)
    ghost = (1 - r ** 2) * (-r) * (-r) * (-r)
    print(f"     lattice: steps +{first:.4f} at 2T1, {second:+.4f} at 2(T1+T2), ghost {ghost:+.5f} at 2(T1+2T2);"
          f" final rho {first+second+ghost:+.5f} (-> 0 as the series sums)")
    # IFFT of S11 of the cascade (ideal lines, matched far end)
    fmax, N = 6e9, 6000
    f = np.linspace(0, fmax, N + 1)
    w = 2 * np.pi * f

    def abcd(Z, T):
        th = w * T
        return np.array([[np.cos(th), 1j * Z * np.sin(th)], [1j * np.sin(th) / Z, np.cos(th)]])

    M1, M2 = abcd(Z0, T1), abcd(Z2, T2)
    M = np.einsum("ijf,jkf->ikf", M1, M2)
    ZL = Z0
    Zin = (M[0, 0] * ZL + M[0, 1]) / (M[1, 0] * ZL + M[1, 1])
    S11 = (Zin - Z0) / (Zin + Z0)
    win = np.kaiser(2 * N + 1, 6)[N:]          # "normal" window
    spec = S11 * win
    nfft = 2 ** 16
    h = np.fft.irfft(spec, nfft) * (nfft / (2 * N)) * 1.0
    df = f[1]
    dt = 1 / (nfft * df)
    tt = np.arange(nfft) * dt
    stepr = np.cumsum(h) / (nfft / (2 * N)) * 1.0
    # normalise so the first plateau equals the measured first step (window scaling): use DC gain of the window ~ 1
    def plateau(t0, t1):
        m = (tt > t0) & (tt < t1)
        return np.mean(stepr[m])
    p1 = plateau(2 * T1 + 0.3e-9, 2 * (T1 + T2) - 0.3e-9)
    p2 = plateau(2 * (T1 + T2) + 0.3e-9, 2 * (T1 + 2 * T2) - 0.3e-9)
    p3 = plateau(2 * (T1 + 2 * T2) + 0.3e-9, 2 * (T1 + 3 * T2) - 0.3e-9)
    print(f"     IFFT (6 GHz, normal window) plateaux: {p1:+.4f}, {p2:+.5f}, {p3:+.5f}")
    check("TDR plateaux = lattice partial sums (r, r + (1-r^2)(-r), + ghost)",
          abs(p1 - first) < 2e-3 and abs(p2 - (first + second)) < 2e-3 and abs(p3 - (first + second + ghost)) < 2e-3,
          f"lattice {first:+.4f}, {first+second:+.5f}, {first+second+ghost:+.5f}")
    return first, second, ghost


if __name__ == "__main__":
    part1()
    part2()
    part3()
    part4()
    part5()
    print(f"\n{sum(checks)}/{len(checks)} checks passed")
