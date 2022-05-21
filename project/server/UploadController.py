import math
import threading, os, logging, GUIHelpers
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QFileDialog

# TODO - duplicate function from FileExplorer in client files, get rid of annoying f variable
import InspectionWindowView
import OpenConnectionHelpers


def ActualDirectorySize(path, f): # always set f true in call
    size = 0
    try:
        for dir in os.scandir(path):
            try:
                if dir.is_file():
                    size += dir.stat().st_size
                else:
                    size += ActualDirectorySize(dir.path, False)
            except:
                print("Error getting size of " + dir.path)
    except:
        print("Error getting size of " + path)
        if f:
            return 0  # signifying that the size of all accessible files (which is no files) is 0
    return size

class UploadDialogController(QObject, GUIHelpers.MVCModel):
    upload_progress_signal = pyqtSignal(object, object) #string (type of message either

    def __init__(self, fileExplorerSelection, fileExplorerManager, view=None, model=None):
        GUIHelpers.MVCModel.__init__(self)
        QObject.__init__(self)
        self.pathToUploadTo = fileExplorerSelection.path
        self.localPathToUpload = None
        self.fileExplorerManager = fileExplorerManager
        self.total_bytes_uploaded = 0
        self.upload_progress_signal.connect(self.progress_signal)
        self.total_link_excluded = 0
        self.total_accessdenied_excluded = 0

    def progress_signal(self, message, progress):
        if message == "bytes_sent":
            self.total_bytes_uploaded += progress
            self.view.update_progress_bar(min(round(self.total_bytes_uploaded/self.size, 2)*100, 100))
        elif message == "excluded_link":
            self.total_link_excluded += 1
        elif message == "excluded_accessdenied":
            self.total_accessdenied_excluded += 1
        elif message == "finished_upload":
            self.view.update_progress_bar(100)
            if self.total_link_excluded > 0 or self.total_accessdenied_excluded > 0:
                infostring = "Upload complete."
                if self.total_link_excluded > 0:
                    infostring += f"\n{self.total_link_excluded} links were excluded."
                if self.total_accessdenied_excluded > 0:
                    infostring += f"\n{self.total_accessdenied_excluded} files were not accessible."
            else:
                infostring = "All files were successfully uploaded."

            GUIHelpers.infobox("Upload complete", infostring)
            self.view.close()
        elif message == "upload_failed":
            GUIHelpers.infobox("Upload failed", "Upload failed unexpectedly, possibly due to network issues. Try again later.")
            self.view.close()

    def choose_locationClicked(self):
        # qt file dialog
        directory = QFileDialog.getExistingDirectory(self.view, "Choose a directory or file to upload....")
        if directory != "":
            self.localPathToUpload = directory
            # update the text of the view
            self.view.localDirectoryText.setText(self.localPathToUpload)
            self.size = ActualDirectorySize(self.localPathToUpload, True)
            self.view.fileSizeText.setText(InspectionWindowView.bytesToStr(self.size))
            self.view.downloadTimeText.setText(f"{round(self.size / 5000000, 2)}s")
            self.view.b1.setEnabled(True)

    def on_uploadbutton_clicked(self):
        # TODO - add optional encryption
        threading.Thread(target=self.model.upload, args=(self.localPathToUpload, self.pathToUploadTo, False, OpenConnectionHelpers.update_signal_emitter(self.upload_progress_signal, max(math.floor(self.size/100), 1),))).start()

    # required for FileExplorerManager calling stop() on both this controller and downloaddialog's controller
    def stop(self):
        self.model.cancelUpload()

    def closeButtonClicked(self):
        self.stop()
        if self.model.uploading_status == True:
            GUIHelpers.infobox("Upload cancelled. ", "Upload has been cancelled by user. Any files that were fully downloaded were saved.")
        self.view.hide()
        self.fileExplorerManager.DUDialogControllers.remove(self)

    def set_view(self, view):
        GUIHelpers.MVCModel.set_view(self, view)
        self.view.downloadLocationText.setText(self.pathToUploadTo)