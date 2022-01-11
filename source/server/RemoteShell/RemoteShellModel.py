from PyQt5.QtCore import pyqtSignal
from OpenConnectionHelpers import *

class RemoteShellModel:
    def __init__(self, controller):
        self.controller = controller
        self.sock = None

    def send_text(self, text):
        self.sock.send(text.encode())

    def _start(self, client, status: SharedBoolean, text_signal: pyqtSignal(str)):
        self.sock = open_connection(client)
        event = client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetOpenShell.value), track_event=True)
        result = event.wait(15)  # do default 10 seconds for event.wait
        if result:
            data = event.get_data()
            if isinstance(data, NetStatus):
                if data.statusCode != NetStatusTypes.NetOK.value:
                    raise Exception("RemoteShellModel: Failed to open shell")
        self.sock.settimeout(0.5)
        while status:
            try:
                text = self.sock.recv(4016).decode()
                text_signal.emit(text)
            except:
                break