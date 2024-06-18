import cryodecoder

import argparse
import datetime
import pathlib
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

        # Create empty list of loggers to be used
        self.__loggers = list()

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

            # Read packet length - first checking if any bytes are available
            # otherwise we risk getting stuck here when trying to stop the thread
            if self.serial.in_waiting > 0:
                packet_length = self.serial.read(size = 1)
                
                # Determine packet type based off length
                (time, packet) = self.read_packet(packet_length)

                # Iterate over loggers
                for logger in self.__loggers:
                    logger.log(time, packet)

    def add_logger(self, logger):
        self.__loggers.append(logger)
        
    def read_packet(self, packet_length):

        packet_rx_time = datetime.datetime.now(tz = datetime.UTC)

        bytes = self.serial.read(size = int.from_bytes(packet_length))
        
        # Assign default packet to None
        packet = None

        for packet_type in self.valid_packet_types:

            try:
                packet = packet_type(bytes)
                # TODO: implement logic to determine which packets to send, or whether to log all possible ones
                return (packet_rx_time, packet)
            except (cryodecoder.InvalidPacketError, ValueError):
                pass # move on to 

        if packet == None:
            pass # TODO: add action for logging raw data

    def add_logger(self, logger):

        self.__loggers.append(logger)

    def stop(self):
        
        self.alive = False
        # close the serial connection
        self.serial.close()

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
    parser.add_argument("--echo", type=bool, required=False, default=True)
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
        
        with PacketCSVLogger(args.logfile, echo=args.echo) as logger:

            # Assign logger as an output for the decoder
            # - this means that any packet the decoder produces is sent to the logger
            decoder.add_logger(logger)
            # begin the decoder
            decoder.start()

            # as the serial decoder runs in a thread, we just wait until we hit a KeyboardInterrupt
            # - in theory, could start to add some logic here
            while True:
                pass

    except KeyboardInterrupt:
        decoder.stop()
        exit()
        

class PacketCSVLogger:

    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f%z"

    def __init__(self, file_path, echo=True):

        self.file_path = pathlib.Path(file_path)
        self.echo_flag = echo

    def echo(self, msg):
        if self.echo_flag:
            print(msg)

    def __enter__(self):

        write_header = False

        # Create file if it doesn't exist
        if not self.file_path.parent.exists():
            self.echo(f"Making parent directory: {self.file_path.parent}")
            self.file_path.parent.mkdir(parents=True)

        if not self.file_path.exists():
            # Write header
            write_header = True

        self.__file_handle = open(self.file_path, 'a+')
        
        # If we've just created the file, write the header
        if write_header:
            self.echo(f"Writing header...");
            self.write_header()

        self.echo(f"Opening log file: {self.file_path}")
        
        return self
    
    def __exit__(self, _, __, ___):

        self.echo("Closing log file.")
        self.__file_handle.close()

    def write_header(self):

        header = "timestamp,packet_type,packet_length,packet_raw,packet_readable_summary"
        self.__file_handle.write(header + "\n")
        self.__file_handle.flush()
        self.echo(header)
    
    def log(self, time, packet):

        # Create list of fields to write:
        fields_to_write = [
            # Timestamp
            time.strftime(self.TIMESTAMP_FORMAT),
            # Packet type
            packet.__class__.__name__,
            # Packet length
            str(len(packet.raw)),
            # Raw Bytes
            "".join([f"{byte:02x}" for byte in packet.raw]),
            # Readable summary,
            packet.summary() if hasattr(packet, "summary") else "\"\""
        ]

        # Write files 
        self.__file_handle.write(",".join(fields_to_write) + "\n")
        self.__file_handle.flush()
        self.echo(",".join(fields_to_write))