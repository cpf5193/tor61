# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Project 0

# HttpReader.py
# Read thread for Http Proxy

import sys, threading, Tor61Log
from ProxyConnectionListener import ProxyConnectionListener
log = Tor61Log.getLog()

READ_SIZE = 4096

class HttpReader:
	#Store the socket that we will be reading from
	def __init__(self, sock):
		self.sock = sock
		
	#Read from the socket as long as there is data
	def start(self):
		while(True):
			message = self.sock.recv(READ_SIZE)
			log.info("Received: '" + message.strip() + "'")
