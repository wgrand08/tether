#! /usr/bin/env python
"""Simple GLU Tess-object test w/out combine callback"""
from OpenGLContext import testingcontext
BaseContext, MainFunction = testingcontext.getInteractive()
from OpenGLContext.scenegraph import polygontessellator, vertex
from OpenGL.GL import *
from OpenGL.GLU import *
from Numeric import *


outline = array([
	[ 0, 0, 0],
	[ 1, 1, 0],
	[ -1, 1, 0],
], 'd')

class TestContext( BaseContext ):
	scale = 1.0
	def OnInit( self ):
		self.tess = polygontessellator.PolygonTessellator()
	def Render( self, mode = 0):
		BaseContext.Render( self, mode )
		self.renderCap( self.scale )
	def renderCap( self, scale = 1.0):
		"""The cap is generated with GLU tessellation routines...
		"""
		vertices = [
			vertex.Vertex( (x/scale,y/scale,z/scale) ) for (x,y,z) in outline
		]
		glColor3f( 1,0,0)
		glDisable( GL_LIGHTING) 
		for type, vertices in self.tess.tessellate( vertices, forceTriangles=0 ):
			print ' geometry type %s, %s vertices (GL_TRIANGLES=%s GL_TRIANGLE_FAN=%s GL_TRIANGLE_STRIP=%s)'%(
				type,
				len(vertices),
				GL_TRIANGLES, GL_TRIANGLE_FAN, GL_TRIANGLE_STRIP
			)
			glNormal3f( 0,0,1 )
			glBegin( type )
			for v in vertices:
				glVertex2dv( v.point[:2] )
			glEnd()

if __name__ == "__main__":
	MainFunction ( TestContext)
