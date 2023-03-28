#!/bin/bash

###configure the dram ethernet interface to 10.0.0.29
#sudo ip addr add 10.0.0.29/24 dev enp4s0
###


### confgure the 10gbe ethernet interface to 192.168.2.10 and tweak some os features
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

##start python environment
source ~/roach_env/bin/activate

python2 init.py

##calibrate the ADCs
bash_codes/calibrate.sh

##calibrate digital gain for the DRAM
#

