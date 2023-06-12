import PyIndi
import logging, time
import subprocess
import ipdb
from datetime import datetime
###
###
###

class mount_control():
    """
    https://indilib.org/develop/developer-manual/101-standard-properties.html
    https://indilib.org/developers/python-bindings.html
    """
    
    def __init__(self, host='localhost',port=7624, client_telescope='LX200 Autostar',
            server_telescope='indi_lx200autostar', utc_offset=-4, align='polar'):
        """
            host: 
            port:
            client_telescope:   used in the code to connect to the device
            server_telescope:   used by indiserver, it should match the installed driver
            utc_offset:
            align:              alignment, can be 'polar','altaz', 'land'
        """
        self.server_proc = subprocess.Popen(['indiserver', server_telescope])
        time.sleep(1)
        self.client = PyIndi.BaseClient()
        self.client.setServer(host, port)
        self.client.watchDevice(client_telescope)

        #try to connect to the server
        connection = self.client.connectServer()
        if(not connection):
            self.server_proc.terminate()
            raise Exception('Cant connect to the server!')
        ##try to connect to the device
        time.sleep(1)
        self.device = self.client.getDevice(client_telescope)
        device_connect = self.device.getSwitch("CONNECTION")
        time.sleep(1)
        ##retry again with the device
        if(not self.device.isConnected()):
            device_connect[0].s = PyIndi.ISS_ON  ##CONNECT SWITCH
            device_connect[1].s = PyIndi.ISS_OFF ##DISCONNECT SWITCH
            time.sleep(1)
            self.client.sendNewSwitch(device_connect)
            time.sleep(2)
        if(not self.device.isConnected()):
            self.client.disconnectServer()
            self.server_proc.terminate()
            raise Exception('Cant connect to the mount!')
        #configure timezone
        self.utc_mount = self.device.getText('TIME_UTC')
        self.configure_time()
        #configure aligmnet
        self.configure_alignment(align)
        ##get switch that prepares the movement of the mounting
        self.coord_set = self.device.getSwitch('ON_COORD_SET')
        self.coord_set[0].s=PyIndi.ISS_ON  # TRACK  
        self.coord_set[1].s=PyIndi.ISS_OFF # SLEW
        self.coord_set[2].s=PyIndi.ISS_OFF # SYNC
        self.client.sendNewSwitch(self.coord_set)

        self.radec = self.device.getNumber('EQUATORIAL_EOD_COORD')

    def configure_alignment(self,alignment):
        """
        alignment: polar, altaz, land
        """
        align = self.device.getSwitch('Alignment')
        time.sleep(0.5)
        states = [alignment=='polar', alignment=='altaz', alignment=='land']
        for i in range(3):
            align[i].setState(int(states[i]))
        self.client.sendNewSwitch(align)
        time.sleep(0.5)

    def configure_time(self, utc_offset=-4, ):
        """
        set UTC time, UTC offset, geographical coordinates
        utc_offset = 
        latitude = in deg
        longitude = in deg
        """
        utctime = datetime.utcnow()
        utctime = utctime.strftime("%Y-%m-%dT%H:%M:%S") #put it in themount format
        self.utc_mount[0].setText(utctime)
        self.utc_mount[1].setText(("%.2f"%utc_offset))
        self.client.sendNewText(self.utc_mount)
        ##
        #geo_pos = self.device.getNumber('GEOGRAPHIC_COORD')

    def configure_position(self, latitude=-33.395823, longitude=71):
        """
        Seems not be necessary
        """
        geopos = self.client.getNumber('GEOGRAPHIC_COORD')
        geopos[0].setValue(latitude)
        geopos[1].setValue(longitude)
        self.client.sendNewNumber(geopos)


    def prepare_motion(self):
        """
        Action device takes when sent any *_COORD property. 
        N.B: Setting this property does not cause any action but it prepares 
        the mount driver for the next action when any *_COORD number property 
        is received. For example, to sync the mount, first set switch to SYNC 
        and then send the EQUATORIAL_EOD_COORD with the desired sync coordinates.
        
        slew: Slew to a coordinate and stop upon receiving coordinates
        track: Slew to a coordinate and track upon receiving coordinates.
        sync: Accept current coordinate as correct upon receiving coordinates.
        """
        self.coord_set[0].s=PyIndi.ISS_ON  # TRACK  
        self.coord_set[1].s=PyIndi.ISS_OFF # SLEW
        self.coord_set[2].s=PyIndi.ISS_ON # SYNC
        self.client.sendNewSwitch(self.coord_set)

    def move_mount(self, ra, dec):
        """
        It uses JNOW
        ra: Right ascension in hours
        dec: dec in degrees
        """
        ##check the status of the telescope
        if(self.radec.getState() == PyIndi.IPS_BUSY):
            raise Exception("Mount busy!")
        self.prepare_motion()
        time.sleep(0.5)
        self.radec[0].value = ra
        self.radec[1].value = dec
        self.client.sendNewNumber(self.radec)

    def get_radec(self):
        """
        """
        if(self.radec.getState() == PyIndi.IPS_BUSY):
            raise Exception("Mount busy!")
        ra = self.radec[0].getValue()
        dec = self.radec[1].getValue()
        return [ra, dec]
    
    def get_mount_utc_time(self):
        timedata = self.utc_mount[0].getText()
        return timedata
        

    def disconnect(self):
        self.client.disconnectServer()
        self.server_proc.terminate()


