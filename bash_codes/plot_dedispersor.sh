#!/bin/bash
source configuration.sh

python2 ../codes/plot_dedispersor.py \
    --ip    $(echo $ROACH_IP) \
    --DM    45 90 135 180 225 270 315 360 405 450 495

    
    
