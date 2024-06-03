# List of CryoDecoder Packet Types
Various types of packet structure to consider 

- Cryoegg, Cryowurst, etc. packets
- MBusPacket
    - Wrapper for Cryoegg, Cryowurst, etc. packets. from Radiocrafts modules
- CryoReceiver packet
    - Wrapper for MBusPacket

## Packet Sizes and Combinations
Various combinations of packets (and subpackets) are listed below, giving a list of unique (for the moment) packet lengths.
In the case that the lengths are not unique, should a packet be decoded:

- as all packets with clashing types, saved to different logs
- kept to a single (pre-defined) packet type?

| ID | Packet Size | Components                                                         |
| -- | ----------- | ------------------------------------------------------------------ |
| 1  | 28          | CryoReceiverPacket (6), MBusPacket (11), CryoeggPacket (11)        |
| 2  | 22          | MBusPacket (11), CryoeggPacket (11)                                |
| 3  | 42          | CryoReceiverPacket (6), MBusPacket (11), CryowurstPacket (25)      |
| 4  | 36          | MBusPacket (11), CryowurstPacket (25)                              |
| 5  | 20          | MBusPacket (11), HydrobeanPacket (9)                               |
| 6  | 40          | SDSatellitePacket(18), MBusPacket (11), CryoeggPacket (11)         |
| 8  | 54          | SDSatellitePacket(18), MBusPacket (11), CryowurstPacket (25)       |

**Note: TODO - add description of SDSatellitePacket below**

## MBusPacket
Minimum size is **11 bytes**, plus the size of the payload. 

| Bytes | Description     | Formatting                             |
| ----- | --------------- | -------------------------------------- |
| 0     | C field         | Integer (1-byte, always 0x44)          |
| 1,2   | Manufacturer ID | Integer (2-bytes, always 0x4824)       |
| 3-6   | User ID         | Integer (4-bytes)                      | 
| 7     | Version         | Integer (1-byte)                       | 
| 8     | Developer       | Integer (1-byte)                       | 
| 9     | Control Info.   | Integer (1-byte, instrument dependent) | 
| 10-?  | Payload         | Bytes (application data)               | 
| -1    | RSSI            | Integer (1-byte, signed)               |

### MBusPacket CI and User ID Field 

| Instrument                           | CI Field | A Field (User ID)  |
| ------------------------------------ | -------- | ------------------ |
| Cryoegg                              | 0xAA     | CE220001 etc.      |
| Cryowurst (with pressure sensor)     | 0xAC     | CF201001 etc.      |
| Cryowurst (without pressure sensor)  | 0xAC     | CF200001 etc.      |
| Ploughmeter                          | 0xAC     | N/A                |
| Hydrobean                            | 0xAB     | CB220001 etc.      |
| Cryopølse                            | 0xAD     | CA220001 etc.      |


## CryoeggPacket (CI: 0xAA, UserID: 0xCE)
Size is **11 bytes**.

| Bytes | Description     | Formatting                       |
| ----- | --------------- | -------------------------------- |
| 0,1   | Conductivity    | Integer (2-bytes, little endian) |
| 2,3   | PT1000 Temp.    | Integer (2-bytes, always 0x0304) |
| 4,5   | Pressure        | Integer (2-bytes, little endian) |
| 6,7   | Temperature     | Integer (2-bytes, little endian) |
| 8,9   | Battery Voltage | Integer (2-bytes, little endian) |
| 10    | Sequence Number | Integer (1-byte)                 |
 
## CryowurstPacket (CI: 0xAC, UserID: 0xCF)
Size is **25 bytes**.

Packet description not include CI field. According to dataformats document (repeated above), Cryowurst should have a CI field of 0xAC.

| Bytes | Description     | Formatting                       |
| ----- | --------------- | -------------------------------- |
| 0,1   | Temperature     | Integer (2-bytes, big endian?)   | 
| 2,3   | Magnetometer X  | Integer (2-bytes, big endian?)   |
| 4,5   | Magnetometer Y  | Integer (2-bytes, big endian?)   |
| 6,7   | Magnetometer Z  | Integer (2-bytes, big endian?)   |
| 8,9   | Tilt Accel. X   | Integer (2-bytes, big endian?)   |
| 10,11 | Tilt Accel. Y   | Integer (2-bytes, big endian?)   |
| 12,13 | Tilt Accel. Z   | Integer (2-bytes, big endian?)   |
| 14,15 | Tilt Pitch X    | Integer (2-bytes, big endian?)   |
| 16,17 | Tilt Roll Y     | Integer (2-bytes, big endian?)   |
| 18,19 | Conductivity    | Integer (2-bytes, big endian?)   |
| 20,21 | Pressure        | Integer (2-bytes, big endian?)   |
| 22,23 | Battery voltage | Integer (2-bytes, big endian?)   |
| 24    | Sequence number | Integer (1-byte)                 |

# HydrobeanPacket (CI: 0xAB, UserID: 0xCB)
Size is **9 bytes**.

| Bytes | Description     | Formatting                       |
| ----- | --------------- | -------------------------------- |
| 0,1   | Conductivity    | Integer (2-bytes, little endian) |
| 2,3   | Pressure        | Integer (2-bytes, little endian) |
| 4,5   | Temperature     | Integer (2-bytes, little endian) |
| 6,7   | Battery voltage | Integer (2-bytes, little endian) |
| 8     | Sequence number | Integer (1-byte)                 |
