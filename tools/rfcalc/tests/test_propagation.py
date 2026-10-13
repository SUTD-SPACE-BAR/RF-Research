"""Expected values: kb/09-propagation-link-budget/fresnel-zones-los-radio-horizon.md (Worked examples 1-4)."""
import pytest

from rfcalc import propagation as p


def test_fresnel_midpath_30km():
    assert float(p.fresnel_radius(433.125e6, 15e3, 15e3)) == pytest.approx(72.0, abs=0.5)


def test_fresnel_near_station():
    assert float(p.fresnel_radius(433.125e6, 100.0, 30e3 - 100.0)) == pytest.approx(8.3, abs=0.05)
    assert float(p.fresnel_radius(433.125e6, 10.0, 30e3 - 10.0)) == pytest.approx(2.6, abs=0.05)


def test_fresnel_exact_vs_paraxial():
    r_par = float(p.fresnel_radius(915e6, 2.5e3, 2.5e3))
    r_ex = p.fresnel_radius_exact(915e6, 2.5e3, 2.5e3)
    assert r_ex == pytest.approx(r_par, rel=1e-4)


def test_itu_form_matches():
    assert float(p.fresnel_radius_itu(915.0, 2.5, 2.5)) == pytest.approx(float(p.fresnel_radius(915e6, 2.5e3, 2.5e3)),
                                                                        rel=6e-3)   # 550 ~ sqrt(c*1e-3) = 547.5


def test_example3_ground_level_heights():
    # 5 km, 915 MHz: bulge 0.37 m + 0.6 R1 12.1 m ~ 12.5 m
    b = float(p.earth_bulge(2.5e3, 2.5e3))
    r1 = float(p.fresnel_radius(915e6, 2.5e3, 2.5e3))
    assert b == pytest.approx(0.37, abs=0.01)
    assert 0.6 * r1 == pytest.approx(12.1, abs=0.1)


def test_horizon_constants():
    assert float(p.radio_horizon_m(1.0, k=1.0)) / 1e3 == pytest.approx(3.57, abs=0.01)
    assert float(p.radio_horizon_m(1.0, k=4 / 3)) / 1e3 == pytest.approx(4.12, abs=0.01)


@pytest.mark.parametrize("hg,D,alt", [(2.0, 10e3, 1.0), (2.0, 20e3, 12.0), (2.0, 30e3, 34.0), (2.0, 50e3, 115.0),
                                      (5.0, 30e3, 25.0), (20.0, 50e3, 59.0)])
def test_los_altitude_table(hg, D, alt):
    assert p.los_altitude_m(D, hg) == pytest.approx(alt, abs=1.0)


@pytest.mark.parametrize("hg,D,f,alt", [(2.0, 30e3, 433.125e6, 982.0), (2.0, 30e3, 915e6, 494.0),
                                        (20.0, 30e3, 433.125e6, 138.0)])
def test_fresnel_clear_altitude_table(hg, D, f, alt):
    assert p.fresnel_clear_altitude_m(D, hg, f) == pytest.approx(alt, abs=3.0)


def test_elevation_examples():
    el, slant = p.elevation_deg(30e3, 3e3)
    assert el == pytest.approx(5.6, abs=0.1)
    assert slant / 1e3 == pytest.approx(30.15, abs=0.05)
    assert p.elevation_deg(30e3, 10e3)[0] == pytest.approx(18.3, abs=0.1)
    assert p.elevation_deg(30e3, 1e3)[0] == pytest.approx(1.8, abs=0.1)
