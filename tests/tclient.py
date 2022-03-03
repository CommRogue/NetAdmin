import socket

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# create server
socket.bind(('0.0.0.0', 49152))
socket.listen(1)
s, a = socket.accept()
print(s.recv(1024).decode())