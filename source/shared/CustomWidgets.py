from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QRadioButton, QApplication
from PyQt5.QtGui import QIcon

import GUIHelpers
import MWindowModel
from MWindowModel import Client
from PyQt5 import QtCore, QtWidgets, QtGui
import OpenConnectionHelpers

class UPnPVerify(QWidget):
    """
    Widget with button to verify UPnP is enabled.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.retranslateUi(self)
        self.verifyButton.clicked.connect(self.verify)
        self.setVerifiedView(MWindowModel.UPNP_STATUS)

    @staticmethod
    def verify_upnp_with_messagebox():
        """
        Calls verify_upnp() along with a messagebox alerting the user of it.
        """
        msgbox = GUIHelpers.getinfobox("Port Forwarding", "Port Forwarding.... This may take some time....")
        msgbox.show()
        # make sure the msgbox is fully rendered
        QApplication.instance().processEvents()

        upnp_status, err = OpenConnectionHelpers.verify_upnp()
        if not upnp_status:
            GUIHelpers.infobox("UPnP Port Forwarding Error", err)
        return upnp_status, err

    def verify(self):
        """
        Verify UPnP is enabled.
        """
        upnp_status, err = self.verify_upnp_with_messagebox()
        if upnp_status:
            self.setVerifiedView(True)
        else:
            self.setVerifiedView(False)

    def setVerifiedView(self, state):
        if state:
            self.verifyIcon.setPixmap(QtGui.QPixmap(":/checkmark"))
            self.verifyLabel.setText("Verified!")
        else:
            self.verifyIcon.setPixmap(QtGui.QPixmap(":/xmark"))
            self.verifyLabel.setText("Not Verified")

    def setupUi(self, Form):
        Form.setObjectName("Form")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verifyButton = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verifyButton.sizePolicy().hasHeightForWidth())
        self.verifyButton.setSizePolicy(sizePolicy)
        self.verifyButton.setObjectName("verifyButton")
        self.horizontalLayout.addWidget(self.verifyButton)
        self.verifyIcon = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verifyIcon.sizePolicy().hasHeightForWidth())
        self.verifyIcon.setSizePolicy(sizePolicy)
        self.verifyIcon.setMinimumSize(QtCore.QSize(0, 0))
        self.verifyIcon.setMaximumSize(QtCore.QSize(20, 20))
        self.verifyIcon.setText("")
        self.verifyIcon.setPixmap(QtGui.QPixmap(":/xmark"))
        self.verifyIcon.setScaledContents(True)
        self.verifyIcon.setObjectName("verifyIcon")
        self.horizontalLayout.addWidget(self.verifyIcon)
        self.verifyLabel = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verifyLabel.sizePolicy().hasHeightForWidth())
        self.verifyLabel.setSizePolicy(sizePolicy)
        self.verifyLabel.setObjectName("verifyLabel")
        self.horizontalLayout.addWidget(self.verifyLabel)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.verifyButton.setText(_translate("Form", "Verify Port Forwarding Status (UPnP)"))
        self.verifyLabel.setText(_translate("Form", "Not Verified"))


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