import OpenConnectionHelpers
from PyQt5.QtCore import pyqtSignal, QObject
from OpenConnectionHelpers import *
import queue

class DUDialogModel(QObject):
    def __init__(self, controller, client):
        super().__init__()
        self.controller = controller
        self.client = client
        self.status_queue = None

    def cancel_download(self):
        """
        Puts a cancel message in the status queue to cancel the download in the download_files function.
        """
        if self.status_queue is not None:
            self.status_queue.put("cancel")

    def download_files(self, localdir, remotedirs, download_progress_signal : pyqtSignal, infobox_signal : pyqtSignal, totalSize):
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
            localdir: the local directory to download the files to.
            remotedir: the remote directory to download the files from.
            download_progress_signal: a signal to notify the progress of the download.
        Returns: the number of files excluded due from the download due to errors.
        """
        # request a new socket from client
        print(f"Thread of download_files name: {threading.current_thread().name}")
        cancelled = False
        socket = OpenConnectionHelpers.open_connection(self.client)
        excludedCount = 0
        pathlist = []
        for remotedir in remotedirs:
            # send request to client to download file
            socket.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetDownloadFile, extra=remotedir))
            # wait for response
            self.status_queue = queue.Queue()
            # receive files
            received_all, excluded, pathlist = receivefiles(socket, remotedir, localdir, self.status_queue, download_progress_signal, overall_size=totalSize)
            # delete all files from pathlist if download was cancelled
            excludedCount += excluded
            if not received_all:
                 cancelled = True
                 break
        # if download was cancelled, report to user
        if cancelled:
            download_progress_signal.emit(-2)

        # if all items were received fully, then report to user. also check that we received any files and not only excluded
        elif len(pathlist) != 0:
            download_progress_signal.emit(-1)

        # open infobox notifying of files excluded due to errors
        if excludedCount != 0:
            infobox_signal.emit("Excluded files in download request", f"{excludedCount} directories were excluded due to permission errors.")

        # close socket
        socket.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetRequest, NetTypes.NetCloseConnection)))
        socket.close()
        # return number of files excluded
        return excludedCount