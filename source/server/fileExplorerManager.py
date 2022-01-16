from PyQt5.QtCore import *

import GUIHelpers
from DUDialogController import DUDialogController
from DUDialogModel import DUDialogModel
from InspectionWindowController import *
from source.server.InspectionWindowView import FileExplorerItem
import logging
import math
import DUDialog

def bytesToStr(size : int) -> str:
    """
    Convert file size in bytes to human readable string
    Args:
        size: integer of the size in bytes.

    Returns: a string representing the size in human readable format.
    """
    if size:
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        # get size name
        i = int(math.floor(math.log(size, 1024)))
        # get remainder
        p = math.pow(1024, i)
        s = round(size / p, 2)
        return str(f"{s} {size_name[i]}")
    return str(size)

class DirectoryDeletionAction(QRunnable):
    def __init__(self, client, selections, sUpdate, sClear, sRemove, infoboxSignal):
        super().__init__()
        self.client = client
        self.selections = selections
        self.sUpdate = sUpdate
        self.sClear = sClear
        self.sRemove = sRemove
        self.infoboxSignal = infoboxSignal

    def run(self):
        if self.selections:
            for selection in self.selections:
                event = self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetDeleteFile, extra=selection.path), track_event=True)
                result = event.wait(15) # do default 10 seconds for event.wait
                if result:
                    data = event.get_data()
                    if isinstance(data, NetStatus):
                        if data.statusCode == NetStatusTypes.NetOK.value:
                            self.sRemove.emit(selection)
                        elif data.statusCode == NetStatusTypes.NetDirectoryAccessDenied.value:
                            self.infoboxSignal.emit("Access Denied", f"You do not have permission to delete '{selection.path}'.")

class DirectoryListingAction(QRunnable):
    def __init__(self, client, view, sUpdate, sClear, itemParent=None):
        super().__init__()
        self.itemParent = itemParent
        self.view = view
        self.client = client
        self.sUpdate = sUpdate
        self.sClear = sClear

    def run(self):
        if self.itemParent: #if the click is directed towards a directory and not just the drives
            path = self.itemParent.path
            self.sClear.emit(self.itemParent)
            self.sUpdate.emit(FileExplorerItem(None, False, ["Loading...."], size=None, parent=self.itemParent, styling=None), self.itemParent)
        else: #if directory is the drives (root)
            #self.view.fileViewer.insertTopLevelItem(0, QTreeWidgetItem(["Loading..."]))
            path = "" #set the path to none to get root directory listing
        event = self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetDirectoryListing, id=None, extra=path), track_event=True)
        event.wait()
        data = event.get_data()

        if self.itemParent:  # if a directory, then clear the "Loading..." item or the previous items from the last click
            self.sClear.emit(self.itemParent)

        if type(data) is NetStatus and data.statusCode == NetStatusTypes.NetDirectoryAccessDenied.value:
            self.sUpdate.emit(FileExplorerItem(None, False, ["Access is denied to this directory...."], None, self.itemParent, NetErrorStyling), self.itemParent) #will send itemParent as none if there is no parent
        else:
            for item in data.items:
                if item["date_created"]:
                    date_created = str(datetime.datetime.fromtimestamp(item["date_created"]))
                else:
                    date_created = None
                if item["last_modified"]:
                    date_modified = str(datetime.datetime.fromtimestamp(item["last_modified"]))
                else:
                    date_modified = None

                strings = [item["name"], date_created, date_modified]
                if item["size"] and item["size"] != 0 and item["size"] != -1:
                    strings.append(bytesToStr(item["size"]))
                    nosize = False
                elif item["size"] == -1:
                    strings.append("N/A: Download to calculate")
                    nosize = True
                else:
                    nosize = False

                # emit a signal to add the item to the treeview.
                # if no parent, then self.itemParent is None and the item will be added to the top level
                # single-line if statement to handle the case where the item is a directory. if so, then set the collapsable argument to true
                self.sUpdate.emit(FileExplorerItem(item["path"], True if item['itemtype'] == NetTypes.NetDirectoryFolderCollapsable.value else False, strings, item["size"], self.itemParent, None, nosize=nosize), self.itemParent)
        self.view.update()

def getActualDirectorySize(client, item, finishedSignal):
    event = client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetDirectorySize, extra=item.path), track_event=True)
    event.wait()
    data = event.get_data()
    if type(data) is NetDirectorySize:
        item.size = data.size
        finishedSignal.emit()

class FileExplorerManager(QObject):
    sDirectoryListingUpdate = pyqtSignal(FileExplorerItem, object)  # child, parent
    sClearDirectoryListing = pyqtSignal(FileExplorerItem)  # parent
    sRemoveDirectoryListing = pyqtSignal(FileExplorerItem)  # child
    sInfoBox = pyqtSignal(str, str)

    def clearItemChildren(self, item):
        print("started")
        while (item.childCount() > 0):
            child = item.child(0)
            item.removeChild(child)
            del child
        print("finished")

    def __init__(self, client, view):
        super().__init__()
        self.view = view
        self.fileExplorerInitialized = False
        self.sClearDirectoryListing.connect(self.clearDirectoryListing)
        self.sDirectoryListingUpdate.connect(self.updateDirectoryListing)
        self.sRemoveDirectoryListing.connect(self.removeDirectoryListing)
        self.sInfoBox.connect(self.infoBox)
        self.view.fileViewer.itemExpanded.connect(self.fileViewerItemExpanded)
        self.view.fileViewer.itemSelectionChanged.connect(self.fileViewerSelectionChanged)
        self.view.deleteButton.clicked.connect(self.fileViewerDeleteButtonClicked)
        self.view.downloadButton.clicked.connect(self.fileViewerDownloadButtonClicked)
        self.selections = None
        self.client = client

    def infoBox(self, title, body):
        GUIHelpers.infobox(title, body)

    def initializeContents(self):
        self.fileExplorerInitialized = True
        threadPool = QThreadPool.globalInstance()
        threadPool.start(
            DirectoryListingAction(self.client, self.view, self.sDirectoryListingUpdate, self.sClearDirectoryListing, None))

    def is_initialized(self):
        """
        Returns whether the file explorer has been initialized.
        Returns: boolean stating whether the file explorer has been initialized.
        """
        return self.fileExplorerInitialized

    def clearDirectoryListing(self, parent : FileExplorerItem):
        self.clearItemChildren(parent)

    def updateDirectoryListing(self, child : FileExplorerItem, parent: FileExplorerItem):
        if parent:
            parent.insertChild(0, child)
        else:
            self.view.fileViewer.insertTopLevelItem(0, child)

    def removeDirectoryListing(self, item : [FileExplorerItem]):
        # clear current selection
        self.selections = None
        self.view.fileViewer.selectionModel().clearSelection()
        # remove the item from the treeview
        if item.parent():
            item.parent().removeChild(item)


    # signal-response functions
    def fileViewerItemExpanded(self, item):
        threadPool = QThreadPool.globalInstance()
        threadPool.start(DirectoryListingAction(self.client, self.view, self.sDirectoryListingUpdate, self.sClearDirectoryListing, item))

    def fileViewerDeleteButtonClicked(self):
        threadPool = QThreadPool.globalInstance()
        threadPool.start(DirectoryDeletionAction(self.client, self.selections, self.sDirectoryListingUpdate, self.sClearDirectoryListing, self.sRemoveDirectoryListing, self.sInfoBox))

    def fileViewerDownloadButtonClicked(self):
        if self.selections:
            DUController = DUDialogController(self.selections)
            DUView = DUDialog.DownloadDialog(DUController)
            DUModel = DUDialogModel(DUController, self.client)
            # connect the view and the model to the controller
            DUController.set_view(DUView)
            DUController.set_model(DUModel)

            DUController.exec_()

    def fileViewerSelectionChanged(self):
        """
        Responds to the selection (click) of a file in the file explorer.
        Args:
            item: passed by Qt.
        """
        logging.debug("File explorer item changed.")
        self.selections = self.view.fileViewer.selectedItems()