#!/usr/bin/python
import tools.twistReader as Treader
import tools.command as command
import tools.calprop as calprop
from numpy import mean
import matplotlib
import pylab as pl
from tools.functions import *
import sys
import array
from scipy import stats

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




path = ("DC_measure_indriya.txt", "DC_measure_indriya1.txt", "DC_measure_indriya2.txt")
numfiles = len(path)

y1_ctp_c = [[] for i in range(0, numfiles)]
y2_ctp_c = [[] for i in range(0, numfiles)]
y3_ctp_c = [[] for i in range(0, numfiles)]
y1_orw_c = [[] for i in range(0, numfiles)]
y2_orw_c = [[] for i in range(0, numfiles)]
y3_orw_c = [[] for i in range(0, numfiles)]


for i, logfile in enumerate(path):
	with open(logfile) as fo:
		lines = fo.readlines()
		for row in lines:
			row = mysplit(row)
			if row[4] == 'CTP':
				y1_ctp_c[i].append(float(row[1]))
				y2_ctp_c[i].append(float(row[2]))
				y3_ctp_c[i].append(float(row[3]))
				if i == 0:
					x2.append(float(row[0]))
			else:
				y1_orw_c[i].append(float(row[1]))
				y2_orw_c[i].append(float(row[2]))
				y3_orw_c[i].append(float(row[3]))

######## This part is only real measure by lines #######
#average values
avg_y1_ctp = mean(y1_ctp_c, axis=0)
avg_y2_ctp = mean(y2_ctp_c, axis=0)
avg_y3_ctp = mean(y3_ctp_c, axis=0)
avg_y1_orw = mean(y1_orw_c, axis=0)
avg_y2_orw = mean(y2_orw_c, axis=0)
avg_y3_orw = mean(y3_orw_c, axis=0)

#error bar
err_y1_ctp = stats.sem(y1_ctp_c, axis=0)
err_y2_ctp = stats.sem(y2_ctp_c, axis=0)
err_y3_ctp = stats.sem(y3_ctp_c, axis=0)
err_y1_orw = stats.sem(y1_orw_c, axis=0)
err_y2_orw = stats.sem(y2_orw_c, axis=0)
err_y3_orw = stats.sem(y3_orw_c, axis=0)


fig = pl.figure()
ax1 = fig.add_subplot(1,1,1)
#ax1.errorbar(x2, avg_y1_ctp, yerr=err_y1_ctp, fmt='')
#ax1.errorbar(x2, avg_y2_ctp, yerr=err_y2_ctp, fmt='')
#ax1.errorbar(x2, avg_y3_ctp, yerr=err_y3_ctp, fmt='')

ax1.errorbar(x2, avg_y1_orw, yerr=err_y1_orw, fmt='o')
ax1.errorbar(x2, avg_y2_orw, yerr=err_y2_orw, fmt='o')
ax1.errorbar(x2, avg_y3_orw, yerr=err_y3_orw, fmt='o')




'''
############ Figure 2 ############
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
#ax1.scatter(x,y11, color='b', marker='D', alpha=0.7, label='real_SN_ctp')
#ax1.scatter(x,y12, color='r', marker='D', alpha=0.7, label='real_RL_ctp')
#ax1.scatter(x,y13, color='g', marker='D', alpha=0.7, label='real_LF_ctp')
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
	

#ax1.plot(x, y_SN, 'b', label='model_ctp_sinkN')
#ax1.plot(x, y_RL, 'r', label='model_ctp_relay')
#ax1.plot(x, y_LF, 'g', label='model_ctp_leaf')
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
	
ax1.plot(x, y_SN, 'b', label='model_orw_sinkN')
ax1.plot(x, y_RL, 'r', label='model_orw_relay')
ax1.plot(x, y_LF, 'g', label='model_orw_leaf')
ax1.set_xlabel('Wakeup Interval (s)')
ax1.set_ylabel('Duty Cycle (%)')
ax1.set_xscale('log', basex=2)
leg = ax1.legend(loc=2, fontsize=10, fancybox=True)
leg.get_frame().set_alpha(0.5)'''
pl.show()
