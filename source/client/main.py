import threading
import socket
import os
import orjson
import sys
import platform
import win32com.client as com
import wmi
sys.path.insert(1, os.path.join(sys.path[0], '../shared'))
from NetProtocol import *
import psutil
import GPUtil
import winreg
import win32api
from os import listdir
from os.path import isfile, join
from OpenConnectionHelpers import *

def set_id(id):
    """
    Creates or modifies an existing registry key specifying the UUID of the client.
    Args:
        id: the uuid to be set or modified to.
    """
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\NetAdmin\\Configuration")
    winreg.SetValue(key, 'UUID', winreg.REG_SZ, id)

def get_id():
    """
    Gets the UUID of the client. Raises an exception if the key does not exist.

    Returns: the uuid found in the registry or None if not found.

    """
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\NetAdmin\\Configuration")
    return winreg.QueryValue(key, 'UUID')

def createServer(port=0):
    """
    Creates a server socket and binds it to the specified port. If no port is specified, the socket will be bound to an available port.

    Args:
        port: the port to bind the server to.

    Returns: the server socket.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    return server

def receive(sock, proc):
    while True:
        data = sock.recv(1024)
        print(f"Got data: {data.decode()}")
        proc.stdin.write(data)
        proc.stdin.flush()
        proc.stdin.write("\n".encode())
        proc.stdin.flush()

def handleOpenConnection(server):
    try:
        client, address = server.accept()
        print("OpenConnection from: " + str(address))

        # listener loop
        while True:
            # read message
            size, message = NetProtocol.unpackFromSocket(client)
            if size == -1:
                # if server disconnected, close local open connection server
                server.shutdown(socket.SHUT_RDWR)
                break
            message = orjson.loads(message)  # convert the message to dictionary from json

            id = message['id'] # get the echo id of the message, to echo back to the server when sending response

            # if message is a request
            if message['type'] == NetTypes.NetRequest.value:
                # if the request is to close the connection
                if message['data'] == NetTypes.NetCloseConnection.value:
                    print(f"Closing unmanaged connection {address}")
                    server.close()
                    break

                # if the request is to open a shell connection
                elif message['data'] == NetTypes.NetOpenShell.value:
                    # open shell process
                    import subprocess
                    p = subprocess.Popen("cmd.exe", stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, shell=True)
                    thread = threading.Thread(target=receive, args=(client, p,))
                    thread.start()
                    client.send(NetProtocol.packNetMessage(NetMessage(type=NetTypes.NetStatus, data=NetStatus(NetStatusTypes.NetOK.value), id=id)))
                    while p.poll() is None:
                        n = p.stdout.readline()
                        client.send(n)

                # if the request is to download file
                elif message['data'] == NetTypes.NetDownloadFile.value:
                    # get the file directory
                    directory = message['extra']

                    # send all files
                    sendallfiles(client, directory)

                    # send file download end status
                    client.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetStatus.value, NetStatus(NetStatusTypes.NetDownloadFinished.value))))
    except ConnectionResetError:
        print("Connection disconnected by server without message")


def main():
    # create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 49152))

    computer = wmi.WMI()

    # main loop
    # receives and unpacks messages from the server, and checks the type of message
    while True:
        size, message = NetProtocol.unpackFromSocket(s)
        message = orjson.loads(message) # convert the message to dictionary from json

        id = message['id'] # get the echo id of the message, to echo back to the server when sending response

        #if message is an error
        if message['type'] == NetTypes.NetStatus.value:

            # identification error
            if message['data'] == NetStatusTypes.NetInvalidIdentification.value:
                print("Invalid indentification sent. Resetting...")
                #reset the id
                set_id("")
                #send a request to identify again
                s.send(NetProtocol.packNetMessage(NetMessage(type=NetTypes.NetIdentification, data=NetIdentification(get_id()), id=id)))

        # if message is a request
        if message['type'] == NetTypes.NetRequest.value:
            # if the request is to delete a file
            if message['data'] == NetTypes.NetDeleteFile.value:
                path = message['extra']

                # try to delete the path
                try:
                    if os.path.isfile(path): # if the path is a file
                        os.remove(path)
                    else: # if the path is a directory
                        os.rmdir(path)

                # file or directory doesn't exist
                except FileNotFoundError:
                    print("File not found: " + path)
                    s.send(NetProtocol.packNetMessage(NetMessage(type=NetTypes.NetStatus, data=NetStatus(NetStatusTypes.NetFileNotFound.value), id=id)))

                # no access to directory error
                except WindowsError:
                    print("Error deleting file: " + path)
                    s.send(NetProtocol.packNetMessage(NetMessage(type=NetTypes.NetStatus, data=NetStatus(NetStatusTypes.NetDirectoryAccessDenied.value), id=id)))

                 # success
                else:
                    s.send(NetProtocol.packNetMessage(NetMessage(type=NetTypes.NetStatus, data=NetStatus(NetStatusTypes.NetOK.value), id=id)))

            if message['data'] == NetTypes.NetIdentification.value: #if request to identify
                try:
                    uid = get_id()
                except: # will raise an exception if the key does not exist
                    sMessage = NetIdentification("") #if there is no id, then send a blank id to tell the server that this is a new client
                else:
                    sMessage = NetIdentification(uid) #if there is an id, then send the id to the server
                s.send(NetProtocol.packNetMessage(NetMessage(type=NetTypes.NetIdentification, data=sMessage, id=id)))

            # if request system information
            elif message['data'] == NetTypes.NetSystemInformation.value:
                sMessage = NetSystemInformation(
                    platform.node(),
                    platform.system(),
                    platform.processor(),
                    platform.machine(),
                    computer.Win32_VideoController()[0].Name
                )
                s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetSystemInformation, sMessage, id=id)))

            # if request system metrics
            elif message['data'] == NetTypes.NetSystemMetrics.value:
                try:
                    GPU_LOAD = GPUtil.getGPUs()[0].load
                except:
                    GPU_LOAD = 0
                sMessage = NetSystemMetrics(
                    psutil.cpu_percent(),
                    RAM_LOAD=psutil.virtual_memory().percent,
                    GPU_LOAD=GPU_LOAD,
                    DISK_LOAD=psutil.disk_usage('/')[3]
                )
                s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetSystemMetrics, sMessage, id=id)))

            # if request to open a new connection
            elif message['data'] == NetTypes.NetOpenConnection.value:
                # create a server with the port specified in extra, and pass it to handleOpenConnection
                server = createServer()
                thread = threading.Thread(target=handleOpenConnection, args=(server,))
                thread.start()
                s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetStatus, NetStatus(NetStatusTypes.NetOK.value), extra=server.getsockname()[1], id=id)))

            # if request a directory listing
            elif message['data'] == NetTypes.NetDirectoryListing.value:
                # directory string is stored in the extra field of the message
                directory = message['extra']

                # if requesting root directory
                if(directory == ""):
                    drives = win32api.GetLogicalDriveStrings()
                    drives = drives.split('\000')[:-1]
                    sMessage = NetDirectoryListing("", [])
                    for drive in drives:
                        sMessage.items.append(NetDirectoryItem(drive[:2], drive, NetTypes.NetDirectoryFolderCollapsable.value, None, None, None))
                    s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetDirectoryListing, sMessage, id=id)))

                # if requesting normal directory
                else:
                    # check if there is access to the directory
                    try:
                        files = [f for f in listdir(directory) if isfile(join(directory, f))]
                        folders = [f for f in listdir(directory) if not isfile(join(directory, f))]

                    # if there is no access, then there is a PermissionError
                    except PermissionError as e:
                        print("Permission is denied for directory", directory)
                        #send a NetDirectoryAccessDenied error to the server
                        s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetStatus, NetStatus(NetStatusTypes.NetDirectoryAccessDenied.value), id=id)))

                    # if got directory listing (we have permission)
                    else:
                        sMessage = NetDirectoryListing(directory, [])

                        # append NetDirectoryItems for each file/folder
                        for folder in folders:
                            try:
                                winfolderPath = directory+folder+"\\"
                                winfso = com.Dispatch("Scripting.FileSystemObject")
                                winfolder = winfso.GetFolder(winfolderPath)
                                size = winfolder.Size
                            except:
                                size = None
                            sMessage.items.append(NetDirectoryItem(folder, directory+folder+"\\", NetTypes.NetDirectoryFolderCollapsable, date_created=os.path.getctime(directory+folder+"\\"), size=size))
                        for file in files:
                            sMessage.items.append(NetDirectoryItem(file, directory+file, NetTypes.NetDirectoryFile.value, date_created=os.path.getctime(directory+file), last_modified=os.path.getmtime(directory+file), size=os.path.getsize(directory+file)))
                        s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetDirectoryListing, sMessage, id=id)))

        # if server sent an id, then set the id to it
        elif message['type'] == NetTypes.NetIdentification.value:
            set_id(message['data']['id'])

if __name__ == "__main__":
    main()