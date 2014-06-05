#!/usr/bin/python
from tools.constant import *
import tools.command as command
from collections import defaultdict
import numpy
from numpy import mean


#OrwNtMsgs = FileDict['OrwNt']

def prop_orw(FileDict, args):
	OrwDebugMsgs = FileDict['OrwDebug']
	if args['twist'] == True:
		SINK_ID = 153
		time_ratio = 1000000.0
	else:
		SINK_ID = 1
		time_ratio = 1000.0
	#######################section for ORW############################
	num_fwd_orw = defaultdict(int)
	num_init_orw = defaultdict(int)
	route_hist_orw = defaultdict(set)
	rcv_hist_orw = set()
	DutyCycle_orw = defaultdict(list)
	dir_neig_orw = set()
	total_receive_orw = 0

	for msg in OrwDebugMsgs:
		#only record data after 10 minutes
		if msg.timestamp / time_ratio /60 >= 10:
			if msg.type == NET_C_FE_RCV_MSG:
				#make sure we don't count duplicate
				if (msg.msg__origin, msg.dbg__a) not in rcv_hist_orw:
					#add to path and total receive history
					# (origin, SeqNo) += lasthop
					route_hist_orw[(msg.msg__origin, msg.dbg__a)].add(msg.dbg__c)
					rcv_hist_orw.add((msg.msg__origin, msg.dbg__a))
					#if node is SINK, add node to direct neighbour
					if msg.node == SINK_ID:
						dir_neig_orw.add(msg.dbg__c)
						total_receive_orw += 1
			elif msg.type == NET_DC_REPORT:
				if msg.dbg__a + msg.dbg__c < 10000:
					DutyCycle_orw[msg.node].append((msg.dbg__a, msg.dbg__b, msg.dbg__c))
				else:
					#print msg.node, msg.dbg__a, msg.dbg__c, msg.dbg__b
					DutyCycle_orw[msg.node].append((10000, msg.dbg__b, 0))
			elif msg.type == NET_APP_SENT:
				num_init_orw[msg.node] += 1
			elif msg.type == NET_C_FE_SENT_MSG:
				#if origin != curr node, then it's is forwarder
				if msg.dbg__b != msg.node:
					num_fwd_orw[msg.node] += 1

	#Calculate Avg load
	load_orw = {k: num_fwd_orw[k] * 1.0 / num_init_orw[k] + 1 for k in num_init_orw}
	
	
	#Calculate the average hops to SINK
	counter = defaultdict(int)
	total_hops_orw = defaultdict(int)
	for (k, v) in route_hist_orw:
		total_hops_orw[k] += max(len(route_hist_orw[(k,v)]) - 1, 0)
		counter[k] += 1

	avg_hops_orw = {k:total_hops_orw[k] / 1.0 / counter[k] for k in total_hops_orw}	
	
	
	#get the average dutycycle of each node
	Avg_DC_orw = {k: mean(DutyCycle_orw[k], axis=0) for k in DutyCycle_orw}

	Avg_Data_dc_orw = {}
	Avg_Idle_dc_orw = {}
	Avg_Total_dc_orw = {}

	for node in Avg_DC_orw:
		Avg_Data_dc_orw[node] = Avg_DC_orw[node][0]*0.01
		Avg_Idle_dc_orw[node] = Avg_DC_orw[node][2]*0.01
		Avg_Total_dc_orw[node] = Avg_Data_dc_orw[node] + Avg_Idle_dc_orw[node]
		
	
	#Calculate sets for relay and leaves
	leaf_orw = set()
	relay_orw = set()
	for k in load_orw:
		load = load_orw[k]
		if k not in dir_neig_orw:
			if load < 2:
				leaf_orw.add(k)
			else:
				relay_orw.add(k)
	props = {}
	props['Avg_Data_dc'] = Avg_Data_dc_orw
	props['Avg_Idle_dc'] = Avg_Idle_dc_orw
	props['Avg_Total_dc'] = Avg_Total_dc_orw
	props['Avg_Hops'] = avg_hops_orw
	props['Num_Init'] = num_init_orw
	props['Num_Fwd'] = num_fwd_orw
	props['Dir_Neig'] = dir_neig_orw
	props['Relay'] = relay_orw
	props['Leaf'] = leaf_orw
	props['Num_Rcv'] = total_receive_orw
	props['Fwd_Load'] = load_orw
	
	return props
	
def prop_ctp(FileDict, args):
	CtpDebugMsgs = FileDict['CtpDebug']
	CtpDataMsgs = FileDict['CtpData']
	if args['twist'] == True:
		SINK_ID = 153
		time_ratio = 1000000.0
	else:
		SINK_ID = 1
		time_ratio = 1000.0
	#######################section for CTP############################
	DutyCycle_ctp = defaultdict(list)
	Avg_DC_ctp = defaultdict(int)
	children_ctp = defaultdict(set)
	rcv_hist_ctp = set()
	num_fwd_ctp = defaultdict(int)
	num_init_ctp = defaultdict(int)
	send_noACK_ctp = defaultdict(int)
	send_Qfull_ctp = defaultdict(int)
	fwd_noACK_ctp = defaultdict(int)
	dir_neig_ctp = set()
	total_receive_ctp = 0
	


	for msg in CtpDebugMsgs:
		#only record data after 10 minutes
		if msg.timestamp / time_ratio /60 >= 10:
			if msg.type == NET_C_FE_SENT_MSG:
				num_init_ctp[msg.node] += 1
				if msg.dbg__c == SINK_ID:
					dir_neig_ctp.add(msg.node)
			#record beacon
			elif msg.type == 0x33:
				pass
			elif msg.type == NET_DC_REPORT and msg.node != SINK_ID:
				if msg.dbg__a + msg.dbg__c < 10000:
					DutyCycle_ctp[msg.node].append((msg.dbg__a, msg.dbg__b, msg.dbg__c))
				else:
					#print msg.node, msg.dbg__a, msg.dbg__c, msg.dbg__b
					DutyCycle_ctp[msg.node].append((10000, msg.dbg__b, 0))
			elif msg.type == NET_C_FE_FWD_MSG:
				num_fwd_ctp[msg.node] += 1
				if msg.dbg__c == SINK_ID:
					dir_neig_ctp.add(msg.node)
			elif msg.type == NET_C_FE_RCV_MSG:
				if msg.node == SINK_ID:
					if (msg.dbg__b, msg.dbg__a) not in rcv_hist_ctp:
						rcv_hist_ctp.add((msg.dbg__b, msg.dbg__a))
						total_receive_ctp += 1
					#dir_neig_ctp.add(msg.msg__other_node)
			elif msg.type == NET_C_FE_SEND_QUEUE_FULL:
				send_Qfull_ctp[msg.node] += 1
			elif msg.type == NET_C_FE_SENDDONE_FAIL_ACK_SEND:
				send_noACK_ctp[msg.node] += 1
			elif msg.type == NET_C_FE_SENDDONE_FAIL_ACK_FWD:
				fwd_noACK_ctp[msg.node] += 1

	#packet lost statics
	'''Qfull = sum(send_Qfull_ctp.values())
	SnoACK = sum(send_noACK_ctp.values())
	FnoACK = sum(fwd_noACK_ctp.values())'''
	
	
	#Calculate load  
	load_ctp = {k: num_fwd_ctp[k] * 1.0 / num_init_ctp[k] + 1 for k in num_init_ctp}
	
	
	#get the average dutycycle of each node
	Avg_DC_ctp = {k: mean(DutyCycle_ctp[k], axis=0) for k in DutyCycle_ctp}

	Avg_Data_dc_ctp = {}
	Avg_Idle_dc_ctp = {}
	Avg_Total_dc_ctp = {}

	for node in Avg_DC_ctp:
		Avg_Data_dc_ctp[node] = Avg_DC_ctp[node][0]*0.01
		Avg_Idle_dc_ctp[node] = Avg_DC_ctp[node][2]*0.01
		Avg_Total_dc_ctp[node] = Avg_Data_dc_ctp[node] + Avg_Idle_dc_ctp[node]
	
	
	
	
	
	#use THL to calculate hops
	thl = defaultdict(int)
	for msg in CtpDataMsgs:
		if thl[(msg.origin, msg.seqno)] != 0:
			thl[(msg.origin, msg.seqno)] = min(msg.thl, thl[(msg.origin, msg.seqno)])
		else:
			thl[(msg.origin, msg.seqno)] = msg.thl
		#if msg.parent == SINK_ID:
		#	dir_neig_ctp.add(msg.node)

	t_thl = defaultdict(int)
	counter = defaultdict(int)
	for (k, v) in thl:
		t_thl[k] += thl[(k,v)]
		counter[k] += 1

	avg_hops_ctp = {k:t_thl[k] / 1.0 / counter[k]-1 for k in t_thl}
	
	#Calculate set of relays and leaves
	relay_ctp = set()
	leaf_ctp = set()
	for i in num_init_ctp:
		load = num_fwd_ctp[i] * 1.0 / num_init_ctp[i] + 1
		if i not in dir_neig_ctp:
			if load < 2:
				leaf_ctp.add(i)
			else:
				relay_ctp.add(i)
	
	props = {}
	props['Avg_Data_dc'] = Avg_Data_dc_ctp
	props['Avg_Idle_dc'] = Avg_Idle_dc_ctp
	props['Avg_Total_dc'] = Avg_Total_dc_ctp
	props['Avg_Hops'] = avg_hops_ctp
	props['Num_Init'] = num_init_ctp
	props['Num_Fwd'] = num_fwd_ctp
	props['Dir_Neig'] = dir_neig_ctp
	props['Relay'] = relay_ctp
	props['Leaf'] = leaf_ctp
	props['Num_Rcv'] = total_receive_ctp
	props['Fwd_Load'] = load_ctp
	
	return props

