import CommandCellOpen, RelayCell, Cell, RouterConnection
import os, threading, subprocess, time
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

  #############################################
  ## Router startup functions
  #############################################
  def registerRouter(self):
    print "Registering router"
    string = "python registration_client.py %s Tor61Router-%s-%s %s" % (self.port, self.groupNum, self.instanceNum, 100001)
    print string
    thread = threading.Thread(target=os.system, args=(string,))
    thread.start()

  def createCircuit(self):
    print "Creating circuit (incomplete)"
    #connect to three other routers and create a circuit
    peers = self.getPeers()
    #if (!((peers[0][0], peers[0][1]) in connections)):
      # create tcp connection
    #send open cell


    #Check whether there is already a tcp connection between this router and
    #the first random router. If not, try to create a tcp connection and send
    #an OPEN cell. If an OPENED cell is returned, send a create cell and enter
    #a None-->circuit,sock entry into the router table. Then send extends twice
    #to the router
    
      

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
      circuitPeers.append(peers[randint(0, len(peers)-1)])
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
  ## Handle Message Functions
  #############################################
  def handleOpen(self):
    # The received cell is an Open cell, do appropriate logic
    print "handling Open message (incomplete)"

  def handleOpened(self):
    return
    # The received cell is an Opened cell, do appropriate logic

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
