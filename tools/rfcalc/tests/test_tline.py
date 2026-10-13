"""Expected values: kb/03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md
(Examples 1, 2, 4), coax-and-cables.md (Example 3), and the FD field-solver numbers recorded there."""
import math

import pytest

from rfcalc import tline as t


def test_example2_pozar_synthesis():
    # 50 ohm, er 4.5, h 1.51 mm: Pozar closed form 2.84 mm; H-J root-find with 35 um: 2.80 mm
    assert t.microstrip_width_pozar(50, 1.51e-3, 4.5) * 1e3 == pytest.approx(2.84, abs=0.005)
    assert t.microstrip_width(50, 1.51e-3, 4.5, 35e-6) * 1e3 == pytest.approx(2.80, abs=0.005)


def test_hj_vs_wheeler_vs_simple():
    z_hj, _ = t.microstrip_hj(2.8e-3, 1.51e-3, 4.5)
    assert t.microstrip_wheeler77(2.8e-3, 1.51e-3, 4.5) == pytest.approx(z_hj, rel=0.01)
    assert t.microstrip_simple(2.8e-3, 1.51e-3, 4.5)[0] == pytest.approx(z_hj, rel=0.01)


def test_hj_vs_fd_solver_msl():
    # own 2-D FD solver (tools/verify/tline_fd2d.py, Richardson-extrapolated) for W 2.80, h 1.51, er 4.5, t 0:
    # Z0 = 50.38 ohm, eps_eff = 3.386 (run for kb/16-simulation-tools/openems-workflow.md); openEMS 50.31 ohm
    z, ee = t.microstrip_hj(2.8e-3, 1.51e-3, 4.5, 0.0)
    assert z == pytest.approx(50.38, rel=0.003)
    assert ee == pytest.approx(3.386, rel=0.003)


def test_example4_quarter_wave_915():
    # 915 MHz on 1.6 mm FR-4 50 ohm microstrip, eps_eff 3.36: lambda_g/4 = 44.7 mm
    assert t.quarter_wave_length(915e6, 3.36) * 1e3 == pytest.approx(44.7, abs=0.05)


def test_jlc7628_matching_page_example4():
    # JLC04161H-7628: 0.36 mm on 0.2104 mm, er 4.4 -> ~51.2 ohm, eps_eff 3.15 (matching page Example 4)
    z, ee = t.microstrip_hj(0.36e-3, 0.2104e-3, 4.4, 35e-6)
    assert z == pytest.approx(51.2, abs=0.6)
    assert ee == pytest.approx(3.15, abs=0.05)


def test_dispersion_small_on_thin_board():
    z0, ee0 = t.microstrip_hj(0.36e-3, 0.2104e-3, 4.4)
    zf, eef = t.microstrip_kj(0.36e-3, 0.2104e-3, 4.4, 2.45e9)
    assert abs(eef / ee0 - 1) < 1e-3          # < 0.1 % at 2.45 GHz on a 0.21 mm dielectric


def test_dispersion_1p6mm_board():
    _, ee0 = t.microstrip_hj(2.8e-3, 1.51e-3, 4.5)
    _, eef = t.microstrip_kj(2.8e-3, 1.51e-3, 4.5, 2.45e9)
    assert 0.005 < eef / ee0 - 1 < 0.025       # ~1.5 % on 1.6 mm boards


def test_cohn_stripline_limits():
    # wide strip -> parallel-plate limit Z ~ eta0 b / (2 W sqrt(er)) (two plates in parallel), check ordering
    z_narrow = t.stripline_cohn(0.3e-3, 1.0e-3, 4.4)
    z_wide = t.stripline_cohn(1.0e-3, 1.0e-3, 4.4)
    assert z_narrow > z_wide
    # Wheeler-78 with thin strip approaches Cohn
    assert t.stripline_wheeler78(0.3e-3, 1.0e-3, 1e-7, 4.4) == pytest.approx(z_narrow, rel=0.01)


def test_cpwg_vs_fd_zero_thickness():
    # own FD solver (tools/verify/tline_cpwg.py fd_cpwg, t = 0, Richardson-extrapolated; run 2026-09-27 by W3-C2):
    #   W 1.01 / S 0.20 / h 1.51 mm, er 4.5  -> 53.25 ohm (the page's 50 ohm includes 35 um copper)
    #   W 0.36 / S 0.30 / h 0.2104 mm, er 4.4 -> 52.07 ohm (S/h = 1.4: formula near its validity edge)
    assert t.cpwg(1.01e-3, 0.2e-3, 1.51e-3, 4.5)[0] == pytest.approx(53.25, rel=0.005)
    assert t.cpwg(0.36e-3, 0.3e-3, 0.2104e-3, 4.4)[0] == pytest.approx(52.07, rel=0.025)


def test_cpwg_large_gap_is_not_microstrip():
    # known limitation (planar-lines page): the conformal-mapping CPWG does NOT tend to microstrip for
    # S >> h (the FD solver does); at S = 13 h it is ~10 % high -> use microstrip formulas there
    z_cp, _ = t.cpwg(2.8e-3, 20e-3, 1.51e-3, 4.5)
    z_ms, _ = t.microstrip_hj(2.8e-3, 1.51e-3, 4.5)
    assert z_cp > 1.05 * z_ms


def test_cpwg_synthesis_roundtrip():
    w = t.cpwg_width(50.0, 0.2e-3, 1.51e-3, 4.5)
    assert t.cpwg(w, 0.2e-3, 1.51e-3, 4.5)[0] == pytest.approx(50.0, abs=1e-6)


def test_coax_lmr400():
    # coax page Example 3: d 2.74, D 7.24, VF 0.85 -> 49.6 ohm
    assert t.coax_z0(2.74e-3, 7.24e-3, 1 / 0.85 ** 2) == pytest.approx(49.6, abs=0.15)


def test_coax_optimum_ratios():
    # min conductor loss at D/d = 3.591 in air -> 76.7 ohm
    assert t.coax_z0(1.0, 3.591, 1.0) == pytest.approx(76.7, abs=0.1)


def test_lc_per_m():
    L, C = t.lc_per_m(50.0, 1.0)
    assert math.sqrt(L / C) == pytest.approx(50.0)
    assert 1 / math.sqrt(L * C) == pytest.approx(299_792_458.0)
