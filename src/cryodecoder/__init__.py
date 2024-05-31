# Lazy import of all for now
from .cryodecoder import *
from .packets import *

from importlib.resources import files, as_file

# Define __all__ to expose public API
# __all__ = []

#
REGISTERED_PACKETS = (
    MBusPacket,
    CryoeggPacket,
    CryowurstPacket,
    HydrobeanPacket
    # CryopolsePacket,
    # CryoeggReceiverPacket
)
PACKET_CONFIG = None
source = files(cryodecoder).joinpath("packets.toml") 
with as_file(source) as packet_config_path:
    # Get config object:
    PACKET_CONFIG = cryodecoder.load_packet_config(packet_config_path)
    # and registor for each packet
    for packet in REGISTERED_PACKETS:
        Packet.configure(packet, PACKET_CONFIG)