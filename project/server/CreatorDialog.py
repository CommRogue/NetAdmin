import configparser
import os
import pathlib
import subprocess
import sys
import threading
from queue import Queue
import psutil
from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5 import QtCore, QtGui, QtWidgets
import GUIHelpers
import client_builder
from CustomWidgets import WidgetGroupParent, UPnPVerify
import logging

PORT = 49152

class StdOutputQueueRedirector(Queue):
    def __init__(self, *args, **kwargs):
        Queue.__init__(self)

    def write(self, text):
        self.put(text)

    def flush(self):
        sys.__stdout__.flush()

class LoggingHandlerRedirector(logging.Handler):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def emit(self, message):
        if 'pyinstaller' in message.name.lower():
            print('logging handler got', message)
            self.queue.put(f"[{message.asctime}] {message.message}")

class CreatorDialog(QDialog):
    currentDialog = None
    def custom(self):
        self.widget.initialize()
        self.widget_2.initialize()
        self.widget_3.initialize()
        self.widget_4.initialize()
        self.widget_5.initialize()
        self.widget_6.initialize()
        self.widget_7.initialize()
        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ipRegex = QRegExp("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$")
        ipValidator = QtGui.QRegExpValidator(ipRegex, self)
        self.privateIpLineEdit.setValidator(ipValidator)
        self.privateIpLineEdit.setCursorPosition(0)
        self.publicIpLineEdit.setValidator(ipValidator)
        self.publicIpLineEdit.setCursorPosition(0)

        # get list of network interfaces
        self.interfaces = psutil.net_if_addrs()
        self.interfaces = [(a, b[1]) for a, b in self.interfaces.items()]
        for interface in self.interfaces:
            self.networkAdapterComboBox.addItem(interface[0])

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(754, 806)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.clientExecutableTitleLabel = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clientExecutableTitleLabel.sizePolicy().hasHeightForWidth())
        self.clientExecutableTitleLabel.setSizePolicy(sizePolicy)
        self.clientExecutableTitleLabel.setObjectName("clientExecutableTitleLabel")
        self.verticalLayout.addWidget(self.clientExecutableTitleLabel)
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.installationProcedureGroupBox = QtWidgets.QGroupBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.installationProcedureGroupBox.sizePolicy().hasHeightForWidth())
        self.installationProcedureGroupBox.setSizePolicy(sizePolicy)
        self.installationProcedureGroupBox.setSizeIncrement(QtCore.QSize(0, 0))
        self.installationProcedureGroupBox.setObjectName("installationProcedureGroupBox")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.installationProcedureGroupBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.widget = WidgetGroupParent(self.installationProcedureGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.silentButton = QtWidgets.QRadioButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.silentButton.sizePolicy().hasHeightForWidth())
        self.silentButton.setSizePolicy(sizePolicy)
        self.silentButton.setObjectName("silentButton")
        self.buttonGroup_2 = QtWidgets.QButtonGroup(Dialog)
        self.buttonGroup_2.setObjectName("buttonGroup_2")
        self.buttonGroup_2.addButton(self.silentButton)
        self.verticalLayout_3.addWidget(self.silentButton)
        self.widget_2 = WidgetGroupParent(self.widget)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.localNetworkButton = QtWidgets.QRadioButton(self.widget_2)
        self.localNetworkButton.setObjectName("localNetworkButton")
        self.buttonGroup_3 = QtWidgets.QButtonGroup(Dialog)
        self.buttonGroup_3.setObjectName("buttonGroup_3")
        self.buttonGroup_3.addButton(self.localNetworkButton)
        self.verticalLayout_5.addWidget(self.localNetworkButton)
        self.widget_6 = WidgetGroupParent(self.widget_2)
        self.widget_6.setObjectName("widget_6")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.widget_6)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.networkAdapterButton = QtWidgets.QRadioButton(self.widget_6)
        self.networkAdapterButton.setObjectName("networkAdapterButton")
        self.buttonGroup_4 = QtWidgets.QButtonGroup(Dialog)
        self.buttonGroup_4.setObjectName("buttonGroup_4")
        self.buttonGroup_4.addButton(self.networkAdapterButton)
        self.verticalLayout_7.addWidget(self.networkAdapterButton)
        self.networkAdapterComboBox = QtWidgets.QComboBox(self.widget_6)
        self.networkAdapterComboBox.setObjectName("networkAdapterComboBox")
        self.verticalLayout_7.addWidget(self.networkAdapterComboBox)
        self.verticalLayout_5.addWidget(self.widget_6)
        self.widget_7 = WidgetGroupParent(self.widget_2)
        self.widget_7.setObjectName("widget_7")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.widget_7)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.privateIpButton = QtWidgets.QRadioButton(self.widget_7)
        self.privateIpButton.setObjectName("privateIpButton")
        self.buttonGroup_4.addButton(self.privateIpButton)
        self.verticalLayout_8.addWidget(self.privateIpButton)
        self.privateIpLineEdit = QtWidgets.QLineEdit(self.widget_7)
        self.privateIpLineEdit.setInputMask("")
        self.privateIpLineEdit.setObjectName("privateIpLineEdit")
        self.verticalLayout_8.addWidget(self.privateIpLineEdit)
        self.verticalLayout_5.addWidget(self.widget_7)
        self.verticalLayout_3.addWidget(self.widget_2)
        self.widget_3 = WidgetGroupParent(self.widget)
        self.widget_3.setObjectName("widget_3")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.widget_3)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.publicNetworkButton = QtWidgets.QRadioButton(self.widget_3)
        self.publicNetworkButton.setObjectName("publicNetworkButton")
        self.buttonGroup_3.addButton(self.publicNetworkButton)
        self.verticalLayout_6.addWidget(self.publicNetworkButton)
        self.publicNetworkLabel = QtWidgets.QLabel(self.widget_3)
        self.publicNetworkLabel.setWordWrap(True)
        self.publicNetworkLabel.setObjectName("publicNetworkLabel")
        self.verticalLayout_6.addWidget(self.publicNetworkLabel)
        self.UPnPVerifyWidget = UPnPVerify(self.widget_3)
        self.UPnPVerifyWidget.setObjectName("UPnPVerifyWidget")
        self.verticalLayout_6.addWidget(self.UPnPVerifyWidget)
        self.widget_4 = WidgetGroupParent(self.widget_3)
        self.widget_4.setObjectName("widget_4")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.widget_4)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.dnsButton = QtWidgets.QRadioButton(self.widget_4)
        self.dnsButton.setObjectName("dnsButton")
        self.buttonGroup_5 = QtWidgets.QButtonGroup(Dialog)
        self.buttonGroup_5.setObjectName("buttonGroup_5")
        self.buttonGroup_5.addButton(self.dnsButton)
        self.verticalLayout_9.addWidget(self.dnsButton)
        self.dnsLineEdit = QtWidgets.QLineEdit(self.widget_4)
        self.dnsLineEdit.setObjectName("dnsLineEdit")
        self.verticalLayout_9.addWidget(self.dnsLineEdit)
        self.verticalLayout_6.addWidget(self.widget_4)
        self.widget_5 = WidgetGroupParent(self.widget_3)
        self.widget_5.setObjectName("widget_5")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.widget_5)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.publicIpButton = QtWidgets.QRadioButton(self.widget_5)
        self.publicIpButton.setObjectName("publicIpButton")
        self.buttonGroup_5.addButton(self.publicIpButton)
        self.verticalLayout_10.addWidget(self.publicIpButton)
        self.publicIpLineEdit = QtWidgets.QLineEdit(self.widget_5)
        self.publicIpLineEdit.setInputMask("")
        self.publicIpLineEdit.setObjectName("publicIpLineEdit")
        self.verticalLayout_10.addWidget(self.publicIpLineEdit)
        self.verticalLayout_6.addWidget(self.widget_5)
        self.verticalLayout_3.addWidget(self.widget_3)
        self.verticalLayout_4.addWidget(self.widget)
        self.manualButton = QtWidgets.QRadioButton(self.installationProcedureGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.manualButton.sizePolicy().hasHeightForWidth())
        self.manualButton.setSizePolicy(sizePolicy)
        self.manualButton.setSizeIncrement(QtCore.QSize(0, 0))
        self.manualButton.setObjectName("manualButton")
        self.buttonGroup_2.addButton(self.manualButton)
        self.verticalLayout_4.addWidget(self.manualButton)
        self.verticalLayout.addWidget(self.installationProcedureGroupBox)
        self.buildOutputGroupBox = QtWidgets.QGroupBox(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.buildOutputGroupBox.sizePolicy().hasHeightForWidth())
        self.buildOutputGroupBox.setSizePolicy(sizePolicy)
        self.buildOutputGroupBox.setObjectName("buildOutputGroupBox")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.buildOutputGroupBox)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.buildOutputTextEdit = QtWidgets.QTextEdit(self.buildOutputGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.buildOutputTextEdit.sizePolicy().hasHeightForWidth())
        self.buildOutputTextEdit.setSizePolicy(sizePolicy)
        self.buildOutputTextEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.buildOutputTextEdit.setSizeIncrement(QtCore.QSize(0, 0))
        self.buildOutputTextEdit.setObjectName("buildOutputTextEdit")
        self.verticalLayout_11.addWidget(self.buildOutputTextEdit)
        self.verticalLayout.addWidget(self.buildOutputGroupBox)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buildInstallerButton = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buildInstallerButton.sizePolicy().hasHeightForWidth())
        self.buildInstallerButton.setSizePolicy(sizePolicy)
        self.buildInstallerButton.setMinimumSize(QtCore.QSize(0, 50))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.buildInstallerButton.setFont(font)
        self.buildInstallerButton.setObjectName("buildInstallerButton")
        self.verticalLayout_2.addWidget(self.buildInstallerButton)
        self.cancelBoxButton = QtWidgets.QDialogButtonBox(Dialog)
        self.cancelBoxButton.setOrientation(QtCore.Qt.Horizontal)
        self.cancelBoxButton.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel)
        self.cancelBoxButton.setObjectName("cancelBoxButton")
        self.verticalLayout_2.addWidget(self.cancelBoxButton)

        self.retranslateUi(Dialog)
        self.cancelBoxButton.accepted.connect(Dialog.accept)  # type: ignore
        self.cancelBoxButton.rejected.connect(Dialog.reject)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.clientExecutableTitleLabel.setText(_translate("Dialog",
                                                           "<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:600;\">Client Installer Creator</span></p></body></html>"))
        self.installationProcedureGroupBox.setTitle(_translate("Dialog", "Installation Procedure"))
        self.silentButton.setText(_translate("Dialog", "Silent Installation"))
        self.localNetworkButton.setText(_translate("Dialog", "Connect to local network...."))
        self.networkAdapterButton.setText(_translate("Dialog", "Choose Network Adapter...."))
        self.privateIpButton.setText(_translate("Dialog", "Custom Network Card IP"))
        self.publicNetworkButton.setText(_translate("Dialog", "Connect to public IP or hostname...."))
        self.publicNetworkLabel.setText(_translate("Dialog",
                                                   "<html><head/><body><p><span style=\" font-size:7pt; font-weight:600;\">Note</span><span style=\" font-size:7pt;\">: NetAdmin will try to port-forward port 49152 on your router via the UPnP protocol, requiring your router to support it. If your router does not support UPnP, you can opt to manually forward the port on your router to your computer\'s appropriate network card.</span></p></body></html>"))
        self.dnsButton.setText(_translate("Dialog", "DNS-Resolvable Hostname"))
        self.publicIpButton.setText(_translate("Dialog", "Public IP (Static IP required)"))
        self.manualButton.setText(_translate("Dialog", "Manual Installation (Installer-like)"))
        self.buildOutputGroupBox.setTitle(_translate("Dialog", "Build Output"))
        self.buildInstallerButton.setText(_translate("Dialog", "Build Installer"))

    def __init__(self, parent=None):
        super(CreatorDialog, self).__init__(parent, )
        self.setWindowTitle("Client Executable Creator Wizard")
        self.setupUi(self)
        self.retranslateUi(self)
        self.custom()
        CreatorDialog.currentDialog = self
        self.finished.connect(self.onFinished)
        self.silentButton.setChecked(True)
        self.privateIpButton.setChecked(True)
        self.networkAdapterButton.setChecked(True)
        self.buildInstallerButton.clicked.connect(self.onBuildInstallerButtonClicked)

    def onBuildInstallerButtonClicked(self):
        import ctypes.wintypes
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value

        # get user documents folder
        od = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, od)
        outputDir = ""
        for c in od:
            if c == '\0':
                break
            outputDir += c
        outputDir = os.path.join(outputDir, "NetAdmin\\ClientBuilder")

        # if manual installation
        q = Queue()
        outputRedirector = LoggingHandlerRedirector(q)
        logging.getLogger().addHandler(outputRedirector)

        if self.manualButton.isChecked():
            t = threading.Thread(target=self.build, args=(outputDir, outputRedirector, "manual",))
        else:
            if self.localNetworkButton.isChecked():
                if self.privateIpButton.isChecked():
                    ip = self.privateIpLineEdit.text()
                    t = threading.Thread(target=self.build, args=(outputDir, outputRedirector, "ip", ip))
                else:
                    ip = self.interfaces[self.networkAdapterComboBox.currentIndex()][1].address
                    print("Selected ip in creator combobox = " + ip)
                    t = threading.Thread(target=self.build, args=(outputDir, outputRedirector, "ip", ip))
                    pass
            else:
                if self.dnsButton.isChecked():
                    hostname = self.dnsLineEdit.text()
                    t = threading.Thread(target=self.build, args=(outputDir, outputRedirector, "hostname", hostname))
                else:
                    ip = self.publicIpLineEdit.text()
                    t = threading.Thread(target=self.build, args=(outputDir, outputRedirector, "ip", ip))


        t.start()
        while True:
            try:
                item = q.get(timeout=0.05)
                if str(item) == "*FINISHED*":
                    GUIHelpers.infobox("Build Complete", "Build Complete")
                    break
                else:
                    self.buildOutputTextEdit.append(str(item))
            except:
                pass
            finally:
                QApplication.instance().processEvents()

    # TODO - make port in config file for server application, add port automatically in this function
    def build(self, outputDir, outputRedirector, type, ip_or_hostname=None, port=PORT):
        options = [
            '..\\client\\main.py',
            f'--distpath={os.path.join(outputDir, "build")}',
            f'--additional-hooks-dir=PyInstaller_hooks',
            '--onefile',
            '--runtime-tmpdir=.',
            '--add-binary=lib_bin\\turbojpeg-bin\\turbojpeg.dll;.',
            '--hidden-import=win32com.client',
            '--hidden-import=win32api',
            '--hidden-import=win32con',
            '--hidden-import=win32timezone',
            f"--paths={os.path.join(sys.path[0], '../shared')}",
        ]

        config = None
        if type != "manual":
            config = configparser.ConfigParser()
            config["CONNECTION"] = {
                "type": type,
                "ip_or_hostname": ip_or_hostname,
                "port": str(port)
            }
            configdir = os.path.join(outputDir, "temp")
            pathlib.Path(configdir).mkdir(parents=True, exist_ok=True)
            configdir = os.path.join(configdir, "runconfig.ini")
            with open(configdir, "w+") as configfile:
                config.write(configfile)
            options.append(f"--add-data={configdir};.")

        client_builder.build(options)
        outputRedirector.queue.put("*FINISHED*")
        subprocess.Popen(rf'explorer /select,{outputDir}')

    def onFinished(self, result):
        CreatorDialog.currentDialog = None