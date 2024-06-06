import pytest
import cryodecoder

VALID_CRYOEGG_DATA = b'\xA0\x0F\x03\x04\xF3\x3F\x45\x59\xAC\x0F\x00'


def test_cryoeggdata_unique():

    packet = cryodecoder.CryoeggPacket(VALID_CRYOEGG_DATA)
    data = cryodecoder.CryoeggData(packet)

    assert packet.temperature_pt1000 == 1027

def test_cryoeggdata_keller_temperature():

    packet = cryodecoder.CryoeggPacket(VALID_CRYOEGG_DATA)
    data = cryodecoder.CryoeggData(packet)

    # Check we're within 50mC
    assert abs(data.temperature - 20.20) < 0.05 

def test_cryoeggdata_keller_pressure():

    packet = cryodecoder.CryoeggPacket(VALID_CRYOEGG_DATA)
    data = cryodecoder.CryoeggData(packet)

    assert data.pressure_keller_max == 100. # default value
    assert data.pressure_keller_min == 0

    assert abs(data.pressure - 0.960) < 0.001 # correct to 1mBar? 