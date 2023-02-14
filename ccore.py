import PyQt5.QtWidgets as widget
import PyQt5.QtCore as core
import PyQt5.QtGui as gui
import settings
import utilities


class SignInEvent(core.QEvent):
    EventType = core.QEvent.Type(core.QEvent.registerEventType())

    def __init__(self, userToken: int):
        super().__init__(SignInEvent.EventType)
        self.userToken = userToken
