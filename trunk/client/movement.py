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


import pygame
import os
import logging


class Movement:
    def __init__(self, clientstate):
        self.client = clientstate
        self.launched = False
        self.landed = False
        self.launch_startx = 0
        self.launch_starty = 0
        self.direction = 0
        self.distance = 0
        self.step = 1
        self.playerlaunched = 1
        self.type = None


    def show_explosion(self, x, y, unittype):
            if unittype == "build":
                self.client.moonaudio.sound("mediumboom.ogg")
                print"hub died"
            if unittype == "weap":
                print"bomb exploded here"
            if unittype == "tether":
                self.client.moonaudio.sound("tetherpop.ogg")
                print"tether died"
