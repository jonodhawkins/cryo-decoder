import cryodecoder

import argparse
import datetime
import serial
import serial.tools.list_ports
import threading

DEFAULT_LOG_FILE_NAME = "%Y-%m-%d_%H%M%S_cryolog.csv"

class SerialDecoder(threading.Thread):

    def __init__(self, port, baud_rate, valid_packets = None, invalid_packets = None):

        # Threaded setup
        self.alive = True
        threading.Thread.__init__(self)

        # Assign valid packet types
        self.__init_packet_types(valid_packets, invalid_packets)

        # Create serial object
        self.serial = serial.Serial(
            port, 
            baudrate = baud_rate,
            bytesize = serial.EIGHTBITS,
            parity   = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            timeout  = None
        )

        # Create buffer

    def __init_packet_types(self, valid_packets, invalid_packets):
        """
        Sorts lists of valid packets (for the decoder to accept).
        
        By default, the list of valid packets is defined by the packets
        registered by the cryodecoder library.

        Invalid packets will be removed from this list.
        """

        # Assign valid packets
        if valid_packets == None:
            self.valid_packet_types = cryodecoder.REGISTERED_PACKETS
        else:
            # Iterate through valid_packets and check they are Cryo* packets
            for packet_type in valid_packets:
                if not issubclass(packet_type, cryodecoder.Packet):
                    raise TypeError("Valid packet types should be subclasses of Packet")
            # assign packet types
            self.valid_packet_types = valid_packets

        # Convert valid packet types to set so that unique values are removed
        self.valid_packet_types = set(self.valid_packet_types)

        # If there are invalid packets, remove them from the valid packet types
        if invalid_packets != None:
            for packet_type in invalid_packets:
                # Check it's a valid Packet type
                if not issubclass(packet_type, cryodecoder.Packet):
                    raise TypeError("Invalid packet types should be subclasses of Packet")
                if packet_type in self.valid_packet_types:
                    self.valid_packet_types.remove(packet_type)

    def run(self):

        # Quit if we are not in thread mode
        while self.alive:

            # Read packet length
            packet_length = self.serial.read(size = 1)
            
            # Determine packet type based off length
            self.read_packet(packet_length)
        
    def read_packet(self, packet_length):

        packet_rx_time = datetime.datetime.now(tz = datetime.UTC)

        bytes = self.serial.read(size = packet_length)
        


def guess_serial_port():

    # List ports
    ports = serial.tools.list_ports.comports()
    
    # if there is more than one, we can't really pick...
    #   in the future, we could log previous ports and attempt those?
    #   TODO: improve port guessing
    if len(ports) == 0:
        raise Exception("No serial ports available.")
    elif len(ports) == 1:
        return ports[0].name
    else:
        # Create port list
        port_list = ",".join([port.name for port in ports])
        raise Exception(f"Multiple serial ports available ({port_list}), please select one and restart.")

def serial_decoder_add_common_cli_args(parser):

    parser.description = "Log serial data from Cryo* instruments"
    # Add arguments
    parser.add_argument("--port", type=str, required=False, default="")
    parser.add_argument("--baud", type=int, required=False, default=19200)
    parser.add_argument(
        "--logfile", 
        type=str, 
        required=False, 
        # Populate default log file name with current timestamp
        default = datetime.datetime.now(tz=datetime.UTC).strftime(DEFAULT_LOG_FILE_NAME)
    )

def serial_decoder_cli_entry():

    parser = argparse.ArgumentParser()
    # Add common arguments (between GUI/CLI entry methods)
    serial_decoder_add_common_cli_args(parser)
    # add unique arguments for serial below
    args = parser.parse_args()

    # Search for COM port if empty
    serial_port = args.port
    if serial_port == "":
        # this will either raise an exception or return the name of the only 
        # connected port
        serial_port = guess_serial_port()

    try:
        
        decoder = SerialDecoder(serial_port, args.baud)
        
        with PacketCSVLogger(args.logfile) as logger:

            while True:
                packet = decoder.read_packet()
                logger.log(packet)

    except KeyboardInterrupt:
        exit()