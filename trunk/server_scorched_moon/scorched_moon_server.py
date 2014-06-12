#!/usr/bin/python3

"""Copyright 2014:
    Kevin Clement

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

import sys
import subprocess
import os

def main():
    debug = False
    check = 0
    for argument in sys.argv:
        if argument == "--debug" or argument == "-d":
            debug = True
        elif argument == "--help" or argument == "-h":
            usage()
        elif check > 0:
            print("Unknown argument: %s" % argument)
            usage()
        check += 1

    import server.main
    server = server.main.Main(debug)

def usage():
    print("usage: [--debug] [--help]")
    sys.exit(0)

main()
