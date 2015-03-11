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
    buffer.put(msg)

  # Read from the remote router
  def readFromRouter(self):
    while not self.end:
      try:
        log.info("Listening on router %s:%s" % (self.ip, self.port))
        routerMsg = self.socket.recv(Cell.LENGTH)
        if not self.end:
          self.router.handleRouterMessage(routerMsg, self.ip, self.port)
      except socket.timeout:
        log.info("Socket timeout")
        continue
        # (origin router should process the message and decide what to do with it)

  def readFromBuffer(self):
    log.info("reading from buffer: ")
    if not self.end:
      try:
        return self.buffer.get(True, self.BLOCK_TIMEOUT) # blocking operation
      except Queue.Empty:
        log.info("Queue timeout")
     
  # Write to the remote router
  def writeToRouter(self, msg):
    # send the indicated message to the router
    if self.end:
      return False
    try:
      log.info("Trying to send msg %s over socket %s:%s " % (msg, self.ip, self.port))
      self.socket.sendall(msg)
      return True
    except socket.error as msg:
      log.info("Failed to write to router: " % msg)
      return False

  def stop(self):
    self.end = True
    self.disconnectFromRouter()
