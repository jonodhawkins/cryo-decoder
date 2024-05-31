import pytest
import cryodecoder

def test_mbuspacket_dummy():

    dummy_data = b'\x44\x24\x48\x02\x00\x24\xCE\x01\x07\xAA\xAA\x0F\x03\x04\xF2\x3F\xF2\x56\x8C\x0F\x19\x5A'

    # \x44
    # \x24\x48
    # \x02\x00\x24\xCE
    # \x01
    # \x07
    # \xAA
    # \xAA\x0F
    # \x03\x04
    # \xF2\x3F
    # \xF2\x56
    # \x8C\x0F
    # \x19
    # \x5A

    packet = cryodecoder.MBusPacket(dummy_data)
    assert packet.c_field == 0x44
    assert packet.manufacturer_id == 0x4824
    assert packet.user_id == 0xCE240002
    assert packet.version == 0x01
    assert packet.dev == 0x07
    assert packet.control_field == 0xAA
    assert packet.rssi == 0x5A
    assert packet.payload == bytearray(b'\xAA\x0F\x03\x04\xF2\x3F\xF2\x56\x8C\x0F\x19')