# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Project 0

# HttpReader.py
# Read thread for Http Proxy

import sys, threading, logging
from ProxyConnectionListener import ProxyConnectionListener

READ_SIZE = 4096

class HttpReader:
	#Store the socket that we will be reading from
	def __init__(self, sock):
		self.sock = sock
		self.setupLog()

	#Initialize logging
	def setupLog(self):
		logging.basicConfig(format='%(levelname)s:%(message)s')
		self.log = logging.getLogger('tor61')
		self.log.setLevel(logging.INFO)
		
	#Read from the socket as long as there is data
	def start(self):
		while(True):
			message = self.sock.recv(READ_SIZE)
			self.log.info("Received: '" + message.strip() + "'")
