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
        self.loglevel = 5


        self.tetherdir = os.getenv("HOME")
        """if str(self.tetherdir) == "None":
            self.tetherdir = os.getenv("USERPROFILE")
            self.tetherdir = os.path.join(self.tetherdir, "moonpy")
        else:
            self.tetherdir = os.path.join(self.tetherdir, ".moonpy")
        if not os.path.exists(self.tetherdir):
            os.mkdir(self.tetherdir)"""

    def load_settings(self):
        logging.debug("")
        #savefile = os.path.join(path, "settings.cfg")
        savefile = os.path.join("settings.cfg")
        logging.info("loading settings from %s" % savefile)
        if os.path.exists(savefile):
            settingsfile=open(savefile, 'r')
            for line in settingsfile:
                line=line.strip()
                if line == "" or line[0] == "#":
                    continue
                input_array = line.split("=", 1)
                if input_array[0].strip() == "version":
                    if float(input_array[1].strip()) != self.version: #checking file version to avoid incompatibilities
                        logging.critical("Invalid settings file detected! aborting startup")
                        logging.critical("Please correct settings file or create new file with -C option")
                        print("Invalid settings file detected! Aborting startup")
                        print("Please correct settings file or create new file with -C option")
                        sys.exit("Invalid settings") #system ends immediately if it detects file with possibly incompatible settings
                elif input_array[0].strip() == "debug":
                    if input_array[1].strip() == "True":
                        self.debug = True
                elif input_array[0].strip() == "serverport":
                    self.serverport = int(input_array[1].strip())
                elif input_array[0].strip() == "webport":
                    self.serverport = int(input_array[1].strip())
                elif input_array[0].strip() == "useweb":
                    if input_array[1].strip() == "True":
                        self.useweb = True



    def create_settings(self, version):
        logging.critical("Creating default settings file")
        #savefile = os.path.join(self.tetherdir, "settings.cfg")
        logging.critical("saving defaults to settings.cfg")
        self.savesettings=open("settings.cfg", mode="w", encoding="utf-8")
        self.savesettings.write("version="+str(version)+"\n")
        self.savesettings.write("debug="+str(self.debug)+"\n")
        self.savesettings.write("serverport="+str(self.serverport)+"\n")
        self.savesettings.write("webport="+str(self.webport)+"\n")
        self.savesettings.write("useweb="+str(self.useweb)+"\n")
        self.savesettings.close()
        logging.critical("Default settings successfully saved")

    def check_settings(self):
        logging.debug("")
        test = True

    def abort_load_settings():
        logging.debug("")
        logging.critical("Invalid settings file detected! aborting startup")
        logging.critical("Please correct settings file or create new file with -C option")
        print("Invalid settings file detected! Aborting startup")
        print("Please correct settings file or create new file with -C option")
        sys.exit("Invalid settings")


    def abort_settings():
        logging.debug("")
        logging.critical("Invalid settings file detected! aborting startup")
        logging.critical("Please correct settings file or create new file with -C option")
        print("Invalid settings file detected! Aborting startup")
        print("Please correct settings file or create new file with -C option")
        sys.exit("Invalid settings")
