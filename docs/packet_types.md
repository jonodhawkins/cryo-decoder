# List of CryoDecoder Packet Types
Various types of packet structure to consider 

- Cryoegg, Cryowurst, etc. packets
- MBusPacket
    - Wrapper for Cryoegg, Cryowurst, etc. packets. from Radiocrafts modules
- CryoReceiver packet
    - Wrapper for MBusPacket

## Packet CI Field 

| Instrument                           | CI Field | A Field (ID)  |
| ------------------------------------ | -------- | ------------- |
| Cryoegg                              | 0xAA     | CE220001 etc. |
| Cryowurst (with pressure sensor)     | 0xAC     | CF201001 etc. |
| Cryowurst (without pressure sensor)  | 0xAC     | CF201001 etc. |
| Ploughmeter                          | 0xAC     | N/A           |
| Hydrobean                            | 0xAB     | CB220001 etc. |
| Cryopølse                            | 0xAD     | CA220001 etc. |


## Cryoegg Packet

| Bytes | Description     | Formatting                       |
| ----- | --------------- | -------------------------------- |
| 0,1   | Conductivity    | Integer (2-bytes, little endian) |
| 2,3   | PT1000 Temp.    | Integer (2-bytes, always 0x0304) |
| 4,5   | Pressure        | Integer (2-bytes, little endian) |
| 6,7   | Temperature     | Integer (2-bytes, little endian) |
| 8,9   | Battery Voltage | Integer (2-bytes, little endian) |
| 10    | Sequence Number | Integer (1-byte)                 |
 
## Cryowurst Packet
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
| 24    | Sequence number | Integer (1-byte, big endian?)    |

Acceleration and gyroscope (X, Y, Z) data are omitted from the Cryowurst packets.

	packet[16] = tilt_data.pitch_x >> 8;
	packet[17] = tilt_data.pitch_x & 0x00FF;
	packet[18] = tilt_data.roll_y >> 8;
	packet[19] = tilt_data.roll_y & 0x00FF;

	/*Conductivity PACKET */
	packet[20] = cond_data.result >> 8;
	packet[21] = cond_data.result & 0x00FF;

	/*Pressure PACKET*/
	packet[22] = pres_data.pressure_result >> 8;
	packet[23] = pres_data.pressure_result & 0x00FF;

	/* Battery voltage */
	packet[24] = battery_mv >> 8;
	packet[25] = battery_mv & 0x00FF;

	/* Sequence number */
	packet[26] = sequence_number;


## MBusPacket


## 

