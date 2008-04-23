"""OpenGL-wide constant types (not OpenGL.GL-specific"""
import ctypes
from OpenGL.constant import Constant

GL_FALSE = Constant( 'GL_FALSE', 0x0 )
GL_TRUE = Constant( 'GL_TRUE', 0x1 )
GL_BYTE = Constant( 'GL_BYTE', 0x1400 )
GL_UNSIGNED_BYTE = Constant( 'GL_UNSIGNED_BYTE', 0x1401 )
GL_SHORT = Constant( 'GL_SHORT', 0x1402 )
GL_UNSIGNED_SHORT = Constant( 'GL_UNSIGNED_SHORT', 0x1403 )
GL_INT = Constant( 'GL_INT', 0x1404 )
GL_UNSIGNED_INT = Constant( 'GL_UNSIGNED_INT', 0x1405 )
GL_FLOAT = Constant( 'GL_FLOAT', 0x1406 )
GL_DOUBLE = Constant( 'GL_DOUBLE', 0x140a )
GL_CHAR = str
GL_HALF_NV = Constant( 'GL_HALF_NV', 0x1401 )

# Basic OpenGL data-types as ctypes declarations...
GLvoid = None
GLboolean = ctypes.c_ubyte
GLenum = ctypes.c_uint

GLfloat = ctypes.c_float
GLdouble = ctypes.c_double

GLbyte = ctypes.c_byte
GLshort = ctypes.c_short
GLint = ctypes.c_int

GLsizei = ctypes.c_int

GLubyte = ctypes.c_ubyte
GLushort = ctypes.c_ushort
GLhandleARB = GLhandle = GLuint = ctypes.c_uint

GLchar = GLcharARB = ctypes.c_char

GLbitfield = ctypes.c_uint

GLclampd = ctypes.c_double
GLclampf = ctypes.c_float

# ptrdiff_t, actually...
GLsizeiptrARB = GLsizeiptr = GLsizei
GLintptrARB = GLintptr = GLint
size_t = ctypes.c_ulong

GLhalfNV = GLhalfARB = ctypes.c_ushort


ARRAY_TYPE_TO_CONSTANT = [
	('GLclampd', GL_DOUBLE),
	('GLclampf', GL_FLOAT),
	('GLfloat', GL_FLOAT),
	('GLdouble', GL_DOUBLE),
	('GLbyte', GL_BYTE),
	('GLshort', GL_SHORT),
	('GLint', GL_INT),
	('GLubyte', GL_UNSIGNED_BYTE),
	('GLushort', GL_UNSIGNED_SHORT),
	('GLuint', GL_UNSIGNED_INT),
	('GLenum', GL_UNSIGNED_INT),
]
