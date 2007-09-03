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
import moon

def main_settings(game):
    #this is the 'main' settings menu
    settingsinput = int(game.input())
    if settingsinput == 6:
        #toggle_fullscreen(game)
        print("toggle fullscreen placeholder")
    print("Main settings menu placeholder")

def game_settings(game):
    #this will be for mid-game settings
    print("Game settings menu placeholder")

def change_resolution(game):
    text = game.showtext("Enter X dimension", (0,0))
    game.WINDOW_XSIZE = int(game.input())
    game.erasetext(text)
    text = game.showtext("Enter Y dimension", (0,0))
    game.WINDOW_YSIZE = int(game.input())
    game.WINDOW_SIZE = game.WINDOW_XSIZE,game.WINDOW_YSIZE
    pygame.display.set_mode(game.WINDOW_SIZE)
    pygame.display.flip()

def toggle_fullscreen(game):
    if game.FULLSCREEN == 1:
        game.FULLSCREEN = 0
        game.WINDOW_SIZE = game.WINDOW_XSIZE,game.WINDOW_YSIZE
        pygame.display.set_mode(game.WINDOW_SIZE)
        #pygame.display.flip()
    else:
        game.FULLSCREEN = 1
        pygame.display.set_mode(game.WINDOW_SIZE, pygame.FULLSCREEN)
