""" Copyright (C) 2007 Isaac Carroll, Kevin Clement, Jon Handy

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from __future__ import division

import pygame, sys,os
from pygame.locals import *
from threading import Thread
from Queue import Queue

window_xsize = 800
window_ysize = 800
SIZE = XSIZE,YSIZE = window_xsize,window_ysize

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
    image_test = pygame.image.load("images/test.png")
    window.blit(image_test, (0, 50))
    pygame.display.update()

    inputbox = InputBox(window, Rect(XSIZE/8, YSIZE/2-25, XSIZE*3/4, 50))
    inputbox.text = "A pointless picture (type something)"

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
