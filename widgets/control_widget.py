import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import json

ui_dir = 'ui/'
config_dir = 'config/'

'''
Child Widget
'''


class MeasureSettingWidget(QWidget):

    SAVE_CONFIG = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)
        uic.loadUi(ui_dir+'MesureSettingWidget.ui', self)
        with open(config_dir+'measurement.json') as json_file:
            self.config = json.load(json_file)
            print(self.config)
            self.durationSpinBox.setValue(int(self.config["duration"]))
            self.log_durationSpinBox.setValue(int(self.config["log_duration"]))
            self.repetitionSpinBox.setValue(int(self.config["repetition"]))
            self.gas_typeLineEdit.setText(self.config["gas_type"])
        self.SAVE_CONFIG.connect(self.save_config)

    @pyqtSlot(name="save_config")
    def save_config(self):
        with open(config_dir+'measurement.json', 'w') as json_file:
            self.config = {}
            self.config["duration"] = str(self.durationSpinBox.value())
            self.config["log_duration"] = str(self.log_durationSpinBox.value())
            self.config["repetition"] = str(self.repetitionSpinBox.value())
            self.config["gas_type"] = self.gas_typeLineEdit.text()
            json.dump(self.config, json_file)


class AdcSettingWidget(QWidget):

    SAVE_CONFIG = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)
        uic.loadUi(ui_dir+'AdcSettingWidget.ui', self)
        with open(config_dir + 'adc.json') as json_file:
            config = json.load(json_file)
            self.drateComboBox.setCurrentText(config["drate"]+" SPS")
            self.gainComboBox.setCurrentText(config["gain"])
            for i in range(8):
                if config["ch"][str(i)] == 1:
                    getattr(self, "ch" + str(i) + "RadioButton").setChecked(True)
                else:
                    getattr(self, "ch" + str(i) + "RadioButton").setChecked(False)
        self.SAVE_CONFIG.connect(self.save_config)

    @pyqtSlot(name="save_config")
    def save_config(self):
        with open(config_dir + 'adc.json', 'w') as json_file:
            config = {}
            config["drate"] = self.drateComboBox.currentText().split(' ')[0].replace('.', '_')
            config["gain"] = self.gainComboBox.currentText()
            config["ch"] = {}
            for i in range(8):
                config["ch"][str(i)] = 1 if getattr(self, "ch"+str(i)+"RadioButton").isChecked() else 0
            json.dump(config, json_file)

    def sensor_num(self):
        self._sensor_num = 0
        for i in range(8):
            self._sensor_num += getattr(self, "ch"+str(i)+"RadioButton").isChecked()
        return self._sensor_num

    def sample_rate(self):
        return int(self.drateComboBox.currentText().split(' ')[0].replace('.', '_'))



'''
End Child Widget
'''