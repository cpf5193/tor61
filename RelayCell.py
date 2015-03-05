import Cell
import sys
from struct import pack, unpack, pack_into, unpack_from

'''
RelayCell represents a Tor61 Relay cell of any type
'''

class RelayCell(Cell.Cell):
  RELAY_FORMAT = '!HbHHIHbs'
  RELAY_HEAD_LEN = 14
  FILLER = 0x0000
  DIGEST = 0x00000000
  CMD_TYPE = 0x03
  STREAM_ID_INDEX = 3
  BODY_LEN_INDEX = 11
  RELAY_CMD_INDEX = 13

  def __init__(self, circuitId, streamId, bodyLen, relayCmd, body):
    padding = '0'.zfill(LENGTH - RELAY_HEAD_LEN - bodyLen)
    if (body == None):
      endString = padding
    else:
      endString = body + padding
    super().__init__(self, circuitId, CMD_TYPE)
    self.buffer = pack_into('!HHIHbs', self.buffer, STREAM_ID_INDEX, streamId, FILLER, DIGEST, bodyLen, relayCmd, endString)

  def getStreamId():
    streamId, rest = unpack_from('!Hs', self.buffer, STREAM_ID_INDEX)
    return streamId

  def getBodyLen():
    bodyLen, rest = unpack_from('!Hs', self.buffer, BODY_LEN_INDEX)
    return bodyLen

  def getRelayCmd():
    relayCmd, rest = unpack_from('!bs', self.buffer, RELAY_CMD_INDEX)
    return relayCmd

  def getBody():
    bodyLen, relayCmd, rest = unpack_from('!Hbs', self.buffer, BODY_LEN_INDEX)
    body = rest[:bodyLen]
    return body

  def getCommandName():
    names = {
      0x01: 'Begin',
      0x02: 'Data',
      0x03: 'End',
      0x04: 'Connected',
      0x06: 'Extend',
      0x07: 'Extended',
      0x0b: 'Begin Failed',
      0x0c: 'Extend Failed'
    }

    name = names.get(self.getRelayCmd())
    if (name == None):
      raise Exception('Invalid relay command type.')
      sys.exit(1)
    else:
      return name

  def getBuffer():
    return self.buffer

  def setBuffer(buffer):
    self.buffer = buffer

  def toString():
    circuitId, cmdType, streamId, filler, digest, bodyLen, relayCmd, rest = unpack(RELAY_FORMAT, self.buffer)
    return "RelayCell: [circuitId: %x, cmdType: %x, streamId: %x, filler: %x, digest: %x, bodyLen: %x, relayCmd: %x, rest: %s]" % (circuitId, cmdType, streamId, filler, digest, bodyLen, relayCmd, rest)
