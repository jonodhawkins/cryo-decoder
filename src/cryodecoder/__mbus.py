    # @staticmethod
    # def convert_logger_rssi(raw):
    #     """
    #     Converts a single byte to a signed integer
    #     """
    #     if isinstance(raw, (bytes, bytearray)):
    #         return int.from_bytes(raw, signed=True)
    #     elif isinstance(raw, int):
    #         return raw
    #     else:
    #         raise ValueError("Raw value must be of type bytes or int")
        
    # @staticmethod
    # def convert_logger_temp(raw):
    #     if isinstance(raw, (bytes, bytearray)):
    #         return int.from_bytes(raw)
    #     elif isinstance(raw, int):
    #         return raw
    #     else:
    #         raise ValueError("Raw value must be of type bytes or int")
        
    # @staticmethod
    # def convert_logger_pressure(raw):
    #      # Divide by 10,000 to convert to bar
    #     if isinstance(raw, (bytes, bytearray)):
    #         return int.from_bytes(raw, byteorder='little', signed=True) / 10000
    #     elif isinstance(raw, int):
    #         return raw / 10000
    #     else:
    #         raise ValueError("Raw value must be of type bytes or int")
        
    # @staticmethod
    # def convert_logger_voltage(raw):
    #      # Divide by 1,000 to convert to Volts
    #     if isinstance(raw, (bytes, bytearray)):
    #         return int.from_bytes(raw, byteorder='little', signed=True) / 1000
    #     elif isinstance(raw, int):
    #         return raw / 1000
    #     else:
    #         raise ValueError("Raw value must be of type bytes or int")
        
    # @staticmethod
    # def validate_rssi(raw):
    #     return True
    
    # @staticmethod
    # def validate_logger_temp(raw):
    #     pass
        
        

# class MBusPacketReaderState(Enum):
#     STATE_WAITING   = 1,
#     STATE_LENGTH    = 2,
#     STATE_CFIELD    = 3,
#     STATE_HEADER    = 4,
#     STATE_CIFIELD   = 5,
#     STATE_RSSI      = 6,
#     STATE_TEMP      = 7,
#     STATE_PRESSURE  = 8,
#     STATE_VOLTAGE   = 9,
#     STATE_PALOAD    = 10,
#     STATE_READY     = 11

# class MBusPacketReader:

#     MAX_BUFFER_LENGTH = 256
#     VALID_ID_PREFIXES = [0xCE,]
#     VALID_RSSI_VALUES = range(-127, 31)

#     def __init__(self, 
#         path_or_data,
#         error_logger_variables = False,
#         error_header_id = True,
#         error_length = False,
#         error_c_field = False,
#         error_ci_field = False
#     ):

#         # Assign empty path
#         self.path = None
#         self.data = None

#         # Assign exception flags
#         self.exception_flags = {
#             "logger_variables"  : error_logger_variables, # raise Exception on suspect RSSI, temp, pressure or voltage values
#             "header_id"                : error_header_id, # if the prefix isn't in VALID_ID_PREFIXES
#             "length"            : error_length, # raise exception for invalid length
#             "c_field"           : error_c_field, # if C-field isn't 0x44
#             "ci_field"          : error_ci_field # if the CI-field isn't valid (need to work out what is valid...)
#         }

#         # Check whether we are dealing with a file path, or raw data
#         if isinstance(path_or_data, str) or isinstance(path_or_data, os.PathLike):
#             self.path = path_or_data
#         elif isinstance(path_or_data, bytes):
#             self.data = path_or_data
#         else:
#             raise TypeError("Path should be str, PathLike. Data should be bytes.")

#         # Initialise buffer to null bytes with max buffer length 
#         self.buffer = bytearray(MBusPacketReader.MAX_BUFFER_LENGTH)
#         # Set header position (to read bytes in at)
#         self.buffer_head = 0 # starts at 0, increases until at end of buffer
#         self.buffer_length = self.MAX_BUFFER_LENGTH # initialise buffer as full
        
#         # Initialise read packet state
#         self.packet_state = MBusPacketReaderState.STATE_WAITING
#         self.packet_temp = None

#     def __enter__(self):

#         # Defined empty BufferedReader object
#         self._reader = None
#         # We shouldn't be in a situation when path and data are both defined
#         if self.path is not None and self.data is not None:
#             raise ValueError("Cannot enter with path and data both defined.")
        
#         # so if not then we either have one or the other, or neither
#         if self.path is not None:
#             self._reader = open(self.path, 'rb')
#         elif self.data is not None:
#             self._reader = io.BufferedReader(io.BytesIO(self.data))
#         else:
#             raise FileNotFoundError("No path or data provided.")
        
#         return self

#     def __exit__(self, type, value, traceback):
#         # Close the buffered reader
#         if self._reader is not None:
#             self._reader.close()

#     def read_packet(self):
        
#         while True:
#             try:
#                 self.read_packet_state_machine()
#             except StopIteration:
#                 return self.packet_temp
#             # Add other exceptions here to handle properly
#             except Exception as e:
#                 raise e
            
#     def read_packet_state_machine(self):
    
#         # Perform action based on state
#         if self.packet_state == MBusPacketReaderState.STATE_WAITING:
            
#             if self._reader is None or self._reader.closed:
#                 raise ValueError("BufferedReader closed.")
            
#             # Read in new byte
#             byte_in = self._reader.read(1)
#             if len(byte_in) == 1:
#                 # Byte available
#                 if self.buffer_length < MBusPacketReader.MAX_BUFFER_LENGTH:
#                     # Append byte
#                     self.buffer[self.buffer_length] = int.from_bytes(byte_in)
#                     self.buffer_length += 1
#                 else:
#                     # Left shift
#                     self.buffer = self.buffer[1:self.buffer_length] + byte_in
#             else:
#                 # Byte unavailable
#                 if self.buffer_length > 0:
#                     self.buffer = self.buffer[1:self.buffer_length]
#                     self.buffer_length -= 1
#                 else:
#                     self.packet_temp = None
#                     raise StopIteration
            
#             # Change state
#             if self.buffer[0] == 0:
#                 self.packet_state = MBusPacketReaderState.STATE_WAITING
#             else:
#                 self.packet_state = MBusPacketReaderState.STATE_LENGTH

#         elif self.packet_state == MBusPacketReaderState.STATE_LENGTH:

#             # Check there are more bytes in the buffer than length
#             if self.buffer_length < int(self.buffer[0]):
#                 self.packet_temp = None
#                 raise StopIteration
            
#             # Is length valid (i.e. within 7-253 inclusive)
#             if int(self.buffer[0]) not in range(7, 254):
#                 # TODO: add logging to indicate bad state
#                 self.packet_state = MBusPacketReaderState.STATE_WAITING
#             else:
#                 # Move to next state
#                 self.packet_state = MBusPacketReaderState.STATE_CFIELD

#         elif self.packet_state == MBusPacketReaderState.STATE_CFIELD:
            
#             # Check c-field is valid
#             if self.buffer[1] != 0x44:
#                 # TODO: add logging to indicate bad value
#                 self.packet_state = MBusPacketReaderState.STATE_WAITING
#             else:
#                 # Move to next state
#                 self.packet_state = MBusPacketReaderState.STATE_HEADER

#         elif self.packet_state == MBusPacketReaderState.STATE_HEADER:

#             # Break down header
#             m_field = self.buffer[2:4]
#             id_field = self.buffer[4:8]
#             ver = self.buffer[8]
#             dev = self.buffer[9]

#             # TODO: Validate any of the above
#             if id_field[0] not in MBusPacketReader.VALID_ID_PREFIXES:
#                 # Skip length of packet
#                 self.skip(self.buffer[0]) # sets state based on buffer length
#                 raise InvalidPacketError("Invalid ID prefix value")
#             else:
#                 self.packet_state = MBusPacketReaderState.STATE_CIFIELD

#         elif self.packet_state == MBusPacketReaderState.STATE_CIFIELD:
            
#             # TODO: Validate CI-field
#             self.packet_state = MBusPacketReaderState.STATE_RSSI

#         elif self.packet_state == MBusPacketReaderState.STATE_RSSI:
            
#             # Get packet length from first byte in buffer
#             length = self.buffer[0]
#             # Convert RSSI
#             rssi = MBusPacket.convert_logger_rssi(self.buffer[length - 6]) # should this throw an exception?
            
#             if not MBusPacket.validate_rssi(rssi):
#                 # Skip length of packet
#                 self.skip(self.buffer[0]) # sets state based on buffer length
#                 # and raise exception if enabled
#                 if self.exception_flags["logger_variables"]:
#                     raise InvalidPacketError("Invalid RSSI value")
#             else:
#                 self.packet_state = MBusPacketReaderState.STATE_TEMP

#         elif self.packet_state == MBusPacketReaderState.STATE_TEMP:
            
#             # Get packet length from first byte in buffer
#             length = self.buffer[0]
#             # Convert temperature
#             if not MBusPacket.validate_logger_temp(self.buffer[length - 5]):
#                 self.skip(self.buffer[0])
#                 if self.exception_flags["logger_variables"]:
#                     raise InvalidPacketError("Invalid logger temperature value")
#             else:
#                 self.packet_state = MBusPacketReaderState.STATE_PRESSURE

#         elif self.packet_state == MBusPacketReaderState.STATE_PRESSURE:
            
#             # Get packet length from first byte in buffer
#             length = self.buffer[0]
#             # Convert temperature
#             if not MBusPacket.validate_logger_pressure(self.buffer[length - 4 : length - 2]): # should this throw an exception?
#                 self.skip(self.buffer[0])
#             else:
#                 self.packet_state = MBusPacketReaderState.STATE_VOLTAGE

#         elif self.packet_state == MBusPacketReaderState.STATE_VOLTAGE:
            
#             # Get packet length from first byte in buffer
#             length = self.buffer[0]
#             # Convert temperature
#             voltage = MBusPacket.convert_logger_voltage(self.buffer[length - 4 : length - 2]) # should this throw an exception?
#             # TODO: validate voltage

#             self.packet_state = MBusPacketReaderState.STATE_PALOAD

#         elif self.packet_state == MBusPacketReaderState.STATE_PALOAD:
            
#             length = self.buffer[0]
#             # If we've got to this stage then we can assign the payload
#             self.packet_temp = MBusPacket(raw=self.buffer[0:length])

#             # Skip length of buffer
#             self.skip(self.buffer[0])

#             if self.buffer_length == 0:
#                 self.packet_state = MBusPacketReaderState.STATE_WAITING
#             else:
#                 self.packet_state = MBusPacketReaderState.STATE_LENGTH

#             raise StopIteration

#         # By default return nothing
#         return None
        
#     def skip(self, to_skip):
            
#         if to_skip > len(self.buffer):
#             raise ValueError("Cannot skip more than buffer length")

#         self.buffer = self.buffer[to_skip:]
#         self.buffer_length = len(self.buffer)

#         if self.buffer_length == 0:
#             self.packet_state = MBusPacketReaderState.STATE_WAITING
#         else:
#             self.packet_state = MBusPacketReaderState.STATE_LENGTH