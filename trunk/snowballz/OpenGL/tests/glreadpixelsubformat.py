import numpy
import PyQt4.Qt as qt

try:
    import OpenGL.GL  as GL
    import OpenGL.GLU as GLU
except ImportError:
    raise ImportError, "OpenGL must be installed to use these functionalities"


class MyGLWidget(qt.QGLWidget):
    def __init__(self, parent = None, crash = 0):
        qt.QGLWidget.__init__(self, parent)
        if crash:
            self._t = numpy.float64
        else:
            self._t = numpy.float32
        self.crash = crash
        self.generateData(512, 512)

    def generateData(self, xsize, ysize):
        self.xsize = xsize
        self.ysize = ysize
        self.vertices = numpy.zeros((xsize * ysize, 3), self._t)
        x = numpy.arange(xsize)
        y = numpy.arange(ysize)
        A=numpy.outer(x, numpy.ones(len(y), numpy.float32))
        B=numpy.outer(y, numpy.ones(len(x), numpy.float32))
        self.vertices[:,0]=A.flatten()
        self.vertices[:,1]=B.transpose().flatten()
        self.vertices[:,2]=range(xsize * ysize)
        self.vertexColors = numpy.zeros((xsize*ysize, 4), self._t)
        i = numpy.arange(len(self.vertices))
        self.vertexColors[:, 0] = (i & 255) / 255.
        self.vertexColors[:, 1] = ((i >> 8) & 255) / 255.
        self.vertexColors[:, 2] = ((i >> 16) & 255) / 255.
        self.vertexColors[:, 3] = 1.0

    def initializeGL(self):
        GL.glClearDepth(1.0)
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glShadeModel(GL.GL_FLAT)
        GL.glDisable(GL.GL_DITHER)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glDisable(GL.GL_CULL_FACE)

    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)


        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0., 512., 0., 512., -self.xsize*self.ysize, self.xsize*self.ysize)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        self.updateGL()


    def paintGL(self):
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        self.drawObject()
        color = GL.glReadPixelsub(0, 0, 1, 1, GL.GL_RGBA)
        if color.dtype == 'int8':
            print "WARNING: int8 received"

    def drawObject(self):
        GL.glVertexPointerf(self.vertices)
        if self.crash != 2:
            GL.glColorPointerf(self.vertexColors)
        else:
            GL.glColorPointerd(self.vertexColors)
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)
        GL.glDrawArrays(GL.GL_POINTS, 0, self.xsize*self.ysize)
        GL.glDisableClientState(GL.GL_COLOR_ARRAY)
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)

    def mousePressEvent(self, event):
        self.lastPos = qt.QPoint(event.pos())
        #get the color
        x = self.lastPos.x()
        y = self.lastPos.y()
        y = self.height()- y
        self.makeCurrent()
        color = GL.glReadPixelsub(x, y, 1, 1, GL.GL_RGBA)
        #workaround a PyOpenGL bug
        if color.dtype == 'int8':
            print "WARNING: int8 received"
            color = color.astype(numpy.uint8)
        else:
            print "received %s" % color.dtype
        print "Color = ", color

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "Usage:"
        print "python OpenGlTest.py 0 to get it going"
        print "python OpenGlTest.py 1 to get it crash"
        print "python OpenGlTest.py 2 to get it thru again using glColorPointerd"
        sys.exit(0)
    app = qt.QApplication(sys.argv)
    value = int(sys.argv[1])
    window = MyGLWidget(crash=value)
    window.show()
    app.exec_()


                
