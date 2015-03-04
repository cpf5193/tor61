import Router, sys, os

def main():
  if (sys.argv.length != 4):
    print "Usage: ./run <group number> <instance number> <HTTP Proxy Port>"
    sys.exit(1)
  groupNum = sys.argv[1]
  instanceNum = sys.argv[2]
  port = sys.argv[3]
  router = Router(None, groupNum, instanceNum, port)
  router.start()
  
