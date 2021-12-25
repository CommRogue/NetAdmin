import threading
import socket
import os
import orjson
import sys
import platform
import wmi
sys.path.insert(1, os.path.join(sys.path[0], '../shared'))
from NetProtocol import *
import psutil
import GPUtil
import winreg
import win32api
from os import listdir
from os.path import isfile, join

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

        if message['type'] == NetTypes.NetRequest.value:
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
                sMessage = NetSystemMetrics(
                    psutil.cpu_percent(),
                    RAM_LOAD=psutil.virtual_memory().percent,
                    GPU_LOAD=GPUtil.getGPUs()[0].load,
                    DISK_LOAD=psutil.disk_usage('/')[3]
                )
                s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetSystemMetrics, sMessage, id=id)))

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
                        sMessage.items.append(NetDirectoryItem(drive[:2], drive, NetTypes.NetDirectoryFolderCollapsable.value))
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
                        s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetError, NetError(NetErrors.NetDirectoryAccessDenied.value), id=id)))

                    # if got directory listing (we have permission)
                    else:
                        sMessage = NetDirectoryListing(directory, [])

                        # append NetDirectoryItems for each file/folder
                        for folder in folders:
                            sMessage.items.append(NetDirectoryItem(folder, directory+folder+"\\", NetTypes.NetDirectoryFolderCollapsable.value))
                        for file in files:
                            sMessage.items.append(NetDirectoryItem(file, directory+file+"\\", NetTypes.NetDirectoryFile.value))
                        s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetDirectoryListing, sMessage, id=id)))

        # if server sent an id, then set the id to it
        elif message['type'] == NetTypes.NetIdentification.value:
            set_id(message['data']['id'])

if __name__ == "__main__":
    main()