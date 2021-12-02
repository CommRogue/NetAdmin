import threading
import socket
from NetProtocol import NetProtocol

#create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 4959))

while True:
    size, message = NetProtocol.unpackFromSocket(s)
    print(f"received {message}")