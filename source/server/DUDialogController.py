import os

from PyQt5.QtWidgets import QMessageBox, QFileDialog

import DUDialog
from PyQt5.QtCore import pyqtSignal, QObject

class DUDialogController(QObject):
    download_progress_signal = pyqtSignal(int)
    def __init__(self, fileExplorerItems, view=None, model=None):
        super().__init__()
        self.fileExplorerItems = fileExplorerItems
        if len(fileExplorerItems) > 1:
            self.itemsString = f"{len(fileExplorerItems)} items"
            self.totalSize = 0
            for item in fileExplorerItems:
                self.totalSize += DUDialogController.calculate_size(item)
        else:
            self.itemsString = fileExplorerItems[0].path
            self.totalSize = DUDialogController.calculate_size(fileExplorerItems[0])
        self.view = view
        self.model = model
        self.view = view
        self.bytes_downloaded = 0
        self.download_progress_signal.connect(self.on_download_progress)
        self.localDownloadDirectory = os.getcwd() + "\\Downloads"

    @staticmethod
    def calculate_size(item):
        """
        Calculates the size of a given item.
        Args:
            item: the item to calculate the size of.
        """
        if not item.collapsable:
            return item.size
        else:
            total_size = 0
            children = []
            DUDialogController.resolveChildren(children, item, item.path)
            for child in children:
                total_size += child.size
            return total_size

    def set_view(self, view):
        """
        Set the view of the controller, and edits the view's fields accordingly.
        Args:
            view: the view of the controller.
        """
        # set the view
        self.view = view

        self.view.remoteDirectoryText.setText(self.itemsString)
        self.view.downloadLocationText.setText(self.localDownloadDirectory)
        self.view.fileSizeText.setText(self.totalSize)
        self.view.downloadTimeText.setText(f"{round(self.totalSize / 2500000, 2)}s")


    def on_download_progress(self, bytes_read):
        if bytes_read == -1:
            dialog = QMessageBox()
            dialog.setText(f'The download of "{self.itemsString}" has finished. \n It can be located at "{self.localDownloadDirectory}"')
            dialog.setWindowTitle("Download finished")
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.exec_()
            self.view.close()
        self.bytes_downloaded += bytes_read
        self.view.update_progress_bar(round(self.bytes_downloaded/self.totalSize, 2)*100)

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
        localdir = self.localDownloadDirectory

        # get remote directory from view
        remotedirs = []
        # iterate over the file explorer items and check if they are collpasable. if so, then add all their children to the list
        for item in self.fileExplorerItems:
            self.resolveChildren(remotedirs, item, item.path)

        # download file
        self.model.download_file(localdir, remotedirs, self.download_progress_signal)

    @staticmethod
    def resolveChildren(clist, item, base_path):
        """
        recursive function that adds a tuple of all the children of a given item and their path offset from the given item to the list.
        Args:
            clist: the list to append the children to.
            item: the item to get the children from.
        """
        if not item.collapsable:
            clist.append((item, os.path.relpath(item.path, base_path)))
        else:
            childCount = item.childCount()
            for i in range(childCount):
                DUDialogController.resolveChildren(clist, item.child(i), base_path)

    def choose_locationClicked(self):
        """
        Handle the choose location button click event.
        """
        # qt file dialog
        directory = QFileDialog.getExistingDirectory(self.view, "Choose a directory....", self.localDownloadDirectory, options=QFileDialog.ShowDirsOnly)
        self.localDownloadDirectory = directory
        # update the text of the view
        self.view.downloadLocationText.setText(self.localDownloadDirectory)