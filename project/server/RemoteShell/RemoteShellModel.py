from PyQt5.QtCore import pyqtSignal, QObject
from OpenConnectionHelpers import *
from NetProtocol import *

class RemoteShellModel(QObject):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.sock = None

    def send_text(self, text):
        self.sock.send(text.encode())

    def _start(self, client, status: SharedBoolean, text_signal: pyqtSignal(str)):
        self.sock = open_connection(client)
        self.sock.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetOpenShell.value))
        # receive response, and access index 1 to get data and not size
        size, response, isEncrypted = self.sock.receive_message()
        if response:
            if response['type'] == NetTypes.NetStatus.value:
                if response['data']['statusCode'] != NetStatusTypes.NetOK.value:
                    raise Exception("RemoteShellModel: Failed to open shell")
        self.sock.settimeout(0.5)
        # set timeout to 0.5 seconds, so that the check for status is run every 0.5 seconds, and when the status is false, stop the thread
        while status:
            try:
                size, text, isEncrypted = self.sock.recv_appended_stream(raise_exceptions=True)
                text_signal.emit(text.decode())
                print("received", isEncrypted, "text")
            except socket.timeout:
                if not status:
                    break
            # except Exception as e:
            #     print(f"ERROR {str(e)}")
            #     break
        if not status:
            self.sock.close()