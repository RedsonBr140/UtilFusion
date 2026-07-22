# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'filiais_window.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_FiliaisWindow(object):
    def setupUi(self, FiliaisWindow):
        if not FiliaisWindow.objectName():
            FiliaisWindow.setObjectName(u"FiliaisWindow")
        FiliaisWindow.resize(800, 600)
        FiliaisWindow.setStyleSheet(u"QWidget {\n"
"    background-color: white;\n"
"}")
        self.mainVerticalLayout = QVBoxLayout(FiliaisWindow)
        self.mainVerticalLayout.setSpacing(6)
        self.mainVerticalLayout.setObjectName(u"mainVerticalLayout")
        self.mainVerticalLayout.setContentsMargins(10, 10, 10, 10)
        self.searchHorizontalLayout = QHBoxLayout()
        self.searchHorizontalLayout.setSpacing(6)
        self.searchHorizontalLayout.setObjectName(u"searchHorizontalLayout")
        self.SearchLabel = QLabel(FiliaisWindow)
        self.SearchLabel.setObjectName(u"SearchLabel")

        self.searchHorizontalLayout.addWidget(self.SearchLabel)

        self.SearchLineEdit = QLineEdit(FiliaisWindow)
        self.SearchLineEdit.setObjectName(u"SearchLineEdit")
        self.SearchLineEdit.setMinimumSize(QSize(200, 0))

        self.searchHorizontalLayout.addWidget(self.SearchLineEdit)

        self.OkButton = QPushButton(FiliaisWindow)
        self.OkButton.setObjectName(u"OkButton")

        self.searchHorizontalLayout.addWidget(self.OkButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.searchHorizontalLayout.addItem(self.horizontalSpacer)

        self.AtualizarFusionButton = QPushButton(FiliaisWindow)
        self.AtualizarFusionButton.setObjectName(u"AtualizarFusionButton")

        self.searchHorizontalLayout.addWidget(self.AtualizarFusionButton)


        self.mainVerticalLayout.addLayout(self.searchHorizontalLayout)

        self.FiliaisTable = QTableWidget(FiliaisWindow)
        if (self.FiliaisTable.columnCount() < 6):
            self.FiliaisTable.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        self.FiliaisTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.FiliaisTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.FiliaisTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.FiliaisTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.FiliaisTable.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.FiliaisTable.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.FiliaisTable.setObjectName(u"FiliaisTable")
        self.FiliaisTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.FiliaisTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.FiliaisTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.FiliaisTable.setAlternatingRowColors(True)
        self.FiliaisTable.setShowGrid(True)
        self.FiliaisTable.setGridStyle(Qt.SolidLine)
        self.FiliaisTable.setSortingEnabled(False)
        self.FiliaisTable.horizontalHeader().setStretchLastSection(True)
        self.FiliaisTable.verticalHeader().setVisible(False)

        self.mainVerticalLayout.addWidget(self.FiliaisTable)


        self.retranslateUi(FiliaisWindow)

        self.OkButton.setDefault(True)


        QMetaObject.connectSlotsByName(FiliaisWindow)
    # setupUi

    def retranslateUi(self, FiliaisWindow):
        FiliaisWindow.setWindowTitle(QCoreApplication.translate("FiliaisWindow", u"Filiais", None))
        self.SearchLabel.setText(QCoreApplication.translate("FiliaisWindow", u"Buscar:", None))
        self.SearchLineEdit.setPlaceholderText(QCoreApplication.translate("FiliaisWindow", u"Digite para buscar...", None))
        self.OkButton.setText(QCoreApplication.translate("FiliaisWindow", u"OK", None))
        self.AtualizarFusionButton.setText(QCoreApplication.translate("FiliaisWindow", u"Atualizar pelo Fusion", None))
        ___qtablewidgetitem = self.FiliaisTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("FiliaisWindow", u"C\u00f3digo", None))
        ___qtablewidgetitem1 = self.FiliaisTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("FiliaisWindow", u"Nome", None))
        ___qtablewidgetitem2 = self.FiliaisTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("FiliaisWindow", u"Endere\u00e7o", None))
        ___qtablewidgetitem3 = self.FiliaisTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("FiliaisWindow", u"Cidade", None))
        ___qtablewidgetitem4 = self.FiliaisTable.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("FiliaisWindow", u"Estado", None))
        ___qtablewidgetitem5 = self.FiliaisTable.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("FiliaisWindow", u"Telefone", None))
    # retranslateUi

