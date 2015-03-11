import Cell
from struct import pack, unpack, pack_into, unpack_from

'''
CommandCellOpen represents an Open, Opened, or Open Failed
'''

COMMAND_FORMAT = '!HbII501s'
OPEN_HEAD_LEN = 11
OPENER_ID_INDEX = 3
OPENED_ID_INDEX = 7

class CommandCellOpen(Cell.Cell):
  def __init__(self, circuitId, cmdType, openerId, openedId):
    padding = '0'.zfill(Cell.LENGTH - OPEN_HEAD_LEN)
    print "circuitId: ", circuitId, ", cmdType: ", cmdType 
    print "openerId: ", openerId, "openedId: ", openedId
    self.buffer = pack(COMMAND_FORMAT, circuitId, cmdType, int(openerId), int(openedId), padding)

  def setBuffer(self, buffer):
    self.buffer = buffer

  def getOpenerId(self):
    openerId, rest = unpack_from('!I504s', self.buffer, OPENER_ID_INDEX)
    return str(openerId)

  def getOpenedId(self):
    openedId, rest = unpack_from('!I500s', self.buffer, OPENED_ID_INDEX)
    return str(openedId)

  def getBuffer(self):
    return self.buffer

  def toString(self):
    #circuitId, cmdType, openerId, openedId, rest = unpack(COMMAND_FORMAT, self.buffer)
    #return "%x%x%x%x%s" % (circuitId, cmdType, openerId, openedId, rest)
    return "%s" % self.buffer
