import pygame
from pygame.locals import *
import util
from const import *

from cellulose import *


class Image(util.widgets.Widget):
    """
    Image(value) -> Image widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Basic widget for simply displaying an image. value should be a pygame
    surface.
    """
    value = util.ReplaceableCellDescriptor()

    def __init__(self, value, **params):
        util.widgets.Widget.__init__(self,**params)
        self.value = value

    def draw_widget(self):
        util.blit(self.value, self.pos, clip_rect=self.value.get_rect())

    def width(self):
        return self.value.get_width()
    width = ComputedCellDescriptor(width)

    def height(self):
        return self.value.get_height()
    height = ComputedCellDescriptor(height)