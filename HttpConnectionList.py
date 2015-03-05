# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpConnectionList.py
# Stores a list of HTTP Connections 

import sys, threading, Tor61Log
from ProxyConnectionListener import ProxyConnectionListener
from HttpConnection import HttpConnection

log = Tor61Log.getLog()

class HttpConnectionList:
	#Initialize port that listens for new Proxy connections	
	def __init__(self, listenerPort):
		self.connections = {}
		self.listener = ProxyConnectionListener(listenerPort, self)
		log.info("__init__() completed")

	#Stor the connection in the connection lists
	def processConnection(self, conn, addr):
		log.info("Processing connection from " + str(addr))
		self.connections[addr] = HttpConnection(conn)
		self.connections[addr].openConnection()
		
	#Add connections to the connection list as they arrive
	def awaitConnections(self):
		thread = threading.Thread(target=self.listener.start, args=())
		thread.start()
				
#Run this module alone as a test giving it a port as an argument
if(__name__ == "__main__"):
	hcl = HttpConnectionList(int(sys.argv[1]))
	hcl.awaitConnections()
