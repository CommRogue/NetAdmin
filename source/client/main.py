import threading
import socket

#create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 4959))

while True:
    txt = s.recv(1024).decode()
    if txt == "heartbeat":
        s.send("heartbeat".encode())