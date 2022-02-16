import functools
import threading
import time
import MWindowModel
import global_windowhooks
from MainWindowView import MainWindow
from MainWindowController import MainWindowController
from MWindowModel import MainWindowModel
from PyQt5.QtWidgets import *
import qtmodern.styles
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import qtmodern.windows
import os
import sys
import pypika

RUNNING = True

def setupAppData():
    """
    Setups the localappdata directory and initializes the database and configuration file in that directory.
    Returns: a tuple of the database clients and the configuration file

    """
    path = os.getenv("LOCALAPPDATA")
    if not os.path.exists(path+"\\NetAdmin"):
        os.makedirs(path+"\\NetAdmin")
    return instantiateDb(path+"\\NetAdmin\\clients.db"), instantiateConfig(path+"\\NetAdmin\\config.ini")

def instantiateConfig(path):
    pass

def instantiateDb(path):
    """
    Instantiates the database and returns the database client.
    Args:
        path: the path to the database file

    Returns: a list of clients found in the database. the list is made up of tuples of the form (client_uuid, client_address)

    """
    returnValue = []

    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName(path)

    #checking we can open the database
    if not con.open():
        QMessageBox.critical(None, "Failed to open database", con.lastError().databaseText())
        sys.exit(1)

    #creating the table if it doesn't exist
    createTable = QSqlQuery()
    createTable.exec_("CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, uuid TEXT, address TEXT)")

    #getting all the clients
    findClients = QSqlQuery()
    findClients.exec_("SELECT uuid, address FROM clients")

    # walking through the clients that were found in the database
    while(findClients.next()):
        print(findClients.value(0), findClients.value(1))

        #appending the clients to the return value. value 0 is the uuid, value 1 is the address
        returnValue.append((findClients.value(0), findClients.value(1)))

    con.close()
    # returning the clients list
    return returnValue

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    import sys
    # create thread on threadCount

    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    databaseClients, config = setupAppData()
    window = MainWindow()

    qtmodern.styles.dark(app)
    mw = qtmodern.windows.ModernWindow(window)

    controller = MainWindowController(window, databaseClients)
    model = MainWindowModel(controller)
    global_windowhooks.init(model, controller)

    mw.show()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(e)

main()