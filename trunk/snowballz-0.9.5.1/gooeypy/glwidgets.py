from widget import Widget as SDLWidget
from OpenGL.GL import *
from glstyleset import StyleSet
import util
import pygame
from cellulose import *


class Widget(SDLWidget):

    def draw(self, drawbg=True):
        if self.focused:
            self.repetitive_events()

        x,y = self.pos
        y = util.screen_height-y
        if self.container:
            y -= self.container.offset_y
            if self.container.offset_y > self.y:
                return
            if self.container.offset_y+self.container.height < self.y+self.height:
                return
        glPushMatrix()
        glTranslatef(x, y, 0)
        self.style.draw()
        glPopMatrix()
        self.draw_widget()

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
    rect = ComputedCellDescriptor(rect)