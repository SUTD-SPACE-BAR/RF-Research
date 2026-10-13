"""LC resonance, Q, bandwidth, loaded Q and resonator insertion loss.

Ported from tools/verify/circuits_resonance_q.py (W1-A2). Page: kb/01-circuit-theory/resonance-and-q.md.
"""
import math


def f_res(l_h, c_f):
    """Resonant frequency 1/(2 pi sqrt(LC)) [Hz]."""
    return 1.0 / (2 * math.pi * math.sqrt(l_h * c_f))


def c_for_f(f_hz, l_h):
    return 1.0 / ((2 * math.pi * f_hz) ** 2 * l_h)


def l_for_f(f_hz, c_f):
    return 1.0 / ((2 * math.pi * f_hz) ** 2 * c_f)


def char_reactance(l_h, c_f):
    """X0 = sqrt(L/C) = omega0 L [ohm]."""
    return math.sqrt(l_h / c_f)


def q_series(l_h, c_f, r_ohm):
    """Q of a series RLC: X0 / R."""
    return char_reactance(l_h, c_f) / r_ohm


def q_parallel(l_h, c_f, r_ohm):
    """Q of a parallel RLC: R / X0."""
    return r_ohm / char_reactance(l_h, c_f)


def bandwidth_3db(f0_hz, q):
    """-3 dB bandwidth of a single resonator: f0/Q."""
    return f0_hz / q


def esr_from_q(x_ohm, q):
    """Series loss resistance of a reactive part with quality factor Q at reactance X."""
    return abs(x_ohm) / q


def q_combined(*qs):
    """1/Q = sum 1/Q_i (e.g. inductor and capacitor Q, or unloaded and external Q)."""
    return 1.0 / sum(1.0 / q for q in qs)


def loaded_q(q_unloaded, q_external):
    return q_combined(q_unloaded, q_external)


def resonator_il_db(q_loaded, q_unloaded):
    """Insertion loss at resonance of a doubly terminated single resonator: -20 log10(1 - QL/Qu) (positive)."""
    return -20 * math.log10(1 - q_loaded / q_unloaded)


def group_delay_s(q_loaded, f0_hz):
    """Group delay at centre of a single resonator: 2 QL / omega0."""
    return 2 * q_loaded / (2 * math.pi * f0_hz)


def srf_hz(l_h, c_par_f):
    """Self-resonant frequency of an inductor with parallel (parasitic) capacitance (or a capacitor
    with series ESL): 1/(2 pi sqrt(LC))."""
    return f_res(l_h, c_par_f)
