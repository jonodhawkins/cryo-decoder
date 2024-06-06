import pytest
import cryodecoder

VALID_CRYOEGG_DATA = b'\xA0\x0F\x03\x04\xF3\x3F\x45\x59\xAC\x0F\x00'
VALID_CRYOWURST_DATA = bytes.fromhex("010a00610137004a002d00e6fc35001a0085047f00000dc6f8") #b'\x0e=\xff\xad\xfd\xf2\x024\x01$\xfdv\x02\xbd\x00\xaa\xfek\r:\x00\x00\rv\xb0'
VALID_CRYORECEIVER_DATA = b'\x44\x24\x48\x02\x00\x24\xCE\x01\x07\xAA\xAA\x0F\x03\x04\xF2\x3F\xF2\x56\x8C\x0F\x19\x5A' + b'\x01\x25\x4C\x27\xE0\x2E'

##############################################################################
# Cryoegg Tests
##############################################################################

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

    assert data.pressure_keller_max == 100.0 # default value
    assert data.pressure_keller_min == 0

    assert abs(data.pressure - 0.960) < 0.001 # correct to 1mBar? 

def test_cryoeggdata_keller_pressure_alternative():

    packet = cryodecoder.CryoeggPacket(VALID_CRYOEGG_DATA)
    data = cryodecoder.CryoeggData(packet, pressure_keller_max = 250.0) 

    assert data.pressure_keller_max == 250.0

    assert abs(data.pressure - 0.900) < 0.001 * 2.5 # scale by 2.5 to account 
    # for 250 bar scaling.   

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

def test_cryoeggdata_conductivity_calibration_alternative():
    
    packet = cryodecoder.CryoeggPacket(VALID_CRYOEGG_DATA)
    
    # Define new conductivity function to convert 4000 mV to 
    # a made up value of 18 uS
    cond_cal = lambda x : x / 1000 / 4 * 18.0e-6

    data = cryodecoder.CryoeggData(packet, conductivity_calibration=cond_cal)

    assert data.conductivity == 18e-6

##############################################################################
# Cryowurst Tests
##############################################################################

def test_cryowurstdata_temperature():
    
    packet = cryodecoder.CryowurstPacket(VALID_CRYOWURST_DATA)
    data = cryodecoder.CryowurstData(packet)

    assert (data.temperature - 2.078125) < 0.0078125 

def test_cryowurstdata_magnetometer():
    
    packet = cryodecoder.CryowurstPacket(VALID_CRYOWURST_DATA)
    data = cryodecoder.CryowurstData(packet)

    raise NotImplementedError

def test_cryowurstdata_accelerometer():
    
    packet = cryodecoder.CryowurstPacket(VALID_CRYOWURST_DATA)
    data = cryodecoder.CryowurstData(packet)

    raise NotImplementedError

def test_cryowurstdata_pitch():
    
    packet = cryodecoder.CryowurstPacket(VALID_CRYOWURST_DATA)
    data = cryodecoder.CryowurstData(packet)

    assert abs(data.pitch_x - 2.6) < 0.1

def test_cryowurstdata_roll():
    
    packet = cryodecoder.CryowurstPacket(VALID_CRYOWURST_DATA)
    data = cryodecoder.CryowurstData(packet)

    assert abs(data.roll_y - 13.3) < 0.1

def test_cryowurstdata_conductivity():
    
    packet = cryodecoder.CryowurstPacket(VALID_CRYOWURST_DATA)
    data = cryodecoder.CryowurstData(packet)

    # Raw value is 0x47f, hence divide by 1000 and validate using 1:1 mapping
    # we check the conductivity class above
    # TODO: introduce conductivitydata class test on its own

    assert data.conductivity == float(0x47f) / 1000

def test_cryowurstdata_pressure():

    packet = cryodecoder.CryowurstPacket(VALID_CRYOWURST_DATA)
    
    # Recored value in VALID_CRYOWURST_DATA is 0x0000 
    # Modify the pressure value to a known prior value we make up
    # here
    
    # Create fake min, max and test pressure values
    pres_min = 0.0; pres_max = 100.0; pres_test = 012.3
    
    packet.pressure = int(32768 * ((pres_test - 1) - pres_min) / (pres_max - pres_min) + 16384)

    # Create data packet with new values
    data = cryodecoder.CryowurstData(packet, \
        pressure_keller_max = pres_max, 
        pressure_keller_mIN = pres_min)
    
    # Check we convert back to the pressure value correctly
    assert abs(data.pressure - pres_test) < (pres_max - pres_min) / 32768

def test_cryowurstdata_battery_voltage():
    
    packet = cryodecoder.CryowurstPacket(VALID_CRYOWURST_DATA)
    data = cryodecoder.CryowurstData(packet)

    # Check battery voltage is valid to within 1 mV
    assert abs(data.battery_voltage - 3.526) < 0.001

def test_cryowurstdata_sequence_number():
    
    packet = cryodecoder.CryowurstPacket(VALID_CRYOWURST_DATA)
    data = cryodecoder.CryowurstData(packet)

    assert data.sequence_number == int(0xf8)

##############################################################################
# Cryoreceiver Tests
##############################################################################

def test_cryoreceiverdata_channel():
    
    packet = cryodecoder.CryoReceiverPacket(VALID_CRYORECEIVER_DATA)
    data = cryodecoder.CryoReceiverData(packet)

    assert data.channel == 1

def test_cryoreceiverdata_temperature_logger():
    
    packet = cryodecoder.CryoReceiverPacket(VALID_CRYORECEIVER_DATA)
    data = cryodecoder.CryoReceiverData(packet)

    assert abs(data.temperature_logger - 37.0) <= 1

def test_cryoreceiverdata_pressure_logger():
    
    packet = cryodecoder.CryoReceiverPacket(VALID_CRYORECEIVER_DATA)
    data = cryodecoder.CryoReceiverData(packet)
    
    assert abs(data.pressure_logger - 1.006) < 0.0001

def test_cryoreceiverdata_solar_voltage():
        
    packet = cryodecoder.CryoReceiverPacket(VALID_CRYORECEIVER_DATA)
    data = cryodecoder.CryoReceiverData(packet)

    assert abs(data.solar_voltage - 12.0) < 0.001

def test_cryoreceiverdata_mbus_packet():

    packet = cryodecoder.CryoReceiverPacket(VALID_CRYORECEIVER_DATA)
    data = cryodecoder.CryoReceiverData(packet)
    
    assert isinstance(data.mbus_packet, cryodecoder.MBusPacket)

##############################################################################
# SD/Satellite Data Tests
##############################################################################
# TODO: implement tests for SD/Satellite Data Tests