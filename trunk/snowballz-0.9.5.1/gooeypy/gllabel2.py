import texture
from cellulose import *
import label
import util
from OpenGL.GL import *
import os
import glFreeType


class Label(label.Label):

    def font(self):
        p = os.path.join(util.app.path, self.style_option["font-family"])
        return glFreeType.Font.get(p, self.style_option["font-size"])
    font = ComputedCellDescriptor(font)

    def width(self):
        # Hack to set textlen! REALLY BAD!
        if not self.font.textlen:
            self.font.glPrint (10, 10, self.value)
        w = self.font.textlen
        return util.widgets.Widget.width.function(self, w)
    width = ComputedCellDescriptor(width)

    def height(self):
        h = self.style_option["font-size"]
        return util.widgets.Widget.height.function(self, h)
    height = ComputedCellDescriptor(height)

    def draw_widget(self):
        # FIXME: clipping?
        color = self.style_option["color"]
        color = [c/255.0 for c in color]
        glColor3f(*color)
        self.font.glPrint (self.font_x, util.screen_height-self.font_y-\
                self.height, self.value)
        glColor3f(1,1,1)