__version__ = 1.2

from events import *
from plugin import DynamicMapObject, Emblem





def init(config):
    p = PowerupPlugin()
    for _,params in config.items("powerups"):
        params = params.split(",")
        powerup = params.pop(0)
        if powerup not in powerups:
            raise ValueError("Invalid powerup '%s'"%powerup)
        cls = powerups[powerup]
        params.insert(0, p)
        cls(*params)
    return p


class PowerupPlugin(object):
    def __init__(self):
        self.map_powerups = set()
        connect(PENGUIN_MOVE, self.pickup_check)
        connect(PENGUIN_FROZEN, self.frozen)

        self.held_powerups = {}  # Keyed by penguin
        self.unheld_powerups = {}  # Keyed by posision

        # Keyed by signal (event) type, then keyed by penguin.
        self.signals = {}

    def pickup_check(self, penguin, x, y):
        if (x,y) in self.unheld_powerups and penguin not in self.held_powerups\
                and penguin.type == "snowballer":
            powerup = self.unheld_powerups[(x,y)]
            powerup.give_to_penguin(penguin)

    def frozen(self, penguin, snowballpenguin):
        if penguin in self.held_powerups:
            powerup = self.held_powerups[penguin]
            if snowballpenguin and snowballpenguin.warmth > 0 and\
                    snowballpenguin not in self.held_powerups:
                powerup.give_to_penguin(snowballpenguin)
            else:
                powerup.take_from_penguin()
        elif penguin._emblems:
            print "ARG!!!!!"

    def connect_signal(self, event, penguin, callback):
        if event in self.signals:
            penguin_callbacks = self.signals[event]
        else:
            penguin_callbacks = {}
            self.signals[event] = penguin_callbacks
            connect(event, lambda *args: self.event_called(penguin_callbacks,
                    *args))
        if not penguin in penguin_callbacks:
            penguin_callbacks[penguin] = set()
        penguin_callbacks[penguin].add(callback)

    def remove_signal(self, event, penguin, callback):
        self.signals[event][penguin].remove(callback)

    def event_called(self, callbacks, penguin, *pargs):
        if penguin in callbacks:
            for callback in callbacks[penguin]:
                callback(*pargs)


class Powerup(object):
    def __init__(self, plugin, x, y):
        self.plugin = plugin
        self.position = (int(x), int(y))
        self.map_object = DynamicMapObject(self.image, self.position,
                hidden=False, minimapimage="plugins/powerup/minipowerup.png",
                animate=True)
        self.penguin = None
        self.plugin.unheld_powerups[self.position] = self

    def give_to_penguin(self, penguin):
        if self.penguin:
            self.take_from_penguin()
        self.penguin = penguin
        self.map_object.hidden = True
        self.penguin.add_emblem(self.emblem)
        del self.plugin.unheld_powerups[self.position]
        self.plugin.held_powerups[self.penguin] = self

    def take_from_penguin(self):
        self.penguin.remove_emblem(self.emblem)
        del self.plugin.held_powerups[self.penguin]
        self.plugin.unheld_powerups[self.position] = self
        self.map_object.hidden = False
        self.penguin = None

    def map_draw(self):
        inview = self.in_view()
        if not self.penguin and inview:
            x,y = inview
            self.render(self.texture, x, y, z=5)


class DoubleSnowball(Powerup):
    image = "plugins/powerup/powerup_1.png"
    emblem = Emblem(image, animate=True, offset=(0,-26))

    def give_to_penguin(self, penguin):
        Powerup.give_to_penguin(self, penguin)
        self.plugin.connect_signal(PENGUIN_RELOAD, self.penguin, self.reload)

    def take_from_penguin(self):
        self.plugin.remove_signal(PENGUIN_RELOAD, self.penguin, self.reload)
        Powerup.take_from_penguin(self)

    def reload(self):
        self.penguin.snowballs = 2



class Defense(Powerup):
    image = "plugins/powerup/powerup_2.png"
    emblem = Emblem(image, animate=True, offset=(0,-26))

    def give_to_penguin(self, penguin):
        Powerup.give_to_penguin(self, penguin)
        penguin.max_warmth += 4
        penguin.warmth += 4
        self.plugin.connect_signal(PENGUIN_DIRECT_HIT, self.penguin, self.hit)

    def take_from_penguin(self):
        self.plugin.remove_signal(PENGUIN_DIRECT_HIT, self.penguin, self.hit)
        self.penguin.max_warmth -= 4
        Powerup.take_from_penguin(self)

    def hit(self, d):
        self.penguin.warmth += d-1


powerups = {
    "DoubleSnowball":DoubleSnowball,
    "Defense":Defense,
}
