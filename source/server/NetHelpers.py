from NetProtocol import *
import socket


def open_connection(client):
    event = client.send_message(NetMessage(NetTypes.NetRequest, NetOpenConnection), track_event=True)

    event.wait()
    data = event.get_data()

    if data is NetStatus:
        if data.statusCode == NetStatusTypes.NetOK:
            # connect to client using new socket
            ocSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ocSocket.connect(client.address)
            return ocSocket