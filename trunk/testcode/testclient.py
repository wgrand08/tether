from socket import *

def runclient():
	HOST = 'localhost'	PORT = 21567	BUFSIZ = 1024	ADDR = (HOST, PORT)	tcpCliSock = socket(AF_INET, SOCK_STREAM)	tcpCliSock.connect(ADDR)

	while True:		data = raw_input('> ')		if not data: break 		tcpCliSock.send(data)		data = tcpCliSock.recv(1024)		if not data: break 	print data	tcpCliSock.close()runclient()