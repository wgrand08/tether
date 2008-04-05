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


# example code located: http://www.devshed.com/c/a/Python/Sockets-in-Python-Into-the-World-of-Python-Network-Programming/2/

from socket import *



def starthost():	HOST = 'localhost'	PORT = 21567	BUFSIZ = 1024	ADDR = (HOST, PORT)
	serversock = socket(AF_INET, SOCK_STREAM)	serversock.bind(ADDR)	serversock.listen(2)

	while 1:		print 'waiting for connection... '		clientsock, addr = serversock.accept()		print 'connected from:', addr
		while 1:
			data = clientsock.recv(BUFSIZ)			if not data: 
				break				clientsock.send('echoed', data)  		clientsock.close()	serversock.close()

starthost()