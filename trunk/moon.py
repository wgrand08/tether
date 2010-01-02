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

import logging
import platform
import sys
import os

import common.log

#****************************************************************************
# Check dependencies (Pygame).
#****************************************************************************
def dependencyCheck():
  logging.info('Platform: ' + platform.platform())
  logging.info('Python version ' + sys.version)
  try:
    import pygame
    logging.info('Pygame version: ' + pygame.version.ver)
  except ImportError, err:
    logging.error('Loading dependency "pygame" failed: ' + str(err))
    sys.exit(1)
  try :
    import PIL.Image as Image
    logging.info('Python Image Library version ' + Image.VERSION)
  except ImportError, err:
    logging.info('Loading dependency "PIL" failed: ' + str(err))
    sys.exit(1)
  try:
    import twisted
    if hasattr(twisted, '__version__'):
      logging.info('Twisted version ' + twisted.__version__)
    else:
      logging.info('Twisted version unknown (probably old)')
  except ImportError, err:
    logging.error('Loading dependency "twisted" failed: ' + str(err))
    sys.exit(1)


def main():

  #logLevel = logging.WARNING
  if os.path.exists("MoonPy.log"):
    os.remove('MoonPy.log')
  LOG_FILENAME = 'MoonPy.log'
  logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)  

  dependencyCheck()
  import client.main
  client = client.main.Main()

main()


