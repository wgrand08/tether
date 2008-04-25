from __future__ import division
import pygame
from pygame.locals import *
import sys, os
import data
import unit
import selectctrl


nums = {K_1:1, K_2:2, K_3:3, K_4:4, K_5:5, K_6:6, K_7:7, K_8:8, K_9:9}
groups = {1:set(), 2:set(), 3:set(), 4:set(), 5:set(), 6:set(), 7:set(),
        8:set(), 9:set(), }


def get_scale_mouse_pos():
    p = list(pygame.mouse.get_pos())
    p[0] /= data.view.zoom
    p[1] /= data.view.zoom
    return p


def handle_mouse_click(button):
    """ Handles all mouse click events from Pygame. """
    pos = get_scale_mouse_pos()
    if not data.draw_minimap:
        if button == 1:
            start_select(pos)
        if button == 2:
            set_job(pos, run_mode=True)
        if button == 3:
            set_job(pos)


def handle_mouse_release(button):
    """ Handles all mouse release events from Pygame. """
    if data.select_box_start:
        end_select()



def start_select((x,y)):
    #data.select_box_start = data.canvas_to_map(x,y)
    data.select_box_start = data.view.x + x, data.view.y + y

def end_select():
    mods = pygame.key.get_mods()
    ctrl_pressed = False
    shift_pressed = False
    # Shift overrules Ctrl
    if (KMOD_LSHIFT | KMOD_RSHIFT) & mods:
        shift_pressed = True
    elif (KMOD_LCTRL | KMOD_RCTRL) & mods:
        ctrl_pressed = True
    # Forget previous selection if neither of the group selection modifiers
    # are pressed.
    if not (shift_pressed or ctrl_pressed):
        for u in data.selected_units:
            u.selected = False
        data.selected_units = set()

    if not data.select_box_end:
        data.select_box_end = data.select_box_start

    start_x, start_y = data.select_box_start
    end_x, end_y = data.select_box_end

    if end_x < start_x:
        start_x, end_x = end_x, start_x
    if end_y < start_y:
        start_y, end_y = end_y, start_y

    for u in data.units:
        cx,cy = u.penguin_sprite.xy
        if cx+32 > start_x and cx < end_x and cy+32 > start_y and cy < end_y:
            if u.igloo.player == data.player:
                if ctrl_pressed and u in data.selected_units:
                    data.selected_units.remove(u)
                    u.selected = False
                else:
                    data.selected_units.add(u)
                    u.selected = True

    data.select_box_start = data.select_box_end = None




def set_job((x,y), run_mode=False):
    if data.selected_units:
        pos = data.canvas_to_map(x,y)
        if data.THIS_IS_SERVER:
            for u in data.selected_units:
                u.set_job(pos, run_mode=run_mode)
        else:
            import networking
            m = networking.MSetJob(pos, run_mode,
                    [u.unit_id for u in data.selected_units])
            networking.send(m)

        worker_selected = False
        for u in data.selected_units:
            if isinstance(u, unit.Worker):
                worker_selected = True; break
        x += data.view.x-16
        y += data.view.y-23
        if run_mode or data.map.tiles[pos].building:
            data.runmoveimprents.add(x,y, data.player.color)
        elif data.map.tiles[pos].resource and\
                data.map.tiles[pos].resource.gatherable and worker_selected:
            data.gathermoveimprents.add(x,y, data.player.color)
        else:
            data.moveimprents.add(x,y, data.player.color)


def disban_units():
    if not data.THIS_IS_SERVER:
        import networking
        m = networking.MDisbanUnits([u.unit_id for u in data.selected_units])
        networking.send(m)
    for u in data.selected_units:
            u.disban()
    data.selected_units = set()


def scroll_screen((x,y), dt):
    speed = 50
    speed = (dt/speed)*32
    speed = speed*(2-data.view.zoom)
    if x < 10:
        data.view.x -= speed
    elif x > data.view.w-10:
        data.view.x += speed
    if y < 10:
        data.view.y -= speed
    elif y > data.view.h - 10:
        data.view.y += speed

    if not chatting:
        k = pygame.key.get_pressed()
        if k[K_RIGHT] or k[K_d]:
            data.view.x += speed
        if k[K_LEFT] or k[K_a]:
            data.view.x -= speed
        if k[K_UP] or k[K_w]:
            data.view.y -= speed
        if k[K_DOWN] or k[K_s]:
            data.view.y += speed

    bind_screen()

def look_at(x, y):
    """
    Center the screen on the given x,y coordinates.
    """
    data.view.x, data.view.y = x - data.view.scale_w//2, y - data.view.scale_h//2
    bind_screen()

def bind_screen():
    """
    Make sure that the screen is within the map bounds.
    """
    if data.view.zoom == 1:
    #if data.view.scale_w < data.map.size[0]*32:
        data.view.x = max(0, min(data.map.size[0]*32-data.view.scale_w, data.view.x))
    #if data.view.scale_h < data.map.size[1]*32:
        data.view.y = max(0, min(data.map.size[1]*32-data.view.scale_h, data.view.y))


holding = False
chatting = False


chatting_msg = ""
chatting_help = ""
last_back_press = 0
last_chat_name = ""
last_received_from = ""


def handle_chatting(event):
    global chatting, chatting_msg, last_back_press, chatting_help, last_chat_name
    if event.key == K_RETURN:
        if chatting_msg:
            data.player.send_msg(chatting_msg)
            if chatting_msg[0] is ">":
                last_chat_name = chatting_msg.split()[0]
            chatting_msg = ""
        chatting_help = ""
        chatting = False
    elif event.key == K_ESCAPE:
        chatting_msg = ""
        chatting = False
        chatting_help = ""
    elif event.key == K_BACKSPACE:
        # prevent repeating.
        last_back_press = data.get_ticks()
        chatting_msg = chatting_msg[:-1]
    elif event.key == K_TAB:
        # TAB completeion.
        if not chatting_msg or len(chatting_msg.split()) > 1:
            return

        curw = chatting_msg

        ps = set()

        if curw[0] == "/":
            options = "/say".split()
            ps = set()
            for o in options:
                if curw in o:
                    ps.add(o)

        if curw[0] == ">":
            options = data.players.values()
            ps = set()
            options.remove(data.player)
            for o in options:
                o = ">"+o.name
                if curw in o:
                    ps.add(o)

        if len(ps) == 1:
            chatting_msg = chatting_msg[:-len(curw)]+ps.pop()+" "
            chatting_help = ""
        elif len(ps) > 1:
            curw = os.path.commonprefix(ps)
            chatting_msg = chatting_msg[:-len(curw)]+curw
            chatting_help = "  ".join(ps)
    else:
        c = str(event.unicode)
        chatting_msg = chatting_msg+c



def handle_events(dt):
    """ Handle input events from pygame. """
    global holding, chatting, chatting_msg

    k = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit(0)

        elif event.type == KEYDOWN:
            if not chatting:
                if event.key == K_ESCAPE:
                    return False
                elif event.key == K_SPACE:
                    data.draw_minimap = True
                elif event.key == K_o:
                    disban_units()
                elif event.key == K_c:
                    data.messages.clear()
                elif event.key == K_COMMA:
                    if last_chat_name:
                        chatting = True
                        chatting_msg = last_chat_name+" "
                elif event.key == K_PERIOD:
                    if last_received_from:
                        chatting = True
                        chatting_msg = ">"+last_received_from+" "
                elif event.key == K_RETURN:
                    chatting = True



                # Group control
                mods = pygame.key.get_mods()
                if data.selected_units and (KMOD_LCTRL | KMOD_RCTRL) & mods:
                    if event.key in nums.keys():
                        group_num = nums[event.key]

                        # Clear group we are going to assign to.
                        for u in groups[group_num]:
                            u.group = None

                        for u in data.selected_units:
                            # Remove unit from any existing group it belongs to.
                            if u.group:
                                groups[u.group].remove(u)

                            u.group = group_num

                        groups[group_num] = data.selected_units.copy()

                # Selecting groups
                elif event.key in nums.keys():
                    group = groups[nums[event.key]]
                    if group:
                        for u in data.selected_units:
                            u.selected = False
                        data.selected_units = group.copy()

                        for u in data.selected_units:
                            u.selected = True
                        look_at(u.x*32, u.y*32)

            else:
                handle_chatting(event)

        elif event.type == KEYUP:
            if event.key == K_SPACE:
                data.draw_minimap = False

        elif event.type == MOUSEBUTTONDOWN:
            if not selectctrl.in_range(get_scale_mouse_pos()):
                handle_mouse_click(event.button)
                holding = True
        elif event.type == MOUSEBUTTONUP:
            if selectctrl.in_range(pygame.mouse.get_pos()) and event.button == 1:
                selectctrl.click(pygame.mouse.get_pos())

            handle_mouse_release(event.button)
            holding = False

    if chatting:
        if data.get_ticks()-last_back_press > 300:
            if k[K_BACKSPACE]:
                chatting_msg = chatting_msg[:-1]

    if k[K_PAGEUP] or k[K_PAGEDOWN]:
        cx = (data.view.x+data.view.scale_w/2)
        cy = (data.view.y+data.view.scale_h/2)
        if k[K_PAGEUP]:
            if data.view.zoom != 1:
                data.view.zoom = min(data.view.zoom+0.02, 1)
        elif k[K_PAGEDOWN]:
            if data.view.zoom != 0.1:
                data.view.zoom = max(data.view.zoom-0.02, 0.1)
        look_at(cx,cy)





    scroll_screen(pygame.mouse.get_pos(), dt)

    if data.draw_minimap and holding:
        data.view.x, data.view.y = data.minimap.pos_to_mappos(*pygame.mouse.get_pos())
        bind_screen()

    if data.select_box_start:
        x,y = get_scale_mouse_pos()
        data.select_box_end = x + data.view.x, y + data.view.y

    return True
