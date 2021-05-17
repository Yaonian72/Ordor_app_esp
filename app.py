###################################################################
#                                                                 #
#                    PLOT A LIVE GRAPH (PyQt5)                    #
#                  -----------------------------                  #
#            EMBED A MATPLOTLIB ANIMATION INSIDE YOUR             #
#            OWN GUI                                              #
#                                                                 #
###################################################################

# system imports
from __future__ import division, print_function, absolute_import
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D

from widgets.control_widget import *
from widgets.tool_widget import *
from runtime.data_src_aio import dataSendLoop, AdcIO


class OdorClassifierApp(QMainWindow):

    CONFIG_ADC = pyqtSignal(dict)

    def __init__(self):
        super(OdorClassifierApp, self).__init__()
        # Define the geometry of the main window
        self.setGeometry(50, 150, 950, 400)
        self.setWindowTitle("Sensor Measure App")
        # Create FRAME_A
        self.FRAME_A = QFrame(self)
        self.FRAME_A.setStyleSheet("QWidget { background-color: %s }" % QColor(210,210,235,255).name())
        self.LAYOUT_A = QGridLayout()
        self.FRAME_A.setLayout(self.LAYOUT_A)
        self.setCentralWidget(self.FRAME_A)


        '''Control Panel'''
        # load measurement setting
        self.LAYOUT_CONTROL = QVBoxLayout()
        self.LAYOUT_A.addLayout(self.LAYOUT_CONTROL, *(0, 50))
        # load measurement setting
        self.measureSettingWidget = MeasureSettingWidget()
        self.LAYOUT_CONTROL.addWidget(self.measureSettingWidget)
        self.measureSettingWidget.start_measureBtn.clicked.connect(self.measureBtnAction)


        # load adc setting
        self.adcSettingWidget = AdcSettingWidget()
        self.LAYOUT_CONTROL.addWidget(self.adcSettingWidget)
        '''End Control Panel'''

        # Place the matplotlib figure
        self.myFig = CustomFigCanvas()
        self.LAYOUT_A.addWidget(self.myFig, *(0,1))
        self.adcSettingWidget.adc_configPushButton.clicked.connect(self.configureBtnAction)
        self.measureSettingWidget.stop_measureBtn.clicked.connect(self.myFig.stop_log)
        self.myFig.MEASUREMENT_UPDATE.connect(self.measurement_update)

        # Add the callbackfunc to ..
        #myDataLoop = threading.Thread(name = 'myDataLoop', target = dataSendLoop, daemon = True, args = (self.addData_callbackFunc,))
        #myDataLoop.start()
        self.mutex = QMutex()
        self.cond = QWaitCondition()
        self.dataSrc_t = QThread()
        self.dataSrc = dataSendLoop(self.addData_callbackFunc, mutex=self.mutex, cond=self.cond)
        self.dataSrc.moveToThread(self.dataSrc_t)
        self.dataSrc_t.started.connect(self.dataSrc.generateData)
        self.adcio_t = QThread()
        self.adcio = AdcIO(mutex=self.mutex, cond=self.cond)
        self.adcio.moveToThread(self.adcio_t)
        self.CONFIG_ADC.connect(self.adcio.configureAdc)

        '''
        Menu Bar
        '''

        mainMenu = self.menuBar()
        toolMenu = mainMenu.addMenu('&Tool')

        # notify dialog
        self.notifyDialog = NotificationsSettingWidget()

        def showNotificationDialog():
            self.notifyDialog.show()

        notifySettingAct = QAction('&Notification', self)
        notifySettingAct.setShortcut('Ctrl+N')
        notifySettingAct.setStatusTip('Notification Setting')
        notifySettingAct.triggered.connect(showNotificationDialog)
        self.myFig.measurementFinished.connect(self.notifyDialog.send_notification)
        toolMenu.addAction(notifySettingAct)

        # routine dialog
        self.routineDialog = RoutineSettingWidget()

        def showRoutineDialog():
            self.routineDialog.show()

        routineSettingAct = QAction('&Routine', self)
        routineSettingAct.setShortcut('Ctrl+R')
        routineSettingAct.setStatusTip('Notification Setting')
        routineSettingAct.triggered.connect(showRoutineDialog)
        toolMenu.addAction(routineSettingAct)

        # file setting dialog
        self.fileDialog = FileSettingWidget()

        def showFileDialog():
            self.fileDialog.show()

        fileSettingAct = QAction('&File Setting', self)
        fileSettingAct.setShortcut('Ctrl+F')
        fileSettingAct.setStatusTip("File Setting")
        fileSettingAct.triggered.connect(showFileDialog)
        toolMenu.addAction(fileSettingAct)
        self.myFig.saveFile.connect(self.fileDialog.save_file)

        '''
        End Menu Bar
        '''

        # init ADC
        self.adcSettingWidget.adc_configPushButton.clicked.emit()
        self.dataSrc_t.start()
        self.adcio_t.start()


    def zoomBtnAction(self):
        print("zoom in")
        self.myFig.zoomIn(5)

    def measureBtnAction(self):
        print("measurement start")
        if self.measureSettingWidget.repetitionSpinBox.value() == 0:
            return
        measure_profile = {
            "sample_rate": self.adcSettingWidget.sample_rate(),
            "sensor_num": self.adcSettingWidget.sensor_num(),
            "duration": self.measureSettingWidget.durationSpinBox.value(),
            "log_duration": self.measureSettingWidget.log_durationSpinBox.value(),
            "repetition":self.measureSettingWidget.repetitionSpinBox.value(),
            "gas_type": self.measureSettingWidget.gas_typeLineEdit.text(),
            "routine": self.routineDialog.routine
        }
        self.myFig.init_log(measure_profile)
        self.measureSettingWidget.SAVE_CONFIG.emit()

    def configureBtnAction(self):
        profile = {}
        profile['ch'] = {}
        for i in range(8):
            profile['ch'][i] = 1 if getattr(self.adcSettingWidget, "ch"+str(i)+"RadioButton").isChecked() else 0
        profile['drate'] = self.adcSettingWidget.drateComboBox.currentText().split(' ')[0].replace('.', '_')
        profile['gain'] = self.adcSettingWidget.gainComboBox.currentText()
        self.CONFIG_ADC.emit(profile)
        self.adcSettingWidget.SAVE_CONFIG.emit()
        self.myFig.RESET.emit()
        print(profile)

    def addData_callbackFunc(self, value):
        self.myFig.add_data(value)

    def measurement_update(self):
        repetitionToStop = self.measureSettingWidget.repetitionSpinBox.value() - 1
        self.measureSettingWidget.repetitionSpinBox.setValue(repetitionToStop)


class CustomFigCanvas(FigureCanvas, TimedAnimation):

    RESET = pyqtSignal()
    MEASUREMENT_UPDATE = pyqtSignal()

    measurementFinished = pyqtSignal(str)
    saveFile = pyqtSignal(list, str)

    COLORMAP = ["blue", "orange", "green", "pink", "red", "black", "teal", "slategrey", "lightblue"]


    def __init__(self):

        print(matplotlib.__version__)

        # Flag Init
        self._inited = False
        self._data_log = False  # Flag for controling save log

        # Data Buffer Init
        self.addedData = []
        self.xlim = 200
        self.n = np.linspace(0, self.xlim - 1, self.xlim)
        self.y = []  # (self.n * 0.0) + 50
        a = []
        b = []
        a.append(2.0)
        a.append(4.0)
        a.append(2.0)
        b.append(4.0)
        b.append(3.0)
        b.append(4.0)

        # Window Init
        self.fig = Figure(figsize=(5,5), dpi=100)
        self.ax1 = self.fig.add_subplot(111)
        # self.ax1 settings
        self.lines = []
        self.ax1.set_xlabel('time/s')
        self.ax1.set_ylabel('raw data/volt')
        self.ax1.set_xlim(0, self.xlim - 1)
        self.ax1.set_ylim(0, 2.2)
        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=50, blit=True)
        self.repetition = 0

        # Redraw Timer
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.start()
        self.timer.timeout.connect(self._redraw)

        # connect signal
        self.RESET.connect(self._reset)

    # =============================================================================
    # Data Management Functions
    # =============================================================================

    @property
    def start_log(self):
        return self._data_log

    @start_log.setter
    def start_log(self, val):
        self._data_log = val

    def init_log(self, profile):

        self.start_log = True
        self.file_saved = False
        if profile is not None:
            self.log_profile = profile

        # init num of data to be logged
        self.log_num_max = self.log_profile["log_duration"] * self.log_profile["sample_rate"] / self.log_profile["sensor_num"]
        self.repeatition_max = self.log_profile["duration"] * self.log_profile["sample_rate"] / self.log_profile["sensor_num"]
        self.log_counter = 0
        self.log_buf = []

        # init routine
        self.routine_time = [tp * self.log_profile["sample_rate"] / self.log_profile["sensor_num"]
                             for tp, _ in self.log_profile["routine"].items()]
        self.routine_cur = 0

        # update repetition
        if self.repetition != 0:
            self.repetition -= 1
        else:
            self.repetition = self.log_profile["repetition"] - 1

    def stop_log(self):
        self.start_log = False
        self.repetition = 0

    def new_frame_seq(self):
        return iter(range(self.n.size))

    # todo
    def add_data(self, value):

        # init graph by data received
        if not self._inited:

            if self._reseted:
                self._reseted = False
                return

            for line in self.lines:
                self.ax1.lines.remove(line['line'])
                self.ax1.lines.remove(line['tail'])
                self.ax1.lines.remove(line['head'])
            print("lines:"+str(len(self.ax1.lines)))
            self.lines = []
            for i in range(value.shape[0]):
                self.lines.append({'line': Line2D([], [], color=self.COLORMAP[i], label="Sensor"+str(i)),
                                   'tail': Line2D([], [], color='red', linewidth=2),
                                   'head': Line2D([], [], color='red', marker='o', markeredgecolor='r')})
                self.ax1.add_line(self.lines[i]['line'])
                self.ax1.add_line(self.lines[i]['tail'])
                self.ax1.add_line(self.lines[i]['head'])
                self.addedData.append([])
                self.y.append((self.n * 0.0))

            self.ax1.legend()

            self._inited = True

        # Logging Started
        if self.start_log:

            self.log_counter += 1
            print(self.log_counter)
            line = []
            for i in range(value.shape[0]):
                self.addedData[i].append(value[i])
                line.append(value[i])

            if self.log_counter <= self.log_num_max:
                self.log_buf.append(line)

            # perform routine
            if self.routine_cur + 1 <= len(self.routine_time) and self.log_counter == self.routine_time[self.routine_cur]:
                # Todo
                for task in self.log_profile["routine"][int(self.log_counter*self.log_profile["sensor_num"]/self.log_profile["sample_rate"])]:
                    task()
                self.routine_cur += 1
                print(self.routine_cur)

            # data logging finished
            if self.log_counter >= self.log_num_max and not self.file_saved:
                self.saveFile.emit(self.log_buf, self.log_profile["gas_type"])
                self.file_saved = True
                #del self.log_buf

            # check maximum repetition
            if self.log_counter >= self.repeatition_max:
                self.start_log = False
                if self.repetition > 0:
                    self.init_log(None)
                else:
                    self.measurementFinished.emit(self.log_profile["gas_type"])
        # Logging Not Started
        else:
            for i in range(value.shape[0]):
                self.addedData[i].append(value[i])

    # =============================================================================
    # Draw Functions
    # =============================================================================

    def _init_draw(self):
        #lines = [self.line1, self.line1_tail, self.line1_head]
        for l in self.lines:
            for _, seg in l.items():
                seg.set_data([], [])

    def _step(self, *args):
        # Extends the _step() method for the TimedAnimation class.
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            TimedAnimation._stop(self)
        return

    def _draw_frame(self, framedata):
        self._drawn_artists = []
        if self._inited:
            margin = 2
            for i in range(len(self.lines)):
                while(len(self.addedData[i]) > 0):
                    self.y[i] = np.roll(self.y[i], -1)
                    self.y[i][-1] = self.addedData[i][0]
                    del(self.addedData[i][0])

                self.lines[i]['line'].set_data(self.n[0: self.n.size - margin], self.y[i][0: self.n.size - margin])
                self.lines[i]['tail'].set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]),
                                         np.append(self.y[i][-10:-1 - margin], self.y[i][-1 - margin]))
                self.lines[i]['head'].set_data(self.n[-1 - margin], self.y[i][-1 - margin])
                self._drawn_artists.extend([self.lines[i]['line'], self.lines[i]['tail'], self.lines[i]['head']])

            up_limit = np.max(self.y)
            low_limit = np.min(self.y)
            self.ax1.set_ylim(low_limit*0.95, up_limit*1.05)
        else:
            self.draw()

    @pyqtSlot(name="reset")
    def _reset(self):
        self._inited = False
        self._reseted = True
        self.y = []

    # refresh plot axis scale
    @pyqtSlot(name="redraw")
    def _redraw(self):
        self.draw()


class Communicate(QObject):
    data_signal = pyqtSignal(np.ndarray)

''' End Class '''

if __name__== '__main__':
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create('Plastique'))
    myGUI = OdorClassifierApp()
    myGUI.show()
    sys.exit(app.exec_())