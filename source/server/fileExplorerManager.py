from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QPushButton, QMenu

import GUIHelpers
import InspectionWindowView
from DUDialogController import DUDialogController
from DUDialogModel import DUDialogModel
from InspectionWindowController import *
from source.server.InspectionWindowView import FileExplorerItem
import logging
import math
import DUDialog

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
        start = datetime.datetime.now()
        event = self.client.send_message(NetMessage(NetTypes.NetRequest, NetTypes.NetDirectoryListing, extra=path), track_event=True)
        event.wait()
        data = event.get_data()
        print(f"Total : {datetime.datetime.now() - start}")
        start = datetime.datetime.now()
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


                # emit a signal to add the item to the treeview.
                # if no parent, then self.itemParent is None and the item will be added to the top level
                # single-line if statement to handle the case where the item is a directory. if so, then set the collapsable argument to true
                self.sUpdate.emit(FileExplorerItem(item["path"], True if item['itemtype'] == NetTypes.NetDirectoryFolderCollapsable.value else False, strings, item["size"], self.itemParent, None, readable=item['readable']), self.itemParent)
        self.view.update()
        print(f"Total 2: {datetime.datetime.now() - start}")

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
    sCalculateSizeSignal = pyqtSignal()

    def clearItemChildren(self, item):
        while (item.childCount() > 0):
            child = item.child(0)
            item.removeChild(child)
            del child

    def __init__(self, client, view):
        super().__init__()
        self.view = view
        self.calculatingSize = False
        self.fileExplorerInitialized = False
        self.sClearDirectoryListing.connect(self.clearDirectoryListing)
        self.sDirectoryListingUpdate.connect(self.updateDirectoryListing)
        self.sRemoveDirectoryListing.connect(self.removeDirectoryListing)
        self.sInfoBox.connect(self.infoBox)
        self.view.fileViewer.itemExpanded.connect(self.fileViewerItemExpanded)
        self.view.fileViewer.itemSelectionChanged.connect(self.fileViewerSelectionChanged)
        self.view.deleteButton.clicked.connect(self.fileViewerDeleteButtonClicked)
        self.view.downloadButton.clicked.connect(self.fileViewerDownloadButtonClicked)
        self.view.fileViewer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.fileViewer.customContextMenuRequested.connect(self.customContextMenuRequested)
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

    @pyqtSlot(FileExplorerItem)
    def clearDirectoryListing(self, parent : FileExplorerItem):
        self.clearItemChildren(parent)

    def customContextMenuRequested(self, pos : QPoint):
        item = self.view.fileViewer.itemAt(pos)
        if item:
            if item.showContextMenu == True:
                menu = QMenu("Item Actions", self.view.fileViewer)
                menu.addAction("Calculate size...", functools.partial(self.calculateSizeButtonClicked, item))
                menu.exec(self.view.fileViewer.viewport().mapToGlobal(pos))

    @pyqtSlot(FileExplorerItem, FileExplorerItem)
    def updateDirectoryListing(self, child : FileExplorerItem, parent: FileExplorerItem):
        if parent:
            parent.insertChild(0, child)
        else:
            self.view.fileViewer.insertTopLevelItem(0, child)

    @staticmethod
    def get_subtree_nodes(tree_widget_item):
        """Returns all QTreeWidgetItems in the subtree rooted at the given node."""
        nodes = []
        nodes.append(tree_widget_item)
        for i in range(tree_widget_item.childCount()):
            nodes.extend(FileExplorerManager.get_subtree_nodes(tree_widget_item.child(i)))
        return nodes

    @staticmethod
    def get_all_items(tree_widget):
        """Returns all QTreeWidgetItems in the given QTreeWidget."""
        all_items = []
        for i in range(tree_widget.topLevelItemCount()):
            top_item = tree_widget.topLevelItem(i)
            all_items.extend(FileExplorerManager.get_subtree_nodes(top_item))
        return all_items

    def removeWidgetButton(self, item, col):
        self.view.fileViewer.removeItemWidget(item, col)
        items = self.get_all_items(self.view.fileViewer)
        for i in items:
            widget = self.view.fileViewer.itemWidget(i, col)
            if widget:
                i.setSizeHint(3, widget.sizeHint())
        self.view.fileViewer.updateGeometries()

    @staticmethod
    def redrawItemSize(item : QTreeWidgetItem, col) -> None:
        item.setData(col, QtCore.Qt.ForegroundRole, None)
        item.setText(col, InspectionWindowView.bytesToStr(item.size))

    def _calculateSizeGenerator(self, item, signal):
        print(threading.current_thread().name)
        loadingView = GUIHelpers.sizeLoadingBox(item.path)
        thread = threading.Thread(target=getActualDirectorySize, args=(self.client, item, signal))
        thread.start()
        yield
        # no need anymore since no buttons
        # self.removeWidgetButton(item, 3)

        # reset colors of size text
        self.redrawItemSize(item, 3)
        loadingView.hide()
        # reset callback signal and calculatesize bool enabler
        try:
            signal.disconnect()
        except:
            print("Failed to disconnect getActualDirectorySize signal...")
        self.calculatingSize = False
        # don't show calculate size context menu item anymore
        item.showContextMenu = False
        yield

    def calculateSizeButtonClicked(self, item):
        if not self.calculatingSize: # if not already calculating
            self.calculatingSize = True
            # create generator
            self._execObj = self._calculateSizeGenerator(item, self.sCalculateSizeSignal)
            # create callback to next function of generator
            funcObj = functools.partial(next, self._execObj)
            # connect the exec signal to the callback
            self.sCalculateSizeSignal.connect(funcObj)
            # start the generator
            next(self._execObj)
        else:
            self.infoBox("Already calculating", "Please wait until the current size calculation is finished.")

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

    @staticmethod
    def checkDownloadable(fileExplorerItems):
        sum = 0
        for item in fileExplorerItems:
            if not item.readable:
                sum += 1
        return sum

    def fileViewerDownloadButtonClicked(self):
        if self.selections:
            not_downloadable = self.checkDownloadable(self.selections)
            # check if all selections are downloadable
            if not_downloadable == 0:
                DUController = DUDialogController(self.selections)
                DUView = DUDialog.DownloadDialog(DUController)
                DUModel = DUDialogModel(DUController, self.client)
                # connect the view and the model to the controller
                DUController.set_view(DUView)
                DUController.set_model(DUModel)

                DUController.exec_()
            else:  # if some selections are not downloadable, show an error message
                GUIHelpers.infobox("Download Unavailable",
                                   f"{not_downloadable} of the {len(self.selections)} selected items are not downloadable. This may have occured because: "
                                   f"\n1. An item selected was a folder that its children were inaccessible. Note that folders that are readable but have children that are inaccessible, will be downloaded excluding their inaccessible children. "
                                   f"\n2. An item selected was a file that was unreadable. ")

    def fileViewerSelectionChanged(self):
            """
            Responds to the selection (click) of a file in the file explorer.
            Args:
                item: passed by Qt.
            """
            logging.debug("File explorer item changed.")
            self.selections = self.view.fileViewer.selectedItems()