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

import os, sys
import string
import os, os.path

import logging


#****************************************************************************
#  This class reads game settings from various files
#****************************************************************************
"""The game settings themselves are stored within a plaintext file."""
class GameSettings:

    def __init__(self):
        self.rulesets = {};

        self.tileset = "data/graphics/tileset.xml"; 
        self.ruleset_name = "MoonPy Default"; 
        rulesetname = "MoonPy Default";
        rulesetsrc = "data/ruleset/ruleset.xml"; 
        self.rulesets.update({rulesetname:rulesetsrc});
        self.screen_width = 1024; 
        self.screen_height = 768;
        self.language = "en" 
        self.psyco = "true";

        self.version = 0.405;
        self.playername = "Commander";
        self.fullscreen = False;
        self.WINDOW_SIZE = self.screen_width,self.screen_height = 1024,768;
        self.appRunning = True;
        self.screenRunning = True;
        self.debug = False;
        self.defaultIP = "127.0.0.1";
        self.language = "en";


    def get_ruleset_src(self, rulesetname):
        return self.rulesets[rulesetname];

    def load_settings(self):
        badsettings = True;
        if os.path.exists("settings.cfg"):
            settingsfile=open("settings.cfg", 'r');
            for line in settingsfile:
                line=line.strip();
                if line == "" or line[0] == "#":
                    continue;
                input_array = line.split("=", 1);
                if input_array[0].strip() == "version":
                    if float(input_array[1].strip()) == self.version: #checking file version to avoid incompatibilities
                        badsettings = False; #confirmation that file exists and has correct version
                if badsettings == False:
                    if input_array[0].strip() == "fullscreen":
                        if input_array[1].strip() == "True":
                            self.fullscreen = True;
                        elif input_array[1].strip() == "False":
                            self.fullscreen = False;
                    if input_array[0].strip() == "xres":
                        self.screen_width = int(input_array[1].strip());
                    if input_array[0].strip() == "yres":
                        self.screen_height = int(input_array[1].strip());
                    if input_array[0].strip() == "name":
                        self.playername = input_array[1].strip();
        if badsettings == True:
            self.save_settings();
        else:
            self.WINDOW_SIZE = self.screen_width,self.screen_height;


    def save_settings(self):
        self.savesettings=open("settings.cfg", 'w');
        self.savesettings.write("version="+str(self.version)+"\n");
        self.savesettings.write("fullscreen="+str(self.fullscreen)+"\n");
        self.savesettings.write("xres="+str(self.screen_width)+"\n");
        self.savesettings.write("yres="+str(self.screen_height)+"\n");
        self.savesettings.write("name="+str(self.playername)+"\n");

	


