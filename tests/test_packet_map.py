"""
Tests of the packet_map module.
"""
from dateutil.parser import parse
import pytest
from collections import namedtuple
from textwrap import dedent

from src import packet_map

DT_STR = "2020-03-17 10:00:00"


ExpectedHeader = namedtuple("ExpectedHeader", ["version_string", "filename",
        "start_time", "char_limit", "header_str", "header_bytes"])


@pytest.fixture()
def expected_header():
    """Returns header parts and resulting header."""
    header = dedent(
        """
        ABC 123
        dummy.unk
        {}
        """.format(DT_STR)
    ).lstrip()
    header_bytes = b'ABC 123\ndummy.unk\n2020-03-17 10:00:00\n\xaa\xaa\x01'
    return ExpectedHeader(
        version_string="ABC 123",
        filename="dummy.unk",
        start_time=parse(DT_STR),
        char_limit=7,
        header_str=header,
        header_bytes=header_bytes
    )


def test_generate_header_str(expected_header):
    """Tests the _generate_header_str method."""
    assert packet_map._generate_header_str(
        expected_header.version_string,
        expected_header.filename,
        expected_header.start_time,
        char_limit=expected_header.char_limit
    ) == expected_header.header_str


def test_get_header_bytes(expected_header):
    """Test the get_header_bytes method."""
    assert packet_map.get_header_bytes(
        expected_header.filename,
        expected_header.start_time,
        char_limit=expected_header.char_limit,
        start_bytes=packet_map.START_BYTES,
        version_string=expected_header.version_string
    ) == expected_header.header_bytes
