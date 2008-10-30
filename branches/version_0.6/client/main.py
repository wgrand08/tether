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

import gameclient
import common.game
import platform
import sys
import introscreen
import mainmenu

class main:

    def __init__(self):
        self.game = common.game.Game();
        self.client = gameclient.GameClient();
        self.client.running = True;
        self.game.logger.info("MoonPy version " + self.client.settings.string_version);
        self.game.logger.info("Operating system " + platform.platform());
        self.game.logger.info("Python Version " + sys.version);
        try:
            import pygame;
            self.game.logger.info('Pygame version: ' + pygame.version.ver);
        except ImportError, err:
            self.game.logger.error("Pygame not found!" + str(err));
            sys.exit(1);
        while self.client.running:
            placeholder = True;
            self.client.running = False;
        introscreen.SplashScreen();
        

        self.game.logger.info("Client Shutdown");