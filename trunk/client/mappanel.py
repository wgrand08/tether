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
# 
#****************************************************************************
"""This class handles the minimap, the chat line, and the buttons to control units"""
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

    self.hub_button = gui.Button(_(" hub " ));
    container.add(self.hub_button, self.client.screen.get_width() * 0.90, self.client.screen.get_height() * 0.4);
    self.hub_button.connect(gui.MOUSEBUTTONDOWN, self.choosehub, None);

    self.bomb_button = gui.Button(_(" bomb "));
    container.add(self.bomb_button, self.client.screen.get_width() * 0.95, self.client.screen.get_height() * 0.4);
    self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.choosebomb, None);

    self.firebutton = gui.Button(_(" Fire "));
    container.add(self.firebutton, self.client.screen.get_width() * 0.94, self.client.screen.get_height() * 0.7);
    self.firebutton.connect(gui.MOUSEBUTTONDOWN, self.use_firebutton, None);

    self.uppower_button = gui.Button(_(" + "));
    container.add(self.uppower_button, self.client.screen.get_width() * 0.92, self.client.screen.get_height() * 0.55);
    self.uppower_button.connect(gui.MOUSEBUTTONDOWN, self.increasepower, None);

    self.downpower_button = gui.Button(_(" - "));
    container.add(self.downpower_button, self.client.screen.get_width() * 0.94, self.client.screen.get_height() * 0.65);
    self.downpower_button.connect(gui.MOUSEBUTTONDOWN, self.decreasepower, None);

    self.rotate_leftbutton = gui.Button(_("  <  "));
    container.add(self.rotate_leftbutton, self.client.screen.get_width() * 0.90, self.client.screen.get_height() * 0.60);
    self.rotate_leftbutton.connect(gui.CLICK, self.rotateleft, None);

    self.rotate_rightbutton = gui.Button(_("  >  "));
    container.add(self.rotate_rightbutton, self.client.screen.get_width() * 0.95, self.client.screen.get_height() * 0.60);
    self.rotate_rightbutton.connect(gui.MOUSEBUTTONDOWN, self.rotateright, None);

    self.firepower = 1;
    self.rotate_display = gui.Label(_(str(self.client.rotate_position)));
    container.add(self.rotate_display, self.client.screen.get_width() * 0.92, self.client.screen.get_height() * 0.3);

    container.add(self.chat_table, self.msgview_rect.left, self.msgview_rect.top);
    self.app.init(container); 
    self.draw_panel();


#****************************************************************************
# Draws the panel background.
#****************************************************************************
  def draw_panel(self):
    panel_right_top = self.client.tileset.get_tile_surf("panel_right_top");
    panel_right_center = self.client.tileset.get_tile_surf("panel_right_center");
    panel_bottom_left = self.client.tileset.get_tile_surf("panel_bottom_left");
    panel_bottom_top = self.client.tileset.get_tile_surf("panel_bottom_top");
    panel_bottom_right = self.client.tileset.get_tile_surf("panel_bottom_right");

    #Draw the right panel.
    self.client.screen.blit(panel_right_top, 
             (self.client.screen_width - panel_right_top.get_width(), 0));
    height = (self.client.screen_height - panel_right_top.get_height());
    for y in range (height / panel_right_center.get_height() + 1): 
      y2 = panel_right_top.get_height() + y * panel_right_center.get_height();
      self.client.screen.blit(panel_right_center, 
             (self.client.screen_width - panel_right_center.get_width(), y2));

    #Draw the bottom panel
    self.client.screen.blit(panel_bottom_left, 
             (0, self.client.screen_height - panel_bottom_left.get_height()));

    width = (self.client.screen_width - panel_bottom_right.get_width() - 
	      - panel_bottom_left.get_width() - panel_right_center.get_width());
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
        self.client.rotate_position = self.client.rotate_position + 1;
        if (self.client.rotate_position > 12):
            self.client.rotate_position = 1;
        logging.info("rotate = %r" % self.client.rotate_position);

  def rotateleft(self, obj):
    if self.client.myturn == True:
        self.client.rotate_position = self.client.rotate_position - 1;
        if (self.client.rotate_position < 1):
            self.client.rotate_position = 12;
        logging.info("rotate = %r" % self.client.rotate_position);

  def increasepower(self, obj):
    if self.client.myturn == True:
        self.firepower = self.firepower + 1;
        if self.firepower > 15:
            self.firepower = 15;
        logging.info("current power = %r" % self.firepower);

  def decreasepower(self, obj):
    if self.client.myturn == True:
        self.firepower = self.firepower - 1;
        if self.firepower < 1:
            self.firepower = 1;
        logging.info("current power = %r" % self.firepower);

  def choosehub(self, obj):
    if self.client.myturn == True:
        logging.info("hub selected");
        self.client.selected_weap = 'hub';

  def choosebomb(self, obj):
    if self.client.myturn == True:
        logging.info("bomb selected");
        self.client.selected_weap = 'bomb';

  def use_firebutton(self, obj):
    if self.client.myturn == True:
        for unit in self.client.selected_unit.values():
            self.client.netclient.launch_unit(unit.id, self.client.selected_weap, self.client.rotate_position, self.firepower);

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

