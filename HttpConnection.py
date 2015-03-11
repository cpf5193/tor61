# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpConnection.py
# Stores a read thread, write thread, and thread-safe
# buffer for writing in an HttP Connection

import sys, threading, Tor61Log, HttpCellConverter
from HttpReader import HttpReader
from HttpWriter import HttpWriter
import Queue

log = Tor61Log.getLog()

class HttpConnection:
	BLOCK_TIMEOUT = 2
	#Initialize port that listens for new Proxy connections	
	def __init__(self, sock, parentList):
		self.buffer = Queue.Queue()
		self.sock = sock
		self.reader = HttpReader(sock, self)
		self.writer = HttpWriter(sock, self.buffer)
		self.parentList = parentList
		self.converter = HttpCellConverter.getConverter()
		self.firstMessage = None
		self.end = False
		log.info("__init__() completed")
		
	#Make a connection from a router
	def openConnection(self, addr):
		log.info("first message:\n" + str(self.firstMessage))
		self.addr = addr
		readThread = threading.Thread(target=self.reader.start,
			args=(addr,))
		writeThread = threading.Thread(target=self.writer.start,
			args=())
		readThread.start()
		writeThread.start()
		if self.firstMessage is not None:
			self.converter.putHttp(self.firstMessage)

	#Asynchronous method for putting an HTTP message into the write
	#buffer
	def putHttp(self, message):
		log.info(message.strip())
		t = threading.Thread(target=self.putHttpWorker,args=(message,))
		t.start()
		
	#Worker thread for placing an Http message
	def putHttpWorker(self, message):
		self.buffer.put(message, True)
		
	def setFirstMessage(self, message):
		self.firstMessage = message
		log.info("Set first message to: \n" + self.firstMessage[1][1])
		
	#Stops all activity on worker threads
	def stop(self):
		self.end = True
		self.reader.stop()
		self.writer.stop()
		self.sock.close()
	#Stop and get out of dictionary
	def killSelf(self):
		self.stop()
		self.parentList.removeConnection(self.addr);
		
