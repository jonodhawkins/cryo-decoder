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

# Syntax for `packets.toml`

## `Packet` object
Packets are used to describe the fields within a byte array so that it can be parsed.
There are defined in the TOML file as top-level tables (i.e. `[MyPacket]`).
They should each be associated with a Python class of the same name, which extends the `cryodecoder.Packet` class.

### Parameters 
Parameters of the packet object describe the packet and settings to be used by the parser:

* `description` [`str`] - a brief description of the packet
* `contains` [`array` of `str`] - an array of valid sub-packet names that may be contained within the packet 
* `length` [`int`, or `array` of `int`] - valid packet length(s). 

Default values for the parameters are given in the table below:

| Parameter Name | Value | Description                              |
| -------------- | ----- | ---------------------------------------- |
| `description`  | ""    | Empty if not provided                    |
| `contains`     | []    | Implies there are no sub-packets         |
| `length`       | None  | Implies the packet has no maximum-length |

An example of the packet parameters is given below, for a packet that has a valid length of 10-bytes and contains a `MySubPacket` within it.
```toml
[MyPacket]
description = "my new packet type"
contains = ["MySubPacket"]
length = 10
```


## `Packet` fields
Fields of the packet object are defined as TOML sub-tables (i.e. `[MyPacket.my_field]`).

### Parameters
Each field can describe the following parameters:

* `description` [`str`] - a brief description of the field
* `offset` [`int`, or `array` of `int`] - the (zero-index) offset indicating the start of the field, or a pair of values indicating the first and last byte.  Negative values can be used to describe an offset from the end of the packet (-1 is the last byte, -2 the second last, etc.).
* `length` [`int`] - the number of bytes occupied by the field. Not used if a pair of values is given in the `offset` field.
* `signed` [`bool`] - "true" if the numeric field is signed, or "false" if unsigned.
* `endianness` [`str`] - "big" or "little" depending or whether the format of a multi-byte field is and integer and big or little endian.
* `parser` [`str`] - the name of the Python method (a member of the corresponding packet class) to be used when parsing the field value.
* `output_type` - not sure this is actually needed, would be better to replace with a more generic type field which describes the data.

Default values for the fields are given in the table below.

| Parameter Name | Value    | Description                                                                                            |
| -------------- | -------- | ------------------------------------------------------------------------------------------------------ |
| `description`  | ""       | No descripition |
| `offset`       | None     | No meaning - all fields must have a unique offset                                                      |
| `length`       | None     | If 'None', the length must be determined  by two offset values                                         |
| `signed`       | False    | Assumes all integers are unsigned unless otherwise specified                                           |
| `endianness`   | "little" | Assumes all integers are little-endian unless otherwise specified (matching SAMD21 micro-controllers). |
| `parser`       | None     | Invalid if parser is None, an exception will be raised.                                                |

Default values for each `Packet` object can be specified by defining the reserved `defaults` field. For example, the below sets default values for all fields to be signed and big-endian if they are integer types:

```toml
[MyPacket]
[MyPacket.defaults]
signed = True
endianness = "big"
[MyPacket.a_field]
description = "a simple, big endian, signed, field"
[MyPacket.b_field]
signed = False
description = "another simple, big endian, UNSIGNED field"
```

# TODO
- Add packet metadata (i.e. description, valid lengths etc.)
- Add description to field parameters
- rewrite default values to be read from a subtable of each packet objects
