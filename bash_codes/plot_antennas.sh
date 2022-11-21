#!/bin/bash
source configuration.sh

python2 ../codes/plot_antennas.py \
    --ip    $(echo $ROACH_IP) 
    
