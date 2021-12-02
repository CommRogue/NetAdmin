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
from NetData import *
import logging

clients = {}

class Client(QObject):
    _message_queue = queue.Queue()
    # Data segements
    # ---------------
    connectionData = None
    systemInformation = None
    systemMetrics = None

    # Signals
    # ---------------
    data_update = pyqtSignal()
    connection_start = pyqtSignal()
    connection_end = pyqtSignal()
    #client_id : str

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
        print(f"sending {data}")
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
        self.message = orjson.loads(message)
        print("messagehandler init", threading.current_thread())

    def run(self) -> None:
        pass


class ListenerWorker(QObject):
    clients_lock = threading.Lock()
    global clients
    sockets = []
    # message_queues = {}

    def __init__(self, controller):
        super().__init__()
        self.controller = controller


    def echo(self):
        while True:
            inp = input("")
            for client in clients.values():
                client.send_message(NetMessage("request", inp))

    def run(self):
        #model
        #listener checks for socket descriptor readability and writability
        #readability - if listener socket, accept new connection, otherwise recv and launch message handler on thread pool
        #writability - message queue of NetMessages that the controller thread makes. send the message when the socket is writable and there is a message in the queue

        threadPool = QThreadPool.globalInstance()
        self.listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener_socket.bind(('0.0.0.0', 4959))
        self.listener_socket.listen(5)
        thread = threading.Thread(target=self.echo)
        thread.start()

        while True:
            readable, writable, exceptional = select.select([self.listener_socket] + self.sockets, self.sockets, [])
            for s in readable:
                if s is self.listener_socket:
                    connection, client_address = s.accept()
                    logging.info(f"Socket connected")
                    self.sockets.append(connection)
                    # self.message_queues[connection] = queue.Queue()
                    clients[connection] = Client(connection, client_address)
                    clients[connection].data_update.connect(functools.partial(self.controller.on_data_update, clients[connection]))
                    clients[connection].connection_start.connect(functools.partial(self.controller.on_connection_start, clients[connection]))
                    clients[connection].connection_end.connect(functools.partial(self.controller.on_connection_end, clients[connection]))
                    clients[connection].connection_start.emit()
                else:
                    size, message = NetProtocol.unpackFromSocket(s)
                    if size == -1:
                        logging.info(f"Socket disconnected")
                        clients[s].connection_end.emit()
                        self.sockets.remove(s)
                        clients.pop(s)
                        s.close()
                    elif size != 0:
                        threadPool.start(MessageHandler(self.clients[s], message))

            for s in writable:
                if not s._closed and not clients[s]._message_queue.empty():
                    message = clients[s]._message_queue.get_nowait()
                    if(type(message) is bytes):
                        s.send(message)
                        print(f"confirmed sent {message}")
                    else:
                        logging.error(f"Received non-bytes message on message-queue of {s.address}")


class MainWindowModel:
    def __init__(self, controller):
        #open communicator thread and listen
        self.communicator = QThread()
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