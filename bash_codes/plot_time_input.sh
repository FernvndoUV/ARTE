#!/bin/bash
source configuration.sh

plot_snapshots.py \
    --ip         $(echo $ROACH_IP)\
    --snapnames  adcsnap0 adcsnap1 adcsnap2 adcsnap3 \
    --dtype      ">i1" \
    --nsamples   200
