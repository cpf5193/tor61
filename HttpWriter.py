# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Project 0

# HttpWriter.py
# Write thread for Http Proxy

import sys, threading, Tor61Log
from ProxyConnectionListener import ProxyConnectionListener
log = Tor61Log.getLog()

class HttpWriter:
	#Store the socket that will be written to and created a buffer
	#to write from
	def __init__(self, sock, inputSource):
		self.sock = sock
		self.buffer = inputSource
		
	#While there is data to be sent, send it
	def start(self):
		while(self.buffer.hasNext()):
			toSend = self.buffer.getNext()
			self.sock.send(toSend)
			log.info("Sent: '" + message + "'")
