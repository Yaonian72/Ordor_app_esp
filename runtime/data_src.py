from PyQt5.QtCore import *
from driver.ADS1256.ADS1256_definitions import *
from driver.ADS1256.pipyadc import ADS1256
import numpy as np
import time

# Sensor 1
SENSOR_1 = POS_AIN7 | NEG_AINCOM
# Sensor 2
SENSOR_2 = POS_AIN6 | NEG_AINCOM
# Sensor 3
SENSOR_3 = POS_AIN5 | NEG_AINCOM
# Sensor 4
SENSOR_4 = POS_AIN4 | NEG_AINCOM

# Sensor Sequence
SEQUENCE = [SENSOR_1, SENSOR_2, SENSOR_3, SENSOR_4]

# buffer size
BUFFER_SIZE = 32

# initiate adc
ads = ADS1256()
ads.cal_self()
# ads setup
ads.drate = DRATE_30
ads.pga_gain = GAIN_4

# sync signal
sync_condition = QWaitCondition()
sync_flag = False

class Communicate(QObject):
    data_signal = pyqtSignal(np.ndarray)

class dataSendLoop(QObject):

    def __init__(self, addData_callbackFunc, mutex, cond, parent=None):
        super(dataSendLoop, self).__init__(parent)
        self.mutex = mutex
        self.cond = cond
        self.mySrc = Communicate()
        self.mySrc.data_signal.connect(addData_callbackFunc)

        # buffer
        rows, columns = BUFFER_SIZE, len(SEQUENCE)
        self.data_buffer = np.zeros((rows, columns), dtype=np.int)

    @pyqtSlot(name="generateData")
    def generateData(self):
        while True:
            # check data buffer shape
            if sync_flag:
                self.cond.wait(self.mutex)
            cur = time.time()
            if not self.mutex.tryLock():
                continue
            data_row = ads.read_continue(SEQUENCE)
            self.mutex.unlock()
            data_row = np.array(data_row)
            print(time.time() - cur)
            voltages = data_row * ads.v_per_digit  # [i * ads.v_per_digit for i in raw_channels]
            print(voltages)
            self.mySrc.data_signal.emit(voltages)



class AdcIO(QObject):

    def __init__(self, mutex, cond):
        super(AdcIO, self).__init__()
        self.mutex = mutex
        self.cond = cond

    @pyqtSlot(dict, name="configure_adc")
    def configureAdc(self, profile):
        self.mutex.lock()
        global SEQUENCE
        SEQUENCE = []
        for ch in range(7, -1, -1):
            if profile['ch'][ch] == 1:
                SEQUENCE.append(globals()["POS_AIN" + str(ch)] | NEG_AINCOM)
        ads.drate = globals()["DRATE_" + profile["drate"]]
        ads.pga_gain = int(profile["gain"])  # globals()["GAIN_"+profile["gain"]]
        ads.cal_self()
        self.mutex.unlock()

if __name__ == '__main__':
    print(globals()["GAIN_"+str(1)])

