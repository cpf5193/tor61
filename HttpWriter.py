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
	def __init__(self, sock, inputSource, addr, connection):
		self.sock = sock
		self.addr = addr
		self.buffer = inputSource
		self.connection = connection
		self.end = False
		
	#While there is data to be sent, send it
	def start(self):
		log.info("ready to write to " + str(self.sock.getpeername()))
		while(not self.end):
			log.info("in the main loop")
			nextItem = ""
			try:
				nextItem = self.buffer.get(True, self.BLOCK_TIMEOUT)
			except Queue.Empty:
				log.info("\n\ntimeout: QSIZE = " + str(self.buffer.qsize()))
				continue
			if not self.end and not (nextItem is None or nextItem == ""):
				try:
					self.sock.send(nextItem)
				except socket.err as msg:
					log.info(str(msg))
					self.stop()
				log.info("Sent: '" + nextItem.strip() + "'\n to " +
					str(self.addr))
			if nextItem == "":
				continue
		log.info("Exiting conn to " + str(self.addr) + " (nextItem: " + str(nextItem) + ")")
		if(self.connection.reader.end):
			self.sock.close()
			
	#Stops all activity
	def stop(self):
		self.end = True
