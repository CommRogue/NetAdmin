import time
import threading

class UniqueIDInstance:
    def __init__(self):
        self.lock = threading.Lock()
        self.__unused = [x for x in range(0, 1000)]
        self.__occupied = []

    def getId(self):
        self.lock.acquire()
        if len(self.__unused) == 0:
            self.lock.release()
            raise Exception("No more IDs available in the UniqueIDInstance")
        else:
            id = self.__unused.pop()
            print("GIVEN ID: " + str(id))
            self.__occupied.append(id)
            self.lock.release()
            return id

    def releaseId(self, id):
        self.lock.acquire()
        if id in self.__occupied:
            self.__occupied.remove(id)
            self.__unused.append(id)
            print("RELEASED ID: " + str(id))
            self.lock.release()
        else:
            self.lock.release()
            raise Exception("Tried to release an ID that was not in the UniqueIDInstance")