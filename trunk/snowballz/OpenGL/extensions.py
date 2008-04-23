"""Extension module support methods

This module provides the tools required to check whether
an extension is available
"""
AVAILABLE_GL_EXTENSIONS = []
AVAILABLE_GLU_EXTENSIONS = []

def hasGLExtension( specifier ):
	"""Given a string specifier, check for extension being available"""
	from OpenGL.GL import glGetString, GL_EXTENSIONS
	if not AVAILABLE_GL_EXTENSIONS:
		AVAILABLE_GL_EXTENSIONS[:] = glGetString( GL_EXTENSIONS ).split()
	return specifier.replace('.','_') in AVAILABLE_GL_EXTENSIONS

def hasGLUExtension( specifier ):
	"""Given a string specifier, check for extension being available"""
	from OpenGL.GLU import gluGetString, GLU_EXTENSIONS
	if not AVAILABLE_GLU_EXTENSIONS:
		AVAILABLE_GLU_EXTENSIONS[:] = gluGetString( GLU_EXTENSIONS )
	return specifier.replace('.','_') in AVAILABLE_GLU_EXTENSIONS
