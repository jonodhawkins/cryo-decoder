import pytest
import cryodecoder

##############################################################################
# Define valid data types
##############################################################################
VALID_CRYOEGG_DATA = b'\xA0\x0F\x03\x04\xF3\x3F\x45\x59\xAC\x0F\x00'
# VALID_CRYOWURST_DATA = b'\x00\xf5\xfe\xfe\x02\x06\xfe\x96\xff\xf4\x00\x1e\xfc\x1a\xff\xfa\x00\x11\x032\x00\x00\r\xdf\x07'
VALID_CRYOWURST_DATA = bytes.fromhex("010a00610137004a002d00e6fc35001a0085047f00000dc6f8") #b'\x0e=\xff\xad\xfd\xf2\x024\x01$\xfdv\x02\xbd\x00\xaa\xfek\r:\x00\x00\rv\xb0'
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

def test_cryoeggpacket_invalid_length():

    # Test undersized
    with pytest.raises(ValueError):
        packet = cryodecoder.CryoeggPacket(VALID_CRYOEGG_DATA[0:-1])
    
    # Test oversized
    with pytest.raises(ValueError):
        packet = cryodecoder.CryoeggPacket(VALID_CRYOEGG_DATA + b'\x00')

def test_cryowrustpacket_real():

    packet = cryodecoder.CryowurstPacket(VALID_CRYOWURST_DATA)

    assert packet.temperature == int.from_bytes(b'\x01\x0a', byteorder="big", signed=True)
    assert packet.magnetometer_x == int.from_bytes(b'\x00\x61', byteorder="big", signed=True)
    assert packet.magnetometer_y == int.from_bytes(b'\x01\x37', byteorder="big", signed=True)
    assert packet.magnetometer_z == int.from_bytes(b'\x00\x4a', byteorder="big", signed=True)
    assert packet.accelerometer_x == int.from_bytes(b'\x00\x2d', byteorder="big", signed=True)
    assert packet.accelerometer_y == int.from_bytes(b'\x00\xe6', byteorder="big", signed=True)
    assert packet.accelerometer_z == int.from_bytes(b'\xfc\x35', byteorder="big", signed=True)
    assert packet.pitch_x == int.from_bytes(b'\x00\x1a', byteorder="big", signed=True)
    assert packet.roll_y == int.from_bytes(b'\x00\x85', byteorder="big", signed=True)
    assert packet.conductivity == 0x47f
    assert packet.pressure == 0x0000
    assert packet.battery_voltage == 0xdc6
    assert packet.sequence_number == 0xf8


def test_cryowurstpacket_invalid_length():

    # Test undersized
    with pytest.raises(ValueError):
        packet = cryodecoder.CryowurstPacket(VALID_CRYOWURST_DATA[0:-1])
    
    # Test oversized
    with pytest.raises(ValueError):
        packet = cryodecoder.CryowurstPacket(VALID_CRYOWURST_DATA + b'\x00')

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
    
def test_sdsatellitereceiverpacket_real():

    sd_packet_data = bytes.fromhex("5731b5a4d7644abf4241fb0d5b44810c0124440102010020cf0107ac00f5fefe0206fe96fff4001efc1afffa0011033200000ddf078e")

    packet = cryodecoder.SDSatellitePacket(sd_packet_data)

    assert isinstance(packet.mbus_packet, cryodecoder.MBusPacket)
    assert isinstance(packet.mbus_packet.payload, cryodecoder.CryowurstPacket)
    assert packet.mbus_packet.user_id == 0xCF200001
    
def test_sdsatellitereceiverpacket_badlength():

    long_sd_packet_data = bytes.fromhex("573184aad764b82c4a41a4025b44920c0124440300020020cf0107ac010c005f01320040002d00e5fc35001a0084047d00000dc8fe9e573184aad764b82c4a41a4025b44920c0224440300020020cf0107ac010c005f01320040002d00e5fc35001a0084047d00000dc8fe94")

    with pytest.raises(ValueError, match=r"Raw packet length .*") as e_info:
        packet = cryodecoder.SDSatellitePacket(long_sd_packet_data)
