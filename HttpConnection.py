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
import Queue

log = Tor61Log.getLog()

class HttpConnection:
	#Initialize port that listens for new Proxy connections	
	def __init__(self, sock):
		self.buffer = Queue.Queue()
		self.sock = sock
		self.reader = HttpReader(sock, self)
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

	#Asynchronous method for putting an HTTP message into the write
	#buffer
	def putHttp(self, message):
		log.info(message.strip())
		t = threading.Thread(target=self.putHttpWorker,args=(message,))
		t.start()
		
	#Worker thread for placing an Http message
	def putHttpWorker(self, message):
		self.buffer.put(message, True)
		
	#Stops all activity on worker threads
	def stop(self):
		self.reader.stop()
		self.writer.stop()
		self.sock.close()