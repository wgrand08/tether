"""Copyright 2010:
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

from moonaudio import *
from settings import *

#****************************************************************************
#This class is the main class for the client part of Scorched Moon. All major client variables and some common functions are stored here
#****************************************************************************
class GameClient:
    def __init__(self):

        self.version = 0.002
        self.stringversion = "0.0.02"
        self.debug = False
        self.screen_width = 1024 
        self.screen_height = 768
        self.screen = None
        self.moonaudio = MoonAudio(self)
        self.settings = ClientSettings()
