"""Copyright 2007:
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
    self.map = map;
    self.time = 0;
    self.unit_counter = 0;
    self.unit_types = {};
    self.terrain_types = {};

    movements = {};
    type = "plains";
    movecost = 0;
    movements.update({type:movecost});
    self.unit_types.update({"hub":UnitType("hub", "hub", 0, "build", movements)});

    movements = {};
    type = "plains";
    movecost = 0;
    movements.update({type:movecost});
    self.unit_types.update({"crater":UnitType("crater", "crater", 0, "doodad", movements)});

    movements = {};
    type = "plains";
    movecost = 0;
    movements.update({type:movecost});
    self.unit_types.update({"void":UnitType("void", "void", 0, "doodad", movements)});

    movements = {};
    type = "plains";
    movecost = 0;
    movements.update({type:movecost});
    self.unit_types.update({"bomb":UnitType("bomb", "bomb", 0, "weap", movements)});

    movements = {};
    type = "plains";
    movecost = 0;
    movements.update({type:movecost});
    self.unit_types.update({"tether":UnitType("tether", "tether", 0, "doodad", movements)});

    self.terrain_types.update({"ocean":TerrainType("ocean", "Ocean")});
    self.terrain_types.update({"plains":TerrainType("plains", "Plains")});
    self.terrain_types.update({"coast":TerrainType("coast", "Coast")});


#****************************************************************************
#
#****************************************************************************
  def game_next_phase(self): 
    self.time = (self.time + 1) % 1024;
    self.move_units();

#****************************************************************************
#
#****************************************************************************
  def move_units(self):
   for unit in self.map.get_unit_list():
     self.map.move_unit(unit); 

#****************************************************************************
#create a new unit and place it on the map
#****************************************************************************
  def create_unit(self, unit_type_id, pos, playerID, parentID):
    self.unit_counter += 1;
    typeset = self.get_unit_typeset(unit_type_id);
    hp = self.get_unit_hp(unit_type_id);
    unit_type = self.get_unit_type(unit_type_id);
    self.map.set_unit(Unit(self.unit_counter, unit_type, playerID), pos, typeset, hp, parentID);

#****************************************************************************
#turns a unit into a crater
#****************************************************************************
#Due to problems actually removing unit information completely from the unit list it became much easier to have destroyed units turn into craters instead. """
  def remove_unit(self, unit):
    if unit.typeset == "tether": #tethers do not leave craters when destroyed
        unit_type_id = "void";
    else:
        unit_type_id = 'crater';
    unit_type = self.get_unit_type(unit_type_id);
    self.map.change_unit(unit, unit_type);
    unit.typeset = 'doodad';
    unit.hp = 0;

#****************************************************************************
#finds a units parent
#****************************************************************************
  def find_parent(self, unit):
    for parent in self.map.unitstore.values():
        if parent.id == unit.parentID:
            return parent;
    return 0;

#****************************************************************************
#Get color based off playerID
#****************************************************************************
  def get_player_color(self, playerID): #todo add more colors
    color = None;
    if playerID == 1:
        color = (255,10,10);
    elif playerID == 2:
        color = (100,100,50);
    else:
        logging.error("PlayerID %r not assigned a color yet" % (playerID));
    return color;

#****************************************************************************
#identify unit type
#****************************************************************************
  def get_unit_type(self, type_id):
    return self.unit_types[type_id];

#****************************************************************************
#get the typeset of a unit
#****************************************************************************
  def get_unit_typeset(self, type_id):
    typeset = "doodad";
    if type_id == "hub" or type_id == "tower" or type_id == "balloon" or type_id == "converter" or type_id == "antiair" or type_id == "offense" or type_id == "shield":
        typeset = "build"
    elif type_id == "bomb" or type_id == "cluster" or type_id == "missile" or type_id == "crawler" or type_id == "emp" or type_id == "spike":
        typeset = "weap";
    elif type_id == "tether":
        typeset = "tether";
    return typeset;

#****************************************************************************
#get the maxHP of a unit
#****************************************************************************
  def get_unit_hp(self, type_id):
    hp = 0;
    if type_id == "hub" or type_id == "converter":
        hp = 3; #should be 5 but set to 3 for debug purposes
    if type_id == "tower" or type_id == "antiair" or type_id == "offense" or type_id == "shield" or type_id == "crawler":
        hp = 3;
    if type_id == "balloon":
        hp = 1;
    if type_id == "tether" or type_id == "void":
        hp = 100; #tethers should not die except by disconnection
    return hp;

#****************************************************************************
#get the power or damage capability of a weapon
#****************************************************************************
  def get_unit_power(self, type_id):
    power = 0;
    if type_id == "bomb" or type_id == "missile" or type_id == "spike":
        power = 3;
    if type_id == "crawler":
        power = 5;
    if type_id == "emp":
        power = 2;
    return power;

#****************************************************************************
#Determine if a unit is tethered
#****************************************************************************
  def check_tether(self, type_id): #returns boolean of a unit is tethered or not
    if (self.get_unit_typeset(type_id) != "build") or (type_id == "balloon"): #all buildings except balloons have tethers, nothing else does
        return False;
    else:
        return True;

#****************************************************************************
#
#****************************************************************************
  def get_terrain_type(self, type_id):
    return self.terrain_types[type_id];
 
#****************************************************************************
#
#****************************************************************************
class TerrainType:
  def __init__(self, id, full_name):
    self.id = id;
    self.full_name = full_name;


#****************************************************************************
#
#****************************************************************************
class UnitType:
  def __init__(self, id, full_name, speed, typeset, movement_costs):
    self.id = id;
    self.full_name = full_name;
    self.speed = speed;
    self.typeset = typeset;
    self.movement_costs = movement_costs;

#****************************************************************************
#
#****************************************************************************
  def get_movement_cost(self, terrain_type):
    return self.movement_costs[terrain_type.id];

#****************************************************************************
#
#****************************************************************************
  def can_unit_move_to_terrain(self, check_terrain_type):
    try:    
      if self.movement_costs[check_terrain_type.id]:
        return 1;
    except:
     return 0;
