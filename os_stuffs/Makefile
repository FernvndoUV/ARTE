XGBE_INTERFACE=enp1s0
ROACH_GBE_INTERFACE=eno2
XGBE_FILE=~/init_xgbe.sh
ROACH_IP=192.168.0.168

.ONESHELL:
basic_stuffs:
	#add arte as sudoers, must be run as root
	#usermod -aG sudo arte
	##add sbin to the path
	echo "PATH=$PATH:/usr/local/sbin:/usr/sbin/" >> ~./bashrc
	bash .bashrc
	#install ssh
	sudo apt install -y openssh-server
	sudo systemctl restart ssh
	sudo apt install -y vim git curl
	#get vim-plug
	curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
	##get nice vim packages..
	wget https://raw.githubusercontent.com/sebajor/verilog_codes/main/vimrc
	mv vimrc ~/.vimrc
	vim -E ~/.vimrc -c PlugInstall -c q -c q
	##add anydesk
	sudo apt install -y gnupg2
	wget -qO - https://keys.anydesk.com/repos/DEB-GPG-KEY | sudo apt-key add -
	echo "deb http://deb.anydesk.com/ all main" | sudo tee /etc/apt/sources.list.d/anydesk-stable.list
	sudo apt update
	sudo apt install -y anydesk
	

xgbe_stuffs:
	#add ethtool
	sudo apt -y install ethtool 
	echo "TODO: configure ethernet ports"
	##modify the default setup of the 10gbe interface
	sudo echo "auto $(XGBE_INTERFACE)" > /etc/network/interfaces.d/$(XGBE_INTERFACE)
	sudo echo "iface $(XGBE_INTERFACE) inet static" >> /etc/network/interfaces.d/$(XGBE_INTERFACE)
	sudo echo "	address 192.168.2.10" >> /etc/network/interfaces.d/$(XGBE_INTERFACE)
	sudo echo "	netmask 255.255.255.0" >> /etc/network/interfaces.d/$(XGBE_INTERFACE)
	sudo echo "	gateway 192.168.2.1" >> /etc/network/interfaces.d/$(XGBE_INTERFACE)
	##modify the default setup of the 1gbe interface that goes to roach
	sudo echo "auto $(ROACH_GBE_INTERFACE)" > /etc/network/interfaces.d/$(ROACH_GBE_INTERFACE)
	sudo echo "iface $(ROACH_GBE_INTERFACE) inet static" >> /etc/network/interfaces.d/$(ROACH_GBE_INTERFACE)
	sudo echo "	address 10.0.0.29" >> /etc/network/interfaces.d/$(ROACH_GBE_INTERFACE)
	sudo echo "	netmask 255.255.255.0" >> /etc/network/interfaces.d/$(ROACH_GBE_INTERFACE)
	sudo echo "	gateway 192.168.2.1" >> /etc/network/interfaces.d/$(ROACH_GBE_INTERFACE)
	#create the initialization file
	touch $(XGBE_FILE)
	echo "#!/bin/bash" >> $(XGBE_FILE)
	echo "#set the eth dev to 192.168.2.10" >> $(XGBE_FILE)
	echo "sudo ip addr add 192.168.2.10/24 dev $(XGBE_INTERFACE)" >> $(XGBE_FILE)
	echo "#enable jumbo frames" >> $(XGBE_FILE)
	echo "sudo ip link set enp2s0 mtu 9000" >> $(XGBE_FILE)
	echo "#kernel configs" >> $(XGBE_FILE)
	echo "sudo sysctl -w net.core.rmem_max=26214400" >> $(XGBE_FILE)
	echo "sudo sysctl -w net.core.rmem_default=26214400" >> $(XGBE_FILE)
	echo "sudo sysctl -w net.core.optmem_max=26214400" >> $(XGBE_FILE)
	echo "sudo sysctl -w net.core.optmem_max=26214400" >> $(XGBE_FILE)
	echo "sudo sysctl -w net.core.netdev_max_backlog=300000" >> $(XGBE_FILE)
	echo "#increase kernel buffers" >> $(XGBE_FILE)
	echo "sudo ethtool -G enp2s0 rx 4096" >> $(XGBE_FILE)
	##pci stuffs (CHECK!!!)
	echo "#increase the pci mmrbc, check https://glenewhittenberg.blogspot.com/2016/03/intel-x520-da2-performance-tuning-for.html" >> $(XGBE_FILE)
	echo "sudo setpci -v -d 8086:10fb e6.b=2e" >> $(XGBE_FILE)	
	echo "sudo ip link set up dev $(XGBE_INTERFACE)" >> $(XGBE_FILE)


	
roach_stuffs:
	sudo apt install -y python3 python2 g++ gcc python3-pip
	sudo apt install -y python2-dev python-tk
	#pip install virtualenv
	sudo apt install -y python3-virtualenv
	virtualenv -p /usr/bin/python2 ~/roach_env 
	source ~/roach_env/bin/activate
	mkdir tmp 
	cd tmp 
	git clone https://github.com/sebajor/calandigital
	pip install -r calandigital/REQUIREMENTS
	pip install calandigital/
	sudo rm -r calandigital/
	#install ipython
	pip install ipython
	##get arte folders
	cd 
	git clone https://github.com/sebajor/ARTE-control/	
	#alias to initiate the environment
	echo "alias start_env="source ~/roach_env/bin/activate" >> ~/.bashrc"

gpu_stuffs:
	echo "Nothing here yet"

mount_stuffs:
	echo "Nothing here yet"
