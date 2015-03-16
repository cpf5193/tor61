# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# RelayCell.py
# Represents a Tor61 Relay cell of any typeimport Cell

import CommandCellOpen, RelayCell, Cell, RouterConnection, Tor61Log
import os, threading, subprocess, time, socket, re, sys, datetime
from datetime import datetime, timedelta
from random import randint
from struct import pack

log = Tor61Log.getLog()

CIRCUIT_TIMEOUT = timedelta(0, 60 * 5)

class Router(object):
  #############################################
  ## Constructor
  #############################################
  def __init__(self, converter, groupNum, instanceNum, port):
    self.routingTable = {}
    self.circuitHosts = {}
    self.allrcs = []
    self.timers = {}
    self.connections = {} #format: (ip, port) --> RouterConnection
    self.converter = converter
    self.groupNum = groupNum
    self.instanceNum = instanceNum
    self.port = port
    self.agentId = str((int(groupNum) << 16) | int(instanceNum))
    self.CMDS = {
      '0x1': self.handleCreate,
      '0x2': self.handleCreated,
      '0x4': self.handleDestroy,
      '0x5': self.handleOpen,
      '0x6': self.handleOpened,
      '0x7': self.handleOpenFailed,
      '0x8': self.handleCreateFailed
    }
    
    self.RELAY_CMDS = {
      '0x1': self.handleBegin,
      '0x2': self.handleData,
      '0x3': self.handleEnd,
      '0x4': self.handleConnected,
      '0x6': self.handleExtend,
      '0x7': self.handleExtended,
      '0xb': self.handleBeginFailed,
      '0xc': self.handleExtendFailed
    }
    self.NEXT_CIRC_ID = 1
    self.circuitLength = 1
    self.end = False

  #############################################
  ## Router startup functions
  #############################################
  def registerRouter(self):
    log.info("Registering router")
    string = "python registration_client.py %s Tor61Router-%s-%s %s" % (self.port, self.groupNum, self.instanceNum, self.agentId)
    log.info(string)
    thread = threading.Thread(target=os.system, args=(string,))
    thread.start()

  #Initial circuit creation
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
      log.info("connecting to %s:%d" % (peers[0]['ip'], peers[0]['port']))
      s.connect((peers[0]['ip'], peers[0]['port']))
    except:
      log.info("Cannot connect to %s:%d" % (peers[0]['ip'], peers[0]['port']))

    sockaddr = s.getsockname()
    log.info("initial socket address: %s:%d" % sockaddr)

    # Create a new connection between this router and the first peer
    conn = RouterConnection.RouterConnection(self, 0, sockaddr[0], sockaddr[1], s)
    self.allrcs.append(conn)
    log.info("allrcs: ")
    log.info(self.allrcs)

    log.info("initial conn: ")
    log.info(conn)
    log.info("----------------------------------")

    # Add this connection to the connection table
    self.connections[sockaddr] = conn

    # Send an OPEN cell to the first peer, the next steps are taken care of by the
    # RouterConnection objects

    self.doOpen(conn, peers[0]['data'])

    log.info("Successfully created circuit with id 1")

  #Fetches a lsit of Tor61 peers
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
      peerObj['port'] = int(randPeer[1])
      peerObj['data'] = randPeer[2]
      circuitPeers.append(peerObj)
    self.peers = circuitPeers
    log.info("circuitPeers: ")
    log.info(circuitPeers)
    return circuitPeers

  # Creates the first circuit and awaits new
  # router connections
  def start(self):
    self.registerRouter()
    # Start listening for other connections once the circuit is created
    connectionAccepter = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostbyname(socket.gethostname())
    log.info("host: %s" % host)
    port = self.port
    connectionAccepter.bind((host, int(port)))
    connectionAccepter.settimeout(2)
    connectionAccepter.listen(5)
    
    thread = threading.Thread(target=self.createCircuit, args = ())
    thread.start()
    timerThread = threading.Thread(target = self.timerScan, args = ())
    timerThread.start()
    self.handleNewConnections(connectionAccepter)
    
  #Accepts new router connections
  def handleNewConnections(self, connectionAccepter):
    while not self.end:
      try:
        log.info("socket at %s:%s listening for new connections" % (socket.gethostbyname(socket.gethostname()), self.port))
        (conn, address) = connectionAccepter.accept()
        conn.settimeout(2)
        log.info("handled connection (addr): new socket %s:%d created" % address)
        log.info(conn)
        log.info("Connection accepted from %s:%s", address[0], address[1])
        rc = RouterConnection.RouterConnection(self, 0, address[0], address[1], conn)
        self.connections[address] = rc
        self.allrcs.append(rc)
        log.info("allrcs: ")
        log.info(self.allrcs)
      except socket.error:
        log.info("Socket error -- handleNewConnections")
        continue
    log.info("self.end (handleNewConnections): %s" % self.end) 

  #############################################
  ## Reading/Delegating functions
  #############################################
  def handleProxyMessage(self):
    # Take a message from the converter and place it into the appropriate
    # buffer using RouterConnection's writeToBuffer
    log.info("Handling message from proxy side (incomplete)")

  # Handles a message from another router
  def handleRouterMessage(self, msg, remoteIp, remotePort):
    # Accept a message from a RouterConnection, process it, and send it either to
    # the converter or to another router connection's buffer
    log.info("Handling message from router buffer from %s:%d!" % (remoteIp, remotePort))
    # Extract the cell type from the Cell
    cell = Cell.Cell()
    cell.setBuffer(pack('!512s', msg))
    circuitId = cell.getCircuitId()
    
    self.resetTimer(circuitId)
    
    cmdId = cell.getCmdId()
    log.info("Command type is %s" % cmdId)
    log.info("cmdId == 0x3 --> %s" % (cmdId == '0x3'))
    # Call the handler method associated with the specified command
    if (cmdId == '0x3'):
      # Use dummy cell then use setBuffer on the dummy
      relayCell = RelayCell.RelayCell()
      relayCell.setBuffer(pack('!512s', msg))
      relayCmd = relayCell.getRelayCmd()
      log.info("relayCmd: %s" % relayCmd)
      self.RELAY_CMDS[relayCmd](msg, remoteIp, remotePort)
    else:
      self.CMDS[cmdId](msg, remoteIp, remotePort)

  #############################################
  ## Destruction functions
  #############################################
  def destroyCircuit(self, circuitId):
    # Destroy the specified circuit
    log.info("Destroying circuit #%x (incomplete)" % circuitId)
    toDestroy = self.circuitHosts[circuitId]
    for host in toDestroy:
      ip, port = host
      self.doDestroy(circuitId, ip, host)
  
  #############################################
  ## Circuit Creation Send Message functions
  #############################################
  def doOpen(self, connection, toAgentId):
    openMsg = CommandCellOpen.CommandCellOpen(self.NEXT_CIRC_ID, 0x05, self.agentId, toAgentId)
    log.info("Sending OPEN cell to %s:%s" % (connection.remoteIp, connection.remotePort))
    connection.writeToBuffer(openMsg.toString())
    
  #Sends a create cell
  def doCreate(self, connection, circuitId):
    createMsg = Cell.Cell(circuitId, 1)
    log.info("Writing CREATE cell to %s:%s" % (connection.remoteIp, connection.remotePort))
    connection.writeToBuffer(createMsg.toString())

  #Sends an extend cell
  def doExtend(self, connection, peerArr):
    bodyString = "%s:%s\0%s" % (peerArr['ip'], peerArr['port'], peerArr['data'])
    extendMsg = RelayCell.RelayCell(self.NEXT_CIRC_ID, 0x00, len(bodyString), 0x06, bodyString)
    log.info("Writing EXTEND cell to %s:%s" % (peerArr['ip'], peerArr['port']))
    connection.writeToBuffer(extendMsg.toString())
    
    if not self.end:
      log.info("connection socket: ")
      log.info(connection.socket.getsockname())
      log.info("Waiting for reply to EXTEND on %s:%d" % connection.socket.getsockname())
      reply = connection.readFromRouter()
    if not self.end:
      replyMsg = RelayCell.RelayCell()
      replyMsg.setBuffer(pack('!512s', reply))
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

  #Sends a destroy cell
  def doDestroy(self, circuitId, remoteIp, removeHost):
    log.info((circuitID, remoteIp, removeHost))
    
  #############################################
  ## Handle Message Functions
  #############################################
  def handleOpen(self, msg, remoteIp, remotePort):
    log.info("handling OPEN cell")
    # If we receive an open cell, check for an open tcp connection
    # to the specified router and if it exists send back an 'Opened' cell
    cell = CommandCellOpen.CommandCellOpen()
    cell.setBuffer(pack('!512s', msg))
    remoteHost = cell.getOpenerId()
    localHost = cell.getOpenedId()
    circId = cell.getCircuitId()
    log.info("circId: %d, remoteIp: %s, remotePort: %d" % (circId, remoteIp, remotePort))
    log.info("pair in connections in self.connections: %s" % ((remoteIp, remotePort) in self.connections))
    log.info("self.agentId: " + self.agentId)
    log.info("localHost: " + localHost)
    log.info("connections: ")
    log.info(self.connections)
    if (localHost != self.agentId):
      log.info("Open cell received by wrong host")
      sys.exit(1)
    elif (remoteIp, remotePort) not in self.connections:
      log.info("Open request sent on invalid connection")
      log.info("tried to look up (%s, %d) in self.connections:" % (remoteIp, remotePort))
      self.stop()
      #Send OPEN FAILED
      failedCell = CommandCellOpen.CommandCellOpen(cell.getCircuitId(), 7, remoteHost, localHost)
      log.info("Sending OPEN FAILED cell to %s:%s" % (remoteIp, remotePort))
      self.connections[(remoteIp, remotePort)].writeToBuffer(openedCell.toString())
    else:
      # Generate an OPENED cell and send over the connection
      openedCell = CommandCellOpen.CommandCellOpen(1, 6, remoteHost, localHost)
      log.info("Writing OPENED cell to %s:%s" % (remoteIp, remotePort))
      self.connections[(remoteIp, remotePort)].writeToBuffer(openedCell.toString())

  # Takes in an OPENED cell and returns a CREATE to the corresponding outgoing socket
  def handleOpened(self, msg, remoteIp, remotePort):
    log.info("received OPENED from %s:%d, replying with CREATE" % (remoteIp, remotePort))
    openMsg = CommandCellOpen.CommandCellOpen()
    openMsg.setBuffer(pack('!512s', msg))
    circId = openMsg.getCircuitId()
    createMsg = Cell.Cell(openMsg.getCircuitId(), 1)
    self.connections[(remoteIp, remotePort)].writeToBuffer(createMsg.toString())

  # Handle an open failed cell
  def handleOpenFailed(self, msg, remoteIp, remotePort):
    log.info("Received OPEN FAILED cell from %s:%d" % (remoteIp, remotePort))
    sys.exit(1)

  # Handle a create cell
  def handleCreate(self, msg, remoteIp, remotePort):
    log.info("Handling CREATE cell")
    # The received cell is a Create cell, establish the new circuit number by
    # Inserting an entry into the routing table as circId --> None
    cell = Cell.Cell()
    cell.setBuffer(pack('!512s', msg))
    circId = cell.getCircuitId()
    incomingTuple = (circId, (remoteIp, remotePort))
    if incomingTuple not in self.routingTable:
      log.info("inserting (%d, (%s, %d)) --> None in routing table" % (circId, remoteIp, remotePort))
      self.routingTable[(circId, (remoteIp, remotePort))] = None

    # Generate a CREATED cell and send back
    createdCell = Cell.Cell(circId, 2)
    log.info("Sending CREATED cell to %s:%s" % (remoteIp, remotePort))

    # Since the connection was created with initial circuitId 0, we update its
    # circuitId in the table when it receives a create
    self.connections[(remoteIp, remotePort)] = self.connections[(remoteIp, remotePort)]
    self.connections[(remoteIp, remotePort)].circuitId = circId
    self.connections[(remoteIp, remotePort)].writeToBuffer(createdCell.toString())

  # Receives a CREATED cell and either sends an EXTENDED back to the previous router or an EXTEND on to
  # next router depending on where it is in the circuit
  def handleCreated(self, msg, remoteIp, remotePort):
    createdMsg = Cell.Cell()
    createdMsg.setBuffer(msg)
    circId = createdMsg.getCircuitId()
    incomingTuple = (circId, (remoteIp, remotePort))
    log.info("checking for (%d, (%s, %d)) in routing table: " % (incomingTuple[0], incomingTuple[1][0], incomingTuple[1][1]))
    log.info(self.routingTable)
    log.info("in table? %s" % (incomingTuple in self.routingTable))
    log.info("entry is None? %s" % (self.routingTable[incomingTuple] == None))
    if incomingTuple in self.routingTable and not (self.routingTable[incomingTuple] == None):
      # If there is an entry in the routing table already, then this Created is being sent to a
      # router that expects to send an extended back to the previous router, use the routing
      # table to do so
      outgoingTuple = self.routingTable[incomingTuple]
      log.info("outgoingTuple: (%d, (%s, %d))" % (outgoingTuple[0], outgoingTuple[1][0], outgoingTuple[1][1])) 
      extendedMsg = RelayCell.RelayCell(outgoingTuple[0], 0x0000, 0x0000, 0x07)
      log.info("cellCmd: %s" % extendedMsg.getCmdId()) 
      log.info("relayId: %s" % extendedMsg.getRelayCmd())
      log.info("connections: ")
      log.info(self.connections)
      log.info("sending EXTENDED to %s:%d" % (self.connections[outgoingTuple[1]].remoteIp, self.connections[outgoingTuple[1]].remotePort))
      self.connections[outgoingTuple[1]].writeToBuffer(extendedMsg.toString())
    else:
      log.info("entry not in table!!!!!")
      #If there is no entry in the routing table, the CREATE was sent to the first peer,
      # and on a CREATED we should send an EXTEND
      peerArr = self.peers[self.circuitLength]
      bodyString = "%s:%s\0%s" % (peerArr['ip'], peerArr['port'], peerArr['data'])
      extendMsg = RelayCell.RelayCell(circId, 0x0000, len(bodyString), 0x06, bodyString)
      self.connections[incomingTuple[1]].writeToBuffer(extendMsg.toString())

  def handleCreateFailed(self, msg, remoteIp, remotePort):
    log.info("Received CREATE FAILED from %s:%d" % (remoteIp, remotePort))
    createMsg = Cell.Cell()
    createMsg.setBuffer(msg)
    incomingTuple = (createMsg.getCircuitId(), (remoteIp, remotePort))
    if incomingTuple in self.routingTable and not self.routingTable[incomingTuple] == None:
      # If the tuple is in the routing table, then the previous router is expecting a response to EXTEND,
      # send an EXTEND FAILED message
      outgoingTuple = self.routingTable[incomingTuple]
      failedMsg = RelayCell.RelayCell(outgoingTuple[0], 0x0000, 0x0000, 0x0c)
      self.connections[incomingTuple[1]].writeToBuffer(failedMsg.toString())
    else:
      # If the tuple is not in the routing table, then the initial create failed
      self.stop()
  
  # Handle a destroy cell
  def handleDestroy(self, msg, remoteIp, remotePort):
    # The received cell is a Destroy cell, do appropriate logic
    self.allrcs[(remoteIp, remotePort)].stop()
    cell = Cell.Cell()
    cell.setBuffer(msg)
    circuitId = cell.getCircuitId()
    key = (circuitId, (remoteIp, remotePort))
    del self.allrcs[(remoteIp, remotePort)]
    other = self.routingTable[key]
    del self.routingTable[key]
    del self.routingTable[other]
    return
    
  #Sends a relay cell to the proxy
  def giveRelayToProxy(self, msg, remoteIp, remotePort):
    cell = RelayCell.RelayCell()
    cell.setBuffer(pack('512s', msg))
    streamId = cell.getStreamId()
    body = cell.getBody()
    key = ((remoteIp, int(remotePort)), streamId)
    toEnqueue = (key, body)
    log.info(str(toEnqueue))
    self.convert.putCell(toEnqueue)

  #Gives a BEGIN to the proxy
  def handleBegin(self, msg, remoteIp, remotePort):
    log.info("Sending BEGIN to " + str((remoteIp, remotePort)))
    giveRelayToProxy(msg, remoteIp, remotePort)

  #Gives a DATA to the proxy
  def handleData(self, msg, remoteIp, remotePort):
    log.info("Sending DATA to " + str((remoteIp, remotePort)))
    giveRelayToProxy(msg, remoteIp, remotePort)

  #Gives an END to the proxy
  def handleEnd(self, msg, remoteIp, remotePort):
    log.info("Sending END to " + str((remoteIp, remotePort)))
    giveRelayToProxy(msg, remoteIp, remotePort)

  #Gives a CONNECTED to the proxy
  def handleConnected(self, msg, remoteIp, remotePort):
    log.info("Sending CONNECTED to " + str((remoteIp, remotePort)))
    giveRelayToProxy(msg, remoteIp, remotePort)

  #Sends an extend to the next router
  def handleExtend(self, msg, remoteIp, remotePort):
    log.info("Handling EXTEND cell")
    # Create dummy cell then set buffer on the cell
    cell = RelayCell.RelayCell()
    cell.setBuffer(pack('!512s', msg))
    bodyString = cell.getBody()
    (ip, port, aid) = re.split('[\0:]', bodyString)
    log.info("extending circuit to %s:%s" % (ip, port))
    routingKey = (cell.getCircuitId(), (remoteIp, remotePort))
    log.info("routing table: ")
    log.info(self.routingTable)

    if self.routingTable[routingKey] == None:
      log.info("EXTEND detected by last in circuit, doing CREATE")
      # The extend is meant for this router, do the extend
      createCell = Cell.Cell(cell.getCircuitId(), int(cell.getCmdId(), 16))
      log.info("trying to get a new connection to %s:%s" % (ip, port))
      # Create a connection between this router and the next one
      log.info("remoteIp, remotePort: (%s, %d)" % (remoteIp, remotePort))
      log.info("connections: ")
      log.info(self.connections)
      log.info("Doing OPEN")
      # Create a new socket
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      try:
        log.info("connecting to %s:%d" % (ip, int(port)))
        s.connect((ip, int(port)))
      except:
        log.info("Failed to connect to %s:%s" % (ip, port))
        self.stop()
        
      # Create a new connection between this router and the specified peer
      nextIpPort = s.getsockname()
      conn = RouterConnection.RouterConnection(self, self.NEXT_CIRC_ID, nextIpPort[0], nextIpPort[1], s)
      self.allrcs.append(conn)
      log.info("created new connection for extend: ")
      log.info("conn.ip: %s, conn.port: %d" % (conn.remoteIp, int(conn.remotePort)))
      log.info("socket.ip: %s, socket.ip: %d" % nextIpPort)
      log.info("-----------------------------------------------------------")
      # Add this connection to the connection table and the routing table
      log.info("writing (%d, (%s, %d)) --> (%d, (%s, %d)) to routing table" % (cell.getCircuitId(), remoteIp, remotePort, self.NEXT_CIRC_ID, nextIpPort[0], nextIpPort[1]))
      self.routingTable[(cell.getCircuitId(), (remoteIp, remotePort))] = (self.NEXT_CIRC_ID, nextIpPort)
      log.info("writing (%d, (%s, %d)) --> (%d, (%s, %d)) to routing table" % (self.NEXT_CIRC_ID, nextIpPort[0], nextIpPort[1], cell.getCircuitId(), remoteIp, remotePort))
      self.routingTable[(self.NEXT_CIRC_ID, nextIpPort)] = (cell.getCircuitId(), (remoteIp, remotePort))
      self.connections[nextIpPort] = conn
      # Open the Tor61 connection
      self.doOpen(conn, aid)
    else:
      outgoingTuple = self.routingTable[routingKey]
      extendMsg = RelayCell.RelayCell()
      extendMsg.setBuffer(msg)
      changedCircuitMsg = RelayCell.RelayCell(extendMsg.getCircuitId(), extendMsg.getStreamId(), extendMsg.getBodyLen(), int(extendMsg.getRelayCmd(), 16), extendMsg.getBody())
      self.circuitLength += 1
      if (self.circuitLength < 3):
        self.connections[outgoingTuple[1]].writeToBuffer(changedCircuitMsg.toString())
      else:
        self.stop()
      time.sleep(1)
      os._exit(1)

  #Handles a an EXTEND from another router
  def handleExtended(self, msg, remoteIp, remotePort):
    log.info("received EXTENDED message from %s:%d" % (remoteIp, remotePort))
    self.circuitLength += 1
    if self.circuitLength < 3:
      log.info("Sending EXTEND cell to %s:%s" % (remoteIp, remotePort))
      peerArr = self.peers[self.circuitLength]
      bodyString = "%s:%s\0%s" % (peerArr['ip'], peerArr['port'], peerArr['data'])
      extendMsg = RelayCell.RelayCell(0x0001, 0x0000, len(bodyString), 0x06, bodyString)
      self.connections[(remoteIp, remotePort)].writeToBuffer(extendMsg.toString())
      log.info("circuitLength: %d" % self.circuitLength)
      log.info("circuit not yet complete. doing another extend")
      return
    else:
      log.info("circuit creation completed.")

  # Exit on an Extend Failed message
  def handleExtendFailed(self, msg, remoteIp, remotePort):
    log.info("EXTEND FAILED received. Exiting.")
    self.stop()

  # Exit on a Begin Failed message
  def handleBeginFailed(self, mg, remoteIp, remotePort):
    log.info("RELAY BEGIN FAILED received. Exiting.")
    self.stop()
      
  #Exit on an unexpected command
  def unexpectedCommand(self):
    log.info("Received unexpected command")
    sys.exit(1)
    
  #Resets the timer for this circuit
  def resetTimer(self, circuitId):
    self.timers[circuitId] = datetime.now()
    
  #Adds a list of addresses associated with a circuit
  def addAddressToCircuit(self, circuitId, ip, port):
    if circuitId in self.circuitHosts:
      self.circuitHosts[circuitId].add((ip, port))
    else:
      self.circuitHosts[circuitId] = [(ip, port)]
    
  #Scans the timer table and removes circuits that have not had
  #activity in CIRCUIT_TIMEOUT seconds
  def timerScan(self):
    while not self.end:
      time.sleep(CIRCUIT_TIMEOUT.total_seconds())
      now = datetime.now()
      for id in self.timers:
        if now - self.timers[id] > CIRCUIT_TIMEOUT:
          destroyCircuit(circuitId)          

  #Signals threads to stop
  def stop(self):
    log.info("stopping")
    log.info(self.allrcs)
    for rc in self.allrcs:
      log.info("stopping : ")
      log.info(rc)
      # TODO: Send DESTROY cell to all circuits connected to router
      rc.stop()
    time.sleep(2)
    self.end = True
    log.info("end of router.py stop")
