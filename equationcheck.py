import scipy.misc as misc
import matplotlib
import pylab as pl
from tools.functions import *

fextra_ctp = 0
fextra_orw = 0
p_ctp = 1.5/60.0
p_orw = 1/60.0
frange = range(1, 10)
x=frange
Q = 12
y_ctp=[]
y_orw=[]
for F in frange:
	for i in xrange(1, Q):
		fextra_ctp += i*misc.comb(F, i, 1)*p_ctp**i*(1-p_ctp)**(F-i)
		fextra_orw += i*misc.comb(F, i, 1)*p_orw**i*(1-p_orw)**(F-i)
	y_ctp.append(fextra_ctp)
	y_orw.append(fextra_orw)
	
fig = pl.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.plot(x, y_ctp)
ax1.plot(x, y_orw)




###########################CTP##########################
#F: number of forward
#Tao: number of children
#N: number of received beacon (actually it's number of neighbours) 
#L: number of overhearing
#Fail: number of send beacon
#Tw: wakeup interval
F_RL=Tao_RL=3
N_RL=8
L_RL= 8
Fail_RL=0
RL_Paras_ctp = [F_RL, Tao_RL, N_RL, L_RL, Fail_RL, 1000]
###########################ORW##########################
#F: number of forward
#Tao: number of children
#Fs: number of parents
#L: number of overhearing
#Fail: Fail
#Tw: wakeup interval
Fs_RL = 1
RL_Paras_orw = [F_RL, Tao_RL, Fs_RL, L_RL, Fail_RL, 1000]
Q = 12
y_ctp=[]
y_orw=[]
for F in frange:
	RL_Paras_orw[0:2]=RL_Paras_ctp[0:2]=[F,F]
	y_ctp.append(DC_Model_ctp(*RL_Paras_ctp))
	y_orw.append(sum(DC_Model_orw(*RL_Paras_orw)))

fig = pl.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.plot(x, y_ctp)
ax1.plot(x, y_orw)
pl.show()