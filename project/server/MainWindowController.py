from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, QThreadPool, pyqtSlot
import GUIHelpers
from NetProtocol import *
import logging
from UIClientEntry import UIClientEntry
from InspectionWindowView import ClientInspectorView
from InspectionWindowController import ClientInspectorController
from PyQt5.QtWidgets import QMessageBox
import functools
from collections import OrderedDict
import MWindowModel

class MainWindowController(QObject):
    sThreadPool_runningTaskCountChanged = pyqtSignal()
    sUpnp_status = pyqtSignal(bool, str)

    def __init__(self, view, databaseClients):
        super().__init__()
        self.view = view
        self.sThreadPool_runningTaskCountChanged.connect(self.onThreadPoolTaskCountChange)
        self.sUpnp_status.connect(self.onUpnpStatus)
        self.view.ClientTable.cellClicked.connect(self.onSelection)
        self.view.ToolBarOpenAction.triggered.connect(self.onClientInspect)
        self.view.ToolBarRefreshConnectionAction.triggered.connect(self.onClientRefresh)
        self.view.ToolBarDeleteAction.triggered.connect(self.onClientDelete)
        self.logger = logging.getLogger()

        # dictionary of inspection window controllers for each client
        self.inspected_clients = {} #uuid : windowController
        # self.connectUISignals()
        self.clientEntries = OrderedDict() #uuid : UIClientEntry
        self.selection = None #UIClientEntry

        # add the clients that were restored from the database as
        for databaseclient in databaseClients:
            clientEntry = UIClientEntry(None, "Disconnected (restored from database)", databaseclient[1], databaseclient[0])
            clientEntry.addToTable(self.view.ClientTable)
            self.clientEntries[databaseclient[0]] = clientEntry # add the UIClientEntry to clientEntries with the uuid as the key

    def onUpnpStatus(self, status, err):
        if status:
            self.view.statusBar.showMessage("UPnP port forwarding enabled successfully!")
        else:
            msgBox = GUIHelpers.getinfobox("UPnP Port Forwarding Error", err, self.view)
            msgBox.show()
            self.view.statusBar.showMessage("UPnP port forwarding failed!")

    def onThreadPoolTaskCountChange(self):
        """
        Function that is called when the thread pool task count changes. It updates the status bar with the current task count.
        """
        pass
        # self.view.statusBar.showMessage(f"Thread pool task count: {QThreadPool.globalInstance().activeThreadCount()}/12")

    def createClientInspector(self, client):
        """
        Create a new client inspector window for the client, and show it. Additionally, the function connects the window's exitEvent to the exitEvent function, that deletes the client inspector (and closes the window).
        Args:
            client: the client instance to create a client inspector on.
        """
        window = ClientInspectorView()
        window.exitEvent.connect(functools.partial(self.exitEvent, client=client))
        windowController = ClientInspectorController(window, client)
        self.inspected_clients[client.uuid] = windowController
        windowController.show()

    def deleteClientInspector(self, client):
        """
        Searches for the client inspector window for the given client, pops it from the inspected_clients dictionary, sets the internal connected event to false, and closes the window.
        Args:
            client: the client instance with the client inspector window that is being deleted.
        """
        if client.uuid in self.inspected_clients:
            window = self.inspected_clients.pop(client.uuid) #remove from inspected clients
            window.close() #call InspectionWindowController.close()

    def exitEvent(self, event, client):
        """
        Function that is called when the client inspector window is closed. It calls deleteClientInspector, that deletes the client inspector and closes the window.
        Args:
            event: automatically passed in by Qt's event system.
            client: the client instance with the client inspector window that is being closed.
        """
        self.logger.info(f"Client inspection {client.address} exited")
        self.deleteClientInspector(client)

    def onClientRefresh(self, checked):
        '''
        Function that is called when the refresh connection button is clicked. Stops the connection (so the client can automatically reconnect after 5 seconds.
        Args:
            checked: qt passed in??
        '''
        self.selection.client.disconnect()

    def onClientInspect(self, checked):
        """
        Function that is called when the inspect button is clicked. It creates a new client inspector window for the selected client and shows it by calling createClientInspector.
        Args:
            checked: qt passed in??
        """
        if self.selection is not None and self.selection.client is not None: #verify that there is a selection and selection is a connected client
            if self.inspected_clients.get(self.selection.client.uuid) != None:
                GUIHelpers.infobox("Client already inspected", f"The client {self.selection.client.address} is already being inspected.", self.view)
            else:
                self.logger.info(f"Inspecting client {self.selection.client.address[0]}")
                self.createClientInspector(self.selection.client)

    def onClientDelete(self, checked):
        """
        Function that is called when the delete button is clicked. It deletes the selected client and removes it from the clientEntries dictionary.
        Also, it removes it from the database, and closes the connection to the client.
        Args:
            checked: qt passed in??
        """
        self.logger.info(f"Deleting client {self.selection._address_field.text()}")
        self.selection.client.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetUninstallClient))
        self.selection.client.disconnect()

    def onSelection(self, row, column):
        """
        Function that is called when a client is selected in the client table. It sets the selection to the selected client's UIClientEntry.
        Args:
            row:
            column:
        """
        self.logger.info(f"Selection changed to {row}")
        self.selection = list(self.clientEntries.items())[row][1] #set selection to UIClientEntry

    def on_Latency_updates(self, updates: typing.Dict):
        '''
        Responds to the GLOBAL latencySignal and updates the given latencies for the clients.
        Args:
            updates: a dict{uuid:latency} specifying the latencies of each client by their uuid.
        '''
        for uuid in updates.keys():
            self.clientEntries[uuid].setLatency(updates[uuid])
            inspect_window = self.inspected_clients.get(uuid)
            if inspect_window is not None:
                pass
                # TODO - create latency bar in UI

    def on_SystemInformation_update(self, client):
        """
        Function that responds to the sSystemInformation signal. It updates the client's UIClientEntry with a connected status, and a desktop name.
        Additionally, it calls the updateSystemInformation function of the client's client inspector, if one exists (if found in the inspected_clients list).
        Args:
            client: the client instance that had a system information update.
        """
        self.logger.info(f"Data update from {client.address}")
        if client.uuid in self.clientEntries:

            client.dataLock.acquire_read()
            #set status and desktop name
            self.clientEntries[client.uuid].setStatus("Connected")
            self.clientEntries[client.uuid].setName(client.systemInformation.DESKTOP_NAME)
            client.dataLock.release_read()

            if client.uuid in self.inspected_clients: #update the system information if an inspection window is open by calling updateSystemInformation
                self.inspected_clients[client.uuid].updateSystemInformation()

    def on_SystemMetrics_update(self, client):
        """
        Function that responds to the sSystemMetrics signal. It calls the updateMetrics function of the client's client inspector, if one exists (if found in the inspected_clients list).
        Args:
            client: the client instance that had a system information update.
        """
        self.logger.info(f"Metrics update from {client.address}")
        if client.uuid in self.inspected_clients:
            self.inspected_clients[client.uuid].updateMetrics()

    def on_Connection_start(self, client):
        """
        Function that responds to the sConnectionStart signal. It sets the client's UIClientEntry to connecting, and updates the address and country fields according to the client's GeoInfo datastructure.
        Args:
            client: the client that a connection was started for.
        """
        self.logger.info(f"Connection event received - {client.address}")
        # if client not in self.clientEntries:
        client.dataLock.acquire_read()

        #find the index of the client in the table if there is one
        # for uuid, UIEntry in list(self.clientEntries.items()):
        #     if client.uuid == UIEntry._uuid_field.text():
        #         found = True
        #         break

        # if client isn't in table, add it
        if not client.uuid in self.clientEntries:
            self.clientEntries[client.uuid] = UIClientEntry(client, "Connecting...", client.geoInformation.REAL_IP, client.uuid, client.geoInformation.CITY + ", " + client.geoInformation.COUNTRY)
            self.clientEntries[client.uuid].addToTable(self.view.ClientTable)

        # if client is already in table (restored from database or just disconnected before), then add it, and and set the UIEntry's client field to the client instance.
        else:
            self.clientEntries[client.uuid].setStatus("Connecting...")
            self.clientEntries[client.uuid].setAddress(client.geoInformation.REAL_IP)
            self.clientEntries[client.uuid].setCountry(client.geoInformation.CITY + ", " + client.geoInformation.COUNTRY)
            self.clientEntries[client.uuid].client = client #set the UIEntry's client to the client object

        client.dataLock.release_read()
        # send request for system information
        client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetSystemInformation))

    def on_Connection_end(self, client):
        """
        Function that responds to the sConnectionEnd signal. It sets the client's UIClientEntry to disconnected, and if the client has a inspection window open, then close it, and alert the user.
        Args:
            client: the client that a connection was started for.
        """
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