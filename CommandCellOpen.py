# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Project 3: Tor61

import Cell
from struct import pack, unpack, pack_into, unpack_from

'''
CommandCellOpen represents an Open, Opened, or Open Failed cell
'''

COMMAND_FORMAT = '!HbII501s'
OPEN_HEAD_LEN = 11
OPENER_ID_INDEX = 3
OPENED_ID_INDEX = 7

class CommandCellOpen(Cell.Cell):
  def __init__(self, circuitId = 0x0000, cmdType = 0x00, openerId = '0', openedId = '0'):
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
    return "%s" % self.buffer
