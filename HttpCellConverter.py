# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpCellConverter.py
# Converter module for communication between the Tor router
# and HTTP proxy

from  Queue import Queue
import Tor61Log
log = Tor61Log.getLog()

class HttpCellConverter:
	#Store the output buffer
	def __init__(self, outputBuffer):
		self.outputBuffer = outputBuffer
		
	#Processes an HTML mesage
	def receiveHttp(self, message):
		log.info(message.strip())
		self.outputBuffer.put(message)
