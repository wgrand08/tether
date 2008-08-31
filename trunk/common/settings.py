# OpenRTS - Copyright (C) 2006 The OpenRTS Project
#
# OpenRTS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# OpenRTS is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

import os, sys
import string
import os, os.path
from xml.dom import minidom, Node

import logging


#****************************************************************************
#  This class reads game settings from a XML file.
#****************************************************************************
class GameSettings:

    def __init__(self):
        filename = os.path.join('data', 'settings.xml');
        self.rulesets = {};

        doc = minidom.parse(filename);
        rootNode = doc.documentElement;

        settingNode = rootNode.getElementsByTagName('openrts').item(0);
        self.version = settingNode.getAttribute('version');

        settingNode = rootNode.getElementsByTagName('fullscreen').item(0);
        self.fullscreen = settingNode.getAttribute('enabled') == 'false';

        settingNode = rootNode.getElementsByTagName('tileset').item(0);
        self.tileset = settingNode.getAttribute('src');

        settingNode = rootNode.getElementsByTagName('ruleset_default').item(0);
        self.ruleset_name = settingNode.getAttribute('name');

        for settingNode in rootNode.getElementsByTagName('ruleset'):
            rulesetname = settingNode.getAttribute('name');
            rulesetsrc = settingNode.getAttribute('src');
            self.rulesets.update({rulesetname:rulesetsrc});

        settingNode = rootNode.getElementsByTagName('screen').item(0);
        self.screen_width = int(settingNode.getAttribute('width'));
        self.screen_height = int(settingNode.getAttribute('height'));

        settingNode = rootNode.getElementsByTagName('language').item(0);
        self.language = settingNode.getAttribute('locale');

        settingNode = rootNode.getElementsByTagName('psyco-jit').item(0);
        self.psyco = settingNode.getAttribute('enabled') == 'true';

        self.dependent = False;
        self.clock = 1;
        self.version = 0.3;
        self.playername = "Commander";
        self.fullscreen = False;
        self.WINDOW_SIZE = self.screen_width,self.screen_height = 1024,768;
        self.theme = "";
        self.appRunning = True;
        self.screenRunning = True;
        self.debug = False;
        self.moonPyApp = "";
        self.activeScreen = "";
        self.hostIP = "127.0.0.1";
        self.playerID = 0;
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
                if input_array[0].strip() == "theme":
                    self.theme = input_array[1].strip();
        if badsettings == True:
            self.WINDOW_SIZE = self.screen_width,self.screen_height = 1024,768;
            self.fullscreen = False;
            self.playername = "Commander";
            self.theme = "default";
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
        self.savesettings.write("theme="+str(self.theme)+"\n");


    def toggle_fullscreen():
        if self.fullscreen == True:
            self.fullscreen = False;
            pygame.display.set_mode(self.WINDOW_SIZE);        else:
            self.fullscreen = True;            pygame.display.set_mode(self.WINDOW_SIZE, pygame.FULLSCREEN);
	


