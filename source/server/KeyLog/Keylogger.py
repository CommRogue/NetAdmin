import GUIHelpers
from NetProtocol import *

class KeyloggerManager(GUIHelpers.TabManager):
    def __init__(self, client, inspector_controller):
        self.inspector_controller = inspector_controller
        self.client = client
        self.time_possibilies = ['15M', "1H", "1D", "1W", "1M", "1Y"]
        self.initialized = False

    def refresh(self, time):
        # self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetKeyloggerGet, extra=))
        pass

    def tab_entered(self):
        if not self.initialized:
            self.initialized = True
            self.refresh()

    def tab_closed(self):
        pass