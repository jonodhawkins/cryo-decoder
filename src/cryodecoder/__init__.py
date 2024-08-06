# Lazy import of all for now
from .base import *
from .packets import *
from .data import *
from .file import read_cryoegg_sd_file

from importlib.resources import files, as_file

# Define __all__ to expose public API
__all__ = [
    "MBusPacket",
    "CryoeggPacket",
    "CryowurstPacket",
    "HydrobeanPacket",
    "CryoReceiverPacket",
    "SDSatellitePacket",
    #
    "CryoeggData"
]

# List registered packet types
REGISTERED_PACKETS = (
    MBusPacket,
    CryoeggPacket,
    CryowurstPacket,
    HydrobeanPacket,
    # CryopolsePacket,
    CryoReceiverPacket,
    SDSatellitePacket
)

# Load packet config from file and configure each packet type
PACKET_CONFIG = None
source = files(__package__).joinpath("packets.toml") 
with as_file(source) as packet_config_path:
    # Get config object:
    PACKET_CONFIG = load_packet_config(packet_config_path)
    # and registor for each packet
    for packet in REGISTERED_PACKETS:
        Packet.configure(packet, PACKET_CONFIG)