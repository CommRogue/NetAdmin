from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QIcon, QPixmap
from MainWindowModel import Client

class InformationDisplayTable(QTableWidget):
    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Key", "Value"])
        self.horizontalHeader().setSelectionMode(QTableWidget.NoSelection)
        self.horizontalHeader().setVisible(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def addEntry(self, key, value,  keyIcon=None, valueIcon=None):
        self.insertRow(self.rowCount())
        if not keyIcon:
            self.setItem(self.rowCount() - 1, 0, QTableWidgetItem(key))
        else:
            self.setItem(self.rowCount() - 1, 0, QTableWidgetItem(keyIcon, key))
        if not valueIcon:
            self.setItem(self.rowCount() - 1, 1, QTableWidgetItem(value))
        else:
            self.setItem(self.rowCount() - 1, 1, QTableWidgetItem(valueIcon, value))

class ClientInformationTable(InformationDisplayTable):
    def __init__(self, parent=None):
        InformationDisplayTable.__init__(self, parent)

    def initializeClient(self, client : Client):
        country_icon = QIcon()
        country_icon.addPixmap(QPixmap(f":flag-{client.geoInformation.COUNTRY_CODE}"), QIcon.Normal, QIcon.Off)
        self.clear()
        self.addEntry("Resolved Address", client.geoInformation.REAL_IP)
        self.addEntry("Managed-connection port", client.address[1])

        self.addEntry("Country", client.geoInformation.COUNTRY, valueIcon=country_icon)