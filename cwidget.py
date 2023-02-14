import PyQt5.QtWidgets as widget
import PyQt5.QtCore as core
import PyQt5.QtGui as gui
from PIL import Image
import io
import sys
import math
import time
import settings
import utilities
import ccore


class LoginScreen(widget.QFrame):
    def __init__(self, parent: widget.QWidget):
        # Call constructor of parent class
        super().__init__(parent)
        self.databaseConnection = None

        # Set login screen background to gradient
        self.setAttribute(core.Qt.WA_StyledBackground, True)
        self.loginScreenBackgroundPalette = gui.QPalette()
        self.setAutoFillBackground(True)
        self.drawBackground()

        # Add a box layout on top of the login screen frame to hold the login box
        self.loginScreenLayout = widget.QStackedLayout()
        self.loginScreenLayout.setAlignment(core.Qt.AlignCenter)
        self.setLayout(self.loginScreenLayout)

        # Define loading screen
        self.loadingScreen = self.LoadingScreen(self, self.postLoadingProcess)
        self.loginScreenLayout.addWidget(utilities.centerWidget(self.loadingScreen))
        self.loadingScreen.start()

        # Define the login container
        self.loginContainer = self.Container()

        # Add loading-screen/login-screen frame to login screen layout
        self.loginScreenLayout.addWidget(utilities.centerWidget(self.loginContainer))

        # Add a page layout on top of the login box to hold the sign-in and create account pages
        self.pageLayout = widget.QStackedLayout()
        self.pageLayout.setAlignment(core.Qt.AlignCenter)
        self.loginContainer.setLayout(self.pageLayout)

        # Define the sign-in page
        self.signInPage = widget.QWidget()
        self.signInPageLayout = widget.QVBoxLayout()

        self.signInLabel = self.Label(text="Sign In")
        self.signInLabel.setAlignment(core.Qt.AlignCenter)
        self.signInPageLayout.addWidget(self.signInLabel, 1)

        self.signInFeedbackLabel = self.ErrorLabel(self.signInPage)
        self.signInFeedbackLabel.setAlignment(core.Qt.AlignCenter)

        self.usernameEntry = self.TextEntry(placeholder="Username")
        self.usernameEntry.setMaxLength(40)
        self.signInPageLayout.addWidget(self.usernameEntry, 2)

        self.passwordEntry = self.TextEntry(placeholder="Password")
        self.passwordEntry.setMaxLength(40)
        self.passwordEntry.setEchoMode(widget.QLineEdit.Password)
        self.signInPageLayout.addWidget(self.passwordEntry, 3)

        self.signInButton = self.Button(text="Continue")
        self.signInButton.clicked.connect(self.signIn)
        self.signInPageLayout.addWidget(self.signInButton, 4)

        self.createAccountButton = self.LinkButton(text="Create Account")
        self.createAccountButton.clicked.connect(self.togglePage)
        self.signInPageLayout.addWidget(self.createAccountButton, 5)

        self.signInPage.setLayout(self.signInPageLayout)

        # Define the create account page
        self.createAccountPage = widget.QWidget()
        self.createAccountPageLayout = widget.QVBoxLayout()

        self.createLabel = self.Label(text="Create Account")
        self.createLabel.setAlignment(core.Qt.AlignCenter)
        self.createAccountPageLayout.addWidget(self.createLabel, 1)

        self.createAccountFeedbackLabel = self.ErrorLabel(self.createAccountPage)
        self.createAccountFeedbackLabel.setAlignment(core.Qt.AlignCenter)

        self.newUsernameEntry = self.TextEntry(placeholder="Username")
        self.newUsernameEntry.setMaxLength(40)
        self.createAccountPageLayout.addWidget(self.newUsernameEntry, 2)

        self.newPasswordEntry = self.TextEntry(placeholder="Password")
        self.newPasswordEntry.setMaxLength(40)
        self.newPasswordEntry.setEchoMode(widget.QLineEdit.Password)
        self.createAccountPageLayout.addWidget(self.newPasswordEntry, 3)

        self.createButton = self.Button(text="Register")
        self.createButton.clicked.connect(self.register)
        self.createAccountPageLayout.addWidget(self.createButton, 4)

        self.backToSignInButton = self.LinkButton(text="Sign In")
        self.backToSignInButton.clicked.connect(self.togglePage)
        self.createAccountPageLayout.addWidget(self.backToSignInButton, 5)

        self.createAccountPage.setLayout(self.createAccountPageLayout)

        # Add both pages to the stack layout
        self.pageLayout.addWidget(self.signInPage)
        self.pageLayout.addWidget(self.createAccountPage)

        # Set fixed size for login container
        self.loginContainer.setFixedSize(self.loginContainer.sizeHint())

    def signIn(self) -> None:
        self.window().threadManager.start(self.signInUser)

    def signInUser(self) -> None:
        self.loginContainer.setDisabled(True)
        username = self.usernameEntry.text()
        password = self.passwordEntry.text()

        # Check for username and password validity
        fullUsername = True if username != "" else False
        fullPassword = True if password != "" else False

        if fullUsername and fullPassword:
            self.window().executeDML("LOCK TABLES users.user WRITE;")
            results = self.window().executeProcedure(procedureName="users.login_user", args=(username, password))
            self.window().executeDML("UNLOCK TABLES;")
            userExists = True if results[0][0][0] is not None else False
        else:
            userExists = True

        if fullUsername and fullPassword and userExists:
            userToken = results[0][0][0]
            event = ccore.SignInEvent(userToken)
            core.QCoreApplication.postEvent(self.window(), event)
            utilities.logger.information("Sign-In successful")
        else:
            if fullUsername is False and fullPassword is False:
                self.displaySignInFeedback("Username and password fields are empty", False)
            elif fullUsername is False:
                self.displaySignInFeedback("Username field empty", False)
            elif fullPassword is False:
                self.displaySignInFeedback("Password field empty", False)
            elif userExists is False:
                self.displaySignInFeedback("Invalid username or password", False)
        self.loginContainer.setDisabled(False)

    def displaySignInFeedback(self, feedback: str, success: bool) -> None:
        self.signInFeedbackLabel.setFeedback(feedback, success)
        if self.signInFeedbackLabel.isInserted() is False:
            self.signInFeedbackLabel.insert()

    def clearSignInFeedback(self) -> None:
        if self.signInFeedbackLabel.isInserted() is True:
            self.signInFeedbackLabel.remove()

    def register(self) -> None:
        self.window().threadManager.start(self.registerUser)

    def registerUser(self) -> None:
        self.loginContainer.setDisabled(True)
        username = self.newUsernameEntry.text()
        password = self.newPasswordEntry.text()

        # Check for username and password validity
        fullUsername = True if username != "" else False
        fullPassword = True if password != "" else False

        if fullUsername and fullPassword:
            self.window().executeDML("LOCK TABLES users.user WRITE;")
            results = self.window().executeProcedure(procedureName="users.check_users", args=(username,))
            self.window().executeDML("UNLOCK TABLES;")
            uniqueUsername = True if len(results[0]) == 0 else False
        else:
            uniqueUsername = True

        # Add user if username and password are valid
        if fullUsername and fullPassword and uniqueUsername:
            # Database insert command
            self.window().executeDML("LOCK TABLES users.user WRITE;")
            self.window().executeProcedure(procedureName="users.add_user", args=(username, password))
            self.window().executeDML("UNLOCK TABLES;")
            self.newUsernameEntry.clear()
            self.newPasswordEntry.clear()
            self.displayCreateAccountFeedback("Account registered", True)
            utilities.logger.information("Account registered successfully")

        else:
            if fullUsername is False and fullPassword is False:
                self.displayCreateAccountFeedback("Username and password fields are empty", False)
            elif fullUsername is False:
                self.displayCreateAccountFeedback("Username field empty", False)
            elif fullPassword is False:
                self.displayCreateAccountFeedback("Password field empty", False)
            elif uniqueUsername is False:
                self.displayCreateAccountFeedback("Username is already taken", False)

        self.loginContainer.setDisabled(False)

    def displayCreateAccountFeedback(self, feedback: str, success: bool) -> None:
        self.createAccountFeedbackLabel.setFeedback(feedback, success)
        if self.createAccountFeedbackLabel.isInserted() is False:
            self.createAccountFeedbackLabel.insert()

    def clearCreateAccountFeedback(self) -> None:
        if self.createAccountFeedbackLabel.isInserted() is True:
            self.createAccountFeedbackLabel.remove()

    def postLoadingProcess(self) -> None:
        self.loginScreenLayout.setCurrentIndex(1)

    def drawBackground(self):
        gradient = gui.QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.1, settings.BG_COLOR_1)
        gradient.setColorAt(1.0, settings.BG_COLOR_2)
        self.loginScreenBackgroundPalette.setBrush(self.backgroundRole(), gradient)
        self.setPalette(self.loginScreenBackgroundPalette)

    def resizeEvent(self, event: gui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self.drawBackground()

    def togglePage(self) -> None:
        if self.pageLayout.currentIndex() == 0:
            self.pageLayout.setCurrentIndex(1)
            self.clearSignInFeedback()
            self.usernameEntry.clear()
            self.passwordEntry.clear()
            self.newUsernameEntry.setFocus()
        else:
            self.pageLayout.setCurrentIndex(0)
            self.clearCreateAccountFeedback()
            self.newUsernameEntry.clear()
            self.newPasswordEntry.clear()
            self.usernameEntry.setFocus()

    class LoadingScreen(widget.QLabel):
        def __init__(self, parent: widget.QWidget, target: callable):
            super().__init__(parent)
            self.postLoadingFunction = target

            self.setAttribute(core.Qt.WA_StyledBackground, True)
            name = str(self)[str(self).rindex(" ") + 1:-1]
            self.setObjectName(name)
            self.setStyleSheet(f"QWidget#{name}"
                               "{"
                               f"border-radius: {15 * settings.DPI}px;"
                               f"background-color: rgba{(255, 255, 255, 120)};"
                               "}")
            self.size = core.QSize(180 * settings.DPI, 180 * settings.DPI)

            # Define logo image
            self.logoImage = PixmapImage(filename="Icon.png")

            # Define pixel map canvas
            self.canvas = gui.QPixmap(self.size)
            self.canvas.fill(core.Qt.transparent)
            self.setPixmap(self.canvas)

            # Define animation painter
            self.painter = gui.QPainter(self.canvas)
            self.painter.setBackground(core.Qt.transparent)
            self.painter.setBackgroundMode(core.Qt.OpaqueMode)

            # Define animation pen from painter
            self.pen = self.painter.pen()
            self.pen.setWidth(6 * settings.DPI)
            self.pen.setColor(settings.DEFAULT_COLOR)
            self.painter.setPen(self.pen)

            # Define animation loop
            # FIXME: Determine why the duration parameter is unexpected
            self.animation = core.QVariantAnimation(duration=1500)
            self.animation.setLoopCount(-1)
            self.animation.setStartValue(0)
            self.animation.setEndValue(360)
            self.animation.valueChanged.connect(self.updateAnimation)

            # Define animation element positions
            self.animationShift = (0 * settings.DPI, 18 * settings.DPI)
            self.arcDimensions = (140 * settings.DPI, 40 * settings.DPI)
            self.arcLength = (16 * 90) * settings.DPI
            self.separationDelta = 30 * settings.DPI
            self.arcPosition = (round(self.canvas.height() / 2 - (self.arcDimensions[0] / 2)),
                                round(self.canvas.width() / 2 - (self.arcDimensions[1] / 2)) + self.separationDelta)
            self.logoImagePosition = (round((self.canvas.width() - self.logoImage.width()) / 2),
                                      round(
                                          (self.canvas.height() - self.logoImage.height()) / 2) - self.separationDelta)

        def close(self) -> None:
            self.stop()
            utilities.logger.information("Animation closed successfully")

        def connectToDatabase(self) -> None:
            databaseConnection = utilities.DatabaseConnection()
            self.window().setDatabaseConnection(databaseConnection)
            self.window().connectToDatabase()
            self.postLoadingFunction()
            self.stop()

        def start(self) -> None:
            self.animation.start()
            self.window().threadManager.start(self.connectToDatabase)

        def stop(self) -> None:
            self.animation.stop()
            self.painter.end()

        def updateAnimation(self) -> None:
            # Clear animation for next frame
            self.canvas.fill(core.Qt.transparent)

            # Draw arcs
            degree = -self.animation.currentValue()

            self.painter.drawArc(self.arcPosition[0] + self.animationShift[0],
                                 self.arcPosition[1] + self.animationShift[1],
                                 self.arcDimensions[0],
                                 self.arcDimensions[1],
                                 16 * degree, self.arcLength)
            self.painter.drawArc(self.arcPosition[0] + self.animationShift[0],
                                 self.arcPosition[1] + self.animationShift[1],
                                 self.arcDimensions[0],
                                 self.arcDimensions[1],
                                 16 * (degree + 180), self.arcLength)

            # Draw logo image
            self.painter.drawPixmap(self.logoImagePosition[0] + self.animationShift[0],
                                    self.logoImagePosition[1] + self.animationShift[1],
                                    self.logoImage)
            self.setPixmap(self.canvas)

    class Container(widget.QWidget):
        def __init__(self):
            super().__init__()
            self.setAttribute(core.Qt.WA_StyledBackground, True)

            # TODO: Figure out a better way to change the stylesheet
            # of a parent widget but not it's descendants
            name = str(self)[str(self).rindex(" ") + 1:-1]
            self.setObjectName(name)
            self.setStyleSheet(f"QWidget#{name}"
                               "{"
                               f"border-radius: {15 * settings.DPI}px;"
                               f"background-color: rgba{(255, 255, 255, 120)};"
                               "}")

        def event(self, event: core.QEvent) -> bool:
            if event.type() == core.QEvent.LayoutRequest:
                self.setFixedHeight(self.sizeHint().height())
            return super().event(event)

    class Label(widget.QLabel):
        def __init__(self, text: str):
            super().__init__()
            self.setText(text)
            self.setStyleSheet(f"font-size: {35 * settings.DPI}px;"
                               f"height: {42 * settings.DPI}px;"
                               f"color: rgba{(0, 0, 0, 130)};"
                               "border-style: solid;"
                               "font-family: Arial;"
                               "font-weight: bold;")

    class ErrorLabel(widget.QLabel):
        def __init__(self, parent: widget.QWidget):
            super().__init__(parent)
            self.inserted = False
            self.setWordWrap(True)
            self.palette = self.palette()
            self.setStyleSheet(f"font-size: {20 * settings.DPI}px;"
                               f"margin-left: {70 * settings.DPI}px;"
                               f"margin-top: {1 * settings.DPI}px;"
                               f"margin-right: {70 * settings.DPI}px;"
                               f"margin-bottom: {5 * settings.DPI}px;")

            self.hide()

        def setFeedback(self, text: str, success: bool) -> None:
            if success is False:
                self.palette.setColor(gui.QPalette.WindowText, gui.QColor(255, 0, 0, 150))

            elif success is True:
                self.palette.setColor(gui.QPalette.WindowText, gui.QColor(0, 200, 0, 150))
            self.setPalette(self.palette)
            self.setText(text)

        def isInserted(self) -> bool:
            return self.inserted

        def insert(self) -> None:
            self.parent().layout().insertWidget(1, self)
            self.show()
            self.inserted = True

        def remove(self) -> None:
            self.parent().layout().removeWidget(self)
            self.hide()
            self.inserted = False

    class TextEntry(widget.QLineEdit):
        def __init__(self, placeholder):
            super().__init__()
            self.setPlaceholderText(placeholder)
            self.setStyleSheet("border-style: solid;"
                               f"background-color: rgba{(255, 255, 255, 190)};"
                               f"height: {40 * settings.DPI}px;"
                               f"border-radius: {math.floor((40 * settings.DPI) / 2)}px;"
                               f"padding-left: {12 * settings.DPI}px;"
                               f"padding-right: {12 * settings.DPI}px;"
                               f"margin-left: {70 * settings.DPI}px;"
                               f"margin-top: {5 * settings.DPI}px;"
                               f"margin-right: {70 * settings.DPI}px;"
                               f"margin-bottom: {5 * settings.DPI}px;"
                               f"font-size: {20 * settings.DPI}px;")

    class Button(widget.QPushButton):
        def __init__(self, text: str = None):
            super().__init__()
            self.setFocusPolicy(core.Qt.NoFocus)
            self.setText(text)
            self.setStyleSheet("QPushButton {"
                               "border: none;"
                               f"background-color: rgb{settings.DEFAULT_COLOR.getRgb()};"
                               "color: white;"
                               f"border-radius: {6 * settings.DPI}px;"
                               f"height: {40 * settings.DPI}px;"
                               f"margin-left: {70 * settings.DPI}px;"
                               f"margin-top: {5 * settings.DPI}px;"
                               f"margin-right: {70 * settings.DPI}px;"
                               f"margin-bottom: {5 * settings.DPI}px;"
                               f"font-size: {20 * settings.DPI}px;"
                               "}"
                               "QPushButton::hover"
                               "{"
                               f"background-color: rgb{settings.DEFAULT_COLOR_SELECTED.getRgb()};"
                               "}"
                               "QPushButton::pressed"
                               "{"
                               f"background-color: rgb{settings.DEFAULT_COLOR_PRESSED.getRgb()};"
                               "}")

    class LinkButton(widget.QPushButton):
        def __init__(self, text: str):
            super().__init__()
            self.setFocusPolicy(core.Qt.NoFocus)
            self.setText(text)
            self.setStyleSheet("QPushButton"
                               "{"
                               "text-align: left;"
                               "border: none;"
                               f"font-size: {16 * settings.DPI}px;"
                               "font-weight: bold;"
                               f"color: rgb{settings.DEFAULT_COLOR.getRgb()};"
                               f"margin-left: {10 * settings.DPI}px;"
                               f"margin-right: {250 * settings.DPI}px;"
                               f"height: {30 * settings.DPI}px;"
                               "}"
                               "QPushButton::pressed"
                               "{"
                               f"color: rgb{settings.DEFAULT_COLOR_PRESSED.getRgb()};"
                               "}")


class PixmapImage(gui.QPixmap):
    def __init__(self, filename: str):
        super().__init__()
        with io.BytesIO() as output:
            with Image.open(filename) as self.image:
                # Resize the image
                self.image = self.image.resize((round(self.image.width * settings.DPI),
                                                round(self.image.height * settings.DPI)))
                self.image.save(output, filename[filename.rfind(".") + 1:])
            data = output.getvalue()
            self.loadFromData(data)


class DisconnectOverlay(widget.QLabel):
    def __init__(self, parent: widget.QWidget):
        super().__init__(parent)
        self.setAlignment(core.Qt.AlignCenter)
        self.setText("Reconnecting...")
        self.setAutoFillBackground(True)
        palette = gui.QPalette()
        palette.setColor(self.backgroundRole(), gui.QColor(0, 0, 0, 100))
        self.setPalette(palette)

