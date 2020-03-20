"""
Module to write data to file
"""
import os
import datetime
from dateutil.parser import parse

# Local imports
from .lib import DecoderRingError, DATA_TYPES
from .packet_map import PACKET_MAP, get_header_bytes
from .sample_data import create_data


def encode_data(filepath, df, start_time, packet_map=PACKET_MAP):
    """Encodes and writes data to a file along with the header.

    Parameters
    ----------
    filepath : str
        Path to file to write
    df : pd.DataFrame
        Data to write to file.  It should contain columns matching those found
        in `packet_map`.
    start_time : datetime.datetime
        Datetime of first datapoint.
    packet_map : dict
        Dict of bytes position to:
            "dtype" : str
                Data-type label.  See packet_map.DATA_TYPES.
            "label" : str
                Column name in `df` containing the data.
            "factor" : float, optional
                Multiplicative factor when encoding `df[label]` as bytes.

    Returns
    -------
    None

    Raises
    ------
    DecoderRingError
    """
    header_bytes = get_header_bytes(os.path.split(filepath)[-1],
            start_time)

    with open(filepath, "wb") as f:
        f.write(header_bytes)
        for _, row in df.iterrows():
            for byte_pos, byte_dict in PACKET_MAP.items():
                try:
                    byte_count, byte_kwargs = DATA_TYPES.get(byte_dict["dtype"])
                except KeyError:
                    raise DecoderRingError(
                        (
                            'Byte position "{}" has invalid data type "{}".'
                        ).format(byte_pos, byte_dict.get("dtype"))
                    )

                f.write(
                    int(
                        row[byte_dict["label"]] * byte_dict.get("factor", 1)
                    ).to_bytes(byte_count, **byte_kwargs)
                )


def main(dt=None):
    """Encodes the sample data-set.

    Returns path to where sample data file was saved.
    """
    if dt is None:
        dt = datetime.datetime.now()
    filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample.unk"))

    encode_data(filepath, create_data(), dt)

    return filepath


if __name__ == "__main__":
    main(parse("20200317 10:00:00"))
