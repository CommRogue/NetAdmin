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
        if message['type'] == NetTypes.NetRequest.value:
            if message['data'] == NetTypes.NetIdentification.value: #if request to identify
                try:
                    uid = get_id()
                except:
                    message = NetIdentification("")
                else:
                    message = NetIdentification(uid)
                s.send(NetProtocol.packNetMessage(NetMessage(type=NetTypes.NetIdentification, data=message)))
            elif message['data'] == NetTypes.NetSystemInformation.value:
                message = NetSystemInformation(
                    platform.node(),
                    platform.system(),
                    platform.processor(),
                    platform.machine(),
                    computer.Win32_VideoController()[0].Name
                )
                s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetSystemInformation, message)))
            elif message['data'] == NetTypes.NetSystemMetrics.value:
                message = NetSystemMetrics(
                    computer.Win32_Processor()[0].LoadPercentage,
                    RAM_LOAD=psutil.virtual_memory().percent,
                    GPU_LOAD=GPUtil.getGPUs()[0].load,
                    DISK_LOAD=psutil.disk_usage('/')[3]
                )
                s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetSystemMetrics, message)))
        elif message['type'] == NetTypes.NetIdentification.value:
            set_id(message['data']['id'])

if __name__ == "__main__":
    main()