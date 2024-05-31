import random

class FakeMBusPacket:

    @staticmethod
    def to_bytes(payload):

        # Total length is given by:
        #
        #   length | 1 byte | 1 byte 
        #   c_field | 1 byte | 2 bytes
        #   m_field | 2 bytes | 4 bytes
        #   id_field | 4 bytes | 8 bytes
        #   version | 1 byte | 9 bytes
        #   dev | 1 byte | 10 bytes
        #   ci_field | 1 byte | 11 bytes
        #   payload | n bytes | 11 + n bytes
        #   rssi | 1 byte | 12 + n bytes
        #   channel | 1 byte | 13 + n bytes
        #   temperature | 1 byte | 14 + n bytes
        #   pressure | 2 bytes | 16 + n bytes
        #   voltage | 2 bytes | 18 + n bytes

        # Create output
        output = bytearray(18 + len(payload))
        
        # Assign length
        output[0] = len(output)
        # Assign c-field
        output[1] = 0x44
        # Assign m-field
        output[2] = 0x48
        output[3] = 0x24
        # Assign user id
        output[4] = 0xCE
        output[5] = 0x24
        output[6] = 0x00
        output[7] = random.randrange(0,100)
        # Assign ver
        output[8] = 0x01
        # Assign dev 
        output[9] = 0x07
        # Assign ci-field
        output[10] = 0x00
        # Assign payload
        output[11:len(payload)] = payload
        # Assign rssi
        output[11+len(payload)] = random.randrange(-127, 30) & 0xff
        # Assign channel
        output[12+len(payload)] = random.randrange(1,3)
        # Assign temperature
        output[13+len(payload)] = random.randrange(0, 256)
        # Assign pressure
        output[14+len(payload)] = random.randrange(0, 256)
        output[15+len(payload)] = random.randrange(0, 256)
        # Assign voltage
        output[16+len(payload)] = random.randrange(0, 256)
        output[17+len(payload)] = random.randrange(0, 256)
        
        return output

if __name__ == "__main__":
    
    with open("test/fake_mbus_packets.bin", 'wb') as fh:

        for k in range(10):
            fh.write(FakeMBusPacket.to_bytes(bytearray()))