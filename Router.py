import CommandCellOpen, RelayCell, Cell, RouterConnection
import os, threading, subprocess, time, socket, re, sys
from random import randint

NEXT_CIRC_ID = 0x0003

class Router(object):
  #############################################
  ## Constructor
  #############################################
  def __init__(self, converter, groupNum, instanceNum, port):
    self.routingTable = {}
    self.timers = {}
    self.connections = {} #format: (ip, port) --> RouterConnection
    self.converter = converter
    self.groupNum = groupNum
    self.instanceNum = instanceNum
    self.port = port
    self.agentId = str((int(groupNum) << 16) | int(instanceNum))
    self.CMDS = {
      0x01: self.handleCreate,
      0x02: self.unexpectedCommand,
      0x03: self.unexpectedCommand,
      0x04: self.handleDestroy,
      0x05: self.handleOpen,
      0x06: self.unexpectedCommand,
      0x07: self.unexpectedCommand,
      0x08: self.unexpectedCommand
    }
    
    self.RELAY_CMDS = {
      0x01: self.handleBegin,
      0x02: self.handleData,
      0x03: self.handleEnd,
      0x04: self.unexpectedCommand,
      0x06: self.unexpectedCommand,
      0x07: self.unexpectedCommand,
      0x0b: self.unexpectedCommand,
      0x0c: self.unexpectedCommand
    }

    self.end = False

  #############################################
  ## Router startup functions
  #############################################
  def registerRouter(self):
    print "Registering router"
    string = "python registration_client.py %s Tor61Router-%s-%s %s" % (self.port, self.groupNum, self.instanceNum, self.agentId)
    print string
    thread = threading.Thread(target=os.system, args=(string,))
    thread.daemon = True
    thread.start()

  def createCircuit(self):
    print "Creating circuit (incomplete)"
    # Find three other routers and create a circuit
    peers = self.getPeers()
    print peers

    # Create an initial socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      s.connect((peers[0]['ip'], int(peers[0]['port'])))
    except:
      print "Cannot connect to %s:%s" % (peers[0]['ip'], peers[0]['port'])
    self.stop()

    # Create a new connection between this router and the first peer
    conn = RouterConnection.RouterConnection(self, 0x0000, peers[0]['ip'], peers[0]['port'], s)

    # Add this connection to the connection table
    self.connections[(peers[0]['ip'], peers[0]['port'])] = conn
    
    # Send an OPEN cell to the first peer
    self.doOpen(conn, peers[0]['data'])
    
    # Send a CREATE cell
    self.doCreate(conn, 0x0001)
    
    # Send a RELAY EXTEND cell x2 using the stream id 0x0000 
    # and the circuit id 0x0001
    self.doExtend(conn, peers[1])
    self.doExtend(conn, peers[2])

    print "Successfully created circuit with id 0x0001"

  def getPeers(self):
    print "fetching registered routers"
    string = "python fetch.py Tor61Router-%s-%s" % (self.groupNum, self.instanceNum)
    print string

    process = subprocess.Popen([string], stdout = subprocess.PIPE, shell=True)
    (output, err) = process.communicate()
    
    peers = output.splitlines()
    for i in range(0, len(peers)):
      peers[i] = peers[i].split('\t')

    print "peers found: ", peers

    circuitPeers = []
    for i in range(0, 3):
      randPeer = peers[randint(0, len(peers)-1)]
      peerObj = {}
      peerObj['ip'] = randPeer[0]
      peerObj['port'] = randPeer[1]
      peerObj['data'] = randPeer[2]
      circuitPeers.append(peerObj)
    print "circuitPeers: ", circuitPeers
    return circuitPeers

  def manageTimeouts(self):
    #create a new thread to manage the timer table,
    #checking if circuits have timed out and calling destroy if so
    print "Creating timeout manager (incomplete)"

  def start(self):
    self.registerRouter()
    # Start listening for other connections once the circuit is created
    connectionAccepter = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostbyname(socket.gethostname())
    print "host: %s" % host
    port = self.port
    connectionAccepter.bind((host, int(port)))
    connectionAccepter.listen(5)
    #threading.thread
    thread = threading.Thread(target=self.handleNewConnections, args=(connectionAccepter,))
    thread.daemon = True
    thread.start()
    time.sleep(1) #Allow time for the registration to happen
    #Should try to make sure there are available peers
    self.createCircuit()

  def handleNewConnections(self, connectionAccepter):
    nextEvenId = 0x0002
    while not self.end:
      try:
        print "Listening on %s:%s" % (socket.gethostbyname(socket.gethostname()), self.port)
        (conn, address) = connectionAccepter.accept()
        rc = RouterConnection.RouterConnection(self, nextEvenId, address[0], address[1], conn)
        self.connections[address] = rc
        nextEvenId += 2
      except socket.error:
        print "Socket error"
        continue

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
    cell = Cell.Cell(0x0000, 0x00)
    cell.setBuffer(msg)
    circuitId = cell.getCircuitId()
    cmdId = cell.getCmdId()

    # Call the handler method associated with the specified command
    if (cmdId == 0x03):
      relayCell = RelayCell.setBuffer(msg)
      relayCmd = relayCell.getRelayCmd()
      self.RELAY_CMDS[relayCmd](msg)
    else:
      self.CMDS[cmdId](msg, remoteIp, remotePort)

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
    print "openMsg: %s" % openMsg.toString()
    if not connection.writeToRouter(openMsg.toString()):
      print "Failed to send OPEN to router"
      sys.exit(1)
    print "written to router"
    if not self.end:
      reply = connection.readFromBuffer()
    if not self.end:
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
    if not connection.writeToRouter(createMsg.toString()):
      print "Failed to write to router"
      sys.exit(1)

    if not self.end:
      reply = connection.readFromBuffer()
    if not self.end:
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
    if not connection.writeToRouter(extendMsg.toString()):
      print "Failed to write to router"
      sys.exit(1)

    if not self.end:
      reply = connection.readFromBuffer()
    if not self.end:
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
      connections[(remoteIp, remotePort)].writeToRouter(openedCell.toString())
    else:
      # Generate an OPENED cell and send over the connection
      openedCell = CommandCellOpen.CommandCellOpen(0x0000, 0x06, remoteHost, localHost)
      connections[(remoteIp, remotePort)].writeToRouter(openedCell.toString())

  def handleCreate(self, msg, remoteIp, remotePort):
    # The received cell is a Create cell, establish the new circuit number by
    # Inserting an entry into the routing table as circId --> None
    cell = Cell.Cell.setBuffer(msg)
    circId = cell.getCircuitId()
    routingTable[(circId, (remoteIp, remotePort))] = None

    # Generate a CREATED cell and send back
    createdCell = Cell.Cell(circId, 0x02)
    connections[(remoteIp, remotePort)].writeToRouter(createdCell.toString())

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
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
          s.connect((ip, int(port)))
        except:
          "Failed to connect to %s:%s" % (ip, port)
          self.stop()

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
      connections[(ip, port)].writeToRouter(extendCell.toString())
      self.routingTable[routingKey] = (NEXT_CIRC_ID, (ip, port))
      self.routingTable[(NEXT_CIRC_ID, (ip, port))] = routingKey
      NEXT_CIRC_ID += 2
    else:
      # Pass on the relay extend as indicated in the routing table
      self.connections[(ip, port)].writeToRouter(cell.toString())

  def unexpectedCommand():
    print "Received unexpected command"
    sys.exit(1)

  def stop(self):
    self.end = True
    for key in self.connections:
      # TODO: Send DESTROY cell to all circuits connected to router
      self.connections[key].stop()
      self.connections.remove(key)
