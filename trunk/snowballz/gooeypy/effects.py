"""
<title>Effects appliable to widgets</title>
<h1>Effects</h1>
"""
import util


try:
    set # Only available in Python 2.4+
except NameError:
    from sets import Set as set # Python 2.3 fallback


class Pulsate:
    """
    This effect will cause the widget it is applied to to fade in and out at
    the designated speed (in the below example, 5).

    ::

        effect:pulsate 5;
    """
    def __init__(self, speed):
        self.speed = speed
        self.t = False
        self.alpha = 255
        self.used_surfs = set()

    def run(self, surf):
        #print self.alpha
        self.used_surfs.add(surf)
        surf.set_alpha(self.alpha)
        if self.alpha <= 150: self.t = True

        if not self.t:
            surf.set_alpha(self.alpha-self.speed)
            self.alpha -= self.speed
        elif self.alpha < 255:
            surf.set_alpha(self.alpha+self.speed)
            self.alpha += self.speed
        else:
            # All done. Clean up and set all used surfs to full opacy.
            for s  in self.used_surfs:
                # FIXME: needs to set to original alpha.
                s.set_alpha(255)
            return False
        return surf