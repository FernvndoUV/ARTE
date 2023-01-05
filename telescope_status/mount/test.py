import logging
import os
import sys
import pty
import time
import datetime
import math
import struct
import socket
import select

import PyIndi

USE_SERIAL=True
USE_TCP=True
TCP_LISTEN_PORT=8091
DEVICE_PORT="/tmp/indi-synscan"
INDI_SERVER_HOST="localhost"
INDI_SERVER_PORT=7624
TELESCOPE_DEVICE="LX200 Autostar"#"EQMod Mount"
TELESCOPE_SIMULATION=True
TELESCOPE_SIMPROP="SIMULATION"


class IndiClient(PyIndi.BaseClient):
    global logger
    def __init__(self):
        super(IndiClient, self).__init__()
        self.isconnected=False
    def newDevice(self, d):
        pass
    def newProperty(self, p):
        pass
    def removeProperty(self, p):
        pass
    def newBLOB(self, bp):
        pass
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        #logger.info("New value for number "+ nvp.name)
        pass
    def newText(self, tvp):
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        logger.info("Message for "+d.getDeviceName()+":"+d.messageQueue(m))
    def serverConnected(self):
        self.isconnected=True
        logger.info("Server connected ("+self.getHost()+":"+str(self.getPort())+")")
    def serverDisconnected(self, code):
        self.isconnected=False
        logger.info("Server disconnected (exit code = "+str(code)+","+str(self.getHost())+":"+str(self.getPort())+")")


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger('pyindi-synscan')

indiclient=IndiClient()
indiclient.setServer(INDI_SERVER_HOST, INDI_SERVER_PORT)
indiclient.watchDevice(TELESCOPE_DEVICE)
device=None


logger.info("Connecting server "+indiclient.getHost()+":"+str(indiclient.getPort()))
serverconnected=indiclient.connectServer()

while (not(serverconnected)):
    logger.info("No indiserver running on "+indiclient.getHost()+":"+str(indiclient.getPort()))
    time.sleep(2)
    serverconnected=indiclient.connectServer()
if not(device):
    device=indiclient.getDevice(TELESCOPE_DEVICE)
    while not(device):
        logger.info("Trying to get device "+TELESCOPE_DEVICE)
        time.sleep(0.5)
        device=indiclient.getDevice(TELESCOPE_DEVICE)
logger.info("Got device "+TELESCOPE_DEVICE)


if not(device.isConnected()):
    device_connect=device.getSwitch("CONNECTION")
    while not(device_connect):
        logger.info("Trying to connect device "+TELESCOPE_DEVICE)
        time.sleep(0.5)
        device_connect=device.getSwitch("CONNECTION")
if not(device.isConnected()):
    device_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
    device_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
    indiclient.sendNewSwitch(device_connect)
while not(device.isConnected()):
    time.sleep(0.2)
logger.info("Device "+TELESCOPE_DEVICE+" connected")


# We want to set the ON_COORD_SET switch to engage tracking after goto
# device.getSwitch is a helper to retrieve a property vector
tel_on_coord_set = device.getSwitch("ON_COORD_SET")
while not tel_on_coord_set:
    time.sleep(0.5)
    tel_on_coord_set = device.getSwitch("ON_COORD_SET")
##set the parameters
tel_on_coord_set[0].s=PyIndi.ISS_ON  # TRACK
tel_on_coord_set[1].s=PyIndi.ISS_OFF # SLEW
tel_on_coord_set[2].s=PyIndi.ISS_OFF # SYNC
indiclient.sendNewSwitch(tel_on_coord_set)


##get coordinates
radec=device.getNumber("EQUATORIAL_EOD_COORD")
while not radec:
    time.sleep(0.5)
    radec=device.getNumber("EQUATORIAL_EOD_COORD")

##print the current position
print("Current position :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))

##move the telescope
radec[0].value = radec[0].value+10.01
radec[1].value = radec[1].value
indiclient.sendNewNumber(radec)
#while(radec.s == PyIndi.IPS_BUSY):
#    print("Moving ", radec[0].value, radec[1].value)
#    time.sleep(2)

radec=device.getNumber("EQUATORIAL_EOD_COORD")
print("New position :\n"+"RA: {:.4f} DEC: {:.4f}".format(radec[0].value, radec[1].value))

