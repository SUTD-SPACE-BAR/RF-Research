"""Expected values: kb/12-phased-arrays/array-factor-linear-arrays.md (Examples 1, 2, 5) and
kb/00-math-foundations/decibels-and-log-units.md (Example 4)."""
import math

import numpy as np
import pytest

from rfcalc import arrays as a


def test_example1_hpbw_and_nulls():
    assert a.hpbw_deg(8, 0.5) == pytest.approx(12.7, abs=0.05)
    assert a.hpbw_deg(8, 0.5, 30) == pytest.approx(14.7, abs=0.05)
    assert a.hpbw_deg(8, 0.5, 45) == pytest.approx(18.0, abs=0.1)   # page rounds 17.95 to 18.0
    assert a.first_null_deg(8, 0.5) == pytest.approx(14.5, abs=0.05)


def test_example1_exact_hpbw_from_af():
    th = np.linspace(-30, 30, 60001)
    af = np.abs(a.array_factor(th, 8, 0.5))
    above = th[af >= 1 / math.sqrt(2)]
    assert above.max() - above.min() == pytest.approx(12.80, abs=0.02)


def test_first_sidelobe():
    th = np.linspace(15, 40, 20001)
    sl = a.array_factor_db(th, 8, 0.5).max()
    assert sl == pytest.approx(-12.8, abs=0.05)


def test_directivity_isotropic():
    assert a.directivity_ula(8, 0.5) == pytest.approx(8.0, rel=1e-9)
    assert a.directivity_ula(8, 0.5, 30.0) == pytest.approx(8.0, rel=1e-9)


def test_example5_broadside_endfire():
    assert a.directivity_ula(10, 0.25) == pytest.approx(5.17, abs=0.01)
    assert a.directivity_ula(10, 0.25, 90.0) == pytest.approx(10.0, abs=0.01)


def test_example2_steering_phase():
    assert a.steering_phase_deg(0.5, 30) == pytest.approx(90.0)
    assert a.steering_phase_deg(15 / 28.3, 30) == pytest.approx(95.4, abs=0.1)


def test_grating_lobe_limit():
    assert a.max_spacing_no_grating(0.0) == pytest.approx(1.0)
    assert a.max_spacing_no_grating(30.0) == pytest.approx(2 / 3)


def test_array_gain():
    assert a.array_gain_db(4) == pytest.approx(6.02, abs=0.01)
    assert a.array_gain_db(5) == pytest.approx(6.99, abs=0.01)
