#!/bin/bash

python2 upload_curve.py \
    --upload \
    --dm 200 \
    --v_min 3 \
    --v_max 8 \
    --freq 1200 1800\
    --genname TCPIP::192.168.1.45::INSTR \
    --npts 16384\
    --trigger


