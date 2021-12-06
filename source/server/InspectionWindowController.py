from NetProtocol import *
import time
import threading
import functools
from PyQt5.QtCore import pyqtSignal
import typing
from PyQt5.QtWidgets import QTableWidgetItem

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

class ClientInspectorController:
    def requestMetrics(self, client, shownEvent : threading.Event, tabEvent : threading.Event):
        while shownEvent.wait() and tabEvent.wait():
            client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetSystemMetrics))
            time.sleep(1)

    def __init__(self, view, client):
        self.tabEventManager = TabThreadEventManager(0, *[threading.Event() for i in range(2)])
        self.view = view
        self.client = client
        self.shown = threading.Event()
        self.view.tabWidget.currentChanged.connect(self.tabChanged)
        client.dataLock.acquire_read()
        if(client.systemInformation is None):
            client.dataLock.release_read()
            client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetSystemInformation))
        else:
            client.dataLock.release_read()
            self.updateSystemInformation()
        thread = threading.Thread(target=self.requestMetrics, args=(client, self.shown, self.tabEventManager.get_event(0)))
        thread.start()

    def startThreads(self):
        self.updateMetricsThread = threading.Thread(target=self.updateMetrics)
        self.updateMetricsThread.start()

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