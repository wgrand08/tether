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
    loglevel = 4
    logready = False
    check = 0
    for argument in sys.argv:
        if argument == "--debug" or argument == "-d":
            debug = True
        elif argument == "--help" or argument == "-h":
            usage()
        elif argument == "--log" or argument == "-l":
            logready = True
        elif argument == "1":
            if logready == True: #don't combine if statements to make it easier to add further 
                logready = False
                loglevel = 1
            else:
                print("Unknown argument: %s" % argument)
                usage()
        elif argument == "2":
            if logready == True: #don't combine if statements to make it easier to add further 
                logready = False
                loglevel = 2
            else:
                print("Unknown argument: %s" % argument)
                usage()
        elif argument == "3":
            if logready == True: #don't combine if statements to make it easier to add further 
                logready = False
                loglevel = 3
            else:
                print("Unknown argument: %s" % argument)
                usage()
        elif argument == "4":
            if logready == True: #don't combine if statements to make it easier to add further 
                logready = False
                loglevel = 4
            else:
                print("Unknown argument: %s" % argument)
                usage()
        elif check > 0:
            print("Unknown argument: %s" % argument)
            usage()
        check += 1

    import server.main
    server = server.main.Main(debug, loglevel)

def usage():
    print(" ")
    print("scorched_moon_server [options]")
    print(" ")
    print("Options are:")
    print(" ")
    print("-d               --debug             Run server in debug mode, this also forces log to level 1")
    print(" ")
    print("-l <number>      --log <number>      Set log level from 1 - 4")
    print(" ")
    print("-h               --help              Display this help screen")
    sys.exit(0)

main()
