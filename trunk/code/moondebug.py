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
import moongame
import pygame

def debug_toggle(game):
    if game.debugmode == False:
        debug_game(game)
    else:
        game.debugmode = False
        pygame.display.set_caption("MoonPy")

def debug_game(game):
    pygame.display.set_caption("MoonPy Debug")
    #this function is to allow hardcoding of settings that will be configurable in solo and multiplayer setup
    game.debugmode = True
    game.imagemapsize = game.imagemapx,game.imagemapy = 3000,3000

