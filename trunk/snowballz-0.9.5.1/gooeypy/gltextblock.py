import pygame
from pygame.locals import *
import util
from const import *

from cellulose import *

from textblock import TextBlock as SDLTextBlock
from OpenGL.GL import *
from texture import Texture


class TextBlock(SDLTextBlock):
    def texture(self):
        linenum = 0
        line_w = self.style_option["width"]
        _,line_h = self.font.size("e")
        surf = pygame.Surface((line_w,line_h*len(self.lines)))
        #print (line_w,line_h*len(self.lines))
        #surf.set_colorkey((0,0,0,0))
        color = [i//255 for i in self.style_option["color"]]
        for line in self.lines:
            x = 0
            y = line_h*linenum
            surf.blit(self.font.render(line, self.style_option["antialias"],
                    color), (x,y))
            linenum += 1
        return Texture(surf)
    texture = ComputedCellDescriptor(texture)

    def draw_widget(self):
        # FIXME: Find out how to draw font in GL.
        pass
        #glPushMatrix()
        #glTranslatef(self.font_x, util.screen_height-self.font_y-self.height, 0)
        #self.texture.render()
        #glPopMatrix()