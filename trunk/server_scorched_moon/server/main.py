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
from miniboa import TelnetServer

#the main server class that handles everything

class Main:

    def __init__(self, debug):

        self.debug = debug
        self.version = 0.001
        self.gameIDs = []
        self.playerIDs = []
        self.clientlist = []
        self.runserver = True
        self.shutdown_command = False
        self.serverport = 6112

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
                        self.shutdown_command = True
                    elif cmd == "broadcast":
                        broadcast(cmd_var)
                    else:
                        client.send("Unknown Command\n")

        def client_connects(client):
            print "%s connected to server" % client.address
            self.clientlist.append(client)
            client.send("Welcome to Scorched Moon version %s\n" % self.version)

        def client_disconnects(client):
            print "%s disconnected from server" % client.address
            client.send("Disconnecting you from server\n")
            self.clientlist.remove(client)

        def broadcast(cmd_var):
            msg = "Broadcast: " + cmd_var + "\n"
            for client in self.clientlist:
                client.send(msg)


        self.server = TelnetServer(port=self.serverport, on_connect=client_connects, on_disconnect=client_disconnects)

        if debug == True:
            print "Server is running in debug mode"
        else:
            print "Server is not running in debug mode"


        ## Server Loop
        while self.runserver:
            self.server.poll()        # Send, Recv, and look for new connections
            process_clients()           # Check for client input
            if self.shutdown_command == True:
                broadcast("Server is being intentionally shutdown, Disconnecting\n")
                self.server.poll()
                self.runserver = False

        print "Scorched Moon server has been successfully shutdown"
