"""
The rabbyt.vertexarrays module is deprecated and will be removed in a future
version of rabbyt.
"""

__credits__ = (
"""
Copyright (C) 2007  Matthew Marshall

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
""")

__author__ = "Matthew Marshall <matthew@matthewmarshall.org>"

from warnings import warn

warn("""
The rabbyt.vertexarrays module is deprecated and will be removed in a future
version of rabbyt.
""", stacklevel=2)

cdef extern from "stdlib.h":
    ctypedef unsigned int size_t
    cdef void *malloc(size_t size)
    cdef void free(void *ptr)
    cdef void *realloc(void *ptr, size_t size)

cdef extern from "include_gl.h":
    ctypedef float GLfloat
    ctypedef float GLclampf
    ctypedef unsigned int GLenum
    ctypedef unsigned int GLbitfield
    ctypedef int GLint
    ctypedef unsigned int GLuint
    ctypedef int GLsizei
    ctypedef double GLdouble
    ctypedef double GLclampd
    ctypedef void GLvoid

    cdef void glPushClientAttrib(GLbitfield mask)
    cdef void glPopClientAttrib()
    cdef void glEnableClientState(GLenum array)
    cdef void glDisableClientState(GLenum array)

    cdef void glVertexPointer(GLint size, GLenum type, GLsizei stride,
            GLvoid *pointer)
    cdef void glTexCoordPointer(GLint size, GLenum type, GLsizei stride,
            GLvoid *pointer)
    cdef void glColorPointer(GLint size, GLenum type, GLsizei stride,
            GLvoid *pointer)

    cdef void glDrawArrays(GLenum mode, GLint first, GLsizei count)
    cdef void glDrawElements(GLenum mode, GLsizei count, GLenum type,
            GLvoid *indices)

    cdef void glEnable(GLenum cap)
    cdef void glBindTexture(GLenum target, GLuint texture)

    cdef int GL_SHORT
    cdef int GL_INT
    cdef int GL_FLOAT
    cdef int GL_UNSIGNED_BYTE
    cdef int GL_UNSIGNED_INT

    cdef int GL_COLOR_ARRAY
    cdef int GL_INDEX_ARRAY
    cdef int GL_TEXTURE_COORD_ARRAY
    cdef int GL_VERTEX_ARRAY

    cdef int GL_CLIENT_VERTEX_ARRAY_BIT
    cdef int GL_QUADS
    cdef int GL_QUAD_STRIP
    cdef int GL_TRIANGLES
    cdef int GL_TRIANGLE_FAN
    cdef int GL_TRIANGLE_STRIP
    cdef int GL_LINES
    cdef int GL_LINE_STRIP
    cdef int GL_LINE_LOOP
    cdef int GL_POINTS

    cdef int GL_TEXTURE_2D

    cdef void glInterleavedArrays( GLenum format, GLsizei stride,
                                           GLvoid *pointer )


_mode_mapping = {
    GL_QUADS:"QUADS",
    GL_QUAD_STRIP:"QUAD_STRIP",
    GL_TRIANGLES:"TRIANGLES",
    GL_TRIANGLE_STRIP:"TRIANGLE_STRIP",
    GL_TRIANGLE_FAN:"TRIANGLE_FAN",
    GL_LINES:"LINES",
    GL_LINE_STRIP:"LINE_STRIP",
    GL_LINE_LOOP:"LINE_LOOP",
    GL_POINTS:"POINTS",
}
for key in list(_mode_mapping):
    _mode_mapping[_mode_mapping[key]] = key


def push_array_attributes():
    glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)

def pop_array_attributes():
    glPopClientAttrib()


#def set_vertex_array():
    #glEnableClientState(GL_VERTEX_ARRAY)
    #glVertexPointer(2, GL_FLOAT, sizeof(vertexinfo_s), self._vertex_info)
    #glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    #glTexCoordPointer(2, GL_FLOAT, sizeof(vertexinfo_s),
            #&self._vertex_info[0].u)
    #if self._use_colors:
        #glEnableClientState(GL_COLOR_ARRAY)
        #glColorPointer(4, GL_UNSIGNED_BYTE, sizeof(vertexinfo_s),
                #&self._vertex_info[0].red)
    #else:
        #glDisableClientState(GL_COLOR_ARRAY)


cdef struct vertexinfo_s:
    float x,y,u,v
    unsigned char red,green,blue,alpha

cdef class VertexArray:
    """
    ``VertexArray(mode="QUADS", use_colors=True)``

    OpenGL vertex arrays provide a way to push a large amount of data to the
    video hardware, very fast.  ``VertexArray`` provides an easy to use class
    to take advantage of this speed.

    ``VertexArray`` supports both item access and assignment using
    ``VertexInfo`` objects.  For example, this would work as expected:

        .. sourcecode:: python

            vertex_array[0].x += 1

    You can also assign using tuples, just like as documented in the append
    method:

        .. sourcecode:: python

            vertex_array[0] = (x, y, u, v, red, green, blue, alpha)
    """
    cdef vertexinfo_s * _vertex_info
    cdef int _len
    cdef int _allocated_size
    cdef int _use_colors

    cdef object _texture_id

    cdef int _mode

    def __init__(self, mode="QUADS", use_colors=True):
        self.mode = mode
        self._use_colors = use_colors
        self._len = 0
        self._allocated_size = 4
        self._vertex_info = <vertexinfo_s*>malloc(sizeof(vertexinfo_s)*4)
        self.texture_id = None

    def __dealloc__(self):
        if self._vertex_info is not NULL:
            free(self._vertex_info)

    property use_colors:
        """
        If ``True``, (the default,) the color data in the vertex array will be
        used. Otherwise, the previous color will be used for all vertexes.
        (such as set by ``rabbyt.set_gl_color()``.)
        """
        def __get__(self):
            return bool(self._use_colors)
        def __set__(self, c):
            self._use_colors = bool(c)

    property mode:
        """
        The default primitive drawing mode.

        Valid modes are "QUADS", "QUAD_STRIP", "TRIANGLES", "TRIANGLE_STRIP",
        "TRIANGLE_FAN", "LINES", "LINE_STRIP", "LINE_LOOP", or "POINTS".  These
        corrispond directly to the OpenGL privitive drawing modes.  (In fact,
        you can also use the OpenGL enumerations instead of the strings, if you
        prefer.)
        """
        def __get__(self):
            return self._mode
        def __set__(self, mode):
            if isinstance(mode, basestring):
                mode = _mode_mapping[mode]
            if mode not in _mode_mapping:
                raise ValueError("must be a valid mode")
            self._mode = mode

    property texture_id:
        """
        The texture used when ``render()`` is called.

        If ``None`` (the default) texturing isn't touched.  This is useful
        if you want to bind the texture yourself.

        If ``0``, texturing is disabled.

        If it is a positive integer (other than 0,) the given texture will be
        bound when rendering.
        """
        def __get__(self):
            return self._texture_id
        def __set__(self, t):
            self._texture_id = t

    def __getitem__(self, int index):
        if index >= self._len or index < 0:
            raise IndexError(str(index))
        return VertexInfo(self, index)

    def __setitem__(self, int index, item):
        if index >= self._len or index < 0:
            raise IndexError(str(index))
        if len(item) > 8:
            raise ValueError(
                    "Vertex information should be at most a length of 8")
        try:
            self._vertex_info[index].x = item[0]
            self._vertex_info[index].y = item[1]
            self._vertex_info[index].u = item[2]
            self._vertex_info[index].v = item[3]
            self._vertex_info[index].red = _to255(item[4])
            self._vertex_info[index].green = _to255(item[5])
            self._vertex_info[index].blue = _to255(item[6])
            self._vertex_info[index].alpha = _to255(item[7])
        except IndexError:
            pass

    cdef _grow(self, int additional_size, exact):
        cdef int new_size, i
        self._len = self._len + additional_size
        if exact:
            new_size = self._len
        else:
            new_size = self._allocated_size
            while self._len > new_size:
                new_size = new_size * 2
        if new_size > self._allocated_size:
            self._vertex_info = <vertexinfo_s*>realloc(self._vertex_info,
                    sizeof(vertexinfo_s)*new_size)
            # Give the data some defaults
            for i from self._allocated_size <= i < new_size:
                self._vertex_info[i].x = 0
                self._vertex_info[i].y = 0
                self._vertex_info[i].u = 0
                self._vertex_info[i].v = 0
                self._vertex_info[i].red = 255
                self._vertex_info[i].green = 255
                self._vertex_info[i].blue = 255
                self._vertex_info[i].alpha = 255
            self._allocated_size = new_size

    def set_size(self, int size):
        """
        ``set_size(size)``

        Sets the size explicitly.

        This is an alternative to using ``append`` and ``extend``.  (It should
        be a little faster.)
        """
        if size > self._len:
            self._grow(size-self._len, True)
        elif size < self._len:
            self._len = size
            self._allocated_size = size
            self._vertex_info = <vertexinfo_s*>realloc(self._vertex_info,
                    sizeof(vertexinfo_s)*size)

    def append(self, vertex):
        """
        ``append(vertex)``

        Appends a vertex to the array.

        vertex should be a tuple of the form
        ``(x,y,u,v,red,green,blue,alpha)``. (You can also make the tuple
        shorter; any missing values will be left at the default.)

        Note that ``vertex`` doesn't need to be a tuple, but anything
        supporting item access.  This includes ``VertexInfo`` instances.
        """
        self._grow(1, False)
        try:
            self[self._len - 1] = (0,0,0,0, 1,1,1,1)
            self[self._len - 1] = vertex
        except:
            # If there was an error assigning the item, we don't want to leave
            # dead vertex behind.
            self._len = self._len - 1
            raise

    def extend(self, vertexes):
        """
        ``extend(vertexes)``

        Iterates over vertexes, calling ``append(vertex)`` on each one.
        """
        for v in vertexes:
            self.append(v)

    def __len__(self):
        return self._len

    def enable_arrays(self):
        """
        ``enable_arrays()``

        Calls the ``glEnableClientState`` and ``gl*Pointer`` functions to set
        up this ``VertexArray`` for usage.  This is automatically called when
        you call ``render()``.

        If you use vertex arrays with PyOpenGL elsewhere in your program, you
        should always wrap this method in
        ``glPushClientAttrib``\/``glPopClientAttrib``.
        """
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, sizeof(vertexinfo_s), self._vertex_info)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glTexCoordPointer(2, GL_FLOAT, sizeof(vertexinfo_s),
                &self._vertex_info[0].u)
        if self._use_colors:
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointer(4, GL_UNSIGNED_BYTE, sizeof(vertexinfo_s),
                    &self._vertex_info[0].red)
        else:
            glDisableClientState(GL_COLOR_ARRAY)

    def render(self, start=0, end=None):
        """
        ``render([start,] [end])``

        Renders the array!

        ``start`` and ``end`` can be specified to only render part of the
        array.
        """
        if self._len == 0:
            return
        if self.texture_id is not None:
            if self.texture_id:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, self.texture_id)
            else:
                glDisable(GL_TEXTURE_2D)
        if end is None:
            end = self._len
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        try:
            self.enable_arrays()
            glDrawArrays(self._mode, start, end-start)
        finally:
            glPopClientAttrib()


cdef class VertexArrayIndexes:
    """
    ``VertexArrayIndexes([sequence])``

    Provides a way to list by indexes the vertexes to be rendered.

    This is useful if you have multiple primitives sharing a vertex, and you
    want to either save memory or make it easier to modify the data.
    """
    cdef unsigned int * _indexes
    cdef unsigned int _len
    cdef unsigned int _allocated_size
    cdef unsigned int _mode

    def __init__(self, iterable=()):
        self._allocated_size = 0
        self._len = 0
        self._mode = 0

        self._grow(len(iterable), True)
        for i, index in enumerate(iterable):
            self._indexes[i] = index

    property mode:
        """
        If non zero, this mode will override the ``VertexArray``'s mode when
        render is called.
        """
        def __get__(self):
            return self._mode
        def __set__(self, mode):
            if not mode:
                mode = 0
            elif isinstance(mode, basestring):
                mode = _mode_mapping[mode]
            elif mode not in _mode_mapping:
                raise ValueError("must be a valid mode")
            self._mode = mode

    cdef _grow(self, int additional_size, exact):
        self._len = self._len + additional_size
        cdef int new_size, i
        if exact:
            new_size = self._len
        else:
            new_size = self._allocated_size
            if new_size == 0:
                new_size = 16
            while self._len > new_size:
                new_size = new_size * 2
        if new_size > self._allocated_size:
            self._indexes = <unsigned int *>realloc(self._indexes,
                    sizeof(unsigned int)*new_size)
            for i from self._allocated_size <= i < new_size:
                self._indexes[i] = 0
            self._allocated_size = new_size

    def append(self, unsigned int index):
        """
        ``append(index)``

        Appends an index to be drawn.
        """
        self._grow(1, False)
        self._indexes[self._len-1] = index

    def extend(self, indexes):
        for i in indexes:
            self.append(i)

    def __getitem__(self, unsigned int i):
        if i >= self._len:
            raise IndexError
        return self._indexes[i]
    def __setitem__(self, unsigned int i, unsigned int index):
        if i >= self._len:
            raise IndexError
        self._indexes[i] = index

    def render(self, VertexArray vertex_array not None, int start=0, end=None,
                enable_arrays=True, safety_check=True):
        """
        ``render(vertex_array, [start, end, enable_arrays, safety_check])``

        This renders the vertexes in ``vertex_array``, which should be an
        instance of ``VertexArray``.

        ``start`` and ``end`` define which vertexes to render, and default to
        rendering all of them.

        If ``enable_arrays`` is ``True``, (the default,)
        ``vertex_array.enable_arrays()`` will be called automatically, along
        with pushing and popping the client state.  If you are rendering many
        ``VertexArrayIndexes`` off of the same ``VertexArray``, you might see a
        small speedup by only calling ``enable_arrays()`` on the
        ``VertexArray`` once.

        If ``safety_check`` is ``True``, (the default,) the ``safety_check()``
        method will be called with the length of the ``VertexArray``.  This
        prevents segmentation faults, but adds a little overhead.  You can set
        this to ``False`` once your code is debugged.  (Just remember to look
        if you ever get a segfault!)
        """
        if end is None:
            end = self._len

        if end <= start:
            return

        if safety_check:
            self.safety_check(len(vertex_array))

        if self.mode:
            mode = self.mode
        else:
            mode = vertex_array.mode

        if enable_arrays:
            glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        try:
            if enable_arrays:
                vertex_array.enable_arrays()
            glDrawElements(mode, end-start, GL_UNSIGNED_INT,
                    &self._indexes[start])
        finally:
            if enable_arrays:
                glPopClientAttrib()

    def safety_check(self, int max_index):
        """
        ``safety_check(max_index)``

        Loops through all of the indexes and raises ``ValueError`` if one is
        greater than or equal to ``max_index``.
        """
        cdef int i
        for i from 0 <= i < self._len:
            if self._indexes[i] >= max_index:
                raise ValueError("Index out of bounds")


cdef unsigned char _to255(float value):
    if value > 1.0:
        value = 1.0
    elif value < 0.0:
        value = 0.0
    return <unsigned char>(value * 255)

cdef class VertexInfo:
    """
    Provides an interface to a single vertex in a ``VertexArray`` object.

    You probably won't ever want to instance this class yourself.  Instead,
    use "``vertex_array[index]``\".

    There are a number of properties for modifing the vertex data:

        ``x``, ``y``, ``u``, ``v``, ``red``, ``green``, ``blue``, ``alpha``

    You can also use these shortcuts to read/write multiple values at a time:

        ``xy``, ``uv``, ``rgb``, ``rgba``

    For example::

        vertex_array[index].x += 5
        vertex_array[index].rgb = 1.0, 0.0, 0.0

    And just in case if it's not obvious, ``u`` and ``v`` are the texture
    coordinates.
    """
    cdef VertexArray _parent
    cdef unsigned int _index

    def __init__(self, VertexArray parent, unsigned int index):
        self._parent = parent
        self._index = index

    def check_index(self):
        """
        check_index()

        Checks to make sure that the stored index is valid.  ``IndexError`` is
        raised if it isn't.
        """
        if self._parent is None:
            raise RuntimeError("Accessing VertexInfo property without parent.")
        if self._index >= self._parent._len:
            raise IndexError

    property index:
        def __get__(self):
            return self._index

    property xy:
        def __get__(self):
            return (self.x, self.y)
        def __set__(self, xy):
            self.x, self.y = xy

    property uv:
        def __get__(self):
            return (self.u, self.v)
        def __set__(self, uv):
            self.u, self.v = uv

    property rgb:
        def __get__(self):
            return (self.red, self.green, self.blue)
        def __set__(self, rgb):
            self.red, self.green, self.blue = rgb

    property rgba:
        def __get__(self):
            return (self.red, self.green, self.blue, self.alpha)
        def __set__(self, rgba):
            self.red, self.green, self.blue, self.alpha = rgba

    property x:
        def __get__(self):
            self.check_index()
            return self._parent._vertex_info[self._index].x
        def __set__(self, float x):
            self.check_index()
            self._parent._vertex_info[self._index].x = x

    property y:
        def __get__(self):
            self.check_index()
            return self._parent._vertex_info[self._index].y
        def __set__(self, float y):
            self.check_index()
            self._parent._vertex_info[self._index].y = y

    property u:
        def __get__(self):
            self.check_index()
            return self._parent._vertex_info[self._index].u
        def __set__(self, float u):
            self.check_index()
            self._parent._vertex_info[self._index].u = u

    property v:
        def __get__(self):
            self.check_index()
            return self._parent._vertex_info[self._index].v
        def __set__(self, float v):
            self.check_index()
            self._parent._vertex_info[self._index].v = v

    property red:
        def __get__(self):
            self.check_index()
            return self._parent._vertex_info[self._index].red/255.0
        def __set__(self, float red):
            self.check_index()
            self._parent._vertex_info[self._index].red = _to255(red)

    property green:
        def __get__(self):
            self.check_index()
            return self._parent._vertex_info[self._index].green/255.0
        def __set__(self, float green):
            self.check_index()
            self._parent._vertex_info[self._index].green = _to255(green)

    property blue:
        def __get__(self):
            self.check_index()
            return self._parent._vertex_info[self._index].blue/255.0
        def __set__(self, float blue):
            self.check_index()
            self._parent._vertex_info[self._index].blue = _to255(blue)

    property alpha:
        def __get__(self):
            self.check_index()
            return self._parent._vertex_info[self._index].alpha/255.0
        def __set__(self, float alpha):
            self.check_index()
            self._parent._vertex_info[self._index].alpha = _to255(alpha)

    def __getitem__(self, int index):
        name = "x y u v red green blue alpha".split()[index]
        return getattr(self, name)

    def __setitem__(self, int index, float value):
        name = "x y u v red green blue alpha".split()[index]
        setattr(self, name, value)

    def __len__(self):
        return 8

__docs_all__ = ('VertexArray VertexInfo VertexArrayIndexes').split()
