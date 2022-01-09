import dataclasses
import orjson
import typing
import struct
from enum import Enum
import datetime


class NetTypes(Enum):
    NetRequest = 0
    NetSystemInformation = 1
    NetSystemMetrics = 2
    NetIdentification = 3
    NetDirectoryListing = 4
    NetDirectoryFile = 5
    NetDirectoryFolderCollapsable = 6
    NetDirectoryFolderEmpty = 7
    NetDeleteFile = 8
    NetDownloadFile = 9
    NetStatus = 10
    NetDownloadFileDescriptor = 11
    NetOpenConnection = 12
    NetCloseConnection = 13

class NetStatusTypes(Enum):
    NetOK = 0
    NetDirectoryAccessDenied = 1
    NetInvalidIdentification = 2
    NetFileNotFound = 3


class NetDataStructure:
    pass


@dataclasses.dataclass
class NetStatus:
    statusCode: int

@dataclasses.dataclass
class NetOpenConnection(NetDataStructure):
    port: int

@dataclasses.dataclass
class NetItemStyling:
    icon: str
    color: str


@dataclasses.dataclass
class NetErrorStyling(NetItemStyling):
    icon = None
    color = "#e80c25"


@dataclasses.dataclass
class NetDirectoryItem:
    name: str
    path: str
    itemtype: str
    styling: NetItemStyling
    date_created: datetime.datetime
    last_modified: datetime.datetime
    size: int


    def __init__(self, name: str, path: str, item_type, date_created=None, last_modified=None, size=None, styling=None):
        self.name = name
        self.path = path
        self.itemtype = item_type
        self.icon = styling
        self.date_created = date_created
        self.last_modified = last_modified
        self.size = size


@dataclasses.dataclass
class NetDirectoryListing(NetDataStructure):
    directory: str
    items: typing.List[NetDirectoryItem]


@dataclasses.dataclass
class NetMessage:
    type: int
    data: typing.Union[NetDataStructure, int]
    id: int
    extra: str

    def __init__(self, type, data, id=None, extra=""):
        self.type = type
        self.data = data
        self.id = id
        self.extra = extra


@dataclasses.dataclass
class NetIdentification(NetDataStructure):
    id: str

@dataclasses.dataclass
class NetDownloadFileDescriptor(NetDataStructure):
    name: str
    size: int
    # buffer_size : int
    # buffer_block_count : int

class NetDownloadBlock(NetDataStructure):
    data : bytes

@dataclasses.dataclass
class NetGeoInfo:
    COUNTRY: str
    CITY: str
    REAL_IP: str


@dataclasses.dataclass
class NetSystemInformation(NetDataStructure):
    DESKTOP_NAME: str
    OPERATING_SYSTEM_VERSION: str
    PROCESSOR_NAME: str
    PROCESSOR_ARCHITECTURE: str
    GPU_NAME: str


@dataclasses.dataclass
class NetSystemMetrics(NetDataStructure):
    CPU_LOAD: float
    GPU_LOAD: float
    RAM_LOAD: float
    DISK_LOAD: float


class NetProtocol:
    @staticmethod
    def serialize(data):
        return orjson.dumps(data)

    # serialize and add byte size
    @staticmethod
    def messagePacker(func):
        def wrapper(*args, **kwargs):
            res = func(**args, **kwargs)
            res = NetProtocol.serialize(res)
            res = struct.pack(">I", len(res)) + res
            return res

        return wrapper

    @staticmethod
    def packNetMessage(data: NetMessage):
        data = NetProtocol.serialize(data)
        data = struct.pack(">I", len(data)) + data
        return data

    @staticmethod
    def unpackFromSocket(socket):
        try:
            # receive the message size as a 4 byte integer
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
