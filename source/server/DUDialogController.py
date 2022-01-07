import DUDialog

class DUDialogController:
    def __init__(self, view=None, model=None):
        self.view = view
        self.model = model
        self.view = view

    def set_view(self, view):
        """
        Set the view of the controller.
        Args:
            view: the view of the controller.
        """
        self.view = view

    def set_model(self, model):
        """
        Set the model of the controller.
        Args:
            model: the model of the controller.
        """
        self.model = model

    def on_downloadbutton_clicked(self):
        """
        Handle the download button click event.
        """
        # get local directory from view
        localdir = self.view.localDownloadDirectory

        # get remote directory from view
        remotedir = self.view.fileExplorerItem.path

        # download file
        self.model.download_file(localdir, remotedir)
