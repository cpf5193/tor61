# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpCellConverter.py
# Converter module for communication between the Tor router
# and HTTP proxy

import Queue, threading
import Tor61Log
from struct import pack, unpack
log = Tor61Log.getLog()

class HttpCellConverter:
	BLOCK_TIMEOUT = 2
	RELAY_CELL_HEADER_FORMAT = '!HBHHIHB498s'
	RELAY_CELL_CIRCUIT_ID = 1
	RELAY_DIGEST = 0
	THREE = 3
	ZERO = 0
	BEGIN_CMD = 1
	DATA_CMD = 2
	END_CMD = 3
	CONNECTED_CMD = 4
	FAIL_CMD = 11
	
	#Store the output buffer
	def __init__(self):
		self.httpInputBuffer = Queue.Queue()
		self.httpOutputBuffer = Queue.Queue()
		self.cellInputBuffer = Queue.Queue()
		self.cellOutputBuffer = Queue.Queue()
		self.end = False
		
	#Place an Http message to convert into a Cell
	def putHttp(self, message):
		log.info(message)
		self.httpInputBuffer.put(message, True)
		
	#Place a Tor61 cell to convert into an HTTP message
	def putCell(self, cell):
		log.info((cell[0], cell[1].strip("\0")))
		self.cellInputBuffer.put(cell, True)
	
	#Builds a cell
	def buildCell(self, body, command):
		log.info((body, command))
		cell = pack(self.RELAY_CELL_HEADER_FORMAT,
			self.RELAY_CELL_CIRCUIT_ID,
			self.THREE,
			self.ZERO,
			self.ZERO,
			self.RELAY_DIGEST,
			len(body),
			command,
			body)
		return cell
		
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
	def processHttp(self, message):
		log.info(message);
		command, payload = message
		addr, body = payload
		cell = self.buildCell(body, command)
		self.cellOutputBuffer.put((addr, cell), True)

	#Process a Cell
	def processCell(self, cell):
		log.info((cell[0], cell[1].strip("\0")))
		addr, payload = cell
		circuit, three, streamId, zero, digest, length, command, body = unpack(self.RELAY_CELL_HEADER_FORMAT, payload)
		message = (command, (addr, body.strip("\0")))
		self.httpOutputBuffer.put(message, True)
		
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
			self.processHttp(nextItem)

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
