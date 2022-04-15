import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 8080))
s.listen(5)

b = s.accept()[0]

n = s.accept()[0]


print(n.recv(1024).decode())
print(b.recv(1024).decode())