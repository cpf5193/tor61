# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpParser.py
# Interprets HTTP messages

import sys, threading, Tor61Log, string
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
  log.info("INITIAL MESSAGE: \n" + message)
  if message == "HTTP/1.0 200 OK\r\n\r\n":
    return message
  originalLines = message.splitlines(True)
  foundProxyKeepAlive = False
  foundConnectionKeepAlive = False
  foundHttp = False
  newLines = []
  if("HTTP/2.0" in originalLines[0]):
    originalLines[0] = originalLines[0].replace("HTTP/2.0", "HTTP/1.0", 1)
    foundHttp = True
  elif("HTTP/1.1" in originalLines[0]):
    originalLines[0] = originalLines[0].replace("HTTP/1.1", "HTTP/1.0", 1)
    foundHttp = True
  elif("HTTP/1.0" in originalLines[0]):
	  foundHttp = True
  
  for line in originalLines:
    if not foundConnectionKeepAlive:
      if line.startswith("Connection: "):
        next = line.replace("keep-alive", "close", 1)
        foundConnectionKeepAlive = True
        newLines.append(next)
        continue
    if not foundProxyKeepAlive:
      if line.startswith("Proxy-Connection: "):
        next = line.replace("keep-alive", "close", 1)
        foundProxyKeepAlive = True
        newLines.append(next)
        continue
    newLines.append(line)
  
  foundKeepAlive = foundProxyKeepAlive
  if foundHttp and not foundKeepAlive:
    newLines.insert(1, "Connection: close\n")
  
  modified = string.join(newLines, "")
  log.info("MODIFIED MESSAGE: \n" + modified)
  return modified
    
def isConnect(message):
  return message.lower().startswith("connect")
