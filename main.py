import sys
import time

import PyQt5.QtCore as core
import PyQt5.QtGui as gui
import PyQt5.QtWidgets as widget
import mysql.connector as ms

import ccore
import cwidget
import settings
import utilities
import content


class ApplicationWindow(widget.QMainWindow):
    def __init__(self, app: widget.QApplication):
        super().__init__()
        self.baseApplication = app
        self.screen = self.baseApplication.primaryScreen()
        settings.DPI.setScreen(self.screen)
        self.databaseConnection = None
        self.isExiting = False
        self.userToken = None
        self.threadManager = core.QThreadPool()
        self.disconnectOverlay = cwidget.DisconnectOverlay(self)
        self.disconnectOverlay.move(0, 0)
        self.disconnectOverlay.resize(self.width(), self.height())
        self.disconnectOverlay.hide()

        # Define window
        self.setWindowTitle("Junktion Suite")
        self.setWindowIcon(gui.QIcon("icon.ico"))

        # Main application code
        self.windowContentStackLayout = widget.QStackedLayout()
        self.centralWidget = widget.QWidget()
        self.centralWidget.setLayout(self.windowContentStackLayout)

        # Set the window central widget
        self.setCentralWidget(self.centralWidget)

        # Define login screen
        self.loginBox = cwidget.LoginScreen(self)
        self.windowContentStackLayout.addWidget(self.loginBox)

        # Application placeholder
        self.mainApplication = content.FileShareApplication(self)
        self.windowContentStackLayout.addWidget(self.mainApplication)

        # Set window size and position
        self.setWindowSizeAndPosition()

        # Show window
        self.show()

    def setWindowSizeAndPosition(self) -> None:
        WINDOW_GEOMETRY_PADDING_MULTIPLIER = 1.9
        size = core.QSize(round(self.loginBox.sizeHint().width() * WINDOW_GEOMETRY_PADDING_MULTIPLIER),
                          round(self.loginBox.sizeHint().height() * WINDOW_GEOMETRY_PADDING_MULTIPLIER))
        self.setGeometry(round((self.screen.size().width() - size.width()) / 2),
                         round((self.screen.size().height() - size.height()) / 2),
                         size.width(),
                         size.height())

    def exiting(self) -> bool:
        return self.isExiting

    def exit(self) -> None:
        self.isExiting = False

    def connectToDatabase(self) -> None:
        connected = False
        while not connected:
            if self.exiting() is True:
                return
            if utilities.connectedToInternet():
                try:
                    self.getDatabaseConnection().connect()
                except ms.errors.DatabaseError:
                    utilities.logger.error("Error in connection process")
                    time.sleep(1)
                else:
                    utilities.logger.information("Connection successful")
                    connected = True
            else:
                utilities.logger.warning("No internet connection")
                time.sleep(1)

    def executeDML(self, statement: str):
        executed = False
        result = tuple()
        while not executed:
            if self.exiting() is True:
                return None
            elif utilities.connectedToInternet():
                try:
                    result = self.getDatabaseConnection().query(statement)
                except Exception as exc:
                    result = tuple()
                    utilities.logger.error("An exception occurred while executing "
                                           f"the following SQL DML statement: {statement}")
                    utilities.logger.error(f"Exception: {exc}\n")
                    time.sleep(1)
                else:
                    executed = True
                    if not self.disconnectOverlay.isHidden():
                        self.hideOverlay()
            else:
                if self.disconnectOverlay.isHidden():
                    self.showOverlay()
                self.connectToDatabase()
        return result

    def executeProcedure(self, procedureName: str, args: tuple):
        executed = False
        result = tuple()
        while not executed:
            if self.exiting() is True:
                return None
            elif utilities.connectedToInternet():
                try:
                    result = self.getDatabaseConnection().executeProcedure(name=procedureName, args=args)
                except Exception as exc:
                    result = tuple()
                    utilities.logger.error("An exception occurred while executing "
                                           f"the following SQL stored procedure: CALL {procedureName}{args};")
                    utilities.logger.error(f"Exception: {exc}\n")
                    time.sleep(1)
                else:
                    executed = True
                    if not self.disconnectOverlay.isHidden():
                        self.hideOverlay()
            else:
                if self.disconnectOverlay.isHidden():
                    self.showOverlay()
                self.connectToDatabase()
        return result

    def getDatabaseConnection(self) -> utilities.DatabaseConnection:
        return self.databaseConnection

    def setDatabaseConnection(self, databaseConnection: utilities.DatabaseConnection) -> None:
        self.databaseConnection = databaseConnection

    def closeDatabaseConnection(self) -> None:
        if self.databaseConnection is not None:
            self.databaseConnection.close()

    def showOverlay(self) -> None:
        self.disconnectOverlay.show()
        self.disconnectOverlay.raise_()

    def hideOverlay(self) -> None:
        self.disconnectOverlay.hide()

    def setUserToken(self, token: str) -> None:
        self.userToken = token

    def getUserToken(self) -> str:
        return self.userToken

    def event(self, event) -> bool:
        # Handle ccore.SignInEvent
        if event.type() == ccore.SignInEvent.EventType:
            self.setUserToken(token=event.userToken)
            self.windowContentStackLayout.setCurrentIndex(1)
            self.loginBox.setParent(None)
            self.mainApplication.setUserToken(token=self.getUserToken())
            return True
        return super().event(event)

    def resizeEvent(self, event: gui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self.disconnectOverlay.move(0, 0)
        self.disconnectOverlay.resize(self.width(), self.height())

    def closeEvent(self, event: gui.QCloseEvent) -> None:
        self.exit()
        self.closeDatabaseConnection()
        for descendant in self.findChildren(widget.QWidget):
            # Note: Should work fine on all descendants that are QWidgets
            descendant.close()
        self.threadManager.waitForDone()
        event.accept()


def exceptionHandler(exceptionType, value, traceback) -> None:
    # Raise the exception
    raise exceptionType


if __name__ == "__main__":
    application = widget.QApplication(sys.argv)
    sys.excepthook = exceptionHandler
    window = ApplicationWindow(app=application)
    application.exec()
