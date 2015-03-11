# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpProxy.py
# Stores a list of HTTP Connections 

import sys, threading, Tor61Log, HttpCellConverter, Queue
from struct import unpack
from ProxyConnectionListener import ProxyConnectionListener
from HttpConnection import HttpConnection

log = Tor61Log.getLog()

class DummyRouter:
	BLOCK_TIMEOUT = 2
	streamId = 1
	BEGIN = 1
	DATA = 2
	END = 3
	CONNECTED = 4
	FAIL = 11
	RELAY_CELL_HEADER_FORMAT = '!HBHHIHB498s'
	table = {}
	end = False
	converter = HttpCellConverter.getConverter()
	
	def start(self):
		t = threading.Thread(target = self.awaitConvertedHttpWorker)
		t.start()
		
	#Worker thread for awaiting converted Tor cells
	def awaitConvertedHttpWorker(self):
		while(not self.end):
			nextItem = None
			try:
				nextItem = self.converter.getCellOutputBuffer().get(True, self.BLOCK_TIMEOUT)
			except Queue.Empty:
				log.info("timeout")
				continue
			self.delegateMessage(nextItem)
		
	#Interpret DATA, BEGIN, and END	
	def delegateMessage(self, cell):
		log.info("here")
		t = threading.Thread(target=self.delegateMessageWorker,
			args=(cell,))
		t.start()

	#Worker for delegation
	def delegateMessageWorker(self, cell):
		log.info("from " + str(cell[0]))
		addr, payload = cell
		circuit, three, streamId, zero, digest, length, command, body = unpack(self.RELAY_CELL_HEADER_FORMAT, payload)
		if command == self.BEGIN:
			hostPort = body.strip("\0").split(":")
			remote = (hostPort[0], int(hostPort[1]))
			self.table[remote] = addr
			self.table[addr] = remote
		log.info("to " + str(self.table[addr]))
		self.converter.putCell((self.table[addr], payload))

	#Stop all activity
	def stop(self):
		self.end = True
