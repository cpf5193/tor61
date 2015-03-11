import CommandCellOpen, RelayCell, Cell, RouterConnection, Tor61Log
import os, threading, subprocess, time, socket, re, sys
from random import randint
from struct import pack

log = Tor61Log.getLog()

NEXT_CIRC_ID = 3

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
      '0x1': self.handleCreate,
      '0x2': self.unexpectedCommand,
      '0x3': self.unexpectedCommand,
      '0x4': self.handleDestroy,
      '0x5': self.handleOpen,
      '0x6': self.unexpectedCommand,
      '0x7': self.unexpectedCommand,
      '0x8': self.unexpectedCommand
    }
    
    self.RELAY_CMDS = {
      '0x1': self.handleBegin,
      '0x2': self.handleData,
      '0x3': self.handleEnd,
      '0x4': self.unexpectedCommand,
      '0x6': self.unexpectedCommand,
      '0x7': self.unexpectedCommand,
      '0xb': self.unexpectedCommand,
      '0xc': self.unexpectedCommand
    }

    self.end = False

  #############################################
  ## Router startup functions
  #############################################
  def registerRouter(self):
    log.info("Registering router")
    string = "python registration_client.py %s Tor61Router-%s-%s %s" % (self.port, self.groupNum, self.instanceNum, self.agentId)
    log.info(string)
    thread = threading.Thread(target=os.system, args=(string,))
    thread.daemon = True
    thread.start()

  def createCircuit(self):
    log.info("Creating circuit")
    # allow time for new connection accepter to start and for the registration to propagate
    time.sleep(1)
    # Find three other routers and create a circuit
    peers = self.getPeers()
    log.info("peers: ")
    log.info(peers)

    # Create an initial socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      s.connect((peers[0]['ip'], int(peers[0]['port'])))
    except:
      log.info("Cannot connect to %s:%s" % (peers[0]['ip'], peers[0]['port']))

    # Create a new connection between this router and the first peer
    conn = RouterConnection.RouterConnection(self, 0, peers[0]['ip'], peers[0]['port'], s)

    log.info("initial conn: ")
    log.info(conn)

    # Add this connection to the connection table
    self.connections[(peers[0]['ip'], peers[0]['port'])] = conn
    
    # Send an OPEN cell to the first peer
    self.doOpen(conn, peers[0]['data'])
    
    # Send a CREATE cell
    self.doCreate(conn, 1)
    
    # Send a RELAY EXTEND cell x2 using the stream id 0 
    # and the circuit id 1
    self.doExtend(conn, peers[1])
    self.doExtend(conn, peers[2])

    log.info("Successfully created circuit with id 1")

  def getPeers(self):
    log.info("fetching registered routers")
    string = "python fetch.py Tor61Router-%s-%s" % (self.groupNum, self.instanceNum)
    log.info(string)

    process = subprocess.Popen([string], stdout = subprocess.PIPE, shell=True)
    (output, err) = process.communicate()
    
    peers = output.splitlines()
    for i in range(0, len(peers)):
      peers[i] = peers[i].split('\t')

    log.info("peers found: ")
    log.info(peers)

    circuitPeers = []
    for i in range(0, 3):
      randPeer = peers[randint(0, len(peers)-1)]
      peerObj = {}
      peerObj['ip'] = randPeer[0]
      peerObj['port'] = randPeer[1]
      peerObj['data'] = randPeer[2]
      circuitPeers.append(peerObj)
    log.info("circuitPeers: ")
    log.info(circuitPeers)
    return circuitPeers

  def manageTimeouts(self):
    #create a new thread to manage the timer table,
    #checking if circuits have timed out and calling destroy if so
    log.info("Creating timeout manager (incomplete)")

  def start(self):
    self.registerRouter()
    # Start listening for other connections once the circuit is created
    connectionAccepter = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostbyname(socket.gethostname())
    log.info("host: %s" % host)
    port = self.port
    connectionAccepter.bind((host, int(port)))
    connectionAccepter.listen(5)
    
    thread = threading.Thread(target=self.createCircuit, args = ())
    thread.daemon = True
    thread.start()
    self.handleNewConnections(connectionAccepter)
    
  def handleNewConnections(self, connectionAccepter):
    nextEvenId = 2
    while not self.end:
      try:
        log.info("socket at %s:%s listening for new connections" % (socket.gethostbyname(socket.gethostname()), self.port))
        (conn, address) = connectionAccepter.accept()
        log.info("handled connection: ")
        log.info(conn)
        log.info("Connection accepted %s:%s", address[0], address[1])
        rc = RouterConnection.RouterConnection(self, nextEvenId, address[0], address[1], conn)
        self.connections[address] = rc
        nextEvenId += 2
      except socket.error:
        log.info("Socket error")
        continue
    log.info("self.end: %s" % self.end) 

  #############################################
  ## Reading/Delegating functions
  #############################################
  def handleProxyMessage(self):
    # Take a message from the converter and place it into the appropriate
    # buffer using RouterConnection's writeToBuffer
    log.info("Handling message from proxy side (incomplete)")

  def handleRouterMessage(self, msg, remoteIp, remotePort):
    # Accept a message from a RouterConnection, process it, and send it either to
    # the converter or to another router connection's buffer
    log.info("Handling message from router buffer!")

    # Extract the cell type from the Cell
    cell = Cell.Cell(0, 0)
    log.info("msg: %s" % msg)
    cell.setBuffer(pack('!512s', msg))
    circuitId = cell.getCircuitId()
    cmdId = cell.getCmdId()
    log.info("Command type is %s" % cmdId)

    # Call the handler method associated with the specified command
    if (cmdId == '0x3'):
      # Use dummy cell then use setBuffer on the dummy
      relayCell = RelayCell.setBuffer(pack('!512s', msg))
      relayCmd = relayCell.getRelayCmd()
      self.RELAY_CMDS[relayCmd](msg)
    else:
      self.CMDS[cmdId](msg, remoteIp, remotePort)

  #############################################
  ## Destruction functions
  #############################################
  def destroyCircuit(self, circuitId):
    # Destroy the specified circuit
    log.info("Destroying circuit #%x (incomplete)" % circuitId)
  
  #############################################
  ## Circuit Creation Send Message functions
  #############################################
  def doOpen(self, connection, toAgentId):
    openMsg = CommandCellOpen.CommandCellOpen(0, 5, self.agentId, toAgentId)
    log.info("openMsg: %s" % openMsg.toString())
    if not connection.writeToRouter(openMsg.toString()):
      log.info("Failed to send OPEN to router")
      sys.exit(1)
    if not self.end:
      log.info("Waiting for reply to OPEN on connection with ")
      reply = connection.readFromBuffer()
      log.info("got reply: %s" % reply)
    if not self.end:
      openMsg.setBuffer(reply)
      msgType = openMsg.getCmdId()
      if (msgType == '0x6'):
        #Opened cell
        log.info("OPENED cell received")
      elif (msgType == '0x7'):
        log.info("ERROR: received OPEN FAILED cell")
        #We may be able to improve this by picking a different peer and trying
        # to do an open before giving up
        sys.exit(1)
      else:
        log.info("ERROR: unexpected command type in response to OPEN")
        sys.exit(1)

  def doCreate(self, connection, circuitId):
    createMsg = Cell.Cell(circuitId, 1)
    if not connection.writeToRouter(createMsg.toString()):
      log.info("Failed to write to router")
      sys.exit(1)

    if not self.end:
      reply = connection.readFromBuffer()
    if not self.end:
      replyMsg = Cell.setBuffer(reply)
      msgType = replyMsg.getCmdId()
      if (msgType == '0x2'):
        log.info("CREATED cell received")
        #Add the mapping of (circuitId, (ip:port)) --> (circuitId, (ip:port))
        #to the routing table
        key = None
        value = (connection.circuitId, (connection.ip, connection.port))
        self.routingTable[key] = value
      elif (msgType == '0x8'):
        log.info("CREATE FAILED cell received")
        sys.exit(1)
      else:
        log.info("ERROR: unexpected command type in response to CREATE")
        sys.exit(1)
  
  def doExtend(self, connection, peerArr):
    bodyString = "%s:%s\0%s" % (peerArr['ip'], peerArr['port'], peerArr['data'])
    extendMsg = RelayCell.RelayCell(1, 0, len(bodyString), 6, bodyString)
    if not connection.writeToRouter(extendMsg.toString()):
      log.info("Failed to write to router")
      sys.exit(1)

    if not self.end:
      reply = connection.readFromBuffer()
    if not self.end:
      replyMsg = RelayCell.setBuffer(reply)
      msgType = replyMsg.getCmdId()
      if not (msgType == '0x3'):
        log.info("ERROR: expected RELAY cell type, received %s" % msgType)
        sys.exit(1)
        relayType = replyMsg.getRelayCmd()
        if (relayType == '0x7'):
          log.info("EXTENDED cell received")
        elif (relayType == '0xc'):
          log.info("EXTEND FAILED cell received")
          sys.exit(1)
        else:
          log.info("ERROR: unexpected command type in response to EXTEND")
          sys.exit(1)
          
  #############################################
  ## Handle Message Functions
  #############################################
  def handleOpen(self, msg, remoteIp, remotePort):
    # If we receive an open cell, check for an open tcp connection
    # to the specified router and if it exists send back an 'Opened' cell
    cell = CommandCellOpen.CommandCellOpen(0, 0, 0, 0)
    cell.setBuffer(pack('!512s', msg))
    remoteHost = cell.getOpenerId()
    localHost = cell.getOpenedId()
    remotePort = str(remotePort)
    log.info("remoteIp: %s, remotePort: %s" % (remoteIp, remotePort))
    log.info("pair in connections: %s" % ((remoteIp, remotePort) in self.connections))
    log.info("self.agentId: " + self.agentId)
    log.info("localHost: " + localHost)
    log.info("connections: ")
    log.info(self.connections)
    if (localHost != self.agentId):
      log.info("Open cell received by wrong host")
      sys.exit(1)
    elif (remoteIp, remotePort) not in self.connections:
      log.info("Open request sent on invalid connection")
      #Send OPEN FAILED
      failedCell = CommandCellOpen.CommandCellOpen(cell.getCircuitId(), 7, remoteHost, localHost)
      self.connections[(remoteIp, remotePort)].writeToBuffer(openedCell.toString())
    else:
      # Generate an OPENED cell and send over the connection
      openedCell = CommandCellOpen.CommandCellOpen(0, 6, remoteHost, localHost)
      log.info("Writing OPENED cell to buffer")
      log.info("Writing OPENED cell to buffer of socket with ip:port of %s:%s" % (self.connections[(remoteIp, remotePort)].ip, self.connections[(remoteIp, remotePort)].port))
      self.connections[(remoteIp, remotePort)].writeToBuffer(openedCell.toString())

  def handleCreate(self, msg, remoteIp, remotePort):
    # The received cell is a Create cell, establish the new circuit number by
    # Inserting an entry into the routing table as circId --> None
    cell = Cell.Cell(0, 0)
    cell.setBuffer(pack('!512s', msg))
    circId = cell.getCircuitId()
    routingTable[(circId, (remoteIp, remotePort))] = None

    # Generate a CREATED cell and send back
    createdCell = Cell.Cell(circId, 2)
    self.connections[(remoteIp, remotePort)].writeToRouter(createdCell.toString())

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
    # Create dummy cell then set buffer on the cell
    cell = RelayCell.setBuffer(pack('!512s', msg))
    bodyString = cell.getBody()
    (ip, port, aid) = re.split('\0:', bodyString)
    
    routingKey = (cell.getCircuitId(), (remoteIp, remotePort))

    if routingKey not in self.routingTable:
      log.info("Invalid destination in RELAY EXTEND")
      sys.exit(1)
    elif self.routingTable[routingKey] == None:
      # The extend is meant for this router, do the extend
      createCell = Cell.Cell(cell.getCircuitId(), cell.getCmdId())

      # Create a connection between this router and the next one
      if (ip, port) not in self.connections:
        # Create a new socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
          s.connect((ip, int(port)))
        except:
          log.info("Failed to connect to %s:%s" % (ip, port))
          self.stop()

        # Create a new connection between this router and the specified peer
        conn = RouterConnection.RouterConnection(self, NEXT_CIRC_ID, ip, port, s)
        # Add this connection to the connection table
        self.connections[(ip, port)] = conn
        # Open the TCP connection
        doOpen(conn, aid)
      doCreate(self.connections[(ip, port)], NEXT_CIRC_ID)
      # TODO: create and catch exception in doCreate so we can report
      # an EXTEND FAILED when the create fails
      extendCell = RelayCell.RelayCell(NEXT_CIRC_ID, cell.getStreamId(), 0, 7)
      self.connections[(ip, port)].writeToRouter(extendCell.toString())
      self.routingTable[routingKey] = (NEXT_CIRC_ID, (ip, port))
      self.routingTable[(NEXT_CIRC_ID, (ip, port))] = routingKey
      NEXT_CIRC_ID += 2
    else:
      # Pass on the relay extend as indicated in the routing table
      self.connections[(ip, port)].writeToRouter(cell.toString())

  def unexpectedCommand():
    log.info("Received unexpected command")
    sys.exit(1)

  def stop(self):
    log.info("stopping")
    self.end = True
    for key in self.connections:
      # TODO: Send DESTROY cell to all circuits connected to router
      self.connections[key].stop()
