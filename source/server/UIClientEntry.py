from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget

class UIClientEntry:
    def __init__(self, client, status, address, identifier, country="N/A", name="N/A", latency="N/A"):
        self.client = client
        self._status_field = QTableWidgetItem(status)
        self._address_field = QTableWidgetItem(address)
        self._uuid_field = QTableWidgetItem(identifier)
        self._country_field = QTableWidgetItem(country)
        self._name_field = QTableWidgetItem(name)
        self._latency_field = QTableWidgetItem(latency)
        self.table = None

    def addToTable(self, table : QTableWidget):
        self.table = table
        rowCount = self.table.rowCount()
        self.table.insertRow(rowCount)
        self.table.setItem(rowCount, 0, self._status_field)
        self.table.setItem(rowCount, 1, self._address_field)
        self.table.setItem(rowCount, 2, self._country_field)
        self.table.setItem(rowCount, 3, self._name_field)
        self.table.setItem(rowCount, 4, self._latency_field)
        self.table.setItem(rowCount, 5, self._uuid_field)

    def removeFromTable(self):
        if self.table is not None:
            self.table.removeRow(self.table.rowCount() - 1)

    def setDisconnected(self):
        self.client = None
        self._status_field.setText("Disconnected")

    def setStatus(self, status):
        newStatus = QTableWidgetItem(status)
        self.table.setItem(self.table.rowCount() - 1, 0, newStatus)
        self._status_field = newStatus

    def setAddress(self, address):
        newAddress = QTableWidgetItem(address)
        self.table.setItem(self.table.rowCount() - 1, 1, newAddress)
        self._address_field = newAddress

    def setCountry(self, country):
        newCountry = QTableWidgetItem(country)
        self.table.setItem(self.table.rowCount() - 1, 2, newCountry)
        self._country_field = newCountry

    def setName(self, name):
        newName = QTableWidgetItem(name)
        self.table.setItem(self.table.rowCount() - 1, 3, newName)
        self._name_field = newName

    def setLatency(self, latency):
        newLatency = QTableWidgetItem(latency)
        self.table.setItem(self.table.rowCount() - 1, 4, newLatency)
        self._latency_field = newLatency

    def setIdentifier(self, identifier):
        newIdentifier = QTableWidgetItem(identifier)
        self.table.setItem(self.table.rowCount() - 1, 5, newIdentifier)
        self._uuid_field = newIdentifier

    def getStatus(self):
        return self._status_field.text()

    def getAddress(self):
        return self._address_field.text()

    def getCountry(self):
        return self._country_field.text()

    def getName(self):
        return self._name_field.text()

    def getLatency(self):
        return self._latency_field.text()