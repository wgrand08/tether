"""Copyright 2012:
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

import os, sys
import string
import os, os.path

import logging


#****************************************************************************
#  This class reads game settings from various files
#****************************************************************************
"""The game settings themselves are stored within a plaintext file titled settings.config"""
class ClientSettings:

    def __init__(self):
        self.rulesets = {}

        self.tileset = "data/graphics/tileset.xml" 
        self.screen_width = 1024 
        self.screen_height = 768
        self.language = "en" 

        self.version = 0.001
        self.string_version = "0.0.01"
        self.playername = "Commander"
        self.fullscreen = False
        self.WINDOW_SIZE = self.screen_width,self.screen_height = 1024,768
        self.appRunning = True
        self.screenRunning = True
        self.debug = False
        self.lastIP = "127.0.0.1"
        self.language = "en"
        self.play_music = True
        self.music_volume = 10
        self.play_sound = True
        self.sound_volume = 10
        self.play_narrate = True
        self.narrate_volume = 10
        self.tetherdir = os.getenv("HOME")
        if str(self.tetherdir) == "None":
            self.tetherdir = os.getenv("USERPROFILE")
            self.tetherdir = os.path.join(self.tetherdir, "scorchedmoon")
        else:
            self.tetherdir = os.path.join(self.tetherdir, ".scorchedmoon")
        if not os.path.exists(self.tetherdir):
            os.mkdir(self.tetherdir)
