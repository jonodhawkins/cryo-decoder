import pytest
import cryodecoder

##############################################################################
# Define valid data types
##############################################################################
VALID_CRYOEGG_DATA = b'\xA0\x0F\x03\x04\xF3\x3F\x45\x59\xAC\x0F\x00'
VALID_MBUSPACKET_DATA = b'\x44\x24\x48\x02\x00\x24\xCE\x01\x07\xAA\xAA\x0F\x03\x04\xF2\x3F\xF2\x56\x8C\x0F\x19\x5A'
VALID_MBUSPACKET_DATA_CONSTRUCTED = \
    b'\x44\x24\x48\x02\x00\x24\xCE\x01\x07\xAA' + VALID_CRYOEGG_DATA + b'\x5A'
VALID_CRYORECEIVER_DATA = b'\x01\x25\x4C\x27\xE0\x2E'

##############################################################################
# Test CryoeggPacket
##############################################################################
def test_cryoeggpacket_dummy():

    packet = cryodecoder.CryoeggPacket(VALID_CRYOEGG_DATA)

    assert packet.conductivity == int.from_bytes(b'\xA0\x0F', byteorder="little")
    assert packet.temperature_pt1000 == int.from_bytes(b'\x03\x04', byteorder="little")
    assert packet.pressure == int.from_bytes(b'\xF3\x3F', byteorder="little")
    assert packet.temperature == int.from_bytes(b'\x45\x59', byteorder="little")
    assert packet.battery_voltage == int.from_bytes(b'\xAC\x0F', byteorder="little")
    assert packet.sequence_number == int.from_bytes(b'\x00', byteorder="little")

    assert packet.raw == VALID_CRYOEGG_DATA
    assert len(packet) == len(VALID_CRYOEGG_DATA)

def test_mbuspacket_dummy():

    packet = cryodecoder.MBusPacket(VALID_MBUSPACKET_DATA_CONSTRUCTED)
    assert packet.c_field == 0x44
    assert packet.manufacturer_id == 0x4824
    assert packet.user_id == 0xCE240002
    assert packet.version == 0x01
    assert packet.dev == 0x07
    assert packet.control_field == 0xAA
    assert packet.rssi == 0x5A
    assert isinstance(packet.payload, cryodecoder.CryoeggPacket)
    assert packet.payload.raw == bytearray(VALID_CRYOEGG_DATA)

def test_mbuspacket_with_cryoegg():

    packet = cryodecoder.MBusPacket(VALID_MBUSPACKET_DATA)
    assert packet.c_field == 0x44
    assert packet.manufacturer_id == 0x4824
    assert packet.user_id == 0xCE240002
    assert packet.version == 0x01
    assert packet.dev == 0x07
    assert packet.control_field == 0xAA
    assert packet.rssi == 0x5A
    assert packet.payload == cryodecoder.CryoeggPacket(b'\xAA\x0F\x03\x04\xF2\x3F\xF2\x56\x8C\x0F\x19')

def test_cryoreceiverpacket_dummy():

    mbus_dummy_data = VALID_MBUSPACKET_DATA

    # 10060 tenths of a millibar = 0x274C -> little endian 0x4C, 0x27
    # 12000 millivolts = 0x2EE0 -> 0xE0, 0x2E
    dummy_data = mbus_dummy_data + VALID_CRYORECEIVER_DATA

    packet = cryodecoder.CryoReceiverPacket(dummy_data)
    
    assert isinstance(packet.mbus_packet, cryodecoder.MBusPacket)
    assert isinstance(packet.mbus_packet.payload, cryodecoder.CryoeggPacket)
    assert packet.temperature_logger == 0x25
    assert packet.channel == 1
    assert packet.pressure_logger == 10060
    assert packet.solar_voltage == 12000
