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
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\NetAdmin\\Configuration")
    winreg.SetValue(key, 'UUID', winreg.REG_SZ, id)

def get_id():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\NetAdmin\\Configuration")
    return winreg.QueryValue(key, 'UUID')

def main():
    # create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 49152))
    computer = wmi.WMI()
    while True:
        size, message = NetProtocol.unpackFromSocket(s)
        message = orjson.loads(message)
        id = message['id']
        if message['type'] == NetTypes.NetRequest.value:
            if message['data'] == NetTypes.NetIdentification.value: #if request to identify
                try:
                    uid = get_id()
                except:
                    sMessage = NetIdentification("")
                else:
                    sMessage = NetIdentification(uid)
                s.send(NetProtocol.packNetMessage(NetMessage(type=NetTypes.NetIdentification, data=sMessage, id=id)))
            elif message['data'] == NetTypes.NetSystemInformation.value:
                sMessage = NetSystemInformation(
                    platform.node(),
                    platform.system(),
                    platform.processor(),
                    platform.machine(),
                    computer.Win32_VideoController()[0].Name
                )
                s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetSystemInformation, sMessage, id=id)))
            elif message['data'] == NetTypes.NetSystemMetrics.value:
                sMessage = NetSystemMetrics(
                    psutil.cpu_percent(),
                    RAM_LOAD=psutil.virtual_memory().percent,
                    GPU_LOAD=GPUtil.getGPUs()[0].load,
                    DISK_LOAD=psutil.disk_usage('/')[3]
                )
                s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetSystemMetrics, sMessage, id=id)))
            elif message['data'] == NetTypes.NetDirectoryListing.value:
                directory = message['extra']
                if(directory == ""):
                    drives = win32api.GetLogicalDriveStrings()
                    drives = drives.split('\000')[:-1]
                    sMessage = NetDirectoryListing("", [])
                    for drive in drives:
                        sMessage.items.append(NetDirectoryItem(drive[:2], drive, NetTypes.NetDirectoryFolderCollapsable.value))
                else:
                    files = [f for f in listdir(directory) if isfile(join(directory, f))]
                    folders = [f for f in listdir(directory) if not isfile(join(directory, f))]
                    sMessage = NetDirectoryListing(directory, [])
                    for folder in folders:
                        sMessage.items.append(NetDirectoryItem(folder, directory+folder+"\\", NetTypes.NetDirectoryFolderCollapsable.value))
                    for file in files:
                        sMessage.items.append(NetDirectoryItem(file, directory+file+"\\", NetTypes.NetDirectoryFile.value))
                s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetDirectoryListing, sMessage, id=id)))
        elif message['type'] == NetTypes.NetIdentification.value:
            set_id(message['data']['id'])

if __name__ == "__main__":
    main()