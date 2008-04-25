#!/usr/bin/env python
from __future__ import division
import sys
import rabbyt

"""try:
    import rabbyt
except ImportError:
    print "Could not find the rabbyt library! You can get it at the python cheese shop.\nTry running:\n\n$ sudo easy_install rabbyt"
    sys.exit()"""


from player import Player

import struct

import threading, socket
from Queue import Queue, Empty

import networking
from networking import NetLoopBase

from OpenGL.GL import *
import pygame
from pygame.locals import *
import textures
import operator
import settings
import menu
import selectctrl

import data, ctrl, unit

import display

try:
    import psyco
    psyco.profile()
except ImportError: pass

import unit


pygame.init()

class Main:
    def __init__(self):
        # For networked games a peer will be assigned here.
        self.net = None

        self.load_lobby_data()

        unit.set_unit_base(unit.Unit)

    def lobby(self, mapname):
        self.mapname = mapname
        self.load_lobby_data()
        self.running = True
        self.loading_screen()
        if data.THIS_IS_SERVER:
            self.load_data(self.mapname)
        self.clock = pygame.time.Clock()
        self.last_fps = 0
        self.lobbybg = textures.Texture.get("data/lobbybg.png")
        if data.THIS_IS_SERVER:
            # Create a local player on the server.
            data.player = self.add_player(settings.config.get("player", "name"),
                    None)
            data.player.loading = False
            networking.send(networking.MClientFinishedLoading(
                    data.player.player_id))
        if self.net:
            self.lobbying = True
            glClearColor(0.95, 0.95, 0.95, 1)
            while self.lobbying and self.running:
                self.lobby_loop()
        else:
            self.lobbying = False
        if self.running:
            self.run()

    def lobby_loop(self):
        dt = self.clock.tick(35)
        self.handle_network()

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)

            elif event.type == KEYDOWN:
                if not ctrl.chatting:
                    if event.key == K_ESCAPE:
                        self.running = False
                        self.lobbying = False
                    elif event.key == K_s:
                        self.lobbying = False
                    elif event.key == K_RETURN:
                        ctrl.chatting = True
                    elif event.key == K_c:
                        data.messages.clear()
                    elif event.key == K_COMMA:
                        if ctrl.last_chat_name:
                            ctrl.chatting = True
                            ctrl.chatting_msg = ctrl.last_chat_name+" "
                    elif event.key == K_PERIOD:
                        if ctrl.last_received_from:
                            ctrl.chatting = True
                            ctrl.chatting_msg = ">"+ctrl.last_received_from+" "
                else:
                    ctrl.handle_chatting(event)

        if ctrl.chatting:
            if data.get_ticks()-ctrl.last_back_press > 300:
                k = pygame.key.get_pressed()
                if k[K_BACKSPACE]:
                    ctrl.chatting_msg = ctrl.chatting_msg[:-1]

        glClear(GL_COLOR_BUFFER_BIT)

        x = y = 0
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.snow.texture_id)
        glColor4f(1,1,1,1)
        glBegin(GL_QUADS)
        glTexCoord2f(x/512,y/512)
        glVertex2i(0,0)
        glTexCoord2f((x+vw)/512,y/512)
        glVertex2i(vw, 0)
        glTexCoord2f((x+vw)/512,(y+vh)/512)
        glVertex2i(vw, vh)
        glTexCoord2f(x/512,(y+vh)/512)
        glVertex2i(0, vh)
        glEnd()

        self.lobbybg.render(y=60, invert_y=False)

        # Draw chat.
        if ctrl.chatting:
            glColor4f(0,0,0,0.75)
            glBegin(GL_QUADS)
            glVertex2f(0, 0)
            glVertex2f(vw, 0)
            glVertex2f(vw, 60)
            glVertex2f(0, 60)
            glEnd()

            if ctrl.chatting_help:
                data.chat_font.render(10, 30, ctrl.chatting_help,
                        (0.65,0.65,0.65))

            data.chat_font.render(10, 00, ctrl.chatting_msg+"_", (1,1,1))
        data.messages.drawall()


        if data.THIS_IS_SERVER:
            data.chat_font.render(self.vw/2 - 200, 20,
                    "Waiting for connections - Press 'S' to start",
                    (0,0,0))
        else:
            data.chat_font.render(self.vw/2 - 230, 20,
                    "Waiting for more players to join - Press 'Enter' to chat",
                    (0,0,0))

        i = 0
        for p in data.players.values():
            c = p.glcolor[:]
            t = p.name
            if p.loading:
                a = .35
                t += " (loading)"
            else: a = 1
            c.append(a)
            data.chat_font.render(self.vw/2 - 60, 100 + 23*i, t, c)

            i += 1
        data.chat_font.render(self.vw/2 - 80, 100 + 23*i, "Players:", (0,0,0))


        glColor3f(1,1,1)

        if settings.get_option("cursor") == "1":
            pos = pygame.mouse.get_pos()
            self.mouse_cursor.render(pos[0], (vh-64)-pos[1])

        pygame.display.flip()

    def run(self):
        self.pause_time = 0

        # 0 = midnight; max is 87 before loops back to 0
        self.time = 45
        self.clock = pygame.time.Clock()
        self.running = True

        self.last_ai_tick = 0
        self.last_alert_tile_tick = data.get_ticks()
        self.last_rc_tick = 0
        self.last_time_tick = data.get_ticks()
        #glScalef(0.5, 0.5, 1)
        #glTranslatef(0, 500,0)
        data.play_game_music()
        self.run_loop()

    def run_loop(self):
        self.add_map_players()
        self.look_at_starting_igloo()
        while self.running:
            self.ai_loop()
            self.loop()
            if data.player.victory != None:
                self.running = False

        pygame.mixer.music.fadeout(1000)
        self.end_game_loop()

    def end_game_loop(self):
        if data.player.victory:
            screen = textures.Texture.get("data/winner.png").sub(0,0,640,480)
        else:
            screen = textures.Texture.get("data/loser.png").sub(0,0,640,480)
        end_screen = True
        glClearColor(0, 0, 0, 1)
        glPushMatrix()
        x = (self.vw-640)/2
        y = (self.vh-480)/2
        glTranslatef(x,self.vh-480-y,0)
        pygame.event.clear()
        alpha = 0
        while end_screen:
            self.clock.tick(35)
            for event in pygame.event.get():
                if event.type == KEYUP:
                    end_screen = False
                    break
            if alpha <= 1:
                glClear(GL_COLOR_BUFFER_BIT)
                alpha += 0.05
                glColor4f(1,1,1,alpha)
                screen.render(invert_y=False)
                pygame.display.flip()
        glPopMatrix()

    def get_new_player_id(self):
        id = 1
        while id in data.players:
            id += 1
        return id

    def add_player(self, name, color):
        if data.map.regions.has_key(color):
            region = data.map.regions[color]
        else:
            # If we can't find a region with the requested color, find whatever
            # is available.
            items = data.map.regions.items()
            from random import shuffle
            shuffle(items)
            for color, region in items:
                if (not region.player or region.player.type == "ai") and\
                        region.igloo:
                    break
        new_player = Player(name, "human", color)
        new_player.loading = True
        old_player = data.map.regions[color].player
        if old_player and not old_player.is_alive():
            data.players[old_player.player_id] = None
        new_player.player_id = self.get_new_player_id()
        data.players[new_player.player_id] = new_player
        # Send new player alert
        networking.send(networking.MNewPlayer(new_player.player_id,
                new_player.name, color, new_player.loading))
        data.map.regions[color].player = new_player
        return new_player

    def add_map_players(self):
        """
        Adds local player and AI players.

        Should not be called on the client.
        """
        # Create some ai players.
        for key, region in data.map.regions.items():
            if region.player or not region.igloo: continue
            new_player = Player("ai"+str(len(data.players)), "ai", key)
            new_player.player_id = self.get_new_player_id()
            data.players[new_player.player_id] = new_player
            networking.send(networking.MNewPlayer(new_player.player_id,
                new_player.name, new_player.color, new_player.loading))
            region.player = new_player

    def look_at_starting_igloo(self):
        # Start the view at the player's igloo
        if not data.player: return
        for i in data.buildings:
            if i.player == data.player:
                ctrl.look_at(i.x*32, i.y*32)
                break

    def loading_screen(self):
        # Loading screen.
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        loading = textures.Texture.get("data/loading.png").sub(0,0,640,480)
        glPushMatrix()
        x = (self.vw-640)/2
        y = (self.vh-480)/2
        glTranslatef(x,self.vh-480-y,0)
        loading.render(invert_y=False)
        glPopMatrix()
        pygame.display.flip()
        self.loading_screen_alpha = 1

    def load_lobby_data(self):
        self.snow = textures.Texture("data/snow.png")
        self.warningtexture = textures.Texture("data/warning.png", scale_format="linear")
        self.mouse_cursor = textures.Texture("data/mouse_cursor.png")

    def load_data(self, mapname):
        data.init(mapname)

        import terrain
        self.snow_terrain = terrain.Terrain(None, "all")
        self.ice_terrain = terrain.Terrain(None, "ice")

        if settings.get_option("cursor") == "1":
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)

    def ai_loop(self):
        # Only needs to run AI functions so often.
        if data.get_ticks() > self.last_ai_tick + 3000:
            self.last_ai_tick = data.get_ticks()
            for player in data.players.values():
                if player and player.type == "ai" and player.is_alive():
                    player.ai.run()

        # Fade alert tiles.
        if data.get_ticks() > self.last_alert_tile_tick + 3*1000:
            self.last_alert_tile_tick = data.get_ticks()

            for player in data.players.values():
                if not player: continue
                t_r = set()
                for t in player.alert_tiles.keys():
                    if player.alert_tiles[t] != 0:
                        player.alert_tiles[t] -= 1
                        if player.alert_tiles[t] == 0:
                            t_r.add(t)
                for t in t_r:
                    del player.alert_tiles[t]


    def loop(self):
        start = pygame.time.get_ticks()
        #if pygame.time.get_ticks() - self.last_fps > 1000:
            #print "FPS: ", self.clock.get_fps()
            #self.last_fps = pygame.time.get_ticks()
        dt = self.clock.tick(35)
        if dt > 144: dt = 144
        if not ctrl.handle_events(dt):
            self.running = False
        else:
            display.draw(self, dt)

        #end = pygame.time.get_ticks()
        #if end-start > 60: print "stutter!", end-start


class ServerMain(Main, networking.NetLoopBase):
    def __init__(self):
        # We will need to listen for new connections in the main thread, so when
        # they come in on the server listening thread we will add them to this
        # queue to handle later.
        self.incomming_connections = Queue()

        self.net = networking.Server(5555)
        self.net.new_connection = lambda c: self.incomming_connections.put(c)
        networking.net = self.net
        self.net.start()
        print 'Waiting for a connection'

        unit.set_unit_base(networking.MasterUnit)

    def handle_network(self):
        networking.NetLoopBase.handle_network(self)
        self.handle_incomming_connections()

    def run_loop(self):
        self.add_map_players()
        self.look_at_starting_igloo()
        networking.send(networking.MGameStart())
        while self.running:
            self.ai_loop()
            self.handle_network()
            self.loop()
            if data.player.victory != None:
                self.running = False

        self.end_game_loop()

    def handle_incomming_connections(self):
        # Handles a new connection from the incomming_connections queue.
        try:
            con = self.incomming_connections.get(False)
        except Empty:
            return

        # Somewhere in here is where the connection should be authenticated.

        # We replaced ``new_connection`` so that we could intercept new
        # connections.  Lets call the original now...
        networking.Server.new_connection(self.net, con)

        con.send(networking.MMapname(self.mapname))


    def handle_MNewPlayer(self, m):
        # A client is requesting creating a new player.

        name = m.name
        num = 0
        # Find a non-conflicting name
        taken = [p.name for p in data.players.values()]
        while name in taken:
            num += 1
            name = m.name+str(num)

        p = self.add_player(name, m.color)
        p.loading = m.loading
        p.connection = m.connection

        con = p.connection

        # Tell client about all players.
        for player in data.players.values():
            m = networking.MNewPlayer(player.player_id, player.name,
                    player.color, player.loading)
            con.send(m)
        # Tell client about all igloo owners.
        for b in data.buildings:
            if hasattr(b, "player") and b.player:
                m = networking.MBuildingOwner(b.building_id,
                        b.player.player_id)
                con.send(m)

        # Tell client which player THEY are.
        m = networking.MWhoYouAre(p.player_id)
        con.send(m)

        # Tell the client about dynamic map objects:
        for o in data.map._dynamic_objects:
            o.alert_creation(to=[con])


    def handle_MClientFinishedLoading(self, m):
        try:
            p = data.players[m.player_id]
        except KeyError:
            return
        p.loading = False
        networking.send(networking.MClientFinishedLoading(p.player_id))

    def handle_MSetJob(self, m):
        # TODO make sure this is comming from the correct address!
        for unit in [data.units[i] for i in m.unit_ids]:
            if unit.player.connection == m.connection:
                unit.set_job(m.pos, m.run_mode)

    def handle_MDisbanUnits(self, m):
        for unit in [data.units[i] for i in m.unit_ids]:
            if unit.player.connection == m.connection:
                unit.disban()

    def handle_MChatMessage(self, m):
        from_player = data.players[m.from_id]
        if from_player.connection == m.connection:
            if m.to_id == 0xffff:
                to_player = None
            else:
                to_player = data.players[m.to_id]
            data.messages.send(m.msg, from_player, to_player)


class ClientMain(Main, NetLoopBase):
    def __init__(self, host = "localhost"):
        data.THIS_IS_SERVER = False
        self.host = host
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, 5555))
        self.net = networking.Connection(s)
        networking.net = self.net

        # Tell the server our name
        m = networking.MNewPlayer(0xffff, settings.config.get('player', 'name'),
                (0,0,0), True)
        networking.send(m)

        unit.set_unit_base(networking.SlaveUnit)

    def run_loop(self):
        while self.running:
            self.handle_network()
            self.loop()
            if data.player.victory != None:
                self.running = False
        self.end_game_loop()

    def handle_message(self, m):
        if NetLoopBase.handle_message(self, m):
            return True
        handled = False
        name = "handle_" + m.__class__.__name__
        if hasattr(m, "unit_id") and m.unit_id < len(data.units):
            u = data.units[m.unit_id]
            if hasattr(u, name):
                handled = True
                getattr(u, name)(m)
        if hasattr(m,"building_id") and m.building_id < len(data.buildings):
            b = data.buildings[m.building_id]
            if hasattr(b, name):
                handled = True
                getattr(b, name)(m)
        if hasattr(m, "dmo_id") and m.dmo_id < len(data.map._dynamic_objects):
            dmo = data.map._dynamic_objects[m.dmo_id]
            if hasattr(dmo, name):
                handled = True
                getattr(dmo, name)(m)
        if hasattr(m, "player_id") and m.player_id in data.players:
            player = data.players[m.player_id]
            if hasattr(player, name):
                handled = True
                getattr(player, name)(m)
        return handled

    def handle_MResourceQuantity(self, m):
        data.map.tiles[(m.tx, m.ty)].resource.quantity = m.q

    def handle_MNewPlayer(self, m):
        p = Player(m.name, "human", m.color)
        p.player_id = m.player_id
        p.loading = m.loading
        data.players[p.player_id] = p

    def handle_MWhoYouAre(self, m):
        p = data.players[m.player_id]
        data.player = p

        # Now that we know who we are, we should center the view on our igloo.
        self.look_at_starting_igloo()

        # Tell the server that we have finished loading.
        # NOTE we only assume that we are done loading here because no network
        # messages are processed until loading is finished.
        networking.send(networking.MClientFinishedLoading(p.player_id))

    def handle_MClientFinishedLoading(self, m):
        p = data.players[m.player_id]
        p.loading = False

    def handle_MGameStart(self, m):
        self.lobbying = False

    def handle_MCreateDynamicMapObject(self, m):
        assert m.dmo_id == len(data.map._dynamic_objects)
        # dmo_id will be the first value, but __init__ won't expect that so
        # we'll leave it out.  (It will be assigned when it is added to the
        # map.
        dmo = networking.SlaveDynamicMapObject(*m.values()[1:])

    def handle_MChatMessage(self, m):
        from_player = data.players[m.from_id]
        if m.to_id == 0xffff:
            to_player = None
        else:
            to_player = data.players[m.to_id]
        data.messages.display(m.msg, from_player, to_player)

    def handle_MMapname(self, m):
        self.mapname = m.mapname
        self.load_data(m.mapname)

    def load_data(self, mapname):

        Main.load_data(self, mapname)





# Setup display
if settings.get_option("fullscreen") == "1":
    flags = OPENGL | DOUBLEBUF | FULLSCREEN
else:
    flags = OPENGL | DOUBLEBUF
vw,vh = viewport = settings.get_res()
pygame.display.set_mode(viewport, flags)
pygame.display.set_caption("Snowballz")

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glViewport(0, 0, vw, vh)
glOrtho(0, vw, 0, vh, -50, 50)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glDisable(GL_LIGHTING)
glDisable(GL_DEPTH_TEST)

glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
glEnable(GL_BLEND)

data.view.w, data.view.h = viewport

data.load_font()
data.load_snowflakes()

if len(sys.argv) <= 1:
    mainmenu = menu.Main(viewport)
while True:
    pygame.mouse.set_visible(True)
    data.play_menu_music()
    if len(sys.argv) <= 1:
        mapname, gametype, arg = mainmenu.run()
    else:
        mapname = "whiteforest"
        if "--server" in sys.argv:
            gametype = "server"
        elif "--client" in sys.argv:
            gametype = "client"
            arg = sys.argv[sys.argv.index("--client")+1]
        elif "--single" in sys.argv:
            gametype = "single"
        else:
            raise ValueError("No gameplay type")
        if len(sys.argv) > 2:
            mapname = sys.argv[2]

    #glHint(GL_TEXTURE_COMPRESSION_HINT, GL_FASTEST)
    pygame.mixer.music.fadeout(3000)

    if gametype == "single":
        main = Main()
    elif gametype == "server":
        main = ServerMain()
    elif gametype == "client":
        main = ClientMain(arg)
    main.vw, main.vh = main.viewport = viewport
    main.lobby(mapname)
    if len(sys.argv) > 1:
        break
