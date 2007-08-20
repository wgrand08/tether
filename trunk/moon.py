from __future__ import division

import pygame, sys,os
from pygame.locals import *

SIZE = 800,800

def main():
    pygame.display.init()
    pygame.font.init()

    pygame.display.set_caption("Moonbase Thingy")
    window = pygame.display.set_mode(SIZE)
    screen = pygame.display.get_surface() 

    window.fill(color.black)
    image_test = pygame.image.load("jupiter.gif")
    pygame.display.update()
    screen.blit(image_test, (0, 50))

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
        self.font = pygame.font.Font(None, 50)

        self.text = "A picture of Jupiter"
        self.rect = (0,0,0,0)

        self.cursor = self.font.render("|", True, color.green)

        self.update()

    def key(self, key):
        if key.key == K_BACKSPACE:
            self.text = self.text[:-1]
        else:
            self.text += key.unicode

        self.update()

    def update(self):
        self.window.fill(color.black, self.rect)
        surface = self.font.render(self.text, True, color.white)
        self.rect = self.window.blit(surface, (0,0))
        cursorrect = self.window.blit(self.cursor, (surface.get_width(),0))
        self.rect.union_ip(cursorrect)
        pygame.display.update()

class color:
    def __getattr__(self, name):
        return pygame.Color(name)
    __getitem__ = __getattr__
color = color()

if __name__ == "__main__":
    main()
