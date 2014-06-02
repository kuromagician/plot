'''
Created on Jun 9, 2011

@author: olaf
'''
import struct

ntDumpMsgType = 25
seqNumOffset = 1;
seqNumLength = 2;
dumpNumOffset = seqNumOffset + seqNumLength
dumpNumLength = 1

entryOffset = dumpNumOffset + dumpNumLength
entryCount = 5
entryAddrSubOffset = 0
entryAddrLength = 2
entryCountSubOffset = entryAddrSubOffset + entryAddrLength
entryCountLength = 1
entryEdcSubOffset = entryCountSubOffset + entryCountLength
entryEdcLength = 1
entryPSubOffset = entryEdcSubOffset + entryEdcLength
entryPLength = 1
entryLength = entryAddrLength + entryCountLength + entryEdcLength + entryPLength

class NtDumpEntry:
    def __init__(self, addr, count, edc, p):
        self.addr = addr
        self.count = count
        self.edc = edc
        self.p = p
     
class NtDumpMsg:
    def __init__(self, node, globalTime, seqNum, dumpNum, entries):
        self.node = node
        self.globalTime = globalTime
        self.seqNum = seqNum
        self.dumpNum = dumpNum
        self.entries = entries

def build(node, globalTime, offset, data):
    seqNum = struct.unpack('!H', data[offset+seqNumOffset:offset+seqNumOffset+seqNumLength])
    dumpNum = struct.unpack('!B', data[offset+dumpNumOffset:offset+dumpNumOffset+dumpNumLength])
    entries = []
    for i in range(0, entryCount):
        localOffset = offset+entryOffset+(i * entryLength)
        addr = struct.unpack('!H', data[localOffset+entryAddrSubOffset:localOffset+entryAddrSubOffset+entryAddrLength])
        count = struct.unpack('!B', data[localOffset+entryCountSubOffset:localOffset+entryCountSubOffset+entryCountLength])
        edc = struct.unpack('!B', data[localOffset+entryEdcSubOffset:localOffset+entryEdcSubOffset+entryEdcLength])
        p = struct.unpack('!B', data[localOffset+entryPSubOffset:localOffset+entryPSubOffset+entryPLength])
        entry = NtDumpEntry(addr[0], count[0], edc[0], p[0])
        entries.append(entry)
    return NtDumpMsg(node, globalTime, seqNum[0], dumpNum[0], entries)
        