""" An panel for making working with selected units easier. """

from OpenGL.GL import *
import data
import pygame
from pygame.locals import *
from textures import Texture

_display = False
_selected_units = {"worker":0, "snowballer":0}

def update():
    global _display, _selected_units
    if data.selected_units:
        _display = True
        _selected_units = {"worker":0, "snowballer":0}
        for u in data.selected_units:
            _selected_units[u.type] += 1
    else:
        _display = False


def draw():

    #glColor4f(0, 0, 0, 0.6)
    #data.draw_box(data.view.w-64, 0, 64, 160)
    glColor4f(1,1,1,1)
    Texture.get("data/selectctrl.png").render(data.view.w-64, 0, invert_y=False)


    t = data.penguins["walk"].images[("idle", (0,1))]

    if _selected_units["snowballer"]:
        to = data.penguins["snowballerwalk"].images[("idle", (0,1))]
        x = data.view.w-64+16
        y = 111
        glColor4f(1,1,1,1)
        t.render(x, y, invert_y=False)
        glColor3f(*data.player.glcolor)
        to.render(x, y, invert_y=False)
        data.chat_font.render(x+8, y-19, str(_selected_units["snowballer"]),
                (0,0,0))

    if _selected_units["worker"]:
        to = data.penguins["workerwalk"].images[("idle", (0,1))]
        x = data.view.w-64+16
        y = 58
        glColor4f(1,1,1,1)
        t.render(x, y, invert_y=False)
        glColor3f(*data.player.glcolor)
        to.render(x, y, invert_y=False)
        data.chat_font.render(x+8, y-19, str(_selected_units["worker"]),
                (0,0,0))

    if _selected_units["worker"] or _selected_units["snowballer"]:
        glColor3f(*data.player.glcolor)
        Texture.get("data/marker_leave.png").render(data.view.w-64+16, 2, 
                invert_y=False)
        glColor3f(1,1,1)


def in_range((x,y)):
    return _display and x > data.view.w-64 and y > data.view.h-160


def click((x,y)):
    ns = set()
    if y < data.view.h-160+64:
        # Snowballer.
        if not _selected_units["snowballer"]: return
        for u in data.selected_units:
            if u.type is "snowballer":
                ns.add(u)
            else:
                u.selected = False
        data.selected_units = ns
    elif y < data.view.h-160+128:
        # Worker.
        if not _selected_units["worker"]: return
        for u in data.selected_units:
            if u.type is "worker":
                ns.add(u)
            else:
                u.selected = False
        data.selected_units = ns
    else:
        import ctrl
        ctrl.disban_units()
