import pytest
import cryodecoder
import cryodecoder.file

def test_sd_read():

    cryodecoder.file.read_cryoegg_sd_file("tests/fake_sdsatellite_cryoegg_data.bin")

    pass