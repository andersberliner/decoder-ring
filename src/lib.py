"""
Contains global methods, parameters to be used thruout the package.
"""

class DecoderRingError(Exception):
    """Custom exception class for this package."""
    pass


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


