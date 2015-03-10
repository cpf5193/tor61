# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpReader.py
# Read thread for Http Proxy

import sys, threading, Tor61Log, HttpCellConverter, socket
from ProxyConnectionListener import ProxyConnectionListener
log = Tor61Log.getLog()

READ_SIZE = 4096

class HttpReader:
	BLOCK_TIMEOUT = 2
	#Store the socket that we will be reading from
	def __init__(self, sock, connection):
		self.sock = sock
		self.sock.settimeout(self.BLOCK_TIMEOUT)
		self.converter = HttpCellConverter.getConverter()
		self.connection = connection
		self.end = False
		
	#Read from the socket as long as there is data
	def start(self):
		while(not self.end):
			message = None
			try:
				message = self.sock.recv(READ_SIZE)
				if(len(message) == 0):
					self.connection.stop()
			except socket.timeout:
				log.info("timeout")
				continue
			log.info("Received: '" + message.strip() + "'")
			self.converter.putHttp(self.sock, message)
	
	#Stops all activity
	def stop(self):
		self.end = True
