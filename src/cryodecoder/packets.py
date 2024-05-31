from cryodecoder import *

class MBusPacket(Packet):

    def __init__(self, *args, **kwargs):
        # Call super class constructor
        Packet.__init__(self, *args, **kwargs)

    @staticmethod
    def parse_cfield(raw):
        return int.from_bytes(raw)
    
    @staticmethod
    def parse_m_id(raw):
        return int.from_bytes(raw, byteorder="little")
    
    @staticmethod
    def parse_user_id(raw):
        return int.from_bytes(raw, byteorder="little")
    
    @staticmethod
    def parse_version(raw):
        return int.from_bytes(raw)
    
    @staticmethod
    def parse_dev(raw):
        return int.from_bytes(raw)
    
    @staticmethod
    def parse_control_field(raw):
        return int.from_bytes(raw)
    
    @staticmethod
    def parse_rssi(raw):
        return int.from_bytes(raw, signed=True)
    
    @staticmethod
    def parse_payload(raw):
        return raw
    
class CryoeggPacket(Packet):

    def __init__(self, *args, **kwargs):
        # Call super class constructor
        Packet.__init__(self, *args, **kwargs)

    @staticmethod
    def parse_conductivity(raw):
        # Return voltage
        return int.from_bytes(raw, byteorder="little") / 1000

    @staticmethod
    def parse_temperature_pt1000(raw):
        return int.from_bytes(raw, byteorder="little")

    @staticmethod
    def parse_pressure_keller(raw):
        return int.from_bytes(raw, byteorder="little")

    @staticmethod
    def parse_temperature_keller(raw):
        return int.from_bytes(raw, byteorder="little")

    @staticmethod
    def parse_battery_voltage(raw):
        return int.from_bytes(raw, byteorder="little") / 1000

    @staticmethod
    def parse_sequence_number(raw):
        return int.from_bytes(raw)
    
class HydrobeanPacket(Packet):

    def __init__(self, *args, **kwargs):
        Packet.__init__(self, *args, **kwargs)

    @staticmethod
    def parse_conductivity(raw):
        return CryoeggPacket.parse_conductivity(raw)
    
    @staticmethod
    def parse_pressure_keller(raw):
        return CryoeggPacket.parse_pressure_keller(raw)
    
    @staticmethod
    def parse_temperature_keller(raw):
        return CryoeggPacket.parse_temperature_keller(raw)
    
    @staticmethod
    def parse_battery_voltage(raw):
        return CryoeggPacket.parse_battery_voltage(raw)
    
    @staticmethod
    def parse_sequence_number(raw):
        return CryoeggPacket.parse_sequence_number(raw)
    
class CryowurstPacket(Packet):

    def __init__(self, *args, **kwargs):
        Packet.__init__(self, *args, **kwargs)

    @staticmethod
    def parse_conductivity(raw):
        return int.from_bytes(raw, byteorder="big")
    
    @staticmethod
    def parse_pressure_keller(raw):
        return int.from_bytes(raw, byteorder="big")
    
    @staticmethod
    def parse_battery_voltage(raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    @staticmethod
    def parse_sequence_number(raw):
        return CryoeggPacket.parse_sequence_number(raw)
    
    # ------------
    @staticmethod
    def parse_temperature_tmp117(raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
        # save for later * 7.8125 / 1000

    @staticmethod
    def parse_magnetometer_x(raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    @staticmethod
    def parse_magnetometer_y(raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    @staticmethod
    def parse_magnetometer_z(raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    @staticmethod
    def parse_accelerometer_x(raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    @staticmethod
    def parse_accelerometer_y(raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    @staticmethod
    def parse_accelerometer_z(raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    @staticmethod
    def parse_pitch_x(raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    @staticmethod
    def parse_roll_y(raw):
        return int.from_bytes(raw, byteorder="big", signed=True)