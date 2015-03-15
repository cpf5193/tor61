# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpWriter.py
# Write thread for Http Proxy

import sys, threading, Tor61Log
from ProxyConnectionListener import ProxyConnectionListener
log = Tor61Log.getLog()
import Queue

class HttpWriter:
  BLOCK_TIMEOUT = 2
  #Store the socket that will be written to and created a buffer
  #to write from
  def __init__(self, sock, inputSource, remoteAddress, httpConnection):
    self.sock = sock
    self.remoteAddress = remoteAddress
    self.writeBuffer = inputSource
    self.httpConnection = httpConnection
    self.end = False
    
  #While there is data to be sent, send it
  def start(self):
    log.info("ready to write to " + str(self.sock.getpeername()))
    while not self.end:
      log.info("Getting from the buffer")
      nextItem = None
      try:
        nextItem = self.writeBuffer.get(True, self.BLOCK_TIMEOUT)
      except Queue.Empty:
        log.info("timeout")
        continue
      if nextItem is None:
        log.info("Received None from buffer, closing writer")
        self.stop()
      elif not self.end:
        try:
          self.sock.send(nextItem)
        except socket.err as msg:
          log.info(str(msg))
          self.stop()
        log.info("Sent: '" + nextItem.strip() + "'\n to " +
          str(self.remoteAddress))

    log.info("Exiting conn to " + str(self.remoteAddress) + 
      " (nextItem: " + str(nextItem) + ")")
    if self.httpConnection.reader.end:
      self.sock.close()
      self.httpConnection.killSelf()
      
  #Stops all activity
  def stop(self):
    self.end = True
