'''
Created on May 12, 2011

@author: olaf
'''

import struct

ntDebugMsgType = 24
typeOffset = 1
typeLength = 1
edcOffset = typeOffset + typeLength
edcLength = 1
nextHopEdcOffset = edcOffset + edcLength
nextHopEdcLength = 1
indexesInUseOffset = nextHopEdcOffset + nextHopEdcLength
indexesInUseLength = 1
indexesOffset = indexesInUseOffset + indexesInUseLength
indexesLength = 1
seqNumOffset = indexesOffset + indexesLength
seqNumLength = 2
avgDcOffset = seqNumOffset + seqNumLength
avgDcLength = 4
txTimeOffset = avgDcOffset + avgDcLength
txTimeLength = 4
timestampOffset = txTimeOffset + txTimeLength
timestampLength = 4
     
class NtDebugMsg:
    def __init__(self, node, globalTime, type, edc, nextHopEdc, indexesInUse, indexes, seqNum, avgDc, txTime, timestamp):
        self.node = node
        self.globalTime = globalTime
        self.type = type
        self.edc = edc
        self.nextHopEdc = nextHopEdc
        self.indexesInUse = indexesInUse
        self.indexes = indexes
        self.seqNum = seqNum
        self.avgDc = avgDc
        self.txTime = txTime
        self.timestamp = timestamp        

def build(node, globalTime, offset, data):
    type = struct.unpack('!B', data[offset+typeOffset:offset+typeOffset+typeLength])
    edc = struct.unpack('!B', data[offset+edcOffset:offset+edcOffset+edcLength])
    nextHopEdc = struct.unpack('!B', data[offset+nextHopEdcOffset:offset+nextHopEdcOffset+nextHopEdcLength])
    indexesInUse = struct.unpack('!B', data[offset+indexesInUseOffset:offset+indexesInUseOffset+indexesInUseLength])
    indexes = struct.unpack('!B', data[offset+indexesOffset:offset+indexesOffset+indexesLength])

    seqNum = struct.unpack('!H', data[offset+seqNumOffset:offset+seqNumOffset+seqNumLength])    
    avgDc = struct.unpack('!I', data[offset+avgDcOffset:offset+avgDcOffset+avgDcLength])
    txTime = struct.unpack('!I', data[offset+txTimeOffset:offset+txTimeOffset+txTimeLength])
    timestamp = struct.unpack('!I', data[offset+timestampOffset:offset+timestampOffset+timestampLength])
    return NtDebugMsg(node, globalTime, type[0], edc[0], nextHopEdc[0], indexesInUse[0], indexes[0], seqNum[0], avgDc[0], txTime[0], timestamp[0])           
        