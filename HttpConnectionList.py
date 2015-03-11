# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpProxy.py
# Stores a list of HTTP Connections 

import sys, threading, Tor61Log, HttpCellConverter, Queue
from ProxyConnectionListener import ProxyConnectionListener
from HttpConnection import HttpConnection

log = Tor61Log.getLog()

class HttpProxy:
	BLOCK_TIMEOUT = 2
	streamId = 1
	BEGIN = 1
	DATA = 2
	END = 3
	CONNECTED = 4
	FAIL = 11
	
	#Initialize port that listens for new Proxy connections	
	def __init__(self, listenerPort):
		self.connections = {}
		self.listener = ProxyConnectionListener(listenerPort, self)
		self.incomingHttp = HttpCellConverter.getHttpOutputBuffer()
		self.end = False
		log.info("__init__() completed")

	#Store the connection in the connection lists
	def processConnectionFromBrowser(self, conn, addr):
		log.info("Processing connection from " + str(addr))
		self.connections[addr] = HttpConnection(conn, addr, self)
		self.connections[addr].openConnectionFromBrowser()
		
	#Get a connection from a tor router
	def processConnectionFromRouter(self, addr):
		serverSocket = socket.socket(socket.AF_INET, 
			socket.SOCK_STREAM)
		serverSocket.connect((host, port))
		self.connections[addr] = HttpConnection(conn, addr, self)
		self.connections[addr].openConnection()
		
	#Add connections to the connection list as they arrive
	def awaitConnections(self):
		self.awaitConvertedCells()
		thread = threading.Thread(target=self.listener.start, args=())
		thread.start()
		
	#Await incoming converted Tor cells
	def awaitConvertedCells(self):
		self.thread = threading.Thread(target=self.awaitConvertedCellsWorker)
		self.thread.start()
		
	#Worker thread for awaiting converted Tor cells
	def awaitConvertedCellsWorker(self):
		while(not self.end):
			nextItem = None
			try:
				nextItem = self.incomingHttp.get(True, self.BLOCK_TIMEOUT)
			except Queue.Empty:
				log.info("timeout")
				continue
			self.delegateMessage(nextItem)
		
	#Interpret DATA, BEGIN, and END	
	def delegateMessage(message):
		t = threading.Thread(target=self.delegateMessageWorker,
			args=(message,))
		t.start()

	#Worker for delegation
	def delegateMessageWorker(message):
		command, payload = message
		addr, body = payload
		if command == self.DATA:
			if addr in self.connections:
				self.connections[addr].putHttp(body)
		if command == self.BEGIN:
			self.processConnectionFromRouter(addr)
		if command == self.END:
			if addr in self.connections:
				self.connections[addr].stop()
		if command == self.CONNECTED:
			if addr in self.connections:
				self.conections[addr].buffer.put("SUCCESS")
		if command == self.FAIL:
			if addr in self.connections:
				self.connections[addr].buffer.put("FAIL")
			
			
	
	
	#Stop all activity
	def stop(self):
		self.listener.stop()
		self.end = True
		for conn in self.connections:
			self.connections[conn].stop()
	
	#Removes a connection identified by streamId		
	def removeConnection(self, addr):
		del self.connections[addr]
				
#Run this module alone as a test giving it a port as an argument
if(__name__ == "__main__"):
	import HttpCellConverter
	HttpCellConverter.getConverter().start()
	hcl = HttpConnectionList(int(sys.argv[1]))
	hcl.awaitConnections()
	stop = False
	while(not stop):
		try:
			for line in sys.stdin:
				print line
		except KeyboardInterrupt:
			log.info("Keyboard Interrupt")
			stop = True
			hcl.stop()
			HttpCellConverter.getConverter().stop()
