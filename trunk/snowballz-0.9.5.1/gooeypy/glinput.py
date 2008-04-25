import texture
from cellulose import *
import input
import util
from OpenGL.GL import *
import os


class Input(input.Input):

    def font_clip_rect(self):
        vx = max(self.font.size(self.value)[0] - self.size[0], 0)
        return pygame.Rect((vx, 0), self.size)
    font_clip_rect = ComputedCellDescriptor(font_clip_rect)

    def font_clip_rect(self):
        vx = max(self.font.size(self.value)[0] - self.size[0], 0)
        return (vx, 0, self.size[0], self.size[1])
    font_clip_rect = ComputedCellDescriptor(font_clip_rect)

    def font_value(self):
        surf = self.font.render(self.value, self.style_option["antialias"],
                self.style_option["color"])
        t = texture.Texture(surf)
        if t.width > self.font_clip_rect[2]:
            t = t.sub(*self.font_clip_rect)
        return t
    font_value = ComputedCellDescriptor(font_value)

    def font_y(self):
        return self.pos[1] - self.style_option["padding-top"]
    font_y = ComputedCellDescriptor(font_y)

    def draw_widget(self):
        if self.value:
            glPushMatrix()
            glTranslatef(self.font_x, util.screen_height-self.font_y-self.height, 0)
            self.font_value.render()
            glPopMatrix()

        if self.focused:
            w,h = self.font.size(self.value[0:self.cur_pos])
            x = min(w, self.size[0])
            color = self.style_option["color"]
            color = [c/255.0 for c in color]
            glColor3f(*color)
            glPushMatrix()
            glTranslatef(self.font_x+x, util.screen_height-self.font_y-self.height, 0)
            glBegin(GL_QUADS)
            glVertex2i(0,0)
            glVertex2i(2, 0)
            glVertex2i(2, self.size[1])
            glVertex2i(0, self.size[1])
            glEnd()
            glPopMatrix()
            glColor3f(1,1,1)