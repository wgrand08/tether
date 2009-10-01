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
from random import *
from twisted.internet import task, reactor
from twisted.cred.portal import Portal
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.spread import pb
from twisted.cred.portal import IRealm

from common.map import * 
from common.game import * 
from common.mapgen import *
from common.settings import *
from connectionhandler import *


#****************************************************************************
#
#****************************************************************************
class ServerState:
    def __init__(self):
        self.settings = GameSettings()
        self.game = None 
        self.currentplayer = 1
        self.skippedplayers = []
        self.skippedplayers.append(0) #this can *not* be empty or next player will never be found
        self.interrupted_tether = False
        self.waitingplayers = 0
        self.totalplayers = 0
 
#****************************************************************************
#Starts a new game, loads the map, adds starting hubs
#****************************************************************************
    def setup_new_game(self):

        if not self.game:
            self.map = Map(self)
            self.game = Game(self.map)

            MapGen(self.map, self.game)

            for player in range(0, self.totalplayers):
                unplaced = True
                while unplaced: #make certain starting hub is placed on grass
                    x = randint(5, 175)
                    y = randint(5, 175)
                    tile = self.map.get_tile((x, y))
                    if tile.type == self.game.get_terrain_type("grass"):
                        unplaced = False
                self.game.create_unit('hub', (x, y), (0,0), (player + 1), 0)

            #Initialize main loop callback.
            self.loop = task.LoopingCall(self.mainloop)
            self.loop.start(1.0)


#****************************************************************************
# This method is called every second.
#****************************************************************************
    def mainloop(self):
        #place code here to find out if a player has lost all units and if so declare them dead
        self.connections.remote_all('network_sync')

#****************************************************************************
#add a unit
#****************************************************************************
    def add_unit(self, unit_type, unit_loc, offset, playerID, parentID):
        self.game.create_unit(unit_type, unit_loc, offset, playerID, parentID)

#****************************************************************************
#find and remove all units without any HP remaining
#****************************************************************************
    def process_death(self):
        #This function searches for units without any HP remaining, removes them from the game, then sets the HP of any dependent units connected to them to 0. This function then repeats the process until all dependent units are found and removed
        notclear = True 
        while notclear:
            notclear = False
            for unit in self.map.unitstore.values():
                if (unit.hp < 1 and unit.typeset != "doodad"):
                    notclear = True 
                    self.connections.remote_all('kill_unit', unit.x, unit.y, unit.typeset, unit.playerID, unit.type.id)
                    self.game.remove_unit(unit)
                    for unit2 in self.map.unitstore.values(): 
                        if unit2.parentID == unit.id:
                            unit2.hp = 0

#****************************************************************************
#Determine where a shot lands
#****************************************************************************
    def find_trajectory(self, parentID, rotation, power, child, playerID):
        unit = self.map.get_unit_from_id(parentID)
        start_tile = self.map.get_tile_from_unit(unit)
        endX = start_tile.x
        endY = start_tile.y
        self.interrupted_tether = False
        power = power + 4 #launching has minimal range
        power = power * 2 #compensating for higher map resolution
        offsetX = 0
        offsetY = 0
        for find_target in range(1, power):
            temp_rotation = rotation - 90 #following is to adjust for difference between degrees and radians
            if temp_rotation < 1:
                temp_rotation = rotation + 270
            endX = find_target * math.cos(temp_rotation / 180.0 * math.pi)
            endY = find_target * math.sin(temp_rotation / 180.0 * math.pi)
            endX = round(endX, 0)
            endY = round(endY, 0)
            endX = endX + start_tile.x
            endY = endY + start_tile.y

            #code for looping the map edges
            if endX < 0:
                endX = self.map.xsize + endX
            if endX > self.map.xsize - 1:
                endX = endX - (self.map.xsize - 1)
            if endY < 0:
                endY = self.map.ysize + endY
            if endY > self.map.ysize - 1:
                endY = endY - (self.map.ysize - 1)

            #placing tethers if applicable
            if self.game.check_tether(child) == True: #if launched unit has tethers, then place tethers
                for target in self.map.unitstore.values():
                    double_tether = False
                    tile = self.map.get_tile((endX, endY))
                    if tile.type == self.game.get_terrain_type("water"): #determine if tether lands in water
                        self.interrupted_tether = True
                        victim = self.map.get_unit_from_id(self.game.unit_counter) #find and kill partially laid tether
                        victim.hp = 0
                        self.connections.remote_all("splash")
                        return (start_tile.x, start_tile.y, endX, endY)
                    if (target.x == endX and target.y == endY): #determine if tether crosses another unit/tether
                        if (target.typeset != "doodad") and (target.parentID != parentID):
                            if target.parentID != self.game.unit_counter + 1: #prevents tether from 'crossing' itself due to rounding
                                logging.info("You crossed a tether at step %r" % find_target)
                                self.interrupted_tether = True
                                victim = self.map.get_unit_from_id(self.game.unit_counter) #find and kill partially laid tether
                                victim.hp = 0
                                return (start_tile.x, start_tile.y, endX, endY)
                            else:
                                double_tether = True #doesn't place 'doubled' tethers due to rounding
                if double_tether == False:
                    #tether didn't land on anything, ready to place tether! The following is to prevent spaces around the launching hub
                    if (rotation < 23 or rotation > 338) and find_target > 0 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 #tethers have reverse dependency compared to buildings
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent)
                    elif rotation > 22 and rotation < 67 and find_target > 1 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent)
                    elif rotation > 66 and rotation < 111 and find_target > 1 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent)
                    elif rotation > 110 and rotation < 155 and find_target > 2 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent)
                    elif rotation > 154 and rotation < 200 and find_target > 1 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent)
                    elif rotation > 199 and rotation < 245 and find_target > 1 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent)
                    elif rotation > 244 and rotation < 290 and find_target > 0 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent)
                    elif rotation > 289 and rotation < 339 and find_target > 1 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent)

        #determine if building landed on rocks or water
        if self.game.get_unit_typeset(child) == "build":
            tile = self.map.get_tile((endX, endY))
            if tile.type == self.game.get_terrain_type("rocks"): 
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter)
                victim.hp = 0
                self.connections.remote_all("hit_rock")
            elif tile.type == self.game.get_terrain_type("water"):
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter)
                victim.hp = 0
                self.connections.remote_all("splash")

            tile = self.map.get_tile((endX + 1, endY))
            if tile.type == self.game.get_terrain_type("rocks"):
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter)
                victim.hp = 0
                self.connections.remote_all("hit_rock")
            elif tile.type == self.game.get_terrain_type("water"): 
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter)
                victim.hp = 0
                self.connections.remote_all("splash")

            tile = self.map.get_tile((endX, endY + 1))
            if tile.type == self.game.get_terrain_type("rocks"):
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter) 
                victim.hp = 0
                self.connections.remote_all("hit_rock")
            elif tile.type == self.game.get_terrain_type("water"):
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter) 
                victim.hp = 0
                self.connections.remote_all("splash")

            tile = self.map.get_tile((endX + 1, endY + 1))
            if tile.type == self.game.get_terrain_type("rocks"): 
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter) 
                victim.hp = 0
                self.connections.remote_all("hit_rock")
            elif tile.type == self.game.get_terrain_type("water"): 
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter) 
                victim.hp = 0
                self.connections.remote_all("splash")

        return (start_tile.x, start_tile.y, endX, endY)

#****************************************************************************
#Find out if a unit is hit or not
#****************************************************************************
    def determine_hit(self, unit, pos):
        x, y = pos
        power = self.game.get_unit_power(unit)
        for target in self.map.unitstore.values():
            for targetx in range(target.x, target.x + 2):
                for targety in range(target.y, target.y + 2):
                    for hitx in range(x, x + 2):
                        for hity in range(y, y + 2):
                            #print"possible floats gameserverstate.py line 160: ", targetx, ", ", targety, ", ", target.x, ", ", target.y
                            if targetx == hitx and targety == hity and target.typeset != "doodad":
                                target.hp = target.hp - power

#****************************************************************************
#calculate the number of players currently connected to the game
#****************************************************************************
    def max_players(self, clients):
        q = 0
        placeholder = 0
        for q in clients:
            placeholder = placeholder + 1
        self.totalplayers = placeholder
        return placeholder
#****************************************************************************
#Calculate the amount of energy per player
#****************************************************************************
    def calculate_energy(self, playerID, energy):
        energy = energy + 7
        for unit in self.map.unitstore.values():
            if unit.playerID == playerID and unit.type == "converter" and unit.disabled == False:
                energy = energy + 1
            if unit.collecting == True:
                energy = energy + 2
        if energy > 35:
            energy = 35
        return (energy)

#****************************************************************************
#
#****************************************************************************
    def setup_network(self):
        self.connections = ConnectionHandler(self)
        portal = Portal(self.connections)
        checker = InMemoryUsernamePasswordDatabaseDontUse()
        checker.addUser("guest", "guest")
        portal.registerChecker(checker)
        reactor.listenTCP(6112, pb.PBServerFactory(portal))

#****************************************************************************
#
#****************************************************************************
    def run_network(self):

        reactor.run()

