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

import sys
import logging
from miniboa import TelnetServer
import moonnet
import player

#the main server class that handles everything

class Main:
    def __init__(self, debug):

        self.debug = debug
        self.version = 0.001
        self.runserver = True
        self.shutdown_command = False
        self.serverport = 6112
        self.player = [] # a list of player classes
        self.game = [] # a list of game classes
        self.clientlist = [] # a list of all connected clients
        netcommand = moonnet.NetCommands(self.clientlist)

        if debug == True:
            print "Launching Scorched Moon server ver. %s in debug mode" % self.version
            logging.basicConfig(filename="errors.log",level=logging.DEBUG)
        else:
            print "Launching Scorched Moon server ver. %s normally" % self.version
            logging.basicConfig(filename="errors.log",level=logging.ERROR)

        def process_clients():
            for client in self.clientlist:
                if client.active and client.cmd_ready:
                    total_cmd = client.get_command()   
                    if total_cmd.find(" ") != -1:
                        cmd, cmd_var = total_cmd.split(" ", 1)
                    else:
                        cmd = total_cmd
                        cmd_var = ""
                    if cmd == "exit":
                        client.active = False
                    elif cmd == "shutdown":
                        logging.info("Shutdown command recieved by " % client.address)
                        self.shutdown_command = True
                    elif cmd == "broadcast":
                        netcommand.broadcast(cmd_var)
                    else:
                        client.send("unknown %s \n" % total_cmd)
                        client.debug("Unknown command = %s" % total_cmd)

        def client_connects(client):
            self.clientlist.append(client) 
            logging.info("%s connected to server" % client.address)
            client.send("version %s\n" % self.version)

        def client_disconnects(client):
            logging.info("%s disconnected to server" % client.address)
            client.send("Disconnecting\n")
            self.clientlist.remove(client)

        self.server = TelnetServer(port=self.serverport, on_connect=client_connects, on_disconnect=client_disconnects)

        ## Server Loop
        while self.runserver:
            self.server.poll()        # Send, Recv, and look for new connections
            process_clients()           # Check for client input
            if self.shutdown_command == True:
                netcommand.broadcast("Server is being intentionally shutdown, Disconnecting\n")
                self.server.poll()
                self.runserver = False

        print "Scorched Moon server has been successfully shutdown"
