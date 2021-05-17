import logging
from telnetlib import Telnet
import time
from driver.AiO.protoc import *

class TelnetClient():
    def __init__(self,host_ip):
        try:
            self.tn = Telnet(host_ip, 23)
            self.protoc_manager = AioProtocol()
        except Exception as e:
            print("wifi not available!")
            print(e)
            pass


    def valveSet(self, index, state):
        cmd = self.protoc_manager.packValveSet(index, state)
        self.tn.write(cmd)

    def pumpPwm(self, speed):
        cmd = self.protoc_manager.packPumpPwn(speed)
        self.tn.write(cmd)

    def airFlow(self):
        cmd = self.protoc_manager.packAirFlow()
        self.tn.write(cmd)

    def fragFlow(self):
        cmd = self.protoc_manager.packFragFlow()
        self.tn.write(cmd)

    def chamClose(self):
        cmd = self.protoc_manager.packChamClose()
        self.tn.write(cmd)

    def close(self):
        self.tn.close()

    def read(self):
        '''
        :return: the read data point
        '''
        try:
            data = self.tn.read_until(b"\n").decode('utf-8').strip().split(',')
            data = list(map(float, data))
            # print(data)#test
        except Exception as e:
            data = None
            print(e)
        return data

if __name__ == '__main__':

    # 如果登录结果返加True，则执行命令，然后退出
    host_ip = '192.168.1.165'
    telnet_client = TelnetClient(host_ip)
    # telnet_client.valveSet(index=3, state=1)
    # time.sleep(10)
    # telnet_client.valveSet(index=3, state=0)

    telnet_client.fragFlow()
    telnet_client.valveSet(index=3, state=1)
    time.sleep(5)
    telnet_client.airFlow()
    telnet_client.valveSet(index=3, state=0)
    time.sleep(5)
    while True:
        telnet_client.read()


