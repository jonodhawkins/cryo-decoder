from abc import ABC, abstractmethod

import sys

if sys.version_info <= (3,11):
    import toml as tomllib
else:
    import tomllib


##############################################################################
# PACKETS
##############################################################################

class InvalidPacketError(Exception):
    pass

class Packet:

    CONFIG = {}
    # Define magic word class variable
    MAIGC_WORD = b'\00'

    def __init__(self, raw = None, encoding = "utf-8"):

        # Define common instance variables for Packet
        if raw != None:
            self.set_raw_data(raw, encoding)
            # and parse
            self.parse()

    def set_raw_data(self, raw = None, encoding = "utf-8"):
        # Validate packet
        Packet.__validate_raw(raw)
        # and then assign data
        if isinstance(raw, str):
            self.raw = bytearray(raw, encoding)
        elif isinstance(raw, bytes): 
            self.raw = bytearray(raw)
        elif isinstance(raw, bytearray):
            self.raw = raw
        else:
            # TODO: fix with proper error message
            raise TypeError("Raw data must be str, bytes or bytearray")

        # Validate length        
        if len(raw) < self.__class__.MIN_SIZE:
            raise ValueError(f"Raw data should meet or exceed minimum size ({self.MIN_SIZE}) for packet type {self.__class__.__name__}")

    def __eq__(self, comparator):
        # Packets are equal if they are the same type,
        # and the raw data is the same for both
        if isinstance(comparator, self.__class__):
            return self.raw == comparator.raw
        else:
            return False

    # @abstractmethod
    # All subclasses should implement the parse method to assign 
    # instance variables
    def parse(self):
        
        # Store length variable locally
        length = len(self.raw)

        # Iterate through fields
        for field, field_config in Packet.CONFIG[self.__class__].fields.items():
            
            # Get start and end index
            if isinstance(field_config.offset, list): 
                offset_list = field_config.offset.copy()
            else:
                if field_config.length == None:
                    raise ValueError("Length field cannot be NoneType")
                # otherwise create a new list                
                offset_list = [field_config.offset, field_config.offset + field_config.length - 1]


            # Correct negative values
            for i in range(len(offset_list)):
                if offset_list[i] < 0:
                    # Substract from length
                    offset_list[i] = length + offset_list[i]

            # unpack indices
            start_idx, end_idx = offset_list

            # parse value
            parser = getattr(self.__class__, field_config.parser)
            setattr(self, field, parser(self, self.raw[start_idx : end_idx + 1]))

    def __len__(self):
        return len(self.raw)

    @classmethod
    def configure(this_class, packet_class, config_obj):

        # Check that a valid configuration exists
        if not packet_class.__name__ in config_obj:
            raise ValueError(f"Could not find class{config_obj} in the provided configuration file.")
        else:
            # Assign configuration to class
            this_class.CONFIG[packet_class] = \
                PacketConfig(config_obj[packet_class.__name__], packet_class.__name__)

            packet_class.MIN_SIZE = this_class.CONFIG[packet_class].length

    @staticmethod
    def __validate_raw(raw):    
        if not isinstance(raw, (str, bytes, bytearray)):
            raise TypeError("Raw data should be of type 'str', 'bytes' or 'bytearray'")
        

class PacketConfigParameters:
    
    OUTPUT_TYPE_MAP = {
        "int" : int,
        "float" : float,
        "str" : str,
        "bytes"  : bytes,
    } 

    def __init__(self, 
        offset = None,
        length = None,
        endianness = "little",
        output_type = "int",
        signed = False,
        parser = None
    ):
        self.offset = offset
        self.length = length
        self.endianness = endianness
        self.output_type = output_type,
        self.signed = signed,
        self.parser = parser

    def copy(self):
        return PacketConfigParameters(
            offset = self.offset,
            length = self.length,
            endianness = self.endianness,
            output_type = self.output_type,
            signed = self.signed,
            parser = self.parser,
        )
    
    def __repr__(self):
        return f"PacketConfigParameters: offset={self.offset}, length={self.length} -> parser={self.parser}"


class PacketConfig:

    PARAMETERS = {
        # Parameter name | Default value
        # -------------- | -------------
        "offset"         : None, 
        "length"         : 1,
        "endianness"     : "little",
        "output_type"    : "int",
        "signed"         : False,
        "parser"         : None
    }

    def __init__(self, config_obj, name):
        # Initialise default parameter array
        # - need to call dict to avoid shared reference
        self.__default_parameters = PacketConfigParameters()
        # and empty field array for packet components
        self.fields = dict()
        self.length = 0
        self.name = name
        
        # Check that the config contains the current packet
        self.parse(config_obj)

    def parse(self, config_obj):

        # Iterate through top level fields:
        #   these should either be within a list of default keywords, or
        #   they should be sub-dictionaries, in which case they are fields
        for field in config_obj:

            # Check it's a valid parameter and not a dictionary
            if field in PacketConfig.PARAMETERS \
                and not isinstance(config_obj[field], dict):

                # assign updated default parameter
                setattr(self.__default_parameters, field, config_obj[field])

            elif isinstance(config_obj[field], dict):    
                pass# Ignore for now because we need to parse all default parameters first
            else:
                raise ValueError(f"Invalid parameter {field} in config file.")

        # Now repeat again, because we've collected all the default parameters
        # we can add all the fields
        for field in config_obj:

            if not isinstance(config_obj[field], dict):
                # Ignore if it's not a dict
                pass
            else:
                # Create a temp dictionary to store parameter values
                # - need to call dict to avoid shared reference
                temp_parameters = self.__default_parameters.copy()
                # Iterate through parameters in the field definition
                field_obj = config_obj[field]

                for parameter in field_obj:
                    if parameter not in PacketConfig.PARAMETERS:
                        raise ValueError(f"Invalid parameter {parameter} in defition for {field}")
                    else:
                        setattr(temp_parameters, parameter, field_obj[parameter])

                # Sum up the number of bytes we have - if a value has None length 
                # (i.e. it's a variable field) then we leave this as zero.
                self.length += temp_parameters.length or 0

                # Assign the field to the packet defintion
                self.fields[field] = temp_parameters

def load_packet_config(path):
        if sys.version_info <= (3,11):
            # Load string
            with open(path, "r") as config_fh:
                toml_file = config_fh.read()
                return tomllib.loads(toml_file)
        else:  
            with open(path, "rb") as config_fh:
                return tomllib.load(config_fh)

##############################################################################
# DATA
##############################################################################
class Data:
    def __init__(self, packet):
        if not isinstance(packet, Packet):
            raise TypeError("Invalid type, should be of type Packet")
        self.packet = packet

    def get_packet(self):
        return self.packet
    
    def convert(self, packet = None):
        
        # Unless we are explicitly converting another packet
        # to allow stuffing of multiple data fields into one Data type 
        # then we should use the internal packet
        packet = packet or self.packet

        # First of all, we need to inspect the fields available:
        packet_config = Packet.CONFIG[packet.__class__]
        for field in packet_config.fields:

            # Then for each type, we can call the Data objects parse_* method
            # on the raw field value

            field_config = packet_config.fields[field]

            # get the raw field value (i.e. after we have sorted byte order, etc.)
            raw_value = getattr(self.packet, field)

            # get the conversion function
            converter_function = getattr(self, field_config.parser)
            # perform the conversion on the raw value and assign
            setattr(self, field, converter_function(raw_value))

##############################################################################