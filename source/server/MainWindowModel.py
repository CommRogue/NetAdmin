import os
import sys
import typing
import re
import json
from urllib.request import urlopen
sys.path.insert(1, os.path.join(sys.path[0], '../shared'))
from NetProtocol import *
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


clients = {}

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# logger.setFormatter(logging.Formatter(bcolors.WARNING + '%[(asctime)s] - [%(threadName)s] - [%(levelname)s]:' + bcolors.OKGREEN + '    %(message)s'))
logging.basicConfig(format=bcolors.WARNING + '%(asctime)s - %(threadName)s - %(levelname)s:' + bcolors.OKGREEN + '    %(message)s' + bcolors.END, level=logging.DEBUG)


class Client(QObject):
    #synchronization objects
    uuid = None
    identificationNotification = threading.Condition()
    dataLock = SocketLock.SocketLock()
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
    #client_id : str

    def __str__(self):
        return f"{self.address}"

    def __init__(self, socket, address):
        super().__init__()
        #self.client_id = client_id
        self._socket = socket
        self.address = address
        self._socket_lock = threading.Lock()

    def close(self):
        self.connection_end.emit()
        self.socket.close() #check for problems

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

    def send_message(self, data : NetMessage):
        logging.debug(f"Sending message {data}")
        self._message_queue.put(NetProtocol.packNetMessage(data))

# class GetSystemInfo(QRunnable):
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

class MessageHandler(QRunnable):
    def __init__(self, client: Client, message: bytes):
        super().__init__()
        self.client = client
        self._message_bytes = message
        self.message = None

    def run(self) -> None:
        self.message = orjson.loads(self._message_bytes)
        logging.debug(f"MessageHandler running with message {self.message} from client {self.client.address}")
        if self.message["type"] == NetTypes.NetRequest:
            pass
        elif self.message["type"] == NetTypes.NetIdentification.value: #check if client sent ID or else send ID
            if self.message['data']["id"] != "": #also check if id in database
                self.client.uuid = self.message['data']["id"]
                logging.debug(f"Client {self.client.address} identified as {self.client.uuid}")
                self.client.identificationNotification.acquire()
                self.client.identificationNotification.notify_all()
                self.client.identificationNotification.release()
            else: #if no id sent
                cid = str(uuid.uuid4())
                logging.info(f"Client {self.client.address} sent identification request. Generating new ID {cid} and sending...")
                self.client.send_message(NetMessage(NetTypes.NetIdentification, NetIdentification(cid))) #send a client id
                self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetIdentification)) #request to identify again
        elif self.message["type"] == NetTypes.NetSystemInformation.value: #if a message is
            data = self.message["data"]
            dataStructure = NetSystemInformation(**data)

            self.client.dataLock.acquire_write()
            self.client.systemInformation = dataStructure
            self.client.dataLock.release_write()

            self.client.sSystemInformation_update.emit()
        elif self.message["type"] == NetTypes.NetSystemMetrics.value: #if a message is
            data = self.message["data"]
            dataStructure = NetSystemMetrics(**data)
            self.client.dataLock.acquire_write()
            self.client.systemMetrics = dataStructure
            self.client.dataLock.release_write()
            self.client.sSystemMetrics_update.emit()

class ClientConnectionHandler(QRunnable):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    def run(self) -> None:
        logging.debug(f"ClientConnectionHandler running with client {self.client.address}")
        self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetIdentification))
        self.client.identificationNotification.acquire()
        result = self.client.identificationNotification.wait(10)
        if result:
            self.client.identificationNotification.release()
        else:
            raise Exception("Client identification timed out")


        #add client to database
        con = QSqlDatabase.addDatabase("QSQLITE")
        con.setDatabaseName(os.getenv("LOCALAPPDATA")+"\\NetAdmin\\clients.db")
        if not con.open():
            print("Failed to open database")
            sys.exit(1)
        findClients = QSqlQuery()
        findClients.exec_("SELECT uuid, address FROM clients WHERE uuid = '" + self.client.uuid + "'")
        if findClients.next():
            logging.debug(f"Client {self.client.uuid} already in database")
        else:
            logging.debug(f"Client {self.client.uuid} not in database. Adding to database....")
            addClient = QSqlQuery()
            addClient.prepare(f"INSERT INTO clients (uuid, address) VALUES (?, ?)")
            addClient.addBindValue(str(self.client.uuid))
            addClient.addBindValue(str(self.client.address[0]))
            addClient.exec_()
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