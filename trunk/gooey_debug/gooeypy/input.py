import pygame
import util
from const import *

from cellulose import *


class Input(util.widgets.Widget):
    """
    Input([value, [max_length, [disallowed_chars]]]) - Input widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Creates an HTML like input field.

    Arguments
    ---------
    value
        The initial value of the input (defaults to ""). Note that due to the
        nature of the value, you cannot link to it (but you can from it). If
        you really want to link it's value you can do so it _value, but it may
        not always work like you expect!

    max_length
        The maximum number of character that can be put into the Input.

    disallowed_chars
        A list of characters that are disallowed to enter.
    """

    _value = util.ReplaceableCellDescriptor()
    cur_pos = util.ReplaceableCellDescriptor()
    max_length = util.ReplaceableCellDescriptor()

    def __init__(self, value="", max_length=None, disallowed_chars=[], **params):
        util.widgets.Widget.__init__(self, **params)
        self._value = ''
        self.cur_pos = 0
        self.max_length = max_length
        self.value = value
        self.disallowed_chars = disallowed_chars
        self.last_press = {K_BACKSPACE:0, K_LEFT:0, K_RIGHT:0, K_DELETE:0}


    def font(self):
        """
        Input.font -> pygame.Font
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        The font that this input is using.
        """
        f = util.app.get_font(self.style_option["font-family"], self.style_option["font-size"])
        if self.style_option["font-weight"] == "bold":
            f.set_bold(True)
        return f
    font = ComputedCellDescriptor(font)

    def set_value(self,v):
        if v == None: v = ''
        v = str(v)
        if self.max_length and len(v) > self.max_length:
            v = v[0:self.max_length-1]
        self._value = v
        if self.cur_pos-1 > len(v):
            #print self.cur_pos-1, len(v)
            self.cur_pos = len(v)
        self.send(CHANGE)
    value = property(lambda self: self._value, set_value)

    def size(self):
        s,_ = self.font.size("e")
        num = self.style_option["width"]/s
        return self.font.size("e"*num)
    size = ComputedCellDescriptor(size)

    def width(self):
        w = self.size[0] + self.style_option["padding-left"]+\
                self.style_option["padding-right"]
        return util.widgets.Widget.width.function(self, w)
    width = ComputedCellDescriptor(width)

    def height(self):
        h = self.size[1] + self.style_option["padding-top"]+\
                self.style_option["padding-bottom"]
        return util.widgets.Widget.height.function(self, h)
    height = ComputedCellDescriptor(height)

    def font_clip_rect(self):
        vx = max(self.font.size(self.value)[0] - self.size[0], 0)
        return pygame.Rect((vx, 0), self.size)
    font_clip_rect = ComputedCellDescriptor(font_clip_rect)

    def font_x(self):
        x,_ = self.pos
        return x + self.style_option["padding-left"]
    font_x = ComputedCellDescriptor(font_x)

    def font_y(self):
        _,y = self.pos
        return y + self.style_option["padding-top"]
    font_y = ComputedCellDescriptor(font_y)

    def draw_widget(self):
        util.blit(self.font.render(self.value, self.style_option["antialias"],
                self.style_option["color"]),
                (self.font_x,self.font_y),
                clip_rect=self.font_clip_rect)

        if self.focused:
            w,h = self.font.size(self.value[0:self.cur_pos])
            r = pygame.Surface((2,self.size[1]))
            r.fill(self.style_option["color"])
            x = min(w, self.size[0])
            util.blit(r, (self.font_x+x, self.font_y))

    def repetitive_events(self):
        # Key repeating. Better way to do this?
        k = pygame.key.get_pressed()
        if k[K_BACKSPACE] and util.get_ticks()-self.last_press[K_BACKSPACE] > 300:
            self.value = self.value[:self.cur_pos-1] + self.value[self.cur_pos:]
            self.cur_pos -= 1
        elif k[K_DELETE] and util.get_ticks()-self.last_press[K_DELETE] > 300:
            if len(self.value) > self.cur_pos:
                self.value = self.value[:self.cur_pos] + self.value[self.cur_pos+1:]
        elif k[K_LEFT] and util.get_ticks()-self.last_press[K_LEFT] > 300:
            if self.cur_pos > 0: self.cur_pos -= 1
        elif k[K_RIGHT] and util.get_ticks()-self.last_press[K_RIGHT] > 300:
            if self.cur_pos < len(self.value): self.cur_pos += 1



    def event(self,e):
        if e.type == KEYDOWN:
            if e.key == K_BACKSPACE:
                if self.cur_pos:
                    self.value = self.value[:self.cur_pos-1] + self.value[self.cur_pos:]
                    self.cur_pos -= 1
                    self.last_press[K_BACKSPACE] = util.get_ticks()
            elif e.key == K_DELETE:
                if len(self.value) > self.cur_pos:
                    self.value = self.value[:self.cur_pos] + self.value[self.cur_pos+1:]
                self.last_press[K_DELETE] = util.get_ticks()
            elif e.key == K_HOME: 
                self.cur_pos = 0
            elif e.key == K_END:
                self.cur_pos = len(self.value)
            elif e.key == K_LEFT:
                if self.cur_pos > 0: self.cur_pos -= 1
                self.last_press[K_LEFT] = util.get_ticks()
            elif e.key == K_RIGHT:
                if self.cur_pos < len(self.value): self.cur_pos += 1
                self.last_press[K_RIGHT] = util.get_ticks()
            elif e.key == K_ESCAPE: pass
            elif e.key == K_RETURN:
                self.next()
            else:
                if self.max_length:
                    if len(self.value) == self.max_length:
                        return
                c = str(e.unicode)
                #c = (e.unicode).encode('latin-1')
                if c and c not in self.disallowed_chars:
                    self.value = self.value[:self.cur_pos] + c + self.value[self.cur_pos:]
                    self.cur_pos += 1