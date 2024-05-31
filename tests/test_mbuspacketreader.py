import pytest
import cryodecoder

def test_mbuspacketreader_singlepacket():

    pr = cryodecoder.MBusPacketReader("tests/fake_mbus_packets.bin")
    
    with pr:
        
        assert isinstance(pr.read_packet(), cryodecoder.MBusPacket)


def test_mbuspacketreader_mutlipacket():

    pr = cryodecoder.MBusPacketReader("tests/fake_mbus_packets.bin")
    
    with pr:
        
        packet_count = 0
    
        packet = pr.read_packet()
        while packet != None:
            packet_count += 1
            packet = pr.read_packet()
            
        assert packet_count == 10

def test_mbuspacketreader_corruptpacket():

    pr = cryodecoder.MBusPacketReader("tests/corrupt_mbus_packets.bin")
    
    with pr:
        
        packet_count = 0
        error_count = 0

        packet = 0

        while packet != None:
            print(f"P{packet_count} vs E{error_count}")
            try:
                packet = pr.read_packet()
                if packet != None:
                    packet_count += 1
            except cryodecoder.InvalidPacketError as e:
                error_count += 1
                
        assert packet_count == 9
        assert error_count == 1

