import threading
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRunnable, QThreadPool, pyqtSlot
from MainWindowModel import Client


class MainWindowController(QObject):
    def __init__(self, view):
        super().__init__()
        self.view = view
        # self.model = model

    def on_data_update(self, client, data):
        print(f"Data update from {client.socket}: {data}")

    def on_connection_start(self, client):
        print(f"Connection {client.socket} started")

    def on_connection_end(self, client):
        print(f"Connection {client.socket} ended")