import ctypes
import os
import sys
import threading

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_exe_directory():
    return os.path.dirname(sys.executable) + "\\"

# create a decorator to try the function and catch any exceptions
def try_connection(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ConnectionAbortedError, ConnectionResetError, OSError) as e:
            print(f"THREAD {threading.current_thread().name} [FUNC {func.__name__}]: Connection disconnected by server without message:")
            print(e)
    return wrapper