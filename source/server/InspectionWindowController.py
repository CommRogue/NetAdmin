from NetProtocol import *
import time
import threading
import functools
from PyQt5.QtCore import pyqtSignal, QThread, QObject, QRunnable, QThreadPool
import typing
from PyQt5.QtWidgets import QTableWidgetItem, QTreeWidgetItem, QTreeWidgetItemIterator

from source.server.InspectionWindowView import FileExplorerItem


def clearItemChildren(item):
    # print("started")
    # while(item.childCount() > 0):
    #     child = item.child(0)
    #     item.removeChild(child)
    #     del child
    # print("finished")
    pass


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


class DirectoryListingAction(QRunnable):
    def __init__(self, client, view, itemParent=None):
        super().__init__()
        self.itemParent = itemParent
        self.view = view
        self.client = client

    def run(self):
        if self.itemParent: #if the click is directed towards a directory and not just the drives
            path = self.itemParent.path
            self.itemParent.insertChild(0, QTreeWidgetItem(["Loading..."]))
        else: #if directory is the drives (root)
            #self.view.fileViewer.insertTopLevelItem(0, QTreeWidgetItem(["Loading..."]))
            path = "" #set the path to none to get root directory listing
        event = self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetDirectoryListing, id=None, extra=path), track_event=True)
        event.wait()
        data = event.get_data()
        if self.itemParent: #if a directory, then clear the "Loading..." item or the previous items from the last click
            clearItemChildren(self.itemParent)
        for item in data.items:
            if self.itemParent: #if must connect as a child to another item in the tree view
                if item['itemtype'] == NetTypes.NetDirectoryFolderCollapsable.value:
                    collapsable = True
                else:
                    collapsable = False
                self.itemParent.insertChild(0, FileExplorerItem(item["name"], item["path"], collapsable, None, None))
            else:
                self.view.fileViewer.insertTopLevelItem(0, FileExplorerItem(item["name"], item["path"], True, None, None))


class ClientInspectorController:
    def requestMetrics(self, client, shownEvent : threading.Event, tabEvent : threading.Event):
        while shownEvent.wait() and tabEvent.wait():
            event = client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetSystemMetrics), track_event=True)
            print("sent request, waiting for response")
            event.wait()
            print("got response")
            time.sleep(0.5)

    def __init__(self, view, client):
        self.fileExplorerInitialized = False
        self.tabEventManager = TabThreadEventManager(0, *[threading.Event() for i in range(2)])
        self.view = view
        self.client = client
        self.shown = threading.Event()
        self.view.tabWidget.currentChanged.connect(self.tabChanged)
        self.view.fileViewer.itemExpanded.connect(self.fileViewerItemExpanded)
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

    def fileViewerItemExpanded(self, item):
        threadPool = QThreadPool.globalInstance()
        threadPool.start(DirectoryListingAction(self.client, self.view, item))

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
        if index == 1: #file explorer tab
            if not self.fileExplorerInitialized:
                self.fileExplorerInitialized = True
                threadPool = QThreadPool.globalInstance()
                threadPool.start(DirectoryListingAction(self.client, self.view, None))

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