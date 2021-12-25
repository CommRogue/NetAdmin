import os
import sys
import typing
import re
import json
from urllib.request import urlopen
import threading
import socket
import select
import uuid
import queue
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, QThreadPool
import functools
import orjson
from time import sleep
import logging
import SocketLock
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlError, QSqlQueryModel
import uuid
import UniqueID
sys.path.insert(1, os.path.join(sys.path[0], '../shared'))
from NetProtocol import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# the UID instance for generating IDs for each message to be echoed by the client
UniqueIDInstance = UniqueID.UniqueIDInstance()

# stored events that are used by functions that call send_message and are tracking the response
response_events = {}

clients = {}

logging.basicConfig(format=bcolors.WARNING + '%(asctime)s - %(threadName)s - %(levelname)s:' + bcolors.OKGREEN + '    %(message)s' + bcolors.END, level=logging.DEBUG)

class DataEvent(threading.Event):
    '''
    An override of the threading.Event class that allows for the data to be stored in the event,
    so that it can be accessed by the thread that is waiting on the event to finish.
    '''

    def __init__(self):
        super().__init__()
        self.data = None

    def set_data(self, data):
        """
        sets the event's data. may only be called once.
        Args:
            data: the data to be stored in the event
        """
        #check if there is no data already stored in the event
        if self.data == None:
            self.data = data

        #if there is data already stored in the event, raise an exception
        else:
            raise Exception('Cannot reset data of a DataEvent object')

    def get_data(self):
        """
        gets the event's data.
        Returns: the event's data.

        """
        return self.data

class Client(QObject):
    #synchronization objects
    #uuid of the client
    uuid = None

    #condition to tell the ConnectionHandler that client identified
    identificationNotification = threading.Condition()
    #tuple of (is_identified, is_new) to tell ConnectionHandler how to react
    identificationNotificationResource = None

    #custom write-read lock for each client so data can be read by multiple threads and written by only one thread at the same time
    dataLock = SocketLock.SocketLock()

    #queue for storing messages to be sent to the client by the select.select loop
    _message_queue = queue.Queue()

    # Data segments
    # ---------------
    connectionData = None
    systemInformation = None
    systemMetrics = None
    geoInformation = None

    # Signals
    # ---------------
    sSystemInformation_update = pyqtSignal()
    sSystemMetrics_update = pyqtSignal()
    sConnection_start = pyqtSignal()
    sConnection_end = pyqtSignal()

    #toString function
    def __str__(self):
        """
        returns the formatted address of the client as a string.
        Returns: formatted address of the client.

        """
        return f"{self.address}"

    def __init__(self, socket, address):
        super().__init__()
        #self.client_id = client_id
        self._socket = socket
        self.address = address
        self._socket_lock = threading.Lock()

    def close(self):
        """
        closes the client and emits a connection_end signal.
        """
        self.connection_end.emit()
        self.socket.close() #check for problems



    def send_message(self, data : NetMessage, track_event=False):
        logging.debug(f"Sending message {data}")
        if track_event: #if wants to track the response, then add an id to the message and add it to the response_events dict and return the event
            id = UniqueIDInstance.getId()
            response_events[id] = DataEvent()
            data.id = id #send the id to the client so it can copy it
            self._message_queue.put(NetProtocol.packNetMessage(data))
            return response_events[id]
        else:
            self._message_queue.put(NetProtocol.packNetMessage(data))

class DatabaseHelpers:
    @staticmethod
    def open_database(path):
        """
        opens the database connection to the database at the given path.
        Args:
            path: the path to the database

        Returns: a new database connection to the database at the given path.

        """
        con = QSqlDatabase.addDatabase("QSQLITE")
        con.setDatabaseName(path)
        if not con.open():
            print("Failed to open database")
            sys.exit(1)
        return con

    @staticmethod
    def find_client(database : QSqlDatabase, uuid : str):
        """
        finds a client in the database specified with the specified uuid.
        Args:
            uuid: the client's uuid to search for.

        Returns: a tuple of (client_address, client_uuid) if the client is found, None otherwise.

        """
        findClients = QSqlQuery(database)
        findClients.exec_("SELECT uuid, address FROM clients WHERE uuid = '" + uuid + "'")
        if findClients.next():
            logging.debug(f"Found client in database {uuid}")
        else:
            return None

        # ---- suggested autopilot code ---- (consider using this)
        # query = QSqlQuery(database)
        # query.prepare("SELECT uuid, address FROM clients WHERE uuid = (:uuid)")
        # query.bindValue(":uuid", uuid)
        # query.exec_()
        # if query.next():
        #     return Client(uuid=uuid)
        # else:
        #     return None

    @staticmethod
    def insert_client(database : QSqlDatabase, uuid : str, address : str):
        logging.debug(f"Inserting client {uuid} at {address}")
        insertClient = QSqlQuery(database)
        insertClient.prepare(f"INSERT INTO clients (uuid, address) VALUES (?, ?)")
        insertClient.addBindValue(uuid)
        insertClient.addBindValue(address)
        insertClient.exec_()



class MessageHandler(QRunnable):
    """
    A job that handles a message sent to it by the communicator thread.
    """
    def __init__(self, client: Client, message: bytes):
        super().__init__()
        self.client = client
        self._message_bytes = message
        self.message = None

    def run(self) -> None:
        # set the event data used to track the response to None
        eventAttachedData = None

        # unpack the message from bytes (done here so unpacking is done by the thread and not the communicator)
        self.message = orjson.loads(self._message_bytes)
        logging.debug(f"MessageHandler running with message {self.message} from client {self.client.address}")


        # --- start of message handling ---

        if self.message["type"] == NetTypes.NetRequest:
            pass

        # if client sent an error
        elif self.message["type"] == NetTypes.NetError.value:
            logging.error(f"Error from client {self.client.address}: {self.message['data']}")

            # if invalid access to a directory while browsing files
            if self.message['data']['errorCode'] == NetErrors.NetDirectoryAccessDenied.value:
                # set the event data to the error message
                datastructure = NetError(**self.message['data'])
                eventAttachedData = datastructure

        # if related to identification
        elif self.message["type"] == NetTypes.NetIdentification.value: #check if client sent ID or else send ID
            #if existing client sent identification
            if self.message['data']["id"] != "":
                # check if id is found in database

                self.client.uuid = self.message['data']["id"]
                logging.debug(f"Client {self.client.address} identified as {self.client.uuid}")
                self.client.identificationNotification.acquire()
                self.client.identificationNotification.notify_all()
                self.client.identificationNotification.release()

            # if new client wants identification
            else:
                cid = str(uuid.uuid4())
                logging.info(f"Client {self.client.address} sent identification request. Generating new ID {cid} and sending...")
                self.client.send_message(NetMessage(NetTypes.NetIdentification, NetIdentification(cid))) #send a client id
                self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetIdentification)) #request to identify again

        # if related to response to system information
        elif self.message["type"] == NetTypes.NetSystemInformation.value:
            data = self.message["data"]
            dataStructure = NetSystemInformation(**data)

            self.client.dataLock.acquire_write()
            self.client.systemInformation = dataStructure
            self.client.dataLock.release_write()

            self.client.sSystemInformation_update.emit()
        elif self.message["type"] == NetTypes.NetSystemMetrics.value: #if a message is metrics
            data = self.message["data"]
            dataStructure = NetSystemMetrics(**data)
            if(dataStructure.CPU_LOAD == None): #fix for cpu load being None
                dataStructure.CPU_LOAD = 0
            self.client.dataLock.acquire_write()
            self.client.systemMetrics = dataStructure
            self.client.dataLock.release_write()
            self.client.sSystemMetrics_update.emit()
        elif self.message["type"] == NetTypes.NetDirectoryListing.value:
            data = self.message["data"]
            dataStructure = NetDirectoryListing(**data)
            eventAttachedData = dataStructure
        if self.message["id"] is not None: #check is message has response id
            UniqueIDInstance.releaseId(self.message["id"]) #release the id from the id pool
            if eventAttachedData is not None: #if there is data to attach to the event
                response_events[self.message["id"]].set_data(eventAttachedData)
            response_events[self.message["id"]].set() #set the event to notify the waiting thread
            response_events.pop(self.message["id"]) #remove the event from the response events

class ClientConnectionHandler(QRunnable):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    def run(self) -> None:
        logging.debug(f"ClientConnectionHandler running with client {self.client.address}")
        self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetIdentification))
        self.client.identificationNotification.acquire()

        #wait for the client to identify for 10 seconds
        result = self.client.identificationNotification.wait(10)

        if not result:
            raise Exception("ClientConnectionHandler did not receive a response to the identification request it sent to the client...")

        resultData = self.client.identificationNotificationResource
        self.client.identificationNotification.release()

        #NOTE - WE CAN'T SET RESULT DATA 0 (WHETHER IDENTIFIED OR NOT), SO INSTEAD, JUST STORE WHETHER FOUND IN DATABASE OR NOT (NO TUPLE), AND CHECK IF IDENTIFIED VIA THE RESULT OF IDENTIFICATIONNOTIFICATION

        #if client identified
        if not resultData[0]:
            logging.warning(f"Client {self.client.address} timed out while identifying")
            #optionally remove the client from the global list?


        # ---- add client to database if needed (specified by the identification data ----
        if resultData[1]: # if new client (need to add to database)
            #open database
            con = DatabaseHelpers.open_database(os.getenv("LOCALAPPDATA")+"\\NetAdmin\\clients.db")

            ########DELETE
            # findClients = QSqlQuery()
            # findClients.exec_("SELECT uuid, address FROM clients WHERE uuid = '" + self.client.uuid + "'")
            # if findClients.next():
            #     logging.debug(f"Client {self.client.uuid} already in database")

            # insert the client into the database
            DatabaseHelpers.insert_client(con, self.client.uuid, self.client.address[0])

                ############DELETE
                # logging.debug(f"Client {self.client.uuid} not in database. Adding to database....")
                # addClient = QSqlQuery()
                # addClient.prepare(f"INSERT INTO clients (uuid, address) VALUES (?, ?)")
                # addClient.addBindValue(str(self.client.uuid))
                # addClient.addBindValue(str(self.client.address[0]))
                # addClient.exec_()
            con.close()

        if self.client.address[0] != "127.0.0.1":
            response = urlopen(f"http://ipinfo.io/{self.client.address[0]}/json")
        else:
            response = urlopen("http://ipinfo.io/json")
        data = json.load(response)
        IP = data['ip']
        org = data['org']
        city = data['city']
        country = data['country']
        region = data['region']

        self.client.dataLock.acquire_write()
        self.client.geoInformation = NetGeoInfo(country, city, IP)
        self.client.dataLock.release_write()
        self.client.sConnection_start.emit() #emit signal to update UI


class ListenerWorker(QObject):
    clients_lock = threading.Lock()
    global clients
    sockets = []
    # message_queues = {}

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def connectSignals(self, connection : socket):
        clients[connection].sSystemInformation_update.connect(functools.partial(self.controller.on_SystemInformation_update, clients[connection]))
        clients[connection].sSystemMetrics_update.connect(functools.partial(self.controller.on_SystemMetrics_update, clients[connection]))
        clients[connection].sConnection_end.connect(functools.partial(self.controller.on_Connection_end, clients[connection]))
        clients[connection].sConnection_start.connect(functools.partial(self.controller.on_Connection_start, clients[connection]))

    def CommandLineEcho(self):
        while True:
            inp = input("")
            for client in clients.values():
                if (inp == "information"):
                    client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetSystemInformation))

    def run(self):
        #model
        #listener checks for socket descriptor readability and writability
        #readability - if listener socket, accept new connection, otherwise recv and launch message handler on thread pool
        #writability - message queue of NetMessages that the controller thread makes. send the message when the socket is writable and there is a message in the queue

        threadPool = QThreadPool.globalInstance()
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_socket.bind(('0.0.0.0', 49152))
        self.listener_socket.listen(5)
        thread = threading.Thread(target=self.CommandLineEcho)
        thread.start()

        while True:
            readable, writable, exceptional = select.select([self.listener_socket] + self.sockets, self.sockets, [])
            for s in readable:
                if s is self.listener_socket:
                    connection, client_address = s.accept()
                    self.sockets.append(connection)
                    # self.message_queues[connection] = queue.Queue()
                    clients[connection] = Client(connection, client_address)
                    self.connectSignals(connection) #connect signals from the client to the controller
                    logging.debug(f"{clients[connection].address} connected")
                    threadPool.start(ClientConnectionHandler(clients[connection]))
                else:
                    size, message = NetProtocol.unpackFromSocket(s)
                    if size == -1:
                        logging.debug(f"{clients[s].address} disconnected")
                        self.sockets.remove(s)
                        cl = clients.pop(s)
                        s.close()
                        cl.sConnection_end.emit()
                    elif size != 0:
                        threadPool.start(MessageHandler(clients[s], message))

            for s in writable:
                if not s._closed and not clients[s]._message_queue.empty():
                    message = clients[s]._message_queue.get_nowait()
                    if(type(message) is bytes):
                        s.send(message)
                    else:
                        logging.error(f"Received non-bytes message on message-queue of {clients[s].address}")
            #cycle delay
            sleep(0.01)

class MainWindowModel: #fix main window closing and not client inspection windows
    def __init__(self, controller):
        #open communicator thread and listen
        self.communicator = QThread()
        self.communicator.setObjectName("Communicator Thread")
        print(threading.current_thread())
        self.worker = ListenerWorker(controller)
        self.worker.moveToThread(self.communicator)
        self.communicator.started.connect(self.worker.run)
        self.communicator.start()

    def socket_listen(self):
        pass

    def checkInstallation(self):
        pass

    def install(self):
        pass


#acquire and release client.socket_lock
    # def persist_connection(func):
    #     def wrapper(self, *args, **kwargs):
    #         try:
    #             self.client.socket_lock.acquire()
    #             return func(self, *args, **kwargs)
    #         except socket.error as e:
    #             if self.client.socket in clients:
    #                 c = clients.pop(self.socket)
    #                 print(f"Client {c} error: {str(e)}")
    #                 c.close()
    #         finally:
    #             self.client.socket_lock.release()
    #     return wrapper

#class GetSystemInfo(QRunnable):
#     def __init__(self, client: Client):
#         super().__init__()
#         self.client = client
#
#     @Client.persist_connection
#     def run(self) -> None:
#         # self.client.send_data(NetProtocol.heartbeat())
#         self.client.send_text("info")
#         response = self.client.read_text()
#         if response == "heartbeat":
#             print("heartbeat from ", self.client.address)
#
# class Heartbeat(QRunnable):
#     def __init__(self, client: Client):
#         super().__init__()
#         self.client = client
#
#     @Client.persist_connection
#     def run(self) -> None:
#         # self.client.send_data(NetProtocol.heartbeat())
#         self.client.send_text("heartbeat")
#         response = self.client.read_text()
#         if response == "heartbeat":
#             print("heartbeat from ", self.client.address)