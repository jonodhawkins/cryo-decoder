from cryodecoder import Data, CryoeggPacket

class CryoeggData(Data):

    # Define default min/max pressure values
    PRESSURE_MAX_DEFAULT = 100.0 # bar
    PRESSURE_MIN_DEFAULT = 0.0   # bar
    # Define default conductivity calibration value
    CONDUCTIVITY_CALIBRATION_DEFAULT = lambda x : x 
    # use a 1-to-1 mapping as a default for now 
    # (i.e. return an invalid value in V, rather than Siemens?)
    # - we might be able to improve this by taking a set of conductivity
    #   calibrations across multiple CEs

    # Requires knowledge of pressure sensor to correctly define packet data
    def __init__(self, packet, pressure_min = None, pressure_max = None, conductivity_calibration = None):

        super().__init__(packet)

        # Check we've been passed a CryoeggPacket
        if not isinstance(packet, CryoeggPacket):
            raise TypeError("Invalid packet type, packet should be of type CryoeggPacket")

        # Set pressure values to default
        self.pressure_max = pressure_max or CryoeggData.PRESSURE_MAX_DEFAULT
        self.pressure_min = pressure_min or CryoeggData.PRESSURE_MIN_DEFAULT 

        # Set conductivity calibration to default
        self.conductivity_calibration = conductivity_calibration or CryoeggData.CONDUCTIVITY_CALIBRATION_DEFAULT

        # Convert packet fields to values
        self.convert()

    # Implement the same functions as the packet object to convert data from
    #  raw to a usable value
    @staticmethod
    def parse_conductivity(raw, self):
        # Return calibration conductivity from voltage
        return self.conductivity_calibration(float(raw) / 1000)

    @staticmethod
    def parse_temperature_pt1000(raw, _):
        # No need to do anything for the PT1000
        return raw

    @staticmethod
    def parse_pressure_keller(raw, self):
        # The Keller conversion is given by
        return (raw - 16384) * (self.pressure_max - self.pressure_min) / 32768 + self.pressure_min

    @staticmethod
    def parse_temperature_keller(raw, self):
        return ((raw >> 4) - 24) * 0.05 - 50

    @staticmethod
    def parse_battery_voltage(raw, _):
        return raw / 1000

    @staticmethod
    def parse_sequence_number(raw, _):
        return raw
    

class CryoReceiverData(Data):
    
    
    def __init__(self, packet):
        # Initialise object
        super().__init__(packet)
        # Convert packet fields to values
        self.convert()

    @staticmethod
    def parse_mbus_packet(raw, self):
        return raw

    @staticmethod
    def parse_channel(raw, _):
        if raw not in [1,2]:
            raise ValueError("Channel can only be 1 or 2")
        return raw
    
    @staticmethod
    def parse_temperature_logger(raw, _):
        return raw
    
    @staticmethod
    def parse_pressure_logger(raw, _):
        # returns units in bar
        return raw / 10000
    
    @staticmethod
    def parse_solar_voltage(raw, _):
        # returns units in volts
        return raw / 1000 