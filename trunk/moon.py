#!/usr/bin/python
 
"""Copyright 2009:
    Isaac Carroll, Kevin Clement, Jon Handy, David Carroll, Daniel Carroll

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
import logging

def main():
    #this is to verify compatible python version is in use
    if sys.version_info < (2, 4):
        print("MoonPy requires python2.5 or higher")
        logging.error("Python version incompatibility: python < 2.5")
        sys.exit(1)
    if not sys.version_info < (3, 0):
        print("MoonPy is not compatible with python3.x yet")
        logging.error("Python version incompatibility: python >= 3.0")
        sys.exit(1)
    try:
        import pygame
    except:
        if os.name == "nt":
            logging.info("Pygame not installed, attempting automatic installation")
            subprocess.Popen([r"msiexec", "-i", "http://pygame.org/ftp/pygame-1.9.1.win32-py2.6.msi"]).wait()
        elif os.name == "mac":
            logging.error("automatic osX pygame installation not yet implemented")
            sys.exit(1)
        else:
            logging.error("Missing dependency: pygame will need to be installed manually on this system")
            sys.exit(1)
        try:
            import pygame
            logging.info('Pygame version: ' + pygame.version.ver)
        except:
            logging.error("Automatic pygame dependency resolution failed! Exiting...")
            sys.exit(1)
    try:
        import PIL.Image as Image
    except:
        if os.name == "nt":
            logging.info("PIL not installed, attempting automatic installation")
            subprocess.Popen([r"explorer", "http://effbot.org/downloads/PIL-1.1.7.win32-py2.6.exe"]).wait()
        elif os.name == "mac":
            logging.error("automatic osX PIL installation not yet implemented")
            sys.exit(1)
        else:
            logging.error("Missing depedency: PIL will need to be installed manually on this system")
            sys.exit(1)
        try:
            import PIL.Image as Image
            logging.info('Python Image Library version ' + Image.VERSION)
        except:
            logging.error("Automatic PIL dependency resolution failed! Exiting...")
            sys.exit(1)
    try:
        import twisted
        logging.debug('Twisted version ' + twisted.__version__)
    except ImportError, err:
      logging.error("Missing dependency: twisted will need to be installed manually")
      sys.exit(1)

    import client.main
    client = client.main.Main(False)

main()
