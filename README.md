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

Create a `DataDecoder` object, which will be seeded on initialization:

```python
from src.decode_data import DataDecoder, PACKET_LENGTH

decoder = DataDecoder(
    "sample.unk",
    ndpts=4,
    starting_bytes=[0,1,2],
    packet_length=PACKET_LENGTH,
    # Keep this empty to "start-fresh"
    knowns=None,
)
```

To view, for example, byte position 9 in a sub-sample of data-types, with the first byte reserved as a _starting byte_:

```python
DataDecoder.view_byte_idx(9, 1, ["uint16le", "uint16be", "uint32le", "uint32be"])
```

To view the full set of packets with starting_byte 1, try:

```python
DataDecoder.view_dtypes(1, ["uint16le", "uint16be", "uint32le", "uint32be"])
```

If you have a guess of a data-type and want to grab the full-set of data, you
will need to either specify the number of datapoints expected in the file, or
make sure the `knowns` you pass in on initialization includes the correct dpt
position (1, uint32le in `sample.unk`).  Then you can, for example, to
investigate byte 5 as a little-endian short (i.e. 16 bit), you would:

```python
DataDecoder.decode_byte_idx(byte_idx=5, dtype="uint16le")
```

And to see all the data in your knowns (with the same dpt caveat as before):

```python
DataDecoder.decode_knowns()
```

Add the "actual" csv as an arg to include that data as well for comparison:

```python
DataDecode.decode_knowns("sample.csv")
```

Currently, in the `KNOWNS` static variable in `decode_data`, I have included a few bytes (see `src.packet_map.PACKET_MAP` for the official map).  You can update as you go to "fill-in" the byte-packet.

## Tests

To run all tests, do the following:

```
# Activate virtualenv if you haven't already
source decoder/bin/activate

# Run the tests
python -m pytest -s -vv tests/
```

General-use fixtures are found in `tests/fixtures`.
