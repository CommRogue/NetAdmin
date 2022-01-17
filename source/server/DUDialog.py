from PyQt5 import QtCore, QtGui, QtWidgets


class DownloadDialog(QtWidgets.QDialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setupUi(self)
        self.custom()

    def update_progress_bar(self, value):
        self.downloadProgressBar.setValue(int(value))

    def custom(self):
        b1 = self.buttonBox.addButton("Start Download", QtWidgets.QDialogButtonBox.YesRole)
        b1.clicked.connect(self.controller.on_downloadbutton_clicked)
        b2 = self.buttonBox.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        b2.clicked.connect(self.controller.closeButtonClicked)
        self.chooseDirectoryButton.clicked.connect(self.controller.choose_locationClicked)
        # self.remoteDirectoryText.setText(self.fileExplorerItem.path)
        # self.downloadLocationText.setText(self.localDownloadDirectory)
        # self.fileSizeText.setText(self.fileExplorerItem.sizeStr)
        # self.downloadTimeText.setText(f"{round(self.fileExplorerItem.size/2500000, 2)}s")

    def setupUi(self, DownloadDialog):
        DownloadDialog.setObjectName("DownloadDialog")
        DownloadDialog.resize(480, 343)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DownloadDialog.sizePolicy().hasHeightForWidth())
        DownloadDialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(DownloadDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_3 = QtWidgets.QLabel(DownloadDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.line = QtWidgets.QFrame(DownloadDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setLineWidth(2)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(DownloadDialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.remoteDirectoryText = QtWidgets.QLineEdit(DownloadDialog)
        self.remoteDirectoryText.setReadOnly(True)
        self.remoteDirectoryText.setObjectName("remoteDirectoryText")
        self.horizontalLayout_2.addWidget(self.remoteDirectoryText)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(DownloadDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.downloadLocationText = QtWidgets.QLineEdit(DownloadDialog)
        self.downloadLocationText.setReadOnly(True)
        self.downloadLocationText.setObjectName("downloadLocationText")
        self.horizontalLayout.addWidget(self.downloadLocationText)
        self.chooseDirectoryButton = QtWidgets.QToolButton(DownloadDialog)
        self.chooseDirectoryButton.setObjectName("chooseDirectoryButton")
        self.horizontalLayout.addWidget(self.chooseDirectoryButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.fileSizeLabel = QtWidgets.QLabel(DownloadDialog)
        self.fileSizeLabel.setObjectName("fileSizeLabel")
        self.horizontalLayout_3.addWidget(self.fileSizeLabel)
        self.fileSizeText = QtWidgets.QLineEdit(DownloadDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileSizeText.sizePolicy().hasHeightForWidth())
        self.fileSizeText.setSizePolicy(sizePolicy)
        self.fileSizeText.setReadOnly(True)
        self.fileSizeText.setObjectName("fileSizeText")
        self.horizontalLayout_3.addWidget(self.fileSizeText)
        self.downloadTimeLabel = QtWidgets.QLabel(DownloadDialog)
        self.downloadTimeLabel.setObjectName("downloadTimeLabel")
        self.horizontalLayout_3.addWidget(self.downloadTimeLabel)
        self.downloadTimeText = QtWidgets.QLineEdit(DownloadDialog)
        self.downloadTimeText.setReadOnly(True)
        self.downloadTimeText.setObjectName("downloadTimeText")
        self.horizontalLayout_3.addWidget(self.downloadTimeText)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.downloadProgressBar = QtWidgets.QProgressBar(DownloadDialog)
        self.downloadProgressBar.setProperty("value", 0)
        self.downloadProgressBar.setObjectName("downloadProgressBar")
        self.verticalLayout.addWidget(self.downloadProgressBar)
        self.buttonBox = QtWidgets.QDialogButtonBox(DownloadDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.NoButton)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DownloadDialog)
        QtCore.QMetaObject.connectSlotsByName(DownloadDialog)

    def retranslateUi(self, DownloadDialog):
        _translate = QtCore.QCoreApplication.translate
        DownloadDialog.setWindowTitle(_translate("DownloadDialog", "Download File...."))
        self.label_3.setText(_translate("DownloadDialog",
                                        "<html><head/><body><p><span style=\" font-size:14pt; font-weight:600;\">Download Item/s</span></p></body></html>"))
        self.label_2.setText(_translate("DownloadDialog", "Remote file or directory to download"))
        self.label.setText(_translate("DownloadDialog", "Location to download to"))
        self.chooseDirectoryButton.setText(_translate("DownloadDialog", "..."))
        self.fileSizeLabel.setText(_translate("DownloadDialog", "File size: "))
        self.downloadTimeLabel.setText(_translate("DownloadDialog", "Estimated time to download (20 mb/s):"))