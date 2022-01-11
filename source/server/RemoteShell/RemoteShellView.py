from PyQt5 import QtWidgets

class RemoteShellView(QtWidgets.QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.CommandLineTab = QtWidgets.QWidget()
        self.CommandLineTab.setObjectName("CommandLineTab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.CommandLineTab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.shellTextViewer = QtWidgets.QTextEdit(self.CommandLineTab)
        self.shellTextViewer.setReadOnly(True)
        self.shellTextViewer.setObjectName("shellTextViewer")
        self.verticalLayout_3.addWidget(self.shellTextViewer)
        self.shellInput = QtWidgets.QLineEdit(self.CommandLineTab)
        self.shellInput.setInputMask("")
        self.shellInput.setObjectName("shellInput")
        self.verticalLayout_3.addWidget(self.shellInput)
        self.shellInput.setPlaceholderText("Enter a command...")

    def add_text(self, text):
        self.shellTextViewer.append(text)