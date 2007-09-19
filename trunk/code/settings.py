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

def main_settings(game):
    #this is the 'main' settings menu
    settingsloop = True
    while settingsloop == True:
        text = game.showtext("Enter 1 for resolution", (0,0))
        text2 = game.showtext("Enter 2 to toggle fullscreen", (0,25))
        text3 = game.showtext("Enter 0 to return to Main Menu", (0,50))
        settingsinput = int(game.input())
        if settingsinput == 0:
            settingsloop = False
        if settingsinput == 1:
            change_resolution(game)
        if settingsinput == 2:
            toggle_fullscreen(game)
    game.surface.fill(color.black)

def game_settings(game):
    #this will be for mid-game settings
    print("placeholder")

def change_resolution(game):
    text = game.showtext("Enter X dimension", (0,0))
    game.WINDOW_XSIZE = int(game.input())
    game.erasetext(text)
    text = game.showtext("Enter Y dimension", (0,0))
    game.WINDOW_YSIZE = int(game.input())
    game.WINDOW_SIZE = game.WINDOW_XSIZE,game.WINDOW_YSIZE
    pygame.display.set_mode(game.WINDOW_SIZE)
    pygame.display.flip()
    game.surface.fill(color.black)

def toggle_fullscreen(game):
    if game.FULLSCREEN == True:
        game.FULLSCREEN = False
        game.WINDOW_SIZE = game.WINDOW_XSIZE,game.WINDOW_YSIZE
        pygame.display.set_mode(game.WINDOW_SIZE)
        #pygame.display.flip()
    else:
        game.FULLSCREEN = True
        pygame.display.set_mode(game.WINDOW_SIZE, pygame.FULLSCREEN)
        game.surface.fill(color.black)

def load_settings(game):
    print("placeholder")

def save_settings(game):
    print("placeholder")
