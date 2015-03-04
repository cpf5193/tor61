import Router

class RouterConnection(object):
  def __init__(self, router, circuitId, port):
    self.buffer = {} #some type of threadsafe queue
    self.circuitId = circuitId
    self.router = router # The router that this RouterConnection is a part of
    self.port = port
    #start the reader and writer threads
    # e.g. readFromRouter() && readFromBuffer()

  #############################################
  ## Connection Functions
  #############################################
  def connectToRouter(circuitId, port):
    # do a tcp connect to the specified router
    return

  def disconnectFromRouter(hostname, port):
    # destroy the tcp connection to this router
    return

  #############################################
  ## Read/Write Functions
  #############################################
  def writeToBuffer(msg):
    #insert msg into buffer
    return

  # Read from the remote router
  def readFromRouter():
    # read from the router and call the router's function to process the message
    handleRouterMessage(msg)
    # (origin router should process the message and decide what to do with it)

  def readFromBuffer():
    # Take a queued message from the buffer and write to the Router
    writeToRouter(msg)

  # Write to the remote router
  def writeToRouter(msg):
    # send the indicated message to the router
    return
