import pygame, random
from pygame.locals import *
import data
import textures
from OpenGL.GL import *
import bisect


class Building(object):
    """ Model for buildable buildings (markets, inns, paths, etc). """
    def __init__(self, tile, player, construction=0):
        self._player = None

        self.jeopardy = False
        self.jeopardy_count = 0
        self.player_taking_over = None

        self.tile = tile
        self.region = self.tile.region

        self.x = tile.x
        self.y = tile.y
        self.construction = construction

        self._storage = {"fish":0, "crystal":0}

        self.select_surface = False

        self.tiles_in_range = {}

        self.units = set()

        self.units_in_building = set()

        self.player = player

        if hasattr(self, "smoke_start"):
            self.smoke = [(self.smoke_start,40)]
            self.smoke_counter = data.get_ticks()

        self.image = textures.Texture.get("data/"+self.image_name+".png")


    def draw(self):
        x = self.x*32
        y = self.y*32 - self.tile.elevation *\
                data.map.elevation_multiplier

        bisect.insort(data.draw_buffer, data.Rendered(self.image, x, y, z=3))

        if self.player:
            marker_y = y+(self.size-1)*32
            if self.jeopardy:
                bisect.insort(data.draw_buffer, data.Rendered(
                    data.jeopardy_marker, x+self.size*32-32, marker_y, z=4))

                # Draw time left before takeover.
                data.stat_font.render(x, y, "Takeover: %i" %\
                        ((self.jeopardy_count+self.takeover_time-\
                        data.get_ticks())//1000),
                        self.player_taking_over.glcolor)
            else:
                bisect.insort(data.draw_buffer, data.Rendered(data.marker,
                    x+self.size*32-32, marker_y, colorize=self.player.glcolor,
                    z=4))

            if self.player == data.player:
                s = []
                for k,v in self._storage.items():
                    if v:
                        s.append(k+": "+str(v))
                data.stat_font.render(x, marker_y+25, "  ".join(s), (0,0,0))


    def _set_player(self, player):
        if player:
            self._player = player
            for u in self.units:
                u.player = player
    def _get_player(self):
        return self._player
    player = property(_get_player, _set_player)

    def draw_smoke(self):
        # Smoke.
        if hasattr(self, "smoke_start"):
            #print self.smoke
            #print len(self.smoke)
            old_smoke = self.smoke
            self.smoke = set()
            for (x,y), life_left in old_smoke:
                dx = self.x*32+x
                dy = self.y*32+y - self.tile.elevation *\
                        data.map.elevation_multiplier

                if life_left:
                    opc = life_left/60.0
                    s = life_left/60.0
                else:
                    opc = 0
                    s = 0

                s = 1-s

                s += 0.7

                glPushMatrix()
                glColor4f(1, 1, 1, opc)
                glTranslatef(dx, dy, 0)
                glScalef(s,s,1)
                data.smoke.render()
                glPopMatrix()


                #if data.get_ticks() > self.smoke_counter+30:
                a = random.randint(0,1)
                a -= 0.5
                a = max(0,a)
                x += a
                y -= 0.5
                life_left -= 1
                if life_left > 0:
                    self.smoke.add(((x,y), life_left))

            if self.units_in_building:
                if data.get_ticks() > self.smoke_counter+100:
                    self.smoke_counter = data.get_ticks()
                    sx, sy = self.smoke_start
                    sx += random.randint(-2,2)
                    self.smoke.add(((sx, sy),60))


    def can_enter(self, u):
        return False


    def get_image(self):
        """ Gets the correct image to display. """
        if self.construction < 100:
            return self.construction_image
        else:
            return self.image

    def is_in_range(self, obj):
        if self.construction < 100:
            return False

        in_range = True


        if obj.x <= self.x-self.range:
            in_range = False
        if obj.x >= self.x+self.range:
            in_range = False
        if obj.y <= self.y-self.range:
            in_range = False
        if obj.y >= self.y+self.range:
            in_range = False

        return in_range

    def add_storage(self, type, count=1):
        self._storage[type] += count
        self.storage_changed()

    def remove_storage(self, type, count=1):
        self._storage[type] -= count
        self.storage_changed()

    def num_storage(self, type):
        return self._storage[type]

    def storage_changed(self):
        pass


    def check_const(self):
        if self.construction < 100:
            for r in self.cost.items():
                if self._storage[r[0]] < r[1]:
                    return
            self.construction = 100

            for r in self.cost.items():
                self._storage[r[0]] -= r[1]
