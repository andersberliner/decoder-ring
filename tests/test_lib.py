"""
Tests of the src.lib module.
"""
import numpy as np
import pytest

# Relative imports
from src import lib


# fmt: off
@pytest.mark.parametrize(
    "dtype,expected",
    [
        ("uint8le", 1),
        ("int32be", 4),
        ("f64le", 8),
        ("bool", 1),
    ]
)
def test_get_nbytes(dtype, expected):
    """Tests the get_nbytes method."""
    assert lib.get_nbytes(dtype) == expected


# fmt: on


def test_get_nbytes__bad_dtype():
    """Tests the get_nbytes method raises an error when invalid dtype is used."""
    with pytest.raises(lib.DecoderRingError):
        _ = lib.get_nbytes("junk")
        assert False, "DecoderRingError should have been raised."


# fmt: off
@pytest.mark.parametrize(
    "byte_list,dtype,expected",
    [
        (
            b'\x1d',
            "uint8le",
            29
        ),
        (
            b'\x1d\x00',
            "uint16le",
            29
        ),
        (
            b'\x00\x1d',
            "uint16be",
            29
        ),
        (
            b'\xff\xff',
            "uint16le",
            65535
        ),
        (
            b'\xff\xff',
            "int16le",
            -1
        ),
    ]
)
def test_cast_from_bytes(byte_list, dtype, expected):
    """Tests the cast_from_bytes method."""
    assert lib.cast_from_bytes(byte_list, dtype) == expected

# fmt: on


def test_cast_from_bytes__bad_dtype():
    """Tests the cast_from_bytes method raises an error when invalid dtype is used."""
    with pytest.raises(lib.DecoderRingError):
        _ = lib.cast_from_bytes(None, "junk")
        assert False, "DecoderRingError should have been raised."


# fmt: off
@pytest.mark.parametrize(
    "data,dtype,expected",
    [
        (
            29,
            "uint8le",
            b'\x1d'
        ),
        (
            29,
            "uint16le",
            b'\x1d\x00'
        ),
        (
            29,
            "uint16be",
            b'\x00\x1d'
        ),
        (
            65535,
            "uint16le",
            b'\xff\xff'
        ),
        (
            -1,
            "int16le",
            b'\xff\xff'
        ),
    ]
)
def test_cast_to_bytes(data, dtype, expected):
    """Tests the cast_to_bytes method."""
    assert lib.cast_to_bytes(data, dtype) == expected


# fmt: on


def test_cast_to_bytes__bad_dtype():
    """Tests the cast_from_bytes method raises an error when invalid dtype is used."""
    with pytest.raises(lib.DecoderRingError):
        _ = lib.cast_to_bytes(None, "junk")
        assert False, "DecoderRingError should have been raised."
