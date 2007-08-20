from __future__ import division

import pygame, sys,os
from pygame.locals import *

SIZE = XSIZE,YSIZE = 800,800

def main():
    pygame.display.init()
    pygame.font.init()

    pygame.key.set_repeat(250, 50)

    pygame.display.set_caption("Moonbase Thingy")
    window = pygame.display.set_mode(SIZE)
    screen = pygame.display.get_surface() 

    window.fill(color.black)
    image_test = pygame.image.load("images/jupiter.gif")
    screen.blit(image_test, (0, 50))

    pygame.display.update()

    inputbox = InputBox(window)

    while True:
        e = pygame.event.wait()
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                break
            else:
                inputbox.key(e)
        elif e.type == QUIT:
            break

class InputBox:
    def __init__(self, window):
        self.window = window

        self.rect = Rect(0,0,XSIZE,50)
        self.font = pygame.font.Font(None, self.rect.height)

        self.text = "A picture of Jupiter (type something)"
        self.drawn = (0,0,0,0)

        self.cursor = self.font.render("|", True, color.green)
        self.cursorwidth = self.cursor.get_width()

        self.update()

    def key(self, key):
        if key.key == K_BACKSPACE:
            self.text = self.text[:-1]
        else:
            self.text += key.unicode

        self.update()

    def update(self):
        self.window.fill(color.black, self.drawn)
        surface = self.font.render(self.text, True, color.white)
        width = surface.get_width()

        overage = max(0, width + self.cursorwidth - self.rect.width)
        draw = Rect(overage,0,self.rect.width,self.rect.height)
        self.drawn = self.window.blit(surface, (0,0), draw)

        cursorrect = self.window.blit(self.cursor, (self.drawn.right,0))
        self.drawn.union_ip(cursorrect)

        pygame.display.update()

class color:
    def __getattr__(self, name):
        return pygame.Color(name)
    __getitem__ = __getattr__
color = color()

if __name__ == "__main__":
    main()
