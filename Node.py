# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Project 3: Tor61

'''
Node.py is an overall abstraction of a Router, including both proxy and Tor sides
'''

import Router, Tor61Log, HttpCellConverter, HttpProxy
import sys, os, threading
log = Tor61Log.getLog()

def main():
  log.info(len(sys.argv))
  if (len(sys.argv) != 4):
    log.info("Usage: ./run <group number> <instance number> <HTTP Proxy Port>")
    sys.exit(1)
  groupNum = sys.argv[1]
  instanceNum = sys.argv[2]
  port = int(sys.argv[3])
  converter = HttpCellConverter.getConverter()
  proxy = HttpProxy.HttpProxy(port)
  router = Router.Router(converter, groupNum, instanceNum, groupNum)
  try:
    proxy.awaitConnections()
    router.start()
  except KeyboardInterrupt:
    log.info("Interupted! Shutting down.")
    router.stop()
    log.info("exited router.stop()")
    os._exit(0)
  log.info("Router shutting down")

if __name__ == '__main__':
  main()
