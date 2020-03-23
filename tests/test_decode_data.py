"""
Tests of the decode_data module.

See the end-to-end test in test_encode_data.
"""
import pytest
from collections import namedtuple

from src import decode_data


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


@pytest.mark.skip("TODO")
def test_data_decoder_init():
    """Test the init of the DataDecoder class."""
    pass


@pytest.mark.skip("TODO")
def test_decode_byte_idx():
    """Tests the decode_byte_idx method of the DataDecoder class."""
    pass


@pytest.mark.skip("TODO")
def test_decode_knowns():
    """Tests the decode_knowns of the DataDecoder class."""
    pass


@pytest.mark.skip("TODO")
def test_seed_data():
    """Tests the seed_data method."""
    pass


@pytest.mark.skip("TODO")
def test_view_byte_idx():
    """Tests the view_byte_idx method."""
    pass


@pytest.mark.skip("TODO")
def test_view_dtypes():
    """Tests the view_dtypes method."""
    pass


@pytest.mark.skip("TODO")
def test_decode_packet():
    """Tests the decode_packet method."""
    pass


@pytest.mark.skip("TODO")
def test_fill_known_bytes():
    """Tests the fill_known_bytes method."""
    pass


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
