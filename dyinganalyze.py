import matplotlib
import tools.reader as reader
import numpy as np
import array
import networkx as nx
import pylab as pl
from tools.functions import *
from tools import command
import sys
from tools.constant import *
from tools.functions import update_progress
from tools import calprop
import math
from collections import defaultdict
from numpy import mean
import cPickle
'''
resultc = command.main(sys.argv[1:])
FileDict, props = command.getfile(resultc)
CtpDebugMsgs = FileDict['CtpDebug']
OrwDebugMsgs = FileDict['OrwDebug']
OrwNtMsgs = FileDict['OrwNt']
'''
font = {'size'   : 17}
SINK_ID = 1

matplotlib.rc('font', **font)
FileNames = {'OrwDebug':('26108.dat',), 'CtpDebug':('26102.dat',), 
	             'CtpData':('24463.dat',), 'ConnectDebug':('25593.dat',),
	             'OrwNt':('23738.dat',)}
#base_path = '/home/nagatoyuki/Thesis/Traces/Indriya/'
base_path = '/media/Data/ThesisData/Indriya/'
#elimit=1000
#files_ctp = ["data-50305","data-49912", "data-49283"]
#elimit=2000
#files_ctp = [ "data-49991", "data-49272", ]
#elimit=1000, mod3
#files_ctp = [ "data-49766","data-50271", "data-50317"]
#elimit=1000, density=29
SINK_ID = 136
#files_ctp = [ "data-50231","data-50234", "data-50237"] 
files_ctp = ["data-50225","data-50557", "data-50573"] 

numfiles = len(files_ctp)

#diemark = [98.5, int(99*0.75)+0.5, int(99*0.5)+0.5, int(99*0.25)+0.5]
diemark = [28.5, int(29*0.75)+0.5, int(29*0.5)+0.5, int(29*0.25)+0.5]
############   processing CTP   ############
die_order_ctp = defaultdict(dict)
total_count_ctp = [[] for i in range(0, numfiles)]
connect_count_ctp = [[] for i in range(0, numfiles)]
die_time_ctp = [[] for i in range(0, numfiles)]


for i, logfile in enumerate(files_ctp):
	'''
	if i == 0:
		FileNames['OrwDebug'] = ('23739.dat',)
		FileNames['CtpDebug'] = ('26099.dat',)
	else:
		FileNames['OrwDebug'] = ('26108.dat',)
		FileNames['CtpDebug'] = ('26102.dat',)
	'''
	CtpDebugMsgs  = reader.loadDebug(base_path+logfile, FileNames['CtpDebug'])
	#first iteration: construct the network connectivity graph
	G_ctp = nx.Graph()
	for msg in CtpDebugMsgs:
		if msg.type == NET_C_FE_SENT_MSG or msg.type == NET_C_FE_FWD_MSG:
			G_ctp.add_edge(msg.node, msg.dbg__c)
	total_connected = len(nx.shortest_path(G_ctp,SINK_ID)) - 1
	total_count_ctp[i].append(total_connected)
	connect_count_ctp[i].append(total_connected)
	die_time_ctp[i].append(0)
	connect_list = nx.shortest_path(G_ctp,SINK_ID)
	print "Total connected nodes: {:3d}".format(total_connected)
	
	#Then remove the node one by one
	for msg in CtpDebugMsgs:
		if msg.type == NET_C_DIE:
			if msg.node != 15 and msg.node in connect_list:
				if msg.node not in die_order_ctp[i]:
					sec = msg.timestamp / 1000.0 / 60.0
					die_order_ctp[i][msg.node] = sec
					die_time_ctp[i].append(sec)
					G_ctp.remove_node(msg.node)
					curr_connected = len(nx.shortest_path(G_ctp,SINK_ID)) - 1
					connect_count_ctp[i].append(curr_connected)
					total_connected -= 1
					total_count_ctp[i].append(total_connected)


print die_order_ctp[0]
fig = pl.figure()
ax = fig.add_subplot(1,1,1)
minlength = min(len(v) for k, v in die_order_ctp.iteritems())

templist=[]
for v in die_time_ctp:
	templist.append(v[0:minlength+1]) 

mean_time_ctp =  mean(templist, axis = 0)

std_time_ctp = np.std(templist, axis = 0)
for mark in diemark:
	index1 = total_count_ctp[0].index(closest(mark, total_count_ctp[0])) 
	index2 = connect_count_ctp[0].index(closest(mark, connect_count_ctp[0])) 
	print "{:7d}%{:7.2f}{:7.2f}".format(index1, mean_time_ctp[index1], std_time_ctp[index1])
	print "{:7d}%{:7.2f}{:7.2f}".format(index2, mean_time_ctp[index2], std_time_ctp[index2])


x = mean_time_ctp
y = total_count_ctp[0]
print len(x), len(y), len(std_time_ctp)
ax.plot(x, y)
ax.errorbar(x, y, xerr=std_time_ctp, fmt='bD', label="CTP")

fig2 = pl.figure(figsize=(8.8,6.6))
ax2 = fig2.add_subplot(1,1,1)
ax2.step(x, y, 'bv', where='post', alpha=0.6, markersize=11 , label='ctp, all nodes')
ax2.step(x, connect_count_ctp[0], 'bo', where='post', alpha=0.6, markersize=11, label='ctp, connected nodes')



############   processing ORW   ############
#elmit=0x1000
#files_orw = [ "data-50306","data-49953", "data-49278",]
#elmit=0x2000
#files_orw = [ "data-49997" ,"data-49273"] 
#el=1000, mod3
#files_orw = [ "data-49755","data-50272", "data-50318"] 
#el=1000, same density 29
files_orw = [ "data-50226","data-50547", "data-50572"] 

die_order_orw = defaultdict(dict)
total_count_orw = [[] for i in range(0, numfiles)]
connect_count_orw = [[] for i in range(0, numfiles)]
die_time_orw = [[] for i in range(0, numfiles)]


for i, logfile in enumerate(files_orw):
	'''
	if i == 0:
		FileNames['OrwDebug'] = ('23739.dat',)
		FileNames['CtpDebug'] = ('26099.dat',)
	else:
		FileNames['OrwDebug'] = ('26108.dat',)
		FileNames['CtpDebug'] = ('26102.dat',)
	'''
	OrwDebugMsgs  = reader.loadDebug(base_path+logfile, FileNames['OrwDebug'])
	#first iteration: construct the network connectivity graph
	G_orw = nx.Graph()
	for msg in OrwDebugMsgs:
		if msg.type == NET_C_FE_RCV_MSG:
			G_orw.add_edge(msg.node, msg.dbg__c)
	total_connected = len(nx.shortest_path(G_orw,SINK_ID)) - 1
	total_count_orw[i].append(total_connected)
	connect_count_orw[i].append(total_connected)
	die_time_orw[i].append(0)
	connect_list = nx.shortest_path(G_orw,SINK_ID)
	print "Total connected nodes: {:3d}".format(total_connected)
	
	#Then remove the node one by one
	for msg in OrwDebugMsgs:
		if msg.type == NET_C_DIE:
			if msg.node != 15 and msg.node in connect_list:
				if msg.node not in die_order_orw[i]:
					sec = msg.timestamp / 1000.0 / 60.0
					die_order_orw[i][msg.node] = sec
					die_time_orw[i].append(sec)
					G_orw.remove_node(msg.node)
					curr_connected = len(nx.shortest_path(G_orw,SINK_ID)) - 1
					connect_count_orw[i].append(curr_connected)
					total_connected -= 1
					total_count_orw[i].append(total_connected)

minlength = min(len(v) for k, v in die_order_orw.iteritems())

templist=[]
for v in die_time_orw:
	templist.append(v[0:minlength+1])


mean_time_orw =  mean(templist, axis = 0)

std_time_orw = np.std(templist, axis = 0)


for mark in diemark:
	index1 = total_count_orw[0].index(closest(mark, total_count_orw[0]))
	index2 = connect_count_orw[0].index(closest(mark, connect_count_orw[0]))
	print "{:7d}%{:7.2f}{:7.2f}".format(index1, mean_time_orw[index1], std_time_orw[index1])
	print "{:7d}%{:7.2f}{:7.2f}".format(index2, mean_time_orw[index2], std_time_orw[index2])

x = mean_time_orw
y = total_count_orw[0]
print connect_count_orw[0]
print total_count_orw[0]
print len(x), len(y), len(std_time_orw)
ax.plot(x, y, 'g')
'''
ax.plot((0,80),(7,7), 'r--', label='75%')
ax.plot((0,80), (14, 14), 'b--', label='50%')
ax.plot((0,80),(21,21), 'g--', label='25%')
'''
ax.plot((0,80),(7, 7), 'r--')
ax.text(20, 7, '25%', color ='r', ha="center", va="center",bbox = dict(ec='1',fc='1'))
ax.plot((0,80), (14, 14), 'b--')
ax.text(20, 14, '50%', color ='b', ha="center", va="center",bbox = dict(ec='1',fc='1'))
ax.plot((0,80),(21, 21), 'g--')
ax.text(20, 21, '75%', color ='g', ha="center", va="center",bbox = dict(ec='1',fc='1'))
ax.errorbar(x, y, xerr=std_time_orw, fmt='go', label='ORW')
limits = ax.axis()
ax.set_xlim([10,limits[1]])
ax.set_ylim([0,limits[3]])
ax.set_xlabel("Time (min)")
ax.set_ylabel("# Surviving Nodes")
ax.legend()
fig.tight_layout()

ax2.step(x, y, 'gv', where='post', alpha=0.6, markersize=11, label='orw, all nodes')
ax2.step(x, connect_count_orw[0], 'go', where='post', alpha=0.6, markersize=11, label='orw, connected nodes')
ax2.set_xlabel("Time (min)")
ax2.set_ylabel("# Surviving nodes")


fig2.tight_layout()
ax2.plot((0,80),(7, 7), 'r--')
ax2.text(70, 7, '25%', color ='r', ha="center", va="center",bbox = dict(ec='1',fc='1'))
ax2.plot((0,80), (14, 14), 'b--')
ax2.text(70, 14, '50%', color ='b', ha="center", va="center",bbox = dict(ec='1',fc='1'))
ax2.plot((0,80),(21, 21), 'g--')
ax2.text(70, 21, '75%', color ='g', ha="center", va="center",bbox = dict(ec='1',fc='1'))
limits = ax2.axis()
ax2.set_xlim([10,limits[1]])
ax2.set_ylim([0,limits[3]])
leg = ax2.legend(loc=0, prop={'size':15})
leg.get_frame().set_alpha(0.5)
'''
f = open("temp1.dat", "ab+")

cPickle.dump(mean_time_ctp, f)
cPickle.dump(connect_count_ctp[0], f)
cPickle.dump(total_count_ctp[0], f)
cPickle.dump(mean_time_orw, f)
cPickle.dump(connect_count_orw[0], f)
cPickle.dump(total_count_orw[0], f)

f.close()'''
pl.show()
