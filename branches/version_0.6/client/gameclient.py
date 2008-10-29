"""Copyright 2008:
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



class GameClient:
    def __init__(self):


        #self.settings = GameSettings();
        #self.settings.load_settings();
        #self.screen_width = self.settings.screen_width;
        #self.screen_height = self.settings.screen_height;
        self.screen = None;

        #self.map = Map(self);
        self.mappanel = None;
        self.pregame = None;
        #self.tileset = Tileset(self);
        self.ruleset = None;
        self.game = None;
        #self.clock = pygame.time.Clock();
        self.fps = 40;
        #self.loop = task.LoopingCall(self.mainloop);
        self.process_confirmation = False;
        self.myturn = False; 
        self.skipped = False;
        self.current_energy = 0;
        self.stored_energy = 0;
        self.selected_weap = "hub";
        self.rotate_position = 1;
        self.playerID = 0;
        self.conf_startX = 0;
        self.conf_startY = 0;
        self.conf_endX = 0;
        self.conf_endY = 0;

        self.selected_unit = {};
