import pytest
import cryodecoder
    
def test_import():
    import cryodecoder
    pass
    # TODO: write a proper test...

def test_packetconfig_length():

    assert cryodecoder.CryoeggPacket.MIN_SIZE == 11
    assert cryodecoder.MBusPacket.MIN_SIZE == 11