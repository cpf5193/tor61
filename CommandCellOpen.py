import Cell
from struct import pack, unpack

'''
CommandCellOpen represents an Open, Opened, or Open Failed
'''

class CommandCellOpen(Cell):
  COMMAND_FORMAT = '!HbIIs'
  OPEN_HEAD_LEN = 11
  OPENER_ID_INDEX = 3
  OPENED_ID_INDEX = 7

  def __init__(self, circuitId, cmdType):
    padding = '0'.zfill(LENGTH - OPEN_HEAD_LEN)
    self.buffer = pack(COMMAND_FORMAT, circuitId, cmdType, openerId, openedId, padding)

  def getOpenerId():
    openerId, rest = unpack_from('!Is', self.buffer, OPENER_ID_INDEX)
    return openerId

  def getOpenedId():
    openedId, rest = unpack_from('!Is', self.buffer, OPENED_ID_INDEX)
    return openedId

  def getBuffer():
    return self.buffer