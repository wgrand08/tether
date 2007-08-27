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

import os
import pygame
from pygame.locals import *
import threading
from Queue import Queue
from time import sleep
from itertools import chain, cycle

#TODO(isaac): scrollable map surface
#TODO(isaac): scrolling multiline text box
#TODO(isaac): erasable image

WINDOW_SIZE = WINDOW_XSIZE,WINDOW_YSIZE = 550,550

CALL = USEREVENT + 0

def main(game):
    AnimTestdirectory = "images/AnimTest/"
    AnimTestimagenames = [AnimTestdirectory + name for name in os.listdir(AnimTestdirectory)
                  if name.endswith(".png")]
    AnimTestimages = game.loadimages(sorted(AnimTestimagenames))

    background = game.loadimage("images/Enceladus.png")
    game.showimage(background, (0,0))

    animation1 = game.startanimation(cycle(AnimTestimages), 100, (0,100))

    text = game.showtext("Enter a direction (0-360)", (0,0))
    direction = game.input()
    game.erasetext(text)

    animation2 = game.startanimation(cycle(AnimTestimages), 150, (256,100))
    game.playanimation(backandforth(AnimTestimages), 50, (0,356))
    game.stopanimation(animation1)

    text = game.showtext("Enter a power (1-100)", (0,0))
    power = game.input()
    game.erasetext(text)

    game.stopanimation(animation2)
    game.stopanimation(animation3)

    print "Direction =", direction
    print "Power =", power
    sleep(1)

def mainthread(fn):
    "Decorator for code which must run in the main thread."
    def decorated(*args, **kwargs):
        if threading.currentThread() != MAIN_THREAD:
            raise NeedsMainThread()
        else:
            return fn(*args, **kwargs)
    return decorated

class NeedsMainThread(Exception):
    "Thrown when code is mistakenly run outside the main thread."

class Game:
    def __init__(self, gamelogic):
        global MAIN_THREAD
        MAIN_THREAD = threading.currentThread()

        pygame.display.init()
        pygame.font.init()

        self.font = pygame.font.Font(None, 50)
        pygame.key.set_repeat(250, 50)
        self.keylistener = None

        self.inputrect = Rect(0, WINDOW_YSIZE-50, WINDOW_XSIZE, 50)

        pygame.display.set_caption("MoonPy")
        self.window = pygame.display.set_mode(WINDOW_SIZE)

        self.window.fill(color.black)
        pygame.display.update()

        self.gamelogic = threading.Thread(target=self._go, args=(gamelogic,))
        self.gamelogic.setDaemon(True)
        self.gamelogic.start()

        while True:
            e = pygame.event.wait()
            if e.type == KEYDOWN:
                if self.keylistener:
                    self.keylistener(e)
            elif e.type == CALL:
                #TODO(isaac): include caller info in exception tracebacks
                result = e.fn(*e.args)
                e.respond(result)
            elif e.type == QUIT:
                break

    def _go(self, gamelogic):
        try:
            gamelogic(self)
        finally:
            pygame.event.post(pygame.event.Event(QUIT))

    def loadimage(self, filename):
        return call(self._loadimage, filename)

    @mainthread
    def _loadimage(self, filename):
        return pygame.image.load(filename).convert()

    def showimage(self, image, pos):
        return call(self._showimage, image, pos)

    @mainthread
    def _showimage(self, image, pos):
        rect = self.window.blit(image, pos)
        pygame.display.update(rect)
        return rect

    def showtext(self, text, pos):
        return call(TextBox, self.window, text, pos)

    def erasetext(self, textbox):
        return call(textbox.erase)

    def input(self, rect=None):
        if rect is None:
            rect = self.inputrect

        inputbox = call(InputBox, self.window, rect)
        old = self.keylistener
        self.keylistener = inputbox.key
        inputbox.done.wait()
        self.keylistener = old
        return call(inputbox.close)

    def loadimages(self, filenames):
        return [self.loadimage(name) for name in filenames]

    def playanimation(self, images, delay, pos):
        animation = self.startanimation(images, delay, pos)
        animation.wait()

    def startanimation(self, images, delay, pos):
        return call(AnimationBox, self.showimage, self.window, images, delay, pos)

    def stopanimation(self, *animations):
        for animation in animations:
            animation.done = True

        for animation in animations:
            animation.wait()

def call(fn, *args):
    "Cause code to be run in the main thread, and return its result."
    q = Queue()
    e = pygame.event.Event(CALL, fn=fn, args=args, respond=q.put)
    pygame.event.post(e)
    return q.get()

#TODO(isaac): replace all background captures with clip()
def clip(source, rect):
    surface = pygame.Surface(rect.size)
    surface.blit(source, (0,0), rect)
    return surface

class AnimationBox:
    @mainthread
    def __init__(self, showimage, window, images, delay, pos):
        self.showimage = showimage
        self.window = window
        self.delay = delay/1000
        self.pos = pos

        self.images = Peekable(iter(images))
        image = self.images.peek()

        self.rect = Rect(pos, image.get_size())
        self.background = pygame.Surface(self.rect.size)
        self.background.blit(window, (0,0), self.rect)

        self.done = False
        self.finish = threading.Event()
        self.start()

    def start(self):
        self.thread = threading.Thread(target=self._go)
        self.thread.setDaemon(True)
        self.thread.start()

    def _go(self):
        for image in self.images:
            if self.done:
                break
            self.showimage(image, self.pos)
            sleep(self.delay) #TODO(isaac): use event instead

        self.finish.set()

    def wait(self):
        self.finish.wait()
        #TODO(isaac): return values from erase
        call(self.erase)

    @mainthread
    def erase(self):
        self.window.blit(self.background, self.pos)
        pygame.display.update(self.rect)

class TextBox:
    @mainthread
    def __init__(self, window, text, pos):
        self.window = window
        self.text = text
        self.pos = pos

        self.font = pygame.font.Font(None, 50)
        surface = self.font.render(self.text, True, color.white)
        self.rect = Rect(pos, surface.get_size())

        self.background = pygame.Surface(self.rect.size)
        self.background.blit(window, (0,0), self.rect)

        self.window.blit(surface, self.rect)
        pygame.display.update(self.rect)

    @mainthread
    def erase(self):
        self.window.blit(self.background, self.pos)
        pygame.display.update(self.rect)

class InputBox:
    @mainthread
    def __init__(self, window, rect, text=""):
        self.window = window
        self.rect = Rect(rect)

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

class Peekable:
    def __init__(self, iterator):
        self.iterator = iterator
        self.buffer = []

    def __iter__(self):
        return self

    def next(self):
        if self.buffer:
            return self.buffer.pop(0)
        else:
            return self.iterator.next()

    def peek(self):
        if not self.buffer:
            self.buffer.append(self.iterator.next())
        return self.buffer[0]

def backandforth(iterator):
    return chain(iterator, reversed(iterator))

if __name__ == "__main__":
    Game(main)
