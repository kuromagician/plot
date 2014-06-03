#!/usr/bin/python
from tools.constant import *
from tools.functions import *
import tools.command as command
import tools.reader as reader
import sys
from collections import defaultdict
import matplotlib
import pylab as pl
from numpy import mean
from numpy import absolute
import tools.twistReader as Treader
import numpy as np
import tools.calprop as calprop
import csv

result = command.main(sys.argv[1:])

#constants maybe used in this file
TWIST = result['twist']
CHECK = result['check']
FileDict = {}
if not TWIST:
	if result['desktop']:
		base_path = '/home/nagatoyuki/Thesis/Traces/Indriya/'
	else:
		base_path = '/media/Data/ThesisData/Indriya/'
	FileNames = {'OrwDebug':('23739.dat',), 'CtpDebug':('24460.dat',), 
				'CtpData':('24463.dat',), 'ConnectDebug':('25593.dat',),
				'OrwNt':('23738.dat',)}
	if not CHECK:
		#file path and wakeup range
		wakeup = [0.25, 0.5, 1, 1.5, 2, 2.5, 4, 6, 16]
		FileCollection_orw = ['data-48680', 'data-48564', 'data-48640', 'data-48627', 
							'data-48623', 'data-48631', 'data-48646', 'data-48714', 'data-48775']
		FileCollection_ctp = ['data-48672', 'data-48556', 'data-48639', 'data-48641', 
							'data-48637', 'data-48642', 'data-48651', 'data-48710', 'data-48774']
	else:
		wakeup = [0.25, 0.5, 1, 2, 4, 8, 16]
		'''FileCollection_orw = ['data-48795', 'data-48847', 'data-48848', 'data-48849', 
							'data-48850', 'data-48851']
		FileCollection_ctp = ['data-48828', 'data-48829', 'data-48836', 'data-48837', 
							'data-48839', 'data-48846']'''
		FileCollection_orw = ['data-48936', 'data-48934', 'data-48933', 'data-48932', 
							'data-48931', 'data-48930', 'data-48952']
		FileCollection_ctp = ['data-48929', 'data-48928', 'data-48925', 'data-48924', 
							'data-48923', 'data-48922', 'data-48949']
else:
	base_path = '/media/Data/ThesisData/Twist/'
	if not CHECK:
		FileCollection_orw = ['trace_20140515_132005.1.txt', 'trace_20140515_160513.3.txt', 
							'trace_20140515_185012.5.txt', 'trace_20140515_210915.7.txt',
							'trace_20140515_232715.9.txt', 'trace_20140516_031415.11.txt']
							#'trace_20140518_231215.38.txt']
		
		FileCollection_ctp = ['trace_20140515_120916.0.txt', 'trace_20140515_145530.2.txt', 
							'trace_20140515_174113.4.txt', 'trace_20140515_200012.6.txt', 
							'trace_20140515_221814.8.txt', 'trace_20140516_020516.10.txt']
							#'trace_20140518_220334.37.txt']
		wakeup = [0.25, 0.5, 1, 2, 4, 8]#16]
	else:
		FileCollection_orw = ['trace_20140516_182314.19.txt', 'trace_20140516_125914.15.txt', 
							'trace_20140516_160435.17.txt', 'trace_20140516_054116.13.txt',
							'trace_20140516_204414.21.txt', 'trace_20140516_230416.23.txt']
							#'trace_20140519_015714.40.txt']
		
		FileCollection_ctp = ['trace_20140516_171413.18.txt', 'trace_20140516_115018.14.txt', 
							'trace_20140517_004915.24.txt', 'trace_20140516_043214.12.txt', 
							'trace_20140516_193515.20.txt', 'trace_20140516_215516.22.txt']
							#'trace_20140519_002313.39.txt']
		wakeup = [0.25, 0.5, 1, 2, 4, 8.7]

#parameters


Tmin = 6.0

Trx = 25.0
#time needed for a transmition to sink
Ttx = 3.0 + 3.0 + 20 #cca + trans+ack + post(20ms)

Tpost=20.0
Tipi = 1000*60.0
Tibi = 8*1000*60.0

y = []
for test in FileCollection_orw:
	if not TWIST:
		FileDict['OrwDebug'] = reader.loadDebug(base_path + test, FileNames['OrwDebug']) 
	else:
		FileDict['OrwDebug'], FileDict['OrwNt'], _, _ = Treader.load(base_path + test) 
	prop_orw = calprop.prop_orw(FileDict, result)
	templist = []
	d1, d2, d3 = Seperate_Avg(prop_orw['Avg_Total_dc'], prop_orw['Dir_Neig'],
							prop_orw['Relay'], prop_orw['Leaf'])
	y.append((d1, d2, d3))
	print "Dir_Neig:{:.2f}	Relay:{:.2f} 	Leaf:{:.2f}".format(d1, d2, d3)
	
fig = pl.figure()

ax = fig.add_subplot(1,1,1)
ym = np.array(y)
ax.plot(wakeup, ym[:,0], ls='--', color='b', label='ORW_SN')
ax.plot(wakeup, ym[:,1], ls='--', color='r',label='ORW_RL')
ax.plot(wakeup, ym[:,2], ls='--', color='g',label='ORW_LF')



####################write to a file, no need to recompute#######################
####################write to a file, no need to recompute#######################
if TWIST:
	fo = open("DC_measure_twist.txt", "a")
else:
	fo = open("DC_measure_indriya.txt", "a")
title = 'WakeupT\tSinkN\tRelay\tLeaf\tProto\tTw\n'
#fo.write(title)
for i, item in enumerate(y):
	msg = "{:^6.2f}\t{:^6.2f}\t{:^6.2f}\t{:^6.2f}\t{:^8s}\t{:^8s}\n".format(wakeup[i], item[0], item[1], item[2], "ORW", str(CHECK))
	fo.write(msg)
	
################################################################################



y = []
for test in FileCollection_ctp:
	if not TWIST:
		FileDict['CtpDebug'] = reader.loadDebug(base_path + test, FileNames['CtpDebug']) 
		FileDict['CtpData'] = reader.loadDataMsg(base_path + test, FileNames['CtpData'])
	else:
		FileDict['CtpDebug'], _, _, FileDict['CtpData'] = Treader.load(base_path + test)
	prop_ctp = calprop.prop_ctp(FileDict, result)
	d1, d2, d3 = Seperate_Avg(prop_ctp['Avg_Total_dc'], prop_ctp['Dir_Neig'],
							prop_ctp['Relay'], prop_ctp['Leaf'])
	y.append((d1, d2, d3))
	print "Dir_Neig:{:.2f}\tRelay:{:.2f}\tLeaf:{:.2f}".format(d1, d2, d3)

for i, item in enumerate(y):
	msg = "{:^6.2f}\t{:^6.2f}\t{:^6.2f}\t{:^6.2f}\t{:^8s}\t{:^8s}\n".format(wakeup[i], item[0], item[1], item[2], "CTP", str(CHECK))
	fo.write(msg)
	
fo.close()

ym = np.array(y)
ax.plot(wakeup, ym[:,0], color="b", label='CTP_SN')
ax.plot(wakeup, ym[:,1], color="r", label='CTP_RL')
ax.plot(wakeup, ym[:,2], color="g", label='CTP_LF')
ax.legend()
pl.show()


####################################### PARAMETERS TREND ############################
#######################################       CTP        ############################
'''

F_SN = [] 
Tao_SN = [] 
N_SN = []
L_SN = [] 
Fail_SN = []

F_RL = [] 
Tao_RL = [] 
N_RL = []
L_RL = [] 
Fail_RL = []

F_LF = [] 
Tao_LF = [] 
N_LF = []
L_LF = [] 
Fail_LF = []
SN_Paras = [F_SN, Tao_SN, N_SN, L_SN, Fail_SN]
RL_Paras = [F_RL, Tao_RL, N_RL, L_RL, Fail_RL]
LF_Paras = [F_LF, Tao_LF, N_LF, L_LF, Fail_LF]

#for wake in wakeup:
with open("CTP_Paras.txt", "r") as csvfile:
	fileReader = csv.reader(csvfile)
	for j, row in enumerate(fileReader):
		a = mysplit(row[0])
		if a[1] == 'SN':
			for i, item in enumerate(SN_Paras):
				item.append(a[i+2])
		if a[1] == 'RL':
			for i, item in enumerate(RL_Paras):
				item.append(a[i+2])
		if a[1] == 'LF':
			for i, item in enumerate(LF_Paras):
				item.append(a[i+2])
			
print SN_Paras

linestyles = ['-', '--', ':']

fig = pl.figure()
labellist=['F', 'Tao', 'N', 'L', 'Fail']

ax1 = fig.add_subplot(3,1,1)
for i, item in enumerate(SN_Paras):
	du, = ax1.plot(wakeup, item, linestyle=linestyles[i%3], label=labellist[i])
ax1.legend(ncol=5, fontsize=10, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           mode="expand", borderaxespad=0.)

ax2 = fig.add_subplot(3,1,2)
for i, item in enumerate(RL_Paras):
	ax2.plot(wakeup, item, linestyle=linestyles[i%3], label=labellist[i])
ax2.legend(ncol=5, fontsize=10, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           mode="expand", borderaxespad=0.)

ax3 = fig.add_subplot(3,1,3)
for i, item in enumerate(LF_Paras):
	ax3.plot(wakeup, item, linestyle=linestyles[i%3], label=labellist[i])
ax3.legend(ncol=5, fontsize=10, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           mode="expand", borderaxespad=0.)


####################################### PARAMETERS TREND ############################
#######################################       ORW        ############################

F_SN = [] 
Tao_SN = [] 
Fs_SN = []
L_SN = [] 
FWD_SN = []

F_RL = [] 
Tao_RL = [] 
Fs_RL = []
L_RL = [] 
FWD_RL = []

F_LF = [] 
Tao_LF = [] 
Fs_LF = []
L_LF = [] 
FWD_LF = []
SN_Paras = [F_SN, Tao_SN, Fs_SN, L_SN, FWD_SN]
RL_Paras = [F_RL, Tao_RL, Fs_RL, L_RL, FWD_RL]
LF_Paras = [F_LF, Tao_LF, Fs_LF, L_LF, FWD_LF]
def mysplit(s, delim=None):
    return [x for x in s.split(delim) if x]
#for wake in wakeup:
with open("ORW_Paras.txt", "r") as csvfile:
	fileReader = csv.reader(csvfile)
	for j, row in enumerate(fileReader):
		a = mysplit(row[0])
		if a[1] == 'SN':
			for i, item in enumerate(SN_Paras):
				item.append(a[i+2])
		if a[1] == 'RL':
			for i, item in enumerate(RL_Paras):
				item.append(a[i+2])
		if a[1] == 'LF':
			for i, item in enumerate(LF_Paras):
				item.append(a[i+2])
			
print SN_Paras
fig = pl.figure()

labellist=['F', 'Tao', 'Fs', 'L', 'FWD']

ax1 = fig.add_subplot(3,1,1)
for i, item in enumerate(SN_Paras):
	du, = ax1.plot(wakeup, item, linestyle=linestyles[i%3], label=labellist[i])
ax1.legend(ncol=5, fontsize=10, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           mode="expand", borderaxespad=0.)

ax2 = fig.add_subplot(3,1,2)
for i, item in enumerate(RL_Paras):
	ax2.plot(wakeup, item, linestyle=linestyles[i%3], label=labellist[i])
ax2.legend(ncol=5, fontsize=10, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           mode="expand", borderaxespad=0.)

ax3 = fig.add_subplot(3,1,3)
for i, item in enumerate(LF_Paras):
	ax3.plot(wakeup, item, linestyle=linestyles[i%3], label=labellist[i])
ax3.legend(ncol=5, fontsize=10, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           mode="expand", borderaxespad=0.)

pl.show()
'''
'''
F_SN = [] 
Tao_SN = [] 
N_SN = []
L_SN = [] 
Fail_SN = []

F_RL = [] 
Tao_RL = [] 
N_RL = []
L_RL = [] 
Fail_RL = []

F_LF = [] 
Tao_LF = [] 
N_LF = []
L_LF = [] 
Fail_LF = []
SN_Paras = [F_SN, Tao_SN, N_SN, L_SN, Fail_SN]
RL_Paras = [F_RL, Tao_RL, N_RL, L_RL, Fail_RL]
LF_Paras = [F_LF, Tao_LF, N_LF, L_LF, Fail_LF]

if not TWIST:
	path = 'DC_measure.txt'
else:
	path = 'DC_measure_twist.txt'
with open(path, "r") as csvfile:
	fileReader = csv.reader(csvfile)
	for j, row in enumerate(fileReader):
		a = mysplit(row[0])
		if a[1] == 'SN':
			for i, item in enumerate(SN_Paras):
				item.append(float(a[i+2]))
		if a[1] == 'RL':
			for i, item in enumerate(RL_Paras):
				item.append(float(a[i+2]))
		if a[1] == 'LF':
			for i, item in enumerate(LF_Paras):
				item.append(float(a[i+2]))

#classic definition
def DC_Model_ctp(F, Tao, N, L, Fail, Tw):
	#dc = Tc/Tw + Tw/Tibi + Trx/Tibi*N/6 + (Fail)*Tw/Tipi + Tw/5/Tipi*F + (Trx)/Tipi*L
	if F > 3:
		F = F*1.0/min(F, 4)
	dc = Tc/Tw + Tw/Tibi + Trx/Tibi*N/6 + Tw/2/Tipi*F + (Trx)/Tipi*L
	return dc*100
	
def DC_Model_ctp_SN(F, Tao, N, L, Fail, Tw):
	#dc = Tc/Tw + Tw/Tibi  + Ttx/Tipi*F*Tao + (Trx)/Tipi*L
	dc = Tc/Tw + Tw/Tibi + Trx/Tibi*N/6 + Ttx/Tipi*F + (Trx)/Tipi*L
	#print F, type(F), Tao, type(Tao), N, type(N), L, type(L), Fail, type(Fail), Tw, type(Tw)
	return dc*100
	
#add the miss chance 4/11
def DC_Model_ctp_k(F, Tao, N, L, Fail, Tw):
	#dc = Tc/Tw + Tw/Tibi + Trx/Tibi*N/6 + (Fail)*Tw/Tipi + Tw/5/Tipi*F + (Trx)/Tipi*L
	dc = 6/Tw + Tw/Tibi + Trx/Tibi*N/6 + (4/11*Tw + Tw/2)/Tipi*F + (Trx)/Tipi*L
	return dc*100

	
y_SN=[]
y_RL=[]
y_LF=[]
y_LF_k=[]
y_RL_k=[]
ID_I_WANT = 3
Tc = 11	

for i, time in enumerate(wakeup):
	temp = DC_Model_ctp_SN(*(zip(*SN_Paras)[ID_I_WANT]), Tw=wakeup[i]*1000.0)
	y_SN.append(temp)
	temp = DC_Model_ctp(*(zip(*RL_Paras)[ID_I_WANT]), Tw=wakeup[i]*1000.0)
	y_RL_k.append(DC_Model_ctp_k(*(zip(*RL_Paras)[ID_I_WANT]), Tw=wakeup[i]*1000.0))
	y_RL.append(temp)
	temp = DC_Model_ctp(*(zip(*LF_Paras)[ID_I_WANT]), Tw=wakeup[i]*1000.0)
	y_LF_k.append(DC_Model_ctp_k(*(zip(*LF_Paras)[ID_I_WANT]), Tw=wakeup[i]*1000.0))
	y_LF.append(temp)
	

	
	
fig = pl.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.plot(wakeup, y_SN)
ax1.plot(wakeup, y_RL)
ax1.plot(wakeup, y_LF)
ax1.plot(wakeup, y_RL_k, '--')
ax1.plot(wakeup, y_LF_k, '--')

y1 = []
y2 = []
y3 = []
if not TWIST:
	path = 'DC_measure.txt'
else:
	path = 'DC_measure_twist.txt'
with open(path) as fo:
	lines = fo.readlines()
	for row in lines:
		content = mysplit(row)
		if content[4] == 'CTP':
			y1.append(content[1])
			y2.append(content[2])
			y3.append(content[3])
ax1.scatter(wakeup, y1)		
ax1.scatter(wakeup, y2)	
ax1.scatter(wakeup, y3)	

pl.show()
'''	
