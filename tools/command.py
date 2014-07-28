import getopt
import sys
import reader
import twistReader as Treader
import simReader as Sreader

def main(argv):
	result = {'kill':False, 'simple':False, 'lim':0, 'twist':False, \
			  'connectivity':False, 'experiment':False, 'model':False,\
			  'wakeup':float(1.5), 'check':False, 'desktop':False,\
			  'postpone':False, 'simulation': False, 'numnodes':36}
	try:
		opts, args = getopt.getopt(argv,"ehdl:m:kstcapin:",["limit","twist","experiment","cca"])
	except getopt.GetoptError:
		print 'plot.py -l <energy limit>\
             \n        -k \tkill some nodes\
             \n        -s \tsimple version\
             \n        -t \tuse files from twist\
             \n        -c \tconnectivity test\
             \n        -e \ttest files\
             \n        -h \tshow help\
			 \n        -m <wakeup interval>\t Set wakeup interval\
			 \n        -p \tignore first 10 minutes\
			 \n        -i \tuse simulation\
			 \n        -n \tspecify how many nodes in simulation'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'plot.py -l <energy limit>'
			sys.exit()
		elif opt in ("-d"):
			result['desktop'] = True
		elif opt in ("-l", "--limit"):
			result['lim'] = int(arg, 16)
		elif opt in ("-k",):
			result['kill'] = True
		elif opt in ("-s",):
			result['simple'] = True
		elif opt in ("-t", "--twist"):
			result['twist'] = True
		elif opt in ("-c",):
			result['connectivity'] = True
		elif opt in ("-e", "--experiment"):
			result['experiment'] = True
		elif opt in ("-m", "--model"):
			result['model'] = True
			result['wakeup'] = float(arg)
		elif opt in ("-a", "--cca"):
			result['check'] = True
		elif opt in ("-p",):
			result['postpone'] = True
		elif opt in ("-i",):
			result['simulation'] = True
		elif opt in ("-n",):
			result['numnodes'] = int(arg)
	return result

	
	
def getfile(args):
	ELIMIT = args['lim']
	#print args
	if args['desktop']:
		base_path = '/home/nagatoyuki/Thesis/Traces/Indriya/'
	else:
		base_path = '/media/Data/ThesisData/Indriya/'
	FileNames = {'OrwDebug':('23739.dat',), 'CtpDebug':('24460.dat',), 
	             'CtpData':('24463.dat',), 'ConnectDebug':('25593.dat',),
	             'OrwNt':('23738.dat',)}
	FileDict = {}
	lookup_dic = {}
	props = {'SINK_ID':1, 'prefix':'Indriya_', 'timeratio':1000.0, 'time_TH':-1}
	props['energy'] = hex(ELIMIT)
	#
	#files are from TWIST
	#
	if args['twist']:
		props['SINK_ID'] = 153
		props['timeratio'] = 1000000.0
		if args['postpone']:
			props['time_TH'] = props['timeratio']*60*10
		if args['desktop']:
			base_path = '/home/nagatoyuki/Thesis/Traces/Twist/'
		else:
			base_path = '/media/Data/ThesisData/Twist/'
		props['prefix']='Twist_'
		#
		# use wakeup time as parameters, Indriya
		if args['model']:
			if not args['check']:
				if args['wakeup'] == 0.25:
					limited_ctp = 'trace_20140515_120916.0.txt'
					limited_orw = 'trace_20140515_132005.1.txt'
				elif args['wakeup'] == 0.5:
					limited_ctp = 'trace_20140515_145530.2.txt'
					limited_orw = 'trace_20140515_160513.3.txt'
				elif args['wakeup'] == 1:
					limited_ctp = 'trace_20140515_174113.4.txt'
					limited_orw = 'trace_20140515_185012.5.txt'
				elif args['wakeup'] == 2:
					limited_ctp = 'trace_20140515_200012.6.txt'
					limited_orw = 'trace_20140515_210915.7.txt'
				elif args['wakeup'] == 4:
					limited_ctp = 'trace_20140515_221814.8.txt'
					limited_orw = 'trace_20140515_232715.9.txt'
				elif args['wakeup'] == 8:
					limited_ctp = 'trace_20140516_020516.10.txt'
					limited_orw = 'trace_20140516_031415.11.txt'
			else:
				if args['wakeup'] == 0.25:
					limited_ctp = 'trace_20140516_171413.18.txt'
					limited_orw = 'trace_20140516_182314.19.txt'
				elif args['wakeup'] == 0.5:
					limited_ctp = 'trace_20140516_115018.14.txt'
					limited_orw = 'trace_20140516_125914.15.txt'
				elif args['wakeup'] == 1:
					limited_ctp = 'trace_20140517_004915.24.txt'
					limited_orw = 'trace_20140516_160435.17.txt'
				elif args['wakeup'] == 2:
					limited_ctp = 'trace_20140516_043214.12.txt'
					limited_orw = 'trace_20140516_054116.13.txt'
				elif args['wakeup'] == 4:
					limited_ctp = 'trace_20140516_193515.20.txt'
					limited_orw = 'trace_20140516_204414.21.txt'
				elif args['wakeup'] == 8.7:
					limited_ctp = 'trace_20140516_215516.22.txt'
					limited_orw = 'trace_20140516_230416.23.txt'
			FileDict['CtpDebug'], _, _, FileDict['CtpData'] = Treader.load(base_path+limited_ctp) 
			FileDict['OrwDebug'], FileDict['OrwNt'], _, _ = Treader.load(base_path+limited_orw)
			return FileDict, props
		
		if ELIMIT == 0x1000:
			#limited_ctp = 'trace_20140420_234914.3.txt'
			#limited_orw = 'trace_20140420_212823.2.txt'
			limited_ctp = 'trace_20140517_133316.27.txt'
			#limited_ctp = 'trace_20140517_195115.29.txt'
			limited_orw = 'trace_20140517_164214.28.txt'
		elif ELIMIT == 0x2000:
			limited_ctp = 'trace_20140518_002516.30.txt'
			limited_orw = 'trace_20140518_033416.31.txt'
		elif ELIMIT == 0x4000:
			limited_ctp = 'trace_20140518_101919.33.txt'
			limited_orw = 'trace_20140518_132824.34.txt'
		elif ELIMIT == 0:
			limited_ctp = 'trace_20140420_182200.0.txt'
			limited_orw = 'trace_20140420_194245.1.txt' 
		#load files
		FileDict['CtpDebug'], _, _, FileDict['CtpData'] = Treader.load(base_path+limited_ctp) 
		FileDict['OrwDebug'], FileDict['OrwNt'], _, _ = Treader.load(base_path+limited_orw) 
	#
	#files are from Simulation
	#
	elif args['simulation']:
		props['timeratio'] = 1.0
		if args['postpone']:
			props['time_TH'] = props['timeratio']*60*10
		if args['model']:
			if args['wakeup'] == 1:
				if args['numnodes'] == 81:
					limited_ctp = "../Simulation/S_CTP_1s_1h.txt"
					limited_orw = "../Simulation/S_ORW_1s_1h.txt"
				else:
					limited_ctp = "../Simulation/CTP_1s.txt"
					#limited_orw = "../Simulation/ORW_1s.txt"
					limited_orw = "../Simulation/ORW_test_cca.txt"
			elif args['wakeup'] == 2:
				#limited_ctp = "../Simulation/CTP_2s.txt"
				#limited_orw = "../Simulation/ORW_2s.txt"
				limited_ctp = "../Simulation/S_CTP_2s_N36_D10s_1h.txt"
				limited_orw = "../Simulation/S_ORW_2s_N36_D10s_1h.txt"
			elif args['wakeup'] == 4:
				limited_ctp = "../Simulation/S_CTP_4s_N36_D10s_1h.txt"
				limited_orw = "../Simulation/S_ORW_4s_N36_D10s_1h.txt"
			elif args['wakeup'] == 8:
				limited_ctp = "../Simulation/S_CTP_8s_N36_D10s_1h.txt"
				limited_orw = "../Simulation/S_ORW_8s_N36_D10s_1h.txt"
			elif args['wakeup'] == 0.5:
				limited_ctp = "../Simulation/S_CTP_05s_N36_D10s_1h.txt"
				limited_orw = "../Simulation/S_ORW_05s_N36_D10s_1h.txt"
			elif args['wakeup'] == 0.25:
				limited_ctp = "../Simulation/S_CTP_025s_N36_D10s_1h.txt"
				limited_orw = "../Simulation/S_ORW_025s_N36_D10s_1h.txt"
			else:
				limited_ctp = "../Simulation/S_CTP_r9c4_R35_1h.txt"
				limited_orw = "../Simulation/S_ORW_r9c4_D10s_1h.txt"
		elif args['lim']:
			if ELIMIT == 0x1000:
				limited_ctp = "../Simulation/CTP_el1000_2h.txt"
				limited_orw = "../Simulation/ORW_el1000_2h.txt"
			elif ELIMIT == 0x2000:
				if args['numnodes'] == 36:
					limited_ctp = "../Simulation/CTP_el2000_2h45m.txt"
					limited_orw = "../Simulation/ORW_el2000_2h45m.txt"
				elif args['numnodes'] == 81:
					#limited_ctp = "../Simulation/CTP_el2000_N81_R35_5h.txt"
					#limited_orw = "../Simulation/ORW_el2000_N81_R35_2h33.txt"
					limited_ctp = "../Simulation/S_CTP_el2000_R35_N81_7h.txt"
					limited_orw = "../Simulation/ORW_el2000_N81_R35_2h33.txt"
			elif ELIMIT == 0x4000:
				if args['numnodes'] == 36:
					limited_ctp = "../Simulation/CTP_el4000_N81_R35_7h.txt"
					limited_orw = "../Simulation/ORW_el4000_5h_144.txt"
				elif args['numnodes'] == 81:
					#limited_ctp = "../Simulation/CTP_el4000_N81_R35_7h.txt"
					#limited_orw = "../Simulation/ORW_el4000_N81_R35_3h15_.txt"
					limited_ctp = "../Simulation/S_CTP_el4000_R35_N81_7h.txt"
					limited_orw = "../Simulation/ORW_el4000_N81_R35_3h15_.txt"
			elif ELIMIT == 0x8000:
				if args['numnodes'] == 36:
					limited_ctp = "../Simulation/CTP_el8000_7h50.txt"
					limited_orw = "../Simulation/ORW_el8000_9h.txt"
				elif args['numnodes'] == 81:
					limited_ctp = "../Simulation/S_CTP_el8000_R35_N81_7h.txt"
					limited_orw = "../Simulation/S_ORW_el8000_R35_N81_7h.txt"
		#this is for testing only, any files can be listed here
		elif args['experiment']:
			limited_ctp = "../Simulation/S_CTP_el8000_R35_N81_7h.txt"
			limited_orw = "../Simulation/S_ORW_el8000_R35_N81_7h.txt"
		FileDict['CtpDebug'], FileDict['CtpData'], _, _ = Sreader.loadDebug(base_path+limited_ctp)
		_, _, FileDict['OrwDebug'], FileDict['OrwNt']	= Sreader.loadDebug(base_path+limited_orw)
	#
	#files are from Indriya
	#
	else:
		#
		# use wakeup time as parameters
		if args['postpone']:
			props['time_TH'] = props['timeratio']*60*10
		if args['connectivity']:
			#power=full
			#folder = 'data-49759'
			#power=11
			#folder = 'data-49758'
			#power=full, all nodes
			#folder = 'data-48413'
			#power=11, all nodes
			#folder = 'data-49995'
			folder = 'data-50224'
			FileDict['ConnectDebug'] = reader.load_C_Data(base_path+folder, FileNames['ConnectDebug'])
			return FileDict, props
		if args['experiment']:
			#this is from faisal's account, only with 29 nodes, 1h
			props['SINK_ID'] = 136
			FileNames['CtpDebug'] = ('26102.dat',)
			FileNames['CtpData'] = ('26103.dat',)
			FileNames['OrwDebug'] = ('26108.dat',)
			FileNames['OrwNt'] = ('26107.dat',)
			limited_ctp = 'data-50231'
			limited_orw = 'data-50232'
		if args['model']:
			if not args['check']:
				wakeup_i = [0.25, 0.5, 1, 1.5, 2, 2.5, 4, 6, 16]
				FileCollection_orw = ['data-48680', 'data-48564', 'data-48640', 'data-48627', 
							'data-48623', 'data-48631', 'data-48646', 'data-48714', 'data-48775']
				FileCollection_ctp = ['data-48672', 'data-48556', 'data-48639', 'data-48641', 
							'data-48637', 'data-48642', 'data-48651', 'data-48710', 'data-48774']
			else:
				wakeup_i = [0.25, 0.5, 1, 2, 4, 8, 16]
				'''#1st result. This is wrong log of neighbour
				FileCollection_orw = ['data-48936', 'data-48934', 'data-48933', 'data-48932', 
							'data-48931', 'data-48930', 'data-48952']
				FileCollection_ctp = ['data-48929', 'data-48928', 'data-48925', 'data-48924', 
							'data-48923', 'data-48922', 'data-48949']
				'''#2nd
				'''
				FileCollection_orw = ['data-49167', 'data-49137', 'data-49175', 'data-49104', 
							'data-48931', 'data-48930', 'data-49088']
				FileCollection_ctp = ['data-49023', 'data-49029', 'data-49030', 'data-49045', 
							'data-49054', 'data-49059', 'data-49079']'''
				#latest results
				FileCollection_orw = ['data-49683', 'data-49664', 'data-49662', 'data-49637', 
							'data-49635', 'data-49715', 'data-49413']
				FileCollection_ctp = ['data-49747', 'data-49733', 'data-49731', 'data-49718', 
							'data-49714', 'data-49709', 'data-49698']
				
			if args['wakeup'] not in wakeup_i:
				print "No traces available for this setting, exit"
				sys.exit(0)
			for k, ORW, CTP in zip(wakeup_i, FileCollection_orw, FileCollection_ctp):
				lookup_dic[k] = (CTP, ORW)
			limited_ctp = lookup_dic[args['wakeup']][0]
			limited_orw = lookup_dic[args['wakeup']][1]
		elif args['kill']:
			#These are only for the 1 hour kill
			FileNames['CtpDebug'] = ('26099.dat',)
			FileNames['CtpData'] = ('26100.dat',)
			if ELIMIT == 0x1000:
				#power=11, 1h
				limited_ctp = 'data-49766'
				limited_orw = 'data-49755'
			elif ELIMIT == 0x2000:
				#power=31, 1h
				#limited_ctp = 'data-49762'
				#limited_orw = 'data-49763'
				#power=11, 3h
				FileNames['CtpDebug'] = ('26102.dat',)
				FileNames['CtpData'] = ('26103.dat',)
				FileNames['OrwDebug'] = ('26108.dat',)
				FileNames['OrwNt'] = ('26107.dat',)
				limited_ctp = 'data-49270'
				limited_orw = 'data-50125'
		elif args['lim']:
			if ELIMIT == 0:
				#if not CONNECT:
				limited_ctp = 'data-47464'
				limited_orw = 'data-47470'
				#else:
				#	limited_ctp = 'data-47933'
				#	limited_orw = 'data-47934'
			elif ELIMIT == 0xA00:
				limited_ctp = 'data-47436'
				limited_orw = 'data-47438'
			elif ELIMIT == 0x1000:
				FileNames['CtpDebug'] = ('26102.dat',)
				FileNames['CtpData'] = ('26103.dat',)
				FileNames['OrwDebug'] = ('26108.dat',)
				FileNames['OrwNt'] = ('26107.dat',)
				#29 connected nodes, power=11
				props['SINK_ID'] = 136
				#limited_ctp = 'data-49283'
				limited_ctp = 'data-50225'
				limited_orw = 'data-50226'
				#this is lower 36 nodes
				#limited_ctp = 'data-50051'
				#limited_orw = 'data-50160'
				'''if not CONNECT:
					limited_ctp = 'data-47540'
					limited_orw = 'data-47398'
				else:
					limited_ctp = 'data-48017'
					limited_orw = 'data-48019'
				'''
			elif ELIMIT == 0x1200:
				limited_ctp = 'data-47546'
				limited_orw = 'data-47581'
			elif ELIMIT == 0x1400:
				limited_ctp = 'data-47566'
				limited_orw = 'None'
			elif ELIMIT == 0x2000:
				FileNames['CtpDebug'] = ('26102.dat',)
				FileNames['CtpData'] = ('26103.dat',)
				FileNames['OrwDebug'] = ('26108.dat',)
				FileNames['OrwNt'] = ('26107.dat',)
				limited_ctp = 'data-49272'
				limited_orw = 'data-49273'
			else:
				print "Energy limit", hex(ELIMIT), "is not available, exit"
				sys.exit()
		#load files
		FileDict['CtpDebug'] = reader.loadDebug(base_path+limited_ctp, FileNames['CtpDebug']) 
		FileDict['CtpData'] = reader.loadDataMsg(base_path+limited_ctp, FileNames['CtpData']) 
		FileDict['OrwDebug'] = reader.loadDebug(base_path+limited_orw, FileNames['OrwDebug']) 
		FileDict['OrwNt'] = reader.loadNtDebug(base_path+limited_orw, FileNames['OrwDebug']) 
	return FileDict, props
