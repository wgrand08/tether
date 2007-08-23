#!/usr/bin/python2.4

"""Copyright 2007:
    Isaac Carroll, Kevin Clement, Jon Handy, David Carroll, Daniel Carroll

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

import pygame
from pygame.locals import *
import threading
from Queue import Queue
from time import sleep

WINDOW_SIZE = WINDOW_XSIZE,WINDOW_YSIZE = 550,550

CALL = USEREVENT + 0

def main(game):
    game.show(game.loadimage("images/Enceladus.png"), (0,0))
    sleep(2)

    game.showtext("Enter a direction (0-360)", (0,0))
    ShotDirection = int(game.input())
    if (ShotDirection < 0) or (ShotDirection > 360):
		print "Invalid Entry"
    else:
		print ShotDirection

    game.showtext("Enter a power (1-100)", (0,150))
    ShotPower = int(game.input())
    if (ShotPower < 0) or (ShotPower > 100):
		print "Invalid Entry"
    else:
		print ShotPower
	
def mainthread(f):
    def decorated(*args, **kwargs):
        if threading.currentThread() != MAIN_THREAD:
            pygame.event.post(pygame.event.Event(QUIT))
            raise NotMainThread()
        else:
            return f(*args, **kwargs)
    return decorated

class NotMainThread(Exception):
    pass

class Game:
    def __init__(self, mainfn):
        global MAIN_THREAD
        MAIN_THREAD = threading.currentThread()

        pygame.display.init()
        pygame.font.init()

        self.font = pygame.font.Font(None, 50)
        pygame.key.set_repeat(250, 50)
        self.keylistener = None

        pygame.display.set_caption("MoonPy")
        self.window = pygame.display.set_mode(WINDOW_SIZE)

        self.window.fill(color.black)
        pygame.display.update()

        self.gamelogic = threading.Thread(target=self._go, args=(mainfn,))
        self.gamelogic.setDaemon(True)
        self.gamelogic.start()

        while True:
            e = pygame.event.wait()
            if e.type == KEYDOWN:
                if self.keylistener:
                    self.keylistener(e)
            elif e.type == CALL:
                result = e.fn(*e.args)
                e.respond(result)
            elif e.type == QUIT:
                break

    def _go(self, mainfn):
        mainfn(self)
        pygame.event.post(pygame.event.Event(QUIT))

    def loadimage(self, filename):
        return call(self._loadimage, filename)

    @mainthread
    def _loadimage(self, filename):
        return pygame.image.load(filename).convert()

    def show(self, image, pos):
        return call(self._show, image, pos)

    @mainthread
    def _show(self, image, pos):
        rect = self.window.blit(image, pos)
        pygame.display.update(rect)
        return rect

    def showtext(self, text, pos):
        return call(self._showtext, text, pos)

    @mainthread
    def _showtext(self, text, pos):
        surface = self.font.render(text, True, color.white)
        return self._show(surface, (pos))

    def input(self):
        inputbox = call(InputBox, self.window)
        old = self.keylistener
        self.keylistener = inputbox.key
        inputbox.done.wait()
        self.keylistener = old
        return call(inputbox.close)

def call(fn, *args):
    q = Queue()
    e = pygame.event.Event(CALL, fn=fn, args=args, respond=q.put)
    pygame.event.post(e)
    return q.get()

#class TextBox:
#    def __init__(self, window, 

class InputBox:
    @mainthread
    def __init__(self, window, rect=None, text=""):
        self.window = window
        self.rect = rect
        if self.rect is None:
            self.rect = Rect(0, WINDOW_YSIZE-50, WINDOW_XSIZE, 50)

        self.background = pygame.Surface(self.rect.size)
        self.background.blit(window, (0,0), self.rect)

        self.font = pygame.font.Font(None, self.rect.height)
        self.text = text

        self.cursor = self.font.render("|", True, color.green)
        self.textwidth = self.rect.width - self.cursor.get_width()

        self.done = threading.Event()

        self.update()

    @mainthread
    def key(self, key):
        if key.key == K_BACKSPACE:
            self.text = self.text[:-1]
        elif key.key == K_RETURN:
            self.done.set()
        elif key.key == K_ESCAPE:
            self.text = None
            self.done.set()
        else:
            self.text += key.unicode

        self.update()

    @mainthread
    def update(self):
        surface = self.font.render(self.text, True, color.white)
        overage = max(0, surface.get_width() - self.textwidth)

        draw = Rect(overage, 0, self.rect.width, self.rect.height)

        self.window.blit(self.background, self.rect)
        drawn = self.window.blit(surface, self.rect, draw)
        self.window.blit(self.cursor, drawn.topright)

        pygame.display.update(self.rect)

    @mainthread
    def close(self):
        self.window.blit(self.background, self.rect)
        pygame.display.update(self.rect)
        return self.text

class color:
    def __getattr__(self, name):
        return pygame.Color(name)
    __getitem__ = __getattr__
color = color()

if __name__ == "__main__":
    Game(main)
