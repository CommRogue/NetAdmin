import DUDialogController
from NetProtocol import *
import socket
import NetHelpers
import os
from PyQt5.QtCore import pyqtSignal

class DUDialogModel:
    def __init__(self, controller, client):
        self.controller = controller
        self.client = client

    def download_file(self, localdir, remotedir, download_progress_signal : pyqtSignal):
        socket = NetHelpers.open_connection(self.client)
        socket.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetRequest, NetTypes.NetDownloadFile, extra=remotedir)))
        response = NetProtocol.unpackFromSocket(socket)
        if response['type'] == NetTypes.NetDownloadFileDescriptor.value:
            file_size = response['data']['size']
            file_directory_offset = response['data']['directory']
            bytes_read = 0
            with open(os.path.join(localdir, file_directory_offset), 'wb+') as f:
                while True:
                    data = socket.recv(1024)
                    bytes_read += len(data)
                    if not data:
                        break
                    f.write(data)
                    download_progress_signal.emit(bytes_read)
        socket.close()