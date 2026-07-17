# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        if not LoginWindow.objectName():
            LoginWindow.setObjectName(u"LoginWindow")
        LoginWindow.resize(299, 412)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LoginWindow.sizePolicy().hasHeightForWidth())
        LoginWindow.setSizePolicy(sizePolicy)
        LoginWindow.setMinimumSize(QSize(299, 412))
        LoginWindow.setMaximumSize(QSize(299, 412))
        LoginWindow.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        LoginWindow.setStyleSheet(u"QDialog {\n"
"    background-color: white;\n"
"}")
        self.verticalLayoutWidget = QWidget(LoginWindow)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, -10, 301, 71))
        self.BannerVLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.BannerVLayout.setObjectName(u"BannerVLayout")
        self.BannerVLayout.setContentsMargins(0, 0, 0, 0)
        self.UtilFusionBanner = QLabel(self.verticalLayoutWidget)
        self.UtilFusionBanner.setObjectName(u"UtilFusionBanner")
        self.UtilFusionBanner.setPixmap(QPixmap(u"ui/res/LoginBanner.png"))

        self.BannerVLayout.addWidget(self.UtilFusionBanner)

        self.UsuarioLineEdit = QLineEdit(LoginWindow)
        self.UsuarioLineEdit.setObjectName(u"UsuarioLineEdit")
        self.UsuarioLineEdit.setGeometry(QRect(10, 100, 131, 32))
        self.UsuarioLabel = QLabel(LoginWindow)
        self.UsuarioLabel.setObjectName(u"UsuarioLabel")
        self.UsuarioLabel.setGeometry(QRect(10, 60, 61, 41))
        self.SenhaLabel = QLabel(LoginWindow)
        self.SenhaLabel.setObjectName(u"SenhaLabel")
        self.SenhaLabel.setGeometry(QRect(10, 140, 61, 41))
        self.SenhaLineEdit = QLineEdit(LoginWindow)
        self.SenhaLineEdit.setObjectName(u"SenhaLineEdit")
        self.SenhaLineEdit.setGeometry(QRect(10, 180, 131, 32))
        self.SenhaLineEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.LoginButton = QPushButton(LoginWindow)
        self.LoginButton.setObjectName(u"LoginButton")
        self.LoginButton.setGeometry(QRect(160, 130, 121, 61))
        self.LoginButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.LoginButton.setAutoFillBackground(False)

        self.retranslateUi(LoginWindow)

        self.LoginButton.setDefault(True)


        QMetaObject.connectSlotsByName(LoginWindow)
    # setupUi

    def retranslateUi(self, LoginWindow):
        LoginWindow.setWindowTitle(QCoreApplication.translate("LoginWindow", u"UtilFusion - Login", None))
        self.UtilFusionBanner.setText("")
        self.UsuarioLabel.setText(QCoreApplication.translate("LoginWindow", u"Usu\u00e1rio", None))
        self.SenhaLabel.setText(QCoreApplication.translate("LoginWindow", u"Senha", None))
        self.SenhaLineEdit.setInputMask("")
        self.LoginButton.setText(QCoreApplication.translate("LoginWindow", u"Entrar", None))
    # retranslateUi

