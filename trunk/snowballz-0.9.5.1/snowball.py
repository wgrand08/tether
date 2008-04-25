from __future__ import division
from math import cos, sin, sqrt
import random, pygame
import data
from OpenGL.GL import *
import random
import settings

import rabbyt


class SnowParticles:
    def __init__(self, x, y, direction, numparticles):
        self.x = x
        self.y = y

        self.particles = []

        dt = 400

        self.start = rabbyt.get_time()
        self.end = self.start + dt

        for i in xrange(numparticles):
            dx, dy = direction
            dx += (random.random() -1) * 30
            dy += (random.random() -1) * 30
            tex = data.snowparticle
            s = rabbyt.Sprite(tex.texture_id, tex.get_shape_pos(),
                    tex.get_shape_tex())
            s.x = rabbyt.lerp(x, x+dx, dt=dt)
            s.y = rabbyt.lerp(y, y+dy, dt=dt)
            s.rgba = (1,1,1, rabbyt.lerp(1, 0, self.start+dt/2, self.end))
            self.particles.append(s)

    def run(self, timestep):

        if rabbyt.get_time() < self.end:
            rabbyt.render_unsorted(self.particles)
            return True
        else:
            return False



class Snowball:
    @classmethod
    def throw_at_target(cls, penguin, target_penguin):
        """
        Starts the snowball with being thrown as a specified target, with
        random accuracy.
        """


        # t_x_t stands for "tile x target".
        if penguin.x <= target_penguin.x + 3 and penguin.x >= target_penguin.x - 3\
        and penguin.y <= target_penguin.y + 3 and penguin.y >= target_penguin.y - 3:
            t_x_t = target_penguin.x
            t_y_t = target_penguin.y
        else:
            t_x_t = random.randint(target_penguin.x-1,target_penguin.x+1)
            t_y_t = random.randint(target_penguin.y-1,target_penguin.y+1)

        end_tile = data.map.tiles[(t_x_t, t_y_t)]
        end_x = t_x_t*32+random.randint(0, 20)
        end_y = t_y_t*32+random.randint(0, 20) - end_tile.elevation *\
                data.map.elevation_multiplier

        start_tile = data.map.tiles[(penguin.x, penguin.y)]
        start_x, start_y = penguin.x*32, penguin.y*32
        start_y -= start_tile.elevation*data.map.elevation_multiplier

        return cls(start_x,start_y, end_x,end_y,end_tile, start_tile, penguin)


    def __init__(self, start_x, start_y, end_x, end_y, end_tile,
            start_tile=None, penguin=None):
        """ start_x, start_y, end_x and end_y and all pixel based. """
        self.end_tile = end_tile

        # These are only needed for the server (unit code). They arn't sent
        # over the network.
        self.start_tile = start_tile
        self.penguin = penguin

        self.end_x, self.end_y = end_x, end_y
        self.start_x, self.start_y = start_x, start_y

        self.speed = .15
        self.y_offset = 0

        self.dist_x = self.end_x - start_x
        self.dist_y = self.end_y - start_y

        self.dist = (self.dist_x**2 + self.dist_y**2)**.5
        self.total_time = self.dist/self.speed

        self.height = ((self.dist/2)/10)**2

        self.start_time = data.get_ticks()

        tex = data.snowballtextures[0]
        self.sprite = rabbyt.Sprite(tex.texture_id,tex.get_shape_pos(),
                tex.get_shape_tex(invert_y=True))

        tex = data.snowballtextures[1]
        self.shadow_sprite = rabbyt.Sprite(tex.texture_id,tex.get_shape_pos(),
                tex.get_shape_tex(invert_y=True))

    def move(self):
        time_diff = data.get_ticks()-self.start_time
        to_move = time_diff*self.speed

        mx = (to_move*self.dist_x)/self.dist
        my = (to_move*self.dist_y)/self.dist

        offset = -((to_move-self.dist/2)/10)**2 + self.height

        self.sprite.x = self.start_x + mx
        self.sprite.y = self.start_y + my + 8 - offset/2
        
        self.shadow_sprite.x = self.start_x + mx
        self.shadow_sprite.y = self.start_y + my

        if data.get_ticks() - self.start_time >= self.total_time:
            # Snowball reached dest.
            vw = data.view.w
            vh = data.view.h
            hit = 1
            if self.end_tile.resource:
                hit = 0
            else:
                for u in data.map.unit_nodes.get_objs_around_tile(
                        (self.end_tile.x, self.end_tile.y)):
                    #if u.player is not self.player:
                    if u.warmth > 0:
                        if u.state != "inbuilding":
                            v = u.detect_hit(self)
                            if v == 2: hit = 2

            if hit != 2 and int(settings.get_option("snowballdetail")) >= 2:
                if self.end_tile.type == "snow":
                    data.snowballimprents.add(self.sprite.x, self.sprite.y)
                else:
                    data.snowball_ice_imprents.add(self.sprite.x, self.sprite.y)

            if self.sprite.x > data.view.x and self.sprite.x < data.view.x+vw\
                    and self.sprite.y > data.view.y and self.sprite.y <\
                    data.view.y+vh:
                d = sqrt(self.dist_y*self.dist_y + self.dist_x*self.dist_x)
                y = self.dist_y * (30/d)
                x = self.dist_x * (30/d)
                if hit == 2:
                    x, y = -x, -y
                    particles = random.randint(13,20)
                else:
                    particles = random.randint(8,10)

                if int(settings.get_option("snowballdetail")) == 3:
                    data.particles.add(SnowParticles(self.sprite.x,
                            self.sprite.y, (x,y), particles))

            return True
        return False
