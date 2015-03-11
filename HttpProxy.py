# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpProxy.py
# Stores a list of HTTP Connections 

import sys, threading, Tor61Log, HttpCellConverter, Queue, HttpParser, socket
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
	READ_SIZE = 498
	
	#Initialize port that listens for new Proxy connections	
	def __init__(self, listenerPort):
		self.connections = {}
		self.listener = ProxyConnectionListener(listenerPort, self)
		self.incomingHttp = HttpCellConverter.getHttpOutputBuffer()
		self.converter = HttpCellConverter.getConverter()
		self.end = False
		log.info("__init__() completed")

	#Store the connection in the connection lists
	def processConnectionFromBrowser(self, conn, addr):
		log.info((conn, addr))
		t = threading.Thread(target=self.processConnectionFromBrowserWorker,
			args=(conn, addr))
		t.start()
		
	#Worker thread
	def processConnectionFromBrowserWorker(self, conn, addr):
		log.info(addr)
		self.connections[addr] = HttpConnection(conn, self)
		while not self.connections[addr].end:
			try:
				firstMessage = conn.recv(self.READ_SIZE)
				if len(firstMessage) == 0:
					self.connections[addr].killSelf()
				else:
					break
			except socket.timeout:
				log.info("timeout")
				continue
		log.info("Got first message:\n" + firstMessage)
		hostPort = HttpParser.getHostAndPort(firstMessage)
		if hostPort is not None:
			self.connections[addr].setFirstMessage(((self.DATA, (addr, 
				firstMessage))))
			host, port = hostPort
			body = host + ":" + str(port) + "\0"
			beginMessage = (self.BEGIN, (addr, body))
			self.converter.putHttp(beginMessage)
		else:
			self.connections[addr].killSelf()
		
	#Get a connection from a tor router
	def processConnectionFromRouter(self, addr):
		log.info(addr)
		serverSocket = socket.socket(socket.AF_INET, 
			socket.SOCK_STREAM)
		try:
			serverSocket.connect(addr)
		except socket.error as (errno, msg):
			log.info(msg)
			self.converter.putHttp((self.FAIL, (addr, "")))
			return
		self.connections[addr] = HttpConnection(serverSocket, self)
		self.connections[addr].openConnection(addr)
		self.converter.putHttp((self.CONNECTED, (addr, "")))
		
	#Add connections to the connection list as they arrive
	def awaitConnections(self):
		self.awaitConvertedCells()
		thread = threading.Thread(target=self.listener.start, args=())
		thread.start()
		log.info("started")

		
	#Await incoming converted Tor cells
	def awaitConvertedCells(self):
		self.thread = threading.Thread(target=self.awaitConvertedCellsWorker)
		self.thread.start()
		log.info("started")
		
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
	def delegateMessage(self, message):
		t = threading.Thread(target=self.delegateMessageWorker,
			args=(message,))
		t.start()

	#Worker for delegation
	def delegateMessageWorker(self, message):
		log.info(message)
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
				self.connections[addr].openConnection(addr)
		if command == self.FAIL:
			if addr in self.connections:
				del self.connections[addr]

	#Stop all activity
	def stop(self):
		self.listener.stop()
		self.end = True
		for conn in self.connections:
			self.connections[conn].stop()
	
	#Removes a connection identified by streamId		
	def removeConnection(self, addr):
		log.info(addr[0])
		self.converter.putHttp((self.END, (addr, "")))
		del self.connections[addr]
				
#Run this module alone as a test giving it a port as an argument
if(__name__ == "__main__"):
	import DummyRouter
	HttpCellConverter.getConverter().start()
	proxy = HttpProxy(int(sys.argv[1]))
	tor = DummyRouter.DummyRouter()
	tor.start()
	proxy.awaitConnections()
	stop = False
	while(not stop):
		try:
			for line in sys.stdin:
				print line
		except KeyboardInterrupt:
			log.info("Keyboard Interrupt")
			stop = True
			proxy.stop()
			tor.stop()
			HttpCellConverter.getConverter().stop()
