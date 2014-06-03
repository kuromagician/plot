import csv
import numpy as np
from StringIO import StringIO
import os
import ctpDebugMsg
import ntDebugMsg

def run(path, fileNames):
	loadDebug(path, fileNames)

#same for both ctp and orw from indriya
def loadDebug(path, fileNames):
    DebugMsgs = []
    hit = False
    for fileName in fileNames:
        file = os.path.join(path, fileName)
        if os.path.isfile(file):
            hit = True
            f = open(file, 'rb')
            fileReader = csv.reader(f, delimiter='\t')
            startTime = long(0)
            next(fileReader)
            for row in fileReader:
                type, arg,\
                msg__msg_uid, msg__origin, msg__other_node,\
                route_info__parent, route_info__hopcount, route_info__metric,\
                dbg__a, dbg__b, dbg__c,\
                seqno, _, motelabMoteID, milli_time, _ = row
                node = int(motelabMoteID) - 40000
                if startTime == 0:
                    startTime = long(milli_time)
                timestamp = (long(milli_time) - startTime)
                DebugMsgs.append(ctpDebugMsg.CtpDebugMsg(node, timestamp, int(type), int(arg), 
                         int(msg__msg_uid), int(msg__origin), int(msg__other_node), 
                         int(route_info__parent), int(route_info__hopcount), int(route_info__metric),
                         int(dbg__a), int(dbg__b), int(dbg__c), int(seqno)))
            f.close()
    if hit == False:
        print 'Error, no trace file found:'
        for fileName in fileNames:
            file = os.path.join(path, fileName)
            print file
    return DebugMsgs

#load the message from sink of ctp 
def loadDataMsg(path, fileNames):
    DataMsgs = []
    hit = False
    for fileName in fileNames:
        file = os.path.join(path, fileName)
        if os.path.isfile(file):
            hit = True
            f = open(file, 'rb')
            fileReader = csv.reader(f, delimiter='\t')
            startTime = long(0)
            next(fileReader)
            for row in fileReader:
                options, thl, etx, origin, originSeqNo, type, source, seqno, parent, \
                metric,data ,hopcount, sendCount, sendSuccessCount, _, motelabMoteID, milli_time, _ = row
                node = int(motelabMoteID) - 40000
                if startTime == 0:
                    startTime = long(milli_time)
                timestamp = (long(milli_time) - startTime)
                DataMsgs.append(ctpDebugMsg.CtpDataMsg(node, timestamp, int(thl), int(origin), int(originSeqNo), int(parent)))
            f.close()
    if hit == False:
        print 'Error, no trace file found:'
        for fileName in fileNames:
            file = os.path.join(path, fileName)
            print file
    return DataMsgs

#raw data acquired from own testing
def load_raw(path, fileNames):
    rawdata = []
    hit = False
    for fileName in fileNames:
        file = os.path.join(path, fileName)
        if os.path.isfile(file):
            hit = True
            f = open(file, 'rb')
            fileReader = csv.reader(f, delimiter=' ')
            for row in fileReader:
                type, dbg__a, dbg__b, dbg__c = row[8], row[9] + row[10], row[11] + row[12], row[13] + row[14]
                rawdata.append(ctpDebugMsg.RawMsg(int(type, 16), int(dbg__a, 16), int(dbg__b, 16), int(dbg__c, 16)))
            f.close()
    if hit == False:
        print 'Error, no trace file found:'
        for fileName in fileNames:
            file = os.path.join(path, fileName)
            print file
    return rawdata
    
#load connectivity data
def load_C_Data(path, fileNames):
    C_Data = []
    hit = False
    for fileName in fileNames:
        file = os.path.join(path, fileName)
        if os.path.isfile(file):
            hit = True
            f = open(file, 'rb')
            fileReader = csv.reader(f, delimiter='\t')
            startTime = long(0)
            next(fileReader)
            for row in fileReader:
                counter, source, _, motelabMoteID, milli_time, _ = row
                node = int(motelabMoteID) - 40000
                if startTime == 0:
                    startTime = long(milli_time)
                timestamp = (long(milli_time) - startTime)
                C_Data.append(ctpDebugMsg.ConnectMsg(node, int(counter), int(source), timestamp))
            f.close()
    if hit == False:
        print 'Error, no trace file found:'
        for fileName in fileNames:
            file = os.path.join(path, fileName)
            print file
    return C_Data

def loadNtDebug(path, fileNames):
    ntDebugMsgs = []
    for fileName in fileNames:
        file = os.path.join(path, fileName)
        if os.path.isfile(file):
            file = os.path.join(path, fileName)
            f = open(file, 'rb')
            fileReader = csv.reader(f, delimiter='\t')
            startTime = long(0)
            try:
                next(fileReader)
            except StopIteration:
                pass
            for row in fileReader:
                if len(row) == 13:
                    type, edc, nextHopEdc, indexesInUse, indexes, seqNum, avgDc, txTime,\
                    timestamp, _, motelabMoteID, milli_time, _ = row
                    node = int(motelabMoteID) - 40000
                    if startTime == 0:
                        startTime = long(milli_time)
                    globalTime = (long(milli_time) - startTime) * 1000
                    ntDebugMsgs.append(ntDebugMsg.NtDebugMsg(node, globalTime, 
                             int(type), int(edc), int(nextHopEdc), int(indexesInUse), 
                             int(indexes), int(seqNum), int(avgDc), int(txTime), int(timestamp)))            
            f.close()
    return ntDebugMsgs

if __name__ == '__main__':
	run('/home/nagatoyuki/Desktop/Thesis/Indriya/data-43811', ('23739.dat',))
