#!/bin/bash
source configuration.sh

python2 ../codes/plot_rfi_signals.py \
    --ip    $(echo $ROACH_IP) 
