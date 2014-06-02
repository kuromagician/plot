#!/usr/bin/python

import matplotlib
import tools.reader as reader
import numpy as np
import array
import networkx as nx
import pylab as pl
from matplotlib.pyplot import pause
from matplotlib import animation

pl.ion()

path = '/home/nagatoyuki/Desktop/Thesis/Indriya/data-47398'
fileNames = ('23739.dat',)

SINK_ID = 1
#type constant
NET_C_FE_SENT_MSG = 0x20        #:app. send       :msg uid, origin, next_hop
NET_C_FE_RCV_MSG =  0x21        #:next hop receive:msg uid, origin, last_hop
NET_C_FE_FWD_MSG =  0x22        #:fwd msg         :msg uid, origin, next_hop
NET_C_FE_DST_MSG =  0x23        #:base app. recv  :msg_uid, origin, last_hop 
NET_C_DIE		= 0x71

debugMsgs = reader.loadDebug(path, fileNames)

fig = pl.figure(figsize=[10,10])
G = nx.Graph()
node_w = {}
die_orw = {}
direct_nb_orw = set()

for msg in debugMsgs:
	G.add_node(msg.node)
	#if type is receive, record every edge that appears
	if msg.type == NET_C_FE_RCV_MSG:
		#Network graph construction
		if G.has_edge(msg.dbg__c, msg.node):
			G[msg.dbg__c][msg.node]['weight'] += 1
		else:
			G.add_edge(msg.dbg__c, msg.node, weight = 1)
		if(msg.node == SINK_ID):
			direct_nb_orw.add(msg.dbg__c)
	elif msg.type == NET_C_DIE:
		die_orw[msg.node] = msg.dbg__b
		
sorted_die_orw = sorted(die_orw.iteritems(), key=lambda (k,v): v)
#print sorted_die_orw

pos = nx.graphviz_layout(G)
nodelist = G.nodes()
init_func = nx.draw_networkx_nodes(G, pos, node_size = 150)


limit = pl.gca().axis()
print limit
#nx.draw_networkx_nodes(G, pos, node_size = 150, node_color='b')
#nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='r')
#nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=direct_nb_orw, node_color='y')
#pl.savefig('test.png')

def update_fig(i):
	pl.clf()
	ax = pl.gca()
	nx.draw_networkx_nodes(G, pos, init_func=init_func, nodelist=nodelist[i:len(nodelist)], node_size = 150, node_color='b')
	nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='r')
	nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=set(direct_nb_orw) & set(nodelist[i:len(nodelist)]), node_color='y')
	ax.set_xlim([limit[0], limit[1]])
	ax.set_ylim([limit[2], limit[3]])
	ax.set_autoscale_on(False)
	

#for (x,y) in sorted_die_orw:
#	update_fig(x)
#	pause(0.1)
anim = animation.FuncAnimation(fig, update_fig, frames=len(sorted_die_orw), interval=20, blit=True)

anim.save('a.mp4', fps=5)
pl.show()
#pl.draw()
#pl.savefig('test.png')
#pause(5)