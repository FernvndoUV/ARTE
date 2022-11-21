#!/bin/bash
source configuration.sh
plot_snapshots.py \
    --ip         $(echo $ROACH_IP) \
    `#--bof      $(echo $BOF_FILE)` \
    --upload      \
    --snapnames  snapshot adcsnap1 \
    --dtype      ">b" \
    --nsamples   200
