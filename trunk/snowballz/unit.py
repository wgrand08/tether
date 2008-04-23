import textures
import os
from OpenGL.GL import *
import data
from random import *
import math, sys
import snowball
import events
import bisect

import rabbyt


class UnitRendered(data.Rendered):
    def __init__(self, unit):
        self.unit = unit
        self.x, self.y = unit.penguin_sprite.xy
        self.height = 32
        self.z = 1

    def render(self):
        self.unit.penguin_sprite.render()
        if self.unit.outfit_sprite.texture_id != 0:
            self.unit.outfit_sprite.render()


class Unit(object):
    max_warmth = 10
    gather_time = 20000
    create_snowball_time = 3000

    @property
    def walk_speed(self):
        r = 800
        np = self.pos_in_dir(self.direction)
        t = data.map.tiles[(self.x, self.y)]
        try:
            t2 = data.map.tiles[np]
            d = t2.elevation - t.elevation
        except:
            d = 0
        r += d*50
        return r

    def __init__(self, pos, igloo, type, state="inbuilding"):
        self.direction = None

        self.x,self.y = pos
        self.draw_x = self.draw_y = 0

        self.current_frame = randint(0, 10)
        self.last_tick = 0

        # Some client only stuff:
        self.group = None
        self.selected = False


        self.type = type
        self.warmth = self.max_warmth
        self.prv_node = None

        self.igloo = igloo
        self.igloo.units.add(self)

        self.target_pos = None
        self.stray_range = 5

        self._go_to_building = None

        self.state = state
        if state == "inbuilding":
            self.go_to_building = igloo
            igloo.units_in_building.add(self)

        self.holding = None

        self.targeted_unit = None


        self.move_time = 0
        self.moving = False

        # Direction that the unit is moving in
        self.direction = (0,-1)

        self.target_resource = None

        # Used so that the penguin doesn't get stuck going back and forth.
        self.last_tiles = []

        self.counter = 0

        self.__fail_time = 0

        self.run_mode = False

        # Plugins applied to this penguin.
        self.plugins = set()
        self._emblems = set()


        xy = self.x*32, self.y*32 - data.map.tiles[(self.x,
                self.y)].elevation*data.map.elevation_multiplier
        self.penguin_sprite = rabbyt.Sprite(shape=(0,0,32,32), xy=xy)
        self.outfit_sprite = rabbyt.Sprite(shape=(0,0,32,32), xy=xy)

    def add_emblem(self, emblem):
        self._emblems.add(emblem)

    def remove_emblem(self, emblem):
        if emblem in self._emblems:
            self._emblems.remove(emblem)

    def _set_go_to_building(self, building):
        if self.state != "entering" and (self.state != "inbuilding" or not self._go_to_building):
            self._go_to_building = building
    go_to_building = property(lambda self: self._go_to_building, _set_go_to_building)


    def draw(self):
        if self.direction == (0,0):
            print "warnning: direction is (0,0)"
            self.direction = (0,1)
        x,y = self.penguin_sprite.xy
        self.draw_x = x
        self.draw_y = y

        #self.penguin_sprite.xy = x,y
        #self.outfit_sprite.xy = x,y

        if self.igloo.player: color = self.igloo.player.glcolor
        else: color = (1,1,1)

        self.outfit_sprite.rgb = color

        if data.view.zoom < 0.5:
            # So zoomed out... just draw a box.
            scolor = list(color)
            alpha = min(1-(data.view.zoom-0.2)/0.2, 1)
            scolor.append(alpha)
            glColor4f(*scolor)
            glDisable(GL_TEXTURE_2D)
            data.draw_box(x,y,32,32)
            if alpha == 1:
                return

        if self.state == "frozen":
            t = data.penguins["frozen"]
            to = None
        elif self.state == "unloading":
            t = data.penguins["unload"+self.holding].images[(self.current_frame,
                        self.direction)]
            to = data.penguins["workerunload"+self.holding].images[(self.current_frame,
                        self.direction)]
        elif self.state in ["throwing", "getting_snowball",
                "gathering"]:
            t = data.penguins[self.state].images[(self.current_frame,
                        self.direction)]
            to = data.penguins[self.type+self.state].images[(self.current_frame,
                        self.direction)]
        elif self.type == "worker" and self.holding:
            t = data.penguins["walk"+self.holding].images[(self.current_frame,
                        self.direction)]
            to = data.penguins["workerwalk"+self.holding].images[(self.current_frame,
                        self.direction)]
        else:
            if self.moving:
                t = data.penguins["walk"].images[(self.current_frame,
                        self.direction)]
                to = data.penguins[self.type+"walk"].images[(self.current_frame,
                        self.direction)]
            else:
                t = data.penguins["walk"].images[("idle", self.direction)]
                to = data.penguins[self.type+"walk"].images[("idle", self.direction)]

        self.penguin_sprite.texture_id = t.texture_id
        self.penguin_sprite.tex_shape = t.get_shape_tex(invert_y=True)
        if to:
            self.outfit_sprite.texture_id = to.texture_id
            self.outfit_sprite.tex_shape = to.get_shape_tex(invert_y=True)
        else:
            self.outfit_sprite.texture_id = 0

        if self.selected:
            # Draw selection.
            bisect.insort(data.draw_buffer, data.Rendered(data.penguinselection,
                x, y, z=1))

        # Draw penguin
        bisect.insort(data.draw_buffer, UnitRendered(self))


        for e in self._emblems:
            e.draw(self.draw_x, self.draw_y)


        # Warmth bar.
        if self.state != "frozen" and self.warmth < self.max_warmth:
            glDisable(GL_TEXTURE_2D)
            b = lambda w: max(min(abs((w/float(self.max_warmth)*2)-2), 1), 0)
            g = lambda w: max(min(w/float(self.max_warmth)*2, 1), 0)

            x += 32
            y += 28

            height = self.warmth*20/self.max_warmth

            glPushMatrix()
            glColor4f(0,g(self.warmth),b(self.warmth), 1)

            glTranslatef(x, y-height, 0)
            glBegin(GL_QUADS)
            glVertex2f(0, 0)
            glVertex2f(2, 0)
            glVertex2f(2, height)
            glVertex2f(0, height)
            glEnd()

            glColor3f(1,1,1)

            glPopMatrix()

        if self.group:
            data.stat_font.render(self.draw_x, self.draw_y, str(self.group),
                    (1,1,1,1))


    def animate(self, dt):
        #TODO: make the rate of penguin walking based on time.

        #if not self.last_tick:
            #self.last_tick = dt

        #if self.last_tick+2 <= dt:
            #print dt
            self.current_frame += 1
            if self.current_frame > 9:
                self.current_frame = 0

                # BAD HACK to unload penguins
                if self.state == "unloading":
                    # Finished unloading.
                    self.state = "stray"
                    if data.THIS_IS_SERVER:
                        self.igloo.add_storage(self.holding)
                        events.fire(events.PENGUIN_UNLOADED, self, self.holding)
                    self.holding = None

            if self.moving and (self.current_frame == 6 or
                    self.current_frame == 9) and data.footprints_settings:
                x,y = self.penguin_sprite.xy

                if self.direction[0] == 0:
                    if self.current_frame == 6:
                        x += 8
                        y += 10
                    elif self.current_frame == 9:
                        x += 17
                        y += 10
                elif self.direction[1] == 0:
                    y += 16
                    if self.current_frame == 6:
                        x += 11
                        y += 4
                    elif self.current_frame == 9:
                        x += 9
                        y += 8
                else:
                    y += 16
                    if self.current_frame == 6:
                        x += 16
                        y += 8
                    elif self.current_frame == 9:
                        x += 16
                        y += 3

                data.footimprents.add(x,y)


    def pos_in_dir(self, direction):
        """ Returns the next position in this direction relative to the
            penguin. """
        return (self.x+direction[0], self.y+direction[1])
    def try_direction(self, direction):
        """ Check if the penguin can move to this direction. """
        pos = self.pos_in_dir(direction)
        try:
            tile = data.map.tiles[pos]
        except KeyError:
            return False


        if self.state != "entering":
            if tile.building:
                # Penguins can walk on the top row of a building.
                if not tile.building.y == pos[1]:
                    return False

            for o in data.map._dynamic_objects:
                if o.obstruction and o.position == (self.x,self.y):
                    return False

            for u in data.map.unit_nodes.get_objs_around_tile((self.x,self.y)):
                if u is not self:
                    if (u.x,u.y) == pos:
                        return False

        else:
            self.state = "inbuilding"

        if tile.resource:
            return False

        if len(self.last_tiles) >= 30:
            self.last_tiles.pop(0)

        if (tile.x,tile.y) in self.last_tiles:
            return False


        return True


    def move(self):
        startxy = self.x, self.y
        # Skip the check if the penguin is moving.
        if not self.moving:
            # Check with the AI to see if we want to move somewhere.
            if data.get_ticks() > self.__fail_time+randint(200, 400):
                r = self.check_direction()
                if r is False:
                    self.__fail_time = data.get_ticks()
        else:
            time_passed = data.get_ticks()-self.counter
            if time_passed/float(self.walk_speed) >= 1:
                self.check_direction()

        endxy = self.x, self.y
        if startxy != endxy:
            self.move_sprites(startxy, endxy)


    def move_sprites(self, startxy, endxy):
        sx = startxy[0]*32
        sy = startxy[1]*32 - data.map.tiles[startxy].elevation *\
                data.map.elevation_multiplier
        ex = endxy[0]*32
        ey = endxy[1]*32 - data.map.tiles[endxy].elevation *\
                data.map.elevation_multiplier

        x = rabbyt.lerp(sx, ex, dt=self.walk_speed)
        y = rabbyt.lerp(sy, ey, dt=self.walk_speed)

        self.penguin_sprite.xy = x,y
        self.outfit_sprite.xy = x,y

    def check_direction(self):
        direction = self.find_path()
        if direction:
            # Move penguin.
            self.last_tiles.append((self.x,self.y))
            self.x,self.y = self.pos_in_dir(direction)

            events.fire(events.PENGUIN_MOVE, self, self.x, self.y)

            # Update position in node.
            current_node = data.map.unit_nodes.find_current_node(self.x,self.y)
            if not (self.prv_node is current_node):
                if self.prv_node:
                    self.prv_node.remove(self)
                current_node.add(self)
                self.prv_node = current_node

            self.direction = direction
            self.moving = True
            self.counter = data.get_ticks()
            return True
        else:
            self.moving = False
            return direction


    def find_path(self):
        direction = self.stray()
        if not direction:
            return direction

        turn_right_map = {
                (0,1)  :(-1,1),
                (-1,1) :(-1,0),
                (-1,0) :(-1,-1),
                (-1,-1):(0,-1),
                (0,-1) :(1,-1),
                (1,-1) :(1,0),
                (1,0)  :(1,1),
                (1,1)  :(0,1)
                }
        turn_left_map = {
                (-1, -1): (-1, 0),
                (-1, 0): (-1, 1),
                (-1, 1): (0, 1),
                (0, -1): (-1, -1),
                (0, 1): (1, 1),
                (1, -1): (0, -1),
                (1, 0): (1, -1),
                (1, 1): (1, 0)
                }

        turn_left = turn_left_map[direction]
        turn_right = direction
        while True:
            if self.try_direction(turn_right):
                direction = turn_right
                break
            if self.try_direction(turn_left):
                direction = turn_left
                break
            turn_right = turn_right_map[turn_right]
            # Check to see if we have exahsted all posibilities.
            if turn_right == turn_left:
                self.last_tiles = []
                return False
            turn_left = turn_left_map[turn_left]
        return direction





    def stray(self):
        """ AI for penguins.
            This code is a MESS!!! Read at your own risk! Don't say I didn't
            warn you... """

        time = data.get_ticks()

        if self.warmth == 0:
            if data.map.tiles[(self.x,self.y)].building_root == True:
                self.warmth = 1

        if self.warmth < 1:
            self.state = "frozen"
            return False


        # can't interrupt these states.
        if self.state == "unloading":
            return None
        if self.state == "entering":
            self.last_tiles = []
            self.counter = data.get_ticks()
            self.go_to_building.units_in_building.add(self)
            self.go_to_building.unit_enter(self)
            return (1,1)
        if self.state == "inbuilding":
            return self.go_to_building.in_building(self)
        if self.state == "throwing":
            # Throw it!
            if self.current_frame < 9:
                self.state = "throwing"
                return None
            else:
                # All done throwing.
                self.state = "stray"
                self.targeted_unit = None


        # Go to igloo if too cold.
        if self.warmth < 5:
            # clear job.
            self.state = "stray"
            self.gathering_from = None
            self.target_resource = None
            self.target_pos = None
            if self.igloo.can_enter(self):
                self.go_to_building = self.igloo

        else:
            # If penguin gets cold, these states can be interrupted.
            if self.state == "getting_snowball":
                if self.counter+self.create_snowball_time <= data.get_ticks():
                    self.snowballs += 1
                    events.fire(events.PENGUIN_RELOAD, self)
                    self.state = "stray"
                else:
                    return None
            if self.state == "gathering" and not self.target_pos:
                self.last_tiles = []
                if self.gathering_from.resource.quantity == 0:
                    # Resource ran out while gathering.
                    self.gathering_from = None
                    self.target_resource = None
                    self.state = "stray"
                    return self.stray_at_igloo()
                if self.counter+self.gather_time <= data.get_ticks():
                    # Finnished gathering.
                    self.gathering_from.resource.quantity -= 1
                    self.holding = self.gathering_from.resource.type
                    self.gathering_from = None
                    self.target_resource = None
                    self.state = "stray"
                    events.fire(events.PENGUIN_GATHERED, self, self.holding)
                    return self.move_to_building(self.igloo)
                else:
                    return None
            elif self.state == "gathering" and self.target_pos:
                self.gathering_from = None
                self.target_resource = None
                self.state = "stray"


        if not self.igloo.player:
            return self.stray_at_igloo()

        if self.type == "snowballer" and self.igloo.jeopardy == True:
            self.go_to_building = self.igloo

        if self.go_to_building:
            if (self.x, self.y) == (self.go_to_building.x,self.go_to_building.y):
                if self.go_to_building.can_enter(self):
                    self.state = "entering"
                    return
                else:
                    self.go_to_building = None
        if self.go_to_building:
            return self.move_to_building(self.go_to_building)

        # What is this for??? For some reason it must be before next if block!
        if self.type == "snowballer" and\
        data.map.tiles[(self.x,self.y)].building_root and\
        data.map.tiles[(self.x,self.y)].building.player is self.igloo.player\
        or data.map.tiles[(self.x,self.y)].building:
            return self.stray_at_igloo(True)

        return self.work()


    def throw_snowball(self, target):
        # Throw snowball.
        s = snowball.Snowball.throw_at_target(self, target)
        data.snowballs.add(s)
        self.snowballs -= 1
        self.state = "throwing"
        self.direction = self.direction_to_tile(target.x, target.y)
        self.current_frame = 1
        return s

    def direction_to_tile(self, tx, ty):
        """
        returns the direction from this penguin to the given tile coordinates.
        """
        # FIXME  This could perform better for tiles that are not immediately
        # adjacent.  (It is WAY to biased tward the diagonal.)
        if tx > self.x:
            x = 1
        elif tx < self.x:
            x = -1
        else:
            x = 0
        if ty > self.y:
            y = 1
        elif ty < self.y:
            y = -1
        else:
            y = 0
        return (x, y)

    def stray_at_igloo(self, will_stray=False):
        if self.igloo.is_in_range(self):
            if not will_stray:
                will_stray = randint(1,5)
            if will_stray == 1 or will_stray == True:
                d_x = randint(-1, 1)
                d_y = randint(-1, 1)
                if d_x == 0 and d_y == 0:
                    return False

                return (d_x,d_y)
            return False
        else:
            return self.move_to_building(self.igloo)



    def set_job(self, pos, run_mode=False):
        t = data.map.tiles[pos]
        if self.state == "entering" or self.state == "inbuilding":
            return

        self.run_mode = run_mode

        self.last_tiles = []
        self.go_to_building = None
        self.target_pos = None

        if self.type == "worker" and t.resource and t.resource.gatherable:
            self.going_for = t.resource.type
            self.target_resource = t.resource
        elif t.building:
            if not self in t.building.units_in_building:
                self.go_to_building = t.building
        else:
            self.target_pos = pos
            self.stray_range = len(data.selected_units)/2
            self.stray_range = min(max(0, self.stray_range), 6)

    def check_demand(self, b):
        if b.construction < 100:
            demand = b.cost
        else:
            demand = b.demand
        return demand



    def move_to_building(self, building):
        return self.find_next_tile_to_object(building)

    def find_next_tile_to_object(self, object):
        x, y = object.x, object.y
        return self.find_next_tile_to_pos(x, y)

    def find_next_tile_to_pos(self, x, y):
        dx = x - self.x
        dy = y - self.y
        # Normalize...
        d = (dx**2+dy**2)**.5
        dx, dy = dx*(1/d), dy*(1/d)
        # Make it so that the to right corner is (1,1) etc.
        dx *= 2**.5
        dy *= 2**.5

        x = y = 0
        if dx == 0.0:
            x = 0
        elif dx > 0 and dx > random():
            x = 1
        elif dx < 0 and dx < -random():
            x = -1
        if dy == 0.0:
            y = 0
        elif dy > 0 and dy > random():
            y = 1
        elif dy < 0 and dy < -random():
            y = -1

        return (x,y)


    def check_enemy_units_in_range(self):
        units_in_range = set()
        for u in data.map.unit_nodes.get_objs_around_tile((self.x,self.y)):
            if u.igloo.player is not self.igloo.player:
                t = data.map.tiles[(self.x, self.y)]
                ot = data.map.tiles[(u.x, u.y)]
                a = 7 + (t.elevation - ot.elevation)
                if  not (u.x > self.x+a or u.x < self.x-a)\
                and not (u.y > self.y+a or u.y < self.y-a):
                    if u.warmth > 0:
                        if u.state != "inbuilding":
                            units_in_range.add(u)
        return units_in_range


    def detect_hit(self, snowball):
        x,y = snowball.end_tile.x, snowball.end_tile.y
        d = 0
        hit = 0
        if x == self.x and y == self.y:
            d = 3
            self.last_tiles = []
            hit = 2
            events.fire(events.PENGUIN_DIRECT_HIT, self, d)
        elif x in range(self.x-1,self.x+1) and y in range(self.y-1,self.y+1):
            d = 1
            self.last_tiles = []
            hit = 1
            events.fire(events.PENGUIN_HIT, self, d)

        if hit and self.warmth > 0 and self.state != "inbuilding":
            x,y = snowball.start_tile.x, snowball.start_tile.y
            self.igloo.player.alert_tiles[(x, y)] = 3
            self.warmth -= d
            self.last_tiles = []

        if self.warmth < 1:
            self.warmth = 0
            events.fire(events.PENGUIN_FROZEN, self, snowball.penguin)

        return hit

    def is_in_range(self, (x,y)):
        in_range = True
        if x < self.x-self.stray_range:
            in_range = False
        if x > self.x+self.stray_range:
            in_range = False
        if y < self.y-self.stray_range:
            in_range = False
        if y > self.y+self.stray_range:
            in_range = False
        return in_range




class Snowballer(Unit):
    def __init__(self, pos, igloo, state="inbuilding"):
        super(Snowballer, self).__init__(pos, igloo, "snowballer", state)

        self.snowballs = 1

        # What dynamic map object to go directly to.
        self.going_for = None


    def disban(self):
        self.selected = False
        self.go_to_building = None
        self.target_pos = None
        self.going_for = None


    def work(self):
        # We don't want it to stop if in run_mode.
        if not self.run_mode:
            if self.snowballs:
                units_in_range = self.check_enemy_units_in_range()
                if units_in_range:
                    if not self.targeted_unit:
                        snowballers = [u for u in units_in_range if
                                u.type == "snowballer"]

                        if snowballers:
                            units_in_range = snowballers

                        for u in units_in_range:
                            if data.map.tiles[(self.x,self.y)].building_root:
                                continue

                            # Make sure not taking over building belonging to this penguin.
                            if u.warmth < 5:
                                c = False
                                for un in u.igloo.units_in_building:
                                    if un.player == self.igloo.player:
                                        c = True
                                        break
                                if c:
                                    continue

                            if not self.targeted_unit:
                                self.targeted_unit = u
                            else:
                                if ((u.x-self.x)**2 + (u.y-self.y)**2)**.5 <\
                                        (abs(self.targeted_unit.x-self.x)**2 +\
                                        abs(self.targeted_unit.y-self.y)**2)**.5:
                                    self.targeted_unit = u
                    # Putting this in an else makes it so they will move farward
                    # before throwing again.
                    else:
                        if not self.targeted_unit in units_in_range:
                            self.targeted_unit = None
                            return None
                        else:
                            self.throw_snowball(self.targeted_unit)
                            self.targeted_unit = None
                            return None
            else:
                # Get a snowball.
                if data.map.tiles[(self.x,self.y)].type == "snow":
                    self.state = "getting_snowball"
                    self.counter = data.get_ticks()
                    return None



        if self.target_pos:
            if self.is_in_range(self.target_pos):
                # Reached destination. It's now okay to through and gather
                # snowballs again.
                self.run_mode = False

                # This way it won't stand still once it reaches destination if
                # you only told one penguin to go there.
                if self.stray_range == 1:
                    self.stray_range = 3

                # Stray around the current job position.
                self.last_tiles = []
                will_stray = randint(1,3)
                if will_stray == 1:
                    d_x = randint(-1, 1)
                    d_y = randint(-1, 1)
                    if not d_x and not d_y:
                        return False

                    return (d_x,d_y)
                return False
            else:
                return self.find_next_tile_to_pos(*self.target_pos)
        else:
            # Move to alert tiles.
            ts = []
            for t in self.igloo.player.alert_tiles.items():
                x,y = t[0]
                if self.igloo.player.snowballer_alert_range >= ((x-self.x)**2 + (y-self.y)**2)**.5 and t[1] != 0:
                    ts.append(t)

            if ts:
                best_t = None
                for t in ts:
                    x,y = t[0]
                    leng = ((x-self.x)**2 + (y-self.y)**2)**.5
                    if leng and (not best_t or leng < best_t[1]):
                        best_t = (t,leng)

                #if best_t[1] > 4:
                if best_t:
                    return self.find_next_tile_to_pos(x=best_t[0][0][0],
                            y=best_t[0][0][1])
                else:
                    return None

        # No job availible. Stray around home igloo.
        return self.stray_at_igloo()








class Worker(Unit):
    def __init__(self, pos, igloo, state="inbuilding"):
        super(Worker, self).__init__(pos, igloo, "worker", state)

        # Resource to go gather from.
        self.gathering_from = None

        # What type of resource to gather.
        self.going_for = "fish"

        self.holding = None


    def disban(self):
        self.selected = False
        self.go_to_building = None
        self.target_pos = None
        self.going_for = "fish"
        self.target_resource = None


    def work(self):

        if not self.go_to_building:
            if self.target_pos:
                if self.is_in_range(self.target_pos):
                    # Reached destination. Stray around.
                    self.last_tiles = []
                    will_stray = randint(1,4)
                    if self.holding or will_stray == 1:
                        d_x = randint(-1, 1)
                        d_y = randint(-1, 1)
                        if not d_x and not d_y:
                            d_y = 1

                        return (d_x,d_y)
                    return False
                else:
                    return self.find_next_tile_to_pos(*self.target_pos)


            if self.holding:
                # Got a resource, go dump it.
                direction = self.move_to_building(self.igloo)
                next_pos = (direction[0]+self.x, direction[1]+self.y)
                if next_pos == (self.igloo.x,self.igloo.y):
                    self.state = "unloading"
                    self.current_frame=1
                    return
            else:
                # Go get resource.
                direction = self.move_to_resource(self.going_for)


            if direction:
                return direction
            elif self.state == "gathering" or self.state == "unloading":
                return None
            else:
                return self.stray_at_igloo()

        # No job availible. Stray around home igloo.
        return self.stray_at_igloo()


    def move_to_resource(self, resource_type):
        if not self.target_resource and resource_type:
            # Randomly pick from the nearest resources.
            best_option = None
            if resource_type == "fish":
                resources = self.igloo.player.open_resources
            else:
                resources = data.resources
            for r in resources:
                if r.type == resource_type and r.quantity > 0:
                    dist = ((r.tile.x-self.x)**2 + (r.tile.y-self.y)**2)**.5
                    if not best_option:
                        best_option = (dist,r)
                    else:
                        if dist < best_option[0] + 6 and randint(0,1):
                            best_option = (dist,r)

            if best_option:
                self.target_resource = best_option[1]
            else:
                # No more resources of this type availible.
                return False

        if not self.target_resource: return False

        direction = self.find_next_tile_to_object(self.target_resource.tile)
        next_tile = data.map.tiles[(direction[0]+self.x, direction[1]+self.y)]

        if next_tile is self.target_resource.tile:
            if next_tile.resource.quantity > 0:
                self.gathering_from = next_tile
                self.counter = data.get_ticks()
                self.state = "gathering"
                self.direction = direction
                return None
            else:
                # Resources ran out here.
                self.target_resource = None
                return False
        else:
            return direction

def set_unit_base(cls):
    """
    Sets the base class for Snowballer and Worker to the given class.

    This is to mix in different behaviors for the server or clients.
    """
    for unit_class in [Snowballer, Worker]:
        unit_class.__bases__ = (cls,)
