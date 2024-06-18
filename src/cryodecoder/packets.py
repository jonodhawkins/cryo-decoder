from cryodecoder import Packet, InvalidPacketError
import struct

class MBusPacket(Packet):

    def __init__(self, raw, allow_any_payload = False, *args, **kwargs):
        # Call super class constructor
        self.allow_any_payload = allow_any_payload
        super().__init__(raw, *args, **kwargs)

    def parse_cfield(self, raw):
        return int.from_bytes(raw, byteorder="little")
    
    def parse_m_id(self, raw):
        return int.from_bytes(raw, byteorder="little")
    
    def parse_user_id(self, raw):
        return int.from_bytes(raw, byteorder="little")
    
    def parse_version(self, raw):
        return int.from_bytes(raw, byteorder="little")
    
    def parse_dev(self, raw):
        return int.from_bytes(raw, byteorder="little")
    
    def parse_control_field(self, raw):
        return int.from_bytes(raw, byteorder="little")
    
    def parse_rssi(self, raw):
        return -int.from_bytes(raw, byteorder="little") / 2
    
    def parse_payload(self, raw):
        # Check length of payload
        if len(raw) == CryoeggPacket.MIN_SIZE:
            # Try and create a Cryoegg payload
            return CryoeggPacket(raw)
        elif len(raw) == CryowurstPacket.MIN_SIZE:
            return CryowurstPacket(raw)
        elif len(raw) == HydrobeanPacket.MIN_SIZE:
            return HydrobeanPacket(raw)
        elif self.allow_any_payload:
            return raw
        else:
            raise InvalidPacketError("allow_any_payload must be enabled for raw MBusPacket payloads")
    
    def summary(self):

        payload_summary = None
        if self.allow_any_payload and isinstance(self.payload, (bytes, bytearray)):
            payload_summary = "".join([f"{byte:02x}" for byte in self.payload])
        else:
            payload_summary = self.payload.summary() if hasattr(self.payload, "summary") else "".join([f"{byte:02x}" for byte in self.payload.raw])

        return f"MBusPacket ({self.user_id:x} @ {self.rssi} dBm): {payload_summary}"

class CryoeggPacket(Packet):

    def __init__(self, raw, *args, **kwargs):
        # Call super class constructor
        super().__init__(raw, *args, **kwargs)
        # Validate packet length
        if len(self.raw) != self.__class__.MIN_SIZE:
            raise InvalidPacketError(f"Invalid packet length ({len(self.raw)}), expecting {self.__class__.MIN_SIZE}")

    def parse_conductivity(self, raw):
        # Return voltage
        return int.from_bytes(raw, byteorder="little")

    def parse_temperature_pt1000(self, raw):
        return int.from_bytes(raw, byteorder="little")

    def parse_pressure_keller(self, raw):
        return int.from_bytes(raw, byteorder="little")

    def parse_temperature_keller(self, raw):
        return int.from_bytes(raw, byteorder="little")

    def parse_battery_voltage(self, raw):
        return int.from_bytes(raw, byteorder="little")

    def parse_sequence_number(_, raw):
        return int.from_bytes(raw, byteorder="little")
    
    


class HydrobeanPacket(Packet):

    def __init__(self, raw, *args, **kwargs):
        super().__init__(raw, *args, **kwargs)
        # Validate packet length
        if len(self.raw) != self.__class__.MIN_SIZE:
            raise InvalidPacketError(f"Invalid packet length ({len(self.raw)}), expecting {self.__class__.MIN_SIZE}")

    def parse_conductivity(self, raw):
        return CryoeggPacket.parse_conductivity(self, raw)
    
    def parse_pressure_keller(self, raw):
        return CryoeggPacket.parse_pressure_keller(self, raw)
    
    def parse_temperature_keller(self, raw):
        return CryoeggPacket.parse_temperature_keller(self, raw)
    
    def parse_battery_voltage(self, raw):
        return CryoeggPacket.parse_battery_voltage(self, raw)
    
    def parse_sequence_number(_, raw):
        return CryoeggPacket.parse_sequence_number(_, raw)
    
class CryowurstPacket(Packet):

    def __init__(self, raw, *args, **kwargs):
        super().__init__(raw, *args, **kwargs)
        # Validate packet length
        if len(self.raw) != self.__class__.MIN_SIZE:
            raise InvalidPacketError(f"Invalid packet length ({len(self.raw)}), expecting {self.__class__.MIN_SIZE}")

    def parse_conductivity(self, raw):
        return int.from_bytes(raw, byteorder="big")
    
    def parse_pressure_keller(self, raw):
        return int.from_bytes(raw, byteorder="big")
    
    def parse_battery_voltage(self, raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    def parse_sequence_number(_, raw):
        return CryoeggPacket.parse_sequence_number(_, raw)
    
    # ------------
    def parse_temperature_tmp117(self, raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
        # save for later * 7.8125 / 1000

    def parse_magnetometer_x(self, raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    def parse_magnetometer_y(self, raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    def parse_magnetometer_z(self, raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    def parse_accelerometer_x(self, raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    def parse_accelerometer_y(self, raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    def parse_accelerometer_z(self, raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    def parse_pitch_x(self, raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
    def parse_roll_y(self, raw):
        return int.from_bytes(raw, byteorder="big", signed=True)
    
class CryoReceiverPacket(Packet):

    def __init__(self, raw, *args, **kwargs):
        super().__init__(raw, *args, **kwargs)

    def parse_channel(self, raw):
        return int.from_bytes(raw, byteorder="little")

    def parse_temperature_logger(self, raw):
        return int.from_bytes(raw, byteorder="little")

    def parse_pressure_logger(self, raw):
        return int.from_bytes(raw, byteorder="little")

    def parse_solar_voltage(self, raw):
        return int.from_bytes(raw, byteorder="little")

    def parse_mbus_packet(self, raw):
        
        # For any CryoReceiverPacket we're assuming that the
        # payload will be an MBusPacket, hence
        return MBusPacket(raw)
    
class SDSatellitePacket(Packet):

    def __init__(self, raw, *args, **kwargs):
        #
        super().__init__(raw, *args, **kwargs)
        # Validate packet length
        if len(self.raw) > self.__class__.MIN_SIZE + self.length:
            raise ValueError(f"Raw packet length ({len(self.raw)}) exceeds expected length {self.__class__.MIN_SIZE + self.length}")

    def parse_header(self, raw):
        return raw.decode("ascii")
    
    def parse_timestamp(self, raw):
        # TODO: assuming little-endian but need to verify
        return int.from_bytes(raw, byteorder="little")
    
    def parse_temperature_logger(self, raw):
        return struct.unpack("<f", raw)[0]
    
    def parse_pressure_logger(self, raw):
        return struct.unpack("<f", raw)[0]
    
    def parse_solar_voltage(self, raw):
        return int.from_bytes(raw, byteorder="little")
    
    def parse_channel(self, raw):
        return int.from_bytes(raw, byteorder="little")
    
    def parse_length(self, raw):
        return int.from_bytes(raw, byteorder="little")
        
    def parse_mbus_packet(self, raw):
        return CryoReceiverPacket.parse_mbus_packet(self, raw)
    
    