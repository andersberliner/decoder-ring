# decoder-ring
Encoding and decoding data as a byte stream

## Requirements

Requirements are very simple.  Assuming you have pip installed:

```
pip install -r requirements.txt
```

You might want to, first, create a virtual environment:

```
pip install virtualenv
virtualenv decoder
source decode/bin/activate
pip install -r requirements.txt
```

You can just run `./setup.sh` to do all of the above.

Activate the virtual environment before any of the below sections.

```
source decode/bin/activate
```

## Sample Data

A very simple set of sample data can be generated for comparisons purposes.

```python
from src import sample_data

# Create set of sample data
df = sample_data.create_data()

# Create data and save to a file - i.e. sample_data.csv
sample_data.main()
```

## Encoding Data

To encode the sample data to .unk file, use the `encode_data` module:

```python
from src import encode_data

encode_data.main()
```

This encodes the sample data in `sample.unk`.  Because `sample.unk` is checked in, to avoid git diffs, you can specify the timestamp to be written in the header of the file to match the stored version, if you desire.

```python
from src import encode_data
from dateutil.parser import parse

encode_data.main(parse("20200317 10:00:00"))
```

The sample data is encoded according to the rules laid-forth in `packet_map`:
* A header is generated with a version string, filename and timestamp string
* Data is encoded with datatypes and scale factors given in `PACKET_MAP`.

## Decoding Data

To experiment with decoding data (i.e. from `sample.unk`), use the `decode_data` module.

First, see a dataframe with the scope of the parameters you want to investigate.

```python
from src import decode_data

seed_df = decode_data.seed_data(
    "sample.unk",
    4,
    starting_bytes=[0,1,2],
    packet_length=decode_data.PACKET_LENGTH,
    # Keep this empty to "start-fresh"
    knowns=None,
)
```

To view, for example, byte position 9 in a sub-sample of data-types, with the first byte reserved as a _starting byte_:

```python
decode_data.view_byte_position(
    seed_df,
    9,
    1,
    ["uint16le", "uint16be", "uint32le", "uint32be"])
```

Currently, in the `KNOWNS` static variable in `decode_data`, I have included a few bytes (see `src.packet_map.PACKET_MAP` for the official map).  You can update as you go to "fill-in" the byte-packet.

## Tests

Coverage will be extended shortly, but to run all tests, do the following:

```
# Activate virtualenv if you haven't already
source decoder/bin/activate

# Run the tests
python -m pytest -s -vv tests/
```
