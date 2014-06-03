#!/bin/bash
name=$(uname -n)
if [ "$1" == "t" ]||[ "$1" == "twist" ]; then
	echo "Using twist data is not recommended"
	exit 0
else
	#clean the original file
	rm -f CTP_Paras.txt
	rm -f ORW_Paras.txt
	rm -f DC_measure_indriya.txt
	#detect which computer it is
	if [ "$name" == "js41" ]; then
		args="am"
	else
		args="dam"
	fi
fi
./model.py -$args 0.25
./model.py -$args 0.5
./model.py -$args 1
./model.py -$args 2
./model.py -$args 4
./model.py -$args 8
./model.py -$args 16
python dataR_W.py -a

#this file is used to generate parameter file
#./model.py -m 0.25
#./model.py -m 0.5
#./model.py -m 1
#./model.py -m 1.5
#./model.py -m 2
#./model.py -m 2.5
#./model.py -m 4
#./model.py -m 6
#./model.py -tm 0.25
#./model.py -tm 0.5
#./model.py -tm 1
#./model.py -tm 2
#./model.py -tm 4
#./model.py -tm 8
