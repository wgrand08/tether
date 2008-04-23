#! /usr/bin/env python
import unittest, pygame, pygame.display, time, traceback
try:
	from numpy import *
except ImportError, err:
	from Numeric import *
pygame.display.init()
from OpenGL.GL import *
from OpenGL import constants
from OpenGL.GLU import *
import ctypes


class Test( unittest.TestCase ):
	evaluator_ctrlpoints = [[[ -1.5, -1.5, 4.0], [-0.5, -1.5, 2.0], [0.5, -1.5,
		-1.0], [1.5, -1.5, 2.0]], [[-1.5, -0.5, 1.0], [-0.5, -0.5, 3.0], [0.5, -0.5,
		0.0], [1.5, -0.5, -1.0]], [[-1.5, 0.5, 4.0], [-0.5, 0.5, 0.0], [0.5, 0.5,
		3.0], [1.5, 0.5, 4.0]], [[-1.5, 1.5, -2.0], [-0.5, 1.5, -2.0], [0.5, 1.5,
		0.0], [1.5, 1.5, -1.0]]]
	def setUp( self ):
		"""Set up the operation"""
		self.screen = pygame.display.set_mode(
			(300,300),
			pygame.OPENGL | pygame.DOUBLEBUF,
		)
		
		pygame.display.set_caption('Testing system')
		pygame.key.set_repeat(500,30)
		glMatrixMode (GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(40.0, 300/300, 1.0, 20.0)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		gluLookAt(
			-2,0,3, # eyepoint
			0,0,0, # center-of-view
			0,1,0, # up-vector
		)
		glClearColor( 0,0,.25, 0 )
		glClear( GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT )
	def tearDown( self ):
		glFlush()
		pygame.display.flip()
		time.sleep( .25 )
		#raw_input( 'Okay? ' )
	def test_evaluator( self ):
		"""Test whether the evaluator functions work"""
		glDisable(GL_CULL_FACE)
		glEnable(GL_MAP2_VERTEX_3)
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_NORMALIZE)
		glMap2f(GL_MAP2_VERTEX_3, 0, 1, 0, 1, self.evaluator_ctrlpoints)
		glMapGrid2f(20, 0.0, 1.0, 20, 0.0, 1.0)
		glShadeModel(GL_FLAT)
		glEvalMesh2(GL_FILL, 0, 20, 0, 20)
		glTranslatef( 0,0.001, 0 )
		glEvalMesh2(GL_POINT, 0, 20, 0, 20)
	def test_nurbs_raw( self ):
		"""Test nurbs rendering using raw API calls"""
		from OpenGL.raw import GLU 
		knots = (constants.GLfloat* 8) ( 0,0,0,0,1,1,1,1 )
		ctlpoints = (constants.GLfloat*(3*4*4))( -3., -3., -3.,
			-3., -1., -3.,
			-3.,  1., -3.,
			-3.,  3., -3.,

		   -1., -3., -3.,
			-1., -1.,  3.,
			-1.,  1.,  3.,
			-1.,  3., -3.,

		    1., -3., -3.,
			 1., -1.,  3.,
			 1.,  1.,  3.,
			 1.,  3., -3.,

		    3., -3., -3.,
			 3., -1., -3.,
			 3.,  1., -3.,
			 3.,  3., -3. )
		theNurb = gluNewNurbsRenderer()
		GLU.gluBeginSurface(theNurb)
		GLU.gluNurbsSurface(
			theNurb, 
			8, ctypes.byref(knots), 8, ctypes.byref(knots),
			4 * 3, 3, ctypes.byref( ctlpoints ),
			4, 4, GL_MAP2_VERTEX_3
		)
		GLU.gluEndSurface(theNurb)
	def test_nurbs_raw_arrays( self ):
		"""Test nurbs rendering using raw API calls with arrays"""
		from OpenGL.raw import GLU 
		import numpy
		knots = numpy.array( ( 0,0,0,0,1,1,1,1 ), 'f' )
		ctlpoints = numpy.array( [[[-3., -3., -3.],
			[-3., -1., -3.],
			[-3.,  1., -3.],
			[-3.,  3., -3.]],

		   [[-1., -3., -3.],
			[-1., -1.,  3.],
			[-1.,  1.,  3.],
			[-1.,  3., -3.]],

		   [[ 1., -3., -3.],
			[ 1., -1.,  3.],
			[ 1.,  1.,  3.],
			[ 1.,  3., -3.]],

		   [[ 3., -3., -3.],
			[ 3., -1., -3.],
			[ 3.,  1., -3.],
			[ 3.,  3., -3.]]], 'f' )
		theNurb = GLU.gluNewNurbsRenderer()
		GLU.gluBeginSurface(theNurb)
		GLU.gluNurbsSurface(
			theNurb, 
			8, knots, 8, knots,
			4 * 3, 3, ctlpoints ,
			4, 4, GL_MAP2_VERTEX_3
		)
		GLU.gluEndSurface(theNurb)
	def test_nurbs( self ):
		"""Test nurbs rendering"""
		from OpenGL.raw import GLU 
		def buildControlPoints( ):
			ctlpoints = zeros( (4,4,3), 'd')
			for u in range( 4 ):
				for v in range( 4):
					ctlpoints[u][v][0] = 2.0*(u - 1.5)
					ctlpoints[u][v][1] = 2.0*(v - 1.5);
					if (u == 1 or u ==2) and (v == 1 or v == 2):
						ctlpoints[u][v][2] = 3.0;
					else:
						ctlpoints[u][v][2] = -3.0;
			return ctlpoints
		controlPoints = buildControlPoints()
		theNurb = GLU.gluNewNurbsRenderer()[0]
		#theNurb = gluNewNurbsRenderer();
		gluNurbsProperty(theNurb, GLU_SAMPLING_TOLERANCE, 25.0);
		gluNurbsProperty(theNurb, GLU_DISPLAY_MODE, GLU_FILL);
		knots= array ([0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0], "d")
		glPushMatrix();
		try:
			glRotatef(330.0, 1.,0.,0.);
			glScalef (0.5, 0.5, 0.5);

			gluBeginSurface(theNurb);
			try:
				gluNurbsSurface(
					theNurb,
					knots, knots,
					controlPoints,
					GL_MAP2_VERTEX_3
				);
			finally:
				gluEndSurface(theNurb);
		finally:
			glPopMatrix();
	def test_errors( self ):
		"""Test for error catching/checking"""
		try:
			glClear( GL_INVALID_VALUE )
		except Exception, err:
			assert err.err == 1281, ("""Expected invalid value (1281)""", err.err)
		else:
			raise RuntimeError( """No error on invalid glClear""" )
		try:
			glColorPointer(GL_INVALID_VALUE,GL_BYTE,0,None)
		except Exception, err:
			assert err.err == 1281, ("""Expected invalid value (1281)""", err.err)
			assert err.baseOperation, err.baseOperation
			assert err.pyArgs == [GL_INVALID_VALUE, GL_BYTE, 0, None], err.pyArgs
			assert err.cArgs == [GL_INVALID_VALUE, GL_BYTE, 0, None], err.cArgs
		else:
			raise RuntimeError( """No error on invalid glColorPointer""" )
		try:
			glBitmap(-1,-1,0,0,0,0,"")
		except Exception, err:
			assert err.err == 1281, ("""Expected invalid value (1281)""", err.err)
		else:
			raise RuntimeError( """No error on invalid glBitmap""" )
	def test_quadrics( self ):
		"""Test for rendering quadric objects"""
		quad = gluNewQuadric()
		glColor3f( 1,0, 0 )
		gluSphere( quad, 1.0, 16, 16 )
	def test_simple( self ):
		"""Test for simple vertex-based drawing"""
		glDisable( GL_LIGHTING )
		glBegin( GL_TRIANGLES )
		try:
			try:
				glVertex3f( 0.,1.,0. )
			except Exception, err:
				traceback.print_exc()
			glVertex3fv( [-1,0,0] )
			glVertex3dv( [1,0,0] )
			try:
				glVertex3dv( [1,0] )
			except ValueError, err:
				#Got expected value error (good)
				pass
			else:
				raise RuntimeError(
					"""Should have raised a value error on passing 2-element array to 3-element function!""",
				)
		finally:
			glEnd()
		a = glGenTextures( 1 )
		assert a
		b = glGenTextures( 2 )
		assert len(b) == 2
	def test_arbwindowpos( self ):
		"""Test the ARB window_pos extension will load if available"""
		from OpenGL.GL.ARB.window_pos import glWindowPos2dARB
		if glWindowPos2dARB:
			glWindowPos2dARB( 0.0, 3.0 )
	def test_getstring( self ):
		assert glGetString( GL_EXTENSIONS )
	def test_pointers( self ):
		"""Test that basic pointer functions work"""
		vertex = constants.GLdouble * 3
		vArray =  vertex * 2
		glVertexPointerd( [[2,3,4,5],[2,3,4,5]] )
		glVertexPointeri( ([2,3,4,5],[2,3,4,5]) )
		glVertexPointers( [[2,3,4,5],[2,3,4,5]] )
		glVertexPointerd( vArray( vertex(2,3,4),vertex(2,3,4) ) )
		myVector = vArray( vertex(2,3,4),vertex(2,3,4) )
		glVertexPointer(
			3,
			GL_DOUBLE,
			0,
			ctypes.cast( myVector, ctypes.POINTER(constants.GLdouble)) 
		)
			
		
		repr(glVertexPointerb( [[2,3],[4,5]] ))
		glVertexPointerf( [[2,3],[4,5]] )
		assert arrays.ArrayDatatype.dataPointer( None ) == None
		glVertexPointerf( None )
		
		glNormalPointerd( [[2,3,4],[2,3,4]] )
		glNormalPointerd( None )
	
		glTexCoordPointerd( [[2,3,4],[2,3,4]] )
		glTexCoordPointerd( None )
	
		glColorPointerd( [[2,3,4],[2,3,4]] )
		glColorPointerd( None )
	
		glEdgeFlagPointerb( [0,1,0,0,1,0] )
		glEdgeFlagPointerb( None )
	
		glIndexPointerd( [0,1,0,0,1,0] )
		glIndexPointerd( None )
		
		glColor4fv( [0,0,0,1] )
		
		# string data-types...
		import struct
		s = struct.pack( '>iiii', 2,3,4,5 ) * 2
		result = glVertexPointer( 4,GL_INT,0,s )
	TESS_TEST_SHAPE = [
			[191,   0],
			[ 191, 1480],
			[ 191, 1480],
			[ 401, 1480],
			[ 401, 1480],
			[401,   856],
			[401,   856],
			[1105,  856],
			[1105,  856],
			[1105, 1480],
			[1105, 1480],
			[1315, 1480],
			[1315, 1480],
			[1315,    0],
			[1315,    0],
			[1105,    0],
			[1105,    0],
			[1105,  699],
			[1105,  699],
			[401,   699],
			[401,   699],
			[401,     0],
			[401,     0],
			[191,     0],
			[191,     0],
			[191,     0],
		]
	def test_tess(self ):
		"""Test that tessellation works"""
		glDisable( GL_LIGHTING )
		glColor3f( 1,1,1 )
		glNormal3f( 0,0,1 )
		def begin( *args ):
			return glBegin( *args )
		def vertex( *args ):
			return glVertex3dv( *args )
		def end( *args ):
			return glEnd( *args )
		def combine( coords, vertex_data, weight):
			return coords
		tobj = gluNewTess()
		gluTessCallback(tobj, GLU_TESS_BEGIN, begin);
		gluTessCallback(tobj, GLU_TESS_VERTEX, vertex); 
		gluTessCallback(tobj, GLU_TESS_END, end); 
		gluTessCallback(tobj, GLU_TESS_COMBINE, combine); 
		gluTessBeginPolygon(tobj, None); 
		gluTessBeginContour(tobj);
		for (x,y) in self.TESS_TEST_SHAPE:
			vert = (x,y,0.0)
			gluTessVertex(tobj, vert, vert);
		gluTessEndContour(tobj); 
		gluTessEndPolygon(tobj);
	def test_texture( self ):
		"""Test texture (requires OpenGLContext and PIL)"""
		try:
			from OpenGLContext import texture
			import Image 
			from OpenGL.GLUT import glutSolidTeapot
		except ImportError, err:
			pass
		else:
			glEnable( GL_TEXTURE_2D )
			ourTexture = texture.Texture(
				Image.open( 'yingyang.png' )
			)
			ourTexture()
			
			glEnable( GL_LIGHTING )
			glEnable( GL_LIGHT0 )
			glBegin( GL_TRIANGLES )
			try:
				try:
					glTexCoord2f( .5, 1 )
					glVertex3f( 0.,1.,0. )
				except Exception, err:
					traceback.print_exc()
				glTexCoord2f( 0, 0 )
				glVertex3fv( [-1,0,0] )
				glTexCoord2f( 1, 0 )
				glVertex3dv( [1,0,0] )
				try:
					glVertex3dv( [1,0] )
				except ValueError, err:
					#Got expected value error (good)
					pass
				else:
					raise RuntimeError(
						"""Should have raised a value error on passing 2-element array to 3-element function!""",
					)
			finally:
				glEnd()
	def test_numpyConversion( self ):
		"""Test that we can run a numpy conversion from double to float for glColorArray"""
		import numpy
		a = numpy.arange( 0,1.2, .1, 'd' ).reshape( (-1,3 ))
		glEnableClientState(GL_VERTEX_ARRAY)
		glColorPointerf( a )
		glColorPointerd( a )


if __name__ == "__main__":
	unittest.main()

