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
import sys
import pygame
from pygame.locals import *
import threading
from Queue import Queue
from time import sleep
from itertools import chain, cycle
import settings
import moonedit
import multiplayer_setup
import solo_setup

#TODO(isaac): scrolling multiline text box
#TODO(isaac): remove local backgrounds

CALL = USEREVENT + 0

def main(game):
    directory = "images/AnimTest/"
    imagenames = [directory + name for name in os.listdir(directory)
                  if name.endswith(".png")]
    images = game.loadimages(sorted(imagenames))

    splash = game.loadimage("images/Enceladus.png")
    #disabling splash screen until image can be properly destroyed
    #game.setbackgroundimage(splash)
    #sleep(2)
    settings.load_settings(game)
    mainloop = True
    pygame.mouse.set_visible(True)
    while mainloop == True:
        buttons = [((10,10), game.textbutton("Solo Game"), "Solo"),
                   ((10,100), game.textbutton("Multiplayer Game"), "Multi"),
                   ((10,200), game.textbutton("Settings"), "Set"),
                   ((10,300), game.textbutton("Editor"), "Editor"),
                   ((10,400), game.textbutton("Quit"), "Quit")]
        maininput = game.buttoninput(buttons)
        if maininput == "Solo":
            solo_setup.solo_screen(game)
        if maininput == "Multi":
            multiplayer_setup.multiplayer_screen(game)
        if maininput == "Set":
            settings.main_settings(game)
        if maininput == "Editor":
            moonedit.editor_screen(game)
        if maininput == "Quit":
            mainloop = False

    """
    animation1 = game.startanimation(cycle(images), 100, (0,100))

    text = game.showtext("Enter a direction (0-360)", (0,0))
    direction = game.input()
    game.erasetext(text)

    animation2 = game.startanimation(cycle(images), 150, (256,100))
    game.playanimation(backandforth(images), 50, (0,356))
    stopanimation(animation1)

    text = game.showtext("Enter a power (1-100)", (0,0))
    power = game.input()
    game.erasetext(text)

    stopanimation(animation2)
    """

    """
    # why does this silently exit the program?
    map = game.createmap((512,512), Rect((19,550-384-19), (512,384)))

    animation1 = map.startanimation(cycle(backandforth(images)), 75, (0,0))
    animation2 = map.startanimation(cycle(images), 80, (256,128))
    sleep(3)
    stopanimation(animation1, animation2)
    #TODO(isaac): close map

    map = game.createmap((2560,384), Rect((19,550-384-19), (512,384)))
    #doesn't work anymore# call(map.surface.fill, color.darkblue)
    map.scrollto(0,0)
    delay = 200
    y = 0
    anims = []
    for x in range(0, 2560, 256):
        loop = cycle(backandforth(images))
        anim = map.startanimation(loop, delay, (x,y))
        anims.append(anim)
        delay -= 10
        y += 50

    for _ in range(2560-512):
        sleep(.01)
        map.scroll(1,0)

    stopanimation(*anims)
    """

def mainthread(fn):
    "Decorator for code which must run in the main thread."
    def decorated(*args, **kwargs):
        if threading.currentThread() == MAIN_THREAD:
            # in main thread, so call normally
            return fn(*args, **kwargs)
        else:
            # not in main thread, so call through event queue
            #TODO(isaac): fix exception reporting problems
            q = Queue()
            e = pygame.event.Event(CALL, fn=fn, args=args, kwargs=kwargs,
                                   respond=q.put)
            pygame.event.post(e)
            raised,outcome = q.get()
            if raised:
                raise outcome
            else:
                return outcome
    return decorated

#TODO(isaac): make Canvas create a surface
class Canvas:
    """A surface with convenient drawing functions.

    Note: Canvas does not create its own surface. Subclasses must do so.
    """
    @mainthread
    def __init__(self):
        self.font = pygame.font.Font(None, 50)

    @mainthread
    def showimage(self, image, pos):
        rect = self.surface.blit(image, pos)
        #TODO(isaac): move update out of Canvas (perhaps overloaded method?)
        pygame.display.update(rect)
        return rect

    def showtext(self, text, pos):
        return TextBox(self, text, pos)

    def erasetext(self, textbox):
        return textbox.erase()

    def playanimation(self, images, delay, pos):
        animation = self.startanimation(images, delay, pos)
        animation.wait()

    def startanimation(self, images, delay, pos):
        return AnimationBox(self, images, delay, pos)

    @mainthread
    def erase(self, *rects):
        for rect in rects:
            self.surface.fill(color.black, rect)
        pygame.display.update(rects)

def stopanimation(*animations):
    for animation in animations:
        animation.done = True

    for animation in animations:
        animation.wait()

class BGCanvas(Canvas):
    """A Canvas with a background Canvas for erasing.

    Note: BGCanvas does not create a foreground surface. Subclasses must
          do so.
    """
    def __init__(self, size):
        Canvas.__init__(self)

        self.background = Canvas()
        self.background.surface = pygame.Surface(size)

    def setbackgroundimage(self, image):
        self.background.showimage(image, (0,0))
        self.showimage(image, (0,0))

    @mainthread
    def erase(self, *rects):
        for rect in rects:
            self.surface.blit(self.background.surface, rect, rect)
        pygame.display.update(rects)

#TODO(isaac): have Game pass the window to canvas to override its surface
class Game(BGCanvas):
    def __init__(self, gamelogic):
        global MAIN_THREAD
        MAIN_THREAD = threading.currentThread()
        self.WINDOW_SIZE = self.WINDOW_XSIZE,self.WINDOW_YSIZE = 550,550
        self.FULLSCREEN = False
        pygame.display.init()
        pygame.font.init()

        pygame.key.set_repeat(250, 50)
        self.keylistener = None

        self.clicklistener = None

        self.inputrect = Rect(0, self.WINDOW_YSIZE-50, self.WINDOW_XSIZE, 50)

        self.playername = "Commander"

        self.debugmode = False

        self.settingsversion = 1 #to be updated with changes to the way settings are saved
        self.networkversion = 0 #to be updated with changes to the way the clients communicate
        self.mapversion = 0 #to be updated with changes to the way maps are read
        self.savegameversion = 0 #to be updated with changes to the way games are saved
        
        pygame.display.set_caption("MoonPy")
        self.surface = pygame.display.set_mode(self.WINDOW_SIZE)

        BGCanvas.__init__(self, self.WINDOW_SIZE)

        self.gamelogic = threading.Thread(target=self._go, args=(gamelogic,))
        self.gamelogic.setDaemon(True)
        self.gamelogic.start()

        while True:
            e = pygame.event.wait()
            if e.type == KEYDOWN:
                if self.keylistener:
                    self.keylistener(e)
            elif e.type == MOUSEBUTTONDOWN:
                if self.clicklistener:
                    self.clicklistener(e)
            elif e.type == CALL:
                try:
                    result = e.fn(*e.args, **e.kwargs)
                    e.respond((False, result))
                except:
                    _,exception,_ = sys.exc_info()
                    print exception
                    e.respond((True, exception))
            elif e.type == QUIT:
                break

    def _go(self, gamelogic):
        try:
            gamelogic(self)
        finally:
            pygame.event.post(pygame.event.Event(QUIT))

    @mainthread
    def loadimage(self, filename):
        return pygame.image.load(filename).convert()

    def loadimages(self, filenames):
        return [self.loadimage(name) for name in filenames]

    def input(self, rect=None):
        if rect is None:
            rect = self.inputrect

        inputbox = InputBox(self, rect)
        old = self.keylistener
        self.keylistener = inputbox.key
        inputbox.done.wait()
        self.keylistener = old
        return inputbox.close()

    def createmap(self, size, viewrect):
        return Map(size, self.surface, viewrect)

    def buttoninput(self, buttons):
        """Display buttons and wait for user to click one.

        Takes a list of (<pos>, <image>, <value>) tuples, where <image> is
        the appearance of the button, <pos> is the x,y coordinates of the
        button's upper left corner, and <value> is the value to be returned
        if the button is clicked. After the user clicks one, the buttons
        are erased and the value corresponding to the clicked button is
        returned."""
        sentinel = object()
        rectvalues = []
        for pos,image,value in buttons:
            rect = self.showimage(image, pos)
            if value is None:
                value = sentinel
            rectvalues.append((rect, value))

        old = self.clicklistener
        q = Queue()
        self.clicklistener = q.put

        gotvalue = None
        while gotvalue is None:
            click = q.get()
            for rect,value in rectvalues:
                if rect.collidepoint(*click.pos):
                    self.clicklistener = old
                    gotvalue = value

        self.erase(*[rect for rect,_ in rectvalues])

        if gotvalue is sentinel:
            gotvalue = None
        return gotvalue

    def textbutton(self, text):
        font = pygame.font.Font(None, 50)
        textimage = font.render(text, True, color.white)
        xsize,ysize = textimage.get_size()

        buttonimage = pygame.Surface((xsize+40, ysize+40))
        buttonimage.blit(textimage, (20,20))
        rect = buttonimage.get_rect()
        pygame.draw.rect(buttonimage, color.white, rect, 4)
        return buttonimage

#TODO(isaac): wrapped updates
class Map(BGCanvas):
    @mainthread
    def __init__(self, size, viewsurface, viewrect):
        self.surface = pygame.Surface(size)
        self.view = viewsurface.subsurface(viewrect)

        BGCanvas.__init__(self)

        self._scrollto(0,0)

    @mainthread
    def _showimage(self, image, pos):
        sizex,_ = image.get_size()
        posx,posy = pos
        surfacewidth,_ = self.surface.get_size()
        if sizex + posx > surfacewidth:
            self._showimage2(image, (posx-surfacewidth, posy))

        return self._showimage2(image, pos)

    @mainthread
    def _showimage2(self, image, pos):
        _,sizey = image.get_size()
        posx,posy = pos
        _,surfaceheight = self.surface.get_size()
        if sizey + posy > surfaceheight:
            self._showimage3(image, (posx, posy-surfaceheight))

        return self._showimage3(image, pos)

    @mainthread
    def _showimage3(self, image, pos):
        rect = self.surface.blit(image, pos)
        self._updateview(rect)
        return rect

    @mainthread
    def _updateview(self, rect):
        rectx,recty = rect.topleft
        viewx,viewy = self.viewxy
        pos = rectx - viewx, recty - viewy
        update = self.view.blit(self.surface, pos, rect)

        update.move_ip(*self.view.get_abs_offset())
        pygame.display.update(update)

    def scroll(self, dx, dy):
        x,y = self.viewxy
        self.scrollto(x+dx, y+dy)

    @mainthread
    def scrollto(self, x, y):
        self.viewxy = x,y
        rect = pygame.Rect(self.viewxy, self.view.get_size())
        self.view.blit(self.surface, (0,0), rect)
        self._updateview(rect)

def clip(source, rect):
    surface = pygame.Surface(rect.size)
    surface.blit(source, (0,0), rect)
    return surface

class AnimationBox:
    @mainthread
    def __init__(self, canvas, images, delay, pos):
        self.canvas = canvas
        self.delay = delay/1000
        self.pos = pos

        self.images = Peekable(iter(images))
        image = self.images.peek()

        self.rect = Rect(pos, image.get_size())
        self.background = clip(self.canvas.surface, self.rect)

        self.done = False
        self.finish = threading.Event()
        self.start()

    def start(self):
        self.thread = threading.Thread(target=self._go)
        self.thread.setDaemon(True)
        self.thread.start()

    def _go(self):
        try:
            for image in self.images:
                if self.done:
                    break
                self.canvas.showimage(image, self.pos)
                sleep(self.delay) #TODO(isaac): use event for early exit
        finally:
            self.finish.set()

    def wait(self):
        self.finish.wait()
        #TODO(isaac): return values from erase
        self.erase()

    @mainthread
    def erase(self):
        self.canvas.showimage(self.background, self.pos)

class TextBox:
    @mainthread
    def __init__(self, canvas, text, pos):
        self.canvas = canvas
        self.text = text
        self.pos = pos

        self.font = pygame.font.Font(None, 50)
        image = self.font.render(self.text, True, color.white)
        self.rect = Rect(pos, image.get_size())

        self.background = clip(self.canvas.surface, self.rect)

        self.canvas.showimage(image, self.pos)

    @mainthread
    def erase(self):
        self.canvas.showimage(self.background, self.pos)

class InputBox:
    @mainthread
    def __init__(self, canvas, rect, text=""):
        self.canvas = canvas
        self.rect = Rect(rect)

        self.background = clip(self.canvas.surface, self.rect)

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
        image = self.font.render(self.text, True, color.white)
        overage = max(0, image.get_width() - self.textwidth)

        draw = Rect(overage, 0, self.rect.width, self.rect.height)

        self.canvas.surface.blit(self.background, self.rect)
        drawn = self.canvas.surface.blit(image, self.rect, draw)
        self.canvas.surface.blit(self.cursor, drawn.topright)

        pygame.display.update(self.rect)

    @mainthread
    def close(self):
        self.canvas.showimage(self.background, self.rect)
        return self.text

class color:#todo: make this global in scope so it can be used by other modules
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
