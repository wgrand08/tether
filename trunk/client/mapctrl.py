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
import logging
from pygame.locals import *

#****************************************************************************
# Mapctrl handles user-input on the main map view, and tells the client
# what to do.
#****************************************************************************
class Mapctrl:

    def __init__(self, gameclient):
        self.client = gameclient
        self.mouse_state = "default"

#****************************************************************************
# Handle input events from pygame.
#****************************************************************************
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.client.quit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                self.client.quit()
            elif event.type == KEYDOWN and event.key == K_RETURN:
                self.client.mappanel.send_chat()
            elif event.type == KEYDOWN and event.key == K_f:
                logging.info(self.client.clock.get_fps())
            elif event.type == KEYDOWN and event.key == K_a:
                self.set_mouse_state('attack')
            elif event.type == MOUSEBUTTONDOWN:
                self.handle_mouse_click(pygame.mouse.get_pos(), event.button)
            elif event.type == MOUSEBUTTONUP:
                self.handle_mouse_release(pygame.mouse.get_pos(), event.button)
            elif event.type == MOUSEMOTION:
                self.mouse_motion(pygame.mouse.get_pos())

            self.client.mappanel.app.event(event)

            self.client.mapview.cursor.update(event)

#****************************************************************************
# Handles all mouse click events from Pygame.
#****************************************************************************
    def handle_mouse_click(self, pos, button):
        if button == 1:
            (x, y) = pos 
            if self.mouse_state == "default":
                self.select_pos_start = pygame.mouse.get_pos() 
                self.select_pos_end = pygame.mouse.get_pos() 
                self.set_mouse_state('select')

        elif button == 3:
            map_pos = self.client.mapview.gui_to_map(pos) 
            self.client.mapview.center_view_on_tile(map_pos)

        self.client.mappanel.handle_mouse_click(pos)

#****************************************************************************
# Handles all mouse release events from Pygame.
#****************************************************************************
    def handle_mouse_release(self, pos, button):
        if button == 1 and self.mouse_state == 'select': 
            self.define_tiles_within_rectangle()
        self.client.heldbutton = "void"

#****************************************************************************
#Section for when a user 'drags' the cursor 
#****************************************************************************
    def define_tiles_within_rectangle(self):
        w = self.client.tileset.tile_width / 2
        h = self.client.tileset.tile_height / 6
        half_w = w / 2
        half_h = h / 2
        (x1, y1) = self.select_pos_start
        (x2, y2) = self.select_pos_end
        rec_w = x2 - x1
        rec_h = y2 - y1
        segments_x = abs(rec_w/ half_w)
        segments_y = abs(rec_h/ half_h)
        self.set_mouse_state('default')         
  
        # Iteration direction   
        if rec_w > 0:
            inc_x = half_w
        else:
            inc_x = -half_w
        if rec_h > 0:
            inc_y = half_h
        else:
            inc_y = -half_h
     
        y = y1
        yy = 0
        while (yy <= segments_y): 
            x = x1
            xx = 0
#following code is to determine if a unit has been selected. There are 4 seperate checks due to each unit occupying 4 tiles on the map. 
            while (xx <= segments_x):
                map_pos = self.client.mapview.gui_to_map((x, y))
                unit = self.client.map.get_unit(map_pos)
                if unit: 
                    self.client.selected_unit = {}
                    if unit.typeset == "build" and unit.playerID == self.client.playerID: #only allow players to select their own buildings
                        if len(self.client.selected_unit.values()) == 0: #this is to prevent user from selecting multiple units
                            self.client.selected_unit.update({map_pos:unit})
                            logging.info("Selected unit ID %r" % unit.id)
                            logging.info("It's parent ID is %r" % unit.parentID)
                else:
                    subX = x - 24
                    subY = y - 24
                    map_pos = self.client.mapview.gui_to_map((subX, subY))
                    unit = self.client.map.get_unit(map_pos)
                    if unit: 
                        self.client.selected_unit = {}
                        if unit.typeset == "build" and unit.playerID == self.client.playerID: #only allow players to select their own buildings
                            if len(self.client.selected_unit.values()) == 0: #this is to prevent user from selecting multiple units
                                self.client.selected_unit.update({map_pos:unit})
                                logging.info("Selected unit ID %r" % unit.id)
                                logging.info("It's parent ID is %r" % unit.parentID)
                    else:
                        subX = x - 24
                        subY = y
                        map_pos = self.client.mapview.gui_to_map((subX, subY))
                        unit = self.client.map.get_unit(map_pos)
                        if unit: 
                            self.client.selected_unit = {}
                            if unit.typeset == "build" and unit.playerID == self.client.playerID: #only allow players to select their own buildings
                                if len(self.client.selected_unit.values()) == 0: #this is to prevent user from selecting multiple units
                                    self.client.selected_unit.update({map_pos:unit})
                                    logging.info("Selected unit ID %r" % unit.id)
                                    logging.info("It's parent ID is %r" % unit.parentID)
                        else:
                            subX = x
                            subY = y - 24
                            map_pos = self.client.mapview.gui_to_map((subX, subY))
                            unit = self.client.map.get_unit(map_pos)
                            if unit: 
                                self.client.selected_unit = {}
                                if unit.typeset == "build" and unit.playerID == self.client.playerID: #only allow players to select their own buildings
                                    if len(self.client.selected_unit.values()) == 0: #this is to prevent user from selecting multiple units
                                        self.client.selected_unit.update({map_pos:unit})
                                        logging.info("Selected unit ID %r" % unit.id)
                                        logging.info("It's parent ID is %r" % unit.parentID)


                yy += 1
                y += inc_y
                xx += 1
                x += inc_x


#****************************************************************************
# The mouse moved, do a scroll. 
#****************************************************************************
    def mouse_motion(self, pos):
        (x, y) = pos
        """if y > self.client.mapview.mapcanvas.get_height(): 
            self.client.mapview.cursor.disable()
        else:
            self.client.mapview.cursor.set_cursor_type(self.mouse_state)"""
        if self.mouse_state == 'select':
           self.select_pos_end = pygame.mouse.get_pos() 


#****************************************************************************
#
#****************************************************************************
    def set_mouse_state(self, state):

        if state == 'default':
            self.client.mapview.cursor.disable()
        else:
            self.client.mapview.cursor.set_cursor_type(state)
        self.client.mapview.cursor.disable() #disable to show mouse cursors
        self.mouse_state = state

