# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

#HttpProxy.py

#Contains an interface for internet browsers to connect to the Tor
#router associated with this proxy.

from HttpConnectionList import HttpConnectionList
from ProxyConnectionListener import ProxyConnectionListener
import sys

#Initialize port that listens for new Proxy connections
def __init__(self, port):
	self.connections = ProxyConnectionList()
	self.newConnectionListener = ProxyConnectionListener(port, 
		self.connections)

if(__name__ == "__main__"):
	hcl = HttpConnectionList(int(sys.argv[1]))
	hcl.awaitConnections()
