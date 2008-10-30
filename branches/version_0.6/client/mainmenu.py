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

import pygame
import gooeypy as gui
from gooeypy.const import *
import gameclient


class MainMenu:
    def __init__(self, client):
        clock = pygame.time.Clock()
        self.client = client;
        if (self.client.settings.fullscreen):
            screen_mode = pygame.FULLSCREEN;
        else:
            screen_mode = 0;
        screen_width = self.client.settings.screen_width; 
        screen_height = self.client.settings.screen_height; 
        screen = pygame.display.set_mode((screen_width, screen_height), screen_mode);
        pygame.display.set_caption("MoonPy %s" % (self.client.settings.string_version));
        self.client.screen = screen;
        gui.init(screen_width, screen_height);
        app = gui.App(width=1024, height=768)
        settings_button = gui.Button("settings", x=500, y=500)
        app.add(settings_button);
        run = True;
        while run:
            clock.tick(30)

            # We do this so we can share the events with the gui.
            events = pygame.event.get()

            for event in events:
                if event.type == QUIT:
                    run = False;

            app.run(events)
            app.draw()
            gui.update_display()



