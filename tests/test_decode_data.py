"""
Tests of the decode_data module.

See the end-to-end test in test_encode_data.
"""
import os
import pandas as pd
import numpy as np
import pytest
from collections import namedtuple

from src import decode_data, packet_map


SampleFile = namedtuple("SampleFile", ["filesize", "ndpts",
        "starting_bytes", "dtypes", "seed_df", "sample_bytes", "packet_length",
        "dpt_index", "knowns"])


@pytest.fixture()
def sample_file():
    """Returns a fixture containing small number of sample bytes and params for decoding."""
    header_str = "debug.unk \n"

    sample_bytes = (
        # Header bytes - debug.unk \n\xaa\xaa\x01
        bytes(header_str, encoding="utf-8") + packet_map.START_BYTES +
        # Datapoint 1: 1 (8bit), 2 (16bit), 3 (32bit)
        b'\x01\x02\x00\x03\x00\x00\x00'
        # Datapoint 2: 2 (8bit), 3 (16bit), 4 (32bit)
        b'\x02\x03\x00\x04\x00\x00\x00'
        # Datapoint 3: 3 (8bit), 4 (16bit), 5 (32bit)
        b'\x03\x04\x00\x05\x00\x00\x00'
    )

    knowns = None

    seed_df = pd.DataFrame(
        data=[
            # "sbyte", "dtype", "n", "idx", "val", "label"
            (0, "uint8le", 3, 0, 1, "-"),
            (0, "uint8le", 3, 1, 2, "-"),
            (0, "uint8le", 3, 2, 0, "-"),
            (0, "uint8le", 3, 3, 3, "-"),
            (0, "uint8le", 3, 4, 0, "-"),
            (0, "uint8le", 3, 5, 0, "-"),
            (0, "uint8le", 3, 6, 0, "-"),
            (1, "uint8le", 3, 0, "", ""),
            (1, "uint8le", 3, 1, 2, "-"),
            (1, "uint8le", 3, 2, 0, "-"),
            (1, "uint8le", 3, 3, 3, "-"),
            (1, "uint8le", 3, 4, 0, "-"),
            (1, "uint8le", 3, 5, 0, "-"),
            (1, "uint8le", 3, 6, 0, "-"),
            (0, "uint16le", 3, 0, 513, "-"),
            (0, "uint16le", 3, 1, "-", ""),
            (0, "uint16le", 3, 2, 768, "-"),
            (0, "uint16le", 3, 3, "-", ""),
            (0, "uint16le", 3, 4, 0, "-"),
            (0, "uint16le", 3, 5, "-", ""),
            (0, "uint16le", 3, 6, "", "-"),
            (0, "uint16le", 3, 7, "-", ""),
            (1, "uint16le", 3, 0, "", ""),
            (1, "uint16le", 3, 1, 2, "-"),
            (1, "uint16le", 3, 2, "-", ""),
            (1, "uint16le", 3, 3, 3, "-"),
            (1, "uint16le", 3, 4, "-", ""),
            (1, "uint16le", 3, 5, 0, "-"),
            (1, "uint16le", 3, 6, "-", ""),
            (0, "uint16be", 3, 0, 258, "-"),
            (0, "uint16be", 3, 1, "-", ""),
            (0, "uint16be", 3, 2, 3, "-"),
            (0, "uint16be", 3, 3, "-", ""),
            (0, "uint16be", 3, 4, 0, "-"),
            (0, "uint16be", 3, 5, "-", ""),
            (0, "uint16be", 3, 6, "", "-"),
            (0, "uint16be", 3, 7, "-", ""),
            (1, "uint16be", 3, 0, "", ""),
            (1, "uint16be", 3, 1, 512, "-"),
            (1, "uint16be", 3, 2, "-", ""),
            (1, "uint16be", 3, 3, 768, "-"),
            (1, "uint16be", 3, 4, "-", ""),
            (1, "uint16be", 3, 5, 0, "-"),
            (1, "uint16be", 3, 6, "-", ""),
            (0, "uint32le", 3, 0, 50332161, "-"),
            (0, "uint32le", 3, 1, "-", ""),
            (0, "uint32le", 3, 2, "-", ""),
            (0, "uint32le", 3, 3, "-", ""),
            (0, "uint32le", 3, 4, "", "-"),
            (0, "uint32le", 3, 5, "-", ""),
            (0, "uint32le", 3, 6, "-", ""),
            (0, "uint32le", 3, 7, "-", ""),
            (1, "uint32le", 3, 0, "", ""),
            (1, "uint32le", 3, 1, 196610, "-"),
            (1, "uint32le", 3, 2, "-", ""),
            (1, "uint32le", 3, 3, "-", ""),
            (1, "uint32le", 3, 4, "-", ""),
            (1, "uint32le", 3, 5, "", "-"),
            (1, "uint32le", 3, 6, "-", ""),
            (1, "uint32le", 3, 7, "-", ""),
            (1, "uint32le", 3, 8, "-", ""),
            (0, "uint8le", 2, 0, 2, "-"),
            (0, "uint8le", 2, 1, 3, "-"),
            (0, "uint8le", 2, 2, 0, "-"),
            (0, "uint8le", 2, 3, 4, "-"),
            (0, "uint8le", 2, 4, 0, "-"),
            (0, "uint8le", 2, 5, 0, "-"),
            (0, "uint8le", 2, 6, 0, "-"),
            (1, "uint8le", 2, 0, "", ""),
            (1, "uint8le", 2, 1, 3, "-"),
            (1, "uint8le", 2, 2, 0, "-"),
            (1, "uint8le", 2, 3, 4, "-"),
            (1, "uint8le", 2, 4, 0, "-"),
            (1, "uint8le", 2, 5, 0, "-"),
            (1, "uint8le", 2, 6, 0, "-"),
            (0, "uint16le", 2, 0, 770, "-"),
            (0, "uint16le", 2, 1, "-", ""),
            (0, "uint16le", 2, 2, 1024, "-"),
            (0, "uint16le", 2, 3, "-", ""),
            (0, "uint16le", 2, 4, 0, "-"),
            (0, "uint16le", 2, 5, "-", ""),
            (0, "uint16le", 2, 6, "", "-"),
            (0, "uint16le", 2, 7, "-", ""),
            (1, "uint16le", 2, 0, "", ""),
            (1, "uint16le", 2, 1, 3, "-"),
            (1, "uint16le", 2, 2, "-", ""),
            (1, "uint16le", 2, 3, 4, "-"),
            (1, "uint16le", 2, 4, "-", ""),
            (1, "uint16le", 2, 5, 0, "-"),
            (1, "uint16le", 2, 6, "-", ""),
            (0, "uint16be", 2, 0, 515, "-"),
            (0, "uint16be", 2, 1, "-", ""),
            (0, "uint16be", 2, 2, 4, "-"),
            (0, "uint16be", 2, 3, "-", ""),
            (0, "uint16be", 2, 4, 0, "-"),
            (0, "uint16be", 2, 5, "-", ""),
            (0, "uint16be", 2, 6, "", "-"),
            (0, "uint16be", 2, 7, "-", ""),
            (1, "uint16be", 2, 0, "", ""),
            (1, "uint16be", 2, 1, 768, "-"),
            (1, "uint16be", 2, 2, "-", ""),
            (1, "uint16be", 2, 3, 1024, "-"),
            (1, "uint16be", 2, 4, "-", ""),
            (1, "uint16be", 2, 5, 0, "-"),
            (1, "uint16be", 2, 6, "-", ""),
            (0, "uint32le", 2, 0, 67109634, "-"),
            (0, "uint32le", 2, 1, "-", ""),
            (0, "uint32le", 2, 2, "-", ""),
            (0, "uint32le", 2, 3, "-", ""),
            (0, "uint32le", 2, 4, "", "-"),
            (0, "uint32le", 2, 5, "-", ""),
            (0, "uint32le", 2, 6, "-", ""),
            (0, "uint32le", 2, 7, "-", ""),
            (1, "uint32le", 2, 0, "", ""),
            (1, "uint32le", 2, 1, 262147, "-"),
            (1, "uint32le", 2, 2, "-", ""),
            (1, "uint32le", 2, 3, "-", ""),
            (1, "uint32le", 2, 4, "-", ""),
            (1, "uint32le", 2, 5, "", "-"),
            (1, "uint32le", 2, 6, "-", ""),
            (1, "uint32le", 2, 7, "-", ""),
            (1, "uint32le", 2, 8, "-", ""),
            (0, "uint8le", 1, 0, 3, "-"),
            (0, "uint8le", 1, 1, 4, "-"),
            (0, "uint8le", 1, 2, 0, "-"),
            (0, "uint8le", 1, 3, 5, "-"),
            (0, "uint8le", 1, 4, 0, "-"),
            (0, "uint8le", 1, 5, 0, "-"),
            (0, "uint8le", 1, 6, 0, "-"),
            (1, "uint8le", 1, 0, "", ""),
            (1, "uint8le", 1, 1, 4, "-"),
            (1, "uint8le", 1, 2, 0, "-"),
            (1, "uint8le", 1, 3, 5, "-"),
            (1, "uint8le", 1, 4, 0, "-"),
            (1, "uint8le", 1, 5, 0, "-"),
            (1, "uint8le", 1, 6, 0, "-"),
            (0, "uint16le", 1, 0, 1027, "-"),
            (0, "uint16le", 1, 1, "-", ""),
            (0, "uint16le", 1, 2, 1280, "-"),
            (0, "uint16le", 1, 3, "-", ""),
            (0, "uint16le", 1, 4, 0, "-"),
            (0, "uint16le", 1, 5, "-", ""),
            (0, "uint16le", 1, 6, "", "-"),
            (0, "uint16le", 1, 7, "-", ""),
            (1, "uint16le", 1, 0, "", ""),
            (1, "uint16le", 1, 1, 4, "-"),
            (1, "uint16le", 1, 2, "-", ""),
            (1, "uint16le", 1, 3, 5, "-"),
            (1, "uint16le", 1, 4, "-", ""),
            (1, "uint16le", 1, 5, 0, "-"),
            (1, "uint16le", 1, 6, "-", ""),
            (0, "uint16be", 1, 0, 772, "-"),
            (0, "uint16be", 1, 1, "-", ""),
            (0, "uint16be", 1, 2, 5, "-"),
            (0, "uint16be", 1, 3, "-", ""),
            (0, "uint16be", 1, 4, 0, "-"),
            (0, "uint16be", 1, 5, "-", ""),
            (0, "uint16be", 1, 6, "", "-"),
            (0, "uint16be", 1, 7, "-", ""),
            (1, "uint16be", 1, 0, "", ""),
            (1, "uint16be", 1, 1, 1024, "-"),
            (1, "uint16be", 1, 2, "-", ""),
            (1, "uint16be", 1, 3, 1280, "-"),
            (1, "uint16be", 1, 4, "-", ""),
            (1, "uint16be", 1, 5, 0, "-"),
            (1, "uint16be", 1, 6, "-", ""),
            (0, "uint32le", 1, 0, 83887107, "-"),
            (0, "uint32le", 1, 1, "-", ""),
            (0, "uint32le", 1, 2, "-", ""),
            (0, "uint32le", 1, 3, "-", ""),
            (0, "uint32le", 1, 4, "", "-"),
            (0, "uint32le", 1, 5, "-", ""),
            (0, "uint32le", 1, 6, "-", ""),
            (0, "uint32le", 1, 7, "-", ""),
            (1, "uint32le", 1, 0, "", ""),
            (1, "uint32le", 1, 1, 327684, "-"),
            (1, "uint32le", 1, 2, "-", ""),
            (1, "uint32le", 1, 3, "-", ""),
            (1, "uint32le", 1, 4, "-", ""),
            (1, "uint32le", 1, 5, "", "-"),
            (1, "uint32le", 1, 6, "-", ""),
            (1, "uint32le", 1, 7, "-", ""),
            (1, "uint32le", 1, 8, "-", ""),
        ],
        columns=["sbyte", "dtype", "n", "idx", "val", "label"],
    ).set_index(["sbyte", "dtype", "n", "idx"])

    ndpts = 3
    starting_bytes = [0, 1]
    dtypes = ["uint8le", "uint16le", "uint16be", "uint32le"]

    return SampleFile(
        filesize=35,
        ndpts=ndpts,
        starting_bytes=starting_bytes,
        seed_df=seed_df,
        dtypes=dtypes,
        sample_bytes=sample_bytes,
        packet_length=7,
        dpt_index=0,
        knowns=knowns,
    )


@pytest.fixture()
def temp_file(sample_file, tmp_path):
    """Stores the data of sample_file in a temporary file.

    Notes
    -----
    `tmp_path` is a built-in pytest fixture.  Scoped to a session, it creates a
    temporary directory for storage and cleans it up after a test session.
    """
    tmp = os.path.join(tmp_path.as_posix(), "tmp.unk")

    with open(tmp, "wb") as f:
        f.write(sample_file.sample_bytes)

    return tmp


@pytest.fixture()
def sample_decoder(sample_file, temp_file):
    """Returns a sample data_decoder object."""
    return decode_data.DataDecoder(
        filepath=temp_file,
        ndpts=sample_file.ndpts,
        dtypes=sample_file.dtypes,
        starting_bytes=sample_file.starting_bytes,
        packet_length=sample_file.packet_length,
        knowns=sample_file.knowns,
        dpt_index=0,
    )


@pytest.fixture()
def sample_knowns():
    """Returns a dictionary that can serve as sample knowns for these tests."""
    return {
    0: {
        "dtype": "uint8le",
        "label": "start",
    },
    1: {
        "dtype": "uint32le",
        "label": "dpt",
    },
    13: {
        "dtype": "int32le",
        "label": "cur",
        "factor": 1000 * 100, # 0.01 mA precision
    },
}


ByteIdxLists = namedtuple("ByteIdxLists", ["starting_byte", "nbytes",
        "packet_length", "known_bytes", "first_bytes", "wasted_bytes",
        "filled_bytes"])


@pytest.fixture()
def byte_idx_lists(sample_knowns):
    """Returns a fixture for tests of all the byte-idx methods."""
    return ByteIdxLists(
        starting_byte=0,
        nbytes=4,
        packet_length=18,
        known_bytes=[0, 1, 2, 3, 4, 13, 14, 15, 16],
        first_bytes=[0, 4, 8, 12, 16],
        wasted_bytes=[5, 6, 7, 12, 17],
        filled_bytes=[8, 9, 10, 11],
    )


@pytest.fixture()
def sample_bytes():
    """Returns a byte str of sample bytes for use in decoding data.

    Sample bytes are 1 12 -123 in 8, 16 and 32 bit, little endian integers.
    """
    return (
        b'\x01' # 1
        b'\x0c\x00' # 12
        b'\x85\xff\xff\xff' # -123
    )


def test_data_decoder_init(sample_file, temp_file, sample_decoder):
    """Test the init of the DataDecoder class."""

    # Check that all expected class attributes are populated
    assert sample_decoder._packet_length == sample_file.packet_length
    assert sample_decoder._knowns == {}
    assert sample_decoder._dpt_idx == sample_file.dpt_index
    assert sample_decoder._filepath == temp_file
    assert sample_decoder._total_bytes == sample_file.filesize

    # Affirm columns and values are as expected (for seeded df)
    assert set(sample_decoder._seed_df.columns) == set(sample_file.seed_df.columns)
    assert (sample_decoder._seed_df[sample_file.seed_df.columns] ==
            sample_file.seed_df).all().all()

    assert sample_decoder._knowns == {}


def test_decode_byte_idx(sample_file, temp_file, sample_decoder):
    """Tests the decode_byte_idx method of the DataDecoder class."""
    actual = sample_decoder.decode_byte_idx(byte_idx=1, dtype="uint16le", dpts=3)

    assert (actual == np.array([2, 3, 4])).all()


def test_decode_knowns(sample_file, temp_file, sample_decoder):
    """Tests the decode_knowns of the DataDecoder class."""
    # Reset knowns to something.
    sample_decoder._knowns = {0: {"label": "dpt", "dtype": "uint8le"}}
    sample_decoder._known_labels = {"dpt": 0}

    expected = pd.DataFrame(data={"dpt": [1, 2, 3]})
    actual = sample_decoder.decode_knowns(dpts=3)

    assert (expected == actual).all().all()


def test_seed_data(sample_file, temp_file):
    """Tests the seed_data method."""

    actual = decode_data.seed_data(
        temp_file,
        ndpts=sample_file.ndpts,
        dtypes=sample_file.dtypes,
        starting_bytes=sample_file.starting_bytes,
        packet_length=sample_file.packet_length,
        knowns=None,
    )

    # Affirm columns and values are as expected
    assert set(actual.columns) == set(sample_file.seed_df.columns)
    assert (sample_file.seed_df[actual.columns] == actual).all().all()


def test_view_byte_idx(sample_file, temp_file):
    """Tests the view_byte_idx method."""
    expected = pd.DataFrame(
        data=[
            (3, 2, 512),
            (2, 3, 768),
            (1, 4, 1024),
        ],
        columns=["n", "uint8le", "uint16be"]
    ).set_index("n")

    expected.columns.name = "dtype"

    actual = decode_data.view_byte_idx(sample_file.seed_df, 1, 1,
            dtypes=["uint8le", "uint16be"])

    assert (expected == actual).all().all()


def test_view_dtypes(sample_file, temp_file):
    """Tests the view_dtypes method."""
    expected = pd.DataFrame(
        data=[
            [0, "", "", "", "", "", "", "", "", "", ""],
            [1, "-", 2, 3, 4, 2, 3, 4, 512, 768, 1024],
            [2, "-", 0, 0, 0, "-", "-", "-", "-", "-", "-"],
            [3, "-", 3, 4, 5, 3, 4, 5, 768, 1024, 1280],
            [4, "-", 0, 0, 0, "-", "-", "-", "-", "-", "-"],
            [5, "-", 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [6, "-", 0, 0, 0, "-", "-", "-", "-", "-", "-"],
        ],
        columns=[
            "idx",
            "label",
            "uint8le-3",
            "uint8le-2",
            "uint8le-1",
            "uint16le-3",
            "uint16le-2",
            "uint16le-1",
            "uint16be-3",
            "uint16be-2",
            "uint16be-1",
        ],
    ).set_index("idx")

    actual = decode_data.view_dtypes(sample_file.seed_df, 1,
            ["uint8le", "uint16le", "uint16be"])

    assert (actual == expected).all().all()


def test_decode_packet(sample_file, temp_file):
    """Tests the decode_packet method."""
    expected = {
        0: {"val": 3, "label": "-"},
        1: {"val": 4, "label": "-"},
        2: {"val": 0, "label": "-"},
        3: {"val": 5, "label": "-"},
        4: {"val": 0, "label": "-"},
        5: {"val": 0, "label": "-"},
        6: {"val": 0, "label": "-"},
    }

    actual = decode_data.decode_packet(
        sample_file.sample_bytes[-7:],
        "uint8le",
        0,
        packet_length=sample_file.packet_length,
        knowns=None
    )

    assert actual == expected


def test_fill_known_bytes(sample_file, temp_file):
    """Tests the fill_known_bytes method."""
    expected = {
        0: {"val": 3, "label": "dpt"},
        1: {"val": 4, "label": "cur"},
        2: {"val": ".", "label": "cur"},
        3: {"val": None, "label": None},
        4: {"val": None, "label": None},
        5: {"val": None, "label": None},
        6: {"val": None, "label": None},
    }

    actual = decode_data.fill_known_bytes(
        sample_file.sample_bytes[-sample_file.packet_length:],
        {
            0: {"label": "dpt", "dtype": "uint8le"},
            1: {"label": "cur", "dtype": "uint16le"},
        },
        packet_length=sample_file.packet_length
    )

    assert actual == expected


def test_get_known_bytes(sample_knowns, byte_idx_lists):
    """Tests the _get_known_bytes method."""
    assert decode_data._get_known_bytes(
        sample_knowns,
        byte_idx_lists.packet_length
    ) == byte_idx_lists.known_bytes


def test_get_wasted_bytes(sample_knowns, byte_idx_lists):
    """Tests the _get_wasted_bytes method."""
    assert decode_data._get_wasted_bytes(
        byte_idx_lists.starting_byte,
        byte_idx_lists.nbytes,
        sample_knowns,
        packet_length=byte_idx_lists.packet_length,
        known_bytes=byte_idx_lists.known_bytes,
        first_bytes=byte_idx_lists.first_bytes
    ) == byte_idx_lists.wasted_bytes


def test_get_filled_bytes(sample_knowns, byte_idx_lists):
    """Tests the _get_filled_bytes method."""
    assert decode_data._get_filled_bytes(
        byte_idx_lists.starting_byte,
        byte_idx_lists.nbytes,
        sample_knowns,
        packet_length=byte_idx_lists.packet_length,
        known_bytes=byte_idx_lists.known_bytes,
        first_bytes=byte_idx_lists.first_bytes,
        wasted_bytes=byte_idx_lists.wasted_bytes,
    ) == byte_idx_lists.filled_bytes


def test_get_first_bytes():
    """Tests the _get_first_bytes method."""
    assert decode_data._get_first_bytes(0, 3, packet_length=10) == [0, 3, 6, 9]


@pytest.mark.filterwarnings("ignore:This method is deprecated")
def test_get_packet(sample_bytes):
    """Tests the get_packet method."""
    assert decode_data.get_packet(sample_bytes, 1, packet_length=2) == sample_bytes[-2:]


@pytest.mark.parametrize(
    "byte_idx,dtype,expected",
    [
        (0, "int8le", 1),
        (1, "int16le", 12),
        (3, "int32le", -123),
    ]
)
def test_decode_bytes(byte_idx, dtype, expected, sample_bytes):
    """Tests the decode_bytes method."""
    assert decode_data.decode_bytes(sample_bytes, byte_idx, dtype) == expected
