"""
Module to decode byte-stream
"""
import pandas as pd
import numpy as np
from copy import deepcopy

# Relative imports
from .lib import DATA_TYPES, DecoderRingError

# Number of bytes in the packet
PACKET_LENGTH = 21
FILLED_BYTE = "-"
FILLED_KNOWN_BYTE = "."
WASTED_BYTE = "*"

# Portions of the packet map we know thus far
KNOWNS = {
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

def seed_data(filepath, ndpts, dtypes=None, starting_bytes=None, packet_length=PACKET_LENGTH, knowns=KNOWNS):
    """Returns dataframe, indexed by byte position, of each byte interpretted as different data types.

    Parameters
    ----------
    filepath : str
        Path to file to parse
    ndpts : int
        Number of datapoints from the end of the file to parse.
    starting_bytes : list of int or None
        Position to start parsing bytes from
    packet_length : int
        Number of bytes in each packet
    knowns : dict
        Portions of the byte map that are known.  Key is starting byte idx.
        Value is a dict containing, at least:
            "dtype" : str
                Datatype bytes should be parsed as
            "label" : str
                Column label for the data.

    Returns
    -------
    seed_df : pd.DataFrame
    """
    if dtypes is None:
        dtypes = list(DATA_TYPES)

    if starting_bytes is None:
        starting_bytes = range(0, packet_length)

    with open(filepath, "rb") as f:
        byte_stream = f.read()

    data = []

    for n in range(1, ndpts + 1):
        # Select current packet
        packet = get_packet(byte_stream, n, packet_length=packet_length)
        known_data = fill_known_bytes(packet, knowns, packet_length=packet_length)

        for dtype in dtypes:
            nbytes = DATA_TYPES.get(dtype)[0]

            for starting_byte in starting_bytes:
                # Parse values
                tmp_df = pd.DataFrame(seed_data_point(packet, dtype, starting_byte, packet_length, knowns=knowns, known_data=known_data)).T

                # Add labels
                tmp_df["sbit"] = starting_byte
                tmp_df["n"] = n
                tmp_df["dtype"] = dtype

                data.append(tmp_df)

    df = pd.concat(data)
    df.index.name = "foo"

    # The below might provide a higher density view.
    # return pd.DataFrame(data).set_index(["sbit", "n", "dtype"]).fillna("")

    return df


def view_byte_position(seed_df, byte_idx, starting_byte, dtypes):
    """Returns view of byte as position `byte_idx` where packets starting from posn `starting_byte`.

    Parameters
    ----------
    seed_df : pd.DataFrame
        Output of seed_data
    byte_idx : int
        Index of byte to view
    starting_byte : int
        Position bytes where decoded from (in whichever data-type).  Bytes
        before this position are assumed to be "start bytes".
    dtypes : list of str
        Data-types to show decoded values for.

    Returns
    -------
    view_df : pd.DataFrame
    """
    return seed_df.loc[byte_idx][seed_df.loc[byte_idx]["sbit"] == starting_byte]\
            .pivot(index="dtype", columns="n", values="val")\
            .T[dtypes]\
            .sort_index(ascending=False)


def view_byte_positions(seed_df, starting_byte, dtypes):
    pass
    # The following is in progress and may provide a better view.
    # return seed_df.loc[pd.IndexSlice[starting_byte, :, dtypes], :].sort_index(level=["dtype", "n"]).T


def seed_data_point(packet, dtype, starting_byte, packet_length=PACKET_LENGTH, knowns=KNOWNS, known_data=None):

    nbytes, byte_kwargs = DATA_TYPES[dtype]

    if known_data is None:
        data = fill_known_bytes(packet, knowns, packet_length=packet_length)
    else:
        data = deepcopy(known_data)

    # Could just use existing data for this.
    # TODO: optimize
    known_bytes = _get_known_bytes(knowns)
    first_bytes = _get_first_bytes(starting_byte, nbytes, packet_length=packet_length)
    wasted_bytes = _get_wasted_bytes(starting_byte, nbytes, knowns, packet_length=packet_length, known_bytes=known_bytes, first_bytes=first_bytes)
    filled_bytes = _get_filled_bytes(starting_byte, nbytes, knowns, packet_length=packet_length, known_bytes=known_bytes, first_bytes=first_bytes, wasted_bytes=wasted_bytes)

    # Populate filler bytes
    for byte in wasted_bytes:
        data[byte] = {"val": WASTED_BYTE}

    for byte in filled_bytes:
        data[byte] = {"val": FILLED_BYTE}

    # Parse available values
    for byte in first_bytes:
        if byte in filled_bytes:
            data[byte] = {"val": read_bytes(packet, byte, dtype), "label": FILLED_BYTE}

    return data


def fill_known_bytes(packet, knowns, packet_length=PACKET_LENGTH):

    decoded_packet = {i: {"val": None, "label": None} for i in range(packet_length)}

    for i, byte_dict in knowns.items():
        dtype = byte_dict["dtype"]
        label = byte_dict["label"]

        decoded_packet[i] = {"val": read_bytes(packet, i, dtype), "label": label}

        for j in range(i + 1, i + DATA_TYPES[dtype][0]):
            decoded_packet[j] = {"val": FILLED_KNOWN_BYTE, "label": label}

    return decoded_packet



def view_dtypes(seed_df, dtypes, starting_byte):
    """Displays view of seeded data `seed_df` for data types `dtypes'."""
    return seed_df.loc[starting_byte].sort_index(level=["dtype", "n"], ascending=True).T


def _get_known_bytes(knowns, packet_length=PACKET_LENGTH):
    """Returns list of byte indexes containing known values."""
    known_bytes = []

    for known, known_dict in knowns.items():
        nbytes = DATA_TYPES.get(known_dict["dtype"])[0]

        known_bytes.extend(range(known, known + nbytes))

    return known_bytes


def _get_wasted_bytes(starting_byte, nbytes, knowns, packet_length=PACKET_LENGTH, known_bytes=None, first_bytes=None):
    """Returns list of byte indexes that are wasted when filling bytes."""
    wasted_bytes = []
    if known_bytes is None:
        known_bytes = _get_known_bytes(knowns=knowns, packet_length=packet_length)

    if first_bytes is None:
        first_bytes = _get(starting_byte, nbytes, packet_length=packet_length)

    # Find collision with known bytes and/or the end of the packet
    for first_byte in first_bytes:
        bytes_to_fill = np.arange(first_byte, first_byte + nbytes)
        waste = bytes_to_fill[np.in1d(bytes_to_fill, known_bytes)]

        if waste.any():
            wasted_bytes.extend([x for x in bytes_to_fill[~np.in1d(bytes_to_fill, known_bytes)] if x not in knowns])

        edge_waste = bytes_to_fill[bytes_to_fill >= packet_length]

        if edge_waste.any():
            wasted_bytes.extend([x for x in bytes_to_fill[bytes_to_fill < packet_length]  if x < packet_length])

    return sorted(list(set(wasted_bytes)))


def _get_filled_bytes(starting_byte, nbytes, knowns, packet_length=PACKET_LENGTH, known_bytes=None, first_bytes=None, wasted_bytes=None):
    """Returns list of byte indexes filled by new values."""
    filled_bytes = []

    if known_bytes is None:
        known_bytes = _get_known_bytes(knowns=knowns, packet_length=packet_length)

    if first_bytes is None:
        first_bytes = _get(starting_byte, nbytes, packet_length=packet_length)

    if wasted_bytes is None:
        wasted_bytes = _get_wasted_bytes(starting_byte, nbytes, knowns, packet_length=packet_length, known_bytes=known_bytes, first_bytes=first_bytes)

    for first_byte in first_bytes:
        if first_byte not in known_bytes and first_byte not in wasted_bytes:
            filled_bytes.extend(range(first_byte, first_byte + nbytes))

    return filled_bytes


def _get_first_bytes(starting_byte, nbytes, packet_length=PACKET_LENGTH):
    return list(range(starting_byte, packet_length, nbytes))




def get_packet(byte_stream, n, packet_length=PACKET_LENGTH):
    """Returns the bytes from the nth from the end data-packet.

    Parameters
    ----------
    byte_stream : byte str
    n : int
        Ordinal from the end datapoints (e.g. 1 is the "last").
    packet_length : int
        Number of bytes in a data-packet.

    Returns
    -------
    packet : byte str
    """
    if n == 1:
        return byte_stream[-packet_length:]

    return byte_stream[-packet_length * n : -packet_length * (n - 1)]


def read_bytes(packet, byte_idx, dtype, knowns=KNOWNS):
    """Reads the `byte_idx` byte of `packet` as type `dtype`.

    Parameters
    ----------
    packet : byte str
        Bytes from one datapoint (one data-packet)
    byte_idx : int
        Index of byte to read (i.e. 0 is the "first")
    dtype : str
        Code indicating data-type to parse bytes as; must be a key in
        `DATA_TYPES`.

    Returns
    -------
    val : int or None
        Integer value of decoded bytes.  None if too-few bytes remain in
        packet to parse as provided `dtype`.

    Raises
    ------
    DecoderRingError : for invalid data types
    """
    try:
        nbytes, byte_kwargs = DATA_TYPES[dtype]
    except KeyError:
        raise DecoderRingError("Invalid data-type {}.".format(dtype))

    sub_bytes = packet[byte_idx: byte_idx + nbytes]

    # Not enough bytes to finish
    if len(sub_bytes) < nbytes:
        return None

    return int.from_bytes(sub_bytes, **byte_kwargs)


def read_packet(packet, starting_byte, dtype):
    """Reads bytes in `packet` starting from `starting_byte` as `dtype`.

    For any bytes that cannot be parsed in the provided type (i.e. if to few
    bytes remain), a `None` is included instead of a value.

    Parameters
    ----------
    packet : byte str
        Bytes from one datapoint (one data-packet)
    starting_byte : int
        Index of byte to starting reading from (i.e. 0 is the "first")
    dtype : str
        Code indicating data-type to parse bytes as; must be a key in
        `DATA_TYPES`.

    Returns
    -------
    val_tuples : list of (int, int or None)
        Starting byte-idx, val for data in packet.

    See Also
    --------
    read_bytes

    Raises
    ------
    DecoderRingError : for invalid data types
    """
    try:
        nbytes, _ = DATA_TYPES[dtype]
    except KeyError:
        raise DecoderRingError("Invalid data-type {}.".format(dtype))

    return [(i, read_bytes(packet, i, dtype)) for i in
            range(starting_byte, PACKET_LENGTH, nbytes)]
