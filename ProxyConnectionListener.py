# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# ProxyConnectionListener.py
# Listens for TCP connections on a specific port
# and delegates them to a connection handler

import Tor61Log, socket, threading, sys
from datetime import *
log = Tor61Log.getLog()

LISTENER_BACKLOG = 1

class ProxyConnectionListener:
	BLOCK_TIMEOUT = 2
	#Initialize port that listens for new Proxy connections	
	def __init__(self, port, connectionHandler):
		self.connectionHandler = connectionHandler
		self.streamId = 1
		self.bindPort(port)
		self.end = False
		log.info("__init__() completed")

	#Bind a port to the listener
	def bindPort(self, port):
		host = socket.gethostname()
		self.listener = socket.socket(socket.AF_INET, 
			socket.SOCK_STREAM)
		self.listener.bind((host, port))
		self.listener.listen(LISTENER_BACKLOG)
		self.listener.settimeout(self.BLOCK_TIMEOUT)

	#Await connections and pass them to the connection handler
	def start(self):
		while(not self.end):
			try:
				log.info("Listening for connections")
				conn, addr = self.listener.accept()
				log.info("Received new connection from " + str(addr))
				self.connectionHandler.processConnectionFromBrowser(conn,
					addr)
			except socket.timeout:
				log.info("timeout")
				continue
			except socket.error, msg:
				log.error(msg)
				
		self.listener.close()

	#Stop activity on this listener
	def stop(self):
		self.end = True
				
#Run this module alone as a test giving it a port as an argument
if(__name__ == "__main__"):
	class Dummy:
		def processConnection(self, conn, addr):
			return
	d = Dummy()
	pcl = ProxyConnectionListener(int(sys.argv[1]), d)
	pcl.start()
