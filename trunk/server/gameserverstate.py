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
                self.game.create_unit('hub', (x, y), (0,0), (player + 1), 0, False, 360)

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
    def add_unit(self, unit_type, unit_loc, offset, playerID, parentID, collecting, dir):
        self.game.create_unit(unit_type, unit_loc, offset, playerID, parentID, collecting, dir)

#****************************************************************************
#find and remove all units without any HP remaining
#****************************************************************************
    def process_death(self):
        #This function searches for units without any HP remaining, removes them from the game, then sets the HP of any dependent units connected to them to 0. This function then repeats the process until all dependent units are found and removed
        logging.info("process death")
        notclear = True 
        while notclear:
            notclear = False
            for unit in self.map.unitstore.values():
                if unit.typeset == "tether" and unit.hp > 0: #tethers heal between turns so they never die except by death of parent
                    unit.hp = 1000
                if (unit.hp < 1 and unit.typeset != "doodad"):
                    notclear = True 
                    self.connections.remote_all('kill_unit', unit.x, unit.y, unit.typeset, unit.playerID, unit.type.id)
                    self.game.remove_unit(unit)
                    for unit2 in self.map.unitstore.values(): 
                        if unit2.parentID == unit.id:
                            unit2.hp = 0
        self.handle_water()

#****************************************************************************
#find and move viruses
#****************************************************************************
    def process_virus(self):
        logging.info("process virus")
        for unit in self.map.unitstore.values():
            if unit.virused == True and unit.type != "build": #remove viruses from non-buildings
                unit.virused = False
                unit.just_virused = False
            if unit.virused == True and unit.just_virused == True:
                unit.just_virused = False
            if unit.virused == True and unit.just_virused == False:
                unit.virused = False
                unit.just_virused = True
                unit.hp = unit.hp - 1
                if unit.hp < 1:
                    unit.hp = 1
                for find_tethered in self.map.unitstore.values():
                    if unit.just_virused == False and (find_tethered.id == unit.parentID or find_tethered.parentID == unit.id):
                        logging.info("virus has spread to unit %s" % find_tethered.id)
                        find_tethered.virused = True
                        find_tether.just_virused = False
        self.process_death()

#****************************************************************************
#handle bridges, units in water and destruction
#****************************************************************************
    def handle_water(self): #todo: convert all death by water to this function
        logging.info("handling water")
        for unit in self.map.unitstore.values():
            tile = self.map.get_tile((unit.x, unit.y))
            if unit.type.id == "bridge":
                if tile.type != self.game.get_terrain_type("water"):
                    unit.hp = 0 #killing bridges that don't land on water
            elif unit.typeset == "build":
                if tile.type == self.game.get_terrain_type("water"):
                    gosplash = True
                    for unit2 in self.map.unitstore.values():
                        if unit2.x == unit.x and unit2.y == unit.y and unit2.type.id == "bridge":
                            gosplash = false
                    if gosplash == True:
                        unit.hp = 0
                        self.connections.remote_all("splash")
                        logging.info("went splash")
            elif unit.typeset == "tether":
                if tile.type == self.game.get_terrain_type("water"):
                    logging.info("tether in water?")
                    gosplash = True
                    for unit2 in self.map.unitstore.values():
                        if unit2.type.id == "bridge" and ((unit2.x == unit.x and unit2.y == unit.y) or ((unit2.x + 1) == unit.x and unit2.y == unit.y) or (unit2.x == unit.x and (unit2.y + 1 == unit.y)) or ((unit2.x + 1) == unit.x and (unit2.y + 1) == unit.y)):
                            gosplash = False
                    if gosplash == True:
                        logging.info("splashing a tether")
                        (target1, target2) = self.game.find_tether_ends(unit)
                        logging.info("tried destroying target1 as %s" % target1)
                        for target in self.map.unitstore.values():
                            if target.id == target1:
                                target.hp = 0
                                self.connections.remote_all("splash")
                                logging.info("went splash")

#****************************************************************************
#detonate all crawlers/mines that are too close to something
#****************************************************************************
    def detonate_waiters(self):
        logging.info("detonate waiters")
        for unit in self.map.unitstore.values():
            blasted = False
            if unit.type.id == "mines":
                power = self.game.get_unit_power(unit.type.id)
                radius = 4
                endX = unit.x
                endY = unit.y
                for find_target in range(1, radius):
                    spinner = 0
                    while spinner < 360:
                        endX = find_target * math.cos(spinner / 180.0 * math.pi)
                        endY = find_target * math.sin(spinner / 180.0 * math.pi)
                        endX = round(endX, 0)
                        endY = round(endY, 0)
                        endX = endX + unit.x
                        endY = endY + unit.y
                        for target in self.map.unitstore.values():
                            #logging.info("comparing possible targets: %s, %s - %s, %s" % (endX, endY, target.x, target.y))
                            if target.x == endX and target.y == endY and target.playerID != unit.playerID and target.typeset != "doodad":
                                unit.hp = 0 #target detonates, damage is incurred while processing death
                        spinner = spinner + 5

            elif unit.type.id == "crawler":
                power = self.game.get_unit_power(unit)
                radius = 1
                endX = unit.x
                endY = unit.y
                for find_target in range(1, radius):
                    spinner = 0
                    while spinner < 360:
                        endX = find_target * math.cos(spinner / 180.0 * math.pi)
                        endY = find_target * math.sin(spinner / 180.0 * math.pi)
                        endX = round(endX, 0)
                        endY = round(endY, 0)
                        endX = endX + unit.x
                        endY = endY + unit.y
                        for target in self.map.unitstore.values():
                            #logging.info("comparing possible targets: %s, %s - %s, %s" % (endX, endY, target.x, target.y))
                            if target.x == endX and target.y == endY and target.playerID != unit.playerID and target.typeset != "doodad":
                                unit.hp = 0 #target detonates, damage is incurred while processing death
                        spinner = spinner + 5
        self.process_virus()


#****************************************************************************
#Move all crawlers at the end of the round
#****************************************************************************
    def move_crawlers(self):
        for unit in self.map.unitstore.values(): #note, in OMBC crawlers move about half a power bar in length
            if unit.type.id == "crawler" and unit.disabled == False:
                temp_rotation = unit.dir
                start_tile = self.map.get_tile_from_unit(unit)
                for find_target in range(1, 15):
                    temp_rotation = unit.dir - 90 #following is to adjust for difference between degrees and radians
                    if temp_rotation < 1:
                        temp_rotation = unit.dir + 270
                    endX = find_target * math.cos(temp_rotation / 180.0 * math.pi)
                    endY = find_target * math.sin(temp_rotation / 180.0 * math.pi)
                    endX = round(endX, 0)
                    endY = round(endY, 0)
                    endX = endX + start_tile.x
                    endY = endY + start_tile.y
                unit.x = endX
                unit.y = endY


#****************************************************************************
#Determine where a shot lands
#****************************************************************************
    def find_trajectory(self, parentID, rotation, power, child, playerID):
        unit = self.map.get_unit_from_id(parentID)
        start_tile = self.map.get_tile_from_unit(unit)
        endX = start_tile.x #todo: can this be safely removed?
        endY = start_tile.y
        self.interrupted_tether = False
        power = power + 4 #launching has minimal range
        power = power * 2 #compensating for higher map resolution
        offsetX = 0
        offsetY = 0
        collecting = False
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
                    """if tile.type == self.game.get_terrain_type("water"): #determine if tether lands in water
                        self.interrupted_tether = True
                        victim = self.map.get_unit_from_id(self.game.unit_counter) #find and kill partially laid tether
                        victim.hp = 0
                        self.connections.remote_all("splash")
                        return (start_tile.x, start_tile.y, endX, endY, collecting)"""
                    if (target.x == endX and target.y == endY): #determine if tether crosses another unit/tether
                        if (target.typeset != "doodad") and (target.parentID != parentID):
                            if target.parentID != self.game.unit_counter + 1: #prevents tether from 'crossing' itself due to rounding
                                logging.info("You crossed a tether at step %r" % find_target)
                                self.interrupted_tether = True
                                victim = self.map.get_unit_from_id(self.game.unit_counter) #find and kill partially laid tether
                                victim.hp = 0
                                return (start_tile.x, start_tile.y, endX, endY, collecting)
                            else:
                                double_tether = True #doesn't place 'doubled' tethers due to rounding
                if double_tether == False:
                    #tether didn't land on anything, ready to place tether! The following is to prevent spaces around the launching hub
                    testX = round(endX)
                    testY = round(endX)
                    testX = str(testX)
                    testY = str(testY)
                    if (rotation < 23 or rotation > 338) and find_target > 0 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 #tethers have reverse dependency compared to buildings
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent, False, 0)
                        logging.info("added tether at " + testX + ", " + testY)
                    elif rotation > 22 and rotation < 67 and find_target > 1 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent, False, 0)
                        logging.info("added tether at " + testX + ", " + testY)
                    elif rotation > 66 and rotation < 111 and find_target > 1 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent, False, 0)
                        logging.info("added tether at " + testX + ", " + testY)
                    elif rotation > 110 and rotation < 155 and find_target > 2 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent, False, 0)
                        logging.info("added tether at " + testX + ", " + testY)
                    elif rotation > 154 and rotation < 200 and find_target > 1 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent, False, 0)
                        logging.info("added tether at " + testX + ", " + testY)
                    elif rotation > 199 and rotation < 245 and find_target > 1 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent, False, 0)
                        logging.info("added tether at " + testX + ", " + testY)
                    elif rotation > 244 and rotation < 290 and find_target > 0 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent, False, 0)
                        logging.info("added tether at " + testX + ", " + testY)
                    elif rotation > 289 and rotation < 339 and find_target > 1 and find_target < (power - 1):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (round(endX, 0), round(endY, 0)), (offsetX, offsetY), playerID, chain_parent, False, 0)
                        logging.info("added tether at " + testX + ", " + testY)

        #determine if building landed on rocks or water
        #todo: move all destruction of units by landing in water to function 'handle_water'
        if self.game.get_unit_typeset(child) == "build":
            tile = self.map.get_tile((endX, endY))
            if tile.type == self.game.get_terrain_type("rocks"):
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter)
                victim.hp = 0
                self.connections.remote_all("hit_rock")
            elif tile.type == self.game.get_terrain_type("energy"):
                collecting = True

            tile = self.map.get_tile((endX + 1, endY))
            if tile.type == self.game.get_terrain_type("rocks"):
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter)
                victim.hp = 0
                self.connections.remote_all("hit_rock")
            elif tile.type == self.game.get_terrain_type("energy"):
                collecting = True

            tile = self.map.get_tile((endX, endY + 1))
            if tile.type == self.game.get_terrain_type("rocks"):
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter) 
                victim.hp = 0
                self.connections.remote_all("hit_rock")
            elif tile.type == self.game.get_terrain_type("energy"):
                collecting = True

            tile = self.map.get_tile((endX + 1, endY + 1))
            if tile.type == self.game.get_terrain_type("rocks"): 
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter) 
                victim.hp = 0
                self.connections.remote_all("hit_rock")
            elif tile.type == self.game.get_terrain_type("energy"):
                collecting = True

        logging.info("collecting = %r" % collecting)
        return (start_tile.x, start_tile.y, endX, endY, collecting)

#****************************************************************************
#Determine where a split shot lands
#****************************************************************************
    def split_trajectory(self, parentID, rotation, power, child, playerID):
        unit = self.map.get_unit_from_id(parentID)
        start_tile = self.map.get_tile_from_unit(unit)
        endX = start_tile.x
        endY = start_tile.y
        self.interrupted_tether = False
        power = power + 4 #launching has minimal range
        power = power * 2 #compensating for higher map resolution
        offsetX = 0
        offsetY = 0
        arc = power - round((power / 2), 0) #find location where shots split
        temp_rotation = rotation - 90 #following is to adjust for difference between degrees and radians
        if temp_rotation < 1:
            temp_rotation = rotation + 270
        endX = arc * math.cos(temp_rotation / 180.0 * math.pi)
        endY = arc * math.sin(temp_rotation / 180.0 * math.pi)
        endX = round(endX, 0)
        endY = round(endY, 0)
        splitX = endX + start_tile.x
        splitY = endY + start_tile.y

        #code for looping the map edges
        if splitX < 0:
            splitX = self.map.xsize + endX
        if splitX > self.map.xsize - 1:
            splitX = endX - (self.map.xsize - 1)
        if splitY < 0:
            splitY = self.map.ysize + endY
        if splitY > self.map.ysize - 1:
            splitY = endY - (self.map.ysize - 1)

        end_arc = power - arc
        endX = end_arc * math.cos(temp_rotation / 180.0 * math.pi)
        endY = end_arc * math.sin(temp_rotation / 180.0 * math.pi)
        endX = round(endX, 0)
        endY = round(endY, 0)
        coordX1 = endX + splitX
        coordY1 = endY + splitY
        default_rotation = temp_rotation

        temp_rotation = default_rotation + 45
        if temp_rotation > 360:
            temp_rotation = default_rotation - 315

        endX = end_arc * math.cos(temp_rotation / 180.0 * math.pi)
        endY = end_arc * math.sin(temp_rotation / 180.0 * math.pi)
        endX = round(endX, 0)
        endY = round(endY, 0)
        coordX2 = endX + splitX
        coordY2 = endY + splitY

        temp_rotation = default_rotation - 45
        if temp_rotation < 1:
            temp_rotation = default_rotation + 315

        endX = end_arc * math.cos(temp_rotation / 180.0 * math.pi)
        endY = end_arc * math.sin(temp_rotation / 180.0 * math.pi)
        endX = round(endX, 0)
        endY = round(endY, 0)
        coordX3 = endX + splitX
        coordY3 = endY + splitY

        return (start_tile.x, start_tile.y, coordX1, coordY1, coordX2, coordY2, coordX3, coordY3)



#****************************************************************************
#Find out if a unit is hit or not
#****************************************************************************
    def determine_hit(self, unit, pos, player):
        x, y = pos
        power = self.game.get_unit_power(unit)
        if unit != "crawler" or unit != "mines":
            for target in self.map.unitstore.values():
                target.blasted = False
                for targetx in range(target.x, target.x + 2):
                    for targety in range(target.y, target.y + 2):
                        for hitx in range(x, x + 2):
                            for hity in range(y, y + 2):
                                #print"possible floats gameserverstate.py line 260: ", targetx, ", ", targety, ", ", target.x, ", ", target.y
                                if targetx == hitx and targety == hity and target.typeset == "build" and target.blasted == False:
                                    if unit == "repair":
                                        logging.info("repaired target for 1")
                                        target.hp = target.hp + 1
                                        logging.info("it's current HP = %s" % target.hp)
                                        if target.hp > self.game.get_unit_hp(target.type.id):
                                            target.hp = self.game.get_unit_hp(target.type.id) #prevent units from going over max HP
                                            target.blasted = True
                                    elif unit == "spike": #spike on a building
                                        target.hp = target.hp - power
                                        for target2 in self.map.unitstore.values(): #if direct hit on building, parent unit gets zapped
                                            if target2.id == target.playerID:
                                                target2.hp = target.hp - 1
                                    elif unit == "virus":
                                        target.virused = True
                                    elif unit == "recall":
                                        if target.playerID == player.playerID: #if own target, insta-death
                                            player.energy = player.energy + target.hp
                                            target.hp = 0
                                            target.blasted = True
                                        else:
                                            if target.hp < 3: #if not own target
                                                player.energy = player.energy + target.hp
                                                target.hp = 0
                                                target.blasted = True
                                            else:
                                                player.energy = player.energy + power
                                                target.hp = target.hp - power
                                                target.blasted = True
                                    else:
                                        logging.info("hit target for %s" % power)
                                        target.hp = target.hp - power
                                        target.blasted = True
                                elif targetx == hitx and targety == hity and target.typeset == "tether" and unit == "spike": #spikes landing on tethers zaps buildings on both ends
                                    (target1, target2) = self.game.find_tether_ends(target)
                                    for tetherend in self.map.unitstore.values():
                                        if tetherend.id == target1 or tetherend.id == target2:
                                            tetherend.hp = tetherend.hp - 1
                                            logging.info("spike damaged unit %s" % tetherend.id)
                                    return #spikes only affect one tether, so when one tether is hit, no further damage is calculated

        if unit == "emp":
            radius = 15 #the radius the EMP will be 15 on a side so it will be 30 from side to side, this is about half of a hubs launch range minux the minimum which appears to be how OMBC works
            endX = x
            endY = y
            for find_target in range(1, radius):
                spinner = 0
                while spinner < 360:
                    endX = find_target * math.cos(spinner / 180.0 * math.pi)
                    endY = find_target * math.sin(spinner / 180.0 * math.pi)
                    endX = round(endX, 0)
                    endY = round(endY, 0)
                    endX = endX + x
                    endY = endY + y
                    for target in self.map.unitstore.values():
                        #logging.info("comparing possible targets: %s, %s - %s, %s" % (endX, endY, target.x, target.y))
                        if target.x == endX and target.y == endY and target.typeset == "build":
                            target.disabled = True
                            player.Idisabled.append(target.id)
                            player.undisable = True
                            logging.info("you disabled a %r" % target.type.id)
                    spinner = spinner + 5


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
            if unit.playerID == playerID and unit.type.id == "collector" and unit.disabled == False:
                energy = energy + 1
                logging.info("added unpowered collector energy")
                if unit.collecting == True:
                    energy = energy + 2
                    logging.info("added powered collector energy")
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

