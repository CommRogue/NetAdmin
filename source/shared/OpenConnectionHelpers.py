import socket
import typing

import orjson

import MainWindowModel
from NetProtocol import *
import os
from PyQt5.QtCore import pyqtSignal
import threading

from NetProtocol import NetMessage, NetTypes, NetStatus, NetStatusTypes, NetProtocol


class SharedBoolean:
    def __init__(self, init_value):
        self._data = init_value
        self._lock = threading.Lock()

    def __bool__(self):
        with self._lock:
            return self._data

    def set(self, value):
        with self._lock:
            self._data = value

def verify_dir(dir):
    """
    Verify if a directory exists, if not, create it.
    Args:
        dir: the directory to verify.
    """
    if not os.path.exists(dir):
        os.makedirs(dir)
        return False
    return True


def sendfile(directory, socket):
    try:
        file = open(directory, 'rb')
    except:
        socket.send(NetProtocol.packNetMessage(
            NetMessage(type=NetTypes.NetStatus.value, data=NetStatus(NetStatusTypes.NetDirectoryAccessDenied.value), extra=directory)))
    else:
        # get file size
        size = os.path.getsize(directory)
        # get file name from directory
        name = os.path.basename(directory)
        # send file descriptor
        socket.send(NetProtocol.packNetMessage(
            NetMessage(type=NetTypes.NetDownloadFileDescriptor.value, data=NetDownloadFileDescriptor(directory, size))))

        # read file and send
        buffer = file.read(4096)
        while buffer:
            socket.send(buffer)
            buffer = file.read(4096)
        file.close()

def sendallfiles(socket, dir) -> None:
    if socket.fileno() == -1:
        raise ConnectionResetError("Socket is closed")
    if os.path.islink(dir):
        return
    if os.path.isfile(dir):
        sendfile(dir, socket)
    else:
        try:
            for item in os.scandir(dir):
                sendallfiles(socket, os.path.join(dir, item.name))
        except:
            socket.send(NetProtocol.packNetMessage(
                NetMessage(type=NetTypes.NetStatus.value, data=NetStatus(NetStatusTypes.NetDirectoryAccessDenied.value),
                           extra=dir)))

def receivefiles(socket, base_remote_dir, local_dir, status_queue, download_progress_signal=None) -> tuple[
    bool, int, list[str]]:
    """
    Receives files from the specified socket from a single remote directory or file while reporting progress to the download_progress_signal.
    It places the files in the specified base_dir, and combines the relative directory of each
    received file with the base directory, so that the original directory structure is preserved.
    Note: This function takes care of creating the necessary directories according to the downloaded remote directory.
    **Note: Use only after sending a NetDownloadRequest, and making sure that no more NetMessages are in the socket buffer.
    Args:
        socket: socket to receive from
        base_remote_dir: base directory that was requested to download.
        local_dir: local directory to place the files/directories in.
        status_queue: a queue that contains instructions for this function to do, for example, cancel receive operation.
        download_progress_signal (optional): signal to notify of download progress.

    Returns: amount of files that were excluded due to errors.

    """
    pathlist = []
    excludedCount = 0
    # receive response, and access index 1 to get data and not size
    size, message = NetProtocol.unpackFromSocket(socket)
    response = orjson.loads(message)  # convert the message to dictionary from json
    # while we are not getting a file download finished code, continue reading files
    while response['data'].get("statusCode") != NetStatusTypes.NetDownloadFinished.value and status_queue.empty():
        if response['type'] == NetTypes.NetStatus.value:
            if response['data'].get("statusCode") == NetStatusTypes.NetDirectoryAccessDenied.value:
                excludedCount += 1
        if response['type'] == NetTypes.NetDownloadFileDescriptor.value:
            # get size and name
            file_size = response['data']['size']
            file_directory = response['data']['directory']
            # get the relative path from the directory that the user chose to the directory that the file is in
            relative_path = os.path.relpath(file_directory, os.path.join(base_remote_dir, ".."))

            # combine the relative path with the local directory that the user chose
            path = os.path.join(local_dir, relative_path)
            # append the path to the list of paths downloaded to
            pathlist.append(path)
            # verify if the directory that the file exists in exists
            if not verify_dir(os.path.dirname(path)):
                logging.info(f"Directory {path} didn't exist. Created it.")

            bytes_received = 0
            # open file by combining the local download directory (+directory offset) and the file name
            with open(path, 'wb+') as f:
                # read file data in chunks of 1024 bytes
                while status_queue.empty() and bytes_received < file_size:
                    # receive data from client in 1024 bytes. if the remaining bytes in the buffer are less than 1024, read the remaining bytes
                    data = socket.recv(min(1024, file_size - bytes_received))
                    if not data:
                        # emit -1 signaling that the file has been fully downloaded
                        break
                    f.write(data)
                    bytes_received += len(data)

                    # report progress (1024 bytes read)
                    if download_progress_signal:
                        download_progress_signal.emit(len(data))

                    #if we received all the bytes, then finished file download
                    if bytes_received == file_size:
                        break
                if not status_queue.empty():
                    # if the status queue is not empty, then the user has requested to cancel the download
                    # close the partially downloaded file and delete it
                    f.close()
                    os.remove(path)
                    break

        # receive next message
        size, message = NetProtocol.unpackFromSocket(socket)
        response = orjson.loads(message)  # convert the message to dictionary from json

    # if loop exited due to status code cancel, then log
    if not status_queue.empty():
        status = status_queue.get_nowait()
        if status == "cancel":
            logging.info("Receive of 1 item cancelled.")
            return False, excludedCount, pathlist
    else:
        logging.info("Receive of 1 item succeeded.")
        return True, excludedCount, pathlist


def open_connection(client : typing.Union[MainWindowModel.Client, socket.socket]):
    """
    Opens a new socket to the client or socket passed in.
    Args:
        client: a MainWindowModel.Client or socket.socket object.

    Returns: socket of the new connection.
    """
    # if passed in MainWindowModel.Client
    if isinstance(client, MainWindowModel.Client):
        # send open connection request
        event = client.send_message(NetMessage(NetTypes.NetRequest.value, NetTypes.NetOpenConnection.value), track_event=True)
        # wait for response and get data from it
        event.wait()
        data = event.get_data()
        extra = event.get_extra()

        # if response is ok
        if type(data) is NetStatus:
            if data.statusCode == NetStatusTypes.NetOK.value:
                # connect to client using new socket
                ocSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ocSocket.connect((client.address[0], int(extra)))
                return ocSocket

    if isinstance(client, socket.socket):
        # send open connection request
        client.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetRequest.value, NetTypes.NetOpenConnection.value)))

        # wait for response and get data from it
        size, message = NetProtocol.unpackFromSocket(client)
        message = orjson.loads(message)
        data = message["data"]
        extra = message["extra"]

        # if response is ok
        if data == NetStatusTypes.NetOK.value:
            # connect to client using new socket
            ocSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ocSocket.connect((client.getpeername()[0], int(extra)))
            return ocSocket