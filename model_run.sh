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

function generate_data(){
	#theses genereate model parameters
	./model.py -$1 0.25
	./model.py -$1 0.5
	./model.py -$1 1
	./model.py -$1 2
	./model.py -$1 4
	./model.py -$1 8
	./model.py -$1 16
	#this generates real measurements
	python dataR_W.py -a
}

generate_data $args
