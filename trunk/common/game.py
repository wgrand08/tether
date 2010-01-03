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

from common.map import * 
from common.unit import * 


#****************************************************************************
#
#****************************************************************************
"""This handles game related functions for both client and server. Most functions are server related however."""
class Game:
    def __init__(self, map):
        self.map = map
        self.time = 0
        self.unit_counter = 0
        self.unit_types = {}
        self.terrain_types = {}

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"hub":UnitType("hub", "hub", 0, "build", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"offense":UnitType("offense", "offense", 0, "build", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"tower":UnitType("tower", "tower", 0, "build", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"antiair":UnitType("antiair", "hub", 0, "build", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"balloon":UnitType("balloon", "balloon", 0, "balloon", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"bridge":UnitType("bridge", "bridge", 0, "build", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"collector":UnitType("collector", "collector", 0, "build", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"crater":UnitType("crater", "crater", 0, "doodad", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"void":UnitType("void", "void", 0, "doodad", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"bomb":UnitType("bomb", "bomb", 0, "weap", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"cluster":UnitType("cluster", "cluster", 0, "weap", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"crawler":UnitType("crawler", "crawler", 0, "weap", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"emp":UnitType("emp", "emp", 0, "weap", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"mines":UnitType("mines", "mines", 0, "weap", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"missile":UnitType("missile", "missile", 0, "weap", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"recall":UnitType("recall", "recall", 0, "recall", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"repair":UnitType("repair", "repair", 0, "weap", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"spike":UnitType("spike", "spike", 0, "weap", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"virus":UnitType("virus", "virus", 0, "weap", movements)})

        movements = {}
        type = "grass"
        movecost = 0
        movements.update({type:movecost})
        self.unit_types.update({"tether":UnitType("tether", "tether", 0, "doodad", movements)})

        self.terrain_types.update({"grass":TerrainType("grass", "grass")})
        self.terrain_types.update({"water":TerrainType("water", "water")})
        self.terrain_types.update({"energy":TerrainType("energy", "energy")})
        self.terrain_types.update({"rocks":TerrainType("rocks", "rocks")})


#****************************************************************************
#Process next phase of game
#****************************************************************************
    def game_next_phase(self): 
        self.time = (self.time + 1) % 1024
        self.move_units()

#****************************************************************************
#Move units todo: this code is now obsolete and should be removed
#****************************************************************************
    def move_units(self):
        for unit in self.map.get_unit_list():
            self.map.move_unit(unit) 

#****************************************************************************
#create a new unit and place it on the map
#****************************************************************************
    def create_unit(self, unit_type_id, pos, offset, playerID, parentID, collecting, dir):
        self.unit_counter += 1
        typeset = self.get_unit_typeset(unit_type_id)
        hp = self.get_unit_hp(unit_type_id)
        unit_type = self.get_unit_type(unit_type_id)
        if unit_type_id != "crawler": #all units face same direction except for crawlers
            dir = 360
        self.map.set_unit(Unit(self.unit_counter, unit_type, playerID), pos, offset, typeset, hp, parentID, collecting, dir)

#****************************************************************************
#turns a unit into a crater
#****************************************************************************
#Due to problems actually removing unit information completely from the unit list it became much easier to have destroyed units turn into something else. Tethers become 'void' while just about everything else becomes a crater.
    def remove_unit(self, unit):
        endX = unit.x
        endY = unit.y
        tile1 = self.map.get_tile((endX, endY))
        tile2 = self.map.get_tile((endX + 1, endY))
        tile3 = self.map.get_tile((endX, endY + 1))
        tile4 = self.map.get_tile((endX + 1, endY + 1))
        if (tile1.type == self.get_terrain_type("grass")) and (tile2.type == self.get_terrain_type("grass")) and (tile3.type == self.get_terrain_type("grass")) and (tile4.type == self.get_terrain_type("grass")) : #craters are only placed on grass
            unit_type_id = "crater"

        else: #if even partially placed on rocks or water or energy, no crater is formed
            unit_type_id = "void"

        if unit.typeset == "tether": #tethers do not leave craters when destroyed
            unit_type_id = "void"

        if unit.typeset == "ballon": #balloons do not leave craters when destroyed
            unit_type_id = "void"

        if unit.type.id == "virus": #viruses do not leave craters when destroyed
            unit_type_id = "void"
            
        if unit.type.id == "bridge": #bridges do not leave craters
            unit_type_id = "void"

        unit_type = self.get_unit_type(unit_type_id)
        #self.map.change_unit(unit, unit_type)
        unit.typeset = 'doodad'
        unit.hp = 0
        logging.info("removed a " + str(unit.type.id) + " at location: " + str(unit.x) + ", " + str(unit.y))
        self.map.remove_unit(unit)

#****************************************************************************
#finds a units parent
#****************************************************************************
    def find_parent(self, unit):
        for parent in self.map.unitstore.values():
            if parent.id == unit.parentID:
                return parent
        return 0

#****************************************************************************
#Get color based off playerID
#****************************************************************************
    def get_unit_color(self, teamID): #The players own units are green, allies are blue, enemies are red
        color = None
        if teamID == 1:
            color = (10,255,10)
        elif teamID == 2:
            color = (10,10,255)
        elif teamID == 3:
            color = (255,10,10)
        else:
            logging.info("error specifying colors")
        return color

#****************************************************************************
#Get units team number
#****************************************************************************
    def get_unit_team(self, clientID, playerID): #team 1 is the players own units, team 2 is allied units, team 3 is enemies
        if clientID == playerID:
            team = 1
        #todo: add allied abilities which will be team 2
        else:
            team = 3
        return team

#****************************************************************************
#identify unit type
#****************************************************************************
    def get_unit_type(self, type_id):
        return self.unit_types[type_id]

#****************************************************************************
#get the typeset of a unit
#****************************************************************************
    def get_unit_typeset(self, type_id):
        typeset = "doodad"
        if type_id == "hub" or type_id == "tower" or type_id == "collector" or type_id == "antiair" or type_id == "offense" or type_id == "shield" or type_id == "bridge":
            typeset = "build"
        elif type_id == "bomb" or type_id == "cluster" or type_id == "missile" or type_id == "crawler" or type_id == "emp" or type_id == "spike" or type_id == "virus" or type_id == "recall" or type_id == "repair":
            typeset = "weap"
        #following do not really follow the standard rules for buildings or weapons so they have their own typeset
        elif type_id == "ballon": 
            typeset = "ballon"
        elif type_id == "tether":
            typeset = "tether"
        return typeset

#****************************************************************************
#get the maxHP of a unit
#****************************************************************************
    def get_unit_hp(self, type_id):
        hp = 0
        if type_id == "hub" or type_id == "collector":
            hp = 5 
        if type_id == "tower" or type_id == "antiair" or type_id == "offense" or type_id == "shield" or type_id == "crawler":
            hp = 3
        if type_id == "balloon" or type_id == "bridge" or type_id == "mines":
            hp = 1
        if type_id == "tether" or type_id == "void":
            hp = 1000 #tethers should not die except by disconnection
        return hp

#****************************************************************************
#get the power or damage capability of a weapon
#****************************************************************************
    def get_unit_power(self, type_id):
        power = 0
        if type_id == "bomb" or type_id == "missile" or type_id == "spike" or type_id == "recall" or type_id == "mines":
            power = 3
        if type_id == "crawler":
            power = 4
        if type_id == "emp":
            power = 2
        if type_id == "cluster":
            power = 1
        return power

#****************************************************************************
#get the explosive radius of a weapon
#****************************************************************************
    def get_unit_radius(self, type_id):
        if type_id == "crawler":
            radius = 4
        elif type_id == "emp":
            radius = 8
        elif type_id == "mines":
            radius = 2
        elif type_id == "collector":
            radius = 5
        else:
            radius = 1
        return radius

#****************************************************************************
#get the cost of a unit or weapon
#****************************************************************************
    def get_unit_cost(self, type_id):
        cost = 0
        if type_id == "antiair" or type_id == "bomb" or type_id == "bridge" or type_id == "tower" or type_id == "cluster" or type_id == "repair":
            cost = 1
        if type_id == "ballon" or type_id == "emp" or type_id == "spike" or type_id == "mines" or type_id == "recall" or type_id == "missile":
            cost = 3
        if type_id == "hub" or type_id == "shield" or type_id == "collector" or type_id == "crawler" or type_id == "offense" or type_id == "virus":
            cost = 7
        return cost


#****************************************************************************
#Determine if a unit is tethered
#****************************************************************************
    def check_tether(self, type_id): #returns boolean of a unit is tethered or not
        if self.get_unit_typeset(type_id) != "build" or type_id == "bridge": #all buildings except bridges have tethers, nothing else does. Note that balloons are not considered buildings
            return False
        else:
            return True

#****************************************************************************
#Find units on both ends of a tether
#****************************************************************************
    def find_tether_ends(self, tether):
        notfound = True
        while notfound == True:
            for test in self.map.unitstore.values():
                if test.id == tether.parentID:
                    if test.typeset == "tether":
                        tether = test
                    else: #found outer end of tether, other end is it's parentID
                        target1 = test.id
                        target2 = test.parentID
                        notfound = False
        return target1, target2

#****************************************************************************
#get terrain type
#****************************************************************************
    def get_terrain_type(self, type_id):
        return self.terrain_types[type_id]
 
#****************************************************************************
#
#****************************************************************************
class TerrainType:
    def __init__(self, id, full_name):
        self.id = id
        self.full_name = full_name


#****************************************************************************
#
#****************************************************************************
class UnitType:
    def __init__(self, id, full_name, speed, typeset, movement_costs):
        self.id = id
        self.full_name = full_name
        self.speed = speed
        self.typeset = typeset
        self.movement_costs = movement_costs

#****************************************************************************
#
#****************************************************************************
    def get_movement_cost(self, terrain_type):
        return self.movement_costs[terrain_type.id]

#****************************************************************************
#
#****************************************************************************
    def can_unit_move_to_terrain(self, check_terrain_type):
        try:    
            if self.movement_costs[check_terrain_type.id]:
                return 1
        except:
           return 0
