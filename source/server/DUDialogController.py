import os
import threading

from PyQt5.QtWidgets import QMessageBox, QFileDialog

import DUDialog
from PyQt5.QtCore import pyqtSignal, QObject

import GUIHelpers
import fileExplorerManager

# class DUDialogController(QObject):
#     du_progress_signal = pyqtSignal(int)
#     def __init__(self, parent=None):

class DUDialogController(QObject, GUIHelpers.MVCModel):
    du_progress_signal = pyqtSignal(int)
    def __init__(self, fileExplorerItems, view=None, model=None):
        QObject.__init__(self)
        self.fileExplorerItems = fileExplorerItems
        self.totalSize = 0
        for item in fileExplorerItems:
            if item.size:
                self.totalSize += item.size
        self.totalSizeStr = fileExplorerManager.bytesToStr(self.totalSize)
        if len(fileExplorerItems) > 1:
            self.itemsString = f"{len(fileExplorerItems)} items"
        else:
            self.itemsString = fileExplorerItems[0].path
        self.totalSizeStr = str(self.totalSizeStr)

        # if len(fileExplorerItems) > 1:
        #     self.itemsString = f"{len(fileExplorerItems)} items"
        #     self.totalSize = 0
        #     for item in fileExplorerItems:
        #         self.totalSize += DUDialogController.calculate_size(item)
        #     self.totalSizeStr = fileExplorerManager.bytesToStr(self.totalSize)
        # else:
        #     self.itemsString = fileExplorerItems[0].path
        #     self.totalSize = DUDialogController.calculate_size(fileExplorerItems[0])
        #     self.totalSizeStr = fileExplorerManager.bytesToStr(self.totalSize)
        GUIHelpers.MVCModel.__init__(self, model, view)
        self.bytes_downloaded = 0
        self.du_progress_signal.connect(self.on_download_progress)
        self.localDownloadDirectory = os.getcwd() + "\\Downloads"

    @staticmethod
    def calculate_size(item):
        """
        Calculates the size of a given item from the file viewer.
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
        # set the view (included in MVCModel)
        GUIHelpers.MVCModel.set_view(self, view)

        self.view.remoteDirectoryText.setText(self.itemsString)
        self.view.downloadLocationText.setText(self.localDownloadDirectory)
        self.view.fileSizeText.setText(self.totalSizeStr)
        self.view.downloadTimeText.setText(f"{round(self.totalSize / 2500000, 2)}s")


    def on_download_progress(self, bytes_read):
        print(f"Thread of progress: {threading.current_thread().name}")
        if bytes_read == -2:
            GUIHelpers.infobox("Download Cancelled",
                               "Download request was cancelled by the user. All partially downloaded files were deleted.")
            # don't have to close since closeButtonClicked will close the window
        elif bytes_read == -1:
            GUIHelpers.infobox("Download finished",
                               f'The download of "{self.itemsString}" has finished. \n It can be located at "{self.localDownloadDirectory}"')
            self.view.close()
        else:
            self.bytes_downloaded += bytes_read
            self.view.update_progress_bar(min(round(self.bytes_downloaded/self.totalSize, 2)*100, 100))

    def closeButtonClicked(self):
        self.model.cancel_download()
        self.view.close()

    def on_downloadbutton_clicked(self):
        """
        Handle the download button click event.
        """
        # get local directory from view
        localdir = self.localDownloadDirectory

        # get remote directory from view
        remotedirs = self.fileExplorerItems
        remotedirs = map(lambda x: x.path, remotedirs)

        #-- # iterate over the file explorer items and check if they are collpasable. if so, then add all their children to the list
        #-- for item in self.fileExplorerItems:
        #--     self.resolveChildren(remotedirs, item, item.path)

        # download file
        download_thread = threading.Thread(target=self.model.download_files, args=(localdir, remotedirs, self.du_progress_signal))
        download_thread.start()

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