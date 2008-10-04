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

import string
import sys, os, os.path
import logging
from xml.dom import minidom, Node

#****************************************************************************
# Ruleset handles all the 'rules' of the game
#****************************************************************************
class Ruleset:
  def __init__(self, file_src):
    self.unit_types = {};
    self.terrain_types = {};
    self.load_ruleset(file_src);

#****************************************************************************
#load ruleset information from XML file
#****************************************************************************
  def load_ruleset(self, filename):
    doc = minidom.parse(filename);
    rootNode = doc.documentElement;
    self.name = str(rootNode.getAttribute('name'));
    logging.info("Loading ruleset %s" % self.name);

    for unitNode in rootNode.getElementsByTagName('unit'):
      type_id = str(unitNode.getAttribute('type'));
      full_name = str(unitNode.getAttribute('full_name'));
      speed = int(unitNode.getAttribute('speed'));
      typeset = str(unitNode.getAttribute('typeset'));
      movements = {};
      for movementNode in unitNode.getElementsByTagName('movement'):
        type = str(movementNode.getAttribute('type'));
        movecost = int(movementNode.getAttribute('movecost'));
        movements.update({type:movecost});

      self.unit_types.update({type_id:
                  UnitType(type_id, full_name, speed, typeset, movements)});

    for terrainNode in rootNode.getElementsByTagName('terrain'):
      type_id = str(terrainNode.getAttribute('type'));
      full_name = str(terrainNode.getAttribute('full_name'));
      self.terrain_types.update({type_id:
                         TerrainType(type_id, full_name)});

#****************************************************************************
#Get color based off playerID
#****************************************************************************
  def get_player_color(self, playerID): #todo add more colors
    if playerID == 1:
        color = (255,10,10);
    elif playerID == 2:
        color = (100,100,50);
    else:
        logging.error("PlayerID %r not assigned a color yet" % (playerID));
        color = None;
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
