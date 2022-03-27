import socket
import os, sys
import SmartSocket
sys.path.insert(1, os.path.join(sys.path[0], '../server'))
import MWindowModel
from NetProtocol import *
import os
import threading
import upnpclient
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

def verify_upnp(port=49152):
    '''
    Uses the forward_upnp function to forward the specified port, while handling exceptions and returning the result and an optional error message that the caller can display to the user if needed.
    Args:
        port: the port to forward.

    Returns:
        True if the port was forwarded on at least one UPnP device, False otherwise.
    '''
    res = False
    err_msg = None
    try:
        res = forward_upnp(port)
    except Exception as e:
        err_msg = "NetAdmin encountered the following error while trying to forward port 49152 via UPnP: \n"+str(e)
    else:
        if not res:
            err_msg = "NetAdmin could not find any compatible UPnP devices to port-forward your connection. If you would like computers outside of your network to connect to this application, either enable UPnP on your router, or manually set up port-forwarding on port 49152 on your router."
    return res, err_msg

def forward_upnp(port=49152):
    """
    Forwards the specified port to all available UPnP devices that support the AddPortMapping action in the WANIPConn1 service.
    Args:
        port: the port to forward.
    Returns:
        True if the port was forwarded on at least one UPnP device, False otherwise.
    """
    forwarded = False
    devices = upnpclient.discover()
    # iterate the devices that we discovered that support UPnP
    for device in devices:
        # if UPnP device has the WANIPConn1 service
        if hasattr(device, 'WANIPConn1'):
            device.WANIPConn1.AddPortMapping(
                NewRemoteHost="0.0.0.0",
                NewExternalPort=port,
                NewProtocol="TCP",
                NewInternalPort=port,
                NewInternalClient="192.168.1.205",
                NewEnabled='1',
                NewPortMappingDescription="NetAdmin Server Port Forward",
                NewLeaseDuration=100000
            )
            forwarded = True
    return forwarded

def sendfile(directory, socket : SmartSocket.SmartSocket):
    try:
        file = open(directory, 'rb')
    except:
        socket.send_message(
            NetMessage(type=NetTypes.NetStatus.value, data=NetStatus(NetStatusTypes.NetDirectoryAccessDenied.value), extra=directory))
    else:
        # get file size
        size = os.path.getsize(directory)
        # get file name from directory
        name = os.path.basename(directory)
        # send file descriptor
        socket.send_message(
            NetMessage(type=NetTypes.NetDownloadFileDescriptor.value, data=NetDownloadFileDescriptor(directory, size)))

        # read file and send exactly maximum of 16KB at a time.
        # the receiver receives exactly 16KB, or the remainder of the file (which it can calculate using the file size and amount of bytes received)
        # then the receiver decrypts exactly that amount of data
        buffer = file.read(16384)
        while buffer:
            if socket.Fkey:
                print("Encrypted 16KB chunk or file remainder of data on NetTransferProtocol")
            socket.send_appended_stream(buffer)
            buffer = file.read(16384)
        file.close()

def sendallfiles(socket, dir) -> None:
    try:
        if socket.fileno() == -1:
            raise ConnectionResetError("Socket is closed")
        if os.path.islink(dir):
            return
        if os.path.isfile(dir):
            sendfile(dir, socket)
        else:
            try:
                scan = os.scandir(dir)
                # check if there are any items in the iterator
                if any(True for _ in scan):
                    for item in os.scandir(dir):
                        sendallfiles(socket, os.path.join(dir, item.name))
                else:
                    socket.send_message(
                        NetMessage(type=NetTypes.NetDownloadDirectoryDescriptor.value,
                                   data=NetDownloadDirectoryDescriptor(dir)))
            except PermissionError:
                socket.send_message(
                    NetMessage(type=NetTypes.NetStatus.value, data=NetStatus(NetStatusTypes.NetDirectoryAccessDenied.value),
                               extra=dir))
    except ConnectionResetError:
        print("Connection reset")

def resolveRemoteDirectoryToLocal(base_remote_directory, actual_remote_directory, local_directory) -> str:
    # get the relative path from the directory that the user chose to the directory that the file is in
    relative_path = os.path.relpath(actual_remote_directory, os.path.join(base_remote_directory, ".."))

    # combine the relative path with the local directory that the user chose
    return  os.path.join(local_directory, relative_path)

def receivefiles(socket : SmartSocket.SmartSocket, base_remote_dir, local_dir, status_queue, download_progress_signal=None, overall_size=None) -> tuple[
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
    size, response, _ = socket.receive_message()

    # while we are not getting a file download finished code, continue reading files
    bytes_to_signal = overall_size / 100
    tbs = bytes_to_signal
    while response['data'].get("statusCode") != NetStatusTypes.NetDownloadFinished.value and status_queue.empty():
        if response['type'] == NetTypes.NetStatus.value:
            if response['data'].get("statusCode") == NetStatusTypes.NetDirectoryAccessDenied.value:
                excludedCount += 1
        elif response['type'] == NetTypes.NetDownloadFileDescriptor.value:
            # get size and name
            file_size = response['data']['size']
            file_directory = response['data']['directory']

            # resolve to local directory
            path = resolveRemoteDirectoryToLocal(base_remote_dir, file_directory, local_dir)

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
                    # receive data from client (size appeneded to 16KB chunks of data because of AES enlargement of bytes.). if the remaining bytes in the buffer are less than 1024, read the remaining bytes
                    # data = socket.recv_exact(min(16384, file_size - bytes_received), decrypt_if_available=True)
                    size, data, isEncrypted = socket.recv_appended_stream()
                    print(f"NetFileTransfer:RECEIVEFILES received an encrypted file chunk: {len(data)} bytes")
                    if not data:
                        # emit -1 signaling that the file has been fully downloaded
                        break
                    f.write(data)
                    bytes_received += len(data)
                    tbs -= len(data)
                    # report progress
                    if download_progress_signal and tbs < 0:
                        # calculate the difference between the temporary bytes read and the bytes to signal
                        t = bytes_to_signal-tbs
                        download_progress_signal.emit(t)
                        # remove the rmainder of temporary bytes read from the bytes to signal
                        tbs = bytes_to_signal

                    #if we received all the bytes, then finished file download
                    if bytes_received == file_size:
                        logging.info("Finished downloading file.")
                        # download_progress_signal.emit(bytes_to_signal-tbs)
                        break
                if not status_queue.empty():
                    # if the status queue is not empty, then the user has requested to cancel the download
                    # close the partially downloaded file and delete it
                    f.close()
                    os.remove(path)
                    break
        elif response['type'] == NetTypes.NetDownloadDirectoryDescriptor.value:
            file_directory = response['data']['directory']
            path = resolveRemoteDirectoryToLocal(base_remote_dir, file_directory, local_dir)
            verify_dir(path)
        # receive next message
        size, response, _ = socket.receive_message()

    # if loop exited due to status code cancel, then log
    if not status_queue.empty():
        status = status_queue.get_nowait()
        if status == "cancel":
            logging.info("Receive of 1 item cancelled.")
            return False, excludedCount, pathlist
    else:
        logging.info("Receive of 1 item succeeded/excluded.")
        return True, excludedCount, pathlist

def _copy_socket(originalSocket : SmartSocket.SmartSocket):
    """
    Copies the socket with the encryption key of the original socket and returns the new socket.
    Args:
        originalSocket: the original socket to copy.

    Returns: the new socket with the encryption key of the original socket.

    """
    key = None
    if originalSocket.fernetInstance != None:
        key = originalSocket.Fkey
    return SmartSocket.SmartSocket(key, socket.AF_INET, socket.SOCK_STREAM)

def open_connection(client : typing.Union[MWindowModel.Client, SmartSocket.SmartSocket]):
    """
    Opens a new socket to the client or socket passed in.
    Args:
        client: a MainWindowModel.Client or socket.socket object.

    Returns: socket of the new connection.
    """
    # if passed in MainWindowModel.Client
    if isinstance(client, MWindowModel.Client):
        # send open connection request
        event = client.send_message(NetMessage(NetTypes.NetRequest.value, NetTypes.NetOpenConnection.value), track_event=True)
        # wait for response and get data from it
        event.wait()
        data = event.get_data()
        extra = event.get_extra()

        # if response is ok
        if type(data) is NetStatus:
            if data.statusCode == NetStatusTypes.NetOK.value:
                client.dataLock.acquire_read()
                Fkey = client._socket.Fkey
                client.dataLock.release_read()
                # connect to client using new socket
                ocSocket = SmartSocket.SmartSocket(Fkey, socket.AF_INET, socket.SOCK_STREAM)
                ocSocket.connect((client.address[0], int(extra)))
                return ocSocket

    if isinstance(client, SmartSocket.SmartSocket):
        # send open connection request
        client.send_message((NetMessage(NetTypes.NetRequest.value, NetTypes.NetOpenConnection.value)))

        # wait for response and get data from it
        size, message, isEncrypted = client.receive_message()
        data = message["data"]
        extra = message["extra"]

        # if response is ok
        if data == NetStatusTypes.NetOK.value:
            # connect to client using new socket
            ocSocket = SmartSocket.SmartSocket(client.Fkey, socket.AF_INET, socket.SOCK_STREAM)
            ocSocket.connect((client.getpeername()[0], int(extra)))
            return ocSocket