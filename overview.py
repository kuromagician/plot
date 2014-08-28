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
from collections import deque, defaultdict
import sys

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
time_TH = props['time_TH']


################################section of CTP#########################
CtpDebugMsgs = FileDict['CtpDebug']
#Calibrate timestamp not needed?
'''for msg in CtpDebugMsgs:
	if msg.type == NET_DC_REPORT:
		dt = msg.dbg__b - msg.timestamp/time_ratio
		break'''

#store the packet as (src, seqNo)
#hist_ctp = deque(maxlen=12000)
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
die_ctp = set()
#support counter 
counter_r = 0
counter_s = 0
counter_d_SN = 0
counter_d_RL = 0
counter_d_LF = 0
#duplicates
counter_d = 0

cal_prop_ctp = calprop.prop_ctp(FileDict, result)
cal_prop_orw = calprop.prop_orw(FileDict, result)
leaf_set = cal_prop_ctp['Leaf']
relay_set = cal_prop_ctp['Relay']
dirn_set = cal_prop_ctp['Dir_Neig']
a = len(dirn_set)
b = len(relay_set)
c = len(leaf_set)
print "CTP:", a, b, c

firstsee_ctp={}

for msg in CtpDebugMsgs:
	if msg.node not in firstsee_ctp:
		firstsee_ctp[msg.node] = msg.timestamp
	if msg.timestamp >= time_TH:
		#if msg.node == 77:
		#	print msg.node, msg.type
		temp = msg.timestamp/time_ratio
		if msg.type == NET_C_FE_RCV_MSG:
			if msg.node == SINK_ID:
				#remove dumplicate
				if (msg.dbg__b, msg.dbg__a) not in hist_ctp and msg.dbg__b <=140:
					hist_ctp.add((msg.dbg__b, msg.dbg__a))
					counter_r += 1
					rcv_time_ctp.append(temp/60.0)
					rcv_num_ctp.append(counter_r)
				else:
					counter_d += 1
		elif msg.type == NET_C_FE_SENT_MSG:
			send_hist_ctp.add((msg.dbg__b, msg.dbg__a))
			counter_s += 1
			send_num_ctp.append(counter_s)
			send_time_ctp.append(temp/60.0)
		elif msg.type == NET_C_DIE:
			if msg.node not in die_ctp:
				die_ctp.add(msg.node)
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
'''
for k, v in firstsee_ctp.iteritems():
	print "Node {}'s first log is {}".format(k,v)
'''
print "CTP Total Receive:{:6d}, Total Send:{:6d}, Duplicates:{:6d}, Deliver Rate:{:.2f}%".format(
	                            counter_r, counter_s, counter_d, counter_r*100.0/counter_s)

		
##############################section of ORW#########################
OrwDebugMsgs = FileDict['OrwDebug']
#store the packet as (src, seqNo)
hist_orw = deque(maxlen=12000)
send_hist_orw = deque(maxlen=12000)
#hist_orw = set()
#send_hist_orw = set()
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
counter_d = 0
counter_cd = 0
die_orw = set()


leaf_set = cal_prop_orw['Leaf']
relay_set = cal_prop_orw['Relay']
dirn_set = cal_prop_orw['Dir_Neig']
a = len(dirn_set)
b = len(relay_set)
c = len(leaf_set)
print "ORW:", a, b, c

step_SN = 100.0/a
if b == 0:
	step_RL = 0
else:
	step_RL = 100.0/b
if c == 0:
	step_LF = 0
else:
	step_LF = 100.0/c

for msg in OrwDebugMsgs:
	if msg.timestamp >= time_TH:
		temp = msg.timestamp/time_ratio
		if msg.type == NET_C_FE_RCV_MSG:
			if msg.node == SINK_ID:
				if (msg.dbg__b, msg.dbg__a) not in hist_orw and msg.dbg__b <=140:
					hist_orw.append((msg.dbg__b, msg.dbg__a))
					counter_r += 1
					rcv_time_orw.append(temp/60.0)
					rcv_num_orw.append(counter_r)
				else:
					counter_d += 1
		elif msg.type == NET_APP_SENT:
			if (msg.dbg__b, msg.dbg__a) not in send_hist_orw:
				send_hist_orw.append((msg.dbg__b, msg.dbg__a))
				counter_s += 1
				send_num_orw.append(counter_s)
				send_time_orw.append(temp/60.0)
		elif msg.type == NET_C_DIE:
			if msg.node not in die_orw:
				die_orw.add(msg.node)
				if msg.node in relay_set:
					counter_d_RL += step_RL
				elif msg.node in leaf_set:
					counter_d_LF += step_LF
				elif msg.node in dirn_set:
					counter_d_SN += step_SN
				die_num_SN_orw.append(counter_d_SN)
				die_num_RL_orw.append(counter_d_RL)
				die_num_LF_orw.append(counter_d_LF)
				die_time_orw.append(temp/60.0)
		elif msg.type == NET_C_FE_DUPLICATE_CACHE:
			counter_cd += 1
		#elif msg.type == NET_LL_DUPLICATE:
		#	counter_cd += 1
print "ORW Total Receive:{:6d}, Total Send:{:6d}, Duplicates:{:6d}, Deliver Rate:{:.2f}%".format(
	                            counter_r, counter_s, counter_d, counter_r*100.0/counter_s)


'''for (k,v) in send_hist_orw:
	if (k,v) not in hist_orw:
		print k, v'''
		
print "ORW DIE TIME:\n", die_time_orw

#sys.exit()
###########################PLOT SECTION##############################
###########################  FIGURE 1  ##############################
#      ax1: send/receive over time for ORW, CTP
#      ax2: throughput over time for ORW, CTP                    
#      ax3: die % over time for ORW, CTP, classified into LF, SN, RL
#####################################################################
fig = pl.figure()
lb = max(rcv_time_ctp[0], rcv_time_orw[0])
ub = min(rcv_time_ctp[-1], rcv_time_orw[-1])
x = np.arange(lb, ub, 0.1)

ax1 = fig.add_subplot(3,1,1)
ax1.plot(rcv_time_ctp, rcv_num_ctp, lw=2, color='b', label='CTP_Receive')
ax1.plot(send_time_ctp, send_num_ctp, 'b--', lw=2, label='CTP_Send')
ax1.plot(rcv_time_orw, rcv_num_orw, lw=2, color='g', label='ORW_Receive')
ax1.plot(send_time_orw, send_num_orw, 'g--', lw=2, label='ORW_Send')
ax1.legend(prop={'size':6})
#create interpolate curves so that we can use same x axis
f_ctp = interp1d(rcv_time_ctp, rcv_num_ctp)
f_orw = interp1d(rcv_time_orw, rcv_num_orw)

#calculate derivative using interpolated result get from above
xp = np.arange(lb+1.1, ub-1.1, 1)
drcv_ctp = derivative(f_ctp,xp,dx=1,n=1)
drcv_orw = derivative(f_orw,xp,dx=1,n=1)
ax2 = fig.add_subplot(3,1,2)
ax2.plot(xp, drcv_ctp, label='CTP_Throughput')
ax2.plot(xp, drcv_orw, label='ORW_Throughput')
ax2.legend()

if result['lim']:
	ax3 = fig.add_subplot(3,1,3)
	ax3.plot(die_time_orw, die_num_SN_orw, 'b--', label='SN_orw')
	ax3.plot(die_time_orw, die_num_RL_orw, 'r--', label='RL_orw')
	ax3.plot(die_time_orw, die_num_LF_orw, 'g--', label='LF_orw')
	ax3.plot(die_time_ctp, die_num_SN_ctp, color='b', label='SN_ctp')
	ax3.plot(die_time_ctp, die_num_RL_ctp, color='r', label='RL_ctp')
	ax3.plot(die_time_ctp, die_num_LF_ctp, color='g', label='LF_ctp')
	
###########################  FIGURE 2  ##############################
#      ax1: load over hops for ORW, CTP
#      ax2: die % over time for ORW, CTP, classified into LF, SN, RL
#      ax3: dutycycle over load                    
#      
#####################################################################
fig = pl.figure()

###########################     ax1    ##############################   
#to prevent unexpect error, we get the common part
hops_ctp, load_ctp = common_dict (cal_prop_ctp['Avg_Hops'], cal_prop_ctp['Fwd_Load'])
hops_orw, load_orw = common_dict (cal_prop_orw['Avg_Hops'], cal_prop_orw['Fwd_Load'])

ax1 = fig.add_subplot(1,1,1)
ax1.scatter(hops_ctp.values(), load_ctp.values(), label='CTP')
ax1.scatter(hops_orw.values(), load_orw.values(), marker='x', color='g', label='ORW')
ax1.legend()
ax1.set_xlabel("Average Hops to Sink")
ax1.set_ylabel("Average Load")
fig.savefig("figures/hops_load.pdf")

###########################     ax2    ##############################
fig = pl.figure()
hops_ctp, dc_ctp = common_dict (cal_prop_ctp['Avg_Hops'], cal_prop_ctp['Avg_Total_dc'])
hops_orw, dc_orw = common_dict (cal_prop_orw['Avg_Hops'], cal_prop_orw['Avg_Total_dc'])

ax2 = fig.add_subplot(1,1,1)
ax2.scatter(hops_ctp.values(), dc_ctp.values(), label='CTP')
ax2.scatter(hops_orw.values(), dc_orw.values(), marker='x', color='g', label='ORW')
ax2.legend()
ax2.set_xlabel("Average Hops to Sink")
ax2.set_ylabel("Average Duty Cycle(%)")
fig.savefig("figures/hops_dc.pdf")

###########################     ax3    ##############################
fig = pl.figure()
load_ctp, dc_ctp = common_dict (cal_prop_ctp['Fwd_Load'], cal_prop_ctp['Avg_Total_dc'])
load_orw, dc_orw = common_dict (cal_prop_orw['Fwd_Load'], cal_prop_orw['Avg_Total_dc'])

ax3 = fig.add_subplot(1,1,1)
ax3.scatter(load_ctp.values(), dc_ctp.values(), label='CTP')
ax3.scatter(load_orw.values(), dc_orw.values(), marker='x', color='g', label='ORW')
ax3.legend()
ax3.set_xlabel("Average Load")
ax3.set_ylabel("Average Duty Cycle(%)")

#final axis adjustment
limits = ax1.axis()
ax1.set_ylim([0, limits[3]])
ax1.set_xlim([-0.5, limits[1]])
limits = ax3.axis()
ax3.set_xlim([-1, limits[1]])
fig.tight_layout()
fig.savefig("figures/load_dc.pdf")


###########################  FIGURE 3  ##############################
#      Shows # received packets distribution of each node 
#      
#                         
#      
#####################################################################
counter_ctp = defaultdict(int)
temp_ctp = set()
for packet in hist_ctp:
	counter_ctp[packet[0]] += 1
	if packet[0] == 19:
		temp_ctp.add(packet[1])
print sorted(temp_ctp)
	
counter_orw = defaultdict(int)
for packet in hist_orw:
	counter_orw[packet[0]] += 1	
	if packet[0] == 36:
		print packet[1]
		
	
fig = pl.figure()
ax1=fig.add_subplot(2,1,1)
ax1.bar(counter_ctp.keys(), counter_ctp.values())

ax2=fig.add_subplot(2,1,2)
ax2.bar(counter_orw.keys(), counter_orw.values())



total_send_ctp = cal_prop_ctp['Total_Send']
total_receive_ctp = cal_prop_ctp['Num_Rcv']
total_send_orw = cal_prop_orw['Total_Send']
total_receive_orw = cal_prop_orw['Num_Rcv']
ratio = 100.0*total_send_orw/total_send_ctp
ratio1 = 100.0*total_receive_orw/total_send_orw
ratio2 = 100.0*total_receive_ctp/total_send_ctp
print "Total send: ORW {:5d}, CTP {:5d}, ratio:{:5.2f}\
     \nTotal Rcv:  ORW {:5d}, ratio:{:5.2f}, CTP {:5d}, ratio:{:5.2f}".format(total_send_orw, total_send_ctp, ratio, total_receive_orw, ratio1, total_receive_ctp, ratio2)

pl.show()



