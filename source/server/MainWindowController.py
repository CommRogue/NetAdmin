import threading
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, QThreadPool, pyqtSlot
from MainWindowModel import Client
from NetProtocol import *
import logging
from UIClientEntry import UIClientEntry
from InspectionWindowView import ClientInspectorView
from InspectionWindowController import ClientInspectorController
from PyQt5.QtWidgets import QMessageBox
import functools
from collections import OrderedDict

class MainWindowController(QObject):
    def __init__(self, view, databaseClients):
        super().__init__()
        self.view = view
        self.view.ClientTable.cellClicked.connect(self.onSelection)
        self.view.ToolBarOpenAction.triggered.connect(self.onClientInspect)
        self.view.ToolBarDeleteAction.triggered.connect(self.onClientDelete)
        self.logger = logging.getLogger()
        self.inspected_clients = {} #uuid : windowController
        # self.connectUISignals()
        self.clientEntries = OrderedDict() #uuid : UIClientEntry
        self.selection = None #UIClientEntry
        for databaseclient in databaseClients:
            clientEntry = UIClientEntry(None, "Disconnected (restored from database)", databaseclient[1], databaseclient[0])
            clientEntry.addToTable(self.view.ClientTable)
            self.clientEntries[databaseclient[0]] = clientEntry

        # self.model = model

    def createClientInspector(self, client):
        window = ClientInspectorView()
        window.exitEvent.connect(functools.partial(self.exitEvent, client=client))
        windowController = ClientInspectorController(window, client)
        self.inspected_clients[client.uuid] = windowController
        windowController.show()

    def deleteClientInspector(self, client):
        if client.uuid in self.inspected_clients:
            window = self.inspected_clients.pop(client.uuid) #remove from inspected clients
            window.close() #call InspectionWindowController.close()

    def exitEvent(self, event, client):
        self.logger.info(f"Client inspection {client.address} exited")
        self.deleteClientInspector(client)

    def onClientInspect(self, checked):
        if self.selection is not None and self.selection.client is not None: #verify that there is a selection and selection is a connected client
            self.logger.info(f"Inspecting client {self.selection.client.address[0]}")
            self.createClientInspector(self.selection.client)

    def onClientDelete(self, checked):
        self.logger.info(f"Deleting client {self.selection._address_field.text()}")

    def onSelection(self, row, column):
        self.logger.info(f"Selection changed to {row}")
        self.selection = list(self.clientEntries.items())[row][1] #set selection to UIClientEntry

    def on_SystemInformation_update(self, client):
        self.logger.info(f"Data update from {client.address}")
        if client.uuid in self.clientEntries:
            client.dataLock.acquire_read()
            self.clientEntries[client.uuid].setStatus("Connected")
            self.clientEntries[client.uuid].setName(client.systemInformation.DESKTOP_NAME)
            client.dataLock.release_read()
            if client.uuid in self.inspected_clients: #update the system information if an inspection window is open
                self.inspected_clients[client.uuid].updateSystemInformation()

    def on_SystemMetrics_update(self, client):
        self.logger.info(f"Metrics update from {client.address}")
        if client.uuid in self.inspected_clients:
            self.inspected_clients[client.uuid].updateMetrics()

    def on_Connection_start(self, client):
        self.logger.info(f"Connection event received - {client.address}")
        if client not in self.clientEntries:
            client.dataLock.acquire_read()
            found = False
            b = list(self.clientEntries.items())
            for uuid, UIEntry in list(self.clientEntries.items()): #find the index of the client in the table if there is one
                if uuid == UIEntry._uuid_field.text():
                    found = True
                    break
            if not found: #if client isn't in table, add it
                self.clientEntries[client.uuid] = UIClientEntry(client, "Connecting...", client.geoInformation.REAL_IP, client.uuid, client.geoInformation.CITY + ", " + client.geoInformation.COUNTRY)
                self.clientEntries[client.uuid].addToTable(self.view.ClientTable)
            else: #if client is already in table, then add it, and add the client object to the UIClientEntry
                self.clientEntries[client.uuid].setStatus("Connecting...")
                self.clientEntries[client.uuid].setAddress(client.geoInformation.REAL_IP)
                self.clientEntries[client.uuid].setCountry(client.geoInformation.CITY + ", " + client.geoInformation.COUNTRY)
                self.clientEntries[client.uuid].client = client #set the UIEntry's client to the client object
            client.dataLock.release_read()
            client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetSystemInformation))

    def on_Connection_end(self, client):
        self.logger.info(f"Disconnection event received - {client.address}")
        if client.uuid in self.clientEntries:
            self.clientEntries[client.uuid].setDisconnected() #set client state to disconnected
        if client.uuid in self.inspected_clients: #display messagebox if client is being inspected and was disconnected
            self.deleteClientInspector(client)
            dialog = QMessageBox()
            dialog.setText("The client you have been inspecting has disconnected.")
            dialog.setWindowTitle("Client disconnected")
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.exec_()