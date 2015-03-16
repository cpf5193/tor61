# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpReader.py
# Read thread for an Http Proxy connection

import sys, threading, Tor61Log, HttpCellConverter, socket, HttpParser
from ProxyConnectionListener import ProxyConnectionListener
log = Tor61Log.getLog()

READ_SIZE = 498

class HttpReader:
  BLOCK_TIMEOUT = 2
  DATA_CMD = 2
  END_CMD = 3
  #Store the socket that we will be reading from
  def __init__(self, sock, httpConnection, remoteAddress, streamId):
    self.sock = sock
    self.converter = HttpCellConverter.getConverter()
    self.httpConnection = httpConnection
    self.remoteAddress = remoteAddress
    self.end = False
    self.streamId = streamId
    
  #Read from the socket as long as there is data
  def start(self):
    myname = str(self.sock.getsockname())
    peer = str(self.remoteAddress)
    
    log.info("starting read from " + str(self.remoteAddress) +
     " into " + myname)

    while(not self.end):
      message = None
      self.sock.settimeout(self.BLOCK_TIMEOUT)
      try:
        message = self.sock.recv(READ_SIZE)
        if(len(message) == 0):
          log.info("received empty message from " + 
            peer + " into " + myname + " on " + str(self.streamId))
          self.converter.putHttp((self.END_CMD, 
            (self.remoteAddress, self.streamId, "")))
          self.stop()
      except socket.timeout:
        log.info("timeout reading " + peer +
          " into " + myname)
        continue
      except socket.error as msg:
        log.info(msg)
        self.httpConnection.killSelf()
      if not self.end:
        log.info("Received: '" + message.strip() + "' " +
          "from " + peer + " into " + myname + " on " + str(self.streamId))
        if not self.httpConnection.isTunnel:
          if HttpParser.isConnect(message):
            self.httpConnection.isTunnel = True
        self.converter.putHttp((self.DATA_CMD, 
          (self.remoteAddress, self.streamId, message)))
    if(self.httpConnection.writer.end):
      self.sock.close()
      self.httpConnection.killSelf()
        
  
  #Stops all activity
  def stop(self):
    self.end = True
