import GUIHelpers
import threading
from OpenConnectionHelpers import *
from PyQt5.QtCore import QObject, pyqtSignal
import socket


class RemoteShellController(QObject, GUIHelpers.MVCModel):
    updateTextSignal = pyqtSignal(str)
    sendTextSignal = pyqtSignal(str)

    def __init__(self, client, model=None, view=None):
        GUIHelpers.MVCModel.__init__(self, model, view)
        QObject.__init__(self)
        self.client = client
        self.continue_reading = SharedBoolean(True)

    def get_command(self):
        if self.view and self.model:
            text_input = self.view.shellInput.text()
            if text_input != "":
                self.view.shellInput.clear()
                text_input += '\n'
                self.sendTextSignal.emit(text_input)

    def set_view(self, view):
        GUIHelpers.MVCModel.set_view(self, view)
        self.view.shellInput.returnPressed.connect(self.get_command)
        def lmbd(text):
            self.view.add_text(text)
        self.updateTextSignal.connect(lmbd)

    def set_model(self, model):
        GUIHelpers.MVCModel.set_model(self, model)
        self.sendTextSignal.connect(self.model.send_text)

    def stop(self):
        self.continue_reading.set(False)

    def start(self):
        if self.view and self.model:
            thread = threading.Thread(target=self.model._start, args=(self.client, self.continue_reading, self.updateTextSignal,))
            thread.start()
        else:
            raise Exception("View or Model not set for RemoteShellController")