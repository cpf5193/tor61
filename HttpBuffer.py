# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

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
		log.info("")
		return self.data.get()
		
	#Places a piece of data in the buffer
	def put(self, message):
		log.info(message.strip())
		self.data.put(message)
