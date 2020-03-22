"""
Tests of the encode_data moduel and end-to-end tests.
"""
import pytest
import os
import pandas as pd
from tempfile import NamedTemporaryFile

# Relative imports
from src import sample_data, packet_map, encode_data, decode_data, lib


@pytest.fixture()
def sample_df():
    """Returns dataframe of data; should match data in `assets/data.unk`."""
    return pd.DataFrame(data={
        "dpt": [1, 2],
        "cyc": [1, 1],
        "stp": [1, 2],
        "cur": [1.0, 0.0],
        "pot": [2.0, 3.0],
        "time": [0.5, 1.0],
        "start": [170, 170],
    })


def test_encode_data(sample_df):
    """Test the encode_data method."""
    tmp = NamedTemporaryFile()

    encode_data.encode_data(tmp.name, sample_df, encode_data.DT)

    total_bytes = lib.get_filesize(tmp.name)
    with open(tmp.name, "rb") as f:
        f.seek(total_bytes - 21)
        packet = f.read(21)

    # Check that the last 4 bytes are the potential * 1000 = 3000
    assert packet[-4:] == b'\xb8\x0b\x00\x00'

    # Check that the 1-4th bytes are 2
    assert packet[1:5] == b'\x02\x00\x00\x00'


def test_encode_data__end_to_end():
    """Tests that `sample.unk` is the result of encoding `sample.csv`."""
    df = sample_data.create_data()

    tmp = NamedTemporaryFile()

    encode_data.encode_data(tmp.name, df, start_time=encode_data.DT)

    # Decode the data, too, and make sure it matches.
    decoder = decode_data.DataDecoder(tmp.name, starting_bytes=[1], dtypes=["uint8le"], knowns=packet_map.PACKET_MAP)

    decoded_df = decoder.decode_knowns()

    assert set(df.columns) == set(decoded_df.columns)
    assert (df[decoded_df.columns] == decoded_df).all().all()
