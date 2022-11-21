#!/bin/bash
source configuration.sh
initialize_roach.py \
    --ip     $(echo $ROACH_IP) \
    --bof    $(echo $BOF_FILE) \
    --upload
