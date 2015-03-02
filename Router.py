# RoutingTable
# TimerTable
# Connections
# Initializer to run on prompting from the node class
# Register function

class Router(object):
  def __init__(self):
    self.routingTable = {}
    self.timers = {}
    self.connections = {}

  def registerRouter():
    print "Registering router (incomplete)"
    #register with the registration service here

  def createCircuit():
    print "Creating circuit (incomplete)"
    #connect to three other routers and create a circuit

  def start():
    registerRouter()
    createCircuit()
    #accept incoming connections here
    print "Starting the router (incomplete)"

  def handleProxyMessage():
    # Take a message from the converter and place it into the appropriate
    # buffer
    print "Handling message from proxy side (incomplete)"

  def handleRouterMessage():
    # Take a message from the buffer, process it, and send it either to
    # the converter or to another router connection's buffer
    print "Handling message from router buffer (incomplete"

  def destroyCircuit(circuitId):
    # Destroy the specified circuit
    print "Destroying circuit #%x" % circuitId

  