from random import *
import pygame, os
from pygame.locals import *
import ctrl, data
from ConfigParser import ConfigParser, NoOptionError
import bisect
import events

try:
    from networking import MasterIgloo as Igloo
except ImportError:
    from buildings.igloo import Igloo

from unit import Snowballer, Worker


from buildings.landobstruction import LandObstruction
from OpenGL.GL import *
import zipfile

from cStringIO import StringIO
from textures import Texture

import rabbyt

class Map:
    def __init__(self):
        self.name = "Unnamed"
        self.tiles = {}
        self.size = (0,0)
        self.borders = set()
        self.unit_nodes = NodeSet(7)
        self._dynamic_objects = []
        self.loaded_plugins = set()

        self.elevation_multiplier = 4

    @classmethod
    def load(cls, name):
        map = cls()
        data.map = map
        z = zipfile.ZipFile(os.path.join("maps", name+".zip"), "r")
        settingsfile = z.read("settings.ini")
        map.config = config = ConfigParser()
        config.readfp(StringIO(settingsfile))


        # Regions, buildings, and resources.
        simage = z.read(config.get("map", "resources"))
        simage = pygame.image.load(StringIO(simage))
        rimage = z.read(config.get("map", "regions"))
        rimage = pygame.image.load(StringIO(rimage))


        # optional maps.
        if config.has_option("map", "terrain"):
            timage = z.read(config.get("map", "terrain"))
            timage = pygame.image.load(StringIO(timage))
        else:
            timage = None

        if config.has_option("map", "land"):
            land_image = z.read(config.get("map", "land"))
            land_image = pygame.image.load(StringIO(land_image))
        else:
            land_image = None



        map.size = (rimage.get_width(), rimage.get_height())

        # Regions and terrain
        map.regions = {}
        for x in range(map.size[0]):
            for y in range(map.size[1]):
                rn = rimage.get_at((x,y))[:3]
                if not map.regions.has_key(rn):
                    map.regions[rn] = Region(rn)
                region = map.regions[rn]
                ttype = "snow"
                if land_image:
                    if land_image.get_at((x,y)) == (0,255,255,255):
                        ttype = "ice"
                elevation = 0
                if timage:
                    c = timage.get_at((x,y))[0]
                    elevation = c/255.0 * 30 #steps
                t = Tile(ttype, x, y, region, elevation)
                map.tiles[(x,y)] = t

        # Unit settings.
        for op, val in config.items("snowballers"):
            if hasattr(Snowballer, op):
                setattr(Snowballer, op, int(val))
        for op, val in config.items("workers"):
            if hasattr(Worker, op):
                setattr(Worker, op, int(val))

        # AI settings.
        if config.has_section("ai"):
            import ai
            if config.has_option("ai", "gather"):
                ai.Ai.gather = config.get("ai", "gather")
            if config.has_option("ai", "guard"):
                pos = config.get("ai", "guard").split(",")
                ai.Ai.guard_pos = (int(pos[0]), int(pos[1]))
            if config.has_option("ai", "gather_force"):
                ai.Ai.gather_force = config.getint("ai", "gather_force")

        # Buildings
        for n,pos in config.items("igloos"):
            x,y = pos.split(",")
            map.add_igloo(int(x),int(y))

        # Resources
        for x in range(map.size[0]):
            for y in range(map.size[1]):
                t = map.tiles[(x,y)]
                if map.pos_is_open_check((x,y)):
                    c = simage.get_at((x,y))
                    r = None
                    if c == (0,255,0,255) and t.type == "snow":
                        image = data.trees[randint(0,3)]
                        Resource(t, "tree", 10, image)
                    if c == (0,0,255,255) and t.type == "ice":
                        image = data.icepinnacle[randint(0,2)]
                        Resource(t, "icepinnacle", 10, image)
                    elif c == (0,255,255,255):
                        Resource(t, "fish", 7, data.fish,
                                empty_image=Texture.get("data/fishempty.png"))
                    elif c == (255,0,255,255):
                        Resource(t, "crystal", 7, Texture.get("data/crystal.png"),
                                empty_image=Texture.get("data/crystalempty.png"))


        # For networking the units and buildings need to know their IDs.
        for id, u in enumerate(data.units):
            u.unit_id = id
        for id, b in enumerate(data.buildings):
            b.building_id = id

        # Plugins
        if data.THIS_IS_SERVER:
            plugins = config.get("map", "required_plugins").split(",")
            for p in plugins:
                p = p.strip()
                p,v = p.split("-v")
                try:
                    pl = __import__("plugins."+p, None, None, "plugins")
                except ImportError:
                    raise ImportError("Could not find plugin %s"%p)
                if float(v) > pl.__version__:
                    raise ImportError("%s plugin is too old. Required version is %s"%(p,v))
                map.loaded_plugins.add(pl.init(config))

        return map

    def add_igloo(self,x,y):
        if not data.THIS_IS_SERVER:
            from networking import SlaveIgloo as I
        else:
            I = Igloo

        new_building = I(self.tiles[(x,y)], player=None, construction=100)

        root_tile = self.tiles[(x,y)]
        if root_tile.region.igloo:
            raise ValueError("You can only have 1 igloo per region!")
        tiles = []
        for xx in range(new_building.size):
            for yy in range(new_building.size):
                c = self.tiles[x+xx,y+yy]
                if c.building == None and c.type == "snow" and not c.resource:
                    tiles.append(c)
                else:
                    raise ValueError("building already there!")

        data.buildings.append(new_building)
        root_tile.building_root = True
        for c in tiles:
            c.building = new_building

        # Add units.
        for i in xrange(self.config.getint("igloo_settings", "workers")):
            u = Worker((new_building.x+1,new_building.y+1),
                    new_building)
            data.units.append(u)

        for i in xrange(self.config.getint("igloo_settings", "snowballers")):
            u = Snowballer((new_building.x+1,new_building.y+1),
                    new_building)
            data.units.append(u)


    def pos_is_open_check(self, pos):
        if not self.tiles.has_key(pos): return False
        t = self.tiles[pos]
        if not t.building and not t.resource:
            return True
        return False

    def place_landobstruction(self, pos, name):
        new_building = LandObstruction(pos, name)

        root_tile = self.tiles[pos]

        tiles = set()
        for x in range(new_building.size):
            for y in range(new_building.size):
                c = self.tiles[pos[0]+x,pos[1]+y]
                if c.building == None and c.type == "snow" and not c.resource:
                    tiles.add(c)
                else:
                    raise ValueError("building already there!")

        data.buildings.append(new_building)
        root_tile.building_root = True
        for c in tiles:
            c.building = new_building


    def add_dynamic_object(self, object):
        # TODO alert clients
        object.dmo_id = len(self._dynamic_objects)
        self._dynamic_objects.append(object)

    def remove_dynamic_object(self, object):
        # We can't just remove it because it would mess up looking up other
        # objects by their id.
        object.hidden = True
        #self._dynamic_objects.remove(object)


    def draw(self):
        vw, vh = data.view.scale_w, data.view.scale_h
        #for r in data.resources:
            #x = r.x*32
            #y = r.y*32 - r.image.height + 32

            #if x+64 > data.view.x and x < data.view.x+vw\
                    #and y+64 > data.view.y and y < data.view.y+vh+64:
                #bisect.insort(data.draw_buffer, data.Rendered(r.image, x, y,
                    #z=1))

        for o in self._dynamic_objects:
            if o.hidden: continue
            x,y = o.position
            x = x*32
            y = y*32 - self.tiles[o.position].elevation *\
                    self.elevation_multiplier
            t = Texture.get(o.image_name)
            w,h = t.width, t.height
            if x+w > data.view.x and x < data.view.x+vw\
                    and y+h > data.view.y and y < data.view.y+vh+h:
                bisect.insort(data.draw_buffer, data.Rendered(t, x, y, z=1))


class NodeSet:
    def __init__(self, num_tiles):
        self.node_size = num_tiles
        self.nodes = {}

    def find_current_node(self, tilex,tiley):
        i = (tilex//self.node_size, tiley//self.node_size)
        if not self.nodes.has_key(i):
            node = set()
            self.nodes[i] = node
            return node
        else:
            return self.nodes[i]

    def get_nodes_around_tile(self, pos):
        x = int(pos[0])//self.node_size
        y = int(pos[1])//self.node_size
        idxs = ((x, y), (x-1, y), (x+1, y),
                (x, y+1), (x-1, y+1), (x+1, y+1),
                (x, y-1), (x-1, y-1), (x+1, y-1))
        for idx in idxs:
            if self.nodes.has_key(idx):
                yield self.nodes[idx]

    def get_objs_around_tile(self, pos):
        for node in self.get_nodes_around_tile(pos):
            for obj in node:
                yield obj


class Tile:
    """ A map tile. """
    def __init__(self, type, x, y, region, elevation=0):
        self.x = x
        self.y = y
        self.type = type
        self.building = None
        self.building_root = False
        self.resource = None
        self.region = region
        self.region.tiles.add(self)

        self.elevation = elevation

class Region(object):
    def __init__(self, name):
        self.name = name
        self._player = None
        self.tiles = set()
        self.resources = set()
        self.adjacent_regions = set()
        self._igloo = None


    def _get_igloo(self):
        if not self._igloo:
            for b in data.buildings:
                if b.name == "igloo" and b.region == self:
                    self._igloo = b
                    break
        return self._igloo
    igloo = property(_get_igloo)

    def _set_player(self, value):
        old_player = self._player
        self._player = value

        events.fire(events.REGION_TAKEOVER, self, old_player)

        for t in self.tiles:
            if t.resource:
                if old_player: old_player.open_resources.remove(t.resource)
                self._player.open_resources.add(t.resource)
            if t.building_root and t.building and t.building.name == "igloo":
                t.building.player = self._player

        for player in data.players.values():
            if player and player.type == "ai":
                player.ai.setup()

    def _get_player(self):
        return self._player
    player = property(_get_player, _set_player)

from rabbyt import Sprite

class Resource(rabbyt.Sprite):
    def __init__(self, tile, type, quantity, image, empty_image=None):
        rabbyt.Sprite.__init__(self, image.texture_id, image.get_shape_pos(),
                image.get_shape_tex(invert_y=True))
        self.xy = (tile.x*32, tile.y*32 - image.height + 32 - tile.elevation*\
                data.map.elevation_multiplier)

        # This is so that Resource can act as a Rendered instance.
        self.height = image.height
        self.z = 1

        self.tile = tile
        data.resources.add(self)
        data.sprite_sets.get(self.x, self.y).add(self)
        tile.resource = self
        tile.region.resources.add(self)
        self.type = type
        self._image = image
        self.empty_image = empty_image
        self.quantity = quantity

    #def __hash__(self):
        #return id(self)

    def _set_quantity(self, q):
        if q <= 0 and self.empty_image:
            self.texture_id = self.empty_image.texture_id
        else:
            self.texture_id = self._image.texture_id
        try:
            if data.THIS_IS_SERVER:
                from networking import send, MResourceQuantity
                send(MResourceQuantity(self.tile.x, self.tile.y, q))
        except ImportError:
            pass
        self._quantity = q
    def _get_quantity(self):
        return self._quantity
    quantity = property(_get_quantity, _set_quantity)

    @property
    def image(self):
        if self.quantity <= 0 and self.empty_image: return self.empty_image
        return self._image

    def replenish(self):
        self.quantity = randint(5,10)

    def gatherable(self):
        if self.type == "fish" or self.type == "crystal": return True
        return False

    gatherable = property(gatherable)

    def __cmp__(self, other):
        # This is taken from Rendered.__cmp__
        return cmp((self.z, self.y+self.height, -self.x), (other.z, other.y+other.height, -other.x))
