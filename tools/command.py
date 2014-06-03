import getopt
import sys
import reader
import twistReader as Treader

def main(argv):
	result = {'kill':False, 'simple':False, 'lim':0, 'twist':False, \
			  'connected':False, 'experiment':False, 'model':False,\
			  'wakeup':float(1.5), 'check':False, 'desktop':False}
	try:
		opts, args = getopt.getopt(argv,"ehdl:m:kstca",["limit","twist","experiment","cca"])
	except getopt.GetoptError:
		print 'plot.py -l <energy limit>\
             \n        -k \tkill some nodes\
             \n        -s \tsimple version\
             \n        -t \tuse files from twist\
             \n        -c \tgood connectivity\
             \n        -e \ttest files'
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
			result['connected'] = True
		elif opt in ("-e", "--experiment"):
			result['experiment'] = True
		elif opt in ("-m", "--model"):
			result['model'] = True
			result['wakeup'] = float(arg)
		elif opt in ("-a", "--cca"):
			result['check'] = True
	return result

	
	
def getfile(args):
	ELIMIT = args['lim']
	CONNECT = args['connected']
	if args['desktop']:
		base_path = '/home/nagatoyuki/Thesis/Traces/Indriya/'
	else:
		base_path = '/media/Data/ThesisData/Indriya/'
	FileNames = {'OrwDebug':('23739.dat',), 'CtpDebug':('24460.dat',), 
	             'CtpData':('24463.dat',), 'ConnectDebug':('25593.dat',),
	             'OrwNt':('23738.dat',)}
	FileDict = {}
	props = {'SINK_ID':1, 'prefix':'Indriya_', 'timeratio':1000.0}
	props['energy'] = hex(ELIMIT)
	
	#
	#files are from Indriya
	#
	if not args['twist']:
		#
		# use wakeup time as parameters
		#
		if args['model']:
			if not args['check']:
				if args['wakeup'] == 0.5:
					limited_ctp = 'data-48556'
					limited_orw = 'data-48564'
				elif args['wakeup'] == 1.5:
					limited_ctp = 'data-48556'
					limited_orw = 'data-48627'
				elif args['wakeup'] == 1:
					limited_ctp = 'data-48639'
					limited_orw = 'data-48640'
				elif args['wakeup'] == 2:
					limited_ctp = 'data-48633'
					#limited_orw = 'data-48632'
					limited_orw = 'data-48623'
				elif args['wakeup'] == 2.5:
					limited_ctp = 'data-48556'
					limited_orw = 'data-48631'
				elif args['wakeup'] == 4:
					limited_ctp = 'data-48651'
					limited_orw = 'data-48646'
				elif args['wakeup'] == 0.25:
					limited_ctp = 'data-48672'
					limited_orw = 'data-48680'
				elif args['wakeup'] == 6:
					limited_ctp = 'data-48710'
					limited_orw = 'data-48714'
				elif args['wakeup'] == 16:
					limited_ctp = 'data-48774'
					limited_orw = 'data-48775'
			else:
				if args['wakeup'] == 0.25:
					limited_ctp = 'data-48929'
					limited_orw = 'data-48936'
				elif args['wakeup'] == 0.5:
					limited_ctp = 'data-48928'
					limited_orw = 'data-48934'
				elif args['wakeup'] == 1:
					limited_ctp = 'data-48925'
					limited_orw = 'data-48933'
				elif args['wakeup'] == 2:
					limited_ctp = 'data-48924'
					limited_orw = 'data-48932'
				elif args['wakeup'] == 4:
					limited_ctp = 'data-48923'
					limited_orw = 'data-48931'
				elif args['wakeup'] == 8:
					#limited_ctp = 'data-48922'
					limited_ctp = 'data-48993'
					limited_orw = 'data-48930'
				elif args['wakeup'] == 16:
					limited_ctp = 'data-48949'
					limited_orw = 'data-48952'
			FileDict['CtpDebug'] = reader.loadDebug(base_path+limited_ctp, FileNames['CtpDebug']) 
			FileDict['CtpData'] = reader.loadDataMsg(base_path+limited_ctp, FileNames['CtpData']) 
			FileDict['OrwDebug'] = reader.loadDebug(base_path+limited_orw, FileNames['OrwDebug']) 
			FileDict['OrwNt'] = reader.loadNtDebug(base_path+limited_orw, FileNames['OrwNt']) 
			return FileDict, props
		if args['check']:
			limited_ctp = 'data-48718'
			limited_orw = 'data-48719'
		#file prefix
		if ELIMIT == 0:
			if not CONNECT:
				limited_ctp = 'data-47464'
				limited_orw = 'data-47470'
			else:
				limited_ctp = 'data-47933'
				limited_orw = 'data-47934'
		elif ELIMIT == 0xA00:
			limited_ctp = 'data-47436'
			limited_orw = 'data-47438'
		elif ELIMIT == 0x1000:
			if not CONNECT:
				limited_ctp = 'data-47540'
				limited_orw = 'data-47398'
			else:
				limited_ctp = 'data-48017'
				limited_orw = 'data-48019'
		elif ELIMIT == 0x1200:
			limited_ctp = 'data-47546'
			limited_orw = 'data-47581'
		elif ELIMIT == 0x1400:
			limited_ctp = 'data-47566'
			limited_orw = 'None'
		else:
			print "Energy limit", hex(ELIMIT), "is not available, exit"
			sys.exit()
		#load files
		FileDict['CtpDebug'] = reader.loadDebug(base_path+limited_ctp, FileNames['CtpDebug']) 
		FileDict['CtpData'] = reader.loadDataMsg(base_path+limited_ctp, FileNames['CtpData']) 
		FileDict['OrwDebug'] = reader.loadDebug(base_path+limited_orw, FileNames['OrwDebug']) 
	#
	#files are from TWIST
	#
	else:
		props['SINK_ID'] = 153
		props['timeratio'] = 1000000.0
		
		if args['desktop']:
			base_path = '/home/nagatoyuki/Thesis/Traces/Twist/'
		else:
			base_path = '/media/Data/ThesisData/Twist/'
		props['prefix']='Twist_'
		#
		# use wakeup time as parameters, Indriya
		#
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
	return FileDict, props
