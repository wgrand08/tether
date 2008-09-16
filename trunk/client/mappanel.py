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

import gui

from minimap import *


#****************************************************************************
# The Mappanel has the minimap, chatline etc. 
#****************************************************************************
class Mappanel:

  def __init__(self, clientstate):
    self.client = clientstate;

    self.app = gui.App();
    self.app.connect(gui.QUIT, self.app.quit, None);
    container = gui.Container(align=-1, valign=-1);


    self.minimap_rect = pygame.Rect(self.client.screen_width - 124 , 9,
                                   120, 107);

    self.minimap = Minimap(clientstate, self.minimap_rect.left , self.minimap_rect.top, 
                           120, 107);

    self.input_rect = pygame.Rect(3, self.client.screen_height - 14,
                                  self.client.screen_width - 159, 14);
    self.msgview_rect = pygame.Rect(3, self.client.screen_height - 104, 
                                     self.client.screen_width - 155, 82);

    self.chat_table = gui.Table(width=self.msgview_rect.width,height=self.msgview_rect.height)

    self.chat_table.tr()
    self.lines = gui.Table()
    self.message_out = StringStream(self.lines);
    self.box = gui.ScrollArea(self.lines, self.msgview_rect.width, self.msgview_rect.height)

    #self.chat_table.td(self.box) #this line is broken in windows

    self.chat_table.tr()
    self.line = gui.Input()
    self.line.style.width = self.input_rect.width;
    self.line.style.height = self.input_rect.height;
    self.chat_table.td(self.line)

    self.chat_table.tr()
    self.chat_table.td(MySpacer(1,1, self.box))

    self.firebutton = gui.Button(_(" Fire "));
    container.add(self.firebutton, self.client.screen.get_width() * 0.92, self.client.screen.get_height() * 0.7);
    self.firebutton.connect(gui.MOUSEBUTTONDOWN, self.use_firebutton, None);

    self.rotate_leftbutton = gui.Button(_("  <  "));
    container.add(self.rotate_leftbutton, self.client.screen.get_width() * 0.90, self.client.screen.get_height() * 0.65);
    self.rotate_leftbutton.connect(gui.CLICK, self.rotateleft, None);

    self.rotate_rightbutton = gui.Button(_("  >  "));
    container.add(self.rotate_rightbutton, self.client.screen.get_width() * 0.95, self.client.screen.get_height() * 0.65);
    self.rotate_rightbutton.connect(gui.MOUSEBUTTONDOWN, self.rotateright, None);

    self.rotate_position = 1;
    self.firepower = 0;
    self.rotate_display = gui.Label(_(str(self.rotate_position)));
    container.add(self.rotate_display, self.client.screen.get_width() * 0.92, self.client.screen.get_height() * 0.3);

    container.add(self.chat_table, self.msgview_rect.left, self.msgview_rect.top);
    self.app.init(container); 
    self.draw_panel();


#****************************************************************************
# Draws the panel background.
#****************************************************************************
  def draw_panel(self):
    panel_right_top = self.client.tileset.get_tile_surf("panel_right_top");
    panel_right_bottom = self.client.tileset.get_tile_surf("panel_right_bottom");
    panel_right_center = self.client.tileset.get_tile_surf("panel_right_center");
    panel_bottom_left = self.client.tileset.get_tile_surf("panel_bottom_left");
    panel_bottom_top = self.client.tileset.get_tile_surf("panel_bottom_top");
    panel_bottom_right = self.client.tileset.get_tile_surf("panel_bottom_right");

    #Draw the right panel.
    self.client.screen.blit(panel_right_top, 
             (self.client.screen_width - panel_right_top.get_width(), 0));
    height = (self.client.screen_height - panel_right_top.get_height() - 
	      panel_right_bottom.get_height());
    for y in range (height / panel_right_center.get_height() + 1): 
      y2 = panel_right_top.get_height() + y * panel_right_center.get_height();
      self.client.screen.blit(panel_right_center, 
             (self.client.screen_width - panel_right_center.get_width(), y2));
    self.client.screen.blit(panel_right_bottom, 
             (self.client.screen_width - panel_right_bottom.get_width(),
              self.client.screen_height - panel_right_bottom.get_height()));

    #Draw the bottom panel
    self.client.screen.blit(panel_bottom_left, 
             (0, self.client.screen_height - panel_bottom_left.get_height()));

    width = (self.client.screen_width - panel_bottom_right.get_width() - 
	      - panel_bottom_left.get_width() - panel_right_bottom.get_width());
    for x in range (width / panel_bottom_top.get_width() + 1): 
      x2 = panel_bottom_left.get_width() + x * panel_bottom_top.get_width();
      self.client.screen.blit(panel_bottom_top, 
             (x2, self.client.screen_height - panel_bottom_left.get_height() ));

    self.client.screen.blit(panel_bottom_right, 
             ((self.client.screen_width - panel_right_top.get_width()
              - panel_bottom_right.get_width()), 
              self.client.screen_height - panel_bottom_right.get_height()));

    self.app.repaint();
    self.app.update(self.client.screen);


#****************************************************************************
# Draws the mini map to the screen.
#****************************************************************************
  def draw_minimap(self):
    self.minimap.draw();
    self.draw_panel();
    
#****************************************************************************
#
#****************************************************************************
  def show_message(self, text):
    self.message_out.write(text); 
    self.line.focus();


#****************************************************************************
# User clicked enter
#****************************************************************************
  def send_chat(self):
    input_text = str(self.line.value);
    if (input_text == ""): return;
    self.line.value = "";
    self.client.netclient.send_chat(input_text);

#****************************************************************************
# Handles mouse click events.
#****************************************************************************
  def handle_mouse_click(self, pos):
    (x, y) = pos;
    if self.minimap_rect.collidepoint(x, y):
      self.minimap.handle_mouse_click(pos);


#****************************************************************************
# Handle button inputs
#****************************************************************************
  def rotateright(self, obj):
    if self.client.myturn == True:
        self.rotate_position = self.rotate_position + 1;
        if (self.rotate_position > 12):
            self.rotate_position = 1;
        print('rotate = ', self.rotate_position);

  def rotateleft(self, obj):
    if self.client.myturn == True:
        self.rotate_position = self.rotate_position - 1;
        if (self.rotate_position < 1):
            self.rotate_position = 12;
        print('rotate = ', self.rotate_position);

  def increasepower(self, obj):
    if self.client.myturn == True:
        self.firepower = self.firepower + 1;
        if self.firepower > 15:
            self.firepower = 15;

  def choosehub(self, obj):
    if self.client.myturn == True:
        self.client.selected_weap = 'hub';

  def choosebomb(self, obj):
    if self.client.myturn == True:
        self.client.selected_weap = 'bomb';

  def use_firebutton(self, obj):
    if self.client.myturn == True:
        for unit in self.client.selected_unit.values():
            start_tile = self.client.map.get_tile_from_unit(unit);
            endX = start_tile.x; #todo: need to add true 360 degrees of rotation
            endY = start_tile.y;
            for find_target in range(1, self.firepower):
                if self.rotate_position == 1:
                    endX = endX + 0;
                    endY = endY - 1;
                    startX = start_tile.x + 0;
                    startY = start_tile.y - 1;
                elif self.rotate_position == 2:
                    endX = endX + .25;
                    endY = endY - .75;
                    startX = start_tile.x + 0;
                    startY = start_tile.y - 1;
                elif self.rotate_position == 3:
                    endX = endX + .75;
                    endY = endY - .25;
                    startX = start_tile.x + 1;
                    startY = start_tile.y + 0;
                elif self.rotate_position == 4:
                    endX = endX + 1;
                    endY = endY + 0;
                    startX = start_tile.x + 1;
                    startY = start_tile.y + 0;
                elif self.rotate_position == 5:
                    endX = endX + .75;
                    endY = endY + .25;
                    startX = start_tile.x + 1;
                    startY = start_tile.y + 0;
                elif self.rotate_position == 6:
                    endX = endX + .25;
                    endY = endY + .75;
                    startX = start_tile.x + 0;
                    startY = start_tile.y + 1;
                elif self.rotate_position == 7:
                    endX = endX + 0;
                    endY = endY + 1;
                    startX = start_tile.x + 0;
                    startY = start_tile.y + 1;
                elif self.rotate_position == 8:
                    endX = endX - .25;
                    endY = endY + .75;
                    startX = start_tile.x + 0;
                    startY = start_tile.y + 1;
                elif self.rotate_position == 9:
                    endX = endX - .75;
                    endY = endY + .25;
                    startX = start_tile.x - 1;
                    startY = start_tile.y + 0;
                elif self.rotate_position == 10:
                    endX = endX - 1;
                    endY = endY + 0;
                    startX = start_tile.x - 1;
                    startY = start_tile.y + 0
                elif self.rotate_position == 11:
                    endX = endX - .75;
                    endY = endY - .25;
                    startX = start_tile.x - 1;
                    startY = start_tile.y - 0;
                elif self.rotate_position == 12:
                    endX = endX - .25;
                    endY = endY - .75;
                    startX = start_tile.x - 0;
                    startY = start_tile.y - 1;
                if endX == 0:
                    endX = 90;
                if endX == 91:
                    endX = 1;
                if endY == 0:
                    endY = 90;
                if endY == 91:
                    endY = 1;
        endX = round(endX, 0);
        endY = round(endY, 0);
        #logging.info("endX = %r" % endX);
        #logging.info("endY = %r" % endY);
        self.client.netclient.end_turn(self.client.selected_weap, (endX, endY));
        #self.client.netclient.end_turn('hub', (startX, startY));
        #following is to give time for server to process network commands before running animated launch
        #self.client.process_confirmation = True;
        self.client.conf_startX = startX;
        self.client.conf_startY = startY;
        self.client.conf_endX = endX;
        self.client.conf_endY = endY;

#****************************************************************************
# Hack, to scroll to the latest new message.
#****************************************************************************
class MySpacer(gui.Spacer):
  def __init__(self,width,height,box,**params):
    params.setdefault('focusable', False);
    self.box = box;
    gui.widget.Widget.__init__(self,width=width,height=height,**params);

#****************************************************************************
# 
#****************************************************************************
  def resize(self,width=None,height=None):
    self.box.set_vertical_scroll(65535);
    return 1,1;

#****************************************************************************
# 
#****************************************************************************
class StringStream:

  def __init__(self, lines):
    self.lines = lines;

  def write(self,data):
    self.lines.tr()
    self.lines.td(gui.Label(str(data)),align=-1)

