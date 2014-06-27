'''
Created on June 18, 2011

@author: Si Li
'''

from functions import  *
import sys
import os
import ctpDebugMsg

filepath = "/home/nagatoyuki/Thesis/CTP_1s.txt"

FILE_TYPE_CTPDEBUG = 0
FILE_TYPE_CTPDATA = 1
FILE_TYPE_ORWDEBUG = 2
FILE_TYPE_ORWNT = 3

def loadDebug(filepath):
	if not os.path.isfile(filepath):
		sys.exit("File does not exist!")
	CtpDebugMsgs = []
	CtpDataMsgs = []
	OrwDebugMsgs = []
	OrwNtMsgs = []
	
	with open(filepath, 'rb') as f:
		lines = f.readlines()
		for row in lines:
			row = mysplit(row)
			if len(row) == 7:
				time = row[0].split(':')
				if len(time) == 2:
					timestamp = int(time[0])*60 + float(time[1])
				else:
					timestamp = int(time[0])*3600 + int(time[1])*60 + float(time[2])
				#get the node ID
				node = int((row[1].split(':'))[1])
				filetype = int(row[2])
				if filetype == FILE_TYPE_CTPDEBUG:
					#debug msgs, get into dbg__a, dbg__b, msg.dbg__c
					CtpDebugMsgs.append(ctpDebugMsg.SimDebugMsg(node, timestamp, int(row[3]), int(row[4]), int(row[5]), int(row[6])))
				elif filetype == FILE_TYPE_CTPDATA:
					CtpDataMsgs.append(ctpDebugMsg.SimDataMsg(node, timestamp, int(row[4]), int(row[5]), int(row[6])))
				elif filetype == FILE_TYPE_ORWDEBUG:
					OrwDebugMsgs.append(ctpDebugMsg.SimDebugMsg(node, timestamp, int(row[3]), int(row[4]), int(row[5]), int(row[6])))
				elif filetype == FILE_TYPE_ORWNT:
					OrwNtMsgs.append(ctpDebugMsg.SimNtMsg(node, timestamp, int(row[3]), int(row[4]), int(row[5]), int(row[6])))

	return CtpDebugMsgs, CtpDataMsgs, OrwDebugMsgs, OrwNtMsgs
				
if __name__ == '__main__':
	loadDebug(filepath)