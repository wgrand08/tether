"""Copyright 2012:
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
import time

from gameserverstate import *


class Main:

    def on_connect(self, client):
        print "Client attempted to connect from %s" % client.addrport()
        client.send("Welcome to the Scorched Moon Server, %s.\n" % client.addrport() )

    def on_disconnect(self, client):
        print "Client disconnected from %s" % client.addrport()

    def __init__(self, debug, skipintro):

        self.server = ServerState()

        telnet_server = TelnetServer(port=6112, timeout=.05)
        telnet_server.on_connect=self.on_connect
        telnet_server.on_disconnect=self.on_disconnect

        print(">> Listening for connections on port %d.  CTRL-C to break."
            % telnet_server.port)
        self.server.runningserver = True
        ## Server Loop
        while self.server.runningserver:
            telnet_server.poll()
            self.server.process_game()

        print(">> Server shutdown.")
