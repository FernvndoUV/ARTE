#!/bin/bash
source configuration.sh

#set up the 10gbe interface
#sudo ip addr add 192.168.2.10/24 dev enp2s0
#enable jumbo frame
sudo ip link set enp2s0 mtu 9000        
#kernel configs
sudo sysctl -w net.core.rmem_max=26214400
sudo sysctl -w net.core.rmem_default=26214400
sudo sysctl -w net.core.optmem_max=26214400
sudo sysctl -w net.core.optmem_max=26214400
sudo sysctl -w net.core.netdev_max_backlog=300000

#increase kernel buffers
sudo ethtool -G enp2s0 rx 4096
#increase pci mmrbc (this depend on the pci address of your nic)
sudo setpci -v -d 8086:10fb e6.b=2e
#put it up
#sudo ip link set up dev enp2s0

sleep 3



python2 ../codes/logger.py \
    --folder    ../logger\
    --filetime  5\
    --totaltime 360\
    --roach_ip 10.17.89.91\
    --cal 1\
    --dms 45 90 135 180 225 270 315 360 405 450 495
