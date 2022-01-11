from PyQt5.QtWidgets import QMessageBox
import logging

def infobox(title, text):
    logging.info("GUI: InfoBox: " + text)
    dialog = QMessageBox()
    dialog.setText(text)
    dialog.setWindowTitle(title)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec_()

class MVCModel:
    def __init__(self, model=None, view=None):
        MVCModel.set_view(self, view)
        MVCModel.set_model(self, model)

    def set_view(self, view):
        """
        Set the view of the controller.
        Args:
            view: the view of the controller.
        """
        # set the view
        self.view = view

    def set_model(self, model):
        """
        Set the model of the controller.
        Args:
            model: the model of the controller.
        """
        self.model = model