# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Project 0

# HttpConnectionList.py
# Stores a list of HTTP Connections 

import sys, threading, logging
from ProxyConnectionListener import ProxyConnectionListener

class HttpConnectionList:
	#Initialize port that listens for new Proxy connections	
	def __init__(self, listenerPort):
		self.connections = {}
		self.setupLog()
		self.listener = ProxyConnectionListener(listenerPort, self)
		self.log.info("__init__() completed")

	#Initialize logging based on DEBUG_FLAG
	def setupLog(self):
		logging.basicConfig(format='%(levelname)s:%(message)s')
		self.log = logging.getLogger('ProxyConnectionListener')
		self.log.setLevel(logging.INFO)

	#Stor the connection in the connection lists
	def processConnection(self, conn, addr):
		self.log.info("Processing connection from " + str(addr))
		self.connections[addr] = conn
		
	#Add connections to the connection list as they arrive
	def awaitConnections(self):
		thread = threading.Thread(target=self.listener.start, args=())
		thread.start()
				
#Run this module alone as a test giving it a port as an argument
if(__name__ == "__main__"):
	hcl = HttpConnectionList(int(sys.argv[1]))
	hcl.awaitConnections()
