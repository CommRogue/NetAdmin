import OpenConnectionHelpers
from PyQt5.QtCore import pyqtSignal, QObject
from OpenConnectionHelpers import *
import queue

class UploadDialogModel:
    def __init__(self, controller, client):
        self.controller = controller
        self.client = client
        self.open_con = None
        self.uploading_status = False

    def cancelUpload(self):
        if self.open_con:
            self.open_con.close()
            self.open_con = None

    def upload(self, pathToUpload : str, remotePath : str, encrypt, signal_emitter : OpenConnectionHelpers.update_signal_emitter):
        self.uploading_status = True
        con = OpenConnectionHelpers.open_connection(self.client, encrypt=encrypt)
        self.open_con = con
        con.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetStartUpload))
        # replace character / with \\ in pathToUpload
        pathToUpload = pathToUpload.replace('/', '\\')
        result = OpenConnectionHelpers.server_to_client_sendallfiles(con, pathToUpload, pathToUpload, signal_emitter, remotePath)
        if result != -1:
            con.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetEndUpload))
            size, response, _ = con.receive_message()
            if size != -1:
                if response['type'] == NetTypes.NetStatus.value:
                    if response['data']['statusCode'] == NetStatusTypes.NetOK.value:
                        con.close()
                        self.open_con = None
                        self.uploading_status = False
                        signal_emitter.report_finished_upload()