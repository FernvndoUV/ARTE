import serial

class attenuator():
    
    def __init__(self, dev='/dev/ttyUSB0', baudrate=115200):
        self.ser = serial.Serial(dev, baudrate=baudrate)

    def set_attenuation(self, att):
        if(att>31.75):
            raise Exception("att should be in the range (0,31.75)")
        msg = 'wv0'+format(int(att*100),"04d")+'\n'
        self.ser.write(msg.encode())
    
    def close(self):
        self.ser.close()

