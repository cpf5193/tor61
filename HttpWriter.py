# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Project 0

# HttpWriter.py
# Write thread for Http Proxy

import sys, threading, logging
from ProxyConnectionListener import ProxyConnectionListener

class HttpWriter:
	#Store the socket that will be written to and created a buffer
	#to write from
	def __init__(self, sock, inputSource):
		self.sock = sock
		self.buffer = inputSource
		self.setupLog()

	#Initialize logging based on DEBUG_FLAG
	def setupLog(self):
		logging.basicConfig(format='%(levelname)s:%(message)s')
		self.log = logging.getLogger('tor61')
		self.log.setLevel(logging.INFO)
		
	#While there is data to be sent, send it
	def start(self):
		while(self.buffer.hasNext()):
			toSend = self.buffer.getNext()
			self.sock.send(toSend)
			sef.log.info("Sent: '" + message + "'")
