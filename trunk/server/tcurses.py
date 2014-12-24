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
import os, sys

#custom curses library specifically for telnet connections

class Tcurses:
    def __init__(self, client):
        logging.debug("")
        self.client = client

    def clr(self): #clears the screen
        logging.debug("")
        self.client.send("\033[0m")
        self.client.send("\033[2J\033[;H")

    def pos(self, x, y):
        logging.debug("")
        self.client.send("\033[{};{}H".format(y, x))

    def splashscreen(self, image): #splashscreen displays a pregenerated ascii image that fills the entire screen
        logging.debug("")
        self.client.send("\033[0m")
        self.client.send("\033[2J\033[;H")
        logging.debug("Attempting to open image {}".format(image))
        if os.path.exists(image):
            imagefile=open(image, mode="r", encoding="utf-8")
            for line in imagefile:
                self.client.send(line)




    def test(self): 
        logging.debug("")
        self.client.send("\033[0m")
        self.client.send("\033[2J\033[;H")
        for x in range(1, 48, 2):
            for y in range(2, 24):
                if y == 1:
                    self.client.send("\033[{};{}H#".format(y, x))
                elif x == 1:
                    self.client.send("\033[{};{}H#".format(y, x))
                else:
                    self.client.send("\033[{};{}H.".format(y, x))
        self.client.send("\033[1;3HA B C D E F G H I J K L M N O P Q R S T U V W")
        self.client.send("\033[25;1H")
                
