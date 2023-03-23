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
    def __init__(self, parent: widget.QWidget):
        super().__init__(parent)
        self.userToken = None
        self.username = None

        # Set titlebar/content layout
        self.contentLayout = widget.QVBoxLayout(self)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(0)
        self.contentLayout.setAlignment(core.Qt.AlignTop)
        self.setLayout(self.contentLayout)

        # Titlebar
        self.titleBar = cwidget.TitleBar(self)
        self.contentLayout.addWidget(self.titleBar)

        # Navigation bar
        self.navigationBar = cwidget.NavigationBar(self)
        self.contentLayout.addWidget(self.navigationBar)

    def setUserToken(self, token: str) -> None:
        self.loadContent()

    def loadContent(self) -> None:
        self.loadUserData()
        self.setMinimumSize(700, 500)

    def loadUserData(self) -> None:
        pass
