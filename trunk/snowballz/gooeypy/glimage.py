import pygame
from pygame.locals import *
import util
from const import *

from texture import Texture
from OpenGL.GL import *
from cellulose import *


class Image(util.widgets.Widget):

    value = util.ReplaceableCellDescriptor()

    def __init__(self, value, **params):
        util.widgets.Widget.__init__(self, **params)
        if type(value) == str:
            surf = util.app.get_image(value)
        else:
            surf = value
        self.value = Texture(surf).sub(0,0, surf.get_width(), surf.get_height())

    def draw_widget(self):
        x,y = self.pos
        glPushMatrix()
        glTranslatef(x, util.screen_height-y-self.value.height, 0)
        self.value.render()
        glPopMatrix()