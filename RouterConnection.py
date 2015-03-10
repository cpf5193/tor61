import Router
import Queue, time

class RouterConnection(object):
  def __init__(self, router, circuitId, ip, port, socket):
    self.buffer = Queue(100000)
    self.circuitId = circuitId
    self.router = router # The router that this RouterConnection is a part of
    self.ip = ip
    self.port = port
    self.socket = socket
    self.startThreads()
  
  #############################################
  ## Connection Functions
  #############################################
  
  def startThreads(self):
    #start the reader and writer threads
    # e.g. readFromRouter() && readFromBuffer()
    fromRouter = threading.Thread(target=readFromRouter, args=())
    fromRouter.start()
    #toRouter = threading.Thread(target=readFromBuffer(), args=())
    #toRouter.start()

  def disconnectFromRouter():
    #send a message to router first?
    self.socket.close()
    self.socket = None

  #############################################
  ## Read/Write Functions
  #############################################
  def writeToBuffer(msg):
    buffer.put(msg)

  # Read from the remote router
  def readFromRouter():
    while(True):
      routerMsg = self.socket.recv(Cell.LENGTH)
      router.handleRouterMessage(routerMsg, self.ip, self.port)
      # (origin router should process the message and decide what to do with it)

  def readFromBuffer():
    return self.buffer.get(true) # blocking operation
     
  # Write to the remote router
  def writeToRouter(msg):
    # send the indicated message to the router
    try:
      self.socket.sendAll(msg)
      return true
    except:
      print "Failed to write to router"
      return false
