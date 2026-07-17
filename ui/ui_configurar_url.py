# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configurar_url.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_ConfigurarURLDialog(object):
    def setupUi(self, ConfigurarURLDialog):
        if not ConfigurarURLDialog.objectName():
            ConfigurarURLDialog.setObjectName(u"ConfigurarURLDialog")
        ConfigurarURLDialog.resize(400, 300)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ConfigurarURLDialog.sizePolicy().hasHeightForWidth())
        ConfigurarURLDialog.setSizePolicy(sizePolicy)
        ConfigurarURLDialog.setMinimumSize(QSize(400, 300))
        ConfigurarURLDialog.setMaximumSize(QSize(400, 300))
        ConfigurarURLDialog.setStyleSheet(u"QDialog {\n"
"    background-color: white;\n"
"}")
        self.verticalLayoutWidget_2 = QWidget(ConfigurarURLDialog)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(0, 0, 401, 51))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.LabelConfigurador = QLabel(self.verticalLayoutWidget_2)
        self.LabelConfigurador.setObjectName(u"LabelConfigurador")
        font = QFont()
        font.setPointSize(24)
        font.setUnderline(True)
        self.LabelConfigurador.setFont(font)
        self.LabelConfigurador.setTextFormat(Qt.TextFormat.AutoText)
        self.LabelConfigurador.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.LabelConfigurador)

        self.gridLayoutWidget = QWidget(ConfigurarURLDialog)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(0, 50, 231, 200))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.SenhaLabel = QLabel(self.gridLayoutWidget)
        self.SenhaLabel.setObjectName(u"SenhaLabel")
        self.SenhaLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.SenhaLabel, 2, 0, 1, 1)

        self.PortaLabel = QLabel(self.gridLayoutWidget)
        self.PortaLabel.setObjectName(u"PortaLabel")
        self.PortaLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.PortaLabel, 4, 0, 1, 1)

        self.UsuarioLineEdit = QLineEdit(self.gridLayoutWidget)
        self.UsuarioLineEdit.setObjectName(u"UsuarioLineEdit")

        self.gridLayout.addWidget(self.UsuarioLineEdit, 0, 1, 1, 1)

        self.NomeBancoLineEdit = QLineEdit(self.gridLayoutWidget)
        self.NomeBancoLineEdit.setObjectName(u"NomeBancoLineEdit")

        self.gridLayout.addWidget(self.NomeBancoLineEdit, 6, 1, 1, 1)

        self.UsuarioLabel = QLabel(self.gridLayoutWidget)
        self.UsuarioLabel.setObjectName(u"UsuarioLabel")
        self.UsuarioLabel.setTextFormat(Qt.TextFormat.AutoText)
        self.UsuarioLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.UsuarioLabel, 0, 0, 1, 1)

        self.EnderecoLabel = QLabel(self.gridLayoutWidget)
        self.EnderecoLabel.setObjectName(u"EnderecoLabel")
        self.EnderecoLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.EnderecoLabel, 3, 0, 1, 1)

        self.NomeBancoLabel = QLabel(self.gridLayoutWidget)
        self.NomeBancoLabel.setObjectName(u"NomeBancoLabel")
        self.NomeBancoLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.NomeBancoLabel, 6, 0, 1, 1)

        self.IPServidorLineEdit = QLineEdit(self.gridLayoutWidget)
        self.IPServidorLineEdit.setObjectName(u"IPServidorLineEdit")

        self.gridLayout.addWidget(self.IPServidorLineEdit, 3, 1, 1, 1)

        self.SenhaLineEdit = QLineEdit(self.gridLayoutWidget)
        self.SenhaLineEdit.setObjectName(u"SenhaLineEdit")
        self.SenhaLineEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.gridLayout.addWidget(self.SenhaLineEdit, 2, 1, 1, 1)

        self.PortaLineEdit = QLineEdit(self.gridLayoutWidget)
        self.PortaLineEdit.setObjectName(u"PortaLineEdit")

        self.gridLayout.addWidget(self.PortaLineEdit, 4, 1, 1, 1)

        self.NomeBancoLineEdit.raise_()
        self.UsuarioLabel.raise_()
        self.SenhaLabel.raise_()
        self.EnderecoLabel.raise_()
        self.PortaLabel.raise_()
        self.NomeBancoLabel.raise_()
        self.UsuarioLineEdit.raise_()
        self.IPServidorLineEdit.raise_()
        self.SenhaLineEdit.raise_()
        self.PortaLineEdit.raise_()
        self.gridLayoutWidget_2 = QWidget(ConfigurarURLDialog)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(0, 250, 391, 51))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.RemoveButton = QPushButton(self.gridLayoutWidget_2)
        self.RemoveButton.setObjectName(u"RemoveButton")

        self.gridLayout_2.addWidget(self.RemoveButton, 0, 2, 1, 1)

        self.ApplyButton = QPushButton(self.gridLayoutWidget_2)
        self.ApplyButton.setObjectName(u"ApplyButton")

        self.gridLayout_2.addWidget(self.ApplyButton, 0, 1, 1, 1)

        self.CancelButton = QPushButton(self.gridLayoutWidget_2)
        self.CancelButton.setObjectName(u"CancelButton")
        self.CancelButton.setAutoDefault(False)

        self.gridLayout_2.addWidget(self.CancelButton, 0, 3, 1, 1)

        QWidget.setTabOrder(self.UsuarioLineEdit, self.SenhaLineEdit)
        QWidget.setTabOrder(self.SenhaLineEdit, self.IPServidorLineEdit)
        QWidget.setTabOrder(self.IPServidorLineEdit, self.PortaLineEdit)
        QWidget.setTabOrder(self.PortaLineEdit, self.NomeBancoLineEdit)
        QWidget.setTabOrder(self.NomeBancoLineEdit, self.ApplyButton)
        QWidget.setTabOrder(self.ApplyButton, self.RemoveButton)
        QWidget.setTabOrder(self.RemoveButton, self.CancelButton)

        self.retranslateUi(ConfigurarURLDialog)

        self.ApplyButton.setDefault(True)


        QMetaObject.connectSlotsByName(ConfigurarURLDialog)
    # setupUi

    def retranslateUi(self, ConfigurarURLDialog):
        ConfigurarURLDialog.setWindowTitle(QCoreApplication.translate("ConfigurarURLDialog", u"Dialog", None))
        self.LabelConfigurador.setText(QCoreApplication.translate("ConfigurarURLDialog", u"Configurador URL", None))
        self.SenhaLabel.setText(QCoreApplication.translate("ConfigurarURLDialog", u"Senha", None))
        self.PortaLabel.setText(QCoreApplication.translate("ConfigurarURLDialog", u"Porta", None))
        self.UsuarioLabel.setText(QCoreApplication.translate("ConfigurarURLDialog", u"Usu\u00e1rio", None))
        self.EnderecoLabel.setText(QCoreApplication.translate("ConfigurarURLDialog", u"IP do servidor", None))
        self.NomeBancoLabel.setText(QCoreApplication.translate("ConfigurarURLDialog", u"Nome do Banco", None))
        self.RemoveButton.setText(QCoreApplication.translate("ConfigurarURLDialog", u"Remover", None))
        self.ApplyButton.setText(QCoreApplication.translate("ConfigurarURLDialog", u"Aplicar", None))
        self.CancelButton.setText(QCoreApplication.translate("ConfigurarURLDialog", u"Cancelar", None))
    # retranslateUi

