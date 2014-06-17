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
SN_orw = cal_prop_orw['Dir_Neig']
RL_orw = cal_prop_orw['Relay']
LF_orw = cal_prop_orw['Leaf']
SN_ctp = cal_prop_ctp['Dir_Neig']
RL_ctp = cal_prop_ctp['Relay']
LF_ctp = cal_prop_ctp['Leaf']
end_time = 9000
fps=60

def update_fig(i, args, G, pos, lineset):
	global counter
	progress = i*100/(end_time-1)
	text = 'Creating animation: '
	update_progress(text, progress)
	#ax2.cla()
	ly1 = y1[-1]
	ly2 = y2[-1]
	ly3 = y3[-1]
	if i in sorted_die_time:
		#clear figure
		ax1.cla()
		
		curr_node = sorted_die_node[counter]
		if curr_node in args[0]:
			ly1 += step1
		elif curr_node in args[1]:
			ly2 += step2
		elif curr_node in args[2]:
			ly3 += step3
		
		counter += 1
		#remove the dead nodes
		if curr_node in G.nodes():
			G.remove_node(curr_node)
		nodelist.discard(curr_node)
		
		ax1.set_xlim([limit[0], limit[1]])
		ax1.set_ylim([limit[2], limit[3]])
		ax1.set_axis_off()
		nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='k', ax=ax1)
		nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=args[0] & nodelist, node_color='b', ax=ax1)
		nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=args[1] & nodelist, node_color='r', ax=ax1)
		nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=args[2] & nodelist, node_color='g', ax=ax1)
		nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.5, ax=ax1)
		
		
	lineset[0].set_data([i, i], [0, 100])
	if i > 0:
		x=xrange(0, i+1)
		y1.append(ly1)
		y2.append(ly2)
		y3.append(ly3)
		lineset[1].set_data(x, y1)
		lineset[2].set_data(x, y2)
		lineset[3].set_data(x, y3)
	return ax1, lineset
		
'''
###########################################################
######################      ORW      ######################

fig = pl.figure(figsize=[10,10])
ax1 = pl.subplot2grid((5,4), (0,0), colspan=4, rowspan=4)
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
print "ORW:", len(SN_orw)+len(RL_orw)+len(RL_orw), len(nodelist)
unknown = nodelist - SN_orw - RL_orw - LF_orw
for node in unknown:
	if node != SINK_ID:
		G_orw.remove_node(node)

G = G_orw
pos = pos_orw
nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='k')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=SN_orw & nodelist, node_color='b')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=RL_orw & nodelist, node_color='r')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=LF_orw & nodelist, node_color='g')
nx.draw_networkx_edges(G, pos, nodelist=nodelist, width=0.5, alpha=0.5)

limit = ax1.axis()
ax1.set_axis_off()


#ax2 for die percentage
sets = (SN_orw, RL_orw, LF_orw)
ax2 = pl.subplot2grid((5,4), (4,0), colspan=4, xlim=(0, end_time), ylim=(-2, 100))
timeline, = ax2.plot((0,0), (0, 100), 'k-')
line_SN, = ax2.plot([0], [0], 'b-')
line_RL, = ax2.plot([0], [0], 'r-')
line_LF, = ax2.plot([0], [0], 'g-')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('%')
y1=[0]
y2=[0]
y3=[0]
step1=100.0/len(SN_orw)
step2=100.0/len(RL_orw)
step3=100.0/len(LF_orw)


lineset = [timeline, line_SN, line_RL, line_LF]

counter=0
#end_time = sorted_die_time[-1]+30
anim = animation.FuncAnimation(fig, update_fig, frames=end_time, fargs=[sets, G_orw, pos_orw, lineset], blit=True)
anim.save('orw.mp4', fps=fps, bitrate=4000, extra_args=['-vcodec', 'libx264'])

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
print "CTP:", len(SN_ctp)+len(RL_ctp)+len(LF_ctp), len(nodelist)
unknown = nodelist - SN_ctp - RL_ctp - LF_ctp

for node in unknown:
	if node != SINK_ID:
		G_ctp.remove_node(node)


G = G_ctp
pos = pos_ctp
sets = (SN_ctp, RL_ctp, LF_ctp)
nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='k')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=SN_ctp & nodelist, node_color='b')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=RL_ctp & nodelist, node_color='r')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=LF_ctp & nodelist, node_color='g')
nx.draw_networkx_edges(G, pos, nodelist=nodelist, width=0.5, alpha=0.5)
limit = ax1.axis()
ax1.set_axis_off()

ax2 = pl.subplot2grid((5,4), (4,0), colspan=4, xlim=(0, end_time), ylim=(-2, 100))
timeline, = ax2.plot((0,0), (0, 100), 'k-')
line_SN, = ax2.plot([0], [0], 'b-')
line_RL, = ax2.plot([0], [0], 'r-')
line_LF, = ax2.plot([0], [0], 'g-')
y1=[0]
y2=[0]
y3=[0]
step1=100.0/len(SN_ctp)
step2=100.0/len(RL_ctp)
step3=100.0/len(LF_ctp)


lineset = [timeline, line_SN, line_RL, line_LF]
#nodeset = [node_SN, node_RL, node_LF]
counter=0
#end_time = sorted_die_time[-1]+30
anim = animation.FuncAnimation(fig, update_fig, frames=end_time, fargs=[sets, G_ctp, pos_ctp, lineset], blit=True)
anim.save('ctp.mp4', fps=fps, bitrate=4000, extra_args=['-vcodec', 'libx264'])

#nx.draw(G_ctp, pos_ctp)

#pl.show()
