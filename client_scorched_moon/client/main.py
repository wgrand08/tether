"""Copyright 2015:
    Kevin Clement

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

import sys
import logging
import string
import os
import platform
from time import sleep
from . import settings

class Main:
    def __init__(self, debug, loglevel, skip):
        version = 0.002

        # breaking up sessions in logfile
        tetherdir = os.getenv("HOME")
        if str(tetherdir) == "none":
            tetherdir = os.getenv("USERPROFILE")
            tetherdir = os.path.join(tetherdir, "scorched_moon")
        else:
            tetherdir = os.path.join(tetherdir, ".scorched_moon")
        if not os.path.exists(tetherdir):
            os.mkdir(tetherdir)
        if os.name == "nt":
            logdir = os.path.join(tetherdir, "logs\\")
        else:
            logdir = os.path.join(tetherdir, "logs/")
        if not os.path.exists(logdir):
            os.mkdir(logdir)
        logging.basicConfig(filename=logdir+'scorched_moon_client.log',level=logging.DEBUG,format='%(message)s')
        logging.critical("----------------------------------------------------------------------------------------------------------------------------")
        logging.critical("----------------------------------------------------------------------------------------------------------------------------")

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler) # clears out handler to prepare for next logging session

        logging.basicConfig(filename=logdir+'scorched_moon_client.log',level=logging.ERROR,format='%(levelname)s - %(asctime)s -- %(message)s') #default logging configuration until we can load custom settings

        logging.critical("Initializing Scorched Moon Client")

        if sys.version_info < (3, 0): #checking for dependencies
            logging.critical("Scorched Moon requires python3 or higher")
            sys.exit(1)
        try:
            import pygame
        except:
            logging.critical("Unable to find pygame, please install pygame for python3")
            sys.exit(1)


        self.settings = settings.Settings() #initalizaing settings
        self.settings.version = version
        self.settings.tetherdir = tetherdir
        self.settings.load_settings() #loading custom settings from file

        if loglevel != 0: #arguments override settings file for logging
            self.settings.loglevel = loglevel
        else: # loglevel 0 means no argument used so we go with settings file
            loglevel = self.settings.loglevel

        if debug == True: # arguments override settings file for debug
            self.settings.debug = True

        if self.settings.debug == True: #debug overrides loglevels
            loglevel = 1

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler) # clears out handler again so we can use custom logging settings
        
        if loglevel == 1:
            logging.basicConfig(filename=logdir+'scorched_moon_client.log',level=logging.DEBUG,format='%(levelname)s - %(asctime)s - %(module)s:%(funcName)s:%(lineno)s -- %(message)s')
        elif loglevel == 2:
            logging.basicConfig(filename=logdir+'scorched_moon_client.log',level=logging.INFO,format='%(levelname)s - %(asctime)s -- %(message)s')
        elif loglevel == 3:
            logging.basicConfig(filename=logdir+'scorched_moon_client.log',level=logging.WARNING,format='%(levelname)s - %(asctime)s -- %(message)s')
        elif loglevel == 4:
            logging.basicConfig(filename=logdir+'scorched_moon_client.log',level=logging.ERROR,format='%(levelname)s - %(asctime)s -- %(message)s')
        elif loglevel == 5:
            logging.basicConfig(filename=logdir+'scorched_moon_client.log',level=logging.CRITICAL,format='%(levelname)s - %(asctime)s -- %(message)s')
        else: #invalid loglevel
            logging.critical("Invalid loglevel {}" .format(loglevel))
            logging.critical("Unable to start logging")
            sys.exit()

        # confirming startup status and logging
        if self.settings.debug:
            logging.critical("Scorched Moon client ver. {} running in debug mode" .format(version))
            logging.critical("Log level forced to {}" .format(loglevel))
        else:
            logging.critical("Scorched Moon client ver. {}" .format(version))
            logging.critical("Log level is set to {}" .format(loglevel))
        logging.critical("Platform: {}" .format(platform.platform()))
        logging.critical("Python version: {}" .format(sys.version))
        logging.critical("Pygame version: {}" .format(pygame.version.ver))

        image = "data/graphics/misc/intro_splash.png"
        screen = pygame.display.set_mode((550,550))
        try:
            splashScreen = pygame.image.load(image)
        except pygame.error as message:
            logging.error("unable to open splash image")
            sys.exit(1)
        splashScreen = splashScreen.convert()
        screen.blit(splashScreen, (0,0))
        pygame.display.flip()
        sleep(2)
        screen = pygame.display.set_mode((1024,768))

        """
        moondesk = gui.Desktop(theme=gui.Theme("data/themes/default/"))
        moondesk.connect(gui.QUIT,splashscreen.quit,None)

        splashscreen.run(splashtable)
        """
        logging.critical("Scorched Moon client successfully shutdown")
        logging.shutdown()
        sys.exit(0) # final shutdown confirmation
