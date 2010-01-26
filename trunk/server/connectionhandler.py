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
from twisted.spread import pb
from twisted.cred.portal import IRealm
import cPickle
import zlib

from conninfo import *


#****************************************************************************
#
#****************************************************************************
"""Code for handling both incoming and outgoing networks commands for the server, equivalent to networkclient.py for the client. Everything with 'perspective' in front of it is for commands coming in from a client."""
class ClientPerspective(pb.Avatar):
    def __init__(self, conn_info, conn_handler, serverstate):
        self.conn_info = conn_info
        self.state = serverstate
        self.handler = conn_handler

#****************************************************************************
# Todo: Add error handling.
#****************************************************************************
    def network_prepare(self, object):
        data = cPickle.dumps(object)
        compressed = zlib.compress(data)
        return compressed

#****************************************************************************
#
#****************************************************************************
    def network_handle(self, string):
        data = zlib.decompress(string)
        object = cPickle.loads(data)
        return object


#****************************************************************************
#client connects to game
#****************************************************************************
    def perspective_login(self, username, version):
        if version != self.state.settings.version:
            logging.warning("Server refused login due to version mismatch")
            return "login_failed"
        elif username == "server" or username == "Server": #the name 'server' is reserved for messages from the real server
            logging.warning("Server refused login due to invalid username")
            return "login_failed"
        else:                
            self.conn_info.username = username
            self.conn_info.playerID = self.state.max_players(self.handler.clients)
            self.state.playerIDs.append(self.conn_info.playerID)
            join_message = "Server: %s has joined the game as player %s" % (username, str(self.conn_info.playerID))
            self.handler.remote_all('chat', join_message)
            return self.conn_info.playerID 

#****************************************************************************
#command that everyone is ready and the game actually starts
#****************************************************************************
    def perspective_init_game(self):
        if self.state.max_players(self.handler.clients) == 1:
            solo_message = "Server: Not enough players to begin!"
            self.handler.remote_all('chat', solo_message)
        elif self.state.runningserver == False:
            self.state.runningserver = True
            self.state.setup_new_game()
            net_map = self.network_prepare(self.state.map.mapstore) 
            net_unit_list = self.network_prepare(self.state.map.unitstore) 
            self.handler.remote_all('map', net_map)
            self.handler.remote_all('unit_list', net_unit_list)
            self.handler.remote_all('start_client_game')
            self.handler.remote_all('update_energy', 11) #all players start with 11 energy
            self.state.currentplayer = 1 #player1 goes first 
            self.handler.remote_all('next_turn', self.state.currentplayer)
            self.state.takingturn = False

#****************************************************************************
# recieve command for launching a unit, signifying a players turn is done
#****************************************************************************
    def perspective_launch_unit(self, parentID, unit, rotation, power):
        if self.state.endgame == True: #when game is over no actions are permitted
            return
        self.state.waitingplayers = 0
        if self.conn_info.reload == True: #reloading units remain disabled until the end of this turn
            logging.info("reloading AA's")
            for loaded in self.conn_info.Ireloading:
                for findloaded in self.state.map.unitstore.values():
                    if findloaded.id == loaded:
                        findloaded.reloading = False
                        findloaded.disabled = True
                        self.conn_info.Idisabled.append(findloaded.id)
                        self.conn_info.undisable = True
        self.conn_info.reload = False
        self.conn_info.Ireloading = []

        nocheat = True #trying to detect cheating clients
        if self.conn_info.playerID != self.state.currentplayer:
            self.handler.remote_all("cheat_signal", self.conn_info.playerID)
            logging.critical("PlayerID " + str(self.conn_info.playerID) + " attempted to fire when it was player " + str(self.state.currentplayer) + " turn")
            nocheat = False
        if self.state.takingturn == True:
            self.handler.remote_all("cheat_signal", self.conn_info.playerID)
            logging.critical("PlayerID " + str(self.conn_info.playerID) + " attempted to fire again after they had already fired")
            nocheat = False
        else:
            self.state.takingturn = True
        for checkcheat in self.state.map.unitstore.values():
            if checkcheat.id == parentID and (checkcheat.disabled == True or checkcheat.virused == True):
                self.handler.remote_all("cheat_signal", self.conn_info.playerID)
                logging.critical("PlayerID " + str(self.conn_info.playerID) + " attempted to launch from disabled unit " + str(parentID))
                nocheat = False
        if self.conn_info.energy < self.state.game.get_unit_cost(unit): #attempting to use more energy then the player currently has simply does nothing
            self.handler.remote_all("cheat_signal", self.conn_info.playerID)
            logging.critical("PlayerID " + str(self.conn_info.playerID) + " attempted to use " + str(self.state.game.get_unit_cost(unit)) + " energy when server reports only having " + str(self.conn_info.energy + " energy!"))
            nocheat = False
        for player in self.state.deadplayers:
            if player == self.conn_info.playerID:
                self.handler.remote_all("cheat_signal", self.conn_info.playerID)
                logging.critical("PlayerID " + str(self.conn_info.playerID) + " attempted to take a turn after dying")
                nocheat = False

        if nocheat == True:
            if unit == "mines" or unit == "cluster": #handling 'split' shots
                (startx, starty, coord1X, coord1Y, coord2X, coord2Y, coord3X, coord3Y, disabled1, disabled2, disabled3) = self.state.split_trajectory(parentID, rotation, power, unit, self.conn_info)
                coord1X = int(coord1X)
                coord1Y = int(coord1Y)
                coord2X = int(coord2X)
                coord2Y = int(coord2Y)
                coord3X = int(coord3X)
                coord3Y = int(coord3Y)
                coord1 = (coord1X, coord1Y)
                coord2 = (coord2X, coord2Y)
                coord3 = (coord3X, coord3Y)
                offset = 0, 0
                self.state.deathlist = []
                if self.conn_info.undisable == True: #undisabling units caused by this player previously
                    logging.info("undisabling units")
                    for undisable in self.conn_info.Idisabled:
                        for finddisabled in self.state.map.unitstore.values():
                            if finddisabled.id == undisable :
                                finddisabled.disabled = False
                                logging.debug("undisabled a " + str(finddisabled.type.id))
                self.conn_info.undisable = False
                self.conn_info.Idisabled = []
                self.conn_info.energy = self.conn_info.energy - self.state.game.get_unit_cost(unit)
                self.handler.remote(self.conn_info.ref, "update_energy", self.conn_info.energy)
                collecting = False

                self.state.add_unit(unit, coord1, offset, self.conn_info.playerID, parentID, collecting, rotation)
                if disabled1 == False:
                    self.state.determine_hit(unit, coord1, self.conn_info)
                self.state.add_unit(unit, coord2, offset, self.conn_info.playerID, parentID, collecting, rotation)
                if disabled2 == False:
                    self.state.determine_hit(unit, coord2, self.conn_info)
                self.state.add_unit(unit, coord3, offset, self.conn_info.playerID, parentID, collecting, rotation)
                if disabled3 == False:
                    self.state.determine_hit(unit, coord3, self.conn_info)

                logging.info("added " + unit + " at: " + str(coord1X) + ", " + str(coord1Y))
                logging.info("added " + unit + " at: " + str(coord2X) + ", " + str(coord2Y))
                logging.info("added " + unit + " at: " + str(coord3X) + ", " + str(coord3Y))
                self.handler.remote_all('show_launch', startx, starty, rotation, power, unit, self.conn_info.playerID)

            else: #handling normal shots
                (startx, starty, coordX, coordY, collecting) = self.state.find_trajectory(parentID, rotation, power, unit, self.conn_info)
                coord = (coordX, coordY)
                offset = 0, 0
                self.state.deathlist = []
                if self.conn_info.undisable == True: #undisabling units caused by this player previously
                    logging.info("undisabling units")
                    for undisable in self.conn_info.Idisabled:
                        for finddisabled in self.state.map.unitstore.values():
                            if finddisabled.id == undisable:
                                finddisabled.disabled = False
                                logging.debug("undisabled a " + str(finddisabled.type.id))
                self.conn_info.undisable = False
                self.conn_info.Idisabled = []
                self.conn_info.energy = self.conn_info.energy - self.state.game.get_unit_cost(unit)
                self.handler.remote(self.conn_info.ref, "update_energy", self.conn_info.energy)
                if self.state.doubletether == False:
                    self.state.add_unit(unit, coord, offset, self.conn_info.playerID, parentID, collecting, rotation)
                else:
                    self.state.game.tether2unit(unit, coord, offset, self.conn_info.playerID, parentID, collecting, rotation)
                logging.info("added " + unit + " at: " + str(coordX) + ", " + str(coordY) + "; for playerID " + str(self.conn_info.playerID))
                if self.state.interrupted_tether == True:
                    victim = self.state.map.get_unit_from_id(self.state.game.unit_counter)
                    victim.disabled = True
                    victim.hp = 0
                elif self.state.game.get_unit_typeset(unit) == "weap":
                    self.state.determine_hit(unit, coord, self.conn_info)
                elif collecting == True:
                    self.handler.remote(self.conn_info.ref, "collecting_energy")
                self.handler.remote_all('show_launch', startx, starty, rotation, power, unit, self.conn_info.playerID)

        else: #cheaters miss their turn but no other penalty
            self.state.detonate_waiters()
            self.eliminate_players()
            net_map = self.network_prepare(self.state.map.mapstore) 
            net_unit_list = self.network_prepare(self.state.map.unitstore) 
            self.handler.remote_all("map", net_map)
            self.handler.remote_all("unit_list", net_unit_list)
            foundplayer = False
            while not foundplayer:
                self.state.currentplayer += 1
                if self.state.currentplayer > self.state.max_players(self.handler.clients):
                    logging.info("max players = %s" % self.state.max_players(self.handler.clients))
                    self.state.currentplayer = 0
                if len(self.state.skippedplayers) > 1:
                    for search in self.state.skippedplayers:
                        logging.debug("searching found skipped player# %s" % search)
                        logging.debug("currentplayer = %s" % self.state.currentplayer)
                        if search != 0:
                            if int(search) != self.state.currentplayer and self.state.currentplayer > 0:
                                logging.debug("found searching found %s" % search)
                                logging.info("currentplayer = %s" % self.state.currentplayer)
                                foundplayer = True
                else:
                    logging.debug("no skips yet")
                    if self.state.currentplayer == 0:
                        self.state.currentplayer = 1
                    foundplayer = True
                    logging.info("currentplayer = %s" % self.state.currentplayer)

            self.handler.remote_all('next_turn', self.state.currentplayer)
            self.state.takingturn = False
            

#****************************************************************************
#recieve command indicating that this player is skipping all turns until round is over
#****************************************************************************
    def perspective_skip_round(self):
        if self.state.endgame == True: #when game is over no actions are permitted
            return

        nocheat = True #trying to detect cheating clients
        if self.conn_info.playerID != self.state.currentplayer:
            self.handler.remote_all("cheat_signal", self.conn_info.playerID)
            logging.critical("PlayerID " + str(self.conn_info.playerID) + " attempted to fire when it was player " + str(self.state.currentplayer) + " turn")
            nocheat = False
        if self.state.takingturn == True:
            self.handler.remote_all("cheat_signal", self.conn_info.playerID)
            logging.critical("PlayerID " + str(self.conn_info.playerID) + " attempted to fire again after they had already fired")
            nocheat = False
        else:
            self.state.takingturn = True

        for player in self.state.deadplayers:
            if player == self.conn_info.playerID:
                self.handler.remote_all("cheat_signal", self.conn_info.playerID)
                logging.critical("PlayerID " + str(self.conn_info.playerID) + " attempted to take a turn after dying")
                nocheat = False

        if nocheat == True:
            self.state.skippedplayers.append(self.conn_info.playerID)
            #this is different from OMBC, here energy collection is performed when the player skips, not when the round actually ends. This is because of a problem with the server that prevents me from sending messages to a specific user unless that user sent the command to the server that started the function
            self.state.detonate_waiters()
            self.eliminate_players()
            self.conn_info.energy = self.state.calculate_energy(self.conn_info.playerID, self.conn_info.energy)
            self.handler.remote(self.conn_info.ref, 'update_energy', self.conn_info.energy)
            if self.conn_info.undisable == True: #undisabling units caused by this player previously
                logging.info("undisabling units")
                for undisable in self.conn_info.Idisabled:
                    for finddisabled in self.state.map.unitstore.values():
                        if finddisabled.id == undisable:
                            finddisabled.disabled = False
            self.conn_info.undisable = False
            self.conn_info.Idisabled = []
            if len(self.state.skippedplayers) > self.state.max_players(self.handler.clients): #don't forget, player0 is always skipped to avoid having a blank list so there is always 1 more skipped players then actually exist
                self.state.skippedplayers = []
                for player in self.state.deadplayers:
                    self.state.skippedplayers.append(player) #skipping dead players
                self.state.move_crawlers()
                self.handler.remote_all('next_round')
                self.state.roundplayer += 1
                if self.state.roundplayer > self.state.max_players(self.handler.clients):
                    self.state.roundplayer = 1
                self.state.currentplayer = self.state.roundplayer - 1 #remember currentplayer will be incremented soon
            foundplayer = False
            while not foundplayer:
                self.state.currentplayer += 1
                if self.state.currentplayer > self.state.max_players(self.handler.clients):
                    self.state.currentplayer = 0
                if len(self.state.skippedplayers) > 1:
                    for search in self.state.skippedplayers:
                        logging.debug("searching found skipped player# %s" % search)
                        logging.debug("currentplayer = %s" % self.state.currentplayer)
                        if search != 0:
                            if int(search) != self.state.currentplayer and self.state.currentplayer > 0:
                                logging.debug("found searching found %s" % search)
                                logging.debug("currentplayer = %s" % self.state.currentplayer)
                                foundplayer = True
                else:
                    logging.debug("no skips yet")
                    if self.state.currentplayer == 0:
                        self.state.currentplayer = 1
                    foundplayer = True
                    logging.info("currentplayer = %s" % self.state.currentplayer)


            self.state.detonate_waiters()
            self.eliminate_players()
            net_map = self.network_prepare(self.state.map.mapstore) 
            net_unit_list = self.network_prepare(self.state.map.unitstore) 
            self.handler.remote_all("map", net_map)
            self.handler.remote_all("unit_list", net_unit_list)
            self.handler.remote_all('next_turn', self.state.currentplayer)
            self.state.takingturn = False
            if self.state.endgame == True:
                self.handler.remote_all("endgame")
            self.state.game.unit_dump()

#****************************************************************************
#after all clients reports it has completed animation server sends updated map and process death
#****************************************************************************
    def perspective_unit_landed(self):
        self.state.waitingplayers += 1
        if self.state.waitingplayers == self.state.max_players(self.handler.clients):
            self.state.waitingplayers = 0
            self.state.detonate_waiters()
            self.eliminate_players()
            net_map = self.network_prepare(self.state.map.mapstore) 
            net_unit_list = self.network_prepare(self.state.map.unitstore) 
            self.handler.remote_all("map", net_map)
            self.handler.remote_all("unit_list", net_unit_list)
            foundplayer = False
            while not foundplayer:
                self.state.currentplayer += 1
                if self.state.currentplayer > self.state.max_players(self.handler.clients):
                    self.state.currentplayer = 0
                if len(self.state.skippedplayers) > 1:
                    for search in self.state.skippedplayers:
                        logging.debug("searching found skipped player# %s" % search)
                        logging.debug("currentplayer = %s" % self.state.currentplayer)
                        if search != 0:
                            if int(search) != self.state.currentplayer and self.state.currentplayer > 0:
                                logging.debug("found searching found %s" % search)
                                logging.debug("currentplayer = %s" % self.state.currentplayer)
                                foundplayer = True
                else:
                    logging.debug("no skips yet")
                    if self.state.currentplayer == 0:
                        self.state.currentplayer = 1
                    foundplayer = True
                    logging.info("currentplayer = %s" % self.state.currentplayer)
                    
            self.handler.remote_all('next_turn', self.state.currentplayer)
            self.state.takingturn = False
            if self.state.endgame == True:
                self.handler.remote_all("endgame")

#****************************************************************************
#forward chat information to all clients
#****************************************************************************
    def perspective_send_chat(self, data):
        message = self.conn_info.username + ": " + self.network_handle(data)
        self.handler.remote_all('chat', message)

#****************************************************************************
#client disconnecting from server
#****************************************************************************
    def logout(self):
        logging.info("logged out")
        del self.handler.clients[self.conn_info.ref]
        message = "Server: Player %s has left the game" % str(self.conn_info.playerID)
        self.handler.remote_all('chat', message)

#****************************************************************************
#calculate the number of players currently connected to the game
#****************************************************************************
    def eliminate_players(self):
        for playerID in self.state.playerIDs:
            isdead = True
            unskipped = True
            notdead = True
            if self.state.endgame == False:
                for unit in self.state.map.unitstore.values():
                    if unit.type.id != "tether":
                    if unit.playerID == playerID and unit.type.id == "hub":
                        isdead = False #player is proven alive if they have at least one hub
                if isdead == True:
                    for findskipped in self.state.skippedplayers: #skipping dead player if not pre-skipped
                        if findskipped == playerID:
                            unskipped = False
                    for finddead in self.state.deadplayers:
                        if finddead == playerID:
                            notdead = False
                    if unskipped == True:
                        self.state.skippedplayers.append(playerID)
                    if notdead == True: #player is now dead but wasn't dead before this moment
                        self.state.deadplayers.append(playerID)
                        logging.info("player " + str(playerID) + " has been eliminated")
                    if len(self.state.deadplayers) == self.state.max_players(self.handler.clients):
                        logging.info("game is over")
                        self.state.endgame = True
                        self.handler.remote_all("endgame")
                    logging.debug("Player " + str(playerID) + " is still dead")

#****************************************************************************
#
#****************************************************************************
class ConnectionHandler:
    __implements__ = IRealm

    def __init__(self, serverstate):
        self.state = serverstate
        self.clients = {}

#****************************************************************************
#send data to all clients
#****************************************************************************
    def remote_all(self, methodName, *args):
        dfs = [self.remote(c, methodName, *args) for c in self.clients]
        return dfs 

#****************************************************************************
#send data to a single client
#****************************************************************************
    def remote(self, client, method_name, *args):
        return client.callRemote(method_name, *args)

#****************************************************************************
#server information about each player
#****************************************************************************
    def requestAvatar(self, name, client_ref, *interfaces):
        logging.info("Client connected.")
        if pb.IPerspective in interfaces:
            address = client_ref.broker.transport.getPeer()
            playerID = 0
            energy = 0
            undisable = False
            Idisabled = []
            reload = False
            Ireloading = []
            conn_info = ConnInfo(client_ref, name, address, playerID, energy, Idisabled, reload, Ireloading)
            perspective = ClientPerspective(conn_info, self, self.state)
            self.clients[client_ref] = conn_info
            return (pb.IPerspective, perspective, perspective.logout) 
        else:
            raise NotImplementedError("no interface")


