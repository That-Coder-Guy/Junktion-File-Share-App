import PyQt5.QtWidgets as widget
import PyQt5.QtCore as core
import PyQt5.QtGui as gui
import sys
import settings
import mysql.connector as ms
import utilities
import time
import cwidget
import ccore


class FileShareApplication(widget.QWidget):
    def __init__(self):
        super().__init__()
        self.userToken = None

        # Define content


    def setUserToken(self, token: str) -> None:
        self.userToken = token
        self.loadUserData()

    def getUserToken(self) -> str:
        return self.userToken

    def loadUserData(self) -> None:
        pass
