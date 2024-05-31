import pytest
import cryodecoder

def test_loadpacket():

    dummy_data = b'\xA0\x0F\x03\x04\xF3\x3F\x45\x59\xAC\x0F\x00'

    packet = cryodecoder.CryoeggPacket(dummy_data)

    assert packet.conductivity == int.from_bytes(b'\xA0\x0F', byteorder="little") / 1000
    assert packet.temperature_pt1000 == int.from_bytes(b'\x03\x04', byteorder="little")
    assert packet.pressure == int.from_bytes(b'\xF3\x3F', byteorder="little")
    assert packet.temperature == int.from_bytes(b'\x45\x59', byteorder="little")
    assert packet.battery_voltage == int.from_bytes(b'\xAC\x0F', byteorder="little") /1000
    assert packet.sequence_number == int.from_bytes(b'\x00', byteorder="little")

    assert packet.raw == dummy_data
    assert len(packet) == len(dummy_data)