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
import telnetlib

class Network:
    def __init__(self):
        logging.debug("")
        self.server = []
        self.connected = False
        self.buffer = ""

    def connectserver(self, address, port):
        logging.debug("")
        self.server = telnetlib.Telnet(address, port)
        self.connected = True

    def disconnectserver(self):
        logging.debug("")
        self.server.close()

    def send(self, data):
        logging.debug("")
        data = ''.join([data, "\n"])
        data = data.encode("ascii")
        self.server.write(data)

    def receive(self):
        logging.debug("")
        if self.buffer == "":
            cmd = self.server.read_until(b"\n")
            cmd = cmd.decode("ascii")
            self.buffer = cmd[:-1] #removes carriage return from string
        else:
            pass
        
