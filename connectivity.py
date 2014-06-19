#!/usr/bin/python

import tools.reader as reader
import matplotlib
import pylab as pl
from collections import defaultdict
import itertools
import networkx as nx
from networkx.algorithms.components.connected import connected_components
from numpy import mean
import tools.command as command
from tools.constant import *
import sys


#############################################################
'''

base_path = '/home/nagatoyuki/Desktop/Thesis/Indriya/'
#folder = 'data-48224/'
folder = 'data-48413/'
filenames = ('25593.dat',)


#############################################################


CMsgs = reader.load_C_Data(base_path+folder, filenames)

statics = {}
G = nx.Graph()

for i in xrange(1, 300):
	statics[i] = defaultdict(int)

node_above_100 = set()
Others = set()
for msg in CMsgs:
	if msg.node > 100:
		node_above_100.add(msg.node)
	else:
		#Others.add(msg.node)
		pass
	statics[msg.node][msg.source] += 1
#print statics[20]
#print statics[75]	
for node, neighbour_list in statics.iteritems():
	for nid, num in neighbour_list.iteritems():
		if node in node_above_100:
			G.add_node(node)
		if num >= 45 :
			if node>100 and nid < 100:
			#if True:#(msg.node in [20,75]):
			#print "Node{} has perfect neighbour {}".format(node, nid)
			#if node > 100:
				Others.add(nid)
				G.add_edge(node, nid)
			
pos = nx.graphviz_layout(G)
nodelist = G.nodes()
#print connected_components(G)
labels={}

pl.figure()
for node in node_above_100.union(Others):
	labels[node] = node
nx.draw_networkx_nodes(G, pos, node_size = 120, nodelist=node_above_100, node_color='r')
nx.draw_networkx_nodes(G, pos, node_size = 120, nodelist=Others, node_color='g')
#nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[20,75], node_color='b')
nx.draw_networkx_edges(G, pos, alpha=0.5)
nx.draw_networkx_labels(G,pos, labels=labels, font_size=6)
pl.savefig("connectivity.pdf")'''
################################################ABOVE IS CONNECTIVITY################################
fig = pl.figure(figsize=[10,10])
result = command.main(sys.argv[1:])
FileDict, props = command.getfile(result)
CtpDebugMsgs = FileDict['CtpDebug']
OrwDebugMsgs = FileDict['OrwDebug']
time_ratio = props['timeratio']
#open a file for logging 
fo = open("logging.txt", "a+")
if result['postpone']:
	time_TH = 10*time_ratio*60
else:
	time_TH = -1

###################################   ORW   ######################################
ax3 = pl.subplot2grid((2,5), (1,0), colspan=4)#, sharex=ax1, sharey=ax1)
G_orw = nx.Graph()
#10 minutes later we start collect data


load_counter = defaultdict(int)
for msg in OrwDebugMsgs:
	if msg.timestamp >= time_TH: 
		G_orw.add_node(msg.node)
		if msg.type == NET_C_FE_RCV_MSG:
			G_orw.add_edge(msg.dbg__c, msg.node)
			load_counter[(msg.dbg__c, msg.node)] += 1

edgewidth=[]
VIP_edges = []
nodelist_orw = G_orw.nodes()

#print sorted(pos.keys())
real_load = {}
for t, v in load_counter.items():
	s = t[0]
	d = t[1]
	if s < d:
		real_load[(s, d)] = load_counter[(s, d)] + load_counter[(d, s)]
	else:
		real_load[(d, s)] = load_counter[(s, d)] + load_counter[(d, s)]

mean_load = mean(real_load.values())
sortedload_orw = sorted(real_load.values(), reverse=True)
max_value = max(real_load.values())
NumOfLinks_orw = len(real_load)
logmsg = "Average load per link:{:6.2f}, number of links:{:5d}, total load:{:.2f}".format(mean_load, NumOfLinks_orw, NumOfLinks_orw*mean_load)
print logmsg
logmsg = "{:10s}\t{:6.2f}\t{:4d}\t{:6.0f}\t{:8s}\t{}\n".\
          format(props['prefix'], mean_load, NumOfLinks_orw, 
		         NumOfLinks_orw*mean_load, props['energy'], result['connected'])
#print logmsg
fo.write(logmsg)


for (u,v) in G_orw.edges():
	if u > v:
		u, v = v, u
	edge_weight = real_load[(u,v)]
	if load_counter[(u, v)] != 0 and load_counter[(v, u)]!= 0:
		pass
		#print "Parent Changed!{} {}".format(u, v)
		#print load_counter[(u, v)], load_counter[(v, u)] 
	if edge_weight > mean_load:
		edgewidth.append(edge_weight*10.0/max_value)
		VIP_edges.append((u, v))

pos = nx.graphviz_layout(G_orw, root=props['SINK_ID'])
labels = {}
print "Length of pos:", len(pos)
print "Number of nodes:", len(G_orw.nodes())
for node in pos.keys():
	labels[node] = node
#nx.draw_networkx_edges(G_orw, pos)
nx.draw_networkx_edges(G_orw, pos, alpha=0.3, width=edgewidth, edge_color='m', edgelist=VIP_edges)
#nx.draw_networkx_edges(G_orw, pos, width=0.3, edge_color='k', edgelist=VIP_edges)
nx.draw_networkx_nodes(G_orw, pos , nodelist=pos.keys(), node_size=75)
nx.draw_networkx_labels(G_orw, pos, labels=labels, font_size=5)


ax4 = pl.subplot2grid((2,5), (1,4), colspan=1)
bp = ax4.boxplot(load_counter.values())
#print bp['caps'][0].get_data()
ax4.plot(1, mean_load, marker='*', color='r')
ax4.annotate("Average:{:.2f}".format(mean_load), textcoords = 'offset points', size=10, color='r',
								xy = (1, mean_load), xytext = (0, 0), ha='center')
ax4.annotate("MAX:{}".format(max_value), textcoords = 'offset points', size=10, color='r',
								xy = (1, max_value), xytext = (0, 0), ha='center')
								

###################################   CTP   ######################################
ax1 = pl.subplot2grid((2,5), (0,0), colspan=4, sharex=ax3, sharey=ax3)
G_ctp = nx.Graph()
load_counter = defaultdict(int)
VIP_edges = []
RealLink_ctp = defaultdict(list)

for msg in CtpDebugMsgs:
	if msg.timestamp >= time_TH: 
		G_ctp.add_node(msg.node)
		if msg.type == NET_C_FE_SENT_MSG:
			G_ctp.add_edge(msg.node, msg.dbg__c)
			load_counter[(msg.node, msg.dbg__c)] += 1
		elif msg.type == NET_C_FE_FWD_MSG:
			G_ctp.add_edge(msg.node, msg.dbg__c)
			load_counter[(msg.node, msg.dbg__c)] += 1

edgewidth=[]
labels={}
#pos = nx.graphviz_layout(G_ctp, root=props['SINK_ID'])
print "Length of pos:", len(pos)
print "Number of nodes:", len(G_ctp.nodes())
real_load={}
for t, v in load_counter.items():
	s = t[0]
	d = t[1]
	if s < d:
		real_load[(s, d)] = load_counter[(s, d)] + load_counter[(d, s)]
	else:
		real_load[(d, s)] = load_counter[(s, d)] + load_counter[(d, s)]
	'''if statics[s][d] ==0 and statics[d][s] == 0:
		print "Link:", s, " -> ", d, "doesn't have connection"
		print statics[s]
		print statics[d]'''
'''	RealLink_ctp[s].append(max(statics[s][d], statics[d][s])/50.0)
	
for node in RealLink_ctp:
	print "Node ", node, "MIN QUALITY: ", RealLink_ctp[node]'''
mean_load = mean(real_load.values())
sortedload_ctp = sorted(real_load.values(), reverse=True)
max_value = max(real_load.values())
NumOfLinks_ctp = len(real_load)
logmsg = "Average load per link:{:5.2f}, number of links:{:5d}, total load:{:.2f}".format(mean_load, NumOfLinks_ctp, NumOfLinks_ctp*mean_load)
print logmsg
#fo.write("{}{} when CONNECTIVITY is {}\n".format(props['prefix'], 'CTP', result['connected']))
#fo.write(logmsg + "\n")

logmsg = "{:10s}\t{:6.2f}\t{:4d}\t{:6.0f}\t{:8s}\t{}\n".\
          format(props['prefix'], mean_load, NumOfLinks_ctp, 
                 NumOfLinks_ctp*mean_load, props['energy'], result['connected'])
#print logmsg
fo.write(logmsg)
fo.close()

for (u,v) in G_ctp.edges():
	if u > v:
		u, v = v, u
	edge_weight = real_load[(u,v)]
	if edge_weight > mean_load:
		edgewidth.append(edge_weight*10.0/max_value)
		VIP_edges.append((u, v))

#pos = nx.graphviz_layout(G_ctp, root=props['SINK_ID'])
for node in G_ctp.nodes():
	labels[node] = node
#nx.draw_networkx_edges(G_ctp, pos)
nx.draw_networkx_edges(G_ctp, pos, width=0.3, edge_color='k', edgelist=VIP_edges)
nx.draw_networkx_edges(G_ctp, pos, alpha=0.3, width=edgewidth, edge_color='m', edgelist=VIP_edges)

nx.draw_networkx_nodes(G_ctp, pos, node_size=75)
nx.draw_networkx_labels(G_ctp, pos, labels=labels, font_size=5)

ax2 = pl.subplot2grid((2,5), (0,4), colspan=1)
ax2.boxplot(load_counter.values())
ax2.plot(1, mean_load, marker='*', c='r')
ax2.annotate("Average:{:.2f}".format(mean_load), textcoords = 'offset points', size=10, color='r',
								xy = (1, mean_load), xytext = (0, 0), ha='center')
ax2.annotate("MAX:{}".format(max_value), textcoords = 'offset points', size=10, color='r',
								xy = (1, max_value), xytext = (0, 0), ha='center')

limits = ax1.axis()
ax1.set_ylim([0, limits[3]])
ax1.set_xlim([0, limits[1]])

fig.savefig("networkbond.pdf", bbox_inches='tight')

fig = pl.figure()
ax1 = fig.add_subplot(1,1,1)
y = sortedload_ctp
length = len(y)
JI_ctp = sum(y)**2*1.0/length/sum(k**2 for k in y)

ax1.fill_between(xrange(0, len(y)), 0, y, alpha=0.5)
ax1.annotate("CTP:{}".format(length), xy=(length, 0), xytext=(length, 200),
            arrowprops=dict(width=0.5, headwidth=1.5), ha='center'
            )
y = sortedload_orw

length = len(y)

JI_orw = sum(y)**2*1.0/length/sum(k**2 for k in y)
ax1.fill_between(xrange(0, len(y)), 0, y, alpha=0.5, color='r')
ax1.set_ylabel('Link Load')
ax1.set_xlabel('Link Index')
#ax1.annotate("ORW:{}".format(length), textcoords = 'offset points', size=10,
#								xy = (length, -2), xytext = (0, 0), ha='center')
ax1.annotate("ORW:{}".format(length), xy=(length, 0), xytext=(length, 200),
            arrowprops=dict(width=0.5, headwidth=1.5), ha='center'
            )
            
print "JI CTP:", JI_ctp
print "JI ORW:", JI_orw

limits = ax1.axis()
ax1.set_ylim([0, limits[3]])
ax1.set_xlim([0, limits[1]])
pl.show()







