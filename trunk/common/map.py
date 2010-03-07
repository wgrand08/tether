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

import os, sys
import logging
import math

from maptile import *
from unit import *

#****************************************************************************
# The map class contains the mapstore, which is a dictionary of 
# MapTile objects. The MapTile objects represents a tile on the map,
# which is consistently referenced to with a touple of coordinates (x, y).
#****************************************************************************
class Map:

    def __init__(self, game_state, mapX, mapY):
        self.mapstore = {}
        self.unitstore = {} 
        self.game_state = game_state
        self.xsize = mapX
        self.ysize = mapY

        for x in range(self.xsize):
            for y in range(self.ysize):
                self.mapstore.update({(x,y): MapTile(None, x,y)})

#****************************************************************************
#
#****************************************************************************
    def get_map_width(self):
        return self.xsize

#****************************************************************************
#
#****************************************************************************
    def get_map_height(self):
        return self.ysize

#****************************************************************************
#
#****************************************************************************
    def get_tile(self, pos):
        (endX,endY) = pos
        if endX < 0:
            endX = self.xsize + endX
        if endX > self.xsize - 1:
            endX = endX - (self.xsize - 1)
        if endY < 0:
            endY = self.ysize + endY
        if endY > self.ysize - 1:
            endY = endY - (self.ysize - 1)        
        try:
            return self.mapstore[(endX, endY)]
        except KeyError:
            logging.critical("get_tile error with pos = %s, %s", (endX, endY))
            raise MapTileError

#****************************************************************************
#
#****************************************************************************
    def get_distance(self, start_tile, end_tile):
        x1, y1 = start_tile.x, start_tile.y
        x2, y2 = end_tile.x, end_tile.y
        return int(math.sqrt(pow(x2-x1, 2) + pow(y2-y1,2)))

#****************************************************************************
#
#****************************************************************************
    def get_unit_list(self):
        return self.unitstore.values()

#****************************************************************************
#report position of unit from ID
#****************************************************************************
    def get_unit_pos(self, unit):
        return (unit.x, unit.y) 

#****************************************************************************
#
#****************************************************************************
    def get_tile_from_unit(self, unit):
        return self.mapstore[(unit.x, unit.y)] 

#****************************************************************************
#report non-doodad unit from location
#****************************************************************************
    def get_unit(self, pos):
        x, y = pos
        for unit in self.unitstore.values():
            if unit.x == x and unit.y == y and unit.typeset != "doodad":
                return unit
        return None

#****************************************************************************
#report selectable unit from location
#****************************************************************************
    def get_selectable_unit(self, pos):
        x, y = pos
        for unit in self.unitstore.values():
            if unit.x == x and unit.y == y and (unit.type.id == "hub" or unit.type.id == "offense"):
                return unit
        return None

#****************************************************************************
#report any unit from location
#****************************************************************************
    def get_doodad(self, pos):
        x, y = pos
        for unit in self.unitstore.values():
            if unit.x == x and unit.y == y:
                return unit
        return None

#****************************************************************************
#report any unit from ID
#****************************************************************************
    def get_unit_from_id(self, id):
        try:
            return self.unitstore[id]
        except:
            return None

#****************************************************************************
#
#****************************************************************************
    def move_unit(self, unit):
        current_tile = self.get_tile_from_unit(unit)
        if unit.path:
            #Goto next tile in path.
            next_tile = self.get_tile(unit.path[0])
            if self.can_unit_move_to_tile(unit, next_tile):
                unit.calc_dir(next_tile.x, next_tile.y)
                del unit.path[0]
                unit.x = next_tile.x 
                unit.y = next_tile.y
            else:
                #Unit move interrupted because the unit could not move there.
                unit.speed = (0,0)
                return
        else:
            #Goto is at destination.
            self.path = [] 
            unit.speed = (0,0)
   

#****************************************************************************
#  Determines if the unit is allowed to move to the tile.       
#****************************************************************************
    def can_unit_move_to_tile(self, unit, tile):
        return (self.get_unit((tile.x, tile.y)) == None and unit.type.can_unit_move_to_terrain(tile.type))

#****************************************************************************
# Places the unit at the map position.
#****************************************************************************
    def set_unit(self, unit, pos, typeset, hp, parentID, collecting, dir, glow_tether):
        landing = self.get_unit(pos)
        if (landing == None) or (typeset == "weap") or (landing.type.id == "bridge") or (landing.type.id == "balloon"):
            self.unitstore.update({unit.id:unit})
            (unit.x, unit.y) = pos
            unit.typeset = typeset
            unit.hp = hp
            unit.parentID = parentID
            unit.collecting = collecting
            unit.dir = dir
            unit.glow_tether = glow_tether
        else:
            logging.error("Attempted to add a " + str(landing.type.id) + " but a " + str(landing.type.id) + " was already there!")

#****************************************************************************
# removes unit completely
#****************************************************************************
    def remove_unit(self, unit):
        self.unitstore.pop(unit.id)
            
#****************************************************************************
# transforms one unit type into another type
#****************************************************************************
    def change_unit(self, unit, new_unit):
        unit.type = new_unit

#****************************************************************************
#
#****************************************************************************
    def get_south_tile(self, pos):
        mapx, mapy = pos
        try:
            return self.mapstore[(mapx, mapy + 1)]
        except KeyError:
            raise MapTileError

#****************************************************************************
#
#****************************************************************************
    def get_north_tile(self, pos):
        mapx, mapy = pos
        try:
            return self.mapstore[(mapx, mapy - 1)]
        except KeyError:
            raise MapTileError

#****************************************************************************
#
#****************************************************************************
    def get_east_tile(self, pos):
        mapx, mapy = pos
        try:
            return self.mapstore[(mapx + 1, mapy)]
        except KeyError:
            raise MapTileError

#****************************************************************************
#
#****************************************************************************
    def get_west_tile(self, pos):
        mapx, mapy = pos
        try:
            return self.mapstore[(mapx - 1, mapy)]
        except KeyError:
            raise MapTileError


#****************************************************************************
#
#****************************************************************************
    def get_south_east_tile(self, pos):
        mapx, mapy = pos
        try:
            return self.mapstore[(mapx + 1, mapy + 1)]
        except KeyError:
            raise MapTileError

#****************************************************************************
#
#****************************************************************************
    def get_north_west_tile(self, pos):
        mapx, mapy = pos
        try:
            return self.mapstore[(mapx - 1, mapy - 1)]
        except KeyError:
            raise MapTileError

#****************************************************************************
#
#****************************************************************************
    def get_north_east_tile(self, pos):
        mapx, mapy = pos
        try:
            return self.mapstore[(mapx + 1, mapy - 1)]
        except KeyError:
            raise MapTileError

#****************************************************************************
#
#****************************************************************************
    def get_south_west_tile(self, pos):
        mapx, mapy = pos
        try:
            return self.mapstore[(mapx - 1, mapy + 1)]
        except KeyError:
            raise MapTileError

#****************************************************************************
#  Returns a list of the coordinates of the adjacent tiles.
#****************************************************************************
    def get_tile_adjacent(self, pos):
        map_x, map_y = pos
        adj_tiles = []

        adj_tiles.append(self.wrap_map_pos((map_x - 1, map_y - 1))) 
        adj_tiles.append(self.wrap_map_pos((map_x - 1, map_y))) 
        adj_tiles.append(self.wrap_map_pos((map_x - 1, map_y + 1))) 
        adj_tiles.append(self.wrap_map_pos((map_x, map_y - 1))) 
        adj_tiles.append(self.wrap_map_pos((map_x, map_y + 1))) 
        adj_tiles.append(self.wrap_map_pos((map_x + 1, map_y - 1))) 
        adj_tiles.append(self.wrap_map_pos((map_x + 1, map_y))) 
        adj_tiles.append(self.wrap_map_pos((map_x + 1, map_y + 1))) 

        return adj_tiles     

#****************************************************************************
#  Returns a list of the adjacent tiles.
#****************************************************************************
    def get_adjacent_tiles(self, pos):
        tiles = []
        for map_pos in self.get_tile_adjacent(pos):
            tiles.append(self.get_tile(map_pos))
        return tiles
 
#****************************************************************************
#
#****************************************************************************
    def norm_map_pos(self, pos):
        (x, y) = pos
        if ((x > 0) and (x < self.xsize ) and (y > 0) and  (y < self.ysize) ):
            return 1
        else:
            return 0

#****************************************************************************
#
#****************************************************************************
    def wrap_map_pos(self, pos):
        (x, y) = pos
        return (x % self.xsize, y % self.ysize)

#****************************************************************************
#
#****************************************************************************
    def get_coast_type(self, tile):
        if (tile.type.id == 'ocean' or tile.type.id == 'coast'):
            return 'w'
        else:
            return 'l'

#****************************************************************************
#
#****************************************************************************
    def get_tile_height(self, pos):
        map_x, map_y = pos
        if (self.norm_map_pos((map_x, map_y)) != 0):
            return self.mapstore[(map_x, map_y)].height
        else:
            return 0

#****************************************************************************
#
#****************************************************************************
    def set_tile_height(self, pos, height):
        try:
            self.mapstore[pos].height = height
        except KeyError:
            logging.error("Incorrect map position for tile")
            return

#****************************************************************************
#
#****************************************************************************
    def get_tile_height_pos(self, pos):
        offset = 0

        try:
            height_1 = self.get_tile_height(pos)
            tile_2 = self.get_east_tile(pos)
            tile_3 = self.get_south_east_tile(pos)
            tile_4 = self.get_south_tile(pos)
        except MapTileError:
            # This means we encountered a tile outside the map.
            return (offset, (0,0,0,0))

        height_2 =  tile_2.height
        height_3 =  tile_3.height
        height_4 =  tile_4.height

        while (height_1 != 0 and height_2 != 0 and height_3 != 0 and height_4 != 0):
            offset += 1
            height_1 -= 1
            height_2 -= 1
            height_3 -= 1
            height_4 -= 1

        return (offset, (height_1, height_2, height_3, height_4))

#****************************************************************************
# Return a Node of a tile for Pathfinding. Must be implemented.
#****************************************************************************
    def get_node(self, tile, unit):
        x = tile.x
        y = tile.y
        cost = unit.type.get_movement_cost(tile.type) 
        return Node(tile,cost,((y*self.xsize)+x))              


#****************************************************************************
#         
#****************************************************************************
    def get_adjacent_nodes(self, curnode, dest, unit):
        adjacent_nodes = []
           
        cl = curnode.tile
        dl = dest

        cpos = (cl.x, cl.y)
        for next_tile in self.get_adjacent_tiles(cpos): 
            if self.can_unit_move_to_tile(unit, next_tile): 
                anode = self.handle_node(curnode, next_tile, unit)
                adjacent_nodes.append(anode)

        return adjacent_nodes

#****************************************************************************
# 
#****************************************************************************
    def handle_node(self, current_node, next_tile, unit):
        x = current_node.tile.x
        y = current_node.tile.y
        destx = next_tile.x
        desty = next_tile.y
        dx = max(x,destx) - min(x,destx)
        dy = max(y,desty) - min(y,desty)
        emCost = dx + dy
        n = self.get_node(next_tile, unit)
        n.mCost += current_node.mCost                                   
        n.score = n.mCost + emCost
        n.parent = current_node
        return n


#****************************************************************************
# 
#****************************************************************************
class MapTileError(Exception):
    "Raised when an invalid tile is requested from the map."
