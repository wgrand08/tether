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
from pgu import gui


#****************************************************************************
# The MainMenu class shows buttons with choices for what game-mode
# which will be used.
#****************************************************************************
class MainMenu:
    def __init__(self, client):


        self.client = client
        screen = pygame.display.set_mode((640,480),0)
        app = gui.Desktop()
        app.connect(gui.QUIT,app.quit,None)
        menutable = gui.Table(width=200,height=120)



        quitbutton = gui.Button("Quit")
        quitbutton.connect(gui.CLICK,app.quit,None)
        menutable.add(quitbutton,0,0)


        app.run(menutable)
        print"after app"
