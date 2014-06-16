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

    def arrayID(self, playerlist, username):
        logging.debug("")
        counter = 0
        for players in playerlist:
            if players.username == username:
                logging.debug("arrayID found ", counter)
            else:
                counter += 1
        logging.warning("arrayID unable to find username ", username)