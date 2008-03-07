"""Copyright 2007:
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
import gvars
import gooeypy as gui
from gooeypy.const import *

def second_menu():
	gvars.activeScreen = gui.Container(width=640, height=480)
	gvars.debugApp.add(gvars.activeScreen)
	backButton = gui.Button("Back", x=20, y=400)
	input2 = gui.Input(x=300, y=30, width=150)
	input2.value = gvars.inputvalue2
	gvars.activeScreen.add(input2,backButton)
	backButton.connect(CLICK, endScreen2)
	gvars.debugApp.add(gvars.activeScreen)
	gvars.screenRunning = True 
	while gvars.screenRunning:
	    gvars.clock.tick(30)

	    events = pygame.event.get()

	    for event in events:
		if event.type == QUIT:
		    gvars.running = False

	    gvars.debugApp.run(events)
	    gvars.debugApp.draw()	
	    gui.update_display()


def endScreen2():
	gvars.debugApp.remove(gvars.activeScreen)
	gvars.screenRunning = False
