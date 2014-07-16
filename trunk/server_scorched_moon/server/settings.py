"""Copyright 2014:
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

import logging
import os, sys
import string

# this file handles all settings

class Settings():
    def __init__(self):
        logging.debug("")
        self.version = "0.00.0"
        self.debug = False
        self.runserver = True
        self.shutdown_command = False
        self.serverport = 6112
        self.webport = 6111
        self.useweb = False
        self.loglevel = 4


    def load_settings(self):
        logging.debug("")
        logging.info("loading settings from settings.conf")
        if os.path.exists("settings.conf"):
            settingsfile=open("settings.conf", mode="r", encoding="utf-8")
            for line in settingsfile:
                line=line.strip()
                if line == "" or line[0] == "#":
                    continue
                input_array = line.split("=", 1)
                if input_array[0].strip() == "version":
                    if input_array[1].strip() != self.version: #checking file version to avoid incompatibilities
                        logging.critical("Invalid settings file detected! aborting startup")
                        logging.critical("Please correct settings file or create new file with -C option")
                        print("Invalid settings file detected! Aborting startup")
                        print("Please correct settings file or create new file with -c option")
                        sys.exit("Invalid settings") #system ends immediately if it detects file with possibly incompatible settings
                elif input_array[0].strip() == "debug":
                    if input_array[1].strip() == "True":
                        self.debug = True
                elif input_array[0].strip() == "serverport":
                    self.serverport = int(input_array[1].strip())
                elif input_array[0].strip() == "webport":
                    self.webport = int(input_array[1].strip())
                elif input_array[0].strip() == "useweb":
                    if input_array[1].strip() == "True":
                        self.useweb = True
            settingsfile.close()
        else:
            logging.warning("settings.conf file not found, recommend running Scorched Moon with -c option")



    def create_settings(self, version):
        logging.debug("")
        logging.critical("Creating default settings file")
        logging.critical("saving defaults to settings.conf")
        settingsfile=open("settings.conf", mode="w", encoding="utf-8")
        settingsfile.write("version="+str(version)+"\n")
        settingsfile.write("debug="+str(self.debug)+"\n")
        settingsfile.write("serverport="+str(self.serverport)+"\n")
        settingsfile.write("webport="+str(self.webport)+"\n")
        settingsfile.write("useweb="+str(self.useweb)+"\n")
        settingsfile.close()
        logging.critical("Default settings successfully saved")

    def check_settings(self):
        logging.debug("")
        test = True

    def abort_load_settings():
        logging.debug("")
        logging.critical("Invalid settings file detected! aborting startup")
        logging.critical("Please correct settings file or create new file with -c option")
        print("Invalid settings file detected! Aborting startup")
        print("Please correct settings file or create new file with -c option")
        sys.exit("Invalid settings")


    def abort_settings():
        logging.debug("")
        logging.critical("Invalid settings file detected! aborting startup")
        logging.critical("Please correct settings file or create new file with -C option")
        print("Invalid settings file detected! Aborting startup")
        print("Please correct settings file or create new file with -c option")
        sys.exit("Invalid settings")
