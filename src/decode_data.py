"""
Module to decode byte-stream
"""
from .packet_map import DATA_TYPES

PACKET_LENGTH = 21


def seed_data(filename, ndpts, packet_length=PACKET_LENGTH):
    pass



def get_packet(byte_stream, n, packet_length=PACKET_LENGTH):
    return byte_stream[-packet_length * n : -packet_length * (n - 1)]


def read_byte(packet, byte_idx, dtype):
    nbytes, byte_kwargs = DATA_TYPES.get(dtype)
    sub_bytes = packet[byte_idx: byte_idx + nbytes]

    return int.from_bytes(sub_bytes, **byte_kwargs)



def read_bytes(packet, starting_byte, dtype):
    nbytes, byte_kwargs = DATA_TYPES.get(dtype)

    out = []
    for sub_bytes in [packet[i: i + nbytes] for i in range(starting_byte, PACKET_LENGTH, nbytes)]:
        if len(sub_bytes) < nbytes:
            out.append('-')

            continue

        out.append(int.from_bytes(sub_bytes, **byte_kwargs))

    return out
