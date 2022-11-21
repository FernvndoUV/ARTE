#!/bin/bash
source configuration.sh

python2 ../codes/sync_adcs.py  \
    --ip $(echo $ROACH_IP) \
    --bof $(echo $BOF_FILE) \
    --genname TCPIP::192.168.1.34::INSTR \
    --genpow -6 \
    --bandwidth    600 \
    --points  32 \
    --nyquist_zone 3\
    --snapname adcsnap0 adcsnap1 adcsnap2 adcsnap3

