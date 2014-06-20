'''
Created on May 12, 2011

@author: olaf
'''

import struct

ctpDebugMsgType = 22 #0x16
ctpDataMsgType = 0xEC
typeOffset = 1
typeLength = 1
payloadOffset = typeOffset + typeLength
payloadLength = 6
seqNoOffset = payloadOffset + payloadLength
seqNoLength = 2
#for ctp data msg
ctpDataoffset = 8
datapayloadlength = 10

NET_C_DEBUG_STARTED = 0xDE

NET_C_FE_MSG_POOL_EMPTY = 0x10      #::no args
NET_C_FE_SEND_QUEUE_FULL = 0x11     #::no args
NET_C_FE_NO_ROUTE = 0x12            #::no args
NET_C_FE_SUBSEND_OFF = 0x13
NET_C_FE_SUBSEND_BUSY = 0x14
NET_C_FE_BAD_SENDDONE = 0x15
NET_C_FE_QENTRY_POOL_EMPTY = 0x16
NET_C_FE_SUBSEND_SIZE = 0x17
NET_C_FE_LOOP_DETECTED = 0x18
NET_C_FE_SEND_BUSY = 0x19

NET_C_FE_SENDQUEUE_EMPTY = 0x50
NET_C_FE_PUT_MSGPOOL_ERR = 0x51
NET_C_FE_PUT_QEPOOL_ERR = 0x5,
NET_C_FE_GET_MSGPOOL_ERR = 0x53
NET_C_FE_GET_QEPOOL_ERR = 0x54
NET_C_FE_QUEUE_SIZE=0x55

NET_C_FE_SENT_MSG = 0x20        #:app. send       :msg uid, origin, next_hop
NET_C_FE_RCV_MSG =  0x21        #:next hop receive:msg uid, origin, last_hop
NET_C_FE_FWD_MSG =  0x22        #:fwd msg         :msg uid, origin, next_hop
NET_C_FE_DST_MSG =  0x23        #:base app. recv  :msg_uid, origin, last_hop
NET_C_FE_SENDDONE_FAIL = 0x24
NET_C_FE_SENDDONE_WAITACK = 0x25
NET_C_FE_SENDDONE_FAIL_ACK_SEND = 0x26
NET_C_FE_SENDDONE_FAIL_ACK_FWD  = 0x27
NET_C_FE_DUPLICATE_CACHE = 0x28             #dropped duplicate packet seen in cache
NET_C_FE_DUPLICATE_QUEUE = 0x29             #dropped duplicate packet seen in queue
NET_C_FE_DUPLICATE_CACHE_AT_SEND = 0x2A     #dropped duplicate packet seen in cache
NET_C_FE_CONGESTION_SENDWAIT = 0x2B         # sendTask deferring for congested parent
NET_C_FE_CONGESTION_BEGIN = 0x2C            # 
NET_C_FE_CONGESTION_END = 0x2D              # congestion over: reason is arg;
                                            #  arg=1 => overheard parent's
                                            #           ECN cleared.
                                            #  arg=0 => timeout.
NET_C_FE_CONGESTED = 0x2E

NET_C_TREE_NO_ROUTE   = 0x30   #:        :no args
NET_C_TREE_NEW_PARENT = 0x31   #:        :parent_id, hopcount, metric
NET_C_TREE_ROUTE_INFO = 0x32   #:periodic:parent_id, hopcount, metric
NET_C_TREE_SENT_BEACON = 0x33
NET_C_TREE_RCV_BEACON = 0x34

NET_C_DBG_1 = 0x40             #:any     :uint16_t a
NET_C_DBG_2 = 0x41             #:any     :uint16_t a, b, c
NET_C_DBG_3 = 0x42             #:any     :uint16_t a, b, c

NET_DC_REPORT = 0x60           #:duty cycle report :uint16_t dutyCycle, uint16_t time
NET_LL_DUPLICATE = 0x61       #dropped duplicate packet seen in cache

NET_APP_SENT = 0x70             #app. send       :msg uid, origin
counterss = 0

class CtpDebugMsg:
    def __init__(self, node, timestamp, type, arg, 
                 msg__msg_uid, msg__origin, msg__other_node, 
                 route_info__parent, route_info__hopcount, route_info__metric,
                 dbg__a, dbg__b, dbg__c, seqno):
        self.node = node
        self.timestamp = timestamp
        self.type = type
        self.arg = arg
        self.msg__msg_uid = msg__msg_uid
        self.msg__origin = msg__origin
        self.msg__other_node = msg__other_node
        self.route_info__parent = route_info__parent
        self.route_info__hopcount = route_info__hopcount
        self.route_info__metric = route_info__metric
        self.dbg__a = dbg__a
        self.dbg__b = dbg__b
        self.dbg__c = dbg__c
        self.seqno = seqno

class SimDebugMsg:
    def __init__(self, node, timestamp, type, dbg__a, dbg__b, dbg__c):
        self.node = node
        self.timestamp = timestamp
        self.type = type
        self.dbg__a = dbg__a
        self.dbg__b = dbg__b
        self.dbg__c = dbg__c
        
class CtpDataMsg:
    def __init__(self, node, timestamp, thl, origin, originSeqNo, parent):
        self.node = node
        self.thl = thl
        self.origin = origin
        self.seqno = originSeqNo
        self.parent = parent
        self.timestamp = timestamp
        
class SimDataMsg:
    def __init__(self, node, timestamp, originSeqNo, origin, thl):
        self.node = node
        self.thl = thl
        self.origin = origin
        self.seqno = originSeqNo
        self.timestamp = timestamp
        
class SimNtMsg:
    def __init__(self, node, timestamp, type, indexesInUse, edc, nextHopEdc):
        self.node = node
        self.timestamp = timestamp
        self.type = type
        self.indexesInUse = indexesInUse
        self.edc = edc
        self.nextHopEdc = nextHopEdc

class RawMsg:
    def __init__(self, type, dbg__a, dbg__b, dbg__c):
        self.type = type
        self.dbg__a = dbg__a
        self.dbg__b = dbg__b
        self.dbg__c = dbg__c
        
class ConnectMsg:
    def __init__(self, node, counter, source, timestamp):
        self.node = node
        self.counter = counter
        self.source = source
        self.timestamp = timestamp

def build(node, timestamp, offset, data):
    type = struct.unpack('!B', data[offset+typeOffset:offset+typeOffset+typeLength])
    arg = struct.unpack('!Hxxxx', data[offset+payloadOffset:offset+payloadOffset+payloadLength])
    msg = struct.unpack('!HHH', data[offset+payloadOffset:offset+payloadOffset+payloadLength])
    routeInfo = struct.unpack('!HBHx', data[offset+payloadOffset:offset+payloadOffset+payloadLength])
    dbg = struct.unpack('!HHH', data[offset+payloadOffset:offset+payloadOffset+payloadLength])
    seqNo = struct.unpack('!H', data[offset+seqNoOffset:offset+seqNoOffset+seqNoLength])
    return CtpDebugMsg(node, timestamp, type[0], arg[0],
                       msg[0], msg[1], msg[2],
                       routeInfo[0], routeInfo[1], routeInfo[2],
                       dbg[0], dbg[1], dbg[2], seqNo[0])           

#for twist's ctp data message

def buildData(node, timestamp, offset, data):
    Ctpheader = struct.unpack('!BBHHBB', data[offset:offset+ctpDataoffset])
    CtpDataMsgs = struct.unpack('!HHHHH', data[offset+ctpDataoffset:offset+ctpDataoffset+datapayloadlength])
    return CtpDataMsg(node, timestamp, Ctpheader[1], Ctpheader[3], Ctpheader[4], CtpDataMsgs[2])
