#!/bin/bash

##I change /usr/local/lib/python2.7/dist-packages/calandigital-0.1-py2.7.egg/calandigital/adc5g_devel/SPI.py line 140-146 to modify the
##phase.. when using the 4 adcs the values of the phase are over the 
##-14,14 range so the calibration fails...


calibrate_adc5g.py \
    -i 192.168.0.168\
    -gf 10\
    -gp -8\
    --zdok0snap adcsnap0 adcsnap1 \
    --zdok1snap adcsnap2 adcsnap3 \
    --ns 128\
    -dm -bw 600 -psn -psp
    #-dm -do -di -bw 600 -psn -psp
