import os
import sys
import gvars
import pygame
from pygame.locals import *
import screen2
import gooeypy as gui
from gooeypy.const import *

def main():
	gvars.clock = pygame.time.Clock()
	gui.init()
	gvars.appRunning = True
	#gvars.debugApp = gui.App(width=640, height=480)
	while gvars.appRunning:
		"""This following line along with the similar line above are part of another potential glitch issue that I'm curious about. The program works correctly with it the way I have it now but this seems a little ugly because we keep redefining debugApp instead of just doing it once. However if we don't redefine it every time then sections of screen2 will remain every time we go back to screen1. You can see this for yourself by flipping the comments between the two lines. On a side note I also tried redefining debugApp on screen2 just to see if this resolves the text input bug I working with"""
		gvars.debugApp = gui.App(width=640, height=480)


		gvars.activeScreen = mainMenu()
		gvars.debugApp.add(gvars.activeScreen)
		gvars.screenRunning = True
		while gvars.screenRunning:
		    if gvars.appRunning == False:
			gvars.screenRunning = False
		    gvars.clock.tick(30)

		    events = pygame.event.get()

		    for event in events:
			if event.type == QUIT:
			    gvars.appRunning = False

		    gvars.debugApp.run(events)
		    gvars.debugApp.draw()

		    gui.update_display()

def mainMenu():
	mainMenuScreen = gui.Container(width=640, height=480)
	input1 = gui.Input(x=300, y=30, width=150)
	input1.value = gvars.inputvalue1
	screen2button = gui.Button("Settings", x=20, y=230)
	quit = gui.Button("quit", x=20, y=330)
	mainMenuScreen.add(screen2button,quit,input1)
	
	screen2button.connect(CLICK, clickButton)
	
	quit.connect(CLICK, quitButton)
	return mainMenuScreen


def clickButton():
	gvars.debugApp.remove(gvars.activeScreen)
	screen2.second_menu()


def quitButton():
	gvars.appRunning = False
