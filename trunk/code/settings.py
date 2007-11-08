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

def main_settings(game):
    #this is the 'main' settings menu
    settingsloop = True
    while settingsloop == True:
        buttons = [((10,10), game.textbutton("Change Resolution"), "resolution"),
                  ((10,100), game.textbutton("Toggle Fullscreen"), "fullscreen"),
                  ((10,200), game.textbutton("Change User Name"), "username"),
                  ((10,300), game.textbutton("return to Main Menu"), "quit")]
        setinput = game.buttoninput(buttons)
        if setinput == "resolution":
            change_resolution(game)
        if setinput == "fullscreen":
            toggle_fullscreen(game)
        if setinput == "username":
            change_username(game)
        if setinput == "quit":
           settingsloop = False
    save_settings(game)

def game_settings(game):
    #this will be for mid-game settings
    print("placeholder")

def change_username(game):
    #sets custom user name for player
    text = game.showtext("Enter new user name", (0,0))
    game.playername = (game.input())
    game.surface.fill(color.black)
    print(game.playername)
    
def change_resolution(game):
    text = game.showtext("Enter X dimension", (0,0))
    game.WINDOW_XSIZE = int(game.input())
    game.erasetext(text)
    text = game.showtext("Enter Y dimension", (0,0))
    game.WINDOW_YSIZE = int(game.input())
    game.WINDOW_SIZE = game.WINDOW_XSIZE,game.WINDOW_YSIZE
    pygame.display.set_mode(game.WINDOW_SIZE)
    game.surface.fill(color.black)

def toggle_fullscreen(game):
    if game.FULLSCREEN == True:
        game.FULLSCREEN = False
        game.WINDOW_SIZE = game.WINDOW_XSIZE,game.WINDOW_YSIZE
        pygame.display.set_mode(game.WINDOW_SIZE)
    else:
        game.FULLSCREEN = True
        pygame.display.set_mode(game.WINDOW_SIZE, pygame.FULLSCREEN)
        game.surface.fill(color.black)

def load_settings(game):
    badsettings = True
    if os.path.exists("moon.sys"):
        settingsfile=open("moon.sys", 'r')
        for line in settingsfile:
            line=line.strip()
            if line == "" or line[0] == "#":
                continue
            input_array = line.split("=", 1)
            if input_array[0].strip() == "version":
                if int(input_array[1].strip()) == game.settingsversion: #checking file version to avoid incompatibilities
                    badsettings = False #confirmation that file exists and has correct version
            if badsettings == False:
                if input_array[0].strip() == "fullscreen":
                    if input_array[1].strip() == "True":
                        game.FULLSCREEN = True
                    elif input_array[1].strip() == "False":
                        game.FULLSCREEN = False
                if input_array[0].strip() == "xres":
                    game.WINDOW_XSIZE = int(input_array[1].strip())
                if input_array[0].strip() == "yres":
                    game.WINDOW_YSIZE = int(input_array[1].strip())
                if input_array[0].strip() == "name":
                    game.playername = input_array[1].strip()
    if badsettings == True:
        default_settings(game)
    else:
        game.WINDOW_SIZE = game.WINDOW_XSIZE,game.WINDOW_YSIZE
    if game.FULLSCREEN == True:
        pygame.display.set_mode(game.WINDOW_SIZE, pygame.FULLSCREEN)
    else:
        pygame.display.set_mode(game.WINDOW_SIZE)

def save_settings(game):
    savesettings=open("moon.sys", 'w')
    savesettings.write("version="+str(game.settingsversion)+"\n")
    savesettings.write("fullscreen="+str(game.FULLSCREEN)+"\n")
    savesettings.write("xres="+str(game.WINDOW_XSIZE)+"\n")
    savesettings.write("yres="+str(game.WINDOW_YSIZE)+"\n")
    savesettings.write("name="+str(game.playername)+"\n")

def default_settings(game):
    game.WINDOW_SIZE = game.WINDOW_XSIZE,game.WINDOW_YSIZE = 640,480
    game.FULLSCREEN = False
    game.playername = "Commander"
    save_settings(game)


class color:#fixme: this is an ugly hack to get settings up and running. 
    def __getattr__(self, name):
        return pygame.Color(name)
    __getitem__ = __getattr__
color = color()
