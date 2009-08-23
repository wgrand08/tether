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
import gui
import mainmenu
"""This displays the screen that allows users to modify their settings. """
class SettingsScreen:
    def __init__(self, client):
        self.client = client

    def settings_menu(self):
        self.app = gui.Desktop()
        self.app.connect(gui.QUIT, self.app.quit, None)
        container = gui.Container(align=-1, valign=-1)
        table = gui.Table(width=300, height=220)
        table.add(gui.Widget(),0,0)

        nickname_label = gui.Label(_("Username: "))
        table.add(nickname_label,0,1)
        self.nickname_input = gui.Input(_(self.client.settings.playername))
        table.add(self.nickname_input,1,1)
        table.add(gui.Widget(width=1, height=5), 0, 2)

        self.fullscreen_label = gui.Label(_("Fullscreen:"))
        table.add(self.fullscreen_label, 0,2)

        if self.client.settings.fullscreen == True:
            self.fullscreen_select = gui.Select(value=True)
        else:
            self.fullscreen_select = gui.Select(value=False)
        self.fullscreen_select.add("True",True)
        self.fullscreen_select.add("False",False)
        table.add(self.fullscreen_select, 1,2)

        cancel_button = gui.Button(_("Cancel"))
        cancel_button.connect(gui.CLICK, self.cancel_settings, None)


        ok_button = gui.Button(_("Ok"))
        ok_button.connect(gui.CLICK, self.accept_settings, None)


        table.add(gui.Widget(), 0, 4)
        sub_table = gui.Table(width=140, height=35)
        table.add(sub_table, 1, 4)
        sub_table.add(cancel_button, 0,5)
        sub_table.add(ok_button, 1,5)

        container.add(mainmenu.MenuBackground(client=self.client, width = self.client.screen.get_width(), height = self.client.screen.get_height()), 0, 0)
        container.add(table, self.client.screen.get_width() / 2 - 150, self.client.screen.get_height() / 2 - 120)

        self.app.run(container)

#****************************************************************************
#User cancels and changes are lost
#****************************************************************************
    def cancel_settings(self, obj):
        self.app.quit()
        mainmenu.MainMenu(self.client)

#****************************************************************************
#User wishes to keep changes and settings are automatically saved
#****************************************************************************
    def accept_settings(self, obj):
        self.client.settings.playername = self.nickname_input.value
        self.client.settings.fullscreen = self.fullscreen_select.value
        self.client.settings.save_settings()
        self.app.quit()
        mainmenu.MainMenu(self.client)

        
