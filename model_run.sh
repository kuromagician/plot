#!/bin/sh

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
rm CTP_Paras.txt
rm ORW_Paras.txt
rm DC_measure_indriya.txt
./model.py -dam 0.25
./model.py -dam 0.5
./model.py -dam 1
./model.py -dam 2
./model.py -dam 4
./model.py -dam 8
./model.py -dam 16
python dataR_W.py -da
