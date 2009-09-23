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
import mapview


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
        self.deathtypes = []
        self.deathX = []
        self.deathY = []


    def show_explosion(self):
        unittype = self.deathtypes.pop(0)
        deathX = self.deathX.pop(0)
        deathY = self.deathY.pop(0)
        if unittype == "build":
            self.client.moonaudio.sound("mediumboom.ogg")
            print"hub died"
        if unittype == "weap":
            image = pygame.image.load("data/graphics/misc/boom.png").convert()
            map_pos = deathX, deathY
            blitX, blitY = mapview.Mapview.map_to_gui(mapview, map_pos)
            blitX = blitX + 24
            blitY = blitY + 24
            scale = 0.00
            while scale < 1:
                q = 0.02
                image = pygame.transform.rotozoom(image, 0, scale)
                screen.blit(image, (blitX, blitY))
                pygameg.display.flip()

        if unittype == "tether":
            self.client.moonaudio.sound("tetherpop.ogg")
            print"tether died"
        if not self.deathtypes:
            self.client.dying_unit = False
