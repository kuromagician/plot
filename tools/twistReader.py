'''
Created on May 12, 2011

@author: olaf
'''
import struct
import os

import ctpDebugMsg
import ntDebugMsg
import ntDumpMsg
msgTypeMsgOffset = 7
msgTypeLength = 1
#for ctp data msg only
DataMsgOffset = 8

def convertLine(dataLine):
    #data = ''.join(chr(int(x, 16)) for x in dataLine.rstrip().split(' '))
    dataLine = dataLine.rstrip()
    strList = []
    while dataLine != '':
        str = dataLine[:2]
        dataLine = dataLine[2:]
        num = int(str,16)
        strList.append(chr(num))
    return ''.join(strList)    

def buildFromTwistDump(line, ctpDebugMsgs, ntDebugMsgs, ntDumpMsgs, ctpDataMsgs, startTime):
    #1312895334.579399 218 00ffff00001c001900150000bb01024a00c501034a00e001034a005701044a00ba01044a
    timestampStr, nodeStr, dataStr = line.split(' ', 2)
    node = int(nodeStr)
    if startTime == 0:
        startTime = float(timestampStr)
    timestamp = long((float(timestampStr) - startTime) * 1000 * 1000)
    data = convertLine(dataStr)
    msgType = struct.unpack('<B', data[msgTypeMsgOffset:msgTypeMsgOffset+msgTypeLength])
    if msgType[0] == ctpDebugMsg.ctpDebugMsgType:        
        ctpDebugMsgs.append(ctpDebugMsg.build(node, timestamp, msgTypeMsgOffset, data))
    elif msgType[0] == ntDebugMsg.ntDebugMsgType:
        ntDebugMsgs.append(ntDebugMsg.build(node, timestamp, msgTypeMsgOffset, data))        
    elif msgType[0] == ntDumpMsg.ntDumpMsgType:
        ntDumpMsgs.append(ntDumpMsg.build(node, timestamp, msgTypeMsgOffset, data))
    elif msgType[0] == ctpDebugMsg.ctpDataMsgType: 
		if len(data) == 31:
			ctpDataMsgs.append(ctpDebugMsg.buildData(node, timestamp, DataMsgOffset, data))
    return startTime        
    
def load(file):
    ctpDebugMsgs = []
    ntDebugMsgs = []
    ntDumpMsgs = []
    ctpDataMsgs = []
    startTime = long(0)
    with open(file) as f:
        for line in f:
            if not line.startswith('#'):
                startTime = buildFromTwistDump(line, ctpDebugMsgs, ntDebugMsgs, ntDumpMsgs, ctpDataMsgs, startTime)
    return ctpDebugMsgs, ntDebugMsgs, ntDumpMsgs, ctpDataMsgs

def createPath(file):
    path,file = os.path.split(file)
    ret = os.path.join(path, file + '-trace')
    if not os.path.exists(ret):
        os.mkdir(ret)
    return ret

'''def run(oppFile, ctpFile):
    routeOpp, ntOpp, dumpOpp = load(oppFile)
    routeCtp, _, _ = load(ctpFile) 
    
    oppPath = createPath(oppFile)
    #ctpPath = createPath(ctpFile)
    
if __name__ == '__main__':
    run('/Users/olaf/Documents/projects/opp/svn/experiments/twist/w/w1_trace_20110809_150854.0.txt', 
        '/Users/olaf/Documents/projects/opp/svn/experiments/twist/w/w1_trace_20110809_150854.0.txt')'''



