import queue

from PyQt5.QtWidgets import QMessageBox

import DUDialogController
from NetProtocol import *
import socket
import NetHelpers
import os
from PyQt5.QtCore import pyqtSignal, QObject
import logging
from OpenConnectionHelpers import *
import queue

class DUDialogModel(QObject):
    def __init__(self, controller, client):
        super().__init__()
        self.controller = controller
        self.client = client
        self.status_queue = None

    def cancel_download(self):
        if self.status_queue is not None:
            self.status_queue.put("cancel")

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
        cancelled = False
        socket = NetHelpers.open_connection(self.client)
        excludedCount = 0
        for remotedir in remotedirs:
            # send request to client to download file
            socket.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetRequest, NetTypes.NetDownloadFile, extra=remotedir)))
            # wait for response
            self.status_queue = queue.Queue()
            received_all, excluded, pathlist = receivefiles(socket, remotedir, localdir, self.status_queue, download_progress_signal)
            # # delete all files from pathlist if download was cancelled
            excludedCount += excluded
            if not received_all:
                 cancelled = True
                 break

        # check how many files were excluded
        if excludedCount != 0:
            dialog = QMessageBox()
            dialog.setText(f"{excludedCount} directories were excluded due to permission errors.")
            dialog.setWindowTitle("Excluded files in download request")
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.exec_()
        socket.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetRequest, NetTypes.NetCloseConnection)))
        socket.close()