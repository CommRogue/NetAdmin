import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 8080))

n = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
n.connect(("127.0.0.1", 8080))

s.send("helloS".encode())
n.send("helloN".encode())