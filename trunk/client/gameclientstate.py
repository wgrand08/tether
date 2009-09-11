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

from mapview import *
from mapctrl import *
from mappanel import *
from networkclient import *
from tileset import *
from holdbutton import *
from moonaudio import *
from twisted.internet import task, reactor

from common.map import * 
from common.mapgen import *
from common.settings import *
from common.game import *
from server.main import *

#****************************************************************************
#
#****************************************************************************
"""This class is the main class for the client part of MoonPy. All major client variables and some common functions are stored here"""
class GameClientState:
  def __init__(self):


    self.settings = GameSettings()
    self.holdbutton = HoldButton(self)
    self.moonaudio = MoonAudio(self)
    self.settings.load_settings()
    self.screen_width = self.settings.screen_width
    self.screen_height = self.settings.screen_height
    self.screen = None

    self.map = Map(self)
    self.mappanel = None
    self.pregame = None
    self.tileset = Tileset(self)
    self.ruleset = None
    self.game = None
    self.clock = pygame.time.Clock()
    self.fps = 40
    self.loop = task.LoopingCall(self.mainloop)
    self.process_confirmation = False
    self.myturn = False 
    self.skipped = False
    self.current_energy = 0
    self.stored_energy = 0
    self.selected_weap = "hub"
    self.rotate_position = 1
    self.firepower = 1
    self.playerID = 0
    self.conf_startX = 0
    self.conf_startY = 0
    self.conf_endX = 0
    self.conf_endY = 0
    self.heldbutton = "void"

    self.selected_unit = {}



#****************************************************************************
#
#****************************************************************************
  def mainloop(self):
    self.clock.tick(self.fps)

    self.mapview.drawmap()
    self.mapctrl.handle_events()
    self.mappanel.draw_minimap()
    pygame.display.flip()
 

#****************************************************************************
#
#****************************************************************************
  def host_network_game(self, address, username):
    #Start a new server.
    srv = ServerMain()
    srv.start_from_client()

    #wait, then connect to the server.
    pygame.time.wait(50)

    self.connect_network_game(address, username)

#****************************************************************************
#
#****************************************************************************
  def game_next_phase(self):
    if self.game:
        self.game.game_next_phase()

#****************************************************************************
#
#****************************************************************************
  def connect_network_game(self, address, username):

    self.username = username
    self.netclient = NetworkClient(self) 
    self.netclient.connect(address, 6112, username)

#****************************************************************************
#
#****************************************************************************
  def start_game(self):
    logging.info("Init game state")
    self.game = Game(self.map)

    self.tileset.load_tileset()
    self.mapctrl = Mapctrl(self)
    self.mappanel = Mappanel(self)
    self.mapview = Mapview(self)
    self.loop.start(1.0/self.fps)
    self.mappanel.show_message("The game has started.")


#****************************************************************************
#
#****************************************************************************
  def load_ruleset(self, name):
    ruleset_src = self.settings.get_ruleset_src(name)
    self.ruleset = Ruleset(ruleset_src)

#****************************************************************************
#
#****************************************************************************
  def quit(self):
    if reactor.running:
      reactor.stop()
    if self.mappanel:
      self.mappanel.app.quit()
    pygame.quit()
    sys.exit(0)
 
#****************************************************************************
#
#****************************************************************************
  def enter_pregame(self):
    import networkscreen
    self.pregame = networkscreen.PregameScreen(self) 

#****************************************************************************
#movement confirmation
#****************************************************************************
#This is part of the animation system which is currently disabled due to being broken. Once a unit is placed it is then supposed to move into it's proper position (to simulate being launched) and the confirmation is to make certain that movement doesn't take place until after the server has placed the unit on the map."""
  def confirmed(self):
    if self.process_confirmation == True:
        self.conf_unit = {}
        self.conf_unit = self.map.get_unit((self.conf_startX, self.conf_startY))
        logging.info("confirmed movement of unit %s" % self.conf_unit.id)
        start_tile = self.map.get_tile_from_unit(self.conf_unit)
        #start_tile = self.map.get_tile((self.conf_startX, self.conf_startY))
        end_tile = self.map.get_tile((self.conf_endX, self.conf_endY))
        self.map.find_path(self.conf_unit, self.ruleset, start_tile, end_tile)

    #clearing confirmation once complete
    self.process_confirmation = False
    self.conf_startX = 0
    self.conf_startY = 0
    self.conf_endX = 0
    self.conf_endY = 0

