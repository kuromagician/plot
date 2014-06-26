#!/usr/bin/python
import tools.reader as reader
import tools.twistReader as Treader
import array
import matplotlib 
import pylab as pl
import math
import operator
import os
import itertools
import numpy as np
from collections import defaultdict
from numpy import mean
from mpl_toolkits.mplot3d import Axes3D
import tools.command as command
import tools.calprop as calprop
from tools.constant import *
from tools.functions import *
from scipy.interpolate import interp1d
from scipy.misc import derivative

import sys, getopt

# the threshold of the duty cycle that is regarded as "high"
TH_dc = 6
TH_load = 10

############################ Common Fuctions ######################

#plot the arrows from children pointing to died nodes
def anno_arrow (ax, x, y, dielist, childrenlist, range, die_set):
	for node in dielist[range[0]:range[1]]:
	#print len(children_ctp[node])
		for child in childrenlist[node]:
			if child in die_set and child not in dielist[:range[0]]:
				ax.annotate("",
						xy=(x[node], y[node]), xycoords='data',
						xytext=(x[child], y[child]), textcoords='data',
						arrowprops=dict(alpha=0.2, width=0.0005, headwidth=1))
						
def setbp(bp, alpha=1, linewidth=1, ms=5, color='b'):
	pl.setp(bp['boxes'], alpha=alpha, linewidth=linewidth, color=color)
	pl.setp(bp['medians'], alpha=alpha, linewidth=linewidth)
	pl.setp(bp['whiskers'], alpha=alpha, linewidth=linewidth, color=color)
	pl.setp(bp['caps'], linewidth=linewidth + 0.1)
	pl.setp(bp['fliers'], linewidth=0.4, ms=ms, color=color)
	
def group_barplot(ax, group, values, positions, text, unit=""):
	#text should be a list whose first element should be a list
	#so that we assume the rest should be the same among the two
	temp=[]
	for item in group[0]:
		if item in values[0]:
			temp.append(values[0][item])
	Avg = mean(temp)
	#print "{0[0][0]}'s {0[1]} average {0[2]}: {1:.2f}{2:s}".format(text, Avg, unit)
	ax.boxplot(temp, positions=positions[0:1], widths=0.4)
	ax.plot(positions[0:1], Avg, marker='*')
	
	temp=[]
	for item in group[1]:
		if item in values[1]:
			temp.append(values[1][item])
	Avg = mean(temp)
	#print "{0[0][1]}'s {0[1]} average {0[2]}: {1:.2f}{2:s}".format(text, Avg, unit)
	bp = ax.boxplot(temp, positions=positions[1:2], widths=0.4)
	setbp(bp, color='r')
	ax.plot(positions[1:2], Avg, marker='*') 

#################################################################


#############################General Statics########################
#		1.ctp's thl(average hops) and 
#		2.total number of nodes whose packets have been received by SINK
#		3.Calibrate the clock
#
####################################################################
'''
if not TWIST:
	CtpdebugMsgs = reader.loadDebug(base_path + limited_ctp, fileNames2)
	CtpdataMsgs = reader.loadDataMsg(base_path + limited_ctp, fileNames3)
	time_ratio = 1000.0
else:
	CtpdebugMsgs, _, _, CtpdataMsgs = Treader.load(base_path + limited_ctp)
	time_ratio = 1000000.0
'''	
resultc = command.main(sys.argv[1:])
FileDict, props = command.getfile(resultc)
time_ratio = props['timeratio']
SINK_ID = props['SINK_ID']
prefix = props['prefix']
ELIMIT = resultc['lim']
TWIST = resultc['twist']

CtpdataMsgs = FileDict['CtpData']
CtpdebugMsgs = FileDict['CtpDebug']
props_ctp = calprop.prop_ctp(FileDict, resultc)
props_orw = calprop.prop_orw(FileDict, resultc)
#Average hops
avg_hops_ctp = props_ctp['Avg_Hops']
dir_neig_ctp = props_ctp['Dir_Neig']
relay_ctp = props_ctp['Relay']
leaf_ctp = props_ctp['Leaf']
print "CTP  D R L:", len(dir_neig_ctp), len(relay_ctp), len(leaf_ctp)

dir_neig_orw = props_orw['Dir_Neig']
relay_orw = props_orw['Relay']
leaf_orw = props_orw['Leaf']
print "ORW  D R L:", len(dir_neig_orw), len(relay_orw), len(leaf_orw)

num_node = len(avg_hops_ctp)

print "Total connected nodes:", num_node
#print "They're:\n", sorted(avg_hops_ctp.keys())

'''#normally there should be 86 nodes in the test
if num_node < 86 - 10:
	print "WARNING! THERE ARE ", 86-num_node, "NODES DISCONNECTED FROM SINK!!!!!!!"
'''


####################################     CTP     #################################

PRR_ctp = []
counter = 0
num_init_ctp_bytime = []
timeline_ctp = []
time_beacon = []
node_beacon = []

DutyCycle_ctp = defaultdict(list)
Avg_DC_ctp = defaultdict(int)
children_ctp = defaultdict(set)
num_fwd_ctp = defaultdict(int)
num_init_ctp = defaultdict(int)
total_send_ctp = 0
total_receive_ctp = 0
send_noACK_ctp = defaultdict(int)
send_Qfull_ctp = defaultdict(int)
fwd_noACK_ctp = defaultdict(int)
sendset = set()

throughput = []
Ttimeline = []
Tcounter=0
Tnew=0
Told=0
Tinterval=0
packet_hist = set()
total_rcv_ctp = []
total_rcv_ctp_timeline = []

for msg in CtpdebugMsgs:
	if msg.type == NET_C_FE_SENT_MSG:
		total_send_ctp += 1
		num_init_ctp[msg.node] += 1
		'''if total_send_ctp == num_node:
			PRR_ctp.append(total_receive_ctp * 1.0 / total_send_ctp)
			timeline_ctp.append((msg.timestamp/time_ratio + dt) / 60)
			total_send_ctp = 0
			total_receive_ctp = 0'''
	#record beacon
	elif msg.type == 0x33:
		time_beacon.append((msg.timestamp/time_ratio)/60.0)
		node_beacon.append(msg.node)
	elif msg.type == NET_DC_REPORT and msg.node != SINK_ID:
		if msg.dbg__a + msg.dbg__c < 10000:
			DutyCycle_ctp[msg.node].append((msg.dbg__a, msg.dbg__b, msg.dbg__c))
	elif msg.type == NET_C_FE_FWD_MSG:
		children_ctp[msg.dbg__c].add(msg.node)
		num_fwd_ctp[msg.node] += 1
	elif msg.type == NET_C_FE_RCV_MSG:
		if msg.node == SINK_ID:
			#record origin, seq
			if (msg.dbg__b, msg.dbg__a) not in packet_hist:
				packet_hist.add((msg.dbg__b, msg.dbg__a)) 
				temp = msg.timestamp/time_ratio
				total_receive_ctp += 1
				Tcounter += 1
				counter += 1
				total_rcv_ctp.append(counter)
				total_rcv_ctp_timeline.append(temp/60.0)
				if Told == 0:
					Told = msg.timestamp
				else:
					Tnew = msg.timestamp - Told
					if Tnew > 60*time_ratio:
						throughput.append(Tcounter*time_ratio/Tnew*60)
						PRR_ctp.append(total_receive_ctp * 1.0 / total_send_ctp)
						Ttimeline.append(temp / 60.0)
						Told=0
						Tcounter=0
						total_receive_ctp = 0
						total_send_ctp = 0
				
	elif msg.type == NET_C_FE_SEND_QUEUE_FULL:
		send_Qfull_ctp[msg.node] += 1
	elif msg.type == NET_C_FE_SENDDONE_FAIL_ACK_SEND:
		send_noACK_ctp[msg.node] += 1
	elif msg.type == NET_C_FE_SENDDONE_FAIL_ACK_FWD:
		fwd_noACK_ctp[msg.node] += 1


#packet lost statics
Qfull = sum(send_Qfull_ctp.values())
SnoACK = sum(send_noACK_ctp.values())
FnoACK = sum(fwd_noACK_ctp.values())
print "Qfail:{}\n{}\nSnoACK:{}\n{}\nFnoACK{}\n{}".format(Qfull, send_Qfull_ctp, SnoACK, send_noACK_ctp, FnoACK, fwd_noACK_ctp)


load_ctp = {k: num_fwd_ctp[k] * 1.0 / num_init_ctp[k] + 1 for k in num_init_ctp}
#get the average dutycycle of each node
Avg_DC_ctp = {k: mean(DutyCycle_ctp[k], axis=0) for k in DutyCycle_ctp}

Avg_Data_dc_ctp = {}
Avg_Idle_dc_ctp = {}
Avg_Total_dc_ctp = {}

for node in Avg_DC_ctp:
	Avg_Data_dc_ctp[node] = Avg_DC_ctp[node][0]*0.01
	Avg_Idle_dc_ctp[node] = Avg_DC_ctp[node][2]*0.01
	Avg_Total_dc_ctp[node] = Avg_Data_dc_ctp[node] + Avg_Idle_dc_ctp[node]
		

'''for msg in CtpdebugMsgs:
	if msg.type == 0x26:
		print "Packet dropped @Node", msg.node, "which comes from Node", msg.dbg__b'''

####################################     ORW     #################################

OrwdebugMsgs = FileDict['OrwDebug']

	
children_orw = defaultdict(set)
num_fwd_orw = defaultdict(int)
num_init_orw = defaultdict(int)
route_hist_orw = defaultdict(set)
DutyCycle_orw = defaultdict(list)
# This is the time when packet is generated
timeline_orw = []
# this is every transmission
timeline_transmit_orw = defaultdict(list)
node_transmit_orw = defaultdict(list)
total_rcv_orw_timeline = []
total_rcv_orw = []
PRR_orw = []
total_send_orw = 0
total_receive_orw = 0
connected = set()
packet_hist = set()
Tnew=0
Told=0
Tcounter = 0
counter = 0

for msg in OrwdebugMsgs:
	if msg.type == NET_C_FE_RCV_MSG:
		#if origin != last_hop, then last hop is forwarder
		if msg.dbg__b != msg.dbg__c:
			num_fwd_orw[msg.dbg__c] += 1
		#last hop is current node's child
		children_orw[msg.node].add(msg.dbg__c)
		# (origin, SeqNo) += lasthop
		route_hist_orw[(msg.dbg__b, msg.dbg__a)].add(msg.dbg__c)
		#if node is SINK, add node to direct neighbour
		if msg.node == SINK_ID:
			#dir_neig_orw.add(msg.dbg__c)
			connected.add(msg.dbg__b)
			if (msg.dbg__b, msg.dbg__a) not in packet_hist:
				total_receive_orw += 1
				Tcounter += 1
				counter += 1
				packet_hist.add((msg.dbg__b, msg.dbg__a))
				temp = msg.timestamp/time_ratio
				total_rcv_orw.append(counter)
				total_rcv_orw_timeline.append(temp/60.0)
				if Told == 0:
					Told = msg.timestamp
				else:
					Tnew = msg.timestamp - Told
					if Tnew > 60*time_ratio:
						PRR_orw.append(total_receive_orw * 1.0 / total_send_orw)
						timeline_orw.append(temp / 60.0)
						Told=0
						total_receive_orw = 0
						total_send_orw = 0
	#elif msg.type == NET_DC_REPORT:
	#	if msg.dbg__a + msg.dbg__c < 10000:
	#		DutyCycle_orw[msg.node].append((msg.dbg__a, msg.dbg__b, msg.dbg__c))
	elif msg.type == NET_APP_SENT:
		num_init_orw[msg.node] += 1
		total_send_orw += 1
		'''if total_send_orw == num_node:
			timeline_orw.append( (msg.timestamp/time_ratio +dt)/60.0 )
			PRR_orw.append(total_receive_orw *1.0 / total_send_orw)
			total_send_orw = 0
			total_receive_orw = 0'''
	#note: the parameter msg.dbg__c here is not correct, dont use, only record time
	elif msg.type == NET_C_FE_SENT_MSG:
		timeline_transmit_orw[msg.node].append((msg.timestamp/time_ratio)/60)
		node_transmit_orw[msg.node].append(msg.node)
print "Total connected nodes:", len(connected)
load_orw = {}
for k in num_init_orw:
	if num_init_orw[k] > 40:
		load_orw[k] = num_fwd_orw[k] * 1.0 / num_init_orw[k]
	else:
		pass
		#print "too low init:", k, num_init_orw[k], num_fwd_orw[k]
		#load_orw[k] = num_fwd_orw[k] * 1.0 / 55
#load_orw = {k: num_fwd_orw[k] * 1.0 / num_init_orw[k] + 1 for k in num_init_orw}
#print load_orw
#Calculate the average hops to SINK
counter = defaultdict(int)
total_hops_orw = defaultdict(int)
for (k, v) in route_hist_orw:
	total_hops_orw[k] += max(len(route_hist_orw[(k,v)]) - 1, 0)
	counter[k] += 1

#avg_hops_orw = {k:total_hops_orw[k] / 1.0 / counter[k] for k in total_hops_orw}	
avg_hops_orw = props_orw["Avg_Hops"]
#get the average dutycycle of each node

Avg_Data_dc_orw = props_orw['Avg_Data_dc']
Avg_Idle_dc_orw	= props_orw['Avg_Idle_dc'] 
Avg_Total_dc_orw	= props_orw['Avg_Total_dc'] 
	

#print len(DutyCycle_ctp), "\n", DutyCycle_ctp.keys()		

'''
leaf_orw = set()
relay_orw = set()
for k in load_orw:
	load = load_orw[k]
	if load > TH_load:
		pass
	if k not in dir_neig_orw:
		if load < 2:
			leaf_orw.add(k)
		else:
			relay_orw.add(k)
'''

print "========================================================="


############# Start plot ################
#############Figure 1 fwd load and dc among SN, RL, lF#############

fig = pl.figure()
#plot the barplot of dutycycle among leaf, relay and direct neighbour
ax1 = fig.add_subplot(2,1,1)
values = [Avg_Total_dc_ctp, Avg_Total_dc_orw]

positions = [1, 2]
group = [leaf_ctp, leaf_orw]
text = [('CTP', 'ORW'), 'leaf', 'Avg_Total_dc']
group_barplot(ax1, group, values, positions, text, unit='%')
positions = [4, 5]
group = [relay_ctp, relay_orw]
text = [('CTP', 'ORW'), 'relay', 'Avg_Total_dc']
group_barplot(ax1, group, values, positions, text, unit='%')
positions = [7, 8]
group = [dir_neig_ctp, dir_neig_orw]
text = [('CTP', 'ORW'), 'direct neighbour', 'Avg_Total_dc']
group_barplot(ax1, group, values, positions, text, unit='%')
ax1.set_ylabel("Duty Cycle (%)")
ax1.plot([], c='b', label='CTP')
ax1.plot([], c='r', label='ORW')
ax1.legend(loc=2)

#plot the barplot of load among leaf, relay and direct neighbour
ax2 = fig.add_subplot(2,1,2, sharex=ax1)
values = [load_ctp, load_orw]

positions = [1, 2]
group = [leaf_ctp, leaf_orw]
text = [('CTP', 'ORW'), 'leaf', 'load']
group_barplot(ax2, group, values, positions, text)
positions = [4, 5]
group = [relay_ctp, relay_orw]
text = [('CTP', 'ORW'), 'relay', 'load']
group_barplot(ax2, group, values, positions, text)
positions = [7, 8]
group = [dir_neig_ctp, dir_neig_orw]
text = [('CTP', 'ORW'), 'direct neighbour', 'load']
group_barplot(ax2, group, values, positions, text)

ax2.set_xlim([0,9])
ax2.set_xticklabels(['leaf', 'relay', 'direct neighbour'])
ax2.set_xticks([1.5, 4.5, 7.5])
ax2.set_ylabel("Forwarding Load")
#dummy legend
ax2.plot([], c='b', label='CTP')
ax2.plot([], c='r', label='ORW')
ax2.legend(loc=2)
fig.savefig("./graphs/" + prefix + "L_D.pdf")


#############Figure 2 PDR and send / beacons#############
fig = pl.figure()
ax1 = pl.subplot2grid((3,3), (0,0), colspan=3)
ax2 = pl.subplot2grid((3,3), (1,0), colspan=3, sharex=ax1)
ax3 = pl.subplot2grid((3,3), (2,0), colspan=3, sharex=ax1, sharey=ax2)
#ax4 = pl.subplot2grid((3,3), (0,2), rowspan=3)
ax1.plot(Ttimeline, PRR_ctp, 'g--')
#ax1.plot(timeline_ctp, PRR_ctp, 'g--')
ax1.set_ylim([0,1])
ax1.plot(timeline_orw, PRR_orw)
ax1.set_ylabel("PDR (%)")


if not resultc['simple']:
	#ctp
	ax2.scatter(time_beacon, node_beacon, marker='.', s=1, linewidths=(0.3))
	#orw
	for node in timeline_transmit_orw:
		ax3.scatter(timeline_transmit_orw[node], node_transmit_orw[node], marker='.', s=1, linewidths=(0.3))

#ax2 = fig.add_subplot(2,1,2, projection='3d')
x, y = common_dict(avg_hops_ctp, Avg_Total_dc_ctp)
#ax4.scatter(x.values(), y.values(), color='g', marker='x', label="CTP")
#orw
x, y = common_dict(avg_hops_orw, Avg_Total_dc_orw)
#ax4.scatter(x.values(), y.values(), label="ORW")
#ax4.legend()
#ax2.set_zlim([0,20])
ax1.set_xlim([0,60])
axis_range = ax2.axis()
ax2.set_ylim([0, axis_range[3]])
ax3.set_xlabel("Time (min)")
ax3.set_ylabel("Node ID")

#ax4.set_xlabel("Hops")
#ax4.set_ylabel("DutyCycle (%)")
fig.subplots_adjust(hspace=0)
pl.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)


if not os.path.exists("graphs"):
	os.makedirs("graphs")
pl.savefig("./graphs/" + prefix + "general" + hex(ELIMIT)+ ".pdf")


##################################################################################

if ELIMIT:
####################################     CTP     #################################
	die_time = {}
	num_fwd_ctp = defaultdict(int)
	num_init_ctp = defaultdict(int)
	curr_load_ctp = defaultdict(float)
	counter = 0
	counter1 = 0
	counter2 = 0
	counter3 = 0
	die_leaf_ctp = []
	die_relay_ctp = []
	die_dir_neig_ctp = []
	die_set=set()
	#I have to put it here as it would be memory efficient to plot when it's neccesary
	#############Figure 3 CTP DIE#############
	fig = pl.figure()
	ontime = ELIMIT*1024/32768
	fig.suptitle('Radio on Time:' + str(ontime) + 's, CTP', fontsize=14, fontweight='bold')
	ax1 = fig.add_subplot(4,1,1)
	ax1.grid(True, which='both')
	for msg in CtpdebugMsgs:
		if msg.type == NET_C_DIE:
			if msg.node not in die_set:
				die_set.add(msg.node)
				die_minute = msg.timestamp / 60.0 / time_ratio
				die_time[msg.node] = die_minute
				if counter % 2 >= 0:
					for id in num_init_ctp:
						curr_load_ctp[id] = num_fwd_ctp[id] / num_init_ctp[id] + 1
					bp = ax1.boxplot(curr_load_ctp.values(), positions=[die_minute,], widths=0.4, sym='.')
					setbp(bp, alpha=0.7, linewidth=0.4, ms=3)
					ax1.scatter(die_minute, curr_load_ctp[msg.node], s=4, c='y', marker='D', linewidths=(0.1,))
					ax1.annotate(msg.node, textcoords = 'offset points', size=3, color='k',
									xy = (die_minute, curr_load_ctp[msg.node]), xytext = (0, 0), ha='center')
				num_init_ctp.pop(msg.node, None)
				curr_load_ctp.pop(msg.node, None)
				counter += 1
				#record the ratio of the died nodes
				if msg.node in leaf_ctp:
					counter1 += 1
				elif msg.node in relay_ctp:
					counter2 += 1
				elif msg.node in dir_neig_ctp:
					counter3 += 1
				die_leaf_ctp.append(counter1*100.0/len(leaf_ctp))
				die_relay_ctp.append(counter2*100.0/len(relay_ctp))
				die_dir_neig_ctp.append(counter3*100.0/len(dir_neig_ctp))
				
		elif msg.type == NET_C_FE_FWD_MSG:
			num_fwd_ctp[msg.node] += 1
		elif msg.type == NET_C_FE_SENT_MSG:
			num_init_ctp[msg.node] += 1
	#if we dont want to see the ax, hide it
	#ax1.set_visible(False)		
	
	die_set_ctp = set(die_time.keys())
	
	ax2 = fig.add_subplot(4,1,2, sharex=ax1)
	
	x, y = common_dict(die_time, avg_hops_ctp)
	ax2.scatter(x.values(), y.values(), s=9, linewidths=(0.5))
	#die order
	first = sorted(x, key=x.get)
	#print "Die order:\n", first
	
	for node in x:
		ax2.annotate(node, textcoords = 'offset points', size=4, color='g',
				xy = (x[node], y[node]), xytext = (0, 0))
	
	counter = defaultdict(int)
	for msg in CtpdebugMsgs:
		if msg.node == first[3] and msg.type != 0x40:
			'''print "Node:", msg.node, "Type:", hex(msg.type), \
			(msg.dbg__a), msg.dbg__b, msg.dbg__c, "timestamp", msg.timestamp / time_ratio, \
			"Die time:", x[msg.node] - dt'''
	
	# This part plot the arrows
	anno_arrow (ax2, x, y, first, children_ctp, [0,5], die_set_ctp)
	ax2.grid()
	ax2.set_ylabel("Average Hops")
	
	
	ax3 = pl.subplot(4,1,3, sharex=ax1)
	time_list = sorted(die_time.values())
	#print time_list
	
	ax3.plot(time_list, die_leaf_ctp, linestyle='-', label="leaf")
	ax3.plot(time_list, die_relay_ctp, linestyle='--', label="relay")
	ax3.plot(time_list, die_dir_neig_ctp, linestyle='-.', label="dir_neighbour")
	ax3.grid()
	ax3.set_ylabel("Die Ratio(%)")
	ax3.legend(prop={'size':6}, numpoints=100)
	
	ax4 = pl.subplot(4,1,4, sharex=ax1)
	if not resultc['simple']:
		ax4.scatter(time_beacon, node_beacon, marker='.', s=4, linewidths=(0.3))
		ax4.set_ylabel("Node ID")
	else:
		ax4.plot(Ttimeline, throughput)
		ax4.set_ylabel("Throughput\npackets/min", fontsize=10)
		
	ax1.set_xlim([0,180])
	ax1.set_xticks(range(0,180,20))
	limits = ax1.axis()
	ax1.set_ylim([0, limits[3]])
	limits = ax4.axis()
	ax4.set_ylim([0, limits[3]])
	fig.subplots_adjust(hspace=0)
	pl.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
	pl.savefig("./graphs/" + prefix + "Analysis_ctp_" + hex(ELIMIT) + ".pdf", bbox_inches='tight')
	
		
	#This combines hops, load and die time
	#############Figure 4 CTP DIE#############
	figx = pl.figure()
	ax1_x = figx.add_subplot(2,1,1)
	_, x = common_dict(die_time, avg_hops_ctp)
	_, y = common_dict(die_time, load_ctp)
	x, y = common_dict(x, y)
	z, _ = common_dict(die_time, y)
	vmin=min(die_time.values())
	vmax=max(die_time.values())
	#print die_time.values()
	print "COLOR:", len(load_ctp), len(avg_hops_ctp), len(die_time)
	cm = matplotlib.cm.get_cmap('Reds')
	sc = ax1_x.scatter(z.values(), x.values(), c=y.values(), cmap=cm, s=100, vmin=1, vmax=35)
	ax1_x.set_title("CTP")
	ax1_x.set_ylabel("Hops to sink")
	figx.colorbar(sc)


##################################################################################


	
	
if ELIMIT:
####################################     ORW     #################################
	#############Figure 5 ORW DIE#############
	fig = pl.figure()
	ontime = ELIMIT*1024/32768
	fig.suptitle('Radio on Time:' + str(ontime) + 's, ORW', fontsize=14, fontweight='bold')
	ax1 = fig.add_subplot(4,1,1)
	curr_load_orw = defaultdict(float)
	die_time_orw = {}
	num_fwd_orw = defaultdict(int)
	num_init_orw = defaultdict(int)
	#note this variable has changed
	counter = 0
	counter1 = 0
	counter2 = 0
	counter3 = 0
	die_leaf_orw = []
	die_relay_orw = []
	die_dir_neig_orw = []
	die_set_orw = set()
	
	throughput = []
	Ttimeline = []
	Tcounter=0
	Told=0
	Tinterval=0
	Tnew = 0
	packet_hist = set()
	die_set = set()
	
	for msg in OrwdebugMsgs:
		if msg.type == NET_C_DIE:
			if msg.node not in die_set:
				die_set.add(msg.node)
			
				die_minute = msg.timestamp / time_ratio / 60.0
				die_time_orw[msg.node] = die_minute
				#plot the load when a node die, now disabled
				'''for id in num_init_orw:
					curr_load_orw[id] = num_fwd_orw[id]*1.0 / num_init_orw[id] + 1
				bp = ax1.boxplot(curr_load_orw.values(), positions=[die_minute,], widths=0.8, sym=',')
				setbp(bp, 0.7, 0.5, ms=3)
				ax1.scatter(die_minute, curr_load_orw[msg.node], s=14, c='y', marker='*', linewidths=(0.1,))
				ax1.annotate(msg.node, textcoords = 'offset points', size=3, color='k',
								xy = (die_minute, curr_load_orw[msg.node]), xytext = (0, 0), ha='center')'''
				#num_init_orw.pop(msg.node, None)
				#curr_load_orw.pop(msg.node, None)
				die_set_orw.add(msg.node)
				#record the ratio of the died nodes
				if msg.node in leaf_orw:
					counter1 += 1
				elif msg.node in relay_orw:
					counter2 += 1
				elif msg.node in dir_neig_orw:
					counter3 += 1
				die_leaf_orw.append(counter1*100.0/len(leaf_orw))
				die_relay_orw.append(counter2*100.0/len(relay_orw))
				die_dir_neig_orw.append(counter3*100.0/len(dir_neig_orw))
		elif msg.type == NET_C_FE_RCV_MSG:
			#if origin != last_hop, then last hop is forwarder
			if msg.dbg__b != msg.dbg__c:
				num_fwd_orw[msg.dbg__c] += 1
		elif msg.type == NET_APP_SENT:
			if msg.node not in die_set_orw:
				num_init_orw[msg.node] += 1
	
	#die_time_orw.pop(20)
	#die_time_orw.pop(75)
	print len(die_leaf_orw), len(time_list)
	ax2 = fig.add_subplot(4,1,2, sharex=ax1)
	x, y = common_dict(die_time_orw, avg_hops_orw)
	ax2.scatter(x.values(), y.values())
	
	for node in x:
		ax2.annotate(node, textcoords = 'offset points', size=4, color='g',
				xy = (x[node], y[node]), xytext = (0, 0))
	
	ax3 = pl.subplot(4,1,3, sharex=ax1)
	
	time_list_orw = sorted(die_time_orw.values())
	ax3.plot(time_list_orw, die_leaf_orw, linestyle='-', label="leaf")
	ax3.plot(time_list_orw, die_relay_orw, linestyle='--', label="relay")
	ax3.plot(time_list_orw, die_dir_neig_orw, linestyle='-.', label="dir_neighbour")
	ax3.grid()
	ax3.legend(loc=2, prop={'size':6}, numpoints=100)
	
	ax4 = fig.add_subplot(4,1,4, sharex=ax1)
	
	if not resultc['simple']:
		for node in die_set_orw:
			ax4.scatter(timeline_transmit_orw[node], node_transmit_orw[node], marker='.', s=4, linewidths=(0.3))
	else:
		ax4.plot(Ttimeline, throughput)
	
	
	ax1.set_xlim([0,180])
	ax1.set_xticks(range(0,180,20))
	limits = ax1.axis()
	ax1.set_ylim([0,limits[3]])
	#ax3.set_ylim([0,100])
	ax1.set_ylabel("Forwarding Load")
	ax2.set_ylabel("Average Hops")
	ax3.set_ylabel("Die Ratio (%)")
	if not resultc['simple']:
		ax4.set_ylabel("Node ID")
	else: 
		ax4.set_ylabel("Throughput\npackets/min")
	ax4.set_xlabel("Time (min)")
	fig.savefig("./graphs/" + prefix + "Analysis_orw_" + hex(ELIMIT) + ".pdf")
	
	ax2_x = figx.add_subplot(2,1,2, sharex=ax1_x, sharey=ax1_x)
	_, x = common_dict(die_time_orw, avg_hops_orw)
	_, y = common_dict(die_time_orw, load_orw)
	x, y = common_dict(x, y)
	z, _ = common_dict(die_time_orw, y)
	#print die_time.values()
	print "COLOR:", len(load_orw), len(avg_hops_orw), len(die_time_orw)
	#cm = matplotlib.cm.get_cmap('RdYlBu')
	sc = ax2_x.scatter(z.values(), x.values(), c=y.values(), cmap=cm, s=100, vmin=1, vmax=35)
	figx.colorbar(sc)
	ax1_x.set_xlim([0,180])
	ax2_x.set_title("ORW")
	ax2_x.set_ylabel("Hops to sink")
	ax2_x.set_xlabel("Time (min)")
	figx.tight_layout()

##################################################################################

###################################Put Together####################################
###################################Total Rcv####################################
fig = pl.figure(figsize=(12,8))

#ax1
ax1 = fig.add_subplot(3,1,1)
ax1.plot(total_rcv_orw_timeline, total_rcv_orw, 'g--', linewidth=2)
ax1.plot(total_rcv_ctp_timeline, total_rcv_ctp, 'b', linewidth=2)
f_orw = interp1d(total_rcv_orw_timeline, total_rcv_orw)
f_ctp = interp1d(total_rcv_ctp_timeline, total_rcv_ctp)
lb = max(total_rcv_orw_timeline[0], total_rcv_ctp_timeline[0])
ub = min(total_rcv_orw_timeline[-1], total_rcv_ctp_timeline[-1])
x = np.arange(lb, ub, 0.1)
ax1.fill_between(x, f_orw(x), f_ctp(x), facecolor='y', edgecolor='', hatch='/', where=f_ctp(x)>=f_orw(x))
ax1.fill_between(x, f_orw(x), f_ctp(x), facecolor='r', edgecolor='', hatch='\\', where=f_ctp(x)<=f_orw(x))
#dummy plot only for legend
p1 = matplotlib.patches.Rectangle([0,0], 1, 1, fc='y', hatch='/')
p2 = matplotlib.patches.Rectangle([0,0], 1, 1, fc='r', hatch='\\')
ax1.legend([p1, p2], ["CTP>ORW", "ORW>CTP"], loc=2)
ax1.set_ylabel("# of Received Packets")
#ax1.legend()
ax1.grid()


#ax2
xp = np.arange(lb+1.1, ub-1.1, 1)
first_ctp = derivative(f_ctp,xp,dx=1,n=1)
first_orw = derivative(f_orw,xp,dx=1,n=1) 

ax2 = fig.add_subplot(3,1,2, sharex=ax1)
ax2.plot(xp, first_ctp, label='CTP')
ax2.plot(xp, first_orw, linestyle='--', label='ORW')
ax2.set_ylabel("Throughput (packet/s)")
ax2.grid()
ax2.legend()


#ax3
ax3 = fig.add_subplot(3,1,3, sharex=ax1)
ax3.plot(time_list_orw, die_leaf_orw, color='g',linestyle='--' , label="orw_leaf")
ax3.plot(time_list_orw, die_relay_orw, color='r', linestyle='--', label="orw_relay")
ax3.plot(time_list_orw, die_dir_neig_orw, color='b', linestyle='--', label="orw_sink_neighbour")
ax3.plot(time_list, die_leaf_ctp, color='g', label="ctp_leaf")
ax3.plot(time_list, die_relay_ctp, color='r', label="ctp_relay")
ax3.plot(time_list, die_dir_neig_ctp, color='b', label="ctp_sink_neighbour")
ax3.grid()
ax3.legend(loc=2, numpoints=200, prop={'size':10})
ax3.set_ylabel("die percentage (%)")
ax3.set_xlabel("Time (min)")

#hide time
pl.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
ax1.set_xlim([lb, ub])
fig.subplots_adjust(hspace=0)
for ax in fig.axes:
	yticks = ax.yaxis.get_major_ticks()
	yticks[-1].label1.set_visible(False)
fig.savefig("el1000Indriya.pdf", bbox_inches='tight')

def find_element(element, list_element, another_list):
	try:
		index_element=list_element.index(element)
		return another_list[index_element]
	except ValueError:
		return -1
            
die_S = find_element(100, die_dir_neig_ctp, time_list)
die_R = find_element(100, die_relay_ctp, time_list)
die_L = find_element(100, die_leaf_ctp, time_list)
			
print "CTP: First die:{:.2f} Last S, R, L Die:{:.2f} {:.2f} {:.2f}".format(
                   time_list[0], die_S, die_R, die_L)
                   
die_S = find_element(100, die_dir_neig_orw, time_list_orw)
die_R = find_element(100, die_relay_orw, time_list_orw)
die_L = find_element(100, die_leaf_orw, time_list_orw)               
print "ORW: First die:{:.2f} Last S, R, L Die:{:.2f} {:.2f} {:.2f}".format(
                   time_list_orw[0], die_S, die_R, die_L)
'''
###################################COMMON PART####################################
if ELIMIT:
	marker = ['v','x','<','>','+','s']
	#ctp
	fig = pl.figure()
	ax1 = fig.add_subplot(1,1,1)
	s = set(die_time.keys()) & leaf_ctp
	x = {k:die_time[k] for k in s}
	y = {k:load_ctp[k] for k in s}
	ax1.scatter(x.values(), y.values(), marker=marker[0], label='leaf_ctp')
	s = set(die_time.keys()) & relay_ctp
	x = {k:die_time[k] for k in s}
	y = {k:load_ctp[k] for k in s}
	ax1.scatter(x.values(), y.values(), marker=marker[1], label='relay_ctp')
	s = set(die_time.keys()) & dir_neig_ctp
	x = {k:die_time[k] for k in s}
	y = {k:load_ctp[k] for k in s}
	ax1.scatter(x.values(), y.values(), marker=marker[2], label='dir_neig_ctp')
	
	#orw
	s = set(die_time_orw.keys()) & leaf_orw
	x = {k:die_time_orw[k] for k in s}
	y = {k:load_orw[k] for k in s}
	ax1.scatter(x.values(), y.values(), marker=marker[3], color='r', label='leaf_orw')
	s = set(die_time_orw.keys()) & relay_orw
	
	x = {k:die_time_orw[k] for k in s}
	y = {k:load_orw[k] for k in s}
	ax1.scatter(x.values(), y.values(), marker=marker[4], color='r', label='relay_orw')
	s = set(die_time_orw.keys()) & dir_neig_orw
	x = {k:die_time_orw[k] for k in s}
	y = {k:load_orw[k] for k in s}
	ax1.scatter(x.values(), y.values(), marker=marker[5], color='r', label='dir_neig_orw')
	limits = ax1.axis()
	if not TWIST:
		ax1.set_xlim([0, 60])
	else:
		ax1.set_xlim([0,180])
	ax1.set_ylim([0, limits[3]])
	ax1.legend()
	fig.savefig('./graphs/' + prefix + "combined.pdf")
'''	
pl.show()
