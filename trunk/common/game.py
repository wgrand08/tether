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
        self.unit_types.update({"tether":UnitType("tether", "tether", 0, "doodad", movements)})

        self.terrain_types.update({"grass":TerrainType("grass", "grass")})
        self.terrain_types.update({"water":TerrainType("water", "water")})
        self.terrain_types.update({"energy":TerrainType("energy", "energy")})
        self.terrain_types.update({"rocks":TerrainType("rocks", "rocks")})


#****************************************************************************
#
#****************************************************************************
    def game_next_phase(self): 
        self.time = (self.time + 1) % 1024
        self.move_units()

#****************************************************************************
#
#****************************************************************************
    def move_units(self):
        for unit in self.map.get_unit_list():
            self.map.move_unit(unit) 

#****************************************************************************
#create a new unit and place it on the map
#****************************************************************************
    def create_unit(self, unit_type_id, pos, offset, playerID, parentID):
        self.unit_counter += 1
        typeset = self.get_unit_typeset(unit_type_id)
        hp = self.get_unit_hp(unit_type_id)
        name = unit_type_id
        unit_type = self.get_unit_type(unit_type_id)
        self.map.set_unit(Unit(self.unit_counter, unit_type, playerID), pos, offset, typeset, hp, name, parentID)

#****************************************************************************
#turns a unit into a crater
#****************************************************************************
#Due to problems actually removing unit information completely from the unit list it became much easier to have destroyed units turn into something else. Tethers become 'void' while just about everything else becomes a crater."""
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

        if unit.typeset == "virus": #viruses do not leave craters when destroyed
            unit_type_id = "void"

        unit_type = self.get_unit_type(unit_type_id)
        self.map.change_unit(unit, unit_type)
        unit.typeset = 'doodad'
        unit.hp = 0

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
    def get_player_color(self, playerID): #todo add more colors
        color = None
        if playerID == 1:
            color = (255,10,10)
        elif playerID == 2:
            color = (0,39,228)
        elif playerID == 3:
            color = (0,255,0)
        elif playerID == 4:
            color = (0,0,0)
        else:
            logging.error("PlayerID %r not assigned a color yet" % (playerID))
        return color

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
        if type_id == "hub" or type_id == "tower" or type_id == "converter" or type_id == "antiair" or type_id == "offense" or type_id == "shield":
            typeset = "build"
        elif type_id == "bomb" or type_id == "cluster" or type_id == "missile" or type_id == "crawler" or type_id == "emp" or type_id == "spike" or type_id == "virus":
            typeset = "weap"
        #following do not really follow the standard rules for buildings or weapons so they have their own typeset
        elif type_id == "ballon": 
            typeset = "ballon"
        elif type_id == "recall":
            typeset = "recall"
        elif type_id == "tether":
            typeset = "tether"
        return typeset

#****************************************************************************
#get the maxHP of a unit
#****************************************************************************
    def get_unit_hp(self, type_id):
        hp = 0
        if type_id == "hub" or type_id == "converter":
            hp = 5 
        if type_id == "tower" or type_id == "antiair" or type_id == "offense" or type_id == "shield" or type_id == "crawler":
            hp = 3
        if type_id == "balloon":
            hp = 1
        if type_id == "tether" or type_id == "void":
            hp = 1000 #tethers should not die except by disconnection
        return hp

#****************************************************************************
#get the power or damage capability of a weapon
#****************************************************************************
    def get_unit_power(self, type_id):
        power = 0
        if type_id == "bomb" or type_id == "missile" or type_id == "spike":
            power = 3
        if type_id == "crawler":
            power = 4
        if type_id == "emp":
            power = 2
        if type_id == "cluster":
            power = 1
        return power

#****************************************************************************
#get the cost of a unit or weapon
#****************************************************************************
    def get_unit_cost(self, type_id):
        cost = 0
        if type_id == "antiair" or type_id == "bomb" or type_id == "bridge" or type_id == "tower" or type_id == "cluster" or type_id == "repair":
            cost = 1
        if type_id == "ballon" or type_id == "emp" or type_id == "spike" or type_id == "mines" or type_id == "recall" or type_id == "missile":
            cost = 3
        if type_id == "hub" or type_id == "shield" or type_id == "converter" or type_id == "crawler" or type_id == "offense" or type_id == "virus":
            cost = 7
        return cost


#****************************************************************************
#Determine if a unit is tethered
#****************************************************************************
    def check_tether(self, type_id): #returns boolean of a unit is tethered or not
        if (self.get_unit_typeset(type_id) != "build") or (type_id == "balloon"): #all buildings except balloons have tethers, nothing else does
            return False
        else:
            return True

#****************************************************************************
#
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
