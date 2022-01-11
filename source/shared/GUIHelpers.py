from PyQt5.QtWidgets import QMessageBox
import logging

def infobox(title, text):
    logging.info("GUI: InfoBox: " + text)
    dialog = QMessageBox()
    dialog.setText(text)
    dialog.setWindowTitle(title)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec_()