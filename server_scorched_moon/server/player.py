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

# this class handles information for each player

class Player():
    def __init__(self, client):
        logging.debug("")
        self.username = "guest"
        self.client = client
        self.tcurses = []
        self.raw = True
        self.status = "splash" #key status that keeps track of what player is doing to give commands context
        self.guest = True
        self.energy = 0
        self.channel = "looking_for_game"
        self.team = 0 # team 0 is specifically reserved for players not on a team
        self.dropped = False #whether players client has dropped or not
