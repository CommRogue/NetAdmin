import threading
import socket
import os
import orjson
import sys
import platform
import wmi
sys.path.insert(1, os.path.join(sys.path[0], '../shared'))
from NetProtocol import *

#create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("192.168.1.205", 4959))
computer = wmi.WMI()


while True:
    size, message = NetProtocol.unpackFromSocket(s)
    message = orjson.loads(message)
    if message['type'] == NetTypes.NetRequest.value:
        if message['data'] == NetTypes.NetSystemInformation.value:
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
                computer.Win32_Processor()[0].LoadPercentage
            )
            s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetSystemMetrics, message)))