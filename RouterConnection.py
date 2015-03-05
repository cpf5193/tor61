import Router
import Queue, time

class RouterConnection(object):
  def __init__(self, router, circuitId, ip, port):
    self.buffer = Queue(100000)
    self.circuitId = circuitId
    self.router = router # The router that this RouterConnection is a part of
    self.ip = ip
    self.port = port
  
  #############################################
  ## Connection Functions
  #############################################
  def connectToRouter(self):
    # do a tcp connect to the specified router
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    errno = tcpSocket.connect_ex(self.ip, self.port)
    if not errno == 0:
      print "Failed to create tcp connection to first peer"
      sys.exit(1)
    print "TCP Connection created to %s:%s" % (self.ip, self.port)
    self.socket = tcpSocket

    #start the reader and writer threads
    # e.g. readFromRouter() && readFromBuffer()
    fromRouter = threading.Thread(target=readFromRouter, args=())
    fromRouter.start()
    toRouter = threading.Thread(target=readFromBuffer(), args=())
    toRouter.start()

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
      router.handleRouterMessage(routerMsg)
      # (origin router should process the message and decide what to do with it)

  def readFromBuffer():
    # need to come up with some way to listen to the queue other than
    # sitting in a loop and sleeping for some number of milliseconds

    # Take a queued message from the buffer and write to the router
    while(True):
      if (self.buffer.empty()):
        time.sleep(250)
      else:
        while(not self.buffer.empty()):
          msg = self.buffer.get()
          writeToRouter(msg)

  # Write to the remote router
  def writeToRouter(msg):
    # send the indicated message to the router
    # TODO: add try/catch
    try:
      self.socket.sendAll(msg)
    except:
      print "Failed to write to router"
      sys.exit(1)
