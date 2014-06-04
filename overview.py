#!/usr/bin/python
import matplotlib
import numpy as np
import pylab as pl
import sys
from scipy.interpolate import interp1d
from scipy.misc import derivative

#custom import
import tools.command as command
import tools.twistReader as Treader
import tools.calprop as calprop
from tools.functions import *
from tools.constant import *

'''
props['Avg_Data_dc'] = Avg_Data_dc_ctp
	props['Avg_Idle_dc'] = Avg_Idle_dc_ctp
	props['Avg_Total_dc'] = Avg_Total_dc_ctp
	props['Avg_Hops'] = avg_hops_ctp
	props['Num_Init'] = num_init_ctp
	props['Num_Fwd'] = num_fwd_ctp
	props['Dir_Neig'] = dir_neig_ctp
	props['Relay'] = relay_ctp
	props['Leaf'] = leaf_ctp
	props['Num_Rcv'] = total_receive_ctp
	props['Fwd_Load'] = load_ctp
'''
result = command.main(sys.argv[1:])
FileDict, props = command.getfile(result)
time_ratio = props['timeratio']
SINK_ID = props['SINK_ID']


##################################section of CTP#########################
CtpDebugMsgs = FileDict['CtpDebug']
#Calibrate timestamp
'''for msg in CtpDebugMsgs:
	if msg.type == NET_DC_REPORT:
		dt = msg.dbg__b - msg.timestamp/time_ratio
		break'''
		
		
#store the packet as (src, seqNo)
hist_ctp = set()
send_hist_ctp = set()
#two lists that record number and correspoding
#timestamp of that receive
rcv_num_ctp = []
rcv_time_ctp = []
#two lists that record number and correspoding
#timestamp of that send (init and fwd)
send_num_ctp = []
send_time_ctp = []
#four lists that record number and correspoding
#timestamp of that die event
die_num_SN_ctp = [0]
die_num_RL_ctp = [0]
die_num_LF_ctp = [0]
die_time_ctp = [0]
#support counter 
counter_r = 0
counter_s = 0
counter_d_SN = 0
counter_d_RL = 0
counter_d_LF = 0

cal_prop_ctp = calprop.prop_ctp(FileDict, result)
leaf_set = cal_prop_ctp['Leaf']
relay_set = cal_prop_ctp['Relay']
dirn_set = cal_prop_ctp['Dir_Neig']
a = len(dirn_set)
b = len(relay_set)
c = len(leaf_set)
print "CTP:", a, b, c

for msg in CtpDebugMsgs:
	if msg.type == NET_C_FE_RCV_MSG:
		if msg.node == SINK_ID:
			temp = msg.timestamp/time_ratio
			if (msg.dbg__b, msg.dbg__a) not in hist_ctp:
				hist_ctp.add((msg.dbg__b, msg.dbg__a))
				counter_r += 1
				rcv_time_ctp.append(temp/60.0)
				rcv_num_ctp.append(counter_r)
	if msg.type == NET_C_FE_SENT_MSG:
		temp = msg.timestamp/time_ratio
		if (msg.dbg__b, msg.dbg__a) not in hist_ctp:
			send_hist_ctp.add((msg.dbg__b, msg.dbg__a))
			counter_s += 1
			send_num_ctp.append(counter_s)
			send_time_ctp.append(temp/60.0)
	if msg.type == NET_C_DIE:
		if msg.node in relay_set:
			counter_d_RL += 1
		elif msg.node in leaf_set:
			counter_d_LF += 1
		elif msg.node in dirn_set:
			counter_d_SN += 1
		die_num_SN_ctp.append(counter_d_SN*100.0/a)
		die_num_RL_ctp.append(counter_d_RL*100.0/b)
		die_num_LF_ctp.append(counter_d_LF*100.0/c)
		die_time_ctp.append(temp/60.0)



		
##############################section of CTP#########################
OrwDebugMsgs = FileDict['OrwDebug']
#store the packet as (src, seqNo)
hist_orw = set()
send_hist_orw = set()
#two lists that record number and correspoding
#timestamp of that receive
rcv_num_orw = []
rcv_time_orw = []
#two lists that record number and correspoding
#timestamp of that send (init and fwd)
send_num_orw = []
send_time_orw = []
#four lists that record number and correspoding
#timestamp of that die event
die_num_SN_orw = [0]
die_num_RL_orw = [0]
die_num_LF_orw = [0]
die_time_orw = [0]
#support counter 
counter_r = 0
counter_s = 0
counter_d_SN = 0
counter_d_RL = 0
counter_d_LF = 0

cal_prop_orw = calprop.prop_orw(FileDict, result)
leaf_set = cal_prop_orw['Leaf']
relay_set = cal_prop_orw['Relay']
dirn_set = cal_prop_orw['Dir_Neig']
a = len(dirn_set)
b = len(relay_set)
c = len(leaf_set)
print "ORW:", a, b, c

for msg in OrwDebugMsgs:
	temp = msg.timestamp/time_ratio
	if msg.type == NET_C_FE_RCV_MSG:
		if msg.node == SINK_ID:
			if (msg.dbg__b, msg.dbg__a) not in hist_orw:
				hist_orw.add((msg.dbg__b, msg.dbg__a))
				counter_r += 1
				rcv_time_orw.append(temp/60.0)
				rcv_num_orw.append(counter_r)
	if msg.type == NET_APP_SENT:
		if (msg.dbg__b, msg.dbg__a) not in hist_orw:
			send_hist_orw.add((msg.dbg__b, msg.dbg__a))
			counter_s += 1
			send_num_orw.append(counter_s)
			send_time_orw.append(temp/60.0)
	if msg.type == NET_C_DIE:
		if msg.node in relay_set:
			counter_d_RL += 1
		elif msg.node in leaf_set:
			counter_d_LF += 1
		elif msg.node in dirn_set:
			counter_d_SN += 1
		die_num_SN_orw.append(counter_d_SN*100.0/a)
		die_num_RL_orw.append(counter_d_RL*100.0/b)
		die_num_LF_orw.append(counter_d_LF*100.0/c)
		die_time_orw.append(temp/60.0)



###########################PLOT SECTION##############################
fig = pl.figure()
lb = max(rcv_time_ctp[0], rcv_time_orw[0])
ub = min(rcv_time_ctp[-1], rcv_time_orw[-1])
x = np.arange(lb, ub, 0.1)

ax1 = fig.add_subplot(3,1,1)
ax1.plot(rcv_time_ctp, rcv_num_ctp, lw=2, color='b')
ax1.plot(send_time_ctp, send_num_ctp, 'b--', lw=2)
ax1.plot(rcv_time_orw, rcv_num_orw, lw=2, color='g')
ax1.plot(send_time_orw, send_num_orw, 'g--', lw=2)
#create interpolate curves so that we can use same x axis
f_ctp = interp1d(rcv_time_ctp, rcv_num_ctp)
f_orw = interp1d(rcv_time_orw, rcv_num_orw)

#calculate derivative using interpolated result get from above
xp = np.arange(lb+2, ub-2, 0.1)
drcv_ctp = derivative(f_ctp,xp,dx=1,n=1)
drcv_orw = derivative(f_orw,xp,dx=1,n=1)
ax2 = fig.add_subplot(3,1,2)
ax2.plot(xp, drcv_ctp)
ax2.plot(xp, drcv_orw)

if result['lim']:
	ax3 = fig.add_subplot(3,1,3)
	ax3.plot(die_time_orw, die_num_SN_orw, 'b--', label='SN_orw')
	ax3.plot(die_time_orw, die_num_RL_orw, 'r--', label='RL_orw')
	ax3.plot(die_time_orw, die_num_LF_orw, 'g--', label='LF_orw')
	ax3.plot(die_time_ctp, die_num_SN_ctp, color='b', label='SN_ctp')
	ax3.plot(die_time_ctp, die_num_RL_ctp, color='r', label='RL_ctp')
	ax3.plot(die_time_ctp, die_num_LF_ctp, color='g', label='LF_ctp')

pl.show()



