"""
In this example, I'm going to show you how easy it is to integrate the gui into
your already made game. Also demonstrates linking custom functions (very cool,
be sure to see)!
"""

import sys
sys.path.insert(0, "..")

import pygame
import gooeypy as gui
from gooeypy.const import *

clock = pygame.time.Clock()

# Here is our screen that we are already using in our game.
screen = pygame.display.set_mode((640, 480))

# Here is one thing we do different. We pass it our own surface that we want it
# to use. This way, it won't set the display.
gui.init(myscreen=screen)

app = gui.App(width=640, height=100)


# Lets create a very simple game where you move around an image.
image = gui.get_image("image.png")
x = 200
y = 250


tb = gui.TextBlock(value="This example is for demonstrating how you can easily use GooeyPy in your already made game.", align="center", y=20, width=350)


def get_data():
    # We are going to set this function to be the value of the TextBlock widget,
    # (i.e. link it). Because GooeyPy doesn't know when x or y changes, it will
    # call this function every tick. It will still only update it's widgets when
    # it has to though. :)
    return "Current pie position: %s, %s" % (x,y)
# Remeber that when you pass a function as a value to pass a refrence of the
# function and not call it (as that would assign the vaues, not the actual
# function). This works not only with the value field but with all the
# styling options as well, such as x, y, width, height and the list goes on...
# see docs for full list of style options.
l = gui.Label(get_data, align="center", y=70, font_size=25, color=(255,255,255))

app.add(tb, l)

while True:
    clock.tick(40)

    events = pygame.event.get()

    for event in events:
        if event.type == QUIT:
            sys.exit()

        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit()

    k = pygame.key.get_pressed()
    if k[K_RIGHT]:
        x += 5
    if k[K_LEFT]:
        x -= 5
    if k[K_DOWN]:
        y += 5
    if k[K_UP]:
        y -= 5
    x = max(0, min(x, 460))
    y = max(100, min(y, 360))

    app.run(events)

    # If you want the gui to be drawn to the screen every time, you
    # can set "app.dirty = True" before calling app.draw()
    app.draw()

    # With updating the display you have a few options. If you want to flip the
    # entire screen, you can simply do:
    # pygame.display.flip()
    # Or if you are wanting to just update the parts the screen that need to be
    # updated, you can do something like this:

    # In your game, add the rects of the screen that need updating to this list.
    myupdaterects = []

    # Let's use our image that we move around the screen for example.
    dirty_rect = screen.blit(image, (x,y))
    myupdaterects.append(dirty_rect)

    # Now we update the screen!
    pygame.display.update(myupdaterects)

    # Don't forget to clear the dirty rect list!
    myupdaterects = []

    # Then we update the rects for the gui.
    gui.update_display()