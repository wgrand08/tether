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

import pygame
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
        reactor.connectTCP(server, 6112, factory)
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
        self.client.myturn == False
        self.perspective.callRemote('launch_unit', parentID, unit, rotation, power)

#****************************************************************************
# report completion of animation by client
#****************************************************************************
    def land_unit(self):
        self.perspective.callRemote('unit_landed')

#****************************************************************************
# command that player is 'skipping' this turn
#****************************************************************************
#After being run once this should be run every time this clients turn comes around until server reports that the entire round is over."""
    def skip_round(self):
        self.perspective.callRemote('skip_round')

#****************************************************************************
# 
#****************************************************************************
    def success(self, message):
        logging.debug("Message received: %s" % message)

#****************************************************************************
# 
#****************************************************************************
    def failure(self, error):
        logging.critical("error received from server:")
        reactor.stop()

#****************************************************************************
# 
#****************************************************************************
    def connected(self, perspective):
        self.perspective = perspective
        perspective.callRemote('login', self.username, self.client.settings.version).addCallback(self.login_result)
        
        logging.debug("connected.")

#****************************************************************************
# recieve login information from server
#****************************************************************************
    def login_result(self, result):
        if result == "login_failed":
            logging.debug("Server denied login")
        else:
            self.client.playerID = result
            logging.debug("Server accepted login")
            logging.debug("Your playerID = %r" % self.client.playerID)
            self.client.enter_pregame()
            message = "Server: Welcome player %s" % self.client.playerID
            self.client.pregame.show_message(message)

#****************************************************************************
# player disconnects from server
#****************************************************************************
    def disconnect(self):
        logging.debug("Disconnected from server")
        if reactor.running:
            reactor.stop()
        

#****************************************************************************
# send chat information
#****************************************************************************
    def send_chat(self, message):
        data = self.network_prepare(message)
        self.perspective.callRemote('send_chat', data)


    def error(self, failure, op=""):
        logging.critical('Error in %s: %s' % (op, str(failure.getErrorMessage())))
        if reactor.running:
            reactor.stop()


# Methods starting with remote_ can be called by the server. (basically incoming message)
    def remote_chat(self, message):
        if self.client.mappanel:
            self.client.mappanel.show_message(message)
        if self.client.pregame:
            self.client.pregame.show_message(message)

    def remote_network_sync(self):
        logging.debug("* Network sync")
        self.client.game_next_phase()



#****************************************************************************
# recieve updated unit information
#****************************************************************************
    def remote_unit_list(self, net_unit_list):
        self.client.map.unitstore = self.network_handle(net_unit_list)
        for unit in self.client.map.unitstore.values(): #update selected unit with updated information
            for unit2 in self.client.selected_unit.values():
                if unit.id == unit2.id:
                    map_pos = (unit.x, unit.y)
                    self.client.selected_unit = {}
                    self.client.selected_unit.update({map_pos:unit})

#****************************************************************************
# recieve updated map information
#****************************************************************************
    def remote_map(self, net_map):
        self.client.map.mapstore = self.network_handle(net_map)

#****************************************************************************
# command that server is ready for clients to begin playing
#****************************************************************************
    def remote_start_client_game(self):
        self.client.moonaudio.narrate("launching_game.ogg")
        self.client.pregame.start_game()

#****************************************************************************
# recieve launch data from server
#****************************************************************************
    def remote_show_launch(self, startx, starty, rotation, power, unit, pID):
        self.client.deathtypes = []
        self.client.deathX = []
        self.client.deathY = []
        self.client.launch_startx = startx
        self.client.launch_starty = starty
        self.client.launch_direction = rotation
        self.client.launch_distance = power
        self.client.launch_type = unit
        self.client.playerlaunched = pID
        self.client.launched = True
        self.client.moonaudio.sound("throw.ogg")
        self.client.missilelock = False
        if self.client.game.check_tether(unit) == True:
                if power < 9:
                    self.client.moonaudio.sound("shorttether.ogg")
                elif power > 8 and power < 17:
                    self.client.moonaudio.sound("mediumtether.ogg")
                elif power > 16:
                    self.client.moonaudio.sound("longtether.ogg")

#****************************************************************************
# recieve defense data from server
#****************************************************************************
    def remote_triggered_defense(self):
        logging.debug("defense triggered")
        self.client.moonaudio.sound("laser.ogg")

#****************************************************************************
# recieve unit death data from server
#****************************************************************************
    def remote_kill_unit(self, x, y, unittype, playerID, name, disabled):
        self.client.dying_unit = True
        self.client.deathtypes.append(unittype)
        self.client.deathX.append(x)
        self.client.deathY.append(y)
        self.client.deathplayerID.append(playerID)
        self.client.deathname.append(name)
        self.client.deathdisabled.append(disabled)

#****************************************************************************
# recieve assigned playerID from server
#****************************************************************************
    def remote_get_playerID(self, playerID):
        self.client.playerID = playerID

#****************************************************************************
# get energy from server
#****************************************************************************
    def remote_update_energy(self, energy):
        self.client.energy = energy
        if self.client.energy < self.client.game.get_unit_cost(self.client.selected_weap):
            self.client.selected_weap = "bomb" #game automatically switches to bomb when energy gets low

#****************************************************************************
# recieve command to restore energy and begin a new round
#****************************************************************************
    def remote_next_round(self):
        message = "Server: round over"
        self.client.mappanel.show_message(message)
        self.client.moonaudio.narrate("round_over.ogg")

#****************************************************************************
# notice of possible cheating by server
#****************************************************************************
    def remote_cheat_signal(self, playerID):
        self.client.moonaudio.narrate("cheat.ogg")
        message = "Server: Player ", str(playerID), " tried to cheat"
        if self.client.mappanel:
            self.client.mappanel.show_message(message)
        if self.client.pregame:
            self.client.pregame.show_message(message)

#****************************************************************************
# server detects something landing in water
#****************************************************************************
    def remote_splash(self):
        self.client.moonaudio.sound("watersplash.ogg")
        #self.client.splashed = True

#****************************************************************************
# server detects a building landing on a rock
#****************************************************************************
    def remote_hit_rock(self):
        self.client.hit_rock = True

#****************************************************************************
# server detects collector landing on an energy pool
#****************************************************************************
    def remote_collecting_energy(self):
        self.client.collecting_energy = True

#****************************************************************************
# server has ended the game
#****************************************************************************
    def remote_endgame(self):
        self.client.moonaudio.narrate("winner.ogg")
        message = "Server: Game Over"
        if self.client.mappanel:
            self.client.mappanel.show_message(message)
        if self.client.pregame:
            self.client.pregame.show_message(message)

#****************************************************************************
# recieve command identifying which players turn it is
#****************************************************************************
    def remote_next_turn(self, next_player):
        if next_player == self.client.playerID:
            if self.client.energy < 1:
                self.skip_round()
            else:
                message = "Server: It's your turn commander"
                if self.client.mappanel:
                    self.client.mappanel.show_message(message)
                elif self.client.pregame:
                    self.client.pregame.show_message(message)
                else:
                    logging.critical("unable to find panel for displaying message")
                self.client.myturn = True
                self.client.firepower = 0
                self.client.power_direction = "up"
                self.client.moonaudio.narrate("your_turn.ogg")
        else:
            message = "Server: It is player " + str(next_player) + "'s turn"
            self.client.mappanel.show_message(message)
            self.client.myturn = False
        logging.debug("It is player " + str(next_player) + "'s turn")

