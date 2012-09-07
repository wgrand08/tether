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

import pygame
import settingscreen
import pgu


#****************************************************************************
# The MainMenu class which controls the main menu system
#****************************************************************************

class MainMenu:
    def __init__(self, client):

        print "start menu"
        gui = pgu.gui
        self.app = gui.Desktop()
        self.menucontainer = gui.Container(width=1024,height=768)

        self.settingsbutton = gui.Button("Settings")
        self.settingsbutton.connect(gui.CLICK, self.Settings)
        self.menucontainer.add(self.settingsbutton,250,200)

        self.quitbutton = gui.Button("Quit")
        self.quitbutton.connect(gui.CLICK, self.Quitter)
        self.menucontainer.add(self.quitbutton,250,250)

        self.app.run(self.menucontainer)

        print "end menu"

#****************************************************************************
# Closes the application
#****************************************************************************
    def Settings(self):
        self.menucontainer.remove(self.settingsbutton)
        #settingscreen.SettingsScreen(self.client).settings_menu()
        print "Settings"

#****************************************************************************
# Closes the application
#****************************************************************************
    def Quitter(self):
        print "Quitting"
        quit()
