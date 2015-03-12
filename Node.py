import Router, Tor61Log, HttpCellConverter
import sys, os
log = Tor61Log.getLog()

def main():
  log.info(len(sys.argv))
  if (len(sys.argv) != 4):
    log.info("Usage: ./run <group number> <instance number> <HTTP Proxy Port>")
    sys.exit(1)
  groupNum = sys.argv[1]
  instanceNum = sys.argv[2]
  port = sys.argv[3]
  converter = HttpCellConverter.getConverter()
  router = Router.Router(converter, groupNum, instanceNum, port)
  log.info("Starting Router")
  try:
    router.start()
    log.info("Router finished.")
  except KeyboardInterrupt:
    log.info("Interupted! Shutting down.")
    router.stop()
    sys.exit(0)
  log.info("Router shutting down")

if __name__ == '__main__':
  main()
