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
from pgu import gui


#****************************************************************************
# The MainMenu class shows buttons with choices for what game-mode
# which will be used.
#****************************************************************************
class MainMenu:
    def __init__(self, client):


        self.client = client
        screen = pygame.display.set_mode((self.client.screen_width,self.client.screen_height),0)
        self.app = gui.Desktop()
        menutable = gui.Table(width=200,height=120)
        settingsbutton = gui.Button("Settings")
        settingsbutton.connect(gui.CLICK, self.Settings)
        quitbutton = gui.Button("Quit")
        quitbutton.connect(gui.CLICK, self.Quitter)
        menutable.td(settingsbutton, 0,0)
        menutable.td(quitbutton,0,1)

        self.app.run(menutable)
        print"after app"

#****************************************************************************
# Closes the application
#****************************************************************************
    def Settings(self):
        #audio placeholder
        settingscreen.SettingsScreen(self.client).settings_menu()

#****************************************************************************
# Closes the application
#****************************************************************************
    def Quitter(self):
        print "Quitting"
        quit()
