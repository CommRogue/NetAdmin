import GUIHelpers
from RemoteShellModel import RemoteShellModel
from RemoteShellView import RemoteShellView
from RemoteShellController import RemoteShellController

class RemoteShellManager(GUIHelpers.TabManager):
    def __init__(self, client, inspector_controller):
        self.inspector_controller = inspector_controller
        self.inspector_controller.view.ShellTabContainer.tabCloseRequested.connect(self.tabCloseRequested)
        self.client = client
        self.remote_shell_list = []
        self.inspector_controller.view.shellAddButton.clicked.connect(self.tabAddRequested)

    def create_shell(self):
        controller = RemoteShellController(self.client)
        model = RemoteShellModel(controller)
        view = RemoteShellView(controller)
        controller.set_model(model)
        controller.set_view(view)
        self.remote_shell_list.append(controller)
        controller.start()
        self.inspector_controller.view.ShellTabContainer.addTab(view, "Shell {}".format(len(self.remote_shell_list)))

    def tab_entered(self):
        if len(self.remote_shell_list) == 0:
            self.create_shell()

    def tab_closed(self):pass

    def stop_all(self):
        """
        Stops all shells. Does not remove their tab from the UI.
        """
        for shell in self.remote_shell_list:
            shell.stop()
        self.remote_shell_list = []

    def tabCloseRequested(self, index):
        """
        Responds to the shell tab close signal.
        Args:
            index: index of the shell to be closed.
        """
        self.remote_shell_list[index].stop()
        self.remote_shell_list.pop(index)
        self.inspector_controller.view.ShellTabContainer.removeTab(index)

    def tabAddRequested(self):
        self.create_shell()