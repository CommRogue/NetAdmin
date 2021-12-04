from NetProtocol import *
import time
import threading

class ClientInspectorController:
    def requestMetrics(self, client):
        while(True):
            self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetSystemMetrics))
            time.sleep(1)

    def __init__(self, view, client):
        self.view = view
        self.client = client
        thread = threading.Thread(target=self.requestMetrics, args=(client,))
        thread.start()

    def close(self):
        self.view.close()

    def show(self):
        self.view.show()

    def updateMetrics(self):
        self.client.dataLock.acquire_read()
        metrics = self.client.systemMetrics
        self.view.CPUUsagePrecentage.setText(f"{metrics.CPU_LOAD}%")
        self.view.CPUUsageProgressBar.setValue(metrics.CPU_LOAD)
        self.client.dataLock.release_read()
        self.view.CPUUsagePrecentage.repaint()