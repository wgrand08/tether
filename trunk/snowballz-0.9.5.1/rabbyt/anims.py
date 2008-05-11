"""
This module provides *Animators* (or *anims* for short) for Rabbyt.

*Anims* are little objects that can implement a movement function, primarily
meant to animate sprites.  The movement functions are all implemented in C, so
your sprites can be animated without any python call overhead.

For example, to linearly interpolate a sprite from x=0 to x=100 over the next
second, you can do this:

    .. sourcecode:: python

        sprite.x = rabbyt.lerp(0, 100, dt=1000)

Looks like magic?

It is!  Sorta...

The ``Sprite`` class's ``x`` attribute is really a property.  If you
assign an anim to it, that anim will be called for it's value every time the
sprite needs it's x position.  Nearly all of ``Sprite``'s properties work
like this.

Anims support various arithmatic opperations.  If you add two together,
or add one with a constant number, a new anim will be returned.  Here is a
rather contrived example of doing that:

    .. sourcecode:: python

        sprite.x = rabbyt.lerp(0, 100, dt=1000) + 20

(In this case, you would be better off interpolating from 20 to 120, but
whatever.)

Here is a more useful example:

    .. sourcecode:: python

        sprite2.x = sprite1.attrgetter('x') + 20

That will cause sprite2's x position to always be 20 more than sprite1's x
position.  (``Sprite.attrgetter()`` returns an anim that gets an attribute.)
This all happens in compiled C code, without any python call overhead.  (That
means you can have thousands of sprites doing this and it will still be fast.)

But sometimes you don't really need that much speed.  You can use any python
function as an anim as well.  This example does the same as the last one:

    .. sourcecode:: python

        sprite2.x = lambda: sprite1.x + 20

(``Sprite.x`` will automatically wrap the function in an ``AnimPyFunc``
instance behind the scenes.)

"""

from __future__ import division


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

from rabbyt._anims import *


extend_types = dict(constant=1, extrapolate=2, repeat=3, reverse=4)

def _handle_time_args(startt, endt, dt):
    if startt is None:
        startt = get_time()
    if endt is None:
        if dt is None:
            raise ValueError("Either dt or endt must be given.")
        endt = startt + dt

    assert startt < endt

    return int(startt), int(endt)


def _interpolate(class_, start, end, startt=None, endt=None, dt=None,
        extend="constant"):
    extend = extend_types[extend]

    startt, endt = _handle_time_args(startt, endt, dt)

    try:
        iter(start), iter(end)
    except TypeError:
        return class_(start, end, startt, endt, extend)
    else:
        return [class_(s, e, startt, endt, extend)
                for s,e in zip(start, end)]


def lerp(start, end, startt=None, endt=None, dt=None, extend="constant"):
    """
    ``lerp(start, end, [startt,] [endt,] [dt,] [extend])``

    Linearly interpolates between ``start`` and ``end`` as time moves from
    ``startt`` to ``endt``.

    ``startt`` is the time to start.  It defaults to ``rabbyt.get_time()``.

    To specify the ending time, use either ``endt``, which is the absolute
    time, or ``dt``, which is relative from ``startt``.

    For example, all of the following are equivalent:

        .. sourcecode:: python

            lerp(0, 1, rabbyt.get_time(), rabbyt.get_time()+1000)
            lerp(0, 1, rabbyt.get_time(), dt=1000)
            lerp(0, 1, dt=1000)

    ``extend`` is a string defining what to do before ``startt`` and after
    ``endt``. Possible values are:

        ``"constant"``
            The value will be locked between ``start`` and ``end``.  *This is
            the default.*

        ``"extrapolate"``
            After the value hits ``end`` it just keeps going!

        ``"repeat"``
            After the value hits ``end`` it will start over again at
            ``start``.

        ``"reverse"``
            After the value hits ``end`` it will reverse, moving back to
            ``start``.

    Check out the ``extend_modes.py`` example to see all four side by side.

    ``start`` and ``end`` can either be numbers, or tuples of numbers.  If
    they are tuples, a tuple of anims will be returned.  For example, this
    line:

        .. sourcecode:: python

            sprite.rgba = lerp((0,1,0,.5), (1,0,1,1), dt=1000)

    is equivalent to this:

        .. sourcecode:: python

            sprite.red   = lerp(0, 1, dt=1000)
            sprite.green = lerp(1, 0, dt=1000)
            sprite.blue  = lerp(0, 1, dt=1000)
            sprite.alpha = lerp(.5,1, dt=1000)

    """
    return _interpolate(AnimLerp, start, end, startt, endt, dt, extend)

def exponential(start, end, startt=None, endt=None, dt=None,
        extend="constant"):
    """
    ``exponential(start, end, [startt,] [endt,] [dt,] [extend])``

    Exponentially interpolates between ``start`` and ``end`` as time moves
    from ``startt`` to ``endt``, using a cosine function.

    All arguments work the same as in ``lerp()``.

    The function looks like this::

        (e**t-1) / (e-1)

    If you want to use another base besides ``e``, drop me an email
    explaining why and I'll implement it.  (YAGNI)
    """
    return _interpolate(AnimExponential, start, end, startt, endt, dt, extend)


def cosine(start, end, startt=None, endt=None, dt=None, extend="constant"):
    """
    ``cosine(start, end, [startt,] [endt,] [dt,] [extend])``

    Cosinely [1]_ interpolates between ``start`` and ``end`` as time moves from
    ``startt`` to ``endt``.

    All arguments work the same as in ``lerp()``.

    The function looks like this::

        1-cos(t * pi/2)

    And if math makes your head hurt, that means that your sprite will start
    out slow and speed up as it nears ``end``.

    .. [1] Ok, so 'cosinely' isn't a word :)
    """
    return _interpolate(AnimCosine, start, end, startt, endt, dt, extend)


def sine(start, end, startt=None, endt=None, dt=None, extend="constant"):
    """
    ``sine(start, end, [startt,] [endt,] [dt,] [extend])``

    Sinely [1]_ interpolates between ``start`` and ``end`` as time moves from
    ``startt`` to ``endt``.

    All arguments work the same as in ``lerp()``.

    The function looks like this::

        sin(t * pi/2)

    And if math still makes your head hurt, you should give up game
    development.

    Ok, ok, I give!  Your sprite will start out fast and slow down by the
    time it reaches ``end``.  (Just the opposite of cosinely interpolating.)

    .. [1]  Oh, you say 'sinely' isn't a word either?  That must be a bug.
            Give me your dictionary and a pen and I'll fix it.
    """
    return _interpolate(AnimSine, start, end, startt, endt, dt, extend)


def wrap(bounds, parent, static=True):
    """
    ``wrap(bounds, parent, static=True) -> AnimWrap or tuple of AnimWraps``

    Wraps a parent ``Anim`` to fit within ``bounds``.  ``bounds`` should be an
    object that supports item access for at least ``bounds[0]`` and
    ``bounds[1]``.  (A list or tuple with a length of 2 would work great.)

    If ``static`` is ``True``, ``bounds`` is only read once and stored in C
    variables for fast access. This is much faster, but doesn't work if
    ``bounds`` is an object you wish to mutate.

    If ``parent`` is a iterable, a tuple of anims will be returned instead
    of a single one.  (This is similar to ``lerp()``.)
    """
    try:
        iter(parent)
    except TypeError:
        return AnimWrap(bounds, parent, static)
    else:
        return tuple([AnimWrap(bounds, p, static) for p in parent])

def bezier3(p0, p1, p2, p3, startt=None, endt=None, dt=None, extend="constant"):
    """
    ``bezier3(p0, p1, p2, p3, [startt,] [endt,] [dt,] [extend])``

    Interpolates along a cubic bezier curve as defined by ``p0``, ``p1``,
    ``p2``, and ``p3``.

    ``startt``, ``endt``, ``dt``, and ``extend`` work as in ``lerp()``.

    ``p0``, ``p1``, ``p2``, and ``p3`` can be tuples, but they must all be the
    same length.
    """
    extend = extend_types[extend]
    startt, endt = _handle_time_args(startt, endt, dt)

    try:
        [iter(p) for p in [p0,p1,p2,p3]]
    except TypeError:
        return AnimStaticCubicBezier(p0, p1, p2, p3, startt, endt, extend)
    else:
        return [AnimStaticCubicBezier(p0, p1, p2, p3, startt, endt, extend)
                for p0, p1, p2, p3 in zip(p0, p1, p2, p3)]


__docs_all__ = ('set_time get_time add_time '
'lerp exponential cosine sine bezier3 wrap '
'Anim AnimConst AnimPyFunc AnimProxy '
'to_Anim').split()