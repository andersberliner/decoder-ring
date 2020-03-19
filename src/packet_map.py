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


# Dictionary of data-type short cuts to their `to_bytes` args
DATA_TYPES = {
    # -128 to 127
    "int8le": (1, {"byteorder": "little", "signed": True}),
    "int8be": (1, {"byteorder": "little", "signed": True}),
    # 0 to 255
    "uint8le": (1, {"byteorder": "little", "signed": False}),
    "uint8be": (1, {"byteorder": "little", "signed": False}),
    # -32,768 to 32,767
    "int16le": (2, {"byteorder": "little", "signed": True}),
    "int16be": (2, {"byteorder": "little", "signed": True}),
    # 0 to 65,535
    "uint16le": (2, {"byteorder": "little", "signed": False}),
    "uint16be": (2, {"byteorder": "little", "signed": False}),
    # -2,147,483,648 to 2,147,483,647
    "int32le": (4, {"byteorder": "little", "signed": True}),
    "int32be": (4, {"byteorder": "little", "signed": True}),
    # 0 to 4,294,967,295
    "uint32le": (4, {"byteorder": "little", "signed": False}),
    "uint32be": (4, {"byteorder": "little", "signed": False}),
    # -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807
    "int64le": (8, {"byteorder": "little", "signed": True}),
    "int64be": (8, {"byteorder": "little", "signed": True}),
    # 0 to 18,446,744,073,709,551,615
    "uint64le": (8, {"byteorder": "little", "signed": False}),
    "uint64be": (8, {"byteorder": "little", "signed": False}),
}


HEADER = "{}\n{}\n{}\n".format("Acme v1.0".ljust(25), "sample_data.unk".ljust(25), "2020-03-19 10:00:00".ljust(25))


HEADER_BYTES = bytes(HEADER, encoding="utf-8") + bytearray([170, 170, 1])
