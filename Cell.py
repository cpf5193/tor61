# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Tor61

# Cell.py
# A base class representing the basic format of a Cell.
# All cells contain a circuit id and command type at the beginning of the cell.
# The 'Created', 'Create', 'Create Failed', and 'Destroy' command cells can be
# directly represented by the overall Cell class.

from struct import pack, unpack, unpack_from
import Tor61Log

log = Tor61Log.getLog()

LENGTH = 512
CELL_FORMAT = '!Hb509s'
CELL_HEAD_LEN = 3
CMD_TYPE_INDEX = 2

class Cell(object):
  def __init__(self, circuitId = 0x0000, cmdType = 0x00):
    padding = '0'.zfill(LENGTH - CELL_HEAD_LEN)
    self.buffer = pack(CELL_FORMAT, circuitId, cmdType, padding)

  def getCircuitId(self):
    circuitId, rest = unpack('!H510s', self.buffer)
    return int(circuitId)

  def getCmdId(self):
    cmdType, rest = unpack_from('!b509s', self.buffer, CMD_TYPE_INDEX)
    log.info(cmdType)
    return hex(cmdType)

  def getBuffer(self):
    return self.buffer

  def toString(self):
    return "%s" % self.buffer

  def setBuffer(self, buffer):
    self.buffer = buffer

  def getLength():
    return LENGTH
