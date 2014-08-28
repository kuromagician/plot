#!/usr/bin/python
import tools.twistReader as Treader
import tools.command as command
import tools.calprop as calprop
import numpy as np
from numpy import mean
import matplotlib
import pylab as pl
from tools.functions import *
import sys
import array
from scipy import stats
from matplotlib.patches import Rectangle

FileDict = {}
font = {'size'   : 17}

matplotlib.rc('font', **font)

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

######## This part is only real measurements and error bar#######
#average values
avg_y1_ctp = mean(y1_ctp_c, axis=0)
avg_y2_ctp = mean(y2_ctp_c, axis=0)
avg_y3_ctp = mean(y3_ctp_c, axis=0)
avg_y1_orw = mean(y1_orw_c, axis=0)
avg_y2_orw = mean(y2_orw_c, axis=0)
avg_y3_orw = mean(y3_orw_c, axis=0)

#error bar
err_y1_ctp = np.std(y1_ctp_c, axis=0)
err_y2_ctp = np.std(y2_ctp_c, axis=0)
err_y3_ctp = np.std(y3_ctp_c, axis=0)
err_y1_orw = np.std(y1_orw_c, axis=0)
err_y2_orw = np.std(y2_orw_c, axis=0)
err_y3_orw = np.std(y3_orw_c, axis=0)


fig = pl.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.errorbar(x2, avg_y1_ctp, yerr=err_y1_ctp, fmt='bo')
ax1.errorbar(x2, avg_y2_ctp, yerr=err_y2_ctp, fmt='ro')
ax1.errorbar(x2, avg_y3_ctp, yerr=err_y3_ctp, fmt='go')

#ax1.errorbar(x2, avg_y1_orw, yerr=err_y1_orw, fmt='bo')
#ax1.errorbar(x2, avg_y2_orw, yerr=err_y2_orw, fmt='ro')
#ax1.errorbar(x2, avg_y3_orw, yerr=err_y3_orw, fmt='go')


#########################plot model begins###################
#########################section CTP###################
F_SN = [[] for i in range(0, numfiles)] 
Tao_SN = [[] for i in range(0, numfiles)] 
N_SN = [[] for i in range(0, numfiles)]
L_SN = [[] for i in range(0, numfiles)] 
Fail_SN = [[] for i in range(0, numfiles)]

F_RL = [[] for i in range(0, numfiles)] 
Tao_RL = [[] for i in range(0, numfiles)] 
N_RL = [[] for i in range(0, numfiles)]
L_RL = [[] for i in range(0, numfiles)] 
Fail_RL = [[] for i in range(0, numfiles)]

F_LF = [[] for i in range(0, numfiles)] 
Tao_LF = [[] for i in range(0, numfiles)] 
N_LF = [[] for i in range(0, numfiles)]
L_LF = [[] for i in range(0, numfiles)] 
Fail_LF = [[] for i in range(0, numfiles)]




SN_Paras = [F_SN, Tao_SN, N_SN, L_SN, Fail_SN]
RL_Paras = [F_RL, Tao_RL, N_RL, L_RL, Fail_RL]
LF_Paras = [F_LF, Tao_LF, N_LF, L_LF, Fail_LF]

path = ("CTP_Paras.txt", "CTP_Paras1.txt", "CTP_Paras2.txt")
for k, parafile in enumerate(path):
	with open(parafile) as fo:
		lines = fo.readlines()
		for row in lines:
			a = mysplit(row)
			if a[1] == 'SN':
				for i, item in enumerate(SN_Paras):
					item[k].append(float(a[i+3]))
			if a[1] == 'RL':
				for i, item in enumerate(RL_Paras):
					item[k].append(float(a[i+3]))
			if a[1] == 'LF':
				for i, item in enumerate(LF_Paras):
					item[k].append(float(a[i+3]))
				
Avg_SN_Paras = mean(SN_Paras, axis=1)
for i, items in enumerate(Avg_SN_Paras):
		print items[2]
Avg_RL_Paras = mean(RL_Paras, axis=1)
for i, items in enumerate(Avg_RL_Paras):
		print items[2]
Avg_LF_Paras = mean(LF_Paras, axis=1)
for i, items in enumerate(Avg_LF_Paras):
		print items[2]

y_SN=[]
y_RL=[]
y_LF=[]
y_SN_old=[]
y_RL_old=[]
y_LF_old=[]
y_stack=[]
x=x2
for i, Tw in enumerate(x2):
	#fixed model
	temp = DC_Model_ctp_SN(*(zip(*Avg_SN_Paras)[i]), Tw=Tw*1000.0)
	y_SN.append(temp)
	temp = DC_Model_ctp(*(zip(*Avg_RL_Paras)[i]), Tw=Tw*1000.0)
	y_RL.append(temp)
	temp = DC_Model_ctp(*(zip(*Avg_LF_Paras)[i]), Tw=Tw*1000.0)
	y_LF.append(temp)
	#old model
	temp = DC_Model_ctp_SN(*(zip(*Avg_SN_Paras)[i]), Tw=Tw*1000.0)
	y_SN_old.append(temp)
	temp = DC_Model_ctp_old(*(zip(*Avg_RL_Paras)[i]), Tw=Tw*1000.0)
	y_RL_old.append(temp)
	temp = DC_Model_ctp_old(*(zip(*Avg_LF_Paras)[i]), Tw=Tw*1000.0)
	y_LF_old.append(temp)
	#prepare for stack plot
	y_stack.append( DC_Model_ctp_sep(*(zip(*Avg_RL_Paras)[i]), Tw=Tw*1000.0))
	

ax1.plot(x, y_SN_old, 'b', label='old_model_ctp_sinkN')
ax1.plot(x, y_RL_old, 'r', label='old_model_ctp_relay')
ax1.plot(x, y_LF_old, 'g', label='old_model_ctp_leaf')
#ax1.plot(x, y_SN_old,  label='old_model_ctp_sinkN')
#ax1.plot(x, y_RL_old,  label='old_model_ctp_relay')
#ax1.plot(x, y_LF_old,  label='old_model_ctp_leaf')
#ax1.plot(x, y_SN, 'b', label='model_ctp_sinkN')
#ax1.plot(x, y_RL, 'r', label='model_ctp_relay')
#ax1.plot(x, y_LF, 'g', label='model_ctp_leaf')


for meas, old, new in zip(avg_y2_ctp, y_RL_old, y_RL):
	temp_o = (old-meas)/meas*100
	temp_n = (new-meas)/meas*100
	temp_i = abs(abs(temp_o) - abs(temp_n))/abs(temp_o)*100.0
	print "differece: O:{:.2f} N:{:.2f} I:{:.2f}".format(temp_o, temp_n, temp_i)

'''
#########################section ORW###################
F_SN = [[] for i in range(0, numfiles)] 
Tao_SN = [[] for i in range(0, numfiles)] 
Fs_SN = [[] for i in range(0, numfiles)]
L_SN = [[] for i in range(0, numfiles)] 
Fail_SN = [[] for i in range(0, numfiles)]

F_RL = [[] for i in range(0, numfiles)] 
Tao_RL = [[] for i in range(0, numfiles)] 
Fs_RL = [[] for i in range(0, numfiles)]
L_RL = [[] for i in range(0, numfiles)] 
Fail_RL = [[] for i in range(0, numfiles)]

F_LF = [[] for i in range(0, numfiles)] 
Tao_LF = [[] for i in range(0, numfiles)] 
Fs_LF = [[] for i in range(0, numfiles)]
L_LF = [[] for i in range(0, numfiles)] 
Fail_LF = [[] for i in range(0, numfiles)]
SN_Paras = [F_SN, Tao_SN, Fs_SN, L_SN, Fail_SN]
RL_Paras = [F_RL, Tao_RL, Fs_RL, L_RL, Fail_RL]
LF_Paras = [F_LF, Tao_LF, Fs_LF, L_LF, Fail_LF]
#for wake in wakeup:
x=x2
path = ("ORW_Paras.txt", "ORW_Paras1.txt", "ORW_Paras2.txt")

for k, parafile in enumerate(path):
	with open(parafile, "r") as fo:
		lines = fo.readlines()
		for row in lines:
			a = mysplit(row)
			if a[1] == 'SN':
				for i, item in enumerate(SN_Paras):
					item[k].append(float(a[i+3]))
			elif a[1] == 'RL':
				for i, item in enumerate(RL_Paras):
					item[k].append(float(a[i+3]))
			elif a[1] == 'LF':
				for i, item in enumerate(LF_Paras):
					item[k].append(float(a[i+3]))
				

Avg_SN_Paras = mean(SN_Paras, axis=1)
for i, items in enumerate(Avg_SN_Paras):
		print items[2]
Avg_RL_Paras = mean(RL_Paras, axis=1)
for i, items in enumerate(Avg_RL_Paras):
		print items[2]
Avg_LF_Paras = mean(LF_Paras, axis=1)
for i, items in enumerate(Avg_LF_Paras):
		print items[2]
				
y_SN=[]
y_RL=[]
y_LF=[]
y_SN_old=[]
y_RL_old=[]
y_LF_old=[]
for i, Tw in enumerate(x):
	temp = sum(DC_Model_orw_SN(*(zip(*Avg_SN_Paras)[i]), Tw=Tw*1000.0))
	y_SN.append(temp)
	temp = sum(DC_Model_orw(*(zip(*Avg_RL_Paras)[i]), Tw=Tw*1000.0))
	y_RL.append(temp)
	temp = sum(DC_Model_orw(*(zip(*Avg_LF_Paras)[i]), Tw=Tw*1000.0))
	y_LF.append(temp)
	
	temp = sum(DC_Model_orw_SN(*(zip(*Avg_SN_Paras)[i]), Tw=Tw*1000.0))
	y_SN_old.append(temp)
	temp = sum(DC_Model_orw_old(*(zip(*Avg_RL_Paras)[i]), Tw=Tw*1000.0))
	y_RL_old.append(temp)
	temp = sum(DC_Model_orw_old(*(zip(*Avg_LF_Paras)[i]), Tw=Tw*1000.0))
	y_LF_old.append(temp)

for meas, old, new in zip(avg_y2_orw, y_RL_old, y_RL):
	temp_o = (old-meas)/meas*100
	temp_n = (new-meas)/meas*100
	temp_i = abs(abs(temp_n)-abs(temp_o))/temp_o*100
	print "differece: O:{:.2f} N:{:.2f} I:{:.2f}".format(temp_o, temp_n, temp_i)

ax1.plot(x, y_SN_old, 'b--', label='ported_model_orw_sinkN')
ax1.plot(x, y_RL_old, 'r--', label='ported_model_orw_relay')
ax1.plot(x, y_LF_old, 'g--', label='ported_model_orw_leaf')
ax1.plot(x, y_SN, 'b', label='model_orw_sinkN')
ax1.plot(x, y_RL, 'r', label='model_orw_relay')
ax1.plot(x, y_LF, 'g', label='model_orw_leaf')
'''
#####plot configure#####
ax1.set_xlabel('Wakeup Interval (s)')
ax1.set_ylabel('Duty Cycle (%)')
ax1.set_xscale('log', basex=2)
ax1.set_xlim([0.125, 32])
leg = ax1.legend(loc=2, fancybox=True)
leg.get_frame().set_alpha(0.5)


#########stack plot only for CTP############
fig = pl.figure()
ax=fig.add_subplot(1,1,1)
xx=np.asarray(x)
yy=np.asarray(y_stack).transpose()
colors=['b','g','r','c','m']
labels=[r'$\Delta_{rc}$', r'$\Delta_{bs}$', r'$\Delta_{br}$', r'$\Delta_{us}$', r'$\Delta_{ur}$']
#pl.rc('text', usetex=True)
ax.stackplot(x, yy, colors=colors)

#proxy to draw legends
p=[]
for c in colors:
	p.append(Rectangle((0, 0), 1, 1, fc=c))
ax.legend(p, labels, loc=2)
ax.set_xlabel('Wakeup Interval (s)')
ax.set_ylabel('Duty Cycle (%)')
ax.set_xscale('log', basex=2)


pl.show()
