from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QRadioButton
from PyQt5.QtGui import QIcon, QPixmap
from MWindowModel import Client
import resources.qrc_resources

class WidgetGroupParent(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    # TODO - make style nicer by making the first level after widget visible and grayed out while second level and next not visible
    def initialize(self):
        firstElement, elements = self.getTopAndChildrenWidgets()
        for element in elements:
            element.setVisible(False)
        if not isinstance(firstElement, QRadioButton):
            raise Exception("WidgetGroupParent must have a QRadioButton as first child")
        firstElement.toggled.connect(lambda state: self.setChildState(state))

    def getTopAndChildrenWidgets(self):
        children = self.children()
        # starting at 1 to get rid of layout
        return children[1], children[2:]

    def setChildState(self, state):
        _, children = self.getTopAndChildrenWidgets()
        for child in children:
            child.setVisible(state)


class InformationDisplayTable(QTableWidget):
    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent)

    def addEntry(self, key, value,  keyIcon=None, valueIcon=None):
        self.insertRow(self.rowCount())
        if not keyIcon:
            self.setItem(self.rowCount() - 1, 0, QTableWidgetItem(key))
        else:
            self.setItem(self.rowCount() - 1, 0, QTableWidgetItem(keyIcon, key))
        if not valueIcon:
            self.setItem(self.rowCount() - 1, 1, QTableWidgetItem(value))
        else:
            item = QTableWidgetItem(value)
            item.setIcon(valueIcon)
            self.setItem(self.rowCount() - 1, 1, item)

class ClientInformationTable(InformationDisplayTable):
    def __init__(self, parent=None):
        InformationDisplayTable.__init__(self, parent)

    def initializeClient(self, client : Client):
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Key", "Value"])
        self.horizontalHeader().setSelectionMode(QTableWidget.NoSelection)
        self.horizontalHeader().setVisible(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        # jesus christ pls fix ffs
        # country_icon = QIcon(f":flag-{client.geoInformation.COUNTRY_CODE}")
        # b = f":flag-{client.geoInformation.COUNTRY_CODE}"
        # country_icon.addPixmap(QPixmap(), QIcon.Normal, QIcon.Off)
        country_icon = QIcon("C:\\Users\\guyst\\Documents\\NetAdmin\\source\\server\\resources\\images\\flags\\{}.png".format(client.geoInformation.COUNTRY_CODE))
        self.addEntry("Resolved Address", client.geoInformation.REAL_IP)
        self.addEntry("Managed-connection port", str(client.address[1]))
        self.addEntry("Country", client.geoInformation.COUNTRY, valueIcon=country_icon)
        self.addEntry("ISP", client.geoInformation.ISP)
        self.addEntry("Timezone", client.geoInformation.TIMEZONE)