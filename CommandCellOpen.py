import Cell
from struct import pack, unpack, pack_into, unpack_from

'''
CommandCellOpen represents an Open, Opened, or Open Failed
'''

class CommandCellOpen(Cell.Cell):
  COMMAND_FORMAT = '!HbIIs'
  OPEN_HEAD_LEN = 11
  OPENER_ID_INDEX = 3
  OPENED_ID_INDEX = 7

  def __init__(self, circuitId, cmdType, openerId, openedId):
    padding = '0'.zfill(LENGTH - OPEN_HEAD_LEN)
    super().__init__(self, circuitId, cmdType)
    self.buffer = pack_into('!IIs', self.buffer, OPENER_ID_INDEX, openerId, openedId, padding)

  def setBuffer(buffer):
    self.buffer = buffer

  def getOpenerId():
    openerId, rest = unpack_from('!Is', self.buffer, OPENER_ID_INDEX)
    return openerId

  def getOpenedId():
    openedId, rest = unpack_from('!Is', self.buffer, OPENED_ID_INDEX)
    return openedId

  def getBuffer():
    return self.buffer

  def toString():
    circuitId, cmdType, openerId, openedId, rest = unpack(COMMAND_FORMAT, self.buffer)
    return "CommandCellOpen: [circuitId: %x, cmdType: %x, openerId: %x, openedId: %x, rest: %s]" % (circuitId, cmdType, openerId, openedId, rest)
