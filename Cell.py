from struct import pack, unpack, unpack_from

'''
A base class representing the basic format of a Cell.
All cells contain a circuit id and command type at the beginning of the cell.
The 'Created', 'Create', 'Create Failed', and 'Destroy' command cells can be
directly represented by the overall Cell class.
'''
LENGTH = 512
CELL_FORMAT = '!Hbs'
CELL_HEAD_LEN = 3
CMD_TYPE_INDEX = 2

class Cell(object):
  def __init__(self, circuitId, cmdType):
    padding = '0'.zfill(LENGTH - CELL_HEAD_LEN)
    self.buffer = pack('!Hbs', circuitId, cmdType, padding)

  def getCircuitId(self):
    circuitId, rest = unpack('!Hs', self.buffer.toString())
    return circuitId

  def getCmdId(self):
    cmdType, rest = unpack_from('!bs', self.buffer.toString())
    return cmdType

  def getBuffer(self):
    return self.buffer

  def toString(self):
    circuitId, cmdType, rest = unpack(CELL_FORMAT, self.buffer)
    return "%x%x%s" % (circuitId, cmdType, rest)

  def setBuffer(self, buffer):
    self.buffer = buffer

  def getLength():
    return LENGTH
