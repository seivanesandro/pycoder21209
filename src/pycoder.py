"""
PyCoder is an RLE compression/decompression tool.

This module launches both the PyCoder GUI and the command line
interfaces. Unlike, gzip/gunzip, pycoder.py acts both as compressor and
decompressor.

It reads command line arguments using the docopt library and using
the following grammar:

    $ python3 pycoder.py (-c [-t TYPE] | -d) [-p PASSWD] FILE

This module is also a script and GUI application. Please see function 
'_main' for instructions on how to use 'pycoder.py' as script or GUI 
app.

(c) João Galamba, 2022
$$LICENSE(GPL)
"""

import rle

