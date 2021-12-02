from dataclasses import dataclass

@dataclass
class ConnectionData:
    """
    NetData class
    """
    data: str
    addr: str
    port: int
    def __init__(self, data, addr, port):
        self.data = data
        self.addr = addr
        self.port = port

@dataclass
class SystemInformation:
    """
    SystemData class -
    Describes the client's operating system data
    """
    data: str
    addr: str
    port: int
    def __init__(self, data, addr, port):
        self.data = data
        self.addr = addr
        self.port = port

@dataclass
class SystemMetrics:
    """
    SystemMetrics class -
    Describes the client's operating system metrics
    """
    data: str
    addr: str
    port: int
    def __init__(self, data, addr, port):
        self.data = data
        self.addr = addr
        self.port = port