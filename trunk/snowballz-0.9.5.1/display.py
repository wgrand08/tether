from __future__ import division
from OpenGL.GL import *
import pygame
from pygame.locals import *
import rabbyt

import textures
import data
import settings
import ctrl
import selectctrl


def draw(game, dt):
    """ Actually, this does a bit more than just draw... but all well.
        TODO: Seperate it out?"""

    rabbyt.set_time(pygame.time.get_ticks())

    vw, vh = data.view.scale_w, data.view.scale_h

    # Takes 2 mins for half a day (resources regen at mid-night).
    if data.get_ticks() > game.last_time_tick + 2*1000*60/44:
        game.last_time_tick = data.get_ticks()
        game.time += 1
        if game.time == 88:
            game.time = 0
            for r in data.resources:
                r.replenish()

        #data.map.check_win_lose()

        # unfreez penguins.
        if game.time == 44:
            for penguin in data.units:
                if penguin.warmth <= 0:
                    penguin.warmth = 4
                    penguin.state = "stray"

    # Unselect any penguins that should not be selected:
    for u in list(data.selected_units):
        if u.warmth < 5 or u.state in ["frozen", "entering", "inbuilding"]:
            data.selected_units.remove(u)
            u.selected = False



    # Actual drawing starts here! But there is some non drawing things as well!

    glClear(GL_COLOR_BUFFER_BIT)

    glScalef(data.view.zoom, data.view.zoom, 1)
    x, y = data.view.x, -data.view.y
    glEnable(GL_TEXTURE_2D)
    #game.snow.bind()
    #glColor4f(1,1,1,1)
    #glBegin(GL_QUADS)
    #glTexCoord2f(x/game.snow.width,y/game.snow.height)
    #glVertex2i(0,0)
    #glTexCoord2f((x+vw)/game.snow.width,y/game.snow.height)
    #glVertex2i(vw, 0)
    #glTexCoord2f((x+vw)/game.snow.width,(y+vh)/game.snow.height)
    #glVertex2i(vw, vh)
    #glTexCoord2f(x/game.snow.width,(y+vh)/game.snow.height)
    #glVertex2i(0, vh)
    #glEnd()

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, vw, vh, 0, -50, 50)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    x, y = data.view.x, data.view.y
    glTranslatef(-x,-y,0)

    # Draw terrain
    tx,ty = (x//32, x//32+vw//32+3), (y//32, y//32+vh//32+5)
    game.snow.bind()
    game.snow_terrain.draw(tx,ty)
    textures.Texture.bound_texture_id = None
    textures.Texture.get("data/ice.png").bind()
    game.ice_terrain.draw(tx,ty)


    data.map.draw()

    #t = pygame.time.get_ticks()
    rabbyt.scheduler.pump(pygame.time.get_ticks())
    #print pygame.time.get_ticks() - t

    #rabbyt.VertexStore.bound_vertex_store = None

    ticks = pygame.time.get_ticks()
    #rabbyt.behavior_set.run(ticks, dt)
    #for bs in data.behavior_sets.range(data.view.x, data.view.y,
            #data.view.x+data.view.w, data.view.y+data.view.h):
        #bs.run(ticks, dt)

    #data.rs.generate_indexes()
    #data.rs.do_vertex_calls()
    #data.resource_behavior_set.run(ticks, dt)
    #rs = rabbyt.RenderSet()
    #rs.sprites = list(data.resources)
    #rs.do_vertex_calls()
    #sorted_sprites = list(data.resources)
    view = data.view
    sets = data.sprite_sets.range(view.x, view.y, view.x+view.scale_w,
                view.y+view.scale_h)
    for s in sets:
        data.draw_buffer.extend(s)
    data.draw_buffer.sort()

    ### Draw imprents.
    if int(settings.get_option("snowballdetail")) >= 2:
        data.snowballimprents.draw(dt)
        data.snowball_ice_imprents.draw(dt)
    if data.footprints_settings:
        #print len(data.footimprents.sprites)
        data.footimprents.draw(dt)

    textures.Texture.bound_texture_id = None

    # Move and draw units.
    for u in data.units:
        u.move()
        u.animate(dt)
        cx,cy = u.penguin_sprite.xy
        if cx+64 > data.view.x and cx < data.view.x+vw+64\
                and cy+64 > data.view.y and cy < data.view.y+vh+64:
            u.draw()
        else:
            #FIXME: This doesn't work!!!!! :(
            continue

            # Check to see if unit is an enimy in owned region.
            pos = (u.x,u.y)
            if data.map.tiles[pos].region.player == data.player and\
                    u.igloo.player != data.player and\
                    u.warmth > 4:
                cam_x = data.view.x + game.vw/2
                cam_y = data.view.y + game.vh/2

                offset = u.offset
                if u.moving:
                    offset -= 32
                tx = float(u.x - cam_x) + u.direction[0]*offset
                ty = float(u.y - cam_y) + u.direction[1]*offset

                screen_h = game.vh/2.
                screen_w = game.vw/2.

                pos_x = pos_y = 0

                if ty and abs(tx/ty) < screen_w/screen_h:
                    if ty > 0:
                        pos_y = vh-20
                        pos_x = screen_h*tx/ty + screen_w
                    else:
                        pos_y = 0
                        pos_x = screen_h*tx/-ty + screen_w

                elif tx and abs(ty/tx) < screen_h/screen_w:
                    if tx > 0:
                        pos_x = vw-20
                        pos_y = screen_w*ty/tx #+ screen_h
                    else:
                        pos_x = 0
                        pos_y = screen_w*ty/-tx #+ screen_h

                #FIXME: Take into acount map height too!
                map_size = 2*data.map.size[0]*32

                scale = 1 - (abs(tx)+abs(ty)) / map_size
                data.draw_buffer.append(data.Rendered(game.warningtexture,
                        pos_x, 22+pos_y, z=6, scale=scale))

    # Draw buildings.
    draw_buildings = set()
    for b in data.buildings:
        if b.x*32+256 > data.view.x and b.x*32 < data.view.x+vw\
                and b.y*32+256 > data.view.y and b.y*32 < data.view.y+vh+246:
            b.draw()
            draw_buildings.add(b)

    for d in data.draw_buffer:
        d.render()
    data.draw_buffer = []

    # Draw smoke.
    if settings.get_option("smoke") == "1":
        for b in draw_buildings:
            b.draw_smoke()

    if int(settings.get_option("snowballdetail")) == 3:
        t_r = set()
        for p in data.particles:
            if not p.run(dt/1000.):
                t_r.add(p)
        data.particles.difference_update(t_r)


    # Draw snowballs.
    for s in list(data.snowballs):
        if s.move():
            data.snowballs.discard(s)
        else:
            # Draw snowball.
            s.sprite.render()
            s.shadow_sprite.render()


    data.moveimprents.draw(dt)
    data.runmoveimprents.draw(dt)
    data.gathermoveimprents.draw(dt)


    # Draw select box.
    if data.select_box_start:
        glDisable(GL_TEXTURE_2D)
        glPushMatrix()
        glColor4f(0, 0.3, 0.3, 0.3)

        x,y = data.select_box_start

        x2, y2 = data.select_box_end

        w = x2 - x
        h = y2 - y

        glTranslatef(x, y, 0)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(w, 0)
        glVertex2f(w, h)
        glVertex2f(0, h)
        glEnd()

        glColor4f(1,1,1,1)
        glPopMatrix()
        glEnable(GL_TEXTURE_2D)


    glColor4f(1,1,1,1)
    # Avalanches
    #t_r = set()
    #for a in data.avalanches:
        #a.run()
        #if not a.flakes:
            #t_r.add(a)
    #data.avalanches.difference_update(t_r)

    darkness = float(abs(game.time - 44)*2 - 20)
    darkness = max(0, darkness)
    if darkness:
        darkness /= 255
    darkness = min(1, darkness)

    # Draw snow falling down.
    if darkness > 0.05:
        data.snowflakes.run(True)
    else:
        data.snowflakes.run(False)


    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, data.view.w, 0, data.view.h, -50, 50)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


    glDisable(GL_TEXTURE_2D)

    # Draw night overlay.
    if settings.get_option("daynight") == "1":
        glColor4f(0, 0, 0, darkness)
        data.draw_box(0,0,data.view.w,data.view.h)
        glColor4f(1,1,1,1)


    if ctrl.chatting:
        glColor4f(0,0,0,0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(vw, 0)
        glVertex2f(vw, 60)
        glVertex2f(0, 60)
        glEnd()

        if ctrl.chatting_help:
            data.chat_font.render(10, 30, ctrl.chatting_help, (0.65,0.65,0.65))

        data.chat_font.render(10, 00, ctrl.chatting_msg+"_")

    glEnable(GL_TEXTURE_2D)

    # Draw chat.
    data.messages.drawall()


    # Draw select control
    selectctrl.update()
    if selectctrl._display:
        selectctrl.draw()


    # Draw minimap.
    if data.draw_minimap:
        data.minimap.draw()

    glColor4f(1,1,1,1)

    #game.brpanel.render(vw-128, 0)

    if settings.get_option("cursor") == "1":
        pos = pygame.mouse.get_pos()
        game.mouse_cursor.render(pos[0], data.view.h-64-pos[1], invert_y=False)

    # Fade out loading screen untill all the way fadded out
    if game.loading_screen_alpha > 0:
        glEnable(GL_TEXTURE_2D)
        game.loading_screen_alpha -= 0.05
        glColor4f(0,0,0,game.loading_screen_alpha)
        data.draw_box(0,0,vw,vh)
        glColor4f(1,1,1,game.loading_screen_alpha)
        loading = textures.Texture.get("data/loading.png").sub(0,0,640,480)
        glPushMatrix()
        x = (game.vw-640)/2
        y = (game.vh-480)/2
        glTranslatef(x,game.vh-480-y,0)
        loading.render(invert_y=False)
        glPopMatrix()

    pygame.display.flip()

