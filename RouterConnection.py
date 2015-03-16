# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# RouterConnection.py
# Stores a connection between the parent Tor router
# and a remote Tor router

import Router, Cell, Tor61Log
import Queue, time, threading, socket

log = Tor61Log.getLog()

class RouterConnection(object):

  def __init__(self, router, circuit
  Id, ip, port, socket):
    self.buffer = Queue.Queue(100000)
    self.circuitId = circuitId
    self.router = router # The router that this RouterConnection is a part of
    self.remoteIp = ip
    self.remotePort = port
    self.socket = socket
    self.BLOCK_TIMEOUT = 2
    socket.settimeout(self.BLOCK_TIMEOUT)
    self.end = False
    self.readStopped = False
    self.writeStopped = False
    self.startThreads()
  
  #############################################
  ## Connection Functions
  #############################################
  
  #Begins the read and write threads
  def startThreads(self):
    #start the reader and writer threads
    # e.g. readFromRouter() && readFromBuffer()
    fromRouter = threading.Thread(target=self.readFromRouter, args=())
    fromRouter.start()
    toRouter = threading.Thread(target=self.bufferToRouter, args=())
    toRouter.start()

	#Remotes this Connection from the parent router
  def disconnectFromRouter(self):
    #send a message to router first?
    self.socket.close()
    self.socket = None

  #############################################
  ## Read/Write Functions
  #############################################
  
  #Places a cell to be written out of the connection 
  def writeToBuffer(self, msg):
    self.router.connections[(self.remoteIp, self.remotePort)].buffer.put(msg)

  # Read from the remote router
  def readFromRouter(self):
    while not self.end:
      try:
        log.info("Listening for messages from router at socket %s:%d" % self.socket.getsockname())
        routerMsg = self.socket.recv(Cell.LENGTH)
        if not self.end:
          log.info("self.remoteIp: %s, self.remotePort: %s" % (self.remoteIp, self.remotePort))
          log.info("socket.ip: %s, socket.port: %s" % self.socket.getsockname())
          self.router.handleRouterMessage(routerMsg, self.remoteIp, self.remotePort)
      except socket.timeout:
        log.info("Socket timeout")
        continue
        # (origin router should process the message and decide what to do with it)
    self.readStopped = True
    log.info("ended readFromRouter")

  # Logically, this is the write thread
  def bufferToRouter(self):
    log.info("reading from buffer")
    while not self.end:
      try:
        item = self.buffer.get(True, self.BLOCK_TIMEOUT)
        self.socket.sendall(item)
      except Queue.Empty:
        log.info("Queue timeout, self.end: %s" % self.end)
        continue
    self.writeStopped = True
    log.info("ended bufferToRouter")

  #Gets the next item in the write buffer
  def readFromBuffer(self):
    log.info("reading from buffer")
    if not self.end:
      try:
        return self.buffer.get(True, self.BLOCK_TIMEOUT) # blocking operation
      except Queue.Empty:
        log.info("Queue timeout")
    log.info("ended readFromBuffer")

  #Indicates that the read and write threads should terminate
  def stop(self):
    log.info("calling stop on RouterConnection")
    self.end = True
