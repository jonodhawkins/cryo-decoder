import cryodecoder

import argparse
import datetime
import pathlib

def read_cryoegg_sd_file(input_file, output_file="sd_output.csv", pressure_max=3.0):
    
    # Valid packet size for CryoeggPackets only
    total_size = \
        cryodecoder.SDSatellitePacket.MIN_SIZE + \
        cryodecoder.MBusPacket.MIN_SIZE + \
        cryodecoder.CryoeggPacket.MIN_SIZE;

    # Try to open input file and output file
    with open(input_file, "rb") as input_handle, open(output_file, "w+") as output_handle:

        output_handle.write(",".join((
                "timestamp",
                "channel",
                "temperature_logger",
                "pressure_logger",
                "solar_voltage",
                "rssi",
                "id",
                "sequence_id",
                "temperature",
                "pressure",
                "conductivity",
                "voltage"
        )) + "\n")

        while True:
            # We should know that these are RockBlock/SD output packets?
            data_raw = input_handle.read(total_size)

            if len(data_raw) < total_size:
                print(f"Quitting, no more data")
                break

            # Create SDSatellitePacket
            packet = cryodecoder.SDSatellitePacket(data_raw)

            # Example data
            # b'W1\xb5\xa4\xd7dJ\xbfBA\xfb\r[D\x81\x0c\x01$\x44\x24\x48\x02\x00\x24\xCE\x01\x07\xAA\xAA\x0F\x03\x04\xF2\x3F\xF2\x56\x8C\x0F\x19\x5A'
            
            # Get datalogger data
            timestamp = datetime.datetime.fromtimestamp(packet.timestamp)
            channel = packet.channel
            temperature_logger = packet.temperature_logger
            pressure_logger = packet.pressure_logger
            solar_voltage = packet.solar_voltage
            
            # Get MBusPacket data
            rssi = packet.mbus_packet.rssi
            id = f"{packet.mbus_packet.user_id:x}"

            # Get Cryoegg data
            cryoegg_data = cryodecoder.CryoeggData(
                packet.mbus_packet.payload, 
                pressure_keller_max = pressure_max
            )

            sequence_numbker = cryoegg_data.sequence_number
            temperature = cryoegg_data.temperature
            pressure = cryoegg_data.pressure
            conductivity = cryoegg_data.conductivity
            voltage = cryoegg_data.battery_voltage 

            output_handle.write(
                ",".join((
                    timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    str(channel),
                    f"{temperature_logger:.3f}",
                    f"{pressure_logger:.3f}",
                    f"{solar_voltage:.3f}",
                    f"{rssi:.1f}",
                    id,
                    str(sequence_numbker),
                    f"{temperature:.3f}",
                    f"{pressure:.3f}",
                    f"{conductivity:.3f}",
                    f"{voltage:.3f}"
                )) + "\n"
            )

            

def read_cryoegg_sd_file_cli():
    
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Add arguments
    parser.add_argument("--input", type=str, required=False, default="", help="Path to input file from SD card")
    parser.add_argument("--output", type=str, required=False, default="sd_output.csv", help="Path to ouput CSV file")
    parser.add_argument("--pressure", type=float, required=False, default=3.0, help="Nominal maximum pressure")

    # and parse
    args = parser.parse_args()
    # checking if input file is ready/valid
    if len(args.input) == 0:
        raise ValueError("Input file path should not be empty")
    
    # Store max pressure
    pressure_max = args.pressure
    read_cryoegg_sd_file(args.input, args.output, pressure_max)