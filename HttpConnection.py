# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpConnection.py
# Stores a read thread, write thread, and thread-safe
# buffer for writing in an HttP Connection

import sys, threading, Tor61Log, HttpCellConverter, HttpParser
from HttpReader import HttpReader
from HttpWriter import HttpWriter
import Queue

log = Tor61Log.getLog()

class HttpConnection:
	BLOCK_TIMEOUT = 2
	OK = "HTTP/1.0 200 OK\r\n\r\n"
	#Initialize port that listens for new Proxy connections	
	def __init__(self, sock, parentList, addr):
		self.buffer = Queue.Queue()
		self.addr = addr
		self.sock = sock
		self.reader = HttpReader(sock, self, addr)
		self.writer = HttpWriter(sock, self.buffer, addr, self)
		self.parentList = parentList
		self.converter = HttpCellConverter.getConverter()
		self.isTunnel = False
		self.firstMessage = None
		self.end = False
		log.info("__init__() completed")
		
	#Make a connection from a router
	def openConnection(self):
		log.info("first message:\n" + str(self.firstMessage))
		if self.firstMessage is not None:
			self.converter.putHttp(self.firstMessage)
		readThread = threading.Thread(target=self.reader.start,
			args=())
		writeThread = threading.Thread(target=self.writer.start,
			args=())
		readThread.start()
		writeThread.start()


	#Asynchronous method for putting an HTTP message into the write
	#buffer
	def putHttp(self, message):
		log.info(message.strip())
		if not self.isTunnel:
			if HttpParser.isConnect(message):
				self.isTunnel = True
				self.parentList.converter.putHttp((self.parentList.DATA, 
					(self.addr, self.OK)))
				return
			else:
				message = HttpParser.modifyMessage(message)
		log.info("enqueing for write " + message.strip())
		self.buffer.put(message, True)
		
	def setFirstMessage(self, message):
		self.firstMessage = message
		log.info("Set first message to: \n" + self.firstMessage[1][1])
		
	#Stops all activity on worker threads
	def stop(self):
		self.end = True
		self.reader.stop()
		self.writer.stop()
		
	#Stop and get out of dictionary
	def killSelf(self):
		log.info("");
		self.stop()
		self.parentList.removeConnection(self.addr);
		
