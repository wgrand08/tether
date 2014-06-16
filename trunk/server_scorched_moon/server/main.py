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
from server.miniboa import TelnetServer
from . import moonnet
from . import player
from . import settings
from . import tools

#the main server class that handles everything

class Main: #the main server class
    def __init__(self, debug, loglevel):

        version = "0.00.5" # server version number

        if debug: # debug overrides logging settings
            loglevel = 1

        # breaking up sessions in logfile
        logging.basicConfig(filename='logs/scorched_moon.log',level=logging.DEBUG,format='%(message)s')
        logging.critical("----------------------------------------------------------------------------------------------------------------------------")
        logging.critical("----------------------------------------------------------------------------------------------------------------------------")
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler) # clears out handler used for breaking up sessions to prepare for actual logging
        
        # start logging    
        if loglevel == 1:
            logging.basicConfig(filename='logs/scorched_moon.log',level=logging.DEBUG,format='%(levelname)s - %(asctime)s - %(module)s:%(funcName)s:%(lineno)s -- %(message)s')
        if loglevel == 2:
            logging.basicConfig(filename='logs/scorched_moon.log',level=logging.INFO,format='%(levelname)s - %(asctime)s -- %(message)s')
        if loglevel == 3:
            logging.basicConfig(filename='logs/scorched_moon.log',level=logging.WARNING,format='%(levelname)s - %(asctime)s -- %(message)s')
        if loglevel == 4:
            logging.basicConfig(filename='logs/scorched_moon.log',level=logging.ERROR,format='%(levelname)s - %(asctime)s -- %(message)s')
        
        # confirming startup status and logging
        if debug:
            print("Scorched Moon server ver. %s starting in debug mode" % version)
            print("Logging level forced to 1")
            logging.critical("Scorched Moon server ver. %s starting in debug mode" % version)
            logging.critical("Log level forced to %s" % loglevel)
        else:
            print("Scorched Moon server ver. %s started normally" % version)
            print("Logging level set to %s" % loglevel)
            logging.critical("Scorched Moon server ver. %s started normally" % version)
            logging.critical("Log level is set to %s" % loglevel)

        # setting globals
        self.settings = settings.Settings()
        self.settings.version = version
        self.settings.debug = debug
        self.player = [] # a list of player classes
        self.game = [] # a list of game classes
        self.clientlist = [] # a list of all connected clients
        netcommand = moonnet.NetCommands(self.clientlist, self.settings)


        def process_clients(): #handles commands client has sent to server
            for client in self.clientlist:
                if client.active and client.cmd_ready:
                    total_cmd = client.get_command()   
                    if total_cmd.find(" ") != -1:
                        cmd, cmd_var = total_cmd.split(" ", 1)
                    else:
                        cmd = total_cmd
                        cmd_var = ""
                    if cmd == "exit": #command to disconnect client
                        logging.info("%s disconnected intentionally" % client.address)
                        client.send("goodbye\n")
                        self.server.poll()
                        client.active = False
                    elif cmd == "shutdown": #command to shutdown entire server
                        logging.warning("Shutdown command recieved by %s" % client.address)
                        self.settings.shutdown_command = True
                    elif cmd == "broadcast": #command to send message to all clients
                        netcommand.broadcast(cmd_var)
                    elif cmd == "version": # command to provide the server version
                        netcommand.version(client)
                    elif cmd == "login": # command to log in client and recognize them as an actual player
                        self.player.append(player(client, cmd_var))
                        logging.info("%s logged in from %s" % cmd_var, client.address)
                        test = tools.arrayID(self.player, cmd_var)
                        logging.debug("identified arrayID %s " % test)
                        logging.debug("identified username = %s" % self.player[test])
                        client.send("welcome %s" % self.player[test].username)
                    else:
                        client.send("unknown %s \n" % total_cmd)
                        logging.warning("Unknown command = %s" % total_cmd)

        def client_connects(client): #called when a client first connects
            self.clientlist.append(client) 
            client.send("hello\n")
            logging.info("%s connected to server" % client.address)
            netcommand.version(client)

        def client_disconnects(client): #called when a client drops on it's own without exit command
            logging.info("%s dropped" % client.address)
            self.clientlist.remove(client)

        def get_arrayID(self, username):
            test = True #need code to search self.player list for specific username and return the arrayID

        self.server = TelnetServer(port=self.settings.serverport, on_connect=client_connects, on_disconnect=client_disconnects) #starts server
        logging.debug("Telnet Server starting on port %s" % self.settings.serverport)

        ## Server Loop
        while self.settings.runserver:
            self.server.poll()        # Send, Recv, and look for new connections
            process_clients()           # Check for client input
            if self.settings.shutdown_command == True:
                netcommand.broadcast("Server is being intentionally shutdown, Disconnecting all users")
                self.server.poll()
                for client in self.clientlist: # disconnecting clients before shutdown
                    logging.debug("goodbye %s" % client.address)
                    client.send("disconnecting\n")
                    self.server.poll()
                    client.active = False
                self.settings.runserver = False

        logging.critical("Scorched Moon server successfully shutdown")
        logging.shutdown()
        print("Scorched Moon server has been successfully shutdown") # final shutdown confirmation
