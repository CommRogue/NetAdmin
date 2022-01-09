import DUDialogController
from NetProtocol import *
import socket
import NetHelpers
import os
from PyQt5.QtCore import pyqtSignal, QObject
import logging


def verify_dir(dir):
    """
    Verify if a directory exists, if not, create it
    Args:
        dir: the directory to verify.
    """
    if not os.path.exists(dir):
        os.makedirs(dir)
        return False
    return True

class DUDialogModel(QObject):
    def __init__(self, controller, client):
        super().__init__()
        self.controller = controller
        self.client = client

    def download_file(self, localdir, remotedirs, download_progress_signal : pyqtSignal):
        """
        Download a file from the client to an existing local directory.
        Implementation summary:
        Opens an open socket connection to the client and sends it a request to download the file.
        Waits for a response in the form of a NetProtocol.FileDownloadDescriptor.
        Get the file size and name from the descriptor and create a file with the same name in the local directory.
        Note that the local directory must exist.
        Then, read the remaining bytes off the socket buffer and write them to the file, each time notifying the progress signal.
        Then, close the socket.
        Args:
            localdir:
            remotedir:
            download_progress_signal:
        """
        # request a new socket from client
        socket = NetHelpers.open_connection(self.client)
        for remotedir, relativepath in remotedirs:
            # send request to client to download file
            socket.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetRequest, NetTypes.NetDownloadFile, extra=remotedir)))
            # receive response, and access index 1 to get data and not size
            size, message = NetProtocol.unpackFromSocket(socket)
            response = orjson.loads(message)  # convert the message to dictionary from json

            if response['type'] == NetTypes.NetDownloadFileDescriptor.value:
                # get size and name
                file_size = response['data']['size']
                file_directory_offset = response['data']['name']
                # combine the base directory that the user chose with the relative path from it to the file
                path = os.path.join(localdir, relativepath)
                # verify if the directory that the file exists in exists
                if not verify_dir(os.path.dirname(path)):
                    logging.info(f"Directory {path} didn't exist. Created it.")
                bytes_received = 0
                # open file by combining the local download directory (+directory offset) and the file name
                with open(path, 'wb+') as f:
                    # read file data in chunks of 1024 bytes
                    while True and bytes_received < file_size:
                        # receive data from client in 1024 bytes
                        data = socket.recv(1024)
                        if not data:
                            # emit -1 signaling that the file has been fully downloaded
                            break
                        f.write(data)
                        bytes_received += len(data)
                        # report progress (1024 bytes read)
                        download_progress_signal.emit(len(data))
                    if bytes_received == file_size:
                        download_progress_signal.emit(-1)
        socket.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetRequest, NetTypes.NetCloseConnection)))
        socket.close()