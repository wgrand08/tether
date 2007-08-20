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

    inputbox = InputBox(window, Rect(XSIZE/4, YSIZE/2-25, XSIZE/2, 50))
    inputbox.text = "A picture of Jupiter (type something)"

    pygame.display.update()

    while True:
        e = pygame.event.wait()
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                break
            else:
                inputbox.key(e)
        elif e.type == QUIT:
            break

class InputBox(object):
    def __init__(self, window, rect):
        self.window = window
        self.rect = rect

        self.background = pygame.Surface(self.rect.size)
        self.background.blit(window, (0,0), self.rect)

        self.font = pygame.font.Font(None, self.rect.height)
        self._text = ""

        self.cursor = self.font.render("|", True, color.green)
        self.textwidth = self.rect.width - self.cursor.get_width()

        self.update()

    def _get_text(self):
        return self._text

    def _set_text(self, text):
        self._text = text
        self.update()

    text = property(_get_text, _set_text)

    def key(self, key):
        if key.key == K_BACKSPACE:
            self._text = self._text[:-1]
        else:
            self._text += key.unicode

        self.update()

    def update(self):
        surface = self.font.render(self._text, True, color.white)
        overage = max(0, surface.get_width() - self.textwidth)

        draw = Rect(overage, 0, self.rect.width, self.rect.height)

        self.window.blit(self.background, self.rect)
        drawn = self.window.blit(surface, self.rect, draw)
        self.window.blit(self.cursor, drawn.topright)

        pygame.display.update(self.rect)

    def close(self):
        self.window.blit(self.background, self.rect)
        pygame.display.update(self.rect)
        return self._text

class color:
    def __getattr__(self, name):
        return pygame.Color(name)
    __getitem__ = __getattr__
color = color()

if __name__ == "__main__":
    main()
