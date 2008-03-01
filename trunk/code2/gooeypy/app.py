""" <title>Main GUI element</title> """
import util
import operator
import os, sys
import pygame
#from container import Container

import cellulose

pygame.init()

class App(util.widgets.Container):
    """
    App([theme]) -> App widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    This is actually a container widget with function for running itself and
    all widgets in it. It also has functions for parsing and using themes.
    Applications may only have one App instance (this may change in the
    future).

    Example of use
    --------------
    ::

        myapp = App()

        mywidget = Widget()
        myapp.add(mywidget)

        while True:
            events = pygame.event.get() # We do this so that we can use the
                                        # pygame events in both the gui and
                                        # our program.
            app.run(events)
            app.draw()



    Arguments
    ---------
    theme
        The name of the theme you want to use. The name should
        correspond like so: path_to_project/data/themes/[themename]/
        And within that folder there should be a config.txt file.
    """

    def __init__(self, theme="default", **params):
        util.app = self
        self.theme = {}
        self.theme_name = theme
        self.load_theme(theme)

        super(App, self).__init__(**params)

    def run(self, events):
        for c in util.custom_cells:
            c.dependency_changed()
        cellulose.default_observer_bank.flush()
        for e in events:
            # Normally should call _event... but that makes it run a bit sluggish.
            self.event(e)

    def get_style(self, w):
        if self.theme.has_key(w.__class__.__name__):
            t = self.theme[w.__class__.__name__]
            n = w.__class__.__name__
            while True:
                if w.parent:
                    w = w.parent
                    if self.theme.has_key(w.__class__.__name__+" "+n):
                        n = w.__class__.__name__+" "+n
                        t += self.theme[n]
                else:
                    break
            return t
        else:
            return ""


    def get_font(self, file, size):
        size = int(size)
        return pygame.font.Font(os.path.join(self.path, file), size)


    def get_image_path(self, path):
        if os.path.isfile(os.path.join(self.path, path)):
            path = os.path.join(self.path, path)
        return path

    def get_image(self, path):
        if type(path) != str:
            return pygame.image.load(path)
        path = self.get_image_path(path)
        return util.get_image(path)

    def load_theme(self, theme_name):
        paths = []
        paths.append(os.path.join("data", "themes", theme_name))
        paths.append(os.path.join(os.path.dirname(__file__), "data", "themes", theme_name))
        paths.append(os.path.join("..", "data", "themes", theme_name))
        paths.append(os.path.join("..", "..", "data", "themes", theme_name))

        self.path = None
        p = None
        for p in paths:
            if os.path.isdir(p):
                self.path = p
                break
        if not self.path:
            print "Failed to find theme!"
            sys.exit()

        cfile = open(os.path.join(self.path, "config.txt"))

        ls = cfile.readlines()

        keys = None
        v = ""

        for l in ls:
            l = l.replace('\n', '')
            l = l.strip()
            if not l or l[0] == "#": continue
            if l[-1] == "{":
                # A definition.
                l = l[0:-2]
                keys = l.split(",")
            elif l == "}":
                # End of section.
                for o in keys:
                    o = o.strip()
                    if not self.theme.has_key(o):
                        self.theme[o] = v
                    else:
                        self.theme[o] += v
                v = ""
                keys = None
            else:
                v += l
