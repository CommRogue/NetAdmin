from PyQt5 import QtWidgets, QtGui


class RemoteShellView(QtWidgets.QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("ShellWindow")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.shellTextViewer = QtWidgets.QTextEdit(self)
        self.shellTextViewer.setReadOnly(True)
        self.shellTextViewer.setObjectName("shellTextViewer")
        self.verticalLayout_12.addWidget(self.shellTextViewer)
        self.shellInput = QtWidgets.QLineEdit(self)
        self.shellInput.setInputMask("")
        self.shellInput.setObjectName("shellInput")
        self.verticalLayout_12.addWidget(self.shellInput)
        self.shellInput.setPlaceholderText("Enter a command...")

    def add_text(self, text):
        self.shellTextViewer.append(text)

    def delete_line(self):
        cursor = self.shellTextViewer.textCursor()
        # select last line
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        self.shellTextViewer.setTextCursor(cursor)