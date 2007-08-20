from __future__ import division

import pygame, sys,os
from pygame.locals import *
from threading import Thread
from Queue import Queue

SIZE = XSIZE,YSIZE = 800,800

def main():
    pygame.display.init()
    pygame.font.init()

    pygame.key.set_repeat(250, 50)

    pygame.display.set_caption("Moonbase Thingy")
    window = pygame.display.set_mode(SIZE)

    window.fill(color.black)
    pygame.display.update()

    q = Queue()
    stuff = Thread(target=dostuff, args=(window, q.get))
    stuff.setDaemon(True)
    stuff.start()

    while True:
        e = pygame.event.wait()
        if e.type == KEYDOWN:
            q.put(e)
        elif e.type == QUIT:
            break

def dostuff(window, nextevent):
    image_test = pygame.image.load("images/jupiter.gif")
    window.blit(image_test, (0, 50))
    pygame.display.update()

    inputbox = InputBox(window, Rect(XSIZE/8, YSIZE/2-25, XSIZE*3/4, 50))
    inputbox.text = "A picture of Jupiter (type something)"

    while True:
        k = nextevent()
        if k.key == K_ESCAPE:
            pygame.event.post(pygame.event.Event(QUIT))
        else:
            inputbox.key(k)

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
