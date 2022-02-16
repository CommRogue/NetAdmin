import logging
import os
import threading

from PyQt5.QtWidgets import QMessageBox, QFileDialog, QDialog
import PyQt5.QtCore
import functools
import DUDialog
from PyQt5.QtCore import pyqtSignal, QObject

import GUIHelpers
import InspectionWindowView
import fileExplorerManager

# class DUDialogController(QObject):
#     du_progress_signal = pyqtSignal(int)
#     def __init__(self, parent=None):

class DUDialogController(QObject, GUIHelpers.MVCModel):
    du_progress_signal = pyqtSignal(object)
    infobox_signal = pyqtSignal(str, str)
    exec_signal = pyqtSignal()
    currentLoadingView = None

    def _exec_(self):
        totalsize = 0
        for item in self.fileExplorerItems:
            if item.size != -1:
                totalsize += item.size
            else:
                # print current thread
                print(threading.current_thread().name)
                self.currentLoadingView = GUIHelpers.sizeLoadingBox(item.path)
                thread = threading.Thread(target=fileExplorerManager.getActualDirectorySize, args=(self.model.client, item, self.exec_signal,))
                thread.start()
                yield
                print(threading.current_thread().name)
                if item.size >= 0:
                    totalsize += item.size
                    self.currentLoadingView.hide()
                    # set the size of the file explorer item with the calculated size
                    fileExplorerManager.FileExplorerManager.redrawItemSize(item, 3)
                    # don't show the calculate size menu option anymore
                    item.showContextMenu = False
        self.totalSize = totalsize
        self.totalSizeStr = InspectionWindowView.bytesToStr(self.totalSize)
        self.view.fileSizeText.setText(self.totalSizeStr)
        self.view.downloadTimeText.setText(f"{round(self.totalSize / 2500000, 2)}s")
        self.view.show()
        yield

    def exec_(self):
        """
        Starts the download dialog.
        Summary of implementation:
        This function creates an _exec_ generator and creates a partial function on the next function, giving it the instance of the generator.
        This partial function is connected to the exec_signal, and then the function calls next on the generator.
        Inside the generator, it iterates over the fileExplorerItems:
            - If size is available, then it adds the size to the total size.
            - If size is not available, then it requests a size request from the client in another thread, and passes it the exec_signal. Afterwards, it yields.
            When the exec_signal is emitted by the worker thread, the call goes back to the yield line where the new size is checked and added to the total size.
        """
        # create generator
        self._execObj = self._exec_()
        # create callback to next function of generator
        funcObj = functools.partial(next, self._execObj)
        # connect the exec signal to the callback
        self.exec_signal.connect(funcObj)
        # start the generator
        next(self._execObj)

    def __init__(self, fileExplorerItems, view=None, model=None):
        QObject.__init__(self)
        self.fileExplorerItems = fileExplorerItems
        self.totalSize = 0
        self.downloading = False
        if len(fileExplorerItems) > 1:
            self.itemsString = f"{len(fileExplorerItems)} items"
        else:
            self.itemsString = fileExplorerItems[0].path

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
        self.infobox_signal.connect(GUIHelpers.infobox)
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

    def on_download_progress(self, bytes_read):
        print(f"Thread of progress: {threading.current_thread().name}")
        # download cancelled by user
        if bytes_read == -2:
            GUIHelpers.infobox("Download Cancelled",
                               "Download request was cancelled by the user. All partially downloaded files were deleted.")
            # don't have to close since closeButtonClicked will close the window
        # download finished
        elif bytes_read == -1:
            self.view.update_progress_bar(100)
            GUIHelpers.infobox("Download finished",
                               f'The download of "{self.itemsString}" has finished. \n It can be located at "{self.localDownloadDirectory}"')
            self.view.close()
        # don't display download progress message
        elif bytes_read == -3:
            pass
        else:
            self.bytes_downloaded += bytes_read
            self.view.update_progress_bar(min(round(self.bytes_downloaded/self.totalSize, 2)*100, 100))

    def stop(self):
        self.closeButtonClicked()
        logging.info("STOPPING DOWNLOAD of %s", self.itemsString)

    def closeButtonClicked(self):
        self.model.cancel_download()
        self.view.close()

    def on_downloadbutton_clicked(self):
        """
        Handle the download button click event.
        """
        if not self.downloading:
            # get local directory from view
            self.downloading = True
            localdir = self.localDownloadDirectory

            # get remote directory from view
            remotedirs = self.fileExplorerItems
            remotedirs = map(lambda x: x.path, remotedirs)

            download_thread = threading.Thread(target=self.model.download_files, args=(localdir, remotedirs, self.du_progress_signal, self.infobox_signal, self.totalSize))
            download_thread.start()
        else:
            GUIHelpers.infobox("Download in progress", "The download is already in progress.")


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