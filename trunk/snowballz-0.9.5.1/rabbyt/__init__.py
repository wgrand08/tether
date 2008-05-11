"""
Rabbyt is a fast 2d sprite library for Python.
"""

__credits__ = (
"""
Copyright (C) 2007  Matthew Marshall

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
""")

__author__ = "Matthew Marshall <matthew@matthewmarshall.org>"
__version__ = "0.7.5"

import heapq
import os.path

from rabbyt._rabbyt import *
from rabbyt.sprites import *
from rabbyt.anims import *
import rabbyt.physics, rabbyt.collisions


class Scheduler(object):
    """
    ``Scheduler()``

    Scheduler provides... (wait for it...)  scheduling!

    You may create your own scheduler instances, or use the default
    ``rabbyt.scheduler``
    """
    def __init__(self):
        self.heap = []

    def add(self, time, callback):
        """
        ``add(time, callback)``

        Schedules a ``callback`` to be called at a given ``time``.
        """
        heapq.heappush(self.heap, (time, callback))

    def pump(self, time=None):
        """
        ``pump([time])``

        Calls all callbacks that have been scheduled for before ``time``.

        If ``time`` is not given, the value returned by ``rabbyt.get_time()``
        will be used.
        """
        if time is None:
            time = get_time()
        try:
            while self.heap[0][0] <= time:
                heapq.heappop(self.heap)[1]()
        except IndexError, e:
            # If the IndexError was raised due to something other than an
            # empty heap we don't want to silence it.
            if len(self.heap) != 0:
                raise e

scheduler = Scheduler()


def init_display(size=(640, 480), flags = 0):
    """
    init_display(size=(640, 480), flags = 0)

    This is a small shortcut to create a pygame window, set the viewport, and
    set the opengl attributes need for rabbyt.

    ``flags`` is passed to ``pygame.display.set_mode()`` (OR'ed with
    ``pygame.OPENGL`` and ``pygame.DOUBLEBUF``.)

    The pygame surface returned by ``pygame.display.set_mode()`` is returned.

    This function depends on pygame.
    """
    import pygame
    pygame.init()
    surface = pygame.display.set_mode(size, pygame.OPENGL |
            pygame.DOUBLEBUF | flags)
    set_viewport(size)
    set_default_attribs()
    return surface

_texture_cache = {}

data_directory = ""

def pygame_load_texture(filename, filter=True, mipmap=True):
    """
    ``pygame_load_texture(filename, filter=True, mipmap=True) -> texture_id,
    size``

    Reads an image from a file and loads it as a texture.  Pygame is used for
    reading the image.

    If ``filename`` is a relative path, the working directory is searched
    first, then ``rabbyt.data_directory`` is searched for the file.
    """
    if filename not in _texture_cache:
        import pygame
        if os.path.exists(filename):
            img = pygame.image.load(filename)
        else:
            img = pygame.image.load(os.path.join(data_directory, filename))
        data, size = pygame.image.tostring(img, 'RGBA', True), img.get_size()
        _texture_cache[filename] = load_texture(data, size, "RGBA",
                filter, mipmap), size
    return _texture_cache[filename]
set_load_texture_file_hook(pygame_load_texture)

__all__ = __docs_all__ = ('anims collisions fonts sprites physics vertexarrays '
'Scheduler '
'init_display set_viewport set_default_attribs set_gl_color clear '
'get_gl_vendor '
'render_unsorted '
'load_texture update_texture unload_texture pygame_load_texture '
'set_load_texture_file_hook ').split()