import dataclasses
import orjson
import typing
import struct

@dataclasses.dataclass
class NetMessage:
    client_id : str
    main_data : str

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

    @staticmethod
    def prepareMessage(func):
        def wrapper(*args, **kwargs):
            res = func(**args, **kwargs)
            res = NetProtocol.serialize(res)
            res = bytes(struct.pack(">I", len(res))) + res
            return res
        return wrapper

    @staticmethod
    @prepareMessage
    def heartbeat():
        pass