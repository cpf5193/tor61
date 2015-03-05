# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpConnection.py
# Stores a read thread, write thread, and thread-safe
# buffer for writing in an HttP Connection

import sys, threading, Tor61Log
from HttpReader import HttpReader
from HttpWriter import HttpWriter
from HttpBuffer import HttpBuffer
from HttpCellConverter import HttpCellConverter

log = Tor61Log.getLog()

class HttpConnection:
	#Initialize port that listens for new Proxy connections	
	def __init__(self, sock):
		self.buffer = HttpBuffer()
		self.converter = HttpCellConverter(self.buffer)
		self.reader = HttpReader(sock, self.converter)
		self.writer = HttpWriter(sock, self.buffer)
		log.info("__init__() completed")
		
	#Add connections to the connection list as they arrive
	def openConnection(self):
		readThread = threading.Thread(target=self.reader.start,
			args=())
		writeThread = threading.Thread(target=self.writer.start,
			args=())
		readThread.start()
		writeThread.start()
