import threading
import socket
import select
import uuid
import queue
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, QThreadPool
from NetProtocol import *
import functools
import orjson
from time import sleep

clients = {}

class ClientData:
    pass

class Client(QObject):
    data_update = pyqtSignal()
    connection_start = pyqtSignal()
    connection_end = pyqtSignal()
    client_id : str
    global clients
    def __init__(self, socket, address, client_id):
        super().__init__()
        self.client_id = client_id
        self.socket = socket
        self.address = address
        self.data = ClientData()
        self.socket_lock = threading.Lock()

    def close(self):
        self.connection_end.emit()
        self.socket.close() #check for problems

    def persist_connection(func):
        def wrapper(self, *args, **kwargs):
            try:
                self.client.socket_lock.acquire()
                return func(self, *args, **kwargs)
            except socket.error:
                if self.client.socket in clients:
                    c = clients.pop(self.socket)
                    c.close()
            finally:
                self.client.socket_lock.release()
        return wrapper

    def read_message(self):
        print("reading")
        return self.socket.recv(1024).decode()

    def send_message(self, data : NetMessage):
        print(f"sending {data}")
        data = orjson.dumps(data)
        self.socket.send(data.encode())

class GetSystemInfo(QRunnable):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    @Client.persist_connection 
    def run(self) -> None:
        # self.client.send_data(NetProtocol.heartbeat())
        self.client.send_text("info")
        response = self.client.read_text()
        if response == "heartbeat":
            print("heartbeat from ", self.client.address)

class Heartbeat(QRunnable):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    @Client.persist_connection
    def run(self) -> None:
        # self.client.send_data(NetProtocol.heartbeat())
        self.client.send_text("heartbeat")
        response = self.client.read_text()
        if response == "heartbeat":
            print("heartbeat from ", self.client.address)

class ListenerWorker(QObject):
    global clients
    sockets = []
    # message_queues = {}

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def heartbeat_loop(self):
        while True:
            for client in clients.values():
                threadCount = QThreadPool.globalInstance()
                threadCount.start(Heartbeat(client))
            sleep(5)

    def run(self):
        #model
        #listener checks for socket descriptor readability and writability
        #readability - if listener socket, accept new connection, otherwise recv and launch message handler on thread pool
        #writability - message queue of NetMessages that the controller thread makes. send the message when the socket is writable and there is a message in the queue

        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_socket.bind(('0.0.0.0', 4959))
        self.listener_socket.listen(5)
        thread = threading.Thread(target=self.heartbeat_loop)
        thread.start()
        # while True:
        #     connection, client_address = self.listener_socket.accept()
        #     # self.message_queues[connection] = queue.Queue()
        #

        while True:
            readable, writable, exceptional = select.select([self.listener_socket] + self.sockets, [], [])
            for s in readable:
                if s is self.listener_socket:
                    connection, client_address = s.accept()
                    self.sockets.append(connection)
                    # self.message_queues[connection] = queue.Queue()
                    clients[connection] = Client(connection, client_address, uuid.uuid4())
                    clients[connection].data_update.connect(functools.partial(self.controller.on_data_update, clients[connection]))
                    clients[connection].connection_start.connect(functools.partial(self.controller.on_connection_start, clients[connection]))
                    clients[connection].connection_end.connect(functools.partial(self.controller.on_connection_end, clients[connection]))
                    print(threading.currentThread())
                    clients[connection].connection_start.emit()
                else:
                    self.clients[s].read_data()

            for s in writable:
                if self.message_queues[s].get_nowait():
                    self.clients[s].send_data()

class MainWindowModel:
    def __init__(self, controller):
        #open communicator thread and listen
        self.communicator = QThread()
        print(threading.currentThread())
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