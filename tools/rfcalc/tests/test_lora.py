"""Expected values: kb/15-lora-ism-radios/lora-phy-css-math.md (Examples 1-4) and
kb/07-noise-linearity/sensitivity-and-mds.md (Example 1)."""
import pytest

from rfcalc import lora


def test_example1_sf9():
    assert lora.n_symbols(32, 9, 1, 8, bw_hz=125e3) == pytest.approx(60.25)
    assert lora.time_on_air(32, 9, 125e3) * 1e3 == pytest.approx(246.8, abs=0.05)


def test_example1_sf7():
    assert lora.time_on_air(32, 7, 125e3) * 1e3 == pytest.approx(71.9, abs=0.05)
    assert lora.time_on_air(32, 7, 500e3) * 1e3 == pytest.approx(18.0, abs=0.05)


def test_example3_ldro_sf12():
    assert lora.ldro_auto(12, 125e3)
    assert not lora.ldro_auto(10, 125e3)
    assert lora.time_on_air(32, 12, 125e3) * 1e3 == pytest.approx(1810, abs=1)
    # payload symbols 43 (n_symbols minus preamble 8 and 4.25)
    assert lora.n_symbols(32, 12, 1, 8, bw_hz=125e3) - 12.25 == pytest.approx(43)


def test_example4_lorawan_uplink():
    assert lora.time_on_air(13, 12, 125e3) * 1e3 == pytest.approx(1155, abs=1)


def test_sx126x_equals_sx127x_for_sf7_to_12():
    for sf in range(7, 13):
        for pl in (1, 13, 32, 64, 255):
            for cr in (1, 4):
                a = lora.time_on_air(pl, sf, 125e3, cr, chip="sx127x")
                b = lora.time_on_air(pl, sf, 125e3, cr, chip="sx126x")
                assert a == pytest.approx(b)


def test_sf5_sf6_sx126x_longer_header():
    # SX126x SF5/6 (datasheet rev 1.2 sec. 6.1.4): Npre + 6.25 + 8 + ceil(max(8PL+16CRC-4SF+20H,0)/(4SF))(CR+4)
    # PL = 10, SF5, CRC, explicit: ceil((80 + 16 - 20 + 20)/20) = ceil(4.8) = 5 blocks x 5 = 25 symbols
    assert lora.n_symbols(10, 5, 1, 8, chip="sx126x") == pytest.approx(8 + 6.25 + 8 + 25)


def test_bitrates_and_gain():
    assert lora.bitrate(7, 125e3, 1) == pytest.approx(5469, abs=1)
    assert lora.bitrate(12, 125e3, 1) == pytest.approx(293, abs=0.5)
    assert lora.processing_gain_db(12) == pytest.approx(36.1, abs=0.05)


def test_sensitivity_table():
    # sensitivity page Example 1: NF 6 dB, BW 125 kHz
    for sf, s in ((7, -124.5), (9, -129.5), (10, -132.0), (12, -137.0)):
        assert lora.sensitivity_dbm(sf, 125e3, 6.0) == pytest.approx(s, abs=0.05)


def test_packet_rate():
    # SF9/125 32 B back-to-back: 4.05 frames/s
    assert lora.max_packet_rate_hz(32, 9, 125e3) == pytest.approx(4.05, abs=0.01)
