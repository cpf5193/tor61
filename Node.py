import Router, sys, os

def main():
  print len(sys.argv)
  if (len(sys.argv) != 4):
    print len(sys.argv)
    print len(sys.argv == 4)
    print "Usage: ./run <group number> <instance number> <HTTP Proxy Port>"
    sys.exit(1)
  groupNum = sys.argv[1]
  instanceNum = sys.argv[2]
  port = sys.argv[3]
  router = Router.Router(None, groupNum, instanceNum, port)
  print "Starting Router"
  router.start()

if __name__ == '__main__':
  main()
