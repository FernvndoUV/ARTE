import socket
import time

class external_sensors():

    def __init__(self, ip='192.168.0.15', port=1000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
    
    def ask_measure(self, _sleep=0.01):
        self.sock.send('ARTE:EXTERNAL_SENSOR'.encode())
        time.sleep(_sleep)
        data = self.sock.recv(100)
        data = data.decode()
        return data
