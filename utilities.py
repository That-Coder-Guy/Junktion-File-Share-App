import PyQt5.QtWidgets as widget
import PyQt5.QtCore as core
import PyQt5.QtGui as gui
import sys
import math
import settings
from PIL import Image
import time
import mysql.connector as ms
import requests


def centerWidget(target: widget.QWidget):
    frame = widget.QFrame()
    centerLayout = widget.QVBoxLayout()
    centerLayout.setAlignment(core.Qt.AlignCenter)
    frame.setLayout(centerLayout)
    centerLayout.addWidget(target)
    return frame


def connectedToInternet():
    try:
        requests.get('http://google.com', timeout=1)
        return True
    except requests.ConnectionError:
        return False
    except requests.exceptions.ReadTimeout:
        return False


class DatabaseConnection:
    def __init__(self):
        self.database = None
        self.curser = None

    def connect(self) -> None:
        self.database = ms.connect(
            host="junktion-studios-database.crgexdef5bck.us-east-2.rds.amazonaws.com",
            user="user",
            port="3306",
            password="o4)d2&1@")
        self.curser = self.database.cursor()

    def reconnect(self) -> None:
        self.database.reconnect(attempts=1, delay=0)
        self.curser = self.database.cursor()

    def close(self) -> None:
        if self.database is not None and self.curser is not None:
            self.curser.close()
            self.database.close()
        else:
            raise Exception("No database connection")

    def execute(self, command: str) -> None:
        if self.database is not None and self.curser is not None:
            self.curser.execute(command)
        else:
            raise Exception("No database connection")

    def query(self, command: str) -> tuple:
        if self.database is not None and self.curser is not None:
            self.curser.execute(command)
            data = self.curser.fetchall()
            if not data:
                return tuple()
            elif data:
                return data[0]
        else:
            raise Exception("No database connection")

    def executeProcedure(self, name: str, args: tuple) -> tuple:
        if self.database is not None and self.curser is not None:
            self.curser.callproc(procname=name, args=args)
            return tuple([result.fetchall() for result in self.curser.stored_results()])
        else:
            raise Exception("No database connection")


class Logging:
    def __init__(self):
        self.show_debug = True
        self.show_information = True
        self.show_warning = True
        self.show_error = True

    def debug(self, message) -> None:
        if self.show_information:
            print(f"\033[36m{message}\033[0m")

    def information(self, message) -> None:
        if self.show_information:
            print(f"\033[32m{message}\033[0m")

    def warning(self, message) -> None:
        if self.show_warning:
            print(f"\033[33m{message}\033[0m")

    def error(self, message) -> None:
        if self.show_error:
            print(f"\033[31m{message}\033[0m")


logger = Logging()
