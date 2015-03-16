# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpConnection.py
# Stores a read thread, write thread, and thread-safe
# buffer for writing in an HttP Connection

import sys, threading, Tor61Log, HttpCellConverter, HttpParser, socket
from HttpReader import HttpReader
from HttpWriter import HttpWriter
import Queue

log = Tor61Log.getLog()

class HttpConnection:
  BLOCK_TIMEOUT = 2
  OK = "HTTP/1.0 200 OK\r\n\r\n"

  def __init__(self, sock, proxy, remoteAddress, streamId):
    self.writeBuffer = Queue.Queue()
    self.remoteAddress = remoteAddress
    self.sock = sock
    self.reader = HttpReader(sock, self, remoteAddress, streamId)
    self.writer = HttpWriter(sock, self.writeBuffer, remoteAddress,
     self, streamId)
    self.proxy = proxy
    self.isTunnel = False
    self.firstMessage = None
    self.end = False
    self.streamId = streamId
    
  #Make a connection from a router
  def openConnection(self):
    log.info("first message:\n" + str(self.firstMessage))
    if self.firstMessage is not None:
      self.proxy.converter.putHttp(self.firstMessage)
    readThread = threading.Thread(target=self.reader.start,
      args=())
    writeThread = threading.Thread(target=self.writer.start,
      args=())
    readThread.start()
    writeThread.start()

  #Asynchronous method for putting an HTTP message into the write
  #buffer
  def putHttp(self, message):
    log.info(message.strip())
    if not self.isTunnel:
      if HttpParser.isConnect(message):
        log.info("Detected Http CONNECT")
        self.isTunnel = True
        self.sock = socket.socket(socket.AF_INET, 
          socket.SOCK_STREAM)
        self.sock.connect(self.remoteAddress)
        self.sock.send(message)
        self.reader.sock = self.sock
        self.writer.sock = self.sock
        self.proxy.converter.putHttp((self.proxy.DATA, 
          (self.remoteAddress, self.streamId, self.OK)))
        return
      else:
        message = HttpParser.modifyMessage(message)
    log.info("enqueing for write " + message.strip())
    self.writeBuffer.put(message, True)
    
  #Set the message to be sent upon receiving CONNECTED
  def setFirstMessage(self, message):
    self.firstMessage = message
    log.info("Set first message to: \n" + self.firstMessage[1][2])
    
  #Stops all activity on worker threads
  def stop(self):
    log.info("")
    self.end = True
    self.reader.stop()
    self.writer.stop()
    
  #Stop and get out of dictionary
  def killSelf(self):
    log.info("");
    self.stop()
    self.proxy.removeConnection(self.remoteAddress, self.streamId);
    
