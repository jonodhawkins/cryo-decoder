Decide not to include length in any of the packet specifications - always treat this as an 'extra bit' in the beginning (because the length does also not include itself)

Makes sense that the workflow/use of the decoder is as follows:

1. Create PacketReader with File/byte stream/serial
2. Get *Packet objects
3. Convert *Packet objects to *Data objects based on sensor settings (i.e. pressure sensor)