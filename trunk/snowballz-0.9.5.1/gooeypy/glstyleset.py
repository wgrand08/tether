from __future__ import division
import util
import pygame
from cellulose import *
from OpenGL.GL import *
from styleset import StyleSet as SDLStyleSet
from texture import Texture


class Style:
    def __init__(self, styleset, values):
        self.styleset = styleset
        self.widget = styleset.widget
        self.values = values
        self.setup(values)

    def setup(self, values):
        pass

    def render(self):
        pass


class Opacity(Style):
    def setup(self, values):
        if len(values) == 1:
            values = values[0]
        self.values = int(values)
        # TODO: actually set alpha (or maybe do in draw func?).
        self.styleset.applied_styles["opacity"] = self


class BgColor(Style):
    def setup(self, values):
        self.color = None
        if values[0] != "none":
            if type(values[0]) == str:
                color = values[0][1:-1].split(",")
                color = [int(c) for c in color]
            else:
                color = values[0]
            self.color = [c/255.0 for c in color]

        self.styleset.applied_styles["bgcolor"] = self

    def render(self):
        if not self.color: return
        color = self.color
        o = 1
        if len(color) < 4:
            if self.styleset["opacity"]:
                o = self.styleset["opacity"].values/255
                color.append(o)
            else:
                color.append(1)

        y = 0
        if self.widget.container:
            y += self.widget.container.offset_y

        glColor4f(*color)
        glBegin(GL_QUADS)
        glVertex2f(0, y)
        glVertex2f(self.widget.width, y)
        glVertex2f(self.widget.width, y-self.widget.height)
        glVertex2f(0, y-self.widget.height)
        glEnd()
        glColor4f(1,1,1,o)


class Border(Style):
    def setup(self, values):
        color = values[1][1:-1].split(",")
        self.color = [int(c) for c in color]
        self.width = int(values[0])
        self.styleset.applied_styles["border"] = self

    def render(self):
        pass


class BgImage(Style):
    def setup(self, values):
        if values[0] != "none":
            self.surf = util.app.get_image(values[0])
            self.im = Texture(self.surf)
            self.sub = self.im.sub(0,0,self.surf.get_width(), self.surf.get_height())
            self.style = None
            if len(values) > 1:
                self.style = values[1]
        else:
            self.style = "none"
        self.styleset.applied_styles["bgimage"] = self

        if values[0] != "none":
            # Here we slice up the texture into required sections.
            w = self.w = self.surf.get_width()//2
            h = self.h = self.surf.get_height()//2
            self.tl = self.im.sub(0, 0, w, h)
            self.bl = self.im.sub(0, self.surf.get_height()-h, w, h)
            self.tr = self.im.sub(self.surf.get_width()-w, 0, w, h)
            self.br = self.im.sub(self.surf.get_width()-w, self.surf.get_height()-h, w, h)
            self.l = self.im.sub(0, h, w, 2)
            self.r = self.im.sub(self.surf.get_width()-w, h, w, 2)
            self.t = self.im.sub(w, 0, 4, h)
            self.b = self.im.sub(w, self.surf.get_height()-h, 2, h)
            c = self.surf.get_at((w+1, h+1))
            self.c = [i/255 for i in c]


    def render(self):
        if self.style == "none": return
        if not self.style or self.style == "no-repeat":
            vw = self.surf.get_width()
            vh = self.surf.get_height()
            self.draw_bg(vw, vh)
        elif self.style == "repeat-y":
            vw = self.surf.get_width()
            vh = self.widget.height
            self.draw_bg(vw, vh, im=self.sub)
        elif self.style == "repeat-x":
            vw = self.widget.width
            vh = self.surf.get_height()
            self.draw_bg(vw, vh, im=self.sub)
        elif self.style == "repeat":
            vw = self.widget.width
            vh = self.widget.height
            self.draw_bg(vw, vh, im=self.sub)

        elif self.style == "stretch":
            sy = self.widget.height/self.surf.get_height()
            sx = self.widget.width/self.surf.get_width()
            glPushMatrix()
            glTranslatef(0, -self.im.height, 0)
            glScalef(sx,sy,1)
            self.im.render()
            glPopMatrix()

        elif self.style == "slice":

            # Draw center.
            glColor4f(*self.c)
            glBegin(GL_QUADS)
            glVertex2f(0, -3)
            glVertex2f(self.widget.width, -3)
            glVertex2f(self.widget.width, -self.widget.height+6)
            glVertex2f(0, -self.widget.height+6)
            glEnd()
            glColor4f(1,1,1, 1)

            # Draw the top and bottom.
            self.draw_bg(self.widget.width, self.t.height,
                    y=self.widget.height-self.b.height,
                    im=self.t, repeat=True)
            self.draw_bg(self.widget.width, self.b.height,
                    im=self.b, y=-1, repeat=True)

            # Left and right
            self.draw_bg(self.l.width, self.widget.height, im=self.l, repeat=True)
            self.draw_bg(self.r.width, self.widget.height,
                    x=self.widget.width-self.r.width, im=self.r, repeat=True)

            # Corners.
            self.draw_bg(self.tl.width, self.tl.height, y=self.widget.height-self.h, im=self.tl, repeat=True)
            self.draw_bg(self.tr.width, self.tr.height,
                    x=self.widget.width-self.w, im=self.tr, repeat=True,
                    y=self.widget.height-self.h)
            self.draw_bg(self.bl.width, self.bl.height, y=-1, im=self.bl, repeat=True)
            self.draw_bg(self.br.width, self.br.height, x=self.widget.width-self.w,
                    y=-1, im=self.br, repeat=True)


    def draw_bg(self, vw, vh, x=0, y=0, im=None, repeat=False):
        # vw and vh are the width and height of the area you want to cover.
        if not im: im = self.im
        vh = -vh
        y = -y

        # We find the location on the texture that we need to get from.
        if repeat:
            w, h = float(im.texture.width), float(im.texture.height)
            su, sv = im.x/w, im.y/h
            eu, ev = su + im.w/w, sv + im.h/h
        else:
            su = sv = 0
            eu = vw/im.width
            ev = vh/im.height

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, im.texture_id)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        if repeat:
            # If it's a sub texture, we need to set the wrap to repeat.
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # Draw it.
        glBegin(GL_QUADS)
        glTexCoord2f(su, ev)
        glVertex2f(x, y)

        glTexCoord2f(eu, ev)
        glVertex2f(x+vw, y)

        glTexCoord2f(eu, sv)
        glVertex2f(x+vw, y+vh)

        glTexCoord2f(su, sv)
        glVertex2f(x, y+vh)
        glEnd()
        glDisable(GL_TEXTURE_2D)



class Color(Style):
    def setup(self, values):
        if len(values) != 3:
            color = values[0][1:-1].split(",")
            self.values = [int(c) for c in color]
        else: self.values = values

        self.styleset.applied_styles["color"] = self


class Padding(Style):
    def setup(self, values):
        padding = {}
        if len(values) == 1:
            top = right = bottom = left = values[0]
        elif len(values) == 2:
            top = bottom = values[0]
            left = right = values[1]
        elif len(values) == 4:
            top, right, bottom, left = values

        padding["top"] = int(top)
        padding["right"] = int(right)
        padding["bottom"] = int(bottom)
        padding["left"] = int(left)

        for k in ("top", "left", "right", "bottom"):
            key = "padding-"+k
            if not self.styleset.applied_styles[key]:
                self.styleset.applied_styles[key] = padding[k]



class Effect(Style):
    def setup(self, values):
        if len(values) == 1 and values[0] != "none":
            values.append("10")
        self.styleset.applied_styles["effect"] = values



class StyleSet(SDLStyleSet):
    styles = {
        "opacity":Opacity,
        "bgcolor":BgColor,
        "border":Border,
        "bgimage":BgImage,
        "color":Color,
        "padding":Padding,
        "effect":Effect,
    }

    def draw(self):
        """ Draws the widget based on it's styling. """
        if self.parent:
            self.parent.draw()

        if self["opacity"]:
            o = self["opacity"].values/255
            glColor4f(1,1,1,o)

        for s in self.applied_styles.values():
            if hasattr(s, "render"):
                s.render()
        glColor4f(1,1,1,1)

    def surf(self):
        raise ValueError("GL widgets don't use surface!")
    surf = ComputedCellDescriptor(surf)


    def __getitem__(self, v):
        r = None
        if self.applied_styles.has_key(v):
            r = self.applied_styles[v]
        if not r and self.parent:
            r = self.parent[v]
        if hasattr(r, "value"): r = r.value
        return r

    def __setitem__(self, k, v):
        #self.applied_styles[k] = v
        self.apply(k, v)

    def apply(self, option, values):
        option = option.replace("_", "-")
        o = option.replace("-", "_")
        if type(values) == str or type(values) == int:
            if type(values) == str:
                values = values.split(" ")
            else: values = [values]
        if o in self.styles:
            self.styles[o](self, values)
        else:
            self.generic(option, values)

    def generic(self, n, v):
        if type(v) == list:
            if len(v) == 1:
                v = v[0]
                v = str(v)
                # isdigit returns False if v is a negative number. FIX?
                if v.isdigit(): v = int(v)
        self.applied_styles[n] = v

    #def effect(self, values):
        #if len(values) == 1 and values[0] != "none":
            #values.append("10")
        #self.applied_styles["effect"] = values