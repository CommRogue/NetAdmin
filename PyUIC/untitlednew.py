# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitlednew.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ClientInspectionWindow(object):
    def setupUi(self, ClientInspectionWindow):
        ClientInspectionWindow.setObjectName("ClientInspectionWindow")
        ClientInspectionWindow.resize(795, 596)
        self.centralwidget = QtWidgets.QWidget(ClientInspectionWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.TabContainer = QtWidgets.QTabWidget(self.centralwidget)
        self.TabContainer.setObjectName("TabContainer")
        self.ConnectionInformationTab = QtWidgets.QWidget()
        self.ConnectionInformationTab.setObjectName("ConnectionInformationTab")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.ConnectionInformationTab)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.splitter = QtWidgets.QSplitter(self.ConnectionInformationTab)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 10)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.SystemInformationTable = QtWidgets.QTableWidget(self.layoutWidget)
        self.SystemInformationTable.setColumnCount(2)
        self.SystemInformationTable.setObjectName("SystemInformationTable")
        self.SystemInformationTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.SystemInformationTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.SystemInformationTable.setHorizontalHeaderItem(1, item)
        self.SystemInformationTable.horizontalHeader().setSortIndicatorShown(False)
        self.SystemInformationTable.horizontalHeader().setStretchLastSection(False)
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
        self.TabContainer.addTab(self.ConnectionInformationTab, "")
        self.FileExplorerTab = QtWidgets.QWidget()
        self.FileExplorerTab.setObjectName("FileExplorerTab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.FileExplorerTab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(self.FileExplorerTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.expandButton = QtWidgets.QPushButton(self.groupBox)
        self.expandButton.setObjectName("expandButton")
        self.horizontalLayout_4.addWidget(self.expandButton)
        self.deleteButton = QtWidgets.QPushButton(self.groupBox)
        self.deleteButton.setObjectName("deleteButton")
        self.horizontalLayout_4.addWidget(self.deleteButton)
        self.downloadButton = QtWidgets.QPushButton(self.groupBox)
        self.downloadButton.setObjectName("downloadButton")
        self.horizontalLayout_4.addWidget(self.downloadButton)
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_4.addWidget(self.pushButton)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.fileViewer = QtWidgets.QTreeWidget(self.FileExplorerTab)
        self.fileViewer.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.fileViewer.setColumnCount(4)
        self.fileViewer.setObjectName("fileViewer")
        self.fileViewer.header().setVisible(True)
        self.fileViewer.header().setMinimumSectionSize(50)
        self.fileViewer.header().setSortIndicatorShown(False)
        self.fileViewer.header().setStretchLastSection(False)
        self.verticalLayout_2.addWidget(self.fileViewer)
        self.TabContainer.addTab(self.FileExplorerTab, "")
        self.CommandLineTab = QtWidgets.QWidget()
        self.CommandLineTab.setObjectName("CommandLineTab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.CommandLineTab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.ShellTabContainer = QtWidgets.QTabWidget(self.CommandLineTab)
        self.ShellTabContainer.setTabsClosable(True)
        self.ShellTabContainer.setMovable(True)
        self.ShellTabContainer.setTabBarAutoHide(False)
        self.ShellTabContainer.setObjectName("ShellTabContainer")
        self.verticalLayout_3.addWidget(self.ShellTabContainer)
        self.TabContainer.addTab(self.CommandLineTab, "")
        self.ProcessManagerTab = QtWidgets.QWidget()
        self.ProcessManagerTab.setObjectName("ProcessManagerTab")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.ProcessManagerTab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_2 = QtWidgets.QGroupBox(self.ProcessManagerTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.expandButton_2 = QtWidgets.QPushButton(self.groupBox_2)
        self.expandButton_2.setObjectName("expandButton_2")
        self.horizontalLayout_5.addWidget(self.expandButton_2)
        self.deleteButton_2 = QtWidgets.QPushButton(self.groupBox_2)
        self.deleteButton_2.setObjectName("deleteButton_2")
        self.horizontalLayout_5.addWidget(self.deleteButton_2)
        self.downloadButton_2 = QtWidgets.QPushButton(self.groupBox_2)
        self.downloadButton_2.setObjectName("downloadButton_2")
        self.horizontalLayout_5.addWidget(self.downloadButton_2)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_5.addWidget(self.pushButton_2)
        self.verticalLayout_4.addWidget(self.groupBox_2)
        self.tableWidget = QtWidgets.QTableWidget(self.ProcessManagerTab)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout_4.addWidget(self.tableWidget)
        self.TabContainer.addTab(self.ProcessManagerTab, "")
        self.RemoteDesktopTab = QtWidgets.QWidget()
        self.RemoteDesktopTab.setObjectName("RemoteDesktopTab")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.RemoteDesktopTab)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.pushButton_3 = QtWidgets.QPushButton(self.RemoteDesktopTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout_13.addWidget(self.pushButton_3)
        self.label = QtWidgets.QLabel(self.RemoteDesktopTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_13.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_13.addItem(spacerItem)
        self.TabContainer.addTab(self.RemoteDesktopTab, "")
        self.verticalLayout_10.addWidget(self.TabContainer)
        ClientInspectionWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(ClientInspectionWindow)
        self.statusbar.setObjectName("statusbar")
        ClientInspectionWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(ClientInspectionWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 795, 21))
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
        self.TabContainer.setCurrentIndex(1)
        self.ShellTabContainer.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(ClientInspectionWindow)

    def retranslateUi(self, ClientInspectionWindow):
        _translate = QtCore.QCoreApplication.translate
        ClientInspectionWindow.setWindowTitle(_translate("ClientInspectionWindow", "Client Inspection Window"))
        item = self.SystemInformationTable.horizontalHeaderItem(0)
        item.setText(_translate("ClientInspectionWindow", "Specification"))
        item = self.SystemInformationTable.horizontalHeaderItem(1)
        item.setText(_translate("ClientInspectionWindow", "Value"))
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
        self.TabContainer.setTabText(self.TabContainer.indexOf(self.ConnectionInformationTab), _translate("ClientInspectionWindow", "General Information"))
        self.groupBox.setTitle(_translate("ClientInspectionWindow", "Actions"))
        self.expandButton.setText(_translate("ClientInspectionWindow", "Expand"))
        self.deleteButton.setText(_translate("ClientInspectionWindow", "Delete"))
        self.downloadButton.setText(_translate("ClientInspectionWindow", "Download"))
        self.pushButton.setText(_translate("ClientInspectionWindow", "PushButton"))
        self.fileViewer.headerItem().setText(0, _translate("ClientInspectionWindow", "Name"))
        self.fileViewer.headerItem().setText(1, _translate("ClientInspectionWindow", "Created"))
        self.fileViewer.headerItem().setText(2, _translate("ClientInspectionWindow", "Last Modified"))
        self.fileViewer.headerItem().setText(3, _translate("ClientInspectionWindow", "Size"))
        self.TabContainer.setTabText(self.TabContainer.indexOf(self.FileExplorerTab), _translate("ClientInspectionWindow", "File Explorer"))
        self.TabContainer.setTabText(self.TabContainer.indexOf(self.CommandLineTab), _translate("ClientInspectionWindow", "Command Line"))
        self.groupBox_2.setTitle(_translate("ClientInspectionWindow", "Actions"))
        self.expandButton_2.setText(_translate("ClientInspectionWindow", "Expand"))
        self.deleteButton_2.setText(_translate("ClientInspectionWindow", "Delete"))
        self.downloadButton_2.setText(_translate("ClientInspectionWindow", "Download"))
        self.pushButton_2.setText(_translate("ClientInspectionWindow", "PushButton"))
        self.TabContainer.setTabText(self.TabContainer.indexOf(self.ProcessManagerTab), _translate("ClientInspectionWindow", "Process Manager"))
        self.pushButton_3.setText(_translate("ClientInspectionWindow", "Open Remote Desktop Window"))
        self.label.setText(_translate("ClientInspectionWindow", "Latency: N/A"))
        self.TabContainer.setTabText(self.TabContainer.indexOf(self.RemoteDesktopTab), _translate("ClientInspectionWindow", "Remote Dekstop"))
        self.menuFile.setTitle(_translate("ClientInspectionWindow", "File"))
        self.actionew.setText(_translate("ClientInspectionWindow", "ew"))
        self.actionTest_1.setText(_translate("ClientInspectionWindow", "&Test 1"))
        self.actionTest_2.setText(_translate("ClientInspectionWindow", "Test 2"))
import resources_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ClientInspectionWindow = QtWidgets.QMainWindow()
    ui = Ui_ClientInspectionWindow()
    ui.setupUi(ClientInspectionWindow)
    ClientInspectionWindow.show()
    sys.exit(app.exec_())
