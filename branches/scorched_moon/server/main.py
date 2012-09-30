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

    def __init__(self, debug, skipintro):

        self.server = ServerState

        telnet_server = TelnetServer(
            port=6112,
            address='',
            on_connect=self.server.on_connect,
            on_disconnect=self.server.on_disconnect,
            timeout = .05
            )

        print(">> Listening for connections on port %d.  CTRL-C to break."
            % telnet_server.port)

        ## Server Loop
        while SERVER_RUN:
            telnet_server.poll()
            #self.server.process_game()

        print(">> Server shutdown.")
