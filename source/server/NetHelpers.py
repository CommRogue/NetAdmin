import MainWindowModel
from NetProtocol import *
import socket
import orjson


def open_connection(client : typing.Union[MainWindowModel.Client, socket.socket]):
    """
    Opens a new socket to the client or socket passed in.
    Args:
        client: a MainWindowModel.Client or socket.socket object.

    Returns: socket of the new connection.
    """
    # if passed in MainWindowModel.Client
    if isinstance(client, MainWindowModel.Client):
        # send open connection request
        event = client.send_message(NetMessage(NetTypes.NetRequest.value, NetTypes.NetOpenConnection.value), track_event=True)
        # wait for response and get data from it
        event.wait()
        data = event.get_data()
        extra = event.get_extra()

        # if response is ok
        if type(data) is NetStatus:
            if data.statusCode == NetStatusTypes.NetOK.value:
                # connect to client using new socket
                ocSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ocSocket.connect((client.address[0], int(extra)))
                return ocSocket

    if isinstance(client, socket.socket):
        # send open connection request
        client.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetRequest.value, NetTypes.NetOpenConnection.value)))

        # wait for response and get data from it
        size, message = NetProtocol.unpackFromSocket(client)
        message = orjson.loads(message)
        data = message["data"]
        extra = message["extra"]

        # if response is ok
        if data == NetStatusTypes.NetOK.value:
            # connect to client using new socket
            ocSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ocSocket.connect((client.getpeername()[0], int(extra)))
            return ocSocket