import CommandCellOpen, RelayCell, Cell, RouterConnection
import os, threading, subprocess, time, socket
from random import randint

class Router(object):
  #############################################
  ## Constructor
  #############################################
  def __init__(self, converter, groupNum, instanceNum, port):
    self.routingTable = {}
    self.timers = {}
    self.connections = {}
    self.converter = converter
    self.groupNum = groupNum
    self.instanceNum = instanceNum
    self.port = port
    self.agentId = (groupNum << 16) | instanceNum
    self.circuitStatus = "Not Started"

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
    #connect to three other routers and create a circuit
    peers = self.getPeers()

    # Create a new connection between this router and the first peer
    conn = RouterConnection.RouterConnection(self, 0x0000, peers[0]['ip'], peers[0]['port'])
    conn.connectToRouter()

    #Add this connection to the table
    connections[peers[0]['ip'] + ':' + peers[0]['port']] = conn
    
    #Create an OPEN cell to send to the first peer
    self.doOpen(conn)
    
    #Send a CREATE cell
    self.doCreate(conn)
    
    #Send a RELAY EXTEND cell x2 using the stream id 0x0000 
    #and the circuit id 0x0001
    self.doExtend(conn, peers[1])
    self.doExtend(conn, peers[2])

    print "Successfully created circuit with id 0x0001"
    
    #TODO: Start listening for other connections once the circuit is created
    
  
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
    time.sleep(3)
    self.createCircuit()
    #accept incoming connections here
    print "Starting the router (incomplete)"
    return

  #############################################
  ## Reading/Delegating functions
  #############################################
  def handleProxyMessage(self):
    # Take a message from the converter and place it into the appropriate
    # buffer using RouterConnection's writeToBuffer
    print "Handling message from proxy side (incomplete)"

  def handleRouterMessage(self, msg):
    # Accept a message from a RouterConnection, process it, and send it either to
    # the converter or to another router connection's buffer
    print "Handling message from router buffer (incomplete)"
    # figure out what kind of message this is and delegate the processing
    # to one of the Handle Message functions

  #############################################
  ## Destruction functions
  #############################################
  def destroyCircuit(self, circuitId):
    # Destroy the specified circuit
    print "Destroying circuit #%x (incomplete)" % circuitId
  
  #############################################
  ## Circuit Creation Send Message functions
  #############################################
  def doOpen(self, connection):
    openMsg = CommandCellOpen.CommandCellOpen(0x0000, 0x05, self.agentId, peers[0]['data'])
    connection.writeToBuffer(openMsg.getBuffer())
    reply = connection.readFromRouter()
    replyMsg = CommandCellOpen.setBuffer(reply)
    msgType = replyMsg.getCmdId()
    if (msgType == 0x06):
      #Opened cell
      print "OPENED cell received"
      #Send a create?
    elif (msgType == 0x07):
      print "ERROR: received OPEN FAILED cell"
      #We may be able to improve this by picking a different peer and trying
      # to do an open before giving up
      sys.exit(1)
    else:
      print "ERROR: unexpected command type in response to OPEN"
      sys.exit(1)
    # The received cell is an Opened cell, do appropriate logic

  def doCreate(self, connection):
    createMsg = Cell.Cell(0x0001, 0x01)
    connection.writeToBuffer(createMsg.getBuffer())
    reply = connection.readFromRouter()
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
    connection.writeToBuffer(extendMsg.getBuffer())
    reply = connection.readFromRouter()
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
  def handleOpen(self, msg):
    return
  
  def handleOpenFailed(self):
    return
    # The received cell is an Open Failed cell, do appropriate logic

  def handleCreate(self):
    # The received cell is a Created cell, do appropriate logic
    return

  def handleCreated(self):
    return
    # The received cell is a Created cell, do appropriate logic

  def handleCreateFailed(self):
    # The received cell is a Create Failed cell, do appropriate logic
    return

  def handleDestroy(self):
    # The received cell is a Destroy cell, do appropriate logic
    return

  def handleBegin(self):
    # The received cell is a relay begin cell, do appropriate logic
    return

  def handleData(self):
    # The received cell is a relay data cell, do appropriate logic
    return

  def handleEnd(self):
    # The received cell is a relay end cell, do appropriate logic
    return

  def handleConnected(self):
    # The received cell is a relay connected cell, do appropriate logic
    return

  def handleExtend(self):
    # The received cell is a relay extend cell, do appropriate logic
    return

  def handleExtended(self):
    # The received cell is a relay extended cell, do appropriate logic
    return

  def handleBeginFailed(self):
    # The received cell is a relay Begin Failed cell, do appropriate logic
    return

  def handleExtendFailed(self):
    # The received cell is a relay Extend Failed cell, do appropriate logic
    return
