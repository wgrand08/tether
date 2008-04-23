"""Exceptional cases that need some extra wrapping"""
from OpenGL.platform import GL,GLU,createBaseFunction
from OpenGL import arrays, error
from OpenGL.raw import GL as simple
from OpenGL.raw.GL import constants
from OpenGL.raw.GL import annotations
import OpenGL
import ctypes

__all__ = [
	'glBegin', 
	'glCallLists', 
	'glColor', 
	#'glColorTableParameterfv', 
	'glDeleteTextures', 
	'glEdgeFlagv', 
	'glEnd', 
	'glGenTextures', 
	'glIndexdv', 
	'glIndexfv', 
	'glIndexsv',
	'glIndexubv', 
	'glMap1', 
	'glMap1d', 
	'glMap1f',
	'glMap2',
	'glMap2d',
	'glMap2f',
	'glMaterial', 
	'glRasterPos', 
	'glRectfv', 
	'glRectiv', 
	'glRectsv', 
	'glTexGenfv', 
	'glTexParameter', 
	'glVertex', 
]

glRasterPosDispatch = {
	2: annotations.glRasterPos2dv,
	3: annotations.glRasterPos3dv,
	4: annotations.glRasterPos4dv,
}

if OpenGL.ERROR_CHECKING:
	def glBegin( mode ):
		"""Begin GL geometry-definition mode, disable automatic error checking"""
		error.onBegin( )
		return simple.glBegin( mode )
	def glEnd( ):
		"""Finish GL geometry-definition mode, re-enable automatic error checking"""
		error.onEnd( )
		return simple.glEnd( )
else:
	glBegin = simple.glBegin
	glEnd = simple.glEnd


def glDeleteTextures( array ):
	"""Delete specified set of textures"""
	ptr = arrays.GLuintArray.asArray( array )
	size = arrays.GLuintArray.arraySize( ptr )
	return simple.glDeleteTextures( size, ptr )

def glMap2( target, u1, u2, v1, v2, points, baseFunction, arrayType = arrays.GLfloatArray):
##	import pdb
##	pdb.set_trace()
	ptr = arrayType.asArray( points )
	uorder,vorder,vstride = arrayType.dimensions( ptr )
	ustride = vstride*vorder
	return baseFunction(
		target, 
		u1, u2, 
		ustride, uorder, 
		v1, v2, 
		vstride, vorder, 
		ptr
	)
def glMap2f( target, u1, u2, v1, v2, points ):
	"""glMap2f(target, u1, u2, v1, v2, points[][][]) -> None
	
	This is a completely non-standard signature which doesn't allow for most 
	of the funky uses with strides and the like, but it has been like this for
	a very long time...
	"""
	return glMap2( target, u1, u2, v1, v2, points, simple.glMap2f, arrays.GLfloatArray )
def glMap2d( target, u1, u2, v1, v2, points ):
	"""glMap2d(target, u1, u2, v1, v2, points[][][]) -> None
	
	This is a completely non-standard signature which doesn't allow for most 
	of the funky uses with strides and the like, but it has been like this for
	a very long time...
	"""
	return glMap2( target, u1, u2, v1, v2, points, simple.glMap2d, arrays.GLdoubleArray )
def glMap1(target,u1,u2,points, baseFunction,arrayType):
	ptr = arrayType.asArray( points )
	dims = arrayType.dimensions( ptr )
	uorder = dims[0]
	ustride = dims[1]
	return baseFunction( target, u1,u2,ustride,uorder, ptr )
def glMap1d( target,u1,u2,points):
	"""glMap1d(target, u1, u2, points[][][]) -> None
	
	This is a completely non-standard signature which doesn't allow for most 
	of the funky uses with strides and the like, but it has been like this for
	a very long time...
	"""
	return glMap1( target, u1,u2,points, simple.glMap1d, arrays.GLdoubleArray )
def glMap1f( target,u1,u2,points):
	"""glMap1f(target, u1, u2, points[][][]) -> None
	
	This is a completely non-standard signature which doesn't allow for most 
	of the funky uses with strides and the like, but it has been like this for
	a very long time...
	"""
	return glMap1( target, u1,u2,points, simple.glMap1f, arrays.GLfloatArray )


def glRasterPos( *args ):
	"""Choose glRasterPosX based on number of args"""
	if len(args) == 1:
		# v form...
		args = args[0]
	return glRasterPosDispatch[ len(args) ]( args )

glVertexDispatch = {
	2: annotations.glVertex2dv,
	3: annotations.glVertex3dv,
	4: annotations.glVertex4dv,
}
def glVertex( *args ):
	"""Choose glVertexX based on number of args"""
	if len(args) == 1:
		# v form...
		args = args[0]
	return glVertexDispatch[ len(args) ]( args )

def glCallLists( lists ):
	"""glCallLists( str( lists ) or lists[] ) -> None 
	
	Restricted version of glCallLists, takes a string or a GLuint compatible
	array data-type and passes into the base function.
	"""
	if isinstance( lists, str ):
		return simple.glCallLists(
			len(lists),
			constants.GL_UNSIGNED_BYTE,
			ctypes.c_void_p(arrays.GLubyteArray.dataPointer( lists )),
		)
	ptr = arrays.GLuintArray.asArray( lists )
	size = arrays.GLuintArray.arraySize( ptr )
	return simple.glCallLists( 
		size, 
		constants.GL_UNSIGNED_INT, 
		ctypes.c_void_p( arrays.GLuintArray.dataPointer(ptr))
	)

def glTexParameter( target, pname, parameter ):
	"""Set a texture parameter, choose underlying call based on pname and parameter"""
	if isinstance( parameter, float ):
		return simple.glTexParameterf( target, pname, parameter )
	elif isinstance( parameter, int ):
		return simple.glTexParameteri( target, pname, parameter )
	else:
		return simple.glTexParameterfv( target, pname, parameter )

def glGenTextures( count, textures=None ):
	"""Generate count new texture names"""
	if count <= 0:
		raise ValueError( """Can't generate 0 or fewer textures""" )
	elif count == 1:
		# this traditionally returned a single int/long, so we'll continue to
		# do so, even though it would be easier not to bother.
		textures = simple.GLuint( 0 )
		annotations.glGenTextures( count, textures)
		return textures.value
	else:
		textures = arrays.GLuintArray.zeros( (count,))
		annotations.glGenTextures( count, textures)
		return textures

def glMaterial( faces, constant, *args ):
	"""glMaterial -- convenience function to dispatch on argument type
	
	If passed a single argument in args, calls:
		glMaterialfv( faces, constant, args[0] )
	else calls:
		glMaterialf( faces, constant, *args )
	"""
	if len(args) == 1:
		return annotations.glMaterialfv( faces, constant, args[0] )
	else:
		try:
			return annotations.glMaterialf( faces, constant, *args )
		except Exception, err:
			print 'Args:', args 
			raise

glColorDispatch = {
	3: annotations.glColor3dv,
	4: annotations.glColor4dv,
}

def glColor( *args ):
	"""glColor*f* -- convenience function to dispatch on argument type

	dispatches to glColor3f, glColor2f, glColor4f, glColor3f, glColor2f, glColor4f
	depending on the arguments passed...
	"""
	arglen = len(args)
	if arglen == 1:
		arg = args[0]
		function = glColorDispatch[arrays.GLfloatArray.arraySize( arg )]
		return function( arg )
	elif arglen == 3:
		return simple.glColor3d( *args )
	elif arglen == 4:
		return simple.glColor4d( *args )
	else:
		raise ValueError( """Don't know how to handle arguments: %s"""%(args,))


# Rectagle coordinates,
glRectfv = arrays.setInputArraySizeType(
		arrays.setInputArraySizeType(
		simple.glRectfv,
		2,
		arrays.GLfloatArray,
		'v1',
	),
	2,
	arrays.GLfloatArray,
	'v2',
)
glRectiv = arrays.setInputArraySizeType(
	arrays.setInputArraySizeType(
		simple.glRectiv,
		2,
		arrays.GLintArray,
		'v1',
	),
	2,
	arrays.GLintArray,
	'v2',
)
glRectsv = arrays.setInputArraySizeType(
	arrays.setInputArraySizeType(
		simple.glRectsv,
		2,
		arrays.GLshortArray,
		'v1',
	),
	2,
	arrays.GLshortArray,
	'v2',
)


glIndexsv = arrays.setInputArraySizeType(
	simple.glIndexsv,
	1,
	arrays.GLshortArray,
	'c',
)
glIndexdv = arrays.setInputArraySizeType(
	simple.glIndexdv,
	1,
	arrays.GLdoubleArray,
	'c',
)
glIndexfv = arrays.setInputArraySizeType(
	simple.glIndexfv,
	1,
	arrays.GLfloatArray,
	'c',
)
glIndexubv = arrays.setInputArraySizeType(
	simple.glIndexubv,
	1,
	arrays.GLbyteArray,
	'c',
)
glEdgeFlagv = arrays.setInputArraySizeType(
	simple.glEdgeFlagv,
	1,
	arrays.GLubyteArray,
	'flag',
)
glTexGenfv = arrays.setInputArraySizeType(
	simple.glTexGenfv,
	None,
	arrays.GLfloatArray,
	'params',
)


#glMap2f
#glMap2d
#glMap1f
#glMap1d
#glPixelMapusv
#glTexGenfv
#glLightfv
#glFeedbackBuffer
#glDrawRangeElements
#glSelectBuffer
#glAreTexturesResident
#glPixelMapfv
#glTexGeniv
#glClipPlane
#glTexParameterfv
#glTexParameteriv
#glReadPixels
#glConvolutionParameterfv
#glPolygonStipple
#glFogiv
#glTexEnviv
#glRectdv
#glMaterialiv
#glColorTable
#glColorTableParameteriv
#glIndexiv
#glLightModeliv
#glDrawElements
#glConvolutionFilter1D
#glCallLists
