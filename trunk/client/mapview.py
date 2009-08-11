# OpenRTS - Copyright (C) 2006 The OpenRTS Project
#
# OpenRTS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# OpenRTS is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

import os, sys
import pygame
import time
import logging
from pygame.locals import *
from cursors import *
from common.map import *

#****************************************************************************
# The Mapview class contains all logic for rendering isometric maps.
#****************************************************************************
class Mapview:

  def __init__(self, clientstate):
    self.client = clientstate;
    self.map = clientstate.map;
    self.view_x = 1200; #starting location of viewer
    self.view_y = 1200;
    self.view_delta_x = 0; #for scrolling viewer
    self.view_delta_y = 0;
    self.tileset = self.client.tileset;
    self.cursor = GfxCursor(self.client, self.client.screen);
    self.rect = pygame.Rect(0,0,self.client.screen_width - self.tileset.panel_width,
                          self.client.screen_height - self.tileset.panel_height);
 

#****************************************************************************
# Draws the entire map to the screen.
#****************************************************************************
  def drawmap(self):
    self.delta_scroll();
    mapcoord_list = self.gui_rect_iterate(self.view_x, self.view_y, self.rect.width, int(self.rect.height + self.tileset.tile_height * 0.5));

    """event = pygame.event.poll();
    if event.type == pygame.MOUSEBUTTONUP:
        self.client.heldbutton = "void";"""
    if self.client.heldbutton == "right":
        self.client.holdbutton.rotateright();
    if self.client.heldbutton == "left":
        self.client.holdbutton.rotateleft();
    if self.client.heldbutton == "increase":
        self.client.holdbutton.increasepower();
    if self.client.heldbutton == "decrease":
        self.client.holdbutton.decreasepower();
    logging.info("heldbutton = %r" % self.client.heldbutton);
    if self.client.rotate_position == 45:
        self.client.heldbutton = "void";


    for pos in mapcoord_list:
      self.draw_tile_terrain(pos);

    for pos in mapcoord_list:
        self.draw_unit(pos);

    self.cursor.show();
    self.draw_mapview_selection();
    self.tileset.animation_next();

#****************************************************************************
# Draws a single map tile with terrain to the mapview canvas.
#****************************************************************************
  def draw_tile_terrain(self, pos):
    map_x, map_y = pos
    real_map_x = map_x % self.map.xsize;
    real_map_y = map_y % self.map.ysize;

    tile = self.map.get_tile((real_map_x, real_map_y));
    gui_x, gui_y = self.map_to_gui(pos);
    if not self.tileset.is_edge_tile(tile):
      surface = self.tileset.get_terrain_surf_from_tile(tile);
      if not surface: return;
      blit_x = gui_x - self.view_x; 
      blit_y = (gui_y - self.view_y - (surface.get_height() / 2));
      blit_width = surface.get_width(); 
      blit_height = surface.get_height();

      self.client.screen.blit(surface, (blit_x, blit_y), [0,0, blit_width, blit_height]);
      return; 
    else:
      (surface1, surface2, surface3, surface4) = self.tileset.get_edge_surf_from_tile(tile);
      blit_width = surface1.get_width(); 
      blit_height = surface1.get_height();
      blit_x = gui_x - self.view_x; 
      blit_y = (gui_y - self.view_y );


      self.client.screen.blit(surface1, (blit_x + self.tileset.tile_width / 4, 
                                     blit_y - self.tileset.tile_height / 3),
                                     [0,0, blit_width, blit_height]);
      self.client.screen.blit(surface2, (blit_x + self.tileset.tile_width / 2, 
                                     blit_y - self.tileset.tile_height / 10),
                                     [0,0, blit_width, blit_height]);
      self.client.screen.blit(surface3, (blit_x + self.tileset.tile_width / 4, 
                                     blit_y + self.tileset.tile_height / 6),
                                     [0,0, blit_width, blit_height]);
      self.client.screen.blit(surface4, (blit_x, blit_y - self.tileset.tile_height / 10),
                                     [0,0, blit_width, blit_height]);
#****************************************************************************
# Draws a single map tile with a unit to the mapview canvas.
#****************************************************************************
  def draw_unit(self, map_pos):
    real_map_pos = self.map.wrap_map_pos(map_pos);
    unit = self.map.get_doodad(real_map_pos); 

    if not unit:
        return; 

    if unit.typeset == "doodad": #make certain when placing units that 'doodads' are always on the bottom
        for unit2 in self.map.unitstore.values():
            if (unit2.x == unit.x) and (unit2.y == unit.y) and (unit2.typeset != "doodad"):
                unit = self.map.get_unit(real_map_pos);

    #draw units themselves
    gui_x, gui_y = self.map_to_gui(map_pos);

    unit_surface = self.tileset.get_unit_surf_from_tile(unit.type.id, unit.dir, unit.playerID);

    dx, dy = unit.offset;
    vx, vy = unit.speed;
    
    unit.offset = (dx + vx/(0.1+self.client.clock.get_fps()), 
                   dy + vy/(0.1+self.client.clock.get_fps()));
    blit_x = gui_x - self.view_x + dx * self.tileset.tile_width; 
    blit_y = (gui_y - self.view_y - (unit_surface.get_height() / 2) + dy * self.tileset.tile_height);

    #find and show rotation indicator on selected unit
    for selected in self.client.selected_unit.values():

        if unit.id == selected.id:
            rotation = self.client.rotate_position;
            endX = unit.x;
            endY = unit.y;
            startX = blit_x + 30;
            startY = blit_y + 30;
            (north, west) = self.client.game.percent_from_degree(rotation);
            for find_target in range(1, 4):
                endX = endX + west;
                endY = endY + north;
            offsetX = endX - (round(endX, 0));
            offsetY = endY - (round(endY, 0));
            offsetX = offsetX * 48;
            offsetY = offsetY * 48;
            endX = round(endX, 0);
            endY = round(endY, 0);
            endX, endY = self.map_to_gui((endX, endY));
            endX = endX - self.view_x + dx * self.tileset.tile_width; 
            endY = (endY - self.view_y - (unit_surface.get_height() / 2) + dy * self.tileset.tile_height);
            finalX = endX + offsetX;
            finalY = endY + offsetY;
            pygame.draw.line(self.client.screen, self.client.game.get_player_color(self.client.playerID), (startX, startY), (finalX, endY), 1)
    self.client.screen.blit(unit_surface, (blit_x, blit_y));

#****************************************************************************
# Divides n by d
#****************************************************************************
  def divide(self, n, d):
    res = 0;
    if ( (n) < 0 and (n) % (d) < 0 ):
      res = 1;
    return ((n / d ) - res)

#****************************************************************************
# Increments the mapview scrolling (moves one step).
#****************************************************************************
  def delta_scroll(self):

    self.view_x += (self.view_delta_x / 10);
    self.view_y += (self.view_delta_y / 10);

#****************************************************************************
# Centers the view on a specified tile.
#****************************************************************************
  def center_view_on_tile(self, map_pos):
    new_x, new_y = self.map_to_gui(map_pos);
    self.view_x = new_x - self.client.screen.get_width() / 2;
    self.view_y = new_y - self.client.screen.get_height() / 2;

#****************************************************************************
#
#****************************************************************************
  def draw_mapview_selection(self):

    if self.client.mapctrl.mouse_state == 'select':
      (left, top) = self.client.mapctrl.select_pos_start;
      (right, bottom) = self.client.mapctrl.select_pos_end;
      height = bottom - top;
      width = right - left;
      sel_rect = pygame.Rect(left, top, width, height);
      pygame.draw.rect(self.client.screen, (255,0,0), sel_rect, 1);

#****************************************************************************
# Returns gui-coordinates (eg. screen) from map-coordinates (a map tile).
#****************************************************************************
  def map_to_gui(self, map_pos):
    map_dx, map_dy = map_pos;
    return (((map_dx - map_dy) * self.tileset.tile_width / 2), ((map_dx + map_dy) * self.tileset.tile_height / 2));


#****************************************************************************
# Returns map-coordinates from gui-coordinates.
#****************************************************************************
  def gui_to_map(self, gui_pos):
    gui_x, gui_y = gui_pos;
    return (self.divide(gui_x * self.tileset.tile_height 
                          + gui_y * self.tileset.tile_width,
                        self.tileset.tile_width * self.tileset.tile_height)
            ,self.divide(gui_y * self.tileset.tile_width 
                          - gui_x * self.tileset.tile_height, 
                        self.tileset.tile_width * self.tileset.tile_height)+1);


#****************************************************************************
# Returns map coordinates from canvas-coordinates (visible mapcanvas surface) 
# Note that this method ignores height.
#****************************************************************************
  def canvas_to_map(self, canvas_pos):
    canvas_x, canvas_y = canvas_pos;
    map_pos = self.gui_to_map((self.view_x + canvas_x, self.view_y + canvas_y));
    return self.map.wrap_map_pos(map_pos);

#****************************************************************************
# Returns a list of map coordinates to be shows on the map canvas view.
#****************************************************************************
  def gui_rect_iterate(self, gui_x0, gui_y0, width, height):
    mapcoord_list = []
    if (width < 0): 
      gui_x0 += width                                                      
      width = -width                                                      
                                                                          
    if (height < 0): 
      gui_y0 += height                                                     
      height = -height                                                     
                                                                           
    if (width > 0 and height > 0):                                           
      W = (self.tileset.tile_width / 2)   
      H = (self.tileset.tile_height / 2) 
      GRI_x0 = self.divide(gui_x0,W)
      GRI_y0 = self.divide(gui_y0, H)           
      GRI_x1 = self.divide(gui_x0 + width + W - 1, W)                       
      GRI_y1 = self.divide(gui_y0 + height + H - 1, H)                      
      GRI_x0 -= 1
      GRI_y0 -= 1
      count = (GRI_x1 - GRI_x0) * (GRI_y1 - GRI_y0) 
      for GRI_itr in range(count):                        
        GRI_x_itr = GRI_x0 + (GRI_itr % (GRI_x1 - GRI_x0))                   
        GRI_y_itr = GRI_y0 + (GRI_itr / (GRI_x1 - GRI_x0))                   
        if ((GRI_x_itr + GRI_y_itr) % 2 != 0):                             
          continue                                                         
        map_x = (GRI_x_itr + GRI_y_itr) / 2                                
        map_y = (GRI_y_itr - GRI_x_itr) / 2
        mapcoord_list.insert(0, (map_x, map_y));
      return mapcoord_list


