#!/usr/bin/python
import tools.reader as reader
import numpy as np
import array
import networkx as nx
import matplotlib
import pylab as pl
import math
import operator
import os
from collections import defaultdict
from mpl_toolkits.mplot3d import Axes3D
from tools.constant import *
import tools.command as command
import sys, getopt

resultc = command.main(sys.argv[1:])
FileDict, props = command.getfile(resultc)
ELIMIT = resultc['lim']
folder='./graphs/twist/'

if not resultc['twist']:
	node_range = range(0, 140)
else:
	node_range = range(0, 300)
SINK_ID = props['SINK_ID']
print SINK_ID, resultc['twist']

#add link to linkset
def add_link (link, node, linkset):
	if not node in linkset:
		linkset[node] = set()
	linkset[node].add(link)

#add node to route_hist
def add_route (node, packet, route_hist):
	if not packet in  route_hist:
		route_hist[packet] = []
	if not node in route_hist[packet]:
		route_hist[packet].append(node)
	
#return (x,y) for ecdf plotting
def calc_ecdf (data):
	sorted = np.sort( data )
	#need bias or not?
	yvals = np.arange(len(sorted))/float(len(sorted)) + 0.5/float(len(sorted))
	return sorted, yvals
	
def filter_dict(d, keys, invert=False):
    """ Filters a dict by only permitting certain keys. """
    if invert:
        key_set = set(d.keys()) - set(keys)
    else:
        key_set = set(keys) & set(d.keys())
    return { k: d[k] for k in key_set }
    
def common_dict (d1, d2):
	d1 = filter_dict(d1, d2.keys())
	d2 = filter_dict(d2, d1.keys())
	return d1, d2

def exclu_dict (d1, d2, ed):
	d1 = filter_dict(d1, ed.keys(), invert=True)
	dd1, dd2 = common_dict (d1, d2)
	return dd1, dd2


        
#######################################ORW####################################
#load orw debug message
#debugMsgs = reader.loadDebug(path, fileNames)
debugMsgs = FileDict['OrwDebug']

#create network graph
#G = nx.Graph()
#nodes = {}
#vip_nodes = []
init_orw = array.array('I', (0 for i in node_range))
#record number of forwading load
fwd_orw = array.array('I', (0 for i in node_range))
#record the route history to sink according to (Src, SeqNum)
route_hist = {}
discovered_link = defaultdict(list)
direct_nb_orw = set()
dutyCycle_data_orw = defaultdict(int)
avg_dutyCycle_orw = defaultdict(int)
counter_orw = defaultdict(int)
neighbour_orw = defaultdict(set)
dutyCycle_idle_orw = {}
die_orw = {}
seperate_orw = set()
unstable_orw = set()

lower_life_orw = 2.455*ELIMIT - 30.5

for msg in debugMsgs:
	#if msg.node == 20 or msg.node==75 :
	#	print "node:", msg.node, hex(msg.type), msg.dbg__a, msg.dbg__b, msg.dbg__c 
	#if type is receive, record every edge that appears
	if msg.type == NET_C_FE_RCV_MSG:
		#record the route history to sink according to (Src, SeqNum)
		add_route(msg.node, (msg.dbg__b, msg.dbg__a), route_hist)
		add_link((msg.dbg__c, msg.node), msg.dbg__b, discovered_link)
		#init_orw[msg.dbg__b] = max(0, msg.dbg__a)
		if(msg.node == SINK_ID):
			direct_nb_orw.add(msg.dbg__c)
		if msg.dbg__b != msg.dbg__c and msg.dbg__c < 300:
			fwd_orw[msg.dbg__c] += 1
		neighbour_orw[msg.node].add(msg.dbg__c)
		neighbour_orw[msg.dbg__c].add(msg.node)
	elif msg.type == NET_DC_REPORT and msg.node != SINK_ID:
		dutyCycle_data_orw[msg.node] += (msg.dbg__a + msg.dbg__c)
		counter_orw[msg.node] += 1
		#dutyCycle_idle_orw[msg.node] = msg.dbg__c
	elif msg.type == NET_C_DIE:
		die_orw[msg.node] = (msg.dbg__a, msg.dbg__b)
		if msg.dbg__b < lower_life_orw / 7:
			print "die too early:", msg.node
			unstable_orw.add(msg.node)
	elif msg.type == NET_APP_SENT:
		init_orw[msg.node] += 1
		
num_neighbour_orw = {k : len(neighbour_orw[k]) for k in neighbour_orw}
#print "fwd_orw:\n", fwd_orw
#print "neighbour_orw:\n", neighbour_orw
#print "die_orw:\n", die_orw

avg_dutyCycle_orw = {k:dutyCycle_data_orw[k] * 0.01 / counter_orw[k] for k in dutyCycle_data_orw}
#details can be found in http://stackoverflow.com/questions/4690416/sorting-dictionary-using-operator-itemgetter
sorted_die_orw = sorted(die_orw.iteritems(), key=lambda (k,v): v[1])
last_time_orw = 0

print "direct neighbour: ", len(direct_nb_orw)

#total hops of each node
total_Fhops = array.array('I', (0 for i in node_range))

counterF = array.array('I', (0 for i in node_range))
for (x, y) in route_hist:
	for ID in route_hist[(x,y)]:
		if ID != SINK_ID:
			total_Fhops[ID] += (len(route_hist[(x, y)]) - route_hist[(x, y)].index(ID))
			counterF[ID] += 1
			

avg_Fhops = {}
#in case avg_hops and load, link dont have same length
fwd_load_orw = {}
link_orw = {}

sum_x_dir_orw = 0
sum_x2_dir_orw = 0
sum_x_indir_orw = 0
sum_x2_indir_orw = 0
num_item_orw = 0

#iterate on all possible nodeID
for ID in node_range:
	if not counterF[ID] == 0:
		avg_Fhops[ID] = max(0, 1.0 * total_Fhops[ID] / counterF[ID] - 2)
	if init_orw[ID] > 20:
		fwd_load_orw[ID] = 1.0 * fwd_orw[ID] / init_orw[ID] + 1
		if fwd_load_orw[ID] > 20:
			print fwd_orw[ID], init_orw[ID]
		link_orw[ID] = len(discovered_link[ID])
		#Jane's fairness index
		if ID in direct_nb_orw:
			sum_x_dir_orw += fwd_load_orw[ID]
			sum_x2_dir_orw += math.pow(fwd_load_orw[ID], 2)
		else:
			sum_x_indir_orw += fwd_load_orw[ID]
			sum_x2_indir_orw += math.pow(fwd_load_orw[ID], 2)
		num_item_orw += 1



print 'ORW direct neighbour\'s Jain index:', math.pow(sum_x_dir_orw, 2) / num_item_orw / sum_x2_dir_orw
print 'ORW relay\'s Jain index:', math.pow(sum_x_indir_orw, 2) / num_item_orw / sum_x2_indir_orw


#######################################CTP####################################
'''
CTP data processing

Notice that here using thl to estimate the average hops to sink
'''

#CtpdebugMsgs = reader.loadDebug(path2, fileNames2)

#CtpdataMsgs = reader.loadDataMsg(path3, fileNames3)
CtpdataMsgs = FileDict['CtpData']
CtpdebugMsgs = FileDict['CtpDebug']

fwd_ctp = array.array('I', (0 for i in node_range))
init_ctp = array.array('I', (0 for i in node_range))
#route history of ctp
hist_ctp = {}
discovered_link_ctp = {}
direct_nb_ctp = set()
dutyCycle_data_ctp = defaultdict(int)
counter_ctp = defaultdict(int)
dutyCycle_idle_ctp = defaultdict(int)
neighbour_ctp = defaultdict(set)
die_ctp = {}

for msg in CtpdebugMsgs:
	if msg.type == NET_C_FE_FWD_MSG:
		fwd_ctp[msg.node] += 1
		add_route(msg.dbg__c, (msg.msg__origin, msg.msg__msg_uid), hist_ctp)
		if msg.msg__origin < 300:
			add_link((msg.node, msg.msg__other_node), msg.msg__origin, discovered_link_ctp)
		if msg.dbg__c == SINK_ID:
			direct_nb_ctp.add(msg.node)
		neighbour_ctp[msg.node].add(msg.dbg__c)
	elif msg.type == NET_C_FE_SENT_MSG:
		init_ctp[msg.node] += 1
		add_route(msg.dbg__c, (msg.msg__origin, msg.msg__msg_uid), hist_ctp)
		add_link((msg.node, msg.msg__other_node), msg.node, discovered_link_ctp)
		if(msg.dbg__c == SINK_ID):
			direct_nb_ctp.add(msg.node)
		neighbour_ctp[msg.node].add(msg.dbg__c)
	elif msg.type == NET_DC_REPORT and msg.node != SINK_ID:
		if msg.dbg__a + msg.dbg__c < 10000:
			dutyCycle_data_ctp[msg.node] += (msg.dbg__a + msg.dbg__c)
			counter_ctp[msg.node] += 1
		else:
			print "abnormal data detected: node", msg.node, "dc:", msg.dbg__a + msg.dbg__c
		#dutyCycle_idle_ctp[msg.node] = msg.dbg__c 
	elif msg.type == NET_C_DIE:
		die_ctp[msg.node] = (msg.dbg__a, msg.dbg__b)
		
print len(die_ctp)
num_neighbour_ctp = {k : len(neighbour_ctp[k]) for k in neighbour_ctp}
#avg_dutyCycle_ctp = {}
#for k in dutyCycle_data_ctp:
#	avg_dutyCycle_ctp[k] = dutyCycle_data_ctp[] * 1.0 / counter_ctp[k]
avg_dutyCycle_ctp = {k:dutyCycle_data_ctp[k] * 0.01 / counter_ctp[k] for k in dutyCycle_data_ctp}
sorted_die_ctp = sorted(die_ctp.iteritems(), key=lambda (k,v): v[1])
last_time_ctp = 0
#for (x, y) in sorted_die_ctp:
#	print "node:", x, "energy:", y[0], " Time: ", y[1]

	

print "direct neighbour(CTP): ", len(direct_nb_ctp)
		
#print discovered_link_ctp
'''for ID in xrange(1,140):
	if init_ctp[ID] == 0 and fwd_ctp[ID] != 0:
		print ID'''

fwd_load_ctp = {}
link_ctp = {}
sum_x_dir_ctp = 0
sum_x2_dir_ctp = 0
sum_x_indir_ctp = 0
sum_x2_indir_ctp = 0
num_item_ctp = 0
#use information to calculate hops
for ID in node_range:
	if init_ctp[ID] != 0:
		fwd_load_ctp[ID] = 1.0 * fwd_ctp[ID] / init_ctp[ID] + 1
		#Jane's fairness index
		if ID in direct_nb_ctp:
			sum_x_dir_ctp += fwd_load_ctp[ID]
			sum_x2_dir_ctp += math.pow(fwd_load_ctp[ID], 2)
		else:
			sum_x_indir_ctp += fwd_load_ctp[ID]
			sum_x2_indir_ctp += math.pow(fwd_load_ctp[ID], 2)
		num_item_ctp += 1
'''if ELIMIT:
	for node in direct_nb_ctp:
		if fwd_load_ctp[node] != 1:
			last_time_ctp = max(die_ctp[node][1], last_time_ctp)
print last_time_ctp'''
		
print 'CTP direct neighbour\'s Jain index:', math.pow(sum_x_dir_ctp, 2) / num_item_ctp / sum_x2_dir_ctp
print 'CTP relay\'s Jain index:', math.pow(sum_x_indir_ctp, 2) / num_item_ctp / sum_x2_indir_ctp

#using THL to calculate leaf hops to sink 
thl = defaultdict(int)
for msg in CtpdataMsgs:
	if msg.node == SINK_ID:
		thl[(msg.origin, msg.seqno)] = max(msg.thl, thl[(msg.origin, msg.seqno)])

counter_c_thl = array.array('I', (0 for i in node_range))
total_thl_c = array.array('I', (0 for i in node_range))
for (x, y) in thl:
	total_thl_c[x] += thl[(x, y)]
	counter_c_thl[x] += 1
	
avg_thl_c = {}
#print sorted(discovered_link_ctp.keys())
for ID in discovered_link_ctp:
	if counter_c_thl[ID] != 0:
		avg_thl_c[ID] = max(1.0 * total_thl_c[ID] / counter_c_thl[ID] - 1, 0)
	link_ctp[ID] = len(discovered_link_ctp[ID])



#######################################PLOT SECTION#######################################
#function that plot 1st-order trend line
def polyfit_anno(x, y, order=1, color='k'):
	fit = pl.polyfit(x.values(), y.values(), order)
	fit_fn = pl.poly1d(fit)
	pl.plot(x.values(), fit_fn(x.values()), color)
	midpoint = (min(x.values()) + max(x.values()))/2
	minpointy = min(y.values())/1.5
	# about arrow properties: http://matplotlib.org/1.3.1/users/annotations_guide.html
	ax.annotate(fit_fn, xy=(midpoint, fit_fn(midpoint)), xytext=(1.2*midpoint, minpointy), 
				arrowprops=dict(arrowstyle="->", ec=color))
				

#the figure of hops - forward load
pl.figure()
#get the common set of two source
x = filter_dict(avg_thl_c, fwd_load_ctp.keys())
y = filter_dict(fwd_load_ctp, avg_thl_c.keys())

pl.scatter(x.values(), y.values(), marker='x', color='#FFBF00', label='ctp')

x = filter_dict(avg_Fhops, fwd_load_orw.keys())
y = filter_dict(fwd_load_orw, avg_Fhops.keys())
pl.scatter(x.values(), y.values(), label='orw')
pl.legend()
pl.xlabel('Average # of Hops to Sink')
pl.ylabel('Forwading Load')
pl.savefig(folder + "hops_Fwd.png")


########graph shows send and forward########
pl.figure(figsize=(12,10), dpi=100)
ind = np.arange(0, 300)
width = 0.4
pl.bar(ind, init_orw, width, color='b', label='orw_own', edgecolor='none')
pl.bar(ind, fwd_orw, width, bottom = init_orw, color = '#FF0000', label='orw_forward', edgecolor='none')
pl.bar(ind+width, init_ctp, width, color = '#FFBF00', label='ctp_own', edgecolor='none')
pl.bar(ind+width, fwd_ctp, width, bottom = init_ctp, color = '#00FF00', label='ctp_forward', edgecolor='none')

pl.legend()
pl.xlabel('Node ID')
pl.ylabel('# of Transmitted Packets')
pl.savefig(folder + "send_Fwd.png")


########the figure of hops - discovered links########
pl.figure()
x, y = common_dict(avg_Fhops, link_orw)

pl.scatter(x.values(), y.values(), label='orw')
x, y = common_dict(avg_thl_c, link_ctp)
pl.scatter(x.values(), y.values(), color ='#FFBF00', marker='x', label='ctp')

pl.xlabel("Average # of Hops to Sink")
pl.ylabel("# of discovered links")
pl.legend(loc=2)
pl.savefig(folder + "hops_links.png")

#ecdf of forward load among all nodes
pl.figure()
x, y = calc_ecdf(fwd_load_orw.values())
pl.plot( x, y, label='orw')
x, y = calc_ecdf(fwd_load_ctp.values())
pl.plot(x, y, color='#FFBF00', linestyle='--', label='ctp')
pl.ylabel('Empirical CDF')
pl.xlabel('Forwarding Load')
pl.legend(loc=4)
pl.savefig(folder + "ecdf_ctp_fwdload.png")


########ecdf of direct neighbour########
pl.figure()
#get the load of certain nodes
dir_load_ctp = filter_dict(fwd_load_ctp, direct_nb_ctp)
dir_load_orw = filter_dict(fwd_load_orw, direct_nb_orw)
dic_fwd_orw = defaultdict(int)
dic_fwd_ctp = defaultdict(int)

for i in node_range:
	if fwd_orw[i] != 0 or init_orw[i] != 0:
		dic_fwd_orw[i] = fwd_orw[i] + init_orw[i]
	if fwd_ctp[i] != 0 or init_ctp[i] != 0:
		dic_fwd_ctp[i] = fwd_ctp[i] + init_ctp[i]
	
dir_orw = filter_dict(dic_fwd_orw, direct_nb_orw)
dir_ctp = filter_dict(dic_fwd_ctp, direct_nb_ctp)
#print dir_load_orw

x, y = calc_ecdf(dir_load_orw.values())
pl.plot( x, y, label='orw')
x, y = calc_ecdf(dir_load_ctp.values())
pl.plot(x, y, color='#FFBF00', linestyle='--', label='ctp')
pl.ylabel('Empirical CDF')
pl.xlabel('Forwarding Load')
pl.legend(loc=4)
pl.savefig(folder + "ecdf_fwdload_dir_neighbour.png")


########figure of forwarding load and duty cycle########
pl.figure()
ax = pl.gca()
x, y = common_dict(fwd_load_orw, avg_dutyCycle_orw)
pl.scatter(x.values(),y.values(), label='orw')

x, y = common_dict(fwd_load_ctp, avg_dutyCycle_ctp)
for node in avg_dutyCycle_ctp:
	if avg_dutyCycle_ctp[node] > 20:
		print "Node ",node, "Avg DC is:", avg_dutyCycle_ctp[node]
pl.scatter(x.values(),y.values(), color ='#FFBF00', marker='x', label='ctp')

pl.xlabel('Forwarding load')
pl.ylabel('dutyCycle(%)')
leg = pl.legend(loc=4)
leg.get_frame().set_alpha(0.5)
pl.axis([0, ax.get_xlim()[1], 0, ax.get_ylim()[1]])
pl.show()
pl.savefig(folder + "load_dutyCycle.png")

'''########figure of neighbour and load########
pl.figure()
x, y = common_dict(dic_fwd_orw, num_neighbour_orw)
pl.scatter(x.values(), y.values(), color='#FF0000', marker='v')
pl.xlabel('# of Transmitions')
pl.ylabel('# of parents and children')
pl.savefig(folder + 'load_neighbour.png')'''


if ELIMIT:
	########figure of forwarding load and lifetime########
	pl.figure()
	ax=pl.gca()
	#orw
	die_orw_time = {k:die_orw[k][1] for k in die_orw}
	for node in unstable_orw:
		die_orw_time.pop(node, None)
	
	x, y = common_dict(dic_fwd_orw, die_orw_time)
	pl.scatter(y.values(), x.values(), label='orw')
	#only direc neighbour
	xx, _ = common_dict(dic_fwd_orw, dir_orw)
	x, y = common_dict(xx, die_orw_time)
	pl.scatter(y.values(), x.values(), color='#FF0000', marker='v', label='orw_direct_nb')
	if len(x) > 2:
		polyfit_anno(y, x, color='r')
	max_load = max(dic_fwd_orw.iterkeys(), key=(lambda key: dic_fwd_orw[key]))
	y = pl.arange(1, 3600)
	pl.plot(y, y/60.0, "k--")
	
	#only relays
	x, y = exclu_dict(dic_fwd_orw, die_orw_time, dir_orw)
	polyfit_anno(y, x, color='b')
	

	#ctp
	die_ctp_time = {k:die_ctp[k][1] for k in die_ctp}
	x, y = common_dict(dic_fwd_ctp, die_ctp_time)
	pl.scatter(y.values(), x.values(), color='#FFBF00', marker='x', label='ctp')
	#only direc neighbour
	xx, _ = common_dict(dic_fwd_ctp, dir_ctp)
	x, y = common_dict(xx, die_ctp_time)
	pl.scatter(y.values(), x.values(), color='#00FF00', marker='D', label='ctp_direct_nb')
	leg = pl.legend()
	leg.get_frame().set_alpha(0.5)
	pl.axis([0, ax.get_xlim()[1], 0, ax.get_ylim()[1]])
	pl.title("Energy limit =" + hex(ELIMIT))
	pl.ylabel('# of Transmit')
	pl.xlabel('survive time (s)')
	pl.savefig(folder + "load_lifetime.png")


	########figure of neighbour and lifetime########
	pl.figure()
	ax=pl.gca()
	#orw
	
	x, y = common_dict(num_neighbour_orw, die_orw_time)
	pl.scatter(x.values(), y.values(), label='orw')
	

	#only direc neighbour
	xx, _ = common_dict(num_neighbour_orw, dir_load_orw)
	x, y = common_dict(xx, die_orw_time)
	pl.scatter(x.values(), y.values(), color='#FF0000', marker='v', label='orw_direct_nb')
	
	x, y = exclu_dict(num_neighbour_orw, die_orw_time, dir_load_orw)
	polyfit_anno(x, y, color='b')
	
	#ctp
	
	x, y = common_dict(num_neighbour_ctp, die_ctp_time)
	pl.scatter(x.values(), y.values(), color='#FFBF00', marker='x', label='ctp')
	#only direc neighbour
	xx, _ = common_dict(num_neighbour_ctp, dir_load_ctp)
	x, y = common_dict(xx, die_ctp_time)
	pl.scatter(x.values(), y.values(), color='#00FF00', marker='D', label='ctp_direct_nb')
	pl.xlabel('# of p & c')
	pl.ylabel('survive time (s)')
	leg = pl.legend(loc=7)
	leg.get_frame().set_alpha(0.5)
	pl.axis([0, ax.get_xlim()[1], 0, ax.get_ylim()[1]])
	pl.title("Energy limit =" + hex(ELIMIT))
	pl.savefig(folder + "neighbour_lifetime.png")
	
	'''########3D figure of neighbour and lifetime and load########
	fig = pl.figure()
	ax = pl.axes(projection='3d')
	
	x, y = common_dict(num_neighbour_orw, dic_fwd_orw)
	y, z = common_dict(y, die_orw_time)
	x, _ = common_dict(x, z)
	ax.scatter(x.values(), y.values(), z.values())
	ax.set_xlabel('# of neighbour')
	ax.set_ylabel('# of Transmitions')
	ax.set_zlabel('Time')
	pl.savefig(folder + '3D.png')'''
	

