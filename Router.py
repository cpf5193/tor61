import CommandCellOpen, RelayCell, Cell, RouterConnection
import os, threading, subprocess, time, socket, re
from random import randint

class Router(object):
  #############################################
  ## Constructor
  #############################################
  CMDS = {
    0x01: handleCreate,
    0x02: handleCreated,
    0x03: handleRelay,
    0x04: handleDestroy,
    0x05: handleOpen,
    0x06: handleOpened,
    0x07: handleOpenFailed,
    0x08: handleCreateFailed
  }

  RELAY_CMDS = {
    0x01: handleBegin,
    0x02: handleData,
    0x03: handleEnd,
    0x04: handleConnected,
    0x06: handleExtend,
    0x07: handleExtended,
    0x0b: handleBeginFailed,
    0x0c: handleExtendFailed
  }

  NEXT_CIRC_ID = 0x0003

  def __init__(self, converter, groupNum, instanceNum, port):
    self.routingTable = {}
    self.timers = {}
    self.connections = {} #format: (ip, port) --> RouterConnection
    self.converter = converter
    self.groupNum = groupNum
    self.instanceNum = instanceNum
    self.port = port
    self.agentId = (groupNum << 16) | instanceNum

  #############################################
  ## Router startup functions
  #############################################
  def registerRouter(self):
    print "Registering router"
    string = "python registration_client.py %s Tor61Router-%s-%s %s" % (self.port, self.groupNum, self.instanceNum, self.agentId)
    print string
    thread = threading.Thread(target=os.system, args=(string,))
    thread.start()

  def createCircuit(self):
    print "Creating circuit (incomplete)"
    # Find three other routers and create a circuit
    peers = self.getPeers()

    # Create an initial socket
    s = socket.socket(AF_INET, SOCK_STREAM)
    s.connect(peers[0]['ip'], peers[0]['port'])

    # Create a new connection between this router and the first peer
    conn = RouterConnection.RouterConnection(self, 0x0000, peers[0]['ip'], peers[0]['port'], s)

    # Add this connection to the connection table
    connections[(peers[0]['ip'], peers[0]['port'])] = conn
    
    # Send an OPEN cell to the first peer
    self.doOpen(conn, peers[0]['data'])
    
    # Send a CREATE cell
    self.doCreate(conn, 0x0001)
    
    # Send a RELAY EXTEND cell x2 using the stream id 0x0000 
    # and the circuit id 0x0001
    self.doExtend(conn, peers[1])
    self.doExtend(conn, peers[2])

    print "Successfully created circuit with id 0x0001"
    
    # Start listening for other connections once the circuit is created
    connectionAccepter = socket.socket(AF_INET, SOCK_STREAM)
    host = socket.getHostName()
    port = self.port
    socket.bind((host, port))
    socket.listen(5)
    while(True):
      (conn, address) = socket.accept()
      rc = RouterConnection.RouterConnection(self, NEXT_CIRC_ID, address[0], address[1], conn)
      connections[address] = rc
      NEXT_CIRC_ID += 2

  def getPeers(self):
    print "fetching registered routers"
    string = "python fetch.py Tor61Router-%s" % self.groupNum
    print string

    process = subprocess.Popen([string], stdout = subprocess.PIPE, shell=True)
    (output, err) = process.communicate()
    
    peers = output.splitlines()
    for i in range(0, len(peers)):
      peers[i] = peers[i].split('\t')

    circuitPeers = []
    for i in range(0, 3):
      randPeer = peers[randint(0, len(peers)-1)]
      peerObj = {}
      peerObj['ip'] = randPeer[0]
      peerObj['socket'] = randPeer[1]
      peerObj['data'] = randPeer[2]
      circuitPeers.append(peerObj)
    print "circuitPeers: ", circuitPeers

  def manageTimeouts(self):
    #create a new thread to manage the timer table,
    #checking if circuits have timed out and calling destroy if so
    print "Creating timeout manager (incomplete)"

  def start(self):
    self.registerRouter()
    time.sleep(2) #Allow time for the registration to happen
    #Should try to make sure there are available peers
    self.createCircuit()
    
    print "Starting the router"
    # Start listening for other connections once the circuit is created
    connectionAccepter = socket.socket(AF_INET, SOCK_STREAM)
    host = socket.getHostName()
    port = self.port
    socket.bind((host, port))
    socket.listen(5)
    circuitId = 0x0003
    while(True):
      (conn, address) = socket.accept()
      rc = RouterConnection.RouterConnection(self, circuitId, address[0], address[1], conn)
      connections[address] = rc

  #############################################
  ## Reading/Delegating functions
  #############################################
  def handleProxyMessage(self):
    # Take a message from the converter and place it into the appropriate
    # buffer using RouterConnection's writeToBuffer
    print "Handling message from proxy side (incomplete)"

  def handleRouterMessage(self, msg, remoteIp, remotePort):
    # Accept a message from a RouterConnection, process it, and send it either to
    # the converter or to another router connection's buffer
    print "Handling message from router buffer (incomplete)"

    # Extract the cell type from the Cell
    cell = Cell.setBuffer(msg)
    circuitId = cell.getCircuitId()
    cmdId = cell.getCmdId()

    # Call the handler method associated with the specified command
    if (cmdId == 0x03):
      relayCell = RelayCell.setBuffer(msg)
      relayCmd = relayCell.getRelayCmd()
      RELAY_CMDS[relayCmd](msg)
    else:
      CMDS[cmdId](msg, remoteIp, remotePort)

  #############################################
  ## Destruction functions
  #############################################
  def destroyCircuit(self, circuitId):
    # Destroy the specified circuit
    print "Destroying circuit #%x (incomplete)" % circuitId
  
  #############################################
  ## Circuit Creation Send Message functions
  #############################################
  def doOpen(self, connection, toAgentId):
    openMsg = CommandCellOpen.CommandCellOpen(0x0000, 0x05, self.agentId, toAgentId)
    if not connection.writeToRouter(openMsg.getBuffer()):
      print "Failed to send OPEN to router"
      sys.exit(1)
    reply = connection.readFromBuffer()
    replyMsg = CommandCellOpen.setBuffer(reply)
    msgType = replyMsg.getCmdId()
    if (msgType == 0x06):
      #Opened cell
      print "OPENED cell received"
    elif (msgType == 0x07):
      print "ERROR: received OPEN FAILED cell"
      #We may be able to improve this by picking a different peer and trying
      # to do an open before giving up
      sys.exit(1)
    else:
      print "ERROR: unexpected command type in response to OPEN"
      sys.exit(1)

  def doCreate(self, connection, circuitId):
    createMsg = Cell.Cell(circuitId, 0x01)
    if not connection.writeToRouter(createMsg.getBuffer()):
      print "Failed to write to router"
      sys.exit(1)
    reply = connection.readFromBuffer()
    replyMsg = Cell.setBuffer(reply)
    msgType = replyMsg.getCmdId()
    if (msgType == 0x02):
      print "CREATED cell received"
      #Add the mapping of (circuitId, (ip:port)) --> (circuitId, (ip:port))
      #to the routing table
      key = None
      value = (connection.circuitId, (connection.ip, connection.port))
      self.routingTable[key] = value
    elif (msgType == 0x08):
      print "CREATE FAILED cell received"
      sys.exit(1)
    else:
      print "ERROR: unexpected command type in response to CREATE"
      sys.exit(1)
  
  def doExtend(self, connection, peerArr):
    bodyString = "%s:%s\0%s" % (peerArr['ip'], peerArr['port'], peerArr['data'])
    extendMsg = RelayCell.RelayCell(0x0001, 0x0000, len(bodyString), 0x06, bodyString)
    if not connection.writeToRouter(extendMsg.getBuffer()):
      print "Failed to write to router"
      sys.exit(1)
    reply = connection.readFromBuffer()
    replyMsg = RelayCell.setBuffer(reply)
    msgType = replyMsg.getCmdId()
    if not (msgType == 0x03):
      print "ERROR: expected RELAY cell type, received %s" % msgType
      sys.exit(1)
    relayType = replyMsg.getRelayCmd()
    if (relayType == 0x07):
      print "EXTENDED cell received"
    elif (relayType == 0x0c):
      print "EXTEND FAILED cell received"
      sys.exit(1)
    else:
      print "ERROR: unexpected command type in response to EXTEND"
      sys.exit(1)
      

  #############################################
  ## Handle Message Functions
  #############################################
  def handleOpen(self, msg, remoteIp, remotePort):
    # If we receive an open cell, check for an open tcp connection
    # to the specified router and if it exists send back an 'Opened' cell
    cell = CommandCellOpen.setBuffer(msg)
    remoteHost = cell.getOpenerId()
    localHost = cell.getOpenedId()
    if (localHost != self.agentId):
      print "Open cell received by wrong host"
      sys.exit(1)
    elif (remoteIp, remotePort) not in connections:
      print "Open request sent on invalid connection"
      #Send OPEN FAILED
      failedCell = CommandCellOpen.CommandCellOpen(cell.getCircuitId, 0x07, remoteHost, localHost)
      connections[(remoteIp, remotePort)].writeToRouter(openedCell.getBuffer())
    else:
      # Generate an OPENED cell and send over the connection
      openedCell = CommandCellOpen.CommandCellOpen(0x0000, 0x06, remoteHost, localHost)
      connections[(remoteIp, remotePort)].writeToRouter(openedCell.getBuffer())

  def handleCreate(self, msg, remoteIp, remotePort):
    # The received cell is a Create cell, establish the new circuit number by
    # Inserting an entry into the routing table as circId --> None
    cell = Cell.setBuffer(msg)
    circId = cell.getCircuitId()
    routingTable[(circId, (remoteIp, remotePort))] = None

    # Generate a CREATED cell and send back
    createdCell = Cell.Cell(circId, 0x02)
    connections[(remoteIp, remotePort)].writeToRouter(createdCell.getBuffer())

  def handleDestroy(self, msg, remoteIp, remotePort):
    # The received cell is a Destroy cell, do appropriate logic
    return

  def handleBegin(self, msg, remoteIp, remotePort):
    # The received cell is a relay begin cell, do appropriate logic
    return

  def handleData(self, msg, remoteIp, remotePort):
    # The received cell is a relay data cell, do appropriate logic
    return

  def handleEnd(self, msg, remoteIp, remotePort):
    # The received cell is a relay end cell, do appropriate logic
    return

  def handleConnected(self, msg, remoteIp, remotePort):
    # The received cell is a relay connected cell, do appropriate logic
    return

  def handleExtend(self, msg, remoteIp, remotePort):
    cell = RelayCell.setBuffer(msg)
    bodyString = cell.getBody()
    (ip, port, aid) = re.split('\0:', bodyString)
    
    routingKey = (cell.getCircuitId(), (remoteIp, remotePort))

    if routingKey not in self.routingTable:
      print "Invalid destination in RELAY EXTEND"
      sys.exit(1)
    elif self.routingTable[routingKey] == None:
      # The extend is meant for this router, do the extend
      createCell = Cell.Cell(cell.getCircuitId(), cell.getCmdId())

      # Create a connection between this router and the next one
      if (ip, port) not in connections:
        # Create a new socket
        s = socket.socket(AF_INET, SOCK_STREAM)
        s.connect(ip, port)
        # Create a new connection between this router and the specified peer
        conn = RouterConnection.RouterConnection(self, NEXT_CIRC_ID, ip, port, s)
        # Add this connection to the connection table
        connections[(ip, port)] = conn
        # Open the TCP connection
        doOpen(conn, aid)
      doCreate(connections[(ip, port)], NEXT_CIRC_ID)
      # TODO: create and catch exception in doCreate so we can report
      # an EXTEND FAILED when the create fails
      extendCell = RelayCell.RelayCell(NEXT_CIRC_ID, cell.getStreamId(), 0, 0x07)
      connections[(ip, port)].writeToRouter(extendCell.getBuffer())
      self.routingTable[routingKey] = (NEXT_CIRC_ID, (ip, port))
      NEXT_CIRC_ID += 2
    else:
      # Pass on the relay extend as indicated in the routing table
      self.connections[(ip, port)].writeToRouter(cell.getBuffer())
