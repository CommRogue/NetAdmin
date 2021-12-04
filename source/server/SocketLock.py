import threading

class SocketLock:
    def __init__(self):
        self._readers = 0
        self._read_lock = threading.Condition(threading.Lock())

    def acquire_read(self):
        self._read_lock.acquire()
        try:
            self._readers += 1
        finally:
            self._read_lock.release()

    def release_read(self):
        self._read_lock.acquire()
        try:
            self._readers -= 1
            if self._readers == 0:
                self._read_lock.notify_all()
        finally :
            self._read_lock.release()

    def acquire_write(self):
        self._read_lock.acquire()
        while self._readers > 0:
            self._read_lock.wait()

    def release_write(self):
        self._read_lock.release()