import ipaddress
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

logging.basicConfig(format=bcolors.WARNING + '%(asctime)s - %(threadName)s - %(levelname)s:' + bcolors.OKGREEN + '    %(message)s' + bcolors.END, level=logging.INFO)

def threadpool_job_tracker(attr_str):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            attr = getattr(self, attr_str)
            attr.emit()
            func(self, *args, **kwargs)
            attr.emit()
        return wrapper
    return decorator

# class DataEvent(threading.Condition):
#     '''
#     An override of the threading.Event class that allows for the data to be stored in the event,
#     so that it can be accessed by the thread that is waiting on the event to finish.
#     '''
#
#     def __init__(self):
#         super().__init__()
#         self.data = None
#
#     @staticmethod
#     def _acquire_lock(func):
#         def wrapper(self, *args, **kwargs):
#             with self:
#                 func(*args, **kwargs)
#         return wrapper
#
#     def wait(self, timeout = None) -> bool:
#         with self:
#             if timeout:
#                 return super().wait(timeout)
#             else:
#                 return super().wait()
#
#     def set(self):
#         """
#         sets the event.
#         """
#         with self:
#             super().notify_all()
#
#
#     @_acquire_lock
#     def set_data(self, data):
#         """
#         sets the event's data. may only be called once.
#         Args:
#             data: the data to be stored in the event
#         """
#         #check if there is no data already stored in the event
#         if self.data == None:
#             self.data = data
#
#         #if there is data already stored in the event, raise an exception
#         else:
#             raise Exception('Cannot reset data of a DataEvent object')
#
#     @_acquire_lock
#     def get_data(self):
#         """
#         gets the event's data.
#         Returns: the event's data.
#
#         """
#         return self.data

class DataEvent(threading.Event):
    '''
    An override of the threading.Event class that allows for the data to be stored in the event,
    so that it can be accessed by the thread that is waiting on the event to finish.
    '''

    def __init__(self):
        super().__init__()
        self.data = None
        self.extra = None

    def set_data(self, data, extra=None):
        """
        sets the event's data. may only be called once.
        Args:
            data: the data to be stored in the event
        """
        #check if there is no data already stored in the event
        self.extra = extra
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

    def get_extra(self):
        """
        gets the event's extra data.
        Returns: the event's extra data.

        """
        return self.extra

class Client(QObject):
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
        get the formatted address of the client as a string.
        Returns: formatted address of the client.

        """
        return f"{self.address}"

    def __init__(self, socket, address):
        super().__init__()
        #self.client_id = client_id
        self._socket = socket
        self.address = address
        self._socket_lock = threading.Lock()

        # synchronization objects
        # uuid of the client
        self.uuid = None

        # condition to tell the ConnectionHandler that client identified
        self.identificationNotification = threading.Condition()

        # custom write-read lock for each client so data can be read by multiple threads and written by only one thread at the same time
        self.dataLock = SocketLock.SocketLock()
        # queue for storing messages to be sent to the client by the select.select loop
        self._message_queue = queue.Queue()

    def close(self):
        """
        closes the client and emits a connection_end signal.
        """
        self.connection_end.emit()
        self.socket.close() #check for problems

    def send_message(self, data : NetMessage, track_event=False):
        if track_event: #if wants to track the response, then add an id to the message and add it to the response_events dict and return the event
            id = UniqueIDInstance.getId()
            print(f"{id} for {str(data)}")
            if id not in response_events.keys():
                response_events[id] = DataEvent()
            else:
                raise Exception('Response event already exists')
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
            return (findClients.value(1), findClients.value(0))
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

    # qt signal for signaling that the task is started/finished to control the status bar task count

    def __init__(self, client: Client, message: bytes, taskCountEvent : pyqtSignal):
        super().__init__()
        self.client = client
        # undecoded message in bytes
        self._message_bytes = message
        # decoded message (set in the run method)
        self.message = None
        # qt signal for signaling that the task is started/finished to control the status bar task count
        self.event = taskCountEvent

    @threadpool_job_tracker("event")
    def run(self) -> None:
        # set the event data used to track the response to None
        eventAttachedData = None

        # unpack the message from bytes (done here so unpacking is done by the thread and not the communicator)
        self.message = orjson.loads(self._message_bytes)
        alertstr = f"{self.client.address} MessageHandler running with message {NetTypes(self.message['type'])}"
        if self.message['type'] == NetTypes.NetStatus.value:
            alertstr += f", {NetStatusTypes(self.message['data']['statusCode'])}"
        logging.debug(alertstr)


        # --- start of message handling ---

        if self.message["type"] == NetTypes.NetRequest:
            pass

        # if client sent an status code
        elif self.message["type"] == NetTypes.NetStatus.value:
            # set the event data to the status message
            datastructure = NetStatus(**self.message['data']) # 'data' field contains a NetError instance
            eventAttachedData = datastructure

        # if related to identification
        elif self.message["type"] == NetTypes.NetIdentification.value: #check if client sent ID or else send ID
            con = DatabaseHelpers.open_database(os.getenv("LOCALAPPDATA")+"\\NetAdmin\\clients.db")

            #if existing client sent identification
            if self.message['data']["id"] != "":
                # check if id is found in database
                found = DatabaseHelpers.find_client(con, self.message['data']["id"])

                # if id not found, log and send error to the client
                if found is None:
                    logging.debug(f"Client {self.client.address[0]} sent INVALID identification {self.message['data']['id']}")
                    self.client.send_message(NetMessage(NetTypes.NetStatus, NetStatusTypes.NetInvalidIdentification))

                #if identification is found and valid then log, set the local client instance's uid, and notify identificationNotification
                else:
                    logging.debug(f"Client {self.client.address[0]} sent valid identification {self.message['data']['id']}")
                    self.client.uuid = self.message['data']["id"]
                    logging.debug(f"Client {self.client.address} identified as {self.client.uuid}")
                    self.client.identificationNotification.acquire()
                    self.client.identificationNotification.notify_all()
                    self.client.identificationNotification.release()

            # if new client wants identification
            else:
                # generate a new uuid
                uid = uuid.uuid4().hex
                cid = uid
                logging.info(f"Client {self.client.address} sent identification request. Generating new ID {cid} and sending...")

                #send the new id to the client, add it to the database, and request the client to authunticate again
                self.client.send_message(NetMessage(NetTypes.NetIdentification, NetIdentification(cid))) #send a client id
                DatabaseHelpers.insert_client(con, cid, self.client.address[0])
                self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetIdentification)) #request to identify again

        # if related to response to system information
        elif self.message["type"] == NetTypes.NetSystemInformation.value:
            # load the system information datastructure from the message, update the local client instance, and emit sSystemInformation_update
            data = self.message["data"]
            dataStructure = NetSystemInformation(**data)

            self.client.dataLock.acquire_write()
            self.client.systemInformation = dataStructure
            self.client.dataLock.release_write()

            self.client.sSystemInformation_update.emit()

        # if related to response to directory size
        elif self.message["type"] == NetTypes.NetDirectorySize.value:
            # load the directory size datastructure from the message, update the local client instance, and emit sDirectorySize_update
            data = self.message["data"]
            dataStructure = NetDirectorySize(**data)
            eventAttachedData = dataStructure

        # if related to response to metrics
        elif self.message["type"] == NetTypes.NetSystemMetrics.value: #ADD CHECKS FOR VALID METRICS
            # load the system metrics datastructure from the message, update the local client instance, and emit sSystemMetrics_update
            data = self.message["data"]
            dataStructure = NetSystemMetrics(**data)

            if(dataStructure.CPU_LOAD == None): #fix for cpu load being None
                dataStructure.CPU_LOAD = 0

            self.client.dataLock.acquire_write()
            self.client.systemMetrics = dataStructure
            self.client.dataLock.release_write()
            self.client.sSystemMetrics_update.emit()

        # if related to response to directory listing
        elif self.message["type"] == NetTypes.NetDirectoryListing.value:
            # load the directory listing datastructure from the message, and set the event-attached-data to it, so the thread that called send_message will get the data
            data = self.message["data"]
            dataStructure = NetDirectoryListing(**data)
            eventAttachedData = dataStructure

        # lastly, check if the message is tracked by a thread
        # if so, then set the event, and optionally attach the data to it
        if self.message["id"] is not None and self.message["id"] in response_events: #check is message has response id and if it has an event associated with it
            UniqueIDInstance.releaseId(self.message["id"]) #release the id from the id pool
            # print(f"Response events before: {response_events}")
            if eventAttachedData is not None: #if there is data to attach to the event
                response_events[self.message["id"]].set_data(eventAttachedData, self.message["extra"])
            response_events[self.message["id"]].set() #set the event to notify the waiting thread
            response_events.pop(self.message["id"]) #remove the event from the response events
            # print(f"Response events after: {response_events}")


class ClientConnectionHandler(QRunnable):
    '''
    Job to handle a client connection.
    '''
    def __init__(self, client: Client, threadPoolTaskEvent : pyqtSignal):
        super().__init__()
        self.client = client
        self.event = threadPoolTaskEvent

    @threadpool_job_tracker("event")
    def run(self) -> None:
        '''
        Summary: send a identification request to the client, and wait for a response.
        If the response is a success, then the client is authenticated. Otherwise, it is removed from the client list (implement this!!!)
        After the identification, the function resolves the IP and gets the GEOInfo data of the IP, and updates the client instance with it.
        Lastly, the function emits a sConnection_start signal.
        '''

        logging.debug(f"ClientConnectionHandler running with client {self.client.address}")
        self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetIdentification))
        self.client.identificationNotification.acquire()

        #wait for the client to identify for 10 seconds
        result = self.client.identificationNotification.wait(10)
        self.client.identificationNotification.release()

        #if the client didn't identify within 10 seconds, close the connection (implement close connection
        if not result:
            logging.warning(f"ClientConnectionHandler did not receive a response to the identification request it sent to {self.client.address[0]}...")
            #....remove the client from the global list?
            return

        #if the client identified, resolve the client's IP address
        if self.client.address[0] != "127.0.0.1" and ipaddress.ip_address(self.client.address[0]).is_private != True: # if not our own computer or local IP on our network, then resolve the IP address
            response = urlopen(f"http://ipwhois.app/json/{self.client.address[0]}")
        else: # otherwise resolve our own IP address
            response = urlopen("http://ipwhois.app/json/")
        data = json.load(response)
        IP = data['ip']
        country = data.get('country', "N/A")
        city = data.get('city', "N/A")
        country_code = data.get('country_code', "N/A")
        isp = data.get('isp', "N/A")
        timezone = data.get('timezone_name', "N/A")

        self.client.dataLock.acquire_write()
        self.client.geoInformation = NetGeoInfo(IP, country, country_code, city, isp, timezone)
        self.client.dataLock.release_write()
        self.client.sConnection_start.emit() #emit signal to update UI


class ListenerWorker(QObject):
    '''
    The main communicator thread. Handles the sockets by selecting the active socket descriptors in a background-running loop.
    '''
    global clients
    sockets = []
    # message_queues = {}

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def connectSignals(self, connection : socket):
        """
        Connects the client's signals to the corresnponding slots in the controller.
        Args:
            connection: the client's socket.
        """
        clients[connection].sSystemInformation_update.connect(functools.partial(self.controller.on_SystemInformation_update, clients[connection]))
        clients[connection].sSystemMetrics_update.connect(functools.partial(self.controller.on_SystemMetrics_update, clients[connection]))
        clients[connection].sConnection_end.connect(functools.partial(self.controller.on_Connection_end, clients[connection]))
        clients[connection].sConnection_start.connect(functools.partial(self.controller.on_Connection_start, clients[connection]))

    def run(self):
        #model
        #listener checks for socket descriptor readability and writability
        #readability - if listener socket, accept new connection, otherwise recv and launch message handler on thread pool
        #writability - message queue of NetMessages that the controller thread makes. send the message when the socket is writable and there is a message in the queue

        threadPool = QThreadPool.globalInstance()
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_socket.bind((socket.gethostbyname("0.0.0.0"), 49152))
        self.listener_socket.listen(5)

        while True:
            readable, writable, exceptional = select.select([self.listener_socket] + self.sockets, self.sockets, [])

            #if socket can be read, either a new connection or a new message from a client
            for s in readable:
                #if the socket is the server's socket, then accept a new connection
                if s is self.listener_socket:
                    #accept the connection, append it to the list of sockets, connect the client's signals to the controller, and launch a connection handler job
                    connection, client_address = s.accept()
                    self.sockets.append(connection)
                    # self.message_queues[connection] = queue.Queue()
                    clients[connection] = Client(connection, client_address)
                    self.connectSignals(connection) #connect signals from the client to the controller
                    logging.debug(f"{clients[connection].address} connected")
                    threadPool.start(ClientConnectionHandler(clients[connection], self.controller.sThreadPool_runningTaskCountChanged))

                #if the socket is a client socket, then read a new message
                else:
                    size, message = NetProtocol.unpackFromSocket(s)
                    # if unpackFromSocket returns -1, then the socket closed, and therefore the client disconnected
                    if size == -1:
                        #remove the socket from the list of sockets, close the socket, and emit a sConnection_end signal.
                        logging.debug(f"{clients[s].address} disconnected")
                        self.sockets.remove(s)
                        cl = clients.pop(s)
                        s.close()
                        cl.sConnection_end.emit()
                    #if unpackFromSocket succeeded, then launch a message handler job
                    elif size != 0:
                        threadPool.start(MessageHandler(clients[s], message, self.controller.sThreadPool_runningTaskCountChanged))

            # every cycle (0.01 seconds), check if there is a message in the message queue of each client
            # if there is a message in a client's message queue, send the message to the client
            for s in writable:
                if not s._closed and not clients[s]._message_queue.empty():
                    message = clients[s]._message_queue.get_nowait()
                    if(type(message) is bytes):
                        logging.debug(f"Sending message {message}")
                        s.send(message)
                    else:
                        logging.error(f"Received non-bytes message on message-queue of {clients[s].address}")
            #cycle delay
            sleep(0.01)

class MainWindowModel(QObject): #fix main window closing and not client inspection windows
    def __init__(self, controller):
        super().__init__()
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