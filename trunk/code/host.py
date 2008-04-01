#!/usr/bin/python2.4

"""Copyright 2007:
    Isaac Carroll, Kevin Clement, Jon Handy, David Carroll, Daniel Carroll

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

import hostgvars
import socket
import threading
import pickle
import Queue


#useful example located at:
# http://www.devshed.com/c/a/Python/Basic-Threading-in-Python/1/
class moonHost(threading.Thread):
	#def __init__ ( self, channel, details ):
		#threading.Thread.__init__ ( self )

	def run(self):
		print"start runhost"
		while True:
			client = clientPool.get()
			if client != None:
				print"Recieved connection: ", client [1] [0]
				for x in xrange (10):
					print client [0].recv (1024)
				client [0].close()
				print"Closed connection: ", client [1] [0]

"""clientPool = Queue.Queue (0)
for x in xrange(2):
	moonHost().start()
server = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
server.bind (('', 2727))
server.listen (5)
while True:
	channel, details = server.accept
	moonHost (channel, details ).start()"""
#print"host started"
testhost = True
while testhost == True:
	for x in range(1, 100):
		print x
