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

def settings_menu():
	gvars.activeScreen = gui.Container(width=640, height=480)
	gvars.moonPyApp.add(gvars.activeScreen)
	playernamebutton = gui.Button("Playername", x=20, y=30)
	backButton = gui.Button("Back", x=400, y=30)
	gvars.activeScreen.add(playernamebutton,backButton)
	playernamebutton.connect(CLICK, set_playername)
	backButton.connect(CLICK, endSettings)	
	gvars.moonPyApp.add(gvars.activeScreen)
	gvars.screenRunning = True
	while gvars.screenRunning:
	    gvars.clock.tick(30)

	    # We do this so we can share the events with the gui.
	    events = pygame.event.get()

	    for event in events:
		if event.type == QUIT:
		    gvars.running = False

	    gvars.moonPyApp.run(events)
	    gvars.moonPyApp.draw()

	    gui.update_display()


def load_settings():
    badsettings = True
    if os.path.exists("settings.cfg"):
        settingsfile=open("settings.cfg", 'r')
        for line in settingsfile:
            line=line.strip()
            if line == "" or line[0] == "#":
                continue
            input_array = line.split("=", 1)
            if input_array[0].strip() == "version":
                if int(input_array[1].strip()) == gvars.settingsversion: #checking file version to avoid incompatibilities
                    badsettings = False #confirmation that file exists and has correct version
            if badsettings == False:
                if input_array[0].strip() == "fullscreen":
                    if input_array[1].strip() == "True":
                        gvars.FULLSCREEN = True
                    elif input_array[1].strip() == "False":
                        gvars.FULLSCREEN = False
                if input_array[0].strip() == "xres":
                    gvars.WINDOW_XSIZE = int(input_array[1].strip())
                if input_array[0].strip() == "yres":
                    gvars.WINDOW_YSIZE = int(input_array[1].strip())
                if input_array[0].strip() == "name":
                    gvars.playername = input_array[1].strip()
    if badsettings == True:
        default_settings()
    else:
        gvars.WINDOW_SIZE = gvars.WINDOW_XSIZE,gvars.WINDOW_YSIZE
    if gvars.FULLSCREEN == True:
        pygame.display.set_mode(gvars.WINDOW_SIZE, pygame.FULLSCREEN)
    else:
        pygame.display.set_mode(gvars.WINDOW_SIZE)

def save_settings():
    savesettings=open("settings.cfg", 'w')
    savesettings.write("version="+str(gvars.settingsversion)+"\n")
    savesettings.write("fullscreen="+str(gvars.FULLSCREEN)+"\n")
    savesettings.write("xres="+str(gvars.WINDOW_XSIZE)+"\n")
    savesettings.write("yres="+str(gvars.WINDOW_YSIZE)+"\n")
    savesettings.write("name="+str(gvars.playername)+"\n")

def default_settings():
    gvars.WINDOW_SIZE = gvars.WINDOW_XSIZE,gvars.WINDOW_YSIZE = 640,480
    gvars.FULLSCREEN = False
    gvars.playername = "Commander"
    save_settings()

def set_playername():
	print"set player name"

def endSettings():
	gvars.moonPyApp.remove(gvars.activeScreen)
	gvars.screenRunning = False
