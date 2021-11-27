# Filename: signals_slots.py

"""Signals and slots example."""

import sys
import functools
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import *
import PyQt5
import controller
import model

class CalculatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.layout = QVBoxLayout()
        self._center_widget = QWidget(self)
        self._center_widget.setLayout(self.layout)
        self.setCentralWidget(self._center_widget)
        self.createDisplay()
        self.createButtons()

    def createDisplay(self):
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setContentsMargins(0, 0, 0, 10)
        self.layout.addWidget(self.display)

    def getDisplayText(self):
        return self.display.text()

    def setDisplayText(self, txt):
        self.display.setText(txt)

    def clearDisplay(self):
        self.display.setText("")

    def createButtons(self):
        self.buttons = {}
        buttonLayout = QGridLayout()
        buttons = {'7': (0, 0),
                   '8': (0, 1),
                   '9': (0, 2),
                   '/': (0, 3),
                   'C': (0, 4),
                   '4': (1, 0),
                   '5': (1, 1),
                   '6': (1, 2),
                   '*': (1, 3),
                   '(': (1, 4),
                   '1': (2, 0),
                   '2': (2, 1),
                   '3': (2, 2),
                   '-': (2, 3),
                   ')': (2, 4),
                   '0': (3, 0),
                   '.': (3, 1),
                   '+': (3, 2),
                   '=': (3, 3),
                   'DEL': (3, 4)
                   }
        for btnText, pos in buttons.items():
            self.buttons[btnText] = QPushButton(btnText)
            buttonLayout.addWidget(self.buttons[btnText], *pos)
        self.layout.addLayout(buttonLayout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = CalculatorWindow()
    model = model.CalcModel()
    controller = controller.CalcController(calc, model)
    calc.show()
    sys.exit(app.exec_())