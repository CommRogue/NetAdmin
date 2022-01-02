from PyQt5.QtCore import *
from InspectionWindowController import *
from source.server.InspectionWindowView import FileExplorerItem
import logging
import math
import DUDialog

def bytesToStr(size : int):
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
        return f"{s} {size_name[i]}"
    return size

class DirectoryDeletionAction(QRunnable):
    def __init__(self, client, selection, sUpdate, sClear, sRemove):
        super().__init__()
        self.client = client
        self.selection = selection
        self.sUpdate = sUpdate
        self.sClear = sClear
        self.sRemove = sRemove


    def run(self):
        if self.selection:
            event = self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetDeleteFile, extra=self.selection.path), track_event=True)
            result = event.wait(15)
            if result:
                data = event.get_data()
                if isinstance(data, NetStatus) and data.statusCode == NetStatusTypes.NetOK.value:
                    self.sRemove.emit(self.selection)


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

                strings = [item["name"], date_created, date_modified, bytesToStr(item["size"])]

                # emit a signal to add the item to the treeview.
                # if no parent, then self.itemParent is None and the item will be added to the top level
                # single-line if statement to handle the case where the item is a directory. if so, then set the collapsable argument to true
                self.sUpdate.emit(FileExplorerItem(item["path"], True if item['itemtype'] == NetTypes.NetDirectoryFolderCollapsable.value else False, strings, item["size"], self.itemParent, None), self.itemParent)

class FileExplorerManager(QObject):
    sDirectoryListingUpdate = pyqtSignal(FileExplorerItem, object)  # child, parent
    sClearDirectoryListing = pyqtSignal(FileExplorerItem)  # parent
    sRemoveDirectoryListing = pyqtSignal(FileExplorerItem)  # child

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
        self.view.fileViewer.itemExpanded.connect(self.fileViewerItemExpanded)
        self.view.fileViewer.itemClicked.connect(self.fileViewerItemClicked)
        self.view.deleteButton.clicked.connect(self.fileViewerDeleteButtonClicked)
        self.view.downloadButton.clicked.connect(self.fileViewerDownloadButtonClicked)
        self.selection = None
        self.client = client

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

    def removeDirectoryListing(self, child : FileExplorerItem):
        if child == self.selection:
            self.selection = None
            self.view.fileViewer.selectionModel().clearSelection()
        if child.parent():
            child.parent().removeChild(child)


    # signal-response functions
    def fileViewerItemExpanded(self, item):
        threadPool = QThreadPool.globalInstance()
        threadPool.start(DirectoryListingAction(self.client, self.view, self.sDirectoryListingUpdate, self.sClearDirectoryListing, item))

    def fileViewerDeleteButtonClicked(self):
        threadPool = QThreadPool.globalInstance()
        threadPool.start(DirectoryDeletionAction(self.client, self.selection, self.sDirectoryListingUpdate, self.sClearDirectoryListing, self.sRemoveDirectoryListing))

    def fileViewerDownloadButtonClicked(self):
        if self.selection:
            dialog = DUDialog.DownloadDialog(self.selection)
            dialog.exec_()

    def fileViewerItemClicked(self, item):
        """
        Responds to the selection (click) of a file in the file explorer.
        Args:
            item: passed by Qt.
        """
        logging.debug("File explorer item changed.")
        self.selection = item