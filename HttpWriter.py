# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpWriter.py
# Write thread for an Http Proxy connection

import sys, threading, Tor61Log, socket
from ProxyConnectionListener import ProxyConnectionListener
log = Tor61Log.getLog()
import Queue

class HttpWriter:
  BLOCK_TIMEOUT = 2
  #Store the socket that will be written to and created a buffer
  #to write from
  def __init__(self, sock, inputSource, remoteAddress, httpConnection, streamId):
    self.sock = sock
    self.remoteAddress = remoteAddress
    self.writeBuffer = inputSource
    self.httpConnection = httpConnection
    self.end = False
    self.streamId = streamId
    
  #While there is data to be sent, send it
  def start(self):
    peer = str(self.remoteAddress)
    myname = str(self.sock.getsockname())

    log.info("ready to write to " + peer + " from " + myname)
    while not self.end:
      log.info("Getting from the buffer writing to " + peer + " from " + 
        myname)
      nextItem = None
      try:
        nextItem = self.writeBuffer.get(True, self.BLOCK_TIMEOUT)
      except Queue.Empty:
        log.info("timeout writing to " + peer + " from " + myname)
        continue
      if nextItem is None:
        log.info("Received None from buffer, closing writer to " + 
          peer + " from " + myname)
        try:
          self.sock.send("")
        except socket.error as msg:
          log.info(str(msg))
        self.stop()
      elif not self.end:
        try:
          self.sock.send(nextItem)
        except socket.error as msg:
          log.info(str(msg))
          self.stop()
        log.info("Sent: '" + nextItem.strip() + "'\n to " +
          peer + " from " + myname + " on " + str(self.streamId))

    log.info("Exiting conn to " + str(self.remoteAddress) + 
      " (nextItem: " + str(nextItem) + ") from " + myname + " on " +
        str(self.streamId))
    if self.httpConnection.reader.end:
      self.sock.close()
      self.httpConnection.killSelf()
      
  #Stops all activity
  def stop(self):
    self.end = True
