from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import resources.qrc_resources
from MainWindowController import MainWindowController
from MainWindowModel import MainWindowModel

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
        self.TopToolBar.addAction(QAction(QIcon(":openIcon"), "", self.TopToolBar))
        self.TopToolBar.addAction(QAction(QIcon(":deleteIcon"), "", self.TopToolBar))
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

        self.ClientTable = QTableWidget(20, 4)
        self.layout.addWidget(self.ClientTable)
        self.ClientTable.setHorizontalHeaderLabels(["Status", "Name", "Address", "Latency"])
        h = self.ClientTable.horizontalHeader()
        h.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        h.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        h.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        h.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    controller = MainWindowController(window)
    model = MainWindowModel(controller)
    window.show()
    sys.exit(app.exec_())