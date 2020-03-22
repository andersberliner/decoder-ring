"""
Contains global methods, parameters to be used thruout the package.
"""
import os
import numpy as np


class DecoderRingError(Exception):
    """Custom exception class for this package."""
    pass


# Dictionary of data-type short cuts to data-type, abbrevs and their `to_bytes` args
DATA_TYPES = {
    ## Integer types
    # -128 to 127
    "int8le": np.dtype("<i1"),
    "int8be": np.dtype(">i1"),
    # 0 to 255
    "uint8le": np.dtype("<u1"),
    "uint8be": np.dtype(">u1"),
    # -32,768 to 32,767
    "int16le": np.dtype("<i2"),
    "int16be": np.dtype(">i2"),
    # 0 to 65,535
    "uint16le": np.dtype("<u2"),
    "uint16be": np.dtype(">u2"),
    # -2,147,483,648 to 2,147,483,647
    "int32le": np.dtype("<i4"),
    "int32be": np.dtype(">i4"),
    # 0 to 4,294,967,295
    "uint32le": np.dtype("<u4"),
    "uint32be": np.dtype(">u4"),
    # -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807
    "int64le": np.dtype("<i8"),
    "int64be": np.dtype(">i8"),
    # 0 to 18,446,744,073,709,551,615
    "uint64le": np.dtype("<u8"),
    "uint64be": np.dtype(">u8"),
    ## Float types
    "f32le": np.dtype("<f4"),
    "f32be": np.dtype(">f4"),
    "f64le": np.dtype("<f8"),
    "f64be": np.dtype(">f8"),
    "f128le": np.dtype("<f16"),
    "f128be": np.dtype(">f16"),
    ## Bool types
    "bool": np.dtype("?"),
    # ## Char types
    # "char": np.dtype("U1"),
}


def get_filesize(filepath):
    """Returns the size of the file at `filepath` in bytes."""
    return os.stat(filepath).st_size


def get_nbytes(dtype):
    """Returns the number of bytes a given data-type requires."""
    try:
        return np.dtype(DATA_TYPES[dtype]).itemsize

    except KeyError:
        raise DecoderRingError("Invalid data-type {}.".format(dtype))


def cast_from_bytes(byte_list, dtype):
    """Reads bytes `byte_list` as type indicated in `dtype`.

    Parameters
    ----------
    byte_list : byte str
        Bytes for one value
    dtype : str
        Key of data type in `DATA_TYPES`.

    Returns
    -------
    val : various
        Data in the appropriate data-type.

    """
    try:
        return np.frombuffer(byte_list, dtype=DATA_TYPES[dtype])[0]

    except KeyError:
        raise DecoderRingError("Invalid data-type {}.".format(dtype))


def cast_to_bytes(val, dtype):
    """Returns `val` as bytes of data-type indicated by `dtype`.

    Parameters
    ----------
    val : various
    dtype : str
        Key of data type in `DATA_TYPES`.
    nbytes : int or None
        Number of bytes (for str data).

    Returns
    -------
    byte_list : byte str

    Notes
    -----
    String are not handled at this time.
    """
    try:
        return np.array(val, dtype=DATA_TYPES[dtype]).tobytes()
    except KeyError:
        raise DecoderRingError("Invalid data-type {}.".format(dtype))
