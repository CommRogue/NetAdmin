import ScreenShare
from NetProtocol import *
import time
import threading
import functools
from PyQt5.QtCore import pyqtSignal, QThread, QObject, QRunnable, QThreadPool
import typing
from PyQt5.QtWidgets import QTableWidgetItem, QTreeWidgetItem, QTreeWidgetItemIterator
from fileExplorerManager import FileExplorerManager
from RemoteShell.RemoteShell import RemoteShellManager


class TabThreadEventManager(): #container class for the events that tab threads wait for
    def __init__(self, starterindex, *args : threading.Event):
        self.__tabEvents = list(args)
        self.active_event = self.__tabEvents[starterindex]
        self.active_event.set()

    def set_event(self, eventIndex):
        if not (0 <= eventIndex < len(self.__tabEvents)):
            raise Exception("eventIndex out of tabEvents range")
        self.active_event.clear()
        self.active_event = self.__tabEvents[eventIndex]
        self.active_event.set()

    def get_event(self, eventIndex):
        if not (0 <= eventIndex < len(self.__tabEvents)):
            raise Exception("eventIndex out of tabEvents range")
        return self.__tabEvents[eventIndex]

# class FileExplorerThreadRunner(QObject):
#     def __init__(self, client, view):
#         super().__init__()
#         self.view = view
#         self.client = client
#
#     def run(self):
#         time.sleep(10)

class ClientInspectorController(QObject):
    def requestMetrics(self, client, shownEvent : threading.Event, tabEvent : threading.Event):
        while shownEvent.wait() and tabEvent.wait():
            event = client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetSystemMetrics), track_event=True)
            event.wait()
            time.sleep(0.5)

    def __init__(self, view, client):
        super().__init__()
        self.tabEventManager = TabThreadEventManager(0, *[threading.Event() for i in range(6)])
        self.view = view
        self.client = client
        self.view.connectionInformationTable.initializeClient(client)
        self.shown = threading.Event()
        self.view.TabContainer.currentChanged.connect(self.tabChanged)
        self.view.pushButton_3.clicked.connect(self.remoteDekstopButtonClicked)
        self.fileExplorerManager = FileExplorerManager(client, self.view)
        self.remoteShellManager = RemoteShellManager(client, self)
        client.dataLock.acquire_read()

        # #start the file explorer thread
        # self.fileExplorerThread = QThread()
        # self.fileExplorerThread.setObjectName("File Explorer Thread")
        # self.worker = FileExplorerThreadRunner(self.fileExplorerThread, view)
        # self.worker.moveToThread(self.fileExplorerThread)
        # self.fileExplorerThread.started.connect(self.worker.run)
        # self.fileExplorerThread.start()

        if(client.systemInformation is None): #check if already have client information
            client.dataLock.release_read()
            client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetSystemInformation))
        else:
            client.dataLock.release_read()
            self.updateSystemInformation()
        thread1 = threading.Thread(target=self.requestMetrics, args=(client, self.shown, self.tabEventManager.get_event(0)))
        thread1.start()

    def startThreads(self):
        self.updateMetricsThread = threading.Thread(target=self.updateMetrics)
        self.updateMetricsThread.start()

    def remoteDekstopButtonClicked(self):
        worker = threading.Thread(target=ScreenShare.main(self.client))
        worker.start()

    def close(self):
        if self.shown.is_set():
            self.view.close()
            self.shown.clear()

    def show(self):
        if not self.shown.is_set():
            self.view.show()
            self.shown.set()

    def tabChanged(self, index):
        self.tabEventManager.set_event(index)
        if index == 1: #file explorer tab
            if not self.fileExplorerManager.is_initialized():
                self.fileExplorerManager.initializeContents()
        if index == 2: #remote shell tab
            self.remoteShellManager.tab_entered()

    def updateSystemInformation(self):
        self.client.dataLock.acquire_read()
        information = self.client.systemInformation
        self.view.SystemInformationTable.setItem(0, 1, QTableWidgetItem(information.DESKTOP_NAME))
        self.view.SystemInformationTable.setItem(1, 1, QTableWidgetItem(information.OPERATING_SYSTEM_VERSION))
        self.view.SystemInformationTable.setItem(2, 1, QTableWidgetItem(information.PROCESSOR_NAME))
        self.view.SystemInformationTable.setItem(3, 1, QTableWidgetItem(information.PROCESSOR_ARCHITECTURE))
        self.view.SystemInformationTable.setItem(4, 1, QTableWidgetItem(information.GPU_NAME))
        self.client.dataLock.release_read()


    def updateMetrics(self):
        self.client.dataLock.acquire_read()
        metrics = self.client.systemMetrics
        self.view.CPUUsagePrecentage.setText(f"{int(metrics.CPU_LOAD)}%")
        self.view.CPUUsageProgressBar.setValue(int(metrics.CPU_LOAD))
        self.view.GPUUsagePrecentage.setText(f"{int(metrics.GPU_LOAD)}%")
        self.view.GPUUsageProgressBar.setValue(int(metrics.GPU_LOAD))
        self.view.RamUsagePrecentage.setText(f"{int(metrics.RAM_LOAD)}%")
        self.view.RAMUsageProgressBar.setValue(int(metrics.RAM_LOAD))
        self.view.DiskUsagePrecentage.setText(f"{int(metrics.DISK_LOAD)}%")
        self.view.DiskUsageProgressBar.setValue(int(metrics.DISK_LOAD))
        self.client.dataLock.release_read()
        self.view.CPUUsagePrecentage.repaint()
        self.view.GPUUsagePrecentage.repaint()
        self.view.RamUsagePrecentage.repaint()
        self.view.DiskUsagePrecentage.repaint()