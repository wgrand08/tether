import pygame
from OpenGL.GL import *
import math, os
#import rabbyt

class Texture:
    bound_texture_id = None
    cache = {}
    @classmethod
    def get(cls, image_name, *params, **kwargs):
        if cls.cache.has_key(image_name):
            return cls.cache[image_name]
        else:
            tex = cls(image_name, *params, **kwargs)
            cls.cache[image_name] = tex
            return tex

    disp_lists = {}
    @classmethod
    def gen_disp_list(cls, definition):
        if definition in cls.disp_lists:
            return cls.disp_lists[definition]
        else:
            listid = glGenLists(1)
            cls.disp_lists[definition] = listid
            glNewList(listid, GL_COMPILE)
            glBegin(GL_QUADS)
            for v in definition:
                glTexCoord2f(*v[0])
                glVertex2i(*v[1])
            glEnd()
            glEndList()
            return listid

    texture_id = None
    def __init__(self, image, scale_format="nearest", internal_format=GL_RGBA):
        if isinstance(image, str):
            image = os.path.join(*image.split("/"))
            self.filename = image
            image = pygame.image.load(image)
        else:
            self.filename = repr(image)
        w, h = image.get_width(), image.get_height()

        self.scale_format = scale_format

        # We need to make sure the texture size is always a power of 2.
        tw = int(2 ** math.ceil(math.log(w, 2)))
        th = int(2 ** math.ceil(math.log(h, 2)))

        if w != tw or h != th:
            w,h = tw,th
            s = pygame.Surface((w,h))
            s.blit(image, (0,h-image.get_height()))
        else:
            s = image
        self.width = w
        self.height = h

        data = pygame.image.tostring(s, 'RGBA', 1)
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glPixelStorei(GL_UNPACK_ROW_LENGTH, 0)
        try:
            glTexImage2D(GL_TEXTURE_2D, 0, internal_format, w, h,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        except:
            print "Error: Could not load image data!"
        if scale_format == "nearest":
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        elif scale_format == "linear":
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        self._render_disp_list = None

        #self.context = rabbyt.RenderContext()
        #self.context.texture_id = self.texture_id

    def __repr__(self):
        return '<Texture %rx%r %r>'%(self.width, self.height,
            self.filename)

    def __del__(self):
        try:
            if self.texture_id is None: return
            try:
                glDeleteTextures(self.texture_id)
                self.texture_id = None
            except NameError:
                # glDeleteTextures has been gobbled
                pass
        except TypeError: pass

    def bind(self):
        #if Texture.bound_texture_id is not self.texture_id:
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        Texture.bound_texture_id = self.texture_id

    def get_render_disp_list(self, invert_y=True):
        if invert_y:
            definition = (((0,1), (0,0)),
                    ((1,1), (self.width, 0)),
                    ((1,0), (self.width, self.height)),
                    ((0,0), (0, self.height)))
        else:
            definition = (((0,0), (0,0)),
                    ((1,0), (self.width, 0)),
                    ((1,1), (self.width, self.height)),
                    ((0,1), (0, self.height)))
        return Texture.gen_disp_list(definition)

    def render(self, x=0, y=0, mode=GL_MODULATE, invert_y=True):
        glEnable(GL_TEXTURE_2D)
        self.bind()
        glTranslatef(x,y,0)
        glCallList(self.get_render_disp_list(invert_y))
        glTranslatef(-x,-y,0)
        glDisable(GL_TEXTURE_2D)

    def sub(self, x, y, w, h):
        return SubTexture(self, x, y, w, h)

    def get_shape_pos(self):
        return ((0,0),
                (self.width, 0),
                (self.width, self.height),
                (0, self.height))

    def get_shape_tex(self, invert_y=False):
        if invert_y:
            return  ((0,1),
                    (1,1),
                    (1,0),
                    (0,0))
        else:
            return  ((0,0),
                    (1,0),
                    (1,1),
                    (0,1))


class SubTexture(Texture):
    def __init__(self, texture, x, y, w, h):
        self.__texture = texture            # don't collect the parent!
        #self.context = texture.context
        self.filename = texture.filename
        self.x, self.y = x, y
        self.width, self.height = self.w, self.h = w, h
        self.texture_id = texture.texture_id
        self._render_disp_list = None

    def __repr__(self):
        return '<Texture %rx%r %r>'%(self.w, self.h,
            self.filename)

    def get_render_disp_list(self, invert_y=False):

        w, h = float(self.__texture.width), float(self.__texture.height)
        su, sv = self.x/w, self.y/h
        eu, ev = su + self.w/w, sv + self.h/h
        if invert_y:
            sv, ev = ev, sv
        definition = (((su,sv), (0,0)),
                ((eu,sv), (self.w, 0)),
                ((eu,ev), (self.w, self.h)),
                ((su,ev), (0, self.h)))
        return Texture.gen_disp_list(definition)

    def get_shape_tex(self, invert_y=False):
        w, h = float(self.__texture.width), float(self.__texture.height)
        su, sv = self.x/w, self.y/h
        eu, ev = su + self.w/w, sv + self.h/h
        if invert_y:
            sv, ev = ev, sv
        return ((su,sv),
                (eu,sv),
                (eu,ev),
                (su,ev))

    def __del__(self):
        pass
