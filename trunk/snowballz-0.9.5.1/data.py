from __future__ import division
import itertools

import textures
import pygame
from OpenGL.GL import *
import font
import settings
from random import random, randint

import rabbyt
import os



def play_menu_music():
    pygame.mixer.music.load(os.path.join("data", "music", "main_menu.ogg"))
    pygame.mixer.music.play()

def play_game_music():
    music = "snowballz2.mp3"
    if map.config.has_option("map", "music"):
        music = map.config.get("map", "music")
    try:
        pygame.mixer.music.load(os.path.join("data", "music", music))
    except:
        pygame.mixer.music.load(os.path.join("data", "music", "snowballz2.mp3"))

    pygame.mixer.music.play(-1)


THIS_IS_SERVER = True


class PixNodeSet:
    def __init__(self, size, make_node=lambda:set()):
        self.node_size = size
        self.nodes = {}
        self.make_node = make_node

    def get(self, x, y):
        i = (int(x)//self.node_size, int(y)//self.node_size)
        return self._get_node(i)

    def _get_node(self, node_key):
        if not self.nodes.has_key(node_key):
            node = self.make_node()
            self.nodes[node_key] = node
        return self.nodes[node_key]

    def range(self, x1, y1, x2, y2):
        x1 = int(x1)//self.node_size
        y1 = int(y1)//self.node_size
        x2 = int(x2)//self.node_size
        y2 = int(y2)//self.node_size

        for y in xrange(y1, y2+1):
            for x in xrange(x1, x2+1):
                yield self._get_node((x,y))

# These are all the sprites that need to be sorted with each other.
sprite_sets = PixNodeSet(size=512, make_node=lambda:set())

#behavior_sets = PixNodeSet(size=512, make_node=rabbyt.BehaviorSet)
#resource_behavior_set = rabbyt.BehaviorSet()


class Penguins:
    def __init__(self, bigtexture):
        self.bigtexture = textures.Texture(bigtexture)

        self.images = {}

        directions = [(0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (1,1)]
        for dc in xrange(len(directions)):
            d = directions[dc]
            for i in xrange(11):
                if i == 10:
                    key = ("idle", d)
                else:
                    key = (i, d)
                t = self.bigtexture.sub(32*i, (256-32)-32*dc, 32, 32)
                #print 32*i,(512-32)-32*dc
                self.images[key] = t


class View:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.h = 0
        self.w = 0
        self.zoom = 1.0

    @property
    def scale_h(self):
        return int(self.h // self.zoom)
    @property
    def scale_w(self):
        return int(self.w // self.zoom)

view = View(0,0)

class Rendered:
    def __init__(self, image, x, y, z=0, colorize=(1,1,1), scale=None, alpha=1):
        self.image = image
        self.height = image.height
        self.x = x
        self.y = y
        self.z = z
        self.colorize = list(colorize)+[alpha]
        self.scale = scale

    def render(self):
        glColor4f(*self.colorize)
        if self.scale:
            glPushMatrix()
            glTranslatef(self.x, self.y, 0)
            glScalef(self.scale, self.scale, 1)
            self.image.render()
            glPopMatrix()
        else:
            self.image.render(self.x, self.y)
        glColor4f(1,1,1,1)

    def __cmp__(self, other):
        return cmp((self.z, self.y+self.height, -self.x), (other.z, other.y+other.height, -other.x))

particles = set()



class ImprentSet(object):
    def __init__(self, image, length):
        self.image = textures.Texture(image)
        self.render_sets = PixNodeSet(size=512, make_node=
                lambda: set())

        # convert seconds to milliseconds.
        self.length = length*1000

    def add(self,x,y,color=(1,1,1)):
        fixed_color=[]
        for c in color:
            if c > 1:
                c = c/255
            fixed_color.append(c)
        i = Imprent(x,y, tuple(fixed_color), self.image, self.length)
        rs = self.render_sets.get(x, y)
        rs.add(i)
        rabbyt.scheduler.add(get_ticks()+self.length, lambda:rs.remove(i))

    def draw(self, dt):
        sets = self.render_sets.range(view.x, view.y, view.x+view.w,
                view.y+view.h)
        for s in sets:
            rabbyt.render_unsorted(s)

class Imprent(rabbyt.Sprite):
    def __init__(self, x, y, color, image, length):
        rabbyt.Sprite.__init__(self)
        self.shape = image.get_shape_pos()
        self.tex_shape = image.get_shape_tex(True)
        self.xy = (x,y)
        self.texture_id = image.texture_id

        self.rgba = color + (rabbyt.lerp(1.0, 0.0, dt=length),)


class Animator:
    def __init__(self, speed, max_alpha, min_alpha, active=True):
        self.active = active
        self.alpha = 1
        self.speed = 0.05
        self.max_alpha = max_alpha
        self.min_alpha = min_alpha

    def animate(self):
        if self.active:
            self.alpha += self.speed
            if self.alpha > self.max_alpha:
                self.alpha = self.max_alpha
                self.speed = -self.speed
            elif self.alpha < self.min_alpha:
                self.alpha = self.min_alpha
                self.speed = -self.speed

class Messages:

    class Message(Animator):
        def __init__(self, time, msg, from_player, pulsate=False):
            Animator.__init__(self, 0.05, 1, 0.6, pulsate)
            self.time = time
            self.msg = msg
            self.from_player = from_player
            self.force_close = False
            self.num_lines = len(msg.split("\n"))

    def __init__(self):
        self.messages = []

    def clear(self):
        for m in self.messages:
            m.force_close = True

    def send(self, msg, from_player, to_player):
        self.display(msg, from_player, to_player)
        # Send the message to the server...
        try:
            import networking
            networking.send_chat_message(msg, from_player, to_player)
        except ImportError:
            pass

    def display(self, msg, from_player, to_player):
        global get_ticks, player, view
        # Display the message locally
        if to_player:
            if from_player == player:
                self.messages.append(Messages.Message(get_ticks(),
                        ">%s: %s" % (to_player.name, msg), from_player))
            if to_player == player:
                self.messages.append(Messages.Message(get_ticks(),
                        "%s > %s" % (from_player.name, msg), from_player, True))
                import ctrl
                ctrl.last_received_from = from_player.name

            if to_player.type is "ai" and from_player.type is "human":
                to_player.ai.send_msg(msg, from_player)
        else:
            self.messages.append(Messages.Message(get_ticks(), "%s: %s"%
                    (from_player.name, msg), from_player))
        #print msg

    def drawall(self):
        global get_ticks, view
        lh = float (chat_font.m_font_height) / 0.63
        y = lh
        #fading = False
        to_r = False
        first = False
        for m in self.messages:
            h = lh*m.num_lines
            timep = get_ticks() - m.time

            m.animate()

            alpha = m.alpha
            if first and not m.force_close:
                m.time = get_ticks()
            elif timep > 4000 or m.force_close:
                if m.force_close and timep < 4000:
                    m.time = get_ticks() - 4000
                    timep = 4000
                # Fade out. Takes 1000 milsecs.
                alpha = 1 - (timep-4000)/1000
                y -= h - alpha*h
            alpha = max(0, min(alpha, 1))
            first = True
            color = m.from_player.glcolor[:]
            color.append(alpha)
            chat_font.render(10, view.h-y, m.msg, color)
            if alpha == 0:
                to_r = True
            y += h

        if to_r:
            self.messages.pop(0)


messages = Messages()

class Flake(rabbyt.Sprite):
    def __init__(self, bounds):
        self.tn = randint(0, 3)
        tex = snowflakes_texture[self.tn]
        rabbyt.Sprite.__init__(self)
        self.shape = tex.get_shape_pos()
        self.tex_shape = tex.get_shape_tex()
        self.texture_id = tex.texture_id

        x = random()*view.scale_w
        y = random()*view.scale_h

        speed = random()*.05+.05  # px per ms
        self.life = random()*200+300

        self.lifetime = self.life/speed

        self.x = rabbyt.wrap(bounds[0], x, static=False)
        y = rabbyt.lerp(y, y+self.life, dt=self.lifetime)
        self.y = rabbyt.wrap(bounds[1], y, static=False)

        self.scale = rabbyt.lerp(1, 0, dt=self.lifetime)


class Snowflakes(object):
    def __init__(self):
        self.flakes = set()

        self.max_flakes = 100

        self.bounds = [[0,0],[0,0]]

        self.scheduler = rabbyt.Scheduler()

    def run(self, falling):
        self.scheduler.pump()
        if falling:
            if len(self.flakes) < self.max_flakes:
                self.add_flake()

        # Update the bounds with the view information:
        self.bounds[0][0] = view.x
        self.bounds[1][0] = view.y
        self.bounds[0][1] = view.x + view.scale_w
        self.bounds[1][1] = view.y + view.scale_h

        rabbyt.render_unsorted(self.flakes)

    def add_flake(self):
        f = Flake(self.bounds)
        self.flakes.add(f)
        self.scheduler.add(get_ticks()+f.lifetime,
                lambda: self.flakes.discard(f))

snowflakes = None

class Avalanche(object):
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.flakes = set()

    def run(self):
        self.x += self.direction[0]*10
        self.y += self.direction[1]*10

        if self.x < 0 or self.y < 0 or self.x > map.size[0]*32 or \
                self.y > map.size[1]*32:
            pass
        else:
            for i in range(10):
                fx = self.x + random()*32*6
                fy = self.y
                self.flakes.add(Flake(fx, fy, (100,50)))

        t_r = set()
        for f in self.flakes:
            f.y -= 1
            d = abs(f.y-f.start_pos[1])
            if d > f.life:
                t_r.add(f)
                continue

            scale = 2 - ((f.life - d) / f.life * 2)
            glPushMatrix()
            glTranslatef(f.x,f.y,0)
            glScalef(scale, scale, 0)
            snowflakes_texture[f.tn].render()
            glPopMatrix()
        self.flakes.difference_update(t_r)


#avalanches = set((Avalanche(100*32, 0, (0,1)), ))


draw_buffer = []


selected_units = set()
select_box_start = None
select_box_end = None

draw_minimap = False


units = []
buildings = []
resources = set()
snowballs = set()

# Players in the game.
players = {}

# The player on this client
player = None



pause_time = 0
penguins = {}
map = None
minimap = None
trees = []
snowballtextures = []
smoke = None
snowparticle = None
snowballimprents = None
snowball_ice_imprents = None
footimprents = None
penguinselection = None
moveimprents = None
runmoveimprents = None
gathermoveimprents = None
marker = None
jeopardy_marker = None
fish = None
chat_font = None
stat_font = None
data_loaded = False
footprints_settings = 0
icepinnacle = []
snowflakes_texture = []

def load_snowflakes():
    global snowflakes_texture, snowflakes
    st = textures.Texture("data/snowparticles.png")
    snowflakes_texture.append(st.sub(0,0,8,8))
    snowflakes_texture.append(st.sub(8,0,8,8))
    snowflakes_texture.append(st.sub(0,8,8,8))
    snowflakes_texture.append(st.sub(8,8,8,8))

    snowflakes = Snowflakes()

def load_font():
    global chat_font, stat_font
    # Fonts.
    chat_font = font.Font("data/TSCu_Comic.ttf", 20)
    stat_font = font.Font("data/TSCu_Comic.ttf", 16, True)

def init(mapname):
    from player import Player
    from map import Map
    from minimap import MiniMap
    global data_loaded, penguins, map, player, trees, snowballtextures, smoke, snowparticle, Imprent, snowballimprents, snowball_ice_imprents, footimprents, penguinselection, moveimprents, marker, jeopardy_marker, fish, minimap, units, buildings, resources, snowballs, players, draw_buffer, selected_units, select_box_start, select_box_end, draw_minimap, runmoveimprents, gathermoveimprents, footprints_settings, icepinnacle

    # We cache this here because this option is accessed so often.
    footprints_settings = int(settings.get_option("footprints"))

    #Clear data stores in case filled.
    messages.__init__()
    units = []
    buildings = []
    resources = set()
    snowballs = set()
    players = {}
    draw_buffer = []
    selected_units = set()
    select_box_start = None
    select_box_end = None
    draw_minimap = False

    # Imprent sets. We want to assign these even if data loaded.,
    snowballimprents = ImprentSet("data/snowballimprent.png", 2)
    snowball_ice_imprents = ImprentSet("data/snowball_ice_imprent.png", 2)
    footimprents = ImprentSet("data/footprint.png", 4)
    moveimprents = ImprentSet("data/marker.png", 0.3)
    runmoveimprents = ImprentSet("data/marker_run.png", 0.3)
    gathermoveimprents = ImprentSet("data/marker_gather.png", 0.3)


    if not data_loaded:

        # Some general textures.
        fish = textures.Texture("data/fish.png")
        snowparticle = textures.Texture("data/snowparticle.png")
        jeopardy_marker = textures.Texture("data/jeopardy_marker.png")
        marker = textures.Texture("data/marker.png")
        smoke = textures.Texture("data/smoke.png")
        penguinselection = textures.Texture("data/selected.png")

        # Trees.
        tt = textures.Texture("data/trees.png")
        trees.append(tt.sub(0,0,64,64))
        trees.append(tt.sub(64,0,64,64))
        trees.append(tt.sub(0,64,64,64))
        trees.append(tt.sub(64,64,64,64))

        # Ice pinnacles.
        it = textures.Texture("data/icepinnacles.png")
        icepinnacle.append(it.sub(0,0,64,64))
        icepinnacle.append(it.sub(64,0,64,64))
        icepinnacle.append(it.sub(0,64,64,64))

        # Snowball.
        ss = textures.Texture("data/snowball.png")
        snowballtextures.append(ss.sub(0,0,8,8))
        snowballtextures.append(ss.sub(8,0,8,8))

    # Setup map.
    Map.load(mapname)
    minimap = MiniMap()

    if not data_loaded:

        # Generate penguin textures.
        penguins["walk"] = Penguins("data/walk.png")

        penguins["workerwalk"] = Penguins("data/workerwalk.png")
        penguins["snowballerwalk"] = Penguins("data/snowballerwalk.png")

        penguins["throwing"] = Penguins("data/throw.png")
        penguins["snowballerthrowing"] = Penguins("data/snowballerthrow.png")

        penguins["getting_snowball"] = Penguins("data/gathersnow.png")
        penguins["snowballergetting_snowball"] = Penguins("data/snowballergathersnow.png")

        penguins["unloadfish"] = Penguins("data/unloadfish.png")
        penguins["workerunloadfish"] = Penguins("data/workerunloadfish.png")

        penguins["unloadcrystal"] = Penguins("data/unloadcrystal.png")
        penguins["workerunloadcrystal"] = Penguins("data/workerunloadcrystal.png")

        penguins["gathering"] = Penguins("data/gatherfish.png")
        penguins["workergathering"] = Penguins("data/workergatherfish.png")

        penguins["walkfish"] = Penguins("data/walkfish.png")
        penguins["workerwalkfish"] = Penguins("data/workerwalkfish.png")

        penguins["walkcrystal"] = Penguins("data/walkcrystal.png")
        penguins["workerwalkcrystal"] = penguins["workerwalkfish"]

        penguins["frozen"] = textures.Texture("data/frozen.png")


    data_loaded = True


def get_ticks():
    global pause_time
    return pygame.time.get_ticks()-pause_time


def canvas_to_map(x, y):
    mx, my = view.x + x, view.y + y
    x,y = (max(0, (mx // 32) * 32 // 32), max(0, (my // 32) * 32 // 32))

    match = map.tiles[(x,y)]
    for i in range(1,4):
        try:
            t = map.tiles[(x,y+i)]
            py = t.y*32 - t.elevation*map.elevation_multiplier
            if my > py:
                match = t
        except KeyError:
            pass
    return (match.x,match.y)

def draw_box(x,y,w,h):
    glBegin(GL_QUADS)
    glVertex2f(x, y+h)
    glVertex2f(x+w, y+h)
    glVertex2f(x+w, y)
    glVertex2f(x, y)
    glEnd()
