# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Project 0

# HttpConnection.py
# Stores a read thread, write thread, and thread-safe
# buffer for writing in an HttP Connection

import sys, threading, logging
from HttpReader import HttpReader
from HttpWriter import HttpWriter
from HttpBuffer import HttpBuffer

class HttpConnection:
	#Initialize port that listens for new Proxy connections	
	def __init__(self, sock):
		self.buffer = HttpBuffer()
		self.reader = HttpReader(sock)
		self.writer = HttpWriter(sock, self.buffer)
		self.setupLog()
		self.log.info("__init__() completed")

	#Initialize logging based on DEBUG_FLAG
	def setupLog(self):
		logging.basicConfig(format='%(levelname)s:%(message)s')
		self.log = logging.getLogger('tor61')
		self.log.setLevel(logging.INFO)
		
	#Add connections to the connection list as they arrive
	def openConnection(self):
		readThread = threading.Thread(target=self.reader.start,
			args=())
		writeThread = threading.Thread(target=self.writer.start,
			args=())
		readThread.start()
		writeThread.start()
