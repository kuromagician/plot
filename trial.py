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
import math

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
if result['simulation']:
	end_time = 252000
else:
	end_time = 10800
fps=60

time_ratio = props['timeratio']
if result['postpone']:
	time_TH = 60*time_ratio*10
else:
	time_TH = -1
def update_fig(i, args, G, pos, lineset, start_time):
	global counter
	progress = i*100/(end_time-1)
	text = 'Creating animation: '
	update_progress(text, progress)
	ly1 = y1[-1]
	ly2 = y2[-1]
	ly3 = y3[-1]
	#only reserve 5 secs
	if i > start_time:
		#ax2.cla()
		
		if i in sorted_die_time:
			#clear figure
			ax1.cla()
			die_list=[]
			
			while sorted_die_time[counter] == i:
				die_list.append(sorted_die_node[counter])
				counter += 1
			for curr_node in die_list:
				if curr_node in args[0]:
					ly1 += step1
				elif curr_node in args[1]:
					ly2 += step2
				elif curr_node in args[2]:
					ly3 += step3
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
		
def update_v2(G, pos, args, lineset, time, die_ratio):
	#args are node classes
	timetext = "Elasped Time: \n" + translatetime(time) 
	lineset[0], = ax3.plot([time, time], [0, 100])
	allnodes = G.nodes()
	nodelist=set(allnodes)
	color=('b', 'r', 'g')
	strings=('Sink neighbour', 'Relay', 'Leaf')
	SN = set()
	RL = set()
	LF = set()
	setlist=[SN, RL, LF]
	sinkplot = nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='k', ax=ax1)
	returnlist=[sinkplot]
	for i, s in enumerate(setlist):
		s = args[i] & nodelist
		if len(args[i]) != 0:
			percentage = 100.0*len(s)/len(args[i])
			temp = "\n{:15s}: {:.2f}%".format(strings[i], percentage)
			timetext += temp
		y[i+1].append(die_ratio[i][-1])
		x[i+1].append(time)
		lineset[i+1], = ax3.plot(x[i+1], y[i+1])
			
		if len(s) != 0:
			plotobj = nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=s, node_color=color[i], ax=ax1)
			returnlist.append(plotobj)
	edges = nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.5, ax=ax1)
	textobj = ax2.text(-0.7, 0.2, timetext, bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
	
	returnlist.append(textobj)
	returnlist.append(edges)
	for item in lineset:
		returnlist.append(item)
	return returnlist

def translatetime(time):
	hour = int(time/3600)
	minute = int((time - hour*3600)/60)
	sec = time - 3600*hour - 60*minute

	return "{:02d}:{:02d}:{:05.3f}".format(hour, minute, sec)
	


###########################################################
######################      ORW      ######################

fig = pl.figure(figsize=[8,10])
ax1 = pl.subplot2grid((5,4), (0,0), colspan=4, rowspan=4)
ax1.set_axis_off()


ax2 = pl.subplot2grid((5,4), (4,0), colspan=1, rowspan=1)
ax2.set_axis_off()


ax3 = pl.subplot2grid((5,4), (4,1), colspan=3, rowspan=1)
#ax3 for die percentage
sets = (SN_orw, RL_orw, LF_orw)

timeline, = ax3.plot((0,0), (0, 100), 'k-')
line_SN, = ax3.plot([0], [0], 'b-')
line_RL, = ax3.plot([0], [0], 'r-')
line_LF, = ax3.plot([0], [0], 'g-')
ax3.set_xlabel('Time (s)')
ax3.set_ylabel('%')
y1=[0]
y2=[0]
y3=[0]
y=[[0], [0], [0], [0]]
x=[[0], [0], [0], [0]]
step=[]
step.append(100.0/len(SN_orw))
step.append(100.0/len(RL_orw))
if len(LF_orw) == 0:
	step.append(0)
else:
	step.append(100.0/len(LF_orw))

lineset = [timeline, line_SN, line_RL, line_LF]
die_ratio = [[0], [0], [0]]


G_orw = nx.Graph()
node_w = {}
die_orw = {}
imgs = []

#create postions first for simulation
pos={}
size = int(math.sqrt(result['numnodes']))
interval=1000.0/(size+2)
#row
for i in xrange(1, size+1):
	offset = (i-1)*size
	#column
	for j in xrange(1, size+1):
		pos[offset + j]=(interval*i, interval*j)
		
text = 'ORW processing progress: '
filesize = len(OrwDebugMsgs)
currline = 0
lasttime=0
#create orw network graph
for msg in OrwDebugMsgs:
	currline += 100
	if msg.node <=300 and msg.timestamp >= time_TH:
		if msg.node not in die_orw:
			#if type is receive, record every edge that appears
			if msg.type == NET_C_FE_RCV_MSG:
				if msg.dbg__c not in die_orw:
					if G_orw.has_edge(msg.dbg__c, msg.node):
						G_orw[msg.dbg__c][msg.node]['weight'] += 1
					else:
						G_orw.add_edge(msg.dbg__c, msg.node, weight = 1)
						for i, group in enumerate(sets):
							die_ratio[i].append(die_ratio[i][-1])
						im = update_v2(G_orw, pos, sets, lineset, msg.timestamp, die_ratio)
						imgs.append(im)
						lasttime = msg.timestamp
			elif msg.type == NET_C_DIE:
				if msg.node not in die_orw:
					die_orw[msg.node] = int(round(msg.timestamp/time_ratio))
					G_orw.remove_node(msg.node)
					for i, group in enumerate(sets):
						if msg.node in group:
							die_ratio[i].append(die_ratio[i][-1]+step[i])
						else:
							die_ratio[i].append(die_ratio[i][-1])
						
					im = update_v2(G_orw, pos, sets, lineset, msg.timestamp, die_ratio)
					imgs.append(im)
					lasttime = msg.timestamp
	update_progress(text, currline/filesize)

lasttime = int(math.ceil(lasttime))
ax3.set_xticks(xrange(0, (lasttime+1), lasttime/10))
ax3.set_xticklabels(xrange(0, (lasttime+1)/60, lasttime/600))

sorted_die_orw = sorted(die_orw.iteritems(), key=lambda (k,v): v)
sorted_die_node = [k for (k,v) in sorted_die_orw]
sorted_die_time = [v for (k,v) in sorted_die_orw]
print sorted_die_time

anim = animation.ArtistAnimation(fig,imgs, interval=500, blit=True)
anim.save('orw.mp4', bitrate=4000, extra_args=['-vcodec', 'libx264'])

'''
nx.draw_networkx_nodes(G, pos, node_size = 200, nodelist=[SINK_ID], node_color='k')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=SN_orw & nodelist, node_color='b')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=RL_orw & nodelist, node_color='r')
nx.draw_networkx_nodes(G, pos, node_size = 150, nodelist=LF_orw & nodelist, node_color='g')
nx.draw_networkx_edges(G, pos, nodelist=nodelist, width=0.5, alpha=0.5)

limit = ax1.axis()
ax1.set_axis_off()


###########################################################
######################      CTP      ######################

fig = pl.figure(figsize=(8,10))
ax1 = pl.subplot2grid((5,4), (0,0), colspan=4, rowspan=4)
ax1.set_axis_off()
ax2 = pl.subplot2grid((5,4), (4,0), colspan=1, rowspan=1)
ax2.set_axis_off()
ax3 = pl.subplot2grid((5,4), (4,1), colspan=1, rowspan=3)
G_ctp = nx.Graph()
node_w = {}
die_ctp = {}
sets = (SN_ctp, RL_ctp, LF_ctp)
pos_ctp = pos
imgs=[]


#create ctp network graph
for msg in CtpDebugMsgs:
	if msg.node <=300 and msg.timestamp >= time_TH:
		#if type is receive, record every edge that appears
		if msg.node not in die_ctp:
			G_ctp.add_node(msg.node)
			if msg.type == NET_C_FE_SENT_MSG:
				#Network graph construction
				if G_ctp.has_edge(msg.node, msg.dbg__c):
					G_ctp[msg.node][msg.dbg__c]['weight'] += 1
				else:
					G_ctp.add_edge(msg.node, msg.dbg__c, weight = 1)
					im = update_v2(G_ctp, pos_ctp, sets)
					imgs.append(im)
			elif msg.type == NET_C_FE_FWD_MSG:
				if G_ctp.has_edge(msg.node, msg.dbg__c):
					G_ctp[msg.node][msg.dbg__c]['weight'] += 1
				else:
					G_ctp.add_edge(msg.node, msg.dbg__c, weight = 1)
					im = update_v2(G_ctp, pos_ctp, sets)
					imgs.append(im)
			elif msg.type == NET_C_DIE:
				G_ctp.remove_node(msg.node)
				die_ctp[msg.node] = int(round(msg.timestamp/time_ratio))
				im = update_v2(G_ctp, pos_ctp, sets)
				imgs.append(im)
		
sorted_die_ctp = sorted(die_ctp.iteritems(), key=lambda (k,v): v)
sorted_die_node = []
sorted_die_time = []
for (k,v) in sorted_die_ctp:
	sorted_die_node.append(k)
	sorted_die_time.append(v)


anim = animation.ArtistAnimation(fig,imgs, interval=500, blit=True)
anim.save('ctp.mp4', bitrate=4000, extra_args=['-vcodec', 'libx264'])




print sorted_die_time
pos_ctp = pos_orw
#pos_ctp = nx.graphviz_layout(G_ctp, root=SINK_ID)
nodelist = set(G_ctp.nodes())
print "CTP:", len(SN_ctp)+len(RL_ctp)+len(LF_ctp), len(nodelist)
unknown = nodelist - SN_ctp - RL_ctp - LF_ctp

for node in unknown:
	if node != SINK_ID:
		G_ctp.remove_node(node)





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
ax2.set_xticks(xrange(0, 10801, 1200))
ax2.set_xticklabels(xrange(0, 181, 20))


lineset = [timeline, line_SN, line_RL, line_LF]
anim.save('ctp.mp4', fps=fps, bitrate=4000, extra_args=['-vcodec', 'libx264'])
'''
#nx.draw(G_ctp, pos_ctp)


