import data
from textures import Texture

try:
    import networking
except ImportError:
    networking = None


class Emblem(object):
    def __init__(self, image_name, animate=False, offset=(0,0)):
        self.image_name = image_name
        self.animate = animate
        self.speed = 0.02
        self.offset = offset
        if self.animate:
            self.alpha = 0.5
        else:
            self.alpha = 1

    def doanimate(self):
        if self.animate:
            self.alpha += self.speed
            if self.alpha > 0.8:
                self.alpha = 0.8
                self.speed = -self.speed
            elif self.alpha < 0.4:
                self.alpha = 0.4
                self.speed = -self.speed

    def rendered(self, x, y):
        return data.Rendered(Texture.get(self.image_name),
                x+self.offset[0], y+self.offset[1], z=5, alpha=self.alpha)

    def draw(self, x, y):
        """ Appends a rendered to the data draw buffer. Does not render immediately. """
        data.draw_buffer.append(self.rendered(x,y))


class BaseDynamicMapObject(object):
    def __init__(self, image_name, position, hidden=True, obstruction=False,
                minimapimage=None, animate=False):
        self.minimapimage = minimapimage
        self.image_name = image_name
        self.position = position
        self.hidden = hidden
        self.obstruction = obstruction
        data.map.add_dynamic_object(self)

        self.animate = animate
        self.speed = 0.02
        if self.animate:
            self.alpha = 0.5
        else:
            self.alpha = 1

    def doanimate(self):
        if self.animate:
            self.alpha += self.speed
            if self.alpha > 0.8:
                self.alpha = 0.8
                self.speed = -self.speed
            elif self.alpha < 0.4:
                self.alpha = 0.4
                self.speed = -self.speed

    def minimapicon(self):
        return data.Rendered(Texture.get(self.minimapimage),
                self.position[0], -self.position[1], alpha=self.alpha)
    minimapicon = property(minimapicon)

    def destroy(self):
        data.map.remove_dynamic_object(self)


class DynamicMapObject(BaseDynamicMapObject):
    def alert_creation(self, to="*", exclude=()):
        if not networking:
            return
        m = networking.MCreateDynamicMapObject(self.dmo_id, self.image_name,
                self.position, self.obstruction, self.hidden, self.minimapimage)
        networking.send(m, to=to, exclude=exclude)

    #def destroy(self):
        #BaseDynamicMapObject.destroy(self)
        #self.call_remote("destroy")

    #def _set_position(self, p):
        #if not hasattr(self, '_position'):
            #self._position = p
        #elif p != self.position:
            #self._position = p
            #self.call_remote("position", p)
    #position = property((lambda self:self._position), _set_position)

    def _set_hidden(self, h):
        if not hasattr(self, '_hidden'):
            self._hidden = h
        elif h != self.hidden:
            self._hidden = h
            if networking:
                networking.send(networking.MDMOHidden(self.dmo_id, h))
    hidden = property((lambda self:self._hidden), _set_hidden)

    #def getStateToCacheAndObserveFor(self, perspective, observer):
        #self.observers.append(observer)
        #d = {}
        #for key in ("image_name", "position", "hidden", "obstruction",
                #"minimapimage", "animate"):
            #d[key] = getattr(self, key)
        #return d

