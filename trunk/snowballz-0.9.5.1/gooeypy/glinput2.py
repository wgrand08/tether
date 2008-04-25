import texture
from cellulose import *
import input
import util
from OpenGL.GL import *
import os
import glFreeType

class Input(input.Input):

    def font(self):
        p = os.path.join(util.app.path, self.style_option["font-family"])
        return glFreeType.Font.get(p, self.style_option["font-size"])
    font = ComputedCellDescriptor(font)

    def width(self):
        return util.widgets.Widget.width.function(self)
    width = ComputedCellDescriptor(width)

    def height(self):
        h = self.style_option["font-size"] + self.style_option["padding-top"]+\
                self.style_option["padding-bottom"]
        return util.widgets.Widget.height.function(self, h)
    height = ComputedCellDescriptor(height)

    def font_x(self):
        x,_ = self.pos
        return x + self.style_option["padding-left"]
    font_x = ComputedCellDescriptor(font_x)

    def font_y(self):
        _,y = self.pos
        return y - self.style_option["padding-top"]
    font_y = ComputedCellDescriptor(font_y)

    def draw_widget(self):
        color = self.style_option["color"]
        color = [c/255.0 for c in color]
        glColor3f(*color)
        self.font.glPrint (self.font_x, util.screen_height-self.font_y-\
                self.height, self.value)
        glColor3f(1,1,1)

        #if self.focused:
            #w,h = self.font.size(self.value[0:self.cur_pos])
            #r = pygame.Surface((2,self.size[1]))
            #r.fill(self.style_option["color"])
            #x = min(w, self.size[0])
            #util.blit(r, (self.font_x+x, self.font_y))
