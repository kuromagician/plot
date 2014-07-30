'''
Functions that maybe used in other files
Author: Si Li

'''

import itertools
import math
import scipy.misc as misc
import numpy as np
import sys


#return dictionary that contains the same keys as provided
#@paras: dict1, dict2's keys, common or unique
def filter_dict(d, keys, invert=False):
    if invert:
        key_set = set(d.keys()) - set(keys)
    else:
        key_set = set(keys) & set(d.keys())
    return { k: d[k] for k in key_set }


    #return dictionaries that contains the same keys
def common_dict (d1, d2):
	d1 = filter_dict(d1, d2.keys())
	d2 = filter_dict(d2, d1.keys())
	return d1, d2


#return data into 3 classes by set1,2,3
def Seperate_Avg(data, set1, set2, set3):
	tempdict = {}
	keys = set(data.keys())
	for k in keys & set1:
		tempdict[k] = data[k]
	if len(tempdict):
		s1 = np.mean(tempdict.values())
	else:
		s1 = 0
	
	tempdict = {}
	for k in keys & set2:
		tempdict[k] = data[k]
	if len(tempdict):
		s2 = np.mean(tempdict.values())
	else:
		s2 = 0
	
	tempdict = {}
	for k in keys & set3:
		tempdict[k] = data[k]
	if len(tempdict):
		s3 = np.mean(tempdict.values())
	else:
		s3 = 0
	
	return s1, s2, s3

#return data's max min of 3 classes
def Seperate_maxmin(data, set1, set2, set3):
	tempdict = {}
	keys = set(data.keys())
	for k in keys & set1:
		tempdict[k] = data[k]
	s1 = (max(tempdict.values()), min(tempdict.values()))

	tempdict = {}
	for k in keys & set2:
		tempdict[k] = data[k]
	s2 = (max(tempdict.values()), min(tempdict.values()))

	tempdict = {}
	for k in keys & set3:
		tempdict[k] = data[k]
	s3 = (max(tempdict.values()), min(tempdict.values()))

	return s1, s2, s3

#return lists that seperate by blank, no more indicators that 
#represent original number of spaces
def mysplit(s, delim=None):
    return [x for x in s.split(delim) if x]

    
#generate constant values
def constant_factory(value):
	return itertools.repeat(value).next
	
	
#return (x,y) for ecdf plotting
def calc_ecdf (data):
	sorted = np.sort( data )
	#need bias or not?
	yvals = np.arange(len(sorted))/float(len(sorted)) + 0.5/float(len(sorted))
	return sorted, yvals

#show the progress
def update_progress(text, progress):
	#show something like "progress: ####### 99% "
    sys.stdout.write("\r%-s%-26s%-d%%" %(text, '[ '+ '#'*(progress/5) + ' ]', progress))
    sys.stdout.flush()

########################################################
##################IMPORTANT MODEL!!!!!!#################
#cca check time if nothing happens
_Tc = 12.8
#receive a packet
_Trx = 20.0 + _Tc/2.0
_Trx_orw = 30.0 + _Tc/2.0
#time needed for a transmition to sink
_Ttx = 3 + 3.0 + 20 #cca + trans+ack + post(20ms)
_Ttx_orw = 3 + 3.0 + 30 #cca + trans+ack + post(30ms)
_Tpost=20.0
_Tipi = 1000*60.0
_Tibi = 8*1000*60.0
_T_test = 56.5*1000*60.0
###########################CTP##########################
#F: number of forward
#Tao: number of children
#N: number of received beacon (actually it's number of neighbours) 
#L: number of overhearing
#Fail: number of send beacon
#Tw: wakeup interval

def DC_Model_ctp(F, Tao, N, L, Fail, Tw):
	#N = L = (L+N)/2
	prob = ((1.5)*Tw)/_Tipi
	newF = 0
	total_prob = 0
	
	temp = max(int(round(Tao)),int(round(F-1)))
	#temp = int(round(Tao))#int(round(F))
	for i in xrange(1, 13):
		if i <= temp:
			p = misc.comb(temp, i, 1)*prob**i*(1-prob)**(temp-i)
			newF += i*p
			total_prob += p
	#if temp >= 13:
	#	newF += 12*(1-total_prob)
	Ff = F*1.0/(newF + 1)
	print "CTP fextra:{:.2f}".format(newF)
	#Ff = F
	dc = _Tc/Tw + Tw/_Tibi + _Trx/_Tibi*N  + Tw/2/_Tipi*Ff + (_Trx)/_Tipi*L# + Fail*Tw/_Tipi
	return dc*100

def DC_Model_ctp_special(F, Tao, N, L, Fail, Tw):
	#N = L = (L+N)/2
	prob = ((1.5)*Tw)/_Tipi
	newF = 0
	total_prob = 0
	
	temp = max(int(round(Tao)),int(round(F-1)))
	#temp = int(round(Tao))#int(round(F))
	for i in xrange(1, 13):
		if i <= temp:
			p = misc.comb(temp, i, 1)*prob**i*(1-prob)**(temp-i)
			newF += i*p
			total_prob += p
	#if temp >= 13:
	#	newF += 12*(1-total_prob)
	Ff = F*1.0/(newF + 1) 
	print "CTP fextra:{:.2f}".format(newF)
	#Ff = F
	dc = _Tc/Tw + Tw/_Tibi + _Trx/_Tibi*N  + Tw/2/_Tipi*Ff + (_Trx)/_Tipi*L# + Fail*Tw/_Tipi
	return dc*100, Ff
	
def DC_Model_ctp_SN(F, Tao, N, L, Fail, Tw):
	dc = _Tc/Tw + Tw/_Tibi + _Trx/_Tibi*N + _Ttx/_Tipi*F + (_Trx)/_Tipi*(L)# + Fail*Tw/_Tipi
	return dc*100

def DC_Model_ctp_old(F, Tao, N, L, Fail, Tw):
	dc = _Tc/Tw + Tw/_Tibi + _Trx/_Tibi*N  + Tw/2/_Tipi*F + (_Trx)/_Tipi*L# + Fail*Tw/_Tipi
	return dc*100

def DC_Model_ctp_sep(F, Tao, N, L, Fail, Tw):
	return _Tc/Tw*100, Tw/_Tibi*100, _Trx/_Tibi*N*100, Tw/2/_Tipi*F*100, (_Trx)/_Tipi*L*100
###########################ORW##########################
#F: number of forward
#Tao: number of children
#Fs: number of parents
#L: number of overhearing
#Fail: Fail
#Tw: wakeup interval
def DC_Model_orw(F, Tao, Fs, L, Fail, Tw):
	#L=Fs+F
	prob = 2*Tw/(Fs+1)/_Tipi
	newF = 0
	total_prob = 0
	#temp = max(Tao, int(F))
	temp = int(round(F))
	for i in xrange(1, 11):
		if i <= temp:
			p = misc.comb(temp, i, 1)*prob**i*(1-prob)**(temp-i)
			newF += i*p
			total_prob += p
	'''if temp > 12:
		print newF, total_prob'''
	#if temp >= 12:
	#	newF += 12*(1-total_prob)
	Ff = F*1.0/(newF + 1)
	

	dc1 = _Tc/Tw
	dc2 = 1.0/(Fs+1)*F*Tw/_Tipi# + Fail*Tw/_Tipi
	dc3 = L*(_Trx_orw)/_Tipi
	#print "ORW fextra:{:.2f}, F:{:.2f}, Fs:{:.2f}m dc:{:.2f}".format(newF, Ff, Fs, dc2)
	return dc1*100, dc2*100, dc3*100

def DC_Model_orw_special(F, Tao, Fs, L, Fail, Tw):
	#L=Fs+F
	prob = 2*Tw/(Fs+1)/_Tipi
	newF = 0
	total_prob = 0
	#temp = max(Tao, int(F))
	temp = int(round(F))
	for i in xrange(1, 11):
		if i <= temp:
			p = misc.comb(temp, i, 1)*prob**i*(1-prob)**(temp-i)
			newF += i*p
			total_prob += p
	'''if temp > 12:
		print newF, total_prob'''
	#if temp >= 12:
	#	newF += 12*(1-total_prob)
	F = F*1.0/(newF + 1)
	
	print "ORW fextra:{:.2f}".format(newF)
	dc1 = _Tc/Tw
	dc2 = 1.0/(Fs+1)*F*Tw/_Tipi# + Fail*Tw/_Tipi
	dc3 = L*(_Trx_orw)/_Tipi
	return dc1*100+dc2*100+dc3*100, F
	
def DC_Model_orw_SN(F, Tao, Fs, L, Fail, Tw):
	#print F, Tao, Fs, L, FWD 
	dc1 = _Tc/Tw
	dc2 = _Ttx_orw*(F)/_Tipi# + Fail*Tw/_Tipi
	dc3 = L*_Trx_orw/_Tipi
	
	return dc1*100, dc2*100, dc3*100
	
def DC_Model_orw_old(F, Tao, Fs, L, Fail, Tw):
	dc1 = _Tc/Tw
	dc2 = 1.0/(Fs+1)*F*Tw/_Tipi
	dc3 = L*(_Trx_orw)/_Tipi
	return dc1*100, dc2*100, dc3*100

########################################################







