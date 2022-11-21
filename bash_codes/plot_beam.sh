#!/bin/bash
source configuration.sh

python2 ../codes/plot_beam.py \
    --ip $(echo $ROACH_IP) \
    --bof $(echo $BOF_FILE)
