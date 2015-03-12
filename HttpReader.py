# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpReader.py
# Read thread for Http Proxy

import sys, threading, Tor61Log, HttpCellConverter, socket
from ProxyConnectionListener import ProxyConnectionListener
log = Tor61Log.getLog()

READ_SIZE = 498

class HttpReader:
	BLOCK_TIMEOUT = 2
	DATA_CMD = 2
	#Store the socket that we will be reading from
	def __init__(self, sock, connection):
		self.sock = sock
		self.converter = HttpCellConverter.getConverter()
		self.connection = connection
		self.end = False
		
	#Read from the socket as long as there is data
	def start(self, addr):
		log.info("starting read from " + str(addr))
		while(not self.end):
			message = None
			self.sock.settimeout(self.BLOCK_TIMEOUT)
			try:
				message = self.sock.recv(READ_SIZE)
				if(len(message) == 0):
					log.info("received empty message")
					self.connection.killSelf()
			except socket.timeout:
				log.info("timeout")
				continue
			except socket.error as msg:
				log.info(msg)
				self.connection.killSelf()
			if not self.end:
				log.info("Received: '" + message.strip() + "'")
				self.converter.putHttp((self.DATA_CMD, (addr, message)))
				
	
	#Stops all activity
	def stop(self):
		self.end = True
