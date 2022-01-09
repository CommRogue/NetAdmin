from PyQt5.QtWidgets import QMessageBox

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

    def download_files(self, localdir, remotedirs, download_progress_signal : pyqtSignal):
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
        excludedCount = 0
        for remotedir in remotedirs:
            # send request to client to download file
            socket.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetRequest, NetTypes.NetDownloadFile, extra=remotedir)))
            # receive response, and access index 1 to get data and not size
            size, message = NetProtocol.unpackFromSocket(socket)
            response = orjson.loads(message)  # convert the message to dictionary from json
            # while we are not getting a file download finished code, continue reading files
            while response['data'].get("statusCode") != NetStatusTypes.NetDownloadFinished.value:
                if response['type'] == NetTypes.NetStatus.value:
                    if response['data'].get("statusCode") == NetStatusTypes.NetDirectoryAccessDenied.value:
                        excludedCount += 1
                if response['type'] == NetTypes.NetDownloadFileDescriptor.value:
                    # get size and name
                    file_size = response['data']['size']
                    file_directory = response['data']['directory']
                    # get the relative path from the directory that the user chose to the directory that the file is in
                    relative_path = os.path.relpath(file_directory, os.path.join(remotedir, ".."))

                    # combine the relative path with the local directory that the user chose
                    path = os.path.join(localdir, relative_path)
                    # verify if the directory that the file exists in exists
                    if not verify_dir(os.path.dirname(path)):
                        logging.info(f"Directory {path} didn't exist. Created it.")
                    bytes_received = 0
                    # open file by combining the local download directory (+directory offset) and the file name
                    with open(path, 'wb+') as f:
                        # read file data in chunks of 1024 bytes
                        while True and bytes_received < file_size:
                            # receive data from client in 1024 bytes. if the remaining bytes in the buffer are less than 1024, read the remaining bytes
                            data = socket.recv(min(1024, file_size - bytes_received))
                            if not data:
                                # emit -1 signaling that the file has been fully downloaded
                                break
                            f.write(data)
                            bytes_received += len(data)
                            # report progress (1024 bytes read)
                            download_progress_signal.emit(len(data))
                            if bytes_received == file_size:
                                break

                # receive next message
                size, message = NetProtocol.unpackFromSocket(socket)
                response = orjson.loads(message)  # convert the message to dictionary from json
        if excludedCount != 0:
            dialog = QMessageBox()
            dialog.setText(f"{excludedCount} directories were excluded due to permission errors.")
            dialog.setWindowTitle("Excluded files in download request")
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.exec_()
        download_progress_signal.emit(-1)
        socket.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetRequest, NetTypes.NetCloseConnection)))
        socket.close()