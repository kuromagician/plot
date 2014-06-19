import scipy.misc as misc
import matplotlib
import pylab as pl

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
	
pl.plot(x, y_ctp)
pl.plot(x, y_orw)
pl.show()