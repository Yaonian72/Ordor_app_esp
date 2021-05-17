import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import requests
import json
import pandas as pd
import datetime


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import importlib
import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer



data_base = "database/"
ui_dir = 'ui/'
config_dir = 'config/'

class NotificationsSettingWidget(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent=parent)
        uic.loadUi(ui_dir + 'AlertSettingDialog.ui', self)
        self.setFixedSize(400, 300)
        #self.save_notificatoinPushButton.clicked.connect(lambda :self.send_notification("hello"))
        with open(config_dir+'notification.json') as json_file:
            config = json.load(json_file)
            self.tokenLineEdit.setText(config["token"])
            self.emailListWidget.addItems(config["email"])
            self.alertCheckBox.setChecked(config["alert_enable"])
            for index in range(self.emailListWidget.count()):
                item = self.emailListWidget.item(index)
                item.setFlags(item.flags() | Qt.ItemIsEditable)

    @pyqtSlot(name="save_notification_setting")
    def save_config(self):
        with open(config_dir+'notification.json', 'w') as json_file:
            config = {}
            config["token"] = self.tokenLineEdit.text()
            config["alert_enable"] = self.alertCheckBox.isChecked()
            emails = []
            for index in range(self.emailListWidget.count()):
                if len(self.emailListWidget.item(index).text()) > 0:
                    emails.append(self.emailListWidget.item(index).text())
            config["email"] = emails
            json.dump(config, json_file)

    @pyqtSlot(str, name='send_notification')
    def send_notification(self, gas_type):
        if self.alertCheckBox.isChecked():
            post_msg = {}
            emails = []
            for index in range(self.emailListWidget.count()):
                if len(self.emailListWidget.item(index).text()) > 0:
                    emails.append(self.emailListWidget.item(index).text())
            post_msg["value1"] = ';'.join(emails)
            post_msg["value2"] = gas_type
            print(post_msg)
            requests.post("https://maker.ifttt.com/trigger/MeasurementNotification/with/key/"+self.tokenLineEdit.text(), data=post_msg)

class RoutineSettingWidget(QDialog):

    def __init__(self, parent = None):
        QDialog.__init__(self, parent=parent)
        uic.loadUi(ui_dir + 'RoutineWidget.ui', self)
        self.load_routine(config_dir+"routine_registration.json")
        self.loadPushButton.clicked.connect(self.open_file)
        # set header
        header = self.routineTableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header = self.routineTableWidget.verticalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

    @property
    def routine(self):
        return self._routine

    @routine.setter
    def routine(self, val):
        self._routine = val

    def load_routine(self, filename):
        self._routine = {}
        with open(filename) as f:
            routine = json.load(f)
            for time, task_names in routine.items():
                for task_name in task_names:
                    task = getattr(__import__('routine_function'), task_name)
                    if int(time) in self._routine.keys():
                        self._routine[int(time)].append(task)
                    else:
                        self._routine[int(time)] = [task]
        print(self._routine)
        self._update_routine()


    def _update_routine(self):
        self.routineTableWidget.clearContents()
        self.routineTableWidget.setRowCount(0)
        for time, tasks in self.routine.items():
            rowPosition = self.routineTableWidget.rowCount()
            self.routineTableWidget.insertRow(rowPosition)
            self.routineTableWidget.setItem(rowPosition, 0, QTableWidgetItem(str(time)))
            task_name = [task.__name__ for task in tasks]
            self.routineTableWidget.setItem(rowPosition, 1, QTableWidgetItem('\n'.join(task_name)))

    @pyqtSlot(name="open_data_file")
    def open_file(self):

        # render file dialog
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFilter(QDir.Files)

        # read file
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            # f = open(filenames[0], 'r')
            try:
                self.load_routine(filenames[0])
                self.fileLineEdit.setText(filenames[0])
            except:
                pass

class FileSettingWidget(QDialog):

    onedrive_auth = "onedrive.pickle"
    config_file = config_dir+"fs.json"

    def __init__(self, parent = None):
        QDialog.__init__(self, parent=parent)
        uic.loadUi(ui_dir + 'FileSettingDialog.ui', self)
        self.load_config()
        self.root_dir = os.getcwd()
        self.pushButton.clicked.connect(self.save_config)
        # init onedrive
        if self.onedrive_enableCheckBox.isChecked():
            self._setup_onedrive()

    @pyqtSlot(str, name="upload_file")
    def _upload_onedrive(self, file_dir):
        filename = file_dir.split('/')[-1]
        items = self._navigate()
        dir_found = False
        path_split = file_dir.split('/')
        if len(path_split) == 1 or path_split[-2] == '..' or path_split[-2] == '.':
            filename_c = path_split[-1]
            returned_item = self.client.item(drive='me', id=self.item_id).children[filename_c].upload(file_dir)
            return

        # TODO
        # No secondary folder in the case
        dirname_c = path_split[-2]
        filename_c = path_split[-1]
        # find existing folder
        for count, item in enumerate(items):
            if item.folder is not None and item.name == dirname_c:
                returned_item = self.client.item(drive='me', id=item.id).children[filename_c].upload(file_dir)
                dir_found = True
                break
        # folder not exist yet
        if not dir_found:
            f = onedrivesdk.Folder()
            i = onedrivesdk.Item()
            i.name = dirname_c
            i.folder = f
            returned_item = self.client.item(drive='me', id=self.item_id).children.add(i)
            returned_item = self.client.item(drive='me', id=returned_item.id).children[filename_c].upload(file_dir)

    @pyqtSlot(list, str, name="save_file")
    def save_file(self, data, gas_type):
        print("save file........")
        try:
            os.chdir(self.onedrive_dirLineEdit.text())
        except OSError as e:
            self._create_data_folder()
            os.chdir(self.onedrive_dirLineEdit.text())

        # get folder name
        folder_name = gas_type
        if self.dir_prefixLineEdit.text() != "":
            folder_name = self.dir_prefixLineEdit.text() + '_' + folder_name
        if self.dir_suffixLineEdit.text() != "":
            folder_name = folder_name + '_' + self.dir_suffixLineEdit.text()
        # create folder if not exist
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        # get filename
        file_name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S" + "_" + gas_type)
        if self.file_prefixLineEdit.text() != "":
            file_name = self.file_prefixLineEdit.text() + '_' + file_name
        if self.file_suffixLineEdit.text() != "":
            file_name = file_name + '_' +self.file_suffixLineEdit.text()
        pathname = folder_name + '/' + file_name + '.txt'
        # get data format
        data_format = ""
        for i in range(len(data[0])):
            data_format += "{x[%d]} " % i
        data_format = data_format.strip() + '\n'
        # write to file
        with open(pathname, "w") as f:
            for line in data:
                f.write(data_format.format(x=line))
        if self.onedrive_enableCheckBox.isChecked():
            self._upload_onedrive(pathname)
        os.chdir(self.root_dir)

    def load_config(self):
        with open(self.config_file, 'r') as json_file:
            config = json.load(json_file)
            self.onedrive_dirLineEdit.setText(config["data_root"])
            self.dir_prefixLineEdit.setText(config["dir_prefix"])
            self.dir_suffixLineEdit.setText(config["dir_suffix"])
            self.file_prefixLineEdit.setText(config["file_prefix"])
            self.file_suffixLineEdit.setText(config["file_suffix"])
            self.onedrive_enableCheckBox.setChecked(config["od_enable"])
            self.onedrive_urlLineEdit.setText(config["od_url"])
            self.onedrive_secretLineEdit.setText(config["od_secret"])
            self.client_idLineEdit.setText(config["od_client"])

    @pyqtSlot(name="save_file_setting")
    def save_config(self):
        with open(self.config_file, 'w') as json_file:
            config = {}
            config["data_root"] = self.onedrive_dirLineEdit.text()
            config["dir_prefix"] = self.dir_prefixLineEdit.text()
            config["dir_suffix"] = self.dir_suffixLineEdit.text()
            config["file_prefix"] = self.file_prefixLineEdit.text()
            config["file_suffix"] = self.file_suffixLineEdit.text()
            config["od_enable"] = self.onedrive_enableCheckBox.isChecked()
            config["od_url"] = self.onedrive_urlLineEdit.text()
            config["od_secret"] = self.onedrive_secretLineEdit.text()
            config["od_client"] = self.client_idLineEdit.text()
            json.dump(config, json_file)

    def _create_data_folder(self):
        if self.onedrive_dirLineEdit.text() == "":
            return
        elif os.path.exists(self.onedrive_dirLineEdit.text()):
            return
        else:
            os.chdir(self.root_dir)
            os.mkdir(self.onedrive_dirLineEdit.text())

    def _setup_onedrive(self):
        self.item_id = "root"
        self.client_id = self.client_idLineEdit.text()
        self.URL = self.onedrive_urlLineEdit.text()
        self.secret = self.onedrive_secretLineEdit.text()
        self.client = onedrivesdk.get_default_client(client_id=self.client_id,
                                                     scopes=['wl.signin',
                                                             'wl.offline_access',
                                                             'onedrive.readwrite'])
        auth_url = self.client.auth_provider.get_auth_url(self.URL)
        # Block thread
        code = GetAuthCodeServer.get_auth_code(auth_url, self.URL)
        # authenticate
        self.client.auth_provider.authenticate(code, self.URL, self.secret)
        # create folder
        items = self._navigate()
        dir_found = False
        for count, item in enumerate(items):
            if item.folder is not None and item.name == self.onedrive_dirLineEdit.text():
                dir_found = True
                self.item_id = item.id
                break
        if not dir_found:
            f = onedrivesdk.Folder()
            i = onedrivesdk.Item()
            i.name = self.onedrive_dirLineEdit.text()
            i.folder = f
            returned_item = self.client.item(drive='me', id='root').children.add(i)
            self.client_id = returned_item.id

    def _navigate(self):
        items = self.client.item(id=self.item_id).children.get()
        return items

    def closeEvent(self, QCloseEvent):
        os.chdir(self.root_dir)
        self.client.auth_provider.save_session(path=config_dir+self.onedrive_auth)
        super().closeEvent(QCloseEvent)




