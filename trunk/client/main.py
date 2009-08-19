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
import pygame
import gettext

import introscreen  

from networkclient import *
from gameclientstate import *
from mainmenu import *

from common.translation import *


#****************************************************************************
# The Main class of the client. 
#****************************************************************************
class Main:

  def __init__(self):
    pygame.init();
  
    self.gameclient = GameClientState();    
    logging.info("MoonPy %s" % (self.gameclient.settings.version));

    self.initialize_locale();

    self.create_main_window();
    self.intro = introscreen.IntroScreen(self.gameclient.screen);

    mainmenu = MainMenu(self.gameclient);

#****************************************************************************
#
#****************************************************************************
  def initialize_locale(self):
    translation = Translation();
    translation.setLanguage(self.gameclient.settings.language)

#****************************************************************************
#
#****************************************************************************
  def create_main_window(self):
    screen_width = self.gameclient.settings.screen_width; 
    screen_height = self.gameclient.settings.screen_height; 
    screen_mode = 0;
    screen = pygame.display.set_mode((screen_width, screen_height), screen_mode);

    pygame.display.set_caption("Welcome to MoonPy");
    self.gameclient.screen = screen;


