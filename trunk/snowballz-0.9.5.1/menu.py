import sys, os
import pygame
from gooeypy import gl as gui
from gooeypy.const import *

from OpenGL.GL import *
from gooeypy.texture import Texture

import settings
import glob

import zipfile
from cStringIO import StringIO
from ConfigParser import ConfigParser

import data, rabbyt

class Map:
    def __init__(self, name, image, filename, iconfilename, description,
                objectives):
        self.name = name
        self.image = image
        self.filename = filename
        self.iconfilename = iconfilename
        self.returnvalue = None
        self.description = description
        self.objectives = objectives


class Main:
    def __init__(self, (vw,vh)):
        self.playing = False

        self.cur_map = 0
        self.list_of_maps = []

        # Load maps.
        for f in glob.glob(os.path.join("maps", "*.zip")):
            filename = f.split(os.path.sep)[-1].split(".")[0]
            z = zipfile.ZipFile(os.path.join(*f.split(os.path.sep)), "r")
            settingsfile = z.read("settings.ini")
            cf = ConfigParser()
            cf.readfp(StringIO(settingsfile))
            if "icon.png" in z.namelist():
                iconfilename = StringIO(z.read("icon.png"))
            else:
                iconfilename = "data/noicon.png"
            name = cf.get("map", "name")
            description = cf.get("map", "description")
            objectives = cf.get("map", "objectives")
            icon = pygame.image.load(iconfilename)
            self.list_of_maps.append(Map(name, icon, filename, icon,
                    description, objectives))
        gui.init(vw,vh)
        self.bg = Texture("data/menu.png").sub(0,0,640,480)

        self.x = x = (vw-640)/2
        self.y = y = (vh-480)/2

        self.vh = vh
        self.vw = vw


        self.app = gui.App(width=640, height=480, x=x, y=y, bgimage="none", theme="snowballz")
        menus = Menus(width=640, height=480)
        self.app.add(menus)

        # Now let's create our menus.
        mainmenu = gui.Container(width=640, height=480)
        b1 = gui.Button("Single Play")
        b1.connect(CLICK, menus.activate, 1)
        b2 = gui.Button("Lan Game")
        b2.connect(CLICK, menus.activate, 3)
        b3 = gui.Button("Settings")
        b3.connect(CLICK, menus.activate, 2)
        b4 = gui.Button("Quit")
        b4.connect(CLICK, self.exit)
        menubar = gui.HBox(align="center", valign="bottom", y=-15, spacing=20)
        menubar.add(b1, b2, b3, b4)
        mainmenu.add(menubar)

        back_button = gui.Button("Back")
        back_button.connect(CLICK, menus.activate, 0)

        # Play.
        menu1 = gui.Container(width=640, height=480)
        #w1 = gui.Label("Map", align="center", valign="center",
                #font_size=25)
        p = gui.Image("data/map_img_panel.png", x=20, y=125)
        self.singleplay_image = gui.Image(self.list_of_maps[self.cur_map].iconfilename, x=25, y=130)
        self.singleplay_label = gui.Label(self.list_of_maps[self.cur_map].name, x=300, y=260, font_size=25)
        self.singleplay_objectives = gui.Label(self.list_of_maps[self.cur_map].objectives, x=300, y=310, font_size=13)
        self.singleplay_description = gui.Label(self.list_of_maps[self.cur_map].description, x=300, y=290, font_size=13)
        b = gui.Button("Play")
        b.connect(CLICK, self.singleplay)
        nb = gui.Button("Next")
        nb.connect(CLICK, self.seek, 1)
        pb = gui.Button("Previous")
        pb.connect(CLICK, self.seek, -1)
        menubar = gui.HBox(align="center", valign="bottom", y=-15, spacing=20)
        menubar.add(back_button, pb, nb, b)
        menu1.add(menubar, p, self.singleplay_image, self.singleplay_label,
                self.singleplay_objectives, self.singleplay_description)

        ob = gui.Button("Back")
        ob.connect(CLICK, menus.activate, 0)

        # Options.
        menu2 = gui.Container(width=640, height=480)
        option_table = OptionTable(align="center", valign="top", spacing=10, bgimage="bg.png repeat", padding=10)
        option_table.add("fullscreen", ("0", "1"), "Fullscreen")
        ress = settings.get_res_available()
        reslabels = ["%i x %i"%r for r in ress]
        reses = []
        for i in xrange(len(ress)):
            reses.append(str(i))
        option_table.add("resolution", reses, "Resolution", labels=reslabels)
        option_table.add("daynight", ("0", "1"), "Day/Night cycles")
        #option_table.add("footprints", ("0", "1"), "Footprints")
        option_table.add("smoke", ("0", "1"), "Smoke")
        option_table.add("footprints", ("0", "1"), "Footprints")
        option_table.add("snowballdetail", ("1", "2", "3"), "Snowball detail",
                labels=("Low", "Medium", "High"))

        pname = gui.Input(settings.config.get("player", "name"), width=140,
                disallowed_chars=[" "])
        hb = gui.HBox(spacing="20")
        hb.add(gui.Label("Name:", font_size=20, min_width=180), pname)
        super(OptionTable, option_table).add(hb)
        def savename():
            settings.config.set("player", "name", pname.value)
            settings.save_config()
        pname.connect(CHANGE, savename)

        option_table.add("cursor", ("0", "1"), "Ice Cursor",
                labels=("Off", "On"))

        menubar = gui.HBox(align="center", valign="bottom", y=-15, spacing=20)
        menubar.add(ob)
        menu2.add(menubar, option_table)

        b_button = gui.Button("Back")
        b_button.connect(CLICK, menus.activate, 0)

        # Lan game.
        menu3 = gui.Container(width=640, height=480)
        b1 = gui.Button("Host a game")
        b1.connect(CLICK, menus.activate, 5)
        b2 = gui.Button("Join a game")
        b2.connect(CLICK, menus.activate, 4)
        menubar = gui.HBox(align="center", valign="bottom", y=-15, spacing=20)
        menubar.add(b_button,b1, b2)
        menu3.add(menubar)

        l_button = gui.Button("Back")
        l_button.connect(CLICK, menus.activate, 3)

        # Client. TODO: Find avialible games.
        menu4 = gui.Container(width=640, height=480)
        l = gui.Label("Host:", font_size=20)
        self.host =  gui.Input(width=200, disallowed_chars=[" "])
        b1 = gui.Button("Go!")
        b1.connect(CLICK, self.client)
        menubar = gui.HBox(align="center", valign="center", y=-15, spacing=20)
        menubar.add(l, self.host, b1)
        
        mbar = gui.HBox(align="center", valign="bottom", y=-15, spacing=20)
        mbar.add(l_button)
        menu4.add(menubar, mbar)

        ml_button = gui.Button("Back")
        ml_button.connect(CLICK, menus.activate, 3)

        # MP lobby.
        menu5 = gui.Container(width=640, height=480)
        self.servermap = gui.SelectBox(align="left", valign="center", width=200,
                height=300, scrollable=True)
        for m in self.list_of_maps:
            self.servermap.add(m.name, m.filename)
        b1 = gui.Button("Host")
        b1.connect(CLICK, self.server)
        menubar = gui.HBox(align="center", valign="bottom", y=-15, spacing=20)
        menubar.add(ml_button, b1)
        menu5.add(menubar, self.servermap)


        # Add menus
        menus.add(mainmenu, menu1, menu2, menu3, menu4, menu5)

        # Active the mainmenu.
        menus.activate(0)


    def run(self):
        clock = pygame.time.Clock()
        glClearColor(0, 0, 0, 1)
        while not self.playing:
            clock.tick(35)
            glClear(GL_COLOR_BUFFER_BIT)

            # Draw background.
            glPushMatrix()
            glTranslatef(self.x,self.vh-480-self.y,1)
            self.bg.render()
            glPopMatrix()
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    self.exit()
            self.app.run(events)
            self.app.draw()

            #glMatrixMode(GL_PROJECTION)
            #glLoadIdentity()
            #glOrtho(0, self.vw, self.vh, 0, -50, 50)
            #glMatrixMode(GL_MODELVIEW)
            #glLoadIdentity()
            
            #rabbyt.set_time(pygame.time.get_ticks())
            #data.snowflakes.run(True)

            #glMatrixMode(GL_PROJECTION)
            #glLoadIdentity()
            #glOrtho(0, data.view.w, 0, data.view.h, -50, 50)
            #glMatrixMode(GL_MODELVIEW)
            #glLoadIdentity()
    
            pygame.display.flip()
            Texture.bound_texture_id = None
        self.playing = False
        return self.returnvalue

    def seek(self, direction):
        self.cur_map += direction
        if self.cur_map < 0:
            self.cur_map = len(self.list_of_maps) - 1
        elif self.cur_map > len(self.list_of_maps) -1:
            self.cur_map = 0

        i = self.list_of_maps[self.cur_map].image
        self.singleplay_image.value = Texture(i).sub(0,0, i.get_width(), i.get_height())
        self.singleplay_label.value = self.list_of_maps[self.cur_map].name
        self.singleplay_objectives.value = self.list_of_maps[self.cur_map].objectives
        self.singleplay_description.value = self.list_of_maps[self.cur_map].description

    def exit(self):
        sys.exit()

    def singleplay(self):
        self.playing = True
        self.returnvalue = self.list_of_maps[self.cur_map].filename, "single", None

    def server(self):
        if not self.servermap.selected:
            return
        self.playing = True
        self.returnvalue = self.servermap.values.pop(), "server", None

    def client(self):
        self.playing = True
        self.returnvalue = self.list_of_maps[self.cur_map].filename, "client", self.host.value



class OptionTable(gui.VBox):

    def add(self, option, values, label, labels=("Off", "On")):
        switch = gui.Switch(settings.get_option(option), options=values,
                labels=labels, min_width=140)
        switch.connect(CHANGE, settings.toggle, option, values)

        hb = gui.HBox(spacing="20")
        hb.add(gui.Label(label+":", font_size=20, min_width=180), switch)
        super(OptionTable, self).add(hb)



class Menus(gui.Container):
    """ We have this to hold all of our menus. Keeps things clean and tidy. """

    def activate(self, index):
        """ Basically what we do here is deactivate all the widgets (menus) and
            then activate the menu at index. When a widget is not active, it
            simply disappears. """
        for w in self.widgets:
            w.active = False
        self.widgets[index].active = True
