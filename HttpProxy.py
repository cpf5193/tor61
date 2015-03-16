# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# HttpProxy.py
# Stores a list of HTTP Connections that communicate with both
# their peers and the Tor router

import sys, threading, Tor61Log, HttpCellConverter, Queue, HttpParser, socket
from ProxyConnectionListener import ProxyConnectionListener
from HttpConnection import HttpConnection

log = Tor61Log.getLog()

class HttpProxy:
  BLOCK_TIMEOUT = 2
  streamId = 1
  BEGIN = 1
  DATA = 2
  END = 3
  CONNECTED = 4
  FAIL = 11
  READ_SIZE = 498
  
  #Initialize port that listens for new Proxy connections  
  def __init__(self, listenerPort):
    self.connections = {}
    self.listener = ProxyConnectionListener(listenerPort, self)
    self.converter = HttpCellConverter.getConverter()
    self.end = False

  #Store the connection in the connection lists
  def processConnectionFromBrowser(self, conn, addr):
    log.info((conn, addr))
    t = threading.Thread(target=self.processConnectionFromBrowserWorker,
      args=(conn, addr))
    t.start()
    
  #Worker thread
  def processConnectionFromBrowserWorker(self, conn, addr):
    log.info(addr)
    remoteAddress = conn.getpeername()
    host, streamId = remoteAddress
    self.connections[(addr, streamId)] = HttpConnection(conn, self, addr,
			streamId)
    while not self.connections[(addr, streamId)].end:
      try:
        firstMessage = conn.recv(self.READ_SIZE)
        if len(firstMessage) == 0:
          log.info("First message was empty, killing " + str(addr) + " " +
						str(streamId))
          self.connections[(addr, streamId)].killSelf()
          break
        else:
          break
      except socket.timeout:
        log.info("timeout")
        continue
    log.info("Got first message:\n" + firstMessage)
    hostPort = HttpParser.getHostAndPort(firstMessage)
    if hostPort is not None:
      self.connections[(addr, streamId)].setFirstMessage(((self.DATA, (addr, 
        streamId, firstMessage))))
      host, port = hostPort
      body = host + ":" + str(port) + "\0"
      beginMessage = (self.BEGIN, (addr, streamId, body))
      self.converter.putHttp(beginMessage)
    else:
      log.info("Couldn't get HostPort, killing " + str(addr) + " " +
				str(streamId))
      self.connections[(addr, streamId)].killSelf()
    
  #Get a connection from a tor router
  def processConnectionFromRouter(self, addr, streamId):
    log.info(addr)
    serverSocket = socket.socket(socket.AF_INET, 
      socket.SOCK_STREAM)
    try:
      log.info("Attempting to connect to " + str(addr))
      serverSocket.connect(addr)
    except socket.error as (errno, msg):
      log.info(msg)
      self.converter.putHttp((self.FAIL, (addr, streamId, "")))
      return
    log.info("Connected to " + str(addr) + " " + str(streamId))
    self.converter.putHttp((self.CONNECTED, (addr, streamId, "")))
    self.connections[(addr, streamId)] = HttpConnection(serverSocket, 
			self, addr, streamId)
    self.connections[(addr, streamId)].openConnection()
    
  #Add connections to the connection list as they arrive
  def awaitConnections(self):
    self.awaitConvertedCells()
    thread = threading.Thread(target=self.listener.start, args=())
    thread.start()
    log.info("started")

  #Get an Http message that has been converted from the router
  def getHttpFromRouter(self):
    httpOutputBuffer = self.converter.getHttpOutputBuffer()
    return httpOutputBuffer.get(True, self.BLOCK_TIMEOUT)
    
  #Await incoming converted Tor cells
  def awaitConvertedCells(self):
    self.thread = threading.Thread(target=self.awaitConvertedCellsWorker)
    self.thread.start()
    
  #Worker thread for awaiting converted Tor cells
  def awaitConvertedCellsWorker(self):
    while(not self.end):
      nextItem = None
      try:
        nextItem = self.getHttpFromRouter()
      except Queue.Empty:
        log.info("timeout")
        continue
      self.delegateMessage(nextItem)
    
  #Interpret DATA, BEGIN, and END  
  def delegateMessage(self, message):
    log.info(message)
    command, payload = message
    addr, streamId, body = payload
    key = (addr, streamId)
    log.info(str(addr) + " " + str(streamId))
    if command == self.DATA:
      log.info("Recieved DATA")
      if key in self.connections:
        self.connections[key].putHttp(body)
      else:
        log.info("No connection for " + str(addr) + " " +
					str(streamId))
    if command == self.BEGIN:
      t = threading.Thread(target=self.processConnectionFromRouter,
        args=(addr, streamId))
      t.start()
    if command == self.END:
      if key in self.connections:
        self.connections[key].writeBuffer.put(None, True)
    if command == self.CONNECTED:
      if key in self.connections:
        self.connections[key].openConnection()
    if command == self.FAIL:
      if key in self.connections:
        self.connections[key].killSelf()

  #Stop all activity
  def stop(self):
    self.listener.stop()
    self.end = True
    for conn in self.connections:
      self.connections[conn].stop()
  
  #Removes a connection identified by streamId    
  def removeConnection(self, addr, streamId):
    log.info(str(addr) + " " + str(streamId))
    if addr in self.connections:
      del self.connections[addr]
        
#Run this module alone as a test giving it a port as an argument
if(__name__ == "__main__"):
  import DummyRouter
  HttpCellConverter.getConverter().start()
  proxy = HttpProxy(int(sys.argv[1]))
  tor = DummyRouter.DummyRouter()
  tor.start()
  proxy.awaitConnections()
  stop = False
  while(not stop):
    try:
      for line in sys.stdin:
        print line
    except KeyboardInterrupt:
      log.info("Keyboard Interrupt")
      log.info(str(proxy.connections))
      stop = True
      proxy.stop()
      tor.stop()
      HttpCellConverter.getConverter().stop()
