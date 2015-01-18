"""Copyright 2015:
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

import logging
import pygame
from .pgu import gui

#this file handles is nothing more then a basic template

class MainMenu:

    def __init__(self):
        logging.debug("")
        self.testloop = True
        test_menu = gui.Desktop(theme=gui.Theme("data/themes/default/"))
        test_table = gui.Table(width=800,height=600)
        gui_button = gui.Button("Quit")
        gui_button.connect(gui.CLICK,self.test1,)
        test_table.tr()
        test_table.td(gui_button)

        counting = 0
        test_menu.init(test_table)
        while self.testloop:
            print("we are counting {}" .format(counting))
            counting += 1
            test_menu.loop()

    def test1(self):
        self.testloop = False
