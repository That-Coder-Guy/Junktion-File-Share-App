import PyQt5.QtWidgets as widget
import PyQt5.QtCore as core
import PyQt5.QtGui as gui
import win32ui
import win32gui


def shiftByDelta(color: gui.QColor, delta: int):
    shiftedColor = gui.QColor(max(min(color.red() + delta, 255), 0),
                              max(min(color.green() + delta, 255), 0),
                              max(min(color.blue() + delta, 255), 0))
    return shiftedColor


class DotsPerInch:
    def __init__(self):
        self.dpi = None

    def setScreen(self, screen):
        self.dpi = screen.physicalDotsPerInch() / 140

    def __mul__(self, other):
        return round(other * self.dpi)

    def __rmul__(self, other):
        return round(other * self.dpi)


DPI = DotsPerInch()

# Define Application colors
PRESSED_COLOR_DELTA = -25
SELECTED_COLOR_DELTA = 10

DEFAULT_COLOR = gui.QColor(40, 177, 90)
DEFAULT_COLOR_PRESSED = shiftByDelta(DEFAULT_COLOR, PRESSED_COLOR_DELTA)
DEFAULT_COLOR_SELECTED = shiftByDelta(DEFAULT_COLOR, SELECTED_COLOR_DELTA)

BG_COLOR_1 = gui.QColor(196, 196, 196)  # shiftByDelta(DEFAULT_COLOR, 130)
BG_COLOR_2 = shiftByDelta(DEFAULT_COLOR, 20)

BG_COLOR_3 = gui.QColor(120, 120, 120)
BG_COLOR_4 = shiftByDelta(BG_COLOR_3, 90)
