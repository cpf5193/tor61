# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Project 0

# ProxyConnectionListener.py
# Listens for TCP connections on a specific port
# and delegates them to a connection handler

import Tor61Log, socket, threading, sys
from datetime import *
log = Tor61Log.getLog()

LISTENER_BACKLOG = 1

class ProxyConnectionListener:
	#Initialize port that listens for new Proxy connections	
	def __init__(self, port, connectionHandler):
		self.connectionHandler = connectionHandler
		self.bindPort(port)
		log.info("__init__() completed")

	#Bind a port to the listener
	def bindPort(self, port):
		host = socket.gethostname()
		self.listener = socket.socket(socket.AF_INET, 
			socket.SOCK_STREAM)
		self.listener.bind((host, port))
		self.listener.listen(LISTENER_BACKLOG)

	#Await connections and pass them to the connection handler
	def start(self):
		while(True):
			try:
				log.info("Listening for connections")
				conn, addr = self.listener.accept()
				log.info("Received new connection from " + str(addr))
				self.connectionHandler.processConnection(conn, addr)
			except socket.error, msg:
				self.log.error(msg)
				
#Run this module alone as a test giving it a port as an argument
if(__name__ == "__main__"):
	class Dummy:
		def processConnection(self, conn, addr):
			return
	d = Dummy()
	pcl = ProxyConnectionListener(int(sys.argv[1]), d)
	pcl.start()
