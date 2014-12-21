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

#custom curses library specifically for telnet connections

class Tcurses:
    def __init__(self):
        logging.debug("")

    def init_client(client):
        logging.debug("")

    def clr(client): #clears the screen
        logging.debug("")
        for x in range(0, client.columns):
            for y in range(0, client.rows):
                client.send("\033[{};{}H ".format(y, x))
        client.send("columns = {}\n".format(client.columns))
        client.send("rows = {}\n".format(client.rows))

    def pos(client, x, y):
        logging.debug("")
        client.send("\033[{};{}H".format(y, x))




