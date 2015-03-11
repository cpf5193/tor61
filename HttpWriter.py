# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpWriter.py
# Write thread for Http Proxy

import sys, threading, Tor61Log
from ProxyConnectionListener import ProxyConnectionListener
log = Tor61Log.getLog()
import Queue

class HttpWriter:
	BLOCK_TIMEOUT = 2
	#Store the socket that will be written to and created a buffer
	#to write from
	def __init__(self, sock, inputSource):
		self.sock = sock
		self.buffer = inputSource
		self.end = False
		
	#While there is data to be sent, send it
	def start(self):
		log.info("ready to write to " + str(self.sock.getpeername()))
		while(not self.end):
			nextItem = None
			try:
				nextItem = self.buffer.get(True, self.BLOCK_TIMEOUT)
			except Queue.Empty:
				log.info("\n\ntimeout: QSIZE = " + str(self.buffer.qsize()))
				continue
			if not self.end:
				self.sock.send(nextItem)
				log.info("Sent: '" + nextItem.strip() + "'\n to " +
					str(self.sock.getpeername()))
			
	#Stops all activity
	def stop(self):
		self.end = True
