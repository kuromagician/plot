#!/usr/bin/python

import matplotlib
import tools.reader as reader
import numpy as np
import array
import networkx as nx
import pylab as pl
from matplotlib.pyplot import pause
from matplotlib import animation
#from tools.functions import *
from tools import command
import sys
from tools.constant import *
from tools.functions import update_progress
from tools import calprop

result = command.main(sys.argv[1:])
FileDict, props = command.getfile(result)
cal_prop_orw = calprop.prop_orw(FileDict, result)
cal_prop_ctp = calprop.prop_ctp(FileDict, result)
SINK_ID = props['SINK_ID']
#actual parsed files
OrwDebugMsgs = FileDict['OrwDebug']
CtpDebugMsgs = FileDict['CtpDebug']
time_ratio = props['timeratio']
#set of 3 classes
DN_orw = cal_prop_orw['Dir_Neig']
RL_orw = cal_prop_orw['Relay']
LF_orw = cal_prop_orw['Leaf']
DN_ctp = cal_prop_ctp['Dir_Neig']
RL_ctp = cal_prop_ctp['Relay']
LF_ctp = cal_prop_ctp['Leaf']
end_time = 200
fps=30

def update_fig(i, args, G, pos, line):
	global counter
	progress = i*100/(end_time-1)
	text = 'Creating animation: '
	update_progress(text, progress)
	#ax2.cla()
	if i in sorted_die_time:
		#clear figure
		ax1.cla()
		#ax1 = pl.gca()[0]
		curr_node = sorted_die_node[counter]
		counter += 1
		#remove the dead nodes
		G.remove_node(curr_node)
		nodelist.discard(curr_node)
		
		nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='k', ax=ax1)
		nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=args[0] & nodelist, node_color='b', ax=ax1)
		nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=args[1] & nodelist, node_color='r', ax=ax1)
		nodes = nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=args[2] & nodelist, node_color='g', ax=ax1)
		nx.draw_networkx_edges(G, pos, nodelist=nodelist, width=0.5, alpha=0.5, ax=ax1)
		ax1.set_xlim([limit[0], limit[1]])
		ax1.set_ylim([limit[2], limit[3]])
	line.set_data([i, i], [0, 100])
	return ax1, line
		

###########################################################
######################      ORW      ######################
'''
fig = pl.figure(figsize=[10,10])
G_orw = nx.Graph()
node_w = {}
die_orw = {}

#create orw network graph
for msg in OrwDebugMsgs:
	if msg.node <=300:
		#if type is receive, record every edge that appears
		if msg.type == NET_C_FE_RCV_MSG:
			G_orw.add_node(msg.node)
			if msg.dbg__c <= 300:
				#Network graph construction
				if G_orw.has_edge(msg.dbg__c, msg.node):
					G_orw[msg.dbg__c][msg.node]['weight'] += 1
				else:
					G_orw.add_edge(msg.dbg__c, msg.node, weight = 1)
		elif msg.type == NET_C_DIE:
			G_orw.add_node(msg.node)
			die_orw[msg.node] = int(round(msg.timestamp/time_ratio))
		
sorted_die_orw = sorted(die_orw.iteritems(), key=lambda (k,v): v)
sorted_die_node = [k for (k,v) in sorted_die_orw]
sorted_die_time = [v for (k,v) in sorted_die_orw]
print sorted_die_time

pos_orw = nx.graphviz_layout(G_orw, root=SINK_ID)
nodelist = set(G_orw.nodes())
print "ORW:", len(DN_orw)+len(RL_orw)+len(RL_orw), len(nodelist)

G = G_orw
pos = pos_orw
nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='k')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=DN_orw & nodelist, node_color='b')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=RL_orw & nodelist, node_color='r')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=LF_orw & nodelist, node_color='g')
nx.draw_networkx_edges(G, pos, nodelist=nodelist, width=0.5, alpha=0.5)

#nx.draw(G_orw, pos_orw)
limit = pl.gca().axis()
sets = (DN_orw, RL_orw, LF_orw)

counter=0
#end_time = sorted_die_time[-1]+30
anim = animation.FuncAnimation(fig, update_fig, frames=end_time, fargs=[sets, G_orw, pos_orw], blit=True)
anim.save('orw.mp4', fps=fps)
'''

###########################################################
######################      CTP      ######################

fig = pl.figure(figsize=(8,10))
ax1 = pl.subplot2grid((5,4), (0,0), colspan=4, rowspan=4)
G_ctp = nx.Graph()
node_w = {}
die_ctp = {}
#create ctp network graph
for msg in CtpDebugMsgs:
	if msg.node <=300:
		#if type is receive, record every edge that appears
		if msg.type == NET_C_FE_SENT_MSG:
			G_ctp.add_node(msg.node)
			#if msg.dbg__c <= 300:
			#Network graph construction
			if G_ctp.has_edge(msg.node, msg.dbg__c):
				G_ctp[msg.node][msg.dbg__c]['weight'] += 1
			else:
				G_ctp.add_edge(msg.node, msg.dbg__c, weight = 1)
		elif msg.type == NET_C_FE_FWD_MSG:
			G_ctp.add_node(msg.node)
			if G_ctp.has_edge(msg.node, msg.dbg__c):
				G_ctp[msg.node][msg.dbg__c]['weight'] += 1
			else:
				G_ctp.add_edge(msg.node, msg.dbg__c, weight = 1)
		elif msg.type == NET_C_DIE:
			G_ctp.add_node(msg.node)
			die_ctp[msg.node] = int(round(msg.timestamp/time_ratio))
		
sorted_die_ctp = sorted(die_ctp.iteritems(), key=lambda (k,v): v)
sorted_die_node = []
sorted_die_time = []
for (k,v) in sorted_die_ctp:
	sorted_die_node.append(k)
	sorted_die_time.append(v)
print sorted_die_time

pos_ctp = nx.graphviz_layout(G_ctp, root=SINK_ID)
nodelist = set(G_ctp.nodes())
print "CTP:", len(DN_ctp)+len(RL_ctp)+len(RL_ctp), len(nodelist)


G = G_ctp
pos = pos_ctp
sets = (DN_ctp, RL_ctp, LF_ctp)
nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='k')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=DN_ctp & nodelist, node_color='b')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=RL_ctp & nodelist, node_color='r')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=LF_ctp & nodelist, node_color='g')
nx.draw_networkx_edges(G, pos, nodelist=nodelist, width=0.5, alpha=0.5)
limit = ax1.axis()

ax2 = pl.subplot2grid((5,4), (4,0), colspan=4, xlim=(0, 300), ylim=(-2, 100))
timeline, = ax2.plot((0,0), (0, 100), 'k-')

counter=0
#end_time = sorted_die_time[-1]+30
anim = animation.FuncAnimation(fig, update_fig, frames=end_time, fargs=[sets, G_ctp, pos_ctp, timeline], blit=True)
anim.save('ctp.mp4', fps=fps)

#nx.draw(G_ctp, pos_ctp)

#pl.show()
