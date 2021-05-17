from PyQt5.QtCore import *
from driver.AiO.telnet import *
import numpy as np

# instantiate aio
aio = TelnetClient('192.168.1.165')

# sync signal
sync_condition = QWaitCondition()
sync_flag = False

# communicate object
class Communicate(QObject):
    data_signal = pyqtSignal(np.ndarray)

# data send loop
class dataSendLoop(QObject):

    def __init__(self, addData_callbackFunc, mutex, cond, parent=None):
        super(dataSendLoop, self).__init__(parent)
        self.mutex = mutex
        self.cond = cond
        self.mySrc = Communicate()
        self.mySrc.data_signal.connect(addData_callbackFunc)

    @pyqtSlot(name="generateData")
    def generateData(self):
        while True:
            # check data buffer shape
            if sync_flag:
                self.cond.wait(self.mutex)
            cur = time.time()
            if not self.mutex.tryLock():
                continue
            data_row = aio.read()
            self.mutex.unlock()
            if data_row is None:
                continue
            voltages = np.array(data_row[0:4])
            print(data_row)
            self.mySrc.data_signal.emit(voltages)

# high level io function
class AdcIO(QObject):

    def __init__(self, mutex, cond):
        super(AdcIO, self).__init__()
        self.mutex = mutex
        self.cond = cond

    @pyqtSlot(dict, name="configure_adc")
    def configureAdc(self, profile):
        pass

if __name__ == '__main__':
    while True:
        print(aio.read())