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
        self.lockedmissile = False
 
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
                    x = randint(5, 85)
                    y = randint(5, 85)
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
        logging.debug("processing death")
        notclear = True 
        while notclear:
            notclear = False
            for unit in self.map.unitstore.values():
                if unit.typeset == "tether" and unit.hp > 0: #tethers heal between turns so they never die except by death of parent
                    unit.hp = 1000
                if (unit.hp < 1 and unit.typeset != "doodad"):
                    notclear = True 
                    self.connections.remote_all('kill_unit', unit.x, unit.y, unit.typeset, unit.playerID, unit.type.id, unit.disabled)
                    self.game.remove_unit(unit)
                    for unit2 in self.map.unitstore.values(): 
                        if unit2.parentID == unit.id:
                            unit2.hp = 0
                    radius = self.game.get_unit_radius(unit.type.id) + 1
                    if unit.type.id == "mines" and unit.disabled == False:
                        power = self.game.get_unit_power(unit)
                        endX = unit.x
                        endY = unit.y
                        for find_target in range(0, radius):
                            spinner = 0
                            while spinner < 360:
                                if find_target == 0:
                                    endX = unit.x
                                    endY = unit.y
                                    spinner = 355
                                else:
                                    endX = find_target * math.cos(spinner / 180.0 * math.pi)
                                    endY = find_target * math.sin(spinner / 180.0 * math.pi)
                                    endX = round(endX, 0)
                                    endY = round(endY, 0)
                                    endX = int(endX) + unit.x
                                    endY = int(endY) + unit.y
                                logging.debug("Radius, Spinner = %s, %s" % (find_target, spinner))
                                for target in self.map.unitstore.values():
                                    logging.debug("comparing possible targets: %s, %s - %s, %s" % (endX, endY, target.x, target.y))
                                    if target.x == endX and target.y == endY and target.typeset != "doodad":
                                        target.hp = target.hp - power #unit is caught in explosion and damaged
                                        target.blasted = True
                                spinner = spinner + 5
                    if unit.type.id == "crawler" and unit.disabled == False:
                        power = self.game.get_unit_power(unit)
                        endX = unit.x
                        endY = unit.y
                        for find_target in range(0, radius):
                            spinner = 0
                            while spinner < 360:
                                if find_target == 0:
                                    endX = unit.x
                                    endY = unit.y
                                    spinner = 355
                                else:
                                    endX = find_target * math.cos(spinner / 180.0 * math.pi)
                                    endY = find_target * math.sin(spinner / 180.0 * math.pi)
                                    endX = round(endX, 0)
                                    endY = round(endY, 0)
                                    endX = int(endX) + unit.x
                                    endY = int(endY) + unit.y
                                logging.debug("Radius, Spinner = %s, %s" % (find_target, spinner))
                                for target in self.map.unitstore.values():
                                    logging.debug("comparing possible targets: %s, %s - %s, %s" % (endX, endY, target.x, target.y))
                                    if target.x == endX and target.y == endY and target.typeset != "doodad":
                                        target.hp = target.hp - power #unit is caught in explosion and damaged
                                        target.blasted = True
                                spinner = spinner + 5
                    if unit.type.id == "collector" and unit.disabled == False:
                        logging.info("collector went critical")
                        endX = unit.x
                        endY = unit.y
                        for find_target in range(0, radius):
                            spinner = 0
                            while spinner < 360:
                                if find_target == 0:
                                    endX = unit.x
                                    endY = unit.y
                                    spinner = 355
                                else:
                                    endX = find_target * math.cos(spinner / 180.0 * math.pi)
                                    endY = find_target * math.sin(spinner / 180.0 * math.pi)
                                    endX = round(endX, 0)
                                    endY = round(endY, 0)
                                    endX = int(endX) + unit.x
                                    endY = int(endY) + unit.y
                                logging.debug("Radius, Spinner = %s, %s" % (find_target, spinner))
                                for target in self.map.unitstore.values():
                                    logging.debug("comparing possible targets: %s, %s - %s, %s" % (endX, endY, target.x, target.y))
                                    if target.x == endX and target.y == endY and target.typeset != "doodad":
                                        logging.info("unit got caught in nuke")
                                        target.hp = target.hp - 5 #unit is caught in explosion and damaged
                                        target.blasted = True
                                spinner = spinner + 5
        self.handle_water()

#****************************************************************************
#find and move viruses
#****************************************************************************
    def process_virus(self):
        logging.debug("processing virus")
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
        logging.debug("handling water")
        for unit in self.map.unitstore.values():
            tile = self.map.get_tile((unit.x, unit.y))
            tile2 = self.map.get_tile((unit.x + 1, unit.y))
            tile3 = self.map.get_tile((unit.x, unit.y + 1))
            tile4 = self.map.get_tile((unit.x + 1, unit.y + 1))
            tile5 = self.map.get_tile((unit.x - 1, unit.y - 1))
            tile6 = self.map.get_tile((unit.x - 1, unit.y))
            tile7 = self.map.get_tile((unit.x, unit.y - 1))
            tile8 = self.map.get_tile((unit.x + 1, unit.y - 1))
            tile9 = self.map.get_tile((unit.x - 1, unit.y + 1))

            if unit.type.id == "bridge":
                if tile.type != self.game.get_terrain_type("water") and tile2.type != self.game.get_terrain_type("water") and tile3.type != self.game.get_terrain_type("water") and tile4.type != self.game.get_terrain_type("water") and tile5.type != self.game.get_terrain_type("water") and tile6.type != self.game.get_terrain_type("water") and tile7.type != self.game.get_terrain_type("water") and tile8.type != self.game.get_terrain_type("water") and tile9.type != self.game.get_terrain_type("water"):
                    unit.hp = 0 #killing bridges that don't land on water

            elif unit.typeset == "build":
                if tile.type == self.game.get_terrain_type("water") or tile2.type == self.game.get_terrain_type("water") or tile3.type == self.game.get_terrain_type("water") or tile4.type == self.game.get_terrain_type("water") or tile5.type == self.game.get_terrain_type("water") or tile6.type == self.game.get_terrain_type("water") or tile7.type == self.game.get_terrain_type("water") or tile8.type == self.game.get_terrain_type("water") or tile9.type == self.game.get_terrain_type("water"):
                    gosplash = True
                    for unit2 in self.map.unitstore.values():
                        if (unit2.x == unit.x and unit2.y == unit.y and unit2.type.id == "bridge") or (unit2.x == (unit.x + 1) and unit2.y == unit.y and unit2.type.id == "bridge") or (unit2.x == unit.x and (unit2.y + 1) == unit.y and unit2.type.id == "bridge") or (unit2.x == (unit.x + 1) and unit2.y == (unit.y + 1) and unit2.type.id == "bridge") or (unit2.x == (unit.x - 1) and unit2.y == unit.y and unit2.type.id == "bridge") or (unit2.x == unit.x and (unit2.y - 1) == unit.y and unit2.type.id == "bridge") or (unit2.x == (unit.x - 1) and unit2.y == (unit.y - 1) and unit2.type.id == "bridge") or (unit2.x == (unit.x - 1) and unit2.y == (unit.y + 1) and unit2.type.id == "bridge") or (unit2.x == (unit.x + 1) and unit2.y == (unit.y - 1) and unit2.type.id == "bridge"):
                            gosplash = false
                    if gosplash == True:
                        unit.hp = 0
                        self.connections.remote_all("splash")
                        logging.info("building went splash")

            elif unit.typeset == "tether":
                if tile.type == self.game.get_terrain_type("water"):
                    logging.info("tether in water?")
                    gosplash = True
                    for unit2 in self.map.unitstore.values():
                        if unit2.type.id == "bridge" and ((unit2.x == unit.x and unit2.y == unit.y) or ((unit2.x + 1) == unit.x and unit2.y == unit.y) or (unit2.x == unit.x and (unit2.y + 1 == unit.y)) or ((unit2.x + 1) == unit.x and (unit2.y + 1) == unit.y) or ((unit2.x - 1) == unit.x and (unit2.y - 1) == unit.y) or ((unit2.x + 1) == unit.x and (unit2.y - 1) == unit.y) or ((unit2.x - 1) == unit.x and (unit2.y + 1) == unit.y) or ((unit2.x - 1) == unit.x and (unit2.y) == unit.y) or ((unit2.x) == unit.x and (unit2.y - 1) == unit.y)):
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
        logging.debug("detonating waiters")
        for unit in self.map.unitstore.values():
            blasted = False
            if unit.type.id == "mines":
                power = self.game.get_unit_power(unit.type.id)
                radius = 2
                endX = unit.x
                endY = unit.y
                for find_target in range(1, radius):
                    spinner = 0
                    while spinner < 360:
                        endX = find_target * math.cos(spinner / 180.0 * math.pi)
                        endY = find_target * math.sin(spinner / 180.0 * math.pi)
                        endX = round(endX, 0)
                        endY = round(endY, 0)
                        endX = int(endX) + unit.x
                        endY = int(endY) + unit.y
                        for target in self.map.unitstore.values():
                            logging.debug("comparing possible targets: %s, %s - %s, %s" % (endX, endY, target.x, target.y))
                            if target.x == endX and target.y == endY and target.playerID != unit.playerID and target.typeset != "doodad":
                                unit.hp = 0 #target detonates, damage is incurred while processing death
                        spinner = spinner + 5

            elif unit.type.id == "crawler":
                power = self.game.get_unit_power(unit)
                radius = 1 #note this is different then the explosive radius!
                endX = unit.x
                endY = unit.y
                for find_target in range(1, radius):
                    spinner = 0
                    while spinner < 360:
                        endX = find_target * math.cos(spinner / 180.0 * math.pi)
                        endY = find_target * math.sin(spinner / 180.0 * math.pi)
                        endX = round(endX, 0)
                        endY = round(endY, 0)
                        endX = int(endX) + unit.x
                        endY = int(endY) + unit.y
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
        logging.debug("moving crawlers")
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
                    endX = int(endX) + start_tile.x
                    endY = int(endY) + start_tile.y
                unit.x = endX
                unit.y = endY


#****************************************************************************
#Determine where a shot lands
#****************************************************************************
    def find_trajectory(self, parentID, rotation, power, child, playerID):
        self.lockedmissile = False
        unit = self.map.get_unit_from_id(parentID)
        start_tile = self.map.get_tile_from_unit(unit)
        endX = start_tile.x #todo: can this be safely removed?
        endY = start_tile.y
        self.interrupted_tether = False
        power = power + 6 #launching has minimal range, if modifying to forget to change animation distance to compensate
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
            endX = int(endX) + start_tile.x
            endY = int(endY) + start_tile.y

            #code for looping the map edges
            if endX < 0:
                endX = self.map.xsize + endX
            if endX > self.map.xsize - 1:
                endX = endX - (self.map.xsize - 1)
            if endY < 0:
                endY = self.map.ysize + endY
            if endY > self.map.ysize - 1:
                endY = endY - (self.map.ysize - 1)

            #determine if shot is intercepted by either an AA or shield
            for lookD in self.map.unitstore.values():
                if lookD.playerID != playerID and (lookD.type.id == "shield" or lookD.type.id == "antiair") and (lookD.disabled == False or lookD.virused == False):
                    radius = 6
                    searchX = lookD.x
                    searchY = lookD.y
                    for find_target in range(1, radius):
                        spinner = 0
                        while spinner < 360:
                            searchX = find_target * math.cos(spinner / 180.0 * math.pi)
                            searchY = find_target * math.sin(spinner / 180.0 * math.pi)
                            searchX = round(searchX, 0)
                            searchY = round(searchY, 0)
                            searchX = searchX + lookD.x
                            searchY = searchY + lookD.y
                            if searchX == endX and searchY == endY:
                                spinner = 360
                                self.interrupted_tether = True
                                victim = self.map.get_unit_from_id(self.game.unit_counter)
                                victim.hp = 0
                                self.connections.remote_all("triggered_defense")
                                if lookD.type.id == "antiair":
                                    lookD.disabled == True
                                return (start_tile.x, start_tile.y, endX, endY, collecting)
                            else:
                                spinner = spinner + 5

            #handle missile lockons
            if child == "missile" and self.lockedmissile == False:
                radius = 4
                searchX = endX
                searchY = endY
                for find_target in range(1, radius):
                    spinner = 0
                    while spinner < 360:
                        searchX = find_target * math.cos(spinner / 180.0 * math.pi)
                        searchY = find_target * math.sin(spinner / 180.0 * math.pi)
                        searchX = round(searchX, 0)
                        searchY = round(searchY, 0)
                        searchX = searchX + endX
                        searchY = searchY + endY
                        for target in self.map.unitstore.values():
                            if target.playerID != playerID and searchX == target.x and searchY == target.y and target.typeset == "build":
                                #found a target and changing trajectory to hit it
                                rotation = spinner
                                power = find_target
                                self.lockedmissile = True
                                spinner = 360
                        else:
                            spinner = spinner + 5

            #placing tethers if applicable
            if self.game.check_tether(child) == True: #if launched unit has tethers, then place tethers
                for target in self.map.unitstore.values():
                    double_tether = False
                    tile = self.map.get_tile((endX, endY))
                    if (target.x == endX and target.y == endY): #determine if tether crosses another unit/tether
                        if (target.typeset != "doodad") and (target.parentID != parentID):
                            if target.parentID != self.game.unit_counter + 1: #prevents tether from 'crossing' itself due to rounding
                                logging.info("You crossed a tether at step %r" % find_target)
                                if find_target < 3: #don't remove when crossing on the first tether piece
                                    self.interrupted_tether = True
                                    return (start_tile.x, start_tile.y, endX, endY, collecting)
                                else:
                                    self.interrupted_tether = True
                                    victim = self.map.get_unit_from_id(self.game.unit_counter) #find and kill partially laid tether
                                    victim.hp = 0
                                    return (start_tile.x, start_tile.y, endX, endY, collecting)
                            else:
                                double_tether = True #doesn't place 'doubled' tethers due to rounding
                if double_tether == False:
                    #tether didn't land on anything, ready to place tether! The following is to prevent spaces around the launching hub
                    testX = str(endX)
                    testY = str(endY)
                    if find_target > 1 and find_target < (power - 2):
                        chain_parent = self.game.unit_counter + 2 
                        self.add_unit("tether", (endX, endY), (offsetX, offsetY), playerID, chain_parent, False, 0)
                        logging.debug("added tether at " + testX + ", " + testY)

        #determine if building landed on rocks or water
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

            tile = self.map.get_tile((endX - 1, endY - 1))
            if tile.type == self.game.get_terrain_type("rocks"): 
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter) 
                victim.hp = 0
                self.connections.remote_all("hit_rock")
            elif tile.type == self.game.get_terrain_type("energy"):
                collecting = True

            tile = self.map.get_tile((endX - 1, endY))
            if tile.type == self.game.get_terrain_type("rocks"): 
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter) 
                victim.hp = 0
                self.connections.remote_all("hit_rock")
            elif tile.type == self.game.get_terrain_type("energy"):
                collecting = True

            tile = self.map.get_tile((endX, endY - 1))
            if tile.type == self.game.get_terrain_type("rocks"): 
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter) 
                victim.hp = 0
                self.connections.remote_all("hit_rock")
            elif tile.type == self.game.get_terrain_type("energy"):
                collecting = True

            tile = self.map.get_tile((endX - 1, endY + 1))
            if tile.type == self.game.get_terrain_type("rocks"): 
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter) 
                victim.hp = 0
                self.connections.remote_all("hit_rock")
            elif tile.type == self.game.get_terrain_type("energy"):
                collecting = True

            tile = self.map.get_tile((endX + 1, endY - 1))
            if tile.type == self.game.get_terrain_type("rocks"): 
                self.interrupted_tether = True
                victim = self.map.get_unit_from_id(self.game.unit_counter) 
                victim.hp = 0
                self.connections.remote_all("hit_rock")
            elif tile.type == self.game.get_terrain_type("energy"):
                collecting = True

        logging.debug("collecting = %r" % collecting)
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
        splitX = int(endX) + start_tile.x
        splitY = int(endY) + start_tile.y

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
        coordX1 = int(endX) + splitX
        coordY1 = int(endY) + splitY
        default_rotation = temp_rotation

        temp_rotation = default_rotation + 45
        if temp_rotation > 360:
            temp_rotation = default_rotation - 315

        endX = end_arc * math.cos(temp_rotation / 180.0 * math.pi)
        endY = end_arc * math.sin(temp_rotation / 180.0 * math.pi)
        endX = round(endX, 0)
        endY = round(endY, 0)
        coordX2 = int(endX) + splitX
        coordY2 = int(endY) + splitY

        temp_rotation = default_rotation - 45
        if temp_rotation < 1:
            temp_rotation = default_rotation + 315

        endX = end_arc * math.cos(temp_rotation / 180.0 * math.pi)
        endY = end_arc * math.sin(temp_rotation / 180.0 * math.pi)
        endX = round(endX, 0)
        endY = round(endY, 0)
        coordX3 = int(endX) + splitX
        coordY3 = int(endY) + splitY

        return (start_tile.x, start_tile.y, coordX1, coordY1, coordX2, coordY2, coordX3, coordY3)



#****************************************************************************
#Find out if a unit is hit or not
#****************************************************************************
    def determine_hit(self, unit, pos, player):
        x, y = pos
        power = self.game.get_unit_power(unit)
        radius = self.game.get_unit_radius(unit) + 1
        for target in self.map.unitstore.values():
            target.blasted = False #clearing all targets
        if unit != "crawler" or unit != "mines":
            endX = x
            endY = y
            for find_target in range(0, radius):
                spinner = 0
                while spinner < 360:
                    if find_target == 0:
                        endX = x
                        endY = y
                        spinner = 355
                    else:
                        endX = find_target * math.cos(spinner / 180.0 * math.pi)
                        endY = find_target * math.sin(spinner / 180.0 * math.pi)
                        endX = round(endX, 0)
                        endY = round(endY, 0)
                        endX = int(endX) + x
                        endY = int(endY) + y
                    logging.debug("Radius, Spinner = %s, %s" % (find_target, spinner))
                    for target in self.map.unitstore.values():
                        logging.debug("comparing possible targets: %s, %s - %s, %s" % (endX, endY, target.x, target.y))
                        if target.x == endX and target.y == endY and target.typeset == "build" and target.blasted == False:
                            logging.info("detected hit")
                            if unit == "emp":
                                target.disabled = True
                                player.Idisabled.append(target.id)
                                player.undisable = True
                                logging.info("you disabled a %r" % target.type.id)
                            elif unit == "repair":
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
                                    target.disabled = True
                                else:
                                    if target.hp < 3: #if not own target
                                        player.energy = player.energy + target.hp
                                        target.hp = 0
                                        target.blasted = True
                                        target.disabled = True
                                    else:
                                        player.energy = player.energy + power
                                        target.hp = target.hp - power
                                        target.blasted = True
                            else:
                                logging.info("hit target for %s" % power)
                                target.hp = target.hp - power
                                target.blasted = True
                        elif target.x == endX and target.y == endY and target.typeset == "tether" and unit == "spike": #spikes landing on tethers zaps buildings on both ends
                            (target1, target2) = self.game.find_tether_ends(target)
                            for tetherend in self.map.unitstore.values():
                                if tetherend.id == target1 or tetherend.id == target2:
                                    tetherend.hp = tetherend.hp - 1
                                    logging.info("spike damaged unit %s" % tetherend.id)
                            return #spikes only affect one tether, so when one tether is hit, no further damage is calculated
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

