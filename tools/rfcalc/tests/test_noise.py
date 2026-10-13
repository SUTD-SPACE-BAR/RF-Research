"""Expected values: kb/07-noise-linearity/noise-figure-and-friis.md (Examples 1-4),
receiver-cascade-analysis.md (Examples A-D), sensitivity-and-mds.md (Examples 1, 4, 5),
decibels-and-log-units.md (Example 7)."""
import pytest

from rfcalc import noise as n
from rfcalc.noise import Stage


def test_friis_three_stage():
    # LNA 1 dB/15 dB, mixer 6 dB/-6 dB, IF amp 4 dB/20 dB -> 1.89 dB (1.885)
    assert n.friis_nf_db([1, 6, 4], [15, -6, 20]) == pytest.approx(1.885, abs=0.005)


def test_lna_placement_lesson():
    lna = Stage("LNA", 20, 0.8)
    mod = Stage("module", 0, 6.0)
    cable = Stage("cable", -3.0)
    assert n.cascade_nf_db([cable, lna, mod]) == pytest.approx(3.91, abs=0.01)
    assert n.cascade_nf_db([lna, cable, mod]) == pytest.approx(1.04, abs=0.01)
    assert n.cascade_nf_db([cable, mod]) == pytest.approx(9.0, abs=0.01)


def _a2():
    return [Stage("SAW", -1.5), Stage("LNA", 18, 0.7, iip3=8, ip1db=-5), Stage("coax", -2.6),
            Stage("module", 0.0, 6.0, iip3=-5, ip1db=-15)]


def test_cascade_example_a2():
    res = n.cascade(_a2())[-1]
    assert res["NF_cum_dB"] == pytest.approx(2.55, abs=0.01)
    assert res["Te_cum_K"] == pytest.approx(232, abs=1)
    assert res["IIP3_cum_dBm"] == pytest.approx(-18.9, abs=0.05)
    assert res["IP1dB_cum_dBm"] == pytest.approx(-28.9, abs=0.05)
    floor = n.system_noise_dbm(125e3, res["NF_cum_dB"], 290.0)
    assert floor == pytest.approx(-120.5, abs=0.05)
    assert floor - 20 == pytest.approx(-140.5, abs=0.05)
    assert n.sfdr_db(res["IIP3_cum_dBm"], floor) == pytest.approx(67.7, abs=0.1)


def test_noise_shares_a2():
    fr, _ = n.noise_contributions(_a2())
    assert [round(100 * x, 1) for x in fr] == pytest.approx([51.6, 30.9, 2.3, 15.2], abs=0.1)


def test_cascade_example_a1():
    res = n.cascade([Stage("coax", -2.6), Stage("module", 0, 6.0, iip3=-5)])[-1]
    assert res["NF_cum_dB"] == pytest.approx(8.60, abs=0.01)
    assert res["Te_cum_K"] == pytest.approx(1811, abs=2)


def test_gnss_chain_example_c():
    st = [Stage("patch", -0.3), Stage("LNA1", 17, 0.8, iip3=-5), Stage("SAW", -1.2),
          Stage("LNA2", 12, 1.5, iip3=0), Stage("RG174", -4.2), Stage("rx", 20, 3.0, iip3=-20)]
    res = n.cascade(st)
    assert res[-1]["NF_cum_dB"] == pytest.approx(1.19, abs=0.01)
    assert res[-1]["G_cum_dB"] == pytest.approx(43.3, abs=0.05)
    assert res[-1]["Te_cum_K"] == pytest.approx(91, abs=1)
    assert res[-1]["IIP3_cum_dBm"] == pytest.approx(-43.3, abs=0.1)
    # C/N0 at Ta = 100 K for -128.5 dBm: 47.3 dB-Hz
    assert n.cn0_dbhz(-128.5, res[-1]["NF_cum_dB"], 100.0) == pytest.approx(47.3, abs=0.05)


def test_cn0_simple():
    # decibels page Example 7: -130 dBm, NF 2 dB (T0 source) -> 42.0 dB-Hz
    assert n.cn0_dbhz(-130.0, 2.0, 290.0) == pytest.approx(41.975, abs=0.005)   # page: 42.0 (rounded)


def test_lora_sensitivities():
    # sensitivity page Example 1 (NF 6 dB): SF7 -124.5, SF12 -137.0 dBm at 125 kHz
    assert n.sensitivity_dbm(125e3, 6.0, -7.5) == pytest.approx(-124.5, abs=0.05)
    assert n.sensitivity_dbm(125e3, 6.0, -20.0) == pytest.approx(-137.0, abs=0.05)


def test_mds_sdr():
    # sensitivity page Example 5: NF 6 dB, RBW 1 kHz -> -138 dBm; 125 kHz -> -117 dBm
    assert n.mds_dbm(1e3, 6.0) == pytest.approx(-138.0, abs=0.05)
    assert n.mds_dbm(125e3, 6.0) == pytest.approx(-117.0, abs=0.05)


def test_te_nf_roundtrip_and_lossy_line():
    assert float(n.nf_to_te(3.0103)) == pytest.approx(290.0, abs=0.01)
    assert float(n.te_to_nf(290.0)) == pytest.approx(3.0103, abs=1e-4)
    assert float(n.lossy_line_nf(3.0)) == pytest.approx(3.0)
    # attenuator at 290 K keeps a 290 K source at 290 K
    assert float(n.antenna_temp_through_loss(290.0, 6.0)) == pytest.approx(290.0)


def test_p1db_iip3_gap():
    assert float(n.P1DB_IIP3_GAP_CUBIC_DB) == pytest.approx(9.64, abs=0.01)


def test_two_tone():
    # pure cubic device: IM3 at Pin = IIP3 - 20 dB is 40 dB below the fundamentals
    assert n.iip3_from_two_tone(-30.0, 40.0) == pytest.approx(-10.0)
    assert n.im3_level_dbm(-30.0, -10.0) == pytest.approx(-70.0)
