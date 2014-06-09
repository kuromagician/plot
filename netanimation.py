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
from tools import calprop

result = command.main(sys.argv[1:])
FileDict, props = command.getfile(result)
cal_prop_orw = calprop.prop_orw(FileDict, result)
cal_prop_ctp = calprop.prop_ctp(FileDict, result)
SINK_ID = props['SINK_ID']
OrwDebugMsgs = FileDict['OrwDebug']
CtpDebugMsgs = FileDict['CtpDebug']


fig = pl.figure(figsize=[10,10])
G = nx.Graph()
node_w = {}
die_orw = {}
DN_orw = cal_prop_orw['Dir_Neig']
RL_orw = cal_prop_orw['Relay']
LF_orw = cal_prop_orw['Leaf']

for msg in OrwDebugMsgs:
	G.add_node(msg.node)
	#if type is receive, record every edge that appears
	if msg.type == NET_C_FE_RCV_MSG:
		#Network graph construction
		if G.has_edge(msg.dbg__c, msg.node):
			G[msg.dbg__c][msg.node]['weight'] += 1
		else:
			G.add_edge(msg.dbg__c, msg.node, weight = 1)
	elif msg.type == NET_C_DIE:
		die_orw[msg.node] = msg.dbg__b
		
sorted_die_orw = sorted(die_orw.iteritems(), key=lambda (k,v): v)
sorted_die_node = [k for (k,v) in sorted_die_orw]

pos = nx.graphviz_layout(G)
nodelist = G.nodes()
init_func = nx.draw_networkx_nodes(G, pos, node_size = 150)


limit = pl.gca().axis()
#print limit
#nx.draw_networkx_nodes(G, pos, node_size = 150, node_color='b')
#nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='r')
#nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=DN_orw, node_color='y')
#pl.savefig('test.png')

def update_fig(i, args, G):
	pl.clf()
	ax = pl.gca()
	livenodes = set(nodelist) - set(sorted_die_node[0:i])
	nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='k')
	nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=args[0] & livenodes, node_color='b')
	nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=args[1] & livenodes, node_color='r')
	nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=args[2] & livenodes, node_color='g')
	ax.set_xlim([limit[0], limit[1]])
	ax.set_ylim([limit[2], limit[3]])
	ax.set_autoscale_on(False)
	return ax

#for (x,y) in sorted_die_orw:
#	update_fig(x)
#	pause(0.1)
sets = (DN_orw, RL_orw, LF_orw)
anim = animation.FuncAnimation(fig, update_fig, frames=len(sorted_die_orw), fargs=[sets, G], blit=True)
anim.save('orw.mp4', fps=2)

#pl.show()