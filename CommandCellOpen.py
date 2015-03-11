import Cell
from struct import pack, unpack, pack_into, unpack_from

'''
CommandCellOpen represents an Open, Opened, or Open Failed
'''

COMMAND_FORMAT = '!HbIIs'
OPEN_HEAD_LEN = 11
OPENER_ID_INDEX = 3
OPENED_ID_INDEX = 7

class CommandCellOpen(Cell.Cell):
  def __init__(self, circuitId, cmdType, openerId, openedId):
    padding = '0'.zfill(Cell.LENGTH - OPEN_HEAD_LEN)
    print "openerId: ", openerId, "openedId: ", openedId
    self.buffer = pack(COMMAND_FORMAT, circuitId, cmdType, int(openerId), int(openedId), padding)

  def setBuffer(buffer):
    self.buffer = buffer

  def getOpenerId(self):
    openerId, rest = unpack_from('!Is', self.buffer, OPENER_ID_INDEX)
    return openerId

  def getOpenedId(self):
    openedId, rest = unpack_from('!Is', self.buffer, OPENED_ID_INDEX)
    return openedId

  def getBuffer(self):
    return self.buffer

  def toString(self):
    circuitId, cmdType, openerId, openedId, rest = unpack(COMMAND_FORMAT, self.buffer)
    return "%x%x%x%x%s" % (circuitId, cmdType, openerId, openedId, rest)
