import CommandCellOpen, RelayCell, Cell, RouterConnection, os

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
  def registerRouter():
    print "Registering router"
    string = "python registration_client.py %s Tor61Router-%s-%s" % (self.groupNum, self.instanceNum, self.port)
    os.system(string)

  def createCircuit():
    print "Creating circuit (incomplete)"
    print "fetching registered routers"
    string = "python fetch.py Tor61Router-%s" % self.groupNum
    os.system(string)
    #connect to three other routers and create a circuit

  def manageTimeouts():
    #create a new thread to manage the timer table,
    #checking if circuits have timed out and calling destroy if so
    print "Creating timeout manager (incomplete)"

  def start():
    registerRouter()
    createCircuit()
    #accept incoming connections here
    print "Starting the router (incomplete)"


  #############################################
  ## Reading/Delegating functions
  #############################################
  def handleProxyMessage():
    # Take a message from the converter and place it into the appropriate
    # buffer using RouterConnection's writeToBuffer
    print "Handling message from proxy side (incomplete)"

  def handleRouterMessage(msg):
    # Accept a message from a RouterConnection, process it, and send it either to
    # the converter or to another router connection's buffer
    print "Handling message from router buffer (incomplete)"
    # figure out what kind of message this is and delegate the processing
    # to one of the Handle Message functions

  #############################################
  ## Destruction functions
  #############################################
  def destroyCircuit(circuitId):
    # Destroy the specified circuit
    print "Destroying circuit #%x (incomplete)" % circuitId
  

  #############################################
  ## Handle Message Functions
  #############################################
  def handleOpen():
    # The received cell is an Open cell, do appropriate logic
    print "handling Open message (incomplete)"

  def handleOpened():
    return
    # The received cell is an Opened cell, do appropriate logic

  def handleOpenFailed():
    return
    # The received cell is an Open Failed cell, do appropriate logic

  def handleCreate():
    # The received cell is a Created cell, do appropriate logic
    return

  def handleCreated():
    return
    # The received cell is a Created cell, do appropriate logic

  def handleCreateFailed():
    # The received cell is a Create Failed cell, do appropriate logic
    return

  def handleDestroy():
    # The received cell is a Destroy cell, do appropriate logic
    return

  def handleBegin():
    # The received cell is a relay begin cell, do appropriate logic
    return

  def handleData():
    # The received cell is a relay data cell, do appropriate logic
    return

  def handleEnd():
    # The received cell is a relay end cell, do appropriate logic
    return

  def handleConnected():
    # The received cell is a relay connected cell, do appropriate logic
    return

  def handleExtend():
    # The received cell is a relay extend cell, do appropriate logic
    return

  def handleExtended():
    # The received cell is a relay extended cell, do appropriate logic
    return

  def handleBeginFailed():
    # The received cell is a relay Begin Failed cell, do appropriate logic
    return

  def handleExtendFailed():
    # The received cell is a relay Extend Failed cell, do appropriate logic
    return
