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
    
class CryowurstData(Data):

    ACCELEROMETER_FULL_SCALE_DEFAULT = 2 # g
    MAGNETOMETER_FULL_SCALE_DEFAULT = 4912 # uT
    CONDUCTIVITY_CALIBRATION_DEFAULT = lambda x : x 
    # use a 1-to-1 mapping as a default for now 
    # (i.e. return an invalid value in V, rather than Siemens?)
    # - we might be able to improve this by taking a set of conductivity
    #   calibrations across multiple CEs

    def __init__(self, packet, accelerometer_full_scale = None, magnetometer_full_scale = None, conductivity_calibration = None):
        super().__init__(packet)

        self.accelerometer_full_scale = accelerometer_full_scale or CryowurstData.ACCELEROMETER_FULL_SCALE_DEFAULT
        self.magnetometer_full_scale = magnetometer_full_scale or CryowurstData.MAGNETOMETER_FULL_SCALE_DEFAULT
        self.conductivity_calibration = conductivity_calibration or CryoeggData.CONDUCTIVITY_CALIBRATION_DEFAULT

        self.convert()

    @staticmethod
    def parse_temperature(raw, _):
        # For TMP117 sensor, multiple returned value by 7.8125mC
        return float(raw) * 0.0078125 # degC
    
    @staticmethod
    def __magnetometer_icm_20948(raw, self):
        if raw > 32752 or raw < -32752:
            raise ValueError("Invalid raw magnetometer value outside [-32752,32752] range.")
        else:
            return float(raw) / 32752 * self.accelerometer_full_scale # uT

    @staticmethod
    def parse_magnetometer_x(raw, self):
        return CryowurstData.__magnetometer_icm_20948(raw, self)
    
    @staticmethod
    def parse_magnetometer_y(raw, self):
        return CryowurstData.__magnetometer_icm_20948(raw, self)
    
    @staticmethod
    def parse_magnetometer_z(raw, self):
        return CryowurstData.__magnetometer_icm_20948(raw, self)
    
    @staticmethod
    def __accelerometer_tilt05(raw, _):
        # For TILT-05 convert the accelerometer data from mg to g
        return float(raw) / 1000

    @staticmethod
    def __accelerometer(raw, self):
        # TODO: Switch behaviour based on which accelerometer was used
        return CryowurstData.__accelerometer_tilt05(raw, self)
    
    @staticmethod
    def parse_accelerometer_x(raw, self):
        return CryowurstData.__accelerometer(raw, self)
    
    @staticmethod
    def parse_accelerometer_y(raw, self):
        return CryowurstData.__accelerometer(raw, self)
    
    @staticmethod
    def parse_accelerometer_z(raw, self):
        return CryowurstData.__accelerometer(raw, self)
    
    @staticmethod
    def parse_pitch_x(raw, self):
        # convert back from 10*degrees to degrees
        raise float(raw) / 10
    
    @staticmethod
    def parse_roll_y(raw, self):
        # convert back from 10*degrees to degrees
        raise float(raw) / 10
    
    @staticmethod
    def parse_conductivity(raw, self):
        # Return calibration conductivity from voltage
        return self.conductivity_calibration(float(raw) / 1000)
    
    @staticmethod
    def parse_pressure_sensor(raw, self):
        # The Keller conversion is given by
        return (raw - 16384) * (self.pressure_max - self.pressure_min) / 32768 + self.pressure_min

    @staticmethod
    def parse_battery_voltage(raw, self):
        raise float(raw) / 1000

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