import texture
from cellulose import *
import label
import util
from OpenGL.GL import *

class Label(label.Label):

    def font_value(self):
        surf = self.font.render(self.value, self.style_option["antialias"],
                self.style_option["color"])
        return texture.Texture(surf)
    font_value = ComputedCellDescriptor(font_value)

    def draw_widget(self):
        # FIXME: put clipping.
        if self.value:
            glPushMatrix()
            glTranslatef(self.font_x, util.screen_height-self.font_y-self.height, 0)
            self.font_value.render()
            glPopMatrix()