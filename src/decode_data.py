"""
Module to decode byte-stream
"""
import os
import pandas as pd
import numpy as np
from copy import deepcopy
from warnings import warn

# Relative imports
from .lib import DATA_TYPES, DecoderRingError, cast_from_bytes, get_nbytes, get_filesize

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

DPT_INDEX = 1


class DataDecoder(object):
    """Class for decoding a binary file."""

    def __init__(self, filepath, ndpts=4, dtypes=None, starting_bytes=None,
            packet_length=PACKET_LENGTH, knowns=KNOWNS, dpt_index=DPT_INDEX):
        """Initializes the DataDecoder object, including seeding the data."""
        self._packet_length = packet_length
        self._knowns = knowns if knowns is not None else {}
        self._dpt_idx = dpt_index
        self._filepath = filepath
        self._filename = os.path.split(filepath)[1]
        self._total_bytes = get_filesize(self._filepath)

        # Seed the last four datapoints.
        self._seed_df = seed_data(
            filepath,
            ndpts=ndpts,
            dtypes=dtypes,
            starting_bytes=starting_bytes,
            packet_length=packet_length,
            knowns=knowns
        )

        # Determine the maximum number of data-points in the file.
        self._max_dpts = None
        if (dpt_index is not None) and (dpt_index in self._knowns):
            sbyte, dtype, n, _ = self._seed_df.index.min()
            self._max_dpts = self._seed_df.loc[sbyte, dtype, 1, dpt_index].iloc[0]

        # Find the known labels
        self._known_labels = {byte_dict["label"]: byte_idx for
                byte_idx, byte_dict in self._knowns.items()}

    def decode_byte_idx(self, byte_idx=None, dtype=None, label=None, dpts=None):
        """Decodes all data in the file at specified byte in specified datatype.

        If `label` is specified and in the knowns, get the byte_idx and dtype
        from the knowns dict.  Otherwise, `byte_idx` and `dtype` must be
        specified.

        If `dpts` is specified, will override the found maximum datapoints
        during init.

        Parameters
        ----------
        byte_idx : int
        dtype : str
        label : str
        dpts : int, optional

        Returns
        -------
        decoded_data : list of various
            Array of decoded data.

        Raises
        ------
        DecoderRingError : for invalid arguments
        """
        decoded_data = []

        factor = 1.0
        if label in self._known_labels:
            byte_idx = self._known_labels[label]
            dtype = self._knowns[byte_idx]["dtype"]
            factor = self._knowns[byte_idx].get("factor", 1.0)

        if byte_idx is None:
            raise DecoderRingError("A label in the knowns or byte_idx must be specified.")

        if dtype is None:
            raise DecoderRingError("A label in the knowns or dtype must be specified.")

        if dpts is None:
            dpts = self._max_dpts

        if dpts is None:
            raise DecoderRingError("Dpt must be in the knowns or dpts must be specified.")

        with open(self._filepath, "rb") as f:
            for i, n in enumerate(range(1, dpts + 1)[::-1]):
                if i == 0:
                    f.seek(self._total_bytes - dpts * self._packet_length)
                packet = f.read(self._packet_length)

                decoded_data.append(decode_bytes(packet, byte_idx, dtype) / factor)

        return decoded_data

    def decode_knowns(self, csv_file=None, dpts=None):
        """Decode all known portions of the file and return as dataframe.

        If a csv_file is provided, add those columns, too.

        Parameters
        ----------
        csv_file : str or None.
            Path to csv_file containing the 'actual' data.
        dpts : int, optional
            Specify number of datapoints to parse.  If not specified, dpt must
            be specified in the knowns and will be used to determine who many
            bytes back to parse.

        Returns
        -------
        out_df : pd.DataFrame

        Raises
        ------
        DecoderRingError : for invalid arguments
        """
        data = []

        if dpts is None:
            dpts = self._max_dpts

        if dpts is None:
            raise DecoderRingError("Dpt must be in the knowns or dpts must be specified.")

        with open(self._filepath, "rb") as f:
            for i, n in enumerate(range(1, dpts + 1)[::-1]):
                if i == 0:
                    f.seek(self._total_bytes - dpts * self._packet_length)
                # Get position of the first data-point
                packet = f.read(self._packet_length)

                dpt_data = {}
                for byte_idx, byte_dict in self._knowns.items():
                    dpt_data[byte_dict["label"]] = decode_bytes(
                        packet,
                        byte_idx,
                        byte_dict["dtype"]
                    ) / byte_dict.get("factor", 1)

                data.append(dpt_data)

        knowns_df = pd.DataFrame(data)

        csv_df = pd.DataFrame()
        if csv_file is not None:
            csv_df = pd.read_csv(csv_file)

        # If csv data is present, merge files together
        if not csv_df.empty:
            out_df = csv_df.copy()

            for label in knowns_df:
                out_df["{}_decoded".format(label)] = knowns_df[label]

        else:
            out_df = knowns_df

        return out_df

    def view_byte_idx(self, byte_idx, starting_byte, dtypes=None):
        """Returns view of byte at position `byte_idx` in data types `dtypes`.

        Data in packets start from posn `starting_byte`.

        Parameters
        ----------
        seed_df : pd.DataFrame
            Output of seed_data
        byte_idx : int
            Index of byte to view
        starting_byte : int
            Position bytes where decoded from (in whichever data-type).  Bytes
            before this position are assumed to be "start bytes".
        dtypes : list of str, optional
            Data-types to show decoded values for.

        Returns
        -------
        view_df : pd.DataFrame

        See Also
        --------
        view_byte_idx
        """
        return view_byte_idx(self._seed_df, byte_idx, starting_byte,
                dtypes=dtypes)

    def view_dtypes(self, starting_byte, dtypes):
        """Returns a view of parsed data for a given starting byte and dtypes.

        Fills all possible values, starting at `starting_byte`, with each of
        the provided datatypes `dtypes`.

        Parameters
        ----------
        seed_df : pd.DataFrame
            Output of `seed_data`.  Must have been seeded with the provided
            `dtypes` and `starting_byte`.
        starting_byte : int
        dtypes : list of str
            Datatype keys.  See `lib.DATA_TYPES` for supported data types.

        Returns
        -------
        view_df : pd.DataFrame

        Raises
        ------
        DecoderRingError : for `starting_byte` or `dtypes` not seeded in
        `self._seed_df`.

        Notes
        -----
        Since `self._seed_df` will reflect the `knowns` you used when seeding,
        known bytes will not be re-parsed.

        See Also
        --------
        view_byte_idx
        """
        return view_dtypes(self._seed_df, starting_byte, dtypes)

    def __repr__(self):
        """String representation of the DataDecoder."""
        return "<DataDecoder>: {}".format(self._filepath)

    def summary(self):
        """Returns a well-formatted summary of this DataDecoder."""
        output = [
            "Packet Length: {}".format(self._packet_length),
            "Total Bytes: {}".format(self._total_bytes),
            "Dpt Idx: {}".format(self._dpt_idx),
            "Max Dpts: {}".format(self._max_dpts),
            "Knowns: {}".format(self._known_labels),
        ]

        return "<DataDecoder: {}\n\t{}".format(self._filepath, "\n\t".join(output))


def seed_data(filepath, ndpts, dtypes=None, starting_bytes=None,
        packet_length=PACKET_LENGTH, knowns=KNOWNS):
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

    if knowns is None:
        knowns = {}

    data = []

    with open(filepath, "rb") as f:
        for i, n in enumerate(range(1, ndpts + 1)[::-1]):
            if i == 0:
                f.seek(get_filesize(filepath) - ndpts * packet_length)

            # Select current packet
            # packet = get_packet(byte_stream, n, packet_length=packet_length)
            packet = f.read(packet_length)
            known_data = fill_known_bytes(packet, knowns, packet_length=packet_length)

            for dtype in dtypes:
                nbytes = get_nbytes(dtype)

                for starting_byte in starting_bytes:
                    # Parse values
                    tmp_df = pd.DataFrame(
                        decode_packet(
                            packet,
                            dtype,
                            starting_byte,
                            packet_length,
                            knowns=knowns,
                            known_data=known_data
                        )
                    ).T

                    # Add labels
                    tmp_df["sbyte"] = starting_byte
                    tmp_df["n"] = n
                    tmp_df["dtype"] = dtype

                    data.append(tmp_df)

    df = pd.concat(data)
    df.index.name = "idx"

    # Re-index for more efficient decoding later
    return df.reset_index().set_index(["sbyte", "dtype", "n", "idx"]).fillna("")


def view_byte_idx(seed_df, byte_idx, starting_byte, dtypes=None):
    """Returns view of byte at position `byte_idx` in data type `dtypes`.

    Data in packets start from posn `starting_byte`.

    Parameters
    ----------
    seed_df : pd.DataFrame
        Output of seed_data
    byte_idx : int
        Index of byte to view
    starting_byte : int
        Position bytes where decoded from (in whichever data-type).  Bytes
        before this position are assumed to be "start bytes".
    dtypes : list of str, optional
        Data-types to show decoded values for.

    Returns
    -------
    view_df : pd.DataFrame
    """
    if dtypes is None:
        dtypes = seed_df.index.get_level_values("dtype").unique()

    return seed_df.loc[pd.IndexSlice[starting_byte, dtypes, :, byte_idx], :]\
        .reset_index()\
        .pivot(index="dtype", columns="n", values="val")\
        .T[dtypes]\
        .sort_index(ascending=False)


def view_dtypes(seed_df, starting_byte, dtypes):
    """Returns a view of parsed data for a given starting byte and dtypes.

    Fills all possible values, starting at `starting_byte`, with each of the
    provided datatypes `dtypes`.

    Parameters
    ----------
    seed_df : pd.DataFrame
        Output of `seed_data`.  Must have been seeded with the provided
        `dtypes` and `starting_byte`.
    starting_byte : int
    dtypes : list of str
        Datatype keys.  See `lib.DATA_TYPES` for supported data types.

    Returns
    -------
    view_df : pd.DataFrame

    Raises
    ------
    DecoderRingError : for `starting_byte` or `dtypes` not seeded in `seed_df`.

    Notes
    -----
    Since `seed_df` will reflect the `knowns` you used when seeding, known
    bytes will not be re-parsed.

    See Also
    --------
    view_byte_idx
    """
    ndpts = seed_df.index.get_level_values("n").max()

    # Validate inputs
    if starting_byte not in seed_df.index.get_level_values("sbyte").unique():
        raise DecoderRingError(
            (
                "Invalid starting_byte {}; this starting_byte was not seeded."
            ).format(starting_byte)
        )

    invalid_dtypes = set(dtypes).difference(
            seed_df.index.get_level_values("dtype").unique())
    if invalid_dtypes:
        raise DecoderRingError(
            (
                "Invalid dtype(s) {}; these dtypes were not seeded."
            ).format(dtypes)
        )

    # Create composite column names and see data.
    df = seed_df.loc[starting_byte]

    dtype_dfs = []

    for i, dtype in enumerate(dtypes):
        # dtype_data = df[df["dtype"] == dtype]
        dtype_data = df.loc[dtype]

        for n in range(1, ndpts + 1)[::-1]:
            # tmp_df = dtype_data[dtype_data["n"] == n]
            tmp_df = dtype_data.loc[n]

            # Add label column on first iteration
            if i == 0 and n == ndpts:
                out_df = tmp_df["label"].to_frame().copy()

            out_df["{}-{}".format(dtype, n)] = tmp_df["val"]

    # The following is in progress and may provide a better view.
    # return seed_df.loc[pd.IndexSlice[starting_byte, :, dtypes], :].sort_index(level=["dtype", "n"]).T

    return out_df


def decode_packet(packet, dtype, starting_byte, packet_length=PACKET_LENGTH,
        knowns=KNOWNS, known_data=None):
    """Decodes the bytes in `packet`, converting to `dtype`.

    If byte(s) are assigned to `knowns`, uses the specified data types for
    those bytes (instead of `dtype`).

    Denotes bytes that can not be used for the specified data type with '*'.

    For data types requiring multiple bytes, decoded value is in the first
    byte and the remaining required bytes are deonted as being filled with '-'
    or '.'.

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
    packet_df : dict
        Data from `packet` decoded into `dtype` (or knowns).
        Byte idx => {label: label (str), val: val (various)}
    """
    nbytes = get_nbytes(dtype)

    if known_data is None:
        data = fill_known_bytes(packet, knowns, packet_length=packet_length)
    else:
        data = deepcopy(known_data)

    # Handle already populated bytes or reservered/wasted bytes.
    known_bytes = _get_known_bytes(knowns)
    first_bytes = _get_first_bytes(starting_byte, nbytes, packet_length=packet_length)
    wasted_bytes = _get_wasted_bytes(starting_byte, nbytes, knowns, packet_length=packet_length, known_bytes=known_bytes, first_bytes=first_bytes)
    filled_bytes = _get_filled_bytes(starting_byte, nbytes, knowns, packet_length=packet_length, known_bytes=known_bytes, first_bytes=first_bytes, wasted_bytes=wasted_bytes)

    # Populate filler bytes
    for byte_idx in wasted_bytes:
        data[byte_idx] = {"val": WASTED_BYTE}

    for byte_idx in filled_bytes:
        data[byte_idx] = {"val": FILLED_BYTE}

    # Parse available values
    for byte_idx in first_bytes:
        if byte_idx in filled_bytes:
            data[byte_idx] = {
                "val": decode_bytes(packet, byte_idx, dtype),
                "label": FILLED_BYTE
            }

    return data


def fill_known_bytes(packet, knowns, packet_length=PACKET_LENGTH):
    """Returns a byte dictionary (pos=> {val, label}) for known bytes.

    Parameters
    ----------
    packet : byte str
    knowns : dict
        Portions of the byte map that are known.  Key is starting byte idx.
        Value is a dict containing, at least:
            "dtype" : str
                Datatype bytes should be parsed as
            "label" : str
                Column label for the data.
    packet_length : int
        Number of bytes in each packet

    Returns
    -------
    byte_vals_dict : dict
        Byte_idx to dict of:
            {"val": value in appropriate type, "label": column label}
    """
    if knowns is None:
        knowns = {}

    decoded_packet = {i: {"val": None, "label": None} for i in
            range(packet_length)}

    for i, byte_dict in knowns.items():
        dtype = byte_dict["dtype"]
        label = byte_dict["label"]

        decoded_packet[i] = {"val": decode_bytes(packet, i, dtype), "label": label}

        for j in range(i + 1, i + get_nbytes(dtype)):
            decoded_packet[j] = {"val": FILLED_KNOWN_BYTE, "label": label}

    return decoded_packet


def _get_known_bytes(knowns, packet_length=PACKET_LENGTH):
    """Returns list of byte indexes containing known values.

    Parameters
    ----------
    knowns : dict
        Portions of the byte map that are known.  Key is starting byte idx.
        Value is a dict containing, at least:
            "dtype" : str
                Datatype bytes should be parsed as
            "label" : str
                Column label for the data.
    packet_length : int
        Number of bytes in each packet.

    Returns
    -------
    known_bytes : list of int
        Index of bytes populated by 'known' values.
    """
    if knowns is None:
        knowns = {}
    known_bytes = []

    for known, known_dict in knowns.items():
        nbytes = get_nbytes(known_dict["dtype"])

        known_bytes.extend(range(known, known + nbytes))

    return known_bytes


def _get_wasted_bytes(starting_byte, nbytes, knowns,
        packet_length=PACKET_LENGTH, known_bytes=None, first_bytes=None):
    """Returns list of byte indexes that are wasted when filling bytes.

    Parameters
    ----------
    starting_byte : int
        Position bytes where decoded from (in whichever data-type).  Bytes
        before this position are assumed to be "start bytes".
    nbytes : int
        Number of bytes required to parsed into data-type.
    packet_length : int
        Number of bytes in each packet.
    known_bytes : list of int, optional
        Output of `_get_known_bytes`.  Will be computed if not provided.
    first_bytes : list of int, optional
        Output of `_get_first_bytes`.  Will be computed if not provided.

    Returns
    -------
    wasted_bytes : list of int
        Index of bytes wasted (i.e. can not be filled) given `knowns`, `nbytes`
        and `starting_byte`.
    """
    wasted_bytes = []
    if known_bytes is None:
        known_bytes = _get_known_bytes(knowns=knowns, packet_length=packet_length)

    if first_bytes is None:
        first_bytes = _get_first_bytes(starting_byte, nbytes, packet_length=packet_length)

    # Find collision with known bytes and/or the end of the packet
    for first_byte in first_bytes:
        bytes_to_fill = np.arange(first_byte, first_byte + nbytes)
        waste = bytes_to_fill[np.in1d(bytes_to_fill, known_bytes)]

        if waste.any():
            wasted_bytes.extend([
                x for x in
                bytes_to_fill[~np.in1d(bytes_to_fill, known_bytes)]
                if x not in knowns and x < packet_length
            ])

    return sorted(list(set(wasted_bytes)))


def _get_filled_bytes(starting_byte, nbytes, knowns,
        packet_length=PACKET_LENGTH, known_bytes=None, first_bytes=None,
        wasted_bytes=None):
    """Returns list of byte indexes filled by new values.

    Parameters
    ----------
    starting_byte : int
        Position bytes where decoded from (in whichever data-type).  Bytes
        before this position are assumed to be "start bytes".
    nbytes : int
        Number of bytes required to parsed into data-type.
    packet_length : int
        Number of bytes in each packet.
    known_bytes : list of int, optional
        Output of `_get_known_bytes`.  Will be computed if not provided.
    first_bytes : list of int, optional
        Output of `_get_first_bytes`.  Will be computed if not provided.
    wasted_bytes : list of int, optional
        Output of `_get_wasted_bytes`.  Will be computed if not provided.

    Returns
    -------
    filled_bytes : list of int
        Index of bytes to be filled by decoding as data of `nbytes`.
    """
    filled_bytes = []

    if known_bytes is None:
        known_bytes = _get_known_bytes(knowns=knowns,
                packet_length=packet_length)

    if first_bytes is None:
        first_bytes = _get_first_bytes(starting_byte, nbytes,
                packet_length=packet_length)

    if wasted_bytes is None:
        wasted_bytes = _get_wasted_bytes(starting_byte, nbytes, knowns,
                packet_length=packet_length, known_bytes=known_bytes,
                first_bytes=first_bytes)

    for first_byte in first_bytes:
        if first_byte not in known_bytes and first_byte not in wasted_bytes:
            filled_bytes.extend(range(first_byte, first_byte + nbytes))

    return filled_bytes


def _get_first_bytes(starting_byte, nbytes, packet_length=PACKET_LENGTH):
    """Returns list of bytes that values can start on in the packet.

    Parameters
    ----------
    starting_byte : int
        Position bytes where decoded from (in whichever data-type).  Bytes
        before this position are assumed to be "start bytes".
    nbytes : int
        Number of bytes required to parsed into data-type.
    packet_length : int
        Number of bytes in each packet.

    Returns
    -------
    first_bytes : list of int
        Index of starting bytes for a packet of length `packet_length` starting
        at byte `starting_byte` where each value is `nbytes` bytes in length.
    """
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

    Notes
    -----
    This method is deprecated.  All consumers no work from a filestream to
    alleviate memory concerns.
    """
    warn(
        (
            "This method is deprecated as it requires the full byte-stream."
            "  See less memory intensive implementations in, e.g., seed_data."
        ),
        DeprecationWarning,
        stacklevel=2
    )

    if n == 1:
        return byte_stream[-packet_length:]

    return byte_stream[-packet_length * n : -packet_length * (n - 1)]


def decode_bytes(packet, byte_idx, dtype):
    """Reads the `byte_idx` byte of `packet` as type `dtype`.

    Parameters
    ----------
    packet : byte str
        Bytes from one datapoint (one data-packet)
    byte_idx : int
        Index of byte to read (i.e. 0 is the "first")
    dtype : str
        Code indicating data-type to parse bytes as; must be a key in
        `DATA_TYPES` (associated with valid numpy type).

    Returns
    -------
    val : int or None
        Integer value of decoded bytes.  None if too-few bytes remain in
        packet to parse as provided `dtype`.
    """
    nbytes = get_nbytes(dtype)
    sub_bytes = packet[byte_idx: byte_idx + nbytes]

    # Not enough bytes to finish
    if len(sub_bytes) < nbytes:
        return None

    return cast_from_bytes(sub_bytes, dtype)
