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
        self.client = clientstate

        self.app = gui.App()
        self.app.connect(gui.QUIT, self.app.quit, None)
        container = gui.Container(align=-1, valign=-1)


        self.minimap_rect = pygame.Rect(self.client.screen_width - 124 , 9, 120, 107)

        self.minimap = Minimap(clientstate, self.minimap_rect.left , self.minimap_rect.top, 120, 107)


        self.input_rect = pygame.Rect(1, self.client.screen_height - 14, self.client.screen_width - 250, 14)
        self.msgview_rect = pygame.Rect(1, self.client.screen_height - 72, self.client.screen_width - 250, 50)

        self.chat_table = gui.Table(width=self.msgview_rect.width,height=self.msgview_rect.height)

        self.chat_table.tr()
        self.lines = gui.Table()
        self.message_out = StringStream(self.lines)
        self.box = gui.ScrollArea(self.lines, self.msgview_rect.width, self.msgview_rect.height)

        self.chat_table.td(self.box) 

        self.chat_table.tr()
        self.line = gui.Input()
        self.line.style.width = self.input_rect.width
        self.line.style.height = self.input_rect.height
        self.chat_table.td(self.line) 

        self.chat_table.tr()
        self.chat_table.td(MySpacer(1,1, self.box))

        container.add(self.chat_table, self.msgview_rect.left, self.msgview_rect.top)


        self.bomb_button = gui.Button(_(" bomb "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.80, self.client.screen.get_height() * 0.20)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.choosebomb, None)

        self.hub_button = gui.Button(_(" anti-air " ))
        container.add(self.hub_button, self.client.screen.get_width() * 0.89, self.client.screen.get_height() * 0.20)
        self.hub_button.connect(gui.MOUSEBUTTONDOWN, self.chooseantiair, None)

        self.bomb_button = gui.Button(_(" bridge "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.80, self.client.screen.get_height() * 0.25)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.choosebridge, None)

        self.bomb_button = gui.Button(_(" tower "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.89, self.client.screen.get_height() * 0.25)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.choosetower, None)

        self.bomb_button = gui.Button(_(" repair "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.80, self.client.screen.get_height() * 0.30)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.chooserepair, None)

        self.bomb_button = gui.Button(_(" cluster "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.89, self.client.screen.get_height() * 0.30)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.choosecluster, None)

        self.bomb_button = gui.Button(_(" recall "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.80, self.client.screen.get_height() * 0.35)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.chooserecall, None)

        self.bomb_button = gui.Button(_(" spike "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.89, self.client.screen.get_height() * 0.35)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.choosespike, None)

        self.bomb_button = gui.Button(_(" balloon "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.80, self.client.screen.get_height() * 0.40)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.chooseballoon, None)

        self.bomb_button = gui.Button(_(" EMP "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.89, self.client.screen.get_height() * 0.40)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.chooseEMP, None)

        self.bomb_button = gui.Button(_(" missile "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.80, self.client.screen.get_height() * 0.45)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.choosemissile, None)

        self.bomb_button = gui.Button(_(" mines "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.89, self.client.screen.get_height() * 0.45)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.choosemines, None)

        self.bomb_button = gui.Button(_(" crawler "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.80, self.client.screen.get_height() * 0.50)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.choosecrawler, None)

        self.bomb_button = gui.Button(_(" collector "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.89, self.client.screen.get_height() * 0.50)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.choosecollector, None)

        self.bomb_button = gui.Button(_(" hub "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.80, self.client.screen.get_height() * 0.55)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.choosehub, None)

        self.bomb_button = gui.Button(_(" offense "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.89, self.client.screen.get_height() * 0.55)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.chooseoffense, None)

        self.bomb_button = gui.Button(_(" shield "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.80, self.client.screen.get_height() * 0.60)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.chooseshield, None)

        self.bomb_button = gui.Button(_(" virus "))
        container.add(self.bomb_button, self.client.screen.get_width() * 0.89, self.client.screen.get_height() * 0.60)
        self.bomb_button.connect(gui.MOUSEBUTTONDOWN, self.choosevirus, None)

        self.rotate_leftbutton = gui.Button(_("  <  "))
        container.add(self.rotate_leftbutton, self.client.screen.get_width() * 0.80, self.client.screen.get_height() * 0.70)
        self.rotate_leftbutton.connect(gui.MOUSEBUTTONDOWN, self.rotateleft, None)

        self.rotate_rightbutton = gui.Button(_("  >  "))
        container.add(self.rotate_rightbutton, self.client.screen.get_width() * 0.92, self.client.screen.get_height() * 0.70)
        self.rotate_rightbutton.connect(gui.MOUSEBUTTONDOWN, self.rotateright, None)

        self.firebutton = gui.Button(_(" Fire "))
        container.add(self.firebutton, self.client.screen.get_width() * 0.86, self.client.screen.get_height() * 0.70)
        self.firebutton.connect(gui.MOUSEBUTTONDOWN, self.use_firebutton, None)

        self.firebutton = gui.Button(_(" skip "))
        container.add(self.firebutton, self.client.screen.get_width() * 0.86, self.client.screen.get_height() * 0.65)
        self.firebutton.connect(gui.MOUSEBUTTONDOWN, self.use_skipbutton, None)

        """self.uppower_button = gui.Button(_(" + "))
        container.add(self.uppower_button, self.client.screen.get_width() * 0.89, self.client.screen.get_height() * 0.85)
        self.uppower_button.connect(gui.MOUSEBUTTONDOWN, self.increasepower, None)

        self.downpower_button = gui.Button(_(" - "))
        container.add(self.downpower_button, self.client.screen.get_width() * 0.82, self.client.screen.get_height() * 0.85)
        self.downpower_button.connect(gui.MOUSEBUTTONDOWN, self.decreasepower, None)"""

        self.app.init(container) 
        self.draw_panel()


#****************************************************************************
# Draws the panel background.
#****************************************************************************
    def draw_panel(self):
        panel_right_top = self.client.tileset.get_tile_surf("panel_right_top")
        panel_right_center = self.client.tileset.get_tile_surf("panel_right_center")
        #panel_bottom_left = self.client.tileset.get_tile_surf("panel_bottom_left")
        #panel_bottom_top = self.client.tileset.get_tile_surf("panel_bottom_top")
        panel_bottom_right = self.client.tileset.get_tile_surf("panel_bottom_right")

        energy_indicator_background = self.client.tileset.get_tile_surf("energy_indicator_background")


        #draw the energy indicator background
        self.client.screen.blit(energy_indicator_background, (self.client.screen_width - panel_right_top.get_width() - energy_indicator_background.get_width() + 32, 0))


        if self.client.energy > 0:
            temp_loc = 680
            red = 255 - (self.client.energy * 7)
            green = self.client.energy * 7
            temp_color = (red, green, 10)
            for show_energy in range(1, self.client.energy + 1):
                pygame.draw.line(self.client.screen, temp_color, (705, temp_loc), (755, temp_loc), 10)
                temp_loc = temp_loc - 15
        #Draw the right panel.
        self.client.screen.blit(panel_right_top, (self.client.screen_width - panel_right_top.get_width(), 0))
        height = (self.client.screen_height - panel_right_top.get_height())
        for y in range (height / panel_right_center.get_height() + 1): 
            y2 = panel_right_top.get_height() + y * panel_right_center.get_height()
            self.client.screen.blit(panel_right_center, (self.client.screen_width - panel_right_center.get_width(), y2))
        temp_loc = 780

        if self.client.firepower != 0:
            for show_power in range(1, (self.client.firepower + 1)): #display power bar
                temp_loc = temp_loc + 7
                pygame.draw.line(self.client.screen, (255,10,10), (temp_loc, 24), (temp_loc, 96), 1)


        for selected in self.client.selected_unit.values(): #prevent offenses from launching non-weapons
            if selected.type.id == "offense" and self.client.game.get_unit_typeset(self.client.selected_weap) != "weap":
                self.client.moonaudio.narrate("invalid_choice.ogg")
                self.client.selected_weap = "bomb"

        #display the currently selected unit/weapon
        unit_surface = self.client.tileset.get_unit_surf_from_tile(self.client.selected_weap, 0, self.client.playerID)
        blit_x = self.client.screen.get_width() * 0.86
        blit_y = self.client.screen.get_height() * 0.80
        self.client.screen.blit(unit_surface, (blit_x, blit_y))

        if self.client.heldbutton == "firing":
            self.client.holdbutton.firing()


        self.app.repaint()
        self.app.update(self.client.screen)


#****************************************************************************
# Draws the mini map to the screen.
#****************************************************************************
    def draw_minimap(self):
        self.minimap.draw()
        self.draw_panel()
    
#****************************************************************************
#
#****************************************************************************
    def show_message(self, text):
        self.message_out.write(text) 
        self.line.focus()


#****************************************************************************
# User clicked enter
#****************************************************************************
    def send_chat(self):
        input_text = str(self.line.value)
        if (input_text == ""): return
        self.line.value = ""
        self.client.netclient.send_chat(input_text)

#****************************************************************************
# Handles mouse click events.
#****************************************************************************
    def handle_mouse_click(self, pos):
        (x, y) = pos
        if self.minimap_rect.collidepoint(x, y):
          self.minimap.handle_mouse_click(pos)


#****************************************************************************
# Handle button inputs
#****************************************************************************
    def rotateright(self, obj):
        if self.client.myturn == True:
            self.client.heldbutton = "right"

    def rotateleft(self, obj):
        if self.client.myturn == True:
            self.client.heldbutton = "left"

    def increasepower(self, obj):
        if self.client.myturn == True:
            self.client.heldbutton = "increase"

    def decreasepower(self, obj):
        if self.client.myturn == True:
            self.client.heldbutton = "decrease"

    def use_firebutton(self, obj):
        if self.client.myturn == True:
            self.client.heldbutton = "firing"

    def choosebomb(self, obj):
        if self.client.myturn == True:
            if self.client.energy < self.client.game.get_unit_cost("bomb"):
                self.client.moonaudio.narrate("no_energy.ogg")
            else:
                self.client.selected_weap = "bomb"

    def chooseantiair(self, obj):
            if self.client.energy < self.client.game.get_unit_cost("antiair"):
                self.client.moonaudio.narrate("no_energy.ogg")
            else:
                self.client.selected_weap = "antiair"

    def choosebridge(self, obj):
        if self.client.myturn == True:
            if self.client.energy < self.client.game.get_unit_cost("bridge"):
                self.client.moonaudio.narrate("no_energy.ogg")
            else:
                self.client.selected_weap = "bridge"

    def choosetower(self, obj):
        if self.client.energy < self.client.game.get_unit_cost("tower"):
            self.client.moonaudio.narrate("no_energy.ogg")
        else:
            self.client.selected_weap = "tower"

    def chooserepair(self, obj):
        if self.client.energy < self.client.game.get_unit_cost("repair"):
            self.client.moonaudio.narrate("no_energy.ogg")
        else:
            self.client.selected_weap = "repair"

    def choosecluster(self, obj):
        if self.client.energy < self.client.game.get_unit_cost("cluster"):
            self.client.moonaudio.narrate("no_energy.ogg")
        else:
            self.client.selected_weap = "cluster"

    def chooserecall(self, obj):
        if self.client.energy < self.client.game.get_unit_cost("recall"):
            self.client.moonaudio.narrate("no_energy.ogg")
        else:
            self.client.selected_weap = "recall"

    def choosespike(self, obj):
        if self.client.energy < self.client.game.get_unit_cost("spike"):
            self.client.moonaudio.narrate("no_energy.ogg")
        else:
            self.client.selected_weap = "spike"

    def chooseballoon(self, obj):
        self.client.moonaudio.narrate("disabled.ogg")

    def chooseEMP(self, obj):
        if self.client.myturn == True:
            if self.client.energy < self.client.game.get_unit_cost("emp"):
                self.client.moonaudio.narrate("no_energy.ogg")
            else:
                self.client.selected_weap = "emp"

    def choosemissile(self, obj):
        self.client.moonaudio.narrate("disabled.ogg")

    def choosemines(self, obj):
        if self.client.myturn == True:
            if self.client.energy < self.client.game.get_unit_cost("mines"):
                self.client.moonaudio.narrate("no_energy.ogg")
            else:
                self.client.selected_weap = "mines"

    def choosecrawler(self, obj):
        if self.client.myturn == True:
            if self.client.energy < self.client.game.get_unit_cost("crawler"):
                self.client.moonaudio.narrate("no_energy.ogg")
            else:
                self.client.selected_weap = "crawler"

    def choosecollector(self, obj):
        if self.client.myturn == True:
            if self.client.energy < self.client.game.get_unit_cost("collector"):
                self.client.moonaudio.narrate("no_energy.ogg")
            else:
                self.client.selected_weap = "collector"

    def choosehub(self, obj):
        if self.client.myturn == True:
            if self.client.energy < self.client.game.get_unit_cost("hub"):
                self.client.moonaudio.narrate("no_energy.ogg")
            else:
                self.client.selected_weap = "hub"

    def chooseoffense(self, obj):
        if self.client.myturn == True:
            if self.client.energy < self.client.game.get_unit_cost("offense"):
                self.client.moonaudio.narrate("no_energy.ogg")
            else:
                self.client.selected_weap = "offense"

    def chooseshield(self, obj):
        if self.client.energy < self.client.game.get_unit_cost("shield"):
            self.client.moonaudio.narrate("no_energy.ogg")
        else:
            self.client.selected_weap = "shield"

    def choosevirus(self, obj):
        if self.client.myturn == True:
            if self.client.energy < self.client.game.get_unit_cost("virus"):
                self.client.moonaudio.narrate("no_energy.ogg")
            else:
                self.client.selected_weap = "virus"

    def use_skipbutton(self, obj):
        self.client.netclient.skip_round()

#****************************************************************************
# Hack, to scroll to the latest new message.
#****************************************************************************
class MySpacer(gui.Spacer):
    def __init__(self,width,height,box,**params):
        params.setdefault('focusable', False)
        self.box = box
        gui.widget.Widget.__init__(self,width=width,height=height,**params)

#****************************************************************************
# 
#****************************************************************************
    def resize(self,width=None,height=None):
        self.box.set_vertical_scroll(65535)
        return 1,1

#****************************************************************************
# 
#****************************************************************************
class StringStream:

    def __init__(self, lines):
        self.lines = lines

    def write(self,data):
        self.lines.tr()
        self.lines.td(gui.Label(str(data)),align=-1)

