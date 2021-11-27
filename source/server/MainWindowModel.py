import threading
import socket
import select
import queue
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, QThreadPool
from NetProtocol import NetProtocol
import functools
from time import sleep

class ClientData:
    pass

class Client(QObject):
    data_update = pyqtSignal()
    connection_start = pyqtSignal()
    connection_end = pyqtSignal()
    def __init__(self, socket, address):
        super().__init__()
        self.socket = socket
        self.address = address
        self.data = ClientData()
        self.socket_lock = threading.Lock()

    def __del__(self):
        self.connection_end.emit()
        self.socket.close() #check for problems

    def read_text(self):
        return self.socket.recv(1024).decode()

    def send_text(self, data):
        self.socket.send(data.encode())

class Heartbeat(QRunnable):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    def run(self) -> None:
        # self.client.send_data(NetProtocol.heartbeat())
        self.client.send_text("heartbeat")
        response = self.client.read_text()
        if response == "heartbeat":
            print("heartbeat from ", self.client.address)

class ListenerWorker(QObject):
    sockets = []
    clients = {}
    # message_queues = {}

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def heartbeat_loop(self):
        while True:
            for client in self.clients.values():
                threadCount = QThreadPool.globalInstance()
                threadCount.start(Heartbeat(client))
            sleep(5)

    def run(self):
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_socket.bind(('0.0.0.0', 4959))
        self.listener_socket.listen(5)
        thread = threading.Thread(target=self.heartbeat_loop)
        thread.start()
        while True:
            connection, client_address = self.listener_socket.accept()
            # self.message_queues[connection] = queue.Queue()
            self.clients[connection] = Client(connection, client_address)
            self.clients[connection].data_update.connect(functools.partial(self.controller.on_data_update, self.clients[connection]))
            self.clients[connection].connection_start.connect(functools.partial(self.controller.on_connection_start, self.clients[connection]))
            self.clients[connection].connection_end.connect(functools.partial(self.controller.on_connection_end, self.clients[connection]))
            self.clients[connection].connection_start.emit()
        # while True:
        #     readable, writable, exceptional = select.select([self.listener_socket] + self.sockets, [], [])
        #     for s in readable:
        #         if s is self.listener_socket:
        #             connection, client_address = s.accept()
        #             self.sockets.append(connection)
        #             # self.message_queues[connection] = queue.Queue()
        #             self.clients[connection] = Client(connection, client_address)
        #             self.clients[connection].data_update.connect(functools.partial(MainWindowController.on_data_update, self.clients[connection]))
        #             self.clients[connection].data_update.emit()
                # else:
                #     self.clients[s].read_data()

            # for s in writable:
            #     if self.message_queues[s].get_nowait():
            #         self.clients[s].send_data()

class MainWindowModel:
    def __init__(self, controller):
        #open communicator thread and listen
        self.communicator = QThread()
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
