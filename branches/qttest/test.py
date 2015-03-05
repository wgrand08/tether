import sys
from PyQt4 import QtGui, QtCore, uic

class TestApp(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
 
		self.ui = uic.loadUi('mytest.ui')
		self.ui.show()
 
if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	win = TestApp()
	sys.exit(app.exec_())
