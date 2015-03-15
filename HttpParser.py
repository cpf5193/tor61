# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpParser.py
# Interprets HTTP messages

import sys, threading, Tor61Log
from ProxyConnectionListener import ProxyConnectionListener
log = Tor61Log.getLog()

def getHostAndPort(message):
	lines = message.lower().splitlines()
	uriLine = lines[0].split(" ")
	if(len(uriLine) < 2):
		return None
	uri = uriLine[1]
	host = None
	port = None
	for line in lines:
		if line.startswith("host:"):
			hostLine = line.split(":")
			if len(hostLine[1]) > 0:
				host = hostLine[1].strip()
				if len(hostLine) > 2 and hostLine[2].strip().isdigit():
					port = int(hostLine[2].strip())
				break
	if host is None:
		return None
	elif port is None:
		if(uri.startswith("https")):
			log.info((host, 443))
			return (host, 443)
		else:
			hostPort = uri.split(":")
			if hostPort[1].isdigit():
				port = int(hostPort[1])
				log.info((host, port))
				return (host, port)
			else:
				log.info((host, 80))
				return (host, 80)
	else:
		log.info((host, port))
		return (host, port)
		
def modifyMessage(message):
	modified = message.replace("Proxy-connection: keep-alive", 
		"Proxy-connection: close", 1)
	modified = modified.replace("Connection: keep-alive", 
		"Connection: close", 1)
	modified = modified.replace(" HTTP/2.0", " HTTP/1.0", 1)
	modified = modified.replace(" HTTP/1.1", " HTTP/1.0", 1)
	return modified
		
def isConnect(message):
	return message.lower().startswith("connect")
