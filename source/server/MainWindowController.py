import threading
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, QThreadPool, pyqtSlot
from MainWindowModel import Client
from NetProtocol import *
import logging
from UIClientEntry import UIClientEntry
from InspectionWindowView import ClientInspectorView
from InspectionWindowController import ClientInspectorController
from PyQt5.QtWidgets import QMessageBox

class MainWindowController(QObject):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.view.ClientTable.cellClicked.connect(self.onSelection)
        self.view.ToolBarOpenAction.triggered.connect(self.onClientInspect)
        self.view.ToolBarDeleteAction.triggered.connect(self.onClientDelete)
        self.logger = logging.getLogger()
        self.inspected_clients = {}
        # self.connectUISignals()
        self.clientEntries = {}
        self.rows = []
        self.selection = None
        # self.model = model

    def createClientInspector(self, client):
        window = ClientInspectorView()
        windowController = ClientInspectorController(window, client)
        self.inspected_clients[client] = windowController
        windowController.show()

    def deleteClientInspector(self, client):
        if client in self.inspected_clients:
            window = self.inspected_clients.pop(client)
            window.close()

    def onClientInspect(self, checked):
        self.logger.info(f"Inspecting client {self.selection.client.address[0]}")
        self.createClientInspector(self.selection.client)

    def onClientDelete(self, checked):
        self.logger.info(f"Deleting client {self.selection.client.address[0]}")

    def onSelection(self, row, column):
        self.logger.info(f"Selection changed to {row}")
        self.selection = self.rows[row]

    def on_SystemInformation_update(self, client):
        self.logger.info(f"Data update from {client.address}")
        if client in self.clientEntries:
            client.dataLock.acquire_read()
            self.clientEntries[client].setStatus("Connected")
            self.clientEntries[client].setName(client.systemInformation.DESKTOP_NAME)
            client.dataLock.release_read()

    def on_SystemMetrics_update(self, client):
        self.logger.info(f"Metrics update from {client.address}")
        if client in self.inspected_clients:
            self.inspected_clients[client].updateMetrics()

    def on_Connection_start(self, client):
        self.logger.info(f"Connection event received - {client.address}")
        if client not in self.clientEntries:
            client.dataLock.acquire_read()
            self.clientEntries[client] = UIClientEntry(client, "Connecting...", client.geoInformation.REAL_IP, client.geoInformation.CITY + ", " + client.geoInformation.COUNTRY)
            self.clientEntries[client].addToTable(self.view.ClientTable)
            self.rows.append(self.clientEntries[client])
            client.dataLock.release_read()
            client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetSystemInformation))

    def on_Connection_end(self, client):
        self.logger.info(f"Disconnection event received - {client.address}")
        if client in self.clientEntries:
            self.clientEntries[client].removeFromTable()
            self.rows.remove(self.clientEntries[client])
            self.clientEntries.pop(client)
        if client in self.inspected_clients:
            self.deleteClientInspector(client)
            dialog = QMessageBox()
            dialog.setText("The client you have been inspecting has disconnected.")
            dialog.setWindowTitle("Client disconnected")
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.exec_()