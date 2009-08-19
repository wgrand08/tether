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

#****************************************************************************
#
#****************************************************************************
"""Both buildings and weapons are considered units since they are launched in the same way. Doodads are also units but are generally treated differently in the game."""
class Unit:
  def __init__(self, id, type, playerID):
    self.id = id;
    self.type = type;
    self.playerID = playerID;    
    self.dir = 0;
    self.owner = None;
    self.path = None;
    self.x = 0;
    self.y = 0;
    self.offset = (0,0);
    self.speed = (0,0);
    self.rotate = 3;
    self.typeset = None;
    self.hp = 0;
    self.parentID = 0;
    self.disabled = False;

#****************************************************************************
#
#****************************************************************************
  def calc_dir(self, new_x, new_y):
    if new_x == self.x - 1 and new_y == self.y:
      self.dir = 3;
      self.offset = (0.5, 0.5);
    if new_x == self.x and new_y == self.y - 1:
      self.dir = 1;
      self.offset = (-0.5, 0.5);
    if new_x == self.x + 1 and new_y == self.y - 1:
      self.dir = 0;
      self.offset = (-1.0, 0.0);
    if new_x == self.x - 1 and new_y == self.y - 1:
      self.dir = 2;
      self.offset = (0.0, 1.0);
    if new_x == self.x - 1 and new_y == self.y + 1:
      self.dir = 4;
      self.offset = (1.0, 0);
    if new_x == self.x and new_y == self.y + 1:
      self.dir = 5;
      self.offset = (0.5, -0.5);
    if new_x == self.x + 1 and new_y == self.y + 1:
      self.dir = 6;
      self.offset = (0.0, -1.0);
    if new_x == self.x + 1 and new_y == self.y:
      self.dir = 7; 
      self.offset = (-0.5, -0.5);
    self.dir = 0;
    ox, oy = self.offset;
    self.speed = (-ox, -oy);
    #logging.info("unit dir %r" % (self.dir));
    #logging.info(self.offset);
