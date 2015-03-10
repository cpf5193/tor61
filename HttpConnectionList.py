# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpConnectionList.py
# Stores a list of HTTP Connections 

import sys, threading, Tor61Log, HttpCellConverter, Queue
from ProxyConnectionListener import ProxyConnectionListener
from HttpConnection import HttpConnection

log = Tor61Log.getLog()

class HttpConnectionList:
	BLOCK_TIMEOUT = 2
	#Initialize port that listens for new Proxy connections	
	def __init__(self, listenerPort):
		self.connections = {}
		self.listener = ProxyConnectionListener(listenerPort, self)
		self.incomingHttp = HttpCellConverter.getHttpOutputBuffer()
		self.end = False
		log.info("__init__() completed")

	#Stor the connection in the connection lists
	def processConnection(self, conn, addr):
		log.info("Processing connection from " + str(addr))
		self.connections[conn] = HttpConnection(conn)
		self.connections[conn].openConnection()
		
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
			(sock, message) = nextItem
			self.connections[sock].putHttp(message)
	
	#Stop all activity
	def stop(self):
		self.listener.stop()
		self.end = True
		for conn in self.connections:
			self.connections[conn].stop()
				
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
