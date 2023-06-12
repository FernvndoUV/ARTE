import astropy.coordinates as coord
from astropy.time import Time
from mount_control import mount_control
import logging, time
import numpy as np

###Hyperparameters
###
refresh_time = 2    ##minutes 
filename = "positions"
test_time = 6       ##hrs


log_file = 'sun_track_log'
log_level = logging.DEBUG
host='localhost'
port=7624
client_telescope='LX200 Autostar'
server_telescope='indi_lx200autostar'

###
###

iters = test_time*60//refresh_time

##create logger
logging.basicConfig()
logformat = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger("track_logger")
logger.setLevel(log_level)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logformat)
logger.addHandler(console_handler)
if(log_file is not None):
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logformat)
    logger.addHandler(file_handler)

##create file
f = open(filename, 'w')
f.close()


##connect to the mount
logger.info("Attempting to connect the mounting")
mount = mount_control(host=host,
        port=port,
        client_telescope=client_telescope,
        server_telescope=server_telescope)
logger.info("Mount connected")
time.sleep(1)

##array to store the 
data = np.zeros(7)
##[stamp_moving, ra,dec, stamp_read, ra,dec, success]

for i in range(iters):
    mount.configure_time()
    print('Iteration {:}'.format(i))
    time.sleep(refresh_time/2*60)
    t = Time.now()
    sun_pos = coord.get_sun(t)
    ra = sun_pos.ra.hour
    dec = sun_pos.dec.deg
    logger.info("Moving mount to {:},{:}".format(ra,dec))
    ##save the data
    data[0] = time.time()
    data[1] = ra
    data[2] = dec
    try:
        mount.move_mount(ra,dec)
        data[3] = 1
    except:
        logger.warn("Fail!")
        data[3] = 0
    time.sleep(refresh_time/2*60)
    logger.info("Reading ra,dec")
    data[4] = time.time()
    try:
        ra,dec = mount.get_radec()
        logger.info("Read position {:},{:}".format(ra,dec))
        data[5] = ra
        data[6] = dec
    except:
        logger.warn("Fail")
        data[5] = np.nan
        data[6] = np.nan
    ##write data to the file
    with open(filename, 'ab') as f:
        f.write(b'\r\n')
        np.savetxt(f, [data], delimiter=',')
mount.disconnect()
