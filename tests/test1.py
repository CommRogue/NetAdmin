import socket
import threading

HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

def get_input(socket):
    while True:
        inputt = input()
        inputt += '\n'
        socket.send(inputt.encode())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    # create thread on get_input
    thread = threading.Thread(target=get_input, args=(conn,))
    thread.start()
    while True:
        data = conn.recv(1024)
        print(data.decode())