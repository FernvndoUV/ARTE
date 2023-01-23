import telnetlib, os, time
import numpy as np

"""
When changing the kernel the monitor its moved, so the katcp commands dont work 
well. But I found the actual description of the monitors here
https://github.com/ska-sa/katcp/blob/master/tcpborphserver3/hwmon.c

I couldnt found the absolute values.. but this one are for roach1
https://casper.astro.berkeley.edu/wiki/Roach_monitor_and_management_subsystem


hwmon0: inlet ambient temperature       max:40
hwmon1: outlet ambient temperature      max:40
hwmon2: in0_input --> 1V rail           crit: 5.538
        in1_input --> 1.5V rail         crit: 5.538
        in2_input --> 1.8V rail         crit: 5.538
        in3_input --> 2.5V rail         crit: 5.538
        in4_input --> 3.3V rail         crit: 5.538
        in5_input --> 5V rail           crit: 5.538
        in6_input --> 12V rail          crit: 5.538
        in7_input --> 3.3Vaux rail      crit: 5.538
        curr1_input --> 12V current     
hwmon3: in0_input --> 3.3V current      
        in1_input --> 2.5V current
        in2_input --> 1.8V current
        in3_input --> 1.5V current
        in4_input --> 1V current
        in6_input --> 5V rail
        curr1_input --> 5V current
            
hwmon4: temp1 --> ambient               max:45
        temp2 --> ppc                   max:120
        temp3 --> fpga                  max:80
hwmon5: fan fpga                
hwmon6: fan chasis0
hwmon7: fan chasis1
hwmon8: fan chasis2

"""
class telnet_roach():
    def __init__(self, roach_ip):
        print('Dummy telnet')
        self.msg = ''
    
    def write(self, msg):
        self.msg = msg+'\r\n'
        
    def read_very_eager(self):
        resp = np.random.randint(low=1000, high=30000)
        out = self.msg +resp+'\r\n'
        self.msg = ''
        return out
    
    def close(self):
       print('Closing telnet') 
        


def roach_connect(roach_ip, sleep_time=0.5, debug=False):
    if(debug):
        tn = telnet_roach(roach_ip)
        return tn
    else:
        user = 'root'
        tn = telnetlib.Telnet(roach_ip)
        tn.read_until("login: ".encode())
        tn.write((user + "\n").encode())
        time.sleep(sleep_time)
        tn.read_very_eager()
        time.sleep(sleep_time)
        return tn

def read_ambient_temp(roach_ip, sleep_time=0.5):
    """Read the ambient temperature in degrees
    """
    tn = roach_connect(roach_ip, sleep_time=sleep_time)
    #tn.write('cat /sys/bus/i2c/devices/0-0018/temp1_input \n')
    tn.write('cat /sys/bus/i2c/devices/0-0018/hwmon/hwmon4/temp1_input \n'.encode())
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    time.sleep(sleep_time)
    tn.close()
    temp = float(ans.split('\r\n')[1])
    temp /= 1000.
    return temp


def read_ppc_temp(roach_ip, sleep_time=0.5):
    """Read the Powerpc temperature in degrees
    """
    tn = roach_connect(roach_ip, sleep_time=sleep_time)
    #tn.write('cat /sys/bus/i2c/devices/0-0018/temp2_input \n')
    tn.write('cat /sys/bus/i2c/devices/0-0018/hwmon/hwmon4/temp2_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    time.sleep(sleep_time)
    tn.close()
    temp = float(ans.split('\r\n')[1])
    temp /= 1000.
    return temp

def read_fpga_temp(roach_ip, sleep_time=0.5):
    """Read the ambient temperature in degrees
    """
    tn = roach_connect(roach_ip, sleep_time=sleep_time)
    #tn.write('cat /sys/bus/i2c/devices/0-0018/temp3_input \n')
    tn.write('cat /sys/bus/i2c/devices/0-0018/hwmon/hwmon4/temp3_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    time.sleep(sleep_time)
    tn.close()
    temp = float(ans.split('\r\n')[1])
    temp /= 1000.
    return temp

def pcb_temperature_1(roach_ip, sleep_time=0.5):
    """Read sensor 1 in the pcb
    """
    tn = roach_connect(roach_ip, sleep_time=sleep_time)
    tn.write('cat /sys/bus/i2c/devices/0-004c/hwmon/hwmon0/temp1_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    time.sleep(sleep_time)
    tn.close()
    temp = float(ans.split('\r\n')[1])
    temp /= 1000.
    return temp
    
def pcb_temperature_2(roach_ip, sleep_time=0.5):
    """Read sensor2 in the pcb
    """
    tn = roach_connect(roach_ip, sleep_time=sleep_time)
    tn.write('cat /sys/bus/i2c/devices/0-004e/hwmon/hwmon1/temp1_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    time.sleep(sleep_time)
    tn.close()
    temp = float(ans.split('\r\n')[1])
    temp /= 1000.
    return temp


###
###
###
def read_temperatures(tn, sleep_time=0.1):
    tn.write('cat /sys/bus/i2c/devices/0-0018/hwmon/hwmon4/temp1_input \n'.encode())
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    ans = ans.decode()
    ambient = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0018/hwmon/hwmon4/temp2_input \n'.encode())
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    ans = ans.decode()
    ppc = float(ans.split('\r\n')[1])/1000.
    
    tn.write('cat /sys/bus/i2c/devices/0-0018/hwmon/hwmon4/temp3_input \n'.encode())
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    ans = ans.decode()
    fpga = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-004c/hwmon/hwmon0/temp1_input \n'.encode())
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    ans = ans.decode()
    inlet = float(ans.split('\r\n')[1])/1000. #amp
    
    tn.write('cat /sys/bus/i2c/devices/0-004e/hwmon/hwmon1/temp1_input \n'.encode())
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    ans = ans.decode()
    outlet = float(ans.split('\r\n')[1])/1000. #amp

    return ambient, ppc, fpga, inlet, outlet


def read_voltages(tn, sleep_time=0.1):
    tn.write('cat /sys/bus/i2c/devices/0-0050/hwmon/hwmon2/in0_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    volt1v = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0050/hwmon/hwmon2/in1_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    volt1_5v = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0050/hwmon/hwmon2/in2_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    volt1_8v = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0050/hwmon/hwmon2/in3_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    volt2_5v = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0050/hwmon/hwmon2/in4_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    volt3_3v = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0050/hwmon/hwmon2/in5_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    volt5v = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0050/hwmon/hwmon2/in6_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    volt12v = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0050/hwmon/hwmon2/in7_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    volt3_3v2 = float(ans.split('\r\n')[1])/1000.
    
    tn.write('cat /sys/bus/i2c/devices/0-0051/hwmon/hwmon3/in6_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    volt5v2 = float(ans.split('\r\n')[1])/1000.

    return [volt1v, volt1_5v, volt1_8v, volt2_5v, volt3_3v, 
            volt5v, volt12v, volt3_3v2, volt5v2]



def read_currents(tn, sleep_time=0.1):
    tn.write('cat /sys/bus/i2c/devices/0-0051/hwmon/hwmon3/in0_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    curr3_3v = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0051/hwmon/hwmon3/in1_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    curr2_5v = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0051/hwmon/hwmon3/in2_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    curr1_8v = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0051/hwmon/hwmon3/in3_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    curr1_5v = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0051/hwmon/hwmon3/in4_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    curr1v = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0051/hwmon/hwmon3/in6_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    curr5v = float(ans.split('\r\n')[1])/1000.

    tn.write('cat /sys/bus/i2c/devices/0-0050/hwmon/hwmon2/curr1_input \n')
    time.sleep(sleep_time)
    ans = tn.read_very_eager()
    curr12v = float(ans.split('\r\n')[1])/1000. #amp

    return curr3_3v, curr2_5v, curr1_8v, curr1_5v, curr1v, curr5v, curr12v
    

def read_all_sensors(roach_ip, sleep_time=0.1):
    tn = roach_connect(roach_ip, sleep_time=sleep_time)
    ambient, ppc, fpga, inlet, outlet = read_temperatures(tn, sleep_time=sleep_time)
    [volt1v, volt1_5v, volt1_8v, volt2_5v, volt3_3v, 
            volt5v, volt12v, volt3_3v2, volt5v2] = read_voltages(tn, sleep_time=sleep_time)

    [curr3_3v, curr2_5v, curr1_8v, 
     curr1_5v, curr1v, curr5v, curr12v] = read_currents(tn, sleep_time=sleep_time)
    return [ambient, ppc, fpga, inlet, outlet, volt1v, volt1_5v, volt1_8v, volt2_5v, 
            volt3_3v, volt5v, volt12v, volt3_3v2, volt5v2, curr3_3v, curr2_5v, curr1_8v, 
            curr1_5v, curr1v, curr5v, curr12v]


      



    
