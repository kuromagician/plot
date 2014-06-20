#!/usr/bin/python
import tools.twistReader as Treader
import tools.command as command
import tools.calprop as calprop
from numpy import mean
import matplotlib
import pylab as pl
from tools.functions import *
import sys

FileDict = {}

base_path = '/media/Data/ThesisData/Twist/'
FileCollection_orw = ['trace_20140515_132005.1.txt', 'trace_20140515_160513.3.txt', 
							'trace_20140515_185012.5.txt', 'trace_20140515_210915.7.txt',
							'trace_20140515_232715.9.txt', 'trace_20140516_031415.11.txt']
		
FileCollection_ctp = ['trace_20140515_120916.0.txt', 'trace_20140515_145530.2.txt', 
							'trace_20140515_174113.4.txt', 'trace_20140515_200012.6.txt', 
							'trace_20140515_221814.8.txt', 'trace_20140516_020516.10.txt']
result = command.main(sys.argv[1:])


'''for test in FileCollection_ctp:
	FileDict['CtpDebug'], _, _, FileDict['CtpData'] = Treader.load(base_path + test)
	props_ctp = calprop.prop_ctp(FileDict, result)
	print Seperate_Avg(props_ctp['Avg_Total_dc'], props_ctp['Dir_Neig'], props_ctp['Relay'], props_ctp['Leaf'])
	#print sorted(props_ctp['Avg_Total_dc'].keys())
	#print sorted(props_ctp['Dir_Neig'])'''
'''for test in FileCollection_orw:
	FileDict['OrwDebug'], FileDict['OrwNt'], _, _  = Treader.load(base_path + test)
	props_orw = calprop.prop_orw(FileDict, result)
	print Seperate_Avg(props_orw['Avg_Total_dc'], props_orw['Dir_Neig'], props_orw['Relay'], props_orw['Leaf'])'''

x1 = []
x2 = []
y1_ctp = []
y2_ctp = []
y3_ctp = []
y1_ctp_c = []
y2_ctp_c = []
y3_ctp_c = []
y1_orw = []
y2_orw = []
y3_orw = []
y1_orw_c = []
y2_orw_c = []
y3_orw_c = []

if result['twist']:
	path = "DC_measure_twist.txt"
else:
	path = "DC_measure_indriya.txt"

with open(path) as fo:
	lines = fo.readlines()
	for row in lines:
		row = mysplit(row)
		if row[5] == 'True':
			if row[4] == 'CTP':
				y1_ctp_c.append(row[1])
				y2_ctp_c.append(row[2])
				y3_ctp_c.append(row[3])
				x2.append(float(row[0]))
			else:
				y1_orw_c.append(row[1])
				y2_orw_c.append(row[2])
				y3_orw_c.append(row[3])
		else:
			if row[4] == 'CTP':
				y1_ctp.append(row[1])
				y2_ctp.append(row[2])
				y3_ctp.append(row[3])
				x1.append(float(row[0]))
			else:
				y1_orw.append(row[1])
				y2_orw.append(row[2])
				y3_orw.append(row[3])

######## This part is only real measure by lines #######
fig = pl.figure()
ax1 = fig.add_subplot(3,1,1)
ax1.set_xscale('log', basex=2)
ax1.plot(x1, y1_ctp, 'b', label='cca=400, ctp')
ax1.plot(x1, y1_orw, 'r', label='cca=400, orw')

if result['check']:
	ax1.plot(x2, y1_ctp_c, 'b--', label='cca=900, ctp', dashes=(4,4))
	ax1.plot(x2, y1_orw_c, 'r--', label='cca=900, orw', dashes=(4,4))
ax1.set_title('Sink neighbour')
#ax1.xaxis.set_ticklabels([])
ax1.grid()
leg = ax1.legend(loc='best', fontsize=10, fancybox=True)
leg.get_frame().set_alpha(0.5)

ax2 = fig.add_subplot(3,1,2, sharex=ax1, sharey=ax1)
ax2.plot(x1, y2_ctp, 'b', label='cca=400, ctp')
ax2.plot(x1, y2_orw, 'r', label='cca=400, orw')
if result['check']:
	ax2.plot(x2, y2_ctp_c, 'b--', label='cca=900, ctp', dashes=(4,4))
	ax2.plot(x2, y2_orw_c, 'r--', label='cca=900, orw', dashes=(4,4))
#ax2.xaxis.set_ticklabels([])
ax2.grid()
ax2.set_title('Relay')
leg = ax2.legend(loc='best', fontsize=10, fancybox=True)
leg.get_frame().set_alpha(0.5)

ax3 = fig.add_subplot(3,1,3, sharex=ax1, sharey=ax1)
ax3.plot(x1, y3_ctp, 'b', label='cca=400, ctp')
ax3.plot(x1, y3_orw, 'r', label='cca=400, orw')
if result['check']:
	ax3.plot(x2, y3_ctp_c, 'b--', label='cca=900, ctp', dashes=(4,4))
	ax3.plot(x2, y3_orw_c, 'r--', label='cca=900, orw', dashes=(4,4))
ax3.set_title('Leaf')
leg = ax3.legend(loc='best', fontsize=10, fancybox=True)
leg.get_frame().set_alpha(0.5)
ax3.grid()
ax1.set_xlim([0.125,32])
ax3.set_xlabel('Wakeup Interval (s)')

#ax3.set_ylabel('Duty Cycle (%)')
fig.text(0.06, 0.5, 'Duty Cycle (%)', ha='center', va='center', rotation='vertical')
pl.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)


fig = pl.figure()
if result['check']:
	y11 = y1_ctp_c
	y12 = y2_ctp_c
	y13 = y3_ctp_c
	y21 = y1_orw_c
	y22 = y2_orw_c
	y23 = y3_orw_c
	x = x2
else:
	y11 = y1_ctp
	y12 = y2_ctp
	y13 = y3_ctp
	y21 = y1_orw
	y22 = y2_orw
	y23 = y3_orw
	x = x1
ax1 = fig.add_subplot(1,1,1)
ax1.scatter(x,y11, color='b', marker='D', alpha=0.7, label='real_SN_ctp')
ax1.scatter(x,y12, color='r', marker='D', alpha=0.7, label='real_RL_ctp')
ax1.scatter(x,y13, color='g', marker='D', alpha=0.7, label='real_LF_ctp')
ax1.scatter(x,y21, color='b', alpha=0.7, label='real_SN_orw')
ax1.scatter(x,y22, color='r', alpha=0.7, label='real_RL_orw')
ax1.scatter(x,y23, color='g', alpha=0.7, label='real_LF_orw')

#########################plot real point ends###################

#########################plot model begins###################
#########################section CTP###################
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

if result['twist']:
	path = "CTP_Paras_twist.txt"
else:
	path = "CTP_Paras.txt"
with open(path) as fo:
	lines = fo.readlines()
	for row in lines:
		a = mysplit(row)
		if a[1] == 'SN':
			for i, item in enumerate(SN_Paras):
				item.append(float(a[i+3]))
		if a[1] == 'RL':
			for i, item in enumerate(RL_Paras):
				item.append(float(a[i+3]))
		if a[1] == 'LF':
			for i, item in enumerate(LF_Paras):
				item.append(float(a[i+3]))
				
y_SN=[]
y_RL=[]
y_LF=[]
for i, Tw in enumerate(x):
	temp = DC_Model_ctp_SN(*(zip(*SN_Paras)[i]), Tw=Tw*1000.0)
	y_SN.append(temp)
	temp = DC_Model_ctp(*(zip(*RL_Paras)[i]), Tw=Tw*1000.0)
	y_RL.append(temp)
	temp = DC_Model_ctp(*(zip(*LF_Paras)[i]), Tw=Tw*1000.0)
	y_LF.append(temp)
	

ax1.plot(x, y_SN, 'b', label='model_ctp_sinkN')
ax1.plot(x, y_RL, 'r', label='model_ctp_relay')
ax1.plot(x, y_LF, 'g', label='model_ctp_leaf')
#########################section ORW###################
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
SN_Paras = [F_SN, Tao_SN, Fs_SN, L_SN, Fail_SN]
RL_Paras = [F_RL, Tao_RL, Fs_RL, L_RL, Fail_RL]
LF_Paras = [F_LF, Tao_LF, Fs_LF, L_LF, Fail_LF]
#for wake in wakeup:

if result['twist']:
	path = "ORW_Paras_twist.txt"
else:
	path = "ORW_Paras.txt"

with open(path, "r") as fo:
	lines = fo.readlines()
	for row in lines:
		a = mysplit(row)
		if a[1] == 'SN':
			for i, item in enumerate(SN_Paras):
				item.append(float(a[i+3]))
		if a[1] == 'RL':
			for i, item in enumerate(RL_Paras):
				item.append(float(a[i+3]))
		if a[1] == 'LF':
			for i, item in enumerate(LF_Paras):
				item.append(float(a[i+3]))
				
y_SN=[]
y_RL=[]
y_LF=[]
for i, Tw in enumerate(x):
	temp = sum(DC_Model_orw_SN(*(zip(*SN_Paras)[i]), Tw=Tw*1000.0))
	y_SN.append(temp)
	temp = sum(DC_Model_orw(*(zip(*RL_Paras)[i]), Tw=Tw*1000.0))
	y_RL.append(temp)
	temp = sum(DC_Model_orw(*(zip(*LF_Paras)[i]), Tw=Tw*1000.0))
	y_LF.append(temp)
	
ax1.plot(x, y_SN, 'b--', label='model_orw_sinkN')
ax1.plot(x, y_RL, 'r--', label='model_orw_relay')
ax1.plot(x, y_LF, 'g--', label='model_orw_leaf')
ax1.set_xlabel('Wakeup Interval (s)')
ax1.set_ylabel('Duty Cycle (%)')
ax1.set_xscale('log', basex=2)
leg = ax1.legend(loc=2, fontsize=10, fancybox=True)
leg.get_frame().set_alpha(0.5)
pl.show()
