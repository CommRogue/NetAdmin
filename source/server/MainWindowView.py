from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import resources.qrc_resources
from MainWindowController import MainWindowController
from MainWindowModel import MainWindowModel
import qtmodern.styles
import qtmodern.windows

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetAdmin")
        self.layout = QVBoxLayout()
        self._center_widget = QWidget(self)
        self._center_widget.setLayout(self.layout)
        self.setCentralWidget(self._center_widget)
        self.setFixedSize(1000, 400)
        self.TopToolBar = QToolBar("Actions", self)
        self.ToolBarOpenAction = QAction(QIcon(":openIcon"), "", self.TopToolBar)
        self.ToolBarDeleteAction = QAction(QIcon(":deleteIcon"), "", self.TopToolBar)
        self.TopToolBar.addAction(self.ToolBarOpenAction)
        self.TopToolBar.addAction(self.ToolBarDeleteAction)
        self.addToolBar(self.TopToolBar)
        self.statusBar = self.statusBar()
        self.statusBar.showMessage(f"ThreadPool Usage: 0/{QThreadPool.globalInstance().maxThreadCount()} with max worker limit 12", 0)
        # self._buttonLayoutWidget = QWidget()
        # self.buttonLayout = QHBoxLayout()
        # self._buttonLayoutWidget.setLayout(self.buttonLayout)
        # self._buttonLayoutWidget.setMaximumWidth(1000)
        # self.buttonLayout.addWidget(QPushButton("temp"))
        # self.buttonLayout.addWidget(QPushButton("temp"))
        # self.buttonLayout.addWidget(QPushButton("temp"))
        # self.buttonLayout.addWidget(QPushButton("temp"))
        # self.buttonLayout.addWidget(QPushButton("temp"))
        # self.layout.addWidget(self._buttonLayoutWidget)

        self.ClientTable = QTableWidget(0, 6)
        self.ClientTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ClientTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.layout.addWidget(self.ClientTable)
        self.ClientTable.setHorizontalHeaderLabels(["Status", "Address", "Country", "Name", "Latency", "UUID"])
        h = self.ClientTable.horizontalHeader()
        h.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        h.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        h.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        h.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        h.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        # self.ClientTable.insertRow(self.ClientTable.rowCount())
        # c = self.ClientTable.rowCount()
        # self.ClientTable.setItem(c-1, 0, QTableWidgetItem("text1"))
        # self.ClientTable.setItem(c-1, 1, QTableWidgetItem("text2"))
        # self.ClientTable.setItem(c-1, 2, QTableWidgetItem("text3"))
        self.init_menu()

    def init_menu(self):
        self._menuBar = QMenuBar(self)
        subMenu = self._menuBar.addMenu("File")

        subMenu = self._menuBar.addMenu("Options")

        subMenu = self._menuBar.addMenu("Generate")
        subMenu.addAction("Generate Client Payload...")
        self.setMenuBar(self._menuBar)

    # def setClientEntry(self, item, status, address, name="N/A", latency="N/A"):
    #     row = item.row()
    #     self.ClientTable.setItem(row, 0, QTableWidgetItem(status))
    #     self.ClientTable.setItem(row, 1, QTableWidgetItem(address))
    #     self.ClientTable.setItem(row, 2, QTableWidgetItem(name))
    #     self.ClientTable.setItem(row, 3, QTableWidgetItem(latency))
    #     return self.ClientTable.itemAt(row, 0)
    #
    # def addClientEntry(self, status, address, name="N/A", latency="N/A"):
    #     rowCount = self.ClientTable.rowCount()
    #     self.ClientTable.insertRow(rowCount)
    #     c = rowCount #temp im lazy you can remove this
    #     self.ClientTable.setItem(rowCount, 0, QTableWidgetItem(status))
    #     self.ClientTable.setItem(rowCount, 1, QTableWidgetItem(address))
    #     self.ClientTable.setItem(rowCount, 2, QTableWidgetItem(name))
    #     self.ClientTable.setItem(rowCount, 3, QTableWidgetItem(latency))
    #     return self.ClientTable.itemAt(c, 0)
    #
    # def removeClientEntry(self, item):
    #     row = item.row()
    #     self.ClientTable.removeRow(row)