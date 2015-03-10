# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpCellConverter.py
# Converter module for communication between the Tor router
# and HTTP proxy

import Queue, threading
import Tor61Log
log = Tor61Log.getLog()

class HttpCellConverter:
	BLOCK_TIMEOUT = 2
	#Store the output buffer
	def __init__(self):
		self.httpInputBuffer = Queue.Queue()
		self.httpOutputBuffer = Queue.Queue()
		self.cellInputBuffer = Queue.Queue()
		self.cellOutputBuffer = Queue.Queue()
		self.end = False
		
	#Place an Http message to convert into a Cell
	def putHttp(self, sock, message):
		log.info(message.strip())
		self.httpInputBuffer.put((sock, message), True)
		
	#Place a Tor61 cell to convert into an HTTP message
	def putCell(self, cell):
		log.info(str(cell).strip())
		self.cellInputBuffer.put(cell, True)
		
	#Get a Http message that has been converted from a Tor61 Cell
	def getCellOutputBuffer(self):
		return self.cellOutputBuffer
		
	#Get a Tor61 cell that has been converted from a Http message
	def getHttpOutputBuffer(self):
		return self.httpOutputBuffer
		
	#Stop all activity
	def stop(self):
		self.end = True;
	
	#Porcess an Http message
	def processHttp(self, sock, message):
		log.info("here");
		t = threading.Thread(target=self.processHttpWorker,
			args=(sock, message))
		t.start()
	
	#Worker thread for asynchronous HTTP to Cell conversion
	def processHttpWorker(self, sock, message):
		log.info("");
		self.httpOutputBuffer.put((sock, message), True) #TODO: Actual conversion
	
	#Process a Cell
	def processCell(self, cell):
		log.info("here");
		t = threading.Thread(target=self.processCellWorker, 
			args=(cell))
		t.start()
		
	#Worker thread for asynchronous Cell to Http conversion
	def processCellWorker(self, cell):
		log.ingo("")
		self.putCell(cell) #TODO: actual conversion

	#Worker thread for reading from incoming Http
	def httpWorker(self):
		while(not self.end):
			nextItem = None
			try:
				nextItem = self.httpInputBuffer.get(True, self.BLOCK_TIMEOUT)
			except Queue.Empty:
				log.info("timeout")
				log.info(self.httpInputBuffer.qsize())
				continue
			sock, message = nextItem
			self.processHttp(sock, message)

	#Worker thread for reading incoming Http
	def cellWorker(self):
		while(not self.end):
			nextItem = None
			try:
				nextItem = self.cellInputBuffer.get(True, self.BLOCK_TIMEOUT)
			except Queue.Empty:
				log.info("timeout")
				continue
			self.processCell(nextItem)

	#Start listening for incoming Cells and HTTP messages
	def start(self):
		httpThread = threading.Thread(target=self.httpWorker)
		cellThread = threading.Thread(target=self.cellWorker)
		cellThread.start()
		httpThread.start()
			
		
#Use a single instance of the converter
converterSingleton = HttpCellConverter()
def getConverter():
	return converterSingleton;
	
#Public access for Http output buffer
def getHttpOutputBuffer():
	return getConverter().getHttpOutputBuffer()
	
#public access for Cell output buffer
def getCellOutputBuffer():
	return getConverter().getCellOutputBuffer()
