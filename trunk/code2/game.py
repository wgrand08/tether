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


import os
import sys
import gvars
from time import sleep
import pygame
from pygame.locals import *
import settings
import gooeypy as gui
from gooeypy.const import *

def main():
	pygame.init()
	pygame.display.set_caption("MoonPy")
	drawSplashScreen()
	settings.load_settings()
	screen = pygame.display.set_mode(gvars.WINDOW_SIZE, SWSURFACE, 32)
	pygame.mouse.set_visible(1)
	blackScreen = screen.map_rgb((0x00, 0x00, 0x00))
	pygame.display.flip()
	guitest()
	sleep(2)
	print "successful end"	

def drawSplashScreen():
	image = "images/Enceladus.png"
	screen = pygame.display.set_mode((550,550))
	try:
		splashScreen = pygame.image.load(image)
	except pygame.error, message:
		print 'Cannot load splash image'
		raise SystemExit, message
	splashScreen = splashScreen.convert()
	screen.blit(splashScreen, (0,0))
	pygame.display.flip()
	sleep(2)

def guitest():
	clock = pygame.time.Clock()
	gui.init(640, 480)
	app = gui.App(width=640, height=480)
	w1 = gui.Button("reset", x=20, y=30)
	w2 = gui.Input(x=100, y=30, width=240)
	w3 = gui.Switch(x=500, y=30)
	w4 = gui.HSlider(min_value=20, length=10, x=200, y=160)
	w9 = gui.VSlider(length=40, x=600, y=160, step=False)
	l1 = gui.Label(value="Pulsate:", x=395, y=30, font_size=25)
	data = """This example is to demonstrate GooeyPy's widgets and functionality.

	You can also have line breaks."""
	tb = gui.TextBlock(value=data, x=200, y=350, width=300)
	app.add(w1,w2,w3,w4,w9,l1,tb)
	quit = False
	while not quit:
	    clock.tick(30)

	    # We do this so we can share the events with the gui.
	    events = pygame.event.get()

	    for event in events:
		if event.type == QUIT:
		    quit = True

	    app.run(events)
	    app.draw()

	    gui.update_display()

#main()
