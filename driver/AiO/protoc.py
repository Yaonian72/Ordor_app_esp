import functools
import struct


START_BYTE = '^'.encode('utf-8')
END_BYTE   = '\n'.encode('utf-8')
ESCAPE_BYTE = '?'.encode('utf-8')

# Protocol Def
VALVE_SET    = 0xF0
PUMP_PWM     = 0xF1
AIRFLOW      = 0x00
FRAGFLOW     = 0x01
CHAMCLOSE    = 0x02


# Decorator for command
def protocol_wrap(func):
    @functools.wraps(func)
    def wapper(*args, **kwargs):
        byteList = func(*args, **kwargs)
        msg_buf = START_BYTE
        csum = 0x00
        for b in byteList:
            csum ^= b
            if (b == int.from_bytes(ESCAPE_BYTE, byteorder='little')):
                msg_buf += ESCAPE_BYTE
            msg_buf += struct.pack(">B", b)
        msg_buf += struct.pack(">B", csum)
        msg_buf += END_BYTE
        print(msg_buf)
        return msg_buf
    return wapper


class AioProtocol:

    def __init__(self):
        pass

    @protocol_wrap
    def packValveSet(self, index, state):
        '''
        :param index: index of valve
        :param state: on/off state of valve
        :return: packed command
        '''
        cmd = struct.pack("<BBB", VALVE_SET, index, state)
        return cmd

    @protocol_wrap
    def packPumpPwn(self, speed):
        '''
        :param speed: the speed of motor
        :return: packed command
        '''
        speed = max(min(speed, 255), 0)
        cmd = struct.pack("<BB", PUMP_PWM, speed)
        return cmd

    @protocol_wrap
    def packAirFlow(self):
        '''
        :return: packed command
        '''
        cmd = struct.pack("<B", AIRFLOW)
        return cmd

    @protocol_wrap
    def packFragFlow(self):
        '''
        :return: packed command
        '''
        cmd = struct.pack("<B", FRAGFLOW)
        return cmd

    @protocol_wrap
    def packChamClose(self):
        '''
        command to close chamber
        :return: packed command
        '''
        cmd = struct.pack("<B", CHAMCLOSE)
        return cmd






