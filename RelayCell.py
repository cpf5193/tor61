# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Project 3: Tor61

import Cell
import sys
from struct import pack, unpack, pack_into, unpack_from

'''
RelayCell represents a Tor61 Relay cell of any type
'''

class RelayCell(Cell.Cell):
  RELAY_FORMAT = '!HbHHIHb498s'
  RELAY_HEAD_LEN = 14
  FILLER = 0x0000
  DIGEST = 0x00000000
  CMD_TYPE = 0x03
  STREAM_ID_INDEX = 3
  BODY_LEN_INDEX = 11
  RELAY_CMD_INDEX = 13

  def __init__(self, circuitId = 0x0000, streamId = 0x0000, bodyLen = 0x0000, relayCmd = 0x00, body=None):
    padding = '0'.zfill(Cell.LENGTH - self.RELAY_HEAD_LEN - bodyLen)
    if (body == None):
      endString = padding
    else:
      endString = body + padding
    self.buffer = pack(self.RELAY_FORMAT, circuitId, self.CMD_TYPE, streamId, self.FILLER, self.DIGEST, bodyLen, relayCmd, endString)

  def getStreamId(self):
    streamId, rest = unpack_from('!H507s', self.buffer, self.STREAM_ID_INDEX)
    return int(streamId)

  def getBodyLen(self):
    bodyLen, rest = unpack_from('!H499s', self.buffer, self.BODY_LEN_INDEX)
    return int(bodyLen)

  def getRelayCmd(self):
    relayCmd, rest = unpack_from('!b498s', self.buffer, self.RELAY_CMD_INDEX)
    return hex(relayCmd)

  def getBody(self):
    bodyLen, relayCmd, rest = unpack_from('!Hb498s', self.buffer, self.BODY_LEN_INDEX)
    body = rest[:bodyLen]
    return body

  def getBuffer(self):
    return self.buffer

  def setBuffer(self, buffer):
    self.buffer = buffer

  def toString(self):
    return "%s" % self.buffer
