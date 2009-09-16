"""Copyright 2009:
    Isaac Carroll, Kevin Clement, Jon Handy, David Carroll, Daniel Carroll

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
from twisted.internet import reactor
from twisted.spread import pb
from twisted.cred.credentials import UsernamePassword
import cPickle
import zlib

#****************************************************************************
#
#****************************************************************************
"""Code for handling both incoming and outgoing networks commands for the client, equivalent to connectionhandler.py for the server. Everything with 'remote' in front of it is an incoming command from the server."""
class NetworkClient(pb.Referenceable):
    def __init__(self, clientstate):
        self.perspective = None
        self.client = clientstate

#****************************************************************************
# Todo: Add error handling
#****************************************************************************
    def network_handle(self, string):
        data = zlib.decompress(string)
        object = cPickle.loads(data)
        return object

#****************************************************************************
#
#****************************************************************************
    def network_prepare(self, object):
        data = cPickle.dumps(object)
        compressed = zlib.compress(data)
        return compressed


#****************************************************************************
# connect to server
#****************************************************************************
    def connect(self, server, serverPort, username):
        self.server = server
        self.serverPort = serverPort
        self.username = username
        factory = pb.PBClientFactory()
        reactor.connectTCP("localhost", 6112, factory)
        df = factory.login(UsernamePassword("guest", "guest"), self)
        df.addCallback(self.connected)
        reactor.run()

#****************************************************************************
# command for server to setup game
#****************************************************************************    
    def start_server_game(self):
        self.perspective.callRemote('init_game')

#****************************************************************************
# command to actually fire something
#****************************************************************************
    def launch_unit(self, parentID, unit, rotation, power):
        self.perspective.callRemote('launch_unit', parentID, unit, rotation, power)

#****************************************************************************
# command that player is 'skipping' this turn
#****************************************************************************
#After being run once this should be run every time this clients turn comes around until server reports that the entire round is over."""
    def skip_round(self):
        self.perspective.callRemote('skip_round')

    def success(self, message):
        logging.info("Message received: %s" % message)

    def failure(self, error):
        logging.info("error received:")
        reactor.stop()

    def connected(self, perspective):
        self.perspective = perspective
        perspective.callRemote('login', self.username, self.client.settings.version).addCallback(self.login_result)
        logging.info("connected.")

#****************************************************************************
# recieve login information from server
#****************************************************************************
    def login_result(self, result):
        if result == "login_failed":
            logging.info("Server denied login")
        else:
            self.client.playerID = result
            logging.info("Server accepted login")
            logging.info("Your playerID = %r" % self.client.playerID)
            self.client.enter_pregame()

#****************************************************************************
# send chat information
#****************************************************************************
    def send_chat(self, message):
        data = self.network_prepare(message)
        self.perspective.callRemote('send_chat', data)


    def error(self, failure, op=""):
        logging.info('Error in %s: %s' % (op, str(failure.getErrorMessage())))
        if reactor.running:
            reactor.stop()


# Methods starting with remote_ can be called by the server. (basically incoming message)
    def remote_chat(self, message):
        if self.client.mappanel:
            self.client.mappanel.show_message(message)
        if self.client.pregame:
            self.client.pregame.show_message(message)

    def remote_network_sync(self):
        logging.info("* Network sync")
        self.client.game_next_phase()

#****************************************************************************
# recieve confirmation from server that units have been placed on map and to go ahead and begin movement
#****************************************************************************
    def remote_confirmation(self):
        self.client.confirmed()

#****************************************************************************
# recieve updated unit information
#****************************************************************************
    def remote_unit_list(self, net_unit_list):
        self.client.map.unitstore = self.network_handle(net_unit_list)

#****************************************************************************
# recieve updated map information
#****************************************************************************
    def remote_map(self, net_map):
        self.client.map.mapstore = self.network_handle(net_map)

    def remote_start_client_game(self):
        self.client.pregame.start_game()

#****************************************************************************
# recieve assigned playerID from server
#****************************************************************************
    def remote_get_playerID(self, playerID):
        self.client.playerID = playerID

#****************************************************************************
# recieve command to restore energy and begin a new round
#****************************************************************************
    def remote_next_round(self):
        self.client.current_energy = self.client.stored_energy
        #todo: add code to calculate stored energy for next turn

#****************************************************************************
# recieve command to make an explosion sound
#****************************************************************************
    def remote_go_boom(self):
        self.client.moonaudio.sound("mediumboom.ogg")

#****************************************************************************
# recieve command identifying which players turn it is
#****************************************************************************
    def remote_next_turn(self, next_player):
        if next_player == self.client.playerID:
            self.client.myturn = True
            logging.info("It's your turn commander")
        else:
            self.client.myturn = False
            logging.info("It is player %r turn" % next_player)

