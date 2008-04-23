"""
A convenience file for packaging maps.

Example::

        python package.py whiteforest

Which zips up the contents of the folder whiteforest as whiteforest.zip and
places in maps/
"""

import sys, zipfile, glob, os

name = sys.argv[1]

z = zipfile.ZipFile(name+".zip", "w")

for f in glob.glob(name+os.path.sep+"*"):
    filename = f.split(os.path.sep)[-1]
    z.write(f, filename)
