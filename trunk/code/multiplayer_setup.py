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

def multiplayer_screen(game)
    menuloop = True
    while menuloop == True:
        buttons = [((10,10), game.textbutton("Host game"), "host"),
                  ((10,100), game.textbutton("Join game"), "join"),
                  ((10,200), game.textbutton("Cancel"), "quit")]
        menuinput = game.buttoninput(buttons)
        if menuinput == "host":
            host_screen(game)
        if menuinput == "join":
            join_screen(game)
        if menuinput == "quit":
            menuloop = False

def host_screen(game)
    print("host_screen placeholder")

def join_screen(game)
    print("join_screen placeholder")

def debug_game(game)
    #this is to allow 'cheating' for debugging purposes
    game.debugmode = True

