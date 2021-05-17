#
# from telnetlib import Telnet
#
#
# print("begin")
# # HOST = "http://192.168.1.176:23/"
# i = 0
# while True:
#     with Telnet('192.168.1.165', 23) as tn:
#         print(tn.read_until(b"\n"))
#     # if(i > 10)
#     #
#     i += 1
# tn.write(user + "\n")
# print("end")

'''
Gas Sensor All in One
Communication Driver
'''

import serial
import logging
import time
from driver.AiO.protoc import *
import telnetlib

class AiO(object):

    def __init__(self, ):
        self.tn = telnetlib.Telnet()
        try:
            # self.device = serial.Serial(
            #         port=port,
            #         baudrate=baudrate,
            #         timeout=2,
            #         parity=serial.PARITY_NONE,
            #         stopbits=serial.STOPBITS_ONE,
            #         bytesize=serial.EIGHTBITS
            #     )
            # self.tn = telnetlib.Telnet(host_ip,port=23)
            self.tn.open(host_ip,port=23)
        except:
            logging.warning('%sconnect fail'%host_ip)
            # return False
            pass

        self.protoc_manager = AioProtocol()

    def valveSet(self, index, state):
        cmd = self.protoc_manager.packValveSet(index, state)
        self.device.write(cmd)

    def pumpPwm(self, speed):
        cmd = self.protoc_manager.packPumpPwn(speed)
        self.device.write(cmd)

    def airFlow(self):
        cmd = self.protoc_manager.packAirFlow()
        self.device.write(cmd)

    def fragFlow(self):
        cmd = self.protoc_manager.packFragFlow()
        self.device.write(cmd)

    def chamClose(self):
        cmd = self.protoc_manager.packChamClose()
        self.device.write(cmd)

    def close(self):
        self.device.close()

    def read(self):
        '''
        :return: the read data point
        '''
        try:
            data = self.device.readline().decode('utf-8').strip().split(',')
            data = list(map(float, data))
        except Exception as e:
            data = None
            print(e)
        return data


if __name__ == '__main__':
    aio = AiO(port="/dev/cu.usbserial-AO0059X0")
    aio.pumpPwm(80)

    while True:
        aio.valveSet(index=3, state=1)
        time.sleep(10)
        aio.valveSet(index=3, state=0)
        time.sleep(10)



