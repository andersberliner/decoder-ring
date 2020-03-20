"""
Defines the byte-packet shape and data header.
"""

# Byte-packet definition for each datapoint
PACKET_MAP = {
    0: {
        "dtype": "uint8le",
        "label": "start",
    },
    1: {
        "dtype": "uint32le",
        "label": "dpt",
    },
    5: {
        "dtype": "uint16le",
        "label": "cyc",
    },
    7: {
        "dtype": "uint16le",
        "label": "stp",
    },
    9: {
        "dtype": "uint32le",
        "label": "time",
        "factor": 1000 * 10, # 0.1 ms precision
    },
    13: {
        "dtype": "int32le",
        "label": "cur",
        "factor": 1000 * 100, # 0.01 mA precision
    },
    17: {
        "dtype": "uint32le",
        "label": "pot",
        "factor": 1000, # 1 mV precision
    },
}

# Bytes indicating the end of the header, start of the data
START_BYTES = bytearray([170, 170, 1])

# Characters provided for each header field.
HEADER_CHAR_LIMIT = 25

VERSION = "Acme v1.0"


def _generate_header_str(version_string, filename, start_time,
        char_limit=HEADER_CHAR_LIMIT):
    """Returns header-str for a given file, including test metadata.

    Parameters
    ----------
    version_string : str
        Encoding version number.
    filename : str
        Name of file data is written too.
    start_time : datetime.datetime
        Datetime of first datapoint.
    char_limit : int
        White-space padding of header fields.

    Returns
    -------
    header_str : str
    """
    return "{}\n{}\n{}\n".format(
        version_string.ljust(char_limit),
        filename.ljust(char_limit),
        start_time.strftime("%Y-%m-%d %H:%M:%S").ljust(char_limit)
    )


def get_header_bytes(filename, start_time,
        char_limit=HEADER_CHAR_LIMIT, start_bytes=START_BYTES,
        version_string=VERSION):
    """Returns header-bytes for a given file; encodes test metadata.

    Parameters
    ----------
    filename : str
        Name of file data is written too.
    start_time : datetime.datetime
        Datetime of first datapoint.
    char_limit : int
        White-space padding of header fields.
    start_bytes : bytearray
        List of bytes indicating the end of the header, start of the data.
    version_string : str
        Encoding version number.

    Returns
    -------
    header_bytes : byte str
    """
    return bytes(_generate_header_str(version_string, filename, start_time,
            char_limit=char_limit), encoding="utf-8") + start_bytes
