from MainWindowView import MainWindow
from MainWindowController import MainWindowController
from MainWindowModel import MainWindowModel
from PyQt5.QtWidgets import *
import qtmodern.styles
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import qtmodern.windows
import os
import sys
import pypika

def setupAppData():
    path = os.getenv("LOCALAPPDATA")
    if not os.path.exists(path+"\\NetAdmin"):
        os.makedirs(path+"\\NetAdmin")
    return instantiateDb(path+"\\NetAdmin\\clients.db"), instantiateConfig(path+"\\NetAdmin\\config.ini")

def instantiateConfig(path):
    pass

def instantiateDb(path):
    returnValue = []
    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName(path)
    if not con.open():
        QMessageBox.critical(None, "Failed to open database", con.lastError().databaseText())
        sys.exit(1)
    createTable = QSqlQuery()
    createTable.exec_("CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, uuid TEXT, address TEXT)")
    findClients = QSqlQuery()
    findClients.exec_("SELECT uuid, address FROM clients")
    while(findClients.next()):
        print(findClients.value(0), findClients.value(1))
        returnValue.append((findClients.value(0), findClients.value(1)))
    con.close()
    return returnValue


def main():
    app = QApplication(sys.argv)
    databaseClients, config = setupAppData()
    window = MainWindow()
    qtmodern.styles.dark(app)
    mw = qtmodern.windows.ModernWindow(window)
    controller = MainWindowController(window, databaseClients)
    model = MainWindowModel(controller)
    mw.show()
    sys.exit(app.exec_())

main()