import tools.reader as reader
import tools.twistReader as treader
import array
import matplotlib
import pylab as pl
import math
import operator
import os
import itertools
from collections import defaultdict
from numpy import mean

def filter_dict(d, keys, invert=False):
    if invert:
        key_set = set(d.keys()) - set(keys)
    else:
        key_set = set(keys) & set(d.keys())
    return { k: d[k] for k in key_set }
    
def common_dict (d1, d2):
	d1 = filter_dict(d1, d2.keys())
	d2 = filter_dict(d2, d1.keys())
	return d1, d2
#generate constant values
def constant_factory(value):
	return itertools.repeat(value).next

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
						
def setbp(bp, alpha, linewidth, ms):
	pl.setp(bp['boxes'], alpha=alpha, linewidth=linewidth)
	pl.setp(bp['medians'], alpha=alpha, linewidth=linewidth)
	pl.setp(bp['whiskers'], alpha=alpha, linewidth=linewidth)
	pl.setp(bp['caps'], linewidth=linewidth + 0.1)
	pl.setp(bp['fliers'], linewidth=0.4, ms=1.5)

SINK_ID = 13
#type constant
NET_C_FE_NO_ROUTE 	= 0x12			#no arg
NET_C_FE_SENT_MSG	= 0x20			#:app. send       :msg uid, origin, next_hop
NET_C_FE_RCV_MSG 	= 0x21			#:next hop receive:msg uid, origin, last_hop
NET_C_FE_FWD_MSG 	= 0x22			#:fwd msg         :msg uid, origin, next_hop
NET_C_FE_DST_MSG 	= 0x23			#:base app. recv  :msg_uid, origin, last_hop 
NET_DC_REPORT 		= 0x60			#duty cycle report :uint16_t dutyCycle, uint16_t time
NET_LL_DUPLICATE 	= 0x61			#dropped duplicate packet seen in cache:dsn, source, accept
NET_LPL_SENDDONE 	= 0x62			#report duration of send duty cycle
#Filters a dict by only permitting certain keys.
NET_APP_SENT 		= 0x70			#app. send       :msg uid, origin
NET_C_DIE 			= 0x71
NET_DC_REPORT		= 0x60

#trace_20140420_212823.2 orw 0x1000 2 hour
#trace_20140420_234914.3

path = '/home/nagatoyuki/Desktop/Thesis/Twist/trace_20140420_212823.2.txt'
OrwdebugMsgs, _, _, _= treader.load(path)
path = '/home/nagatoyuki/Desktop/Thesis/Twist/trace_20140420_234914.3.txt'
CtpdebugMsgs, _, _, CtpDataMsgs= treader.load(path)


children_orw = defaultdict(set)
num_fwd_orw = defaultdict(int)
num_init_orw = defaultdict(int)
route_hist_orw = defaultdict(set)
DutyCycle_orw = defaultdict(list)
dir_neig_orw = set()	
# This is the time when packet is generated
timeline_orw = []
# this is every transmission
timeline_transmit_orw = defaultdict(list)
node_transmit_orw = defaultdict(list)
PRR_orw = []
total_send_orw = 0
total_receive_orw = 0
connected = set()

dt=0
num_node = 86
SIMPLE = True
ELIMIT = 0x1500

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
dir_neig_ctp = set()

#ctp
for msg in CtpdebugMsgs:
	if msg.type == NET_C_FE_SENT_MSG:# or msg.type == 0x26:
		total_send_ctp += 1
		num_init_ctp[msg.node] += 1
		if total_send_ctp == num_node:
			PRR_ctp.append(total_receive_ctp * 1.0 / total_send_ctp)
			timeline_ctp.append((msg.timestamp/1000.0 + dt) / 60)
			total_send_ctp = 0
			total_receive_ctp = 0
	#record beacon
	elif msg.type == 0x33:
		time_beacon.append((msg.timestamp/1000 + dt)/60.0)
		node_beacon.append(msg.node)
	elif msg.type == NET_DC_REPORT and msg.node != SINK_ID:
		DutyCycle_ctp[msg.node].append((msg.dbg__a, msg.dbg__b, msg.dbg__c))
	elif msg.type == NET_C_FE_FWD_MSG:
		children_ctp[msg.dbg__c].add(msg.node)
		num_fwd_ctp[msg.node] += 1
	elif msg.type == NET_C_FE_RCV_MSG:
		if msg.node == SINK_ID:
			total_receive_ctp += 1
			dir_neig_ctp.add(msg.dbg__c)

fig = pl.figure()

ax1 = fig.add_subplot(2,1,1)
x = sorted(num_init_ctp.keys())
y = [num_init_ctp[k] for k in x]
ax1.bar(x, y)

#orw
for msg in OrwdebugMsgs:
		#if msg.node == 13:
		#	print "type", hex(msg.type), msg.dbg__a, msg.dbg__b, msg.dbg__c, msg.timestamp
		if msg.type == NET_C_FE_RCV_MSG:
			#if origin != last_hop, then last hop is forwarder
			if msg.dbg__b != msg.dbg__c:
				num_fwd_orw[msg.dbg__c] += 1
			#last hop is current node's child
			children_orw[msg.node].add(msg.dbg__c)
			# (origin, SeqNo) += lasthop
			route_hist_orw[(msg.msg__origin, msg.dbg__a)].add(msg.dbg__c)
			#if node is SINK, add node to direct neighbour
			if msg.node == SINK_ID:
				dir_neig_orw.add(msg.dbg__c)
				total_receive_orw += 1
				connected.add(msg.msg__origin)
		elif msg.type == NET_DC_REPORT:
			DutyCycle_orw[msg.node].append((msg.dbg__a, msg.dbg__b, msg.dbg__c))
		elif msg.type == NET_APP_SENT:
			total_send_orw += 1
			num_init_orw[msg.node] += 1
			if total_send_orw == num_node:
				timeline_orw.append( (msg.timestamp/1000 +dt)/60.0 )
				PRR_orw.append(total_receive_orw *1.0 / total_send_orw)
				total_send_orw = 0
				total_receive_orw = 0
		#note: the parameter msg.dbg__c here is not correct, dont use, only record time
		elif msg.type == NET_C_FE_SENT_MSG:
			timeline_transmit_orw[msg.node].append((msg.timestamp/1000.0 + dt)/60)
			node_transmit_orw[msg.node].append(msg.node)


#Calculate the average hops to SINK
counter = defaultdict(int)
total_hops_orw = defaultdict(int)
for (k, v) in route_hist_orw:
	total_hops_orw[k] += max(len(route_hist_orw[(k,v)]) - 1, 0)
	counter[k] += 1

avg_hops_orw = {k:total_hops_orw[k] / 1.0 / counter[k] for k in total_hops_orw}	
#get the average dutycycle of each node
Avg_DC_orw = {k: mean(DutyCycle_orw[k], axis=0) for k in DutyCycle_orw}

Avg_Data_dc_orw = {}
Avg_Idle_dc_orw = {}
Avg_Total_dc_orw = {}

for node in Avg_DC_orw:
	Avg_Data_dc_orw[node] = Avg_DC_orw[node][0]*0.01
	Avg_Idle_dc_orw[node] = Avg_DC_orw[node][2]*0.01
	Avg_Total_dc_orw[node] = Avg_Data_dc_orw[node] + Avg_Idle_dc_orw[node]
	if Avg_Total_dc_orw[node] > 10:
		print "Too High DC(ORW)", node, Avg_Total_dc_orw[node]

#load_ctp = {k: num_fwd_ctp[k] * 1.0 / num_init_ctp[k] + 1 for k in num_init_ctp}
load_orw = {k: num_fwd_orw[k] * 1.0 / num_init_orw[k] + 1 for k in num_init_orw}

leaf_orw = set()
relay_orw = set()
for k in load_orw:
	if load_orw[k] > 20:
		print "Too High load", k, load_orw[k], "Fwd:", num_fwd_orw[k], "Init", num_init_orw[k]
	if load_orw[k] < 1.1:
		leaf_orw.add(k)
	elif k not in dir_neig_orw:
		relay_orw.add(k)
		
#fig = pl.figure(figsize=(12,12))
width = 0.4
ax2 = fig.add_subplot(2,1,2)
x=sorted(num_init_orw.keys())
y1=[num_init_orw[k] for k in x]
ax2.bar(x, y1, width=width, edgecolor='none')
y2=[num_fwd_orw[k] for k in x]
ax2.bar(x, y2, bottom = y1, color='y', width=width, edgecolor='none')

#x=sorted(num_init_ctp.keys())
x1 = [v+width for v in x]
y1=[num_init_ctp[k] for k in x]
ax2.bar(x1, y1, color='r', width=width, label='ctp_init', edgecolor='none')
y2=[num_fwd_ctp[k] for k in x]
ax2.bar(x1, y2, bottom = y1, color='g', width=width, label='ctp_forward', edgecolor='none')
ax2.legend()
fig.savefig('twist.pdf')
#pl.show()
'''	
fig = pl.figure()
ax1 = fig.add_subplot(4,1,1)
curr_load_orw = defaultdict(float)
die_time = {}
num_fwd_orw = defaultdict(int)
num_init_orw = defaultdict(int)
counter = 0
counter1 = 0
counter2 = 0
counter3 = 0
die_leaf_orw = []
die_relay_orw = []
die_dir_neig_orw = []

for msg in OrwdebugMsgs:
	if msg.type == NET_C_DIE:
		die_minute = msg.dbg__b / 60.0
		die_time[msg.node] = die_minute
		for id in num_init_orw:
			curr_load_orw[id] = num_fwd_orw[id]*1.0 / num_init_orw[id] + 1
			#max_load_orw = max(max_load_orw, curr_load_orw[id])
		bp = ax1.boxplot(curr_load_orw.values(), positions=[die_minute,], widths=0.8, sym=',')
		setbp(bp, 0.7, 0.5, ms=3)
		ax1.scatter(die_minute, curr_load_orw[msg.node], s=14, c='y', marker='*', linewidths=(0.1,))
		ax1.annotate(msg.node, textcoords = 'offset points', size=3, color='k',
						xy = (die_minute, curr_load_orw[msg.node]), xytext = (0, 0), ha='center')
		num_init_orw.pop(msg.node)
		curr_load_orw.pop(msg.node)
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
		#else it's inital sender
		elif msg.node != SINK_ID:
			num_init_orw[msg.dbg__c] += 1

#die_time.pop(20)
#die_time.pop(75)

die_set_orw = set(die_time.keys())
print "DIE:\n", die_set_orw
ax2 = fig.add_subplot(4,1,2, sharex=ax1)
x, y = common_dict(die_time, avg_hops_orw)
ax2.scatter(x.values(), y.values())

for node in x:
	ax2.annotate(node, textcoords = 'offset points', size=4, color='g',
			xy = (x[node], y[node]), xytext = (0, 0))

ax3 = pl.subplot(4,1,3, sharex=ax1)
time_list = sorted(die_time.values())
ax3.plot(time_list, die_leaf_orw, linestyle='-', label="leaf")
ax3.plot(time_list, die_relay_orw, linestyle='--', label="relay")
ax3.plot(time_list, die_dir_neig_orw, linestyle='-.', label="dir_neighbour")
ax3.grid()
ax3.legend(loc=2, prop={'size':6}, numpoints=100)

ax4 = fig.add_subplot(4,1,4, sharex=ax1)

if not SIMPLE:
	for node in die_set_orw:
		ax4.scatter(timeline_transmit_orw[node], node_transmit_orw[node], marker='.', s=4, linewidths=(0.3))

ax1.set_xlim([0,60])
ax1.set_ylim([0,15])
#ax3.set_ylim([0,100])
fig.savefig("./graphs/Analysis_orw_" + hex(ELIMIT) + ".pdf")'''
