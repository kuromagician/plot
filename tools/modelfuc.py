

def DC_Model_ctp(F, Tao, N, L, Fail, Tw):
	#dc = Tc/Tw + Tw/Tibi + Trx/Tibi*N/6 + (Fail)*Tw/Tipi + Tw/5/Tipi*F + (Trx)/Tipi*L
	dc = Tc/Tw + Tw/Tibi + Trx/Tibi*N/6 + Tw/2/Tipi*F + (Trx)/Tipi*L
	return dc*100
	
def DC_Model_ctp_SN(F, Tao, N, L, Fail, Tw):
	#print "F:{:2f} L:{:2f} Tao:{:2f} N:{:2f}".format(F, L, Tao, N)
	#dc = Tc/Tw + Tw/Tibi  + Ttx/Tipi*F*Tao + (Trx)/Tipi*L
	dc = Tc/Tw + Tw/Tibi + Trx/Tibi*N/6 + Ttx/Tipi*F + (Trx)/Tipi*L
	return dc*100