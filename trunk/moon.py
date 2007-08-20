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

        self.rect = Rect(XSIZE/4,YSIZE/2-25,XSIZE/2,50)

        self.background = pygame.Surface(self.rect.size)
        self.background.blit(window, (0,0), self.rect)

        self.font = pygame.font.Font(None, self.rect.height)

        self.text = "A picture of Jupiter (type something)"

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
        self.window.blit(self.background, self.rect)

        surface = self.font.render(self.text, True, color.white)
        width = surface.get_width()

        overage = max(0, width + self.cursorwidth - self.rect.width)
        draw = Rect(overage,0,self.rect.width,self.rect.height)
        drawn = self.window.blit(surface, self.rect, draw)

        self.window.blit(self.cursor, drawn.topright)

        pygame.display.update(self.rect)

class color:
    def __getattr__(self, name):
        return pygame.Color(name)
    __getitem__ = __getattr__
color = color()

if __name__ == "__main__":
    main()
