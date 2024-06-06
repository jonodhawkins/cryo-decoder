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

def test_cryoeggdata_sequence_number():

    packet = cryodecoder.CryoeggPacket(VALID_CRYOEGG_DATA)
    data = cryodecoder.CryoeggData(packet)

    assert data.sequence_number == 0

def test_cryoeggdata_battery_voltage():

    packet = cryodecoder.CryoeggPacket(VALID_CRYOEGG_DATA)
    data = cryodecoder.CryoeggData(packet)

    assert data.battery_voltage == int.from_bytes(b'\xAC\x0F', byteorder="little") / 1000

def test_cryoeggdata_conductivity_calibration_default():

    packet = cryodecoder.CryoeggPacket(VALID_CRYOEGG_DATA)
    data = cryodecoder.CryoeggData(packet)

    assert data.conductivity == float(int.from_bytes(b'\xA0\x0F', byteorder="little")) / 1000