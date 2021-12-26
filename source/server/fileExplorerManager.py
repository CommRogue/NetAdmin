from PyQt5.QtCore import *
from InspectionWindowController import *
from source.server.InspectionWindowView import FileExplorerItem
import logging

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
            self.sUpdate.emit(FileExplorerItem("Loading...", "", False, None, None), self.itemParent)
        else: #if directory is the drives (root)
            #self.view.fileViewer.insertTopLevelItem(0, QTreeWidgetItem(["Loading..."]))
            path = "" #set the path to none to get root directory listing
        event = self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetDirectoryListing, id=None, extra=path), track_event=True)
        event.wait()
        data = event.get_data()

        if self.itemParent:  # if a directory, then clear the "Loading..." item or the previous items from the last click
            self.sClear.emit(self.itemParent)

        if type(data) is NetStatus and data.statusCode == NetStatusTypes.NetDirectoryAccessDenied.value:
            self.sUpdate.emit(FileExplorerItem("Access is denied to this directory", "", False, None, NetErrorStyling), self.itemParent) #will send itemParent as none if there is no parent
        else:
            for item in data.items:
                if self.itemParent: #if must connect as a child to another item in the tree view
                    if item['itemtype'] == NetTypes.NetDirectoryFolderCollapsable.value:
                        collapsable = True
                    else:
                        collapsable = False
                    self.sUpdate.emit(FileExplorerItem(item["name"], item["path"], collapsable, None, None), self.itemParent)
                else:
                    self.sUpdate.emit(FileExplorerItem(item["name"], item["path"], True, None, None), None)

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

    def fileViewerItemClicked(self, item):
        """
        Responds to the selection (click) of a file in the file explorer.
        Args:
            item: passed by Qt.
        """
        logging.debug("File explorer item changed.")
        self.selection = item