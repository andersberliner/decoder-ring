"""
Module to write data to file
"""
import os
from .packet_map import PACKET_MAP, DATA_TYPES, HEADER_BYTES
from .sample_data import create_data


def encode_data(filename, df, header_bytes=HEADER_BYTES):
    with open(filename, "wb") as f:
        f.write(HEADER_BYTES)
        for idx, row in df.iterrows():
            for byte_pos, byte_dict in PACKET_MAP.items():
                byte_count, byte_kwargs = DATA_TYPES.get(byte_dict["dtype"])
                f.write(
                    int(
                        row[byte_dict["label"]] * byte_dict.get("factor", 1)
                    ).to_bytes(byte_count, **byte_kwargs)
                )


def main():
    encode_data(os.path.join(os.path.dirname(__file__), "..", "sample.unk"), create_data())


if __name__ == "__main__":
    main()
