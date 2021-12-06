import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import pyqtSignal

class ClientInspectorView(QMainWindow):
    exitEvent = pyqtSignal(QCloseEvent)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.addToTable()

    def closeEvent(self, event):
        self.exitEvent.emit(event)

    def addToTable(self):
        self.SystemInformationTable.insertRow(0)
        self.SystemInformationTable.setItem(0, 0, QTableWidgetItem("DESKTOP_NAME"))
        self.SystemInformationTable.insertRow(1)
        self.SystemInformationTable.setItem(1, 0, QTableWidgetItem("OPERATING_SYSTEM_VERSION"))
        self.SystemInformationTable.insertRow(2)
        self.SystemInformationTable.setItem(2, 0, QTableWidgetItem("PROCESSOR_NAME"))
        self.SystemInformationTable.insertRow(3)
        self.SystemInformationTable.setItem(3, 0, QTableWidgetItem("PROCESSOR_ARCHITECTURE"))
        self.SystemInformationTable.insertRow(4)
        self.SystemInformationTable.setItem(4, 0, QTableWidgetItem("GPU_NAME"))


    def setupUi(self, ClientInspectionWindow):
        ClientInspectionWindow.setObjectName("ClientInspectionWindow")
        ClientInspectionWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(ClientInspectionWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.splitter = QtWidgets.QSplitter(self.tab)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 10)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.SystemInformationTable = QtWidgets.QTableWidget(0, 2, self.layoutWidget)
        self.SystemInformationTable.setObjectName("SystemInformationTable")
        self.SystemInformationTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.SystemInformationTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.SystemInformationTable.setHorizontalHeaderLabels(["Specification", "Value"])
        h = self.SystemInformationTable.horizontalHeader()
        h.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        h.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.horizontalLayout_2.addWidget(self.SystemInformationTable)
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(20, -1, 20, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.CPUUsageLabel = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.CPUUsageLabel.setFont(font)
        self.CPUUsageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.CPUUsageLabel.setObjectName("CPUUsageLabel")
        self.verticalLayout.addWidget(self.CPUUsageLabel)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.CPUUsageProgressBar = QtWidgets.QProgressBar(self.layoutWidget)
        self.CPUUsageProgressBar.setMinimumSize(QtCore.QSize(0, 0))
        self.CPUUsageProgressBar.setProperty("value", 24)
        self.CPUUsageProgressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.CPUUsageProgressBar.setOrientation(QtCore.Qt.Vertical)
        self.CPUUsageProgressBar.setInvertedAppearance(False)
        self.CPUUsageProgressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.CPUUsageProgressBar.setObjectName("CPUUsageProgressBar")
        self.horizontalLayout.addWidget(self.CPUUsageProgressBar)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.CPUUsagePrecentage = QtWidgets.QLabel(self.layoutWidget)
        self.CPUUsagePrecentage.setAlignment(QtCore.Qt.AlignCenter)
        self.CPUUsagePrecentage.setObjectName("CPUUsagePrecentage")
        self.verticalLayout.addWidget(self.CPUUsagePrecentage)
        self.horizontalLayout_9.addLayout(self.verticalLayout)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setContentsMargins(20, -1, 20, -1)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.GPUUsageLabel = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.GPUUsageLabel.setFont(font)
        self.GPUUsageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.GPUUsageLabel.setObjectName("GPUUsageLabel")
        self.verticalLayout_5.addWidget(self.GPUUsageLabel)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.GPUUsageProgressBar = QtWidgets.QProgressBar(self.layoutWidget)
        self.GPUUsageProgressBar.setProperty("value", 24)
        self.GPUUsageProgressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.GPUUsageProgressBar.setOrientation(QtCore.Qt.Vertical)
        self.GPUUsageProgressBar.setObjectName("GPUUsageProgressBar")
        self.horizontalLayout_6.addWidget(self.GPUUsageProgressBar)
        self.verticalLayout_5.addLayout(self.horizontalLayout_6)
        self.GPUUsagePrecentage = QtWidgets.QLabel(self.layoutWidget)
        self.GPUUsagePrecentage.setAlignment(QtCore.Qt.AlignCenter)
        self.GPUUsagePrecentage.setObjectName("GPUUsagePrecentage")
        self.verticalLayout_5.addWidget(self.GPUUsagePrecentage)
        self.horizontalLayout_9.addLayout(self.verticalLayout_5)
        self.verticalLayout_8.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setContentsMargins(20, -1, 20, -1)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.RAMUsageLabel = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.RAMUsageLabel.setFont(font)
        self.RAMUsageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.RAMUsageLabel.setObjectName("RAMUsageLabel")
        self.verticalLayout_6.addWidget(self.RAMUsageLabel)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.RAMUsageProgressBar = QtWidgets.QProgressBar(self.layoutWidget)
        self.RAMUsageProgressBar.setProperty("value", 24)
        self.RAMUsageProgressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.RAMUsageProgressBar.setOrientation(QtCore.Qt.Vertical)
        self.RAMUsageProgressBar.setObjectName("RAMUsageProgressBar")
        self.horizontalLayout_7.addWidget(self.RAMUsageProgressBar)
        self.verticalLayout_6.addLayout(self.horizontalLayout_7)
        self.RamUsagePrecentage = QtWidgets.QLabel(self.layoutWidget)
        self.RamUsagePrecentage.setAlignment(QtCore.Qt.AlignCenter)
        self.RamUsagePrecentage.setObjectName("RamUsagePrecentage")
        self.verticalLayout_6.addWidget(self.RamUsagePrecentage)
        self.horizontalLayout_10.addLayout(self.verticalLayout_6)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setContentsMargins(0, -1, 0, -1)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.DiskUsageLabel = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.DiskUsageLabel.setFont(font)
        self.DiskUsageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.DiskUsageLabel.setObjectName("DiskUsageLabel")
        self.verticalLayout_7.addWidget(self.DiskUsageLabel)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.DiskUsageProgressBar = QtWidgets.QProgressBar(self.layoutWidget)
        self.DiskUsageProgressBar.setProperty("value", 24)
        self.DiskUsageProgressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.DiskUsageProgressBar.setOrientation(QtCore.Qt.Vertical)
        self.DiskUsageProgressBar.setObjectName("DiskUsageProgressBar")
        self.horizontalLayout_8.addWidget(self.DiskUsageProgressBar)
        self.verticalLayout_7.addLayout(self.horizontalLayout_8)
        self.DiskUsagePrecentage = QtWidgets.QLabel(self.layoutWidget)
        self.DiskUsagePrecentage.setAlignment(QtCore.Qt.AlignCenter)
        self.DiskUsagePrecentage.setObjectName("DiskUsagePrecentage")
        self.verticalLayout_7.addWidget(self.DiskUsagePrecentage)
        self.horizontalLayout_10.addLayout(self.verticalLayout_7)
        self.verticalLayout_8.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_2.addLayout(self.verticalLayout_8)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.ConnectionInformationHeader = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.ConnectionInformationHeader.setFont(font)
        self.ConnectionInformationHeader.setObjectName("ConnectionInformationHeader")
        self.verticalLayout_11.addWidget(self.ConnectionInformationHeader)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout.setObjectName("gridLayout")
        self.label_8 = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 1, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 0, 0, 1, 1)
        self.horizontalLayout_11.addLayout(self.gridLayout)
        self.verticalLayout_11.addLayout(self.horizontalLayout_11)
        self.verticalLayout_9.addWidget(self.splitter)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout_10.addWidget(self.tabWidget)
        ClientInspectionWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(ClientInspectionWindow)
        self.statusbar.setObjectName("statusbar")
        ClientInspectionWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(ClientInspectionWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        ClientInspectionWindow.setMenuBar(self.menubar)
        self.actionew = QtWidgets.QAction(ClientInspectionWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/collapse_closed.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionew.setIcon(icon)
        self.actionew.setObjectName("actionew")
        self.actionTest_1 = QtWidgets.QAction(ClientInspectionWindow)
        self.actionTest_1.setIcon(icon)
        self.actionTest_1.setObjectName("actionTest_1")
        self.actionTest_2 = QtWidgets.QAction(ClientInspectionWindow)
        self.actionTest_2.setObjectName("actionTest_2")
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(ClientInspectionWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ClientInspectionWindow)

    def retranslateUi(self, ClientInspectionWindow):
        _translate = QtCore.QCoreApplication.translate
        ClientInspectionWindow.setWindowTitle(_translate("ClientInspectionWindow", "Client Inspection Window"))
        self.CPUUsageLabel.setText(_translate("ClientInspectionWindow", "CPU Usage"))
        self.CPUUsagePrecentage.setText(_translate("ClientInspectionWindow", "TextLabel"))
        self.GPUUsageLabel.setText(_translate("ClientInspectionWindow", "GPU Usage"))
        self.GPUUsagePrecentage.setText(_translate("ClientInspectionWindow", "TextLabel"))
        self.RAMUsageLabel.setText(_translate("ClientInspectionWindow", "Ram Usage"))
        self.RamUsagePrecentage.setText(_translate("ClientInspectionWindow", "TextLabel"))
        self.DiskUsageLabel.setText(_translate("ClientInspectionWindow", "Disk Usage"))
        self.DiskUsagePrecentage.setText(_translate("ClientInspectionWindow", "TextLabel"))
        self.ConnectionInformationHeader.setText(_translate("ClientInspectionWindow", "Connection Information"))
        self.label_8.setText(_translate("ClientInspectionWindow", "Latency"))
        self.label_10.setText(_translate("ClientInspectionWindow", "Address"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("ClientInspectionWindow", "Tab 1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("ClientInspectionWindow", "Tab 2"))
        self.menuFile.setTitle(_translate("ClientInspectionWindow", "File"))
        self.actionew.setText(_translate("ClientInspectionWindow", "ew"))
        self.actionTest_1.setText(_translate("ClientInspectionWindow", "&Test 1"))
        self.actionTest_2.setText(_translate("ClientInspectionWindow", "Test 2"))