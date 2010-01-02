"""Copyright 2009:
    Isaac Carroll, Kevin Clement, Jon Handy, David Carroll, Daniel Carroll

This program is free software you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

import os, sys
import pygame
import time
import logging
import math
import random
from pygame.locals import *
from cursors import *
from common.map import *


#****************************************************************************
# The Mapview class contains all logic for rendering maps.
#****************************************************************************
class Mapview:

    def __init__(self, clientstate):
        self.client = clientstate
        self.map = clientstate.map
        for unit in self.map.unitstore.values(): #finds starting position and places it over starting hub
            if unit.playerID == self.client.playerID:
                self.view_x = unit.x - 14
                self.view_y = unit.y - 14

        self.tileset = self.client.tileset
        self.rect = pygame.Rect(0,0,self.client.screen_width - self.tileset.panel_width, self.client.screen_height - self.tileset.panel_height)
 

#****************************************************************************
# Draws the entire map to the screen.
#****************************************************************************
    def drawmap(self):
        self.delta_scroll()
        mapcoord_list = self.gui_rect_iterate(self.view_x, self.view_y)


        if self.client.heldbutton == "right":
            self.client.holdbutton.rotateright()
        if self.client.heldbutton == "left":
            self.client.holdbutton.rotateleft()
        if self.client.heldbutton == "increase":
            self.client.holdbutton.increasepower()
        if self.client.heldbutton == "decrease":
            self.client.holdbutton.decreasepower()


        for pos in mapcoord_list:
            self.draw_tile_terrain(pos)

        for pos in mapcoord_list:
            self.draw_unit(pos)

        if self.client.launched == True:
            self.show_launch()

        if self.client.dying_unit == True:
            self.show_explosion()

        self.draw_mapview_selection()
        self.tileset.animation_next()

#****************************************************************************
# Draws a single map tile with terrain to the mapview canvas.
#****************************************************************************
    def draw_tile_terrain(self, pos):
        map_x, map_y = pos
        real_map_x = map_x % self.map.xsize
        real_map_y = map_y % self.map.ysize

        tile = self.map.get_tile((real_map_x, real_map_y))
        gui_x, gui_y = self.map_to_gui(pos)
        if not self.tileset.is_edge_tile(tile):
            surface = self.tileset.get_terrain_surf_from_tile(tile)
            if not surface: return
            blit_x = gui_x
            blit_y = gui_y
            blit_width = surface.get_width() 

            blit_height = surface.get_height()

            self.client.screen.blit(surface, (blit_x, blit_y), [0,0, blit_width, blit_height])
            return 
        else:
            (surface1, surface2, surface3, surface4) = self.tileset.get_edge_surf_from_tile(tile)
            blit_width = surface1.get_width() 
            blit_height = surface1.get_height()
            blit_x = gui_x - self.view_x 
            blit_y = gui_y - self.view_y


            self.client.screen.blit(surface1, (blit_x + self.tileset.tile_width / 4, blit_y - self.tileset.tile_height / 3), [0,0, blit_width, blit_height])
            self.client.screen.blit(surface2, (blit_x + self.tileset.tile_width / 2, blit_y - self.tileset.tile_height / 10), [0,0, blit_width, blit_height])
            self.client.screen.blit(surface3, (blit_x + self.tileset.tile_width / 4, blit_y + self.tileset.tile_height / 6), [0,0, blit_width, blit_height])
            self.client.screen.blit(surface4, (blit_x, blit_y - self.tileset.tile_height / 10), [0,0, blit_width, blit_height])
#****************************************************************************
# Draws a single map tile with a unit to the mapview canvas.
#****************************************************************************
    def draw_unit(self, map_pos):
        real_map_pos = self.map.wrap_map_pos(map_pos)
        unit = self.map.get_doodad(real_map_pos) 

        if not unit:
            return 

        if unit.typeset == "doodad": #make certain when placing units that 'doodads' are always on the bottom
            for unit2 in self.map.unitstore.values():
                if (unit2.x == unit.x) and (unit2.y == unit.y) and (unit2.typeset != "doodad"):
                    unit = self.map.get_unit(real_map_pos)
                elif ((unit.x + 1) == unit2.x) and (unit.y == unit2.y) and (unit2.typeset != "doodad"):
                    return
                elif (unit.x == unit2.x) and ((unit.y + 1) == unit2.y) and (unit2.typeset != "doodad"):
                    return
                elif ((unit.x + 1) == unit2.x) and ((unit.y + 1) == unit2.y) and (unit2.typeset != "doodad"):
                    return

        #draw units themselves
        gui_x, gui_y = self.map_to_gui(map_pos)

        #unit_surface = self.tileset.get_unit_surf_from_tile(unit.type.id, 0, unit.playerID)
        unit_surface = self.tileset.get_unit_surf_from_tile(unit.type.id, 0, self.client.game.get_unit_team(self.client.playerID, unit.playerID))

        blit_x = gui_x
        blit_y = gui_y

        if unit.type.id == "mines":
            tempX = blit_x + 12
            tempY = blit_y + 12
            scale = 4 * 24
            pygame.draw.circle(self.client.screen, (255, 75, 10), (tempX, tempY), scale, 1)

        if unit.type.id == "shields":
            tempX = blit_x + 12
            tempY = blit_y + 12
            scale = 6 * 24
            pygame.draw.circle(self.client.screen, (255, 75, 10), (tempX, tempY), scale, 1)

        if unit.type.id == "antiair":
            tempX = blit_x + 12
            tempY = blit_y + 12
            scale = 6 * 24
            pygame.draw.circle(self.client.screen, (255, 75, 10), (tempX, tempY), scale, 1)

        #find and show rotation indicator on selected unit
        for selected in self.client.selected_unit.values():

            if unit.id == selected.id:
                rotation = self.client.rotate_position
                endX = unit.x
                endY = unit.y
                startX = blit_x + 24
                startY = blit_y + 24
                temp_rotation = rotation - 90 #following is to adjust for difference between degrees and radians
                if temp_rotation < 1:
                    temp_rotation = rotation + 270
                endX = 175 * math.cos(temp_rotation / 180.0 * math.pi)
                endY = 175 * math.sin(temp_rotation / 180.0 * math.pi)
                finalX = endX + startX
                finalY = endY + startY
                pygame.draw.line(self.client.screen, (255, 10, 10), (startX, startY), (finalX, finalY), 1)
        self.client.screen.blit(unit_surface, (blit_x, blit_y))

#****************************************************************************
# Divides n by d
#****************************************************************************
    def divide(self, n, d):
        res = 0
        if ( (n) < 0 and (n) % (d) < 0 ):
            res = 1
        return ((n / d ) - res)

#****************************************************************************
# Increments the mapview scrolling (moves one step).
#****************************************************************************
    def delta_scroll(self):
        self.view_x += (self.client.view_delta_x / 10)
        self.view_y += (self.client.view_delta_y / 10)

#****************************************************************************
# Centers the view on a specified tile.
#****************************************************************************
    def center_view_on_tile(self, map_pos):
        x, y = map_pos
        self.view_x = x - 16
        self.view_y = y - 16


#****************************************************************************
#
#****************************************************************************
    def draw_mapview_selection(self):

        if self.client.mapctrl.mouse_state == 'select':
            (left, top) = self.client.mapctrl.select_pos_start
            (right, bottom) = self.client.mapctrl.select_pos_end
            height = bottom - top
            width = right - left
            sel_rect = pygame.Rect(left, top, width, height)
            pygame.draw.rect(self.client.screen, (255,0,0), sel_rect, 1)

#****************************************************************************
# Returns gui-coordinates (eg. screen) from map-coordinates (a map tile).
#****************************************************************************
    def map_to_gui(self, map_pos):
        map_dx, map_dy = map_pos
        map_dx = map_dx - (self.view_x)
        map_dy = map_dy - (self.view_y)
        return (map_dx * self.tileset.tile_width, map_dy * self.tileset.tile_height)


#****************************************************************************
# Returns map-coordinates from gui-coordinates.
#****************************************************************************
    def gui_to_map(self, gui_pos):
        gui_x, gui_y = gui_pos
        map_x = self.divide(gui_x, self.tileset.tile_width)
        map_y = self.divide(gui_y, self.tileset.tile_height)
        endX = map_x + self.view_x
        endY = map_y + self.view_y
        if endX < 0:
            endX = self.map.xsize + endX
        if endX > self.map.xsize - 1:
            endX = endX - (self.map.xsize - 1)
        if endY < 0:
            endY = self.map.ysize + endY
        if endY > self.map.ysize - 1:
            endY = endY - (self.map.ysize - 1)
        return (endX, endY)

#****************************************************************************
# Returns a list of map coordinates to be shows on the map canvas view.
#****************************************************************************
    def gui_rect_iterate(self, gui_x0, gui_y0):
        mapcoord_list = []
        for map_x in range(gui_x0, (gui_x0 + 29)):
            for map_y in range(gui_y0, (gui_y0 + 29)):
                mapcoord_list.insert(0, (map_x, map_y))
            
        return mapcoord_list

#****************************************************************************
# Displays launched unit
#****************************************************************************
    def show_launch(self):
        if self.client.launch_type == "cluster" or self.client.launch_type == "mines":
            if (self.client.launch_step < ((self.client.launch_distance + 3.5) * 2)):
                self.client.launch_step = self.client.launch_step + .5
                temp_rotation = self.client.launch_direction - 90 #following is to adjust for difference between degrees and radians
                if temp_rotation < 1:
                    temp_rotation = self.client.launch_direction + 270
                midpoint = ((self.client.launch_distance + 3.5) * 2) - round((((self.client.launch_distance + 3.5) * 2) / 2), 0)
                if self.client.launch_step < midpoint:
                    logging.info("unsplit cluster")
                    endX = self.client.launch_step * math.cos(temp_rotation / 180.0 * math.pi)
                    endY = self.client.launch_step * math.sin(temp_rotation / 180.0 * math.pi)
                    endX = endX + self.client.launch_startx
                    endY = endY + self.client.launch_starty
                    self.client.launch_splitx = endX
                    self.client.launch_splity = endY
                    map_pos = endX, endY
                    blit_x, blit_y = self.map_to_gui(map_pos)
                    unit_surface = self.tileset.get_unit_surf_from_tile(self.client.launch_type, 0, self.client.playerlaunched)
                    self.client.screen.blit(unit_surface, (blit_x, blit_y))
                else:
                    logging.info("split a cluster")
                    endX = self.client.launch_step * math.cos(temp_rotation / 180.0 * math.pi)
                    endY = self.client.launch_step * math.sin(temp_rotation / 180.0 * math.pi)
                    endX = endX + self.client.launch_startx
                    endY = endY + self.client.launch_starty
                    map_pos = endX, endY
                    blit_x, blit_y = self.map_to_gui(map_pos)
                    unit_surface = self.tileset.get_unit_surf_from_tile(self.client.launch_type, 0, self.client.playerlaunched)
                    self.client.screen.blit(unit_surface, (blit_x, blit_y))

                    default_rotation = temp_rotation

                    temp_rotation = default_rotation + 45
                    if temp_rotation > 360:
                        temp_rotation = default_rotation - 315

                    launch_step = self.client.launch_step - midpoint
                    endX = launch_step * math.cos(temp_rotation / 180.0 * math.pi)
                    endY = launch_step * math.sin(temp_rotation / 180.0 * math.pi)
                    endX = endX + self.client.launch_splitx
                    endY = endY + self.client.launch_splity
                    map_pos = endX, endY
                    blit_x, blit_y = self.map_to_gui(map_pos)
                    unit_surface = self.tileset.get_unit_surf_from_tile(self.client.launch_type, 0, self.client.playerlaunched)
                    self.client.screen.blit(unit_surface, (blit_x, blit_y))

                    temp_rotation = default_rotation - 45
                    if temp_rotation < 1:
                        temp_rotation = default_rotation + 315

                    launch_step = self.client.launch_step - midpoint
                    endX = launch_step * math.cos(temp_rotation / 180.0 * math.pi)
                    endY = launch_step * math.sin(temp_rotation / 180.0 * math.pi)
                    endX = endX + self.client.launch_splitx
                    endY = endY + self.client.launch_splity
                    map_pos = endX, endY
                    blit_x, blit_y = self.map_to_gui(map_pos)
                    unit_surface = self.tileset.get_unit_surf_from_tile(self.client.launch_type, 0, self.client.playerlaunched)
                    self.client.screen.blit(unit_surface, (blit_x, blit_y))

            else: 
                if self.client.launch_type == "mines":
                    self.client.moonaudio.sound("landing.ogg")
                self.client.launched = False
                self.client.landed = True
                self.client.launch_step = 1
            return

        if self.client.launch_type == "missile":
            if (self.client.launch_step < ((self.client.launch_distance + 3.5) * 2)):
                self.client.launch_step = self.client.launch_step + .5
                temp_rotation = self.client.launch_direction - 90 #following is to adjust for difference between degrees and radians
                if temp_rotation < 1:
                    temp_rotation = self.client.launch_direction + 270
                endX = self.client.launch_step * math.cos(temp_rotation / 180.0 * math.pi)
                endY = self.client.launch_step * math.sin(temp_rotation / 180.0 * math.pi)
                endX = endX + self.client.launch_startx
                endY = endY + self.client.launch_starty
                map_pos = endX, endY

                #find possible trajectory change in midflight
                radius = 6
                searchX = endX
                searchY = endY
                for find_target in range(1, radius):
                    spinner = 0
                    while spinner < 360:
                        searchX = find_target * math.cos(spinner / 180.0 * math.pi)
                        searchY = find_target * math.sin(spinner / 180.0 * math.pi)
                        searchX = round(searchX, 0)
                        searchY = round(searchY, 0)
                        searchX = searchX + endX
                        searchY = searchY + endY
                        for target in self.map.unitstore.values():
                            if target.playerID != playerID and searchX == target.x and searchY == target.y and target.typeset == "build":
                                #found a target and changing trajectory to hit it
                                self.client.launch_direction = spinner
                                self.client.launch_distance = find_target
                                self.client.missilelock = True
                                spinner = 360
                                logging.info("missile homed in on target")
                        else:
                            spinner = spinner + 5

                blit_x, blit_y = self.map_to_gui(map_pos)
                unit_surface = self.tileset.get_unit_surf_from_tile(self.client.launch_type, 0, self.client.playerlaunched)
                self.client.screen.blit(unit_surface, (blit_x, blit_y))
                return
            else: 
                if self.client.splashed == True:
                    self.client.moonaudio.sound("watersplash.ogg")
                    self.client.splashed = False
                self.client.launched = False
                self.client.landed = True
                self.client.launch_step = 1
            return

        else:
            #if (self.client.launch_step < ((self.client.launch_distance + 3.5) * 2)):
            if (self.client.launch_step < (self.client.launch_distance + 3.5)):
                self.client.launch_step = self.client.launch_step + .5
                temp_rotation = self.client.launch_direction - 90 #following is to adjust for difference between degrees and radians
                if temp_rotation < 1:
                    temp_rotation = self.client.launch_direction + 270
                endX = self.client.launch_step * math.cos(temp_rotation / 180.0 * math.pi)
                endY = self.client.launch_step * math.sin(temp_rotation / 180.0 * math.pi)
                endX = endX + self.client.launch_startx
                endY = endY + self.client.launch_starty
                map_pos = endX, endY
                blit_x, blit_y = self.map_to_gui(map_pos)
                unit_surface = self.tileset.get_unit_surf_from_tile(self.client.launch_type, 0, self.client.playerlaunched)
                self.client.screen.blit(unit_surface, (blit_x, blit_y))
                return
            else: 
                if self.client.splashed == True:
                    self.client.moonaudio.sound("watersplash.ogg")
                    self.client.splashed = False
                elif self.client.hit_rock == True:
                    self.client.moonaudio.sound("mediumboom.ogg")
                    self.client.hit_rock = False
                elif self.client.game.get_unit_typeset(self.client.launch_type) == "build":
                    self.client.moonaudio.sound("landing.ogg")
                if self.client.collecting_energy == True:
                    self.client.moonaudio.sound("recall.ogg")
                    self.client.moonaudio.narrate("capture.ogg")
                    self.client.collecting_energy = False
                self.client.launched = False
                self.client.landed = True
                self.client.launch_step = 1
            return

#****************************************************************************
# Displays explosions
#****************************************************************************
    def show_explosion(self):

        place = 0
        for deathname in self.client.deathname:
            map_pos = self.client.deathX[place], self.client.deathY[place]
            blitX, blitY = self.map_to_gui(map_pos)
            unit_surface = self.tileset.get_unit_surf_from_tile(deathname, 0, self.client.deathplayerID[place])
            if self.client.deathtypes[place] != "weap" or deathname != "recall":
                self.client.screen.blit(unit_surface, (blitX, blitY))
            place = place + 1

        unittype = self.client.deathtypes.pop(0)
        deathX = self.client.deathX.pop(0)
        deathY = self.client.deathY.pop(0)
        deathplayerid = self.client.deathplayerID.pop(0)
        deathname = self.client.deathname.pop(0)
        if unittype == "build":
            self.client.moonaudio.sound("biggestboom.ogg")
            map_pos = deathX, deathY
            blitX, blitY = self.map_to_gui(map_pos)
            blitX = blitX + 24
            blitY = blitY + 24
            scale = 0
            while scale < 48:
                scale = scale + 1
                pygame.draw.circle(self.client.screen, (255, 75, 10), (blitX, blitY), scale, 0)
                pygame.display.flip()
                pygame.time.wait(2)
        if unittype == "weap":
            if deathname == "recall":
                self.client.moonaudio.sound("recall.ogg")   
            elif deathname == "repair":
                self.client.moonaudio.sound("repair.ogg")
            elif deathname == "virus":
                self.client.moonaudio.sound("virus.ogg")
            elif deathname == "spike":
                self.client.moonaudio.sound("spike.ogg")
            elif deathname == "emp":
                self.client.moonaudio.sound("emp.ogg")
                map_pos = deathX, deathY
                blitX, blitY = self.map_to_gui(map_pos)
                blitX = blitX + 24
                blitY = blitY + 24
                scale = 0
                while scale < 360:
                    scale = scale + 1
                    pygame.draw.circle(self.client.screen, (10, 75, 255), (blitX, blitY), scale, 0)
                    pygame.display.flip()
                    pygame.time.wait(2)
            else:
                self.client.moonaudio.sound("mediumboom.ogg")
                map_pos = deathX, deathY
                blitX, blitY = self.map_to_gui(map_pos)
                blitX = blitX + 24
                blitY = blitY + 24
                scale = 0
                while scale < 24:
                    scale = scale + 1
                    pygame.draw.circle(self.client.screen, (255, 75, 10), (blitX, blitY), scale, 0)
                    pygame.display.flip()
                    pygame.time.wait(2)


        if unittype == "tether":
            pop = random.randint(1, 6)
            if pop == 1:
                self.client.moonaudio.sound("tetherpop.ogg")
            if pop == 2:
                self.client.moonaudio.sound("tetherpop2.ogg")
            if pop == 3:
                self.client.moonaudio.sound("tetherpop3.ogg")
            if pop == 4:
                self.client.moonaudio.sound("tetherpop4.ogg")
            if pop == 5:
                self.client.moonaudio.sound("tetherpop5.ogg")
            if pop == 6:
                self.client.moonaudio.sound("tetherpop6.ogg")

            map_pos = deathX, deathY
            blitX, blitY = self.map_to_gui(map_pos)
            blitX = blitX + 12
            blitY = blitY + 12
            scale = 0
            while scale < 24:
                scale = scale + 1
                pygame.draw.circle(self.client.screen, (255, 75, 10), (blitX, blitY), scale, 0)
                pygame.display.flip()
                pygame.time.wait(2)
        if not self.client.deathtypes:
            self.client.dying_unit = False

