"""Copyright 2014:
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

# this file is for useful tools and calculations 

class Tools:
    def __init__(self):
        logging.debug("")

    def name2ID(players, username): #this function is to find a players location in the player list and return it
        logging.debug("")
        counter = 0
        logging.debug("searching for ID with username: {}" .format(username))
        for checkplayer in players:
            if checkplayer.username == username:
                logging.debug("found ID {}" .format(counter))
                return counter
            else:
                counter += 1
        logging.info("unable to find ID with username ", username)

    def client2ID(players, client):
        logging.debug("")
        counter = 0
        logging.debug("searching for ID with client")
        for checkplayer in players:
            if checkplayer.client == client:
                logging.debug("found ID {}".format(counter))
                return counter
            else:
                counter += 1
        logging.info("unable to find ID with client")
