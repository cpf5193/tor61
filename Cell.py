from struct import pack, unpack

'''
A base class representing the basic format of a Cell.
All cells contain a circuit id and command type at the beginning of the cell.
The 'Created', 'Create', 'Create Failed', and 'Destroy' command cells can be
directly represented by the overall Cell class.
'''

class Cell(object):
  LENGTH = 512
  CELL_FORMAT = '!Hbs'
  CELL_HEAD_LEN = 3
  CMD_TYPE_INDEX = 2

  def __init__(self, circuitId, cmdType):
    padding = '0'.zfill(LENGTH - CELL_HEAD_LEN)
    self.buffer = pack('!Hbs', circuitId, cmdType, padding)

  def getCircuitId():
    circuitId, rest = unpack('!Hs', self.buffer)
    return circuitId

  def getCmdId():
    cmdType, rest = unpack_from('!bs', self.buffer, CMD_TYPE_INDEX)
    return cmdType

  def getBuffer():
    return self.buffer

  def toString():
    circuitId, cmdType, rest = unpack(CELL_FORMAT, self.buffer)
    return "Cell: [circuitId: %x, cmdType: %x, rest: %s]" % (circuitId, cmdType, rest)