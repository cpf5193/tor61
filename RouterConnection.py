import Router, Cell, Tor61Log
import Queue, time, threading, socket

log = Tor61Log.getLog()

class RouterConnection(object):

  def __init__(self, router, circuitId, ip, port, socket):
    self.buffer = Queue.Queue(100000)
    self.circuitId = circuitId
    self.router = router # The router that this RouterConnection is a part of
    self.ip = ip
    self.port = port
    self.socket = socket
    self.end = False
    self.BLOCK_TIMEOUT = 3.5
    self.startThreads()
  
  #############################################
  ## Connection Functions
  #############################################
  
  def startThreads(self):
    #start the reader and writer threads
    # e.g. readFromRouter() && readFromBuffer()
    fromRouter = threading.Thread(target=self.readFromRouter, args=())
    fromRouter.daemon = True
    fromRouter.start()
    #toRouter = threading.Thread(target=self.readFromBuffer(), args=())
    #toRouter.start()

  def disconnectFromRouter(self):
    #send a message to router first?
    self.socket.close()
    self.socket = None

  #############################################
  ## Read/Write Functions
  #############################################
  def writeToBuffer(self, msg):
    #self.buffer.put(msg)
    self.router.connections[(self.ip, self.port)].buffer.put(msg)
    #log.info("queue: ")
    #log.info(self.buffer)
    #log.info("RouterConnection:")
    #log.info(self)
    #log.info("queue size: %d" % self.buffer.qsize())

  # Read from the remote router
  def readFromRouter(self):
    while not self.end:
      try:
        log.info("Listening for messages from router at socket %s:%s" % (self.ip, self.port))
        routerMsg = self.socket.recv(Cell.LENGTH)
        if not self.end:
          log.info("self.ip: %s, self.port: %s" % (self.ip, self.port))
          log.info("socket.ip: %s, socket.port: %s" % self.socket.getsockname())
          sockinfo = self.socket.getsockname()
          self.router.handleRouterMessage(routerMsg, sockinfo[0], str(sockinfo[1]))
      except socket.timeout:
        log.info("Socket timeout")
        continue
        # (origin router should process the message and decide what to do with it)

  def readFromBuffer(self):
    log.info("reading from buffer")
    #log.info(self.buffer)
    if not self.end:
      try:
        return self.buffer.get(True, self.BLOCK_TIMEOUT) # blocking operation
      except Queue.Empty:
        #log.info("queue: ")
        #log.info(self.buffer)
        #log.info("RouterConnection: ")
        #log.info(self)
        #log.info("router reference: ")
        #log.info(self.router)
        #log.info("queue size: %d" % self.buffer.qsize())
        log.info("Queue timeout")
     
  # Write to the remote router
  def writeToRouter(self, msg):
    # send the indicated message to the router
    if self.end:
      return False
    try:
      #log.info("Trying to send msg over socket %s:%s " % (self.ip, self.port))
      self.socket.sendall(msg)
      return True
    except socket.error as msg:
      log.info("Failed to write to router: %s" % msg)
      return False
    log.info("written to router")

  def stop(self):
    self.end = True
    self.disconnectFromRouter()
