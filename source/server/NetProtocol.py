import dataclasses
import orjson
import typing
import struct

@dataclasses.dataclass
class NetMessage:
    type : str
    data : str

@dataclasses.dataclass
class NetRequest(NetMessage):
    pass

@dataclasses.dataclass
class NetResponse(NetMessage):
    pass

class NetProtocol:
    @staticmethod
    def serialize(data):
        return orjson.dumps(data)

    #serialize and add byte size
    @staticmethod
    def messagePacker(func):
        def wrapper(*args, **kwargs):
            res = func(**args, **kwargs)
            res = NetProtocol.serialize(res)
            res = struct.pack(">I", len(res)) + res
            return res
        return wrapper

    @staticmethod
    def packNetMessage(data : NetMessage):
        data = NetProtocol.serialize(data)
        data = struct.pack(">I", len(data)) + data
        return data

    @staticmethod
    def unpackFromSocket(socket):
        try:
            size = socket.recv(4)
        except ConnectionError:
            return -1, -1
        else:
            if size:
                size = struct.unpack(">I", size)[0]
                data = socket.recv(size)
                return size, data
            else:
                return -1, -1

    @staticmethod
    @messagePacker
    def heartbeat():
        pass