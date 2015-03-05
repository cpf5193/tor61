#HttpProxy.py

#Contains an interface for internet browsers to connect to the Tor
#router associated with this proxy.

#Initialize port that listens for new Proxy connections
def __init__(self, port):
	self.connections = ProxyConnectionList()
	self.newConnectionListener = ProxyConnectionListener(port, 
		self.connections)
