# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Project 0

# HttpReader.py
# Read thread for Http Proxy

from  Queue import Queue
import Tor61Log
log = Tor61Log.getLog()

class HttpBuffer:
	#Store the data to be consumed
	def __init__(self):
		self.data = Queue()
		
	#Returns True if there is data to process, else False
	def hasNext(self):
		return not self.data.empty()
		
	#Gets the next piece of data in the buffer
	def getNext(self):
		return self.data.get()
		
	#Places a piece of data in the buffer
	def put(self, message):
		self.data.put(message)
		
