from cryodecoder import Data, CryoeggPacket, CryowurstPacket

class KellerPressureData:
    # Define default min/max pressure values
    PRESSURE_MAX_DEFAULT  = 100.00 #bar
    PRESSURE_MIN_DEFAULT  =    0.0 #bar
    PRESSURE_TYPE_DEFAULT =    "PA" #absolute pressure + 1bar
    #
    def __init__(self, pressure_keller_min = None, pressure_keller_max = None, keller_sensor_id = None, pressure_type = None, atmospheric_pressure = None, **kwargs):

        # Assign defaults in case of no info provided
        self.pressure_keller_max = pressure_keller_max or KellerPressureData.PRESSURE_MAX_DEFAULT
        self.pressure_keller_min = pressure_keller_min or KellerPressureData.PRESSURE_MIN_DEFAULT
        self.pressure_type = pressure_type or KellerPressureData.PRESSURE_TYPE_DEFAULT
        self.atmospheric_pressure = atmospheric_pressure or None 
        
        # then fallback to sensor ID (i.e. label provided by Cardiff)
        # in format:
        #   
        #       PA7LD30-2409        30bar  - 0 to 30
        #       PA7LHPD250-2410     250bar - 0 to 250
        if (pressure_keller_min == None and pressure_keller_max == None) and keller_sensor_id != None:
            # Assign sensor ID
            self.set_keller_sensor_id(keller_sensor_id)

    def set_keller_sensor_id(self, sensor_id):
        # TODO: Lookup sensor from catalogue
        raise NotImplementedError

    def parse_pressure_keller(self, raw):
        
        # Pressure value taken from Keller 7LD datasheet
        pressure = (raw - 16384) * (self.pressure_keller_max - self.pressure_keller_min) / 32768 + self.pressure_keller_min
    
        if self.pressure_type == "PR":
            # For relative pressure type (i.e. unsealed)
            if self.atmospheric_pressure == None:
                raise ValueError("Must set atmospheric pressure if using PR sensors")
            else:
                return pressure + self.atmospheric_pressure
        elif self.pressure_type == "PA":
            # For sealed gauge
            return pressure + 1.0
        elif self.pressure_type == "PAA":
            return pressure
        
class KellerTemperatureData:

    def __init__(self, **kwargs):
        pass

    def parse_temperature_keller(self, raw):
        return ((raw >> 4) - 24) * 0.05 - 50
    
class BatteryVoltageData:

    def __init__(self, **kwargs):
        pass

    def parse_battery_voltage(self, raw):
        # Convert mV to V
        return float(raw) / 1000

class SequenceNumberData:

    def __init__(self, **kwargs):
        pass

    def parse_sequence_number(self, raw):
        return raw
    
class ConductivityData:

    # Define default conductivity calibration value
    CONDUCTIVITY_CALIBRATION_DEFAULT = lambda x : float(x) / 1000 
    # use a mV to V mapping as a default for now 
    # (i.e. return an invalid value in V, rather than Siemens?)
    # - we might be able to improve this by taking a set of conductivity
    #   calibrations across multiple CEs

    def __init__(self, conductivity_calibration = None, **kwargs):

        if conductivity_calibration != None and not callable(conductivity_calibration):
            raise ValueError("conductivity calibration should be a callable (function-like) object.")

        # Set conductivity calibration to default
        self.conductivity_calibration = conductivity_calibration or CryoeggData.CONDUCTIVITY_CALIBRATION_DEFAULT

    def parse_conductivity(self, raw):
        # Return calibration conductivity from voltage
        return self.conductivity_calibration(raw)

##############################################################################
# CRYOWURST SPECIFIC SENSORS
##############################################################################

class TMP117TemperatureData:
    
    def __init__(self, **kwargs):
        pass

    def parse_temperature_tmp117(_, raw):
        # For TMP117 sensor, multiple returned value by 7.8125mC
        return float(raw) * 0.0078125 # degC
    
class ICM20948MagnetometerData:
    
    MAGNETOMETER_FULL_SCALE_DEFAULT = 4912 # uT
        
    def __init__(self, magnetometer_full_scale = None, **kwargs):
        # Assign default magnetometer full scale
        self.magnetometer_full_scale = \
            magnetometer_full_scale \
            or ICM20948MagnetometerData.MAGNETOMETER_FULL_SCALE_DEFAULT
    
    def __magnetometer_icm_20948(self, raw):
        if raw > 32752 or raw < -32752:
            raise ValueError("Invalid raw magnetometer value outside [-32752,32752] range.")
        else:
            return float(raw) / 32752 * self.magnetometer_full_scale # uT
    
    def parse_magnetometer_x(self, raw):
        return self.__magnetometer_icm_20948(raw)
    
    def parse_magnetometer_y(self, raw):
        return self.__magnetometer_icm_20948(raw)
    
    def parse_magnetometer_z(self, raw):
        return self.__magnetometer_icm_20948(raw)

class CTiTilt05AccelerometerData:

    ACCELEROMETER_FULL_SCALE_DEFAULT = 2 # g
    
    def __init__(self, accelerometer_full_scale = None, **kwargs):
        self.accelerometer_full_scale = accelerometer_full_scale or CryowurstData.ACCELEROMETER_FULL_SCALE_DEFAULT
        
    def __accelerometer_tilt05(_, raw):
        # For TILT-05 convert the accelerometer data from mg to g
        return float(raw) / 1000
    
    def parse_accelerometer_x(self, raw):
        return self.__accelerometer_tilt05(raw)
    
    def parse_accelerometer_y(self, raw):
        return self.__accelerometer_tilt05(raw)
    
    def parse_accelerometer_z(self, raw):
        return self.__accelerometer_tilt05(raw)

class CTiTilt05OrientationData:

    def __init__(self, **kwargs):
        pass

    def parse_pitch_x(self, raw):
        # convert back from 10*degrees to degrees
        return float(raw) / 10

    def parse_roll_y(self, raw):
        # convert back from 10*degrees to degrees
        return float(raw) / 10
    
##############################################################################
# CRYOEGG
##############################################################################

class CryoeggData(
    Data, 
    KellerPressureData, 
    KellerTemperatureData,
    ConductivityData,
    BatteryVoltageData,
    SequenceNumberData
):
    # Requires knowledge of pressure sensor to correctly define packet data
    def __init__(self, packet, **kwargs):
        
        Data.__init__(self, packet) 
        KellerPressureData.__init__(self, **kwargs) 
        KellerTemperatureData.__init__(self, **kwargs)
        ConductivityData.__init__(self, **kwargs)
        BatteryVoltageData.__init__(self, **kwargs)
        SequenceNumberData.__init__(self, **kwargs)

        # Check we've been passed a CryoeggPacket
        if not isinstance(packet, CryoeggPacket):
            raise TypeError("Invalid packet type, packet should be of type CryoeggPacket")

        # Convert packet fields to values
        self.convert()

    def parse_temperature_pt1000(_, raw):
        # No need to do anything for the PT1000
        return raw

##############################################################################
# CRYOWURST
##############################################################################    

class CryowurstData(
    Data, 
    KellerPressureData, 
    ICM20948MagnetometerData,
    CTiTilt05AccelerometerData,
    CTiTilt05OrientationData,
    TMP117TemperatureData,
    ConductivityData,
    BatteryVoltageData,
    SequenceNumberData
    ):

    def __init__(self, packet, **kwargs):

        # Call constructors of subclasses
        # TODO: add logic here for sensor_ids
        KellerPressureData.__init__(self, **kwargs) 
        ICM20948MagnetometerData.__init__(self, **kwargs)
        CTiTilt05AccelerometerData.__init__(self, **kwargs)
        CTiTilt05OrientationData.__init__(self, **kwargs)
        TMP117TemperatureData.__init__(self, **kwargs)
        BatteryVoltageData.__init__(self, **kwargs)
        SequenceNumberData.__init__(self, **kwargs)
        ConductivityData.__init__(self, **kwargs)

        # Check we've been passed a CryoeggPacket
        if not isinstance(packet, CryowurstPacket):
            raise TypeError("Invalid packet type, packet should be of type CryoeggPacket")
        # otherwise okay to assign the packet
        self.packet = packet

        # convert values
        self.convert()
        
##############################################################################
# CRYOWURST
##############################################################################    

class CryoReceiverData(Data):
    
    def __init__(self, packet):
        # Initialise object
        super().__init__(packet)
        # Convert packet fields to values
        self.convert()

    def parse_mbus_packet(self, raw):
        return raw

    def parse_channel(_, raw):
        if raw not in [1,2]:
            raise ValueError("Channel can only be 1 or 2")
        return raw
    
    def parse_temperature_logger(_, raw):
        return raw
    
    def parse_pressure_logger(_, raw):
        # returns units in bar
        return raw / 10000
    
    def parse_solar_voltage(_, raw):
        # returns units in volts
        return raw / 1000 