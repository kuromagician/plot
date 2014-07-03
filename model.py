#!/usr/bin/python
from tools.constant import *
from tools import twistReader as Treader
import tools.calprop as calprop
import tools.reader as reader
import tools.command as command
import sys
from collections import defaultdict
import matplotlib
import pylab as pl
from numpy import mean
from numpy import absolute
import numpy
from tools.functions import *
import scipy.misc as misc
from tools import calprop

resultc = command.main(sys.argv[1:])
FileDict, props = command.getfile(resultc)
CtpDebugMsgs = FileDict['CtpDebug']
OrwDebugMsgs = FileDict['OrwDebug']
OrwNtMsgs = FileDict['OrwNt']
props_orw = calprop.prop_orw(FileDict, resultc)
props_ctp = calprop.prop_ctp(FileDict, resultc)
'''for node in props_orw['Fwd_Load']:
	print "Node {} Fwd_Load {}".format(node, props_orw['Fwd_Load'][node])'''
TWIST = resultc['twist']



if resultc['twist'] == True:
	base_path = '/media/Data/ThesisData/Twist/'
	FileCollection_orw = ['trace_20140515_132005.1.txt', 'trace_20140515_160513.3.txt', 
						'trace_20140515_185012.5.txt', 'trace_20140515_210915.7.txt',
						'trace_20140515_232715.9.txt', 'trace_20140516_031415.11.txt']
						#'trace_20140518_231215.38.txt']
	
	FileCollection_ctp = ['trace_20140515_120916.0.txt', 'trace_20140515_145530.2.txt', 
						'trace_20140515_174113.4.txt', 'trace_20140515_200012.6.txt', 
						'trace_20140515_221814.8.txt', 'trace_20140516_020516.10.txt']
elif resultc['simulation']:
	time_ratio = 1.0
else:
	base_path = '/media/Data/ThesisData/Indriya/'
	FileCollection_orw = ['data-48680', 'data-48564', 'data-48640', 'data-48627', 
							'data-48623', 'data-48631', 'data-48646', 'data-48714',
							'data-48775']
	FileCollection_ctp = ['data-48672', 'data-48556', 'data-48639', 'data-48641', 
							'data-48637', 'data-48642', 'data-48651', 'data-48710',
							'data-48774']

time_ratio = props['timeratio']
if resultc['postpone']:
	time_TH = 60*time_ratio*10
else:
	time_TH = -1

FileNames = {'OrwDebug':('23739.dat',), 'CtpDebug':('24460.dat',), 
				'CtpData':('24463.dat',), 'ConnectDebug':('25593.dat',),
				'OrwNt':('23738.dat',)}

#################            CONSTANT             ############


Tw = resultc['wakeup']*1000.0
Tc = 6.0

Trx = 20.0 + Tc/2.0
#time needed for a transmition to sink
Ttx = 3.0 + 3.0 + 20 #cca + trans+ack + post(20ms)
Tmin = 6.0
Tpost=20.0
Tipi = 1000*60.0
Tibi = 8*1000*60.0
T_test = 50*1000*60.0
ratio_ipi = Tipi/T_test
ratio_ibi = Tibi/T_test

SINK_ID = props['SINK_ID']

#DutyCycle_orw = defaultdict(list)
F_orw = defaultdict(int)
Tao_orw = defaultdict(set)
L_orw = defaultdict(int)
rcv_hist_orw = set()
nodelist = set()
relay_orw = set()
leaf_orw = set()
Fail_orw = defaultdict(int)
counter1=0
counter2=0
sink_neighbour_orw = set()
#ForwardSet = defaultdict(set)

for msg in OrwDebugMsgs:
	if msg.timestamp / time_ratio / 60>= 10:
		if msg.node != SINK_ID:
			nodelist.add(msg.node)
		if msg.type == NET_SNOOP_RCV:
			L_orw[msg.node] += 1
			counter1 += 1
		elif msg.type == NET_C_FE_SENT_MSG:
			t = (msg.dbg__c >> 8)/10.0
			F_orw[msg.node] += 1
		elif msg.type == NET_C_FE_RCV_MSG:
			if (msg.dbg__b, msg.dbg__a) not in rcv_hist_orw:
				rcv_hist_orw.add((msg.dbg__b, msg.dbg__a))
				counter2 += 1
				Tao_orw[msg.node].add(msg.dbg__c)
				#ForwardSet[msg.dbg__c].add(msg.node)
		elif msg.type == NET_C_FE_SENDDONE_WAITACK:
			Fail_orw[msg.node] += 1
#print "ORW Fail: ", Fail_orw
#print sink_neighbour_orw



#Avg_F_orw = {k:F_orw[k]*ratio_ipi for k in F_orw}
Avg_F_orw = props_orw['Fwd_Load']


Avg_L_orw = {k:L_orw[k]*ratio_ipi for k in L_orw}
Avg_Tao_orw = {k: len(Tao_orw[k]) for k in Tao_orw}
Avg_Fail_orw = defaultdict(int)
for k, v in Fail_orw.iteritems():
	Avg_Fail_orw[k] = v*ratio_ipi


#get division set
sink_neighbour_orw = props_orw['Dir_Neig']
relay_orw = props_orw['Relay']
leaf_orw = props_orw['Leaf']
#print sorted(sink_neighbour_orw)

ForwardSet = defaultdict(list)
for msg in OrwNtMsgs:
	ForwardSet[msg.node].append(msg.indexesInUse)
	
Avg_Fs_orw = {k:mean(ForwardSet[k]) for k in ForwardSet}

#Avg_Fs_orw = {k:len(ForwardSet[k]) for k in ForwardSet}

modeled_dc_orw = {}
part1 = {}
part2 = {}
part3 = {}
#print sorted(Avg_Tao_orw.keys())
#print sorted(sink_neighbour_orw)

Avg_Data_dc_orw = props_orw['Avg_Data_dc']
Avg_Idle_dc_orw = props_orw['Avg_Idle_dc'] 
Avg_Total_dc_orw = props_orw['Avg_Total_dc']


for node in nodelist:
	if node in Avg_F_orw:
		F = props_orw['Fwd_Load'][node]
	else:
		F = 0
	if node in Avg_L_orw:
		L = Avg_L_orw[node] 
	else:
		L = 0
	if node in Avg_Fs_orw:
		Fs = Avg_Fs_orw[node]
	else:
		Fs = 0
	if node in Avg_Tao_orw:
		Tao = Avg_Tao_orw[node]
	else:
		Tao = 0
	if node in sink_neighbour_orw:
		Fail = Avg_Fail_orw[msg.node]
		modeled_dc_orw[node] = sum(DC_Model_orw_SN(F, Tao, Fs, L, Fail, Tw))
		part1[node], part2[node], part3[node] = DC_Model_orw_SN(F, Tao, Fs, L, Fail, Tw)
	else:
		Fail = Avg_Fail_orw[msg.node]
		modeled_dc_orw[node] = sum(DC_Model_orw(F, Tao, Fs, L, Fail, Tw))
		part1[node], part2[node], part3[node] = DC_Model_orw(F, Tao, Fs, L, Fail, Tw)
	#if node in (54,66,83):
	#	print "Node!!!", node, F, Tao, Fs, L, Fail, "\n", \
	#		             modeled_dc_orw[node], "%", Avg_Total_dc_orw[node], "%"
		
		
fig = pl.figure()
ax1 = fig.add_subplot(2,1,1)
ax1.bar(part1.keys(), part1.values())
ax1.bar(part1.keys(), part2.values(), bottom = part1.values(), color='r')
temp1 = numpy.array(part1.values())
temp2 = numpy.array(part2.values())
temp1 += temp2
ax1.bar(part1.keys(), part3.values(), bottom = temp1, color='y')


#print mean(Avg_Total_dc_orw.values())
ax2 = fig.add_subplot(2,1,2)
ax2.bar(Avg_Data_dc_orw.keys(), Avg_Idle_dc_orw.values())
ax2.bar(Avg_Data_dc_orw.keys(), Avg_Data_dc_orw.values(), bottom=Avg_Idle_dc_orw.values(), color='r')

fig = pl.figure()
ax1 = fig.add_subplot(2,1,1)
#h = fig.findobj(gca,'Type','patch')
#set(h,'FaceColor','r','EdgeColor','w','facealpha',0.75)
ax1.bar(Avg_Total_dc_orw.keys(), Avg_Total_dc_orw.values(), alpha=0.5)
values = [modeled_dc_orw[k] for k in sink_neighbour_orw]
#ax1.bar(sink_neighbour_orw, Avg_Total_dc_orw.values(), alpha=0.5)
ax1.bar(modeled_dc_orw.keys(), modeled_dc_orw.values(), color='r', alpha=0.5)
#ax1.bar(sink_neighbour_orw ,values, color='r', alpha=0.5)

#calculate difference
ax2 = fig.add_subplot(2,1,2)
diff_value = {}
diff_ratio = {}
for k in set(modeled_dc_orw.keys()) & set(Avg_Total_dc_orw.keys()) :
	cal_result = modeled_dc_orw[k] - Avg_Total_dc_orw[k]
	ratio = cal_result*100.0/Avg_Total_dc_orw[k]
	#print k, result*100.0/Avg_Total_dc_orw[k], "%"
	diff_value[k] = cal_result
	diff_ratio[k] = ratio
ax2.bar(diff_value.keys(), diff_value.values(), color='r')
print "diff ratio orw:", mean(absolute(diff_ratio.values())), "%"

testload = props_orw['Fwd_Load']
print "SN, LF, RL", Seperate_Avg(testload, sink_neighbour_orw, leaf_orw, relay_orw)
'''for node in [3,9,15,14,13]:
	print "LOAD ORW: ", node, Avg_F_orw[node]'''
##################################  CTP ################################
###############################  Data Process ##########################

DutyCycle_ctp = defaultdict(list)
F_ctp = defaultdict(int)
Tao_ctp = defaultdict(set)
petx = defaultdict(list)
L_ctp = defaultdict(int)
N_ctp = defaultdict(int)
sink_neighbour_ctp = set()
neighbour_ctp = defaultdict(set)
rcv_hist_ctp = set()
relay_ctp = set()
leaf_ctp = set()
fail_ctp = defaultdict(int)
counter1=0
counter2=0
for msg in CtpDebugMsgs:
	if msg.timestamp >= time_TH:
		if msg.type == NET_SNOOP_RCV:
			counter1 += 1
			L_ctp[msg.node] += 1
		elif msg.type == NET_C_TREE_RCV_BEACON:
			counter2 += 1
			N_ctp[msg.node] += 1
			if resultc['simulation']:
				neighbour_ctp[msg.node].add(msg.dbg__a)
			else:
				neighbour_ctp[msg.node].add(msg.route_info__parent)
		elif msg.type == NET_DC_REPORT:
			if msg.dbg__a + msg.dbg__c < 10000:
				DutyCycle_ctp[msg.node].append((msg.dbg__a, msg.dbg__b, msg.dbg__c))
			else:
				#print "DC ERROR:", msg.node, msg.dbg__a, msg.dbg__b, msg.dbg__c, msg.timestamp / time_ratio
				DutyCycle_ctp[msg.node].append((10000, msg.dbg__b, 0))
		elif msg.type == NET_C_TREE_SENT_BEACON:
			#fail_ctp[msg.node] += 1
			#Tao_ctp[msg.node].append(msg.route_info__metric/100.0)
			'''elif msg.type == 0x73:
			Tao_ctp[msg.node].append(route_info__parent/10.0)'''
		elif msg.type == NET_C_FE_SENT_MSG or msg.type == NET_C_FE_FWD_MSG:
			F_ctp[msg.node] += 1
			'''if msg.dbg__c == SINK_ID:
				sink_neighbour_ctp.add(msg.node)'''
			Tao_ctp[msg.dbg__c].add(msg.node)
		#elif msg.type == NET_C_FE_SENDDONE_FAIL_ACK_SEND or\
		#     msg.type == NET_C_FE_SENDDONE_FAIL_ACK_FWD:
		elif msg.type == NET_C_FE_SENDDONE_WAITACK: 
			fail_ctp[msg.node] += 1
		'''elif msg.type == 0x73:
			petx[msg.node].append(msg.route_info__parent/10.0)'''
			
#haha={k:mean(petx[k]) for k in petx}
#for k in haha:
#	print "PETX: ", k, haha[k]


############################# real DC ##########################
Avg_DC_ctp = {k: mean(DutyCycle_ctp[k], axis=0) for k in DutyCycle_ctp}
Avg_Data_dc_ctp = {}
Avg_Idle_dc_ctp = {}
Avg_Total_dc_ctp = {}

for node in Avg_DC_ctp:
	Avg_Data_dc_ctp[node] = Avg_DC_ctp[node][0]*0.01
	Avg_Idle_dc_ctp[node] = Avg_DC_ctp[node][2]*0.01
	Avg_Total_dc_ctp[node] = Avg_Data_dc_ctp[node] + Avg_Idle_dc_ctp[node]
	
print mean(Avg_Total_dc_ctp.values())
############################# real DC ##########################

#F_ctp = prop_ctp['load']

#Avg_F_ctp = {k:F_ctp[k]*ratio_ipi for k in F_ctp}
Avg_F_ctp = props_ctp['Fwd_Load']

Avg_L_ctp = {k:L_ctp[k]*ratio_ipi for k in L_ctp}
#Avg_N_ctp = {k:N_ctp[k]*ratio_ibi for k in N_ctp}
Avg_N_ctp = {k:len(neighbour_ctp[k]) for k in neighbour_ctp}
Avg_Tao_ctp = defaultdict(int)
for k in Tao_ctp:
	Avg_Tao_ctp[k] = len(Tao_ctp[k])
#Avg_Tao_ctp = {k: mean(Tao_ctp[k]) for k in Tao_ctp}
Avg_Fail_ctp = {k:fail_ctp[k]*ratio_ipi for k in fail_ctp}
#print Avg_Fail_ctp

#get sinkN, relay and leaf set
sink_neighbour_ctp = props_ctp['Dir_Neig']
relay_ctp = props_ctp['Relay']
leaf_ctp = props_ctp['Leaf']
				
modeled_dc_ctp = {}

for node in F_ctp.keys():
	F = props_ctp['Fwd_Load'][node]
	N = Avg_N_ctp[node]
	L = Avg_L_ctp[node]
	Tao = Avg_Tao_ctp[node]
	if node not in Avg_Fail_ctp:
		Fail = 0
	else:
		Fail = Avg_Fail_ctp[node]
	if node in sink_neighbour_ctp:
		modeled_dc_ctp[node] = DC_Model_ctp_SN(F, Tao, N, L, Fail, Tw)
	else:
		modeled_dc_ctp[node] = DC_Model_ctp(F, Tao, N, L, Fail, Tw)
	#if node == 10:
	#	print "Node!!!", node, F, N, L, Tao, Fail, "\n", \
	#		             modeled_dc_ctp[node], "%", Avg_Total_dc_ctp[node], "%"


fig = pl.figure()
ax = fig.add_subplot(2,1,1)

ax.bar(Avg_Total_dc_ctp.keys(), Avg_Total_dc_ctp.values(), alpha=0.5)
ax.bar(modeled_dc_ctp.keys(), modeled_dc_ctp.values(), color='r', alpha=0.5)

ax2 = fig.add_subplot(2,1,2)
diff_value = {}
diff_ratio = {}
for k in modeled_dc_ctp:
	if k in Avg_Total_dc_ctp:
		cal_result = modeled_dc_ctp[k] - Avg_Total_dc_ctp[k]
		ratio = cal_result*100.0/Avg_Total_dc_ctp[k]
	#print k, ratio, "%"
		diff_value[k] = cal_result
		diff_ratio[k] = ratio
ax2.bar(diff_value.keys(), diff_value.values(), color='r')
print "diff CTP:", mean(absolute(diff_ratio.values())), "%"


fig = pl.figure()
ax = fig.add_subplot(1,1,1)
ax.boxplot([Avg_F_ctp.values(),Avg_F_orw.values()] , positions=[1,2])
#ax.boxplot(Avg_F_orw.values())
'''for node in [3,9,15,14,13]:
	print "LOAD CTP: ", node, Avg_F_ctp[node]'''
pl.show()


###################### draw model curve ########################
######################       CTP MODEL CALCULATION      ########################
fig = pl.figure(figsize=(13,10))

F_SN, F_leaf, F_relay = Seperate_Avg(Avg_F_ctp, sink_neighbour_ctp, leaf_ctp, relay_ctp)

Tao_SN, Tao_leaf, Tao_relay = Seperate_Avg(Avg_Tao_ctp, sink_neighbour_ctp, leaf_ctp, relay_ctp)

N_SN, N_leaf, N_relay = Seperate_Avg(Avg_N_ctp, sink_neighbour_ctp, leaf_ctp, relay_ctp)

L_SN, L_leaf, L_relay = Seperate_Avg(Avg_L_ctp, sink_neighbour_ctp, leaf_ctp, relay_ctp)

Fail_SN, Fail_leaf, Fail_relay = Seperate_Avg(Avg_Fail_ctp, sink_neighbour_ctp, leaf_ctp, relay_ctp)

'''

if resultc['twist'] == True:
	realrange = [0.25, 0.5, 1, 2, 4, 8]
else:
	realrange = [0.25, 0.5, 1, 1.5, 2, 2.5, 4, 6]
ax1 = pl.subplot2grid((5, 5), (0, 0), colspan=5, rowspan=3)
s = "Using data from wakeup time: {} s".format(resultc['wakeup'],)
ax1.set_title(s)
y = [DC_Model_ctp_SN(F_SN, Tao_SN, N_SN, L_SN, Fail_SN, k*1000)for k in realrange]
ax1.plot(realrange, y, label='ctp_SN')
y = [DC_Model_ctp(F_leaf, Tao_leaf, N_leaf, L_leaf,  Fail_leaf, k*1000)for k in realrange]
ax1.plot(realrange, y, color='g', label='ctp_leaf')
y = [DC_Model_ctp(F_relay, Tao_relay, N_relay, L_relay, 0, k*1000)for k in realrange]
ax1.plot(realrange, y, color='r', label='ctp_relay')

######################       CTP PLOT        ########################
#this part is plot real dc over model, part ctp, and provide some imformation
#below graph

y1 = []
y2 = []
y3 = []
err1 = []
err2 = []
err3 = []

for test, k in zip(FileCollection_ctp, realrange):
	if not TWIST:
		FileDict['CtpDebug'] = reader.loadDebug(base_path + test, FileNames['CtpDebug']) 
		FileDict['CtpData'] = reader.loadDataMsg(base_path + test, FileNames['CtpData'])
	else:
		FileDict['CtpDebug'], _, _, FileDict['CtpData'] = Treader.load(base_path + test)
	prop_ctp = calprop.prop_ctp(FileDict, resultc)
	d1, d2, d3 = Seperate_Avg(prop_ctp['Avg_Total_dc'], prop_ctp['Dir_Neig'],
							prop_ctp['Relay'], prop_ctp['Leaf'])
	e1, e2, e3 = Seperate_maxmin(prop_ctp['Avg_Total_dc'], prop_ctp['Dir_Neig'],
							prop_ctp['Relay'], prop_ctp['Leaf'])
	err1.append((d1-e1[1], e1[0]-d1))
	err2.append((d2-e2[1], e2[0]-d2))
	err3.append((d3-e3[1], e3[0]-d3))
	y1.append(d1)
	y2.append(d2)
	y3.append(d3)
	sn = DC_Model_ctp_SN(F_SN, Tao_SN, N_SN, L_SN, Fail_SN, k*1000)
	lf = DC_Model_ctp(F_leaf, Tao_leaf, N_leaf, L_leaf,  Fail_leaf, k*1000)
	rl = DC_Model_ctp(F_relay, Tao_relay, N_relay, L_relay, 0, k*1000)
	print "CTP For wakeup interval", k, "s"
	s = "SN:real {:5.2f} model {:5.2f} err {:5.2f}%    ".format(d1, sn, (d1-sn)/sn*100)+\
        "RL:real {:5.2f} model {:5.2f} err {:5.2f}%".format(d2, rl, (d2-rl)/rl*100)+\
        "LF:real {:5.2f} model {:5.2f} err {:5.2f}%\n".format(d3, lf, (d3-lf)/lf*100)
	print "SN:real {:.2f} model {:.2f} err {:.2f}%".format(d1, sn, (d1-sn)/sn*100)
	print "RL:real {:.2f} model {:.2f} err {:.2f}%".format(d2, rl, (d2-rl)/rl*100)
	print "LF:real {:.2f} model {:.2f} err {:.2f}%\n".format(d3, lf, (d3-lf)/lf*100)
	ax1.annotate(s, (0,0), (0, -(k+realrange[-1] + 3.5)*20), xycoords='axes fraction', \
	              textcoords='offset points', va='top')
	              
s = "F_SN:{:5.2f}, Tao_SN:{:5.2f}, N_SN:{:5.2f}, L_SN:{:5.2f}, Fail_SN:{:5.2f}\n".format(F_SN, Tao_SN, N_SN, L_SN, Fail_SN) +\
    "F_leaf:{:5.2f}, Tao_leaf:{:5.2f}, N_leaf:{:5.2f}, L_leaf:{:5.2f}, Fail_leaf:{:5.2f}\n".format(F_leaf, Tao_leaf, N_leaf, L_leaf, Fail_leaf) +\
    "F_relay:{:5.2f}, Tao_relay:{:5.2f}, N_relay:{:5.2f}, L_relay:{:5.2f}, Fail_relay:{:5.2f}".format(F_relay, Tao_relay, N_relay, L_relay, Fail_relay)
ax1.annotate(s, (0,0), (0, -(k+realrange[-1]+4.5)*20), xycoords='axes fraction', \
	              textcoords='offset points', va='top')
'''	          
'''e1, e2, e3 = Seperate_maxmin(prop_ctp['Avg_Total_dc'], prop_ctp['Dir_Neig'],
							prop_ctp['Relay'], prop_ctp['Leaf'])
ax1.errorbar(realrange, y1, yerr=zip(*err1), fmt='D', alpha=0.6, color='b')
ax1.errorbar(realrange, y2, yerr=zip(*err2), fmt='D', alpha=0.6, color='r')
ax1.errorbar(realrange, y3, yerr=zip(*err3), fmt='D', alpha=0.6, color='g')'''

'''ax1.scatter(realrange, y1, color='r', marker='D', alpha=0.6)
ax1.scatter(realrange, y2, color='r', marker='D', alpha=0.6)
ax1.scatter(realrange, y3, color='g', marker='D', alpha=0.6)'''

######################       CTP SAVE        ########################

if not TWIST:
	fo = open("CTP_Paras.txt", "a+")
else:
	fo = open("CTP_Paras_twist.txt", "a+")
line = "{:<8.2f}{:<8s}{:<8s}{:<8.2f}{:<8.2f}{:<8.2f}{:<8.2f}{:<8.2f}\n".format(resultc['wakeup'],"SN", "CTP", F_SN, Tao_SN, N_SN, L_SN, Fail_SN)
fo.write(line)
line = "{:<8.2f}{:<8s}{:<8s}{:<8.2f}{:<8.2f}{:<8.2f}{:<8.2f}{:<8.2f}\n".format(resultc['wakeup'],"RL", "CTP", F_relay, Tao_relay, N_relay, L_relay, Fail_relay)
fo.write(line)
line = "{:<8.2f}{:<8s}{:<8s}{:<8.2f}{:<8.2f}{:<8.2f}{:<8.2f}{:<8.2f}\n".format(resultc['wakeup'],"LF", "CTP", F_leaf, Tao_leaf, N_leaf, L_leaf, Fail_leaf)
fo.write(line)
fo.close()


################################   ORW MODEL CALCULATION   ####################
F_SN, F_leaf, F_relay = Seperate_Avg(Avg_F_orw, sink_neighbour_orw, leaf_orw, relay_orw)

Tao_SN, Tao_leaf, Tao_relay = Seperate_Avg(Avg_Tao_orw, sink_neighbour_orw, leaf_orw, relay_orw)

Fs_SN, Fs_leaf, Fs_relay = Seperate_Avg(Avg_Fs_orw, sink_neighbour_orw, leaf_orw, relay_orw)

L_SN, L_leaf, L_relay = Seperate_Avg(Avg_L_orw, sink_neighbour_orw, leaf_orw, relay_orw)

Fail_SN, Fail_leaf, Fail_relay = Seperate_Avg(Avg_Fail_orw, sink_neighbour_orw, leaf_orw, relay_orw)

'''
y = [sum(DC_Model_orw_SN(F_SN, L_SN, FWD_SN,  k*1000)) for k in realrange]
ax1.plot(realrange, y, 'b--', label='orw_SN')
y = [sum(DC_Model_orw(F_leaf, Tao_leaf, Fs_leaf, L_leaf, k*1000)) for k in realrange]
ax1.plot(realrange, y, 'g--', label='orw_leaf')
y = [sum(DC_Model_orw(F_relay, Tao_relay, Fs_relay, L_relay, k*1000)) for k in realrange]
ax1.plot(realrange, y, 'r--', label='orw_relay')
ax1.legend()

#################################  ORW   PLOT####################################

y1 = []
y2 = []
y3 = []
err1 = []
err2 = []
err3 = []
result = defaultdict(bool)
for test, k in zip(FileCollection_orw, realrange):
	if not TWIST:
		FileDict['OrwDebug'] = reader.loadDebug(base_path + test, FileNames['OrwDebug']) 
	else:
		FileDict['OrwDebug'], FileDict['OrwNt'], _, _ = Treader.load(base_path + test) 
	prop_orw = calprop.prop_orw(FileDict, resultc)
	d1, d2, d3 = Seperate_Avg(prop_orw['Avg_Total_dc'], prop_orw['Dir_Neig'],
							prop_orw['Relay'], prop_orw['Leaf'])
	e1, e2, e3 = Seperate_maxmin(prop_ctp['Avg_Total_dc'], prop_ctp['Dir_Neig'],
							prop_ctp['Relay'], prop_ctp['Leaf'])
	err1.append((d1-e1[1], e1[0]-d1))
	err2.append((d2-e2[1], e2[0]-d2))
	err3.append((d3-e3[1], e3[0]-d3))
	y1.append(d1)
	y2.append(d2)
	y3.append(d3)
	sn = sum(DC_Model_orw_SN(F_SN, L_SN, FWD_SN,  k*1000))
	lf = sum(DC_Model_orw(F_leaf, Tao_leaf, Fs_leaf, L_leaf, k*1000))
	rl = sum(DC_Model_orw(F_relay, Tao_relay, Fs_relay, L_relay, k*1000))
	print "ORW For wakeup interval", k, "s"
	print "SN:real {:5.2f} model {:5.2f} err {:5.2f}%".format(d1, sn, (d1-sn)/sn*100)
	print "RL:real {:5.2f} model {:5.2f} err {:5.2f}%".format(d2, rl, (d2-rl)/rl*100)
	print "LF:real {:5.2f} model {:5.2f} err {:5.2f}%\n".format(d3, lf, (d3-lf)/lf*100)
	s =  "SN:real {:5.2f} model {:5.2f} err {:5.2f}%".format(d1, sn, (d1-sn)/sn*100) +\
	     "RL:real {:5.2f} model {:5.2f} err {:5.2f}%".format(d2, rl, (d2-rl)/rl*100) +\
	     "LF:real {:5.2f} model {:5.2f} err {:5.2f}%\n".format(d3, lf, (d3-lf)/lf*100)
	ax1.annotate(s, (0,0), (0, -(k+0.2)*20), xycoords='axes fraction', \
	              textcoords='offset points', va='top')
	       
s = "F_SN:{:5.2f}, L_SN:{:5.2f}, FWD_SN:{:5.2f}\n".format(F_SN, L_SN, FWD_SN) +\
    "F_leaf:{:5.2f}, Tao_leaf:{:5.2f}, Fs_leaf:{:5.2f}, L_leaf:{:5.2f}\n".format(F_leaf, Tao_leaf, Fs_leaf, L_leaf) +\
    "F_relay:{:5.2f}, Tao_relay:{:5.2f}, Fs_relay:{:5.2f}, L_relay:{:5.2f}".format(F_relay, Tao_relay, Fs_relay, L_relay)
ax1.annotate(s, (0,0), (0, -(k+1)*20), xycoords='axes fraction', \
	              textcoords='offset points', va='top')'''
'''ax1.errorbar(realrange, y1, yerr=zip(*err1), fmt='o', alpha=0.6, color='b')
ax1.errorbar(realrange, y2, yerr=zip(*err2), fmt='o', alpha=0.6, color='r')
ax1.errorbar(realrange, y3, yerr=zip(*err3), fmt='o', alpha=0.6, color='g')'''

'''ax1.scatter(realrange, y1, alpha=0.6)
ax1.scatter(realrange, y2, color='r', alpha=0.6)
ax1.scatter(realrange, y3, color='g', alpha=0.6)

limits = ax1.axis()
ax1.set_xlim([0, limits[1]])
ax1.set_ylim([0, limits[3]])
fig.savefig("model" + str(resultc['wakeup']) + ".pdf")'''
#
	
#########################################################################################################

############################################ ORW SAVE ################################################
#record the result in to files that we dont need to run again
if not TWIST:
	fo = open("ORW_Paras.txt", "a+")
else:
	fo = open("ORW_Paras_twist.txt", "a+")
line = "{:<8.2f}{:<8s}{:<8s}{:<8.2f}{:<8.2f}{:<8.2f}{:<8.2f}{:<8.2f}\n".format(resultc['wakeup'],"SN", "ORW", F_SN, Tao_SN, Fs_SN, L_SN, Fail_SN)
fo.write(line)
line = "{:<8.2f}{:<8s}{:<8s}{:<8.2f}{:<8.2f}{:<8.2f}{:<8.2f}{:<8.2f}\n".format(resultc['wakeup'],"RL", "ORW", F_relay, Tao_relay, Fs_relay, L_relay, Fail_relay)
fo.write(line)
line = "{:<8.2f}{:<8s}{:<8s}{:<8.2f}{:<8.2f}{:<8.2f}{:<8.2f}{:<8.2f}\n".format(resultc['wakeup'],"LF", "ORW", F_leaf, Tao_leaf, Fs_leaf, L_leaf, Fail_leaf)
fo.write(line)
fo.close()

#########################################################################################################


