from RemoteShellModel import RemoteShellModel
from RemoteShellView import RemoteShellView
from RemoteShellController import RemoteShellController

class RemoteShellManager:
    def __init__(self, client, inspector_controller):
        self.inspector_controller = inspector_controller
        self.client = client
        self.remote_shell_list = []

    def create_shell(self):
        controller = RemoteShellController(self.client)
        model = RemoteShellModel(controller)
        view = RemoteShellView(controller)
        controller.set_model(model)
        controller.set_view(view)
        self.remote_shell_list.append(controller)
        controller.start()
        self.inspector_controller.ShellTabContainer.addTab(view, "Remote Shell")

    def tab_entered(self):
        if len(self.remote_shell_list) == 0:
            self.create_shell()