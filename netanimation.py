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
#actual parsed files
OrwDebugMsgs = FileDict['OrwDebug']
CtpDebugMsgs = FileDict['CtpDebug']
#set of 3 classes
DN_orw = cal_prop_orw['Dir_Neig']
RL_orw = cal_prop_orw['Relay']
LF_orw = cal_prop_orw['Leaf']
DN_ctp = cal_prop_ctp['Dir_Neig']
RL_ctp = cal_prop_ctp['Relay']
LF_ctp = cal_prop_ctp['Leaf']

def update_fig(i, args, G, pos):
	#clear figure
	fig.clf()
	ax = pl.gca()
	livenodes = set(nodelist) - set(sorted_die_node[0:i])
	nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='k')
	nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=args[0] & livenodes, node_color='b')
	nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=args[1] & livenodes, node_color='r')
	nodes = nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=args[2] & livenodes, node_color='g')
	nx.draw_networkx_edges(G, pos, nodelist=livenodes, width=0.5, alpha=0.5)
	ax.set_xlim([limit[0], limit[1]])
	ax.set_ylim([limit[2], limit[3]])
	ax.set_autoscale_on(False)
	#return edges

###########################################################
######################      ORW      ######################

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
			die_orw[msg.node] = msg.dbg__b
		
sorted_die_orw = sorted(die_orw.iteritems(), key=lambda (k,v): v)
sorted_die_node = [k for (k,v) in sorted_die_orw]

pos_orw = nx.graphviz_layout(G_orw, root=SINK_ID)
nodelist = G_orw.nodes()
print "ORW:", len(DN_orw)+len(RL_orw)+len(RL_orw), len(nodelist)

G = G_orw
pos = pos_orw
nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='k')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=DN_orw & set(nodelist), node_color='b')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=RL_orw & set(nodelist), node_color='r')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=LF_orw & set(nodelist), node_color='g')
edges = nx.draw_networkx_edges(G, pos, nodelist=nodelist, width=0.5, alpha=0.5)
limit = pl.gca().axis()
sets = (DN_orw, RL_orw, LF_orw)


anim = animation.FuncAnimation(fig, update_fig, frames=len(sorted_die_orw), \
                               fargs=[sets, G_orw, pos_orw], blit=True)
anim.save('orw.mp4', fps=3)

'''
###########################################################
######################      CTP      ######################

fig = pl.figure(figsize=(10,10))
G_ctp = nx.Graph()
node_w = {}
die_ctp = {}
#create ctp network graph
for msg in CtpDebugMsgs:
	if msg.node <=300:
		#if type is receive, record every edge that appears
		if msg.type == NET_C_FE_SENT_MSG:
			G_orw.add_node(msg.node)
			#if msg.dbg__c <= 300:
			#Network graph construction
			if G_ctp.has_edge(msg.node, msg.dbg__c):
				G_ctp[msg.node][msg.dbg__c]['weight'] += 1
			else:
				G_ctp.add_edge(msg.node, msg.dbg__c, weight = 1)
		elif msg.type == NET_C_FE_FWD_MSG:
			G_orw.add_node(msg.node)
			if G_ctp.has_edge(msg.node, msg.dbg__c):
				G_ctp[msg.node][msg.dbg__c]['weight'] += 1
			else:
				G_ctp.add_edge(msg.node, msg.dbg__c, weight = 1)
		elif msg.type == NET_C_DIE:
			G_orw.add_node(msg.node)
			die_ctp[msg.node] = msg.dbg__b
		
sorted_die_ctp = sorted(die_ctp.iteritems(), key=lambda (k,v): v)
sorted_die_node = [k for (k,v) in sorted_die_ctp]

pos_ctp = nx.graphviz_layout(G_ctp, root=SINK_ID)
nodelist = G_ctp.nodes()
print "CTP:", len(DN_ctp)+len(RL_ctp)+len(RL_ctp), len(nodelist)


nx.draw_networkx_nodes(G_ctp, pos_ctp)
limit = pl.gca().axis()
sets = (DN_ctp, RL_ctp, LF_ctp)
anim = animation.FuncAnimation(fig, update_fig, frames=len(sorted_die_ctp), fargs=[sets, G_ctp, pos_ctp], blit=True)
anim.save('ctp.mp4', fps=3)

#nx.draw(G_ctp, pos_ctp)
'''
#pl.show()
